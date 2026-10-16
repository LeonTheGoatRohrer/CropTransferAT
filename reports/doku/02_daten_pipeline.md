Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 2 Daten, Pipeline, Definitionen und Leakage-Schutz

## 2.1 Datenquellen und Lizenzen

Quelle aller Angaben: `DATA_SOURCES.md` (Abruf 2026-10-15). Rohdaten liegen nicht im Repository.

| Datensatz | Rolle | Umfang | Lizenz / Nutzung |
|---|---|---|---|
| KBS LTER (Michigan), MCSE-Parzellen, Ertragspunkte, Scale-up | Feld-Ertrag (Längsschnitt) | 295 Mais-Parzellen-Jahre (14 Mais-Jahre 1989–2023), davon 96 in der HLS-Zeit (2014/17/20/23) | KBS-Nutzungsbedingungen: Veröffentlichung nur mit **schriftlicher Erlaubnis**; Anfrage durch den Projektinhaber nötig |
| USDA BARC (Maryland) | Feld-Ertrag (Längsschnitt), Ertragskarten | 62 Mais-Feld-Jahre, ca. 33 Felder, 2014, 2016–2021 | U.S. Public Domain |
| Colorado (Akron), Poss et al. | Ergänzung | 10 Mais-Teilflächen-Jahre, 2019–2022; nur Stichprobenpunkte | CC0 |
| Mead, Nebraska (AmeriFlux) | geplant | Konto nötig, Erträge ungeprüft | CC-BY-4.0 (nach Login); **nicht verfügbar** |
| One Acre Fund (Afrika) | nur Tabellendatensatz | 14 773 Maisfelder, 2016–2022 (ohne 2021), je ein Jahr; 10 332 mit exakter Position | CC BY 4.0 |
| YieldSAT (Argentinien, Brasilien) | geplant | Mais: 185 + 118 Felder, 2017–2024 | Lizenz unklar; **Zugang beantragt** |
| SSURGO (USDA NRCS) | Boden-Ertragspotenzial, nur USA, nur Analyse | NCCPI Mais, Mais-Ertragsschätzung (lückenhaft) | U.S. Public Domain |
| CY-Bench v1.10 | Regionalmodell EU | Mais, 23 EU-Länder in den Dateien (16 mit Auswertungsjahren) | EUPL-1.2 |
| Statistik Austria / Eurostat | Regionalerträge Österreich, **nur Test** | Bundesländer 2010–2026 | Quellenangabe |
| INVEKOS Schläge (AMA) | Feldgrenzen Österreich, **nur Test** | 2018–2025; Körnermais (Code 105) 106 667 bis 114 509 Schläge pro Jahr in Österreich | CC BY 4.0 |
| Verwaltungsgrenzen (Statistik Austria) | Zuordnung Gemeinden | Gemeinden 2025: 2 114 | CC BY 4.0 |
| Versuchsberichte Hatzendorf, LK Oberösterreich | lokale Test-Erträge, **nur Test** | 150 Zeilen (Steiermark 44, Oberösterreich 106) | öffentlich, Quellenangabe |
| Bodenklimazahl | optional | nicht beschafft | unklar |
| HLS v2, Sentinel-2 L2A, Cloud Score+, ERA5-Land, SoilGrids, Copernicus-DEM (über Google Earth Engine) | Satellit, Wetter, Boden, Gelände | – | **[Lizenz prüfen]** (steht nicht in den Quelldateien) |

Alle Erträge werden auf **t/ha bei 15,5 % Kornfeuchte** umgerechnet (1 bu/ac = 62,77 kg/ha). Die Feuchtebasis der Quellen ist verschieden (14 %, 15 %, 15,5 %, nass); das ist besonders bei BARC wichtig, weil sie von Jahr zu Jahr wechselt.

**Wichtig zur Österreich-Regel:** Die österreichischen Daten (INVEKOS, Statistik Austria, Versuchsberichte) wurden bis jetzt nur heruntergeladen, gezählt und abgeschrieben, nicht ausgewertet.

## 2.2 Pipeline (Überblick)

1. **Ertragsdaten vereinheitlichen** (`groundtruth.py`): Ergebnis sind **365 Mais-Feld-Jahre** (KBS 294, BARC 61, Colorado 10); 7 Zeilen wurden mit Grund ausgeschlossen (z. B. unklare Einheit bei einem BARC-Raster).
2. **Satellitenkurven je Feld-Jahr** über Google Earth Engine: HLS (30 m, Landsat 8/9 + Sentinel-2 harmonisiert) ab 2013 und Sentinel-2 (10 m) ab 2017. Feldgrenze mit 10 m Innenpuffer; Median aller klaren Pixel je Szene; Szene gültig bei Klar-Anteil ≥ 0,7 (Sentinel-2 mit Cloud Score+ ≥ 0,60). Dann **Dekaden** (10-Tage-Mediane), Lücken innerhalb der Saison linear interpoliert und als „nicht beobachtet“ markiert. Indizes: NDVI, EVI, GNDVI, NDMI, SAVI (Sentinel-2 zusätzlich NDRE).
3. **Wetter** (ERA5-Land, täglich am Feldzentrum): Wärmesumme (Basis 10 °C, Deckel 30 °C), Hitzetage, Niederschlag, Wasserbilanz, Dampfdruckdefizit, Bodenwasser, dazu ein Wasserstress-Index der Wurzelzone (FAO-56-Bodenspeichermodell, nutzbare Feldkapazität nach Saxton & Rawls 2006).
4. **Boden und Gelände:** SoilGrids (250 m), Copernicus-DEM (Höhe, Neigung, Exposition, TPI, TWI). Für US-Felder zusätzlich SSURGO (nur Analyse, nicht im Hauptmodell).
5. **Merkmalsgruppen** (jeweils nur Daten bis zum Stichtag): S = Satellit, W = Wetter, B = Boden und Gelände (B+ = SSURGO nur USA). **Stichtage:** 1.6., 15.6., 1.7., 15.7., 1.8., 15.8., 1.9.
6. **Modelle:** je Merkmalsgruppe ein Modell und Kombinationen, jeweils Ridge-Regression und flaches LightGBM (Baumtiefe ≤ 3); wenige Daten verlangen einfache Modelle.
7. **Auswertung:** Spearman-Rangkorrelation ρ, RMSE, Skill gegenüber der Baseline, 95-%-Konfidenzintervalle (KI) per Bootstrap.

*In einfachen Worten:* ρ misst, ob das Modell die Felder in die richtige **Reihenfolge** bringt (1 = perfekt, 0 = Zufall). Das KI sagt, in welchem Bereich der wahre Wert mit 95 % Sicherheit liegt; enthält es die 0, ist ein Zusammenhang nicht gesichert.

## 2.3 Definitionen

- **Ertrag Y:** Mittel der bereinigten Ertragspunkte im gepufferten Feld (KBS: offizieller Parzellenwert, Tabelle 51).
- **Relativer Ertrag RY (trendbereinigt).** Idee: RY = 1 heißt „so viel wie für dieses Feld in diesem Jahr normal“, RY = 0,8 heißt 20 % darunter. Der Normalwert kommt aus den *anderen* Mais-Jahren desselben Feldes. Weil Erträge über die Jahre steigen (KBS: +0,087 t/ha pro Jahr in den Rohdaten; in der Phase-1-Auswertung mit festen Feldeffekten +0,119 t/ha pro Jahr **[Zahl prüfen]**), wird je Datensatz ein linearer Trend geschätzt und abgezogen:
  `RY = Y / (Trend(y) + Mittel der Residuen der anderen Jahre)`.
  Der Trend wird **nie** mit dem Zieljahr geschätzt, in der Kreuzvalidierung nur aus Trainingsdaten (Test `test_targets.py`). Entscheidung des Projektinhabers vom 2026-10-15; ohne Trendbereinigung hätte „gefährdet“ bei KBS vor allem die Bio-Behandlung gemessen.
- **Gefährdet:** RY < 0,85, also mindestens 15 % unter dem eigenen Normalniveau.
- **Nachbar-relativer Ertrag RY_nb:** Ertrag / Median der *anderen* Felder derselben Gruppe im selben Jahr. Misst Unterschiede zwischen Feldern, nicht zwischen Jahren; wird nie mit RY vermischt.
- **Problemzone innerhalb eines Feldes:** zusammenhängende Pixel mit relativem Pixel-Ertrag < 0,85 (Pixel-Ertrag / Feldmittel desselben Feld-Jahres).
- **LOFYO** (Leave-One-Field-and-Year-Out): beim Testen sind **Feld und Jahr zugleich unbekannt**. Konkret (DECISIONS 2026-10-15): Felder je Datensatz in 3 Gruppen (KBS nach Wiederholungspaaren R1–2, R3–4, R5–6; BARC/Colorado zufällig mit Seed). Ein Fold ist (Jahr y, Gruppe g): Test = Feld-Jahre in y und g; Training = alle Feld-Jahre mit Jahr ≠ y **und** Gruppe ≠ g. Das Jahr wird über alle Datensätze ausgeschlossen. Ergänzend LOFO (Feld ungesehen, Jahr gesehen), LOYO (Jahr ungesehen), Leave-One-Dataset-Out (LODO).
- **Baselinen:** B0 = „normales Jahr“ (RY = 1). B1 = Ridge auf einem einzigen Index-Merkmal.

## 2.4 Leakage-Schutz (Schutz vor „Schummeln“ durch Zukunfts- oder Testwissen)

1. **As-of-Regel:** Für einen Stichtag t dürfen Merkmale nur Daten mit Zeitstempel ≤ t nutzen (Assertion und Unit-Test, `test_no_leakage.py`).
2. **Trend und Normalwerte ohne Zieljahr:** RY-Trend und -Normalwert nur aus Trainingszeilen (Test `test_in_fold_uses_training_rows_only`); Referenzkurve „gesunder Mais“ je Fold nur aus Trainings-Feld-Jahren.
3. **Verschachteltes Tuning:** Hyperparameter werden nur innerhalb der Trainingsdaten gewählt (Jahr ausgelassen im inneren Durchlauf).
4. **Kontrolltests:** Label-Shuffle (Ziel zufällig mischen; Modell muss auf Zufallsniveau fallen), Leistung innerhalb eines Jahres (Jahres-Proxy), LOFO vs. LOFYO (Auswendiglernen), Adversarial Validation (kann man Datensätze an den Merkmalen unterscheiden?), keine Feld- oder Orts-Kennungen als Merkmal.
5. **Österreich-Regel:** Bis zum Freeze keine österreichischen Satelliten- oder Ertragsdaten auswerten; nach dem Freeze nichts am Modell ändern. **Offen berichteter Vorfall:** In Phase 0 standen kurz vor Einführung der Regel österreichische Bundesland-Erträge in `DATA_SOURCES.md` (Commit `2d3035b`) und ein Agent hat sie beim Plausibilisieren gesehen. Sie flossen in **keine** Entscheidung ein und wurden aus den Dokumenten entfernt; die Git-Historie wurde nicht umgeschrieben (`DECISIONS.md`, 2026-10-15; Datenkritik Phase 0).

## 2.5 Vorab-Festlegungen (alles vor dem Ansehen der jeweiligen Ergebnisse in `DECISIONS.md`)

| Festlegung | Datum (laut DECISIONS) |
|---|---|
| Kriterium „stark genug“ (4 Teilbedingungen, siehe Kapitel 4) | 2026-10-15 |
| Grenze der Landsat-Harmonisierung: für NDVI **und** EVI \|Median der Differenz\| ≤ 0,03 und RMSD ≤ 0,07 | 2026-10-15 |
| Metriken und Bootstrap (Cluster über Datensatz-Jahre, 1000 Wiederholungen, Seed 42) | 2026-10-15 |
| Datenqualitätsregel für Satellitenmerkmale (fehlt statt fortschreiben) | 2026-10-16 |
| Trainings- und Bewertungsmenge Phase 2 | 2026-10-16 |
| Drei Verbesserungsrunden, Auswahlregel, Hauptmodell-Kandidat für Phase 3 | 2026-10-16 |
| Ursachen-Regeln für gefährdete Felder (feste Faustwerte) | 2026-10-16 |
| Phase 5: Zielgröße YAS, Hyperparameter-Raster, EU-Freeze, AT-Zero-Shot-Protokoll | 2026-10-15 |

**[prüfen: Die Reihenfolge „vorab“ ist in DECISIONS nur durch das Datum belegt; mit der Git-Historie (Commit-Zeitpunkte) nachweisen.]**

Eine Abweichung ist offen zu nennen: Das **erste Hyperparameter-Raster in Phase 5 wurde nach einem Pilotlauf erweitert**, wobei das Pilotergebnis der äußeren Evaluation sichtbar war (siehe Kapitel 5 und 6).
