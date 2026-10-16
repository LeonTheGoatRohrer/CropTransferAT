"""Phase 2: model family x cutoffs x satellite basis, nested LOFYO on in-fold RY (PLAN.md Phase 2).

Writes results/<date>_phase2/: oof.parquet (out-of-fold predictions), metrics.csv, config, git hash.
Usage:  python -m croptransfer.run_phase2 [--quick] [--jobs 14]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from croptransfer import evaluate, features, splits, targets
from croptransfer.config import load_config, repo_path
from croptransfer.models import family

TARGET = "RY"


def load_features(cfg, mmdd: str) -> pd.DataFrame:
    df = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / f"features_{mmdd.replace('-', '')}.parquet")
    return df.reset_index(drop=True)


def columns_for(code: str, basis: str, groups: dict[str, list[str]]) -> list[str]:
    s = groups["S_hls" if basis == "HLS" else "S_s2"]
    out = []
    for g in family.FAMILY[code]:
        if g == "B1":
            out.append(f"ndvi_{basis.lower()}_max")
        elif g == "S":
            out += s
        else:
            out += groups[g]
    return out


def pool_mask(df: pd.DataFrame, code: str, basis: str, variant: str) -> pd.Series:
    """Rows a model may be trained on (DECISIONS 2026-10-16)."""
    m = df.sensor_era == "HLS"
    if basis == "S2" and code not in family.NO_SATELLITE:
        m &= df.year >= 2017
    if variant == "W-lang" and code in family.NO_SATELLITE:
        m |= (df.dataset == "KBS") & (df.sensor_era == "L57")
    return m


def eval_mask(df: pd.DataFrame, basis: str) -> pd.Series:
    m = (df.sensor_era == "HLS") & df.RY_descr.notna()
    return m & (df.year >= 2017) if basis == "S2" else m


def fit_predict(df, cols, kind, fit_idx, y_fit, pred_idx, seed, shuffle_rng=None, grid=None):
    """Nested tuning (leave-one-year-out inside fit_idx) then fit + predict."""
    X = df[cols]
    use = family.usable_columns(X.loc[fit_idx])
    if not use:
        return np.full(len(pred_idx), float(np.mean(y_fit))), None
    best, best_rmse = None, np.inf
    grid = grid or family.grid(kind)
    if len(grid) > 1:
        for params in grid:
            errs = []
            for a, b in splits.inner_year_folds(df, fit_idx):
                ya, yb = targets.ry_in_fold(df, a, b)
                ya, yb = ya.dropna(), yb.dropna()
                if len(ya) < 10 or len(yb) == 0:
                    continue
                if shuffle_rng is not None:
                    ya = pd.Series(shuffle_rng.permutation(ya.to_numpy()), index=ya.index)
                mdl = family.make(kind, params, seed).fit(X.loc[ya.index, use], ya.to_numpy())
                errs.append((yb.to_numpy() - mdl.predict(X.loc[yb.index, use])) ** 2)
            if errs:
                r = float(np.sqrt(np.concatenate(errs).mean()))
                if r < best_rmse:
                    best, best_rmse = params, r
    best = best or grid[0]
    mdl = family.make(kind, best, seed).fit(X.loc[fit_idx, use], y_fit)
    return mdl.predict(X.loc[pred_idx, use]), best


def run_task(df: pd.DataFrame, groups, code: str, kind: str, basis: str, mmdd: str, variant: str,
             seed: int, folds_name: str = "LOFYO", shuffle: bool = False, folds=None,
             cols: list[str] | None = None, grid: list[dict] | None = None) -> pd.DataFrame:
    em = eval_mask(df, basis)
    folds = folds or splits.lofyo(df, em)
    pool = pool_mask(df, code, basis, variant)
    cols = cols or columns_for(code, basis, groups)
    rng = np.random.default_rng(seed) if shuffle else None
    out = []
    for name, tr, te in folds:
        ry_tr, ry_te = targets.ry_in_fold(df, tr, te)
        fit_idx = ry_tr.index[ry_tr.notna() & pool.loc[ry_tr.index]]
        te = ry_te.index[ry_te.notna()]
        if len(fit_idx) < 10 or len(te) == 0:
            continue
        y_fit = ry_tr.loc[fit_idx].to_numpy()
        if shuffle:
            y_fit = rng.permutation(y_fit)
        pred, params = fit_predict(df, cols, kind, fit_idx, y_fit, te, seed, rng, grid)
        out.append(pd.DataFrame({"fy_key": df.loc[te, "fy_key"].to_numpy(), "dataset": df.loc[te, "dataset"].to_numpy(),
                                 "year": df.loc[te, "year"].to_numpy(), "y": ry_te.loc[te].to_numpy(),
                                 "pred": pred, "fold": name, "params": json.dumps(params)}))
    res = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    res["model"], res["kind"], res["basis"], res["cutoff"], res["variant"] = code, kind, basis, mmdd, variant
    res["split"], res["shuffle"] = folds_name, shuffle
    return res


def metrics(oof: pd.DataFrame, b1: pd.DataFrame | None, cfg) -> dict:
    n_boot, seed = cfg["validation"]["bootstrap_n"], cfg["seed"]
    cl = oof.dataset + "-" + oof.year.astype(str)
    rho, lo, hi = evaluate.spearman_ci(oof.pred, oof.y, cl, n_boot, seed)
    wy = evaluate.within_year_rhos(oof, "pred", "y")
    r_b0 = evaluate.rmse(oof.y, np.ones(len(oof)))
    d0, d0lo, d0hi = evaluate.rmse_diff_ci(oof.y, oof.pred, np.ones(len(oof)), cl, n_boot, seed)
    m = dict(n=len(oof), clusters=int(cl.nunique()), rho=rho, rho_lo=lo, rho_hi=hi,
             median_within_year_rho=float(wy.median()) if len(wy) else np.nan, n_within_years=int(len(wy)),
             rmse=evaluate.rmse(oof.y, oof.pred), r2=evaluate.r2(oof.y, oof.pred),
             skill_b0=1 - evaluate.rmse(oof.y, oof.pred) / r_b0,
             d_rmse_b0=d0, d_rmse_b0_lo=d0lo, d_rmse_b0_hi=d0hi)
    if b1 is not None and len(b1):
        j = oof.merge(b1[["fy_key", "pred"]].rename(columns={"pred": "p_b1"}), on="fy_key")
        cl1 = j.dataset + "-" + j.year.astype(str)
        d1, d1lo, d1hi = evaluate.rmse_diff_ci(j.y, j.pred, j.p_b1, cl1, n_boot, seed)
        m.update(d_rmse_b1=d1, d_rmse_b1_lo=d1lo, d_rmse_b1_hi=d1hi)
    return m


def tasks_for(cutoffs, bases=("HLS", "S2")):
    t = []
    for mmdd in cutoffs:
        for basis in bases:
            for code in family.FAMILY:
                if code in family.NO_SATELLITE and basis == "S2":
                    continue  # identical to the HLS-basis run on its own rows; evaluated separately below
                kinds = ["ridge"] if code == "B1" else ["ridge", "lgbm"]
                variants = ["main", "W-lang"] if code in family.NO_SATELLITE else ["main"]
                for kind in kinds:
                    for v in variants:
                        t.append((code, kind, basis, mmdd, v))
    return t


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="only cutoff 09-01")
    ap.add_argument("--jobs", type=int, default=14)
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    cutoffs = ["09-01"] if args.quick else cfg["cutoffs"]["yield_model"]
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_phase2"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    data = {m: load_features(cfg, m) for m in cutoffs}
    groups = features.feature_groups(data[cutoffs[0]].columns)
    tasks = tasks_for(cutoffs)
    print(f"{len(tasks)} tasks", flush=True)
    res = Parallel(n_jobs=args.jobs, verbose=5)(
        delayed(run_task)(data[t[3]], groups, *t, seed) for t in tasks)
    oof = pd.concat(res, ignore_index=True)
    # no-satellite models evaluated on the S2 evaluation rows as well (same predictions)
    s2keys = set(data[cutoffs[0]].loc[eval_mask(data[cutoffs[0]], "S2"), "fy_key"])
    ns = oof[oof.model.isin(family.NO_SATELLITE) & oof.fy_key.isin(s2keys)].assign(basis="S2")
    oof = pd.concat([oof, ns], ignore_index=True)
    oof.to_parquet(run / "oof.parquet")
    rows = []
    for (code, kind, basis, mmdd, v), g in oof.groupby(["model", "kind", "basis", "cutoff", "variant"]):
        b1 = oof[(oof.model == "B1") & (oof.basis == basis) & (oof.cutoff == mmdd)]
        rows.append(dict(model=code, kind=kind, basis=basis, cutoff=mmdd, variant=v, **metrics(g, b1, cfg)))
    met = pd.DataFrame(rows)
    met.to_csv(run / "metrics.csv", index=False)
    show = met[met.cutoff == "09-01"].sort_values("median_within_year_rho", ascending=False)
    print(show[["model", "kind", "basis", "variant", "n", "rho", "rho_lo", "rho_hi",
                "median_within_year_rho", "rmse", "skill_b0"]].round(3).to_string())


if __name__ == "__main__":
    main()
