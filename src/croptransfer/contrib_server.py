"""Local backend for the website's "Add your field" form.

Standard library only. Stores contributions in SQLite (data/contributions/, gitignored).

    python -m croptransfer.contrib_server            # http://127.0.0.1:8787
    CT_ADMIN_TOKEN=secret python -m croptransfer.contrib_server --host 0.0.0.0

Endpoints:
    POST /api/contributions   store one contribution (validated)
    GET  /api/contributions   list all (localhost, or header X-Admin-Token == CT_ADMIN_TOKEN)
    GET  /api/health
Other paths serve web/dist when it exists, so one process can run behind a domain.
"""

from __future__ import annotations

import argparse
import hmac
import json
import math
import mimetypes
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "contributions" / "contributions.sqlite"
DIST = ROOT / "web" / "dist"

AUSTRIA = (9.45, 46.3, 17.25, 49.1)  # west, south, east, north
MIN_AREA_M2, MAX_AREA_M2 = 3_000, 2_000_000
MAX_BODY = 100_000
MAX_YIELD_T_HA = 25
YEAR_RANGE = (2000, 2035)
RATE_LIMIT = (20, 3600)  # submissions per client and seconds


class Invalid(ValueError):
    pass


def ring_area_m2(ring: list[list[float]]) -> float:
    """Planar area (shoelace) after a local equirectangular projection."""
    lat0 = sum(p[1] for p in ring) / len(ring)
    kx = 111_320 * math.cos(math.radians(lat0))
    ky = 110_540
    pts = [(p[0] * kx, p[1] * ky) for p in ring]
    s = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    return abs(s) / 2


def _yield_ok(v: object) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 < v <= MAX_YIELD_T_HA:
        raise Invalid("Yields must be between 0 and 25 t/ha.")
    return float(v)


def _year_ok(v: object) -> int:
    if not isinstance(v, int) or isinstance(v, bool) or not YEAR_RANGE[0] <= v <= YEAR_RANGE[1]:
        raise Invalid("Invalid year.")
    return v


def validate(body: dict) -> dict:
    """Return the cleaned record or raise Invalid with a message safe to show the user."""
    if body.get("consent") is not True:
        raise Invalid("Consent is required.")
    poly = body.get("polygon")
    try:
        ring = poly["coordinates"][0]
        assert poly["type"] == "Polygon" and 4 <= len(ring) <= 500
        ring = [[float(x), float(y)] for x, y in ring]
    except Exception as e:  # noqa: BLE001
        raise Invalid("The field outline is not a valid polygon.") from e
    west, south, east, north = AUSTRIA
    if not all(west <= x <= east and south <= y <= north for x, y in ring):
        raise Invalid("The field must be in Austria.")
    area = ring_area_m2(ring)
    if not MIN_AREA_M2 <= area <= MAX_AREA_M2:
        raise Invalid("The field must be between 0.3 and 200 ha.")

    past = [{"year": _year_ok(i.get("year")), "tPerHa": _yield_ok(i.get("tPerHa"))} for i in body.get("pastYields") or []]
    if len({p["year"] for p in past}) != len(past):
        raise Invalid("Each year can only appear once.")
    this = body.get("thisYear")
    if this is not None:
        if this.get("status") not in ("harvested", "estimate"):
            raise Invalid("Invalid current-season entry.")
        this = {"year": _year_ok(this.get("year")), "tPerHa": _yield_ok(this.get("tPerHa")), "status": this["status"]}
    if not past and this is None:
        raise Invalid("Enter at least one yield.")
    if body.get("cropType") not in ("grain", "silage"):
        raise Invalid("Invalid maize type.")
    return {
        "polygon": {"type": "Polygon", "coordinates": [ring]},
        "area_m2": round(area),
        "field_name": str(body.get("fieldName") or "")[:80],
        "crop_type": body["cropType"],
        "irrigated": bool(body.get("irrigated")),
        "past_yields": past,
        "this_year": this,
    }


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS contributions (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, record TEXT NOT NULL)")
    return db


def store(db: sqlite3.Connection, record: dict) -> dict:
    full = {"id": str(uuid.uuid4()), "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record}
    db.execute("INSERT INTO contributions VALUES (?,?,?)", (full["id"], full["createdAt"], json.dumps(full)))
    db.commit()
    return full


def list_all(db: sqlite3.Connection) -> list[dict]:
    return [json.loads(r[0]) for r in db.execute("SELECT record FROM contributions ORDER BY created_at")]


_hits: dict[str, list[float]] = {}


def rate_limited(client: str, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    recent = [t for t in _hits.get(client, []) if now - t < RATE_LIMIT[1]]
    _hits[client] = recent
    if len(recent) >= RATE_LIMIT[0]:
        return True
    recent.append(now)
    return False


class Handler(BaseHTTPRequestHandler):
    server_version = "CropTransferContrib/1"

    def _send(self, code: int, payload: object, ctype: str = "application/json") -> None:
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _is_admin(self) -> bool:
        token = os.environ.get("CT_ADMIN_TOKEN", "")
        if token:
            return hmac.compare_digest(self.headers.get("X-Admin-Token", ""), token)
        return self.client_address[0] in ("127.0.0.1", "::1")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/contributions":
            return self._send(404, {"error": "not found"})
        if rate_limited(self.client_address[0]):
            return self._send(429, {"error": "Too many submissions, please try again later."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                raise Invalid("Request too large.")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise Invalid("Invalid request.")
            record = validate(body)
        except Invalid as e:
            return self._send(400, {"error": str(e)})
        except ValueError:
            return self._send(400, {"error": "Invalid request."})
        with connect() as db:
            full = store(db, record)
        self._send(201, {"id": full["id"], "createdAt": full["createdAt"]})

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/api/health":
            return self._send(200, {"ok": True})
        if path == "/api/contributions":
            if not self._is_admin():
                return self._send(403, {"error": "forbidden"})
            with connect() as db:
                return self._send(200, list_all(db))
        if path.startswith("/api/") or not DIST.exists():
            return self._send(404, {"error": "not found"})
        target = (DIST / path.lstrip("/")).resolve()
        if not target.is_file() or DIST.resolve() not in target.parents:
            target = DIST / "index.html"  # single-page app fallback
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._send(200, target.read_bytes(), ctype)

    def log_message(self, fmt: str, *args: object) -> None:  # path only, no client addresses
        print(f"[contrib] {self.command} {self.path.split('?')[0]} -> {args[1] if len(args) > 1 else ''}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    a = ap.parse_args()
    print(f"Contribution server on http://{a.host}:{a.port} · database {DB_PATH}")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
