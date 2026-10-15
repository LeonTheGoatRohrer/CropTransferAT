import geopandas as gpd
from shapely.geometry import box

from croptransfer import groundtruth as gt


def test_iou():
    assert gt.iou(box(0, 0, 10, 10), box(0, 0, 10, 10)) == 1.0
    assert gt.iou(box(0, 0, 10, 10), box(5, 0, 15, 10)) == 50 / 150
    assert gt.iou(box(0, 0, 1, 1), box(5, 5, 6, 6)) == 0.0


def test_assign_field_uid_matches_over_years():
    g = gpd.GeoDataFrame(dict(
        dataset=["D"] * 5, field_id=["a", "a2", "b", "a_shift", "c"],
        year=[2014, 2016, 2014, 2019, 2016],
        geometry=[box(0, 0, 100, 100), box(2, 2, 100, 100),     # same field, renamed
                  box(500, 0, 600, 100),                         # other field
                  box(40, 0, 140, 100),                          # IoU 0.43 -> new field
                  box(498, 0, 600, 100)]))                       # matches b
    uid = gt.assign_field_uid(g, 0.7)
    assert uid[0] == uid[1] == "D:a"
    assert uid[2] == uid[4] == "D:b"
    assert uid[3] == "D:a_shift"


def test_same_year_never_merged():
    g = gpd.GeoDataFrame(dict(dataset=["D", "D"], field_id=["x", "y"], year=[2014, 2014],
                              geometry=[box(0, 0, 10, 10), box(0, 0, 10, 10)]))
    uid = gt.assign_field_uid(g, 0.7)
    assert uid[0] != uid[1]
