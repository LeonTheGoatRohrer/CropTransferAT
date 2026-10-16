"""ERA5-Land daily weather per 0.1-degree cell and harvest year for all multi-crop site-years (W3.2).

Window: 1 Aug of the year before .. 1 Nov of the harvest year (covers winter crops). Point = cell centre.
Cached: data/interim/weather_multi/era5_<year>.parquet (column ``pt`` = cell_id). Requests are chunked so that
points x days stays below the Earth Engine getInfo limit (5000 elements).

Usage:  python -m croptransfer.weather_multi [--workers 3]
"""

from __future__ import annotations

import argparse
import math
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path
from croptransfer.groundtruth_multi import CELL_DEG

MAX_ELEMENTS = 4500


def cell_centre(cell_id: str) -> tuple[float, float]:
    """(lon, lat) of the centre of a ``<lat_idx>_<lon_idx>`` cell."""
    la, lo = (int(x) for x in cell_id.split("_"))
    return round((lo + 0.5) * CELL_DEG, 4), round((la + 0.5) * CELL_DEG, 4)


def chunks(keys: list[str], n_days: int) -> list[list[str]]:
    """Split keys so that len(chunk) * n_days <= MAX_ELEMENTS (at least one key per chunk)."""
    n = max(1, MAX_ELEMENTS // n_days)
    return [keys[i:i + n] for i in range(0, len(keys), n)]


def _job(cfg, year, keys, start, end):
    pts = {k: cell_centre(k) for k in keys}
    return gee_extract.era5_daily(pts, start, end, cfg)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    cfg = load_config()
    gee_extract.init_ee()
    gt = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_site_years.parquet")
    out_dir = repo_path(cfg["paths"]["interim"]) / "weather_multi"
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = {}
    for yr, g in gt.groupby("year"):
        out = out_dir / f"era5_{int(yr)}.parquet"
        if out.exists():
            continue
        start, end = f"{int(yr) - 1}-08-01", f"{int(yr)}-11-01"
        n_days = (pd.Timestamp(end) - pd.Timestamp(start)).days
        plan[int(yr)] = (out, [(c, start, end) for c in chunks(sorted(g.cell_id.unique()), n_days)])
    print({y: len(v[1]) for y, v in plan.items()}, flush=True)
    results: dict[int, list[pd.DataFrame]] = {y: [] for y in plan}
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(_job, cfg, y, keys, s, e): y for y, (_, items) in plan.items() for keys, s, e in items}
        for fut in as_completed(futs):
            y = futs[fut]
            if results[y] is None:
                continue
            try:
                results[y].append(fut.result())
            except Exception as e:  # year stays uncached and is re-run next time
                print("FAIL", y, repr(e)[:200], flush=True)
                traceback.print_exc()
                results[y] = None
    for y, (out, items) in plan.items():
        parts = results[y]
        if parts is not None and len(parts) == len(items):
            pd.concat(parts, ignore_index=True).to_parquet(out)
            print("OK", out.name, flush=True)


if __name__ == "__main__":
    main()
