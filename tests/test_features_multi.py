"""features_multi: as-of rule for satellite features (D5, no future scenes), harvest date fill, curve test."""

from datetime import date

import numpy as np
import pandas as pd

from croptransfer import features_multi as fm


def _obs(n=12, start="2018-03-01"):
    dates = pd.date_range(start, periods=n, freq="10D")
    ndvi = 0.2 + 0.6 * np.sin(np.linspace(0, np.pi, n))
    return pd.DataFrame({"date": dates, "ndvi": ndvi, "evi": ndvi * 0.8, "ndmi": ndvi - 0.3})


def test_satellite_features_ignore_future_scenes():
    o = _obs()
    cut = date(2018, 5, 20)
    a = fm.satellite_row(o, date(2018, 3, 1), cut)
    o2 = o.copy()
    o2.loc[o2.date > pd.Timestamp(cut), ["ndvi", "evi", "ndmi"]] = 0.99
    b = fm.satellite_row(o2, date(2018, 3, 1), cut)
    for k in a:
        assert (pd.isna(a[k]) and pd.isna(b[k])) or a[k] == b[k], k


def test_curve_test_thresholds():
    ok = fm.satellite_row(_obs(), date(2018, 3, 1), date(2018, 7, 1))
    assert ok["curve_ok"]
    flat = _obs(); flat["ndvi"] = 0.3
    assert not fm.satellite_row(flat, date(2018, 3, 1), date(2018, 7, 1))["curve_ok"]
    few = _obs().iloc[:4]
    assert not fm.satellite_row(few, date(2018, 3, 1), date(2018, 7, 1))["curve_ok"]


def test_stale_last_value_is_missing_and_empty_input_safe():
    r = fm.satellite_row(_obs(), date(2018, 3, 1), date(2018, 9, 1))
    assert np.isnan(r["k5_ndvi_last"])            # last scene older than 20 days
    e = fm.satellite_row(pd.DataFrame(), date(2018, 3, 1), date(2018, 9, 1))
    assert e["n_obs"] == 0 and not e["curve_ok"]


def test_harvest_dates_fill_with_median_of_same_crop_dataset():
    gt = pd.DataFrame({"dataset": ["a", "a", "a"], "crop": ["wheat"] * 3, "year": [2016, 2017, 2018],
                       "harvest_date": [pd.Timestamp("2016-07-20"), pd.Timestamp("2017-07-20"), pd.NaT]})
    h = fm.harvest_dates(gt)
    assert h.iloc[2] == pd.Timestamp("2018-07-20") or h.iloc[2].dayofyear in (201, 202)
