# Datenkritik – Österreich-Test (erster, explorativ)

Zu: `reports/at_test_ergebnis.md`, Protokoll `reports/freeze_protocol_at.md` (`freeze-at-1`). Zahlen: `results/2026-10-17_at_test/{qc.json,review.json,metrics.json}`.
Entscheidung: ⚠️ **weiter mit Einschränkung** (Ergebnisse berichten, als explorativ kennzeichnen, Grenzen offenlegen).

## 3.1 Repräsentativität (Auswahl-Bias)
- **Steiermark fehlt vollständig (⚠️ wesentlich).** Die vorab festgelegten Versuchsarten (Sorten-/Praxisversuche) gibt es nur in Oberösterreich; Wagna, Kalsdorf, Hatzendorf haben Düngungs-/Bodenbearbeitungsversuche (siehe Metadaten von `at_trials.csv`). Folge: V2 ist ein Oberösterreich-Test (5 Standorte: Walding, Mauthausen, Linden, Bad Wimsbach, Innviertel; 34 Standort-Jahre, 7 Jahre; 2019 hat kein `YAS_site`).
- **Ausgeschlossene Standort-Jahre:** Standorte mit weniger als 3 anderen Jahren (Aistersheim, Pasching, Enns, Dietach, Eberstalzell: Bio-Sortenversuche, je 1–2 Jahre) haben keinen `YAS_site` und fallen aus V2 heraus (alle 104 Standort-Jahre haben einen Score).
- **Baseline `YAS_site`:** nur 6 von 34 Werten nutzen 5 komplette Vorjahre; 28 nutzen den Mittelwert aller anderen Jahre (`baseline_short`, enthält auch spätere Jahre, im Protokoll so festgelegt). Das macht `YAS_site` weniger streng als die Regionalversion.
- Wolken: Felder mit ≥ 4 beobachteten HLS-Dekaden in 6…k: 99,9–100 % in jedem Jahr; Mediane 16–20 beobachtete Dekaden. Kein Wolken-Bias erkennbar (2018 mit 20 Dekaden das klarste Jahr, wie ein Trockenjahr es erwarten lässt).
- Zielverteilung: `YAS_site` 0,86–1,26; Jahresmittel 0,95 (2023) bis 1,19 (2022). Wenige schwere Stressfälle (vor allem 2023 trägt den Kontrast).

## 3.2 Sind die Daten korrekt?
- **Kurvenform:** Median der Spitzen-NDVI je Jahr 0,86–0,90, Anteil mit Spitze < 0,6 ≤ 0,1 %: Die INVEKOS-Körnermaisfelder haben maistypische Kurven (Stichprobe aus 10 159 Feld-Jahren; keine visuelle Einzelprüfung von 20 Feldern, nur die Kennzahl).
- **Frühernte/Abfall (⚠️):** Anteil Felder mit abruptem Abfall im Juli/August: 2018 43 %, 2024 49 %, 2022 18 %, übrige Jahre ≤ 5 %. 2018 und 2022 passen zu Trockenstress/vorzeitiger Abreife (der Ertrag fiel 2018 in Oberösterreich trotzdem durchschnittlich aus); **2024 ist nicht erklärt** (möglich: Witterung, Frühernte/Silomais-Verwechslung, Szenenartefakt). Die Regel ist die vorab festgelegte aus `stress.py`; es wurde nichts herausgefiltert.
- **Sättigung (⚠️):** 32 % der Felder haben einen Score ≈ 0 (> −0,001), je nach Jahr 5 % (2018) bis 59 % (2020). Österreichischer Mais liegt in vielen Dekaden über der US-Referenzkurve; der Score kann gesunde Felder dann nicht unterscheiden. Er unterscheidet nur Stress nach unten.
- **Auflösung:** HLS 30 m mit −10-m-Innenpuffer; Feld-Mittel; ERA5/CY-Bench-Prädiktoren sind Regionsmittel (NUTS 2) und beschreiben kein einzelnes Feld.
- **Standortposition:** Gemeindemitte (Hatzendorf → Fehring, Kalsdorf → Ilz, Katzenberg → Kirchdorf am Inn + Geinberg: Zuordnung aus dem Namen). Die gezogenen 100 Felder liegen irgendwo im 5-km-Umkreis, nicht neben der Versuchsparzelle.
- **Erträge:** Versuchsmittel aus Sortenversuchen (Parzellen, gut geführt, wechselnde Sortensätze), keine Praxisfelder; Feuchtebasis 14 % laut Berichten (30 Zeilen ohne Angabe), im Quotienten unkritisch.

## 3.3 Scheinzusammenhänge
- **Jahres-Proxy (⚠️ Hauptbefund):** ρ über die 7 Jahresmittel 0,79; nach Abzug der Jahresmittel 0,31; nach Abzug der Standortmittel 0,46; zwischen Standorten innerhalb eines Jahres ρ im Median −0,1 (6 Jahre). Der Test misst überwiegend den Jahreseffekt.
- **Baseline NDVI:** Das ohne Lernen berechnete mittlere NDVI (Dekaden 9–14) erreicht ρ = 0,50 [0,09; 0,65] gegen 0,50 [0,19; 0,68] beim Score; Korrelation Score ↔ NDVI auf Feldebene 0,88, auf Standort-Jahr-Ebene 0,83. Der Score ist hier praktisch ein NDVI-Maß.
- **Einfluss einzelner Jahre:** Leave-one-year-out 0,41–0,55; ohne 2018 **und** 2023 ρ = 0,37; ohne zwei beliebige Jahre 0,35–0,60. Richtung stabil, Stärke abhängig von den belasteten Jahren.
- **Einzelne Standorte:** Linden −0,50 (7 Jahre), Walding 0,82 – Standorte streuen stark; Median 0,60 aus nur 5.
- **KBS-T4-Effekt (Frage aus Protokoll §5):** Streuung innerhalb eines Standort-Jahres vs. zwischen Standort-Jahren siehe `qc.json` (`score_sd_within_site_year`, `score_sd_between_site_year_means`); ein Hinweis auf „immer dieselbe Gegend markiert“ wurde nicht gezielt geprüft (kein Feld-Ertrag).
- Konfundierung: Sorte, Aussaattermin, Düngung, Bodenart, Hagel sind unbekannt und können Standortunterschiede erklären.

## 3.4 Leakage
- Österreich-Regel: Modelle (Stress-Referenz, Regionalmodell) wurden ohne österreichische Daten gebaut und vor der Auswertung festgeschrieben (Prüfsummen, Tag `freeze-at-1`); nach dem Lauf wurde nichts am Modell, an Schwellen oder an der Auswahl geändert. Die Hilfsanalysen in `review.json` (Jahre weglassen, Baselines) sind beschreibend.
- **Offengelegt:** 15 Notizzeilen mit Versuchsmitteln wurden vor dem Freeze versehentlich gesehen (Protokoll §6), ohne Einfluss auf Festlegungen. Während des Laufs hat eine parallele Sitzung nur Auswertungs-/QC-Ausgaben (`qc_summary`, Jahres-Parameter) an `at_test.py` ergänzt; die Metrik-Logik ist gegenüber dem vorher committeten Stand unverändert (Vergleich der Datei).
- Die Statistik-Austria-Erträge sind gleichzeitig Ziel des Regionaltests und Quelle des `YAS` (Vorjahre); es gibt keine Trainingsüberlappung, da das EU-Modell nie österreichische Daten sah.
- Ein nachfolgender Versuch „regionales Nachtrainieren mit Bundesland-Erträgen“ (`reports/plan_at_nachtraining.md`) ist ein **eigener**, nicht unabhängiger Schritt auf denselben Daten und verändert dieses Ergebnis nicht.

## 3.5 Ergebnis-Plausibilität
- Das Regionalmodell liegt im Mittel um +0,09 zu hoch und ist nach RMSE nicht besser als „normales Jahr“ (0,121 vs. 0,101); passt zu den EU-Ergebnissen (Skill vs. YAS = 1 nur 0,07).
- ρ-Werte von 0,5 aus 6–7 Jahren sind keine starken Belege; Cluster-Bootstrap mit so wenigen Clustern ist grob (obere KI-Grenzen liegen teils unter dem Punktwert, z. B. 0,65 [0,40; 0,70]).
- Fallstudien (Jahresmittel, `review.json`): 2023 passt (Score −0,024, YAS_site 0,95, niedrigster Ertrag); **2018 passt nicht** (niedrigster Score −0,052, aber YAS_site 1,04); 2022 und 2025 haben die höchsten Erträge (1,19 / 1,15) bei Score ≈ 0. Bei Score ≈ 0 streut YAS_site von 0,86 bis 1,26, gesunde Standort-Jahre werden also nicht unterschieden (Abbildung `at_test_scatter.png`).

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Berichten: V2-A bestanden, aber Jahreseffekt und kein Vorteil gegenüber NDVI; Regionalmodell V1 bestanden, nicht stark; Steiermark nicht getestet; kein Feldbefund.
