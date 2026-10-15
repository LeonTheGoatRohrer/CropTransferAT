"""US yield ground truth (KBS, BARC, Colorado) -> one schema (PLAN.md Phase 1.1, §3.6).

Outputs (data/processed/):
  gt_field_years.parquet   one row per maize field-year (GeoParquet, EPSG:4326, buffered field)
  gt_yield_points.parquet  within-field yields (BARC kriging raster aggregated to 10 m)
  gt_excluded.csv          every excluded row with reason

Yields are converted to t/ha at 15.5 % grain moisture (DATA_SOURCES.md).
Usage:  python -m croptransfer.groundtruth
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union

from croptransfer.config import load_config, repo_path

BU_AC_TO_KG_HA = 62.77  # 1 bu/ac maize (56 lb) in kg/ha

FIELD_YEAR_COLUMNS = [
    "dataset", "design", "field_id", "field_uid", "year", "crop", "Y_t_ha", "n_points",
    "frac_points_removed", "irrigated", "moisture_basis", "sowing_date", "reported_damage",
    "sensor_era", "harvest_part", "double_crop", "area_ha", "source", "geometry",
]


def to_standard_moisture(y: np.ndarray | float, basis: float, standard: float = 0.155):
    """Convert a yield at moisture `basis` to `standard` moisture (same dry matter)."""
    return np.asarray(y) * (1 - basis) / (1 - standard)


def clean_points(values: np.ndarray, valid_range: tuple[float, float], n_sd: float) -> np.ndarray:
    """Boolean mask of points kept: inside valid_range and within mean +- n_sd*SD (§3.6)."""
    v = np.asarray(values, dtype=float)
    keep = np.isfinite(v) & (v >= valid_range[0]) & (v <= valid_range[1])
    if keep.sum() > 2:
        mu, sd = v[keep].mean(), v[keep].std()
        keep &= np.abs(v - mu) <= n_sd * sd
    return keep


def sensor_era(year: int) -> str:
    """Satellite basis available for a year: HLS from 2013, Landsat 5/7 before."""
    return "HLS" if year >= 2013 else "L57"


# ---------------------------------------------------------------- KBS -----
def load_kbs(cfg: dict[str, Any]) -> tuple[gpd.GeoDataFrame, list[dict]]:
    """KBS MCSE plots, table 51 (whole_plot yield, 15.5 % basis per metadata)."""
    raw = repo_path(cfg["paths"]["raw"]) / "kbs"
    t51 = pd.read_csv(raw / "kbs_datatable_51.csv", comment="#")
    maize = t51[t51.Crop.str.contains("Zea", na=False)].copy()
    excluded = []
    for _, r in maize[maize.whole_plot_yield_kg_ha.isna()].iterrows():
        excluded.append(dict(dataset="KBS", field_id=f"{r.Treatment}{r.Replicate}", year=r.Year,
                             reason="no whole_plot yield"))
    maize = maize[maize.whole_plot_yield_kg_ha.notna()]
    bad = ~maize.Treatment.isin(["T1", "T2", "T3", "T4"])
    for _, r in maize[bad].iterrows():
        excluded.append(dict(dataset="KBS", field_id=f"{r.Treatment}{r.Replicate}", year=r.Year,
                             reason="unexplained treatment label (not T1-T4)"))
    maize = maize[~bad]
    plots = gpd.read_file(f"zip://{raw / 'gis' / 'exp_plots_mainsite.zip'}!plot_polygons_mainsite.shp")
    plots = plots.set_index("PlotID")
    rows = []
    for _, r in maize.iterrows():
        pid = f"{r.Treatment}{r.Replicate}"
        year = int(r.Year)
        rows.append(dict(
            dataset="KBS", design="longitudinal", field_id=pid, year=year, crop="maize",
            Y_t_ha=float(r.whole_plot_yield_kg_ha) / 1000.0, n_points=np.nan,
            frac_points_removed=np.nan, irrigated=False, moisture_basis=0.155,
            sowing_date=pd.NaT, reported_damage=None, sensor_era=sensor_era(year),
            harvest_part="east_half" if year <= 2016 else "whole",
            double_crop=False, source="KBS LTER table 51", treatment=r.Treatment,
            geometry=plots.loc[pid, "geometry"],
        ))
    gdf = gpd.GeoDataFrame(rows, crs=plots.crs)
    return gdf, excluded


# --------------------------------------------------------------- BARC -----
BARC_BASIS = {2014: 0.14, 2019: 0.14, 2020: 0.14, 2016: 0.15, 2017: 0.15, 2018: 0.15, 2021: 0.15}


def barc_field_key(filename: str) -> tuple[str, str] | None:
    """('CentralFarm_1_7', 'CORN') from a BARC kriging raster file name."""
    stem = Path(filename).stem
    stem = re.sub(r"^(USDA|usda)_", "", stem)
    m = re.match(r"(.+?)_(20\d\d)_([A-Za-z]+)", stem)
    if not m:
        return None
    field = m.group(1).replace("Central_Farm", "CentralFarm").replace("East_Farm", "EastFarm")
    field = field.replace(" ", "").replace("-", "_")
    return field, m.group(3).upper()


def _raster_footprint(mask: np.ndarray, transform) -> Any:
    from rasterio import features

    polys = [shape(g) for g, v in features.shapes(mask.astype("uint8"), mask=mask, transform=transform)]
    return unary_union(polys)


def load_barc(cfg: dict[str, Any]) -> tuple[gpd.GeoDataFrame, pd.DataFrame, list[dict]]:
    """BARC block-kriging rasters (5 m) of maize field-years."""
    import rasterio

    gt = cfg["groundtruth"]
    raw = repo_path(cfg["paths"]["raw"]) / "barc"
    rows, points, excluded = [], [], []
    for zpath in sorted(raw.glob("20*.zip")):
        year = int(zpath.stem)
        names = [n for n in zipfile.ZipFile(zpath).namelist() if n.lower().endswith(".tif")
                 and n.split("/")[1].startswith("6")]
        keys = {n: barc_field_key(n) for n in names}
        other_crop_fields = {k[0] for k in keys.values() if k and k[1] != "CORN"}
        for name, key in keys.items():
            if not key or key[1] != "CORN":
                continue
            field = key[0]
            with rasterio.open(f"/vsizip/{zpath.as_posix()}/{name}") as r:
                a = r.read(1, masked=True).astype(float)
                transform, crs = r.transform, r.crs
            valid = ~np.ma.getmaskarray(a) & np.isfinite(a.filled(np.nan))
            vals = a.filled(np.nan)
            raw_mean = float(np.nanmean(vals[valid]))
            if raw_mean < 20:  # bu/ac expected (~60-250); values ~3 => unknown unit (DATA_SOURCES §4)
                excluded.append(dict(dataset="BARC", field_id=field, year=year,
                                     reason=f"raster unit unclear (mean {raw_mean:.2f}, expected bu/ac)"))
                continue
            t_ha = to_standard_moisture(vals * BU_AC_TO_KG_HA / 1000.0, BARC_BASIS[year], gt["moisture_standard"])
            keep = valid & clean_points(t_ha, tuple(gt["yield_valid_range_t_ha"]), gt["outlier_sd"])
            footprint = _raster_footprint(valid, transform)
            rows.append(dict(
                dataset="BARC", design="longitudinal", field_id=field, year=year, crop="maize",
                Y_t_ha=float(t_ha[keep].mean()), n_points=int(keep.sum()),
                frac_points_removed=float(1 - keep.sum() / valid.sum()), irrigated=np.nan,
                moisture_basis=BARC_BASIS[year], sowing_date=pd.NaT, reported_damage=None,
                sensor_era=sensor_era(year), harvest_part="whole",
                double_crop=field in other_crop_fields, source=f"BARC {name.split('/')[-1]}",
                treatment=None, geometry=footprint,
            ))
            # within-field points: 5 m -> 10 m blocks (mean of kept 5 m cells)
            ys, xs = np.nonzero(keep)
            blk = pd.DataFrame({"r": ys // 2, "c": xs // 2, "v": t_ha[ys, xs]})
            blk = blk.groupby(["r", "c"], as_index=False).v.mean()
            x, y = rasterio.transform.xy(transform, blk.r * 2 + 0.5, blk.c * 2 + 0.5)
            points.append(pd.DataFrame(dict(dataset="BARC", field_id=field, year=year,
                                            x=x, y=y, yield_t_ha=blk.v, crs=str(crs))))
    crs = rasterio.crs.CRS.from_epsg(32618)
    gdf = gpd.GeoDataFrame(rows, crs=crs)
    return gdf, pd.concat(points, ignore_index=True), excluded


# ----------------------------------------------------------- Colorado -----
def load_colorado(cfg: dict[str, Any]) -> tuple[gpd.GeoDataFrame, list[dict]]:
    """Akron dryland sample points: field-year mean, footprint = convex hull of points.

    Points are hand-curated samples (not a yield monitor), so the monitor cleaning
    rule (§3.6) is not applied; zero yields are real crop failures.
    """
    raw = repo_path(cfg["paths"]["raw"]) / "colorado"
    c = pd.read_csv(raw / "Modeling_data.csv")
    c = c[c.crop.str.contains("corn", case=False, na=False)]
    rows = []
    for (field, year), g in c.groupby(["field", "year"]):
        pts = gpd.points_from_xy(g.easting_UTM13N, g.northing_UTM13N)
        rows.append(dict(
            dataset="Colorado", design="longitudinal", field_id=str(field), year=int(year),
            crop="maize", Y_t_ha=float(g.yield_kg_ha.mean() / 1000.0), n_points=len(g),
            frac_points_removed=0.0, irrigated=False, moisture_basis=0.155, sowing_date=pd.NaT,
            reported_damage=None, sensor_era=sensor_era(int(year)), harvest_part="sample_points",
            double_crop=False, source="Akron Modeling_data.csv", treatment=None,
            geometry=unary_union(pts).convex_hull,
        ))
    return gpd.GeoDataFrame(rows, crs="EPSG:32613"), []


# ------------------------------------------------------- field matching ---
def iou(a, b) -> float:
    """Intersection over union of two polygons (0 if disjoint)."""
    inter = a.intersection(b).area
    return float(inter / a.union(b).area) if inter > 0 else 0.0


def assign_field_uid(gdf: gpd.GeoDataFrame, min_iou: float) -> pd.Series:
    """Same physical field over years: IoU >= min_iou with any earlier member (§3.1).

    Greedy in year order; the uid is '<dataset>:<first field_id>'. Two field-years of
    the same year never share a uid.
    """
    uids: list[str] = [""] * len(gdf)
    groups: list[tuple[str, list[int]]] = []
    order = np.argsort(gdf["year"].to_numpy(), kind="stable")
    for i in order:
        geom, year = gdf.geometry.iloc[i], gdf["year"].iloc[i]
        best, best_iou = None, min_iou
        for gi, (uid, members) in enumerate(groups):
            if any(gdf["year"].iloc[m] == year for m in members):
                continue
            v = max(iou(geom, gdf.geometry.iloc[m]) for m in members)
            if v >= best_iou:
                best, best_iou = gi, v
        if best is None:
            uid = f"{gdf['dataset'].iloc[i]}:{gdf['field_id'].iloc[i]}"
            groups.append((uid, [i]))
        else:
            groups[best][1].append(i)
            uid = groups[best][0]
        uids[i] = uid
    return pd.Series(uids, index=gdf.index)


def build(cfg: dict[str, Any] | None = None) -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:
    """All US datasets -> buffered field-years (EPSG:4326), yield points, exclusion log."""
    cfg = cfg or load_config()
    buf = cfg["field"]["inner_buffer_m"]
    parts, excluded = [], []
    kbs, ex = load_kbs(cfg)
    excluded += ex
    barc, points, ex = load_barc(cfg)
    excluded += ex
    colo, ex = load_colorado(cfg)
    excluded += ex
    for g in (kbs, barc, colo):
        g = g.copy()
        g["field_uid"] = assign_field_uid(g, cfg["field"]["iou_match_min"])
        # Colorado hulls already lie inside the field (sample points), no extra buffer
        g["geometry"] = g.geometry if g["dataset"].iloc[0] == "Colorado" else g.geometry.buffer(buf)
        g["area_ha"] = g.geometry.area / 1e4
        parts.append(g.to_crs("EPSG:4326"))
    fy = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs="EPSG:4326")
    empty = fy.geometry.is_empty | (fy.area_ha <= 0)
    for _, r in fy[empty].iterrows():
        excluded.append(dict(dataset=r.dataset, field_id=r.field_id, year=r.year,
                             reason="empty geometry after inner buffer"))
    fy = fy[~empty].reset_index(drop=True)
    fy = fy[FIELD_YEAR_COLUMNS[:-1] + ["treatment", "geometry"]]
    return fy, points, pd.DataFrame(excluded)


def main() -> None:
    cfg = load_config()
    out = repo_path(cfg["paths"]["processed"])
    out.mkdir(parents=True, exist_ok=True)
    fy, points, excluded = build(cfg)
    fy.to_parquet(out / "gt_field_years.parquet")
    points.to_parquet(out / "gt_yield_points.parquet")
    excluded.to_csv(out / "gt_excluded.csv", index=False)
    print(fy.groupby(["dataset", "sensor_era"]).agg(field_years=("year", "size"),
          fields=("field_uid", "nunique"), years=("year", "nunique")).to_string())
    print(f"excluded rows: {len(excluded)}; yield points: {len(points)}")


if __name__ == "__main__":
    main()
