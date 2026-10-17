"""Validation and storage of the website's contribution backend."""

import copy

import pytest

from croptransfer import contrib_server as cs

# about 300 m x 330 m near Leibnitz (Styria)
RING = [[15.55, 46.78], [15.554, 46.78], [15.554, 46.783], [15.55, 46.783], [15.55, 46.78]]
GOOD = {
    "consent": True,
    "polygon": {"type": "Polygon", "coordinates": [RING]},
    "fieldName": "Acker",
    "cropType": "grain",
    "irrigated": False,
    "pastYields": [{"year": 2024, "tPerHa": 10.1}, {"year": 2025, "tPerHa": 11.0}],
    "thisYear": {"year": 2026, "tPerHa": 9.5, "status": "harvested"},
}
TINY = [[15.55, 46.78], [15.5501, 46.78], [15.5501, 46.7801], [15.55, 46.78]]
MARYLAND = [[-76.8, 39.0], [-76.79, 39.0], [-76.79, 39.01], [-76.8, 39.0]]


def bad(**kw):
    b = copy.deepcopy(GOOD)
    b.update(kw)
    return b


def test_valid_record_is_cleaned():
    r = cs.validate(GOOD)
    assert r["crop_type"] == "grain" and 3_000 < r["area_m2"] < 2_000_000 and len(r["past_yields"]) == 2


@pytest.mark.parametrize(
    "body",
    [
        bad(consent=False),
        bad(cropType="wheat"),
        bad(pastYields=[{"year": 2024, "tPerHa": 99}], thisYear=None),
        bad(pastYields=[{"year": 2024, "tPerHa": 5}, {"year": 2024, "tPerHa": 6}]),
        bad(pastYields=[], thisYear=None),
        bad(polygon={"type": "Polygon", "coordinates": [MARYLAND]}),
        bad(polygon={"type": "Polygon", "coordinates": [TINY]}),
    ],
)
def test_invalid_records_rejected(body):
    with pytest.raises(cs.Invalid):
        cs.validate(body)


def test_store_roundtrip(tmp_path):
    db = cs.connect(tmp_path / "c.sqlite")
    full = cs.store(db, cs.validate(GOOD))
    assert [r["id"] for r in cs.list_all(db)] == [full["id"]]


def test_rate_limit():
    cs._hits.clear()
    assert not any(cs.rate_limited("x", now=1000.0) for _ in range(cs.RATE_LIMIT[0]))
    assert cs.rate_limited("x", now=1001.0)
    assert not cs.rate_limited("x", now=1000.0 + cs.RATE_LIMIT[1] + 1)
