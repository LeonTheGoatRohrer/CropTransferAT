"""As-of rule (PLAN §3.5): features for cutoff t never change when data after t change."""

from datetime import date

import numpy as np
import pandas as pd

from croptransfer import features, timeseries as ts


def _obs(year=2020, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{year}-04-03", f"{year}-10-28", freq="5D")
    doy = dates.dayofyear.to_numpy()
    ndvi = 0.2 + 0.6 * np.exp(-((doy - 220) / 35.0) ** 2) + rng.normal(0, 0.01, len(dates))
    return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "ndvi": ndvi, "evi": ndvi * 0.8,
                         "ndmi": ndvi - 0.3, "gndvi": ndvi - 0.1})


def _weather(year=2020, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{year}-03-01", f"{year}-10-31")
    n = len(dates)
    return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "tmax_K": 298 + rng.normal(0, 3, n),
                         "tmin_K": 285 + rng.normal(0, 3, n), "tmean_K": 291 + rng.normal(0, 2, n),
                         "tdew_K": 283 + rng.normal(0, 2, n), "prec_m": rng.exponential(0.002, n),
                         "pev_m": -0.004 * np.ones(n), "rad_J_m2": 2e7 * np.ones(n),
                         "swvl1": 0.3 * np.ones(n), "swvl2": 0.3 * np.ones(n), "swvl3": 0.3 * np.ones(n)})


def _tamper_after(df, cutoff, col, value):
    d = df.copy()
    d.loc[pd.to_datetime(d["date"]).dt.date > cutoff, col] = value
    return d


def test_dekad_composite_ignores_future():
    obs, cut = _obs(), date(2020, 7, 15)
    a = ts.dekad_composite(obs, cut, "ndvi")
    b = ts.dekad_composite(_tamper_after(obs, cut, "ndvi", 0.99), cut, "ndvi")
    pd.testing.assert_frame_equal(a, b)
    assert a.loc[a.dekad > 10, "value"].isna().all()   # nothing after the cutoff dekad


def test_interpolation_uses_only_past():
    obs = _obs()
    cut = date(2020, 7, 15)
    # remove all obs in the last 3 weeks before the cutoff: gap must be filled by carry-forward,
    # not by interpolating towards later observations
    o = obs[~pd.to_datetime(obs.date).between("2020-06-25", "2020-07-15")]
    a = ts.dekad_composite(o, cut, "ndvi")
    b = ts.dekad_composite(_tamper_after(o, cut, "ndvi", 0.99), cut, "ndvi")
    pd.testing.assert_frame_equal(a, b)


def test_satellite_features_as_of():
    obs, cut = _obs(), date(2020, 8, 1)
    a = features.satellite_features(obs, cut, ["ndvi", "evi"], "hls")
    b = features.satellite_features(_tamper_after(obs, cut, "ndvi", -0.5), cut, ["ndvi", "evi"], "hls")
    assert a.keys() == b.keys()
    for k in a:
        assert (np.isnan(a[k]) and np.isnan(b[k])) or a[k] == b[k], k
    assert np.isnan(a["ndvi_hls_aug"])     # K1 needs data through August


def test_weather_features_as_of():
    lat = 42.4
    w = features.daily_weather(_weather(), lat)
    cut = date(2020, 7, 1)
    a = features.weather_features(w, cut, taw_mm=150)
    w2 = w.copy()
    late = w2.date.dt.date > cut
    w2.loc[late, ["tmax", "prec", "gdd", "et0"]] = 99.0
    b = features.weather_features(w2, cut, taw_mm=150)
    assert a == b


def test_rzwsi_bounds():
    w = features.daily_weather(_weather(), 42.4)
    w = w[w.date >= "2020-04-01"]
    r = features.rzwsi_series(w, taw_mm=100)
    assert ((r >= 0) & (r <= 1)).all()
    dry = w.assign(prec=0.0)
    assert features.rzwsi_series(dry, 100)[-1] > r[-1] - 1e-9


def test_saxton_rawls_plausible():
    loam = features.saxton_rawls_awc(0.40, 0.20, 2.5)
    sand = features.saxton_rawls_awc(0.90, 0.05, 1.0)
    assert 0.10 < loam < 0.25 and sand < loam
