# Feinjustierung – Ergebnis (F3.3) und Gate H2

Stand 2026-10-16. Plan: `reports/plan_feinjustierung.md`; Vorab-Festlegungen: `reports/feinjust_vorab.md` (committet vor jedem Lauf, Commit `6cc9285`); Läufe: `results/2026-10-16_feinjust_baseline/`, `results/2026-10-16_feinjust_ablation/` (`metrics.json`, `metrics.csv`, `controls.json`, `product.json`, `sensitivity_T4.json`). Datenkritik: `reports/data_review/f2_merkmale.md`, `reports/data_review/f3_ablation.md`.

## Kurzfassung

1. **Gate H1 ✓:** Ausgangswerte reproduziert – Stress-Score PR-AUC 0,710 (berichtet 0,71), NDVI 16.7.–15.8. innerhalb der Felder Median-ρ 0,676 (berichtet 0,676).
2. **Keines der vier neuen Merkmale erfüllt die vorab festgelegte Regel.** Alle verschlechtern Ziel A, Radar auch Ziel B leicht.
3. **Gate H2: negatives Ergebnis.** Laut Plan endet die Feinjustierung hier; Etappe F4 (Hauptmodell, Prüfrunde H3, Freeze-Vorbereitung) entfällt, Österreich wird nicht berührt. Ziele A und B bleiben auf dem Stand von Phase 3 bzw. Phase 2.3.
4. **Neuer Befund aus der Fallprüfung:** Bei KBS erkennt der Stress-Score vor allem die Bio-Parzellen T4 (späte Saat nach Zwischenfrucht). Ohne T4 ist der Nachweis für Ziel A nicht mehr gesichert (PR-AUC 0,60, KI [0,18; 0,95], Prävalenz 0,24).

## 1. Ablation (eine Runde, Stichtag 1.9.)

Ziel A: 89 Feld-Jahre, 8 Standort-Jahre, 29 gefährdet (Prävalenz 0,33). Ziel B: 41 BARC-Feld-Jahre, 27 Felder, 23 912 Pixel. KI = 95 %, Cluster-Bootstrap (A: Standort-Jahre, B: Felder), Δ gepaart auf denselben Zeilen.

| Modell | PR-AUC [KI] | Recall @ 20 % FPR | ΔPR-AUC vs. A0 [KI] | ΔMedian-ρ Ziel B [KI] | behalten |
|---|---|---|---|---|---|
| A-roh (Stress-Score, Phase 3) | 0,710 [0,429; 0,899] | 0,69 | – | – | – |
| **A0** (log. Regression auf Score) | 0,688 [0,424; 0,892] | 0,72 | – | – | Basis |
| A0 + M1 Radar | 0,547 [0,359; 0,967] | 0,45 | −0,141 [−0,317; +0,169] | −0,014 [−0,041; +0,023] | nein |
| A0 + M2 Temperatur + Verdunstung | 0,463 [0,330; 0,848] | 0,48 | −0,225 [−0,281; −0,009] | n/a | nein |
| A0 + M3 GDD-Achse | 0,660 [0,345; 0,900] | 0,59 | −0,028 [−0,126; +0,058] | n/a | nein |
| A0 + M4 Begrünungsdatum | 0,619 [0,393; 0,839] | 0,59 | −0,069 [−0,133; −0,024] | n/a | nein |

Ziel B: B0 (NDVI w2) Median-ρ 0,676 [0,544; 0,708]; B0 + Radar 0,662 [0,541; 0,692].

„Innerhalb Standort-Jahr“ (nur 4 Standort-Jahre mit beiden Klassen, berichtet, nicht Teil der Regel): A0 Median PR-AUC − Prävalenz 0,30, Median-ρ 0,52; mit M1 0,11/0,22, M2 0,38/0,50, M3 0,23/0,20, M4 0,33/0,45.

**Warum die Merkmale schaden (Deutung, nicht geprüft):** Bei rund 70 Trainingszeilen je Fold kostet jedes zusätzliche Merkmal mehr, als es bringt. M2 ist überwiegend Jahresinformation (ERA5 je Standort-Jahr konstant, LST zu 47 % leer) und hilft deshalb in ungesehenen Jahren nicht. Radar misst Feuchte und Struktur der Pflanzen; innerhalb der Felder liegt es knapp unter NDVI.

## 2. Kontrollen (F3.2, Hauptmodell A0 bzw. B0)

| Kontrolle | Ergebnis | Bewertung |
|---|---|---|
| Label-Shuffle Ziel A (20×) | mittlere PR-AUC 0,47 (SD 0,09), Prävalenz 0,33 | über dem Zufall: der Score braucht die Labels kaum (Abweichung von einer typischen Kurve). Keine Leakage, aber H3-Kriterium 3 wäre **nicht** erfüllt (Grenze 0,43) |
| Label-Shuffle Ziel B | Median-ρ 0,41 [−0,53; 0,59] | bei **einem** linearen Merkmal hängt ρ nur vom Vorzeichen ab; der Test ist hier nicht aussagekräftig. B-roh (NDVI ohne Training) zeigt dasselbe Signal |
| Koordinaten | +0,006 [−0,118; +0,090] | kein Ortseffekt |
| Adversarial Validation | Median-AUC 0,61 (max 0,75), 9 Folds | Trainings- und Testjahre leicht unterscheidbar, wie bei Jahreseffekten erwartet |
| Leave-One-Dataset-Out | KBS → BARC 0,863 (gesamt 0,835), BARC → KBS 0,789 (gesamt 0,727) | kein Verlust; Übertragung zwischen Standorten ok |

## 3. Fallprüfung: Was erkennt der Score? (AGENTS §3.5)

Rangliste je Standort-Jahr (`reports/figures/fj_ranking.png`, `ranking.csv`):

| KBS-Behandlung | 2017 RY / Risiko | 2020 RY / Risiko | 2023 RY / Risiko |
|---|---|---|---|
| T1 konventionell | 0,91 / 0,54 | 0,71 / 0,67 | 1,22 / 0,44 |
| T2 Direktsaat | 1,02 / 0,28 | 1,02 / 0,30 | 1,18 / 0,53 |
| T3 reduzierter Input | 0,92 / 0,38 | 0,92 / 0,31 | 1,16 / 0,38 |
| **T4 bio** | **0,43 / 0,86** | **1,04 / 0,87** | **0,54 / 0,94** |

T4 bekommt in jedem Jahr das höchste Risiko, weil die Maiskurve nach der Zwischenfrucht später ansteigt. 2017 und 2023 stimmt das (T4 gefährdet), 2020 nicht: dort sind die sechs höchsten Werte Fehlalarme, und T1 (tatsächlich gefährdet) landet dahinter.

Sensitivität (`sensitivity_T4.json`, nur beschreibend):

| Auswahl | n / gefährdet | PR-AUC A0 [KI] | Prävalenz |
|---|---|---|---|
| alle | 89 / 29 | 0,688 [0,424; 0,892] | 0,33 |
| ohne KBS T4 | 71 / 17 | 0,600 [0,180; 0,951] | 0,24 |
| nur BARC | 17 / 7 | 0,835 [0,333; 1,000] | 0,41 |
| innerhalb KBS-Behandlung × Jahr (6 Wiederholungen) | 12 Gruppen | Median-ρ −0,29 | – |

**Folge:** Ziel A ist in den US-Daten zu einem großen Teil „Bewirtschaftung + Jahr“: späte Bio-Saat bei KBS, ganze Standort-Jahre bei BARC (2017, 2018 alle gefährdet). Zwischen Feldern mit gleicher Bewirtschaftung ist kein Signal nachweisbar. Für Österreich heißt das: Ein Alarm kann auch „spät gesät“ bedeuten, nicht nur „gestresst“.

## 4. Hauptergebnis (F3.4)

Siehe `reports/doku/hauptergebnis.md`. Kurz: Rangliste der Felder je Region mit konformer Alarmschwelle (US-Out-of-Fold: Recall 0,69, Fehlalarmrate 0,18, Präzision 0,65, 31 Alarme bei 89 Feld-Jahren); Feldkarte „unterstes NDVI-Viertel 16.7.–15.8.“ trifft 58 % Problemzonen-Pixel (Anteil 27 %, Lift 2,3); Alarme entstehen meist durch fehlendes Grün im Juli (22 von 31).

## 5. Gate H2 und weiteres Vorgehen

**H2 nicht erfüllt.** Kein Merkmal behalten, die Regel wird nicht nachträglich geändert. Laut Plan endet die Feinjustierung mit diesem negativen Ergebnis; **F4 (H3-Prüfrunde, Freeze-Protokoll, AT-Testprotokoll) wurde nicht ausgeführt**. Die einzige erlaubte Modellrunde ist verbraucht.

Optionen für den Projektinhaber (Entscheidung nötig, nichts davon begonnen):
- (a) **Stress-Score und Innerhalb-Feld-Karte ohne neue Merkmale einfrieren** und für Österreich vorbereiten. Dafür bräuchte es eine neue Entscheidung, weil H3 nur nach H2 vorgesehen war. Ehrliche Lage: Kriterium 3 (Label-Shuffle) wäre verfehlt und der T4-Befund begrenzt die Aussage.
- (b) **Feldkarten** (YIPEEO, SwissYield, F0.3) abwarten: mehr unabhängige Standort-Jahre und Felder ohne Versuchsbehandlungen.
- (c) Phase 5 (CY-Bench, Regionalebene) und die Innerhalb-Feld-Karte als Hauptergebnis für die Abgabe.
