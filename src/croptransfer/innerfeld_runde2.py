"""Round 2 of the within-field study: smoothing of the prediction and cleaning of the Kayad yield points
(pre-registered in reports/innerfeld_vorab_runde2.md). One computation, no parameter search.

Usage:  python -m croptransfer.innerfeld_runde2 [--out results/<dir>]
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path
from croptransfer.innerfeld import KAYAD_CAP_KG_HA, KAYAD_MIN_POINTS, add_relative_yield, aggregate_points, load_kayad_points
from croptransfer.innerfeld_ceiling import block_means, pass_ids
from croptransfer.innerfeld_run import (INTERIOR_M, M1_COLS, MIN_CELLS, PROBLEM, SEED, SPACE_COLS, _z, folds_by_group,
                                        git_info, main_rows, paired_delta, per_fy_table, prepare, run_folds, spearman,
                                        summarize)

LOW_YIELD_T_HA = 3.0
DROP_FIRST = 8
DROP_LAST = 3
SMOOTH_RADIUS = {"S0": 0, "S1": 1, "S2": 2}      # 1 -> 3x3 (30 m), 2 -> 5x5 (50 m)
MIN_VALID_WINDOW = 3
GATE_DELTA = 0.02
SITES = ("BARC", "KAYAD")


# ----------------------------------------------------------------------------------------------
# pure functions (unit-tested)
# ----------------------------------------------------------------------------------------------
def smooth_grid(x: np.ndarray, y: np.ndarray, v: np.ndarray, radius: int, step: float = 10.0,
                min_valid: int = MIN_VALID_WINDOW) -> np.ndarray:
    """Mean over the (2r+1)^2 window of grid cells, own cell included. radius 0 returns v unchanged.

    Missing cells (not in the table or NaN) do not count; windows with fewer than `min_valid` valid cells keep the
    cell's own value (NaN stays NaN).
    """
    v = np.asarray(v, dtype=float)
    if radius == 0:
        return v.copy()
    ix, iy = np.floor(np.asarray(x) / step).astype(int), np.floor(np.asarray(y) / step).astype(int)
    val = {(a, b): c for a, b, c in zip(ix, iy, v) if np.isfinite(c)}
    out = v.copy()
    for k, (a, b) in enumerate(zip(ix, iy)):
        vals = [val[(a + da, b + db)] for da in range(-radius, radius + 1) for db in range(-radius, radius + 1)
                if (a + da, b + db) in val]
        if len(vals) >= min_valid:
            out[k] = float(np.mean(vals))
    return out


def clean_kayad_points(pts: pd.DataFrame, low: float = LOW_YIELD_T_HA, first: int = DROP_FIRST,
                       last: int = DROP_LAST) -> pd.DataFrame:
    """P1: drop points under `low` t/ha and the first/last points of every pass (one year per call)."""
    p = pts.sort_values("number", kind="stable").reset_index(drop=True)
    p["pass_id"] = pass_ids(p)
    p["pos"] = p.groupby("pass_id").cumcount()
    p["n_in_pass"] = p.groupby("pass_id").pass_id.transform("size")
    keep = (p.pos >= first) & (p.pos < p.n_in_pass - last) & (p.yield_t_ha >= low)
    return p[keep].drop(columns=["pass_id", "pos", "n_in_pass"]).reset_index(drop=True)


# ----------------------------------------------------------------------------------------------
def kayad_p1(df: pd.DataFrame) -> pd.DataFrame:
    """Kayad rows of the feature table with labels recomputed from the cleaned points (P1)."""
    raw = load_kayad_points(repo_path("data/raw/kayad"))
    parts = []
    for yr, g in raw.groupby("year"):
        c = clean_kayad_points(g)
        c["site"], c["field_id"], c["year"] = "KAYAD", "KAYAD_1", int(yr)
        parts.append(c)
    pts = pd.concat(parts, ignore_index=True)
    cells = aggregate_points(pts, ["site", "field_id", "year"], min_points=KAYAD_MIN_POINTS,
                             cap=KAYAD_CAP_KG_HA / 1000.0)
    cells["fy_key"] = "KAYAD|KAYAD_1|" + cells.year.astype(str)
    cells = add_relative_yield(cells)
    k = df[df.site == "KAYAD"].drop(columns=["rel", "yield_t_ha", "n_points", "frac_cap", "moisture_pct", "problem", "zrel"])
    m = k.merge(cells[["fy_key", "x", "y", "yield_t_ha", "rel", "n_points", "frac_cap", "moisture_pct"]],
                on=["fy_key", "x", "y"], how="inner")
    m["problem"] = m.rel < PROBLEM
    m["zrel"] = m.groupby("fy_key").rel.transform(_z)
    return m.reset_index(drop=True)


def predictions(s: pd.DataFrame, group_col: str) -> dict[str, pd.Series]:
    folds = folds_by_group(s, s[group_col])
    return {"B0": s.z_b0.copy(), "M1": run_folds(s, folds, M1_COLS), "KRAUM": run_folds(s, folds, SPACE_COLS)}


def smoothed(s: pd.DataFrame, pred: pd.Series, radius: int) -> pd.Series:
    out = pd.Series(np.nan, index=s.index)
    for _, g in s.groupby("fy_key"):
        out.loc[g.index] = smooth_grid(g.x.to_numpy(), g.y.to_numpy(), pred.loc[g.index].to_numpy(), radius)
    return out


def block_rho(s: pd.DataFrame, pred: pd.Series, size_m: float = 30.0) -> float:
    rhos = []
    for _, g in s.groupby("fy_key"):
        ok = pred.loc[g.index].notna() & g.rel.notna()
        b = block_means(g.x[ok].to_numpy(), g.y[ok].to_numpy(), size_m,
                        dict(pred=pred.loc[g.index][ok].to_numpy(), rel=g.rel[ok].to_numpy()))
        if len(b) >= MIN_CELLS:
            rhos.append(spearman(b.pred.to_numpy(), b.rel.to_numpy()))
    return float(np.median(rhos)) if rhos else float("nan")


def evaluate_set(s: pd.DataFrame, group_col: str, eval_mask: pd.Series | None = None) -> tuple[dict, pd.DataFrame]:
    """All variants S0/S1/S2 x {B0, M1, KRAUM, random} on one set of cells; returns summaries and per-FY table."""
    s = s.reset_index(drop=True)
    mask = pd.Series(True, index=s.index) if eval_mask is None else eval_mask.reset_index(drop=True)
    preds = predictions(s, group_col)
    rng = np.random.default_rng(SEED)
    preds["ZUFALL"] = pd.Series(rng.normal(size=len(s)), index=s.index)
    res: dict[str, Any] = {}
    tabs = []
    for name, p in preds.items():
        for sm, r in SMOOTH_RADIUS.items():
            ps = smoothed(s, p, r)
            t = per_fy_table(s[mask], ps[mask], name, sm)
            tabs.append(t)
            res.setdefault(name, {})[sm] = summarize(t, "cluster") | dict(block30_rho_median=block_rho(s[mask], ps[mask]))
    tab = pd.concat(tabs, ignore_index=True)
    gates: dict[str, Any] = {}
    for name in ("B0", "M1", "KRAUM"):
        base = tab[(tab.model == name) & (tab.scheme == "S0")]
        for sm in ("S1", "S2"):
            gates[f"{name}_{sm}_minus_S0"] = paired_delta(tab[(tab.model == name) & (tab.scheme == sm)], base)
    return dict(summary=res, deltas=gates), tab


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_config()
    run = repo_path(args.out) if args.out else repo_path(cfg["paths"]["results"]) / f"{date.today()}_innerfeld_runde2"
    run.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo_path("config.yaml"), run / "config.yaml")
    (run / "git.txt").write_text(git_info())

    df = main_rows(prepare(cfg)).reset_index(drop=True)
    barc = df[df.site == "BARC"]
    kay0 = df[df.site == "KAYAD"]
    kay1 = kayad_p1(df)
    out: dict[str, Any] = dict(date=str(date.today()), seed=SEED, gate_delta=GATE_DELTA,
                               n_cells=dict(BARC=int(len(barc)), KAYAD_P0=int(len(kay0)), KAYAD_P1=int(len(kay1))))
    tabs = []
    for label, s, grp in (("BARC_P0", barc, "field_cluster"), ("KAYAD_P0", kay0, "year"), ("KAYAD_P1", kay1, "year")):
        r, t = evaluate_set(s, grp)
        out[label] = r
        tabs.append(t.assign(set=label))
        # control: interior cells only (smoothing is computed on all cells, evaluation on interior cells)
        inner = (s.dist_edge_m >= INTERIOR_M)
        r2, _ = evaluate_set(s, grp, eval_mask=inner.reset_index(drop=True))
        out[f"{label}_interior"] = r2

    def gate(site_set: str, need_ci: bool) -> dict[str, Any]:
        d = out[site_set]["deltas"]
        res: dict[str, Any] = {}
        for m in ("B0", "M1"):
            x = d[f"{m}_S1_minus_S0"]
            ok = x.get("delta_median", np.nan) >= GATE_DELTA
            if need_ci:
                ok = ok and x.get("delta_ci", [np.nan])[0] > 0
            res[m] = dict(delta=x.get("delta_median"), ci=x.get("delta_ci"), passed=bool(ok))
        return res

    g_barc = gate("BARC_P0", True)
    k_tab = pd.concat(tabs, ignore_index=True)
    g_kay = gate("KAYAD_P0", False)
    kt = k_tab[(k_tab.set == "KAYAD_P0")]
    for m in ("B0", "M1"):
        a = kt[(kt.model == m) & (kt.scheme == "S1")].set_index("fy_key").rho
        b = kt[(kt.model == m) & (kt.scheme == "S0")].set_index("fy_key").rho
        g_kay[m]["all_years_positive"] = bool(((a - b) > 0).all())
        g_kay[m]["passed"] = bool(g_kay[m]["passed"] and g_kay[m]["all_years_positive"])
    out["gates"] = dict(R2_BARC=g_barc, R2_KAYAD=g_kay,
                        glaettung_hilft=bool(all(v["passed"] for v in g_barc.values())
                                             and all(v["passed"] for v in g_kay.values())))
    pd.concat(tabs, ignore_index=True).to_csv(run / "per_fy.csv", index=False)
    (run / "metrics.json").write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"written {run}")


if __name__ == "__main__":
    main()
