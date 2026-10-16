"""GEE scene extraction for the multi-crop S2 points (plan_mehrkultur.md W3.2, D4).

Evaluation area = circle of ``radius_m`` (30 m, D4) around the trial coordinate; only label tier S2
(coordinate <= 100 m). HLS from 2013, Sentinel-2 from 2017. Winter crops start in the autumn before the
harvest year (config ``crops``). Results are cached per dataset x year x sensor x chunk and skipped if present:
  data/interim/obs_multi/<dataset>_<year>_<sensor>_<chunk>.parquet

AUSTRIA RULE: Austrian rows cannot be in gt_site_years (see groundtruth_multi); asserted here again.
Usage:  python -m croptransfer.extract_multi [--sample] [--workers 4]
"""

from __future__ import annotations

import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import geopandas as gpd
import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path
from croptransfer.crops import get_crop

RADIUS_M = 30.0          # D4
CHUNK = 12               # fields per GEE request (keeps results < getInfo limit, bounds compact)
S2_FIRST_YEAR, HLS_FIRST_YEAR = 2017, 2013


def point_key(df: pd.DataFrame) -> pd.Series:
    """Unique key per site-year row: dataset|crop|variant|site|year."""
    return (df.dataset + "|" + df.crop + "|" + df.crop_variant.astype(str) + "|" + df.site.astype(str)
            + "|" + df.year.astype(int).astype(str))


def circles(df: pd.DataFrame, radius_m: float = RADIUS_M) -> gpd.GeoDataFrame:
    """30 m circles around the coordinates (buffer in UTM-free metric CRS EPSG:3035 for Europe/US alike)."""
    g = gpd.GeoDataFrame(df.copy(), geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
    # equal-area metric CRS; the 30 m buffer is accurate to a few per cent, enough for a sampling circle
    g["geometry"] = g.to_crs("EPSG:6933").buffer(radius_m).to_crs("EPSG:4326")
    return g


def load_points(cfg) -> gpd.GeoDataFrame:
    d = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_site_years.parquet")
    assert not (d.country == "Austria").any(), "Austrian rows are not allowed before the freeze"
    d = d[d.tier == "S2"].copy()
    d["fy_key"] = point_key(d)
    return circles(d)


def window(crop: str, year: int) -> tuple[str, str]:
    """Satellite window: season start (autumn before for winter crops) .. 1.11. (winter crops: 1.9.)."""
    spec = get_crop(crop)
    end = f"{year}-09-01" if spec.winter else f"{year}-11-01"
    return spec.season_start(year).isoformat(), end


def sensors_for(year: int) -> list[str]:
    return (["HLS"] if year >= HLS_FIRST_YEAR else []) + (["S2"] if year >= S2_FIRST_YEAR else [])


def _job(cfg, sub, sensor, start, end, out):
    df = gee_extract.scene_stats(sub, sensor, start, end, cfg)
    if df.empty:
        df = pd.DataFrame(columns=["fy_key", "date", "sensor"])
    df.to_parquet(out)
    return f"{out.name}: {len(df)} rows"


def build_jobs(pts: gpd.GeoDataFrame, out_dir, sample: bool):
    jobs = []
    for (ds, crop, variant, yr), g in pts.groupby(["dataset", "crop", "crop_variant", "year"]):
        start, end = window(crop, int(yr))
        g = g.assign(_o=list(zip(g.lat.round(1), g.lon.round(1)))).sort_values("_o")
        for ci in range(0, len(g), CHUNK):
            sub = g.iloc[ci:ci + CHUNK]
            for s in sensors_for(int(yr)):
                out = out_dir / f"{ds}_{crop}_{variant}_{int(yr)}_{s}_{ci // CHUNK:02d}.parquet"
                if not out.exists():
                    jobs.append((out.name, (None, sub, s, start, end, out)))
    if sample:
        jobs = jobs[:2]
    return jobs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", action="store_true", help="two jobs only")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    cfg = load_config()
    gee_extract.init_ee()
    out_dir = repo_path(cfg["paths"]["interim"]) / "obs_multi"
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = build_jobs(load_points(cfg), out_dir, args.sample)
    print(f"{len(jobs)} jobs", flush=True)
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(_job, cfg, *a[1][1:]): a[0] for a in jobs}
        for fut in as_completed(futs):
            try:
                print("OK", fut.result(), flush=True)
            except Exception as e:  # failed jobs are re-run on the next call
                print("FAIL", futs[fut], repr(e)[:300], flush=True)
                traceback.print_exc()


if __name__ == "__main__":
    main()
