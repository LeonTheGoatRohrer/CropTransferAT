"""INVEKOS schema/count helpers on a tiny synthetic GeoPackage."""

import geopandas as gpd
import pytest
from shapely.geometry import box

from croptransfer.invekos import count_in_state, crop_code_counts, find_gpkgs, schema


@pytest.fixture
def gpkg(tmp_path):
    year_dir = tmp_path / "invekos" / "2025"
    year_dir.mkdir(parents=True)
    gdf = gpd.GeoDataFrame(
        {
            "SNAR_CODE": ["105", "105", "109", "140"],
            "SNAR_BEZEICHNUNG": ["KÖRNERMAIS", "KÖRNERMAIS", "SILOMAIS", "WINTERWEICHWEIZEN"],
            "SL_FLAECHE_BRUTTO_HA": [0.5, 2.0, 1.5, 3.0],
        },
        geometry=[box(0, 0, 1, 1)] * 4,
        crs="EPSG:31287",
    )
    path = year_dir / "inspire_schlaege_2025-2_polygon.gpkg"
    gdf.to_file(path, driver="GPKG")
    return tmp_path / "invekos", path


def test_find_gpkgs(gpkg):
    root, path = gpkg
    assert find_gpkgs(root) == {2025: path}


def test_schema(gpkg):
    s = schema(gpkg[1])
    assert s["features"] == 4
    assert "SNAR_CODE" in s["columns"]


def test_crop_code_counts(gpkg):
    c = crop_code_counts(gpkg[1], {"105": "koernermais", "109": "silomais", "106": "ccm"})
    assert c.loc["105", "n"] == 2
    assert c.loc["105", "area_ha"] == pytest.approx(2.5)
    assert c.loc["105", "n_ge_1ha"] == 1
    assert c.loc["109", "name"] == "SILOMAIS"
    assert c.loc["106", "n"] == 0  # absent code is reported as zero, not dropped


def test_count_in_state(gpkg):
    # Two municipalities: 60101 (Styria) covers x 0..1, 30101 (Lower Austria) x 1..2.
    gem = gpd.GeoDataFrame({"g_id": ["60101", "30101"]},
                           geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)], crs="EPSG:31287")
    r = count_in_state(gpkg[1], gem, code="105")
    assert r["n_austria"] == 2 and r["n"] == 2 and r["unmatched"] == 0
    assert r["area_ha"] == pytest.approx(2.5) and r["n_ge_min_area"] == 1
    assert count_in_state(gpkg[1], gem, code="105", state_prefix="3")["n"] == 0
