"""Data review numbers for the multi-crop packages (W1.3/W2.2/W2.3) -> reports/data_review/phase1b_mehrkultur.md.

Usage:  python -m croptransfer.review_multi
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path
from croptransfer.groundtruth_multi import count_cells

FENCE = "`" * 3
AT_RISK = 0.85  # RY below this counts as "gefaehrdet" (PLAN Phase 3)


def summarize(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tables used in the review: per dataset/tier counts, RY distribution, yield ranges, per-year counts."""
    by = d.groupby(["dataset", "crop", "tier"])
    counts = by.agg(site_years=("Y_t_ha", "size"), sites=("site", "nunique"), years=("year", "nunique"),
                    cells=("cell_id", "nunique"), y_min=("Y_t_ha", "min"), y_med=("Y_t_ha", "median"),
                    y_max=("Y_t_ha", "max"), n_plots_med=("n_plots", "median"), with_RY=("RY", "count"),
                    with_RY_nb=("RY_nb", "count")).round(2).reset_index()
    ry = d.dropna(subset=["RY"]).groupby(["dataset", "tier"])["RY"].agg(
        n="size", p05=lambda x: x.quantile(.05), median="median", p95=lambda x: x.quantile(.95),
        share_at_risk=lambda x: (x < AT_RISK).mean()).round(3).reset_index()
    per_year = d.groupby(["dataset", "year"]).size().unstack(0, fill_value=0)
    dup = d.duplicated(["dataset", "crop", "crop_variant", "site", "country", "year"]).sum()
    return {"counts": counts, "ry": ry, "per_year": per_year, "cells": count_cells(d), "duplicates": pd.DataFrame({"duplicate_site_years": [dup]})}


def main() -> None:
    cfg = load_config()
    d = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_site_years.parquet")
    t = summarize(d)
    out = repo_path(cfg["paths"]["data_review"]) / "phase1b_mehrkultur_zahlen.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Zahlen zur Datenkritik Mehr-Kulturen (automatisch erzeugt, `python -m croptransfer.review_multi`)\n\n")
        for k, v in t.items():
            body = v.to_string(index=(k == "per_year"))
            f.write(f"## {k}\n\n{FENCE}\n{body}\n{FENCE}\n\n")
    print(out)
    for k, v in t.items():
        print(k); print(v.to_string())


if __name__ == "__main__":
    main()
