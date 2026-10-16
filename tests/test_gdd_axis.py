from datetime import date

import numpy as np
import pandas as pd

from croptransfer.gdd_axis import gdd_features


def _daily(year=2020):
    dates = pd.date_range(f"{year}-04-01", f"{year}-10-31")
    return pd.DataFrame({"date": dates, "gdd": np.full(len(dates), 10.0)})   # 10 GDD per day


def _obs(year=2020):
    dates = pd.date_range(f"{year}-04-05", f"{year}-10-25", freq="10D")
    v = np.linspace(0.2, 0.8, len(dates))
    return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "ndvi": v, "evi": v, "ndmi": v})


def test_value_at_gdd_point():
    f = gdd_features(_obs(), _daily(), date(2020, 9, 1), "hls")
    # 600 GDD reached on day 60 after 1.4. (31.5.) -> interpolated between obs around that date
    assert 0.2 < f["ndvi_hls_gdd600"] < 0.8
    assert f["ndvi_hls_gdd300"] < f["ndvi_hls_gdd600"] < f["ndvi_hls_gdd900"]


def test_gdd_as_of():
    obs = _obs()
    a = gdd_features(obs, _daily(), date(2020, 7, 1), "hls")
    obs2 = obs.copy()
    obs2.loc[pd.to_datetime(obs2.date) > "2020-07-01", "ndvi"] = 0.99
    b = gdd_features(obs2, _daily(), date(2020, 7, 1), "hls")
    assert a == b or all((np.isnan(a[k]) and np.isnan(b[k])) or a[k] == b[k] for k in a)
    assert np.isnan(a["ndvi_hls_gdd1500"])     # not reached by 1.7. (910 GDD)
