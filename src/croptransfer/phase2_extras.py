"""Phase 2 controls + Phase 4 criterion check for the selected main-model candidate.

- main-model choice by the pre-registered rule (PLAN Phase 4, DECISIONS 2026-10-15)
- Leave-One-Dataset-Out KBS->BARC and BARC->KBS, LOYO, LOFO
- label-shuffle control, adversarial validation KBS vs BARC
- split-conformal intervals (cross-conformal over LOFYO folds) and coverage
- SHAP (TreeExplainer) of M-alle LightGBM, early-warning figure
- "stark genug" criteria 1-4 -> criteria.json

Usage:  python -m croptransfer.phase2_extras --run results/<date>_phase2 [--tag main]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from croptransfer import evaluate, features, splits, targets
from croptransfer.config import load_config, repo_path
from croptransfer.models import family
from croptransfer.run_phase2 import (columns_for, eval_mask, fit_predict, load_features, metrics,
                                     pool_mask, run_task)

SIMPLE_KIND = {"ridge": 0, "lgbm": 1}
SIMPLE_BASIS = {"HLS": 0, "S2": 1}
SIMPLE_VARIANT = {"main": 0, "W-lang": 1}
LATE_CUTOFFS = ["08-01", "08-15", "09-01"]


def select_main(met: pd.DataFrame, cutoff: str = "09-01") -> pd.Series:
    """Highest median within-year rho at 1.9.; within 0.05 of the best the simplest wins."""
    c = met[(met.cutoff == cutoff) & ~met.model.isin(["B1", "M-B+"])].copy()
    best = c.median_within_year_rho.max()
    near = c[c.median_within_year_rho >= best - 0.05].copy()
    near["simplicity"] = list(zip(near.kind.map(SIMPLE_KIND), near.model.map(lambda m: len(family.FAMILY[m])),
                                  near.basis.map(SIMPLE_BASIS), near.variant.map(SIMPLE_VARIANT),
                                  -near.median_within_year_rho))
    return near.sort_values("simplicity").iloc[0]


def lodo_eval(df, groups, spec, a, b, seed):
    """Train on dataset a (in-fold labels within a), test on b (b's own trend-adjusted RY)."""
    code, kind, basis, mmdd, variant = spec
    em = eval_mask(df, basis)
    pool = pool_mask(df, code, basis, variant)
    tr = df.index[df.dataset == a]
    te = df.index[(df.dataset == b) & em]
    ry_tr = targets.compute_ry(df.loc[tr], df.loc[tr], df.loc[tr])
    fit_idx = ry_tr.index[ry_tr.notna() & pool.loc[ry_tr.index]]
    y_te = targets.ry_descriptive(df).loc[te].dropna()
    cols = columns_for(code, basis, groups)
    pred, _ = fit_predict(df, cols, kind, fit_idx, ry_tr.loc[fit_idx].to_numpy(), y_te.index, seed)
    o = pd.DataFrame({"fy_key": df.loc[y_te.index, "fy_key"].to_numpy(), "dataset": b,
                      "year": df.loc[y_te.index, "year"].to_numpy(), "y": y_te.to_numpy(), "pred": pred})
    return o


def cross_conformal(oof: pd.DataFrame, alpha: float = 0.2) -> dict:
    """Interval half-width per fold from |residuals| of the OTHER folds; coverage on the fold."""
    cov, widths = [], []
    for f, g in oof.groupby("fold"):
        res = np.abs(oof.loc[oof.fold != f, "y"] - oof.loc[oof.fold != f, "pred"])
        n = len(res)
        q = np.quantile(res, min(1.0, np.ceil((n + 1) * (1 - alpha)) / n))
        cov += list(np.abs(g.y - g.pred) <= q)
        widths.append(q)
    return {"alpha": alpha, "coverage": float(np.mean(cov)), "nominal": 1 - alpha,
            "median_halfwidth": float(np.median(widths)), "n": len(cov)}


def adversarial(df, groups, seed) -> dict:
    """Can a classifier tell KBS from BARC rows (HLS era) from S+W+B features?"""
    from lightgbm import LGBMClassifier
    from sklearn.model_selection import cross_val_predict, GroupKFold
    from sklearn.metrics import roc_auc_score

    d = df[(df.sensor_era == "HLS") & df.dataset.isin(["KBS", "BARC"])]
    cols = groups["S_hls"] + groups["W"] + groups["B"]
    y = (d.dataset == "KBS").astype(int).to_numpy()
    clf = LGBMClassifier(max_depth=2, n_estimators=100, verbose=-1, random_state=seed)
    p = cross_val_predict(clf, d[cols], y, groups=d.year, cv=GroupKFold(4), method="predict_proba")[:, 1]
    clf.fit(d[cols], y)
    imp = pd.Series(clf.feature_importances_, index=cols).sort_values(ascending=False)
    return {"auc": float(roc_auc_score(y, p)), "top_features": imp.head(5).index.tolist()}


def shap_summary(df, groups, mmdd, seed, out_png: Path) -> dict:
    import shap

    spec_cols = columns_for("M-alle", "HLS", groups)
    em = eval_mask(df, "HLS")
    y = targets.ry_descriptive(df).loc[em]
    X = df.loc[y.index, spec_cols]
    use = family.usable_columns(X)
    mdl = family.make("lgbm", family.LGBM_GRID[0], seed).fit(X[use], y.to_numpy())
    sv = shap.TreeExplainer(mdl).shap_values(X[use])
    imp = pd.Series(np.abs(sv).mean(axis=0), index=use).sort_values(ascending=False)
    grp = {"S": groups["S_hls"], "W": groups["W"], "B": groups["B"]}
    by_group = {g: float(imp[[c for c in cols if c in imp.index]].sum()) for g, cols in grp.items()}
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    top = imp.head(10)[::-1]
    ax.barh(top.index, top.values, color="#2f7a3e")
    ax.set_xlabel("mittlerer |SHAP| (RY)")
    ax.set_title(f"M-alle LightGBM, Stichtag {mmdd} (in-sample, nur Erklärung)", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)
    return {"top10": imp.head(10).round(4).to_dict(), "by_group": by_group}


def early_warning_png(met: pd.DataFrame, specs: list[tuple], out_png: Path):
    fig, ax = plt.subplots(figsize=(6, 3.6))
    colors = ["#2f7a3e", "#a86a00", "#3b6ea8", "#8a4f9e", "#b3392f", "#555"]
    for (code, kind, basis, variant), c in zip(specs, colors):
        g = met[(met.model == code) & (met.kind == kind) & (met.basis == basis) & (met.variant == variant)].sort_values("cutoff")
        if g.empty:
            continue
        ax.plot(g.cutoff, g.rho, marker="o", color=c, label=f"{code} {kind} {basis}{'' if variant == 'main' else ' ' + variant}")
        ax.fill_between(g.cutoff, g.rho_lo, g.rho_hi, color=c, alpha=0.12)
    ax.axhline(0, color="#888", lw=0.8)
    ax.axhline(0.4, color="#b3392f", lw=0.8, ls="--")
    ax.set_ylabel("Spearman ρ (LOFYO, gepoolt)")
    ax.set_xlabel("Stichtag")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(out_png, dpi=110)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--tag", default="main")
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    run = Path(args.run)
    met = pd.read_csv(run / "metrics.csv", dtype={"cutoff": str})
    figs = repo_path(cfg["paths"]["figures"])
    sel = select_main(met)
    spec = (sel.model, sel.kind, sel.basis, "09-01", sel.variant)
    out: dict = {"selected": sel.to_dict()}
    df = load_features(cfg, "09-01")
    groups = features.feature_groups(df.columns)

    # criterion 1: beats B0 and B1 at >= 1 cutoff from 1.8. (CI of RMSE difference excludes 0)
    m = met[(met.model == sel.model) & (met.kind == sel.kind) & (met.basis == sel.basis) & (met.variant == sel.variant)]
    late = m[m.cutoff.isin(LATE_CUTOFFS)]
    c1 = bool(((late.d_rmse_b0_hi < 0) & (late.d_rmse_b1_hi < 0)).any())
    c2_row = m[m.cutoff == "09-01"].iloc[0]
    c2 = bool(c2_row.rho >= 0.4)
    lodo = {}
    for a, b in [("KBS", "BARC"), ("BARC", "KBS")]:
        o = lodo_eval(df, groups, spec, a, b, seed)
        cl = o.dataset + "-" + o.year.astype(str)
        r, lo, hi = evaluate.spearman_ci(o.pred, o.y, cl, cfg["validation"]["bootstrap_n"], seed)
        lodo[f"{a}->{b}"] = {"n": len(o), "rho": r, "lo": lo, "hi": hi}
    c3 = all(v["rho"] > 0 for v in lodo.values())
    sh = run_task(df, groups, *spec, seed, folds_name="LOFYO", shuffle=True)
    shm = metrics(sh, None, cfg)
    c4 = bool(shm["rho_lo"] <= 0 <= shm["rho_hi"] and not shm["d_rmse_b0_hi"] < 0)
    out["criteria"] = {
        "1_beats_B0_B1_from_0801": {"passed": c1, "rows": late[["cutoff", "d_rmse_b0", "d_rmse_b0_lo", "d_rmse_b0_hi",
                                                                "d_rmse_b1", "d_rmse_b1_lo", "d_rmse_b1_hi"]].round(4).to_dict("records")},
        "2_rho_ge_0.4_at_0901": {"passed": c2, "rho": c2_row.rho, "lo": c2_row.rho_lo, "hi": c2_row.rho_hi, "n": int(c2_row.n)},
        "3_lodo_both_directions_rho_gt_0": {"passed": c3, **lodo},
        "4_label_shuffle_baseline": {"passed": c4, "rho": shm["rho"], "lo": shm["rho_lo"], "hi": shm["rho_hi"],
                                     "skill_b0": shm["skill_b0"]},
    }
    out["strong_enough"] = bool(c1 and c2 and c3 and c4)
    # secondary splits for the selected model
    for name, fn in [("LOYO", splits.loyo), ("LOFO", splits.lofo)]:
        o = run_task(df, groups, *spec, seed, folds_name=name, folds=fn(df, eval_mask(df, sel.basis)))
        out[name] = {k: v for k, v in metrics(o, None, cfg).items() if k in ("n", "rho", "rho_lo", "rho_hi", "rmse", "skill_b0")}
    # uncertainty from the LOFYO oof of the selected model
    oof = pd.read_parquet(run / "oof.parquet")
    so = oof[(oof.model == sel.model) & (oof.kind == sel.kind) & (oof.basis == sel.basis) & (oof.variant == sel.variant) & (oof.cutoff == "09-01")]
    out["conformal_80"] = cross_conformal(so, 0.2)
    out["conformal_90"] = cross_conformal(so, 0.1)
    out["adversarial_KBS_vs_BARC"] = adversarial(df, groups, seed)
    out["shap_M-alle_lgbm_0901"] = shap_summary(df, groups, "09-01", seed, figs / f"phase2_shap_{args.tag}.png")
    early_warning_png(met, [("M-alle", "lgbm", "HLS", "main"), ("M-alle", "ridge", "HLS", "main"),
                            ("M-S", "ridge", "S2", "main"), ("M-W", "lgbm", "HLS", "W-lang"),
                            (sel.model, sel.kind, sel.basis, sel.variant)],
                      figs / f"phase2_earlywarning_{args.tag}.png")
    (run / f"criteria_{args.tag}.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps({k: out[k] for k in ["selected", "criteria", "strong_enough", "LOYO", "LOFO", "conformal_80",
                                           "adversarial_KBS_vs_BARC"]}, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
