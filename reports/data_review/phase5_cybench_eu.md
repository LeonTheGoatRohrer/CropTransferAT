# Datenkritik Phase 5 – CY-Bench-Regionalmodell, EU-Freeze (AGENTS.md §3)

Stand: 2026-10-16, Code-Stand der Läufe `6c5c693` (Freeze). Geprüft wird die Stufe **bis zum EU-Freeze, ohne jeden Österreich-Test**.
Alle Zahlen stammen aus `results/2026-10-16_cybench_eu/metrics.json` und `results/2026-10-16_cybench_eu/data_structure.json`
(Letztere erzeugt mit `python -m croptransfer.regional_cybench --summary-only`, schreibt nur die Strukturzusammenfassung der EU-Daten).
KI = 95-%-Perzentil-Bootstrap über Region-Jahre (1000 Ziehungen, Seed 42), wenn nicht anders angegeben.
ρ = Spearman, Skill = 1 − MSE/MSE₀ gegenüber YAS = 1. Referenzstichtag der Zusammenfassung: **09-01**.

## Kurzfazit
Das EU-Regionalmodell ist **schwach, aber echt**: Ab 15.7. liegt der Skill gegenüber YAS = 1 über null (09-01: 0,07 [0,06; 0,09]), davor nicht.
Der Label-Shuffle fällt auf Baseline-Niveau, es gibt keinen Hinweis auf Leakage. Ein großer Teil des Signals ist ein **gemeinsames Jahressignal**
(Spearman der Jahresmittel 0,86 über 19 Jahre), der Anteil innerhalb eines Jahres ist klein (ρ = 0,22). **Entscheidung: ⚠️ weiter mit Einschränkung** (Abschnitt 6).

---

## 3.1 Repräsentativität (Auswahl-Bias)

**Geprüft wie?** `data_structure.json` (Zeilen und Regionen je Land, NUTS-Ebene über die Länge der Regions-ID, Jahre) und `metrics.json` (`data_report`, `target_summary`).

| Befund | Zahl (Quelle) |
|---|---|
| Region-Jahre im Modell | 8371 in 652 Regionen, 16 Länder (BE, BG, CZ, DE, EL, ES, FR, HR, HU, IT, LT, NL, PL, PT, RO, SK) |
| Deutschland-Anteil | 30,6 % der Region-Jahre (2565, 229 Regionen); DE + FR + IT + ES + RO zusammen 7012 von 8371 (83,8 %) |
| NUTS-Ebene | 93,5 % NUTS-3, 6,5 % NUTS-2 (NUTS-2: BE, BG, HR, NL, PL, PT; NUTS-3: alle übrigen) |
| Sehr kleine Länder | BE 21, HR 22, SK 50, LT 53, NL 58 Region-Jahre; Landesmetriken nur ab 30 Region-Jahren („reported“), BE und HR daher nicht einzeln berichtet |
| Jahre | 2003–2021; 2021 nur 61 Region-Jahre (nur DE), 2003–2020 je 382–530 |
| Verlust durch die 5-Vorjahre-Regel | von 10 458 Kandidaten-Region-Jahren entfallen 2027 (keine 5 gültigen Vorjahre) und 60 (keine Meteodaten); 8371 bleiben |

**Welche Fälle fallen heraus, und sind sie systematisch anders?**
- *Länder:* EE, FI, IE, LV (nur Nullerträge) sind ausgeschlossen; DK und SE haben nach der Vorjahre-Regel keine Region-Jahre (`stages_per_country`: kept = 0). Das sind Länder mit kleinem oder marginalem Maisanbau, also genau Grenzstandorte; die Aussagen gelten für Länder mit etablierter Maiswirtschaft.
- *Kurze Reihen:* Länder mit kurzen Reihen verlieren viel (BE: 21 von 85 Zeilen bleiben, LT 53 von 150, NL 58 von 126, EL 245 von 492, CZ 136 von 212). Dort stammen die Region-Jahre nur aus den **letzten Jahren** (BE 2017–2020, EL 2014–2019, SK 2012–2018), langlaufende Länder (DE, ES, FR, IT, RO, BG, PT, HU: 2003–2020) decken alle Jahre ab. Das Modell sieht frühe Jahre also fast nur in großen Ländern.
- *Stress selten und wenigen Jahren zugeordnet:* 1219 Region-Jahre (14,6 %) haben YAS < 0,85. Die fünf häufigsten Jahre (2015, 2003, 2013, 2018, 2012) stellen davon 549 (54,9 %); 2003 allein 47,1 % seiner Region-Jahre unter 0,85. Die Stress-Metriken hängen also von wenigen Jahren ab; deshalb wird zusätzlich ein Jahres-Cluster-Bootstrap berichtet (Abschnitt 3.5).
- *Verteilung der Zielgröße je Jahr:* Jahresmittel YAS von 0,87 (2003) bis 1,15 (2021) bzw. 1,14 (2014); das Training sieht also Jahre mit sehr unterschiedlichem Mittel, kein Jahr ist leer.
- *Aggregationsebene:* 93,5 % der Daten sind NUTS-3, die Bundesländer-Ebene (NUTS-2) ist mit 6,5 % unterrepräsentiert. NUTS-2-Werte sind flächengemittelt und glatter; ob das Modell auf der gröberen Ebene gleich gut ist, ist **nicht** geprüft. Die Länder mit NUTS-2-Daten haben nur 21 bis 216 Region-Jahre (PL 216, BG 108, PT 123, NL 58, HR 22, BE 21). In der Doku als Grenze nennen.
- *Wolken-Bias (3.1):* n/a im Sinne der Feldpipeline (keine Pixel-Beobachtungen, Wetter und Bodenfeuchte sind wolkenfrei; fPAR/NDVI sind Kompositprodukte). Gültigkeit der Prädiktoren: keine Wertebereichsverletzungen (`range_violations`: überall 0); 60 Region-Jahre ohne Meteodaten wurden entfernt (0,6 % der Kandidaten).
- *Gewichtung:* Jedes Region-Jahr zählt gleich, unabhängig von der Anbaufläche (keine Flächengewichte). Kleine Regionen mit rauschbehafteten Erträgen zählen damit so viel wie Hauptanbaugebiete. Als Gegenprobe gibt es die länderbalancierte Auswertung (R² 0,08 [0,05; 0,11]).

**Konsequenz:** Aussagen gelten für mittel- und südeuropäische Regionen mit eingeführtem Maisanbau, mit starkem Gewicht von DE/FR/IT. Gegenprobe ohne Deutschland siehe 3.3.

---

## 3.2 Korrektheit der Daten

**Geprüft wie?** `data_report` (Nullerträge, Bereichsprüfungen), `data_structure.json` (Ertragsextrema, YAS-Ausreißer), `case_studies`.

- **Nullerträge:** 201 von 19 050 Rohzeilen der 18 gelisteten Länder (1,1 %); sie stammen fast nur aus EL (67), FR (86), LT (22), PT (13). Sie werden als **fehlend** behandelt (DECISIONS: gemeldete Nullen sind fehlende Meldungen, keine Totalausfälle). Das ist eine Annahme: Falls einzelne Nullen echte Totalausfälle wären, fehlten genau die schwersten Stressfälle. Bei einem echten Maisanbau in EL/FR/LT/PT ist das unwahrscheinlich, aber nicht belegt. Die vier Länder EE, FI, IE, LV haben ausschließlich Nullen und sind ausgeschlossen.
- **Einheit/Bereich:** In den ausgewerteten Region-Jahren liegt kein Ertrag über 20 t/ha (`n_yield_above_20` = 0, gesamt und je Land). Die Rohdaten von EL enthalten Werte über 20 t/ha (Maximum 24,1 t/ha in EL431 2009–2013, direkte Sichtung der EL-Ertragsdatei); sie liegen **vor** dem ersten Auswertungsjahr von EL (2014) und können daher nur als Vorjahre in die Erwartung eingehen. Mittelwerte je Land sind plausibel (z. B. NL 11,3, EL 10,0, DE 9,2, FR 8,8, RO 4,1 t/ha).
- **YAS-Ausreißer:** 143 Region-Jahre (1,7 %) haben YAS außerhalb 0,5–2,0 (RO 63, EL 22, IT 22, LT 8, ES 6, HU 6, DE 10, BG 4). Extremwerte: YAS bis 4,57 (EL), 3,92 (LT), 3,58 (IT); minimal 0,07 (RO). RO 2007 (Dürre) und EL (kleine Anbauflächen, Ertragssprünge) sind nicht entscheidbar echt oder Meldeartefakt; sie bleiben in der Hauptauswertung (DECISIONS), die „robuste“ Auswertung (YAS 0,5–2,0, n = 8228) ist nur Sensitivität: R² 0,07 [0,05; 0,09], ρ 0,37 [0,35; 0,39] bei 09-01, also praktisch unverändert.
- **Fallstudien:** Die drei schlechtesten Vorhersagen sind an **allen sieben** Stichtagen dieselben drei EL-Region-Jahre (YAS 4,4–4,6; EL623 2015, EL421 2014, EL411 2016, Fehler 3,5 YAS-Einheiten). Es sind die Jahre 2014–2016, also der Beginn der EL-Auswertungsjahre; ein YAS > 4 verlangt, dass das Mittel der Vorjahre unter einem Viertel des Ertrags liegt, das spricht für Meldeartefakte der Vorjahre (nicht Einzel-Region-Jahr geprüft). Die „besten“ drei (Fehler ≤ 9·10⁻⁶ YAS) wurden nach kleinstem Fehler ausgewählt und sagen nichts über die Güte aus.
- **Sensor/Produkt-Wechsel, Harmonisierung:** Die Prädiktoren sind von CY-Bench vorgegebene Produkte (AgERA5, GLDAS, MODIS-fPAR/NDVI); die Reihe 2003–2021 wurde nicht auf Brüche geprüft (kein Sensorwechsel-Test wie in der Feldpipeline). Offen.
- **Auflösungs-Mismatch:** Die Prädiktoren sind Regionsmittel über die Maisfläche (Crop-Mask); sie beschreiben die Region, nicht ein Feld, und werden nicht feldbezogen interpretiert.
- **Regionalstatistiken:** Erträge sind amtliche Meldungen der Länder, ggf. revidiert; Einheit t/ha. Eine nachträgliche Revision wurde nicht verfolgt (CY-Bench v1.10 wird als gegeben genommen).

**Konsequenz:** Schwache Ertragsdaten in EL (und Teilen von RO/LT/IT) verzerren RMSE/R², weshalb länderbalanciert, ohne DE und robust zusätzlich berichtet werden; die Rangmaße (ρ) sind gegen Ausreißer deutlich unempfindlicher.

---

## 3.3 Scheinzusammenhänge

**Jahres-Proxy.** Das Modell sagt zum großen Teil „welches Jahr ist das“ (europaweit gemeinsames Wetter, z. B. 2003, 2018). Gemessen:

| Stichtag | ρ gepoolt [KI] | ρ innerhalb eines Jahres (Mittel über 19 Jahre) [KI] | ρ innerhalb Land und Jahr (199 Gruppen) | ρ der Jahresmittel (19 Jahre) |
|---|---|---|---|---|
| 06-01 | 0,03 [0,01; 0,06] | −0,05 [−0,12; 0,04] | −0,01 | 0,54 |
| 06-15 | 0,09 [0,07; 0,11] | −0,01 [−0,07; 0,06] | 0,01 | 0,53 |
| 07-01 | 0,16 [0,14; 0,18] | 0,05 [−0,02; 0,12] | 0,03 | 0,55 |
| 07-15 | 0,33 [0,31; 0,35] | 0,21 [0,15; 0,26] | 0,12 | 0,71 |
| 08-01 | 0,36 [0,34; 0,38] | 0,21 [0,13; 0,29] | 0,10 | 0,90 |
| 08-15 | 0,37 [0,35; 0,39] | 0,23 [0,15; 0,30] | 0,13 | 0,86 |
| 09-01 | 0,38 [0,36; 0,40] | 0,22 [0,12; 0,30] | 0,14 [0,09; 0,19] | 0,86 |

Nur etwa die Hälfte bis zwei Drittel des gepoolten ρ bleibt innerhalb eines Jahres. Vor dem 15.7. ist die Leistung innerhalb eines Jahres null. Ein späterer Test mit wenigen Regionen pro Jahr (Bundesländer) hängt daher überwiegend an Jahreseffekten; das wird im Protokoll mit dem Jahres-Cluster-Bootstrap und ρ innerhalb eines Jahres abgesichert.

**Orts-Proxy / Auswendiglernen.**
- Koordinaten (lat/lon) als Zusatzmerkmale verbessern die LOCO-Leistung deutlich (09-01: R² 0,13 [0,11; 0,15] statt 0,06; ρ 0,45 statt 0,38). Koordinaten kodieren ein **großräumiges Klima- und Anbaumuster** (benachbarte Regionen, auch über Landesgrenzen hinweg, verhalten sich ähnlich); der Gewinn zeigt, dass Ortsinformation Signal trägt, das die rein wetterbasierten Merkmale nicht fassen. Für einen Transfer in ein neues Land ist das nicht übertragbar; Koordinaten sind deshalb **nicht** im Freeze-Modell (Protokoll Abschnitt 1). Die Zahl ist nur Kontrolle, kein Ergebnis.
- Statische Bodenmerkmale (`awc`, `bulk_density`): Ohne sie ist das Modell **besser**, nicht schlechter (09-01: R² 0,07 [0,06; 0,09] vs. 0,06 [0,04; 0,07]; ρ 0,40 vs. 0,38). Im eingefrorenen Modell trägt `awc` und `bulk_density` am Stichtag 09-01 und 08-15 0,0 des Gain-Anteils, an den früheren Stichtagen höchstens 0,022. Die Adversarial-Validation (Land vs. Rest, 2-fach-CV) liefert AUC 0,98–1,00 für jedes Land, mit `awc` als wichtigstem Merkmal in 7 von 16 Ländern, `bulk_density` in 2 weiteren: **Statische Merkmale sind ein Länder-Fingerabdruck**. Dass das Modell sie praktisch nicht nutzt, ist gut; formal bleiben sie im eingefrorenen Merkmalssatz (so registriert) und werden nicht nachträglich entfernt.
- Länder-ID, Regions-ID, Jahr: nicht im Merkmalssatz (Protokoll Abschnitt 1).

**Label-Shuffle.** Ziel zufällig permutiert (3 Wiederholungen je Stichtag, feste Hyperparameter): R² −0,02 bis −0,005, ρ −0,10 bis 0,02, Skill −0,004 bis 0,009. Bei 09-01: R² −0,012/−0,005/−0,008, ρ −0,016/0,015/0,023, Skill 0,003/0,009/0,006. Alle Werte auf Baseline-Niveau, deutlich unter den echten Werten (R² 0,058, ρ 0,38, Skill 0,071). Kein Hinweis auf Leakage.

**Adversarial Validation.** Siehe oben: Länder sind nahezu perfekt unterscheidbar (AUC 0,984–1,000). Das ist erwartbar (Klima-/Bodenfingerabdrücke) und heißt: Der Länder-Hold-out ist ein **echter Domänentransfer**, kein Zufalls-Split; die Güte darf nicht als „in-Land“-Güte gelesen werden. Dass Österreich leicht als eigene Domäne erkennbar sein dürfte, ist eine Erwartung, nicht geprüft.

**Deutschland-Dominanz (30,6 %).**
- Auswertung ohne DE (n = 5806): R² 0,04 [0,02; 0,06], ρ 0,32 [0,30; 0,35], Skill 0,06 [0,04; 0,08].
- Training ohne DE (Auswertung auf den Nicht-DE-Ländern): R² 0,05 [0,03; 0,06], ρ 0,32 [0,30; 0,34]; verglichen mit dem Hauptmodell auf denselben Zeilen (R² 0,04, ρ 0,32) ist das Ergebnis praktisch gleich. Die Leistung hängt also nicht daran, dass DE im Training steht.
- Länderbalanciert: R² 0,08 [0,05; 0,11]; Mittel über 14 berichtete Länder: R² 0,06, ρ 0,38.
- Je Land (09-01, nur Länder mit ≥ 30 Region-Jahren): Gut sind SK (R² 0,51, ρ 0,82, n = 50), HU (0,34, 0,66), CZ (0,34, 0,63), BG (0,30, 0,68), FR (0,25, 0,54), DE (0,16, 0,58). **Kein Skill** in ES (R² −0,61, ρ 0,02), IT (−0,20, 0,11), PT (−0,22, −0,13), EL (−0,11, −0,06) und LT (−0,34, −0,05; n = 53, Ausreißer). Hypothese (nicht geprüft, da keine Bewässerungsdaten): Das Modell funktioniert dort, wo Niederschlag und Temperatur den Mais begrenzen, und nicht dort, wo Bewässerung die Wetterabhängigkeit entkoppelt. Ob und wie das für Österreich gilt, ist die offene Testfrage.

**Konfundierung (3.3).** Bewässerung, Sorte, Saattermin, Düngung und Anbauflächenverschiebungen sind nicht Teil der Daten und können die Befunde (z. B. das Versagen in ES/IT/PT/EL) erklären. Ertragsanomalie YAS enthält auch den Fortschritt (Sortenwechsel, Technik) der letzten Jahre, der nicht wettergetrieben ist; die Trend-Baseline fängt davon nur lineare Anteile ab.

---

## 3.4 Leakage

| Frage | Prüfung | Befund |
|---|---|---|
| Features nach dem Stichtag? | As-of-Filter (Datum ≤ Stichtag); fPAR-Dekaden ab Etikett + 9 Tage, NDVI-Fenster ab + 7 Tage; Stichtagsmonat nur bis zum Stichtag. Tests `test_aggregate_asof_ignores_everything_after_the_cutoff`, `test_composite_with_start_label_is_usable_only_after_its_window_ends`, `test_asof_assertion_fires_on_violation`, `test_build_country_features_do_not_depend_on_data_after_the_cutoff`, `test_composites_not_yet_complete_at_the_cutoff_are_excluded` | kein Zukunftswissen. Echte Produktlatenzen (z. B. GLDAS Wochen) werden **nicht** modelliert (DECISIONS): Aussage „Wissensstand nach Datum“, nicht Echtzeit-Betrieb |
| Erwartung / YAS nur aus Vorjahren? | `add_yas` nutzt ausschließlich y−5 … y−1 derselben Region; Tests `test_yas_hand_example_uses_only_previous_years`, `test_yas_and_trend_ignore_the_year_itself_and_the_future`, `test_yas_requires_five_consecutive_valid_previous_years` | ja; Trend-Baseline ebenfalls nur Vorjahre |
| Skalierung/Imputation/Schwellen mit Testdaten? | keine Skalierung, keine Imputation (LightGBM mit NaN); Schwelle YAS < 0,85 ist eine feste Konstante | nein |
| Hyperparameter verschachtelt getunt? | äußerer Leave-One-Country-Out für die Bewertung, innerer LOCO nur auf den Trainingsländern (`fold_hyperparameters` je Außen-Fold; Tests `test_loco_splits_never_share_a_country`, `test_tuning_only_sees_the_rows_it_is_given`) | ja. Die gewählten Werte schwanken je Fold (09-01: (3, 600, 100) in 5, (3, 600, 200) in 4, (3, 600, 50) in 4 von 16 Außen-Folds), das Tuning ist wenig stabil, die Modelle sind aber flach (max_depth ≤ 3) |
| Rasteranpassung nach Sicht der Außen-Ergebnisse? | DECISIONS (Hyperparameter-Raster): das erste Raster wurde nach einem Pilotlauf (07-01, 09-01) erweitert, weil Randwerte gewählt wurden; die äußeren Ergebnisse des Piloten waren sichtbar | leichter Selektionsverdacht, offengelegt; die Richtung ist stärkere Regularisierung, die Erweiterung war durch die Randwahl, nicht die Außengüte begründet. Kleiner möglicher Optimismus der LOCO-Zahlen, in der Doku zu nennen |
| Räumliche/zeitliche Nähe | Länder-Hold-out verhindert Nachbarregionen **im selben Land**; Regionen jenseits der Grenze (DE–NL, FR–BE, DE–CZ, DE–PL) bleiben im Training. **Es gibt kein Leave-One-Year-Out:** Trainingsländer enthalten dieselben Jahre wie das Testland, das Modell kann „Dürrejahr 2003“ aus Nachbarländern lernen | siehe unten |
| Österreich-Regel | siehe unten | eingehalten |

**Same-year-Struktur.** Der gemeinsame Jahreseffekt (ρ der Jahresmittel 0,86) kann beim LOCO aus anderen Ländern desselben Jahres gelernt werden. Das ist für den vorgesehenen Zero-Shot-Test dieselbe Situation (Trainingsländer enthalten dieselben Jahre wie Österreich 2006–2020), also konsistent, und es ist keine Verwendung von Test-**Labels**; es heißt aber: Die Zahlen zeigen „Transfer über Länder bei bekannten EU-Jahren“, nicht „Vorhersage eines neuen Jahres“. Ein Leave-One-Year-Out-Zusatztest (nur EU-Daten, ohne Änderung am Freeze) würde das sauber trennen; er ist **nicht** gemacht und als offener Punkt vorgeschlagen.

**Österreich-Regel (PLAN §0, §6).**
- Wurden österreichische Daten vor dem Freeze ausgewertet oder genutzt? **Nein.** Die Länderliste enthält kein AT (`assert_no_austria` an allen Einstiegen, Test `test_austria_is_excluded`, `test_training_entry_points_reject_austrian_rows`). Die Strukturzusammenfassung für diese Datenkritik wurde nur auf der EU-Tabelle berechnet (16 Länder, kein AT); es wurde keine Datei aus dem Verzeichnis `maize/AT/` geöffnet, nicht `stat_at_maize.csv`, nicht `at_trials`.
- Wurde nach dem Freeze etwas am Modell geändert? **Nein.** Die SHA-256 aller 14 Freeze-Dateien (7 Modelle, 7 Meta-Dateien in `results/models/cybench_freeze/`) wurden am 2026-10-16 gegen Abschnitt 5 von `reports/freeze_protocol_cybench.md` geprüft: alle 14 stimmen überein. Der Zero-Shot-Test Österreich wurde **nicht** ausgeführt und bleibt bis zur Freigabe des Protokolls durch den Projektinhaber gesperrt.
- Auch nach der Auswertung gilt: Alle Kontrollen und Kennzahlen dieses Berichts betreffen nur die EU-Länder.

---

## 3.5 Plausibilität der Ergebnisse

**Schlägt das Modell die Baselines?** (Außen-LOCO, n = 8371 Region-Jahre in 16 Ländern, alle Stichtage)

| Stichtag | R² [KI] | ρ [KI] | Skill vs. YAS = 1 [KI] | Skill, Jahres-Cluster-KI | Skill vs. Trend [KI] |
|---|---|---|---|---|---|
| 06-01 | −0,02 [−0,03; −0,01] | 0,03 [0,01; 0,06] | −0,00 [−0,01; 0,00] | [−0,04; 0,03] | 0,04 [−0,04; 0,10] |
| 06-15 | −0,02 [−0,02; −0,01] | 0,09 [0,07; 0,11] | −0,00 [−0,01; 0,01] | [−0,03; 0,03] | 0,04 [−0,04; 0,11] |
| 07-01 | −0,02 [−0,03; −0,01] | 0,16 [0,14; 0,18] | −0,00 [−0,01; 0,01] | [−0,05; 0,03] | 0,04 [−0,04; 0,11] |
| 07-15 | 0,03 [0,02; 0,04] | 0,33 [0,31; 0,35] | 0,04 [0,03; 0,06] | [0,00; 0,09] | 0,08 [0,00; 0,15] |
| 08-01 | 0,05 [0,03; 0,07] | 0,36 [0,34; 0,38] | 0,06 [0,05; 0,08] | [0,02; 0,12] | 0,10 [0,02; 0,18] |
| 08-15 | 0,03 [0,02; 0,05] | 0,37 [0,35; 0,39] | 0,05 [0,03; 0,06] | [−0,00; 0,10] | 0,09 [0,01; 0,16] |
| 09-01 | 0,06 [0,04; 0,07] | 0,38 [0,36; 0,40] | 0,07 [0,06; 0,09] | [0,02; 0,13] | 0,11 [0,03; 0,18] |

- **Gegen YAS = 1:** ab 15.7. ein kleiner, bei Region-Jahr-Bootstrap klar positiver Skill; beim Jahres-Cluster-Bootstrap liegt die untere Grenze an 07-15 bei 0,00 und an 08-15 bei −0,00 (Null eingeschlossen), erst 08-01 und 09-01 sind klar positiv. Vor dem 15.7. kein Skill, das ist das ehrliche Ergebnis der Frühwarnkurve.
- **Gegen die lineare Trendfortschreibung:** Die Trend-Baseline ist selbst schlecht (R² −0,06 [−0,14; 0,02] bei 09-01, ρ 0,03); der Skill gegen sie (0,11 [0,03; 0,18]) schließt beim Jahres-Cluster-Bootstrap die Null ein (−0,07; 0,24). Gegen den Trend ist der Gewinn also **nicht robust** gegen gemeinsame Jahreseffekte.
- **Zu gut?** Nein: R² ≤ 0,06 (gepoolt), nirgends nahe 0,9. Das Gegenteil ist der Fall – das Modell erklärt wenig. Der Verdacht „zu gut“ ist damit hinfällig; der Label-Shuffle bestätigt, dass die kleine Güte nicht aus Leakage kommt.
- **Dass ρ (0,38) deutlich über R² (0,06) liegt**, spricht für eine teilweise richtige Rangfolge, aber kaum nutzbare Größenordnung: Das Modell sagt kleine Abweichungen von 1 voraus, die tatsächlichen YAS streuen deutlich stärker (RMSE der Baseline YAS = 1: 0,246, des Modells: 0,237).
- **Konfidenzintervalle und n:** Alle KI stehen in den Tabellen; die Region-Jahr-KI sind zu eng, weil Region-Jahre im selben Jahr abhängig sind (19 Jahre, 199 Land-Jahr-Gruppen). Maßgeblich ist das Jahres-Cluster-KI (Beispiel 09-01: ρ [0,30; 0,45], Skill [0,02; 0,13], R² [0,00; 0,11]).
- **Vergleich mit publizierter Baseline:** Der einzige publizierte Vergleichswert im Repo (`DATA_SOURCES.md`) ist die CY-Bench-Baseline für **Österreich**: R² 0,13 (SklearnRF, Median über LOYO-Folds, Datenversion v1.8, In-Domain). Das ist **kein** Vergleich mit unseren EU-Zahlen (anderes Land, anderer Aufbau: In-Domain-LOYO statt Länder-Hold-out, andere Version). Der Wert dient erst nach dem Zero-Shot-Test zur Einordnung. Für den EU-Raum als Ganzes liegt im Repo kein publizierter Vergleichswert vor; ein solcher wird nicht aus dem Gedächtnis eingesetzt.
- **Fallstudien:** siehe 3.2 (die drei schlechtesten sind EL-Region-Jahre mit Verdacht auf Meldeartefakte; die „besten“ sind nach dem Fehler gewählt und nicht aussagekräftig). Eine inhaltliche Sichtung weiterer Fälle (z. B. 2003, 2015 als Stressjahre) steht aus.
- **Wichtige Merkmale (Gain-Anteile, 09-01):** `tmax` 0,29, `cwb` 0,22, `prec` 0,18, `tmin` 0,15; fPAR 0,06, SSM 0,05, NDVI 0,03, RSM 0,02. Das Wetter trägt das Signal, die Satellitenindizes wenig; das ist die erwartete Tendenz (Hitze- und Wasserbilanz im Sommer), aber bei korrelierten Merkmalen nur eine Größenordnung, kein kausaler Beleg.

---

## 3.6 Entscheidung

**⚠️ Weiter mit Einschränkung.** Kein ⛔: Es gibt keinen Hinweis auf Leakage (As-of, Vorjahre-Regel und verschachteltes Tuning geprüft und getestet, Label-Shuffle auf Baseline-Niveau), die Österreich-Regel ist eingehalten, die Freeze-Prüfsummen stimmen. Aber folgende Grenzen sind in der Doku und im Abschlussbericht festzuhalten:

1. **Das Modell ist schwach.** Vor dem 15.7. kein Skill; am 1.9. R² 0,06 und Skill 0,07 gegen YAS = 1; gegen die Trendfortschreibung nicht robust gegen Jahreseffekte.
2. **Großer Anteil Jahressignal.** ρ innerhalb eines Jahres 0,22 [0,12; 0,30], innerhalb Land und Jahr 0,14 [0,09; 0,19]. Ein Test mit 5 Regionen pro Jahr (geplanter Österreich-Zero-Shot, n = 75) hängt überwiegend am Jahreseffekt.
3. **Kein Skill in ES, IT, PT, EL** (vermutlich Bewässerung/Mittelmeerklima, nicht geprüft), Gewinne in SK, HU, CZ, BG sowie FR und DE.
4. **Länder-Hold-out, kein Jahres-Hold-out.** Trainingsländer enthalten dieselben Jahre wie das Testland (siehe 3.4).
5. **Ebenenmischung:** 93,5 % NUTS-3, Bundesländer-Ebene (NUTS-2) schwach vertreten.
6. **Datenqualität:** Nullerträge als „fehlend“ angenommen; EL-Ausreißer (YAS > 4) und hohe Rohwerte in EL; keine Prüfung auf Produktbrüche der Prädiktoren; echte Produktlatenzen nicht modelliert.
7. **Statische Bodenmerkmale** wirken als Länder-Fingerabdruck und verschlechtern das Ergebnis leicht (R² 0,075 ohne vs. 0,058 mit); im Freeze bleiben sie wie registriert, die Gain-Anteile sind null bis klein.

**Offene Punkte für den Projektinhaber (keine Änderung am Freeze):**
- Freigabe des Freeze-Protokolls (`reports/freeze_protocol_cybench.md`) und Entscheidung über die Testjahre 2021–2023 **vor** dem Zero-Shot-Test.
- Optionaler EU-Zusatztest Leave-One-Year-Out (ohne Österreich, ohne Eingriff ins Modell) zur Trennung von Länder- und Jahres-Transfer.
- Optionale inhaltliche Sichtung der EL-Region-Jahre mit YAS > 4 und der Nullerträge.
