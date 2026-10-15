# Ergebnisübersicht

Eine Zeile je relevantem Lauf (AGENTS.md §6). Metriken immer mit 95-%-KI (Cluster-Bootstrap über Datensatz-Jahre), n = Feld-Jahre / Cluster.

| Datum | Commit | Experiment | Kernmetriken | Kommentar |
|---|---|---|---|---|
| 2026-10-16 | siehe `results/2026-10-16_phase1/metrics.json` | Phase 1: Indikatoren K1–K4 vs. RY (HLS-Zeit) | EVI-K4 ρ = 0,44 [0,10; 0,75], n = 74/9; EVI-K1 ρ = 0,43 [0,09; 0,56], n = 62/6 | Signal vorhanden, aber nur 9 Standort-Jahre; KBS-Werte beruhen auf 2 Jahren |
| 2026-10-16 | `results/2026-10-16_phase2/git.txt` | Phase 2: Modellfamilie × 7 Stichtage × HLS/S2, LOFYO verschachtelt | gewählt nach Regel M-S Ridge S2: ρ(1.9.) = −0,04 [−0,29; 0,37], n = 89/8, Skill vs. B0 −1,13; bestes gepooltes ρ M-alle Ridge S2 0,23 [0,05; 0,43] | Modelle übertragen Jahreseffekte nicht auf ungesehene Jahre; Details `reports/data_review/phase2_models.md` |
