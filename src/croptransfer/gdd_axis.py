"""Phase 2.4: calendar axis vs. thermal-time (GDD) axis for satellite features (US only, analysis).

GDD-axis features: index value at fixed GDD sums since 1.4. (linear interpolation between clear
observations dated <= cutoff; NaN if the GDD sum is not reached by the cutoff or not bracketed by
observations), plus the maximum. Compared with the calendar features (M-S) via LODO both
directions and LOFYO at 1.9.
Usage:  python -m croptransfer.gdd_axis
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date

import numpy as np
import pandas as pd

from croptransfer import evaluate, features, splits, targets
from croptransfer.config import load_config, repo_path
from croptransfer.dataset_us import basis_obs, load_obs, weather_by_fy
from croptransfer.extract_us import load_field_years
from croptransfer.phase2_extras import lodo_eval
from croptransfer.run_phase2 import columns_for, eval_mask, fit_predict, load_features, metrics, run_task

GDD_POINTS = [300, 600, 900, 1200, 1500]
INDICES = ["ndvi", "evi", "ndmi"]


def gdd_features(obs: pd.DataFrame, daily: pd.DataFrame, cutoff: date, suffix: str) -> dict:
    """Index values at GDD_POINTS on the thermal-time axis (as-of cutoff)."""
    d = daily[(daily.date >= pd.Timestamp(f"{cutoff.year}-04-01")) & (daily.date <= pd.Timestamp(cutoff))]
    if d.empty or obs is None or obs.empty:
        return {}
    cum = pd.Series(d.gdd.cumsum().to_numpy(), index=d.date.dt.normalize())
    o = obs[pd.to_datetime(obs["date"]).dt.date <= cutoff].copy()
    if len(o) < 2:
        return {}
    o["g"] = pd.to_datetime(o["date"]).dt.normalize().map(cum)
    o = o.dropna(subset=["g"]).sort_values("g")
    out = {}
    for idx in INDICES:
        v = o.groupby("g")[idx].median()
        if len(v) < 2:
            continue
        for gp in GDD_POINTS:
            inside = v.index.min() <= gp <= v.index.max()
            out[f"{idx}_{suffix}_gdd{gp}"] = float(np.interp(gp, v.index, v.values)) if inside else np.nan
        out[f"{idx}_{suffix}_gddmax"] = float(v.max())
    return out


def main() -> None:
    cfg = load_config()
    seed = cfg["seed"]
    run = repo_path(cfg["paths"]["results"]) / f"{date.today().isoformat()}_gdd_axis"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
    fy = load_field_years(cfg)
    by_key = basis_obs(load_obs(cfg), fy)
    wx = weather_by_fy(cfg, fy)
    rows = []
    for r in fy.itertuples():
        f = {"fy_key": r.fy_key}
        cut = date(int(r.year), 9, 1)
        for basis in ("HLS", "S2"):
            f.update(gdd_features(by_key.get(r.fy_key, {}).get(basis), wx.get(r.fy_key, pd.DataFrame()), cut, basis.lower()))
        rows.append(f)
    g = pd.DataFrame(rows)
    base = load_features(cfg, "09-01")
    groups = features.feature_groups(base.columns)   # before the merge: GDD columns must not enter "S"
    df = base.merge(g, on="fy_key", how="left")
    out = {}
    for basis in ("HLS", "S2"):
        cal = columns_for("M-S", basis, groups)
        gdd = [c for c in g.columns if c.startswith(tuple(f"{i}_{basis.lower()}_gdd" for i in INDICES))]
        for axis, cols in [("Kalender", cal), ("GDD", gdd)]:
            for kind in ("ridge", "lgbm"):
                key = f"{basis}-{axis}-{kind}"
                lofyo = run_task(df, groups, "M-S", kind, basis, "09-01", "main", seed, cols=cols)
                m = metrics(lofyo, None, cfg)
                res = {"lofyo_rho": m["rho"], "lofyo_lo": m["rho_lo"], "lofyo_hi": m["rho_hi"], "n": m["n"],
                       "median_within_year_rho": m["median_within_year_rho"]}
                for a, b in [("KBS", "BARC"), ("BARC", "KBS")]:
                    o = _lodo(df, cols, kind, basis, a, b, seed)
                    rho, lo, hi = evaluate.spearman_ci(o.pred, o.y, o.dataset + o.year.astype(str),
                                                       cfg["validation"]["bootstrap_n"], seed)
                    res[f"{a}->{b}"] = {"rho": rho, "lo": lo, "hi": hi, "n": len(o)}
                res["lodo_mean_rho"] = float(np.mean([res["KBS->BARC"]["rho"], res["BARC->KBS"]["rho"]]))
                out[key] = res
                print(key, round(res["lofyo_rho"], 3), round(res["lodo_mean_rho"], 3), flush=True)
    (run / "metrics.json").write_text(json.dumps(out, indent=2, default=float))


def _lodo(df, cols, kind, basis, a, b, seed):
    em = eval_mask(df, basis)
    pool = (df.sensor_era == "HLS") & ((df.year >= 2017) if basis == "S2" else True)
    tr = df.index[df.dataset == a]
    te = df.index[(df.dataset == b) & em]
    ry_tr = targets.compute_ry(df.loc[tr], df.loc[tr], df.loc[tr])
    fit = ry_tr.index[ry_tr.notna() & pool.loc[ry_tr.index]]
    y_te = targets.ry_descriptive(df).loc[te].dropna()
    pred, _ = fit_predict(df, cols, kind, fit, ry_tr.loc[fit].to_numpy(), y_te.index, seed)
    return pd.DataFrame({"dataset": b, "year": df.loc[y_te.index, "year"].to_numpy(), "y": y_te.to_numpy(), "pred": pred})


if __name__ == "__main__":
    main()
