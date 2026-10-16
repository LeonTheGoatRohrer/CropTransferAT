# Datenkritik Phase 2 – Basismodelle: Was bestimmt den Ertrag? (F0, F1)

Datum: 2026-10-16 · Branch `phase-2-models` · Läufe: `results/2026-10-16_phase2/` (metrics.csv, criteria_main.json; `oof.parquet` nicht in Git) · Code: `run_phase2.py`, `phase2_extras.py`.

**Aufbau:** 9 Modelle (B1, M-S, M-W, M-B, M-B+, M-WB, M-SW, M-SB, M-alle) × Ridge/LightGBM × 7 Stichtage × Satelliten-Basis HLS/S2 (+ Variante „W-lang“ für Modelle ohne Satellit) = 238 Läufe. Validierung LOFYO (Feldgruppe × Jahr, 24 Folds), Hyperparameter verschachtelt (Jahr ausgelassen innerhalb der Trainingsdaten), RY-Labels und Trend in jedem Fold nur aus Trainingszeilen. Bewertung: HLS 123 Feld-Jahre / 11 Standort-Jahre, S2 89 / 8.

## Kernergebnisse (Stichtag 1.9., LOFYO)

| Modell | ρ gepoolt [KI] | Median-ρ innerhalb Jahr | RMSE | Skill vs. B0 |
|---|---|---|---|---|
| B0 (RY = 1) | – | – | HLS 0,27 / S2 0,29 | 0 |
| B1 Ridge HLS | −0,17 [−0,51; 0,25] | 0,21 | 0,27 | −0,02 |
| **M-S Ridge S2** (nach Regel gewählt) | −0,04 [−0,29; 0,37] | **0,40** | 0,61 | −1,13 |
| M-alle Ridge S2 | 0,23 [0,05; 0,43] | 0,21 | 0,55 | −0,91 |
| M-alle LightGBM HLS | −0,37 [−0,60; 0,10] | −0,06 | 0,34 | −0,28 |
| M-W LightGBM HLS (W-lang) | −0,06 [−0,48; 0,31] | 0,14 | 0,35 | −0,30 |
| M-B Ridge HLS | 0,03 [−0,17; 0,31] | −0,01 | 0,28 | −0,03 |

Kein Modell schlägt B0 im RMSE an irgendeinem Stichtag (alle KI der RMSE-Differenz > 0 oder um 0).

**Kontrollen (gewähltes Modell M-S Ridge S2):**
- LOYO ρ = 0,00 [−0,32; 0,48]; **LOFO ρ = 0,65 [0,31; 0,75]** (Jahr gesehen, Feld ungesehen) → das Modell kann Jahre, die es kennt, auf neue Felder übertragen, aber **keine ungesehenen Jahre vorhersagen**.
- Leave-One-Dataset-Out: KBS→BARC ρ = 0,42 [−0,06; 0,92] (n = 17), BARC→KBS ρ = −0,19 [−0,36; 0,32] (n = 72).
- Label-Shuffle: ρ = 0,00 [−0,22; 0,35] → fällt auf Zufallsniveau (keine Leakage-Spur).
- Adversarial Validation KBS vs. BARC: AUC = 1,00 (GDD, Beobachtungszahl, NDVI-Niveau) → die Standorte sind in den Merkmalen vollständig trennbar.
- Split-Conformal (über Folds): Abdeckung 79 % (Soll 80 %), 89 % (Soll 90 %), aber halbe Intervallbreite 0,78 bzw. 0,97 RY → formal kalibriert, praktisch nutzlos breit.

## Kriterium „stark genug“ (PLAN Phase 4, vorab festgelegt)

| # | Kriterium | Ergebnis |
|---|---|---|
| 1 | schlägt B0 und B1 an ≥ 1 Stichtag ab 1.8. signifikant | ✗ (RMSE-Differenz zu B0 am 1.9. +0,33 [0,11; 0,46]) |
| 2 | ρ ≥ 0,4 am 1.9. | ✗ (−0,04) |
| 3 | LODO beide Richtungen ρ > 0 | ✗ (BARC→KBS −0,19) |
| 4 | Label-Shuffle auf Baseline | ✓ |

→ **Nicht stark genug.** Nach PLAN Phase 4 geht nichts nach Österreich; die vorab festgelegten Verbesserungsrunden 1–3 (DECISIONS 2026-10-16) laufen.

## Schriftliche Antwort auf F0 und F1 (vorläufig, auch wenn schwach)

**F0 – Wie gut sagen Satellit, Wetter und Boden den gemessenen Feldertrag voraus, und ab wann?** Mit den verfügbaren US-Daten **nicht verlässlich für ungesehene Jahre**. Innerhalb eines Jahres ordnen Satellitenmodelle die Felder teilweise richtig (Median-ρ bis 0,40 auf S2), und für bekannte Jahre übertragen sie auf neue Felder (LOFO 0,65). Der Jahreseffekt – der den größten Teil der RY-Streuung ausmacht – lässt sich aus 8–11 Standort-Jahren nicht lernen. Ein früher Stichtag hilft nicht; die Frühwarnkurve bleibt um 0 (`phase2_earlywarning_main.png`).

**F1 – Welche Faktoren bestimmen den Ertrag?** Deskriptiv (Phase 1) hängt RY mit der späten Kurve zusammen (EVI-Integral K4 ρ = 0,44). In den Modellen sind die SHAP-Beiträge (nur zur Erklärung, im Trainingsdatensatz) auf Satellit (0,22), Boden (0,14) und Wetter (0,13) verteilt; die wichtigsten Einzelmerkmale (nFK, org. Kohlenstoff, Strahlung) sind aber **Standort-Kennungen** (Adversarial AUC 1,0), keine Ursachen. Wetter allein (auch mit 14 KBS-Jahren, „W-lang“) erklärt RY nicht über die Jahre. **Innerhalb der Felder** (BARC, 41 Feld-Jahre, `phase2_within_field.md`): Hier ist das Signal stark. Der S2-NDVI Mitte Juli bis Mitte August ordnet die Ertragszonen mit Median-ρ = 0,68 [0,54; 0,72] (NDRE ebenso 0,68), Problemzonen PR-AUC 0,66 bei Prävalenz 0,28. Schwache Zonen liegen meist jedes Jahr am selben Ort (ρ zwischen Jahren 0,67); Gelände (30 m) erklärt davon wenig (Pixelmodell nur Gelände 0,29 vs. nur Satellit 0,70). **Fazit F1:** Zwischen Feldern und innerhalb eines Feldes sieht der Satellit den Ertrag gut; den Unterschied zwischen Jahren können die Modelle mit 8–11 Standort-Jahren nicht verallgemeinern.

## Prüfliste AGENTS §3

- **3.1 Repräsentativität:** 8 (S2) bzw. 11 (HLS) Standort-Jahre; KBS 2014/2017 ohne HLS-Sommerkurve; BARC-Jahre mit 1–5 RY-Feldern. Ein einzelnes extremes Jahr (BARC 2018 RY ≈ 0,5, KBS 2017) bestimmt die gepoolten Werte.
- **3.2 Korrektheit:** Vorhersagen der Ridge-S2-Modelle reichen bis RY ≈ 1,5 (Extrapolation bei unbekannten Kurvenniveaus) → hohe RMSE. Kein Hinweis auf fehlerhafte Labels (Label-Shuffle neutral, Kurven plausibel).
- **3.3 Scheinzusammenhänge:** Jahres-/Orts-Proxy bestätigt: LOFO ≫ LOFYO, Adversarial AUC 1,0. Feld-Kennungen sind nie Merkmale. SSURGO (M-B+) wirkt bei KBS nur als Standort-Konstante.
- **3.4 Leakage:** As-of-Tests grün; RY und Trend in jedem Fold nur aus Trainingszeilen (Test `test_in_fold_uses_training_rows_only`); Tuning verschachtelt; Label-Shuffle neutral; keine österreichischen Daten verwendet.
- **3.5 Plausibilität:** Kein Ergebnis „zu gut“. Modelle schlagen B0 nicht. Fallstudien → Phase 3.
- **3.6 Entscheidung:** ⚠️ **Weiter mit Einschränkung** – die Pipeline ist korrekt, das Ergebnis ist ehrlich schwach. Phase 2 wird als abgeschlossen getaggt (Abnahme: alle Modelle mit KI, Kontrolltests, schriftliche Antwort F0/F1), das Kriterium „stark genug“ ist **nicht** erfüllt.

## Nachtrag: sekundäre Zielgröße absoluter Ertrag Y (`python -m croptransfer.run_phase2_y`, `results/2026-10-16_phase2_Y/`)

LOFYO, Stichtag 1.9., gleiche Folds/Tuning; Bewertung HLS: 167 Feld-Jahre / 15 Standort-Jahre (inkl. Colorado), S2: 123 / 12.

| Modell | ρ [KI] | R² | RMSE (Mittelwert-Referenz) | Median-ρ innerhalb Jahr |
|---|---|---|---|---|
| M-S Ridge HLS | 0,52 [0,22; 0,76] | 0,32 | 2,37 (2,88) | 0,63 |
| M-alle LightGBM S2 | 0,55 [0,24; 0,75] | 0,28 | 2,56 (3,02) | 0,40 |
| M-alle Ridge HLS | 0,49 [0,23; 0,72] | 0,32 | 2,37 (2,88) | 0,33 |
| M-B LightGBM HLS | 0,16 [0,02; 0,36] | −0,06 | 2,96 | −0,04 |
| M-B+ (SSURGO) Ridge HLS | 0,09 [−0,09; 0,34] | 0,12 | 2,71 | 0,12 |

*Befund:* Den **absoluten** Ertrag ordnet der Satellit mäßig (ρ ≈ 0,5); innerhalb eines Jahres stecken darin v. a. die dauerhaften Unterschiede der KBS-Behandlungen (Bio-Parzellen niedriger) – das ist leichter als die Jahresabweichung RY. Boden (SoilGrids) und SSURGO erklären Y über ungesehene Felder und Jahre kaum (ρ ≤ 0,16): SoilGrids ist für Parzellen zu grob, SSURGO ist bei KBS konstant. Damit ist auch die PLAN-Frage „ist SoilGrids ein brauchbarer Ersatz für SSURGO?“ hier nicht entscheidbar – beide tragen nichts bei. Referenz-RMSE ist der Mittelwert über die Bewertungszeilen (großzügig zugunsten der Referenz).

## Nachtrag: Kalender- vs. GDD-Achse (PLAN 2.4, `python -m croptransfer.gdd_axis`, `results/2026-10-16_gdd_axis/`)

Nur Satellitenmerkmale (M-S), Stichtag 1.9.; GDD-Merkmale = Indexwert bei 300/600/900/1200/1500 °C·d seit 1.4. (+ Maximum), as-of. Kontrolle: Die Kalender-Variante reproduziert exakt die Phase-2-Werte.

| Basis / Modell | Achse | LOFYO ρ [KI] | LODO KBS→BARC / BARC→KBS |
|---|---|---|---|
| HLS Ridge | Kalender | −0,16 [−0,45; 0,25] | 0,27 / 0,21 |
| HLS Ridge | GDD | −0,02 [−0,31; 0,32] | 0,16 / −0,17 |
| S2 Ridge | Kalender | −0,04 [−0,29; 0,37] | 0,42 / −0,19 |
| S2 Ridge | GDD | −0,06 [−0,22; 0,37] | 0,41 / 0,31 |
| S2 LightGBM | Kalender | 0,21 [−0,29; 0,42] | −0,11 / – |
| S2 LightGBM | GDD | 0,35 [−0,29; 0,63] | 0,43 / – |

„–“: LightGBM mit nur 27 BARC-Trainingszeilen liefert konstante Vorhersagen (kein ρ). *Befund:* kein robuster Unterschied zwischen den Achsen; mit S2 ist die GDD-Achse in der LODO-Richtung BARC→KBS besser (0,31 statt −0,19), alle KI sind breit. Nach PLAN-Regel (Auswahl nach LODO) spräche das leicht für die GDD-Achse bei S2 – für den Österreich-Transfer (kühlerer Anbaukalender) ist sie ohnehin die plausiblere Wahl. Entscheidung erst mit mehr Standort-Jahren.
