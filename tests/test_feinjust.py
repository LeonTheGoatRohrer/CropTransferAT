"""Feinjustierung: hand examples for features, decision rule and paired deltas."""

from datetime import date

import numpy as np
import pandas as pd

from croptransfer import feinjust, fj_features as fjf
from croptransfer.config import load_config

CFG = load_config()


def test_neighbour_anomaly_hand_example():
    df = pd.DataFrame({"g": ["a"] * 4 + ["b"] * 2, "v": [1.0, 2.0, 3.0, 10.0, 5.0, 6.0]})
    an = fjf.neighbour_anomaly(df, "v", ["g"], min_others=3)
    assert an.iloc[0] == 1.0 - 3.0          # median of 2, 3, 10
    assert an.iloc[3] == 10.0 - 2.0
    assert an.iloc[4:].isna().all()         # group b has only one other row


def test_emergence_on_synthetic_curve():
    dates = pd.date_range("2020-04-05", "2020-08-30", freq="5D")
    doy = dates.dayofyear.to_numpy()
    ndvi = 0.2 + 0.6 / (1 + np.exp(-(doy - 170) / 8.0))       # logistic green-up centred on DOY 170
    obs = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "ndvi": ndvi})
    e = fjf.emergence_doy(obs, date(2020, 9, 1), CFG)
    assert 145 < e < 170                    # 20 % amplitude is reached before the midpoint


def test_emergence_low_amplitude_is_nan():
    dates = pd.date_range("2020-04-05", "2020-08-30", freq="5D")
    obs = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "ndvi": 0.3 + 0.01 * np.sin(np.arange(len(dates)))})
    assert np.isnan(fjf.emergence_doy(obs, date(2020, 9, 1), CFG))


def test_gdd_score_only_negative_deviations():
    ref = pd.Series([0.5, 0.7, 0.8], index=[3, 4, 5])
    bins = pd.Series([0.6, 0.5, 0.8], index=[3, 4, 5])
    assert np.isclose(fjf.gdd_score(bins, ref), (0 - 0.2 + 0) / 3)


def test_decision_rule():
    fj = CFG["feinjust"]
    assert feinjust.decide({"delta": 0.03, "lo": 0.001}, None, fj)["keep"]
    assert not feinjust.decide({"delta": 0.03, "lo": -0.01}, None, fj)["keep"]      # CI touches 0
    assert not feinjust.decide({"delta": 0.019, "lo": 0.01}, None, fj)["keep"]      # below +0.02
    assert not feinjust.decide({"delta": 0.05, "lo": 0.01}, {"delta": -0.03, "lo": -0.05}, fj)["keep"]
    assert feinjust.decide({"delta": 0.0, "lo": -0.1}, {"delta": 0.03, "lo": 0.01}, fj)["keep"]


def test_delta_A_zero_for_identical_predictions():
    rng = np.random.default_rng(0)
    o = pd.DataFrame({"fy_key": [f"k{i}" for i in range(40)], "dataset": "X", "year": np.repeat([1, 2, 3, 4], 10),
                      "ry": rng.uniform(0.6, 1.2, 40), "p": rng.uniform(0, 1, 40)})
    d = feinjust.delta_A(o, o, CFG)
    assert d["delta"] == 0 and d["lo"] == 0 and d["hi"] == 0


def test_delta_B_paired():
    t = pd.DataFrame({"fy_key": list("abcdef"), "field_id": list("aabbcc"), "rho": [0.5, 0.6, 0.7, 0.4, 0.5, 0.6]})
    t2 = t.assign(rho=t.rho + 0.1)
    wf = {"seed": 42, "bootstrap_n": 200}
    d = feinjust.delta_B(t2, t, wf)
    assert np.isclose(d["delta"], 0.1) and np.isclose(d["lo"], 0.1) and np.isclose(d["hi"], 0.1)


def test_emergence_ignores_spring_cover_crop_peak():
    dates = pd.date_range("2020-04-05", "2020-08-30", freq="5D")
    doy = dates.dayofyear.to_numpy()
    cover = 0.6 * np.exp(-((doy - 130) / 12.0) ** 2)               # green cover crop in May
    maize = 0.6 / (1 + np.exp(-(doy - 190) / 8.0))                  # maize green-up in July
    obs = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "ndvi": 0.2 + cover + maize})
    e = fjf.emergence_doy(obs, date(2020, 9, 1), CFG)
    assert e > 160                          # after the tillage minimum, not in April/May


def test_conformal_threshold_controls_fpr():
    from croptransfer.fj_product import conformal_threshold

    neg = np.arange(1, 10, dtype=float)          # n = 9 -> k = ceil(10 * 0.8) = 8 -> 8th smallest
    t = conformal_threshold(neg, 0.2)
    assert t == 8.0 and (neg > t).mean() <= 0.2
