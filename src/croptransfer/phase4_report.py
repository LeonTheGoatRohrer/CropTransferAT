"""Phase 4: collect the "stark genug" checks of Phase 2 and rounds 1-3 -> report + figure.

Usage:  python -m croptransfer.phase4_report
Writes reports/phase4_stark_genug.md and reports/figures/phase4_rounds.png.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from croptransfer.config import load_config, repo_path


def load_stages(results) -> list[dict]:
    stages = []
    p2 = sorted(results.glob("*_phase2"))[-1] / "criteria_main.json"
    d = json.loads(p2.read_text())
    c = d["criteria"]
    stages.append(dict(name="Phase 2", sel=d["selected"], c1=c["1_beats_B0_B1_from_0801"], c2=c["2_rho_ge_0.4_at_0901"],
                       c3=c["3_lodo_both_directions_rho_gt_0"], c4=c["4_label_shuffle_baseline"], ok=d["strong_enough"]))
    for r in (1, 2, 3):
        f = sorted(results.glob(f"*_round{r}"))
        if not f:
            continue
        d = json.loads((f[-1] / "criteria.json").read_text())
        c = d["criteria"]
        stages.append(dict(name=f"Runde {r}", sel=d["selected"], c1=c["1"], c2=c["2"], c3=c["3"], c4=c["4"], ok=d["strong_enough"]))
    return stages


def fmt(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def main() -> None:
    cfg = load_config()
    results = repo_path(cfg["paths"]["results"])
    st = load_stages(results)
    lines = ["# Phase 4 – „Stark genug?“", "",
             "Automatisch erzeugt mit `python -m croptransfer.phase4_report` aus den Kriterien-Dateien der Läufe. "
             "Kriterium und Auswahlregel: PLAN.md Phase 4, Konkretisierung DECISIONS.md (2026-10-15/16). Alle Werte LOFYO, Stichtag 1.9., 95-%-KI per Cluster-Bootstrap über Datensatz-Jahre.", "",
             "| Stufe | gewähltes Modell | ρ 1.9. [KI] (n) | 1 schlägt B0/B1 ab 1.8. | 2 ρ ≥ 0,4 | 3 LODO KBS→BARC / BARC→KBS | 4 Label-Shuffle | stark genug |",
             "|---|---|---|---|---|---|---|---|"]
    for s in st:
        sel = s["sel"]
        c3 = s["c3"]
        lines.append(
            f"| {s['name']} | {sel['model']} {sel['kind']} {sel['basis']} | {fmt(s['c2']['rho'])} [{fmt(s['c2']['lo'])}; {fmt(s['c2']['hi'])}] ({s['c2']['n']}) | "
            f"{'✓' if s['c1']['passed'] else '✗'} | {'✓' if s['c2']['passed'] else '✗'} | "
            f"{fmt(c3['KBS->BARC']['rho'])} / {fmt(c3['BARC->KBS']['rho'])} {'✓' if c3['passed'] else '✗'} | "
            f"{fmt(s['c4']['rho'])} {'✓' if s['c4']['passed'] else '✗'} | **{'ja' if s['ok'] else 'nein'}** |")
    passed = [s for s in st if s["ok"]]
    lines += ["", "## Entscheidung", ""]
    if passed:
        lines.append(f"Erste bestandene Stufe: **{passed[0]['name']}** → Freeze nach PLAN Phase 4.")
    else:
        lines += ["**Keine Stufe erfüllt das Kriterium.** Nach PLAN Phase 4 („Nicht stark genug? Nicht nach Österreich gehen“) "
                  "wird **nicht eingefroren** und **kein Österreich-Test** vorbereitet. Weitere Runden sind nach der Vorab-Festlegung "
                  "(höchstens 3) nicht erlaubt; jede weitere Änderung braucht eine neue Entscheidung des Projektinhabers.", "",
                  "Woran es scheitert: Kriterium 1 (RMSE besser als RY = 1) und Kriterium 2 (ρ ≥ 0,4). Die Rangfolge der "
                  "Feld-Jahre wird mit relativen Merkmalen besser (ρ ≈ 0,37, beide LODO-Richtungen > 0), aber die Höhe der "
                  "Abweichung vom Normaljahr trifft das Modell nicht genauer als „normales Jahr“. Ursache ist vor allem die kleine "
                  "Zahl unabhängiger Standort-Jahre (8 in der S2-Basis)."]
    # robustness: does ANY model of any stage meet criterion 1 (and 2), regardless of the selection rule?
    import pandas as pd

    any_c1, any_c12, n_models = [], [], 0
    for d in [sorted(results.glob("*_phase2"))[-1]] + [sorted(results.glob(f"*_round{r}"))[-1] for r in (1, 2, 3)
                                                         if sorted(results.glob(f"*_round{r}"))]:
        m = pd.read_csv(d / "metrics.csv", dtype={"cutoff": str})
        m = m[~m.model.isin(["B1", "M-B+"])]
        keys = [c for c in ["model", "kind", "basis", "variant"] if c in m]
        for k, g in m.groupby(keys):
            n_models += 1
            late = g[g.cutoff.isin(["08-01", "08-15", "09-01"])]
            c1 = bool(((late.d_rmse_b0_hi < 0) & (late.d_rmse_b1_hi < 0)).any())
            c2 = bool((g[g.cutoff == "09-01"].rho >= 0.4).any())
            if c1:
                any_c1.append(f"{d.name}: {k}")
            if c1 and c2:
                any_c12.append(f"{d.name}: {k}")
    lines += ["", "## Robustheit gegenüber der Auswahlregel", "",
              f"Geprüft: alle {n_models} Modellvarianten aus Phase 2 und den Runden (ohne B1/M-B+). "
              f"Kriterium 1 erfüllt von **{len(any_c1)}**, Kriterien 1 und 2 zusammen von **{len(any_c12)}** Varianten. "
              + ("Das Urteil hängt also nicht an der Auswahlregel: Auch ein anderes Modell wäre nicht „stark genug“ gewesen. "
                 "(Einige nicht gewählte Varianten erreichen ρ ≥ 0,4, z. B. M-alle-rel Ridge S2 in Runde 1 mit 0,55, "
                 "scheitern aber an Kriterium 1.)" if not any_c12 else "Betroffene Varianten: " + "; ".join(any_c12))]
    out = repo_path("reports") / "phase4_stark_genug.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for i, s in enumerate(st):
        c2 = s["c2"]
        ax.errorbar(i, c2["rho"], yerr=[[c2["rho"] - c2["lo"]], [c2["hi"] - c2["rho"]]], fmt="o",
                    color="#2f7a3e" if s["ok"] else "#a86a00", capsize=4)
    ax.axhline(0.4, color="#b3392f", ls="--", lw=0.8, label="Kriterium ρ ≥ 0,4")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xticks(range(len(st)), [s["name"] for s in st])
    ax.set_ylabel("ρ (LOFYO, 1.9.) gewähltes Modell")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(repo_path(cfg["paths"]["figures"]) / "phase4_rounds.png", dpi=110)
    print(f"written {out}")


if __name__ == "__main__":
    main()
