"""Assemble the US training data from the GEE extracts (PLAN.md Phase 1.3-1.5, 1.7).

Steps
  1. scene stats -> reflectance (Landsat 5/7 harmonised to OLI) -> indices -> valid scenes
  2. Landsat 7 vs HLS harmonisation check (threshold fixed in DECISIONS.md before the check)
  3. full-season dekad composites per field-year and basis -> gt_dekads.parquet
  4. static (SoilGrids, terrain, SSURGO) per field -> gt_static.parquet
  5. as-of features per cutoff -> features_<MMDD>.parquet (one row per field-year)

Usage:  python -m croptransfer.dataset_us
"""

from __future__ import annotations

import json
from datetime import date

import geopandas as gpd
import numpy as np
import pandas as pd

from croptransfer import features, soil_ssurgo, targets, timeseries as ts
from croptransfer.config import load_config, repo_path
from croptransfer.extract_us import load_field_years, weather_points

HARMONISATION = {"bias_max": 0.03, "rmsd_max": 0.07, "indices": ["ndvi", "evi"]}


def load_obs(cfg) -> pd.DataFrame:
    files = sorted((repo_path(cfg["paths"]["interim"]) / "obs").glob("*.parquet"))
    obs = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    obs = ts.add_indices(ts.to_reflectance(obs))
    return ts.valid_obs(obs, cfg["field"]["clear_frac_min"])


def basis_obs(obs: pd.DataFrame, fy: pd.DataFrame) -> dict[str, dict[str, pd.DataFrame]]:
    """{fy_key: {'HLS': obs, 'S2': obs}}; HLS basis = HLS from 2013, harmonised L5/L7 before."""
    era = fy.set_index("fy_key")["sensor_era"]
    out: dict[str, dict[str, pd.DataFrame]] = {}
    for key, g in obs.groupby("fy_key"):
        e = era.get(key)
        hls = g[g.sensor == "HLS"] if e == "HLS" else g[g.sensor.isin(["L5", "L7"])]
        out[key] = {"HLS": hls, "S2": g[g.sensor == "S2"]}
    return out


def full_composites(by_key, fy: pd.DataFrame) -> pd.DataFrame:
    """Season-end (31.10.) dekad composites of all indices per field-year and basis."""
    rows = []
    for r in fy.itertuples():
        for basis, idxs in features.SAT_INDICES.items():
            o = by_key.get(r.fy_key, {}).get(basis)
            if o is None or o.empty:
                continue
            for idx in idxs:
                c = ts.dekad_composite(o, date(int(r.year), 10, 31), idx)
                c["fy_key"], c["basis"], c["index"] = r.fy_key, basis, idx
                rows.append(c)
    return pd.concat(rows, ignore_index=True)


def harmonisation_check(obs: pd.DataFrame, fy: pd.DataFrame) -> dict:
    """L7 vs HLS dekad medians on the same field-years 2013-2021 (KBS, BARC)."""
    keys = fy[(fy.year.between(2013, 2021)) & fy.dataset.isin(["KBS", "BARC"])].fy_key
    o = obs[obs.fy_key.isin(keys) & obs.sensor.isin(["L7", "HLS"])].copy()
    o["dk"] = ts.dekad_index(o["date"])
    res = {}
    for idx in HARMONISATION["indices"]:
        m = o.groupby(["fy_key", "dk", "sensor"])[idx].median().unstack("sensor").dropna()
        d = m["L7"] - m["HLS"]
        res[idx] = {"n_pairs": int(len(d)), "n_field_years": int(m.index.get_level_values(0).nunique()),
                    "median_diff": float(d.median()), "rmsd": float(np.sqrt((d ** 2).mean())),
                    "spearman": float(m["L7"].corr(m["HLS"], method="spearman"))}
    passed = all(abs(r["median_diff"]) <= HARMONISATION["bias_max"] and r["rmsd"] <= HARMONISATION["rmsd_max"]
                 for r in res.values())
    return {"criteria": HARMONISATION, "results": res, "passed": bool(passed)}


def static_table(cfg, fy: gpd.GeoDataFrame) -> pd.DataFrame:
    interim = repo_path(cfg["paths"]["interim"])
    st = features.static_features(pd.read_parquet(interim / "static_gee.parquet"))
    cache = interim / "ssurgo_fields.parquet"
    if cache.exists():
        ss = pd.read_parquet(cache)
    else:
        first = fy.sort_values("year").drop_duplicates("field_uid")
        rows = []
        for uid, geom in zip(first.field_uid, first.geometry):
            try:
                v, _ = soil_ssurgo.query_field(geom.wkt, cfg)
            except Exception as e:  # network errors: leave NaN, logged in the row
                v = {"error": repr(e)[:200]}
            rows.append({"field_uid": uid, **v})
        ss = pd.DataFrame(rows)
        ss.to_parquet(cache)
    ss = ss.rename(columns={"nccpi_corn": "nccpi_corn", "nonirryield_r": "ssurgo_corn_yield"})
    keep = ["field_uid"] + [c for c in ["nccpi_corn", "ssurgo_corn_yield"] if c in ss]
    return st.merge(ss[keep], on="field_uid", how="left")


def weather_by_fy(cfg, fy: gpd.GeoDataFrame) -> dict[str, pd.DataFrame]:
    wdir = repo_path(cfg["paths"]["interim"]) / "weather"
    fy = fy.assign(wpt=weather_points(fy), lat=fy.geometry.centroid.y)
    out = {}
    for yr, g in fy.groupby("year"):
        f = wdir / f"era5_{yr}.parquet"
        if not f.exists():
            continue
        w = pd.read_parquet(f)
        for pt, gg in g.groupby("wpt"):
            d = features.daily_weather(w[w.pt == pt], float(gg.lat.iloc[0]))
            for k in gg.fy_key:
                out[k] = d
    return out


def field_groups(fy: pd.DataFrame, seed: int, n_groups: int = 3) -> pd.Series:
    """LOFYO field groups (DECISIONS 2026-10-15): KBS by replicate pairs, others seeded random."""
    grp = pd.Series(-1, index=fy.index)
    kbs = fy.dataset == "KBS"
    rep = fy.loc[kbs, "field_id"].str.extract(r"R(\d)")[0].astype(int)
    grp[kbs] = (rep - 1) // 2
    rng = np.random.default_rng(seed)
    for ds in fy.loc[~kbs, "dataset"].unique():
        uids = np.array(sorted(fy.loc[fy.dataset == ds, "field_uid"].unique()))
        perm = rng.permutation(len(uids))
        gmap = {u: int(i % n_groups) for u, i in zip(uids[perm], range(len(uids)))}
        m = fy.dataset == ds
        grp[m] = fy.loc[m, "field_uid"].map(gmap)
    return grp.astype(int)


def main() -> None:
    cfg = load_config()
    proc = repo_path(cfg["paths"]["processed"])
    fy = load_field_years(cfg)
    fy["RY_descr"] = targets.ry_descriptive(fy)
    fy["field_group"] = field_groups(fy, cfg["seed"])
    obs = load_obs(cfg)
    print("valid scenes per sensor:", obs.groupby("sensor").size().to_dict(), flush=True)
    harm = harmonisation_check(obs, fy)
    (proc / "harmonisation_check.json").write_text(json.dumps(harm, indent=2))
    print("harmonisation:", json.dumps(harm["results"]), "passed:", harm["passed"], flush=True)
    by_key = basis_obs(obs, fy)
    full_composites(by_key, fy).to_parquet(proc / "gt_dekads.parquet")
    static = static_table(cfg, fy)
    static.to_parquet(proc / "gt_static.parquet")
    wx = weather_by_fy(cfg, fy)
    meta = pd.DataFrame(fy.drop(columns="geometry"))
    for mmdd in cfg["cutoffs"]["yield_model"]:
        feat = features.build_rows(fy, by_key, wx, static, mmdd)
        out = meta.merge(feat, on="fy_key", how="left")
        out.to_parquet(proc / f"features_{mmdd.replace('-', '')}.parquet")
        print(f"features {mmdd}: {out.shape}", flush=True)
    fy.to_parquet(proc / "gt_field_years.parquet")


if __name__ == "__main__":
    main()
