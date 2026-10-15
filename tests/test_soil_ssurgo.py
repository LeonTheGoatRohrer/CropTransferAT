"""SSURGO aggregation (component -> map unit -> field) and SQL builders, offline."""

import math

import pandas as pd
import pytest

from croptransfer.soil_ssurgo import component_values_sql, field_value, mapunit_areas_sql, mapunit_values

COLS = ["nonirryield_r", "nccpi_corn"]


def _components():
    # map unit 1: like KBS "KaB" - only a 1 % minor component has a corn yield
    # map unit 2: two major components with values, one minor without
    return pd.DataFrame({
        "mukey": ["1", "1", "2", "2", "2"],
        "comppct_r": ["99", "1", "40", "40", "20"],
        "nonirryield_r": [None, "120", "100", "140", None],
        "nccpi_corn": ["0.6", "0.8", "0.5", "0.7", None],
    })


def test_mapunit_values_weight_by_component_percent():
    mu = mapunit_values(_components(), COLS)
    assert mu.loc["1", "nonirryield_r"] == 120 and mu.loc["1", "nonirryield_r_pct"] == 1
    assert mu.loc["2", "nonirryield_r"] == pytest.approx(120.0)
    assert mu.loc["1", "nccpi_corn"] == pytest.approx(0.6 * 0.99 + 0.8 * 0.01)
    assert mu.loc["2", "nccpi_corn_pct"] == 80


def test_field_value_area_weighted_and_coverage_rule():
    mu = mapunit_values(_components(), COLS)
    areas = pd.DataFrame({"mukey": ["1", "2"], "area": [3.0, 1.0]})
    res = field_value(areas, mu, COLS, min_comp_pct=50)
    # corn yield: only 0.75*1 + 0.25*80 = 20.75 % of the field has a value -> NaN
    assert res["nonirryield_r_comp_pct"] == pytest.approx(20.75)
    assert math.isnan(res["nonirryield_r"])
    # NCCPI: coverage 0.75*100 + 0.25*80 = 95 %
    expected = (0.75 * (0.6 * 0.99 + 0.8 * 0.01) + 0.25 * 0.6)
    assert res["nccpi_corn"] == pytest.approx(expected)
    assert res["n_mapunits"] == 2
    # without the rule the minor-component value would be used
    assert field_value(areas, mu, COLS)["nonirryield_r"] == pytest.approx(120.0)


def test_sql_builders():
    sql = mapunit_areas_sql("POLYGON ((0 0, 1 0, 1 1, 0 0))")
    assert "STIntersects" in sql and "4326" in sql and "GROUP BY mukey" in sql
    sql = component_values_sql(["187069", "2455269"], "Corn", "NCCPI ver", "Corn sub")
    assert "'187069','2455269'" in sql
    assert "cropname = 'Corn'" in sql and "rulename = 'Corn sub'" in sql
    with pytest.raises(ValueError):
        component_values_sql(["1; DROP TABLE x"], "Corn", "a", "b")


def test_coverage_sql_only_accepts_plain_area_symbols():
    from croptransfer.soil_ssurgo import coverage_sql
    sql = coverage_sql(["MI077", "MD033", "x'; --"], "Corn", "NCCPI - NCCPI Corn Submodel (I)")
    assert "'MI077','MD033'" in sql and "--" not in sql.split("IN (")[-1]
