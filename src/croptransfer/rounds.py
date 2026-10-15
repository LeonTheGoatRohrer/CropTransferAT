"""Phase-4 improvement rounds 1-3 (pre-registered in DECISIONS.md 2026-10-16).

Round 1  relative satellite features (site other-years anomaly + same-year other-fields anomaly)
Round 2  simpler: 8 relative EVI/NDMI features + 4 weather features
Round 3  round-1 features with stronger regularisation (Ridge alpha 30-3000, LightGBM stumps)

Every round: all cutoffs, LOFYO, same metrics and selection rule; the selected model of the
round is checked against the four "stark genug" criteria. Rounds run sequentially; the first
round whose selected model passes is the freeze candidate.

Usage:  python -m croptransfer.rounds --round 1 [--jobs 15]
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

from croptransfer import evaluate, features, targets
from croptransfer.config import load_config, repo_path
from croptransfer.phase2_extras import SIMPLE_BASIS, SIMPLE_KIND, cross_conformal
from croptransfer.run_phase2 import eval_mask, fit_predict, load_features, metrics, pool_mask, run_task

REL_INDICES = ["ndvi", "evi", "ndmi"]
REL_STATS = ["max", "auc", "mean_jun", "last"]
R2_INDICES, R2_STATS = ["evi", "ndmi"], ["auc", "max"]
R2_WEATHER = ["cwb", "gdd", "heat32_flower", "rzwsi_flower"]
R3_RIDGE = [{"alpha": a} for a in (30.0, 100.0, 300.0, 1000.0, 3000.0)]
R3_LGBM = [dict(max_depth=1, num_leaves=2, n_estimators=n, learning_rate=0.05, min_child_samples=15)
           for n in (100, 200, 300)]


def add_relative(df: pd.DataFrame, basis: str, indices=REL_INDICES, stats=REL_STATS,
                 site: str = "dataset", min_fields: int = 3) -> tuple[pd.DataFrame, list[str]]:
    """Anomalies of curve statistics (same cutoff):
    _relyr  value - median of the same site in the OTHER years
    _relfld value - median of the OTHER fields of the same site-year (>= min_fields).
    Only HLS-era rows enter (pre-2013 Landsat curves are excluded, DECISIONS 2026-10-16)."""
    d = df.copy()
    new = []
    b = basis.lower()
    for idx in indices:
        for st in stats:
            c = f"{idx}_{b}_{st}"
            if c not in d:
                continue
            ry, rf = np.full(len(d), np.nan), np.full(len(d), np.nan)
            vals = d[c].to_numpy(dtype=float).copy()
            vals[d["sensor_era"].to_numpy() != "HLS"] = np.nan   # no Landsat-era curves (harmonisation failed)
            for i, (s, y) in enumerate(zip(d[site], d["year"])):
                if np.isnan(vals[i]):
                    continue
                other_years = vals[(d[site].to_numpy() == s) & (d["year"].to_numpy() != y) & ~np.isnan(vals)]
                if len(other_years):
                    ry[i] = vals[i] - np.median(other_years)
                same = (d[site].to_numpy() == s) & (d["year"].to_numpy() == y) & ~np.isnan(vals)
                same[i] = False
                if same.sum() >= min_fields:
                    rf[i] = vals[i] - np.median(vals[same])
            d[f"{c}_relyr"], d[f"{c}_relfld"] = ry, rf
            new += [f"{c}_relyr", f"{c}_relfld"]
    return d, new


def round_specs(rnd: int, df: pd.DataFrame, groups, basis: str):
    """[(code, kind, cols, grid)] of one round for one basis."""
    if rnd in (1, 3):
        df2, rel = add_relative(df, basis)
        sets = {"M-Srel": rel, "M-alle-rel": rel + groups["W"] + groups["B"]}
    else:
        df2, rel = add_relative(df, basis, R2_INDICES, R2_STATS)
        sets = {"M-Srel-einfach": rel, "M-Srel-einfach+W4": rel + R2_WEATHER}
    grids = {"ridge": R3_RIDGE, "lgbm": R3_LGBM} if rnd == 3 else {"ridge": None, "lgbm": None}
    specs = [(code, kind, cols, grids[kind]) for code, cols in sets.items() for kind in ("ridge", "lgbm")]
    return df2, specs


def _task(df, code, kind, cols, grid, basis, mmdd, seed, shuffle=False):
    # pool: satellite rows of the basis (relative features always need satellite data)
    r = run_task(df, None, "M-alle", kind, basis, mmdd, "main", seed, shuffle=shuffle, cols=cols, grid=grid)
    r["model"] = code
    return r


def lodo(df, kind, cols, grid, basis, a, b, seed):
    em = eval_mask(df, basis)
    pool = pool_mask(df, "M-alle", basis, "main")
    tr = df.index[df.dataset == a]
    te = df.index[(df.dataset == b) & em]
    ry_tr = targets.compute_ry(df.loc[tr], df.loc[tr], df.loc[tr])
    fit_idx = ry_tr.index[ry_tr.notna() & pool.loc[ry_tr.index]]
    y_te = targets.ry_descriptive(df).loc[te].dropna()
    pred, _ = fit_predict(df, cols, kind, fit_idx, ry_tr.loc[fit_idx].to_numpy(), y_te.index, seed, None, grid)
    return pd.DataFrame({"dataset": b, "year": df.loc[y_te.index, "year"].to_numpy(), "y": y_te.to_numpy(), "pred": pred})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--round", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--jobs", type=int, default=15)
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    rnd = args.round
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_round{rnd}"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    cutoffs = cfg["cutoffs"]["yield_model"]
    jobs, prepared = [], {}
    for mmdd in cutoffs:
        base = load_features(cfg, mmdd)
        groups = features.feature_groups(base.columns)
        for basis in ("HLS", "S2"):
            df2, specs = round_specs(rnd, base, groups, basis)
            prepared[(mmdd, basis)] = (df2, specs)
            for code, kind, cols, grid in specs:
                jobs.append((df2, code, kind, cols, grid, basis, mmdd))
    res = Parallel(n_jobs=args.jobs, verbose=2)(delayed(_task)(*j, seed) for j in jobs)
    oof = pd.concat(res, ignore_index=True)
    oof["variant"] = f"round{rnd}"
    oof.to_parquet(run / "oof.parquet")
    # B1 of the same basis/cutoff from the main Phase-2 run (for criterion 1)
    p2 = sorted(repo_path(cfg["paths"]["results"]).glob("*_phase2"))[-1]
    p2oof = pd.read_parquet(p2 / "oof.parquet")
    rows = []
    for (code, kind, basis, mmdd), g in oof.groupby(["model", "kind", "basis", "cutoff"]):
        b1 = p2oof[(p2oof.model == "B1") & (p2oof.basis == basis) & (p2oof.cutoff == mmdd)]
        rows.append(dict(model=code, kind=kind, basis=basis, cutoff=mmdd, **metrics(g, b1, cfg)))
    met = pd.DataFrame(rows)
    met.to_csv(run / "metrics.csv", index=False)
    # selection rule (same as Phase 4)
    c = met[met.cutoff == "09-01"].copy()
    best = c.median_within_year_rho.max()
    near = c[c.median_within_year_rho >= best - 0.05].copy()
    near["simp"] = list(zip(near.kind.map(SIMPLE_KIND), near.model.map(lambda m: 0 if "alle" not in m and "+W" not in m else 1),
                            near.basis.map(SIMPLE_BASIS), -near.median_within_year_rho))
    sel = near.sort_values("simp").iloc[0]
    df2, specs = prepared[("09-01", sel.basis)]
    _, kind, cols, grid = next(s for s in specs if s[0] == sel.model and s[1] == sel.kind)
    m = met[(met.model == sel.model) & (met.kind == sel.kind) & (met.basis == sel.basis)]
    late = m[m.cutoff.isin(["08-01", "08-15", "09-01"])]
    c1 = bool(((late.d_rmse_b0_hi < 0) & (late.d_rmse_b1_hi < 0)).any())
    c2 = bool(sel.rho >= 0.4)
    lo = {}
    for a, b in [("KBS", "BARC"), ("BARC", "KBS")]:
        o = lodo(df2, kind, cols, grid, sel.basis, a, b, seed)
        r, l, h = evaluate.spearman_ci(o.pred, o.y, o.dataset + o.year.astype(str), cfg["validation"]["bootstrap_n"], seed)
        lo[f"{a}->{b}"] = {"n": len(o), "rho": r, "lo": l, "hi": h}
    c3 = all(v["rho"] > 0 for v in lo.values())
    sh = _task(df2, sel.model, kind, cols, grid, sel.basis, "09-01", seed, shuffle=True)
    shm = metrics(sh, None, cfg)
    c4 = bool(shm["rho_lo"] <= 0 <= shm["rho_hi"] and not shm["d_rmse_b0_hi"] < 0)
    so = oof[(oof.model == sel.model) & (oof.kind == sel.kind) & (oof.basis == sel.basis) & (oof.cutoff == "09-01")]
    out = {"round": rnd, "selected": sel.drop(labels=["simp"]).to_dict(),
           "criteria": {"1": {"passed": c1, "rows": late[["cutoff", "d_rmse_b0", "d_rmse_b0_lo", "d_rmse_b0_hi", "d_rmse_b1",
                                                         "d_rmse_b1_lo", "d_rmse_b1_hi"]].round(4).to_dict("records")},
                        "2": {"passed": c2, "rho": sel.rho, "lo": sel.rho_lo, "hi": sel.rho_hi, "n": int(sel.n)},
                        "3": {"passed": c3, **lo},
                        "4": {"passed": c4, "rho": shm["rho"], "lo": shm["rho_lo"], "hi": shm["rho_hi"]}},
           "strong_enough": bool(c1 and c2 and c3 and c4),
           "conformal_80": cross_conformal(so, 0.2)}
    (run / "criteria.json").write_text(json.dumps(out, indent=2, default=float))
    print(met[met.cutoff == "09-01"].sort_values("median_within_year_rho", ascending=False)[
        ["model", "kind", "basis", "n", "rho", "rho_lo", "rho_hi", "median_within_year_rho", "rmse", "skill_b0"]].round(3).to_string())
    print(json.dumps({k: out[k] for k in ["selected", "criteria", "strong_enough"]}, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
