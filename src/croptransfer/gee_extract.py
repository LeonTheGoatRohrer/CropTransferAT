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


def init_ee(project: str | None = None) -> str:
    """Initialise Earth Engine; project from argument, env var EE_PROJECT or config."""
    import ee

    project = project or os.environ.get("EE_PROJECT") or load_config()["gee"]["project"]
    if not project:
        raise RuntimeError(
            "No Earth Engine project set: fill gee.project in config.yaml or set EE_PROJECT."
        )
    ee.Initialize(project=project)
    return project


def count_scenes(collection_id: str, lon: float, lat: float, start: str, end: str) -> int:
    """Number of images of a collection intersecting a point in [start, end)."""
    import ee

    point = ee.Geometry.Point([lon, lat])
    coll = ee.ImageCollection(collection_id).filterBounds(point).filterDate(start, end)
    return int(coll.size().getInfo())


def access_test(cfg: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Scene counts per site for HLS (L30, S30) and Sentinel-2 L2A in the test window."""
    gee = cfg["gee"]
    test = gee["access_test"]
    keys = ["hls_l30", "hls_s30", "s2_sr", "s2_cloudscore"]
    counts: dict[str, dict[str, int]] = {}
    for site, xy in test["sites"].items():
        counts[site] = {
            k: count_scenes(gee["collections"][k], xy["lon"], xy["lat"], test["start"], test["end"])
            for k in keys
        }
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
