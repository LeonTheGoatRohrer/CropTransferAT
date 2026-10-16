"""One Acre Fund as a TABLE dataset (PLAN Phase 2.4 and Phase 3.4a; DECISIONS 2026-10-15).

No satellite or GEE data, no Austrian data. Results do NOT transfer to Austria: management
columns (fertiliser, seed, density) are not available there; this is an analysis of what
explains differences BETWEEN smallholder fields in sub-Saharan Africa.

A) How much of the between-field variation in RY_nb do reported management, soil, weather
   (CHIRP columns of the table) and reported damages explain?  Flat LightGBM (max_depth 3) and
   Ridge per feature group, outer Leave-One-Country-Out (LOCO) and Leave-One-Year-Out (LOYO),
   hyper-parameters tuned only inside the training part (nested leave-one-unit-out),
   cluster-bootstrap CIs (cluster = country x year), group ablation, SHAP (explanation only),
   label-shuffle control.
B) Phase 3.4a as far as possible: is a reported damage associated with RY_nb < 0.85?
   Country-years where a damage share is exactly 0 are treated as "question not asked" (missing).

Usage:  python -m croptransfer.oaf_analysis [--out DIR] [--n-boot N] [--n-jobs K]
Writes: results/<date>_oaf_tabular/ (metrics.json, config copies, git.txt, tables) and
        reports/figures/phase2_oaf_*.png
"""

from __future__ import annotations

import argparse
import itertools
import json
import shutil
import warnings
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from croptransfer import one_acre_fund as oaf
from croptransfer.config import load_config, repo_path
from croptransfer.evaluate import _boot_clusters, _spearman, r2, rmse, spearman_ci
from croptransfer.targets import ry_nb

SEED = 42

# a feature that is empty in a whole training fold is dropped by the imputer (and in the test part)
warnings.filterwarnings("ignore", message="Skipping features without any observed values")

# --------------------------------------------------------------------------------------------
# Defaults (an optional `oaf_analysis:` section in config.yaml overrides them, shallow merge)
# --------------------------------------------------------------------------------------------
DEFAULTS: dict = {
    "seed": SEED,
    "n_boot": 1000,
    "risk_threshold": 0.85,                      # PLAN 3.6: "gefaehrdet" = RY_nb < 0.85
    "target_group_cols": ["cz", "season", "year"],   # DECISIONS 2026-10-15 (before any analysis)
    "sensitivity_group_cols": ["country", "cz", "season", "year"],
    "shuffle_seeds": [42, 43, 44, 45, 46],
    # Feature groups. "hyb_type" expands to one 0/1 column per category (NaN stays NaN).
    # plant_doy (absolute sowing day-of-year) is left out on purpose: it identifies location and
    # season, the table already has the sowing deviation from the climate-zone average.
    "subgroups": {
        "duenger": ["N_kg_ha", "P_kg_ha", "K_kg_ha", "compost", "comp_kg_ha", "manure",
                    "fert_in_hole", "lime_kg_ha"],
        "saatgut": ["hybrid", "hyb_type", "hyb_mat", "hyb_yor", "hyb_tol_mln", "hyb_tol_msv",
                    "hyb_tol_gls", "hyb_tol_nclb", "hyb_tol_rust", "hyb_tol_ear_rot"],
        "aussaat": ["pl_m2", "row_spacing", "plant_date_dev"],
        "pflege": ["weeding", "pesticide"],
        "boden": list(oaf.SOIL_COLUMNS),
        "wetter": ["season_prec", "season_prec_1", "season_prec_2", "season_prec_3"],
        "schaeden": ["disease", "pest", "striga", "water_excess"],
        "ort": ["lon", "lat", "elev", "twi"],     # location proxy, reference only, not in "alle"
    },
    "management": ["duenger", "saatgut", "aussaat", "pflege"],
    "lgbm": {"learning_rate": 0.05, "num_leaves": 8, "max_depth": 3,
             "n_estimators_grid": [50, 100, 200, 400], "min_child_samples_grid": [20, 100],
             "reg_lambda": 1.0},
    "ridge_alpha_grid": [1.0, 10.0, 100.0, 1000.0, 10000.0],
}

GROUP_LABEL = {"M": "Bewirtschaftung", "B": "Boden", "W": "Wetter (Tabelle)", "S": "Schäden", "ORT": "Ort/Gelände"}
SET_ORDER = ["M_duenger", "M_saatgut", "M_aussaat", "M_pflege", "M", "B", "W", "S", "ORT",
             "alle", "ohne_M", "ohne_B", "ohne_W", "ohne_S"]


def oaf_config(cfg: dict | None = None) -> dict:
    cfg = cfg or load_config()
    out = json.loads(json.dumps(DEFAULTS))
    out.update(cfg.get("oaf_analysis", {}))
    out["min_other"] = cfg["one_acre_fund"]["ry_nb_min_other_fields"]
    out["damage_columns"] = list(cfg["one_acre_fund"]["damage_columns"])
    return out


# --------------------------------------------------------------------------------------------
# Data preparation
# --------------------------------------------------------------------------------------------
def as_float(s: pd.Series) -> pd.Series:
    """Booleans / 'True' / 'False' / NaN -> 1.0 / 0.0 / NaN; numeric stays numeric."""
    if s.dtype == bool:
        return s.astype(float)
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    return pd.to_numeric(s.map({True: 1.0, False: 0.0, "True": 1.0, "False": 0.0}), errors="coerce")


def not_asked_table(df_all: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Boolean table (country, year) x damage column: True where the question was probably not asked.

    "Not asked" = share of reports exactly 0 in the whole country-year (all fields, DATA_SOURCES §9)
    or no answer at all (NaN share). Computed from all fields, not only the exact-position ones.
    """
    rates = oaf.damage_rates(df_all, columns)
    return rates.eq(0.0) | rates.isna()


def damage_matrix(df: pd.DataFrame, not_asked: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Reported damages as 0/1 floats; NaN for missing answers AND for country-years not asked."""
    out = pd.DataFrame({c: as_float(df[c]) for c in columns}, index=df.index)
    key = pd.MultiIndex.from_arrays([df["country"], df["year"]])
    for c in columns:
        flag = not_asked[c].reindex(key).to_numpy()
        out.loc[np.asarray(flag, dtype=bool), c] = np.nan
    return out


def analysis_frame(df_all: pd.DataFrame, oc: dict, group_cols: list[str] | None = None
                   ) -> tuple[pd.DataFrame, dict]:
    """Exact-position fields with a defined RY_nb (group = cz x season x year, >= min_other others).

    Returns the analysis table (RY_nb, damage columns with 'not asked' = NaN) and counts.
    """
    group_cols = group_cols or oc["target_group_cols"]
    exact = df_all[oaf.exact_location(df_all)].copy()
    exact["RY_nb"] = ry_nb(exact, group_cols, "yield_kg_ha", oc["min_other"])
    keep = exact[exact["RY_nb"].notna()].copy()
    na = not_asked_table(df_all, oc["damage_columns"])
    keep[oc["damage_columns"]] = damage_matrix(keep, na, oc["damage_columns"])
    keep = keep.reset_index(drop=True)
    keep["cluster"] = keep["country"].astype(str) + "_" + keep["year"].astype(str)
    info = {
        "n_all": len(df_all), "n_exact": len(exact), "n_ry_nb": len(keep),
        "n_exact_without_group": int(len(exact) - len(keep)),
        "group_cols": group_cols,
        "n_groups": int(keep.groupby(group_cols).ngroups),
        "n_groups_straddling_countries": groups_straddling(keep, group_cols, "country"),
        "n_clusters": int(keep["cluster"].nunique()),
    }
    return keep, info


def groups_straddling(df: pd.DataFrame, group_cols: list[str], unit: str) -> int:
    """Number of RY_nb groups that contain more than one value of `unit` (e.g. country)."""
    return int((df.groupby(group_cols)[unit].nunique() > 1).sum())


def design_matrix(df: pd.DataFrame, subgroups: dict[str, list[str]]) -> tuple[pd.DataFrame, dict[str, str]]:
    """Numeric feature table and feature -> subgroup map. Missing values stay NaN."""
    cols: dict[str, pd.Series] = {}
    owner: dict[str, str] = {}
    for sub, names in subgroups.items():
        for name in names:
            if name == "hyb_type":
                for cat in sorted(df[name].dropna().unique()):
                    cols[f"hyb_type_{cat}"] = (df[name] == cat).astype(float).where(df[name].notna())
                    owner[f"hyb_type_{cat}"] = sub
            else:
                cols[name] = as_float(df[name])
                owner[name] = sub
    return pd.DataFrame(cols, index=df.index), owner


def feature_sets(owner: dict[str, str], oc: dict) -> dict[str, list[str]]:
    """Named feature sets: single sub-groups, groups M/B/W/S/ORT, 'alle' = M+B+W+S and ablations."""
    by_sub: dict[str, list[str]] = {}
    for col, sub in owner.items():
        by_sub.setdefault(sub, []).append(col)
    group = {
        "M": [c for s in oc["management"] for c in by_sub[s]],
        "B": by_sub["boden"], "W": by_sub["wetter"], "S": by_sub["schaeden"], "ORT": by_sub["ort"],
    }
    sets = {f"M_{s}": by_sub[s] for s in oc["management"]}
    sets.update(group)
    allcols = group["M"] + group["B"] + group["W"] + group["S"]
    sets["alle"] = allcols
    for g in ("M", "B", "W", "S"):
        sets[f"ohne_{g}"] = [c for c in allcols if c not in group[g]]
    return {k: sets[k] for k in SET_ORDER}


# --------------------------------------------------------------------------------------------
# Splits
# --------------------------------------------------------------------------------------------
def leave_one_group_out(groups) -> list[tuple[np.ndarray, np.ndarray, str]]:
    """Folds (train_idx, test_idx, label): every distinct group is the test set once."""
    g = np.asarray(groups)
    return [(np.flatnonzero(g != u), np.flatnonzero(g == u), str(u)) for u in pd.unique(g)]


# --------------------------------------------------------------------------------------------
# Models and nested CV
# --------------------------------------------------------------------------------------------
def _lgbm(oc: dict, n_estimators: int, min_child: int, seed: int):
    from lightgbm import LGBMRegressor
    p = oc["lgbm"]
    return LGBMRegressor(
        max_depth=p["max_depth"], num_leaves=p["num_leaves"], learning_rate=p["learning_rate"],
        n_estimators=n_estimators, min_child_samples=min_child, reg_lambda=p["reg_lambda"],
        random_state=seed, n_jobs=1, verbose=-1, deterministic=True, force_col_wise=True)


CLIP_SD = 5.0


def _clip_sd(a):
    """Limit standardised features to +-CLIP_SD (rare categories would otherwise extrapolate wildly
    in a held-out country; seen in a development run: Ridge predicted RY_nb up to 9 for Rwanda)."""
    return np.clip(a, -CLIP_SD, CLIP_SD)


def _ridge(alpha: float):
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import FunctionTransformer, StandardScaler
    # imputer and scaler are fitted on the training part only (inside the pipeline)
    return make_pipeline(SimpleImputer(strategy="mean"), StandardScaler(), FunctionTransformer(_clip_sd),
                         Ridge(alpha=alpha))


def _grid(kind: str, oc: dict) -> list[dict]:
    if kind == "lgbm":
        return [{"n_estimators": n, "min_child_samples": m}
                for m, n in itertools.product(oc["lgbm"]["min_child_samples_grid"], oc["lgbm"]["n_estimators_grid"])]
    return [{"alpha": a} for a in oc["ridge_alpha_grid"]]


def _inner_scores(kind, X, y, groups, oc, seed) -> dict[tuple, float]:
    """Pooled squared error of each grid point over inner leave-one-group-out folds."""
    sse = {tuple(p.items()): 0.0 for p in _grid(kind, oc)}
    for tr, va, _ in leave_one_group_out(groups):
        if kind == "lgbm":
            for m in oc["lgbm"]["min_child_samples_grid"]:
                big = max(oc["lgbm"]["n_estimators_grid"])
                mod = _lgbm(oc, big, m, seed).fit(X[tr], y[tr])
                for n in oc["lgbm"]["n_estimators_grid"]:
                    pr = mod.predict(X[va], num_iteration=n)
                    sse[(("n_estimators", n), ("min_child_samples", m))] += float(np.sum((y[va] - pr) ** 2))
        else:
            for a in oc["ridge_alpha_grid"]:
                pr = _ridge(a).fit(X[tr], y[tr]).predict(X[va])
                sse[(("alpha", a),)] += float(np.sum((y[va] - pr) ** 2))
    return sse


def _fit(kind, params, X, y, oc, seed):
    if kind == "lgbm":
        return _lgbm(oc, params["n_estimators"], params["min_child_samples"], seed).fit(X, y)
    return _ridge(params["alpha"]).fit(X, y)


def nested_oof(X: np.ndarray, y: np.ndarray, groups, kind: str, oc: dict, seed: int = SEED,
               want_shap: bool = False) -> dict:
    """Outer leave-one-group-out; hyper-parameters chosen by an inner leave-one-group-out on the
    outer training part only. Returns out-of-fold predictions, the B0 baseline (training mean),
    the chosen parameters per fold and optionally SHAP values of the held-out rows."""
    g = np.asarray(groups)
    pred = np.full(len(y), np.nan)
    base = np.full(len(y), np.nan)
    shap_vals = np.full(X.shape, np.nan) if want_shap else None
    chosen = []
    for tr, te, label in leave_one_group_out(g):
        scores = _inner_scores(kind, X[tr], y[tr], g[tr], oc, seed) if len(np.unique(g[tr])) > 1 else {
            tuple(_grid(kind, oc)[0].items()): 0.0}
        best = dict(min(scores, key=scores.get))
        model = _fit(kind, best, X[tr], y[tr], oc, seed)
        pred[te] = model.predict(X[te])
        base[te] = y[tr].mean()
        chosen.append({"fold": label, **best})
        if want_shap and kind == "lgbm":
            import shap
            shap_vals[te] = shap.TreeExplainer(model).shap_values(X[te])
    return {"pred": pred, "base": base, "chosen": chosen, "shap": shap_vals}


# --------------------------------------------------------------------------------------------
# Metrics with cluster bootstrap
# --------------------------------------------------------------------------------------------
METRICS = ("rho", "r2", "rmse")


def _metrics(y, p) -> dict[str, float]:
    return {"rho": _spearman(p, y), "r2": r2(y, p), "rmse": rmse(y, p)}


def bootstrap_summary(y, preds: dict[str, np.ndarray], clusters, base: np.ndarray | None = None,
                      pairs: list[tuple[str, str]] | None = None, n_boot: int = 1000,
                      seed: int = SEED, level: float = 0.95) -> dict:
    """Point estimates and percentile CIs (cluster bootstrap, same resamples for all models).

    For each prediction vector: rho, R2, RMSE; if `base` is given also RMSE(model) - RMSE(B0).
    `pairs` (a, b): paired difference metric(a) - metric(b) for rho, R2, RMSE.
    """
    y = np.asarray(y, float)
    clusters = pd.Series(np.asarray(clusters))
    pairs = pairs or []

    def point(idx):
        out = {k: _metrics(y[idx], p[idx]) for k, p in preds.items()}
        if base is not None:
            b = rmse(y[idx], base[idx])
            for k, p in preds.items():
                out[k]["d_rmse_b0"] = out[k]["rmse"] - b
                out[k]["rmse_b0"] = b
        return out

    full = np.arange(len(y))
    est = point(full)
    boots = [point(i) for i in _boot_clusters(clusters, n_boot, seed)]
    lo_q, hi_q = (1 - level) / 2 * 100, (1 + level) / 2 * 100

    def ci(vals):
        v = np.asarray(vals, float)
        return [float(x) for x in np.nanpercentile(v, [lo_q, hi_q])] if np.isfinite(v).any() else [np.nan, np.nan]

    res = {}
    for k in preds:
        res[k] = {"n": int(len(y)), "n_clusters": int(clusters.nunique())}
        for m in list(METRICS) + (["d_rmse_b0"] if base is not None else []):
            res[k][m] = [float(est[k][m])] + ci([b[k][m] for b in boots])
        if base is not None:
            res[k]["rmse_b0"] = float(est[k]["rmse_b0"])
    diffs = {}
    for a, b in pairs:
        diffs[f"{a} - {b}"] = {m: [float(est[a][m] - est[b][m])] + ci([bb[a][m] - bb[b][m] for bb in boots])
                               for m in METRICS}
    return {"models": res, "diffs": diffs}


# --------------------------------------------------------------------------------------------
# Part A: run the model grid
# --------------------------------------------------------------------------------------------
def _run_config(spec: dict, X_all: np.ndarray, cols: list[str], names_all: list[str], y: np.ndarray,
                groups: np.ndarray, oc: dict) -> dict:
    idx = [names_all.index(c) for c in cols]
    out = nested_oof(X_all[:, idx], y, groups, spec["kind"], oc, spec["seed"], spec.get("shap", False))
    out["spec"] = spec
    out["cols"] = cols
    return out


def run_grid(df: pd.DataFrame, X: pd.DataFrame, sets: dict[str, list[str]], oc: dict, n_jobs: int,
             sets_to_run: list[str] | None = None) -> dict[str, dict]:
    """All feature sets x {lgbm, ridge} x {LOCO, LOYO} + label-shuffle controls on 'alle'."""
    from joblib import Parallel, delayed
    y = df["RY_nb"].to_numpy(float)
    units = {"LOCO": df["country"].to_numpy(), "LOYO": df["year"].to_numpy()}
    names, Xa = list(X.columns), X.to_numpy(float)
    specs = []
    for split in units:
        for kind in ("lgbm", "ridge"):
            for s in (sets_to_run or list(sets)):
                specs.append({"split": split, "kind": kind, "set": s, "seed": oc["seed"],
                              "shap": split == "LOCO" and kind == "lgbm" and s == "alle", "shuffle": None})
    for sd in oc["shuffle_seeds"]:
        for split in units:
            for kind in ("lgbm", "ridge"):
                specs.append({"split": split, "kind": kind, "set": "alle", "seed": oc["seed"],
                              "shap": False, "shuffle": sd})

    def y_for(spec):
        if spec["shuffle"] is None:
            return y
        return np.random.default_rng(spec["shuffle"]).permutation(y)

    jobs = [delayed(_run_config)(sp, Xa, sets[sp["set"]], names, y_for(sp), units[sp["split"]], oc) for sp in specs]
    results = Parallel(n_jobs=n_jobs)(jobs)
    return {_key(r["spec"]): r for r in results}


def _key(spec: dict) -> str:
    base = f"{spec['split']}/{spec['kind']}/{spec['set']}"
    return base if spec["shuffle"] is None else f"{base}/shuffle{spec['shuffle']}"


def evaluate_grid(df: pd.DataFrame, runs: dict[str, dict], oc: dict) -> dict:
    """Metrics (with CI) for every run, ablation differences, per-fold table and shuffle control."""
    y = df["RY_nb"].to_numpy(float)
    clusters = df["cluster"].to_numpy()
    real = {k: r for k, r in runs.items() if r["spec"]["shuffle"] is None}
    out = {"models": {}, "ablation": {}, "single_vs_alle": {}, "per_fold": {}, "shuffle": {}, "within_cluster": {}}
    for split in ("LOCO", "LOYO"):
        for kind in ("lgbm", "ridge"):
            keys = {s: f"{split}/{kind}/{s}" for s in SET_ORDER if f"{split}/{kind}/{s}" in real}
            preds = {s: real[k]["pred"] for s, k in keys.items()}
            base = real[next(iter(keys.values()))]["base"]
            pairs = [("alle", f"ohne_{g}") for g in "MBWS" if f"ohne_{g}" in keys] + \
                    [("alle", s) for s in ("M", "B", "W", "S", "ORT") if s in keys]
            summ = bootstrap_summary(y, preds, clusters, base, pairs, oc["n_boot"], oc["seed"])
            out["models"][f"{split}/{kind}"] = summ["models"]
            out["ablation"][f"{split}/{kind}"] = {k: v for k, v in summ["diffs"].items() if "ohne_" in k}
            out["single_vs_alle"][f"{split}/{kind}"] = {k: v for k, v in summ["diffs"].items() if "ohne_" not in k}
            out["within_cluster"][f"{split}/{kind}"] = {s: within_cluster_rho(y, p, clusters) for s, p in preds.items()}
        # per held-out unit, full model
        unit = df["country"] if split == "LOCO" else df["year"]
        for kind in ("lgbm", "ridge"):
            r = real.get(f"{split}/{kind}/alle")
            if r is None:
                continue
            rows = {}
            for u in pd.unique(unit):
                m = (unit == u).to_numpy()
                rows[str(u)] = {"n": int(m.sum()), **_metrics(y[m], r["pred"][m])}
            out["per_fold"][f"{split}/{kind}"] = rows
    # label shuffle: same pipeline on a permuted target, judged against the permuted target
    for split in ("LOCO", "LOYO"):
        for kind in ("lgbm", "ridge"):
            for sd in oc["shuffle_seeds"]:
                r = runs.get(f"{split}/{kind}/alle/shuffle{sd}")
                if r is None:
                    continue
                yp = np.random.default_rng(sd).permutation(y)
                s = bootstrap_summary(yp, {"alle": r["pred"]}, clusters, r["base"], None, oc["n_boot"], oc["seed"])
                out["shuffle"][f"{split}/{kind}/seed{sd}"] = s["models"]["alle"]
    out["chosen_params"] = {k: r["chosen"] for k, r in real.items() if k.endswith("/alle")}
    return out


def within_cluster_rho(y, p, clusters, min_n: int = 30) -> dict:
    """Median Spearman rho inside each country-year with >= min_n fields (removes between-cluster
    level differences, AGENTS 3.3 'year proxy' check)."""
    d = pd.DataFrame({"y": y, "p": p, "c": clusters})
    rhos = [_spearman(g["p"].to_numpy(), g["y"].to_numpy()) for _, g in d.groupby("c") if len(g) >= min_n]
    rhos = [r for r in rhos if np.isfinite(r)]
    return {"median": float(np.median(rhos)), "min": float(np.min(rhos)), "max": float(np.max(rhos)),
            "n_clusters": len(rhos)}


def shap_summary(runs: dict[str, dict], owner: dict[str, str], oc: dict, df: pd.DataFrame) -> dict:
    """Mean |SHAP| of out-of-fold predictions (LOCO, LightGBM, 'alle'); explanation only."""
    r = runs["LOCO/lgbm/alle"]
    vals, cols = r["shap"], r["cols"]
    mean_abs = pd.Series(np.nanmean(np.abs(vals), axis=0), index=cols).sort_values(ascending=False)
    mgmt = set(oc["management"])
    grp = lambda c: "M" if owner[c] in mgmt else {"boden": "B", "wetter": "W", "schaeden": "S"}[owner[c]]
    by_group = mean_abs.groupby([grp(c) for c in mean_abs.index]).sum().sort_values(ascending=False)
    by_sub = mean_abs.groupby([owner[c] for c in mean_abs.index]).sum().sort_values(ascending=False)
    by_country = pd.DataFrame(np.abs(vals), columns=cols).groupby(df["country"].to_numpy()).mean() \
        .T.groupby([grp(c) for c in cols]).sum()
    return {"features": mean_abs.round(5).to_dict(), "by_group": by_group.round(5).to_dict(),
            "by_subgroup": by_sub.round(5).to_dict(), "by_country_group": by_country.round(5).to_dict(),
            "feature_group": {c: grp(c) for c in cols}}


# --------------------------------------------------------------------------------------------
# Part B: reported damages vs RY_nb < 0.85
# --------------------------------------------------------------------------------------------
def odds_ratio(a: float, b: float, c: float, d: float) -> float:
    """OR = a*d/(b*c) for the 2x2 table (a: reported & at risk, b: not reported & at risk,
    c: reported & fine, d: not reported & fine); 0.5 added to all cells if any cell is 0."""
    if min(a, b, c, d) == 0:
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    return (a * d) / (b * c)


def mantel_haenszel_or(strata: np.ndarray, risk: np.ndarray, rep: np.ndarray) -> float:
    """Mantel-Haenszel OR over strata (integer codes); strata without both outcomes drop out."""
    n = np.bincount(strata).astype(float)
    a = np.bincount(strata, weights=rep * risk, minlength=len(n))
    b = np.bincount(strata, weights=(1 - rep) * risk, minlength=len(n))
    c = np.bincount(strata, weights=rep * (1 - risk), minlength=len(n))
    d = np.bincount(strata, weights=(1 - rep) * (1 - risk), minlength=len(n))
    ok = n > 0
    num, den = np.sum(a[ok] * d[ok] / n[ok]), np.sum(b[ok] * c[ok] / n[ok])
    return float(num / den) if den > 0 else np.nan


def _assoc_stats(risk, rep, strata) -> dict[str, float]:
    a, b = np.sum(rep * risk), np.sum((1 - rep) * risk)
    c, d = np.sum(rep * (1 - risk)), np.sum((1 - rep) * (1 - risk))
    share_w = a / (a + c) if a + c > 0 else np.nan
    share_wo = b / (b + d) if b + d > 0 else np.nan
    return {"share_with": share_w, "share_without": share_wo, "risk_diff": share_w - share_wo,
            "or_crude": odds_ratio(a, b, c, d), "or_mh": mantel_haenszel_or(strata, risk, rep)}


def damage_association(df: pd.DataFrame, oc: dict, group_cols: list[str] | None = None) -> dict:
    """Share of RY_nb < 0.85 with / without a reported damage, OR crude and Mantel-Haenszel
    (strata = RY_nb group), 95 % cluster-bootstrap CI (cluster = country x year).
    Fields from country-years with NaN (not asked / no answer) are excluded per damage."""
    group_cols = group_cols or oc["target_group_cols"]
    risk_all = (df["RY_nb"] < oc["risk_threshold"]).to_numpy(float)
    strata_all = pd.factorize(df[group_cols].astype(str).agg("|".join, axis=1))[0]
    out = {}
    for col in oc["damage_columns"]:
        m = df[col].notna().to_numpy()
        if m.sum() == 0 or df.loc[m, col].nunique() < 2:
            out[col] = {"n": int(m.sum()), "note": "no variation / not asked everywhere"}
            continue
        rep = df.loc[m, col].to_numpy(float)
        risk = risk_all[m]
        strata = pd.factorize(strata_all[m])[0]
        clusters = pd.Series(df.loc[m, "cluster"].to_numpy())
        est = _assoc_stats(risk, rep, strata)
        boots = [_assoc_stats(risk[i], rep[i], pd.factorize(strata[i])[0])
                 for i in _boot_clusters(clusters, oc["n_boot"], oc["seed"])]
        res = {"n": int(m.sum()), "n_reported": int(rep.sum()), "prevalence_reported": float(rep.mean()),
               "n_country_years": int(clusters.nunique()),
               "countries": sorted(df.loc[m, "country"].astype(str).unique())}
        for k, v in est.items():
            vals = np.array([b[k] for b in boots], float)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)      # all-NaN bootstrap draws (empty cell)
                lo, hi = np.nanpercentile(vals, [2.5, 97.5])
            res[k] = [float(v), float(lo), float(hi)]
        # per country-year table (no CI, Haldane-corrected OR) to show heterogeneity
        per = []
        for cl, g in df.loc[m].groupby("cluster"):
            r, p = g[col].to_numpy(float), (g["RY_nb"] < oc["risk_threshold"]).to_numpy(float)
            a, b = np.sum(r * p), np.sum((1 - r) * p)
            c, d = np.sum(r * (1 - p)), np.sum((1 - r) * (1 - p))
            per.append({"cluster": cl, "n": len(g), "n_reported": int(r.sum()),
                        "share_with": float(a / (a + c)) if a + c else None,
                        "share_without": float(b / (b + d)) if b + d else None,
                        "or_haldane": float(odds_ratio(a, b, c, d)) if r.sum() and (1 - r).sum() else None})
        res["per_country_year"] = per
        out[col] = res
    return out


def weather_link(df: pd.DataFrame, min_group: int = 20, n_boot: int = 1000, seed: int = SEED) -> dict:
    """EXPLORATORY: reported damage vs CHIRP precipitation anomaly (z within climate zone x season).
    Not the pre-registered ERA5 cause rules (those need daily weather, not available without GEE)."""
    pairs = [("water_excess", "season_prec"), ("water_excess", "season_prec_1"),
             ("pest", "season_prec_2"), ("disease", "season_prec_2"),
             ("pest", "season_prec_3"), ("disease", "season_prec_3")]
    out = {}
    for dmg, prec in pairs:
        z = df.groupby(["cz", "season"])[prec].transform(
            lambda s: (s - s.mean()) / s.std(ddof=0) if len(s) >= min_group and s.std(ddof=0) > 0 else np.nan)
        m = (df[dmg].notna() & z.notna()).to_numpy()
        if m.sum() < 30 or df.loc[m, dmg].nunique() < 2:
            continue
        rho, lo, hi = spearman_ci(z[m], df.loc[m, dmg], df.loc[m, "cluster"], n_boot, seed)
        out[f"{dmg}~z({prec})"] = {"n": int(m.sum()), "rho": [rho, lo, hi]}
    return out


# --------------------------------------------------------------------------------------------
# Data critique numbers
# --------------------------------------------------------------------------------------------
def data_facts(df_all: pd.DataFrame, df: pd.DataFrame, X: pd.DataFrame, owner: dict, oc: dict,
               info: dict) -> dict:
    exact = df_all[oaf.exact_location(df_all)]
    n_cy = df.groupby(["country", "year"]).size()
    cov = X.notna().groupby(df["country"].to_numpy()).mean().T
    sub_cov = cov.groupby([owner[c] for c in cov.index]).mean()
    na = not_asked_table(df_all, oc["damage_columns"])
    return {
        **info,
        "n_by_country_year": {f"{c}_{y}": int(v) for (c, y), v in n_cy.items()},
        "n_by_country": df.groupby("country").size().to_dict(),
        "ry_nb": {"mean": float(df.RY_nb.mean()), "median": float(df.RY_nb.median()),
                  "q01": float(df.RY_nb.quantile(.01)), "q99": float(df.RY_nb.quantile(.99)),
                  "max": float(df.RY_nb.max()), "n_zero": int((df.RY_nb == 0).sum()),
                  "share_below_threshold": float((df.RY_nb < oc["risk_threshold"]).mean())},
        "feature_coverage_by_subgroup_country": sub_cov.round(3).to_dict(),
        "feature_missing_share": X.isna().mean().round(3).to_dict(),
        "damage_not_asked_country_years": {c: sorted(f"{k[0]}_{k[1]}" for k, v in na[c].items() if v)
                                           for c in oc["damage_columns"]},
        "point_duplicates_exact": int((exact.groupby(["lon", "lat", "year", "season"])["year"].transform("size") > 1).sum()),
    }


# --------------------------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------------------------
GROUP_COLOR = {"M": "#E69F00", "B": "#56B4E9", "W": "#009E73", "S": "#D55E00", "ORT": "#7f7f7f"}
SET_COLOR = {s: GROUP_COLOR[s.split("_")[0] if s.startswith("M_") else s] for s in
             ["M_duenger", "M_saatgut", "M_aussaat", "M_pflege", "M", "B", "W", "S", "ORT"]}
SET_LABEL = {"M_duenger": "Dünger", "M_saatgut": "Saatgut/Sorte", "M_aussaat": "Saatdichte/-termin",
             "M_pflege": "Unkraut/Pflanzenschutz", "M": "Bewirtschaftung (alle)", "B": "Boden",
             "W": "Wetter (CHIRP)", "S": "Schäden", "ORT": "Ort/Gelände (Kontrolle)", "alle": "alle (M+B+W+S)",
             "ohne_M": "alle ohne Bewirtschaftung", "ohne_B": "alle ohne Boden",
             "ohne_W": "alle ohne Wetter", "ohne_S": "alle ohne Schäden"}


def plot_groups(metrics: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2), sharey=True)
    for col, split in enumerate(("LOCO", "LOYO")):
        for row, (m, lab) in enumerate((("r2", "R² (außerhalb des Trainings)"), ("rho", "Spearman ρ"))):
            ax = axes[row, col]
            for off, kind, mk in ((-0.16, "lgbm", "o"), (0.16, "ridge", "s")):
                res = metrics["models"].get(f"{split}/{kind}", {})
                for i, s in enumerate(SET_ORDER):
                    if s not in res:
                        continue
                    v, lo, hi = res[s][m]
                    c = SET_COLOR.get(s, "black")
                    ax.errorbar(v, i + off, xerr=[[v - lo], [hi - v]], fmt=mk, color=c, ms=4.5, lw=1.1,
                                mfc=c if kind == "lgbm" else "white")
            ax.axvline(0, color="k", lw=0.6)
            ax.set_yticks(range(len(SET_ORDER)))
            ax.set_yticklabels([SET_LABEL[s] for s in SET_ORDER], fontsize=8)
            ax.invert_yaxis()
            ax.set_xlabel(lab, fontsize=9)
            ax.set_title(f"{split}" + (" (Land ausgelassen)" if split == "LOCO" else " (Jahr ausgelassen)"), fontsize=10)
            ax.grid(axis="x", alpha=.25)
    for ax in axes.ravel():
        ax.xaxis.set_major_locator(MaxNLocator(5))
    fig.legend(handles=[Line2D([], [], color="k", marker="o", ls="", label="LightGBM (Tiefe 3)"),
                        Line2D([], [], color="k", marker="s", mfc="white", ls="", label="Ridge")],
               loc="upper right", fontsize=8, ncol=2, frameon=False)
    fig.suptitle("One Acre Fund: Was erklärt RY_nb zwischen Feldern?  (95-%-Cluster-Bootstrap, Cluster = Land×Jahr)",
                 fontsize=10, x=0.4)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_shap(shap: dict, path: Path, top: int = 16) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    feats = pd.Series(shap["features"]).head(top)[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), gridspec_kw={"width_ratios": [2.2, 1]})
    axes[0].barh(feats.index, feats.values, color=[GROUP_COLOR[shap["feature_group"][c]] for c in feats.index])
    axes[0].set_xlabel("mittleres |SHAP| (Einheit: RY_nb)", fontsize=9)
    axes[0].set_title("Merkmale (LOCO, nur außerhalb des Trainings erklärt)", fontsize=10)
    grp = pd.Series(shap["by_group"])
    axes[1].bar([GROUP_LABEL[g] for g in grp.index], grp.values, color=[GROUP_COLOR[g] for g in grp.index])
    axes[1].set_title("Summe je Gruppe", fontsize=10)
    axes[1].tick_params(axis="x", rotation=35, labelsize=8)
    for lab in axes[1].get_xticklabels():
        lab.set_ha("right")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def plot_damage(dmg: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = [c for c, v in dmg.items() if "or_crude" in v]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
    x = np.arange(len(cols))
    for k, (key, lab, col) in enumerate((("share_with", "Schaden gemeldet", "#D55E00"),
                                         ("share_without", "nicht gemeldet", "#56B4E9"))):
        v = np.array([dmg[c][key][0] for c in cols])
        err = np.array([[dmg[c][key][0] - dmg[c][key][1] for c in cols], [dmg[c][key][2] - dmg[c][key][0] for c in cols]])
        axes[0].bar(x + (k - .5) * .38, v, .38, yerr=err, color=col, label=lab, capsize=3, ecolor="k")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"{c}\n(n={dmg[c]['n']})" for c in cols], fontsize=8)
    axes[0].set_ylabel("Anteil RY_nb < 0,85", fontsize=9)
    axes[0].legend(fontsize=8)
    axes[0].set_title("Niedriger Ertrag mit / ohne gemeldeten Schaden", fontsize=10)
    for k, (key, lab, mk) in enumerate((("or_crude", "roh", "o"), ("or_mh", "Mantel-Haenszel", "s"))):
        for i, c in enumerate(cols):
            v, lo, hi = dmg[c][key]
            axes[1].errorbar(v, i + (k - .5) * .25, xerr=[[v - lo], [hi - v]], fmt=mk, color="#D55E00" if k == 0 else "#333",
                             mfc="#D55E00" if k == 0 else "white", ms=5, capsize=3, label=lab if i == 0 else None)
    axes[1].axvline(1, color="k", lw=.6)
    axes[1].set_xscale("log")
    axes[1].set_xticks([0.5, 1, 2, 4])
    axes[1].set_xticklabels(["0,5", "1", "2", "4"])
    axes[1].set_yticks(range(len(cols)))
    axes[1].set_yticklabels(cols, fontsize=9)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Odds Ratio (log), 95-%-KI", fontsize=9)
    axes[1].legend(fontsize=8)
    axes[1].set_title("Zusammenhang, kein Beleg für Ursache", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# --------------------------------------------------------------------------------------------
# Markdown tables (pasted into the data-review report)
# --------------------------------------------------------------------------------------------
def _f(v, d=2) -> str:
    return f"{v:.{d}f}".replace(".", ",")


def _ci(t, d=2) -> str:
    return f"{_f(t[0], d)} [{_f(t[1], d)}; {_f(t[2], d)}]"


def markdown_tables(res: dict, dmg: dict, shap: dict, weather: dict, sens: dict | None) -> str:
    lines = []
    for split in ("LOCO", "LOYO"):
        lines += [f"\n#### {split}: Merkmalsgruppen (n = {res['models'][f'{split}/lgbm']['alle']['n']}, "
                  f"Cluster = {res['models'][f'{split}/lgbm']['alle']['n_clusters']})\n",
                  "| Merkmalssatz | LightGBM ρ | LightGBM R² | LightGBM RMSE−B0 | Ridge ρ | Ridge R² | Ridge RMSE−B0 |",
                  "|---|---|---|---|---|---|---|"]
        for s in SET_ORDER:
            row = [SET_LABEL[s]]
            for kind in ("lgbm", "ridge"):
                m = res["models"][f"{split}/{kind}"][s]
                row += [_ci(m["rho"]), _ci(m["r2"]), _ci(m["d_rmse_b0"], 3)]
            lines.append("| " + " | ".join(row) + " |")
    for key, title in (("ablation", "Ablation: alle − (alle ohne X) = Beitrag von X"),
                       ("single_vs_alle", "alle − Einzelgruppe = was die Gruppe allein nicht erreicht")):
        lines += [f"\n#### {title} (Differenz von R², 95-%-KI)\n", "| Split/Modell | " +
                  " | ".join(next(iter(res[key].values())).keys()) + " |", "|---|" + "---|" * len(next(iter(res[key].values())))]
        for k, v in res[key].items():
            lines.append(f"| {k} | " + " | ".join(_ci(d["r2"]) for d in v.values()) + " |")
    lines += ["\n#### Median-ρ innerhalb Land-Jahr (≥ 30 Felder; [min; max] über Land-Jahre)\n",
              "| Merkmalssatz | LOCO LightGBM | LOCO Ridge | LOYO LightGBM | LOYO Ridge |", "|---|---|---|---|---|"]
    for s in SET_ORDER:
        cells = []
        for key in ("LOCO/lgbm", "LOCO/ridge", "LOYO/lgbm", "LOYO/ridge"):
            w = res["within_cluster"][key][s]
            cells.append(f"{_f(w['median'])} [{_f(w['min'])}; {_f(w['max'])}], k={w['n_clusters']}")
        lines.append(f"| {SET_LABEL[s]} | " + " | ".join(cells) + " |")
    lines += ["\n#### Label-Shuffle (alle, permutiertes Ziel)\n", "| Lauf | ρ | R² | RMSE−B0 |", "|---|---|---|---|"]
    for k, m in res["shuffle"].items():
        lines.append(f"| {k} | {_ci(m['rho'])} | {_ci(m['r2'])} | {_ci(m['d_rmse_b0'], 3)} |")
    lines += ["\n#### SHAP (LOCO, LightGBM, alle): mittleres |SHAP| je Gruppe / Top-10-Merkmale\n",
              "| " + " | ".join(f"{GROUP_LABEL[g]}" for g in shap["by_group"]) + " |",
              "|" + "---|" * len(shap["by_group"]),
              "| " + " | ".join(_f(v, 3) for v in shap["by_group"].values()) + " |", "",
              ", ".join(f"{c} ({_f(v, 3)})" for c, v in list(shap["features"].items())[:10])]
    lines += ["\n#### Schäden vs. RY_nb < 0,85\n",
              "| Schaden | n (Länder-Jahre) | gemeldet | Anteil <0,85 mit | ohne | OR roh | OR Mantel-Haenszel |",
              "|---|---|---|---|---|---|---|"]
    for c, v in dmg.items():
        if "or_crude" not in v:
            lines.append(f"| {c} | – | – | – | – | – | – ({v.get('note', '')}) |")
            continue
        lines.append(f"| {c} | {v['n']} ({v['n_country_years']}) | {v['n_reported']} ({_f(100 * v['prevalence_reported'], 1)} %) | "
                     f"{_ci(v['share_with'])} | {_ci(v['share_without'])} | {_ci(v['or_crude'])} | {_ci(v['or_mh'])} |")
    lines += ["\n#### Explorativ: Schaden vs. CHIRP-Niederschlagsanomalie (Spearman ρ)\n", "| Paar | n | ρ |", "|---|---|---|"]
    for k, v in weather.items():
        lines.append(f"| {k} | {v['n']} | {_ci(v['rho'])} |")
    if sens:
        lines += ["\n#### Sensitivität: RY_nb-Gruppe mit Land (country × cz × season × year), LOCO\n",
                  f"n = {sens['n']}\n", "| Merkmalssatz | LightGBM ρ | LightGBM R² | Ridge ρ | Ridge R² |", "|---|---|---|---|---|"]
        for s in ("M", "B", "W", "S", "ORT", "alle"):
            lines.append(f"| {SET_LABEL[s]} | " + " | ".join(
                _ci(sens["models"][f"LOCO/{k}"][s][m]) for k in ("lgbm", "ridge") for m in ("rho", "r2")) + " |")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------
def git_info() -> str:
    root = repo_path(".")
    h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=root).stdout
    return f"{h}\n{'dirty (uncommitted changes)' if dirty.strip() else 'clean'}\n"


def run_all(df_all: pd.DataFrame, oc: dict, n_jobs: int, sets_to_run: list[str] | None = None,
            with_sensitivity: bool = True) -> dict:
    df, info = analysis_frame(df_all, oc)
    X, owner = design_matrix(df, oc["subgroups"])
    sets = feature_sets(owner, oc)
    runs = run_grid(df, X, sets, oc, n_jobs, sets_to_run)
    res = evaluate_grid(df, runs, oc)
    shap = shap_summary(runs, owner, oc, df)
    dmg = damage_association(df, oc)
    weather = weather_link(df, n_boot=oc["n_boot"], seed=oc["seed"])
    sens = None
    if with_sensitivity:
        # country-refined groups: no RY_nb group spans two countries -> LOCO targets cannot leak
        oc2 = {**oc, "shuffle_seeds": []}
        df2, info2 = analysis_frame(df_all, oc, oc["sensitivity_group_cols"])
        X2, owner2 = design_matrix(df2, oc["subgroups"])
        runs2 = {}
        from joblib import Parallel, delayed
        y2 = df2["RY_nb"].to_numpy(float)
        specs = [{"split": "LOCO", "kind": k, "set": s, "seed": oc["seed"], "shap": False, "shuffle": None}
                 for k in ("lgbm", "ridge") for s in SET_ORDER]
        sets2 = feature_sets(owner2, oc)
        out = Parallel(n_jobs=n_jobs)(delayed(_run_config)(sp, X2.to_numpy(float), sets2[sp["set"]], list(X2.columns),
                                                           y2, df2["country"].to_numpy(), oc2) for sp in specs)
        runs2 = {_key(r["spec"]): r for r in out}
        preds = {}
        out_models = {}
        for kind in ("lgbm", "ridge"):
            preds = {s: runs2[f"LOCO/{kind}/{s}"]["pred"] for s in SET_ORDER}
            base = runs2[f"LOCO/{kind}/alle"]["base"]
            out_models[f"LOCO/{kind}"] = bootstrap_summary(y2, preds, df2["cluster"].to_numpy(), base, None,
                                                          oc["n_boot"], oc["seed"])["models"]
        sens = {"n": len(df2), "info": info2, "models": out_models}
    facts = data_facts(df_all, df, X, owner, oc, info)
    return {"df": df, "X": X, "owner": owner, "sets": sets, "runs": runs, "res": res, "shap": shap,
            "damage": dmg, "weather": weather, "sens": sens, "facts": facts}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="results dir (default results/<today>_oaf_tabular)")
    ap.add_argument("--n-boot", type=int, default=None)
    ap.add_argument("--n-jobs", type=int, default=8)
    ap.add_argument("--no-sensitivity", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    oc = oaf_config(cfg)
    if args.n_boot:
        oc["n_boot"] = args.n_boot
    df_all = oaf.load()
    out = run_all(df_all, oc, args.n_jobs, with_sensitivity=not args.no_sensitivity)

    run = repo_path(args.out) if args.out else repo_path(cfg["paths"]["results"]) / f"{date.today()}_oaf_tabular"
    run.mkdir(parents=True, exist_ok=True)
    fig_dir = repo_path(cfg["paths"]["figures"])
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "oaf_analysis_config.json").write_text(json.dumps(oc, indent=2), encoding="utf-8")
    (run / "git.txt").write_text(git_info())

    res, dmg, shap = out["res"], out["damage"], out["shap"]
    metrics = {"date": str(date.today()), "seed": oc["seed"], "n_boot": oc["n_boot"], "data": out["facts"],
               "feature_sets": out["sets"], "models": res["models"], "ablation": res["ablation"],
               "single_vs_alle": res["single_vs_alle"], "per_fold": res["per_fold"], "shuffle": res["shuffle"],
               "within_cluster_rho": res["within_cluster"], "chosen_params": res["chosen_params"], "shap": shap, "damage": dmg,
               "weather_link_exploratory": out["weather"], "sensitivity_country_groups": out["sens"]}
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2, default=float), encoding="utf-8")
    (run / "report_tables.md").write_text(markdown_tables(res, dmg, shap, out["weather"], out["sens"]), encoding="utf-8")
    pd.DataFrame(shap["features"].items(), columns=["feature", "mean_abs_shap"]).to_csv(run / "shap_features.csv", index=False)
    pd.DataFrame([x for c, r in dmg.items() for x in [dict(schaden=c, **p) for p in r.get("per_country_year", [])]]
                 ).to_csv(run / "damage_per_country_year.csv", index=False)
    fig_dir.mkdir(parents=True, exist_ok=True)
    plot_groups(res, fig_dir / "phase2_oaf_groups.png")
    plot_shap(shap, fig_dir / "phase2_oaf_shap.png")
    plot_damage(dmg, fig_dir / "phase2_oaf_damage.png")
    print(f"done -> {run}")
    print(markdown_tables(res, dmg, shap, out["weather"], out["sens"]))


if __name__ == "__main__":
    main()
