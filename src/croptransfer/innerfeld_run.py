"""One model round of the multi-site within-field study (reports/innerfeld_vorab.md, I4).

Everything here follows the pre-registered choices (models B0/B1/B2/M1/M2/K-Raum, schemes E/T/L, gates K1/J3a/J3b,
label shuffle). No parameter is tuned. Output: results/<date>_innerfeld/.

Usage:  python -m croptransfer.innerfeld_run [--out results/<dir>]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import Ridge
from sklearn.metrics import average_precision_score

from croptransfer.config import load_config, repo_path
from croptransfer.innerfeld_extract import N_DEKADS, load_dekads
from croptransfer.innerfeld_features import build_features, window_median
from croptransfer.within_field import boot_median_ci, safe_name, zscore_within

SEED = 42
RIDGE_ALPHA = 1.0
PROBLEM = 0.85
MIN_CELLS = 10
B0_DEKADS = (10, 13)
INTERIOR_M = 20.0
COLORADO_REGULAR_MIN_T_HA = 2.0
N_SHUFFLE = 20
M1_COLS = [f"z_m1_ndvi_w{j}" for j in (1, 2, 3)] + [f"z_m1_ndre_w{j}" for j in (1, 2, 3)]
TERRAIN_COLS = ["z_elev", "z_slope", "z_tpi"]
SPACE_COLS = ["z_cx", "z_cy", "z_cx2", "z_cy2", "z_cxy"]
MODEL_COLS = {"M1": M1_COLS, "M2": M1_COLS + TERRAIN_COLS, "KRAUM": SPACE_COLS}
UNTRAINED = {"B0": "z_b0", "B1": "z_b1_ndvi", "B2": "b2"}
DESCRIPTIVE_BELOW = 10          # Feld-Jahre
SITES = ["BARC", "KAYAD", "COLORADO"]


# ----------------------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------------------
def _z(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd > 1e-12 else s * 0.0


def persistence(df: pd.DataFrame) -> pd.Series:
    """B2: mean `rel` of the same cell in the other years of the same field (NaN without another year)."""
    key = df.site + "|" + df.field_id + "|" + df.x.round(1).astype(str) + "|" + df.y.round(1).astype(str)
    s = df.groupby(key).rel.transform("sum")
    n = df.groupby(key).rel.transform("size")
    out = (s - df.rel) / (n - 1)
    return out.where(n >= 2)


def prepare(cfg: dict[str, Any]) -> pd.DataFrame:
    """gt_pixels + features (I2 parameters) + B0 + helper columns, one row per cell."""
    proc = repo_path(cfg["paths"]["processed"])
    gt = pd.read_parquet(proc / "gt_pixels.parquet")
    tab = load_dekads(gt, cfg)
    feats, summ = build_features(tab)
    assert summ.ok.all(), "feature check failed for: " + ", ".join(summ[~summ.ok].fy_key)
    # B0: same cell order as in build_features (groupby fy_key sort=True, order inside kept)
    nd = [f"ndvi_d{k:02d}" for k in range(N_DEKADS)]
    b0 = []
    for key, g in tab.groupby("fy_key", sort=True):
        b0.append(pd.Series(window_median(g[nd].to_numpy(float), *B0_DEKADS), index=g.index))
    feats["b0"] = pd.concat(b0).to_numpy()
    feats = pd.concat([feats, zscore_within(feats, ["b0"])], axis=1)
    feats["fy_mean_yield"] = feats.groupby("fy_key").yield_t_ha.transform("mean")
    feats["problem"] = feats.rel < PROBLEM
    feats["zrel"] = feats.groupby("fy_key").rel.transform(_z)
    for c in ("x", "y"):
        feats[f"z_c{c}"] = feats.groupby("fy_key")[c].transform(_z)
    feats["z_cx2"] = feats.groupby("fy_key").z_cx.transform(lambda s: _z(s ** 2))
    feats["z_cy2"] = feats.groupby("fy_key").z_cy.transform(lambda s: _z(s ** 2))
    feats["z_cxy"] = feats.groupby("fy_key").apply(lambda g: _z(g.z_cx * g.z_cy), include_groups=False) \
        .reset_index(level=0, drop=True)
    feats["b2"] = persistence(feats)
    feats["field_cluster"] = feats.site + "|" + feats.field_id
    return feats.reset_index(drop=True)


def colorado_regular(df: pd.DataFrame) -> pd.Series:
    return (df.site == "COLORADO") & (df.fy_mean_yield >= COLORADO_REGULAR_MIN_T_HA)


def main_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Main evaluation set (vorab §1): Colorado only its regular field-years."""
    return df[(df.site != "COLORADO") | colorado_regular(df)]


# ----------------------------------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------------------------------
def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return np.nan
    ra, rb = rankdata(a), rankdata(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def fy_metrics(pred: np.ndarray, rel: np.ndarray, problem: np.ndarray) -> dict[str, float]:
    """rho, lift of the lowest predicted quarter, PR-AUC minus prevalence for one field-year."""
    m = np.isfinite(pred) & np.isfinite(rel)
    p, r, pr = pred[m], rel[m], problem[m]
    out = dict(n=int(m.sum()), rho=np.nan, lift=np.nan, pr_minus_prev=np.nan, prevalence=np.nan)
    if m.sum() < MIN_CELLS:
        return out
    out["rho"] = spearman(p, r)
    prev = float(pr.mean())
    out["prevalence"] = prev
    if 0.05 <= prev <= 0.95:
        k = max(1, int(round(0.25 * len(p))))
        flagged = np.argsort(p, kind="stable")[:k]
        out["lift"] = float(pr[flagged].mean() / prev)
        out["pr_minus_prev"] = float(average_precision_score(pr, -p) - prev)
    return out


def per_fy_table(df: pd.DataFrame, pred: pd.Series, label: str, scheme: str) -> pd.DataFrame:
    rows = []
    for key, g in df.groupby("fy_key", sort=True):
        m = fy_metrics(pred.loc[g.index].to_numpy(float), g.rel.to_numpy(float), g.problem.to_numpy())
        rows.append(dict(model=label, scheme=scheme, fy_key=key, site=g.site.iloc[0], year=int(g.year.iloc[0]),
                         cluster=g.field_cluster.iloc[0], sd_rel=float(g.rel.std()), **m))
    return pd.DataFrame(rows)


def summarize(t: pd.DataFrame, cluster_col: str, seed: int = SEED) -> dict[str, Any]:
    t = t.dropna(subset=["rho"])
    n = len(t)
    out: dict[str, Any] = dict(n_fy=int(n), n_clusters=int(t[cluster_col].nunique()) if n else 0,
                               descriptive=bool(n < DESCRIPTIVE_BELOW))
    if n == 0:
        return out
    out.update(rho_median=float(t.rho.median()), frac_rho_pos=float((t.rho > 0).mean()),
               lift_median=float(t.lift.median()) if t.lift.notna().any() else None,
               pr_minus_prev_median=float(t.pr_minus_prev.median()) if t.pr_minus_prev.notna().any() else None,
               sd_rel_median=float(t.sd_rel.median()), rho_min=float(t.rho.min()), rho_max=float(t.rho.max()))
    if n >= DESCRIPTIVE_BELOW and t[cluster_col].nunique() >= 2:
        _, lo, hi = boot_median_ci(t.rho, 1000, seed, 0.95, clusters=t[cluster_col])
        out["rho_ci"] = [lo, hi]
    return out


def paired_delta(a: pd.DataFrame, b: pd.DataFrame, cluster_col: str = "cluster", seed: int = SEED) -> dict[str, Any]:
    """Median of per-field-year rho differences a - b on shared field-years, cluster bootstrap CI."""
    m = a.merge(b, on="fy_key", suffixes=("_a", "_b"))
    m = m.dropna(subset=["rho_a", "rho_b"])
    d = m.rho_a - m.rho_b
    out: dict[str, Any] = dict(n_fy=int(len(m)))
    if len(m) == 0:
        return out
    out["delta_median"] = float(d.median())
    if len(m) >= DESCRIPTIVE_BELOW and m[f"{cluster_col}_a"].nunique() >= 2:
        _, lo, hi = boot_median_ci(d, 1000, seed, 0.95, clusters=m[f"{cluster_col}_a"])
        out["delta_ci"] = [lo, hi]
    else:
        out["descriptive"] = True
    return out


# ----------------------------------------------------------------------------------------------
# models
# ----------------------------------------------------------------------------------------------
def fit_predict(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], shuffle_seed: int | None = None) -> np.ndarray:
    """Ridge on z-features; target z-rel; each field-year weighs the same; missing features = 0."""
    y = train.zrel.to_numpy(float).copy()
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        for _, idx in train.groupby("fy_key").indices.items():
            y[idx] = rng.permutation(y[idx])
    w = 1.0 / train.groupby("fy_key").fy_key.transform("size").to_numpy(float)
    X = train[cols].fillna(0.0).to_numpy(float)
    ok = np.isfinite(y)
    mdl = Ridge(alpha=RIDGE_ALPHA).fit(X[ok], y[ok], sample_weight=w[ok])
    return mdl.predict(test[cols].fillna(0.0).to_numpy(float))


def run_folds(df: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], cols: list[str],
              shuffle_seed: int | None = None) -> pd.Series:
    pred = pd.Series(np.nan, index=df.index)
    for tr, te in folds:
        pred.iloc[te] = fit_predict(df.iloc[tr], df.iloc[te], cols, shuffle_seed)
    return pred


def folds_by_group(df: pd.DataFrame, group: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    out = []
    for g in pd.unique(group):
        te = np.flatnonzero((group == g).to_numpy())
        tr = np.flatnonzero((group != g).to_numpy())
        out.append((tr, te))
    return out


def untrained_pred(df: pd.DataFrame, name: str) -> pd.Series:
    return df[UNTRAINED[name]]


# ----------------------------------------------------------------------------------------------
def git_info() -> str:
    try:
        h = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=repo_path(".")).stdout.strip()
        d = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_path(".")).stdout
        return f"{h}\nuncommitted:\n{d}"
    except Exception:   # noqa: BLE001
        return "unknown"


def evaluate(df: pd.DataFrame, subset_name: str, sub: pd.DataFrame) -> tuple[dict, list[pd.DataFrame]]:
    """All pre-registered schemes on `sub` (rows of the evaluation set); training uses `df`-wide rules."""
    tabs: list[pd.DataFrame] = []
    res: dict[str, Any] = {}

    # untrained models per site
    for m in UNTRAINED:
        for site in SITES:
            s = sub[sub.site == site]
            if s.empty:
                continue
            t = per_fy_table(s, untrained_pred(s, m), m, "untrained")
            tabs.append(t)
            res.setdefault("untrained", {}).setdefault(site, {})[m] = summarize(t, "cluster")

    # E: within site
    for site, group_col in (("BARC", "field_cluster"), ("KAYAD", "year"), ("COLORADO", "fy_key")):
        s = sub[sub.site == site].reset_index(drop=True)
        if s.empty:
            continue
        folds = folds_by_group(s, s[group_col])
        for name, cols in MODEL_COLS.items():
            pred = run_folds(s, folds, cols)
            t = per_fy_table(s, pred, name, f"E-{site}")
            tabs.append(t)
            res.setdefault("E", {}).setdefault(site, {})[name] = summarize(t, "cluster")

    # T and L
    for te_site in SITES:
        s_te = sub[sub.site == te_site].reset_index(drop=True)
        if s_te.empty:
            continue
        for tr_site in SITES:
            if tr_site == te_site:
                continue
            tr = sub[sub.site == tr_site]
            for name, cols in MODEL_COLS.items():
                pred = pd.Series(fit_predict(tr, s_te, cols), index=s_te.index)
                t = per_fy_table(s_te, pred, name, f"T-{tr_site}->{te_site}")
                tabs.append(t)
                res.setdefault("T", {}).setdefault(f"{tr_site}->{te_site}", {})[name] = summarize(t, "cluster")
        tr = sub[sub.site != te_site]
        for name, cols in MODEL_COLS.items():
            pred = pd.Series(fit_predict(tr, s_te, cols), index=s_te.index)
            t = per_fy_table(s_te, pred, name, f"L-{te_site}")
            tabs.append(t)
            res.setdefault("L", {}).setdefault(te_site, {})[name] = summarize(t, "cluster")
    return res, tabs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_config()
    run = repo_path(args.out) if args.out else repo_path(cfg["paths"]["results"]) / f"{date.today()}_innerfeld"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(git_info())

    df = prepare(cfg)
    main_df = main_rows(df)
    out: dict[str, Any] = dict(date=str(date.today()), n_cells=int(len(main_df)), n_fy=int(main_df.fy_key.nunique()),
                               ridge_alpha=RIDGE_ALPHA, seed=SEED)
    all_tabs: list[pd.DataFrame] = []

    # ---- main round
    main_res, tabs = evaluate(df, "main", main_df.reset_index(drop=True))
    out["main"] = main_res
    all_tabs += [t.assign(subset="main") for t in tabs]
    main_tab = pd.concat(tabs, ignore_index=True)

    # ---- gates on BARC
    def pick(model: str, scheme: str) -> pd.DataFrame:
        return main_tab[(main_tab.model == model) & (main_tab.scheme == scheme) & (main_tab.site == "BARC")]

    b0, b1 = pick("B0", "untrained"), pick("B1", "untrained")
    m1 = pick("M1", "E-BARC")
    out["gates"] = dict(
        K1_B1_minus_B0_BARC=paired_delta(b1, b0),
        J3a_M1_minus_B1_BARC=paired_delta(m1, b1),
        J3a_M1_minus_B0_BARC=paired_delta(m1, b0),
        M2_minus_M1_BARC=paired_delta(pick("M2", "E-BARC"), m1),
        M1_minus_KRAUM_BARC=paired_delta(m1, pick("KRAUM", "E-BARC")))

    # ---- B0-old reproduction on BARC (calendar window from the Phase 2.3 cache)
    from croptransfer import within_field as wf
    wcfg = wf.wf_config(cfg)
    old = wf.load_table(wf.load_pixels(cfg, wcfg), cfg)
    rho_old = [wf.spearman(g.ndvi_w2.to_numpy()[np.isfinite(g.ndvi_w2)], g.rel.to_numpy()[np.isfinite(g.ndvi_w2)])
               for _, g in old.groupby("fy_key") if np.isfinite(g.ndvi_w2).sum() >= 50]
    out["b0_old_reproduction"] = dict(n_fy=len(rho_old), rho_median=float(np.median(rho_old)), target=0.676)

    # ---- label shuffle (E-BARC, T BARC->KAYAD) for M1
    s_b = main_df[main_df.site == "BARC"].reset_index(drop=True)
    folds = folds_by_group(s_b, s_b.field_cluster)
    shuf_e, shuf_t = [], []
    k_df = main_df[main_df.site == "KAYAD"].reset_index(drop=True)
    for r in range(N_SHUFFLE):
        pred = run_folds(s_b, folds, M1_COLS, shuffle_seed=SEED + r)
        shuf_e.append(per_fy_table(s_b, pred, "M1", "shuffle-E-BARC").rho.median())
        pt = pd.Series(fit_predict(s_b, k_df, M1_COLS, shuffle_seed=SEED + r), index=k_df.index)
        shuf_t.append(per_fy_table(k_df, pt, "M1", "shuffle-T").rho.median())
    out["label_shuffle"] = dict(
        E_BARC_median_rho=dict(mean=float(np.mean(shuf_e)), sd=float(np.std(shuf_e)), max_abs=float(np.max(np.abs(shuf_e)))),
        T_BARC_to_KAYAD_median_rho=dict(mean=float(np.mean(shuf_t)), sd=float(np.std(shuf_t)), max_abs=float(np.max(np.abs(shuf_t)))),
        limit_abs=0.10)

    # ---- sensitivities (evaluation sets from vorab §1/§6)
    sens: dict[str, Any] = {}
    interior = main_df[(main_df.site == "COLORADO") | (main_df.dist_edge_m >= INTERIOR_M)]
    sens["interior_ge_20m"] = evaluate(df, "interior", interior.reset_index(drop=True))[0]
    k_no16 = main_df[~((main_df.site == "KAYAD") & (main_df.year == 2016))]
    sens["kayad_without_2016"] = evaluate(df, "no2016", k_no16.reset_index(drop=True))[0]
    k_nocap = main_df[~((main_df.site == "KAYAD") & (main_df.frac_cap >= 0.5))]
    sens["kayad_without_capped_cells"] = evaluate(df, "nocap", k_nocap.reset_index(drop=True))[0]
    sens["colorado_all_10"] = evaluate(df, "co10", df.reset_index(drop=True))[0]
    out["sensitivities"] = {k: {s: v for s, v in r.items()} for k, r in sens.items()}

    # ---- site description next to every number
    out["site_sd_rel_median"] = {s: float(g.groupby("fy_key").rel.std().median()) for s, g in main_df.groupby("site")}
    out["b2_coverage"] = {s: dict(n_fy_with_b2=int(main_tab[(main_tab.model == "B2") & (main_tab.site == s)].rho.notna().sum()))
                          for s in SITES}

    pd.concat(all_tabs, ignore_index=True).to_csv(run / "per_fy.csv", index=False)
    (run / "metrics.json").write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"written {run}")


if __name__ == "__main__":
    main()
