"""Figure of the fourth Austria test: frozen stress score (1 Sep) against field yield 2026, and yield per score quintile.

Usage:  python -m croptransfer.at_test4_figure   -> reports/figures/at_test4_scatter.png
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from croptransfer.config import load_config, repo_path


def main() -> None:
    cfg = load_config()
    d = pd.read_parquet(repo_path(cfg["at_test4"]["work_dir"]) / "evaluation_table.parquet").dropna(subset=["score_09-01", "y_t_ha"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.4, 1]})
    a.scatter(d["score_09-01"], d.y_t_ha, s=9, alpha=0.45, color="#2a7f62", edgecolors="none")
    a.set_xlabel("Stress-Score am 1.9. (eingefroren, 0 = wie die Referenz)")
    a.set_ylabel("Ertrag 2026 (t/ha, Gesamtertrag / Feldfläche)")
    a.set_title(f"{len(d)} Körnermaisfelder 2026, Hagelversicherung")
    q = pd.qcut(d["score_09-01"], 5, labels=["1\n(tiefster)", "2", "3", "4", "5\n(höchster)"])
    m = d.groupby(q, observed=True).y_t_ha.mean()
    b.bar(range(5), m.to_numpy(), color="#2a7f62")
    b.set_xticks(range(5), m.index)
    b.set_xlabel("Score-Fünftel")
    b.set_ylabel("mittlerer Ertrag (t/ha)")
    for i, v in enumerate(m.to_numpy()):
        b.text(i, v + 0.15, f"{v:.1f}".replace(".", ","), ha="center", fontsize=9)
    fig.tight_layout()
    out = repo_path("reports/figures/at_test4_scatter.png")
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main()
