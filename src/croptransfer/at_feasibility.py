"""AT model, feasibility test only (DECISIONS 2026-10-17; PLAN Phase 8 - not part of the proof).

Counts the Austrian data first (sites, years, coordinates). Runs only if >= 30 site-years with yield and score,
>= 5 years and >= 3 sites. Model: linear regression YAS_site ~ frozen stress score (1 Sep), leave-one-year-out.
Reports Spearman rho, RMSE vs "normal year" (YAS = 1) and vs the training mean, with bootstrap CIs over years.
Uses only the aggregated, already evaluated table results/2026-10-17_at_test/site_year.csv and the metadata
columns of data/raw/at_trials.csv (counting). The frozen US model is not touched.

Usage:  python -m croptransfer.at_feasibility
Writes: results/2026-10-17_at_feasibility/{metrics.json, predictions.csv}
"""

from __future__ import annotations

import json
import subprocess
from datetime import date

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from croptransfer.config import repo_path

MIN_SITE_YEARS, MIN_YEARS, MIN_SITES = 30, 5, 3
N_BOOT, SEED = 2000, 42
SCORE = "score_09-01"


def counts() -> dict:
    sy = pd.read_csv(repo_path("results/2026-10-17_at_test/site_year.csv"))
    usable = sy.dropna(subset=["yas_site", SCORE])
    out = {
        "site_years_total": int(len(sy)),
        "site_years_with_yield_and_score": int(len(usable)),
        "sites": int(usable.site.nunique()),
        "years": int(usable.year.nunique()),
        "year_range": [int(usable.year.min()), int(usable.year.max())] if len(usable) else None,
        "by_land": usable.land.value_counts().to_dict(),
    }
    trials = repo_path("data/raw/at_trials.csv")
    if trials.exists():
        t = pd.read_csv(trials, usecols=["site", "lat", "lon", "loc_precision", "year"])
        out["trial_rows"] = int(len(t))
        out["trial_sites"] = int(t.site.nunique())
        out["trial_rows_with_coordinates"] = int(t[["lat", "lon"]].notna().all(axis=1).sum())
        out["trial_loc_precision"] = t.loc_precision.fillna("none").value_counts().to_dict()
    return out


def loyo(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y in sorted(d.year.unique()):
        tr, te = d[d.year != y], d[d.year == y]
        b1, b0 = np.polyfit(tr[SCORE], tr.yas_site, 1)
        for _, r in te.iterrows():
            rows.append({"site": r.site, "year": int(r.year), "yas": r.yas_site, "score": r[SCORE],
                         "pred": b0 + b1 * r[SCORE], "train_mean": tr.yas_site.mean()})
    return pd.DataFrame(rows)


def metrics(p: pd.DataFrame) -> dict:
    def rmse(a, b):
        return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))

    def stats(q: pd.DataFrame) -> dict:
        return {"rho": float(spearmanr(q.pred, q.yas).statistic), "rmse_model": rmse(q.pred, q.yas),
                "rmse_normal": rmse(np.ones(len(q)), q.yas), "rmse_train_mean": rmse(q.train_mean, q.yas)}

    point = stats(p)
    rng = np.random.default_rng(SEED)
    years = p.year.unique()
    boot = []
    for _ in range(N_BOOT):
        pick = pd.concat([p[p.year == y] for y in rng.choice(years, size=len(years), replace=True)])
        if pick.pred.nunique() > 1 and pick.yas.nunique() > 1:
            s = stats(pick)
            boot.append([s["rho"], s["rmse_model"] - s["rmse_normal"], s["rmse_model"] - s["rmse_train_mean"]])
    b = np.array(boot)
    q = lambda col: [float(np.quantile(b[:, col], 0.025)), float(np.quantile(b[:, col], 0.975))]  # noqa: E731
    return point | {"rho_ci": q(0), "rmse_diff_vs_normal": point["rmse_model"] - point["rmse_normal"], "rmse_diff_vs_normal_ci": q(1),
                    "rmse_diff_vs_train_mean": point["rmse_model"] - point["rmse_train_mean"], "rmse_diff_vs_train_mean_ci": q(2),
                    "n": int(len(p)), "n_years": int(len(years))}


def main() -> None:
    c = counts()
    run = c["site_years_with_yield_and_score"] >= MIN_SITE_YEARS and c["years"] >= MIN_YEARS and c["sites"] >= MIN_SITES
    res = {"date": date.today().isoformat(), "decision": "DECISIONS.md 2026-10-17 AT-Machbarkeitstest",
           "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "criteria": {"min_site_years": MIN_SITE_YEARS, "min_years": MIN_YEARS, "min_sites": MIN_SITES},
           "counts": c, "run": bool(run), "model": "linear regression YAS_site ~ stress score (1 Sep), leave-one-year-out"}
    out = repo_path("results") / f"{date.today().isoformat()}_at_feasibility"
    out.mkdir(parents=True, exist_ok=True)
    if run:
        sy = pd.read_csv(repo_path("results/2026-10-17_at_test/site_year.csv")).dropna(subset=["yas_site", SCORE]).reset_index(drop=True)
        p = loyo(sy)
        p.to_csv(out / "predictions.csv", index=False)
        res["metrics"] = metrics(p)
    (out / "metrics.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
