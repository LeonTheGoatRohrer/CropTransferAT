"""Sentinel-2 dekad composites per yield cell for the multi-site within-field study (plan_innerfeld.md, I2).

Why dekads and not the fixed windows of Phase 2.3: the planned peak-window feature (B1) and the three-window
model (M1) are defined relative to the field's NDVI maximum, so the whole season has to be available. For every
cell and every 10-day period from 1 April (dekad 0) to 27 October (dekad 20) we store the median NDVI / NDRE of
all clear observations (Cloud Score+ cs_cdf >= config) and the number of clear observations. Terrain bands
(Copernicus DEM) are added for the control model M2. Cells are sampled at the cell centre (cell centres lie on
the Sentinel-2 10 m grid for Kayad; BARC blocks are offset by 2.5 m and take the pixel under the centre).

Usage:  python -m croptransfer.innerfeld_extract [--sites KAYAD COLORADO BARC] [--workers 4] [--refresh]
Writes: data/interim/pixels_dekad/<field-year>.parquet  (one file per field-year, rows sorted by (y, x))
"""

from __future__ import annotations

import argparse
import time
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path
from croptransfer.within_field import safe_name

SEASON_START = "04-01"        # dekad 0 starts here; 21 dekads end on 27 Oct (28 Oct exclusive)
N_DEKADS = 21
INDICES = ("ndvi", "ndre")
CHUNK_POINTS = 2500
SAMPLE_SCALE_M = 10
TPI_RADIUS_M = 150


def dekad_bounds(year: int, k: int) -> tuple[str, str]:
    """[start, end) of dekad k in `year` (end exclusive). Dekad 20 ends on 28 Oct (21 dekads = 210 days)."""
    start = date.fromisoformat(f"{year}-{SEASON_START}") + timedelta(days=10 * k)
    end = start + timedelta(days=10)
    return start.isoformat(), end.isoformat()


def dekad_of(day: date) -> int:
    """Dekad index of a calendar day in its own year (may be outside 0..N_DEKADS-1)."""
    return (day - date.fromisoformat(f"{day.year}-{SEASON_START}")).days // 10


def dekad_image(region, year: int, cfg: dict[str, Any]):
    """Image with ndvi_dXX, ndre_dXX, n_dXX for all dekads plus terrain bands."""
    import ee

    g = cfg["gee"]
    start, end = dekad_bounds(year, 0)[0], dekad_bounds(year, N_DEKADS - 1)[1]
    coll = ee.ImageCollection(g["collections"]["s2_sr"]).filterBounds(region).filterDate(start, end)
    cs = ee.ImageCollection(g["collections"]["s2_cloudscore"]).filterBounds(region).filterDate(start, end)
    coll = coll.linkCollection(cs, [g["s2_cloudscore_band"]])

    def prep(img):
        clear = img.select(g["s2_cloudscore_band"]).gte(g["s2_cloudscore_min"])
        valid = clear.And(img.select("B8A").gt(0))
        ndvi = img.normalizedDifference(["B8A", "B4"]).rename("ndvi")
        ndre = img.normalizedDifference(["B8A", "B5"]).rename("ndre")
        # normalizedDifference drops the time stamp, which the per-dekad filterDate below needs
        return ndvi.addBands(ndre).updateMask(valid).copyProperties(img, ["system:time_start"])

    coll = coll.map(prep)
    bands = []
    for k in range(N_DEKADS):
        s, e = dekad_bounds(year, k)
        c = coll.filterDate(s, e)
        for idx in INDICES:
            bands.append(c.select(idx).median().rename(f"{idx}_d{k:02d}"))
        bands.append(c.select("ndvi").count().rename(f"n_d{k:02d}"))
    dem_coll = ee.ImageCollection(g["collections"]["dem"]).select("DEM")
    dem = dem_coll.mosaic().setDefaultProjection(dem_coll.first().projection()).rename("elev")
    slope = ee.Terrain.slope(dem).rename("slope")
    tpi = dem.subtract(dem.focalMean(TPI_RADIUS_M, "circle", "meters")).rename("tpi")
    return ee.Image.cat(bands + [dem, slope, tpi])


def extract_field_year(key: str, pts: pd.DataFrame, year: int, crs: str, cfg: dict[str, Any]) -> pd.DataFrame:
    """Sample all cells of one field-year; returns (pid, x, y, fy_key, bands) with NaN for no clear observation."""
    import ee

    xs, ys = pts.x.to_numpy(float), pts.y.to_numpy(float)
    region = ee.Geometry.Rectangle([xs.min() - 20, ys.min() - 20, xs.max() + 20, ys.max() + 20], crs, False)
    img = dekad_image(region, year, cfg).unmask(-9999)
    rows = []
    for s in range(0, len(pts), CHUNK_POINTS):
        idx = range(s, min(s + CHUNK_POINTS, len(pts)))
        feats = [ee.Feature(ee.Geometry.Point([float(xs[i]), float(ys[i])], crs), {"pid": int(i)}) for i in idx]
        out = img.sampleRegions(ee.FeatureCollection(feats), scale=SAMPLE_SCALE_M, projection=crs).getInfo()
        rows += [f["properties"] for f in out["features"]]
    df = pd.DataFrame(rows).replace(-9999, np.nan).sort_values("pid").reset_index(drop=True)
    assert len(df) == len(pts), f"{key}: sampled {len(df)} of {len(pts)} points"
    df["x"], df["y"], df["fy_key"] = xs[df.pid.to_numpy()], ys[df.pid.to_numpy()], key
    return df


def extract_all(gt: pd.DataFrame, cfg: dict[str, Any], workers: int = 4, refresh: bool = False) -> None:
    from concurrent.futures import ThreadPoolExecutor

    from croptransfer import gee_extract

    cache = repo_path(cfg["paths"]["interim"]) / "pixels_dekad"
    cache.mkdir(parents=True, exist_ok=True)
    log = cache / "_errors.log"
    gee_extract.init_ee()
    todo = []
    for key, g in gt.groupby("fy_key"):
        if refresh or not (cache / f"{safe_name(key)}.parquet").exists():
            todo.append((key, g.sort_values(["y", "x"]).reset_index(drop=True), int(g.year.iloc[0]), g.crs.iloc[0]))
    print(f"extraction: {len(todo)} of {gt.fy_key.nunique()} field-years to fetch", flush=True)

    def work(item):
        key, g, yr, crs = item
        t0 = time.time()
        df = extract_field_year(key, g, yr, crs, cfg)
        df.to_parquet(cache / f"{safe_name(key)}.parquet")
        return key, len(df), time.time() - t0

    def attempt(item, retries: int = 2):
        for k in range(retries + 1):
            try:
                return work(item), None
            except Exception as e:   # noqa: BLE001 - log and continue
                err = f"{type(e).__name__}: {e}"
                if "concurrent" in err.lower() or "too many" in err.lower():
                    return None, "retry_serial"
                if k == retries:
                    with open(log, "a", encoding="utf-8") as f:
                        f.write(f"{date.today()} {item[0]}: {err[:500]}\n")
                    return None, err
                time.sleep(5 * (k + 1))
        return None, "unreachable"

    serial = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for item, (res, err) in zip(todo, ex.map(attempt, todo)):
            if err == "retry_serial":
                serial.append(item)
            elif err:
                print(f"  FAILED {item[0]}: {err[:120]}", flush=True)
            else:
                print(f"  ok {res[0]} n={res[1]} {res[2]:.0f}s", flush=True)
    for item in serial:
        res, err = attempt(item)
        print(f"  serial {item[0]}: {'ok' if res else 'FAILED ' + str(err)[:120]}", flush=True)
    missing = [k for k, *_ in todo if not (cache / f"{safe_name(k)}.parquet").exists()]
    if missing:
        print(f"WARNING: {len(missing)} field-years without cache (see {log})", flush=True)


def load_dekads(gt: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Join cached dekad samples onto the gt table (field-years without cache are dropped)."""
    cache = repo_path(cfg["paths"]["interim"]) / "pixels_dekad"
    parts = []
    for key, g in gt.groupby("fy_key"):
        f = cache / f"{safe_name(key)}.parquet"
        if not f.exists():
            continue
        s = pd.read_parquet(f).drop(columns=["fy_key"])
        g = g.sort_values(["y", "x"]).reset_index(drop=True)
        assert len(s) == len(g) and np.allclose(s.x, g.x) and np.allclose(s.y, g.y), key
        parts.append(pd.concat([g, s.drop(columns=["x", "y", "pid"])], axis=1))
    return pd.concat(parts, ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sites", nargs="+", default=["KAYAD", "COLORADO", "BARC"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    gt = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_pixels.parquet")
    gt = gt[gt.site.isin(args.sites)]
    extract_all(gt, cfg, workers=args.workers, refresh=args.refresh)


if __name__ == "__main__":
    main()
