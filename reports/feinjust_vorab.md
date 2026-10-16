# Feinjustierung – Vorab-Festlegungen (F1.2, vor jedem Modelllauf)

Stand 2026-10-16. Gehört zu `reports/plan_feinjustierung.md`. Alles hier wurde **festgelegt und committet, bevor** ein neues Merkmal berechnet oder mit Erträgen verglichen wurde. Spätere Änderungen sind verboten (Plan §3, Gate H2); Abweichungen würden in `DECISIONS.md` offengelegt.

Bestätigt durch den Projektinhaber (Chat, 2026-10-16, F0.1): Zielhierarchie A/B/C, Behalte-Regel, Mehr-Kulturen nur Nebeneffekt, genau eine Modellrunde.

---

## 1. Zeilen und Ziele

| Ziel | Zeilen | Label | Validierung |
|---|---|---|---|
| **A** gefährdete Felder | US-Feld-Jahre mit `sensor_era = HLS`, Jahr ≥ 2017, RY vorhanden (gleiche Auswahl wie Phase 3, Basis S2): 89 Feld-Jahre, 8 Standort-Jahre | gefährdet = RY < 0,85, RY im Fold (`targets.ry_in_fold`) | LOFYO (`splits.lofyo`) wie Phase 3 |
| **B** innerhalb des Feldes | BARC-Ertragskarten 2017–2021, 41 Feld-Jahre (wie Phase 2.3) | relativer Pixel-Ertrag | Leave-One-Field-Out (`within_field.run_scheme`, Schema `lofo`) |

Stichtag Ziel A: **1.9.** (Hauptwert, wie Phase 3); 1.8. wird nur beschreibend berichtet. Ziel B: Fenster w2 (16.7.–15.8.).

## 2. Kennzahlen (F1.2)

- **Ziel A, Entscheidungskennzahl:** PR-AUC über alle Test-Feld-Jahre (gepoolt), 95-%-KI per Cluster-Bootstrap (Cluster = Datensatz-Jahr, 1 000 Ziehungen, Seed 42). Zusätzlich Recall bei 20 % FPR.
- **Ziel A, „innerhalb“ (berichtet, nicht Teil der Regel):** je Standort-Jahr mit n ≥ 5, mindestens einem gefährdeten und einem nicht gefährdeten Feld: PR-AUC − Prävalenz und Spearman-ρ(Score, RY); Median über diese Standort-Jahre. Grund: gepoolte Werte mischen Jahres- und Feldunterschiede; innerhalb eines Standort-Jahres zählt nur der Vergleich der Felder.
- **Ziel B:** Median über Feld-Jahre des Spearman-ρ (Vorhersage, relativer Ertrag), KI per Bootstrap über **Felder** (Cluster = Feld, strenger als Feld-Jahr).
- **Differenzen Δ:** neues Modell minus Ausgangsmodell auf **denselben Zeilen**, KI per gepaartem Bootstrap (dieselben Ziehungen für beide Modelle).

## 3. Ausgangsmodelle (F1.1)

- **A-roh** = Stress-Score der Referenzkurve (Phase 3, `phase3.reference_scores`, Basis S2, NDVI). Muss die berichtete PR-AUC 0,71 innerhalb ±0,02 reproduzieren (Gate H1).
- **A0** = logistische Regression auf [Stress-Score] im Fold. Vergleichsbasis für neue Merkmale, damit sich nur das Merkmal unterscheidet, nicht die Modellklasse.
- **B-roh** = NDVI w2 vs. relativer Pixel-Ertrag, Median-ρ 0,676 berichtet (Gate H1: ±0,02).
- **B0** = Ridge (α = 1) auf [z-NDVI w2] (z innerhalb des Feld-Jahres), Leave-One-Field-Out.

## 4. Kombinationsmodell (für alle Merkmale gleich)

- **Ziel A:** `LogisticRegression(C = 1,0, class_weight = "balanced")` nach Median-Imputation und Standardisierung, beide nur aus den Trainingszeilen des Folds. Trainingszeilen = Pool wie `phase3.direct_classifier` (HLS-Ära, Jahr ≥ 2017, RY im Fold vorhanden). Stress-Score der Trainingszeilen mit der Referenzkurve desselben Folds. Fehlende Merkmalswerte bleiben in den Zeilen (Imputation), damit alle Varianten dieselben Zeilen haben.
- **Ziel B:** Ridge (α = 1) auf z-standardisierten Pixelmerkmalen, Leave-One-Field-Out.

## 5. Merkmale (Definitionen, Schwellen vorab)

Alle Merkmale nutzen nur Daten mit Datum ≤ Stichtag (As-of-Regel, `tests/test_no_leakage.py`). Kein Merkmal nutzt Erträge. „Nachbaranomalie“ = Wert des Feldes minus Median der **anderen** Felder desselben Datensatzes in derselben Szene bzw. demselben Jahr (mindestens 3 andere Felder, sonst fehlt der Wert); Nachbarn liefern nur Satellitenwerte, nie Labels.

| ID | Merkmale (Ziel A, Feldebene) | Ziel B (Pixel) | Regeln |
|---|---|---|---|
| **M1 Radar** | `s1_rvi_mean` (RVI = 4·VH/(VV+VH), linear), `s1_rvi_anom`, `s1_vhvv_anom` (VH−VV in dB); Mittel über Szenen 1.7.–Stichtag | z-VH, z-(VH−VV), z-RVI im Fenster w2: zeitlicher Median je Pixel nach räumlichem 15-m-Mittel je Szene (Speckle) | `COPERNICUS/S1_GRD`, IW, VV+VH, beide Orbits; Szene gültig mit ≥ 5 Pixeln im Feld und VV ∈ [−30; 5] dB, VH ∈ [−40; 0] dB; Merkmal fehlt bei < 3 gültigen Szenen im Fenster |
| **M2 Temperatur + Verdunstung** | `lst_dt_mean` (Landsat-Oberflächentemperatur − ERA5-Land-Tmax desselben Tages), `lst_anom_mean` (Nachbaranomalie); Szenen 15.6.–Stichtag. `modis_et_ratio` = ΣET/ΣPET (MOD16A2GF) über 8-Tage-Komposite mit Beginn ≥ 1.6. und Ende ≤ Stichtag. `era5_et_ratio` = Σ tatsächliche / Σ potenzielle Verdunstung (ERA5-Land täglich) 1.6.–Stichtag | n/a: Landsat-Thermal hat 100 m native Auflösung, MODIS 500 m – zu grob für Zonen in 2–14-ha-Feldern | Landsat 8/9 C2 L2 `ST_B10`·0,00341802 + 149,0 K; klar = QA_PIXEL-Bits 1, 3, 4, 5 frei, Anteil klarer Pixel ≥ 0,7; LST-Merkmale fehlen bei < 3 klaren Szenen (Plan §6). MODIS-Füllwerte (> 3 270 kg/m²) verworfen |
| **M3 GDD-Achse** | `stress_gdd`: Stress-Score wie Phase 3, aber auf der Achse Temperatursumme (Basis 10 °C, Deckel 30 °C, ab 1.4.): Klassen à 100 °Cd, Referenz = Median der gesunden Trainings-Feld-Jahre (RY ≥ 0,95) je Klasse, Score = Mittel der negativen Abweichungen über beobachtete Klassen ab 300 °Cd, nur vollständig vor dem Stichtag erreichte Klassen | n/a (je Feld konstant) | S2-NDVI wie Phase 3 |
| **M4 Auflaufdatum** | `emerge_doy`: Tag im Jahr, an dem die geglättete S2-NDVI-Dekadenkurve (as-of) erstmals Basis + 20 % der Amplitude erreicht (Basis = Minimum vor dem Maximum, lineare Interpolation zwischen Dekaden); `emerge_anom` (Nachbaranomalie im selben Jahr) | n/a (je Feld konstant) | fehlt, wenn Amplitude < 0,2 oder < 2 beobachtete Dekaden vor dem Maximum |
| M5 Regionalmodell | **entfällt** (F1.4): die lokale CY-Bench-Kopie enthält nur EU-Länder, 0 US-Region-Jahre (`DATA_SOURCES.md`) | – | – |
| M6 Feldkarten | nur nach Freigabe der Anfragen (F0.3) | – | – |

**Sorte und Saattermin:** In keiner lokalen Quelle steht ein Saattermin (`sowing_date` leer für alle 167 HLS-Feld-Jahre); die Sorte nennt nur KBS-Tabelle 828 (2023). M4 wird deshalb nur auf Plausibilität geprüft (Mais-Aufgang Mitte Mai bis Mitte Juni in Michigan/Maryland), nicht gegen Saattermine. Sorte bleibt bekannte Störgröße.

## 6. Behalte-Regel (bestätigt, Plan §3)

Ein Merkmal M wird behalten, wenn **beide** Bedingungen gelten:
1. ΔPR-AUC(A0 + M vs. A0) ≥ +0,02 mit KI-Untergrenze > 0 **oder** ΔMedian-ρ(B0 + M vs. B0) ≥ +0,02 mit KI-Untergrenze > 0;
2. das jeweils andere Ziel verliert nicht mehr als 0,02 (Punktschätzer). Für M2–M4 ist Ziel B unverändert (Δ = 0).

Danach ein Lauf mit allen behaltenen Merkmalen zusammen (A0 + behaltene). Es gibt **eine** Runde; die Regel wird nicht nachträglich geändert.

## 7. Kontrollen (F3.2)

- **Label-Shuffle:** Trainingslabels im Fold permutiert (auch die Auswahl „gesund“ für die Referenzkurve), 20 Wiederholungen (Seeds 42–61), Mittel der PR-AUC; Ziel B: Pixel-Ertrag je Feld-Jahr permutiert (wie Phase 2.3).
- **Koordinaten-Ablation:** Hauptmodell zusätzlich mit Breite/Länge des Feldmittelpunkts; Δ wird berichtet (Merkmale enthalten sonst keine Orts- oder Feld-IDs).
- **Adversarial Validation:** je LOFYO-Fold flaches LightGBM „Training vs. Test“ auf den Merkmalen des Hauptmodells, 5-fach-CV-AUC; Median und wichtigste Merkmale.
- **Leave-One-Dataset-Out:** Training nur KBS → Test BARC und umgekehrt (Referenzkurve und Labels nur aus dem Trainingsdatensatz); PR-AUC auf dem Testdatensatz gegen die PR-AUC derselben Zeilen im LOFYO-Gesamtlauf.

## 8. Hauptmodell und Kriterien H3 (F4)

**Hauptmodell** = A0 + alle behaltenen Merkmale (Ziel A) und B0 + behaltene Pixelmerkmale (Ziel B). Wird kein Merkmal behalten, endet der Plan nach Gate H2 mit einem negativen Ergebnis (Plan F3/H2); F4 entfällt dann.

**H3 („stark genug“ für Stress-Erkennung), bestätigt:**
1. PR-AUC-KI-Untergrenze > Prävalenz (≈ 0,33) **und** Recall bei 20 % FPR ≥ 0,5;
2. Median-ρ innerhalb der Felder ≥ 0,5 mit KI-Untergrenze > 0,3;
3. Label-Shuffle auf Zufallsniveau: Mittel der PR-AUC ≤ Prävalenz + 0,10 und |Median-ρ| ≤ 0,10;
4. Leave-One-Dataset-Out verliert in keiner Richtung mehr als 0,15 PR-AUC gegenüber dem Gesamtlauf.

**Alarmschwelle für Österreich** (nur F4.1): konforme Schwelle aus den US-Out-of-Fold-Werten der nicht gefährdeten Feld-Jahre, so dass die Fehlalarmrate höchstens 20 % beträgt (endliche Stichprobenkorrektur (n + 1)).
