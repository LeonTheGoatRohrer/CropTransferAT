"""One Acre Fund table analysis on small synthetic surveys (offline, no real data)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import oaf_analysis as A
from croptransfer.one_acre_fund import SOIL_COLUMNS

OC = A.oaf_config()
ALL_COLS = [c for cols in OC["subgroups"].values() for c in cols]


def survey(spec, seed=0, extra_nan_soil=0):
    """spec: list of (country, year, season, cz, n_fields). All columns the analysis needs."""
    rng = np.random.default_rng(seed)
    rows = []
    for country, year, season, cz, n in spec:
        for _ in range(n):
            rows.append({"country": country, "year": year, "season": season, "cz": cz})
    df = pd.DataFrame(rows)
    n = len(df)
    df["yield_kg_ha"] = rng.uniform(1000, 4000, n)
    df["lon"], df["lat"] = rng.uniform(30, 35, n), rng.uniform(-2, 2, n)
    for c in ALL_COLS:
        if c not in df:
            df[c] = rng.normal(size=n)
    for c in SOIL_COLUMNS:
        df[c] = rng.normal(size=n)
    for c in OC["damage_columns"]:
        df[c] = rng.random(n) < 0.3
    df["hyb_type"] = rng.choice(["3_way_hyb", "double_cross", None], n)
    df["weeding"] = rng.choice([True, False, None], n)
    if extra_nan_soil:
        df.loc[: extra_nan_soil - 1, SOIL_COLUMNS[0]] = np.nan   # not an exact position
    return df


# ---- RY_nb grouping --------------------------------------------------------------------------
def test_ry_nb_group_median_excludes_own_field_and_small_groups():
    df = survey([("kenya", 2019, "first season", 1, 12), ("kenya", 2019, "first season", 2, 5)])
    df.loc[:11, "yield_kg_ha"] = np.arange(1, 13) * 100.0
    frame, info = A.analysis_frame(df, OC)
    assert info["n_exact"] == 17 and info["n_ry_nb"] == 12          # group of 5 has < 10 others -> dropped
    assert info["n_exact_without_group"] == 5
    first = frame.iloc[0]                                             # yield 100, others 200..1200
    assert first["RY_nb"] == pytest.approx(100 / np.median(np.arange(2, 13) * 100.0))
    assert frame["RY_nb"].notna().all()


def test_non_exact_fields_are_excluded_before_grouping():
    df = survey([("kenya", 2019, "first season", 1, 12)], extra_nan_soil=2)
    frame, info = A.analysis_frame(df, OC)
    # 10 exact fields -> 9 others < 10 -> no RY_nb at all
    assert info["n_exact"] == 10 and info["n_ry_nb"] == 0


def test_group_straddling_countries_is_detected_and_country_group_removes_it():
    df = survey([("kenya", 2019, "first season", 1, 8), ("tanzania", 2019, "first season", 1, 8)])
    frame, info = A.analysis_frame(df, OC)
    assert info["n_groups_straddling_countries"] == 1 and info["n_ry_nb"] == 16
    frame2, info2 = A.analysis_frame(df, OC, OC["sensitivity_group_cols"])
    assert info2["n_groups_straddling_countries"] == 0 and info2["n_ry_nb"] == 0   # 8 per country < 11


# ---- "question not asked" --------------------------------------------------------------------
def test_country_year_with_zero_share_is_treated_as_missing():
    df = survey([("kenya", 2016, "first season", 1, 12), ("kenya", 2017, "first season", 1, 12)])
    df["pest"] = [False] * 12 + [True] * 6 + [False] * 6             # 2016: share exactly 0
    df["striga"] = np.nan                                             # never answered
    df["disease"] = [True, False] * 12
    frame, _ = A.analysis_frame(df, OC)
    y16, y17 = frame[frame.year == 2016], frame[frame.year == 2017]
    assert y16["pest"].isna().all()                                   # not asked -> NaN, not "False"
    assert y17["pest"].notna().all() and y17["pest"].sum() == 6
    assert frame["striga"].isna().all()
    assert frame["disease"].notna().all()


def test_damage_association_ignores_not_asked_rows():
    df = survey([("kenya", 2016, "first season", 1, 40), ("kenya", 2017, "first season", 1, 40)], seed=3)
    frame, _ = A.analysis_frame(df, OC)
    frame["pest"] = np.where(frame["RY_nb"] < 0.85, 1.0, 0.0)         # perfectly linked to low RY_nb
    frame.loc[frame.year == 2016, "pest"] = np.nan                    # not asked in 2016
    frame["striga"] = np.nan
    out = A.damage_association(frame, {**OC, "n_boot": 30})
    assert out["pest"]["n"] == int((frame.year == 2017).sum())
    assert out["pest"]["share_with"][0] == 1.0 and out["pest"]["share_without"][0] == 0.0
    assert out["pest"]["or_crude"][0] > 100                           # Haldane keeps it finite
    assert out["striga"]["note"]                                      # all-NaN column -> reported, not crashed


# ---- odds ratios -----------------------------------------------------------------------------
def test_odds_ratio_hand_example_and_zero_cell():
    assert A.odds_ratio(10, 5, 20, 40) == pytest.approx(4.0)
    assert A.odds_ratio(10, 0, 20, 40) == pytest.approx((10.5 * 40.5) / (0.5 * 20.5))


def test_mantel_haenszel_equals_common_or_for_identical_strata():
    # two strata, each with a=10,b=5,c=20,d=40 -> common OR 4
    strata = np.repeat([0, 1], 75)
    risk = np.concatenate([np.repeat([1, 1, 0, 0], [10, 5, 20, 40])] * 2).astype(float)
    rep = np.concatenate([np.repeat([1, 0, 1, 0], [10, 5, 20, 40])] * 2).astype(float)
    assert A.mantel_haenszel_or(strata, risk, rep) == pytest.approx(4.0)


# ---- splits: no overlap ----------------------------------------------------------------------
def test_leave_one_group_out_has_no_overlap_and_covers_everything():
    g = np.array(["a", "a", "b", "c", "c", "c"])
    folds = A.leave_one_group_out(g)
    assert len(folds) == 3
    seen = np.concatenate([te for _, te, _ in folds])
    assert sorted(seen) == list(range(6))
    for tr, te, label in folds:
        assert not set(tr) & set(te)
        assert set(g[te]) == {label} and label not in set(g[tr])


def test_nested_cv_never_tunes_on_the_held_out_group(monkeypatch):
    rng = np.random.default_rng(1)
    g = np.repeat(["a", "b", "c", "d"], 40)
    X = rng.normal(size=(160, 3))
    y = X[:, 0] + 0.1 * rng.normal(size=160)
    seen = []
    orig = A._inner_scores

    def spy(kind, Xtr, ytr, gtr, oc, seed):
        seen.append(set(gtr))
        return orig(kind, Xtr, ytr, gtr, oc, seed)

    monkeypatch.setattr(A, "_inner_scores", spy)
    out = A.nested_oof(X, y, g, "ridge", OC)
    assert len(seen) == 4 and all(len(s) == 3 for s in seen)           # inner loop sees 3 of 4 groups only
    assert {tuple(sorted(s)) for s in seen} == {("b", "c", "d"), ("a", "c", "d"), ("a", "b", "d"), ("a", "b", "c")}
    assert np.isfinite(out["pred"]).all()
    assert out["base"][g == "a"][0] == pytest.approx(y[g != "a"].mean())   # B0 = training mean only


# ---- models recover signal, shuffle control falls to chance ---------------------------------
def test_models_find_signal_and_shuffle_control_is_at_chance():
    rng = np.random.default_rng(2)
    g = np.repeat(np.arange(5), 120)
    X = rng.normal(size=(600, 4))
    y = X[:, 0] + 0.3 * rng.normal(size=600)
    small = {**OC, "lgbm": {**OC["lgbm"], "n_estimators_grid": [50, 100], "min_child_samples_grid": [20]},
             "ridge_alpha_grid": [1.0, 100.0]}
    for kind in ("ridge", "lgbm"):
        real = A.nested_oof(X, y, g, kind, small)["pred"]
        shuf = A.nested_oof(X, rng.permutation(y), g, kind, small)["pred"]
        assert A._metrics(y, real)["rho"] > 0.7
        assert abs(A._metrics(rng.permutation(y), shuf)["rho"]) < 0.15


# ---- bootstrap, features ---------------------------------------------------------------------
def test_bootstrap_paired_difference_of_identical_predictions_is_zero():
    rng = np.random.default_rng(0)
    y = rng.normal(size=200)
    p = y + rng.normal(size=200)
    clusters = np.repeat(np.arange(10), 20)
    s = A.bootstrap_summary(y, {"a": p, "b": p.copy()}, clusters, base=np.zeros(200), pairs=[("a", "b")], n_boot=40)
    d = s["diffs"]["a - b"]["rho"]
    assert d == [0.0, 0.0, 0.0]
    lo, hi = s["models"]["a"]["rho"][1:]
    assert lo <= s["models"]["a"]["rho"][0] <= hi and s["models"]["a"]["n_clusters"] == 10


def test_design_matrix_keeps_nan_and_sets_are_consistent():
    df = survey([("kenya", 2019, "first season", 1, 12)])
    frame, _ = A.analysis_frame(df, OC)
    X, owner = A.design_matrix(frame, OC["subgroups"])
    assert frame["hyb_type"].isna().sum() == X["hyb_type_3_way_hyb"].isna().sum() > 0
    assert X["weeding"].isin([0.0, 1.0, np.nan]).all()
    sets = A.feature_sets(owner, OC)
    assert not set(sets["ORT"]) & set(sets["alle"])                     # location proxy stays outside "alle"
    for g in "MBWS":
        assert not set(sets[g]) & set(sets[f"ohne_{g}"])
        assert set(sets[g]) | set(sets[f"ohne_{g}"]) == set(sets["alle"])
