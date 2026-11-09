"""Fourth Austria test: cleaning rules and metric helpers on synthetic data (no real yield is read)."""

import numpy as np
import pandas as pd

from croptransfer import at_test4

T4 = {"plausible_t_ha": [1.5, 16.0], "min_share_code": 0.9, "min_area_ha": 1.0, "moisture_range": [0.10, 0.40]}


def _raw():
    return pd.DataFrame({
        "field_id": [1, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "total_kg": [20000, 20000, 46122, 46122, 30000, 30000.5, 10, 9000, 5000, np.nan],
        "moisture": [0.20, 0.20, 0.21, 0.21, 0.25, 0.0, 0.2, 0.2, 0.2, 0.2]})


def test_clean_rules_in_order():
    area = pd.Series({1: 2.0, 2: 1.0, 3: 1.1, 4: 3.0, 5: 3.0, 6: 2.0, 7: 0.5, 8: 1.0, 9: 2.0})
    share = pd.Series({1: 1.0, 2: 1.0, 3: 1.0, 4: 0.2, 5: 0.95, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0})
    cell = pd.Series({1: "a", 2: "b", 3: "b", 4: "c", 5: "c", 6: "d", 7: "d", 8: "e", 9: "e"})
    d = at_test4.clean(_raw(), area, share, cell, T4).set_index("field_id")
    assert len(d) == 9                                       # exact duplicate of field 1 counted once
    assert d.loc[1, "drop"] == "" and d.loc[1, "y_t_ha"] == 10.0
    assert d.loc[2, "drop"] == d.loc[3, "drop"] == "same_total_nearby"
    assert d.loc[4, "drop"] == "not_grain_maize"
    assert d.loc[5, "drop"] == ""                            # 30000.5 is not the same total as 30000
    assert d.loc[6, "drop"] == "implausible_yield"
    assert d.loc[7, "drop"] == "area_below_min"
    assert d.loc[8, "drop"] == ""
    assert d.loc[9, "drop"] == "no_yield"
    assert np.isnan(d.loc[5, "y14_t_ha"])                    # moisture 0 = missing -> no correction
    assert abs(d.loc[1, "y14_t_ha"] - 10.0 * 0.8 / 0.86) < 1e-12


def test_conflicting_duplicates_are_dropped():
    raw = pd.DataFrame({"field_id": [1, 1], "total_kg": [20000, 25000], "moisture": [0.2, 0.2]})
    d = at_test4.clean(raw, pd.Series({1: 2.0}), pd.Series({1: 1.0}), pd.Series({1: "a"}), T4)
    assert (d["drop"] == "conflicting_duplicate").all()


def test_same_total_far_apart_is_kept():
    raw = pd.DataFrame({"field_id": [1, 2], "total_kg": [5000.0, 5000.0], "moisture": [0.2, 0.2]})
    d = at_test4.clean(raw, pd.Series({1: 1.0, 2: 1.0}), pd.Series({1: 1.0, 2: 1.0}), pd.Series({1: "a", 2: "z"}), T4)
    assert (d["drop"] == "").all()                           # round numbers in different regions are coincidence


def test_problem_overlap_perfect_and_rho_diff_zero_for_identical():
    y = np.arange(100, dtype=float)
    r = at_test4.problem_overlap(y, y, 0.2)
    assert r["flagged"] == 20 and r["hit_rate"] == 1.0
    cl = np.repeat(np.arange(10), 10)
    d = at_test4.rho_diff_ci(y, y, y, cl, 50, 42)
    assert d["diff"] == 0.0 and d["lo"] == 0.0 and d["hi"] == 0.0
