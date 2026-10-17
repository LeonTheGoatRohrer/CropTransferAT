"""Austria test: descriptive data review (protocol section 5). No parameter, threshold or model is changed here.

Usage:  python -m croptransfer.at_review [results_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from croptransfer.config import load_config, repo_path


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[ok], b[ok]).statistic) if ok.sum() >= 4 else np.nan


def main() -> None:
    cfg = load_config()
    res = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(repo_path("results").glob("*_at_test"))[-1]
    sy = pd.read_csv(res / "site_year.csv")
    reg = pd.read_csv(res / "region_year.csv")
    fl = pd.read_parquet(res / "field_scores.parquet")
    s, c = "score_09-01", "09-01"
    v = sy[sy.yas_site.notna() & sy[s].notna()]
    out: dict = {}
    out["site_years_per_year"] = v.groupby("year").size().to_dict()
    out["site_years_per_site"] = v.groupby("site").size().to_dict()
    out["baseline_kind"] = v.baseline_kind.value_counts().to_dict()
    ym = v.groupby("year").agg(score=(s, "mean"), yas=("yas_site", "mean"), n=("yas_site", "size"))
    out["year_means"] = ym.round(3).reset_index().to_dict("records")
    out["rho_year_means"] = rho(ym.score, ym.yas)
    # between-year vs within-year: demean score and yas by year, then correlate
    d = v.assign(sd=v[s] - v.groupby("year")[s].transform("mean"), yd=v.yas_site - v.groupby("year").yas_site.transform("mean"))
    out["rho_after_removing_year_means"] = rho(d.sd, d.yd)
    d2 = v.assign(sd=v[s] - v.groupby("site")[s].transform("mean"), yd=v.yas_site - v.groupby("site").yas_site.transform("mean"))
    out["rho_after_removing_site_means"] = rho(d2.sd, d2.yd)
    out["rho_ndvi_baseline_vs_score"] = rho(v.ndvi_base, v[s])
    out["rho_stress_score_to_ndvi_base_in_fields"] = rho(fl["score_09-01"], fl.ndvi_base)
    out["bundesland_rho"] = {b: rho(g[s], g.yas_site) for b, g in v.groupby("bundesland")}
    out["bundesland_n"] = v.groupby("bundesland").size().to_dict()
    out["yas_site_range"] = [float(v.yas_site.min()), float(v.yas_site.max())]
    out["yas_site_by_year"] = v.groupby("year").yas_site.agg(["mean", "min", "max"]).round(3).reset_index().to_dict("records")
    # fields: shares
    g = fl.groupby("year").agg(n=("fy_key", "size"), valid=(s, lambda x: x.notna().mean()), peak_med=("ndvi_peak", "median"),
                              peak_lt_06=("ndvi_peak", lambda x: (x < 0.6).mean()), abrupt=("abrupt_drop", "mean"),
                              score_zero=(s, lambda x: (x > -0.001).mean()), score_med=(s, "median"), obs_med=("n_dekads_obs", "median"))
    out["fields_by_year"] = g.round(3).reset_index().to_dict("records")
    out["score_ties_at_zero_share"] = float((fl[s] > -0.001).mean())
    # regional table
    out["region_year"] = reg[["adm_id", "year", "yas", f"pred_{c}", s]].round(3).to_dict("records")
    # influence of the two stressed years (descriptive): drop 2018 and 2023 together, and each pair of years
    out["rho_site_years_without_2018_2023"] = rho(v[v.year.isin([2018, 2023]) == False][s], v[v.year.isin([2018, 2023]) == False].yas_site)
    out["rho_site_years_without_pairs_min_max"] = {}
    prs = [rho(v[~v.year.isin(p)][s], v[~v.year.isin(p)].yas_site) for p in [(a, b) for i, a in enumerate(sorted(v.year.unique())) for b in sorted(v.year.unique())[i + 1:]]]
    out["rho_site_years_without_pairs_min_max"] = {"min": float(np.nanmin(prs)), "max": float(np.nanmax(prs))}
    out["rho_v1_without_2018_2023"] = rho(reg[~reg.year.isin([2018, 2023])][f"pred_{c}"], reg[~reg.year.isin([2018, 2023])].yas)
    out["v1_pred_mean_vs_obs_mean"] = [float(reg[f"pred_{c}"].mean()), float(reg.yas.mean())]
    out["v1_leave_one_year_out"] = {int(y): rho(reg[reg.year != y][f"pred_{c}"], reg[reg.year != y].yas) for y in sorted(reg.year.unique())}
    out["v1_year_means"] = reg.groupby("year").agg(yas=("yas", "mean"), pred=(f"pred_{c}", "mean")).round(3).reset_index().to_dict("records")
    (res / "review.json").write_text(json.dumps(out, indent=2, default=float, ensure_ascii=False), encoding="utf-8")

    figs = repo_path(cfg["paths"]["figures"])
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    sc = ax[0].scatter(v[s], v.yas_site, c=v.year, cmap="viridis", s=28)
    ax[0].set_xlabel("Stress-Score (09-01), höher = weniger Stress")
    ax[0].set_ylabel("Standort-Ertrag relativ (YAS_site)")
    ax[0].set_title(f"Standort-Jahre (n={len(v)})")
    fig.colorbar(sc, ax=ax[0], label="Jahr")
    r = reg.dropna(subset=[f"pred_{c}", "yas"])
    sc2 = ax[1].scatter(r[f"pred_{c}"], r.yas, c=r.year, cmap="viridis", s=28)
    ax[1].plot([0.7, 1.2], [0.7, 1.2], color="#999", lw=0.8)
    ax[1].set_xlabel("Regionalmodell: vorhergesagtes YAS (09-01)")
    ax[1].set_ylabel("Statistik Austria YAS")
    ax[1].set_title(f"Bundesländer (n={len(r)})")
    fig.tight_layout()
    fig.savefig(figs / "at_test_scatter.png", dpi=110)
    plt.close(fig)
    print(json.dumps(out, indent=1, default=float, ensure_ascii=False)[:5500])


if __name__ == "__main__":
    main()
