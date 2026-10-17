"""Exploratory noise-ceiling analysis for the within-field map (reports/innerfeld_obergrenze.md).

Question: how high can the rank correlation between ANY satellite-based prediction and the measured relative yield
get, given that the measured map is itself noisy? No model is trained or tuned, no gate is attached, and no parameter
of the pre-registered round (reports/innerfeld_vorab.md) is changed. All numbers are descriptive.

Parts
  A  Reliability of the yield map (Kayad raw combine points, 1.5 m apart):
       - random split: points of a cell are split at random into two halves (optimistic, neighbours on the same pass);
       - pass split: points are cut into passes (a new pass starts when the next logged point is > 6 m away) and
         alternate passes form the two halves (pessimistic: two passes cover different strips of the cell).
     Per field-year rho(half A, half B), Spearman-Brown R = 2 r / (1 + r), noise ceiling for the correlation of a
     perfect predictor of the true cell yield with the measured one ~ sqrt(R) (approximation for rank correlation).
  B  Spatial benchmark (Kayad, BARC): rho between a cell's relative yield and the mean of its (up to 8) neighbours.
     BARC maps are kriged and therefore smooth by construction: the BARC benchmark is inflated.
  C  Scale curve: rho(prediction, measured) after averaging both over blocks of 10, 20, 30, 50, 100 m, for the
     untrained NDVI windows B0/B1 and the out-of-fold model M1 (BARC Leave-One-Field-Out, Kayad Leave-One-Year-Out).

Usage:  python -m croptransfer.innerfeld_ceiling [--out results/<dir>]
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path
from croptransfer.innerfeld import KAYAD_MIN_POINTS, cell_center, load_kayad_points
from croptransfer.innerfeld_run import (M1_COLS, MIN_CELLS, folds_by_group, main_rows, prepare, run_folds,
                                        spearman)

SEED = 42
PASS_GAP_M = 6.0
SCALES_M = [10, 20, 30, 50, 100]
MIN_HALF_POINTS = 3


# ----------------------------------------------------------------------------------------------
# pure functions (unit-tested)
# ----------------------------------------------------------------------------------------------
def spearman_brown(r: float) -> float:
    """Reliability of the full measurement from the correlation of two halves."""
    return 2 * r / (1 + r) if np.isfinite(r) and r > -1 else np.nan


def pass_ids(df: pd.DataFrame, gap_m: float = PASS_GAP_M) -> np.ndarray:
    """Pass number of every point of ONE year (rows sorted internally by `number`; returned in the input order)."""
    order = np.argsort(df.number.to_numpy(), kind="stable")
    x, y = df.x.to_numpy()[order], df.y.to_numpy()[order]
    step = np.r_[np.inf, np.hypot(np.diff(x), np.diff(y))]
    seg = np.cumsum(step > gap_m) - 1
    out = np.empty(len(df), dtype=int)
    out[order] = seg
    return out


def neighbour_mean(x: np.ndarray, y: np.ndarray, v: np.ndarray, step: float = 10.0, min_nb: int = 3) -> np.ndarray:
    """Mean of the up-to-8 neighbouring grid cells (queen); NaN with fewer than `min_nb` neighbours."""
    ix, iy = np.floor(np.asarray(x) / step).astype(int), np.floor(np.asarray(y) / step).astype(int)
    val = {(a, b): float(c) for a, b, c in zip(ix, iy, v)}
    out = np.full(len(v), np.nan)
    for k, (a, b) in enumerate(zip(ix, iy)):
        nb = [val[(a + da, b + db)] for da in (-1, 0, 1) for db in (-1, 0, 1)
              if (da or db) and (a + da, b + db) in val]
        if len(nb) >= min_nb:
            out[k] = np.mean(nb)
    return out


def block_means(x: np.ndarray, y: np.ndarray, size_m: float, cols: dict[str, np.ndarray]) -> pd.DataFrame:
    """Mean of each column over square blocks of `size_m` metres."""
    d = pd.DataFrame(cols)
    d["bx"], d["by"] = np.floor(np.asarray(x) / size_m).astype(int), np.floor(np.asarray(y) / size_m).astype(int)
    return d.groupby(["bx", "by"]).mean().reset_index()


# ----------------------------------------------------------------------------------------------
def kayad_reliability(seed: int = SEED) -> dict[str, Any]:
    pts = load_kayad_points(repo_path("data/raw/kayad"))
    rng = np.random.default_rng(seed)
    out: dict[str, Any] = {}
    for yr, g in pts.groupby("year"):
        g = g.reset_index(drop=True)
        g["cx"], g["cy"] = cell_center(g.x), cell_center(g.y)
        g["half_rand"] = rng.integers(0, 2, len(g))
        g["half_pass"] = pass_ids(g) % 2
        res: dict[str, Any] = {}
        for name in ("half_rand", "half_pass"):
            a = g[g[name] == 0].groupby(["cx", "cy"]).yield_t_ha.agg(["mean", "size"])
            b = g[g[name] == 1].groupby(["cx", "cy"]).yield_t_ha.agg(["mean", "size"])
            j = a.join(b, lsuffix="_a", rsuffix="_b", how="inner")
            j = j[(j.size_a >= MIN_HALF_POINTS) & (j.size_b >= MIN_HALF_POINTS)]
            mu = np.nanmean(np.r_[j.mean_a, j.mean_b])
            r = spearman((j.mean_a / mu).to_numpy(), (j.mean_b / mu).to_numpy())
            R = spearman_brown(r)
            res[name] = dict(n_cells=int(len(j)), rho_halves=float(r), reliability=float(R),
                             ceiling_rho=float(np.sqrt(R)) if np.isfinite(R) and R > 0 else None)
        res["n_points"] = int(len(g))
        res["n_passes"] = int(pass_ids(g).max() + 1)
        out[int(yr)] = res
    return out


def neighbour_benchmark(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for site in ("BARC", "KAYAD"):
        rhos = []
        for _, g in df[df.site == site].groupby("fy_key"):
            nb = neighbour_mean(g.x.to_numpy(), g.y.to_numpy(), g.rel.to_numpy())
            m = np.isfinite(nb)
            if m.sum() >= MIN_CELLS:
                rhos.append(spearman(nb[m], g.rel.to_numpy()[m]))
        out[site] = dict(n_fy=len(rhos), rho_median=float(np.median(rhos)), rho_min=float(np.min(rhos)),
                         rho_max=float(np.max(rhos)))
    return out


def scale_curve(df: pd.DataFrame) -> dict[str, Any]:
    """rho(prediction, measured) per field-year after block averaging; median over field-years with >= 10 blocks."""
    preds: dict[str, pd.Series] = {"B0": df.z_b0, "B1": df.z_b1_ndvi}
    for site, group in (("BARC", "field_cluster"), ("KAYAD", "year")):
        s = df[df.site == site]
        folds = folds_by_group(s.reset_index(drop=True), s[group].reset_index(drop=True))
        p = run_folds(s.reset_index(drop=True), folds, M1_COLS)
        preds.setdefault("M1", pd.Series(np.nan, index=df.index))
        preds["M1"].loc[s.index] = p.to_numpy()
    out: dict[str, Any] = {}
    for site in ("BARC", "KAYAD"):
        s = df[df.site == site]
        for name, p in preds.items():
            row: dict[str, Any] = {}
            for size in SCALES_M:
                rhos = []
                for _, g in s.groupby("fy_key"):
                    ok = p.loc[g.index].notna() & g.rel.notna()
                    b = block_means(g.x[ok].to_numpy(), g.y[ok].to_numpy(), size,
                                    dict(pred=p.loc[g.index][ok].to_numpy(), rel=g.rel[ok].to_numpy()))
                    if len(b) >= MIN_CELLS:
                        rhos.append(spearman(b.pred.to_numpy(), b.rel.to_numpy()))
                row[str(size)] = dict(n_fy=len(rhos), rho_median=float(np.median(rhos)) if rhos else None)
            out.setdefault(site, {})[name] = row
    return out


def figure(res: dict[str, Any], path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    col = {"B0": "#7a7a7a", "B1": "#2a6fb0", "M1": "#c4572a"}
    names = {"B0": "NDVI Kalenderfenster", "B1": "NDVI Spitzenfenster", "M1": "Modell M1"}
    for ax, site, title in zip(axes, ("BARC", "KAYAD"), ("BARC (41 Feld-Jahre, Karten interpoliert)", "Kayad (3 Feld-Jahre, Rohpunkte)")):
        for m, c in col.items():
            row = res["C_scale_curve"][site][m]
            xs = [s for s in SCALES_M if row[str(s)]["rho_median"] is not None]
            ax.plot(xs, [row[str(s)]["rho_median"] for s in xs], marker="o", color=c, label=names[m])
        ax.set_xscale("log")
        ax.set_xticks(SCALES_M, [str(s) for s in SCALES_M])
        ax.set_xlabel("Blockgröße, über die gemittelt wird (m)")
        ax.set_title(title, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    rel = res["A_kayad_reliability"]
    lo = np.mean([v["half_pass"]["ceiling_rho"] for v in rel.values()])
    hi = np.mean([v["half_rand"]["ceiling_rho"] for v in rel.values()])
    axes[1].axhspan(lo, hi, color="#2a9d4a", alpha=0.15)
    axes[1].text(10.5, (lo + hi) / 2, "Obergrenze der Ertragskarte,\n10-m-Zellen (Kayad)", fontsize=8, va="center")
    axes[0].set_ylabel("Median-ρ (Vorhersage vs. gemessener rel. Ertrag)")
    axes[0].set_ylim(0.4, 1.0)
    axes[0].legend(fontsize=8, loc="lower left")
    fig.suptitle("Wie weit ist die Satellitenkarte von der Obergrenze entfernt? (explorativ)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_config()
    run = repo_path(args.out) if args.out else repo_path(cfg["paths"]["results"]) / f"{date.today()}_innerfeld_ceiling"
    run.mkdir(parents=True, exist_ok=True)
    df = main_rows(prepare(cfg)).reset_index(drop=True)
    res = dict(date=str(date.today()), note="explorativ, deskriptiv, ohne Gate; keine Parameter der Vorab-Runde geändert",
               A_kayad_reliability=kayad_reliability(), B_neighbour_benchmark=neighbour_benchmark(df),
               C_scale_curve=scale_curve(df))
    (run / "metrics.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    figure(res, repo_path(cfg["paths"]["figures"]) / "if_obergrenze.png")
    print(f"written {run}")


if __name__ == "__main__":
    main()
