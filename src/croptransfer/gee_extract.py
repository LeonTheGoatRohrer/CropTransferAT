"""Google Earth Engine access and extraction.

Phase 0 only contains initialisation and the access test (scene counts over
reference sites). Extraction functions follow in Phase 1.

Usage:  python -m croptransfer.gee_extract --access-test
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from croptransfer.config import load_config


def _use_system_certificates() -> None:
    """Verify TLS against the OS certificate store (needed behind TLS-inspecting
    antivirus/proxies, where Python's bundled certifi store fails)."""
    try:
        import truststore
    except ImportError:
        return
    truststore.inject_into_ssl()


def init_ee(project: str | None = None) -> str:
    """Initialise Earth Engine; project from argument, env var EE_PROJECT or config."""
    import ee

    _use_system_certificates()
    project = project or os.environ.get("EE_PROJECT") or load_config()["gee"]["project"]
    if not project:
        raise RuntimeError(
            "No Earth Engine project set: fill gee.project in config.yaml or set EE_PROJECT."
        )
    ee.Initialize(project=project)
    return project


def utm_zone(lon: float) -> int:
    """UTM zone number (1..60) of a longitude."""
    return min(int((lon + 180) // 6) + 1, 60)


def antimeridian_tile_prefixes(lon: float) -> list[str]:
    """HLS tile-id prefixes to drop for a site at `lon`.

    HLS granules in GEE whose MGRS tile lies in UTM zone 01 or 60 have broken
    (dateline-wrapping) footprints that intersect every point on Earth, so
    `filterBounds` wrongly returns them (found in the Phase-0 access test).
    They are dropped unless the site itself lies in one of these zones.
    """
    return [p for zone, p in ((1, "T01"), (60, "T60")) if utm_zone(lon) != zone]


def hls_collection(collection_id: str, lon: float, lat: float, start: str, end: str):
    """HLS (or other) collection at a point in [start, end), minus antimeridian artefacts."""
    import ee

    point = ee.Geometry.Point([lon, lat])
    coll = ee.ImageCollection(collection_id).filterBounds(point).filterDate(start, end)
    for prefix in antimeridian_tile_prefixes(lon):
        coll = coll.filter(ee.Filter.stringStartsWith("system:index", prefix).Not())
    return coll


def count_scenes(collection_id: str, lon: float, lat: float, start: str, end: str,
                 drop_antimeridian: bool = True) -> int:
    """Number of images of a collection intersecting a point in [start, end)."""
    import ee

    if drop_antimeridian:
        coll = hls_collection(collection_id, lon, lat, start, end)
    else:
        point = ee.Geometry.Point([lon, lat])
        coll = ee.ImageCollection(collection_id).filterBounds(point).filterDate(start, end)
    return int(coll.size().getInfo())


def access_test(cfg: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Scene counts per site for HLS (L30, S30) and Sentinel-2 L2A in the test window.

    `hls_s30_unfiltered` documents the antimeridian artefact (see hls_collection).
    """
    gee = cfg["gee"]
    test = gee["access_test"]
    keys = ["hls_l30", "hls_s30", "s2_sr", "s2_cloudscore"]
    counts: dict[str, dict[str, int]] = {}
    for site, xy in test["sites"].items():
        args = (xy["lon"], xy["lat"], test["start"], test["end"])
        counts[site] = {k: count_scenes(gee["collections"][k], *args) for k in keys}
        counts[site]["hls_s30_unfiltered"] = count_scenes(
            gee["collections"]["hls_s30"], *args, drop_antimeridian=False
        )
    return counts


# ------------------------------------------------------------ Phase 1 -----
# sensor -> collections, band map {standard name: source band}, pixel scale (m)
SENSORS: dict[str, dict[str, Any]] = {
    "HLS": dict(collections=["NASA/HLS/HLSL30/v002", "NASA/HLS/HLSS30/v002"], scale=30,
                bands={"L30": dict(blue="B2", green="B3", red="B4", nir="B5", swir1="B6", swir2="B7"),
                       "S30": dict(blue="B2", green="B3", red="B4", nir="B8A", swir1="B11", swir2="B12")}),
    "L5": dict(collections=["LANDSAT/LT05/C02/T1_L2"], scale=30,
               bands={"L5": dict(blue="SR_B1", green="SR_B2", red="SR_B3", nir="SR_B4", swir1="SR_B5", swir2="SR_B7")}),
    "L7": dict(collections=["LANDSAT/LE07/C02/T1_L2"], scale=30,
               bands={"L7": dict(blue="SR_B1", green="SR_B2", red="SR_B3", nir="SR_B4", swir1="SR_B5", swir2="SR_B7")}),
    "S2": dict(collections=["COPERNICUS/S2_SR_HARMONIZED"], scale=10,
               bands={"S2": dict(blue="B2", green="B3", red="B4", rededge1="B5", nir="B8A", swir1="B11", swir2="B12")}),
}
HLS_FMASK_BITS = (1, 2, 3, 4)          # cloud, adjacent, shadow, snow/ice
LANDSAT_QA_BITS = (1, 3, 4, 5)         # dilated cloud, cloud, shadow, snow


def _bits_clear(qa, bits):
    import ee

    mask = ee.Image(1)
    for b in bits:
        mask = mask.And(qa.bitwiseAnd(1 << b).eq(0))
    return mask


def _prepared(sensor: str, coll_id: str, region, lon: float, start: str, end: str, cfg: dict[str, Any]):
    """Images with standard band names, clear-masked, plus a 'tot' band (valid data)."""
    import ee

    key = {"NASA/HLS/HLSL30/v002": "L30", "NASA/HLS/HLSS30/v002": "S30"}.get(coll_id, sensor)
    bmap = SENSORS[sensor]["bands"][key]
    coll = ee.ImageCollection(coll_id).filterBounds(region).filterDate(start, end)
    if sensor == "HLS":
        for prefix in antimeridian_tile_prefixes(lon):
            coll = coll.filter(ee.Filter.stringStartsWith("system:index", prefix).Not())
    if sensor == "S2":
        cs = ee.ImageCollection(cfg["gee"]["collections"]["s2_cloudscore"])
        coll = coll.linkCollection(cs, [cfg["gee"]["s2_cloudscore_band"]])
    names = list(bmap.keys())

    def prep(img):
        data = img.select(list(bmap.values()), names)
        if sensor == "HLS":
            clear = _bits_clear(img.select("Fmask"), HLS_FMASK_BITS)
        elif sensor == "S2":
            clear = img.select(cfg["gee"]["s2_cloudscore_band"]).gte(cfg["gee"]["s2_cloudscore_min"])
        else:
            clear = _bits_clear(img.select("QA_PIXEL"), LANDSAT_QA_BITS).And(img.select("QA_RADSAT").eq(0))
        tot = data.select("red").mask().gt(0).rename("tot")
        out = data.updateMask(clear).addBands(tot.selfMask())
        return out.set({"date": img.date().format("YYYY-MM-dd"), "source": key,
                        "img_id": img.get("system:index")})

    return coll.map(prep)


def scene_stats(fields, sensor: str, start: str, end: str, cfg: dict[str, Any], key_col: str = "fy_key"):
    """Per scene x field: band medians over clear pixels, n_clear, n_total -> DataFrame."""
    import ee
    import pandas as pd

    feats = [ee.Feature(ee.Geometry(geom.__geo_interface__), {key_col: k})
             for k, geom in zip(fields[key_col], fields.geometry)]
    fc = ee.FeatureCollection(feats)
    region = fc.geometry().bounds(1)
    lon = float(fields.geometry.union_all().centroid.x)
    reducer = ee.Reducer.median().combine(ee.Reducer.count(), sharedInputs=True)
    rows = []
    for coll_id in SENSORS[sensor]["collections"]:
        coll = _prepared(sensor, coll_id, region, lon, start, end, cfg)

        def per_image(img):
            red = img.reduceRegions(fc, reducer, scale=SENSORS[sensor]["scale"])
            return red.map(lambda f: f.set({"date": img.get("date"), "source": img.get("source"),
                                            "img_id": img.get("img_id")}))

        res = coll.map(per_image).flatten().filter(ee.Filter.gt("tot_count", 0))
        rows += [f["properties"] for f in res.getInfo()["features"]]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.rename(columns={"tot_count": "n_total", "red_count": "n_clear"})
    keep = [key_col, "date", "source", "img_id", "n_total", "n_clear"] + \
           [c for c in df.columns if c.endswith("_median") and not c.startswith("tot")]
    df = df[keep].rename(columns=lambda c: c.replace("_median", ""))
    df["sensor"] = sensor
    return df


ERA5_BANDS = {
    "temperature_2m_max": "tmax_K", "temperature_2m_min": "tmin_K", "temperature_2m": "tmean_K",
    "dewpoint_temperature_2m": "tdew_K", "total_precipitation_sum": "prec_m",
    "potential_evaporation_sum": "pev_m", "surface_solar_radiation_downwards_sum": "rad_J_m2",
    "volumetric_soil_water_layer_1": "swvl1", "volumetric_soil_water_layer_2": "swvl2",
    "volumetric_soil_water_layer_3": "swvl3",
}


def era5_daily(points: dict[str, tuple[float, float]], start: str, end: str, cfg: dict[str, Any]):
    """Daily ERA5-Land values at points {key: (lon, lat)} in [start, end) -> DataFrame."""
    import ee
    import pandas as pd

    coll = ee.ImageCollection(cfg["gee"]["collections"]["era5_land_daily"]).filterDate(start, end)
    coll = coll.select(list(ERA5_BANDS), list(ERA5_BANDS.values()))
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(list(xy)), {"pt": k}) for k, xy in points.items()])

    def per_image(img):
        vals = img.reduceRegions(fc, ee.Reducer.first(), scale=11132)
        return vals.map(lambda f: f.set("date", img.date().format("YYYY-MM-dd")))

    data = coll.map(per_image).flatten().getInfo()["features"]
    return pd.DataFrame([f["properties"] for f in data])


def static_stats(fields, cfg: dict[str, Any], key_col: str = "field_uid"):
    """SoilGrids (0-30 cm weighted) and terrain (Copernicus DEM, MERIT upa) means per field."""
    import ee
    import pandas as pd

    feats = [ee.Feature(ee.Geometry(g.__geo_interface__), {key_col: k})
             for k, g in zip(fields[key_col], fields.geometry)]
    fc = ee.FeatureCollection(feats)
    depths, weights = ["0-5cm", "5-15cm", "15-30cm"], [5, 10, 15]
    layers = []
    for prop in ["clay", "sand", "silt", "soc", "bdod", "phh2o", "nitrogen", "cec"]:
        img = ee.Image(f"projects/soilgrids-isric/{prop}_mean")
        wsum = img.select(f"{prop}_{depths[0]}_mean").multiply(weights[0])
        for d, w in zip(depths[1:], weights[1:]):
            wsum = wsum.add(img.select(f"{prop}_{d}_mean").multiply(w))
        layers.append(wsum.divide(sum(weights)).rename(prop))
    dem = ee.ImageCollection(cfg["gee"]["collections"]["dem"]).select("DEM").mosaic() \
        .setDefaultProjection("EPSG:4326", None, 30).rename("elev")
    terr = ee.Terrain.products(dem)
    slope = terr.select("slope")
    asp = terr.select("aspect").multiply(3.14159265 / 180)
    tpi = dem.subtract(dem.focalMean(300, "circle", "meters")).rename("tpi")
    upa = ee.Image("MERIT/Hydro/v1_0_1").select("upa")  # upstream area km2 (90 m)
    tanb = slope.multiply(3.14159265 / 180).tan().max(0.001)
    twi = upa.multiply(1e6).divide(90).divide(tanb).log().rename("twi")
    img = ee.Image.cat(layers + [dem, slope.rename("slope"), asp.cos().rename("northness"),
                                 asp.sin().rename("eastness"), tpi, twi])
    res = img.reduceRegions(fc, ee.Reducer.mean(), scale=30).getInfo()["features"]
    return pd.DataFrame([f["properties"] for f in res])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--access-test", action="store_true", help="count scenes over test sites")
    parser.add_argument("--project", default=None, help="Earth Engine cloud project id")
    args = parser.parse_args()

    cfg = load_config()
    project = init_ee(args.project)
    print(f"Earth Engine initialised (project: {project})")
    if args.access_test:
        test = cfg["gee"]["access_test"]
        print(f"Scenes {test['start']} .. {test['end']} (end exclusive):")
        for site, c in access_test(cfg).items():
            print(f"  {site}: " + ", ".join(f"{k}={v}" for k, v in c.items()))


if __name__ == "__main__":
    main()
