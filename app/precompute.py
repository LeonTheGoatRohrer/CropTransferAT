"""Precompute compact app data under data/app/ (run: python app/precompute.py).

Reads only US data (KBS, BARC, Colorado) from data/processed and one results/ folder.
No Austrian data, no GEE. The Streamlit app reads only the files written here.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "data" / "app"
RESULTS = ROOT / "results"

SIMPLIFY_DEG = 2e-5  # ~2 m; keeps field outlines, drops vertex noise
PROBLEM_REL = 0.85  # pixel yield < 85 % of field mean = problem zone
REF_RY_MIN = 0.95  # "healthy maize" reference: fields with RY_descr >= 0.95
REF_MIN_N = 3  # minimum observations per dekad for a reference value
DEFAULT_SPEC = {"model": "M-alle", "kind": "lgbm", "basis": "HLS", "variant": "main"}


def resolve_model_spec() -> dict:
    """Read data/app/model_spec.json, else fall back to newest phase-2 run with oof.parquet."""
    spec_path = OUT / "model_spec.json"
    if spec_path.exists():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        spec["source"] = "model_spec.json"
    else:
        runs = sorted(p for p in RESULTS.glob("*_phase2*") if (p / "oof.parquet").exists())
        if not runs:
            raise SystemExit("Kein results/*_phase2*/-Ordner mit oof.parquet gefunden.")
        spec = {**DEFAULT_SPEC, "run_dir": f"results/{runs[-1].name}", "source": "fallback"}
    spec = {**DEFAULT_SPEC, **spec}
    run = Path(spec["run_dir"])
    spec["run_path"] = str(run if run.is_absolute() else ROOT / run)
    return spec


def build_fields() -> gpd.GeoDataFrame:
    g = gpd.read_parquet(PROC / "gt_field_years.parquet").to_crs(4326)
    g = g[g["sensor_era"] == "HLS"].copy()
    g["geometry"] = g.geometry.simplify(SIMPLIFY_DEG, preserve_topology=True)
    cols = ["dataset", "field_uid", "field_id", "year", "Y_t_ha", "RY_descr",
            "sensor_era", "treatment", "fy_key", "geometry"]
    return g[cols].reset_index(drop=True)


def build_reference(dek: pd.DataFrame, fields: pd.DataFrame) -> pd.DataFrame:
    """Median + 25/75 percentile per basis/index/dekad over healthy field-years (observed only)."""
    healthy = set(fields.loc[fields["RY_descr"] >= REF_RY_MIN, "fy_key"])
    d = dek[dek["fy_key"].isin(healthy) & dek["is_observed"]]
    grp = d.groupby(["basis", "index", "dekad"])["value"]
    ref = grp.agg(p25=lambda s: s.quantile(0.25), median="median",
                  p75=lambda s: s.quantile(0.75), n="size").reset_index()
    ref.loc[ref["n"] < REF_MIN_N, ["p25", "median", "p75"]] = np.nan
    ref["n_fieldyears"] = len(healthy)
    return ref


def build_yield_points(fields: pd.DataFrame) -> pd.DataFrame:
    p = pd.read_parquet(PROC / "gt_yield_points.parquet")
    key = fields[["dataset", "field_id", "year", "fy_key"]].drop_duplicates()
    p = p.merge(key, on=["dataset", "field_id", "year"], how="inner")
    p = p[np.isfinite(p["yield_t_ha"])].copy()
    mean = p.groupby("fy_key")["yield_t_ha"].transform("mean")
    p["rel_yield"] = p["yield_t_ha"] / mean
    p["problem"] = p["rel_yield"] < PROBLEM_REL
    lon = np.empty(len(p))
    lat = np.empty(len(p))
    for crs, idx in p.groupby("crs").indices.items():
        tr = Transformer.from_crs(crs, 4326, always_xy=True)
        lon[idx], lat[idx] = tr.transform(p["x"].to_numpy()[idx], p["y"].to_numpy()[idx])
    p["lon"], p["lat"] = lon, lat
    return p[["fy_key", "lon", "lat", "yield_t_ha", "rel_yield", "problem"]].reset_index(drop=True)


def build_oof(spec: dict, fy_keys: set[str]) -> pd.DataFrame:
    o = pd.read_parquet(Path(spec["run_path"]) / "oof.parquet")
    m = ((o["model"] == spec["model"]) & (o["kind"] == spec["kind"])
         & (o["basis"] == spec["basis"]) & (o["variant"] == spec["variant"]))
    if "shuffle" in o:
        m &= ~o["shuffle"].astype(bool)
    o = o[m & o["fy_key"].isin(fy_keys)]
    o = o.drop_duplicates(["fy_key", "cutoff"])
    return o[["fy_key", "dataset", "year", "y", "pred", "cutoff", "split"]].reset_index(drop=True)


def build_progress() -> dict:
    changelog = []
    for line in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \[([^\]]+)\](?:\s+[–-]\s+(\S+))?(?:\s+[–-]\s+(.*))?$", line)
        if m:
            changelog.append({"version": m.group(1), "date": m.group(2) or "", "title": m.group(3) or ""})
    reviews = []
    for f in sorted((ROOT / "reports" / "data_review").glob("*.md")):
        first = next((ln for ln in f.read_text(encoding="utf-8").splitlines() if ln.startswith("# ")), f.stem)
        reviews.append({"file": f.name, "title": first.lstrip("# ").strip()})
    figures = sorted(p.name for p in (ROOT / "reports" / "figures").glob("*.png"))
    return {"changelog": changelog, "data_reviews": reviews, "figures": figures}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    spec = resolve_model_spec()
    fields = build_fields()
    fy = set(fields["fy_key"])
    dek = pd.read_parquet(PROC / "gt_dekads.parquet")
    dek = dek[dek["fy_key"].isin(fy)]
    ref = build_reference(dek, fields)
    pts = build_yield_points(fields)
    oof = build_oof(spec, fy)
    metrics = pd.read_csv(Path(spec["run_path"]) / "metrics.csv")

    fields.to_parquet(OUT / "fields.parquet")
    dek[["fy_key", "basis", "index", "dekad", "value", "is_observed"]].to_parquet(OUT / "dekads.parquet")
    ref.to_parquet(OUT / "reference.parquet")
    pts.to_parquet(OUT / "yield_points.parquet")
    oof.to_parquet(OUT / "oof.parquet")
    metrics.to_csv(OUT / "metrics.csv", index=False)
    (OUT / "progress.json").write_text(json.dumps(build_progress(), ensure_ascii=False, indent=2), encoding="utf-8")
    spec_used = {k: v for k, v in spec.items() if k != "run_path"}
    (OUT / "model_spec_used.json").write_text(json.dumps(spec_used, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Modell: {spec['model']}/{spec['kind']}/{spec['basis']}/{spec['variant']} aus {spec['run_dir']} ({spec['source']})")
    print(f"Felder HLS: {len(fields)} Feld-Jahre | Dekaden: {len(dek)} | Ertragspixel: {len(pts)}")
    print(f"OOF-Zeilen: {len(oof)} ({oof['fy_key'].nunique()} Feld-Jahre, Stichtage {sorted(oof['cutoff'].unique())})")
    print(f"Referenz: {ref['n_fieldyears'].iloc[0]} gesunde Feld-Jahre")


if __name__ == "__main__":
    sys.exit(main())
