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


# ---------------- Feinjustierung M1-M4 (plan_feinjustierung F1.3) ----------------
from croptransfer import fj_features as fjf
from croptransfer.config import load_config

_CFG = load_config()


def _s1_raw(year=2020, n_fields=5):
    rng = np.random.default_rng(1)
    rows = []
    for d in pd.date_range(f"{year}-06-01", f"{year}-09-30", freq="6D"):
        for f in range(n_fields):
            rows.append({"fy_key": f"F{f}", "date": d.strftime("%Y-%m-%d"), "orbit_pass": "ASCENDING",
                         "n_pix": 40, "vv_db": -10 + rng.normal(0, 1), "vh_db": -17 + rng.normal(0, 1)})
    return pd.DataFrame(rows)


def _cut(keys, year=2020, mmdd="09-01"):
    return {k: date.fromisoformat(f"{year}-{mmdd}") for k in keys}


def test_s1_features_as_of():
    raw = _s1_raw()
    cut = _cut([f"F{i}" for i in range(5)])
    ds = pd.Series("X", index=list(cut))
    a = fjf.s1_field_features(fjf.s1_scene_table(raw, _CFG), ds, cut, _CFG)
    late = raw.copy()
    late.loc[pd.to_datetime(late.date).dt.date > date(2020, 9, 1), ["vv_db", "vh_db"]] = [-2.0, -3.0]
    b = fjf.s1_field_features(fjf.s1_scene_table(late, _CFG), ds, cut, _CFG)
    pd.testing.assert_frame_equal(a, b)
    assert a.s1_rvi_mean.notna().all()


def test_lst_features_as_of():
    rows = [{"fy_key": f"F{f}", "date": d.strftime("%Y-%m-%d"), "n_clear": 9, "n_total": 10, "lst_k": 300.0 + f}
            for d in pd.date_range("2020-06-20", "2020-09-20", freq="16D") for f in range(5)]
    raw = pd.DataFrame(rows)
    tmax = pd.DataFrame([{"fy_key": f"F{f}", "date": d, "tmax": 25.0}
                         for d in pd.date_range("2020-06-01", "2020-09-30") for f in range(5)])
    cut = _cut([f"F{i}" for i in range(5)])
    ds = pd.Series("X", index=list(cut))
    a = fjf.lst_field_features(raw, tmax, ds, cut, _CFG)
    raw2 = raw.copy()
    raw2.loc[pd.to_datetime(raw2.date).dt.date > date(2020, 9, 1), "lst_k"] = 350.0
    b = fjf.lst_field_features(raw2, tmax, ds, cut, _CFG)
    pd.testing.assert_frame_equal(a, b)


def test_modis_ratio_excludes_composites_ending_after_cutoff():
    raw = pd.DataFrame({"fy_key": "F0", "date": ["2020-07-27", "2020-08-28"], "ET": [10.0, 99.0], "PET": [20.0, 1.0]})
    r = fjf.modis_et_ratio(raw, _cut(["F0"]), _CFG)
    assert r["F0"] == 0.5       # the composite 28.8.-4.9. ends after 1.9. and is ignored


def test_era5_ratio_as_of():
    d = pd.date_range("2020-06-01", "2020-10-31")
    ev = pd.DataFrame({"pt": "p", "date": d.strftime("%Y-%m-%d"), "evap_m": -0.002, "pev_m": -0.004})
    ev2 = ev.copy()
    ev2.loc[d > "2020-09-01", "evap_m"] = -1.0
    w = pd.Series({"F0": "p"})
    assert fjf.era5_et_ratio(ev, w, _cut(["F0"]), _CFG)["F0"] == fjf.era5_et_ratio(ev2, w, _cut(["F0"]), _CFG)["F0"] == 0.5


def test_gdd_bins_as_of_and_complete():
    obs, w = _obs(), features.daily_weather(_weather(), 42.4)
    cut = date(2020, 8, 1)
    a = fjf.gdd_bins(obs, w, cut, _CFG)
    b = fjf.gdd_bins(_tamper_after(obs, cut, "ndvi", 0.99), w, cut, _CFG)
    pd.testing.assert_series_equal(a, b)
    cum = w[(w.date >= "2020-04-01") & (w.date <= "2020-08-01")].gdd.sum()
    assert ((a.index + 1) * _CFG["gdd_score"]["bin_cdd"] <= cum).all()
    assert (a.index * _CFG["gdd_score"]["bin_cdd"] >= _CFG["gdd_score"]["first_cdd"]).all()


def test_emergence_as_of():
    obs, cut = _obs(), date(2020, 9, 1)
    a = fjf.emergence_doy(obs, cut, _CFG)
    b = fjf.emergence_doy(_tamper_after(obs, cut, "ndvi", 0.05), cut, _CFG)
    assert a == b and np.isfinite(a)
