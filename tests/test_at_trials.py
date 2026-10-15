"""Schema checks of the Austrian trial table on synthetic rows (no real yields)."""

import pandas as pd
import pytest

from croptransfer.at_trials import COLUMNS, build, validate

RANGE = (1.0, 20.0)


def _row(**kw):
    row = dict(site="Wagna", bundesland="Steiermark", lat=None, lon=None, loc_precision="municipality",
               year=2020, yield_t_ha=10.0, moisture_basis=0.14, trial_type="duengung",
               variant="Versuchsmittel", sowing_date="2020-04-20", harvest_date="2020-10-05",
               source_pdf="x.pdf", page=3, notes=None)
    row.update(kw)
    return row


def _df(*rows):
    return pd.DataFrame(list(rows), columns=COLUMNS)


def test_valid_table_has_no_problems():
    assert validate(_df(_row(), _row(year=2021, sowing_date=None, harvest_date=None)), RANGE) == []


@pytest.mark.parametrize("kw, msg", [
    (dict(yield_t_ha=100.0), "outside"),          # dt/ha not converted
    (dict(moisture_basis=14), "fraction"),
    (dict(loc_precision="gps"), "loc_precision"),
    (dict(sowing_date="20.04.2020"), "ISO"),
    (dict(harvest_date="2019-10-05"), "year differs"),
])
def test_validate_catches_errors(kw, msg):
    problems = validate(_df(_row(**kw)), RANGE)
    assert any(msg in p for p in problems)


def test_duplicate_key_and_wrong_columns():
    assert any("duplicate" in p for p in validate(_df(_row(), _row()), RANGE))
    assert "columns differ" in validate(pd.DataFrame({"a": [1]}), RANGE)[0]


def test_build_merges_sources(tmp_path):
    src = tmp_path / "at_trials"
    src.mkdir()
    _df(_row()).to_csv(src / "a.csv", index=False)
    _df(_row(site="Grieskirchen", bundesland="Oberösterreich", trial_type="sorten",
             variant="Standortmittel")).to_csv(src / "b.csv", index=False)
    out = build(src, tmp_path / "at_trials.csv", RANGE)
    assert len(out) == 2 and (tmp_path / "at_trials.csv").exists()
    assert out["bundesland"].tolist() == ["Oberösterreich", "Steiermark"]
