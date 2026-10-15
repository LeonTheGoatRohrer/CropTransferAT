"""Model family (PLAN.md Phase 2): one model per feature group + combinations; Ridge + shallow LightGBM.

Hyper-parameters are tuned only inside the training data of an outer fold (nested,
leave-one-year-out on in-fold RY labels).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RIDGE_GRID = [{"alpha": a} for a in (0.3, 3.0, 30.0, 300.0)]
LGBM_BASE = dict(subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
                 verbose=-1, n_jobs=1)
LGBM_GRID = [dict(max_depth=2, num_leaves=4, n_estimators=150, learning_rate=0.05, min_child_samples=10),
             dict(max_depth=3, num_leaves=8, n_estimators=150, learning_rate=0.05, min_child_samples=20),
             dict(max_depth=2, num_leaves=4, n_estimators=400, learning_rate=0.02, min_child_samples=20)]

# model code -> feature groups (S = satellite of the chosen basis)
FAMILY = {
    "B1": ["B1"], "M-S": ["S"], "M-W": ["W"], "M-B": ["B"], "M-B+": ["B", "B+"],
    "M-WB": ["W", "B"], "M-SW": ["S", "W"], "M-SB": ["S", "B"], "M-alle": ["S", "W", "B"],
}
NO_SATELLITE = {"M-W", "M-B", "M-B+", "M-WB"}


def make(kind: str, params: dict, seed: int):
    if kind == "ridge":
        return make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler(), Ridge(**params))
    from lightgbm import LGBMRegressor

    return LGBMRegressor(random_state=seed, **LGBM_BASE, **params)


def grid(kind: str) -> list[dict]:
    return RIDGE_GRID if kind == "ridge" else LGBM_GRID


def usable_columns(X: pd.DataFrame) -> list[str]:
    """Drop all-NaN and constant columns (computed on training data only)."""
    keep = []
    for c in X.columns:
        v = X[c].to_numpy(dtype=float)
        ok = np.isfinite(v)
        if ok.sum() >= 3 and np.nanstd(v) > 0:
            keep.append(c)
    return keep
