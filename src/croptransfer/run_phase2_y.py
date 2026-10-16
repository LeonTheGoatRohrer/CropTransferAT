"""Phase 2, secondary target: absolute yield Y (t/ha, 15.5 %) - where soil should matter (PLAN 2.2, M-B+).

Same LOFYO folds, nested tuning and feature groups as run_phase2; label = Y_t_ha (no normal needed).
Evaluation rows: all HLS-era field-years with yield (KBS, BARC, Colorado); S2 basis from 2017.
Usage:  python -m croptransfer.run_phase2_y [--jobs 15]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import date

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from croptransfer import evaluate, features, splits
from croptransfer.config import load_config, repo_path
from croptransfer.models import family
from croptransfer.run_phase2 import columns_for, fit_predict, load_features

MODELS = ["M-B", "M-B+", "M-S", "M-W", "M-WB", "M-alle"]


def run(df, groups, code, kind, basis, seed):
    em = (df.sensor_era == "HLS") & df.Y_t_ha.notna()
    if basis == "S2":
        em &= df.year >= 2017
    cols = columns_for(code, basis, groups)
    out = []
    for name, tr, te in splits.lofyo(df, em):
        fit = tr[em.loc[tr].to_numpy()]
        if len(fit) < 10:
            continue
        pred, _ = fit_predict(df, cols, kind, fit, df.loc[fit, "Y_t_ha"].to_numpy(), te, seed)
        out.append(pd.DataFrame({"dataset": df.loc[te, "dataset"].to_numpy(), "year": df.loc[te, "year"].to_numpy(),
                                 "y": df.loc[te, "Y_t_ha"].to_numpy(), "pred": pred}))
    o = pd.concat(out, ignore_index=True)
    o["model"], o["kind"], o["basis"] = code, kind, basis
    return o


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", type=int, default=15)
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    run_dir = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_phase2_Y"
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run_dir / "config.yaml")
    (run_dir / "git.txt").write_text(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    df = load_features(cfg, "09-01")
    groups = features.feature_groups(df.columns)
    tasks = [(c, k, b) for c in MODELS for k in ("ridge", "lgbm") for b in ("HLS", "S2")
             if not (b == "S2" and c in family.NO_SATELLITE)]
    res = Parallel(n_jobs=args.jobs)(delayed(run)(df, groups, *t, seed) for t in tasks)
    rows = []
    for o in res:
        cl = o.dataset + "-" + o.year.astype(str)
        rho, lo, hi = evaluate.spearman_ci(o.pred, o.y, cl, cfg["validation"]["bootstrap_n"], seed)
        base = np.full(len(o), o.y.mean())  # reference: overall mean (in-sample, generous to the baseline)
        within = evaluate.within_year_rhos(o, "pred", "y")
        rows.append(dict(model=o.model[0], kind=o.kind[0], basis=o.basis[0], n=len(o), clusters=int(cl.nunique()),
                         rho=rho, rho_lo=lo, rho_hi=hi, rmse=evaluate.rmse(o.y, o.pred), r2=evaluate.r2(o.y, o.pred),
                         rmse_mean=evaluate.rmse(o.y, base), median_within_year_rho=float(within.median())))
    met = pd.DataFrame(rows).sort_values("rho", ascending=False)
    met.to_csv(run_dir / "metrics.csv", index=False)
    print(met.round(3).to_string())


if __name__ == "__main__":
    main()
