"""INVEKOS field parcels (AMA): locate files, read schema, count crop codes.

Phase 0 scope only (Austria rule, PLAN.md §0): schema and counts, no analysis
of Austrian satellite or yield data before the model freeze.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyogrio

CROP_CODE_COL = "SNAR_CODE"
CROP_NAME_COL = "SNAR_BEZEICHNUNG"
AREA_COL = "SL_FLAECHE_BRUTTO_HA"


def find_gpkgs(invekos_dir: str | Path) -> dict[int, Path]:
    """One GeoPackage per year from data/raw/invekos/<year>/ (latest 'Stand' if several)."""
    out: dict[int, Path] = {}
    for year_dir in sorted(Path(invekos_dir).iterdir()):
        if year_dir.is_dir() and year_dir.name.isdigit():
            files = sorted(year_dir.glob("*.gpkg"))
            if files:
                out[int(year_dir.name)] = files[-1]  # e.g. 2025-2 sorts after 2025-1
    return out


def schema(path: str | Path) -> dict:
    """Layer name, feature count, CRS and column dtypes without reading features."""
    info = pyogrio.read_info(path)
    return {
        "layer": info["layer_name"],
        "features": int(info["features"]),
        "crs": info["crs"],
        "columns": dict(zip(info["fields"], info["dtypes"])),
    }


def crop_code_counts(path: str | Path, codes: dict[str, str]) -> pd.DataFrame:
    """Parcel count and summed area per crop code (attributes only, no geometry).

    `codes` maps SNAR_CODE -> label, e.g. {"105": "koernermais"}.
    """
    df = pyogrio.read_dataframe(
        path, columns=[CROP_CODE_COL, CROP_NAME_COL, AREA_COL], read_geometry=False
    )
    df = df[df[CROP_CODE_COL].isin(codes)]
    out = df.groupby(CROP_CODE_COL).agg(
        name=(CROP_NAME_COL, "first"),
        n=(AREA_COL, "size"),
        area_ha=(AREA_COL, "sum"),
        n_ge_1ha=(AREA_COL, lambda s: int((s >= 1.0).sum())),
    )
    out.insert(0, "label", out.index.map(codes))
    return out.reindex(list(codes)).fillna({"n": 0, "area_ha": 0.0, "n_ge_1ha": 0})


def count_in_state(path: str | Path, gemeinden, code: str = "105",
                   state_prefix: str = "6", min_area_ha: float = 1.0) -> dict:
    """Count parcels of one crop code inside a Bundesland (default 6 = Steiermark).

    INVEKOS has no Bundesland attribute: each parcel's representative point is
    joined to the municipalities (`gemeinden`: GeoDataFrame with Gemeindekennziffer
    `g_id`, first digit = Bundesland). Also counts invalid geometries.
    """
    import geopandas as gpd

    parcels = pyogrio.read_dataframe(path, columns=[AREA_COL], where=f"{CROP_CODE_COL} = '{code}'")
    if parcels.crs is None or parcels.crs.to_epsg() != 31287:
        parcels = parcels.set_crs(31287, allow_override=True)  # 2018-2020: same CRS, WKT without EPSG
    invalid = int((~parcels.geometry.is_valid).sum())
    points = parcels.set_geometry(parcels.geometry.representative_point())
    joined = gpd.sjoin(points, gemeinden[["g_id", "geometry"]].to_crs(31287), how="left", predicate="within")
    inside = joined[joined["g_id"].astype(str).str.startswith(state_prefix)]
    return {
        "n_austria": len(parcels),
        "invalid_geometries": invalid,
        "unmatched": int(joined["g_id"].isna().sum()),
        "n": len(inside),
        "area_ha": float(inside[AREA_COL].sum()),
        "n_ge_min_area": int((inside[AREA_COL] >= min_area_ha).sum()),
    }
