"""Austria test machinery: vectorised score == reference implementation, YAS_site rules, trial aggregation."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import at_test, stress
from croptransfer.config import load_config, repo_path


def _ref():
    return pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]


def test_vectorised_score_matches_reference_implementation():
    dek = pd.read_parquet(repo_path("data/processed/gt_dekads.parquet"))
    d = dek[(dek.basis == "HLS") & (dek["index"] == "ndvi")]
    keys = sorted(d.fy_key.unique())[:60]
    obs = d[d.fy_key.isin(keys) & d.is_observed]
    mat = obs.pivot_table(index="fy_key", columns="dekad", values="value").reindex(columns=range(21))
    ref = _ref()
    for cutoff in ["07-15", "09-01"]:
        got = at_test.scores_from_matrix(mat, ref, cutoff, 6, 1)["score"]
        for k in keys:
            want = stress.stress_score(d, k, ref, cutoff, basis="HLS")
            if np.isnan(want):
                assert np.isnan(got.get(k, np.nan))
            else:
                assert got[k] == pytest.approx(want, abs=1e-12)


def test_min_observed_dekads_rule():
    ref = _ref()
    mat = pd.DataFrame(np.nan, index=["a", "b"], columns=range(21))
    mat.loc["a", [6, 7, 8]] = 0.1
    mat.loc["b", [6, 7, 8, 9]] = 0.1
    s = at_test.scores_from_matrix(mat, ref, "09-01", 6, 4)["score"]
    assert np.isnan(s["a"]) and np.isfinite(s["b"])


def test_score_is_never_positive_and_higher_when_closer_to_reference():
    ref = _ref()
    mat = pd.DataFrame({d: [ref[d], ref[d] - 0.2, ref[d] + 0.3] for d in range(21)}, index=["ref", "low", "high"])
    s = at_test.scores_from_matrix(mat, ref, "09-01", 6, 4)["score"]
    assert s["ref"] == 0 and s["high"] == 0 and s["low"] == pytest.approx(-0.2)


def test_yas_site_rules():
    y = pd.DataFrame({"site": "x", "year": list(range(2012, 2019)), "y_t_ha": [10, 9, 11, 12, 8, 10, 11.0]})
    r = at_test.yas_site(y).set_index("year")
    # 2018: five complete previous years 2013..2017 -> olympic mean of [9, 11, 12, 8, 10] = 10
    assert r.loc[2018, "baseline_kind"] == "prior5" and r.loc[2018, "yas_site"] == pytest.approx(1.1)
    # 2013: no five previous years -> mean of the six other years, flagged
    assert r.loc[2013, "baseline_kind"] == "baseline_short"
    assert r.loc[2013, "baseline"] == pytest.approx(np.mean([10, 11, 12, 8, 10, 11]))


def test_yas_site_needs_three_other_years():
    y = pd.DataFrame({"site": "x", "year": [2018, 2019, 2020], "y_t_ha": [10.0, 11.0, 12.0]})
    assert at_test.yas_site(y).yas_site.isna().all()


def test_trial_yield_aggregation(tmp_path):
    cfg = load_config()
    rows = [
        ("Wagna", 2019, 10.0, "sorten", "Standortmittel"), ("Wagna", 2019, 99.0, "sorten", "RZ 300"),
        ("Wagna", 2019, 12.0, "praxisversuch_sorten", "früh"), ("Wagna", 2019, 14.0, "praxisversuch_sorten", "spät"),
        ("Wagna", 2019, 5.0, "duengung", "Versuchsmittel"),
        ("Hatzendorf", 2019, 8.0, "sorten", "Standortmittel"), ("Unterhatzendorf (Hatzendorf)", 2019, 10.0, "sorten", "Standortmittel"),
    ]
    p = tmp_path / "t.csv"
    pd.DataFrame(rows, columns=["site", "year", "yield_t_ha", "trial_type", "variant"]).to_csv(p, index=False)
    y = at_test.trial_yields(cfg, p).set_index(["site", "year"]).y_t_ha
    assert y[("wagna", 2019)] == pytest.approx((10.0 + 13.0) / 2)    # Standortmittel; mean of variants; Düngung ignored
    assert y[("hatzendorf", 2019)] == pytest.approx(9.0)             # aliases of one cluster averaged


def test_rho_ci_flags_small_samples():
    cfg = load_config()
    m = at_test.rho_ci([1, 2, 3], [1, 2, 3], [1, 1, 2], cfg)
    assert np.isnan(m["rho"])
    assert at_test.passed({"rho": 0.5, "lo": 0.1, "n": 20}, 15) == "bestanden"
    assert at_test.passed({"rho": 0.5, "lo": -0.1, "n": 20}, 15) == "nicht belegt"
    assert at_test.passed({"rho": 0.5, "lo": 0.1, "n": 10}, 15) == "nicht auswertbar"
