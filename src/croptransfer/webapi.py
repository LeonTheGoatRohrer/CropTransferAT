"""Local backend for "Dein Feld, dein Verlauf" (FastAPI + SQLite; local only, never deployed).

Start:  python -m croptransfer.webapi        -> http://127.0.0.1:8000  (docs: /docs)
DB:     data/app_local/fields.sqlite (not in git; fields are pseudonymous)

Path A = fielddb.baseline (user's own yield history), path B = field_pipeline.analyse (frozen US stress score
with the frozen alert calibration). Notifications are stored in the app only (no e-mail, no push).
"""

from __future__ import annotations

import os
import threading
import traceback
from datetime import date
from typing import Callable, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from croptransfer import fielddb
from croptransfer.config import repo_path

CUTOFFS = ["06-01", "06-15", "07-01", "07-15", "08-01", "08-15", "09-01"]
MIN_AREA_M2, MAX_AREA_M2 = 3_000, 2_000_000
DEFAULT_DB = "data/app_local/fields.sqlite"


class FieldIn(BaseModel):
    label: str = Field(min_length=1, max_length=40, description="Pseudonym, kein echter Name")
    geometry: dict

    @field_validator("geometry")
    @classmethod
    def polygon_only(cls, g: dict) -> dict:
        if g.get("type") != "Polygon" or not g.get("coordinates"):
            raise ValueError("Nur ein einzelnes Polygon ist erlaubt.")
        return g


class YieldEntry(BaseModel):
    year: int
    value: float


class YieldsIn(BaseModel):
    unit: Literal["t/ha", "dt/ha"]
    entries: list[YieldEntry]


class AlertIn(BaseModel):
    cutoff: str
    hint_pct: int = Field(ge=5, le=50)
    warn_pct: int = Field(ge=5, le=60)

    @field_validator("cutoff")
    @classmethod
    def known_cutoff(cls, c: str) -> str:
        if c not in CUTOFFS:
            raise ValueError("Stichtag muss einer von " + ", ".join(CUTOFFS) + " sein.")
        return c


class AnalysisIn(BaseModel):
    year: int = Field(ge=2013)
    cutoff: str | None = None


def polygon_area_m2(geometry: dict) -> float:
    import geopandas as gpd
    from shapely.geometry import shape

    g = gpd.GeoSeries([shape(geometry)], crs=4326)
    return float(g.to_crs(g.estimate_utm_crs()).area.iloc[0])


def create_app(db_path: str | None = None, analyse_fn: Callable | None = None) -> FastAPI:
    """App factory; `analyse_fn` defaults to field_pipeline.analyse (tests inject a fake)."""
    store = fielddb.Store(db_path or repo_path(DEFAULT_DB))
    if analyse_fn is None:
        from croptransfer import field_pipeline

        analyse_fn = field_pipeline.analyse

    app = FastAPI(title="CropTransfer AT – lokales Backend", version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5180", "http://localhost:5181",
                                                      "http://127.0.0.1:5180", "http://127.0.0.1:5181"],
                       allow_methods=["*"], allow_headers=["*"])

    def field_or_404(fid: str) -> dict:
        f = store.get_field(fid)
        if not f:
            raise HTTPException(404, "Feld nicht gefunden.")
        return f

    def yields_map(fid: str) -> dict[int, float]:
        return {r["year"]: r["t_ha"] for r in store.get_yields(fid)}

    @app.get("/api/health")
    def health():
        from croptransfer import field_pipeline

        cal = field_pipeline.calibration()
        return {"ok": True, "backend": "local", "calibration_date": cal["date"], "model": "freeze-at-1 stress score"}

    @app.get("/api/calibration")
    def calibration():
        from croptransfer import field_pipeline

        cal = field_pipeline.calibration()
        return {k: cal[k] for k in ("date", "n_field_years", "n_site_years", "rules", "table", "frozen_thresholds")}

    @app.post("/api/fields", status_code=201)
    def create_field(body: FieldIn):
        try:
            area = polygon_area_m2(body.geometry)
        except Exception as e:  # invalid coordinates
            raise HTTPException(422, f"Feldgrenze nicht lesbar: {e}") from e
        if not MIN_AREA_M2 <= area <= MAX_AREA_M2:
            raise HTTPException(422, "Das Feld muss zwischen 0,3 ha und 200 ha groß sein.")
        return store.create_field(body.label.strip(), body.geometry, area)

    @app.get("/api/fields")
    def list_fields():
        return store.list_fields()

    @app.get("/api/fields/{fid}")
    def get_field(fid: str, year: int | None = None):
        f = field_or_404(fid)
        alert = store.get_alert(fid)
        y = year or date.today().year
        return f | {"yields": store.get_yields(fid), "alert": alert,
                    "baseline": fielddb.baseline(yields_map(fid), y, alert and alert["hint_pct"], alert and alert["warn_pct"])}

    @app.delete("/api/fields/{fid}", status_code=204)
    def delete_field(fid: str):
        if not store.delete_field(fid):
            raise HTTPException(404, "Feld nicht gefunden.")

    @app.put("/api/fields/{fid}/yields")
    def put_yields(fid: str, body: YieldsIn):
        field_or_404(fid)
        try:
            return store.set_yields(fid, body.unit, [e.model_dump() for e in body.entries])
        except ValueError as e:
            raise HTTPException(422, str(e)) from e

    @app.get("/api/fields/{fid}/baseline")
    def get_baseline(fid: str, year: int):
        field_or_404(fid)
        a = store.get_alert(fid)
        return fielddb.baseline(yields_map(fid), year, a and a["hint_pct"], a and a["warn_pct"])

    @app.put("/api/fields/{fid}/alert")
    def put_alert(fid: str, body: AlertIn):
        field_or_404(fid)
        if body.warn_pct <= body.hint_pct:
            raise HTTPException(422, "Die Warnschwelle muss größer sein als die Hinweisschwelle.")
        return store.set_alert(fid, body.cutoff, body.hint_pct, body.warn_pct)

    def run(aid: str, field: dict, year: int, cutoff: str, hint: int, warn: int) -> None:
        facts: dict = {}

        def progress(stage: str, f: dict) -> None:
            if f:
                facts[stage] = f
            store.update_analysis(aid, status="running", stage=stage, facts=facts)

        try:
            res = analyse_fn(field["geometry"], year, cutoff, hint, warn, progress=progress, key=field["id"])
            res["baseline"] = fielddb.baseline(yields_map(field["id"]), year, hint, warn)
            store.update_analysis(aid, status="completed", stage="completed", facts=facts, result=res, finished_at=fielddb.now())
            state = res.get("alert", {}).get("state")
            if state in ("hint", "warning"):
                store.add_notification(field["id"], aid, state, {"year": year, "cutoff": cutoff, "alert": res["alert"]})
        except Exception as e:  # reported to the UI as a failed analysis
            traceback.print_exc()
            store.update_analysis(aid, status="error", error=str(e)[:500], finished_at=fielddb.now())

    @app.post("/api/fields/{fid}/analyses", status_code=202)
    def start_analysis(fid: str, body: AnalysisIn):
        f = field_or_404(fid)
        if body.year > date.today().year:
            raise HTTPException(422, "Dieses Jahr liegt in der Zukunft.")
        a = store.get_alert(fid) or {"cutoff": "09-01", "hint_pct": 20, "warn_pct": 30}
        cutoff = body.cutoff or a["cutoff"]
        if cutoff not in CUTOFFS:
            raise HTTPException(422, "Unbekannter Stichtag.")
        aid = store.create_analysis(fid, body.year, cutoff)
        threading.Thread(target=run, args=(aid, f, body.year, cutoff, a["hint_pct"], a["warn_pct"]), daemon=True).start()
        return {"id": aid, "status": "queued"}

    @app.get("/api/analyses/{aid}")
    def get_analysis(aid: str):
        a = store.get_analysis(aid)
        if not a:
            raise HTTPException(404, "Analyse nicht gefunden.")
        return a

    @app.get("/api/notifications")
    def notifications():
        return store.list_notifications()

    @app.post("/api/notifications/{nid}/read", status_code=204)
    def read_notification(nid: str):
        if not store.mark_read(nid):
            raise HTTPException(404, "Benachrichtigung nicht gefunden.")

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(create_app(os.environ.get("CROPTRANSFER_DB")), host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))


if __name__ == "__main__":
    main()
