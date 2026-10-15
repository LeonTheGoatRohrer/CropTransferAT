"""Phase 1.6/1.7 + data review numbers: coverage, curve checks, indicators vs RY, figures.

Writes results/<date>_phase1/metrics.json (+ config, git hash) and figures to reports/figures/.
Usage:  python -m croptransfer.explore_phase1
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from croptransfer import evaluate, timeseries as ts
from croptransfer.config import load_config, repo_path
from croptransfer.dataset_us import load_obs

INDICATORS = {"K1 I_Aug": "aug", "K2 postpeak": "postpeak", "K3 peak": "peak", "K4 integral": "auc"}


def same_day_pairs(obs: pd.DataFrame, max_days: int = 1) -> dict:
    """Diagnostic only: L7 vs HLS observations of the same field within +-max_days."""
    o = obs[obs.sensor.isin(["L7", "HLS"])].copy()
    o["d"] = pd.to_datetime(o.date)
    l7, hl = o[o.sensor == "L7"], o[o.sensor == "HLS"]
    m = l7.merge(hl, on="fy_key", suffixes=("_l7", "_h"))
    m = m[(m.d_l7 - m.d_h).abs().dt.days <= max_days]
    out = {}
    for idx in ["ndvi", "evi"]:
        d = m[f"{idx}_l7"] - m[f"{idx}_h"]
        out[idx] = {"n_pairs": int(len(d)), "median_diff": float(d.median()), "rmsd": float(np.sqrt((d ** 2).mean()))}
    return out


def main() -> None:
    cfg = load_config()
    proc = repo_path(cfg["paths"]["processed"])
    figs = repo_path(cfg["paths"]["figures"])
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_phase1"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    M: dict = {"git": git}

    f = pd.read_parquet(proc / "features_0901.parquet")
    hls = f[f.sensor_era == "HLS"].copy()
    dek = pd.read_parquet(proc / "gt_dekads.parquet")
    obs = load_obs(cfg)
    M["harmonisation_dekad"] = json.loads((proc / "harmonisation_check.json").read_text())
    M["harmonisation_sameday_diagnostic"] = same_day_pairs(obs)

    # counts
    M["counts"] = (f.groupby(["dataset", "sensor_era"]).agg(field_years=("fy_key", "size"),
                   with_RY=("RY_descr", "count"), site_years=("year", "nunique"))
                   .reset_index().to_dict("records"))
    # coverage + cloud bias: valid HLS obs until 1.9. vs year and vs RY
    cov = hls.groupby(["dataset", "year"]).agg(n_obs=("n_obs_hls", "median"),
                                               obsfrac=("ndvi_hls_obsfrac", "median"),
                                               ry=("RY_descr", "median")).reset_index()
    M["coverage_by_year"] = cov.round(3).to_dict("records")
    sub = hls.dropna(subset=["RY_descr", "n_obs_hls"])
    M["cloud_bias_spearman_nobs_RY"] = float(sub.n_obs_hls.corr(sub.RY_descr, method="spearman"))

    # maize-like curve check on full-season NDVI (HLS basis)
    nd = dek[(dek.basis == "HLS") & (dek["index"] == "ndvi")]
    piv = nd.pivot_table(index="fy_key", columns="dekad", values="value")
    sm = piv.apply(lambda r: pd.Series(ts.smooth(r.to_numpy())), axis=1)
    pk_dk, pk = sm.idxmax(axis=1), sm.max(axis=1)
    maize_like = (pk_dk.between(8, 16)) & (pk >= 0.6)
    # early harvest: smoothed NDVI below 0.35 already before 1.9. (dekad 15) after a peak
    early = (sm.loc[:, 9:14].min(axis=1) < 0.35) & (pk_dk < 13)
    meta = f.set_index("fy_key")
    chk = pd.DataFrame({"maize_like": maize_like, "early_harvest": early}).join(meta[["dataset", "sensor_era", "year"]])
    M["curve_check"] = chk.groupby(["dataset", "sensor_era"])[["maize_like", "early_harvest"]].mean().round(3).reset_index().to_dict("records")
    M["curve_not_maize_like"] = chk[~chk.maize_like].index.tolist()[:60]

    # indicators vs RY / Y (HLS era only, cluster bootstrap over dataset-years)
    rows = []
    for idx in ["ndvi", "evi", "ndmi", "gndvi"]:
        for kname, k in INDICATORS.items():
            col = f"{idx}_hls_{k}"
            for target in ["RY_descr", "Y_t_ha"]:
                for ds in ["KBS", "BARC", "pooled"]:
                    d = hls if ds == "pooled" else hls[hls.dataset == ds]
                    d = d.dropna(subset=[col, target])
                    if len(d) < 8:
                        continue
                    rho, lo, hi = evaluate.spearman_ci(d[col], d[target], d.dataset + d.year.astype(str),
                                                       n_boot=cfg["validation"]["bootstrap_n"], seed=cfg["seed"])
                    rows.append(dict(index=idx, indicator=kname, target=target, dataset=ds, n=len(d),
                                     clusters=int((d.dataset + d.year.astype(str)).nunique()),
                                     rho=rho, lo=lo, hi=hi))
    ind = pd.DataFrame(rows)
    ind.to_csv(run / "indicators_vs_yield.csv", index=False)
    M["indicators_vs_RY_top"] = ind[ind.target == "RY_descr"].sort_values("rho", ascending=False).head(8).round(3).to_dict("records")

    # figure 1: curves of best vs worst RY years per dataset (HLS basis, NDVI)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, ds in zip(axes, ["KBS", "BARC"]):
        d = hls[(hls.dataset == ds)].dropna(subset=["RY_descr"])
        yr = d.groupby("year").RY_descr.median()
        for y, col in [(yr.idxmax(), "#2f7a3e"), (yr.idxmin(), "#b3392f")]:
            keys = d[d.year == y].fy_key
            sel = sm.loc[sm.index.intersection(keys)]
            for _, r in sel.iterrows():
                ax.plot(r.index * 10, r.values, color=col, alpha=0.25, lw=0.8)
            ax.plot(sel.columns * 10, sel.median(), color=col, lw=2.2, label=f"{y} (RY-Median {yr[y]:.2f})")
        ax.set_title(ds)
        ax.set_xlabel("Tage seit 1. April")
        ax.legend(fontsize=8, frameon=False)
    axes[0].set_ylabel("NDVI (HLS, Dekaden)")
    fig.tight_layout()
    fig.savefig(figs / "phase1_curves_best_worst.png", dpi=110)
    plt.close(fig)

    # figure 2: K1 NDVI vs RY (HLS era)
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    for ds, c in [("KBS", "#2f7a3e"), ("BARC", "#a86a00")]:
        d = hls[hls.dataset == ds]
        ax.scatter(d["ndvi_hls_aug"], d["RY_descr"], s=14, alpha=0.7, color=c, label=ds)
    ax.axhline(0.85, color="#b3392f", lw=0.8, ls="--")
    ax.set_xlabel("K1: NDVI August (HLS)")
    ax.set_ylabel("RY (trendbereinigt)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figs / "phase1_k1_vs_ry.png", dpi=110)
    plt.close(fig)

    (run / "metrics.json").write_text(json.dumps(M, indent=2, default=str))
    print(json.dumps({k: M[k] for k in ["counts", "cloud_bias_spearman_nobs_RY", "curve_check",
                                         "harmonisation_sameday_diagnostic", "indicators_vs_RY_top"]},
                     indent=1, default=str))


if __name__ == "__main__":
    main()
