"""On-demand analysis of one drawn maize field ("Dein Feld, dein Verlauf", DECISIONS 2026-10-17).

Uses exactly the code paths of training and of the Austria test, nothing re-implemented:
  satellite  gee_extract.scene_stats (HLS) -> timeseries.to_reflectance/add_indices/valid_obs
             -> at_test.dekad_matrix -> at_test.scores_from_matrix with the frozen reference (freeze-at-1)
  weather    gee_extract.era5_daily -> features.daily_weather -> features.weather_features
  soil       gee_extract.static_stats -> features.static_features
The frozen model is never refitted. The alert uses the frozen thresholds and hit rates of
results/2026-10-17_alert_calibration (DECISIONS 2026-10-17). Weather hints are the pre-registered rules of
stress.causes without the satellite rule; no cause is claimed.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from functools import lru_cache
from typing import Any, Callable

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import shape

from croptransfer import at_test, features, stress
from croptransfer import timeseries as ts
from croptransfer.config import load_config, repo_path

CUTOFFS = ["06-01", "06-15", "07-01", "07-15", "08-01", "08-15", "09-01"]
N_DEKADS = 21
NORMAL_YEARS = 10                     # weather normal = mean of the 10 previous seasons (labelled in the UI)
CALIBRATION = "results/2026-10-17_alert_calibration/calibration.json"
REFERENCE = "reports/freeze_at/stress_reference_hls_ndvi.csv"
PHASES = {"Jun": (6, 8), "Jul": (9, 11), "Aug": (12, 14)}   # dekads (0 = 1.-10.4.)

Progress = Callable[[str, dict], None]


# ------------------------------------------------------------------------------------- frozen inputs
@lru_cache(maxsize=1)
def frozen_reference() -> pd.Series:
    return pd.read_csv(repo_path(REFERENCE), index_col=0)["ndvi_median"]


@lru_cache(maxsize=1)
def calibration() -> dict:
    return json.loads(repo_path(CALIBRATION).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def us_reference_bands() -> dict:
    """Healthy US reference band (p25/median/p75) per index on the HLS basis, for display only."""
    p = repo_path("data/app/reference.parquet")
    out = {}
    if p.exists():
        ref = pd.read_parquet(p)
        for idx in ("ndvi", "evi", "ndmi"):
            b = ref[(ref.basis == "HLS") & (ref["index"] == idx)].set_index("dekad").reindex(range(N_DEKADS))
            out[idx] = {k: [None if pd.isna(v) else round(float(v), 4) for v in b[k]] for k in ("p25", "median", "p75")}
            out[idx]["n_fieldyears"] = int(ref.n_fieldyears.iloc[0])
    fro = frozen_reference().reindex(range(N_DEKADS))
    out.setdefault("ndvi", {"p25": [None] * N_DEKADS, "p75": [None] * N_DEKADS, "n_fieldyears": 77})
    out["ndvi"]["median"] = [None if pd.isna(v) else round(float(v), 4) for v in fro]
    return out


# ------------------------------------------------------------------------------------- geometry
def prepare_polygon(geometry: dict, key: str, cfg: dict) -> gpd.GeoDataFrame:
    """Drawn polygon -> one-row GeoDataFrame in EPSG:4326 with the training inner buffer (-10 m)."""
    g = gpd.GeoDataFrame({"fy_key": [key]}, geometry=[shape(geometry)], crs=4326)
    if not g.geometry.iloc[0].is_valid:
        raise ValueError("Die Feldgrenze ist ungültig (sich kreuzende Kanten).")
    utm = g.estimate_utm_crs()
    m = g.to_crs(utm)
    area = float(m.area.iloc[0])
    m["geometry"] = m.geometry.buffer(cfg["field"]["inner_buffer_m"])
    if m.geometry.iloc[0].is_empty:
        raise ValueError("Das Feld ist nach dem 10-m-Randpuffer leer; bitte größer zeichnen.")
    out = m.to_crs(4326)
    out["area_m2"] = area
    out["area_buffered_m2"] = float(m.area.iloc[0])
    return out


# ------------------------------------------------------------------------------------- pure steps
def dekad_rows(obs: pd.DataFrame, cfg: dict) -> dict[str, list[float | None]]:
    """Scene table -> observed dekad medians (no interpolation) for NDVI, EVI, NDMI."""
    if obs is None or obs.empty:
        return {i: [None] * N_DEKADS for i in ("ndvi", "evi", "ndmi")}
    o = ts.valid_obs(ts.add_indices(ts.to_reflectance(obs)), cfg["field"]["clear_frac_min"])
    out = {}
    for idx in ("ndvi", "evi", "ndmi"):
        if idx not in o.columns or o.empty:
            out[idx] = [None] * N_DEKADS
            continue
        mat = at_test.dekad_matrix(o, idx)
        row = mat.iloc[0] if len(mat) else pd.Series(np.nan, index=range(N_DEKADS))
        out[idx] = [None if pd.isna(v) else round(float(v), 4) for v in row.reindex(range(N_DEKADS))]
    return out


def frozen_scores(ndvi: list[float | None], cfg: dict) -> dict[str, dict]:
    """Frozen stress score (freeze-at-1) at every cutoff; NaN -> None when < min observed dekads."""
    mat = pd.DataFrame([[np.nan if v is None else v for v in ndvi]], columns=range(N_DEKADS), index=["f"])
    sc = cfg["at_test"]
    out = {}
    for c in CUTOFFS:
        r = at_test.scores_from_matrix(mat, frozen_reference(), c, sc["stress"]["first_dekad"], sc["min_observed_dekads"])
        s = float(r.score.iloc[0])
        out[c] = {"score": None if not np.isfinite(s) else round(s, 5), "n_obs": int(r.n_obs.iloc[0])}
    return out


def phase_shortfall(ndvi: list[float | None]) -> dict[str, float]:
    """Summed NDVI shortfall below the frozen reference per month (observed dekads only; descriptive)."""
    ref = frozen_reference()
    out = {}
    for k, (a, b) in PHASES.items():
        dev = [min(ndvi[d] - float(ref[d]), 0.0) for d in range(a, b + 1) if ndvi[d] is not None and d in ref.index]
        out[k] = round(float(sum(dev)), 4)
    return out


def calibration_row(cutoff: str, x_pct: int) -> dict | None:
    for r in calibration()["table"]:
        if r["cutoff"] == cutoff and int(r["x_pct"]) == int(x_pct):
            return r
    return None


def evaluate_alert(score: float | None, cutoff: str, hint_pct: int, warn_pct: int) -> dict:
    """Level none/hint/warning with the frozen thresholds; 'no_statement' where calibration does not allow one."""
    thr = calibration()["frozen_thresholds"]
    levels = []
    for level, x in (("warning", warn_pct), ("hint", hint_pct)):
        row = calibration_row(cutoff, x)
        s_star = thr.get(f"{cutoff}|{x}")
        ok = row is not None and row["statement"] == "ok" and s_star is not None and score is not None
        levels.append({
            "level": level, "x_pct": x, "statement": "ok" if ok else "no_statement",
            "threshold": s_star, "triggered": bool(ok and score <= s_star),
            "k_hit": row["k_hit"] if row else None, "n_alert": row["n_alert"] if row else None,
            "prevalence": row["prevalence"] if row else None,
            "reasons": (row["reasons"] if row else ["no calibration for this combination"]) if not ok else [],
        })
    warn, hint = levels
    state = "warning" if warn["triggered"] else "hint" if hint["triggered"] else (
        "no_statement" if warn["statement"] != "ok" and hint["statement"] != "ok" else "none")
    return {"state": state, "cutoff": cutoff, "score": score, "levels": levels}


def weather_hints(wf: dict) -> list[dict]:
    """Pre-registered weather rules (stress.py, DECISIONS 2026-10-16), satellite rule left out. No cause claim."""
    out = []
    cwb, rz = wf.get("cwb_30d", np.nan), wf.get("rzwsi_flower", np.nan)
    if (np.isfinite(rz) and rz >= stress.DROUGHT_RZWSI) or (np.isfinite(cwb) and cwb < stress.DROUGHT_CWB30):
        out.append({"key": "drought", "value_cwb_30d_mm": None if not np.isfinite(cwb) else round(float(cwb)),
                    "rule": f"Wasserbilanz 30 Tage < {stress.DROUGHT_CWB30:.0f} mm oder Wasserstress in der Blüte ≥ {stress.DROUGHT_RZWSI}"})
    if wf.get("heat32_flower", 0) >= stress.HEAT_DAYS:
        out.append({"key": "heat_flowering", "days": int(wf["heat32_flower"]),
                    "rule": f"≥ {stress.HEAT_DAYS} Tage über 32 °C zwischen 10.7. und 20.8."})
    if wf.get("prec_spring", 0) >= stress.WET_SPRING_MM:
        out.append({"key": "wet_spring", "mm": round(float(wf["prec_spring"])),
                    "rule": f"Niederschlag 1.4.–31.5. ≥ {stress.WET_SPRING_MM:.0f} mm"})
    return out


def weather_dekads(daily: pd.DataFrame, year: int) -> dict[str, list[float | None]]:
    d = daily[daily.date.dt.year == year].copy()
    start = pd.Timestamp(f"{year}-04-01")
    d["dekad"] = ((d.date - start).dt.days // 10)
    d = d[(d.dekad >= 0) & (d.dekad < N_DEKADS)]
    g = d.groupby("dekad").agg(tmean=("tmean", "mean"), tmax=("tmax", "mean"), prec=("prec", "sum"), gdd=("gdd", "sum"),
                               heat=("tmax", lambda s: int((s > 32).sum())), swvl=("swvl2", "mean"), vpd=("vpd", "mean"))
    g = g.reindex(range(N_DEKADS))
    return {k: [None if pd.isna(v) else round(float(v), 2) for v in g[k]] for k in g.columns}


def normal_dekads(dailies: list[pd.DataFrame], years: list[int]) -> dict[str, list[float | None]]:
    rows = [weather_dekads(d, y) for d, y in zip(dailies, years) if d is not None and len(d)]
    if not rows:
        return {}
    out = {}
    for k in rows[0]:
        arr = np.array([[np.nan if v is None else v for v in r[k]] for r in rows], dtype=float)
        with np.errstate(all="ignore"):
            m = np.nanmean(arr, axis=0)
        out[k] = [None if not np.isfinite(v) else round(float(v), 2) for v in m]
    return out


# ------------------------------------------------------------------------------------- orchestration
def analyse(geometry: dict, year: int, cutoff: str, hint_pct: int, warn_pct: int, cfg: dict | None = None,
            progress: Progress | None = None, key: str = "user") -> dict[str, Any]:
    """Full on-demand analysis (needs Google Earth Engine). Emits progress(stage, facts) per pipeline step."""
    from croptransfer import gee_extract

    cfg = cfg or load_config()
    say = progress or (lambda s, f: None)
    if cutoff not in CUTOFFS:
        raise ValueError(f"Stichtag {cutoff} ist nicht erlaubt.")
    if not 2013 <= year <= date.today().year:
        raise ValueError("HLS-Daten gibt es ab 2013.")
    gee_extract.init_ee()
    fy = prepare_polygon(geometry, f"{key}|{year}", cfg)
    c = fy.geometry.iloc[0].centroid
    lon, lat = float(c.x), float(c.y)

    say("loadingSatellite", {})
    end = min(date.today(), date(year, 11, 1)).isoformat()
    obs = gee_extract.scene_stats(fy, "HLS", f"{year}-04-01", end, cfg)
    n_scenes = 0 if obs is None or obs.empty else len(obs)
    n_clear = 0 if not n_scenes else int((obs.n_clear / obs.n_total >= cfg["field"]["clear_frac_min"]).sum())
    say("loadingSatellite", {"n_scenes": n_scenes, "n_clear": n_clear})

    say("processingSatellite", {})
    idx = dekad_rows(obs, cfg)
    say("processingSatellite", {"n_observed": sum(v is not None for v in idx["ndvi"])})

    say("loadingWeather", {})
    years = [year] + [year - k for k in range(1, NORMAL_YEARS + 1)]
    with ThreadPoolExecutor(4) as ex:
        raw = list(ex.map(lambda y: gee_extract.era5_daily({"p": (lon, lat)}, f"{y}-03-01", f"{y}-11-01", cfg), years))
    dailies = [features.daily_weather(r.assign(date=pd.to_datetime(r.date)), lat) if r is not None and len(r) else None
               for r in raw]
    cur = dailies[0]
    say("loadingWeather", {"normal_years": [years[-1], years[1]]})

    say("loadingEnvironment", {})
    st = gee_extract.static_stats(fy.rename(columns={"fy_key": "field_uid"}), cfg)
    stf = features.static_features(st).iloc[0] if len(st) else None
    say("loadingEnvironment", {})

    say("featureEngineering", {})
    scores = frozen_scores(idx["ndvi"], cfg)
    awc = float(stf["awc"]) if stf is not None else 0.15
    cut_date = features.cutoff_date(year, cutoff)
    wf = features.weather_features(cur, min(cut_date, date.today()), taw_mm=awc * 1000) if cur is not None else {}
    say("featureEngineering", {"score": scores[cutoff]["score"]})

    say("runningModel", {})
    alert = evaluate_alert(scores[cutoff]["score"], cutoff, hint_pct, warn_pct)
    say("runningModel", {"state": alert["state"]})

    ref = us_reference_bands()
    return {
        "year": year, "cutoff": cutoff, "area_m2": round(float(fy.area_m2.iloc[0])), "centroid": [round(lon, 6), round(lat, 6)],
        "satellite": {"indices": idx, "n_scenes": n_scenes, "n_clear_scenes": n_clear,
                      "n_observed_dekads": sum(v is not None for v in idx["ndvi"]),
                      "first_scene": None if not n_scenes else str(obs.date.min()),
                      "last_scene": None if not n_scenes else str(obs.date.max()),
                      "dekad_dates": [(pd.Timestamp(f"{year}-04-01") + pd.Timedelta(days=10 * i)).strftime("%Y-%m-%d") for i in range(N_DEKADS)]},
        "reference": ref,
        "scores": scores,
        "phases": phase_shortfall(idx["ndvi"]),
        "alert": alert,
        "weather": {"era5_cell": f"{lon:.1f}_{lat:.1f}", "climatology_years": [years[-1], years[1]],
                    "n_climatology_years": sum(d is not None for d in dailies[1:]),
                    "dekads": weather_dekads(cur, year) if cur is not None else {},
                    "normal": normal_dekads(dailies[1:], years[1:]), "features": {k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in wf.items()}},
        "weather_hints": weather_hints(wf),
        "soil": None if stf is None else {
            "clay_pct": round(float(stf.clay) * 100, 1), "sand_pct": round(float(stf.sand) * 100, 1), "soc": round(float(stf.soc), 2),
            "awc": round(float(stf.awc), 3), "ph": round(float(stf.phh2o) / 10, 1), "elev_m": round(float(stf.elev), 1),
            "slope_deg": round(float(stf.slope), 2), "twi": round(float(stf.twi), 2), "nccpi_corn": None},
        "model": {"name": "Stress-Score (eingefroren, freeze-at-1)", "basis": "HLS", "reference_field_years": 77,
                  "calibration": CALIBRATION},
    }


def check_us_field(fy_key: str = "BARC|BARC:EastFarm_6_60|2018") -> dict:
    """Live check (needs GEE): re-extract a known US training field on demand and compare with stored training dekads."""
    from croptransfer import gee_extract

    cfg = load_config()
    gee_extract.init_ee()
    fields = gpd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_field_years.parquet")
    fields["fy_key"] = fields.dataset + "|" + fields.field_uid + "|" + fields.year.astype(str)
    row = fields[fields.fy_key == fy_key].to_crs(4326)
    year = int(row.year.iloc[0])
    obs = gee_extract.scene_stats(row[["fy_key", "geometry"]], "HLS", f"{year}-04-01", f"{year}-11-01", cfg)
    live = dekad_rows(obs, cfg)["ndvi"]
    dek = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_dekads.parquet")
    d = dek[(dek.fy_key == fy_key) & (dek.basis == "HLS") & (dek["index"] == "ndvi") & dek.is_observed].set_index("dekad").value
    stored = [None if i not in d.index else round(float(d[i]), 4) for i in range(N_DEKADS)]
    both = [(a, b) for a, b in zip(live, stored) if a is not None and b is not None]
    return {"fy_key": fy_key, "live": live, "stored": stored, "n_both": len(both),
            "max_abs_diff": max((abs(a - b) for a, b in both), default=None),
            "only_live": sum(a is not None and b is None for a, b in zip(live, stored)),
            "only_stored": sum(a is None and b is not None for a, b in zip(live, stored))}


if __name__ == "__main__":
    print(json.dumps(check_us_field(), indent=1))
