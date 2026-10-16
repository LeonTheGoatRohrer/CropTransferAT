"""Offline tests for the within-field analysis (synthetic data, no Earth Engine)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import within_field as wf


def _toy():
    rows = []
    for key, vals in {"A": [10.0, 10.0, 5.0, 15.0], "B": [2.0, 4.0, 6.0, 8.0]}.items():
        for i, v in enumerate(vals):
            rows.append(dict(fy_key=key, yield_t_ha=v, x=i, y=0, ndvi=0.5 + 0.1 * i))
    return pd.DataFrame(rows)


def test_relative_yield_is_pixel_over_field_year_mean():
    df = _toy()
    rel = wf.relative_yield(df)
    assert rel[df.fy_key == "A"].tolist() == pytest.approx([1.0, 1.0, 0.5, 1.5])      # mean A = 10
    assert rel[df.fy_key == "B"].tolist() == pytest.approx([0.4, 0.8, 1.2, 1.6])      # mean B = 5
    assert rel.groupby(df.fy_key).mean().tolist() == pytest.approx([1.0, 1.0])


def test_problem_zone_threshold_is_strict_below_085():
    rel = np.array([0.5, 0.849, 0.85, 0.851, 1.2])
    assert wf.problem_zone(rel, 0.85).tolist() == [True, True, False, False, False]


def test_zscore_within_field_year_ignores_other_field_years():
    df = _toy()
    df["const"] = 3.0
    z = wf.zscore_within(df, ["ndvi", "const"])
    for key in ("A", "B"):
        s = z.loc[df.fy_key == key, "z_ndvi"]
        assert s.mean() == pytest.approx(0.0, abs=1e-12)
        assert s.std(ddof=0) == pytest.approx(1.0)
    assert (z["z_const"] == 0).all()                       # constant column -> 0, not NaN
    # a field-year with a completely different level gives the same z-values
    df2 = df.copy()
    df2.loc[df2.fy_key == "B", "ndvi"] += 100
    z2 = wf.zscore_within(df2, ["ndvi"])
    assert z2["z_ndvi"].to_numpy() == pytest.approx(z["z_ndvi"].to_numpy())


def test_zscore_keeps_nan():
    df = _toy()
    df.loc[0, "ndvi"] = np.nan
    z = wf.zscore_within(df, ["ndvi"])
    assert np.isnan(z.loc[0, "z_ndvi"]) and z.loc[1:, "z_ndvi"].notna().all()


def test_leave_one_field_year_out_has_no_overlap_and_covers_all():
    fy = np.array(["a", "a", "b", "b", "b", "c"])
    folds = wf.logo_folds(fy)
    assert [g for g, _, _ in folds] == ["a", "b", "c"]
    seen = []
    for g, tr, te in folds:
        assert set(tr).isdisjoint(te)
        assert set(fy[te]) == {g} and g not in set(fy[tr])
        seen += list(te)
    assert sorted(seen) == list(range(len(fy)))


def test_leave_one_year_out_never_trains_on_the_test_year():
    d = pd.DataFrame(dict(fy_key=["f1|2017", "f2|2017", "f1|2019", "f2|2019"],
                          year=[2017, 2017, 2019, 2019], field_id=["f1", "f2", "f1", "f2"]))
    for col in ("year", "field_id", "fy_key"):
        for _, tr, te in wf.logo_folds(d[col].to_numpy()):
            assert set(d.loc[tr, col]).isdisjoint(d.loc[te, col])


def test_boot_median_ci_is_reproducible_and_brackets_median():
    v = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    a = wf.boot_median_ci(v, 500, 42)
    assert a == wf.boot_median_ci(v, 500, 42)
    assert a[1] <= a[0] <= a[2] and a[0] == pytest.approx(0.35)


def test_fy_pr_auc_perfect_score_and_degenerate_cases():
    y = np.array([True, True, False, False, False, False])
    auc, prev = wf.fy_pr_auc(y, np.array([5, 4, 3, 2, 1, 0.0]))
    assert auc == pytest.approx(1.0) and prev == pytest.approx(1 / 3)
    assert np.isnan(wf.fy_pr_auc(np.zeros(5, bool), np.arange(5.0))[0])


def test_model_pipeline_on_synthetic_pixels_recovers_signal_and_shuffle_does_not():
    rng = np.random.default_rng(0)
    rows = []
    for k in range(6):
        n = 120
        z = rng.normal(size=n)
        rel = 1 + 0.15 * z + rng.normal(0, 0.03, n)
        rows.append(pd.DataFrame(dict(fy_key=f"F{k}|{2017 + k % 2}", field_id=f"F{k}", year=2017 + k % 2,
                                      rel=rel, problem=rel < 0.85, z_a=z, z_b=rng.normal(size=n))))
    d = pd.concat(rows, ignore_index=True)
    w = dict(wf.DEFAULTS, seed=42, bootstrap_n=50, ci_level=0.95)
    for scheme in ("lofyo", "loyo", "lofo"):
        pred = wf.run_scheme(d, ["z_a", "z_b"], "ridge", scheme, w)
        assert np.isfinite(pred).all()
        m, _ = wf.eval_oof(d, pred, w)
        assert m["rho_median"] > 0.8
    pred = wf.run_scheme(d, ["z_a", "z_b"], "lgbm", "lofyo", w, shuffle=True)
    assert abs(wf.eval_oof(d, pred, w)[0]["rho_median"]) < 0.3


def test_recurring_zones_detects_same_pattern_in_two_years():
    rng = np.random.default_rng(1)
    xs, ys = np.meshgrid(np.arange(15) * 10.0, np.arange(10) * 10.0)
    pattern = rng.normal(size=xs.size)
    rows = []
    for yr, noise, shift in ((2017, 0.1, 0.0), (2019, 0.1, 3.0)):     # 2019 grid shifted by 3 m
        rows.append(pd.DataFrame(dict(field_id="F", year=yr, x=xs.ravel() + shift, y=ys.ravel() + shift,
                                      rel=1 + 0.1 * pattern + rng.normal(0, 0.1 * noise, xs.size))))
    d = pd.concat(rows, ignore_index=True)
    d["fy_key"] = d.field_id + d.year.astype(str)
    out, pairs, loyo = wf.analysis_recurring(d, dict(wf.DEFAULTS, seed=42, bootstrap_n=50, ci_level=0.95))
    assert len(pairs) == 1 and pairs.rho.iloc[0] > 0.8 and pairs.n_pixels.iloc[0] == 150   # shifted grid still matches
    assert out["n_fields"] == 1 and len(loyo) == 2


def test_lag1_corr_smooth_vs_random():
    x, y = np.meshgrid(np.arange(20) * 10.0, np.arange(20) * 10.0)
    smooth = (x + y).ravel()
    rand = np.random.default_rng(0).normal(size=smooth.size)
    assert wf.lag1_corr(x.ravel(), y.ravel(), smooth) > 0.95
    assert abs(wf.lag1_corr(x.ravel(), y.ravel(), rand)) < 0.2
