"""M1 Sentinel-1 radar (plan_feinjustierung F2.1, definitions in reports/feinjust_vorab.md).

Jobs (cached, skipped if present):
  fields   dataset x year (>= 2017): per scene x field median VV/VH (dB) and pixel count
           -> data/interim/obs_s1/<dataset>_<year>.parquet
  pixels   BARC yield-map pixels: window w2 temporal median of speckle-filtered VV/VH
           -> data/interim/obs_s1/pixels/<field-year>.parquet

Usage:  python -m croptransfer.extract_s1 [--only fields|pixels] [--workers 4]
"""

from __future__ import annotations

import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import numpy as np
import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path


def s1_collection(region, start: str, end: str, cfg: dict):
    """IW GRD scenes with both VV and VH in [start, end)."""
    import ee

    s = cfg["s1"]
    return (ee.ImageCollection(s["collection"]).filterBounds(region).filterDate(start, end)
            .filter(ee.Filter.eq("instrumentMode", s["instrument_mode"]))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH")))


def field_scene_stats(fields, start: str, end: str, cfg: dict, key_col: str = "fy_key") -> pd.DataFrame:
    """Per scene x field: median VV, VH (dB) and number of pixels inside the (buffered) outline."""
    import ee

    feats = [ee.Feature(ee.Geometry(g.__geo_interface__), {key_col: k})
             for k, g in zip(fields[key_col], fields.geometry)]
    fc = ee.FeatureCollection(feats)
    coll = s1_collection(fc.geometry(), start, end, cfg)
    reducer = ee.Reducer.median().combine(ee.Reducer.count(), sharedInputs=True)

    def per_image(img):
        red = img.select(["VV", "VH"]).reduceRegions(fc, reducer, scale=cfg["s1"]["scale_m"])
        return red.map(lambda f: f.set({"date": img.date().format("YYYY-MM-dd"),
                                        "img_id": img.get("system:index"),
                                        "orbit_pass": img.get("orbitProperties_pass"),
                                        "rel_orbit": img.get("relativeOrbitNumber_start"),
                                        "platform": img.get("platform_number")}))

    res = coll.map(per_image).flatten().filter(ee.Filter.gt("VV_count", 0)).getInfo()["features"]
    df = pd.DataFrame([f["properties"] for f in res])
    if df.empty:
        return df
    df = df.rename(columns={"VV_median": "vv_db", "VH_median": "vh_db", "VV_count": "n_pix"})
    return df[[key_col, "date", "img_id", "orbit_pass", "rel_orbit", "platform", "n_pix", "vv_db", "vh_db"]]


def pixel_image(region, year: int, window: tuple[str, str], cfg: dict):
    """Window composite: per scene focal mean (linear power), then temporal median -> dB bands."""
    import ee

    first, last = window
    end = (date.fromisoformat(f"{year}-{last}") + timedelta(days=1)).isoformat()
    coll = s1_collection(region, f"{year}-{first}", end, cfg)
    r = cfg["s1"]["speckle_radius_m"]

    def prep(img):
        lin = ee.Image(10).pow(img.select(["VV", "VH"]).divide(10))
        return lin.focalMean(r, "circle", "meters")

    med = coll.map(prep).median()
    vv, vh = med.select("VV"), med.select("VH")
    vh_db = vh.log10().multiply(10).rename("s1_vh_w2")
    vhvv = vh.divide(vv).log10().multiply(10).rename("s1_vhvv_w2")
    rvi = vh.multiply(4).divide(vv.add(vh)).rename("s1_rvi_w2")
    n = coll.select("VV").count().rename("s1_n_w2")
    return ee.Image.cat([vh_db, vhvv, rvi, n])


def extract_pixels(key: str, pts: pd.DataFrame, year: int, cfg: dict, window: tuple[str, str],
                   chunk: int = 2500, scale: int = 10) -> pd.DataFrame:
    """Sample the window composite at all yield-map pixel points of one field-year (EPSG:32618)."""
    import ee

    xs, ys = pts.x.to_numpy(), pts.y.to_numpy()
    region = ee.Geometry.Rectangle([float(xs.min()) - 40, float(ys.min()) - 40,
                                    float(xs.max()) + 40, float(ys.max()) + 40], "EPSG:32618", False)
    img = pixel_image(region, year, window, cfg).unmask(-9999)
    rows = []
    for s in range(0, len(pts), chunk):
        feats = [ee.Feature(ee.Geometry.Point([float(x), float(y)], "EPSG:32618"), {"pid": int(i)})
                 for i, x, y in zip(range(s, min(s + chunk, len(pts))), xs[s:s + chunk], ys[s:s + chunk])]
        out = img.sampleRegions(ee.FeatureCollection(feats), scale=scale, projection="EPSG:32618").getInfo()
        rows += [f["properties"] for f in out["features"]]
    df = pd.DataFrame(rows).replace(-9999, np.nan).sort_values("pid").reset_index(drop=True)
    assert len(df) == len(pts), f"{key}: sampled {len(df)} of {len(pts)} points"
    df["x"], df["y"] = xs[df.pid.to_numpy()], ys[df.pid.to_numpy()]
    df["fy_key"] = key
    return df


def _run(jobs, workers):
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(f, *a): name for name, f, a in jobs}
        for fut in as_completed(futs):
            try:
                print("OK", futs[fut], fut.result(), flush=True)
            except Exception as e:  # keep going; failed jobs are re-run next time
                print("FAIL", futs[fut], repr(e)[:300], flush=True)
                traceback.print_exc()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=["fields", "pixels"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    cfg = load_config()
    gee_extract.init_ee()
    out_dir = repo_path(cfg["paths"]["interim"]) / "obs_s1"
    (out_dir / "pixels").mkdir(parents=True, exist_ok=True)
    jobs = []
    if a.only in (None, "fields"):
        from croptransfer.extract_us import load_field_years

        fy = load_field_years(cfg)
        fy = fy[(fy.sensor_era == "HLS") & (fy.year >= cfg["years"]["s2"][0])]

        def job(sub, yr, out):
            df = field_scene_stats(sub, f"{yr}-04-01", f"{yr}-11-01", cfg)
            df.to_parquet(out)
            return f"{len(df)} rows"

        for (ds, yr), sub in fy.groupby(["dataset", "year"]):
            out = out_dir / f"{ds}_{yr}.parquet"
            if not out.exists():
                jobs.append((out.name, job, (sub, int(yr), out)))
    if a.only in (None, "pixels"):
        from croptransfer import within_field as wfm

        wf = wfm.wf_config(cfg)
        px = wfm.load_pixels(cfg, wf)
        window = tuple(wf["windows"][cfg["feinjust"]["within_window"]])

        def pjob(key, g, yr, out):
            df = extract_pixels(key, g, yr, cfg, window, wf["chunk_points"], wf["sample_scale_m"])
            df.to_parquet(out)
            return f"{len(df)} px"

        for key, g in px.groupby("fy_key"):
            out = out_dir / "pixels" / f"{wfm.safe_name(key)}.parquet"
            if not out.exists():
                jobs.append((out.name, pjob, (key, g.sort_values(["y", "x"]).reset_index(drop=True),
                                              int(g.year.iloc[0]), out)))
    print(f"{len(jobs)} jobs", flush=True)
    _run(jobs, a.workers)


if __name__ == "__main__":
    main()
