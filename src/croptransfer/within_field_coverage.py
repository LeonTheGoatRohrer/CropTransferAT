"""Data critique of the within-field result: how much of the 'measured' yield map is far from any combine point?

The BARC yield rasters are block-kriged from cleaned combine points. Where the combine left a gap, the raster is still
filled. This re-evaluates the frozen NDVI rule (window w2) on all cells and only on cells near a cleaned point. Nothing is
tuned: same field-years, same rule, same metrics as `within_field.analysis_ab` and the 25 % map (hauptergebnis section 1).

Usage:  python -m croptransfer.within_field_coverage
Writes: results/2026-11-06_within_field_coverage/{per_field_year.csv, metrics.json}
"""

from __future__ import annotations

import json
import re
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from croptransfer import within_field as wf_mod
from croptransfer.config import load_config, repo_path

NEAR_M = (15.0, 30.0)
TOP_SHARE = 0.25


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def cleaned_point_files(year: int) -> dict[str, str]:
    """Normalised field key -> shapefile member of the cleaned maize points of one year."""
    with zipfile.ZipFile(repo_path("data/raw/barc") / f"{year}.zip") as z:
        names = [n for n in z.namelist() if "/3A--" in n and n.lower().endswith(".shp") and "corn" in n.lower()]
    out = {}
    for n in names:
        stem = n.rsplit("/", 1)[-1]
        out[_norm(re.split(r"_?(?:19|20)\d\d_", stem)[0].replace("USDA", ""))] = n
    return out


def read_points(year: int, member: str) -> np.ndarray:
    target = repo_path("data/interim/barc_cleaned") / str(year)
    stem = member[:-4]
    with zipfile.ZipFile(repo_path("data/raw/barc") / f"{year}.zip") as z:
        for ext in (".shp", ".shx", ".dbf", ".prj"):
            z.extract(stem + ext, target)
    # Coordinates are UTM 18N as stored. The CRS tags are unreliable (EastFarm_5_3A 2019 says zone 10 with zone 18 values),
    # so they are not used; a truly different system would show up as share_far = 1 in the output.
    g = gpd.read_file(target / member)
    return np.column_stack([g.geometry.x, g.geometry.y])


def map_stats(ndvi: np.ndarray, problem: np.ndarray) -> tuple[float, float, float]:
    """Mark the lowest quarter of NDVI -> precision, prevalence, recall (rule of hauptergebnis section 1)."""
    marked = ndvi <= np.quantile(ndvi, TOP_SHARE)
    hits = problem[marked].mean()
    return float(hits), float(problem.mean()), float(problem[marked].sum() / max(problem.sum(), 1))


def main() -> None:
    cfg = load_config()
    wf = wf_mod.wf_config(cfg)
    window = wf["example_window"]
    col = f"ndvi_{window}"
    df = wf_mod.load_table(wf_mod.load_pixels(cfg, wf), cfg)
    val = wf_mod.window_validity(df, wf)
    keys = val[(val.window == window) & (val["index"] == "ndvi") & val.ok].fy_key
    files = {y: cleaned_point_files(y) for y in sorted(df.year.unique())}
    rows, missing = [], []
    for key in keys:
        g = df[df.fy_key == key]
        g = g[np.isfinite(g[col])]
        year, fid = int(g.year.iloc[0]), g.field_id.iloc[0]
        k = _norm(fid)
        hit = [m for f, m in files[year].items() if f == k or k.endswith(f) or f.endswith(k)]
        if len(hit) != 1:
            missing.append({"fy_key": key, "matches": hit})
            continue
        pts = read_points(year, hit[0])
        dist, _ = cKDTree(pts).query(g[["x", "y"]].to_numpy())
        ndvi, rel, prob = g[col].to_numpy(), g.rel.to_numpy(), g.problem.to_numpy().astype(bool)
        prec, prev, rec = map_stats(ndvi, prob)
        row = {"fy_key": key, "year": year, "field_id": fid, "cells": len(g), "points": len(pts), "rho_all": wf_mod.spearman(ndvi, rel),
               "precision_all": prec, "prevalence_all": prev, "recall_all": rec, "median_dist_m": float(np.median(dist))}
        for m in NEAR_M:
            near = dist <= m
            row[f"share_far_{int(m)}"] = float((~near).mean())
            ok = near.sum() >= wf["min_pixels"]
            row[f"rho_near_{int(m)}"] = wf_mod.spearman(ndvi[near], rel[near]) if ok else np.nan
            prec_n, prev_n, rec_n = map_stats(ndvi[near], prob[near]) if ok else (np.nan, np.nan, np.nan)
            row[f"precision_near_{int(m)}"], row[f"prevalence_near_{int(m)}"], row[f"recall_near_{int(m)}"] = prec_n, prev_n, rec_n
        rows.append(row)
    t = pd.DataFrame(rows)

    def summary(col_: str) -> dict:
        v = t[col_].dropna().to_numpy()
        est, lo, hi = wf_mod.boot_median_ci(v, wf["bootstrap_n"], wf["seed"], wf["ci_level"])
        return {"median": float(est), "lo": float(lo), "hi": float(hi), "n": int(len(v)), "share_positive": float((v > 0).mean())}

    res = {"note": "descriptive data critique, nothing tuned", "n_field_years": int(len(t)), "unmatched": missing,
           "rho_all": summary("rho_all"), "rho_near_15": summary("rho_near_15"), "rho_near_30": summary("rho_near_30")}
    for suffix in ("all", "near_15", "near_30"):
        res[f"map_{suffix}"] = {k: float(t[f"{k}_{suffix}"].median()) for k in ("precision", "prevalence", "recall")}
    res["share_far_15"] = {"median": float(t.share_far_15.median()), "max": float(t.share_far_15.max()), "pooled": float(np.average(t.share_far_15, weights=t.cells))}
    res["share_far_30"] = {"median": float(t.share_far_30.median()), "max": float(t.share_far_30.max()), "pooled": float(np.average(t.share_far_30, weights=t.cells))}
    out = repo_path("results/2026-11-06_within_field_coverage")
    out.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(out / "per_field_year.csv", index=False)
    (out / "metrics.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))
    print(t.sort_values("share_far_15")[["fy_key", "cells", "points", "share_far_15", "rho_all", "rho_near_15"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
