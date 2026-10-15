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
