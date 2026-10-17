"""F3.4 main result "Welches Feld und welcher Feldteil fällt auf?" from the ablation run (no new fitting).

1. ranking of fields per site-year by out-of-fold risk of the main model, with the conformal alarm
   threshold (FPR <= alarm_fpr on non-at-risk US field-years, finite-sample (n+1) correction);
2. explanation: share of the stress score coming from June / July / August (fold reference curves);
3. field map: lowest-NDVI zones (window w2) vs. measured problem zones for BARC example field-years;
4. descriptive sensitivity without the KBS organic plots (T4), found in the case check (not used for selection).
Usage:  python -m croptransfer.fj_product --run results/<date>_feinjust_ablation
Writes <run>/product.json, <run>/ranking.csv and reports/figures/fj_*.png.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from croptransfer import feinjust, splits, stress, targets
from croptransfer.config import load_config, repo_path
from croptransfer.run_phase2 import eval_mask

PHASES = {"Juni": (6, 8), "Juli": (9, 11), "August": (12, 14)}     # dekads (0 = 1.-10.4.)


def conformal_threshold(neg_scores: np.ndarray, fpr: float) -> float:
    """Smallest t with at most `fpr` of future negatives above t (split-conformal, (n+1) correction)."""
    s = np.sort(np.asarray(neg_scores, float))
    n = len(s)
    k = math.ceil((n + 1) * (1 - fpr))
    return float(s[min(k, n) - 1])


def phase_shares(dek: pd.DataFrame, key: str, ref: pd.Series, cutoff: str, basis: str) -> dict:
    """Negative deviation from the reference summed per season phase (observed dekads only)."""
    k = stress.last_complete_dekad(cutoff)
    d = dek[(dek.fy_key == key) & dek.is_observed & dek.dekad.between(6, k)]
    dev = np.minimum(d.value.to_numpy() - ref.reindex(d.dekad).to_numpy(), 0)
    out = {}
    for name, (a, b) in PHASES.items():
        m = d.dekad.between(a, b).to_numpy()
        out[name] = float(np.nansum(dev[m]))
    return out


def explanations(df: pd.DataFrame, dek: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    fj = cfg["feinjust"]
    rows = []
    for name, tr, te in splits.lofyo(df, eval_mask(df, fj["basis"])):
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        ry_tr = ry_tr.dropna()
        healthy = df.loc[ry_tr.index[(ry_tr >= feinjust.HEALTHY) & (df.loc[ry_tr.index, "sensor_era"] == "HLS")], "fy_key"]
        ref = stress.reference_curve(dek, healthy, basis=fj["basis"])
        for i in ry_te.index[ry_te.notna()]:
            rows.append({"fy_key": df.loc[i, "fy_key"], **phase_shares(dek, df.loc[i, "fy_key"], ref, fj["cutoff"], fj["basis"])})
    return pd.DataFrame(rows)


def sensitivity_t4(oof: pd.DataFrame, cfg: dict) -> dict:
    """PR-AUC of A-roh/A0 on subsets (all, without KBS T4, BARC only, KBS without T4) and rho within KBS treatment x year."""
    from croptransfer import evaluate
    from croptransfer.phase3 import pr_metrics

    tr = feinjust.load_features(cfg, cfg["feinjust"]["cutoff"])[["fy_key", "treatment"]]
    out = {}
    for m in ["A_roh", "A0"]:
        x = oof[oof.model == m].merge(tr, on="fy_key")
        subsets = {"alle": x, "ohne_T4": x[x.treatment != "T4"], "nur_BARC": x[x.dataset == "BARC"],
                   "KBS_ohne_T4": x[(x.dataset == "KBS") & (x.treatment != "T4")]}
        for lab, sub in subsets.items():
            r = pr_metrics(sub.ry < feinjust.THR, sub.p, sub.dataset + "-" + sub.year.astype(str), cfg)
            out[f"{m}|{lab}"] = {k: r[k] for k in ["n", "positives", "prevalence", "pr_auc", "pr_auc_lo", "pr_auc_hi",
                                                    "recall_at_20fpr"]}
        w = [evaluate._spearman(-g.p.to_numpy(), g.ry.to_numpy())
             for _, g in x[x.dataset == "KBS"].groupby(["year", "treatment"]) if g.ry.nunique() > 2]
        out[f"{m}|KBS_rho_innerhalb_Behandlung_Jahr"] = {"n_groups": len(w), "median": float(np.median(w)),
                                                         "values": [round(v, 3) for v in w]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    cfg = load_config()
    fj = cfg["feinjust"]
    run = Path(a.run)
    figs = repo_path(cfg["paths"]["figures"])
    met = json.loads((run / "metrics.json").read_text())
    main_a = met["main_model"]["A"]
    oof = pd.read_parquet(run / "oof.parquet")
    o = oof[oof.model == main_a].copy()
    o["risk"] = o.ry < feinjust.THR
    thr = conformal_threshold(o.loc[~o.risk, "p"].to_numpy(), fj["alarm_fpr"])
    o["alarm"] = o.p > thr
    o["rank_in_site_year"] = o.groupby(["dataset", "year"]).p.rank(ascending=False, method="first").astype(int)
    out = {"main_model": main_a, "alarm_threshold_oof": thr,
           "alarm_recall": float(o.loc[o.risk, "alarm"].mean()), "alarm_fpr": float(o.loc[~o.risk, "alarm"].mean()),
           "alarm_precision": float(o.loc[o.alarm, "risk"].mean()) if o.alarm.any() else np.nan,
           "n": int(len(o)), "n_alarm": int(o.alarm.sum())}
    # top-k hit rate per site-year: share of at-risk fields among the k highest-risk fields (k = #at-risk)
    hits = []
    for (ds, yr), g in o.groupby(["dataset", "year"]):
        k = int(g.risk.sum())
        if 0 < k < len(g):
            top = g.nsmallest(k, "rank_in_site_year")
            hits.append({"site_year": f"{ds}-{yr}", "n": len(g), "at_risk": k, "hit_rate_top_k": float(top.risk.mean()),
                         "random": k / len(g)})
    out["top_k_by_site_year"] = hits
    # explanation by season phase
    df = feinjust.load_features(cfg, fj["cutoff"])
    dek = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / "gt_dekads.parquet")
    dek = dek[(dek["index"] == "ndvi") & (dek.basis == fj["basis"])]
    ex = explanations(df, dek, cfg)
    o = o.merge(ex, on="fy_key", how="left")
    ph = list(PHASES)
    o["main_phase"] = o[ph].idxmin(axis=1).where(o[ph].min(axis=1) < 0, "keine Abweichung")
    out["main_phase_alarms"] = o[o.alarm].main_phase.value_counts().to_dict()
    out["main_phase_at_risk"] = o[o.risk].main_phase.value_counts().to_dict()
    out["phase_sum_mean"] = {"gefährdet": o[o.risk][ph].mean().round(3).to_dict(),
                             "nicht gefährdet": o[~o.risk][ph].mean().round(3).to_dict()}
    o.drop(columns=["model"]).round(4).to_csv(run / "ranking.csv", index=False)
    # figure 1: ranking per site-year
    groups = list(o.groupby(["dataset", "year"]))
    fig, axes = plt.subplots(2, math.ceil(len(groups) / 2), figsize=(13, 5.6), sharey=True)
    for ax, ((ds, yr), g) in zip(axes.ravel(), groups):
        g = g.sort_values("p", ascending=False)
        ax.bar(range(len(g)), g.p, color=np.where(g.risk, "#b03a2e", "#9aa9b8"))
        ax.axhline(thr, color="#333", ls="--", lw=0.8)
        ax.set_title(f"{ds} {yr} (gefährdet {int(g.risk.sum())}/{len(g)})", fontsize=8)
        ax.set_xticks([])
    for ax in axes.ravel()[len(groups):]:
        ax.axis("off")
    axes[0, 0].set_ylabel("Risiko (Modell, außerhalb des Trainings)")
    axes[1, 0].set_ylabel("Risiko")
    fig.suptitle("Rangliste je Standort-Jahr: rot = tatsächlich gefährdet (RY < 0,85), Linie = Alarmschwelle (≤ 20 % Fehlalarme)",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(figs / "fj_ranking.png", dpi=110)
    plt.close(fig)
    # figure 2: explanation by season phase
    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = np.arange(len(ph))
    for j, (lab, m, c) in enumerate([("gefährdet", o.risk, "#b03a2e"), ("nicht gefährdet", ~o.risk, "#9aa9b8")]):
        ax.bar(x + (j - 0.5) * 0.38, -o[m][ph].mean().to_numpy(), 0.38, color=c, label=lab)
    ax.set_xticks(x, ph)
    ax.set_ylabel("NDVI unter Referenz (Summe)")
    ax.set_title("Wann weicht die Kurve ab? (Stress-Score nach Monaten, 1.9.)", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figs / "fj_score_phases.png", dpi=110)
    plt.close(fig)
    out["within_field_map"] = field_map(cfg, figs / "fj_field_map.png")
    (run / "sensitivity_T4.json").write_text(json.dumps(sensitivity_t4(oof, cfg), indent=1, default=float))
    (run / "product.json").write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps(out, indent=1, default=float))


def field_map(cfg: dict, path: Path) -> dict:
    """Two BARC field-years: lowest-quartile NDVI w2 ('auffällig') vs measured problem zone (rel < 0.85)."""
    d, _, wf = feinjust.pixel_table(cfg)
    d = d[np.isfinite(d.ndvi_w2)]
    stats = []
    for key, g in d.groupby("fy_key"):
        flag = g.ndvi_w2 <= g.ndvi_w2.quantile(0.25)
        prob = g.problem.astype(bool)
        stats.append({"fy_key": key, "n": len(g), "precision": float(prob[flag].mean()), "prevalence": float(prob.mean()),
                      "recall": float(flag[prob].mean()) if prob.any() else np.nan})
    st = pd.DataFrame(stats)
    st["lift"] = st.precision / st.prevalence
    ex = st.sort_values("n", ascending=False).head(2).fy_key.tolist()
    fig, axes = plt.subplots(len(ex), 2, figsize=(9, 4.2 * len(ex)))
    for row, key in zip(np.atleast_2d(axes), ex):
        g = d[d.fy_key == key]
        flag = g.ndvi_w2 <= g.ndvi_w2.quantile(0.25)
        row[0].scatter(g.x, g.y, c=np.where(flag, "#b03a2e", "#cfd8dc"), s=7, marker="s")
        row[0].set_title(f"{key.split('|')[1]} {key.split('|')[2]}: auffällig (unterstes NDVI-Viertel, 16.7.–15.8.)", fontsize=8)
        row[1].scatter(g.x, g.y, c=np.where(g.problem, "#b03a2e", "#cfd8dc"), s=7, marker="s")
        row[1].set_title("gemessen: Problemzone (Ertrag < 85 % des Feldmittels)", fontsize=8)
        for ax in row:
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return {"n_fy": int(len(st)), "median_precision": float(st.precision.median()),
            "median_prevalence": float(st.prevalence.median()), "median_lift": float(st.lift.median()),
            "median_recall": float(st.recall.median()), "examples": ex}


if __name__ == "__main__":
    main()
