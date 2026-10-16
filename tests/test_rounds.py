import numpy as np
import pandas as pd
import pytest

from croptransfer.rounds import add_relative


def _df():
    rows = []
    for y, base in [(2014, 0.5), (2017, 0.6), (2020, 0.7)]:
        for f in range(4):
            rows.append(dict(dataset="A", year=y, sensor_era="HLS", ndvi_hls_max=base + 0.01 * f))
    rows.append(dict(dataset="A", year=2008, sensor_era="L57", ndvi_hls_max=5.0))  # must be ignored
    return pd.DataFrame(rows)


def test_relative_to_other_years_and_fields():
    d, new = add_relative(_df(), "HLS", ["ndvi"], ["max"])
    assert set(new) == {"ndvi_hls_max_relyr", "ndvi_hls_max_relfld"}
    r = d[(d.year == 2020) & np.isclose(d.ndvi_hls_max, 0.70)].iloc[0]
    other_years = [0.5, 0.51, 0.52, 0.53, 0.6, 0.61, 0.62, 0.63]   # L57 value 5.0 excluded
    assert r.ndvi_hls_max_relyr == pytest.approx(0.70 - np.median(other_years))
    assert r.ndvi_hls_max_relfld == pytest.approx(0.70 - np.median([0.71, 0.72, 0.73]))
    assert d.loc[d.sensor_era == "L57", new].isna().all().all()


def test_relfld_needs_three_other_fields():
    df = _df()
    df = df[~((df.year == 2014) & (df.ndvi_hls_max > 0.505))]   # 2014: 1 field left
    d, _ = add_relative(df, "HLS", ["ndvi"], ["max"])
    assert d.loc[d.year == 2014, "ndvi_hls_max_relfld"].isna().all()
