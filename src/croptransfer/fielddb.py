"""Local SQLite store and path A (reference without training) for "Dein Feld, dein Verlauf".

Path A (DECISIONS 2026-10-17): normal level N(y) = mean of the user's yields of the same field in the OTHER
years (as RY in PLAN 3.6); RY(y) = Y(y) / N(y). History = number of other years: < 3 -> no assessment,
3-4 -> assessment with a hint, >= 5 -> plain. Units t/ha or dt/ha; 0 < Y <= 25 t/ha. Fields are pseudonymous.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

MAX_T_HA = 25.0
MIN_YEAR = 1990
UNIT_FACTOR = {"t/ha": 1.0, "dt/ha": 0.1}
HISTORY_NONE, HISTORY_HINT = 3, 5

SCHEMA = """
CREATE TABLE IF NOT EXISTS fields (
  id TEXT PRIMARY KEY, label TEXT NOT NULL, crop TEXT NOT NULL DEFAULT 'maize',
  geometry TEXT NOT NULL, area_m2 REAL NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS yields (
  field_id TEXT NOT NULL REFERENCES fields(id) ON DELETE CASCADE, year INTEGER NOT NULL,
  t_ha REAL NOT NULL, unit TEXT NOT NULL, value REAL NOT NULL, PRIMARY KEY (field_id, year));
CREATE TABLE IF NOT EXISTS alerts (
  field_id TEXT PRIMARY KEY REFERENCES fields(id) ON DELETE CASCADE, cutoff TEXT NOT NULL,
  hint_pct INTEGER NOT NULL, warn_pct INTEGER NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY, field_id TEXT NOT NULL REFERENCES fields(id) ON DELETE CASCADE, year INTEGER NOT NULL,
  cutoff TEXT NOT NULL, status TEXT NOT NULL, stage TEXT, facts TEXT NOT NULL DEFAULT '{}', result TEXT,
  error TEXT, created_at TEXT NOT NULL, finished_at TEXT);
CREATE TABLE IF NOT EXISTS notifications (
  id TEXT PRIMARY KEY, field_id TEXT NOT NULL REFERENCES fields(id) ON DELETE CASCADE, analysis_id TEXT,
  level TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, read INTEGER NOT NULL DEFAULT 0);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------------------------------ path A
def to_t_ha(value: float, unit: str) -> float:
    if unit not in UNIT_FACTOR:
        raise ValueError("Einheit muss t/ha oder dt/ha sein.")
    v = float(value) * UNIT_FACTOR[unit]
    if not (0 < v <= MAX_T_HA):
        raise ValueError(f"Ertrag muss größer als 0 und höchstens {MAX_T_HA:g} t/ha sein (eingegeben: {value} {unit}).")
    return v


def validate_entries(entries: list[dict], unit: str, today: date | None = None) -> list[tuple[int, float, float]]:
    """-> [(year, t_ha, value)], raises ValueError with a German message on invalid input."""
    today = today or date.today()
    seen: set[int] = set()
    out = []
    for e in entries:
        y = int(e["year"])
        if not (MIN_YEAR <= y <= today.year):
            raise ValueError(f"Jahr {y} liegt außerhalb von {MIN_YEAR}–{today.year}.")
        if y in seen:
            raise ValueError(f"Jahr {y} ist doppelt eingetragen.")
        seen.add(y)
        out.append((y, to_t_ha(e["value"], unit), float(e["value"])))
    return sorted(out)


def history_level(n_other: int) -> str:
    return "too_little" if n_other < HISTORY_NONE else "with_hint" if n_other < HISTORY_HINT else "ok"


def baseline(yields: dict[int, float], year: int, hint_pct: int | None = None, warn_pct: int | None = None) -> dict[str, Any]:
    """Path A for target year `year`: normal level from the other years, RY if the year has a yield."""
    others = {y: v for y, v in yields.items() if y != year}
    n_other = len(others)
    level = history_level(n_other)
    normal = sum(others.values()) / n_other if n_other else None
    y_now = yields.get(year)
    ry = (y_now / normal) if (y_now is not None and normal) else None
    per_year = []
    for y, v in sorted(yields.items()):
        o = [w for z, w in yields.items() if z != y]
        n = sum(o) / len(o) if o else None
        per_year.append({"year": y, "t_ha": round(v, 3), "normal_others": None if n is None else round(n, 3),
                         "ry": None if not n else round(v / n, 3), "n_other": len(o)})
    out: dict[str, Any] = {
        "year": year, "n_other_years": n_other, "history": level,
        "normal_t_ha": None if normal is None else round(normal, 3),
        "yield_t_ha": None if y_now is None else round(y_now, 3),
        "ry": None if ry is None or level == "too_little" else round(ry, 3),
        "per_year": per_year, "state": "no_assessment" if level == "too_little" else ("pending" if ry is None else "ok"),
    }
    if normal is not None and level != "too_little":
        for key, pct in (("hint", hint_pct), ("warning", warn_pct)):
            if pct is not None:
                out[f"{key}_below_t_ha"] = round(normal * (1 - pct / 100), 3)
        if ry is not None:
            if warn_pct is not None and ry < 1 - warn_pct / 100:
                out["state"] = "warning"
            elif hint_pct is not None and ry < 1 - hint_pct / 100:
                out["state"] = "hint"
            else:
                out["state"] = "normal"
    return out


# ------------------------------------------------------------------------------------------ store
class Store:
    """Thread-safe minimal SQLite wrapper (one connection per call)."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.lock = threading.Lock()
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON")
        return c

    # fields
    def create_field(self, label: str, geometry: dict, area_m2: float) -> dict:
        fid = uuid.uuid4().hex[:10]
        with self.lock, self._conn() as c:
            c.execute("INSERT INTO fields VALUES (?,?,?,?,?,?)", (fid, label, "maize", json.dumps(geometry), area_m2, now()))
        return self.get_field(fid)

    def list_fields(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT f.*, (SELECT COUNT(*) FROM yields y WHERE y.field_id=f.id) AS n_yields "
                             "FROM fields f ORDER BY created_at").fetchall()
        return [self._field(r) | {"n_yields": r["n_yields"]} for r in rows]

    def get_field(self, fid: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM fields WHERE id=?", (fid,)).fetchone()
        return self._field(r) if r else None

    def delete_field(self, fid: str) -> bool:
        with self.lock, self._conn() as c:
            return c.execute("DELETE FROM fields WHERE id=?", (fid,)).rowcount > 0

    @staticmethod
    def _field(r) -> dict:
        return {"id": r["id"], "label": r["label"], "crop": r["crop"], "geometry": json.loads(r["geometry"]),
                "area_m2": r["area_m2"], "created_at": r["created_at"]}

    # yields
    def set_yields(self, fid: str, unit: str, entries: list[dict]) -> list[dict]:
        rows = validate_entries(entries, unit)
        with self.lock, self._conn() as c:
            c.execute("DELETE FROM yields WHERE field_id=?", (fid,))
            c.executemany("INSERT INTO yields VALUES (?,?,?,?,?)", [(fid, y, t, unit, v) for y, t, v in rows])
        return self.get_yields(fid)

    def get_yields(self, fid: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT year, t_ha, unit, value FROM yields WHERE field_id=? ORDER BY year", (fid,)).fetchall()
        return [dict(r) for r in rows]

    # alerts
    def set_alert(self, fid: str, cutoff: str, hint_pct: int, warn_pct: int) -> dict:
        with self.lock, self._conn() as c:
            c.execute("INSERT INTO alerts VALUES (?,?,?,?,?) ON CONFLICT(field_id) DO UPDATE SET cutoff=excluded.cutoff, "
                      "hint_pct=excluded.hint_pct, warn_pct=excluded.warn_pct, updated_at=excluded.updated_at",
                      (fid, cutoff, hint_pct, warn_pct, now()))
        return self.get_alert(fid)

    def get_alert(self, fid: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT cutoff, hint_pct, warn_pct, updated_at FROM alerts WHERE field_id=?", (fid,)).fetchone()
        return dict(r) if r else None

    # analyses
    def create_analysis(self, fid: str, year: int, cutoff: str) -> str:
        aid = uuid.uuid4().hex[:12]
        with self.lock, self._conn() as c:
            c.execute("INSERT INTO analyses (id, field_id, year, cutoff, status, created_at) VALUES (?,?,?,?,?,?)",
                      (aid, fid, year, cutoff, "queued", now()))
        return aid

    def update_analysis(self, aid: str, **kw) -> None:
        cols = ", ".join(f"{k}=?" for k in kw)
        vals = [json.dumps(v, default=str) if k in ("facts", "result") else v for k, v in kw.items()]
        with self.lock, self._conn() as c:
            c.execute(f"UPDATE analyses SET {cols} WHERE id=?", (*vals, aid))

    def get_analysis(self, aid: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM analyses WHERE id=?", (aid,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["facts"] = json.loads(d["facts"] or "{}")
        d["result"] = json.loads(d["result"]) if d["result"] else None
        return d

    # notifications
    def add_notification(self, fid: str, aid: str | None, level: str, payload: dict) -> None:
        with self.lock, self._conn() as c:
            c.execute("INSERT INTO notifications VALUES (?,?,?,?,?,?,0)",
                      (uuid.uuid4().hex[:12], fid, aid, level, json.dumps(payload, default=str), now()))

    def list_notifications(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT n.*, f.label FROM notifications n JOIN fields f ON f.id=n.field_id "
                             "ORDER BY n.created_at DESC LIMIT 50").fetchall()
        return [dict(r) | {"payload": json.loads(r["payload"]), "read": bool(r["read"])} for r in rows]

    def mark_read(self, nid: str) -> bool:
        with self.lock, self._conn() as c:
            return c.execute("UPDATE notifications SET read=1 WHERE id=?", (nid,)).rowcount > 0
