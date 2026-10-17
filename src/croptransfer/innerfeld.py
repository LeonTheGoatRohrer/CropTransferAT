"""Common within-field yield table `gt_pixels` for the multi-site within-field study (reports/plan_innerfeld.md, I1).

One row = one 10 m cell of one field-year with a measured yield. Sites: BARC (Maryland, kriged 10 m blocks),
Kayad (Italy, combine points aggregated to the Sentinel-2 grid), Colorado (sparse sample points, kept as a
separate `kind`). Nothing is filtered here beyond what the schema needs; thresholds for the analysis are fixed
later in `reports/innerfeld_vorab.md` (step I3). Quality flags (`frac_cap`, `dist_edge_m`, `n_points`) travel with
the rows so that later filters are explicit.

Usage:  python -m croptransfer.innerfeld            # writes data/processed/gt_pixels.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path

S2_STEP = 10.0                    # Sentinel-2 grid (m); cells are centred on multiples of 10 m + 5 m
KAYAD_CAP_KG_HA = 18000.0         # the yield monitor output saturates at exactly 18 000 kg/ha
KAYAD_MIN_POINTS = 10             # points per 10 m cell (spacing ~1.5 m -> ~40 expected)
COLORADO_CRS = "EPSG:32613"
KAYAD_CRS = "EPSG:32632"

SCHEMA = ["site", "field_id", "year", "fy_key", "crop", "kind", "x", "y", "crs", "yield_t_ha", "rel",
          "n_points", "frac_cap", "moisture_pct", "dist_edge_m", "n_cells_fy", "source"]


# ----------------------------------------------------------------------------------------------
# pure functions (unit-tested)
# ----------------------------------------------------------------------------------------------
def cell_center(v: np.ndarray | pd.Series, step: float = S2_STEP) -> np.ndarray:
    """Centre of the grid cell of size `step` that contains coordinate v (cells start at multiples of step)."""
    return np.floor(np.asarray(v, dtype=float) / step) * step + step / 2.0


def aggregate_points(pts: pd.DataFrame, keys: list[str], step: float = S2_STEP, min_points: int = 1,
                     cap: float | None = None) -> pd.DataFrame:
    """Mean yield of point data per grid cell and group.

    pts needs x, y, yield_t_ha (+ optional moisture_pct) and the `keys` columns. Cells with fewer than
    `min_points` points are dropped. `frac_cap` = share of points at the monitor cap (t/ha value `cap`).
    """
    p = pts.copy()
    p["cx"], p["cy"] = cell_center(p.x, step), cell_center(p.y, step)
    p["is_cap"] = (p.yield_t_ha >= cap - 1e-9) if cap is not None else False
    if "moisture_pct" not in p:
        p["moisture_pct"] = np.nan
    g = p.groupby(keys + ["cx", "cy"], sort=True)
    out = g.agg(yield_t_ha=("yield_t_ha", "mean"), n_points=("yield_t_ha", "size"),
                frac_cap=("is_cap", "mean"), moisture_pct=("moisture_pct", "mean")).reset_index()
    out = out[out.n_points >= min_points].rename(columns={"cx": "x", "cy": "y"})
    return out.reset_index(drop=True)


def add_relative_yield(df: pd.DataFrame, key: str = "fy_key") -> pd.DataFrame:
    """rel = cell yield / mean cell yield of the same field-year; also the number of cells."""
    out = df.copy()
    out["rel"] = out.yield_t_ha / out.groupby(key).yield_t_ha.transform("mean")
    out["n_cells_fy"] = out.groupby(key).yield_t_ha.transform("size")
    return out


def hull_edge_distance(x: np.ndarray, y: np.ndarray, hx: np.ndarray, hy: np.ndarray) -> np.ndarray:
    """Distance (m) of points to the boundary of the convex hull of (hx, hy); negative outside the hull."""
    import shapely

    hull = shapely.MultiPoint(np.c_[hx, hy]).convex_hull
    pts = shapely.points(np.asarray(x, float), np.asarray(y, float))
    d = shapely.distance(hull.boundary, pts)
    inside = shapely.contains_xy(hull, np.asarray(x, float), np.asarray(y, float))
    return np.where(inside, d, -d)


# ----------------------------------------------------------------------------------------------
# site loaders
# ----------------------------------------------------------------------------------------------
def load_kayad_points(raw: Path) -> pd.DataFrame:
    """Kayad et al. (Zenodo 14216165): corn 2016-2018, one 22 ha field in the Po valley (CC BY 4.0).

    2018 is read from the EPSG:32632 copy (the original shapefile carries Gauss-Boaga coordinates).
    """
    import geopandas as gpd

    base = raw / "FIELD_YIELD"
    files = {2016: base / "yield2016" / "yield2016.gpkg", 2017: base / "yield2017" / "yield2017.shp",
             2018: base / "yield2018" / "yield2018_epsg32632.gpkg"}
    parts = []
    for yr, f in files.items():
        g = gpd.read_file(f)
        assert g.crs.to_epsg() == 32632, (yr, g.crs)
        parts.append(pd.DataFrame({"year": yr, "number": g["NUMBER"].to_numpy(), "x": g.geometry.x.to_numpy(),
                                   "y": g.geometry.y.to_numpy(),
                                   "yield_t_ha": g["YIELD"].to_numpy(float) / 1000.0,
                                   "moisture_pct": g["HUMID"].to_numpy(float)}))
    return pd.concat(parts, ignore_index=True)


def build_kayad(raw: Path) -> pd.DataFrame:
    pts = load_kayad_points(raw)
    pts["site"], pts["field_id"] = "KAYAD", "KAYAD_1"
    cells = aggregate_points(pts, ["site", "field_id", "year"], min_points=KAYAD_MIN_POINTS,
                             cap=KAYAD_CAP_KG_HA / 1000.0)
    cells["fy_key"] = "KAYAD|KAYAD_1|" + cells.year.astype(str)
    cells = add_relative_yield(cells)
    # field outline = convex hull of the raw points of the same year (the shapefile has no polygon)
    dist = np.full(len(cells), np.nan)
    for yr, idx in cells.groupby("year").groups.items():
        p = pts[pts.year == yr]
        c = cells.loc[idx]
        dist[cells.index.get_indexer(idx)] = hull_edge_distance(c.x, c.y, p.x.to_numpy(), p.y.to_numpy())
    cells["dist_edge_m"] = dist
    cells["crop"], cells["kind"], cells["crs"] = "maize", "points10", KAYAD_CRS
    cells["source"] = "Kayad et al. 2019, Zenodo 14216165, CC BY 4.0"
    return cells


def build_barc(cfg: dict[str, Any]) -> pd.DataFrame:
    """BARC rows exactly as used in Phase 2.3 (points inside the 10 m inward-buffered field outline)."""
    from croptransfer.within_field import load_pixels, wf_config

    wf = wf_config(cfg)
    px = load_pixels(cfg, wf)
    out = pd.DataFrame({
        "site": "BARC", "field_id": px.field_id, "year": px.year, "fy_key": px.fy_key, "crop": "maize",
        "kind": "raster10", "x": px.x, "y": px.y, "crs": "EPSG:32618", "yield_t_ha": px.yield_t_ha,
        "rel": px.rel, "n_points": 1, "frac_cap": 0.0, "moisture_pct": np.nan,
        "dist_edge_m": px.dist_edge_m, "source": "USDA-ARS BARC, kriged 10 m blocks"})
    out["n_cells_fy"] = out.groupby("fy_key").yield_t_ha.transform("size")
    return out


def build_colorado(raw: Path) -> pd.DataFrame:
    """Akron, Colorado: sparse sample points (about 30 m apart) of dryland corn sub-fields. Not a map."""
    d = pd.read_csv(raw / "colorado" / "Modeling_data.csv", na_values=["NA"])
    d = d[d.crop.str.lower() == "corn"].dropna(subset=["yield_kg_ha"]).copy()
    out = pd.DataFrame({
        "site": "COLORADO", "field_id": "CO_" + d.field.astype(str), "year": d.year.astype(int),
        "crop": "maize", "kind": "sparse_points", "x": d.easting_UTM13N.to_numpy(float),
        "y": d.northing_UTM13N.to_numpy(float), "crs": COLORADO_CRS,
        "yield_t_ha": d.yield_kg_ha.to_numpy(float) / 1000.0, "n_points": 1, "frac_cap": 0.0,
        "moisture_pct": np.nan, "dist_edge_m": np.nan,
        "source": "Poss et al., Ag Data Commons 10.15482/USDA.ADC/28914434.v1, CC0"})
    out["fy_key"] = "COLORADO|" + out.field_id + "|" + out.year.astype(str)
    out = add_relative_yield(out.reset_index(drop=True))
    return out


# ----------------------------------------------------------------------------------------------
def build_gt_pixels(cfg: dict[str, Any]) -> pd.DataFrame:
    raw = repo_path(cfg["paths"]["raw"])
    parts = [build_barc(cfg), build_kayad(raw / "kayad"), build_colorado(raw)]
    df = pd.concat([p[SCHEMA] for p in parts], ignore_index=True)
    return df


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for site, g in df.groupby("site"):
        fy = g.groupby("fy_key").agg(n=("rel", "size"), sd_rel=("rel", "std"))
        out[site] = dict(kind=g.kind.iloc[0], n_rows=int(len(g)), n_field_years=int(fy.shape[0]),
                         n_fields=int(g.field_id.nunique()), years=sorted(int(y) for y in g.year.unique()),
                         cells_per_fy_median=float(fy.n.median()), cells_per_fy_min=int(fy.n.min()),
                         sd_rel_median=float(fy.sd_rel.median()),
                         frac_rel_below_085=float((g.rel < 0.85).mean()),
                         frac_cap_mean=float(g.frac_cap.mean()))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_config()
    df = build_gt_pixels(cfg)
    out = Path(args.out) if args.out else repo_path(cfg["paths"]["processed"]) / "gt_pixels.parquet"
    df.to_parquet(out, index=False)
    s = summarize(df)
    (out.parent / "gt_pixels_summary.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
