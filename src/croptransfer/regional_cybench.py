"""CY-Bench EU regional maize model (PLAN.md Phase 5): data, targets, LOCO evaluation, EU freeze.

Pipeline (``python -m croptransfer.regional_cybench``):
1. Load EU grain-maize yields and predictors (all CY-Bench countries EXCEPT Austria), aggregate the
   predictors per region-year and cutoff (as-of rule: only data available on or before the cutoff).
2. Target ``YAS = yield / olympic mean of the 5 previous years`` (previous years only).
3. Baselines (YAS = 1, linear trend extrapolation) and a shallow LightGBM, evaluated with an outer
   leave-one-country-out (LOCO) loop; hyper-parameters are tuned only by an inner LOCO loop inside
   the training countries (nested).
4. Controls: label shuffle, without Germany, country-balanced metrics, within-year skill,
   coordinates ablation, adversarial validation.
5. EU freeze: final model per cutoff trained on all EU countries, SHA-256 checksums and the
   pre-registered Austrian zero-shot protocol in ``reports/freeze_protocol_cybench.md``.

AUSTRIA RULE (PLAN.md section 0/6, AGENTS.md section 8): no Austrian file is read here. The country
list excludes AT, every training/evaluation entry point asserts it, and ``predict_zero_shot`` is
only defined, never executed on Austria, before the project owner has released the protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import rankdata

from croptransfer.config import REPO_ROOT, load_config

AUSTRIA = "AT"
STATS = ("mean", "min", "max")


# --------------------------------------------------------------------------------------------
# Guards and paths
# --------------------------------------------------------------------------------------------
def assert_no_austria(countries: Any) -> None:
    """Hard guard of the Austria rule: Austria never enters training, tuning or evaluation."""
    assert AUSTRIA not in set(countries), "Austria must not be used before the EU freeze release"


def data_root() -> Path:
    """Folder that contains ``data/`` (env CROPTRANSFER_DATA_ROOT, default: repository root)."""
    return Path(os.environ.get("CROPTRANSFER_DATA_ROOT", REPO_ROOT))


def sha256_file(path: str | Path) -> str:
    """SHA-256 hex digest of a file (streamed)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_info() -> dict[str, Any]:
    """Current commit hash of the code and whether the working tree has uncommitted changes."""
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain", "--untracked-files=no"))}


# --------------------------------------------------------------------------------------------
# Yields and targets (PLAN.md 3.4)
# --------------------------------------------------------------------------------------------
def load_yields(cc: str, raw_dir: Path, allow_austria: bool = False) -> tuple[pd.DataFrame, dict[str, int]]:
    """Yield table of one country (t/ha) without zero/missing yields, plus filter counts.

    ``allow_austria`` is reserved for the zero-shot test after the project owner has released the
    freeze protocol; nothing in this module ever sets it.
    """
    if not allow_austria:
        assert_no_austria([cc])
    df = pd.read_csv(raw_dir / cc / f"yield_maize_{cc}.csv", usecols=["adm_id", "harvest_year", "yield"])
    n_raw = len(df)
    n_missing = int(df["yield"].isna().sum())
    n_zero = int((df["yield"] == 0).sum())
    df = df[df["yield"].notna() & (df["yield"] > 0)].rename(columns={"harvest_year": "year"})
    assert not df.duplicated(["adm_id", "year"]).any(), f"duplicate region-years in {cc}"
    df["country"] = cc
    df["year"] = df["year"].astype(int)
    stats = {"n_raw": n_raw, "n_missing": n_missing, "n_zero": n_zero, "n_valid": len(df)}
    return df[["country", "adm_id", "year", "yield"]].reset_index(drop=True), stats


def olympic_mean(values: Any) -> float:
    """Mean after dropping one maximum and one minimum (olympic average)."""
    v = np.sort(np.asarray(values, dtype=float))
    assert len(v) >= 3, "olympic mean needs at least 3 values"
    return float(v[1:-1].mean())


def add_yas(yields: pd.DataFrame, n_prior: int = 5, trend_window: int = 10, trend_min: int = 5) -> pd.DataFrame:
    """Add expectation, YAS and the linear-trend baseline using PREVIOUS years of a region only.

    Expectation = olympic mean of the years y-n_prior..y-1 (all must exist, otherwise NaN).
    Trend forecast = OLS line through the (up to ``trend_window``) previous years, evaluated in y.
    ``yas_trend`` = trend forecast / expectation, i.e. the trend baseline expressed as a YAS forecast.
    """
    rows = []
    for adm_id, g in yields.groupby("adm_id", sort=False):
        lookup = dict(zip(g["year"].to_numpy(), g["yield"].to_numpy(dtype=float)))
        for y, obs in lookup.items():
            prior = [lookup.get(y - k) for k in range(1, n_prior + 1)]
            if any(v is None for v in prior):
                rows.append((adm_id, y, np.nan, np.nan, np.nan))
                continue
            expectation = olympic_mean(prior)
            pts = [(yy, lookup[yy]) for yy in range(y - trend_window, y) if yy in lookup]
            trend_pred = np.nan
            if len(pts) >= trend_min:
                xs, ys = np.array(pts, dtype=float).T
                slope, intercept = np.polyfit(xs, ys, 1)
                trend_pred = float(intercept + slope * y)
            rows.append((adm_id, y, expectation, obs / expectation, trend_pred / expectation))
    extra = pd.DataFrame(rows, columns=["adm_id", "year", "expectation", "yas", "yas_trend"])
    return yields.merge(extra, on=["adm_id", "year"], how="left")


# --------------------------------------------------------------------------------------------
# Predictors: as-of aggregation (PLAN.md 3.5)
# --------------------------------------------------------------------------------------------
def _mmdd(s: str) -> tuple[int, int]:
    month, day = s.split("-")
    return int(month), int(day)


def asof_mask(dates: pd.Series, avail: pd.Series, cutoff: str, season_start: str) -> pd.Series:
    """Rows usable at ``cutoff`` (MM-DD of the observation year): available <= cutoff, in season.

    ``avail`` is the date from which the observation is known (== ``dates`` for daily data; the end of
    the composite window for fPAR/NDVI). Asserts that no selected row is later than the cutoff.
    """
    year = dates.dt.year
    cm, cd = _mmdd(cutoff)
    sm, sd = _mmdd(season_start)
    cutoff_dt = pd.to_datetime({"year": year, "month": cm, "day": cd})
    start_dt = pd.to_datetime({"year": year, "month": sm, "day": sd})
    mask = (avail <= cutoff_dt) & (dates >= start_dt)
    check_asof(avail[mask], cutoff_dt[mask])
    return mask


def check_asof(avail: pd.Series, cutoff_dt: pd.Series) -> None:
    """Assertion of the as-of rule: no selected observation may become known after its cutoff."""
    if len(avail):
        assert (cutoff_dt - avail).min() >= pd.Timedelta(0), "as-of violation: data after the cutoff"


def aggregate_asof(daily: pd.DataFrame, variables: list[str], sum_variables: list[str],
                   cutoff: str, season_start: str) -> pd.DataFrame:
    """Monthly mean/min/max (+ sum) per region-year from observations known at ``cutoff``.

    ``daily`` needs columns adm_id, date, avail and the variables. Columns of the result are
    ``<var>_<stat>_m<MM>``; the cutoff month is aggregated over its days up to the cutoff only.
    """
    sel = daily.loc[asof_mask(daily["date"], daily["avail"], cutoff, season_start)]
    if sel.empty:
        return pd.DataFrame(columns=["adm_id", "year"])
    agg = {v: [*STATS, *(["sum"] if v in sum_variables else [])] for v in variables}
    grouped = (sel.assign(year=sel["date"].dt.year, month=sel["date"].dt.month)
               .groupby(["adm_id", "year", "month"]).agg(agg))
    wide = grouped.unstack("month")
    wide.columns = [f"{v}_{s}_m{m:02d}" for v, s, m in wide.columns]
    return wide.reset_index()


def feature_columns(cutoff: str, cfg: dict[str, Any], season_start: str) -> list[str]:
    """Expected feature names of the cutoff: months season_start..cutoff month, plus static features."""
    cy = cfg["cybench"]
    first, last = _mmdd(season_start)[0], _mmdd(cutoff)[0]
    names = []
    for var in [v for vs in cy["variables"].values() for v in vs]:
        stats = [*STATS, *(["sum"] if var in cy["sum_variables"] else [])]
        names += [f"{var}_{s}_m{m:02d}" for m, s in product(range(first, last + 1), stats)]
    return names + list(cy["static_features"])


def read_daily_source(path: Path, variables: list[str], years: tuple[int, int], season_start: str,
                      last_cutoff: str, lag_days: int, valid_ranges: dict[str, list[float]]
                      ) -> tuple[pd.DataFrame, dict[str, int]]:
    """Read one predictor file restricted to season months / target years; out-of-range -> NaN."""
    df = pd.read_csv(path, usecols=["adm_id", "date", *variables],
                     dtype={"date": "int32", **{v: "float32" for v in variables}})
    year, mmdd = df["date"] // 10000, df["date"] % 10000
    lo, hi = _mmdd(season_start), _mmdd(last_cutoff)
    keep = (year >= years[0]) & (year <= years[1]) & (mmdd >= lo[0] * 100 + lo[1]) & (mmdd <= hi[0] * 100 + hi[1])
    df = df[keep].copy()
    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d")
    df["avail"] = df["date"] + pd.Timedelta(days=lag_days)
    n_bad = {}
    for v in variables:
        bad = (df[v] < valid_ranges[v][0]) | (df[v] > valid_ranges[v][1])
        n_bad[v] = int(bad.sum())
        df.loc[bad, v] = np.nan
        df[v] = df[v].astype("float64")
    return df, n_bad


def build_country(cc: str, cfg: dict[str, Any], raw_dir: Path, allow_austria: bool = False) -> dict[str, Any]:
    """All per-cutoff tables of one country plus data-quality counts (Austria blocked by default)."""
    if not allow_austria:
        assert_no_austria([cc])
    cy, season_start = cfg["cybench"], cfg["season"]["start_mmdd"]
    cutoffs = cfg["cutoffs"]["yield_model"]
    years = tuple(cy["target_years"])
    yields, ystats = load_yields(cc, raw_dir, allow_austria)
    yields = add_yas(yields, cfg["targets"]["yas_baseline_years"], cy["trend_window_years"], cy["trend_min_years"])
    soil = pd.read_csv(raw_dir / cc / f"soil_maize_{cc}.csv", usecols=["adm_id", *cy["static_features"]])
    loc = pd.read_csv(raw_dir / cc / f"location_maize_{cc}.csv", usecols=["adm_id", "latitude", "longitude"])
    per_cutoff: dict[str, list[pd.DataFrame]] = {c: [] for c in cutoffs}
    range_violations: dict[str, int] = {}
    for source, variables in cy["variables"].items():
        daily, n_bad = read_daily_source(
            raw_dir / cc / f"{source}_maize_{cc}.csv", variables, years, season_start, cutoffs[-1],
            cy["availability_lag_days"].get(source, 0), cy["valid_ranges"])
        range_violations.update(n_bad)
        for c in cutoffs:
            per_cutoff[c].append(aggregate_asof(daily, variables, cy["sum_variables"], c, season_start))
    out = {}
    for c in cutoffs:
        feats = per_cutoff[c][0]
        for other in per_cutoff[c][1:]:
            feats = feats.merge(other, on=["adm_id", "year"], how="outer")
        table = yields[(yields["year"] >= years[0]) & (yields["year"] <= years[1])].merge(
            feats, on=["adm_id", "year"], how="left")
        out[c] = table.merge(soil, on="adm_id", how="left").merge(loc, on="adm_id", how="left")
    return {"country": cc, "tables": out, "yield_stats": ystats, "range_violations": range_violations}


def build_eu_dataset(cfg: dict[str, Any], raw_dir: Path, countries: list[str] | None = None
                     ) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """EU dataset per cutoff (rows with defined YAS and meteo) and a data-quality report."""
    cy = cfg["cybench"]
    countries = list(countries or cy["countries"])
    assert_no_austria(countries)
    assert not set(countries) & set(cy["zero_only_countries"]), "zero-only countries must be excluded"
    results = Parallel(n_jobs=min(cy["n_jobs"], len(countries)))(
        delayed(build_country)(cc, cfg, raw_dir) for cc in countries)
    cutoffs = cfg["cutoffs"]["yield_model"]
    data, report = {}, {"yield_filter": {}, "range_violations": {}, "dropped": {}}
    for r in results:
        report["yield_filter"][r["country"]] = r["yield_stats"]
        for v, n in r["range_violations"].items():
            report["range_violations"][v] = report["range_violations"].get(v, 0) + n
    for c in cutoffs:
        table = pd.concat([r["tables"][c] for r in results], ignore_index=True)
        assert_no_austria(table["country"])
        assert not table["adm_id"].str.startswith(AUSTRIA).any()
        expected = feature_columns(c, cfg, cfg["season"]["start_mmdd"])
        table = table.reindex(columns=[*table.columns, *[f for f in expected if f not in table.columns]])
        has_yas = table["yas"].notna()
        meteo_cols = [col for col in expected if col.startswith("tmax_")]
        has_meteo = table[meteo_cols].notna().any(axis=1)
        if c == cutoffs[0]:
            report["stages_per_country"] = {
                cc: {"target_years_rows": int((g.index.size)), "with_5_prior_years": int(has_yas[g.index].sum()),
                     "kept": int((has_yas & has_meteo)[g.index].sum())}
                for cc, g in table.groupby("country")}
        report["dropped"][c] = {"before_yas_filter": len(table), "no_5_prior_years": int((~has_yas).sum()),
                                "no_meteo": int((has_yas & ~has_meteo).sum()), "kept": int((has_yas & has_meteo).sum())}
        data[c] = table[has_yas & has_meteo].reset_index(drop=True)
    return data, report


def _cache_fingerprint(cfg: dict[str, Any]) -> str:
    keys = ["raw_dir", "countries", "zero_only_countries", "target_years", "variables", "sum_variables",
            "static_features", "availability_lag_days", "trend_window_years",
            "trend_min_years", "valid_ranges"]
    blob = json.dumps({k: cfg["cybench"][k] for k in keys} | {"cutoffs": cfg["cutoffs"]["yield_model"],
                      "season": cfg["season"], "yas": cfg["targets"]}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def load_dataset(cfg: dict[str, Any], rebuild: bool = False) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """Build the EU dataset or read it from the parquet cache (invalidated by config changes)."""
    root = data_root()
    cache = root / cfg["cybench"]["cache_file"]
    meta = cache.with_suffix(".json")
    fingerprint = _cache_fingerprint(cfg)
    if cache.exists() and meta.exists() and not rebuild:
        info = json.loads(meta.read_text(encoding="utf-8"))
        if info["fingerprint"] == fingerprint:
            long = pd.read_parquet(cache)
            return {c: g.drop(columns="cutoff").reset_index(drop=True) for c, g in long.groupby("cutoff", sort=False)}, info["report"]
    data, report = build_eu_dataset(cfg, root / cfg["cybench"]["raw_dir"])
    cache.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([t.assign(cutoff=c) for c, t in data.items()], ignore_index=True).to_parquet(cache)
    meta.write_text(json.dumps({"fingerprint": fingerprint, "report": report}), encoding="utf-8")
    return data, report


# --------------------------------------------------------------------------------------------
# Splits, models
# --------------------------------------------------------------------------------------------
def loco_splits(countries: np.ndarray) -> Iterator[tuple[str, np.ndarray, np.ndarray]]:
    """Leave-one-country-out: yields (held-out country, train idx, test idx); sets never overlap."""
    countries = np.asarray(countries)
    for c in sorted(set(countries)):
        yield c, np.flatnonzero(countries != c), np.flatnonzero(countries == c)


def lgb_params(cfg: dict[str, Any], max_depth: int, min_child_samples: int, seed: int) -> dict[str, Any]:
    """LightGBM parameters; depth is capped (shallow trees) and the run is deterministic."""
    cy = cfg["cybench"]
    assert max_depth <= cy["max_depth_limit"], "trees must stay shallow (max_depth <= 3)"
    return {**cy["lightgbm"]["fixed"], "objective": "regression", "max_depth": max_depth,
            "num_leaves": 2 ** max_depth, "min_child_samples": min_child_samples, "seed": seed,
            "deterministic": True, "force_row_wise": True, "verbose": -1}


def train_booster(X: np.ndarray, y: np.ndarray, params: dict[str, Any], n_estimators: int,
                  feature_names: list[str]) -> Any:
    import lightgbm as lgb
    ds = lgb.Dataset(np.asarray(X, dtype=np.float32), label=y, feature_name=feature_names,
                     params={"verbose": -1, "max_bin": 255}, free_raw_data=True)
    return lgb.train(params, ds, num_boost_round=n_estimators)


def tune_hyperparameters(X: np.ndarray, y: np.ndarray, countries: np.ndarray, feature_names: list[str],
                         cfg: dict[str, Any], seed: int) -> dict[str, Any]:
    """Pick (max_depth, min_child_samples, n_estimators) by inner LOCO RMSE inside the given countries.

    Only the rows passed in are used, so calling this with the outer-training rows keeps the outer
    test country completely out of tuning. Ties go to the first (simplest) grid entry.
    """
    grid = cfg["cybench"]["lightgbm"]["grid"]
    n_list = sorted(grid["n_estimators"])
    combos = list(product(grid["max_depth"], grid["min_child_samples"]))
    sse = np.zeros((len(combos), len(n_list)))
    for _, tr, te in loco_splits(countries):
        for i, (depth, mcs) in enumerate(combos):
            booster = train_booster(X[tr], y[tr], lgb_params(cfg, depth, mcs, seed), n_list[-1], feature_names)
            for j, k in enumerate(n_list):
                sse[i, j] += float(((booster.predict(X[te], num_iteration=k) - y[te]) ** 2).sum())
    i, j = np.unravel_index(int(np.argmin(sse)), sse.shape)
    return {"max_depth": int(combos[i][0]), "min_child_samples": int(combos[i][1]),
            "n_estimators": int(n_list[j]), "inner_rmse": float(np.sqrt(sse[i, j] / len(y)))}


def _fold_task(X_tr, y_tr, c_tr, X_te, feature_names, cfg, seed, fixed: dict | None, shuffle_seed: int | None):
    """One outer fold: tune (unless ``fixed`` given), fit on the training countries, predict the test country."""
    if shuffle_seed is not None:
        y_tr = np.random.default_rng(shuffle_seed).permutation(y_tr)
    best = fixed or tune_hyperparameters(X_tr, y_tr, c_tr, feature_names, cfg, seed)
    booster = train_booster(X_tr, y_tr, lgb_params(cfg, best["max_depth"], best["min_child_samples"], seed),
                            best["n_estimators"], feature_names)
    return booster.predict(X_te, num_iteration=best["n_estimators"]), best


def run_loco(df: pd.DataFrame, features: list[str], cfg: dict[str, Any], seed: int, *,
             fixed: dict | None = None, shuffle_seed: int | None = None, exclude_train: list[str] | None = None,
             only_countries: list[str] | None = None) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Outer LOCO over the countries of ``df``; returns predictions and the per-fold hyper-parameters.

    ``exclude_train`` removes countries from every training set (e.g. Germany) but they are not
    evaluated either; ``only_countries`` restricts the evaluated test countries.
    """
    assert_no_austria(df["country"])
    X = df[features].to_numpy(dtype=np.float32)
    y = df["yas"].to_numpy(dtype=float)
    countries = df["country"].to_numpy()
    tasks, meta = [], []
    for c, tr, te in loco_splits(countries):
        if only_countries is not None and c not in only_countries:
            continue
        if exclude_train:
            tr = tr[~np.isin(countries[tr], exclude_train)]
        assert not set(countries[tr]) & set(countries[te]), "country in train and test"
        tasks.append((X[tr], y[tr], countries[tr], X[te], features, cfg, seed, fixed,
                      None if shuffle_seed is None else shuffle_seed + len(tasks)))
        meta.append((c, te))
    out = Parallel(n_jobs=cfg["cybench"]["n_jobs"])(delayed(_fold_task)(*t) for t in tasks)
    parts, params = [], []
    for (c, te), (pred, best) in zip(meta, out):
        part = df.iloc[te][["country", "adm_id", "year", "yas", "yas_trend"]].copy()
        part["pred"] = pred
        parts.append(part)
        params.append({"country": c, **best})
    pred_df = pd.concat(parts, ignore_index=True)
    pred_df["yas1"] = 1.0
    return pred_df, params


def modal_params(fold_params: list[dict[str, Any]]) -> dict[str, Any]:
    """Most frequent (depth, min_child_samples, n_estimators) over the outer folds (ties: first seen)."""
    keys = [(p["max_depth"], p["min_child_samples"], p["n_estimators"]) for p in fold_params]
    best = max(dict.fromkeys(keys), key=keys.count)
    return {"max_depth": best[0], "min_child_samples": best[1], "n_estimators": best[2]}


# --------------------------------------------------------------------------------------------
# Metrics and bootstrap
# --------------------------------------------------------------------------------------------
def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def metrics_joint(y: np.ndarray, p: np.ndarray, trend: np.ndarray | None = None,
                  w: np.ndarray | None = None) -> dict[str, float]:
    """R2, RMSE, MAE, Spearman of the model, of YAS = 1 and of the trend baseline, plus skills/differences.

    ``w`` are optional sample weights (country-balanced evaluation). Skill = 1 - MSE_model / MSE_baseline.
    """
    w = np.ones_like(y) if w is None else w
    wsum = w.sum()

    def basic(pred: np.ndarray, prefix: str) -> dict[str, float]:
        err = pred - y
        mse = float((w * err ** 2).sum() / wsum)
        mean_y = float((w * y).sum() / wsum)
        sst = float((w * (y - mean_y) ** 2).sum() / wsum)
        return {f"{prefix}_r2": 1 - mse / sst, f"{prefix}_rmse": mse ** 0.5,
                f"{prefix}_mae": float((w * np.abs(err)).sum() / wsum), f"{prefix}_spearman": _spearman(y, pred)}

    out = basic(p, "model") | basic(np.ones_like(y), "yas1")
    out["skill_vs_yas1"] = 1 - out["model_rmse"] ** 2 / out["yas1_rmse"] ** 2
    out["rmse_diff_vs_yas1"] = out["model_rmse"] - out["yas1_rmse"]
    if trend is not None:
        out |= basic(trend, "trend")
        out["skill_vs_trend"] = 1 - out["model_rmse"] ** 2 / out["trend_rmse"] ** 2
        out["rmse_diff_vs_trend"] = out["model_rmse"] - out["trend_rmse"]
    return out


def bootstrap_indices(n: int, rng: np.random.Generator, strata: np.ndarray | None = None,
                      clusters: np.ndarray | None = None) -> np.ndarray:
    """Resample row indices: plain, within strata, or whole clusters."""
    if clusters is not None:
        codes, uniq = pd.factorize(clusters)
        members = [np.flatnonzero(codes == k) for k in range(len(uniq))]
        picked = rng.integers(0, len(uniq), len(uniq))
        return np.concatenate([members[k] for k in picked])
    if strata is not None:
        parts = []
        for s in np.unique(strata):
            idx = np.flatnonzero(strata == s)
            parts.append(rng.choice(idx, len(idx), replace=True))
        return np.concatenate(parts)
    return rng.integers(0, n, n)


def bootstrap_metrics(pred_df: pd.DataFrame, n_boot: int, level: float, seed: int, *,
                      balanced: bool = False, cluster_by: str | None = None) -> dict[str, dict[str, float]]:
    """Point estimate and percentile CI of ``metrics_joint`` over region-years.

    cluster_by='country_year' resamples whole country-years (keeps the same-year dependence);
    balanced=True weights countries equally and resamples within each country.
    """
    y, p = pred_df["yas"].to_numpy(float), pred_df["pred"].to_numpy(float)
    t = pred_df["yas_trend"].to_numpy(float)
    countries = pred_df["country"].to_numpy()
    w = None
    if balanced:
        counts = pd.Series(countries).map(pd.Series(countries).value_counts()).to_numpy(float)
        w = 1.0 / counts
    clusters = None
    if cluster_by == "country_year":
        clusters = (pred_df["country"] + "_" + pred_df["year"].astype(str)).to_numpy()
    point = metrics_joint(y, p, t, w)
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(n_boot):
        idx = bootstrap_indices(len(y), rng, strata=countries if balanced else None, clusters=clusters)
        draws.append(metrics_joint(y[idx], p[idx], t[idx], None if w is None else w[idx]))
    draws_df = pd.DataFrame(draws)
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    return {k: {"value": float(point[k]), "lo": float(draws_df[k].quantile(lo)),
                "hi": float(draws_df[k].quantile(hi))} for k in point}


def group_spearman(pred_df: pd.DataFrame, by: list[str], min_n: int, n_boot: int, level: float,
                   seed: int) -> dict[str, Any]:
    """Mean of per-group Spearman correlations (e.g. within a year across regions), CI over groups."""
    rhos = []
    for _, g in pred_df.groupby(by):
        if len(g) >= min_n:
            r = _spearman(g["yas"].to_numpy(float), g["pred"].to_numpy(float))
            if not np.isnan(r):
                rhos.append(r)
    rhos_arr = np.array(rhos)
    rng = np.random.default_rng(seed)
    means = [rhos_arr[rng.integers(0, len(rhos_arr), len(rhos_arr))].mean() for _ in range(n_boot)]
    return {"mean_rho": float(rhos_arr.mean()), "lo": float(np.quantile(means, (1 - level) / 2)),
            "hi": float(np.quantile(means, 1 - (1 - level) / 2)), "n_groups": len(rhos_arr)}


def yearly_mean_correlation(pred_df: pd.DataFrame) -> dict[str, float]:
    """Correlation of year means (observed vs predicted YAS) = pure year signal ('year proxy')."""
    m = pred_df.groupby("year")[["yas", "pred"]].mean()
    return {"spearman": _spearman(m["yas"].to_numpy(), m["pred"].to_numpy()), "n_years": int(len(m))}


def per_country_metrics(pred_df: pd.DataFrame, min_n: int) -> dict[str, dict[str, float]]:
    out = {}
    for c, g in pred_df.groupby("country"):
        y, p = g["yas"].to_numpy(float), g["pred"].to_numpy(float)
        m = metrics_joint(y, p, g["yas_trend"].to_numpy(float))
        out[c] = {"n": len(g), "r2": m["model_r2"], "spearman": m["model_spearman"],
                  "rmse": m["model_rmse"], "skill_vs_yas1": m["skill_vs_yas1"],
                  "reported": len(g) >= min_n}
    return out


def evaluate_predictions(pred_df: pd.DataFrame, cfg: dict[str, Any], seed: int) -> dict[str, Any]:
    """Full metric block of one cutoff (all variants requested for the data review)."""
    v = cfg["validation"]
    n_boot, level = v["bootstrap_n"], v["ci_level"]
    cy = cfg["cybench"]
    res: dict[str, Any] = {
        "n_region_years": len(pred_df), "n_countries": int(pred_df["country"].nunique()),
        "pooled": bootstrap_metrics(pred_df, n_boot, level, seed),
        "pooled_cluster_bootstrap": bootstrap_metrics(pred_df, n_boot, level, seed, cluster_by="country_year"),
        "country_balanced": bootstrap_metrics(pred_df, n_boot, level, seed, balanced=True),
        "within_year": group_spearman(pred_df, ["year"], cy["min_regions_within_year"], n_boot, level, seed),
        "within_country_year": group_spearman(pred_df, ["country", "year"], cy["min_regions_within_country_year"],
                                              n_boot, level, seed),
        "yearly_mean": yearly_mean_correlation(pred_df),
        "per_country": per_country_metrics(pred_df, cy["min_region_years_country_metrics"]),
    }
    reported = [m for m in res["per_country"].values() if m["reported"]]
    res["macro_over_countries"] = {"n_countries": len(reported),
                                   "r2": float(np.mean([m["r2"] for m in reported])),
                                   "spearman": float(np.nanmean([m["spearman"] for m in reported]))}
    no_de = pred_df[pred_df["country"] != "DE"]
    res["without_DE_eval"] = {"n_region_years": len(no_de),
                              "metrics": bootstrap_metrics(no_de, n_boot, level, seed)}
    return res


# --------------------------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------------------------
def adversarial_auc(df: pd.DataFrame, features: list[str], cfg: dict[str, Any], seed: int,
                    max_rows: int = 4000) -> dict[str, dict[str, Any]]:
    """Per country: AUC of a small classifier separating that country from the rest (2-fold CV)."""
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold
    rng = np.random.default_rng(seed)
    out = {}
    X_all = df[features].to_numpy(np.float32)
    for c in sorted(df["country"].unique()):
        label = (df["country"] == c).to_numpy().astype(int)
        pos, neg = np.flatnonzero(label == 1), np.flatnonzero(label == 0)
        idx = np.concatenate([rng.choice(pos, min(len(pos), max_rows), replace=False),
                              rng.choice(neg, min(len(neg), max_rows), replace=False)])
        X, yb = X_all[idx], label[idx]
        if yb.sum() < 10:
            out[c] = {"auc": None, "n": int(len(pos))}
            continue
        aucs, gains = [], np.zeros(len(features))
        for tr, te in StratifiedKFold(2, shuffle=True, random_state=seed).split(X, yb):
            model = lgb.train({"objective": "binary", "max_depth": 3, "num_leaves": 8, "learning_rate": 0.1,
                               "seed": seed, "verbose": -1, "num_threads": 1, "deterministic": True},
                              lgb.Dataset(X[tr], yb[tr], feature_name=features), 100)
            aucs.append(roc_auc_score(yb[te], model.predict(X[te])))
            gains += model.feature_importance("gain")
        out[c] = {"auc": float(np.mean(aucs)), "n": int(len(pos)), "top_feature": features[int(np.argmax(gains))]}
    return out


def case_studies(pred_df: pd.DataFrame, k: int = 3) -> dict[str, list[dict[str, Any]]]:
    """The k best and k worst predictions by absolute YAS error (to be looked at, not just counted)."""
    d = pred_df.assign(abs_err=(pred_df["pred"] - pred_df["yas"]).abs()).sort_values("abs_err")
    cols = ["country", "adm_id", "year", "yas", "pred", "abs_err"]
    return {"best": d.head(k)[cols].round(6).to_dict("records"), "worst": d.tail(k)[cols].round(6).to_dict("records")}


def data_structure_summary(df: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    """Who is in the dataset: rows/regions per country, NUTS level (by id length), yield and YAS extremes."""
    thr = cfg["targets"]["at_risk_threshold"]
    lo, hi = cfg["cybench"]["robust_yas_range"]
    level = df["adm_id"].str.len().map({4: "NUTS2", 5: "NUTS3"}).fillna("other")
    per_country = {}
    for c, g in df.assign(level=level).groupby("country"):
        per_country[c] = {"region_years": len(g), "regions": int(g["adm_id"].nunique()), "level": g["level"].mode().iloc[0],
                          "years": [int(g["year"].min()), int(g["year"].max())], "mean_yield": round(float(g["yield"].mean()), 2),
                          "n_yield_above_20": int((g["yield"] > 20).sum()), "n_yas_below_threshold": int((g["yas"] < thr).sum()),
                          "n_yas_outside_robust_range": int(((g["yas"] < lo) | (g["yas"] > hi)).sum())}
    return {"n_region_years": len(df), "n_regions": int(df["adm_id"].nunique()),
            "share_by_level": level.value_counts(normalize=True).round(3).to_dict(),
            "share_DE": round(float((df["country"] == "DE").mean()), 3),
            "n_yield_above_20": int((df["yield"] > 20).sum()),
            "n_yas_outside_robust_range": int(((df["yas"] < lo) | (df["yas"] > hi)).sum()),
            "per_country": per_country}


def freeze_importance(freeze_dir: Path, cutoffs: list[str], static: list[str]) -> dict[str, dict[str, float]]:
    """Share of the total split gain per predictor variable in each frozen model (who carries the signal?)."""
    import lightgbm as lgb
    out = {}
    for cutoff in cutoffs:
        booster = lgb.Booster(model_file=str(freeze_dir / f"lgbm_{cutoff_tag(cutoff)}.txt"))
        gain = pd.Series(booster.feature_importance("gain"), index=booster.feature_name())
        group = pd.Series([n if n in static else n.split("_")[0] for n in gain.index], index=gain.index)
        share = gain.groupby(group).sum() / gain.sum()
        out[cutoff] = {k: round(float(v), 4) for k, v in share.sort_values(ascending=False).items()}
    return out


def target_summary(df: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    """Distribution of YAS (overall, per year, per country) and stress-case counts."""
    thr = cfg["targets"]["at_risk_threshold"]
    by_year = df.groupby("year")["yas"].agg(["count", "mean", "std", lambda s: (s < thr).mean()])
    by_year.columns = ["n", "mean", "sd", "share_below_threshold"]
    by_country = df.groupby("country")["yas"].agg(["count", "mean", "std", "min", "max"])
    return {"yas_quantiles": df["yas"].quantile([0, .01, .05, .25, .5, .75, .95, .99, 1]).round(3).to_dict(),
            "n_below_threshold": int((df["yas"] < thr).sum()), "threshold": thr,
            "by_year": by_year.round(3).to_dict("index"), "by_country": by_country.round(3).to_dict("index")}


# --------------------------------------------------------------------------------------------
# EU freeze and zero-shot prediction function (NOT executed on Austria here)
# --------------------------------------------------------------------------------------------
def model_features(df: pd.DataFrame, cutoff: str, cfg: dict[str, Any]) -> list[str]:
    """Feature columns of a cutoff, dropping columns without any observation (e.g. composites not yet
    available for the cutoff month because of the availability lag)."""
    cols = feature_columns(cutoff, cfg, cfg["season"]["start_mmdd"])
    return [c for c in cols if df[c].notna().any()]


def cutoff_tag(cutoff: str) -> str:
    return cutoff.replace("-", "")


def freeze_models(data: dict[str, pd.DataFrame], cfg: dict[str, Any], out_dir: Path, seed: int,
                  features_by_cutoff: dict[str, list[str]]) -> dict[str, dict[str, Any]]:
    """Train the final model per cutoff on ALL EU countries; write model + feature/params json.

    Tuning: the same nested-free inner LOCO over all EU countries (no Austria exists in the data).
    Returns {filename: {sha256, cutoff, kind}}.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    for cutoff, df in data.items():
        assert_no_austria(df["country"])
        feats = features_by_cutoff[cutoff]
        X, y, countries = df[feats].to_numpy(np.float32), df["yas"].to_numpy(float), df["country"].to_numpy()
        best = tune_hyperparameters(X, y, countries, feats, cfg, seed)
        params = lgb_params(cfg, best["max_depth"], best["min_child_samples"], seed)
        booster = train_booster(X, y, params, best["n_estimators"], feats)
        tag = cutoff_tag(cutoff)
        model_path = out_dir / f"lgbm_{tag}.txt"
        booster.save_model(str(model_path))
        meta = {"cutoff": cutoff, "target": "YAS", "features": feats, "hyperparameters": best,
                "lightgbm_params": params, "n_estimators": best["n_estimators"],
                "preprocessing": "none (no imputation, no scaling; missing values handled natively by LightGBM)",
                "train_region_years": int(len(df)), "train_countries": sorted(set(countries))}
        meta_path = out_dir / f"lgbm_{tag}_meta.json"
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
        files[model_path.name] = {"sha256": sha256_file(model_path), "cutoff": cutoff, "kind": "model"}
        files[meta_path.name] = {"sha256": sha256_file(meta_path), "cutoff": cutoff, "kind": "meta"}
    return files


def read_registered_hashes(protocol_path: Path) -> dict[str, str]:
    """Parse ``| `file` | `sha256` |`` rows of the checksum table in the freeze protocol."""
    text = protocol_path.read_text(encoding="utf-8")
    return dict(re.findall(r"\|\s*`([^`|]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", text))


def verify_freeze(freeze_dir: Path, protocol_path: Path) -> list[str]:
    """Check every registered file against its SHA-256; returns the verified file names (raises on mismatch)."""
    registered = read_registered_hashes(protocol_path)
    assert registered, "no checksums registered in the freeze protocol"
    for name, digest in registered.items():
        actual = sha256_file(freeze_dir / name)
        assert actual == digest, f"checksum mismatch for {name}"
    return sorted(registered)


def predict_zero_shot(features: pd.DataFrame, cutoff: str, freeze_dir: Path, protocol_path: Path) -> np.ndarray:
    """Predict YAS with the FROZEN EU model of ``cutoff`` for regions of a country never seen in training.

    Verifies all checksums first, aligns the columns to the frozen feature list and applies the model
    unchanged. Defined for the later Austrian zero-shot test; it must not be run on Austria before
    the project owner has released ``reports/freeze_protocol_cybench.md``.
    """
    import lightgbm as lgb
    verify_freeze(freeze_dir, protocol_path)
    tag = cutoff_tag(cutoff)
    meta = json.loads((freeze_dir / f"lgbm_{tag}_meta.json").read_text(encoding="utf-8"))
    missing = [f for f in meta["features"] if f not in features.columns]
    assert not missing, f"missing frozen features: {missing[:5]}"
    booster = lgb.Booster(model_file=str(freeze_dir / f"lgbm_{tag}.txt"))
    return booster.predict(features[meta["features"]].to_numpy(np.float32), num_iteration=meta["n_estimators"])


# --------------------------------------------------------------------------------------------
# Orchestration, figure, protocol
# --------------------------------------------------------------------------------------------
def compact(bm: dict[str, dict[str, float]], keys: tuple[str, ...] = ("model_r2", "model_rmse", "model_spearman",
                                                                       "skill_vs_yas1")) -> dict[str, Any]:
    return {k: {kk: round(vv, 4) for kk, vv in bm[k].items()} for k in keys}


def _evaluate_cutoff(cutoff: str, preds: dict[str, pd.DataFrame], cfg: dict[str, Any], seed: int) -> dict[str, Any]:
    """All metrics of one cutoff from its prediction tables (runs in a worker process)."""
    v = cfg["validation"]
    n_boot, level = v["bootstrap_n"], v["ci_level"]
    main = preds["main"]
    res = evaluate_predictions(main, cfg, seed)
    lo, hi = cfg["cybench"]["robust_yas_range"]
    robust = main[(main["yas"] >= lo) & (main["yas"] <= hi)]
    res["robust_yas_range"] = {"range": [lo, hi], "n_region_years": len(robust),
                               "metrics": bootstrap_metrics(robust, n_boot, level, seed)}
    res["variants"] = {}
    for name, df in preds.items():
        if name == "main":
            continue
        if name.startswith("shuffle_"):
            continue
        res["variants"][name] = {"n_region_years": len(df), "metrics": bootstrap_metrics(df, n_boot, level, seed)}
        if name == "train_without_DE":
            same = main[main["country"] != "DE"]
            res["variants"][name]["reference_main_on_same_rows"] = bootstrap_metrics(same, n_boot, level, seed)
    shuffles = [metrics_joint(d["yas"].to_numpy(float), d["pred"].to_numpy(float), d["yas_trend"].to_numpy(float))
                for n, d in preds.items() if n.startswith("shuffle_")]
    res["label_shuffle"] = {"repeats": len(shuffles),
                            **{k: [round(float(m[k]), 4) for m in shuffles]
                               for k in ("model_r2", "model_spearman", "skill_vs_yas1")}}
    return res


def run_experiments(cfg: dict[str, Any], data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Outer LOCO for all cutoffs plus the control variants; returns metrics and prediction tables."""
    seed = cfg["seed"]
    cy = cfg["cybench"]
    preds_by_cutoff: dict[str, dict[str, pd.DataFrame]] = {}
    fold_params: dict[str, list] = {}
    features_by_cutoff: dict[str, list[str]] = {}
    for cutoff, df in data.items():
        feats = model_features(df, cutoff, cfg)
        features_by_cutoff[cutoff] = feats
        main, params = run_loco(df, feats, cfg, seed)
        fold_params[cutoff] = params
        fixed = modal_params(params)
        preds = {"main": main}
        non_de = [c for c in sorted(df["country"].unique()) if c != "DE"]
        preds["train_without_DE"], _ = run_loco(df, feats, cfg, seed, fixed=fixed, exclude_train=["DE"],
                                                only_countries=non_de)
        coord_df = df.assign(lat=df["latitude"], lon=df["longitude"])
        preds["with_coordinates"], _ = run_loco(coord_df, [*feats, "lat", "lon"], cfg, seed, fixed=fixed)
        static = list(cy["static_features"])
        preds["without_static_features"], _ = run_loco(df, [f for f in feats if f not in static], cfg, seed,
                                                       fixed=fixed)
        for r in range(cy["shuffle_repeats"]):
            preds[f"shuffle_{r}"], _ = run_loco(df, feats, cfg, seed, fixed=fixed, shuffle_seed=seed + 1000 * (r + 1))
        preds_by_cutoff[cutoff] = preds
        print(f"[{cutoff}] LOCO done: n={len(main)}, modal params {fixed}", flush=True)
    evaluated = Parallel(n_jobs=min(cy["n_jobs"], len(data)))(
        delayed(_evaluate_cutoff)(c, preds_by_cutoff[c], cfg, seed) for c in data)
    metrics = {c: {**res, "n_features": len(features_by_cutoff[c]),
                   "modal_hyperparameters": modal_params(fold_params[c]),
                   "fold_hyperparameters": fold_params[c]}
               for c, res in zip(data, evaluated)}
    return {"metrics": metrics, "preds": preds_by_cutoff, "features": features_by_cutoff}


def plot_earlywarning(metrics: dict[str, Any], path: Path) -> None:
    """Early-warning curve: skill of the LOCO model against the cutoff date (3 panels)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cutoffs = list(metrics)
    x = np.arange(len(cutoffs))
    blue, orange, grey = "#0072B2", "#E69F00", "#6b6b6b"
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.1), constrained_layout=True)

    def band(ax, key, getter, color, label, ls="-", ci=True):
        vals = [getter(metrics[c], key) for c in cutoffs]
        ax.plot(x, [v["value"] for v in vals], ls, color=color, marker="o", ms=3, label=label)
        if ci:
            ax.fill_between(x, [v["lo"] for v in vals], [v["hi"] for v in vals], color=color, alpha=0.18, lw=0)

    pooled = lambda m, k: m["pooled"][k]
    band(axes[0], "model_r2", pooled, blue, "LightGBM (LOCO)")
    band(axes[0], "trend_r2", pooled, orange, "Trend (ohne KI)", ci=False)
    axes[0].axhline(metrics[cutoffs[0]]["pooled"]["yas1_r2"]["value"], color=grey, ls="--", lw=1, label="YAS = 1")
    axes[0].set_ylabel("R² (YAS)")
    band(axes[1], "model_spearman", pooled, blue, "alle Region-Jahre")
    axes[1].plot(x, [metrics[c]["within_year"]["mean_rho"] for c in cutoffs], "-", color=orange, marker="s", ms=3,
                 label="innerhalb eines Jahres")
    axes[1].fill_between(x, [metrics[c]["within_year"]["lo"] for c in cutoffs],
                         [metrics[c]["within_year"]["hi"] for c in cutoffs], color=orange, alpha=0.18, lw=0)
    axes[1].axhline(0, color=grey, lw=0.8)
    axes[1].set_ylabel("Spearman ρ")
    band(axes[2], "skill_vs_yas1", pooled, blue, "Skill vs. YAS = 1")
    axes[2].axhline(0, color=grey, lw=0.8)
    axes[2].set_ylabel("Skill (1 − MSE/MSE₀)")
    for ax in axes:
        ax.set_xticks(x, cutoffs, rotation=45, fontsize=8)
        ax.set_xlabel("Stichtag (MM-TT)")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7, frameon=False)
    n = metrics[cutoffs[-1]]["n_region_years"]
    fig.suptitle(f"CY-Bench EU-Mais, Leave-One-Country-Out (n = {n} Region-Jahre, 95-%-Bootstrap-KI)", fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _fmt_ci(m: dict[str, float], digits: int = 2) -> str:
    return f"{m['value']:.{digits}f} [{m['lo']:.{digits}f}; {m['hi']:.{digits}f}]"


PROTOCOL_TEMPLATE = """# Freeze-Protokoll CY-Bench-Regionalmodell (Phase 5, EU-Freeze)

**Status:** EU-Freeze durchgeführt am {today}. **Der Zero-Shot-Test Österreich ist gesperrt**, bis der Projektinhaber
dieses Protokoll gelesen und freigegeben hat (`DECISIONS.md`, Arbeitsgrenze Freeze). Nach der Freigabe wird am Modell nichts
mehr geändert; ein dokumentierter Fehler führt zu einem neuen Freeze, beide Ergebnisse werden berichtet.

- Code-Stand (Git-Commit beim Freeze): `{commit}`{dirty}
- Erzeugt von `python -m croptransfer.regional_cybench` (Seed {seed}, `config.yaml` Abschnitt `cybench`).
- Datengrundlage: CY-Bench v1.10 (Zenodo 10.5281/zenodo.17279151), Mais, {n_countries} EU-Länder ({countries}); **kein Österreich**
  (Länderliste ohne AT, `assert "AT" not in countries`, Test `test_austria_is_excluded`). Ausgeschlossen: EE, FI, IE, LV (nur Nullerträge);
  DK und SE liefern nach der 5-Vorjahre-Regel keine Region-Jahre.
- Österreich-Regel eingehalten: **Es wurde keine österreichische Datei gelesen** (weder Erträge noch Prädiktoren), nichts an Training, Merkmalen,
  Hyperparametern oder Modellwahl hängt von Österreich ab.

## 1. Zielgröße und Vorverarbeitung
- Ziel: `YAS = Ertrag / olympischer Durchschnitt (ohne Max/Min) der 5 Vorjahre derselben Region` (PLAN 3.4). Alle 5 Kalenderjahre `y-5…y-1`
  müssen einen gültigen Ertrag (> 0) haben, sonst entfällt das Region-Jahr. Trainingsjahre {years}.
- Vorverarbeitung: **keine** (keine Imputation, keine Skalierung); fehlende Werte behandelt LightGBM nativ. Statische Merkmale: `awc`, `bulk_density`.
- Prädiktoren je Region-Jahr und Stichtag: Monatsmittel/-min/-max (zusätzlich Monatssumme für `prec`, `cwb`) von `tmax, tmin, prec, cwb, rsm, ssm, fpar, ndvi`
  für die Monate April bis Stichtagsmonat. **As-of-Regel:** nur Beobachtungen, die am Stichtag bekannt sind (Datum ≤ Stichtag); fPAR (Dekade, Etikett = Beginn)
  zählt ab Etikett + {lag_fpar} Tage, NDVI (8-Tage-Fenster) ab Etikett + {lag_ndvi} Tage. Der Stichtagsmonat enthält nur die Tage bis zum Stichtag.
- Keine Koordinaten, keine Landes- oder Regions-ID, kein Jahr als Merkmal.

## 2. Modell und Hyperparameter
- LightGBM (Regression, L2), flache Bäume (`max_depth ≤ 3`, `num_leaves = 2^max_depth`), `learning_rate {lr}`, `subsample {subsample}`, `colsample_bytree {colsample}`,
  `reg_lambda {reg_lambda}`, deterministisch, 1 Thread, Seed {seed}.
- Hyperparameter-Suchraum (nur über Leave-One-Country-Out innerhalb der Trainingsländer): `max_depth` {g_depth}, `min_child_samples` {g_mcs}, `n_estimators` {g_n}.
- Gewählte Hyperparameter des finalen Modells (Tuning per LOCO über alle {n_countries} EU-Länder):

{hp_table}

## 3. Merkmalsliste
Anzahl je Stichtag: {n_feat_table}. Die Namen folgen `<variable>_<statistik>_m<MM>` (Statistik ∈ mean, min, max, sum; Monat MM = 04 … Stichtagsmonat).
Vollständige Liste des letzten Stichtags (die früheren Stichtage verwenden die Teilmenge der Monate bis zu ihrem Stichtagsmonat; Merkmale ohne Beobachtung am Stichtag entfallen):

```
{features_last}
```
Die exakte Liste je Stichtag steht in `lgbm_<MMTT>_meta.json` (mit Prüfsumme unten).

## 4. EU-Ergebnisse (äußere Leave-One-Country-Out-Evaluation, Zusammenfassung)
{eval_table}

Einordnung (ehrlich): Das Modell ist **schwach**. Am Stichtag {last_cutoff} erklärt es R² = {r2_last} der Varianz von YAS, ρ = {rho_last} über alle Region-Jahre,
aber nur ρ = {wy_last} **innerhalb eines Jahres** (der größere Teil des ρ ist das Jahressignal). Vor dem 15.7. besteht kein Skill gegenüber YAS = 1.
Das vorab festgelegte Kriterium „ρ > 0 mit KI ohne 0“ ist ein niedriger Maßstab; es wird deshalb **nicht** nachträglich verschärft oder gelockert, und die Zusatzkennzahlen unten
(Skill, ρ innerhalb eines Jahres, Cluster-KI) werden immer mit berichtet.

Vollständige Kennzahlen (inkl. ohne Deutschland, länderbalanciert, innerhalb eines Jahres, Label-Shuffle): `results/{result_dir}/metrics.json`.

## 5. Prüfsummen (SHA-256) der eingefrorenen Dateien
Ablage: `results/models/cybench_freeze/` (nicht in Git; mit `python -m croptransfer.regional_cybench` reproduzierbar, die Prüfung
`verify_freeze` vergleicht gegen diese Tabelle).

| Datei | SHA-256 |
|---|---|
{hash_rows}

## 6. Vorab registriertes Zero-Shot-Testprotokoll Österreich (gilt erst nach Freigabe)
**Ziel:** Messen, ob das eingefrorene EU-Modell die Ertragsanomalie österreichischer Bundesländer ohne jede Anpassung vorhersagt (Weg V1 in PLAN Phase 7, Gegenprobe zum Feldmodell).

**Testdaten:** CY-Bench v1.10, Mais, Österreich (NUTS-2 = Bundesländer), Prädiktoren mit derselben Pipeline (`build_country(..., allow_austria=True)`, aktuell nirgends aufgerufen).
- Region-Jahre **2006–2020** (die Erträge in CY-Bench enden 2020). Ausgeschlossen: Wien (AT13), Salzburg (AT32), Tirol (AT33), Vorarlberg (AT34) (< 250 ha Mais, Rundungsartefakte).
  Es verbleiben AT11 Burgenland, AT12 Niederösterreich, AT21 Kärnten, AT22 Steiermark, AT31 Oberösterreich → erwartet **n = 5 × 15 = 75 Region-Jahre**.
- Zielgröße `YAS` exakt wie oben (Vorjahre aus CY-Bench, auch 2001–2005 für 2006).
- Vorhersage: `predict_zero_shot(features, cutoff, freeze_dir, protocol_path)` – prüft zuerst alle Prüfsummen aus Abschnitt 5, wendet das Modell unverändert an;
  keine Rekalibrierung, keine Verschiebung des Mittelwerts, kein Nachtrainieren, kein Zurücklegen von Österreich in irgendeinen Trainings- oder Tuningschritt.
- **Offen, Projektinhaber entscheidet vor dem Test:** Ergänzung der Jahre 2021–2023 aus Statistik Austria (Prädiktoren 2021–2023 sind in CY-Bench vorhanden, Erträge nicht).
  Vorschlag: Hauptergebnis nur 2006–2020 (CY-Bench), die Erweiterung zusätzlich und klar getrennt berichten. Die Entscheidung wird **vor** dem ersten Lauf schriftlich in `DECISIONS.md` festgehalten.

**Metriken (je Stichtag {cutoffs}):** Spearman ρ(vorhergesagter YAS, beobachteter YAS); RMSE des Modells und der Baseline YAS = 1 und deren Differenz; R², Skill gegenüber YAS = 1 und gegenüber der
Trendfortschreibung; ρ innerhalb eines Jahres (Jahres-Proxy-Kontrolle). Konfidenzintervalle: Bootstrap über Region-Jahre, {n_boot} Ziehungen, Perzentil-95-%-KI, Seed {seed}
(`bootstrap_metrics`, dieselbe Funktion wie in der EU-Evaluation). Zusätzlich (Sensitivität) Bootstrap über ganze Jahre (Cluster), da Bundesländer im selben Jahr korreliert sind.

**Erfolgskriterien (wie PLAN Phase 7, V1):**
- **Bestanden (regional):** am Stichtag **09-01** ρ > 0 und die untere Grenze des 95-%-KI von ρ > 0.
- **Stark (regional):** zusätzlich RMSE(Modell) < RMSE(YAS = 1), d. h. das 95-%-KI der Differenz `RMSE_Modell − RMSE_Baseline` liegt vollständig unter 0.
- **Alle Stichtage werden berichtet**, nicht nur der beste; die übrigen Stichtage sind beschreibend (kein zweites Erfolgskriterium, keine Auswahl).
- Liegt nur das Cluster-KI (Jahre) bei 0 oder darüber, wird „bestanden“ mit der Einschränkung „nicht robust gegen gemeinsame Jahreseffekte“ berichtet.
- Bei n = 75 sind die Intervalle breit; das Ergebnis wird mit n und KI berichtet, auch wenn das Kriterium nicht erfüllt ist.
- Vergleichswert: publizierte CY-Bench-Baseline AT (R² 0,13, Datenversion v1.8, In-Domain-LOYO) – anderer Aufbau, nur als Einordnung.

**Nicht Teil dieses Tests (getrennt, Phase 5b / F5):** In-Domain AT (LOYO), Pooled, Few-Shot.

## 7. Eigenerklärung zur Österreich-Regel
- Vor dem Freeze wurden keine österreichischen Daten ausgewertet oder genutzt (Training, Merkmalsauswahl, Schwellen, Modellwahl, Hyperparameter): **ja, eingehalten**.
- Nach dem Freeze wurde nichts am Modell geändert: Prüfsummen siehe Abschnitt 5.
"""


def write_freeze_protocol(path: Path, cfg: dict[str, Any], files: dict[str, dict[str, Any]], metrics: dict[str, Any],
                          features: dict[str, list[str]], data: dict[str, pd.DataFrame], result_dir: str, git: dict[str, Any],
                          freeze_dir: Path) -> None:
    cy, lgbc = cfg["cybench"], cfg["cybench"]["lightgbm"]
    hp_rows = ["| Stichtag | max_depth | min_child_samples | n_estimators | Trainings-Region-Jahre |", "|---|---|---|---|---|"]
    for cutoff in data:
        meta = json.loads((freeze_dir / f"lgbm_{cutoff_tag(cutoff)}_meta.json").read_text(encoding="utf-8"))
        h = meta["hyperparameters"]
        hp_rows.append(f"| {cutoff} | {h['max_depth']} | {h['min_child_samples']} | {h['n_estimators']} | {meta['train_region_years']} |")
    ev_rows = ["| Stichtag | n Region-Jahre | R² [95-%-KI] | ρ [95-%-KI] | ρ innerhalb Jahr | Skill vs. YAS=1 [95-%-KI] |", "|---|---|---|---|---|---|"]
    for c, m in metrics.items():
        p = m["pooled"]
        ev_rows.append(f"| {c} | {m['n_region_years']} | {_fmt_ci(p['model_r2'])} | {_fmt_ci(p['model_spearman'])} | "
                       f"{m['within_year']['mean_rho']:.2f} | {_fmt_ci(p['skill_vs_yas1'])} |")
    hash_rows = "\n".join(f"| `{n}` | `{f['sha256']}` |" for n, f in sorted(files.items()))
    last = list(data)[-1]
    text = PROTOCOL_TEMPLATE.format(
        today=date.today().isoformat(), commit=git["commit"], dirty=" (Arbeitsbaum mit uncommitteten Änderungen!)" if git["dirty"] else "",
        seed=cfg["seed"], n_countries=len(set(pd.concat(list(data.values()))["country"])),
        countries=", ".join(sorted(set(pd.concat(list(data.values()))["country"]))),
        years=f"{cy['target_years'][0]}–{cy['target_years'][1]}", lag_fpar=cy["availability_lag_days"]["fpar"],
        lag_ndvi=cy["availability_lag_days"]["ndvi"], lr=lgbc["fixed"]["learning_rate"], subsample=lgbc["fixed"]["subsample"],
        colsample=lgbc["fixed"]["colsample_bytree"], reg_lambda=lgbc["fixed"]["reg_lambda"], g_depth=lgbc["grid"]["max_depth"],
        g_mcs=lgbc["grid"]["min_child_samples"], g_n=lgbc["grid"]["n_estimators"], hp_table="\n".join(hp_rows),
        n_feat_table=", ".join(f"{c}: {len(f)}" for c, f in features.items()), features_last=", ".join(features[last]),
        eval_table="\n".join(ev_rows), result_dir=result_dir, hash_rows=hash_rows, last_cutoff=last,
        r2_last=_fmt_ci(metrics[last]["pooled"]["model_r2"], 3), rho_last=_fmt_ci(metrics[last]["pooled"]["model_spearman"], 2),
        wy_last=_fmt_ci({"value": metrics[last]["within_year"]["mean_rho"], "lo": metrics[last]["within_year"]["lo"],
                         "hi": metrics[last]["within_year"]["hi"]}, 2),
        cutoffs=", ".join(cfg["cutoffs"]["yield_model"]), n_boot=cfg["validation"]["bootstrap_n"])
    path.write_text(text, encoding="utf-8")


def json_safe(obj: Any) -> Any:
    """Convert numpy scalars to Python and NaN/inf to None so that metrics.json is standard JSON."""
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return None if not np.isfinite(obj) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def update_results_md(path: Path, key: str, row: str) -> None:
    """Insert or replace the line of experiment ``key`` in reports/results.md (created if missing)."""
    header = ("# Ergebnisübersicht\n\nEine Zeile je relevantem Lauf (AGENTS.md §6): Datum, Commit, Experiment, Kernmetriken mit 95-%-KI, Kommentar.\n\n"
              "| Datum | Commit | Experiment | Kernmetriken | Kommentar |\n|---|---|---|---|---|\n")
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else header.splitlines()
    lines = [ln for ln in lines if f"<!--{key}-->" not in ln]
    lines.append(row + f" <!--{key}-->")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="CY-Bench EU regional model: LOCO evaluation + EU freeze")
    ap.add_argument("--rebuild", action="store_true", help="ignore the feature cache")
    ap.add_argument("--refreeze", action="store_true", help="overwrite the freeze files and protocol (never after release!)")
    ap.add_argument("--no-freeze", action="store_true", help="skip the freeze step")
    ap.add_argument("--summary-only", action="store_true", help="only write data_structure.json (no models)")
    args = ap.parse_args(argv)
    cfg = load_config()
    cy = cfg["cybench"]
    assert_no_austria(cy["countries"])
    git = git_info()
    today = date.today().isoformat()
    result_dir = f"{today}_cybench_eu"
    out = REPO_ROOT / cfg["paths"]["results"] / result_dir
    out.mkdir(parents=True, exist_ok=True)

    data, report = load_dataset(cfg, rebuild=args.rebuild)
    print({c: len(d) for c, d in data.items()}, flush=True)
    structure = data_structure_summary(data[list(data)[-1]], cfg)
    (out / "data_structure.json").write_text(json.dumps(json_safe(structure), indent=1), encoding="utf-8")
    if args.summary_only:
        print("summary only ->", out / "data_structure.json", flush=True)
        return
    run = run_experiments(cfg, data)
    metrics = run["metrics"]
    last = list(data)[-1]
    d_last = data[last]
    extras = {
        "target_summary": target_summary(d_last, cfg),
        "case_studies": {c: case_studies(run["preds"][c]["main"]) for c in data},
        "adversarial_validation": adversarial_auc(d_last, run["features"][last], cfg, cfg["seed"]),
        "data_report": report,
    }
    plot_earlywarning(metrics, out / "phase5_cybench_earlywarning.png")
    fig_small = REPO_ROOT / cfg["paths"]["figures"] / "phase5_cybench_earlywarning.png"
    fig_small.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out / "phase5_cybench_earlywarning.png", fig_small)
    assert fig_small.stat().st_size <= 150_000, "figure larger than 150 KB"

    freeze_info: dict[str, Any] = {}
    if not args.no_freeze:
        freeze_dir = REPO_ROOT / cy["freeze"]["dir"]
        protocol = REPO_ROOT / cy["freeze"]["protocol"]
        if args.refreeze or not (freeze_dir.exists() and protocol.exists()):
            files = freeze_models(data, cfg, freeze_dir, cfg["seed"], run["features"])
            write_freeze_protocol(protocol, cfg, files, metrics, run["features"], data, result_dir, git, freeze_dir)
            freeze_info = {"status": "frozen now", "files": files}
        else:
            registered = read_registered_hashes(protocol)
            tmp = out / "_freeze_check"
            files = freeze_models(data, cfg, tmp, cfg["seed"], run["features"])
            same = {n: registered.get(n) == f["sha256"] for n, f in files.items()}
            shutil.rmtree(tmp)
            verified = verify_freeze(freeze_dir, protocol)
            freeze_info = {"status": "already frozen; re-training reproduces registered checksums"
                                     if all(same.values()) else "already frozen; RE-TRAINING DIFFERS",
                           "reproduced": same, "verified_files": verified}
    if not args.no_freeze:
        extras["freeze_gain_share_by_variable"] = freeze_importance(
            REPO_ROOT / cy["freeze"]["dir"], list(data), list(cy["static_features"]))
    metrics_json = {"meta": {"date": today, "git": git, "seed": cfg["seed"], "n_features_by_cutoff": {c: len(f) for c, f in run["features"].items()},
                             "versions": {"python": platform.python_version()}, "freeze": freeze_info},
                    "cutoffs": metrics, **extras}
    (out / "metrics.json").write_text(json.dumps(json_safe(metrics_json), indent=1), encoding="utf-8")
    shutil.copyfile(REPO_ROOT / "config.yaml", out / "config.yaml")
    pd.concat([d.assign(cutoff=c) for c, ps in run["preds"].items() for n, d in ps.items() if n == "main"]
              ).to_parquet(out / "predictions_loco.parquet")
    m9 = metrics[last]["pooled"]
    update_results_md(REPO_ROOT / "reports" / "results.md", "phase5-cybench-eu-loco",
                      f"| {today} | `{git['commit'][:7]}` | Phase 5: CY-Bench EU-Mais, LOCO (LightGBM, YAS), Stichtag {last} | "
                      f"n={metrics[last]['n_region_years']} Region-Jahre, {metrics[last]['n_countries']} Länder; R² {_fmt_ci(m9['model_r2'])}; "
                      f"ρ {_fmt_ci(m9['model_spearman'])}; Skill vs. YAS=1 {_fmt_ci(m9['skill_vs_yas1'])} | "
                      f"Ohne Österreich; alle Stichtage in `results/{result_dir}/metrics.json`; EU-Freeze: `reports/freeze_protocol_cybench.md` |")
    print("done ->", out, flush=True)


if __name__ == "__main__":
    main()
