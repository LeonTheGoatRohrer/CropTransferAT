"""M2 surface temperature and evapotranspiration (plan_feinjustierung F2.2/F2.5, reports/feinjust_vorab.md).

Jobs (cached, skipped if present), all US field-years of the HLS era from 2017:
  lst     Landsat 8/9 C2 L2 ST_B10 per scene x field (median over clear pixels, clear/total counts)
          -> data/interim/obs_lst/<dataset>_<year>.parquet
  modis   MOD16A2GF ET and PET (8-day) at the field centroid
          -> data/interim/obs_et/modis_<dataset>_<year>.parquet
  era5    ERA5-Land daily total and potential evaporation at the weather points
          -> data/interim/obs_et/era5_<year>.parquet

Usage:  python -m croptransfer.extract_lst [--only lst|modis|era5] [--workers 4]
"""

from __future__ import annotations

import argparse

import pandas as pd

from croptransfer import gee_extract
from croptransfer.config import load_config, repo_path
from croptransfer.extract_s1 import _run


def lst_scene_stats(fields, start: str, end: str, cfg: dict, key_col: str = "fy_key") -> pd.DataFrame:
    """Per Landsat 8/9 scene x field: median surface temperature (K) of clear pixels, n_clear, n_total."""
    import ee

    c = cfg["lst"]
    feats = [ee.Feature(ee.Geometry(g.__geo_interface__), {key_col: k})
             for k, g in zip(fields[key_col], fields.geometry)]
    fc = ee.FeatureCollection(feats)
    reducer = ee.Reducer.median().combine(ee.Reducer.count(), sharedInputs=True)
    rows = []
    for coll_id in c["collections"]:
        coll = ee.ImageCollection(coll_id).filterBounds(fc.geometry()).filterDate(start, end)

        def per_image(img):
            st = img.select("ST_B10").multiply(c["scale"]).add(c["offset_k"]).rename("lst")
            clear = gee_extract._bits_clear(img.select("QA_PIXEL"), gee_extract.LANDSAT_QA_BITS)
            tot = img.select("ST_B10").mask().gt(0).rename("tot").selfMask()
            data = st.updateMask(clear).addBands(tot)
            red = data.reduceRegions(fc, reducer, scale=30)
            return red.map(lambda f: f.set({"date": img.date().format("YYYY-MM-dd"),
                                            "img_id": img.get("system:index"),
                                            "spacecraft": img.get("SPACECRAFT_ID")}))

        res = coll.map(per_image).flatten().filter(ee.Filter.gt("tot_count", 0)).getInfo()["features"]
        rows += [f["properties"] for f in res]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.rename(columns={"lst_median": "lst_k", "lst_count": "n_clear", "tot_count": "n_total"})
    return df[[key_col, "date", "img_id", "spacecraft", "n_total", "n_clear", "lst_k"]]


def modis_et(points: dict[str, tuple[float, float]], start: str, end: str, cfg: dict) -> pd.DataFrame:
    """MOD16A2GF ET and PET (kg/m2 per composite, scaled) at points; date = composite start."""
    import ee

    c = cfg["et"]
    coll = ee.ImageCollection(c["modis"]).filterDate(start, end).select(["ET", "PET"])
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(list(xy)), {"fy_key": k}) for k, xy in points.items()])

    def per_image(img):
        vals = img.multiply(c["modis_scale"]).reduceRegions(fc, ee.Reducer.first(), scale=c["modis_scale_m"])
        return vals.map(lambda f: f.set("date", img.date().format("YYYY-MM-dd")))

    res = coll.map(per_image).flatten().getInfo()["features"]
    return pd.DataFrame([f["properties"] for f in res])


def era5_evap(points: dict[str, tuple[float, float]], start: str, end: str, cfg: dict) -> pd.DataFrame:
    """ERA5-Land daily total and potential evaporation (m water, negative = evaporation) at points."""
    import ee

    coll = ee.ImageCollection(cfg["gee"]["collections"]["era5_land_daily"]).filterDate(start, end)
    coll = coll.select(["total_evaporation_sum", "potential_evaporation_sum"], ["evap_m", "pev_m"])
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(list(xy)), {"pt": k}) for k, xy in points.items()])

    def per_image(img):
        vals = img.reduceRegions(fc, ee.Reducer.first(), scale=11132)
        return vals.map(lambda f: f.set("date", img.date().format("YYYY-MM-dd")))

    return pd.DataFrame([f["properties"] for f in coll.map(per_image).flatten().getInfo()["features"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=["lst", "modis", "era5"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    cfg = load_config()
    gee_extract.init_ee()
    from croptransfer.extract_us import load_field_years, weather_points

    fy = load_field_years(cfg)
    fy = fy[(fy.sensor_era == "HLS") & (fy.year >= cfg["years"]["s2"][0])].copy()
    interim = repo_path(cfg["paths"]["interim"])
    (interim / "obs_lst").mkdir(parents=True, exist_ok=True)
    (interim / "obs_et").mkdir(parents=True, exist_ok=True)
    jobs = []

    def save(fn, out, *args):
        df = fn(*args)
        df.to_parquet(out)
        return f"{len(df)} rows"

    for (ds, yr), sub in fy.groupby(["dataset", "year"]):
        yr = int(yr)
        out = interim / "obs_lst" / f"{ds}_{yr}.parquet"
        if a.only in (None, "lst") and not out.exists():
            jobs.append((out.name, save, (lst_scene_stats, out, sub, f"{yr}-04-01", f"{yr}-11-01", cfg)))
        out = interim / "obs_et" / f"modis_{ds}_{yr}.parquet"
        if a.only in (None, "modis") and not out.exists():
            c = sub.geometry.centroid
            pts = {k: (float(x), float(y)) for k, x, y in zip(sub.fy_key, c.x, c.y)}
            jobs.append((out.name, save, (modis_et, out, pts, f"{yr}-04-01", f"{yr}-11-01", cfg)))
    if a.only in (None, "era5"):
        fy["wpt"] = weather_points(fy)
        c = fy.geometry.centroid
        pts = {k: (float(x), float(y)) for k, x, y in zip(fy.wpt, c.x.round(1), c.y.round(1))}
        for yr in sorted(fy.year.unique()):
            out = interim / "obs_et" / f"era5_{int(yr)}.parquet"
            if not out.exists():
                jobs.append((out.name, save, (era5_evap, out, pts, f"{yr}-04-01", f"{yr}-11-01", cfg)))
    print(f"{len(jobs)} jobs", flush=True)
    _run(jobs, a.workers)


if __name__ == "__main__":
    main()
