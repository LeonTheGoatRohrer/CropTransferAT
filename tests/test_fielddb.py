"""Path A (reference without training) and input validation (DECISIONS 2026-10-17)."""
from datetime import date

import pytest

from croptransfer import fielddb as db


def test_units_and_range():
    assert db.to_t_ha(95, "dt/ha") == pytest.approx(9.5)
    assert db.to_t_ha(9.5, "t/ha") == 9.5
    for bad in [(0, "t/ha"), (26, "t/ha"), (300, "dt/ha"), (-1, "dt/ha")]:
        with pytest.raises(ValueError):
            db.to_t_ha(*bad)
    with pytest.raises(ValueError):
        db.to_t_ha(9, "bu/ac")


def test_validate_entries_years():
    rows = db.validate_entries([{"year": 2020, "value": 9}, {"year": 2019, "value": 10}], "t/ha", date(2026, 10, 17))
    assert [r[0] for r in rows] == [2019, 2020]
    with pytest.raises(ValueError):
        db.validate_entries([{"year": 2020, "value": 9}, {"year": 2020, "value": 8}], "t/ha")
    with pytest.raises(ValueError):
        db.validate_entries([{"year": 2030, "value": 9}], "t/ha", date(2026, 10, 17))


def test_history_levels():
    assert db.history_level(2) == "too_little"
    assert db.history_level(3) == "with_hint"
    assert db.history_level(4) == "with_hint"
    assert db.history_level(5) == "ok"


def test_baseline_uses_other_years_only():
    y = {2019: 10.0, 2020: 12.0, 2021: 8.0, 2022: 10.0, 2023: 6.0}
    b = db.baseline(y, 2023, hint_pct=20, warn_pct=30)
    assert b["normal_t_ha"] == pytest.approx(10.0)      # mean of 2019-2022, not of all years
    assert b["ry"] == pytest.approx(0.6)
    assert b["history"] == "with_hint"                   # 4 other years
    assert b["state"] == "warning"                       # 0.6 < 0.7
    assert b["hint_below_t_ha"] == pytest.approx(8.0)
    assert b["warning_below_t_ha"] == pytest.approx(7.0)


def test_baseline_hint_and_normal_states():
    y = {2018: 10.0, 2019: 10.0, 2020: 10.0, 2021: 10.0, 2022: 10.0, 2023: 7.5}
    assert db.baseline(y, 2023, 20, 30)["state"] == "hint"
    y[2023] = 9.5
    b = db.baseline(y, 2023, 20, 30)
    assert b["state"] == "normal" and b["history"] == "ok"


def test_baseline_too_little_history_gives_no_assessment():
    b = db.baseline({2021: 9.0, 2022: 10.0, 2023: 4.0}, 2023, 20, 30)
    assert b["history"] == "too_little" and b["state"] == "no_assessment" and b["ry"] is None


def test_baseline_pending_without_current_yield():
    b = db.baseline({2019: 9.0, 2020: 10.0, 2021: 11.0}, 2024, 20, 30)
    assert b["state"] == "pending" and b["normal_t_ha"] == pytest.approx(10.0) and b["yield_t_ha"] is None


def test_store_roundtrip(tmp_path):
    s = db.Store(tmp_path / "t.sqlite")
    f = s.create_field("Feld 1", {"type": "Polygon", "coordinates": [[[15, 47], [15.01, 47], [15.01, 47.01], [15, 47]]]}, 1e5)
    s.set_yields(f["id"], "dt/ha", [{"year": 2020, "value": 100}, {"year": 2021, "value": 80}])
    assert [r["t_ha"] for r in s.get_yields(f["id"])] == pytest.approx([10.0, 8.0])
    s.set_alert(f["id"], "09-01", 20, 30)
    assert s.get_alert(f["id"])["warn_pct"] == 30
    assert s.delete_field(f["id"]) and s.get_yields(f["id"]) == []
