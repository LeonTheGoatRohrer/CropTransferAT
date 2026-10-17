"""Offline tests for the pre-registered metrics and models of the within-field study (synthetic data)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import innerfeld_run as run


def _cells(n=200, seed=0, signal=1.0, key="A", site="S"):
    rng = np.random.default_rng(seed)
    z = rng.normal(size=n)
    rel = 1.0 + 0.2 * (signal * z + rng.normal(scale=0.5, size=n))
    df = pd.DataFrame(dict(site=site, field_id=key, fy_key=key, year=2020, x=np.arange(n) * 10.0, y=0.0,
                           rel=rel, yield_t_ha=10 * rel, z_b1_ndvi=z))
    for c in run.M1_COLS + run.TERRAIN_COLS:
        df[c] = rng.normal(size=n) if c != "z_m1_ndvi_w2" else z
    df["problem"] = df.rel < run.PROBLEM
    df["zrel"] = (df.rel - df.rel.mean()) / df.rel.std(ddof=0)
    df["field_cluster"] = site + "|" + key
    return df


def test_spearman_known_values():
    a = np.arange(10.0)
    assert run.spearman(a, a * 2) == pytest.approx(1.0)
    assert run.spearman(a, -a) == pytest.approx(-1.0)
    assert np.isnan(run.spearman(a, np.ones(10)))


def test_fy_metrics_lift_and_min_cells():
    rel = np.r_[np.full(8, 0.5), np.full(32, 1.1)]
    pred = np.r_[np.zeros(8), np.ones(32)]                # perfect: low prediction = problem zone
    m = run.fy_metrics(pred, rel, rel < run.PROBLEM)
    assert m["rho"] == pytest.approx(1.0)
    assert m["prevalence"] == pytest.approx(0.2)
    assert m["lift"] == pytest.approx(0.8 / 0.2)           # lowest quarter = 10 cells, 8 of them problem cells
    tiny = run.fy_metrics(pred[:5], rel[:5], rel[:5] < 0.85)
    assert np.isnan(tiny["rho"])


def test_persistence_leave_one_year_out():
    rows = []
    for yr, r in zip((2018, 2019, 2020), (0.8, 1.0, 1.2)):
        rows.append(dict(site="S", field_id="F", x=5.0, y=5.0, rel=r))
    rows.append(dict(site="S", field_id="F", x=15.0, y=5.0, rel=1.0))          # seen in one year only
    out = run.persistence(pd.DataFrame(rows))
    assert out.iloc[:3].tolist() == pytest.approx([1.1, 1.0, 0.9])
    assert np.isnan(out.iloc[3])


def test_fit_predict_learns_signal_and_shuffle_kills_it():
    tr, te = _cells(seed=1, key="A"), _cells(seed=2, key="B")
    p = run.fit_predict(tr, te, run.M1_COLS)
    assert run.spearman(p, te.rel.to_numpy()) > 0.5
    ps = [run.fit_predict(tr, te, run.M1_COLS, shuffle_seed=s) for s in range(10)]
    assert abs(np.mean([run.spearman(q, te.rel.to_numpy()) for q in ps])) < 0.25


def test_fit_predict_weights_field_years_equally():
    a = _cells(n=400, seed=3, key="A", signal=1.0)
    b = _cells(n=20, seed=4, key="B", signal=-1.0)           # small field-year with the opposite sign
    test = _cells(seed=5, key="C")
    alone = run.fit_predict(a, test, ["z_m1_ndvi_w2"])
    both = run.fit_predict(pd.concat([a, b], ignore_index=True), test, ["z_m1_ndvi_w2"])
    assert np.std(both) < 0.5 * np.std(alone)                # equal weights per field-year -> opposite slopes cancel


def test_paired_delta_median_and_descriptive_flag():
    a = pd.DataFrame(dict(fy_key=list("abc"), rho=[0.6, 0.5, 0.7], cluster=["x", "y", "z"]))
    b = pd.DataFrame(dict(fy_key=list("abc"), rho=[0.5, 0.5, 0.5], cluster=["x", "y", "z"]))
    d = run.paired_delta(a, b)
    assert d["delta_median"] == pytest.approx(0.1) and d["descriptive"] is True and "delta_ci" not in d


def test_colorado_regular_rule():
    df = pd.DataFrame(dict(site=["COLORADO", "COLORADO", "BARC"], fy_mean_yield=[0.5, 3.0, 0.1]))
    assert run.colorado_regular(df).tolist() == [False, True, False]
