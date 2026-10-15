"""One Acre Fund inspection helpers on a small synthetic survey table."""

import math

import numpy as np
import pandas as pd

from croptransfer.one_acre_fund import (
    SOIL_COLUMNS,
    damage_rates,
    exact_location,
    likely_not_asked,
    max_decimals,
    neighbour_groups,
    prefilter,
    rounding_error_m,
)


def _survey(n_exact=3, n_town=2, with_size=False):
    n = n_exact + n_town
    df = pd.DataFrame({
        "country": ["kenya"] * n,
        "year": [2019] * n,
        "season": ["first season"] * n,
        "cz": [7701] * n,
        "lon": [34.067, 34.1, 34.08, 34.5, 34.5][:n],
        "lat": [0.227, 0.2, 0.25, 0.3, 0.3][:n],
        "pest": [True, False, False, False, False][:n],
        "water_excess": [False] * n,
    })
    for col in SOIL_COLUMNS:
        df[col] = [1.0] * n_exact + [np.nan] * n_town
    if with_size:
        df["field_size_ha"] = [0.3, 0.6, 1.0, 2.0, 2.0][:n]
    return df


def test_exact_location_needs_all_soil_columns():
    df = _survey()
    df.loc[0, "soil_pH"] = np.nan  # one missing soil value -> not exact
    assert exact_location(df).tolist() == [False, True, True, False, False]


def test_prefilter_reports_missing_field_size_as_nan():
    steps = prefilter(_survey(), 0.5)
    assert steps["n"].tolist()[:2] == [5, 3]
    assert math.isnan(steps["n"].iloc[2])


def test_prefilter_applies_field_size_when_present():
    steps = prefilter(_survey(with_size=True), 0.5)
    assert steps["n"].tolist() == [5, 3, 2]  # exact fields with 0.6 and 1.0 ha


def test_max_decimals_and_rounding_error():
    assert max_decimals(pd.Series([34.067, 34.1, 34.0])) == 3
    ns, ew = rounding_error_m(3, lat_deg=0.0)
    assert round(ns) == 56 and round(ew) == 56
    _, ew60 = rounding_error_m(3, lat_deg=60.0)
    assert math.isclose(ew60, ew / 2, rel_tol=1e-6)


def test_damage_rates_and_not_asked_flag():
    rates = damage_rates(_survey(), ["pest", "water_excess"])
    assert rates.loc[("kenya", 2019), "pest"] == 0.2
    flags = likely_not_asked(rates)
    assert not flags.loc[("kenya", 2019), "pest"]
    assert flags.loc[("kenya", 2019), "water_excess"]


def test_neighbour_groups_need_min_other_fields():
    df = _survey()
    assert neighbour_groups(df, min_other=4).sum() == 5   # 5 fields = 1 + 4 others
    assert neighbour_groups(df, min_other=5).empty
