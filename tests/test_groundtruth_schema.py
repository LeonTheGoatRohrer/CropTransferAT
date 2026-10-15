import numpy as np
import pytest

from croptransfer import groundtruth as gt


def test_moisture_conversion():
    # 14 % basis -> 15.5 %: more water at the standard -> higher yield
    assert gt.to_standard_moisture(10.0, 0.14) == pytest.approx(10.0 * 0.86 / 0.845)
    assert gt.to_standard_moisture(10.0, 0.155) == pytest.approx(10.0)


def test_bu_ac_factor():
    # 150 bu/ac at 15.5 % = 9.4155 t/ha
    assert 150 * gt.BU_AC_TO_KG_HA / 1000 == pytest.approx(9.4155, abs=1e-4)


def test_clean_points_range_and_sd():
    v = np.array([0.5, 8, 8.1, 7.9, 8.2, 7.8, 30.0] + [8.0] * 20 + [14.0])
    keep = gt.clean_points(v, (1.0, 25.0), 3.0)
    assert not keep[0] and not keep[6]       # outside 1-25 t/ha
    assert not keep[-1]                      # > 3 SD
    assert keep[1:6].all()


def test_barc_field_key_normalises_names():
    assert gt.barc_field_key("2014/6C/USDA_Central_Farm_1_7_2014_CORN_clip.tif") == ("CentralFarm_1_7", "CORN")
    assert gt.barc_field_key("2019/6/EastFarm_5_3A_2019_Corn_Clip.tif") == ("EastFarm_5_3A", "CORN")
    assert gt.barc_field_key("x/USDA_APU_5_2016_Soybeans_clip.tif") == ("APU_5", "SOYBEANS")


def test_sensor_era():
    assert gt.sensor_era(2012) == "L57" and gt.sensor_era(2013) == "HLS"


def test_schema_columns():
    for c in ["dataset", "field_uid", "year", "Y_t_ha", "moisture_basis", "irrigated", "sensor_era", "geometry"]:
        assert c in gt.FIELD_YEAR_COLUMNS
