"""Phase 3 - problem fields (F2): at-risk classification, reference curve, causes, indicator choice.

Usage:  python -m croptransfer.phase3 --run results/<dir> --model M --kind K --basis B --variant V
Writes <run>/phase3.json, <run>/phase3_cases.csv and reports/figures/phase3_*.png.
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

from croptransfer import evaluate, features, rounds, splits, stress, targets
from croptransfer.config import load_config, repo_path
from croptransfer.run_phase2 import columns_for, eval_mask, load_features, pool_mask

THR = 0.85
SIMPLE_K = {"K1 I_Aug": 0, "K3 peak": 1, "K2 postpeak": 2, "K4 integral": 3}
SIMPLE_I = {"ndvi": 0, "evi": 1, "ndre": 2, "ndmi": 3, "gndvi": 4}


def pr_metrics(y_risk, score, clusters, cfg) -> dict:
    """PR-AUC (with prevalence), recall at 20 % FPR, cluster-bootstrap CI of PR-AUC."""
    y = np.asarray(y_risk, int)
    s = np.asarray(score, float)
    ok = np.isfinite(s)
    y, s, cl = y[ok], s[ok], pd.Series(np.asarray(clusters)[ok])
    if len(y) < 5 or y.sum() == 0:
        return {"n": int(len(y)), "positives": int(y.sum()), "prevalence": np.nan, "pr_auc": np.nan,
                "recall_at_20fpr": np.nan, "pr_auc_lo": np.nan, "pr_auc_hi": np.nan}
    out = {"n": int(len(y)), "positives": int(y.sum()), "prevalence": float(y.mean()) if len(y) else np.nan,
           "pr_auc": evaluate.pr_auc(y, s), "recall_at_20fpr": evaluate.recall_at_fpr(y, s, 0.2)}
    bs = []
    for idx in evaluate._boot_clusters(cl, cfg["validation"]["bootstrap_n"], cfg["seed"]):
        bs.append(evaluate.pr_auc(y[idx], s[idx]))
    out["pr_auc_lo"], out["pr_auc_hi"] = (float(v) for v in np.nanpercentile(bs, [2.5, 97.5]))
    return out


def model_columns(df, groups, model, basis, variant):
    if variant.startswith("round"):
        df2, specs = rounds.round_specs(int(variant[-1]), df, groups, basis)
        return df2, next(s[2] for s in specs if s[0] == model)
    return df, columns_for(model, basis, groups)


def direct_classifier(df, cols, basis, seed) -> pd.DataFrame:
    """(b) shallow LightGBM classifier for RY < 0.85, LOFYO with in-fold labels."""
    from lightgbm import LGBMClassifier

    em = eval_mask(df, basis)
    pool = pool_mask(df, "M-alle", basis, "main")
    out = []
    for name, tr, te in splits.lofyo(df, em):
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        fit = ry_tr.index[ry_tr.notna() & pool.loc[ry_tr.index]]
        te = ry_te.index[ry_te.notna()]
        y = (ry_tr.loc[fit] < THR).astype(int)
        if len(te) == 0 or y.nunique() < 2:
            p = np.full(len(te), y.mean() if len(y) else np.nan)
        else:
            clf = LGBMClassifier(max_depth=2, num_leaves=4, n_estimators=150, learning_rate=0.05,
                                 min_child_samples=10, class_weight="balanced", verbose=-1, random_state=seed)
            clf.fit(df.loc[fit, cols], y)
            p = clf.predict_proba(df.loc[te, cols])[:, 1]
        out.append(pd.DataFrame({"fy_key": df.loc[te, "fy_key"].to_numpy(), "dataset": df.loc[te, "dataset"].to_numpy(),
                                 "year": df.loc[te, "year"].to_numpy(), "y": ry_te.loc[te].to_numpy(), "p": p}))
    return pd.concat(out, ignore_index=True)


def reference_scores(df, dek, basis, mmdd) -> pd.DataFrame:
    """Stress score with the healthy-maize reference built from training folds only."""
    em = eval_mask(df, basis)
    rows = []
    for name, tr, te in splits.lofyo(df, em):
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        healthy = df.loc[ry_tr.index[(ry_tr >= 0.95) & (df.loc[ry_tr.index, "sensor_era"] == "HLS")], "fy_key"]
        ref = stress.reference_curve(dek, healthy, basis=basis)
        for i in ry_te.index[ry_te.notna()]:
            rows.append({"fy_key": df.loc[i, "fy_key"], "dataset": df.loc[i, "dataset"], "year": df.loc[i, "year"],
                         "y": ry_te[i], "score": stress.stress_score(dek, df.loc[i, "fy_key"], ref, mmdd, basis=basis)})
    return pd.DataFrame(rows)


def choose_indicator(ind: pd.DataFrame) -> dict:
    """PLAN Phase 3.5: highest median rho across datasets; < 0.05 apart -> simpler; needs rho >= 0.4."""
    r = ind[(ind.target == "RY_descr") & (ind.dataset.isin(["KBS", "BARC"]))]
    med = r.groupby(["index", "indicator"]).rho.median().reset_index()
    best = med.rho.max()
    near = med[med.rho >= best - 0.05].copy()
    near["s"] = list(zip(near.indicator.map(SIMPLE_K), near["index"].map(SIMPLE_I)))
    pick = near.sort_values("s").iloc[0]
    sub = ind[(ind["index"] == pick["index"]) & (ind.indicator == pick.indicator) & (ind.target == "RY_descr")]
    ok = bool((sub.rho >= 0.4).any())
    return {"index": pick["index"], "indicator": pick.indicator, "median_rho": float(pick.rho),
            "per_dataset": sub[["dataset", "n", "clusters", "rho", "lo", "hi"]].round(3).to_dict("records"),
            "precondition_rho_ge_0.4": ok, "chosen": ok}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--basis", required=True)
    ap.add_argument("--variant", required=True)
    a = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    run = Path(a.run)
    figs = repo_path(cfg["paths"]["figures"])
    proc = repo_path(cfg["paths"]["processed"])
    dek = pd.read_parquet(proc / "gt_dekads.parquet")
    oof = pd.read_parquet(run / "oof.parquet")
    sel = oof[(oof.model == a.model) & (oof.kind == a.kind) & (oof.basis == a.basis) & (oof.variant == a.variant)]
    out: dict = {"model": vars(a), "per_cutoff": {}}
    for mmdd in cfg["cutoffs"]["yield_model"]:
        df = load_features(cfg, mmdd)
        groups = features.feature_groups(df.columns)
        o = sel[sel.cutoff == mmdd]
        cl = o.dataset + "-" + o.year.astype(str)
        res = {"a_threshold_on_pred_RY": pr_metrics(o.y < THR, -o.pred, cl, cfg)}
        df2, cols = model_columns(df, groups, a.model, a.basis, a.variant)
        dc = direct_classifier(df2, cols, a.basis, seed)
        res["b_direct_classifier"] = pr_metrics(dc.y < THR, dc.p, dc.dataset + "-" + dc.year.astype(str), cfg)
        rs = reference_scores(df, dek, a.basis, mmdd)
        rcl = rs.dataset + "-" + rs.year.astype(str)
        ok = rs.score.notna()
        rho, lo, hi = (evaluate.spearman_ci(rs.score[ok], rs.y[ok], rcl[ok], cfg["validation"]["bootstrap_n"], seed)
                       if ok.sum() >= 5 else (np.nan, np.nan, np.nan))
        res["reference_stress_score"] = {"spearman_RY": rho, "lo": lo, "hi": hi,
                                         **pr_metrics(rs.y < THR, -rs.score, rcl, cfg)}
        out["per_cutoff"][mmdd] = res
        print(mmdd, json.dumps({k: {kk: round(v, 3) if isinstance(v, float) else v for kk, v in r.items()}
                                for k, r in res.items()}), flush=True)
    # causes at 1.9. for at-risk field-years (descriptive RY), HLS era
    df = load_features(cfg, "09-01")
    risk = df[(df.sensor_era == "HLS") & (df.RY_descr < THR)]
    obs = dek[(dek["index"] == "ndvi") & (dek.basis == "HLS") & dek.is_observed]
    cause_rows = []
    for _, r in risk.iterrows():
        c = stress.causes(r, obs[obs.fy_key == r.fy_key][["dekad", "value"]])
        cause_rows.append({"fy_key": r.fy_key, "dataset": r.dataset, "year": r.year, "RY": r.RY_descr, "causes": ", ".join(c)})
    cz = pd.DataFrame(cause_rows)
    out["causes_counts"] = cz.causes.str.split(", ").explode().value_counts().to_dict()
    out["causes_by_site_year"] = cz.groupby(["dataset", "year"]).causes.agg(lambda s: s.value_counts().to_dict()).to_dict()
    out["causes_by_site_year"] = {f"{k[0]}-{k[1]}": v for k, v in out["causes_by_site_year"].items()}
    # case studies at 1.9. with rule (a): 3 hits, 3 misses, 3 false alarms
    o = sel[sel.cutoff == "09-01"].merge(cz[["fy_key", "causes"]], on="fy_key", how="left")
    o["risk"], o["alarm"] = o.y < THR, o.pred < THR
    cases = pd.concat([o[o.risk & o.alarm].nsmallest(3, "y").assign(case="richtig erkannt"),
                       o[o.risk & ~o.alarm].nsmallest(3, "y").assign(case="verpasst"),
                       o[~o.risk & o.alarm].nsmallest(3, "pred").assign(case="Fehlalarm")])
    cases[["case", "fy_key", "dataset", "year", "y", "pred", "causes"]].round(3).to_csv(run / "phase3_cases.csv", index=False)
    out["cases"] = cases[["case", "fy_key", "y", "pred", "causes"]].round(3).to_dict("records")
    # indicator choice (Phase 3.5) from the Phase-1 table
    p1 = sorted(repo_path(cfg["paths"]["results"]).glob("*_phase1"))[-1]
    out["indicator_choice"] = choose_indicator(pd.read_csv(p1 / "indicators_vs_yield.csv"))
    # early-warning figure for "gefährdet"
    cut = list(out["per_cutoff"])
    fig, ax = plt.subplots(figsize=(6, 3.4))
    for key, lab, c in [("a_threshold_on_pred_RY", "(a) Schwelle auf vorhergesagtem RY", "#2f7a3e"),
                        ("b_direct_classifier", "(b) direkter Klassifikator", "#a86a00"),
                        ("reference_stress_score", "Stress-Score Referenzkurve", "#3b6ea8")]:
        v = [out["per_cutoff"][m][key]["pr_auc"] for m in cut]
        lo = [out["per_cutoff"][m][key]["pr_auc_lo"] for m in cut]
        hi = [out["per_cutoff"][m][key]["pr_auc_hi"] for m in cut]
        ax.plot(cut, v, marker="o", color=c, label=lab)
        ax.fill_between(cut, lo, hi, color=c, alpha=0.12)
    prev = out["per_cutoff"]["09-01"]["a_threshold_on_pred_RY"]["prevalence"]
    ax.axhline(prev, color="#888", ls="--", lw=0.8, label=f"Prävalenz {prev:.2f}")
    ax.set_ylabel("PR-AUC (LOFYO)")
    ax.set_xlabel("Stichtag")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(figs / "phase3_earlywarning_risk.png", dpi=110)
    plt.close(fig)
    (run / "phase3.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps({k: out[k] for k in ["causes_counts", "indicator_choice"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
