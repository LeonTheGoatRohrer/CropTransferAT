"""Yield targets: trend-adjusted relative yield RY, neighbour-relative RY_nb (PLAN §3.6).

RY (DECISIONS.md 2026-10-15, owner decision "trend-adjusted"):
  per dataset a common linear yield trend b (slope over years, field fixed effects)
  is estimated WITHOUT the target year; then
      normal(f, y) = b*y + mean_{y' != y}( Y(f, y') - b*y' )
      RY(f, y)     = Y(f, y) / normal(f, y)
  defined only if field f has >= `min_other` other maize years.
In cross-validation `ry_in_fold` estimates the trend from training rows only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def trend_slope(df: pd.DataFrame, field: str = "field_uid", year: str = "year", y: str = "Y_t_ha") -> float:
    """Common within-field OLS slope of yield on year (field fixed effects).

    Fields observed in only one year carry no information and drop out. Returns 0
    if no field has two years (no trend can be estimated).
    """
    g = df.groupby(field)
    t = df[year] - g[year].transform("mean")
    v = df[y] - g[y].transform("mean")
    den = float((t * t).sum())
    return float((t * v).sum() / den) if den > 0 else 0.0


def compute_ry(slope_rows: pd.DataFrame, normal_rows: pd.DataFrame, targets: pd.DataFrame,
               min_other: int = 2, field: str = "field_uid") -> pd.Series:
    """Trend-adjusted RY for `targets`.

    slope_rows  rows used to fit the trend (per dataset, target year always excluded)
    normal_rows rows that may enter the field's normal (target year always excluded)
    """
    out = pd.Series(np.nan, index=targets.index, dtype=float)
    for (ds, yr), tg in targets.groupby(["dataset", "year"]):
        s = slope_rows[(slope_rows.dataset == ds) & (slope_rows.year != yr)]
        b = trend_slope(s, field=field)
        nr = normal_rows[(normal_rows.dataset == ds) & (normal_rows.year != yr)
                         & normal_rows[field].isin(tg[field])]
        resid = (nr["Y_t_ha"] - b * nr["year"]).groupby(nr[field]).agg(["mean", "size"])
        m = tg[field].map(resid["mean"])
        n = tg[field].map(resid["size"]).fillna(0)
        normal = b * yr + m
        ry = tg["Y_t_ha"] / normal
        out.loc[tg.index] = ry.where((n >= min_other) & (normal > 0))
    return out


def ry_descriptive(df: pd.DataFrame, min_other: int = 2) -> pd.Series:
    """RY for every row: trend and normal from all other years (leave-year-out)."""
    return compute_ry(df, df, df, min_other)


def ry_in_fold(df: pd.DataFrame, train_idx, test_idx, min_other: int = 2) -> tuple[pd.Series, pd.Series]:
    """RY labels inside one CV fold.

    Training labels use only training rows (trend and normals). Test labels use a trend
    fitted on training rows only; the test field's normal comes from its own other years
    (definition of RY - these rows are never used for fitting).
    """
    train = df.loc[train_idx]
    test = df.loc[test_idx]
    ry_train = compute_ry(train, train, train, min_other)
    ry_test = compute_ry(train, df, test, min_other)
    return ry_train, ry_test


def ry_nb(df: pd.DataFrame, group_cols: list[str], y: str = "Y_t_ha", min_other: int = 10) -> pd.Series:
    """Neighbour-relative yield: Y / median Y of the OTHER fields in the same group.

    NaN if the group has fewer than `min_other` other fields.
    """
    out = pd.Series(np.nan, index=df.index, dtype=float)
    for _, g in df.groupby(group_cols):
        if len(g) - 1 < min_other:
            continue
        v = g[y].to_numpy(dtype=float)
        meds = np.array([np.median(np.delete(v, i)) for i in range(len(v))])
        with np.errstate(divide="ignore", invalid="ignore"):
            out.loc[g.index] = np.where(meds > 0, v / meds, np.nan)
    return out


def at_risk(ry: pd.Series, threshold: float = 0.85) -> pd.Series:
    """'Gefährdet' = RY below threshold (NaN stays NaN)."""
    return (ry < threshold).astype("float").where(ry.notna())
