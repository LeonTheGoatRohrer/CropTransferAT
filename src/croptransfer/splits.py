"""Validation splits (PLAN §2, DECISIONS 2026-10-15 "LOFYO konkret").

All functions return a list of (name, train_index, test_index) over a DataFrame index.
"""

from __future__ import annotations

import pandas as pd


def lofyo(df: pd.DataFrame, test_mask: pd.Series | None = None, year: str = "year",
          group: str = "field_group") -> list[tuple[str, pd.Index, pd.Index]]:
    """Leave-field-group-and-year-out: test (y, g); train year != y AND group != g."""
    test_mask = pd.Series(True, index=df.index) if test_mask is None else test_mask
    folds = []
    for (y, g), t in df[test_mask].groupby([year, group]):
        train = df.index[(df[year] != y) & (df[group] != g)]
        folds.append((f"{y}-g{g}", train, t.index))
    return folds


def loyo(df: pd.DataFrame, test_mask: pd.Series | None = None, year: str = "year"):
    test_mask = pd.Series(True, index=df.index) if test_mask is None else test_mask
    return [(str(y), df.index[df[year] != y], t.index) for y, t in df[test_mask].groupby(year)]


def lofo(df: pd.DataFrame, test_mask: pd.Series | None = None, group: str = "field_group"):
    test_mask = pd.Series(True, index=df.index) if test_mask is None else test_mask
    return [(f"g{g}", df.index[df[group] != g], t.index) for g, t in df[test_mask].groupby(group)]


def lodo(df: pd.DataFrame, train_ds: str, test_ds: str, test_mask: pd.Series | None = None,
         dataset: str = "dataset"):
    """Leave-one-dataset-out in one direction: train on `train_ds`, test on `test_ds`."""
    test_mask = pd.Series(True, index=df.index) if test_mask is None else test_mask
    return [(f"{train_ds}->{test_ds}", df.index[df[dataset] == train_ds],
             df.index[(df[dataset] == test_ds) & test_mask])]


def inner_year_folds(df: pd.DataFrame, idx: pd.Index, year: str = "year", max_folds: int = 6):
    """Inner CV for tuning inside a training set: leave-one-year-out (at most max_folds years,
    the largest years by row count are kept as separate folds, the rest are merged)."""
    years = df.loc[idx, year].value_counts()
    keep = list(years.index[:max_folds])
    folds = []
    for y in keep:
        folds.append((idx[df.loc[idx, year] != y], idx[df.loc[idx, year] == y]))
    return folds
