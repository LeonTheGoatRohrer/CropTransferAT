"""SSURGO soil productivity for US fields via USDA NRCS Soil Data Access (SDA, no login).

Two attributes (US only, analysis feature M-B+, never a label, see PLAN.md §2):
- non-irrigated corn yield estimate: table `cocropyld`, column `nonirryield_r`
  (cropname = 'Corn', units in `yldunits`, normally 'Bu' = bu/ac), per component;
- NCCPI corn: table `cointerp`, mrulename = NCCPI Ver 3.0, rulename = corn submodel,
  rating 0-1 in `interphr`, per component.
Aggregation: component-percent weighted mean per map unit (components without a value
are left out), then area-weighted mean over the map units that intersect the field.

Usage:  python -m croptransfer.soil_ssurgo      (test query: KBS plots + one BARC field)
"""

from __future__ import annotations

import json
import sys
import urllib.request

import pandas as pd

from croptransfer.config import load_config, repo_path


def sda_query(sql: str, url: str, timeout: int = 120) -> pd.DataFrame:
    """Run one SQL statement on Soil Data Access and return the result table."""
    body = json.dumps({"query": sql, "format": "JSON+COLUMNNAME"}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8")
    if not text.strip():
        return pd.DataFrame()
    if text.lstrip().startswith("<"):
        raise RuntimeError(f"SDA error: {text[:500]}")
    rows = json.loads(text)["Table"]
    return pd.DataFrame(rows[1:], columns=rows[0])


def mapunit_areas_sql(wkt: str) -> str:
    """Map units intersecting a WGS84 polygon with their intersection area (deg², for weights)."""
    geom = f"geometry::STGeomFromText('{wkt}', 4326)"
    return (
        f"SELECT mukey, SUM(mupolygongeo.STIntersection({geom}).STArea()) AS area "
        f"FROM mupolygon WHERE mupolygongeo.STIntersects({geom}) = 1 GROUP BY mukey"
    )


def component_values_sql(mukeys: list[str], crop: str, nccpi_rule: str, nccpi_corn_rule: str) -> str:
    """Per component: share, non-irrigated corn yield and NCCPI corn rating."""
    keys = ",".join(f"'{int(k)}'" for k in mukeys)
    return (
        "SELECT c.mukey, c.cokey, c.compname, c.comppct_r, c.majcompflag, "
        "y.nonirryield_r, y.yldunits, i.interphr AS nccpi_corn "
        "FROM component c "
        f"LEFT JOIN cocropyld y ON y.cokey = c.cokey AND y.cropname = '{crop}' "
        f"LEFT JOIN cointerp i ON i.cokey = c.cokey AND i.mrulename = '{nccpi_rule}' "
        f"AND i.rulename = '{nccpi_corn_rule}' "
        f"WHERE c.mukey IN ({keys})"
    )


def coverage_sql(areasymbols: list[str], crop: str, nccpi_corn_rule: str) -> str:
    """Per soil survey area: major components, and how many have a corn yield / NCCPI corn."""
    areas = ",".join(f"'{a}'" for a in areasymbols if a.isalnum())
    return (
        "SELECT l.areasymbol, COUNT(*) AS n_major, COUNT(y.cokey) AS n_major_corn_yield, "
        "COUNT(i.cokey) AS n_major_nccpi_corn "
        "FROM legend l JOIN mapunit m ON m.lkey = l.lkey "
        "JOIN component c ON c.mukey = m.mukey AND c.majcompflag = 'Yes' "
        f"LEFT JOIN (SELECT DISTINCT cokey FROM cocropyld WHERE cropname = '{crop}') y ON y.cokey = c.cokey "
        f"LEFT JOIN (SELECT DISTINCT cokey FROM cointerp WHERE rulename = '{nccpi_corn_rule}') i ON i.cokey = c.cokey "
        f"WHERE l.areasymbol IN ({areas}) GROUP BY l.areasymbol"
    )


def mapunit_values(components: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Component-percent weighted mean per map unit; components without a value are skipped."""
    comp = components.copy()
    comp["comppct_r"] = pd.to_numeric(comp["comppct_r"], errors="coerce")
    out = {}
    for col in value_cols:
        val = pd.to_numeric(comp[col], errors="coerce")
        ok = val.notna() & comp["comppct_r"].gt(0)
        w = comp["comppct_r"].where(ok)
        num = (val * w).groupby(comp["mukey"]).sum(min_count=1)
        den = w.groupby(comp["mukey"]).sum(min_count=1)
        out[col] = num / den
        out[f"{col}_pct"] = den  # share of the map unit that has a value
    return pd.DataFrame(out)


def field_value(
    areas: pd.DataFrame, mu_values: pd.DataFrame, value_cols: list[str], min_comp_pct: float = 0.0
) -> dict[str, float]:
    """Area-weighted field value over map units.

    `<col>_comp_pct` = area-weighted share (0-100) of the field's soil components that have
    a value. If it is below `min_comp_pct`, the field value is NaN: a value carried by a
    1 % minor component must not stand for the whole field.
    """
    a = areas.assign(area=pd.to_numeric(areas["area"], errors="coerce")).set_index("mukey")["area"]
    total = a.sum()
    result: dict[str, float] = {}
    for col in value_cols:
        v = mu_values[col].reindex(a.index)
        pct = mu_values[f"{col}_pct"].reindex(a.index).fillna(0.0)
        has = v.notna()
        comp_pct = float((pct * a).sum() / total) if total > 0 else float("nan")
        value = float((v[has] * a[has]).sum() / a[has].sum()) if has.any() else float("nan")
        result[col] = value if comp_pct >= min_comp_pct else float("nan")
        result[f"{col}_comp_pct"] = comp_pct
    result["n_mapunits"] = int(len(a))
    return result


def query_field(wkt: str, cfg: dict) -> tuple[dict[str, float], pd.DataFrame]:
    """Field-level SSURGO values for one WGS84 polygon (network call)."""
    s = cfg["ssurgo"]
    areas = sda_query(mapunit_areas_sql(wkt), s["sda_url"])
    comps = sda_query(
        component_values_sql(areas["mukey"].tolist(), s["crop_name"], s["nccpi_rule"], s["nccpi_corn_rule"]),
        s["sda_url"],
    )
    cols = ["nonirryield_r", "nccpi_corn"]
    return field_value(areas, mapunit_values(comps, cols), cols, s["min_comp_pct_with_value"]), comps


def _test_fields(cfg: dict) -> dict[str, str]:
    """WKT (WGS84) of the KBS MCSE plots and one BARC field outline (raster footprint)."""
    import geopandas as gpd
    import rasterio
    from rasterio.features import shapes

    raw = repo_path(cfg["paths"]["raw"])
    plots = gpd.read_file(raw / "kbs/gis/exp_plots_mainsite/plot_polygons_mainsite.shp")
    plots = plots[plots["PlotID"].str.fullmatch(r"T[1-4]R[1-6]")].to_crs(4326)
    fields = {f"KBS {pid}": geom.wkt for pid, geom in zip(plots["PlotID"], plots.geometry)}

    tif = next((raw / "barc/extracted/2014/6A--Interpolated_Yield_Values_GeoTIFF").glob("*Central_Farm_1_7*CORN*.tif"))
    with rasterio.open(tif) as src:
        band = src.read(1, masked=True)
        polys = [shape for shape, val in shapes((~band.mask).astype("uint8"), transform=src.transform) if val == 1]
        crs = src.crs
    from shapely.geometry import shape as to_shape
    outline = gpd.GeoSeries([to_shape(p) for p in polys], crs=crs).union_all()
    outline = gpd.GeoSeries([outline], crs=crs).to_crs(4326).iloc[0].simplify(0.00002)
    fields["BARC CentralFarm 1-7"] = outline.wkt
    return fields


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config()
    rows, comp_tables = [], []
    for name, wkt in _test_fields(cfg).items():
        vals, comps = query_field(wkt, cfg)
        rows.append({"field": name, **vals})
        comp_tables.append(comps.assign(field=name))
    table = pd.DataFrame(rows)
    print(table.round(3).to_string(index=False))
    comps = pd.concat(comp_tables).drop_duplicates(["mukey", "cokey"])
    print("\nKomponenten (Map-Units der Testfelder):")
    print(comps.drop(columns="field").to_string(index=False))
    s = cfg["ssurgo"]
    print("\nAbdeckung je Bodenkarte (Hauptkomponenten):")
    print(sda_query(coverage_sql(s["survey_areas"], s["crop_name"], s["nccpi_corn_rule"]), s["sda_url"]).to_string(index=False))


if __name__ == "__main__":
    main()
