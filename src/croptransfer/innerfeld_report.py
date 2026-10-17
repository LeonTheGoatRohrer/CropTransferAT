"""Figures for the multi-site within-field study (reports/innerfeld_ergebnis.md). Numbers come from the run output.

Usage:  python -m croptransfer.innerfeld_report [--run results/<dir>]
Writes: reports/figures/if_perfy_rho.png, if_transfer_matrix.png, if_kayad_maps.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from croptransfer.config import load_config, repo_path  # noqa: E402
from croptransfer.innerfeld_run import M1_COLS, fit_predict, main_rows, prepare  # noqa: E402

COL = {"B0": "#7a7a7a", "B1": "#2a6fb0", "M1": "#c4572a"}
SITE_LABEL = {"BARC": "BARC (USA)", "KAYAD": "Kayad (Italien)", "COLORADO": "Colorado (USA)"}


def fig_perfy(tab: pd.DataFrame, path: Path) -> None:
    sites = ["BARC", "KAYAD", "COLORADO"]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4), sharey=True, gridspec_kw={"width_ratios": [3, 1.3, 1.6]})
    rng = np.random.default_rng(1)
    for ax, site in zip(axes, sites):
        for i, (model, scheme) in enumerate([("B0", "untrained"), ("B1", "untrained"), ("M1", f"E-{site}")]):
            t = tab[(tab.site == site) & (tab.model == model) & (tab.scheme == scheme)].dropna(subset=["rho"])
            ax.scatter(i + rng.uniform(-0.15, 0.15, len(t)), t.rho, s=16, color=COL[model], alpha=0.65, lw=0)
            if len(t):
                ax.hlines(t.rho.median(), i - 0.3, i + 0.3, color="black", lw=2)
        ax.axhline(0, color="#999", lw=0.8)
        ax.set_xticks(range(3), ["NDVI Kalender", "NDVI Spitze", "Ridge M1"], fontsize=8)
        n = tab[(tab.site == site) & (tab.model == "B0")].fy_key.nunique()
        ax.set_title(f"{SITE_LABEL[site]}\n{n} Feld-Jahre", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Spearman-ρ im Feld-Jahr (Vorhersage vs. rel. Ertrag)")
    fig.suptitle("Je Feld-Jahr: wie gut ordnet das Satellitenmerkmal die Zellen nach Ertrag? (Strich = Median)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def fig_matrix(metrics: dict, path: Path) -> None:
    sites = ["BARC", "KAYAD", "COLORADO"]
    M = np.full((3, 3), np.nan)
    N = np.zeros((3, 3), int)
    for i, tr in enumerate(sites):
        for j, te in enumerate(sites):
            d = metrics["main"]["E"][te]["M1"] if tr == te else metrics["main"]["T"][f"{tr}->{te}"]["M1"]
            M[i, j], N[i, j] = d["rho_median"], d["n_fy"]
    fig, ax = plt.subplots(figsize=(5.4, 4.3))
    im = ax.imshow(M, vmin=0, vmax=0.85, cmap="Blues")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{M[i, j]:.2f}\n({N[i, j]} FJ)", ha="center", va="center", fontsize=9,
                    color="white" if M[i, j] > 0.55 else "black")
    ax.set_xticks(range(3), [SITE_LABEL[s] for s in sites], fontsize=8)
    ax.set_yticks(range(3), [SITE_LABEL[s] for s in sites], fontsize=8)
    ax.set_xlabel("getestet auf")
    ax.set_ylabel("trainiert auf")
    ax.set_title("Median-ρ des Modells M1 (Diagonale: Leave-One-Out am selben Standort)\nFJ = Feld-Jahre; Kayad und Colorado nur beschreibend", fontsize=8.5)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def fig_kayad(df: pd.DataFrame, path: Path) -> None:
    k = df[df.site == "KAYAD"]
    years = sorted(k.year.unique())
    fig, axes = plt.subplots(2, len(years), figsize=(3.6 * len(years), 6.4), sharex=True, sharey=True)
    for j, yr in enumerate(years):
        g = k[k.year == yr]
        a = axes[0, j].scatter(g.x, g.y, c=g.rel, s=3, cmap="RdYlGn", vmin=0.7, vmax=1.2, marker="s")
        axes[0, j].set_title(f"{yr}: gemessener rel. Ertrag", fontsize=9)
        low = g.z_b0 <= g.z_b0.quantile(0.25)
        axes[1, j].scatter(g.x, g.y, c="#dddddd", s=3, marker="s")
        axes[1, j].scatter(g.x[low], g.y[low], c=np.where(g.rel[low] < 0.85, "#b2182b", "#f4a582"), s=3, marker="s")
        axes[1, j].set_title(f"{yr}: NDVI-Warnzone (rot = Problem)", fontsize=9)
        for ax in axes[:, j]:
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
    fig.colorbar(a, ax=axes[0, :], shrink=0.7, label="relativer Ertrag")
    fig.suptitle("Kayad (Italien): Ertragskarte und NDVI-Warnzonen, ohne Training", fontsize=10)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=None)
    args = ap.parse_args()
    cfg = load_config()
    run = repo_path(args.run) if args.run else sorted(repo_path(cfg["paths"]["results"]).glob("*_innerfeld"))[-1]
    figs = repo_path(cfg["paths"]["figures"])
    figs.mkdir(parents=True, exist_ok=True)
    tab = pd.read_csv(run / "per_fy.csv")
    tab = tab[tab.subset == "main"]
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    fig_perfy(tab, figs / "if_perfy_rho.png")
    fig_matrix(metrics, figs / "if_transfer_matrix.png")
    fig_kayad(main_rows(prepare(cfg)), figs / "if_kayad_maps.png")
    print("figures written to", figs)


if __name__ == "__main__":
    main()
