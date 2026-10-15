import numpy as np
import pandas as pd
import pytest

from croptransfer import targets


def _panel(slope=0.1, years=(2000, 2003, 2006, 2009), fields=("a", "b", "c"), level=None):
    level = level or {"a": 8.0, "b": 6.0, "c": 7.0}
    rows = [dict(dataset="D", field_uid=f, year=y, Y_t_ha=level[f] + slope * (y - 2000))
            for f in fields for y in years]
    return pd.DataFrame(rows)


def test_trend_slope_recovers_common_slope():
    assert targets.trend_slope(_panel(0.1)) == pytest.approx(0.1)


def test_pure_trend_gives_ry_one():
    # yields lie exactly on field level + trend -> every RY is 1
    ry = targets.ry_descriptive(_panel(0.25))
    assert np.allclose(ry, 1.0)


def test_ry_hand_example():
    # field a: 2000:10, 2003:10, 2006:10, 2009:4 ; others flat -> slope estimated without target year
    df = _panel(0.0)
    df.loc[(df.field_uid == "a") & (df.year == 2009), "Y_t_ha"] = 4.0
    ry = targets.ry_descriptive(df)
    row = df[(df.field_uid == "a") & (df.year == 2009)].index[0]
    # slope without 2009 = 0 -> normal = mean(8, 8, 8) = 8 -> RY = 0.5
    assert ry[row] == pytest.approx(0.5)
    # for 2000 the 2009 drop enters the trend: b = within-field slope incl. 2009
    r2000 = df[(df.field_uid == "a") & (df.year == 2000)].index[0]
    sub = df[df.year != 2000]
    b = targets.trend_slope(sub)
    others = df[(df.field_uid == "a") & (df.year != 2000)]
    normal = b * 2000 + (others.Y_t_ha - b * others.year).mean()
    assert ry[r2000] == pytest.approx(8.0 / normal)


def test_target_year_never_in_trend():
    # an extreme target-year value must not change its own normal
    df = _panel(0.1)
    i = df[(df.field_uid == "b") & (df.year == 2006)].index[0]
    base = targets.ry_descriptive(df)[i] * df.loc[i, "Y_t_ha"]  # normal
    df.loc[i, "Y_t_ha"] = 100.0
    normal_after = 100.0 / targets.ry_descriptive(df)[i]
    assert normal_after == pytest.approx(base)


def test_min_other_years():
    df = _panel(0.0, years=(2000, 2003))  # only one other year
    assert targets.ry_descriptive(df).isna().all()


def test_in_fold_uses_training_rows_only():
    df = _panel(0.1)
    test_idx = df[(df.field_uid == "a") & (df.year == 2009)].index
    train_idx = df[(df.field_uid != "a") & (df.year != 2009)].index
    # changing a non-training row of the test year must not change training labels
    ry_tr, ry_te = targets.ry_in_fold(df, train_idx, test_idx)
    df2 = df.copy()
    df2.loc[(df2.field_uid == "b") & (df2.year == 2009), "Y_t_ha"] = 50.0
    ry_tr2, ry_te2 = targets.ry_in_fold(df2, train_idx, test_idx)
    assert np.allclose(ry_tr.dropna(), ry_tr2.dropna())
    assert np.allclose(ry_te, ry_te2)
    assert ry_te.notna().all()


def test_ry_nb_excludes_own_field():
    df = pd.DataFrame({"g": ["x"] * 12, "Y_t_ha": [1.0] * 11 + [3.0]})
    r = targets.ry_nb(df, ["g"], min_other=10)
    assert r.iloc[-1] == pytest.approx(3.0)
    assert r.iloc[0] == pytest.approx(1.0)
    assert targets.ry_nb(df.iloc[:10], ["g"], min_other=10).isna().all()


def test_at_risk():
    s = pd.Series([0.8, 0.9, np.nan])
    r = targets.at_risk(s, 0.85)
    assert r.iloc[0] == 1 and r.iloc[1] == 0 and np.isnan(r.iloc[2])
