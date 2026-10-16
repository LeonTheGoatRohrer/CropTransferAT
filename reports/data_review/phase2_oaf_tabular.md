# Datenkritik Phase 2.4 / 3.4a – One Acre Fund als Tabellendatensatz

Datum: 2026-10-16. Code: `src/croptransfer/oaf_analysis.py` (Tests: `tests/test_oaf_analysis.py`, 12 Tests; gesamte Suite 132 grün). Reproduktion: `python -m croptransfer.oaf_analysis` (ca. 15 min mit 14 Prozessen) schreibt `results/2026-10-16_oaf_tabular/` (`metrics.json`, `config.yaml`, `oaf_analysis_config.json`, `git.txt`, `report_tables.md`, CSV) und `reports/figures/phase2_oaf_{groups,shap,damage}.png`. Ein zweiter Lauf lieferte bitgleiche Modell-, SHAP- und Schadenszahlen.

Grundlage: DECISIONS 2026-10-15 (nur Tabelle, keine Satellitenkurven, nicht im Hauptmodell; `RY_nb`-Gruppe `cz × season × year`, ≥ 10 andere Felder; exakte Position = alle fünf `soil_*`-Spalten). **Keine Satelliten-/GEE-Daten, keine österreichischen Daten.** **Die Ergebnisse gelten für Kleinbauern und Kleinbäuerinnen in Subsahara-Afrika und sind nicht auf Österreich übertragbar** (Dünger-, Saatgut- und Dichteangaben gibt es dort nicht).

## 1. Fragen und Antworten in Kürze

**A) Wie viel erklärt gemeldete Bewirtschaftung im Vergleich zu Boden, Wetter und Schäden?** (n = 10 204 Felder, 76 Gruppen, 15 Land-Jahre als Cluster; Ziel `RY_nb`; Werte = Leave-One-Country-Out (LOCO), außerhalb des Trainings, 95-%-Cluster-Bootstrap-KI; jeweils LightGBM / Ridge)
- **Bewirtschaftung ist die einzige Gruppe mit Vorhersagekraft, und sie ist klein:** ρ = 0,25 [0,19; 0,30] / 0,30 [0,27; 0,34], R² = 0,05 [0,01; 0,07] / 0,07 [0,03; 0,10]. Leave-One-Year-Out (LOYO): ρ 0,31 [0,27; 0,36] / 0,33 [0,30; 0,36], R² 0,09 [0,05; 0,11] / 0,10 [0,08; 0,12]. Der RMSE sinkt gegenüber B0 (Trainingsmittel, RMSE 0,584) um 0,014 bis 0,030, also um ca. 2–5 %. **Über 90 % der Unterschiede zwischen Feldern bleiben unerklärt** (auch wegen Messrauschen: zwei Erntekästen je Feld).
- **Boden (`soil_*`), Wetter (CHIRP-Spalten der Tabelle) und gemeldete Schäden erklären außerhalb des Trainings nichts:** LOCO-ρ Boden −0,02 [−0,07; 0,01] / −0,08 [−0,14; −0,03], Wetter −0,03 / −0,06, Schäden −0,04 / −0,06; R² ≤ 0 (LightGBM Boden −0,06 [−0,08; −0,04], Wetter −0,07 [−0,13; −0,03], Schäden −0,04 [−0,10; −0,01], also schlechter als B0). LOYO: Boden ρ 0,08 [0,01; 0,14] bei R² 0,00 – das ist Standort-Wiedererkennung (3.3), keine Erklärung.
- **Gruppen-Ablation** (R² „alle“ minus „alle ohne X“, LOCO): ohne Bewirtschaftung 0,10 [0,05; 0,13] / 0,08 [0,05; 0,11]; ohne Boden 0,01 [−0,00; 0,03] / −0,02 [−0,03; −0,01]; ohne Wetter und ohne Schäden 0 (KI enthalten 0). „Alle“ ist nicht besser als Bewirtschaftung allein (R²-Differenz −0,01 [−0,04; 0,01] / −0,02 [−0,04; 0,01]).
- **Innerhalb der Bewirtschaftung** (LOCO-ρ Ridge; LightGBM ähnlich oder schwächer): Dünger 0,20 [0,17; 0,24], Saatgut/Sorte 0,13 [0,07; 0,20], Saatdichte/-termin 0,16 [0,06; 0,24] (LightGBM 0,20 [0,10; 0,30]), Unkraut/Pflanzenschutz ≈ 0. Kein Einzelblock erreicht R² > 0,05. SHAP (LOCO, nur Erklärung, mittleres |SHAP|): `hybrid` 0,055, `pl_m2` 0,047, `pesticide` 0,033, `plant_date_dev` 0,028, `N_kg_ha` 0,026; Summe je Gruppe Bewirtschaftung 0,257, Wetter 0,052, Boden 0,031, Schäden 0,002.
- **Innerhalb Land-Jahr** (Jahres-/Orts-Proxy-Check): Median-ρ Bewirtschaftung 0,28 / 0,29 (LOCO), „alle“ 0,26 / 0,25, Boden −0,01 / −0,08 – gleiches Bild, die gepoolten Werte sind kein Niveau-Effekt zwischen Ländern.
- **Label-Shuffle** (5 Permutationen × 2 Modelle × 2 Splits, Gruppe „alle“): |ρ| ≤ 0,03, R² zwischen −0,01 und 0,00, RMSE−B0 ≥ −0,000. Bestanden mit Anmerkung: 5 von 20 KI schließen die 0 knapp aus (Erwartung ca. 1); vermutliche Ursache sind die je Fold verschiedenen Trainingsmittel und zu schmale Cluster-KI bei permutiertem Ziel; die Größe liegt rund 10-fach unter den echten Werten.

**B) Phase 3.4a – hängen gemeldete Schäden mit niedrigem RY_nb zusammen?** Land-Jahre mit Anteil exakt 0 oder ohne Antwort gelten als „nicht gefragt“ und gehen als fehlend ein. „Niedrig“ = RY_nb < 0,85, insgesamt 38,8 % der Felder (viel häufiger als im US-Längsschnitt, weil RY_nb Unterschiede zwischen Kleinfeldern misst, nicht Jahresstress).

| Schaden | n (Land-Jahre) | gemeldet | Anteil < 0,85 mit | ohne | OR roh | OR Mantel-Haenszel (Strata = RY_nb-Gruppe) |
|---|---|---|---|---|---|---|
| pest (Schädling, inkl. Dürre) | 8891 (12) | 42,0 % | 0,39 [0,36; 0,42] | 0,38 [0,35; 0,42] | 1,06 [0,85; 1,21] | 1,07 [0,75; 1,19] |
| disease (inkl. Dürre) | 7034 (7) | 4,4 % | 0,50 [0,33; 0,63] | 0,38 [0,37; 0,40] | 1,63 [0,84; 2,58] | 1,41 [0,82; 2,13] |
| striga | 2344 (4) | 30,8 % | 0,44 [0,27; 0,54] | 0,34 [0,29; 0,44] | 1,52 [0,53; 2,19] | 1,54 [1,52; 2,16] (nur 4 Cluster, KI unzuverlässig) |
| water_excess (Nässe) | 8607 (10) | 11,0 % | 0,42 [0,37; 0,46] | 0,39 [0,36; 0,41] | 1,15 [0,88; 1,36] | 1,19 [0,93; 1,43] |

- Alle vier Odds Ratios liegen über 1, aber **kein roher KI schließt 1 aus**: ein schwacher Zusammenhang (OR 1,1–1,6) ist möglich, ein starker nicht. `pest` (42 % Meldungen) hängt praktisch nicht mit niedrigem RY_nb zusammen, was auf Meldungsrauschen und mögliche Gegenmaßnahmen (`pesticide`) hindeutet. Meldungen sind subjektiv, Rückwärtsursache ist möglich (wer wenig erntet, nennt einen Grund). Der Zusammenhang ist **keine Ursachenaussage**.
- **Nicht prüfbar mit „nur Tabelle“:** ob „Schädling/Krankheit“ aus Satellit + Wetter von anderen Ursachen **unterscheidbar** ist (Phase 3.4a, zweiter Teil). Dafür fehlen Satellitenkurven und tägliches Wetter. **Trockenheit steckt laut Datenbeschreibung in `pest`/`disease`, Hagel hat keine Spalte**; damit sind auch die vorab festgelegten Regeln „Trockenstress“ und „abrupter Schaden (Hagel)“ nicht gegen echte Ursachen prüfbar. Die ERA5-Regeln (RZWSI, Hitzetage, Frühjahrsniederschlag) wurden nicht ausgewertet (kein GEE). Die Demo darf aus diesen Daten keine Kategorie „Schädling/Krankheit möglich“ ableiten.
- **Explorativ** (keine vorab festgelegte Regel, kein Schwellenwert): `water_excess` vs. CHIRP-Niederschlagsanomalie (z innerhalb Klimazone × Saison): ρ = 0,17 [−0,02; 0,22] (Saison), 0,13 [−0,08; 0,18] (früh); `pest` vs. Niederschlag zur Blüte −0,14 [−0,28; 0,11]; `disease` ≈ 0. Die Richtung passt zu „Nässe“, alle KI enthalten aber 0.

**C) Konfundierung:** siehe 3.3.

## 2. Methode (vor der Auswertung festgelegt, Abweichung markiert)
- Daten: One Acre Fund, exakte Position (alle fünf `soil_*`), `RY_nb` = Ertrag / Median der **anderen** Felder der Gruppe `cz × season × year` (`targets.ry_nb`, ≥ 10 andere). 10 332 exakte Felder → **10 204** mit `RY_nb` (128 in zu kleinen Gruppen). Länder: Kenia 7004, Tansania 1698, Sambia 699, Ruanda 444, Burundi 135, Nigeria 115, Uganda 109; 15 Land-Jahre (Kenia 5, Tansania 3, Ruanda 2, Sambia 2, Burundi/Nigeria/Uganda je 1).
- Merkmalsgruppen: Dünger (N, P, K, Kompost, Kompostmenge, Mist, Dünger im Pflanzloch, Kalk); Saatgut/Sorte (Hybrid ja/nein, Hybridtyp, Reife, Freigabejahr, 6 Toleranzen); Saatdichte/-termin (`pl_m2`, `row_spacing`, `plant_date_dev`); Unkraut/Pflanzenschutz (`weeding`, `pesticide`); Boden (5 `soil_*`); Wetter (CHIRP `season_prec`, `_1..3`); Schäden (4 Spalten, „nicht gefragt“ = NaN); Kontrollgruppe Ort/Gelände (`lon`, `lat`, `elev`, `twi`), nicht in „alle“. „Alle“ = Bewirtschaftung + Boden + Wetter + Schäden (die Entscheidung nennt „Bewirtschaftung vs. Wetter/Boden“, deshalb Wetter ergänzt). `plant_doy` (absoluter Aussaattag) ist ausgelassen: Orts-/Saison-Kennung; `plant_date_dev` ist die Abweichung vom Klimazonenmittel.
- Modelle: LightGBM (`max_depth` 3, 8 Blätter, Lernrate 0,05) und Ridge (Mittelwert-Imputation, Standardisierung, Begrenzung auf ±5 SD; Imputer/Scaler nur im Training). Hyperparameter (LightGBM: 50–400 Bäume × `min_child_samples` 20/100; Ridge: α 1–10 000) **nur verschachtelt**: je äußerem Fold ein innerer Leave-One-Unit-Out über die Trainings-Länder bzw. -Jahre, Auswahl nach RMSE. B0 = Trainingsmittel von `RY_nb`.
- Validierung: LOCO (7 Folds) und LOYO (6 Folds, 2022 = nur Nigeria). Metriken: Spearman ρ, R² (gegen das Mittel der gepoolten Testwerte), RMSE auf den gepoolten Out-of-Fold-Vorhersagen; **95-%-Perzentil-KI per Cluster-Bootstrap** (Cluster = Land × Jahr, 1000 Ziehungen, Seed 42, gleiche Ziehungen für alle Modelle, Differenzen gepaart).
- **Abweichung nach einem Entwicklungslauf:** Ridge ohne Begrenzung sagte für Ruanda `RY_nb` bis 9,4 voraus (seltene Kategorie, standardisiert; Ruanda-R² −2,6). Die ±5-SD-Begrenzung gilt für alle Ridge-Läufe gleich; sonst wurde nichts an den Ergebnissen der äußeren Folds abgestimmt.

## 3. Datenkritik (AGENTS.md §3)

### 3.1 Repräsentativität (Auswahl-Bias)
- *Geprüft wie:* Zählung je Land/Jahr; Ergebnis je gehaltenes Land; Abgleich mit N.1 der Phase-0-Datenkritik.
- *Befund:* Der GPS-Filter lässt 70 % der Felder; **68,6 % der Analysefelder liegen in Kenia (7004 von 10 204; 5 der 15 Cluster)**, 16,6 % in Tansania. Ausgeschlossene Felder haben niedrigere Erträge und sind vermutlich Nicht-Programm-Betriebe; der Datensatz ist im Kern „Westkenia + etwas Tansania/Sambia“. Ergebnis je gehaltenes Land (LightGBM, „alle“): ρ Kenia 0,23 (n 7004), Tansania 0,26 (1698), Sambia 0,28 (699), Ruanda 0,19 (444; R² −0,35, das Wetter-SHAP ist dort mit 0,17 am höchsten), Burundi 0,41 (135), Uganda 0,36 (109), Nigeria 0,32 (115). Bei kleinen Ländern ist n immer anzugeben, die KI sind breit.
- *Zielverteilung:* `RY_nb` Median 1,00, Mittel 1,08, 1./99. Perzentil 0,00 / 2,84, Maximum 5,1; 153 Nullerträge (Totalausfälle bleiben im Ziel); 38,8 % unter 0,85. Die Autor:innen haben Ausreißer (Bonferroni-Test) und Dünger-/Dichtewerte jenseits 4 SD vor der Veröffentlichung entfernt, die Enden sind also gestutzt.
- *Fehlende Angaben je Land* (Anteil vorhanden): Saatgut/Sorte Burundi 8 %, Nigeria 8 %, Ruanda 8 %, Tansania 44 %, Kenia 64 %; Unkraut/Pflanzenschutz Burundi, Nigeria, Uganda 0 %; Schäden Burundi 0 %. LightGBM kann Fehlmuster lesen (Erhebungsdesign als Kennung), Ridge imputiert den Mittelwert. Die „nicht gefragt“-Land-Jahre je Schaden stehen in `metrics.json` (`data.damage_not_asked_country_years`).
- *Konsequenz:* Ergebnisse nicht als „Subsahara-Afrika“ verallgemeinern; die gepoolten Werte werden von Kenia dominiert.

### 3.2 Korrektheit
- *Wertebereiche:* Erträge 0–11 139 kg/ha, `RY_nb` 0–5,1; Feuchtebasis unbekannt (für `RY_nb` unerheblich). Booleans mit Fehlwerten werden als 0/1/NaN gelesen (Test).
- *Messnähe der Merkmale:* `pl_m2` und `row_spacing` wurden im Erntekasten **bei der Ernte gemessen**, sie sind keine reinen Eingaben (Pflanzenverluste durch Dürre oder Schädlinge verringern `pl_m2`). Dünger, Termin, Sorte, Kalk, Unkraut, Pflanzenschutz und Schäden sind **von Landwirt:innen gemeldet** (Erinnerungsfehler). `pesticide` ist laut Beschreibung meist ein Insektizid gegen den Herbstheerwurm.
- *Schadensspalten:* `pest`/`disease` enthalten Dürre, Hagel hat keine Spalte, `striga` ist zu 77 % leer. Land-Jahre mit Anteil exakt 0 oder ohne Antwort gelten als fehlend (Test `test_country_year_with_zero_share_is_treated_as_missing`).
- *Auflösungs-Mismatch:* Boden (WISE/iSDA-Raster) und CHIRP (≈ 5 km) beschreiben nicht das Einzelfeld; die Koordinaten sind auf 0,001° gerundet. Dass Boden und Wetter nichts erklären, heißt daher nicht „Boden/Wetter ist egal“, sondern „diese Tabellenspalten lösen es nicht auf“.

### 3.3 Scheinzusammenhänge und Konfundierung
- **Programmteilnahme (N.3):** Etwa die Hälfte der Felder gehört zu One-Acre-Fund-Kundschaft, die Spalte fehlt. Hybridsaatgut, Dünger, Pflanzloch-Düngung und Pflanzenschutz sind teils Teil des Programmpakets (`hybrid` ist das stärkste SHAP-Merkmal). „Bewirtschaftung erklärt 5–10 %“ enthält deshalb Programm vs. Nicht-Programm, Betriebsgröße, Wohlstand, Beratung und Feldlage; **kein Effekt von Dünger oder Sorte ist belegt**.
- **GPS-Filter (N.1):** Nur Felder mit exakter Position, v. a. Westkenia; Nicht-Teilnehmende haben vermutlich seltener GPS. Der Anteil der Bewirtschaftung in der Gesamtpopulation kann deshalb größer oder kleiner sein.
- **Orts-/Standort-Proxy:** In LOYO erkennen Modelle denselben Standort in anderen Jahren wieder (Boden ρ 0,08 [0,01; 0,14], Ort ρ 0,15 [0,09; 0,21] bei R² ≈ 0), in LOCO nicht (Boden −0,02, Ort 0,09 [0,02; 0,15] mit R² −0,03). 1254 exakte Felder teilen Punkt + Saison mit anderen; bei Länder- und Jahres-Folds bleiben sie im selben Fold.
- **`RY_nb`-Gruppe mischt Länder:** `cz` ist ein Klimazonen-Code und kommt in mehreren Ländern vor; **36 von 76 Gruppen enthalten mehrere Länder**. Bei LOCO fließen dann Erträge des gehaltenen Landes in die Zielwerte des Trainings ein (Zielleck, kein Merkmalsleck). *Gegenprobe* mit Gruppe `country × cz × season × year` (n = 10 115, 105 Gruppen, keine gemischte Gruppe): LOCO Bewirtschaftung ρ 0,27 [0,21; 0,32] / 0,29 [0,24; 0,33], R² 0,06 / 0,07; „alle“ ρ 0,25 / 0,27; Boden, Wetter, Schäden ρ ≈ 0. Gleiche Aussage, der Effekt ist unerheblich. Vorschlag: `country` in die Gruppe aufnehmen (neuer `DECISIONS.md`-Eintrag, Entscheidung beim Projektinhaber; die Festlegung vom 2026-10-15 blieb unverändert).
- **Jahres-Proxy:** `RY_nb` ist je Gruppe auf 1 normiert; Median-ρ innerhalb Land-Jahr entspricht den gepoolten Werten (A).
- **Label-Shuffle:** bestanden mit Anmerkung (A). **Adversarial Validation:** n/a, Trainings- und Testländer unterscheiden sich in LOCO per Definition. SHAP bei korrelierten Merkmalen (Dünger N/P, Hybrid/Reife/Toleranzen, Niederschlagsphasen) nur grob interpretierbar.

### 3.4 Leakage
- Hyperparameter nur im Training verschachtelt (Test `test_nested_cv_never_tunes_on_the_held_out_group`); Imputer, Scaler und B0 nur aus dem Training; Folds ohne Überlappung (Test `test_leave_one_group_out_has_no_overlap_and_covers_everything`).
- Zielleck bei LOCO durch gemischte `RY_nb`-Gruppen: quantifiziert, unerheblich (3.3). LOYO: `year` steckt in der Gruppe, kein Leck.
- Räumliche Nähe: In LOCO/LOYO liegen Test- und Trainingsfelder nie im selben Land bzw. Jahr; Standort-Wiedererkennung in LOYO siehe 3.3.
- **Österreich-Regel:** Es wurden keine österreichischen Daten ausgewertet oder genutzt, kein Freeze-Modell berührt, keine Satelliten-/GEE-Abfragen gestellt.

### 3.5 Ergebnis-Plausibilität
- Nichts ist „zu gut“ (R² ≤ 0,10). Nur Modelle mit Bewirtschaftung schlagen B0 (ΔRMSE LOCO Bewirtschaftung −0,014 [−0,023; −0,003] / −0,022 [−0,031; −0,011]); Boden, Wetter und Schäden sind schlechter als B0 oder gleich.
- Fallstudien (3 beste/3 schlechteste Felder): n/a für diese Tabellenanalyse; Ersatz: Ergebnis je gehaltenes Land (3.1) und SHAP je Land (`metrics.json`: `shap.by_country_group`).
- Grenzen: 15 Cluster, ein Land stellt 69 % der Daten, KI mit wenigen Clustern sind unscharf (besonders `striga` mit 4 und `disease` mit 7 Clustern).

### 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Die Analyse ist technisch sauber (verschachtelt, ohne Überlappung, Kontrolltest bestanden), die Aussagen sind aber schmal: gemeldete Bewirtschaftung erklärt etwa 5–10 % der Unterschiede zwischen Feldern, Boden, Wetter-Spalten und Schäden nichts; die Schadensmeldungen hängen höchstens schwach mit niedrigem `RY_nb` zusammen. Einschränkungen für die Doku: Programmteilnahme als unbekannter Störfaktor, Westkenia-Dominanz, selbstberichtete Daten, gemischte `RY_nb`-Gruppen (unerheblich), Schädlings-/Krankheits-Unterscheidbarkeit **nicht prüfbar**. Kein ⛔.

## 4. Offene Punkte (außerhalb dieses Auftrags)
- `DECISIONS.md`: Wetter-Gruppe und `plant_doy`-Ausschluss; Ridge-Begrenzung ±5 SD; `country` in der `RY_nb`-Gruppe (Sensitivität).
- `reports/results.md`, `CHANGELOG.md`, `SUPPORT.md` aktualisieren; nichts wurde committet.
- Die Konfiguration steht als `DEFAULTS` im Modul (ein Abschnitt `oaf_analysis:` in `config.yaml` überschreibt sie), weil `config.yaml` nicht geändert werden sollte.

## Anhang: Tabellen aus `results/2026-10-16_oaf_tabular/report_tables.md`

#### LOCO: Merkmalsgruppen (n = 10204, Cluster = 15)

| Merkmalssatz | LightGBM ρ | LightGBM R² | LightGBM RMSE−B0 | Ridge ρ | Ridge R² | Ridge RMSE−B0 |
|---|---|---|---|---|---|---|
| Dünger | 0,15 [0,11; 0,23] | -0,01 [-0,04; 0,02] | 0,001 [-0,007; 0,012] | 0,20 [0,17; 0,24] | 0,04 [0,02; 0,05] | -0,011 [-0,015; -0,006] |
| Saatgut/Sorte | 0,13 [0,06; 0,20] | 0,02 [-0,02; 0,05] | -0,007 [-0,017; 0,004] | 0,13 [0,07; 0,20] | 0,04 [0,01; 0,06] | -0,011 [-0,019; -0,004] |
| Saatdichte/-termin | 0,20 [0,10; 0,30] | 0,04 [-0,00; 0,08] | -0,012 [-0,023; 0,000] | 0,16 [0,06; 0,24] | 0,02 [-0,01; 0,04] | -0,006 [-0,013; 0,002] |
| Unkraut/Pflanzenschutz | 0,02 [-0,01; 0,06] | -0,04 [-0,06; -0,02] | 0,010 [0,004; 0,016] | -0,01 [-0,06; 0,04] | -0,00 [-0,02; -0,00] | 0,001 [-0,000; 0,003] |
| Bewirtschaftung (alle) | 0,25 [0,19; 0,30] | 0,05 [0,01; 0,07] | -0,014 [-0,023; -0,003] | 0,30 [0,27; 0,34] | 0,07 [0,03; 0,10] | -0,022 [-0,031; -0,011] |
| Boden | -0,02 [-0,07; 0,01] | -0,06 [-0,08; -0,04] | 0,016 [0,010; 0,021] | -0,08 [-0,14; -0,03] | -0,01 [-0,02; -0,01] | 0,004 [0,002; 0,006] |
| Wetter (CHIRP) | -0,03 [-0,09; 0,02] | -0,07 [-0,13; -0,03] | 0,020 [0,007; 0,036] | -0,06 [-0,12; -0,00] | -0,03 [-0,04; -0,01] | 0,007 [0,002; 0,012] |
| Schäden | -0,04 [-0,11; -0,00] | -0,04 [-0,10; -0,01] | 0,012 [0,003; 0,026] | -0,06 [-0,11; 0,00] | -0,00 [-0,02; -0,00] | 0,001 [-0,000; 0,003] |
| Ort/Gelände (Kontrolle) | 0,09 [0,02; 0,15] | -0,03 [-0,07; -0,00] | 0,007 [-0,001; 0,018] | -0,09 [-0,15; -0,02] | -0,01 [-0,02; -0,00] | 0,002 [0,001; 0,004] |
| alle (M+B+W+S) | 0,23 [0,17; 0,28] | 0,04 [-0,02; 0,07] | -0,011 [-0,022; 0,007] | 0,26 [0,23; 0,30] | 0,06 [0,03; 0,08] | -0,017 [-0,025; -0,008] |
| alle ohne Bewirtschaftung | -0,04 [-0,09; 0,01] | -0,07 [-0,09; -0,04] | 0,018 [0,011; 0,025] | -0,10 [-0,16; -0,04] | -0,02 [-0,03; -0,02] | 0,006 [0,004; 0,008] |
| alle ohne Boden | 0,22 [0,16; 0,27] | 0,02 [-0,05; 0,06] | -0,007 [-0,021; 0,015] | 0,29 [0,25; 0,33] | 0,07 [0,04; 0,10] | -0,022 [-0,031; -0,013] |
| alle ohne Wetter | 0,22 [0,17; 0,28] | 0,04 [0,00; 0,06] | -0,012 [-0,020; -0,001] | 0,27 [0,25; 0,30] | 0,07 [0,04; 0,09] | -0,020 [-0,027; -0,013] |
| alle ohne Schäden | 0,23 [0,17; 0,28] | 0,04 [-0,02; 0,07] | -0,011 [-0,021; 0,005] | 0,26 [0,23; 0,30] | 0,06 [0,03; 0,08] | -0,018 [-0,026; -0,008] |

#### LOYO: Merkmalsgruppen (n = 10204, Cluster = 15)

| Merkmalssatz | LightGBM ρ | LightGBM R² | LightGBM RMSE−B0 | Ridge ρ | Ridge R² | Ridge RMSE−B0 |
|---|---|---|---|---|---|---|
| Dünger | 0,17 [0,09; 0,24] | 0,02 [-0,03; 0,04] | -0,004 [-0,013; 0,009] | 0,22 [0,20; 0,25] | 0,04 [0,03; 0,05] | -0,013 [-0,016; -0,010] |
| Saatgut/Sorte | 0,22 [0,16; 0,27] | 0,05 [0,02; 0,07] | -0,015 [-0,023; -0,005] | 0,19 [0,12; 0,25] | 0,05 [0,02; 0,07] | -0,014 [-0,022; -0,005] |
| Saatdichte/-termin | 0,20 [0,11; 0,29] | 0,04 [0,00; 0,07] | -0,012 [-0,021; -0,002] | 0,19 [0,10; 0,29] | 0,03 [-0,00; 0,06] | -0,009 [-0,018; -0,000] |
| Unkraut/Pflanzenschutz | 0,05 [-0,00; 0,10] | -0,00 [-0,02; 0,01] | 0,000 [-0,003; 0,004] | 0,07 [0,02; 0,12] | 0,00 [-0,00; 0,01] | -0,001 [-0,003; 0,001] |
| Bewirtschaftung (alle) | 0,31 [0,27; 0,36] | 0,09 [0,05; 0,11] | -0,026 [-0,033; -0,015] | 0,33 [0,30; 0,36] | 0,10 [0,08; 0,12] | -0,030 [-0,036; -0,023] |
| Boden | 0,08 [0,01; 0,14] | 0,00 [-0,01; 0,01] | -0,001 [-0,005; 0,003] | -0,00 [-0,07; 0,06] | -0,00 [-0,01; 0,00] | 0,001 [-0,000; 0,003] |
| Wetter (CHIRP) | -0,01 [-0,05; 0,03] | -0,05 [-0,08; -0,02] | 0,015 [0,005; 0,023] | 0,05 [0,01; 0,11] | 0,00 [-0,01; 0,00] | -0,000 [-0,001; 0,002] |
| Schäden | -0,03 [-0,12; 0,03] | -0,03 [-0,09; -0,01] | 0,010 [0,002; 0,024] | -0,03 [-0,10; 0,05] | -0,00 [-0,01; 0,00] | 0,001 [-0,000; 0,002] |
| Ort/Gelände (Kontrolle) | 0,15 [0,09; 0,21] | 0,01 [-0,02; 0,04] | -0,003 [-0,012; 0,007] | 0,05 [-0,06; 0,14] | -0,00 [-0,02; 0,01] | 0,001 [-0,002; 0,007] |
| alle (M+B+W+S) | 0,30 [0,26; 0,34] | 0,08 [0,05; 0,09] | -0,023 [-0,029; -0,016] | 0,31 [0,28; 0,34] | 0,08 [0,05; 0,11] | -0,025 [-0,032; -0,017] |
| alle ohne Bewirtschaftung | 0,01 [-0,03; 0,07] | -0,02 [-0,04; -0,01] | 0,006 [0,002; 0,010] | 0,01 [-0,05; 0,07] | -0,00 [-0,01; 0,00] | 0,001 [-0,000; 0,003] |
| alle ohne Boden | 0,29 [0,25; 0,33] | 0,07 [0,05; 0,09] | -0,022 [-0,029; -0,014] | 0,32 [0,29; 0,35] | 0,09 [0,06; 0,11] | -0,028 [-0,035; -0,020] |
| alle ohne Wetter | 0,31 [0,27; 0,34] | 0,08 [0,06; 0,10] | -0,024 [-0,031; -0,017] | 0,32 [0,29; 0,35] | 0,09 [0,06; 0,11] | -0,028 [-0,034; -0,020] |
| alle ohne Schäden | 0,30 [0,26; 0,34] | 0,08 [0,05; 0,09] | -0,023 [-0,029; -0,016] | 0,32 [0,29; 0,35] | 0,09 [0,06; 0,11] | -0,026 [-0,034; -0,018] |

#### Ablation: alle − (alle ohne X) = Beitrag von X (Differenz von R², 95-%-KI)

| Split/Modell | alle - ohne_M | alle - ohne_B | alle - ohne_W | alle - ohne_S |
|---|---|---|---|---|
| LOCO/lgbm | 0,10 [0,05; 0,13] | 0,01 [-0,00; 0,03] | -0,00 [-0,03; 0,02] | -0,00 [-0,00; 0,00] |
| LOCO/ridge | 0,08 [0,05; 0,11] | -0,02 [-0,03; -0,01] | -0,01 [-0,02; 0,00] | -0,00 [-0,01; 0,00] |
| LOYO/lgbm | 0,10 [0,07; 0,12] | 0,00 [-0,00; 0,01] | -0,01 [-0,01; 0,00] | 0,00 [-0,00; 0,00] |
| LOYO/ridge | 0,09 [0,06; 0,11] | -0,01 [-0,02; -0,00] | -0,01 [-0,02; 0,00] | -0,00 [-0,01; 0,00] |

#### alle − Einzelgruppe = was die Gruppe allein nicht erreicht (Differenz von R², 95-%-KI)

| Split/Modell | alle - M | alle - B | alle - W | alle - S | alle - ORT |
|---|---|---|---|---|---|
| LOCO/lgbm | -0,01 [-0,04; 0,01] | 0,09 [0,02; 0,13] | 0,11 [0,06; 0,15] | 0,08 [0,01; 0,13] | 0,06 [0,01; 0,11] |
| LOCO/ridge | -0,02 [-0,04; 0,01] | 0,07 [0,04; 0,10] | 0,08 [0,06; 0,11] | 0,06 [0,03; 0,09] | 0,06 [0,03; 0,09] |
| LOYO/lgbm | -0,01 [-0,02; 0,01] | 0,07 [0,05; 0,10] | 0,13 [0,09; 0,15] | 0,11 [0,08; 0,15] | 0,07 [0,03; 0,10] |
| LOYO/ridge | -0,02 [-0,03; -0,00] | 0,09 [0,06; 0,11] | 0,08 [0,06; 0,11] | 0,09 [0,06; 0,11] | 0,09 [0,06; 0,12] |

#### Median-ρ innerhalb Land-Jahr (≥ 30 Felder; [min; max] über Land-Jahre)

| Merkmalssatz | LOCO LightGBM | LOCO Ridge | LOYO LightGBM | LOYO Ridge |
|---|---|---|---|---|
| Dünger | 0,18 [-0,06; 0,35], k=15 | 0,23 [-0,07; 0,36], k=15 | 0,16 [-0,24; 0,34], k=15 | 0,25 [-0,07; 0,36], k=15 |
| Saatgut/Sorte | 0,19 [-0,04; 0,34], k=15 | 0,19 [-0,01; 0,30], k=15 | 0,25 [0,07; 0,39], k=15 | 0,22 [0,06; 0,32], k=15 |
| Saatdichte/-termin | 0,22 [-0,08; 0,42], k=15 | 0,16 [-0,14; 0,34], k=15 | 0,25 [-0,07; 0,41], k=15 | 0,18 [-0,12; 0,45], k=15 |
| Unkraut/Pflanzenschutz | 0,09 [0,01; 0,28], k=11 | 0,09 [-0,03; 0,22], k=11 | 0,10 [-0,14; 0,28], k=11 | 0,10 [0,03; 0,22], k=11 |
| Bewirtschaftung (alle) | 0,28 [0,10; 0,38], k=15 | 0,29 [0,06; 0,44], k=15 | 0,31 [0,05; 0,44], k=15 | 0,32 [0,08; 0,43], k=15 |
| Boden | -0,01 [-0,23; 0,16], k=15 | -0,08 [-0,20; 0,31], k=15 | 0,08 [-0,32; 0,21], k=15 | 0,00 [-0,27; 0,32], k=15 |
| Wetter (CHIRP) | -0,01 [-0,22; 0,12], k=15 | -0,06 [-0,15; 0,36], k=15 | 0,02 [-0,24; 0,10], k=15 | 0,07 [-0,11; 0,34], k=15 |
| Schäden | -0,00 [-0,22; 0,18], k=14 | -0,00 [-0,23; 0,17], k=14 | 0,01 [-0,22; 0,13], k=14 | -0,00 [-0,23; 0,07], k=14 |
| Ort/Gelände (Kontrolle) | 0,12 [-0,19; 0,34], k=15 | -0,08 [-0,26; 0,30], k=15 | 0,15 [-0,21; 0,32], k=15 | 0,11 [-0,21; 0,35], k=15 |
| alle (M+B+W+S) | 0,26 [0,09; 0,41], k=15 | 0,25 [0,04; 0,45], k=15 | 0,32 [0,08; 0,41], k=15 | 0,31 [0,09; 0,43], k=15 |
| alle ohne Bewirtschaftung | -0,03 [-0,18; 0,24], k=15 | -0,06 [-0,21; 0,20], k=15 | 0,06 [-0,23; 0,20], k=15 | -0,00 [-0,23; 0,23], k=15 |
| alle ohne Boden | 0,26 [0,10; 0,41], k=15 | 0,27 [0,08; 0,45], k=15 | 0,30 [0,08; 0,42], k=15 | 0,31 [0,08; 0,45], k=15 |
| alle ohne Wetter | 0,24 [0,10; 0,40], k=15 | 0,24 [0,08; 0,44], k=15 | 0,33 [0,09; 0,43], k=15 | 0,31 [0,09; 0,45], k=15 |
| alle ohne Schäden | 0,26 [0,09; 0,43], k=15 | 0,25 [0,08; 0,45], k=15 | 0,33 [0,08; 0,41], k=15 | 0,31 [0,09; 0,45], k=15 |

#### Label-Shuffle (alle, permutiertes Ziel)

| Lauf | ρ | R² | RMSE−B0 |
|---|---|---|---|
| LOCO/lgbm/seed42 | 0,02 [0,00; 0,03] | -0,00 [-0,00; -0,00] | 0,001 [0,000; 0,001] |
| LOCO/lgbm/seed43 | -0,01 [-0,03; 0,00] | -0,01 [-0,01; -0,01] | 0,002 [0,002; 0,003] |
| LOCO/lgbm/seed44 | -0,01 [-0,03; 0,02] | -0,01 [-0,01; -0,00] | 0,002 [0,001; 0,003] |
| LOCO/lgbm/seed45 | -0,00 [-0,02; 0,01] | -0,01 [-0,02; -0,00] | 0,003 [0,001; 0,004] |
| LOCO/lgbm/seed46 | 0,00 [-0,01; 0,02] | -0,00 [-0,01; -0,00] | 0,001 [0,001; 0,002] |
| LOCO/ridge/seed42 | 0,02 [-0,00; 0,03] | 0,00 [-0,00; 0,00] | -0,000 [-0,000; 0,000] |
| LOCO/ridge/seed43 | -0,02 [-0,04; -0,01] | -0,00 [-0,00; -0,00] | 0,001 [0,001; 0,001] |
| LOCO/ridge/seed44 | -0,01 [-0,04; 0,01] | -0,00 [-0,00; 0,00] | 0,000 [-0,000; 0,001] |
| LOCO/ridge/seed45 | 0,00 [-0,02; 0,03] | -0,00 [-0,00; 0,00] | 0,000 [-0,000; 0,001] |
| LOCO/ridge/seed46 | 0,01 [0,00; 0,03] | -0,00 [-0,00; 0,00] | 0,000 [-0,000; 0,001] |
| LOYO/lgbm/seed42 | 0,01 [-0,02; 0,02] | -0,00 [-0,01; -0,00] | 0,001 [0,000; 0,003] |
| LOYO/lgbm/seed43 | -0,02 [-0,03; 0,00] | -0,00 [-0,01; -0,00] | 0,001 [0,000; 0,002] |
| LOYO/lgbm/seed44 | 0,01 [-0,01; 0,02] | -0,00 [-0,01; -0,00] | 0,001 [0,000; 0,001] |
| LOYO/lgbm/seed45 | 0,01 [-0,01; 0,03] | -0,00 [-0,01; -0,00] | 0,001 [-0,000; 0,001] |
| LOYO/lgbm/seed46 | 0,01 [-0,01; 0,03] | -0,00 [-0,01; -0,00] | 0,001 [0,000; 0,002] |
| LOYO/ridge/seed42 | -0,02 [-0,03; -0,00] | -0,00 [-0,00; -0,00] | 0,001 [0,000; 0,001] |
| LOYO/ridge/seed43 | -0,01 [-0,03; 0,00] | -0,00 [-0,00; -0,00] | 0,000 [0,000; 0,001] |
| LOYO/ridge/seed44 | -0,01 [-0,03; 0,00] | -0,00 [-0,00; -0,00] | 0,000 [0,000; 0,001] |
| LOYO/ridge/seed45 | 0,00 [-0,02; 0,02] | -0,00 [-0,00; -0,00] | 0,000 [-0,000; 0,001] |
| LOYO/ridge/seed46 | 0,03 [0,01; 0,04] | 0,00 [-0,00; 0,00] | -0,000 [-0,000; 0,000] |

#### SHAP (LOCO, LightGBM, alle): mittleres |SHAP| je Gruppe / Top-10-Merkmale

| Bewirtschaftung | Wetter (Tabelle) | Boden | Schäden |
|---|---|---|---|
| 0,257 | 0,052 | 0,031 | 0,002 |

hybrid (0,055), pl_m2 (0,047), pesticide (0,033), plant_date_dev (0,028), N_kg_ha (0,026), P_kg_ha (0,022), season_prec (0,022), season_prec_1 (0,015), soil_pH (0,013), fert_in_hole (0,013)

#### Schäden vs. RY_nb < 0,85

| Schaden | n (Länder-Jahre) | gemeldet | Anteil <0,85 mit | ohne | OR roh | OR Mantel-Haenszel |
|---|---|---|---|---|---|---|
| pest | 8891 (12) | 3735 (42,0 %) | 0,39 [0,36; 0,42] | 0,38 [0,35; 0,42] | 1,06 [0,85; 1,21] | 1,07 [0,75; 1,19] |
| disease | 7034 (7) | 308 (4,4 %) | 0,50 [0,33; 0,63] | 0,38 [0,37; 0,40] | 1,63 [0,84; 2,58] | 1,41 [0,82; 2,13] |
| striga | 2344 (4) | 722 (30,8 %) | 0,44 [0,27; 0,54] | 0,34 [0,29; 0,44] | 1,52 [0,53; 2,19] | 1,54 [1,52; 2,16] |
| water_excess | 8607 (10) | 947 (11,0 %) | 0,42 [0,37; 0,46] | 0,39 [0,36; 0,41] | 1,15 [0,88; 1,36] | 1,19 [0,93; 1,43] |

#### Explorativ: Schaden vs. CHIRP-Niederschlagsanomalie (Spearman ρ)

| Paar | n | ρ |
|---|---|---|
| water_excess~z(season_prec) | 8582 | 0,17 [-0,02; 0,22] |
| water_excess~z(season_prec_1) | 8582 | 0,13 [-0,08; 0,18] |
| pest~z(season_prec_2) | 8834 | -0,14 [-0,28; 0,11] |
| disease~z(season_prec_2) | 7009 | -0,06 [-0,11; 0,05] |
| pest~z(season_prec_3) | 8834 | -0,05 [-0,15; 0,09] |
| disease~z(season_prec_3) | 7009 | -0,03 [-0,07; 0,02] |

#### Sensitivität: RY_nb-Gruppe mit Land (country × cz × season × year), LOCO

n = 10115

| Merkmalssatz | LightGBM ρ | LightGBM R² | Ridge ρ | Ridge R² |
|---|---|---|---|---|
| Bewirtschaftung (alle) | 0,27 [0,21; 0,32] | 0,06 [0,03; 0,08] | 0,29 [0,24; 0,33] | 0,07 [0,04; 0,09] |
| Boden | 0,00 [-0,03; 0,02] | -0,01 [-0,02; -0,01] | 0,02 [-0,01; 0,04] | -0,00 [-0,00; 0,00] |
| Wetter (CHIRP) | -0,02 [-0,06; 0,01] | -0,01 [-0,03; 0,00] | -0,02 [-0,05; 0,01] | -0,00 [-0,01; 0,00] |
| Schäden | -0,00 [-0,03; 0,03] | -0,01 [-0,02; -0,00] | 0,00 [-0,03; 0,04] | -0,00 [-0,00; 0,00] |
| Ort/Gelände (Kontrolle) | 0,03 [-0,02; 0,06] | -0,02 [-0,03; -0,01] | 0,00 [-0,02; 0,03] | -0,00 [-0,00; 0,00] |
| alle (M+B+W+S) | 0,25 [0,19; 0,31] | 0,04 [0,03; 0,07] | 0,27 [0,22; 0,32] | 0,06 [0,03; 0,08] |
