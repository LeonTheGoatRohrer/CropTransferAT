# Datenkritik Phase 2 (Aufgabe 3) / Phase 3 (Aufgabe 3) – Innerhalb des Feldes

Datum: 2026-10-16 · Prüfliste nach `AGENTS.md` §3 · Code `src/croptransfer/within_field.py` (`python -m croptransfer.within_field`) · Ergebnisse `results/2026-10-16_within_field/` (metrics.json, config.yaml, within_field_config.json, git.txt, Tabellen) · Abbildungen `reports/figures/phase2_within_field_maps.png`, `phase2_within_field_rho.png`.

Frage: Welche Feldteile bringen weniger – und hängt das am Satellitenbild, am Gelände oder am Jahr? Nur BARC, Sentinel-2-Basis, 2017–2021. Keine österreichischen Daten verwendet.

## Was gerechnet wurde

- 41 BARC-Feld-Jahre (27 Felder; 2017: 4, 2018: 4, 2019: 11, 2020: 10, 2021: 12), 23 912 Ertragspixel (10 m) innerhalb der −10-m-gepufferten Feldgeometrie (von 32 671 Punkten; 73,2 % bleiben). Median 532 Pixel je Feld-Jahr (Minimum 217).
- Relativer Pixel-Ertrag = Pixel / Mittel der behaltenen Pixel desselben Feld-Jahres. Problemzone = relativer Pixel-Ertrag < 0,85. Medianer Anteil Problemzone je Feld-Jahr 27,5 %; jedes Feld-Jahr hat Problempixel; Variationskoeffizient des relativen Ertrags im Median 0,26 (0,08–0,53).
- GEE: S2 SR Harmonized + Cloud Score+ (cs_cdf ≥ 0,60), NDVI (B8A/B4), NDRE (B8A/B5), Median-Komposite je Pixel in drei Fenstern (15.6.–15.7., 16.7.–15.8., 16.8.–15.9.; Ende = Stichtag, einschließlich, wie `features.py`), Copernicus GLO30: Höhe, Neigung, TPI (150-m-Kreis). Median 5 klare Bilder je Pixel und Fenster (Minimum der Feld-Jahr-Mediane 2–3); kein Feld-Jahr fällt durch den Filter (≥ 50 Pixel, ≥ 1 klares Bild). Keine Extraktionsfehler (`data/interim/pixels/_errors.log` nicht angelegt).
- Alle KI: 95 %-Bootstrap über **Feld-Jahre** (1000×, Seed 42); als Sensitivität auch über Felder (Cluster).

## Kernergebnisse

**a) Spearman ρ(Index, relativer Pixel-Ertrag), Median über 41 Feld-Jahre [95-%-KI]**

| Fenster | NDVI | NDRE | Anteil ρ > 0 (NDVI / NDRE) |
|---|---|---|---|
| 15.6.–15.7. | 0,45 [0,34; 0,53] | 0,49 [0,37; 0,57] | 0,90 / 0,90 |
| 16.7.–15.8. | **0,68** [0,54; 0,72] | **0,68** [0,62; 0,73] | 1,00 / 1,00 |
| 16.8.–15.9. | 0,35 [0,27; 0,52] | 0,40 [0,34; 0,55] | 0,83 / 0,90 |

Feld-Cluster-KI (27 Felder) praktisch gleich (NDVI Fenster 2: [0,54; 0,71]). Ohne die äußeren 20 m (nur Pixel ≥ 20 m vom gepufferten Umriss, n = 40 Feld-Jahre): NDVI Fenster 2 ρ = 0,71 [0,62; 0,75], NDRE 0,72 [0,68; 0,75] – das Ergebnis kommt also nicht vom Feldrand.

**b) Problemzonen, PR-AUC (Score = −Index) minus Prävalenz, Median [KI], n = 41 mit Problemzone, Prävalenz-Median 0,275**
Fenster 2: NDVI PR-AUC 0,66 [0,55; 0,71] (Differenz zur Prävalenz +0,37 [0,32; 0,43]); NDRE 0,63 [0,54; 0,71] (+0,38 [0,31; 0,44]). Fenster 1: NDVI 0,53, NDRE 0,56; Fenster 3: 0,51 / 0,50 (alle klar über Prävalenz).

**c) Pixel-Modell** (flaches LightGBM: Tiefe 3, 200 Bäume, lr 0,05; Ridge α = 1; Merkmale je Feld-Jahr z-standardisiert; feste Hyperparameter, nichts getunt). Median-ρ je Feld-Jahr [KI], R² gepoolt, LightGBM, Stichtag 15.8. (Fenster 1+2):

| Merkmale | ganzes Feld-Jahr aus | ganzes Jahr aus | ganzes Feld aus (zusätzlich) |
|---|---|---|---|
| nur Gelände | 0,29 [0,17; 0,36], R² 0,05 | 0,28 [0,16; 0,34], R² 0,04 | 0,22 [0,07; 0,29], R² 0,015 |
| nur Satellit | 0,70 [0,65; 0,74], R² 0,40 | 0,70 [0,64; 0,74], R² 0,39 | 0,70 [0,64; 0,74], R² 0,39 |
| beides | 0,71 [0,62; 0,76], R² 0,42 | 0,70 [0,62; 0,74], R² 0,40 | 0,70 [0,60; 0,75], R² 0,41 |

Stichtag 15.7.: Satellit 0,48 [0,36; 0,57] (R² 0,22), beides 0,49 [0,42; 0,59]; Stichtag 15.9.: Satellit 0,70, beides 0,71 (R² 0,42). Ridge liegt jeweils innerhalb ±0,01. B0 (relativer Ertrag = 1): R² = 0. Gepaarte Differenz beides − Satellit (15.8., LOFO): +0,007 [−0,01; 0,02]; beides − nur Gelände: +0,48 [0,43; 0,56]. PR-AUC minus Prävalenz (beides, 15.8., LOFO): +0,40 [0,33; 0,45]; nur Gelände +0,07. Das Modell (0,70) ist kaum besser als ein einzelner Index (NDRE Fenster 2: 0,68).

Gelände einzeln (Median-ρ mit relativem Ertrag, n = 41): Höhe −0,23 [−0,37; −0,09] (nur 27 % der Feld-Jahre positiv), Neigung −0,12 [−0,19; −0,05], TPI −0,01 [−0,16; 0,07]; Abstand zum Rand +0,13 [0,04; 0,24] (78 % positiv).

**d) Wiederkehrende Zonen** (gleiche S2-Zellen, 9 Felder mit ≥ 2 Jahren, 19 Jahrespaare, 23 Feld-Jahre): Spearman zwischen Jahren Median 0,67 [0,58; 0,75] (KI über Felder), Spanne 0,37–0,86, alle Paare > 0,3; Pearson 0,68. Mittel der anderen Jahre sagt das ausgelassene Jahr voraus: ρ 0,71 [0,58; 0,79]. Auf denselben 23 Feld-Jahren: Satellit-Modell (ganzes Feld aus) 0,72, Gelände-Modell 0,22.

**Antwort auf die Frage (mit Einschränkungen):** Wenig ertragreiche Feldteile liegen zu einem großen Teil **immer am selben Ort** (ρ ≈ 0,7 zwischen Jahren), das Satellitenbild sieht das Muster im selben Jahr gut (Mitte Juli bis Mitte August ρ ≈ 0,7; früher und später schlechter), das **30-m-Gelände erklärt nur wenig** (ρ ≈ 0,2–0,3, etwas Höhe/Neigung: tiefere Lagen bringen mehr). Was am Ort hängt, ist also nicht über Höhe/Neigung/TPI erklärt – Boden (nicht untersucht, siehe unten), Verdichtung, frühere Bewirtschaftung oder Randeffekte bleiben offen. Jahr: Median-ρ NDVI Fenster 2 je Jahr 0,54 / 0,54 / 0,72 / 0,66 / 0,70 (2017–2021, n = 4 / 4 / 11 / 10 / 12; Kruskal-Wallis p = 0,58) – kein belegbarer Jahresunterschied, aber mit so wenigen Feld-Jahren auch nicht ausschließbar.

## 3.1 Repräsentativität

- **Auswahl:** Nur ein Standort (BARC, Maryland, Forschungsfarm) und 5 Jahre (S2-Zeitraum; BARC 2014/2016 liegen vor der Aufgabenfestlegung 2017–2021). 27 Felder, 18 davon nur ein Jahr. Effektive Stichprobe = Felder/Feld-Jahre, nicht die 23 912 Pixel. Nach Jahr: 2017/2018 nur je 4 Feld-Jahre. Ein Feld-Jahr (CentralFarm_1_14 2020) ist als Zweitfrucht markiert (`double_crop`), nicht ausgeschlossen. *Konsequenz:* Aussagen gelten für BARC; Übertragbarkeit nach KBS/Österreich nicht belegt.
- **Gepufferte Fläche ist nicht das ganze Feld:** 26,8 % der Punkte liegen in den äußeren 10 m und fallen weg. Diese haben Median-relativen Ertrag 0,91 (behalten 1,02) und 43,6 % Problemanteil (behalten 27,9 %). Auch innerhalb der Puffergrenze fällt der Ertrag zum Rand hin: Median-relativer Ertrag 0,94 (0–10 m innen), 0,99 (10–20 m), 1,05 (20–40 m), 1,07 (> 40 m); Problemanteil 38 / 29 / 24 / 21 %. *Konsequenz:* Vorgewende-Problemzonen werden unterschätzt; ein Teil der „Problemzonen“ ist Randeffekt (s. Robustheitsprüfung ohne äußere 20 m: Ergebnis hält).
- **Wolken-Bias:** Median 5 klare Bilder je Pixel in jedem Fenster; Feld-Jahr-Minimum 2–3. Je Jahr schwankt die Zahl (Fenster 2: 2018 Median 2, 2020 Median 3, 2019/2021 Median 5; Fenster 3: 2017 Median 2). Weniger Bilder = rauschigere Komposite → ρ in 2017/2018 etwas niedriger könnte so (teilweise) zustande kommen. Nicht weiter quantifiziert. Kein Feld-Jahr wurde wegen Wolken ausgeschlossen, also kein Auswahl-Bias durch den Filter.
- **Zielverteilung:** Anteil Problemzone je Jahr 25,5 % (2017), 33,4 % (2018), 31,5 % (2019), 28,5 % (2020), 23,5 % (2021); Variationskoeffizient 0,25 / 0,34 / 0,33 / 0,34 / 0,24. Problemzonen sind häufig (kein Seltenheitsproblem für PR-AUC), aber 41 Feld-Jahre bleiben wenig.

## 3.2 Korrektheit

| Prüfpunkt | Geprüft wie | Befund | Konsequenz |
|---|---|---|---|
| Wertebereiche | Min/Max aller Indizes im Cache | NDVI 0,20–0,93, NDRE 0,13–0,83, keine NaN; Höhe 25–61 m, Neigung 0–25° | ✅ |
| Sensorwechsel | `S2_SR_HARMONIZED`; Zeitraum 2017–2021 | Offset-Korrektur 2022 betrifft den Zeitraum nicht | ✅ |
| Wolkenmaske | Cloud Score+ ≥ 0,60, Median über median 5 Bilder | Median unterdrückt einzelne Dunst-/Schattenausreißer; nicht einzeln geprüft | ⚠️ |
| **Auflösung S2** | Bandauflösung | B8A und B5 sind nativ **20 m**, B4 10 m: NDVI (B8A/B4) und besonders NDRE sind effektiv gröber als 10 m. | Pixelaussagen unter ~20 m nicht belastbar |
| **Gitter-Lage** | x/y-Raster der Kriging-Blöcke je Feld-Jahr | Ertragsraster sind je Jahr **um bis zu 7,5 m gegeneinander versetzt** (kein gemeinsames Gitter; exakte Koordinatentreffer 0 für die meisten Felder). Gegen das S2-Gitter ebenfalls versetzt (Versatz des Block-Mittelpunkts zur S2-Pixelmitte bis ~7,5 m); der S2-Wert am Blockmittelpunkt gehört zum Pixel, das bis zu 4 Blöcke überlappt. | Wiederkehrende Zonen auf 10-m-S2-Zellen gemittelt (Test mit 3-m-Versatz); Lagefehler < 1 Pixel senkt ρ eher |
| Kriging glättet | Nachbar-Korrelation (lag-1) | Relativer Ertrag 0,85, NDVI 0,87 (Median über 41 Feld-Jahre): die Ertragskarte ist **nicht glatter** als NDVI auf diesem Maß. Das beweist aber nicht, dass Kriging nichts glättet: Rohpunkte (Mähdrescher) fehlen, und der Wert wird von großräumiger Struktur dominiert. | Kriging entfernt Kleinraum-Rauschen im Ziel → ρ und R² eher zu hoch; Pixel nicht unabhängig, daher KI über Feld-Jahre |
| Lagefehler Mähdrescher | nicht prüfbar (keine Rohdaten) | Versatz Erntegut–Position typisch einige Meter | senkt ρ; nicht korrigiert |
| Gelände-Auflösung | GLO30 ≈ 30 m, Oberflächenmodell (DSM, enthält Vegetation/Bauwerke) | Höhenspanne je Feld-Jahr im Median 10 m (91 verschiedene Höhenwerte), Median-Neigung 2,1°; Vertikalfehler von GLO30 liegt im Meterbereich; 30 m ≈ 3 Ertragspixel, TPI mit 150-m-Kreis greift über das Feld hinaus | Gelände-Merkmale grob; „Gelände erklärt wenig“ heißt **nicht** „Gelände wirkt nicht“. Asset `COPERNICUS/DEM/GLO30` ist von GEE als veraltet markiert (Nachfolger `GLO30_2024_1`). |
| Ertragsmonitor-Fehler | Wertebereich Variationskoeffizient | CV 0,26 im Median (bis 0,53) ist hoch für Mais; relativer Ertrag bis 2,5 (CentralFarm_1_1 2020: viele sehr niedrige und einzelne sehr hohe Pixel, siehe Abbildung). Kann echte Ausfallstellen oder Messfehler enthalten; Ausreißer nicht entfernt (Phase-1-Bereinigung gilt). | ⚠️ Rangkorrelation ist robust, R² weniger |
| Feld-Matching | Zuordnung über `field_id` (Phase 1) | Gleiche Felder haben in Folgejahren teils andere Umrisse (z. B. EastFarm_5_12: 8,7 ha 2018, 13,4 ha 2021); wiederkehrende Zonen nutzen nur die überlappenden Zellen (≥ 50 je Paar) | ✅, Überlappung nicht visuell geprüft |

## 3.3 Scheinzusammenhänge

- **Jahres-Proxy:** n/a – alle Merkmale sind je Feld-Jahr z-standardisiert, bewertet wird innerhalb des Feld-Jahres.
- **Orts-Proxy/Auswendiglernen:** Gelände-Merkmale (je Feld-Jahr z-standardisiert) erkennen dieselbe Stelle in anderen Jahren desselben Felds wieder. Nur Gelände: ρ 0,29 (Feld-Jahr aus) gegenüber 0,22 (ganzes Feld aus) – etwa 0,07 stammt aus Wiedererkennen. Satellit: identisch (0,70 in allen drei Schemata) – kein Auswendiglernen. *Konsequenz:* für Gelände zählt das strengere „ganzes Feld aus“-Ergebnis (0,22).
- **Label-Shuffle (Zielwerte im Training innerhalb des Feld-Jahres permutiert):** ρ −0,03 [−0,06; 0,00] (Satellit, 15.8.), −0,01 [−0,09; 0,04] (beides), alle sechs Kontrollen |ρ| ≤ 0,05, R² ≈ −0,01 → Baseline, keine Leakage im Ablauf.
- **Adversarial Validation:** n/a (ein Datensatz).
- **Konfundierung:** Sorte, Saattermin, Düngung, Verdichtung, Unkraut, Drainage, Bodenart und Vorfrucht sind unbekannt. Der Satellit zeigt im Juli vor allem die Folge (Bestandsdichte, Lücken), nicht die Ursache. „Wiederkehrend“ kann Boden, aber auch gleiche Bewirtschaftungsspuren (Fahrgassen, Verdichtung, Randeffekt) bedeuten. Zonen ≠ Boden-Nachweis. Ein Randeffekt steckt teilweise im Wiederkehren (Ertrag fällt zum Rand, s. 3.1); die wiederkehrenden Zonen wurden nicht separat ohne Rand gerechnet.
- **Boden fehlt:** PLAN nennt SoilGrids/TWI; SoilGrids (250 m) und MERIT-TWI (90 m) variieren innerhalb eines 2–13-ha-Felds kaum und sind in der Aufgabe nicht vorgesehen. Die Frage „Boden“ ist hier daher **nicht** beantwortet, nur Höhe/Neigung/TPI (30 m). Vorschlag: Eintrag in `DECISIONS.md` (nicht von mir geändert).
- Hochkorrelierte Merkmale: NDVI und NDRE je Fenster stark korreliert; Ridge/LightGBM-Ergebnisse gleich, keine SHAP-Interpretation versucht.

## 3.4 Leakage

- As-of: Fensterende = Stichtag; Modelle am Stichtag k nutzen nur Fenster ≤ k (`feature_columns`, `model_dataset`; kein eigener Test für die Fensterauswahl). Z-Standardisierung nutzt nur Satelliten-/Geländewerte des eigenen Feld-Jahres (keine Zielwerte, keine anderen Feld-Jahre; Test `test_zscore_within_field_year_ignores_other_field_years`).
- Leave-one-group-out mit Assertion „keine Gruppe auf beiden Seiten“ (Test). Hyperparameter fest vorgegeben (keine Abstimmung, daher keine verschachtelte Validierung nötig).
- Räumliche Nähe: benachbarte Felder (EastFarm_5_3A–D) liegen im Training. Ein räumlicher Blocksplit wurde nicht gerechnet (Gegenprobe offen); da Satellit-ρ in allen drei Schemata gleich ist, ist ein Nachbarschaftseffekt unwahrscheinlich, für Gelände aber nicht ausgeschlossen.
- **Österreich-Regel:** Es wurden keine österreichischen Daten geöffnet, ausgewertet oder für Modellwahl/Schwellen benutzt: **nein**. Nach dem Freeze nichts geändert: **nein** (kein Freeze erfolgt).

## 3.5 Plausibilität

- ρ ≈ 0,7 und R² ≈ 0,4 liegen im Bereich dessen, was für Mais-NDVI im Hochsommer gegen Ertragskarten berichtet wird; kein „zu gut“-Verdacht. Der Gewinn durch Modell und Gelände gegenüber einem einzelnen Index ist klein (+0,02 ρ), das spricht gegen versteckte Leakage.
- Hoher Wert könnte durch geglättetes Ziel und große Lücken/Ausfallstellen (leicht zu sehen) begünstigt sein. Das Fenster 16.7.–15.8. trifft die Zeit um Blüte/Kornfüllung; später (Abreife, unterschiedliche Reifezeitpunkte) sinkt ρ auf 0,35–0,40.
- Fallstudien (Modell beides, 15.8., ganzes Feld aus): schwächste Feld-Jahre APU_1 2021 (ρ 0,13, Prävalenz 0,35), EastFarm_5_3D 2017 (0,36), EastFarm_5_3B 2017 (0,38) – zwei davon 2017 mit im Median nur 2 klaren Bildern in Fenster 3; beste EastFarm_5_23 2019 (0,86), EastFarm_6_60 2019 (0,85), CentralFarm_1_14 2020 (0,83). Beispielabbildung zeigt das Feld mit Median-ρ (CentralFarm_1_1 2020, ρ 0,68), nicht ein ausgesuchtes: es ist allerdings ein Feld mit extremer Streuung (CV 0,53).
- Konfidenzintervalle über Feld-Jahre statt Pixel (Pixel pseudoreplikiert; sonst wären die KI um Größenordnungen zu eng). Auch Feld-Jahre desselben Felds (bis 3 Jahre) sind nicht unabhängig; Feld-Cluster-KI als Sensitivität ändert nichts Wesentliches.

## 3.6 Entscheidung

⚠️ **Weiter mit Einschränkung.** Das Ergebnis ist belastbar für „Satellit (Mitte Juli bis Mitte August) findet Problemzonen im selben Jahr“ und „Muster wiederholt sich am Ort“. Grenzen, die in der Doku stehen müssen: nur BARC/41 Feld-Jahre/27 Felder; Zielkarten aus Kriging mit versetzten Jahresgittern und unbekanntem Lagefehler; S2-Merkmale effektiv ~20 m; Gelände nur 30 m (DSM) und Boden nicht untersucht; Randeffekte (äußere 10 m fehlen, Ertrag fällt zum Rand); Konfundierung durch unbekannte Bewirtschaftung; kein räumlicher Blocksplit. Kein ⛔-Befund.

Offene Punkte: (1) `config.yaml` unverändert, Parameter stehen in `DEFAULTS` im Modul und in `within_field_config.json` (ein `within_field:`-Abschnitt in `config.yaml` würde sie überschreiben). (2) `DECISIONS.md`/`CHANGELOG.md`/`SUPPORT.md`/`reports/results.md` nicht angefasst. (3) Boden (SoilGrids, SSURGO) und TWI im Pixelmodell fehlen; GEE-DEM-Asset ist veraltet markiert.
