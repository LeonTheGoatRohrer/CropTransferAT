# Ergebnisübersicht Phase 5 (CY-Bench-Regionalmodell, EU-Freeze)

Eigene Datei, weil `reports/results.md` auf `main` aus anderen Phasen stammt; beim Merge werden die Zeilen dort eingetragen.
Format wie AGENTS.md §6: Datum, Commit, Experiment, Kernmetriken mit 95-%-KI, Kommentar. Quelle aller Zahlen:
`results/2026-10-16_cybench_eu/metrics.json` und `data_structure.json`. **Kein Österreich-Test** (Zero-Shot gesperrt bis zur Freigabe des Protokolls).

Außen-LOCO, EU ohne Österreich, 16 Länder, n = 8371 Region-Jahre (je Stichtag dieselben Zeilen), Ziel YAS:

| Datum | Commit | Stichtag | R² [KI] | ρ [KI] | ρ innerhalb Jahr [KI] | Skill vs. YAS = 1 [KI] |
|---|---|---|---|---|---|---|
| 2026-10-16 | `6c5c693` | 06-01 | −0,02 [−0,03; −0,01] | 0,03 [0,01; 0,06] | −0,05 [−0,12; 0,04] | −0,00 [−0,01; 0,00] |
| 2026-10-16 | `6c5c693` | 06-15 | −0,02 [−0,02; −0,01] | 0,09 [0,07; 0,11] | −0,01 [−0,07; 0,06] | −0,00 [−0,01; 0,01] |
| 2026-10-16 | `6c5c693` | 07-01 | −0,02 [−0,03; −0,01] | 0,16 [0,14; 0,18] | 0,05 [−0,02; 0,12] | −0,00 [−0,01; 0,01] |
| 2026-10-16 | `6c5c693` | 07-15 | 0,03 [0,02; 0,04] | 0,33 [0,31; 0,35] | 0,21 [0,15; 0,26] | 0,04 [0,03; 0,06] |
| 2026-10-16 | `6c5c693` | 08-01 | 0,05 [0,03; 0,07] | 0,36 [0,34; 0,38] | 0,21 [0,13; 0,29] | 0,06 [0,05; 0,08] |
| 2026-10-16 | `6c5c693` | 08-15 | 0,03 [0,02; 0,05] | 0,37 [0,35; 0,39] | 0,23 [0,15; 0,30] | 0,05 [0,03; 0,06] |
| 2026-10-16 | `6c5c693` | 09-01 | 0,06 [0,04; 0,07] | 0,38 [0,36; 0,40] | 0,22 [0,12; 0,30] | 0,07 [0,06; 0,09] |

Kontrollen (09-01): Label-Shuffle R² −0,012 / −0,005 / −0,008, Skill 0,003 / 0,009 / 0,006 (Baseline-Niveau); ohne Deutschland ρ 0,32 [0,30; 0,35];
Training ohne DE ρ 0,32 [0,30; 0,34]; länderbalanciert R² 0,08 [0,05; 0,11]; Koordinaten als Zusatzmerkmal R² 0,13 (nur Kontrolle, nicht im Freeze).
Jahres-Cluster-KI Skill 09-01: [0,02; 0,13]. Einordnung und Grenzen: `reports/data_review/phase5_cybench_eu.md` (Entscheidung ⚠️).
EU-Freeze und vorab registriertes Österreich-Protokoll: `reports/freeze_protocol_cybench.md`.

Abbildung: `reports/figures/phase5_cybench_earlywarning.png`.
