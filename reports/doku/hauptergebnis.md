# Hauptergebnis der Abgabe

Stand 2026-10-16. Entwurf für die Projektdoku, vom Projektinhaber in eigenen Worten zu überarbeiten. Festlegung des Projektinhabers (DECISIONS 2026-10-16): Das Hauptergebnis sind die **robusten** Befunde, also die Karte innerhalb des Feldes und das EU-Regionalmodell. Der Stress-Score für ganze Felder steht mit seinen Grenzen daneben. Die Feinjustierung wird als vollständig dokumentiertes negatives Ergebnis berichtet.

Zahlen aus `results/2026-10-16_within_field/`, `results/2026-10-16_feinjust_ablation/` (`product.json`, `metrics.json`, `sensitivity_T4.json`) und `reports/results_phase5.md`.

## In einem Satz

Vom Satelliten aus lässt sich zuverlässig zeigen, **wo innerhalb eines Maisfeldes** Ertrag fehlt. Auf Regionalebene erkennt man schwach, aber nachweisbar, **welche Jahre** schlechter werden. **Welches ganze Feld** gefährdet ist, lässt sich mit den vorhandenen Trainingsdaten nur eingeschränkt sagen.

## 1. Welcher Teil des Feldes fällt auf? (stärkstes Ergebnis)

**Produkt:** eine Feldkarte mit auffälligen Zonen (`reports/figures/fj_field_map.png`, zwei BARC-Felder 2021; weitere in `phase2_within_field_maps.png`).

- **Wie gut?** Innerhalb eines Feldes hängt der Grünindex NDVI zwischen 16.7. und 15.8. mit dem gemessenen Pixel-Ertrag zusammen: Median-ρ **0,68** [0,54; 0,71] über 41 Feld-Jahre und 27 Felder. In allen 41 Feld-Jahren ist der Zusammenhang positiv.
- **Als Karte:** Markiert man das unterste Viertel der NDVI-Pixel als „auffällig“, liegen 58 % dieser Pixel tatsächlich in einer Problemzone (Ertrag unter 85 % des Feldmittels). Bei zufälliger Auswahl wären es 27 %, also Faktor 2,3. 56 % der Problemzonen werden so gefunden.
- **Warum robust?** Es braucht kein Training (NDVI selbst ist das Maß). Es hängt nicht an wenigen Wetter-Jahren, und die Zonen wiederholen sich zwischen den Jahren (ρ 0,67, Phase 2.3). Radar dazu verbessert es nicht (−0,01, Feinjustierung).
- **Update 2026-10-17 (Mehr-Standort-Test, `reports/innerfeld_ergebnis.md`):** Die gleiche Regel zeigt auch in Kayad (Italien, 3 Feld-Jahre, ρ 0,60) und Colorado (6 Teilflächen-Jahre, ρ 0,63) in die gleiche Richtung. Belastbar bleibt nur BARC; die beiden anderen Standorte sind zu klein, ein Gate „überträgt“ ist vorab als nicht prüfbar festgelegt.
- **Negativ, nicht verwenden (2026-10-17):** Eine Glättung der Vorhersage über 30 m bringt **nichts** (`reports/innerfeld_ergebnis_runde2.md`); die Karte bleibt auf 10-m-Zellen. Auch ein größerer ρ bei Blockmittelung kommt nur von der gemittelten Messung und gilt für ein leichteres Produkt.
- **Grenzen:** ein Standort (BARC, Maryland), Ertragskarten interpoliert (10-m-Blöcke), 10 m Randpuffer entfernt. Wiederkehrende Zonen können Boden sein, aber auch Fahrgassen oder Ränder.

## 2. Welche Jahre werden schlecht? (Regionalebene, EU)

Das EU-Regionalmodell (Phase 5, CY-Bench, 16 Länder ohne Österreich) ordnet am 1.9. Region-Jahre nach ihrer Abweichung vom Normalertrag: ρ **0,38** [0,36; 0,40], 8 371 Region-Jahre. Das Signal ist klein (Skill gegenüber „normales Jahr“ 0,07 [0,06; 0,09]), aber durch die große Zahl an Region-Jahren gesichert. Das Modell ist eingefroren (`freeze-cybench-1`); der Österreich-Test wartet auf die Freigabe des Protokolls (`reports/freeze_protocol_cybench.md`).

## 3. Welche Felder fallen auf? (mit klaren Grenzen)

**Produkt:** eine Rangliste der Felder je Region und Jahr mit Alarmschwelle (`reports/figures/fj_ranking.png`).

- **Messwert:** Der Stress-Score (Abweichung der Grünkurve von einer gesunden Referenz) findet gefährdete Feld-Jahre am 1.9. mit PR-AUC 0,69 [0,42; 0,89]; Zufall wäre 0,33 (89 US-Feld-Jahre, 8 Standort-Jahre, nur auf ungesehenen Jahren und Feldgruppen bewertet).
- **Alarmschwelle:** höchstens 20 % Fehlalarme bei nicht gefährdeten Feldern (konforme Schwelle). In den US-Daten gibt es damit 31 Alarme, davon 20 richtig; 69 % der gefährdeten Felder werden gefunden.
- **Warum der Alarm?** Gefährdete Felder liegen vor allem im **Juli** unter der Referenz (`fj_score_phases.png`); 22 von 31 Alarmen kommen hauptsächlich aus dem Juli.
- **Die wichtige Grenze:** Der Score erkennt in den US-Versuchsdaten zu einem großen Teil die **Bewirtschaftung**. Die Bio-Parzellen der Kellogg Biological Station (T4, späte Saat nach Zwischenfrucht) bekommen jedes Jahr das höchste Risiko, auch 2020, als sie normal geerntet haben. Ohne T4 ist der Nachweis nicht gesichert: PR-AUC 0,60 [0,18; 0,95] bei Zufall 0,24. Zwischen gleich bewirtschafteten Parzellen ordnet der Score nicht richtig (Median-ρ −0,29). Ein Alarm heißt deshalb „Kurve auffällig“; das kann Stress sein, aber auch späte Saat.

## 4. Was nicht funktioniert hat (und warum das wichtig ist)

- **Jahresvorhersage auf Feldebene:** in drei vorab festgelegten Runden und mit mehreren Kulturen nicht „stark genug“ (Phase 4, Mehr-Kulturen). Ursache: 8–11 unabhängige Standort-Jahre.
- **Feinjustierung:** Radar, Oberflächentemperatur und Verdunstung, eine Temperatursummen-Achse und das Begrünungsdatum wurden einzeln nach einer vorher festgelegten Regel getestet. Alle machten die Erkennung schlechter (`reports/feinjustierung_ergebnis.md`).
- Jedes Kriterium war vorab festgelegt und wurde nicht nachträglich geändert. Die negativen Ergebnisse zeigen, wo die Grenze der vorhandenen Daten liegt: Mehr Standort-Jahre und echte Praxisfelder sind der Hebel, nicht mehr Merkmale.

## 5. Wie viele Modelle stecken dahinter?

Stand 2026-10-18, gezählt aus allen Ergebnisordnern unter `results/` (alle Branches). Insgesamt wurden **782 Modellvarianten trainiert und bewertet**, in elf Experimentblöcken. Übrig geblieben sind die drei Ergebnisse aus Abschnitt 1–3.

| Block | Was trainiert wurde | Varianten | Quelle |
|---|---|---:|---|
| Phase 2: Basismodelle | Ridge und flaches LightGBM je Merkmalsgruppe (Satellit, Wetter, Boden, Kombinationen) × HLS/S2 × 7 Stichtage; Hauptlauf 224, Variante „Wetter lang“ 112 | 336 | `results/2026-10-16_phase2/` |
| Phase 2: Zusatzfragen | Vorlauf nur 1.9. (48), absoluter Ertrag in t/ha (16), Kalender- gegen Temperatursummen-Achse (8) | 72 | `phase2_quick0901/`, `phase2_Y/`, `gdd_axis/` |
| Verbesserungsrunden 1–3 | relative Satellitenmerkmale, weniger Merkmale, stärkere Regularisierung; je 56 | 168 | `round1/` … `round3/` |
| Phase 3: Problemfelder | direkter Klassifikator „gefährdet“ je Stichtag | 7 | `round3/phase3.json` |
| Innerhalb des Feldes (BARC) | 3 Zeitfenster × 3 Merkmalssätze × Ridge/LightGBM × 3 Aufteilungen | 54 | `within_field/` |
| One Acre Fund (Afrika) | 14 Merkmalssätze × Ridge/LightGBM × Land/Jahr auslassen | 56 | `oaf_tabular/` |
| EU-Regionalmodell | LightGBM je Stichtag (7, **eingefroren**) und 3 Kontrollvarianten je Stichtag (ohne Deutschland, mit Koordinaten, ohne feste Merkmale) | 28 | `cybench_eu/`, `models/cybench_freeze/` |
| Mehr-Kulturen | je Kultur und gepoolt × Wetter / Wetter + Satellit | 16 | `mehrkultur_h030/` |
| Feinjustierung | Stress-Erkennung mit Radar, Temperatur/Verdunstung, Temperatursummen-Achse, Begrünungsdatum (M1–M4) | 4 | `feinjust_ablation/` |
| Innerhalb des Feldes, drei Standorte | M1, M2 und K-Raum je Standort (BARC, Kayad, Colorado), über Feld-Jahre und zwischen Standorten | 36 | `innerfeld/` |
| Österreich, explorativ | Neukalibrierung R1 und Nachtraining R2 je 2 Stichtage (4), Machbarkeitstest (1) | 5 | `at_retrain/`, `at_feasibility/` (Branch `phase-9-feldverlauf`) |
| **Summe** | | **782** | |

**Was nicht mitgezählt ist:** Regeln ohne Training (NDVI-Regeln B0–B2, Stress-Score aus der Referenzkurve, Normaljahr- und Trend-Baselines), die Glättung aus Runde 2 (dieselben Modelle, nur nachbearbeitet), die Kalibrierung der Warnschwellen und alle Label-Shuffle-Kontrollen. Die beiden Österreich-Tests haben nur eingefrorene Modelle angewendet und nichts neu trainiert.

**Zum Lesen der Zahl:** Eine Variante ist ein Modell mit festen Merkmalen und festem Stichtag. Jede Variante wurde in einer Kreuzvalidierung mehrfach trainiert (ein Feld, ein Jahr oder ein Land ausgelassen, teils mit verschachteltem Tuning). Die Zahl der einzelnen Trainingsläufe liegt deshalb bei mehreren Tausend.

**Wichtig für die Darstellung:** Zwei der drei Hauptergebnisse sind keine gelernten Modelle. Die Teilflächenkarte beruht auf der einfachen NDVI-Regel, der Stress-Score auf einer festen Referenzkurve. Die gelernten Modelle waren dort nicht besser. Gespeichert und eingefroren sind nur die 7 Modelle des EU-Regionalmodells.
