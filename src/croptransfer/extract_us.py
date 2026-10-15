"""Batch GEE extraction for the US ground-truth field-years (PLAN.md Phase 1.3-1.5).

Jobs (one GEE request each, results cached under data/interim/ and skipped if present):
  scenes   dataset x year x sensor  -> data/interim/obs/<dataset>_<year>_<sensor>.parquet
           HLS (>= 2013), S2 (>= 2017), L5 (<= 2011), L7 (1999-2021: pre-2013 data and
           the harmonisation check against HLS)
  weather  year (all points)        -> data/interim/weather/era5_<year>.parquet
  static   all fields               -> data/interim/static_gee.parquet

Usage:  python -m croptransfer.extract_us [--sample] [--workers 4] [--only scenes|weather|static]
"""

from __future__ import annotations

import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import geopandas as gpd
import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path


def load_field_years(cfg) -> gpd.GeoDataFrame:
    fy = gpd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_field_years.parquet")
    fy["fy_key"] = fy.dataset + "|" + fy.field_uid + "|" + fy.year.astype(str)
    return fy


def sensors_for(dataset: str, year: int) -> list[str]:
    out = []
    if year >= 2013:
        out.append("HLS")
    if year >= 2017:
        out.append("S2")
    if year <= 2011:
        out.append("L5")
    if 1999 <= year <= 2021 and dataset in ("KBS", "BARC"):
        out.append("L7")
    return out


def weather_points(fy: gpd.GeoDataFrame) -> pd.Series:
    """Weather point key per field-year: field centroid snapped to the 0.1 deg ERA5-Land grid."""
    c = fy.geometry.centroid
    return (c.x.round(1).astype(str) + "_" + c.y.round(1).astype(str))


def _scene_job(cfg, fy, dataset, year, sensor, out):
    sub = fy[(fy.dataset == dataset) & (fy.year == year)]
    df = gee_extract.scene_stats(sub, sensor, f"{year}-04-01", f"{year}-11-01", cfg)
    df.to_parquet(out)
    return f"{out.name}: {len(df)} rows"


def _weather_job(cfg, pts, year, out):
    df = gee_extract.era5_daily(pts, f"{year}-03-01", f"{year}-11-01", cfg)
    df.to_parquet(out)
    return f"{out.name}: {len(df)} rows"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", action="store_true", help="one site-year per sensor only")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", choices=["scenes", "weather", "static"], default=None)
    args = ap.parse_args()
    cfg = load_config()
    gee_extract.init_ee()
    fy = load_field_years(cfg)
    interim = repo_path(cfg["paths"]["interim"])
    (interim / "obs").mkdir(parents=True, exist_ok=True)
    (interim / "weather").mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.only in (None, "scenes"):
        for (ds, yr) in sorted(fy.groupby(["dataset", "year"]).groups):
            for s in sensors_for(ds, yr):
                out = interim / "obs" / f"{ds}_{yr}_{s}.parquet"
                if not out.exists():
                    jobs.append((_scene_job, (cfg, fy, ds, yr, s, out)))
        if args.sample:
            want = {("KBS", 2020, "HLS"), ("KBS", 2020, "S2"), ("KBS", 2008, "L5"), ("KBS", 2020, "L7")}
            jobs = [j for j in jobs if (j[1][2], j[1][3], j[1][4]) in want]
    if args.only in (None, "weather") and not args.sample:
        fy["wpt"] = weather_points(fy)
        c = fy.geometry.centroid
        pts = {k: (float(x), float(y)) for k, x, y in zip(fy.wpt, c.x.round(1), c.y.round(1))}
        for yr in sorted(fy.year.unique()):
            out = interim / "weather" / f"era5_{yr}.parquet"
            if not out.exists():
                jobs.append((_weather_job, (cfg, pts, int(yr), out)))
    if args.only in (None, "static") and not args.sample:
        out = interim / "static_gee.parquet"
        if not out.exists():
            first = fy.sort_values("year").drop_duplicates("field_uid")
            gee_extract.static_stats(first, cfg).to_parquet(out)
            print(f"static: {len(first)} fields", flush=True)
    print(f"{len(jobs)} jobs", flush=True)
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(f, *a): a for f, a in jobs}
        for fut in as_completed(futs):
            try:
                print("OK", fut.result(), flush=True)
            except Exception as e:  # keep going; failed jobs are re-run next time
                print("FAIL", futs[fut][2:5] if len(futs[fut]) > 4 else futs[fut][2], repr(e)[:300], flush=True)
                traceback.print_exc()


if __name__ == "__main__":
    main()
