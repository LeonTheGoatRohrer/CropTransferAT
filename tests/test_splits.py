import pandas as pd

from croptransfer import splits


def _df():
    rows = [dict(dataset=ds, field_uid=f"{ds}{f}", field_group=f % 3, year=y)
            for ds in ["A", "B"] for f in range(6) for y in [2014, 2017, 2020]]
    return pd.DataFrame(rows)


def test_lofyo_no_field_or_year_overlap():
    df = _df()
    folds = splits.lofyo(df)
    assert len(folds) == 9
    covered = []
    for _, tr, te in folds:
        assert not set(df.loc[tr, "year"]) & set(df.loc[te, "year"])
        assert not set(df.loc[tr, "field_uid"]) & set(df.loc[te, "field_uid"])
        covered += list(te)
    assert sorted(covered) == sorted(df.index)        # every row tested exactly once


def test_loyo_and_lofo():
    df = _df()
    for _, tr, te in splits.loyo(df):
        assert not set(df.loc[tr, "year"]) & set(df.loc[te, "year"])
    for _, tr, te in splits.lofo(df):
        assert not set(df.loc[tr, "field_uid"]) & set(df.loc[te, "field_uid"])


def test_lodo():
    df = _df()
    (_, tr, te), = splits.lodo(df, "A", "B")
    assert set(df.loc[tr, "dataset"]) == {"A"} and set(df.loc[te, "dataset"]) == {"B"}


def test_inner_year_folds_stay_inside_training():
    df = _df()
    _, tr, _ = splits.lofyo(df)[0]
    for a, b in splits.inner_year_folds(df, tr):
        assert set(a) | set(b) <= set(tr)
        assert not set(df.loc[a, "year"]) & set(df.loc[b, "year"])
