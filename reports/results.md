# Ergebnisübersicht

Eine Zeile je relevantem Lauf (AGENTS.md §6). Metriken immer mit 95-%-KI (Cluster-Bootstrap über Datensatz-Jahre), n = Feld-Jahre / Cluster.

| Datum | Commit | Experiment | Kernmetriken | Kommentar |
|---|---|---|---|---|
| 2026-10-16 | siehe `results/2026-10-16_phase1/metrics.json` | Phase 1: Indikatoren K1–K4 vs. RY (HLS-Zeit) | EVI-K4 ρ = 0,44 [0,10; 0,75], n = 74/9; EVI-K1 ρ = 0,43 [0,09; 0,56], n = 62/6 | Signal vorhanden, aber nur 9 Standort-Jahre; KBS-Werte beruhen auf 2 Jahren |
| 2026-10-16 | `results/2026-10-16_phase2/git.txt` | Phase 2: Modellfamilie × 7 Stichtage × HLS/S2, LOFYO verschachtelt | gewählt nach Regel M-S Ridge S2: ρ(1.9.) = −0,04 [−0,29; 0,37], n = 89/8, Skill vs. B0 −1,13; bestes gepooltes ρ M-alle Ridge S2 0,23 [0,05; 0,43] | Modelle übertragen Jahreseffekte nicht auf ungesehene Jahre; Details `reports/data_review/phase2_models.md` |
| 2026-10-16 | `results/2026-10-16_within_field/git.txt` | Phase 2.3/3.3: innerhalb der Felder (BARC, S2) | NDVI 16.7.–15.8. vs. relativer Pixel-Ertrag Median-ρ 0,68 [0,54; 0,72], n = 41 Feld-Jahre; Problemzonen PR-AUC 0,66 (Prävalenz 0,28); Pixelmodell Satellit 0,70 vs. Gelände 0,29 | Zonen wiederkehrend (ρ 0,67 zwischen Jahren) |
| 2026-10-16 | `results/2026-10-16_round1/git.txt` | Runde 1: relative Satellitenmerkmale | gewählt M-Srel Ridge S2: ρ 0,37 [−0,01; 0,70], n = 89/8; Median-ρ innerhalb Jahr 0,50; LODO 0,47 / 0,40; Skill −0,69 | Kriterien 1+2 verfehlt |
| 2026-10-16 | `results/2026-10-16_round2/git.txt` | Runde 2: einfachere Merkmale | gewählt M-Srel-einfach Ridge S2: ρ −0,01 [−0,21; 0,59]; LODO −0,21 / 0,18 | schlechter als Runde 1 |
| 2026-10-16 | `results/2026-10-16_round3/git.txt` | Runde 3: stärkere Regularisierung | gewählt M-alle-rel Ridge S2: ρ 0,37 [−0,02; 0,68], n = 89/8; Skill −0,02; LODO 0,77 / 0,53 | Kriterien 1+2 verfehlt → kein Freeze (`reports/phase4_stark_genug.md`) |
| 2026-10-16 | `results/2026-10-16_round3/phase3.json` | Phase 3: gefährdet + Referenzkurve (Kandidat Runde 3) | Stress-Score Referenzkurve ρ(1.9.) 0,43 [0,24; 0,72], PR-AUC 0,71 (Prävalenz 0,33); Modell-Schwelle PR-AUC 0,40 [0,32; 0,82] | gefährdet bei KBS v. a. Bio-Parzellen (T4) |
| 2026-10-16 | Branch `phase-5-cybench` (Tag `freeze-cybench-1`) | Phase 5: CY-Bench EU-Mais, LOCO, YAS (ohne AT) | 1.9.: ρ 0,38 [0,36; 0,40], R² 0,06 [0,04; 0,07], Skill vs. YAS = 1 0,07 [0,06; 0,09], n = 8371 Region-Jahre, 16 Länder | alle Stichtage in `reports/results_phase5.md`; EU-Freeze `reports/freeze_protocol_cybench.md` |
