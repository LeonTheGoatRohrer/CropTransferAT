"""Offline tests for the dekad bookkeeping and the peak-window features (synthetic data)."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from croptransfer import innerfeld_extract as ex
from croptransfer import innerfeld_features as ft


def test_dekad_bounds_cover_season_without_gaps():
    assert ex.dekad_bounds(2021, 0) == ("2021-04-01", "2021-04-11")
    ends = [ex.dekad_bounds(2021, k)[1] for k in range(ex.N_DEKADS - 1)]
    starts = [ex.dekad_bounds(2021, k)[0] for k in range(1, ex.N_DEKADS)]
    assert ends == starts                                    # exclusive end == next start
    assert ex.dekad_bounds(2021, ex.N_DEKADS - 1)[1] == "2021-10-28"


def test_dekad_of_matches_bounds():
    for k in (0, 5, 12, 20):
        s, _ = ex.dekad_bounds(2019, k)
        assert ex.dekad_of(date.fromisoformat(s)) == k


def test_smooth_ignores_nan_and_peak_in_range():
    c = np.array([0.2, 0.4, np.nan, 0.8, 0.9, 0.5, 0.3])
    assert ft.smooth(c, 3)[2] == pytest.approx((0.4 + 0.8) / 2)
    assert ft.peak_dekad(c, 0, 6, 3) == 3          # smoothed: idx3 = mean(0.8, 0.9) = 0.85 beats idx4 = 0.73
    assert ft.peak_dekad(c, 5, 6, 3) == 5                    # search range restricts the maximum
    assert ft.peak_dekad(np.full(7, np.nan), 0, 6, 3) is None


def test_field_curve_needs_valid_share():
    a = np.array([[0.5, np.nan], [0.7, np.nan], [0.9, 0.4]])
    out = ft.field_curve(a, 0.5)
    assert out[0] == pytest.approx(0.7)
    assert np.isnan(out[1])                                  # only 1 of 3 cells valid -> dekad dropped


def test_window_median_clips_and_ignores_nan():
    a = np.array([[1.0, np.nan, 3.0, 5.0], [np.nan, np.nan, np.nan, np.nan]])
    r = ft.window_median(a, -2, 2)
    assert r[0] == pytest.approx(2.0) and np.isnan(r[1])
    assert np.isnan(ft.window_median(a, 10, 12)).all()


def _tab(offset: float):
    """Two field-years; the second has all NDVI shifted by `offset` (level must not leak into z)."""
    rows = []
    for fy, off in (("A", 0.0), ("B", offset)):
        for c in range(6):
            r = dict(fy_key=fy, site="S", year=2020, elev=1.0 + c, slope=0.0, tpi=0.0)
            for k in range(ex.N_DEKADS):
                base = 0.3 + 0.5 * np.exp(-((k - 12) / 4.0) ** 2) + 0.01 * c
                r[f"ndvi_d{k:02d}"], r[f"ndre_d{k:02d}"], r[f"n_d{k:02d}"] = base + off, base * 0.8 + off, 2
            rows.append(r)
    return pd.DataFrame(rows)


def test_build_features_peak_and_z_scores_are_field_year_local():
    feats, summ = ft.build_features(_tab(0.1))
    assert summ.peak_dekad.tolist() == [12, 12] and summ.ok.all()
    for fy, g in feats.groupby("fy_key"):
        assert g["z_b1_ndvi"].mean() == pytest.approx(0.0, abs=1e-9)
    a = feats[feats.fy_key == "A"].z_b1_ndvi.to_numpy()
    b = feats[feats.fy_key == "B"].z_b1_ndvi.to_numpy()
    assert np.allclose(a, b)                                 # level shift disappears after z-scoring
