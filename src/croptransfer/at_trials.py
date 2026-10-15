"""Austrian local trial yields (test data only) -> data/raw/at_trials.csv.

The rows are transcribed by hand from public PDF trial reports (Hatzendorf station,
LK Oberösterreich, see DATA_SOURCES.md §12) into one CSV per source under
data/raw/at_trials/. This module only merges and checks them.

AUSTRIA RULE (PLAN.md §0/§6): no analysis of these yields before the model freeze.
The checks below are schema/range checks only; nothing here compares sites or years.

Usage:  python -m croptransfer.at_trials
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from croptransfer.config import load_config, repo_path

COLUMNS = [
    "site", "bundesland", "lat", "lon", "loc_precision", "year", "yield_t_ha",
    "moisture_basis", "trial_type", "variant", "sowing_date", "harvest_date",
    "source_pdf", "page", "notes",
]
KEY = ["site", "year", "trial_type", "variant"]
LOC_PRECISION = {"report", "municipality", "exact"}


def validate(df: pd.DataFrame, yield_range: tuple[float, float]) -> list[str]:
    """Return a list of problems (empty = valid). Pure schema/range checks."""
    problems = []
    if list(df.columns) != COLUMNS:
        return [f"columns differ: {list(df.columns)}"]
    if df[["site", "bundesland", "year", "trial_type", "variant", "source_pdf"]].isna().any().any():
        problems.append("required field empty")
    y = pd.to_numeric(df["yield_t_ha"], errors="coerce")
    lo, hi = yield_range
    bad = df[y.notna() & ~y.between(lo, hi)]
    if len(bad):
        problems.append(f"{len(bad)} yields outside {lo}-{hi} t/ha (unit error?)")
    m = pd.to_numeric(df["moisture_basis"], errors="coerce").dropna()
    if not m.between(0.10, 0.20).all():
        problems.append("moisture_basis must be a fraction (e.g. 0.14)")
    if not set(df["loc_precision"].dropna()) <= LOC_PRECISION:
        problems.append(f"unknown loc_precision: {set(df['loc_precision'].dropna()) - LOC_PRECISION}")
    for col in ("sowing_date", "harvest_date"):
        d = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d")
        filled = df[col].notna()
        if (d[filled].isna()).any():
            problems.append(f"{col}: not ISO dates")
        elif (d[filled].dt.year != df.loc[filled, "year"]).any():
            problems.append(f"{col}: year differs from trial year")
    dup = df.duplicated(KEY, keep=False)
    if dup.any():
        problems.append(f"{int(dup.sum())} rows with duplicate key {KEY}")
    return problems


def build(src_dir: Path, out_path: Path, yield_range: tuple[float, float]) -> pd.DataFrame:
    """Concatenate all source CSVs, validate, sort and write the merged file."""
    # page is text: it may be a range, e.g. "93-103"
    parts = [pd.read_csv(p, dtype={"page": str}) for p in sorted(src_dir.glob("*.csv"))]
    df = pd.concat(parts, ignore_index=True)[COLUMNS]
    problems = validate(df, yield_range)
    if problems:
        raise ValueError("; ".join(problems))
    df = df.sort_values(["bundesland", "site", "year", "trial_type", "variant"]).reset_index(drop=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    return df


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config()
    raw = repo_path(cfg["paths"]["raw"])
    df = build(raw / "at_trials", raw / "at_trials.csv", tuple(cfg["at_trials"]["yield_range_t_ha"]))
    # inventory only (counts), no yield statistics - Austria rule
    print(f"{len(df)} rows written to {raw / 'at_trials.csv'}")
    print(df.groupby(["bundesland", "site"])["year"].agg(["count", "min", "max"]).to_string())
    print(df.groupby("trial_type").size().to_string())


if __name__ == "__main__":
    main()
