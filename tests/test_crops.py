"""Crop config (D6): maize results stay identical to the former hard-coded version; other crops sane."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from croptransfer import features
from croptransfer.config import load_config
from croptransfer.crops import get_crop
from test_no_leakage import _weather


def _legacy_daily(w, lat):
    """Reference copy of the pre-D6 maize GDD (base 10, cap 30) and Kc nodes."""
    d = features.daily_weather(w, lat)
    tx = d.tmax.clip(upper=30.0)
    tn = d.tmin.clip(lower=10.0).clip(upper=30.0)
    return d, ((tx + tn) / 2 - 10.0).clip(lower=0)


def test_maize_default_equals_legacy_constants():
    w = _weather()
    d, gdd = _legacy_daily(w, 42.4)
    np.testing.assert_allclose(d.gdd.to_numpy(), gdd.to_numpy())
    kc_old = np.interp(d.gdd.cumsum().to_numpy(), [0, 200, 900, 1700, 2600], [0.3, 0.3, 1.2, 1.2, 0.6])
    np.testing.assert_allclose(features.crop_coefficient(d.gdd.cumsum().to_numpy()), kc_old)


def test_maize_explicit_spec_gives_same_features():
    w = features.daily_weather(_weather(), 42.4)
    cut = date(2020, 9, 1)
    a = features.weather_features(w, cut, taw_mm=150)
    b = features.weather_features(w, cut, taw_mm=150, crop=get_crop("maize"))
    assert a == b
    # legacy window: 1.4. start, heat threshold 32 in 10.7.-20.8.
    d = w[(w.date >= "2020-04-01") & (w.date <= "2020-09-01")]
    fl = d[(d.date >= "2020-07-10") & (d.date <= "2020-08-20")]
    assert a["heat32_flower"] == int((fl.tmax > 32).sum())
    assert a["gdd"] == pytest.approx(d.gdd.sum())


def test_all_configured_crops_valid_and_winter_starts_in_autumn():
    cfg = load_config()
    for name in cfg["crops"]:
        spec = get_crop(name, cfg)
        assert spec.kc(np.array([0.0, 1e5])).min() > 0
    ww = get_crop("winter_wheat", cfg)
    assert ww.season_start(2018) == date(2017, 10, 1)
    assert get_crop("maize", cfg).season_start(2018) == date(2018, 4, 1)


def test_winter_wheat_window_uses_previous_autumn_and_base0():
    dates = pd.date_range("2017-09-01", "2018-07-31")
    n = len(dates)
    w = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "tmax_K": 283.15 * np.ones(n), "tmin_K": 277.15 * np.ones(n),
                      "tmean_K": 280.15 * np.ones(n), "tdew_K": 276.15 * np.ones(n), "prec_m": 0.002 * np.ones(n),
                      "pev_m": -0.003 * np.ones(n), "rad_J_m2": 1e7 * np.ones(n),
                      "swvl1": 0.3 * np.ones(n), "swvl2": 0.3 * np.ones(n), "swvl3": 0.3 * np.ones(n)})
    ww = get_crop("winter_wheat")
    d = features.daily_weather(w, 48.0, ww)
    assert d.gdd.iloc[0] == pytest.approx(7.0)            # (10+4)/2 - base 0 = 7
    f = features.weather_features(d, date(2018, 6, 1), taw_mm=150, crop=ww)
    first_day = pd.Timestamp("2017-10-01")
    n_days = (pd.Timestamp("2018-06-01") - first_day).days + 1
    assert f["prec"] == pytest.approx(2.0 * n_days)       # window starts 1.10. of the year before


def test_weather_features_as_of_for_winter_wheat():
    ww = get_crop("winter_wheat")
    dates = pd.date_range("2017-09-01", "2018-09-30")
    n = len(dates)
    rng = np.random.default_rng(1)
    w = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "tmax_K": 290 + rng.normal(0, 3, n), "tmin_K": 280 + rng.normal(0, 3, n),
                      "tmean_K": 285 + rng.normal(0, 2, n), "tdew_K": 278 + rng.normal(0, 2, n), "prec_m": rng.exponential(0.002, n),
                      "pev_m": -0.003 * np.ones(n), "rad_J_m2": 1.5e7 * np.ones(n),
                      "swvl1": 0.3 * np.ones(n), "swvl2": 0.3 * np.ones(n), "swvl3": 0.3 * np.ones(n)})
    cut = date(2018, 6, 15)
    a = features.weather_features(features.daily_weather(w, 48.0, ww), cut, 150, ww)
    w2 = w.copy()
    late = pd.to_datetime(w2.date).dt.date > cut
    w2.loc[late, ["tmax_K", "prec_m"]] = [320.0, 0.2]
    b = features.weather_features(features.daily_weather(w2, 48.0, ww), cut, 150, ww)
    assert a == b
