"""Metrics with cluster-bootstrap confidence intervals (DECISIONS 2026-10-15: clusters = dataset-years)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def _spearman(a, b) -> float:
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return np.nan
    return float(spearmanr(a, b).statistic)


def _boot_clusters(clusters: pd.Series, n_boot: int, seed: int):
    """Yield index arrays of cluster-bootstrap resamples."""
    rng = np.random.default_rng(seed)
    groups = pd.Series(np.arange(len(clusters))).groupby(clusters.to_numpy()).apply(list)
    keys = groups.index.to_numpy()
    for _ in range(n_boot):
        pick = rng.choice(len(keys), len(keys), replace=True)
        yield np.concatenate([groups.iloc[i] for i in pick])


def spearman_ci(x, y, clusters, n_boot: int = 1000, seed: int = 42, level: float = 0.95):
    """Spearman rho with cluster-bootstrap percentile CI."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    clusters = pd.Series(np.asarray(clusters))
    rho = _spearman(x, y)
    bs = [_spearman(x[i], y[i]) for i in _boot_clusters(clusters, n_boot, seed)]
    lo, hi = np.nanpercentile(bs, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return rho, float(lo), float(hi)


def rmse(y, p) -> float:
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(np.sqrt(np.mean((y - p) ** 2)))


def rmse_diff_ci(y, p_model, p_ref, clusters, n_boot: int = 1000, seed: int = 42, level: float = 0.95):
    """RMSE(model) - RMSE(ref) with cluster-bootstrap CI (negative = model better)."""
    y, a, b = (np.asarray(v, float) for v in (y, p_model, p_ref))
    clusters = pd.Series(np.asarray(clusters))
    d = rmse(y, a) - rmse(y, b)
    bs = [rmse(y[i], a[i]) - rmse(y[i], b[i]) for i in _boot_clusters(clusters, n_boot, seed)]
    lo, hi = np.percentile(bs, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(d), float(lo), float(hi)


def r2(y, p) -> float:
    y, p = np.asarray(y, float), np.asarray(p, float)
    ss = np.sum((y - y.mean()) ** 2)
    return float(1 - np.sum((y - p) ** 2) / ss) if ss > 0 else np.nan


def within_year_rhos(df: pd.DataFrame, pred: str, target: str, min_n: int = 5) -> pd.Series:
    """Spearman rho within each dataset-year with >= min_n labelled rows."""
    out = {}
    for (ds, yr), g in df.dropna(subset=[pred, target]).groupby(["dataset", "year"]):
        if len(g) >= min_n:
            out[f"{ds}-{yr}"] = _spearman(g[pred].to_numpy(), g[target].to_numpy())
    return pd.Series(out, dtype=float)


def pr_auc(y_true, score) -> float:
    from sklearn.metrics import average_precision_score

    y_true = np.asarray(y_true)
    return float(average_precision_score(y_true, score)) if 0 < y_true.sum() < len(y_true) else np.nan


def recall_at_fpr(y_true, score, fpr: float = 0.2) -> float:
    """Recall at the threshold where the false-positive rate is <= fpr."""
    from sklearn.metrics import roc_curve

    y_true = np.asarray(y_true)
    if not 0 < y_true.sum() < len(y_true):
        return np.nan
    f, t, _ = roc_curve(y_true, score)
    return float(t[f <= fpr].max())
