"""Offline tests for smoothing and point cleaning of round 2 (synthetic data)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import innerfeld_runde2 as r2


def test_smooth_grid_radius_zero_is_identity_and_window_mean():
    x = np.array([5.0, 15.0, 25.0, 35.0])
    y = np.zeros(4) + 5.0
    v = np.array([1.0, 2.0, 3.0, 10.0])
    assert r2.smooth_grid(x, y, v, 0).tolist() == v.tolist()
    s = r2.smooth_grid(x, y, v, 1)
    assert s[1] == pytest.approx(2.0)                        # (1 + 2 + 3) / 3
    assert s[2] == pytest.approx(5.0)                        # (2 + 3 + 10) / 3
    assert s[0] == pytest.approx(1.0)                        # only 2 valid cells in the window -> own value


def test_smooth_grid_ignores_nan_and_keeps_nan_without_support():
    x = np.array([5.0, 15.0, 25.0, 85.0])
    y = np.zeros(4) + 5.0
    v = np.array([1.0, np.nan, 3.0, np.nan])
    s = r2.smooth_grid(x, y, v, 1)
    assert s[0] == 1.0 and s[2] == 3.0                       # only 2 valid cells around: own value kept
    assert np.isnan(s[1]) and np.isnan(s[3])


def test_smooth_grid_reduces_noise_of_random_field():
    rng = np.random.default_rng(0)
    gx, gy = np.meshgrid(np.arange(30) * 10.0 + 5, np.arange(30) * 10.0 + 5)
    v = rng.normal(size=gx.size)
    s = r2.smooth_grid(gx.ravel(), gy.ravel(), v, 1)
    assert np.std(s) < 0.5 * np.std(v)                       # 3x3 mean of white noise: SD about 1/3


def test_clean_kayad_points_drops_low_and_pass_ends():
    n = 30
    pts = pd.DataFrame(dict(number=np.arange(n), x=np.arange(n) * 1.5, y=0.0, yield_t_ha=10.0))
    pts.loc[15, "yield_t_ha"] = 2.0                          # low-yield point inside the pass
    out = r2.clean_kayad_points(pts, low=3.0, first=8, last=3)
    assert len(out) == n - 8 - 3 - 1
    assert out.number.min() == 8 and out.number.max() == n - 4
    assert 15 not in out.number.tolist()


def test_clean_kayad_points_handles_two_passes_independently():
    a = pd.DataFrame(dict(number=np.arange(20), x=np.arange(20) * 1.5, y=0.0, yield_t_ha=10.0))
    b = pd.DataFrame(dict(number=np.arange(20, 40), x=np.arange(20) * 1.5, y=20.0, yield_t_ha=10.0))   # 20 m away
    out = r2.clean_kayad_points(pd.concat([a, b], ignore_index=True), low=3.0, first=8, last=3)
    assert len(out) == 2 * (20 - 8 - 3)
