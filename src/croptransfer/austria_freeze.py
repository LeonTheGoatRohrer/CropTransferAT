"""Freeze for the Austria test (PLAN.md Phase 4/7): stress-score reference + registered test protocol inputs.

Two frozen models enter the Austria test, side by side (no winner is chosen on Austrian data):
  * Stress score (field level): negative mean deviation of the HLS-NDVI dekad curve from the median curve
    of healthy US maize field-years (RY_descr >= 0.95, HLS era). Needs no fitting beyond the reference
    curve, which is written to reports/freeze_at/ and hashed here.
  * Regional LightGBM (CY-Bench EU, freeze-cybench-1): unchanged, hashes re-verified here.

This module reads only US training data, geometry of municipalities and the config. It never opens an
Austrian satellite or yield value.

Usage:  python -m croptransfer.austria_freeze
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from croptransfer import regional_cybench as rc
from croptransfer import stress
from croptransfer.config import load_config, repo_path

FREEZE_DIR = "reports/freeze_at"


def build_stress_reference(cfg) -> tuple[pd.Series, int]:
    """Median HLS-NDVI per dekad over healthy US HLS-era field-years (all training data, no Austria)."""
    proc = repo_path(cfg["paths"]["processed"])
    sc = cfg["at_test"]["stress"]
    feat = pd.read_parquet(proc / "features_0901.parquet", columns=["fy_key", "dataset", "RY_descr", "sensor_era"])
    assert set(feat.dataset) <= {"KBS", "BARC", "Colorado"}, "unexpected dataset in US training table"
    healthy = feat.loc[(feat.RY_descr >= sc["healthy_ry_min"]) & (feat.sensor_era == "HLS"), "fy_key"]
    dek = pd.read_parquet(proc / "gt_dekads.parquet")
    ref = stress.reference_curve(dek, healthy, index=sc["index"], basis=sc["basis"])
    return ref, int(healthy.nunique())


def site_centroids(cfg) -> dict[str, dict]:
    """Centroid (EPSG:31287 and 4326) of the union of the site's municipalities."""
    gem = gpd.read_file(repo_path("data/raw/admin_at/GEM_20250101/STATISTIK_AUSTRIA_GEM_20250101.shp"))
    gem["g_id"] = gem["g_id"].astype(str)
    out = {}
    for key, s in cfg["at_test"]["sites"].items():
        sel = gem[gem.g_id.isin(s["gemeinden"])]
        assert len(sel) == len(s["gemeinden"]), f"municipality not found for site {key}"
        c = sel.geometry.union_all().centroid
        c4326 = gpd.GeoSeries([c], crs=gem.crs).to_crs(4326).iloc[0]
        out[key] = {"x_31287": round(c.x, 1), "y_31287": round(c.y, 1),
                    "lon": round(c4326.x, 5), "lat": round(c4326.y, 5),
                    "municipalities": list(sel.g_name)}
    return out


def main() -> None:
    cfg = load_config()
    out_dir = repo_path(FREEZE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ref, n_fy = build_stress_reference(cfg)
    ref_path = out_dir / "stress_reference_hls_ndvi.csv"
    ref.rename("ndvi_median").to_csv(ref_path, header=True, float_format="%.6f")
    cent = site_centroids(cfg)
    cent_path = out_dir / "site_centroids.json"
    cent_path.write_text(json.dumps(cent, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    cfg_path = out_dir / "at_test_config.json"
    cfg_path.write_text(json.dumps(cfg["at_test"], indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    cy = cfg["cybench"]["freeze"]
    reg = rc.verify_freeze(repo_path(cy["dir"]), repo_path(cy["protocol"]))
    files = {p.name: rc.sha256_file(p) for p in (ref_path, cent_path, cfg_path)}
    summary = {"stress_reference_field_years": n_fy, "regional_files_verified": len(reg), "files": files,
               "reference_curve": {int(k): round(float(v), 4) for k, v in ref.items()}, "code": rc.git_info()}
    (out_dir / "freeze_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
