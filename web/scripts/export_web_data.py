"""Export compact JSON for the web frontend (run: python web/scripts/export_web_data.py).

Reads only US data (BARC, KBS, Colorado), the non-Austrian within-field sites (Kayad, Colorado)
and committed results/ folders. No Austrian raw or processed data file is opened (PLAN.md §0,
AGENTS.md §3.4); the only Austrian content is the aggregated result of the frozen, already
evaluated test (results/2026-10-17_at_test, results/2026-10-17_at_retrain).
Writes web/public/data/{fields,evidence,explorer}.json. Every number shown on the website as a
"real result" comes from these files; demo/simulated values live in web/src/data/demo/.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from croptransfer.features import daily_weather  # noqa: E402
from croptransfer.innerfeld_features import window_median  # noqa: E402
from croptransfer.innerfeld_run import B0_DEKADS  # noqa: E402
from croptransfer import feinjust, splits, stress, targets  # noqa: E402
from croptransfer.config import load_config  # noqa: E402
from croptransfer.fj_product import PHASES  # noqa: E402
from croptransfer.run_phase2 import eval_mask  # noqa: E402

APP = ROOT / "data" / "app"
PROC = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
RES = ROOT / "results"
OUT = ROOT / "web" / "public" / "data"

PROBLEM_REL = 0.85  # pixel yield < 85 % of field mean = problem zone (hauptergebnis.md)
WEAK_QUANTILE = 0.25  # lowest NDVI quarter = flagged zone (fj_product within-field map)
CLEAR_FRAC_MIN = 0.7  # config.yaml field.clear_frac_min
SEASON_START = "04-01"
N_DEKADS = 21

# Prepared demo fields: real held-out field-years from the training sites (display texts in German).
# Chosen 2026-10-18 among the 89 out-of-fold field-years for dense Sentinel-2 coverage (>= 7 of the 9
# June-August dekads observed) and long yield records; one per outcome type, including a false alarm
# and a miss. `place` is neutral and shown before the analysis; `title`/`blurb` describe the outcome
# and are shown only afterwards.
_BARC = "Beltsville, Maryland (USA)"
_KBS = "Kellogg Biological Station, Michigan (USA)"
DEMO_FIELDS = [
    {"id": "barc-2020", "fy_key": "BARC|BARC:EastFarm_5_3A|2020", "role": "healthy", "place": _BARC,
     "label": "Feld A", "title": "Starke Saison",
     "blurb": "Früh grün und im Juni und Juli über der gesunden Referenz; geerntet wurden 19 % mehr als üblich. Kein Alarm – zu Recht."},
    {"id": "kbs-t1-2020", "fy_key": "KBS|KBS:T1R1|2020", "role": "stressed", "place": _KBS,
     "label": "Feld B", "title": "Stress den ganzen Sommer, erkannt",
     "blurb": "Konventionelle Parzelle. Die Kurve bleibt von Juni bis August unter der Referenz; geerntet wurde gut die Hälfte des üblichen Ertrags. Der Alarm schlägt an."},
    {"id": "kbs-t2-2020", "fy_key": "KBS|KBS:T2R4|2020", "role": "average", "place": _KBS,
     "label": "Feld C", "title": "Normale Saison",
     "blurb": "Direktsaat-Parzelle. Die Kurve liegt fast genau auf der gesunden Referenz, der Ertrag entspricht dem üblichen. Kein Alarm."},
    {"id": "barc-2017-alarm", "fy_key": "BARC|BARC:EastFarm_5_3B|2017", "role": "stressed", "place": _BARC,
     "label": "Feld D", "title": "Später Aufwuchs, knapp Alarm",
     "blurb": "Wird erst Anfang Juli richtig grün und liegt im Juli deutlich unter der Referenz; Ertrag rund ein Viertel unter dem üblichen. Das Risiko liegt knapp über der Alarmschwelle."},
    {"id": "barc-2017-miss", "fy_key": "BARC|BARC:EastFarm_5_3C|2017", "role": "missed", "place": _BARC,
     "label": "Feld E", "title": "Gleiches Muster, knapp übersehen",
     "blurb": "Nachbarfeld von Feld D mit fast derselben Kurve und ähnlichem Ertragsverlust. Das Risiko liegt knapp unter der Schwelle, deshalb kein Alarm – die Grenze ist hart."},
    {"id": "kbs-t4-2020", "fy_key": "KBS|KBS:T4R4|2020", "role": "edge", "place": _KBS,
     "label": "Feld F", "title": "Fehlalarm",
     "blurb": "Bio-Parzelle: Im Mai steht noch die Zwischenfrucht (hoher NDVI), der Mais wird spät gesät und liegt von Juni bis August unter der Referenz. Als auffällig markiert, aber mit überdurchschnittlichem Ertrag geerntet."},
]


def r(x, nd=3):
    """Round for JSON; NaN/inf -> None."""
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return x
    return None if not math.isfinite(f) else round(f, nd)


def ci(d: dict, v="value", lo="lo", hi="hi", nd=3) -> dict:
    return {"value": r(d.get(v), nd), "lo": r(d.get(lo), nd), "hi": r(d.get(hi), nd)}


def dekad_dates(year: int) -> list[str]:
    start = pd.Timestamp(f"{year}-{SEASON_START}")
    return [(start + pd.Timedelta(days=10 * i)).strftime("%Y-%m-%d") for i in range(N_DEKADS)]


# ---------------------------------------------------------------- weather
def weather_for(lon: float, lat: float, year: int) -> dict:
    """Dekad weather for one field-year plus long-term mean of all other years at the same ERA5 cell."""
    files = sorted((INTERIM / "weather").glob("era5_*.parquet"))
    frames = [pd.read_parquet(f) for f in files]
    w = pd.concat(frames, ignore_index=True)
    pts = w["pt"].unique()
    coords = np.array([[float(p.split("_")[0]), float(p.split("_")[1])] for p in pts])
    pt = pts[int(np.argmin(np.hypot(coords[:, 0] - lon, coords[:, 1] - lat)))]
    w = w[w["pt"] == pt]
    d = daily_weather(w, lat)
    d["year"] = d.date.dt.year
    start = pd.to_datetime(d.year.astype(str) + "-" + SEASON_START)
    d["dekad"] = ((d.date - start).dt.days // 10).astype(int)
    d = d[d.dekad.between(0, N_DEKADS - 1)]
    agg = d.groupby(["year", "dekad"]).agg(tmean=("tmean", "mean"), tmax=("tmax", "mean"),
                                           prec=("prec", "sum"), gdd=("gdd", "sum"),
                                           heat=("tmax", lambda s: int((s > 32).sum())),
                                           swvl=("swvl2", "mean"), vpd=("vpd", "mean")).reset_index()
    cur = agg[agg.year == year].set_index("dekad").reindex(range(N_DEKADS))
    clim = agg[agg.year != year].groupby("dekad").mean(numeric_only=True).reindex(range(N_DEKADS))
    years = sorted(int(y) for y in agg.year.unique() if y != year)

    def col(df, c, nd=1):
        return [r(v, nd) for v in df[c].to_numpy()]

    return {
        "era5_cell": pt,
        "climatology_years": [years[0], years[-1]] if years else None,
        "n_climatology_years": len(years),
        "dekads": {k: col(cur, k, 2 if k in ("swvl", "vpd") else 1) for k in ["tmean", "tmax", "prec", "gdd", "heat", "swvl", "vpd"]},
        "normal": {k: col(clim, k, 2 if k in ("swvl", "vpd") else 1) for k in ["tmean", "tmax", "prec", "gdd", "swvl", "vpd"]},
    }


# ---------------------------------------------------------------- fields
def utm_area(geom) -> float:
    s = gpd.GeoSeries([geom], crs=4326)
    return float(s.to_crs(s.estimate_utm_crs()).area.iloc[0])


def pixel_grid(fy_key: str) -> dict | None:
    """10-m cells of a within-field field-year: NDVI window w2 (16.7.-15.8.), measured relative yield,
    and the per-dekad NDVI for the season animation."""
    fi = pd.read_parquet(PROC / "features_innerfeld.parquet")
    c = fi[fi.fy_key == fy_key]
    if c.empty:
        return None
    site, fid, year = fy_key.split("|")[0], fy_key.split("|")[1].split(":", 1)[1], fy_key.split("|")[2]
    pfile = INTERIM / "pixels_dekad" / f"{site}_{site}_{fid}_{year}.parquet"
    dek = pd.read_parquet(pfile) if pfile.exists() else None
    if dek is None:
        return None
    # B0 = untrained calendar-window rule of the pre-registered round (median NDVI of dekads 10-13).
    m = c[["x", "y"]].merge(dek, on=["x", "y"], how="left")
    nd_cols = [f"ndvi_d{i:02d}" for i in range(N_DEKADS)]
    ndvi = window_median(m[nd_cols].to_numpy(float), *B0_DEKADS)
    tr = Transformer.from_crs(c.crs.iloc[0], 4326, always_xy=True)
    lon, lat = tr.transform(c.x.to_numpy(), c.y.to_numpy())
    rel = c.rel.to_numpy()
    ok = np.isfinite(ndvi)
    thr = float(np.nanquantile(ndvi, WEAK_QUANTILE))
    weak = ok & (ndvi <= thr)
    problem = rel < PROBLEM_REL
    rho = float(pd.Series(ndvi[ok]).rank().corr(pd.Series(rel[ok]).rank()))
    prec = float(problem[weak].mean()) if weak.any() else float("nan")
    prev = float(problem[ok].mean())
    xs, ys = c.x.to_numpy(), c.y.to_numpy()
    gx = np.round((xs - xs.min()) / 10).astype(int)
    gy = np.round((ys.max() - ys) / 10).astype(int)
    series = [[r(v, 3) for v in m[col].to_numpy()] for col in nd_cols]
    return {
        "n_cells": int(len(c)),
        "cell_m": 10,
        "window": "Median-NDVI der Dekaden 10. Jul – 18. Aug (Sentinel-2, Regel B0)",
        "weak_threshold": r(thr),
        "rho": r(rho),
        "precision_weak": r(prec),
        "prevalence_problem": r(prev),
        "lift": r(prec / prev) if prev > 0 else None,
        "recall_weak": r(float(weak[problem & ok].mean())) if (problem & ok).any() else None,
        "grid": {"w": int(gx.max()) + 1, "h": int(gy.max()) + 1},
        "cells": [[r(a, 6), r(b, 6), int(i), int(j), r(n, 3), r(y, 3)]
                  for a, b, i, j, n, y in zip(lon, lat, gx, gy, ndvi, rel)],
        "cell_fields": ["lon", "lat", "gx", "gy", "ndvi", "rel_yield"],
        "ndvi_by_dekad": series,
    }


def phase_parts(keys: set[str]) -> dict[str, dict]:
    """Per month: NDVI below (<= 0) and above (>= 0) the fold reference, summed over observed dekads.

    Same folds, healthy reference and dekad windows as fj_product.explanations; the `below` part is
    exactly the value in ranking.csv (checked in build_fields), `above` is the part the score ignores.
    """
    cfg = load_config()
    fj = cfg["feinjust"]
    df = feinjust.load_features(cfg, fj["cutoff"])
    dek = pd.read_parquet(PROC / "gt_dekads.parquet")
    dek = dek[(dek["index"] == "ndvi") & (dek.basis == fj["basis"])]
    k = stress.last_complete_dekad(fj["cutoff"])
    out = {}
    for _, tr, te in splits.lofyo(df, eval_mask(df, fj["basis"])):
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        ry_tr = ry_tr.dropna()
        test_keys = [df.loc[i, "fy_key"] for i in ry_te.index[ry_te.notna()] if df.loc[i, "fy_key"] in keys]
        if not test_keys:
            continue
        healthy = df.loc[ry_tr.index[(ry_tr >= feinjust.HEALTHY) & (df.loc[ry_tr.index, "sensor_era"] == "HLS")], "fy_key"]
        ref = stress.reference_curve(dek, healthy, basis=fj["basis"])
        for key in test_keys:
            d = dek[(dek.fy_key == key) & dek.is_observed & dek.dekad.between(6, k)]
            dev = d.value.to_numpy() - ref.reindex(d.dekad).to_numpy()
            parts = {}
            for name, (a, b) in PHASES.items():
                m = d.dekad.between(a, b).to_numpy()
                parts[name] = {"below": r(np.nansum(np.minimum(dev[m], 0))), "above": r(np.nansum(np.maximum(dev[m], 0)))}
            out[key] = parts
    return out


def build_fields() -> dict:
    fields = gpd.read_parquet(APP / "fields.parquet")
    dek = pd.read_parquet(APP / "dekads.parquet")
    ref = pd.read_parquet(APP / "reference.parquet")
    static = pd.read_parquet(PROC / "gt_static.parquet").set_index("field_uid")
    ranking = pd.read_csv(RES / "2026-10-16_feinjust_ablation" / "ranking.csv").set_index("fy_key")
    oof = pd.read_parquet(RES / "2026-10-16_feinjust_ablation" / "oof.parquet")
    score = oof[oof.model == "A_roh"].set_index("fy_key")["score"]
    product = json.loads((RES / "2026-10-16_feinjust_ablation" / "product.json").read_text(encoding="utf-8"))
    gt = pd.read_parquet(PROC / "gt_field_years.parquet", columns=["field_uid", "year", "Y_t_ha"])

    def ref_band(index: str) -> dict:
        b = ref[(ref.basis == "S2") & (ref["index"] == index)].set_index("dekad").reindex(range(N_DEKADS))
        return {k: [r(v) for v in b[k].to_numpy()] for k in ["p25", "median", "p75"]} | {
            "n_fieldyears": int(ref.n_fieldyears.iloc[0])}

    parts = phase_parts({spec["fy_key"] for spec in DEMO_FIELDS})
    out = []
    for spec in DEMO_FIELDS:
        key = spec["fy_key"]
        row = fields[fields.fy_key == key].iloc[0]
        geom = row.geometry
        c = geom.centroid
        year = int(row.year)
        d = dek[(dek.fy_key == key) & (dek.basis == "S2")]
        idx = {}
        for name in ["ndvi", "evi", "ndmi", "ndre", "gndvi"]:
            s = d[(d["index"] == name)].set_index("dekad")
            if s.empty:
                continue
            s = s.reindex(range(N_DEKADS))
            idx[name] = [r(v) if obs else None for v, obs in zip(s.value.to_numpy(), s.is_observed.fillna(False).to_numpy())]
        obs = pd.read_parquet(INTERIM / "obs" / f"{row.dataset}_{year}_S2.parquet")
        obs = obs[obs.fy_key == key]
        clear = obs[(obs.n_clear / obs.n_total) >= CLEAR_FRAC_MIN]
        rk = ranking.loc[key] if key in ranking.index else None
        st = static.loc[row.field_uid] if row.field_uid in static.index else None
        soil = None
        if st is not None:
            soil = {"clay_pct": r(st.clay * 100 if st.clay < 1 else st.clay, 1),
                    "sand_pct": r(st.sand * 100 if st.sand < 1 else st.sand, 1),
                    "soc": r(st.soc, 2), "awc": r(st.awc, 3), "ph": r(st.phh2o / 10, 1),
                    "elev_m": r(st.elev, 1), "slope_deg": r(st.slope, 2), "twi": r(st.twi, 2),
                    "nccpi_corn": r(st.nccpi_corn, 2)}
        out.append({
            **{k: v for k, v in spec.items()},
            "site": row.dataset, "field_id": row.field_id, "year": year,
            "treatment": None if pd.isna(row.treatment) else row.treatment,
            "geometry": json.loads(gpd.GeoSeries([geom]).to_json())["features"][0]["geometry"],
            "centroid": [r(c.x, 6), r(c.y, 6)],
            "area_m2": round(utm_area(geom)),
            "measured": {"yield_t_ha": r(row.Y_t_ha, 2),
                         "relative_yield": r(rk.ry if rk is not None else row.RY_descr, 2),
                         "at_risk": bool(rk.risk) if rk is not None else (bool(row.RY_descr < 0.85) if pd.notna(row.RY_descr) else None)},
            "satellite": {"dekad_dates": dekad_dates(year), "indices": idx,
                          "n_scenes": int(len(obs)), "n_clear_scenes": int(len(clear)),
                          "n_observed_dekads": int(sum(v is not None for v in idx.get("ndvi", []))),
                          "first_scene": obs.date.min() if len(obs) else None,
                          "last_scene": obs.date.max() if len(obs) else None},
            "reference": {"ndvi": ref_band("ndvi"), "evi": ref_band("evi"), "ndmi": ref_band("ndmi")},
            "stress": None if rk is None else {
                "score": r(score.get(key), 4), "risk_p": r(rk.p), "alarm": bool(rk.alarm),
                "threshold": r(product["alarm_threshold_oof"]),
                "phases": {"Jun": r(rk.Juni), "Jul": r(rk.Juli), "Aug": r(rk.August)},
                # below/above the fold reference per month; below == phases (asserted below)
                "phase_parts": {m: parts[key][de] for m, de in [("Jun", "Juni"), ("Jul", "Juli"), ("Aug", "August")]},
                "main_phase": None if pd.isna(rk.main_phase) else str(rk.main_phase),  # German month name, shown as is
                "rank_in_site_year": None if pd.isna(rk.rank_in_site_year) else int(rk.rank_in_site_year),
                "fold": None if pd.isna(rk.fold) else str(rk.fold)},
            "weather": weather_for(c.x, c.y, year),
            "soil": soil,
            # measured maize yields of the same field/plot in all years (rotation years without maize are absent)
            "history": [{"year": int(h.year), "yield_t_ha": r(h.Y_t_ha, 2)}
                        for h in gt[gt.field_uid == row.field_uid].sort_values("year").itertuples()],
            "pixels": pixel_grid(key),
        })
        st_ = out[-1]["stress"]
        if st_:
            for m in ["Jun", "Jul", "Aug"]:
                assert abs((st_["phase_parts"][m]["below"] or 0) - (st_["phases"][m] or 0)) <= 1.5e-3, (key, m)  # rounding only
        print(f"field {spec['id']}: area {out[-1]['area_m2']} m2, scenes {len(obs)}/{len(clear)}, "
              f"pixels {out[-1]['pixels']['n_cells'] if out[-1]['pixels'] else 0}")
    return {"fields": out, "dekad_count": N_DEKADS, "season_start": SEASON_START}


# ---------------------------------------------------------------- evidence
def build_evidence() -> dict:
    ev: dict = {}

    # Within-field map (BARC, Phase 2.3) + multi-site round (innerfeld).
    wf = json.loads((RES / "2026-10-16_within_field" / "metrics.json").read_text(encoding="utf-8"))
    ivr = wf["index_vs_rel_yield"]
    ev["within_field_indices"] = [{"index": k, **{kk: r(vv) for kk, vv in v.items() if not isinstance(vv, (list, dict))}}
                                  for k, v in ivr.items()]
    inf = json.loads((RES / "2026-10-17_innerfeld" / "metrics.json").read_text(encoding="utf-8"))
    ev["innerfeld_main"] = json.loads(json.dumps(inf["main"], default=float))
    ev["innerfeld_gates"] = {k: {"n_fy": v["n_fy"], "delta": r(v["delta_median"]), "ci": [r(x) for x in v["delta_ci"]]}
                             for k, v in inf["gates"].items()}
    ev["innerfeld_label_shuffle"] = {k: ({kk: r(vv) for kk, vv in v.items() if kk != "values"} if isinstance(v, dict) else r(v))
                                     for k, v in inf["label_shuffle"].items()}
    per = pd.read_csv(RES / "2026-10-17_innerfeld" / "per_fy.csv")
    p0 = per[(per.subset == "main") & (per.scheme.isin(["untrained", "E"]))]
    ev["innerfeld_per_fy"] = [{"model": a.model, "scheme": a.scheme, "site": a.site, "year": int(a.year),
                               "fy_key": a.fy_key, "rho": r(a.rho), "lift": r(a.lift), "n": int(a.n)}
                              for a in p0.itertuples()]
    prod = json.loads((RES / "2026-10-16_feinjust_ablation" / "product.json").read_text(encoding="utf-8"))
    ev["within_field_map"] = {k: r(v) for k, v in prod["within_field_map"].items() if k != "examples"}
    ceil = json.loads((RES / "2026-10-17_innerfeld_ceiling" / "metrics.json").read_text(encoding="utf-8"))
    ev["ceiling_raw"] = json.loads(json.dumps(ceil, default=float))

    # Field-level stress score (feinjustierung ablation, Phase 3).
    fm = json.loads((RES / "2026-10-16_feinjust_ablation" / "metrics.json").read_text(encoding="utf-8"))
    ev["stress_models"] = {k: {kk: r(vv) for kk, vv in v.items() if not isinstance(vv, dict)} for k, v in fm["A"].items()}
    sens = json.loads((RES / "2026-10-16_feinjust_ablation" / "sensitivity_T4.json").read_text(encoding="utf-8"))
    ev["stress_sensitivity"] = {k: ({kk: r(vv) for kk, vv in v.items() if kk != "values"} if isinstance(v, dict) else r(v))
                                for k, v in sens.items()}
    abl = pd.read_csv(RES / "2026-10-16_feinjust_ablation" / "metrics.csv")
    ev["ablation"] = [{k: (r(v) if not isinstance(v, (bool, np.bool_, str)) else (bool(v) if not isinstance(v, str) else v))
                       for k, v in row.items()} for row in abl.to_dict("records")]
    ev["alarm"] = {k: r(v) for k, v in prod.items() if not isinstance(v, (dict, list)) and k != "main_model"} | {
        "main_model": prod["main_model"], "main_phase_alarms": prod["main_phase_alarms"],
        "main_phase_at_risk": prod["main_phase_at_risk"],
        "phase_sum_mean": {("at_risk" if "nicht" not in k else "not_at_risk"): v for k, v in prod["phase_sum_mean"].items()}}
    rk = pd.read_csv(RES / "2026-10-16_feinjust_ablation" / "ranking.csv")
    oof = pd.read_parquet(RES / "2026-10-16_feinjust_ablation" / "oof.parquet")
    sc = oof[oof.model == "A_roh"][["fy_key", "score"]]
    rk = rk.drop(columns=["score"]).merge(sc, on="fy_key", how="left")
    fields = pd.read_parquet(APP / "fields.parquet")[["fy_key", "treatment"]]
    rk = rk.merge(fields, on="fy_key", how="left")
    ev["field_years"] = [{"fy_key": a.fy_key, "site": a.dataset, "year": int(a.year), "score": r(a.score, 4),
                          "ry": r(a.ry), "p": r(a.p), "alarm": bool(a.alarm), "risk": bool(a.risk),
                          "treatment": None if pd.isna(a.treatment) else a.treatment}
                         for a in rk.itertuples()]
    p3 = json.loads((RES / "2026-10-16_round3" / "phase3.json").read_text(encoding="utf-8"))
    ev["early_warning_field"] = [
        {"cutoff": c, **{m: {k: r(v.get(k)) for k in ["pr_auc", "pr_auc_lo", "pr_auc_hi", "prevalence", "n"]}
                         for m, v in d.items() if isinstance(v, dict)}}
        for c, d in p3["per_cutoff"].items()]

    # Phase 2 model family at 1.9. (LOFYO), Phase 4 stages.
    m2 = pd.read_csv(RES / "2026-10-16_phase2" / "metrics.csv", dtype={"cutoff": str})
    m2 = m2[(m2.variant == "main")]
    ev["phase2_models"] = [{k: (r(v) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, (np.integer,)) else v))
                            for k, v in row.items()} for row in m2.to_dict("records")]
    stages = []
    for d, label, crit in [("2026-10-16_phase2", "Phase 2 · Basismodelle", "criteria_main.json"),
                           ("2026-10-16_round1", "Runde 1 · relative Merkmale", "criteria.json"),
                           ("2026-10-16_round2", "Runde 2 · weniger Merkmale", "criteria.json"),
                           ("2026-10-16_round3", "Runde 3 · stärkere Regularisierung", "criteria.json")]:
        c = json.loads((RES / d / crit).read_text(encoding="utf-8"))
        s = c["selected"]
        stages.append({"stage": label, "model": s["model"], "kind": s["kind"], "basis": s["basis"],
                       "n": s["n"], "clusters": s.get("clusters"), "rho": r(s["rho"]), "rho_lo": r(s["rho_lo"]),
                       "rho_hi": r(s["rho_hi"]), "skill_b0": r(s.get("skill_b0")),
                       "criteria": {k: bool(v.get("passed")) for k, v in sorted(c["criteria"].items())},
                       "strong_enough": bool(c.get("strong_enough", False))})
    ev["phase4_stages"] = stages

    # EU regional model (Phase 5, CY-Bench, frozen).
    eu = json.loads((RES / "2026-10-16_cybench_eu" / "metrics.json").read_text(encoding="utf-8"))
    cut = []
    for c, d in eu["cutoffs"].items():
        p = d["pooled"]
        cut.append({"cutoff": c, "n": d["n_region_years"], "countries": d["n_countries"],
                    "spearman": ci(p["model_spearman"]), "r2": ci(p["model_r2"]),
                    "rmse": ci(p["model_rmse"]), "mae": ci(p["model_mae"]),
                    "skill_vs_normal": ci(p["skill_vs_yas1"]),
                    "within_year": {"value": r(d["within_year"]["mean_rho"]), "lo": r(d["within_year"]["lo"]),
                                    "hi": r(d["within_year"]["hi"])},
                    "baselines": {"normal_year": {"rmse": ci(p["yas1_rmse"]), "mae": ci(p["yas1_mae"]), "r2": ci(p["yas1_r2"])},
                                  "trend": {"rmse": ci(p["trend_rmse"]), "mae": ci(p["trend_mae"]), "r2": ci(p["trend_r2"]),
                                            "spearman": ci(p["trend_spearman"])}},
                    "yearly_mean_spearman": r(d["yearly_mean"]["spearman"]),
                    "n_features": d.get("n_features")})
    ev["eu_cutoffs"] = cut
    last = eu["cutoffs"]["09-01"]
    ev["eu_per_country"] = {k: json.loads(json.dumps(v, default=float)) for k, v in last["per_country"].items()}
    ev["eu_controls"] = {k: json.loads(json.dumps(last[k], default=float))
                         for k in ["without_DE_eval", "label_shuffle", "country_balanced", "variants", "macro_over_countries"]
                         if k in last}
    pr = pd.read_parquet(RES / "2026-10-16_cybench_eu" / "predictions_loco.parquet")
    pr = pr[pr.cutoff == "09-01"].copy()
    pr["err_model"] = pr.pred - pr.yas
    pr["err_normal"] = pr.yas1 - pr.yas
    sample = pr.sample(n=min(1600, len(pr)), random_state=42)
    ev["eu_scatter"] = [[r(a, 3), r(b, 3), c] for a, b, c in zip(sample.yas, sample.pred, sample.country)]
    edges = np.linspace(-1.0, 1.0, 41)
    ev["eu_residuals"] = {"edges": [r(e, 2) for e in edges],
                          "model": np.histogram(pr.err_model.clip(-1, 1), edges)[0].tolist(),
                          "normal_year": np.histogram(pr.err_normal.clip(-1, 1), edges)[0].tolist()}
    by_year = pr.groupby("year").apply(lambda g: pd.Series({
        "n": len(g), "mae_model": g.err_model.abs().mean(), "mae_normal": g.err_normal.abs().mean(),
        "mean_yas": g.yas.mean(), "mean_pred": g.pred.mean()}), include_groups=False).reset_index()
    ev["eu_by_year"] = [{k: (int(v) if k in ("year", "n") else r(v)) for k, v in row.items()} for row in by_year.to_dict("records")]
    bins = [0, 0.7, 0.85, 0.95, 1.05, 1.15, 10]
    labels = ["< 0,70", "0,70–0,85", "0,85–0,95", "0,95–1,05", "1,05–1,15", "> 1,15"]  # display labels, decimal comma
    pr["bin"] = pd.cut(pr.yas, bins, labels=labels)
    by_bin = pr.groupby("bin", observed=False).apply(lambda g: pd.Series({
        "n": len(g), "mae_model": g.err_model.abs().mean(), "mae_normal": g.err_normal.abs().mean(),
        "bias_model": g.err_model.mean()}), include_groups=False).reset_index()
    ev["eu_by_range"] = [{"bin": str(row["bin"]), **{k: (int(v) if k == "n" else r(v)) for k, v in row.items() if k != "bin"}}
                         for row in by_bin.to_dict("records")]
    ev["eu_meta"] = {"commit": eu["meta"]["git"]["commit"][:7], "freeze": "freeze-cybench-1",
                     "n_features_by_cutoff": eu["meta"]["n_features_by_cutoff"]}

    # Secondary target: absolute yield (t/ha) from satellite, LOFYO 1.9.
    my = pd.read_csv(RES / "2026-10-16_phase2_Y" / "metrics.csv", dtype={"cutoff": str})
    ev["absolute_yield"] = [{k: (r(v) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, np.integer) else v))
                             for k, v in row.items()} for row in my.to_dict("records")]
    # Austria test (exploratory, freeze-at-1) - aggregated metrics only, written after the freeze.
    at = RES / "2026-10-17_at_test" / "metrics.json"
    if at.exists():
        m = json.loads(at.read_text(encoding="utf-8"))
        ev["austria"] = {"tag": m.get("tag"), "counts": m.get("counts"), "cutoffs": m["cutoffs"]}
        rt = RES / "2026-10-17_at_retrain" / "metrics.json"
        if rt.exists():
            ev["austria"]["retrain"] = json.loads(rt.read_text(encoding="utf-8")).get("cutoffs")
    p1 = json.loads((RES / "2026-10-16_phase1" / "metrics.json").read_text(encoding="utf-8"))
    ev["phase1_raw"] = json.loads(json.dumps(p1, default=float))
    return ev


# ---------------------------------------------------------------- explorer
def build_explorer() -> dict:
    gt = gpd.read_parquet(PROC / "gt_field_years.parquet")
    f = pd.read_parquet(PROC / "features_0901.parquet")
    dek = pd.read_parquet(PROC / "gt_dekads.parquet")
    nd = dek[(dek["index"] == "ndvi") & dek.is_observed]
    peak = nd.groupby("fy_key").value.max().rename("ndvi_peak")
    jul = nd[nd.dekad.between(9, 14)].groupby("fy_key").value.mean().rename("ndvi_jul_aug")
    nobs = nd.groupby("fy_key").dekad.nunique().rename("n_obs_dekads")
    keep = [c for c in ["fy_key", "gdd", "prec", "heat32", "tmax_jun", "vpd_jun", "prec_30d", "clay", "soc", "awc"] if c in f.columns]
    df = gt.drop(columns="geometry").merge(f[keep], on="fy_key", how="left", suffixes=("", "_f"))
    df = df.merge(peak, on="fy_key", how="left").merge(jul, on="fy_key", how="left").merge(nobs, on="fy_key", how="left")
    cols = ["fy_key", "dataset", "year", "treatment", "sensor_era", "Y_t_ha", "RY_descr", "area_ha",
            "ndvi_peak", "ndvi_jul_aug", "n_obs_dekads"] + [c for c in keep if c != "fy_key"]
    cols = [c for c in cols if c in df.columns]
    rows = []
    for row in df[cols].to_dict("records"):
        rows.append({k: (r(v) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, np.integer) else
                         (None if v is None or (isinstance(v, float) and math.isnan(v)) else v))) for k, v in row.items()})
    counts = {"field_years": int(len(df)), "by_site": df.dataset.value_counts().to_dict(),
              "years": [int(df.year.min()), int(df.year.max())],
              "with_relative_yield": int(df.RY_descr.notna().sum())}
    return {"rows": rows, "columns": cols, "counts": counts}


def clean(x):
    """Recursively replace NaN/inf by None so the output is strict JSON."""
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("fields", build_fields), ("evidence", build_evidence), ("explorer", build_explorer)]:
        data = clean(fn())
        p = OUT / f"{name}.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str, allow_nan=False), encoding="utf-8")
        print(f"{p.relative_to(ROOT)}: {p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
