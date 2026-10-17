"""W3.3 curve check and Gate G2 (rule fixed in DECISIONS 2026-10-16 before any curve was looked at).

Per crop at h = 30: share of site-years with a valid curve, Spearman(K1..K5, RY), median K1 in the worst vs
best RY quartile. G2 per crop: >= 3 of 5 positive rho AND median K1 worst quartile < best quartile AND
>= 40 cell-years with a valid curve; G2 overall: >= 2 crops pass.
Outputs: reports/data_review/w33_kurvenpruefung.md, reports/figures/w33_k1_by_ry_quartile.png

Usage:  python -m croptransfer.curve_check [--h 30]
"""

from __future__ import annotations

import argparse
import json

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from croptransfer.config import load_config, repo_path  # noqa: E402
from croptransfer.features_multi import SAT_COLS  # noqa: E402

K = SAT_COLS[:5]
FENCE = "`" * 3


def check(d: pd.DataFrame) -> pd.DataFrame:
    """One row per crop with the G2 ingredients (S2-tier rows with RY only)."""
    s2 = d[(d.tier == "S2") & d.RY.notna()]
    rows = []
    for crop, g in s2.groupby("crop"):
        ok = g[g.curve_ok]
        r = dict(crop=crop, site_years=len(g), curve_ok=len(ok), share_ok=round(len(ok) / len(g), 3),
                 cell_years_ok=ok.drop_duplicates(["cell_id", "year"]).shape[0])
        pos = 0
        for k in K:
            v = ok[[k, "RY"]].dropna()
            rho = spearmanr(v[k], v.RY).statistic if len(v) > 5 and v[k].std() > 0 else np.nan
            r[f"rho_{k}"] = round(float(rho), 3) if not np.isnan(rho) else np.nan
            pos += int(rho > 0) if not np.isnan(rho) else 0
        q = ok.RY.quantile([0.25, 0.75]) if len(ok) else None
        r["k1_worst_q"] = ok.loc[ok.RY <= q.iloc[0], K[0]].median() if q is not None else np.nan
        r["k1_best_q"] = ok.loc[ok.RY >= q.iloc[1], K[0]].median() if q is not None else np.nan
        r["n_pos_rho"] = pos
        r["g2_pass"] = bool(pos >= 3 and r["k1_worst_q"] < r["k1_best_q"] and r["cell_years_ok"] >= 40)
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--h", type=int, default=30)
    args = ap.parse_args()
    cfg = load_config()
    d = pd.read_parquet(repo_path(cfg["paths"]["processed"]) / f"features_multi_h{args.h:03d}.parquet")
    t = check(d)
    g2 = int(t.g2_pass.sum()) >= 2
    fig_dir = repo_path(cfg["paths"]["figures"])
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, len(t), figsize=(3.2 * len(t), 3), squeeze=False)
    for ax, crop in zip(axes[0], t.crop):
        g = d[(d.crop == crop) & (d.tier == "S2") & d.curve_ok & d.RY.notna()]
        g = g.assign(q=pd.qcut(g.RY, 4, labels=["Q1 schlecht", "Q2", "Q3", "Q4 gut"], duplicates="drop"))
        g.boxplot(column=K[0], by="q", ax=ax)
        ax.set_title(crop); ax.set_xlabel("RY-Viertel"); ax.set_ylabel("max NDVI bis Stichtag")
    fig.suptitle(""); fig.tight_layout()
    fig.savefig(fig_dir / "w33_k1_by_ry_quartile.png", dpi=130)
    out = repo_path(cfg["paths"]["data_review"]) / "w33_kurvenpruefung.md"
    out.write_text(
        f"# W3.3 Kurvenprüfung und Gate G2 (h = {args.h})\n\nRegel vorab in DECISIONS.md (2026-10-16). Erzeugt mit "
        f"`python -m croptransfer.curve_check`.\n\n{FENCE}\n{t.to_string(index=False)}\n{FENCE}\n\n"
        f"**G2 gesamt: {'bestanden' if g2 else 'NICHT bestanden'}** (mindestens 2 Kulturen müssen bestehen; "
        f"bestanden: {', '.join(t[t.g2_pass].crop) or 'keine'}).\n\n"
        f"Abbildung: `reports/figures/w33_k1_by_ry_quartile.png`.\n", encoding="utf-8")
    print(t.to_string(index=False)); print("G2:", g2)
    (repo_path(cfg["paths"]["results"]) / "w33_g2.json").write_text(json.dumps({"g2": g2, "h": args.h}), encoding="utf-8")


if __name__ == "__main__":
    main()
