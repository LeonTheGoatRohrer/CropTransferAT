"""Fourth Austria test: field-level maize yields 2026 of the hail insurer (protocol `reports/freeze_protocol_at4.md`, tag freeze-at-4).

First test *between fields within one year*: does the frozen stress score (freeze-at-1, unchanged) rank the
grain-maize Feldstuecke of 2026 like their harvested yield? The yield file gives the total kg per Feldstueck
(despite its header "kg/ha"); dividing by the polygon area gives kg/ha.

Usage:  python -m croptransfer.at_test4 --fields    (cleaning + parcel geometry; no satellite value read)
        python -m croptransfer.at_test4 --extract   (HLS scene statistics per 20-km cell, cached; no yield read)
        python -m croptransfer.at_test4             (scores + evaluation, only after freeze-at-4)
"""

from __future__ import annotations

import argparse
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from croptransfer import at_extract, at_test, evaluate, gee_extract, invekos
from croptransfer.config import load_config, repo_path


# ------------------------------------------------------------------------------------------ yields
def read_raw(path) -> pd.DataFrame:
    """Excel columns by position: field_id, total yield (kg per Feldstueck), harvest moisture (fraction)."""
    d = pd.read_excel(path)
    d = d.iloc[:, :3].copy()
    d.columns = ["field_id", "total_kg", "moisture"]
    d["total_kg"] = pd.to_numeric(d.total_kg, errors="coerce")
    d["moisture"] = pd.to_numeric(d.moisture, errors="coerce")
    return d


def clean(raw: pd.DataFrame, area_ha: pd.Series, share_code: pd.Series, cell: pd.Series, t4: dict) -> pd.DataFrame:
    """Apply the protocol rules in order; every row keeps the first rule that dropped it (`drop`, '' = kept)."""
    d = raw.drop_duplicates().copy()                                   # exact repeats count once
    d["drop"] = ""
    conflict = d.field_id.duplicated(keep=False)
    d.loc[conflict, "drop"] = "conflicting_duplicate"
    d["cell"] = d.field_id.map(cell)
    shared = d.total_kg.notna() & d.duplicated(["total_kg", "cell"], keep=False) & (d["drop"] == "")
    d.loc[shared, "drop"] = "same_total_nearby"                        # split farm totals, not a field yield
    d["area_ha"] = d.field_id.map(area_ha)
    d["share_code"] = d.field_id.map(share_code).fillna(0.0)
    d["y_t_ha"] = d.total_kg / d.area_ha / 1000.0
    lo, hi = t4["plausible_t_ha"]
    for rule, bad in [("no_polygon", d.area_ha.isna()),
                      ("not_grain_maize", d.share_code < t4["min_share_code"]),
                      ("area_below_min", d.area_ha < t4["min_area_ha"]),
                      ("no_yield", d.total_kg.isna()),
                      ("implausible_yield", ~d.y_t_ha.between(lo, hi))]:
        d.loc[bad & (d["drop"] == ""), "drop"] = rule
    mlo, mhi = t4["moisture_range"]
    ok = d.moisture.between(mlo, mhi)
    d["y14_t_ha"] = np.where(ok, d.y_t_ha * (1 - d.moisture) / 0.86, np.nan)
    return d.reset_index(drop=True)


def share_of_code(polys: gpd.GeoDataFrame, invekos_path, code: str) -> pd.Series:
    """Share of each Feldstueck area covered by INVEKOS Schlaege of `code` (EPSG:31287)."""
    p = polys.to_crs(31287)
    s = pyogrio.read_dataframe(invekos_path, mask=p.geometry.buffer(5).union_all(),
                               columns=[invekos.CROP_CODE_COL]).set_crs(31287, allow_override=True)
    s = s[s[invekos.CROP_CODE_COL] == code]
    x = gpd.overlay(p[["field_id", "geometry"]], s, how="intersection", keep_geom_type=True)
    covered = x.assign(a=x.area).groupby("field_id").a.sum()
    return (covered / p.set_index("field_id").area).reindex(p.field_id).fillna(0.0)


def cell_id(geom: gpd.GeoSeries, km: float) -> pd.Series:
    """Grid cell of each centroid in EPSG:31287, e.g. '57_33'."""
    c = geom.to_crs(31287).centroid
    return (c.x // (km * 1000)).astype(int).astype(str) + "_" + (c.y // (km * 1000)).astype(int).astype(str)


def build_fields(cfg) -> pd.DataFrame:
    """Cleaned yield table (written to work_dir) and the buffered parcels of the kept fields (fields.parquet)."""
    t4 = cfg["at_test4"]
    out = repo_path(t4["work_dir"])
    (out / "obs").mkdir(parents=True, exist_ok=True)
    raw = read_raw(repo_path(t4["yields"]))
    polys = gpd.read_file(repo_path(t4["polygons"]))
    polys = polys[polys.field_id.isin(raw.field_id)]
    area = polys.set_index("field_id").area / 1e4
    share = share_of_code(polys, repo_path(t4["invekos"]), t4["invekos_code"])
    g = polys.set_index("field_id").geometry
    d = clean(raw, area, share, cell_id(g, t4["cluster_km"]), t4)
    d["cell_within"] = d.field_id.map(cell_id(g, t4["within_cell_km"]))
    d["fy_key"] = "AT4|" + str(t4["year"]) + "|" + d.field_id.astype(str)
    d.to_csv(out / "yields_clean.csv", index=False)
    extract_rows = d["drop"].isin(["", "implausible_yield"])         # also the implausible ones, for the sensitivity
    keep = polys[polys.field_id.isin(d.loc[extract_rows, "field_id"])].copy()
    keep["fy_key"] = "AT4|" + str(t4["year"]) + "|" + keep.field_id.astype(str)
    keep["cell"] = keep.field_id.map(d.set_index("field_id").cell)
    keep = keep.assign(geometry=keep.geometry.buffer(cfg["field"]["inner_buffer_m"]))
    keep = keep[~keep.geometry.is_empty & keep.geometry.notna()]
    keep.to_crs(4326)[["fy_key", "field_id", "cell", "geometry"]].to_parquet(out / "fields.parquet")
    return d


def extract(cfg) -> None:
    """HLS 1 April - 1 November per 10-km cell (cached), via the frozen `at_extract._stats`."""
    t4 = cfg["at_test4"]
    out = repo_path(t4["work_dir"])
    fields = gpd.read_parquet(out / "fields.parquet")
    gee_extract.init_ee()
    for cell, f in fields.groupby("cell"):
        path = out / "obs" / f"cell_{cell}_HLS.parquet"
        if not path.exists():
            at_extract._stats(cfg, f, t4["year"]).to_parquet(path)
            print("extracted", path.name, len(f), flush=True)


# ------------------------------------------------------------------------------------------ metrics
def rho_diff_ci(a, b, y, clusters, n_boot: int, seed: int) -> dict:
    """rho(a,y) - rho(b,y) with a paired cluster bootstrap (same resampled clusters for both)."""
    a, b, y, cl = (np.asarray(v) for v in (a, b, y, clusters))
    ok = np.isfinite(a.astype(float)) & np.isfinite(b.astype(float)) & np.isfinite(y.astype(float))
    a, b, y, cl = a[ok], b[ok], y[ok], cl[ok]
    point = evaluate._spearman(a, y) - evaluate._spearman(b, y)
    groups = [np.flatnonzero(cl == c) for c in np.unique(cl)]
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        idx = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        diffs.append(evaluate._spearman(a[idx], y[idx]) - evaluate._spearman(b[idx], y[idx]))
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"n": int(ok.sum()), "diff": float(point), "lo": float(lo), "hi": float(hi)}


def problem_overlap(score, y, share: float) -> dict:
    """Of the fields with the lowest `share` of scores, how many are also in the lowest `share` of yields?"""
    s, y = pd.Series(score, dtype=float), pd.Series(y, dtype=float)
    ok = s.notna() & y.notna()
    s, y = s[ok], y[ok]
    low_s = s <= s.quantile(share)
    low_y = y <= y.quantile(share)
    return {"n": int(ok.sum()), "flagged": int(low_s.sum()), "hit_rate": float(low_y[low_s].mean()), "chance": share}


def evaluate_fields(df: pd.DataFrame, cfg, target: str = "y_t_ha") -> dict:
    """Protocol section 3 on one field table (score_*, ndvi_base, target, cell, cell_within)."""
    atc, t4 = cfg["at_test"], cfg["at_test4"]
    res: dict = {"target": target, "cutoffs": {}}
    for c in atc["cutoffs"]:
        m = at_test.rho_ci(df[f"score_{c}"], df[target], df.cell, cfg)
        m["verdict"] = at_test.passed(m, t4["min_fields"])
        r = {"stress_score": m,
             "within_cell": at_test.descriptive_within(df, f"score_{c}", target, "cell_within", t4["min_fields_cell"])}
        if c == atc["primary_cutoff"]:
            r["ndvi_baseline"] = at_test.rho_ci(df.ndvi_base, df[target], df.cell, cfg)
            r["ndvi_within_cell"] = at_test.descriptive_within(df, "ndvi_base", target, "cell_within", t4["min_fields_cell"])
            r["score_minus_ndvi"] = rho_diff_ci(df[f"score_{c}"], df.ndvi_base, df[target], df.cell,
                                                cfg["validation"]["bootstrap_n"], cfg["seed"])
            r["problem_fields"] = problem_overlap(df[f"score_{c}"], df[target], t4["problem_share"])
            q = pd.qcut(df[f"score_{c}"], 5, labels=False, duplicates="drop")
            r["yield_by_score_quintile"] = df.groupby(q)[target].agg(["mean", "size"]).round(3).to_dict("index")
        res["cutoffs"][c] = r
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fields", action="store_true")
    ap.add_argument("--extract", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    t4 = cfg["at_test4"]
    if a.fields:
        d = build_fields(cfg)
        print(d["drop"].replace("", "kept").value_counts().to_string())
        return
    if a.extract:
        extract(cfg)
        return
    out = repo_path(t4["results_dir"])
    out.mkdir(parents=True, exist_ok=True)
    work = repo_path(t4["work_dir"])
    fields = at_test.field_table(cfg, t4["work_dir"])
    fields.to_parquet(work / "field_scores.parquet")
    y = pd.read_csv(work / "yields_clean.csv")
    df = y[y["drop"] == ""].merge(fields, on="fy_key", how="left")
    df.to_parquet(work / "evaluation_table.parquet")                  # field-level, stays outside the repo
    res = {"protocol": "reports/freeze_protocol_at4.md", "tag": "freeze-at-4",
           "drops": y["drop"].replace("", "kept").value_counts().to_dict(),
           "kept": int(len(df)), "scored_primary": int(df[f"score_{cfg['at_test']['primary_cutoff']}"].notna().sum()),
           "primary": evaluate_fields(df, cfg),
           "sens_moisture_14": evaluate_fields(df, cfg, "y14_t_ha"),
           "sens_no_abrupt_drop": evaluate_fields(df[df.abrupt_drop != True], cfg)}   # noqa: E712 (NaN stays in)
    allp = y[y["drop"].isin(["", "implausible_yield"])].merge(fields, on="fy_key", how="left")
    res["sens_without_plausibility_filter"] = evaluate_fields(allp, cfg)
    (out / "metrics.json").write_text(json.dumps(res, indent=2, default=float, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
