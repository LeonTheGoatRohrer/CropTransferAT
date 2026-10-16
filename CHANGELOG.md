# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [SemVer](https://semver.org/lang/de/) – ein Minor-Release pro Phase (siehe AGENTS.md §4.4).

## [Unreleased]
### Added (Branch `phase-mk-mehrkultur`, vorläufig bis W0.1)
- `fetch_open_sets.py`: Download mit Manifest und sicherem Entpacken (INVITE, BRIWECS, Erbsen FR, Nordic Gerste; NVT optional).
- `groundtruth_multi.py`: Schema `gt_site_years` (Stufen S1–S4, RY, RY_nb, 0,1°-Zelle); `review_multi.py`: Zahlen zur Datenkritik.
- Datenkritik `reports/data_review/phase1b_mehrkultur.md`; Zählung: Winterweizen S2 202, Erbse S2 257 Zellen-Jahre, Mais 0 (G2F fehlt).
### Added
- **Datensuche und Mehr-Kulturen-Plan:** `reports/data_search.md` (118 Quellen, Top 10, Zählung je Kultur, Anfragetexte; Korrekturblock zu YIPEEO und Nordic), `reports/plan_mehrkultur.md` (25 Schritte, 4 Gates, Entwurf D1–D12), Kopie des Codex-Katalogs unter `reports/extern/codex_2026-10-16/`; Eintrag `datensuche-mehrkultur` in `app/versions.yaml`.
- **Website (Phase 9, vorgezogen):** `app/streamlit_app.py` als mehrseitige Streamlit-Site (Ziel · Vorgehen & Quellen · Ergebnisse · Vergleich · Felder ansehen · Eigenes Modell · Projektlog), Seiten unter `app/ui/`, Versionsregister `app/versions.yaml` (je Version: was geändert wurde, Kennzahlen in einfacher Sprache, Befunde, Grenzen, Abbildungen, Pfade), Glossar „Was heißt das?“, Theme `.streamlit/config.toml`.
- `app/precompute.py` schreibt zusätzlich `benchmarks.csv` (alle Läufe aus `versions.yaml`) und `stages.json` (gewähltes Modell + Kriterien je Stufe) für den interaktiven Vergleich.
- Seite „Eigenes Modell“: speichert Trainingsaufträge (Kultur, Datensätze, Merkmale) als JSON unter `data/app/train_requests/`; das Training selbst läuft weiterhin über die Module.
- `gallery.py`: Sentinel-2-Galerien der Trainingsfelder (`reports/figures/overview_s2_gallery_barc.png`, `overview_s2_gallery_kbs.png`).
- `tests/test_app.py`: Registerprüfung (Abbildungen/Pfade existieren, Status gültig, Reihenfolge) und Render-Test jeder Seite.
- `oaf_analysis.py`: One Acre Fund als Tabellendatensatz (RY_nb, Leave-One-Country-Out, Ablation, SHAP, Schadens-Odds-Ratios); Datenkritik `phase2_oaf_tabular.md` (⚠️).
- `notebooks/02_drivers.ipynb`, `notebooks/03_problem_fields.ipynb`; Doku-Entwürfe `reports/doku/`; Nachtlauf-Bericht `reports/NACHTLAUF.md`.
- `run_phase2_y.py` (Zielgröße absoluter Ertrag Y: Satellit ρ 0,52, Boden/SSURGO ≤ 0,16) und `gdd_axis.py` (Kalender- vs. GDD-Achse: kein robuster Unterschied); `phase4_report.py` mit Robustheitsprüfung (keine von 64 Varianten erfüllt Kriterium 1).
- App zeigt den Phase-3-Kandidaten mit Hinweis „nicht stark genug“.
### Added
- Phase 5 (bis EU-Freeze, **ohne jeden Österreich-Test**): `regional_cybench.py` – CY-Bench-Mais für 18 gelistete EU-Länder, 16 davon mit Region-Jahren (Länderliste ohne AT, `assert_no_austria` an allen Einstiegen), Prädiktoren je Region-Jahr und Stichtag nach As-of-Regel (Monatsmittel/min/max, Summe für prec/cwb; fPAR/NDVI mit Verfügbarkeitsverzug), Ziel `YAS` (olympischer Durchschnitt der 5 Vorjahre), Baselines YAS = 1 und lineare Trendfortschreibung, flaches LightGBM (`max_depth ≤ 3`), Tuning nur verschachtelt per Leave-One-Country-Out, äußere LOCO-Evaluation mit Bootstrap-KI (Region-Jahre, Land-Jahr-Cluster, länderbalanciert, ohne DE), Frühwarnkurve, Kontrollen (Label-Shuffle, Training ohne DE, Koordinaten-Ablation, Adversarial Validation, Spearman innerhalb eines Jahres).
- EU-Freeze: Modelle je Stichtag unter `results/models/cybench_freeze/` (nicht im Repository), SHA-256, Merkmalsliste, Hyperparameter und vorab registriertes AT-Zero-Shot-Protokoll in `reports/freeze_protocol_cybench.md`; `verify_freeze` und `predict_zero_shot` (nicht auf Österreich ausgeführt).
- `tests/test_regional_cybench.py`: YAS-Handbeispiel, As-of-Regel, AT-Ausschluss, LOCO-Splits, Label-Shuffle, Freeze-Roundtrip.
- Datenkritik `reports/data_review/phase5_cybench_eu.md`; `reports/results_phase5.md`; Abschnitt `cybench` in `config.yaml`.

## [0.4.0] – 2026-10-16 – Phase 3: Problemfelder erkennen (F2)
### Added
- `stress.py` (Referenzkurve „gesunder Mais“, As-of-Stress-Score, vorab festgelegte Ursachen-Regeln), `phase3.py` (Gefährdet-Klassifikation a/b, PR-AUC, Recall bei 20 % FPR, Indikatorwahl, Fallstudien), `phase4_report.py`; Tests `test_stress.py`, `test_rounds.py`.
- Datenkritik `phase3_problem_fields.md`; `reports/phase4_stark_genug.md`.

### Found
- Stressindikator festgelegt: EVI-Integral (K4), Median-ρ 0,49 über KBS/BARC.
- Referenzkurven-Stress-Score am 1.9.: ρ = 0,43 [0,24; 0,72], PR-AUC 0,71 bei Prävalenz 0,33; gelernte Modelle kaum besser als Zufall.
- „Gefährdet“ bei KBS zu 57 % Bio-Parzellen (T4).
- Phase 4: Phase 2 und alle 3 vorab festgelegten Runden verfehlen „stark genug“ → kein Freeze, kein Österreich-Test.

## [0.3.0] – 2026-10-16 – Phase 2: Basismodelle (F0, F1)
### Added
- `splits.py` (LOFYO/LOYO/LOFO/LODO), `models/family.py` (Ridge + flaches LightGBM je Merkmalsgruppe), `run_phase2.py` (238 Läufe, verschachtelt), `phase2_extras.py` (Auswahlregel, Kriterien 1–4, LODO, Label-Shuffle, Cross-Conformal, SHAP, Adversarial Validation), `rounds.py` (vorab festgelegte Verbesserungsrunden), `within_field.py` (BARC-Ertragskarten vs. S2-Pixel).
- Datenkritik `phase2_models.md`, `phase2_within_field.md`; `reports/results.md`.

### Found
- Zwischen Jahren: gewähltes Modell ρ(1.9.) = −0,04 [−0,29; 0,37] (LOFYO), aber 0,65 bei gesehenem Jahr (LOFO) → Jahreseffekt nicht übertragbar; Kriterium „stark genug“ nicht erfüllt.
- Runde 1 (relative Satellitenmerkmale): ρ = 0,37 [−0,01; 0,70], LODO beide Richtungen > 0; Runde 2 schlechter.
- Innerhalb der Felder: NDVI Mitte Juli–Mitte August vs. Pixel-Ertrag Median-ρ 0,68 [0,54; 0,72].

## [0.2.0] – 2026-10-16 – Phase 1: Ertragsdaten aufbereiten
### Added
- `groundtruth.py`: KBS (Tabelle 51, 1989–2023), BARC (Kriging-Raster), Colorado → einheitliches Schema `gt_field_years` (365 Mais-Feld-Jahre, t/ha bei 15,5 %), `gt_yield_points` (BARC 10 m), Ausschluss-Protokoll; Feldzuordnung über IoU ≥ 0,7.
- `targets.py`: trendbereinigter RY (Trend nie mit Zieljahr, in der CV nur aus Trainingszeilen), `RY_nb`, „gefährdet“.
- `gee_extract.py`/`extract_us.py`: Szenenstatistik je Feld (HLS, Landsat 5/7, S2 mit Cloud Score+), ERA5-Land täglich, SoilGrids, Copernicus-DEM (TPI, TWI); 67 GEE-Jobs.
- `timeseries.py`/`features.py`: Reflexion, Roy-2016-Harmonisierung, Indizes, As-of-Dekaden, Merkmalsgruppen S/W/B/B+, RZWSI (FAO-56-Bucket), nFK nach Saxton & Rawls.
- `dataset_us.py`, `explore_phase1.py`, `evaluate.py` (Cluster-Bootstrap); Tests `test_targets`, `test_groundtruth_schema`, `test_field_matching`, `test_no_leakage`.
- `notebooks/01_groundtruth.ipynb`; Datenkritik `reports/data_review/phase1_groundtruth.md` (⚠️).

### Found
- Landsat-7-vs-HLS-Harmonisierung **nicht bestanden** (NDVI-RMSD 0,073 > 0,07) → keine Satellitenmerkmale vor 2013.
- KBS 2014/2017 ohne HLS-Sommertermine; RY-Labels der HLS-Zeit: 123 Feld-Jahre aus 11 Standort-Jahren.
- Erste Zusammenhänge: EVI-Integral (K4) vs. RY gepoolt ρ = 0,44 (KI 0,10–0,75, 9 Cluster).

## [0.1.1] – 2026-10-15 – Phase 0 Korrektur
### Fixed
- `notebooks/00_data_access.ipynb` ausgeführt (alle Zellen fehlerfrei); Spalte `plot` → `plot_id` (Kollision mit pandas `.plot`).
- BARC-RY-Feld-Jahre in Datenkritik/CHANGELOG: 16–27 je nach Feldnamen-Zuordnung (geprüfte Zuordnung folgt in Phase 1).
- `.claude/worktrees/` in `.gitignore`.

## [0.1.0] – 2026-10-15 – Phase 0: Setup & Datenzugang
### Added
- Python-3.11-Umgebung mit fixierten Paketen (`requirements.txt`, CPU-torch), Paket `src/croptransfer/`, `pyproject.toml`, zentrale `config.yaml`, GitHub Actions (`pytest` bei jedem Push).
- `gee_extract.py`: Earth-Engine-Initialisierung (Projekt `croptransfer`, TLS über Windows-Zertifikatsspeicher) und Zugangstest; Filter gegen HLS-Granulen mit Datumsgrenzen-Footprints (UTM-Zone 01/60).
- `regional_stats.py`: Statistik-Austria-/Eurostat-Körnermais je Bundesland → `data/raw/stat_at_maize.csv`.
- `invekos.py`: INVEKOS-Dateien finden, Schema lesen, Kulturcodes zählen, Schläge je Bundesland über Gemeinde-Join (nur Zählung, Österreich-Regel).
- `notebooks/00_data_access.ipynb`: Erreichbarkeit und Kennzahlen aller Quellen, direkt aus den Rohdaten.
- `DATA_SOURCES.md` für alle Quellen (KBS, BARC, Colorado, Mead, CY-Bench, Statistik Austria, One Acre Fund, YieldSAT, SSURGO, AT-Versuchsberichte, Bodenklimazahl, INVEKOS, Verwaltungsgrenzen).
- Datenkritik `reports/data_review/phase0_data_access.md` (Entscheidung ⚠️ weiter mit Einschränkung; One Acre Fund ⛔ für die Feldauswertung bis zur Entscheidung).
- `one_acre_fund.py`: Sichtung des One-Acre-Fund-Datensatzes (Spalten, exakte Positionen, Vorab-Filter, Schadens-Kodierung, `RY_nb`-Gruppen); `python -m croptransfer.one_acre_fund`.
- `soil_ssurgo.py`: SSURGO über Soil Data Access (Mais-Ertragsschätzung `cocropyld.nonirryield_r`, NCCPI Mais aus `cointerp`), Aggregation Komponente → Map-Unit → Feld mit Abdeckungsregel; Testabfrage KBS + BARC.
- `at_trials.py`: Zusammenführung und Schemaprüfung der abgeschriebenen österreichischen Versuchserträge → `data/raw/at_trials.csv` (nur Sammeln, keine Auswertung).
- `DATA_SOURCES.md` §9, §11, §12 mit Kennzahlen; Datenkritik-Nachtrag für die neuen Quellen.

### Changed
- Entscheidungen des Projektinhabers in `DECISIONS.md`: RY-Normalwert trendbereinigt, One Acre Fund nur Tabellendatensatz (`RY_nb`-Gruppe `cz` × Saison × Jahr), Arbeitsgrenze Freeze, nichts veröffentlichen; `ANFRAGEN.md` Nr. 7 (One Acre Fund Koordinaten/Feldgröße).
- Österreich-Regel nachträglich umgesetzt: Werte-Tabelle der Statistik-Austria-Erträge aus `DATA_SOURCES.md` und Einzelwerte aus der Datenkritik entfernt (offen dokumentiert).

### Found
- One Acre Fund: **keine Feldgrößen-Spalte**, Koordinaten auf 0,001° gerundet, Feuchtebasis nicht angegeben, Trockenheit in `pest`/`disease` eingeordnet, Hagel fehlt → Vorab-Filter PLAN §3.1 so nicht umsetzbar (Entscheidung offen).
- SSURGO: alle 24 KBS-Parzellen in einer Map-Unit; Mais-Ertragsschätzung für KBS nicht vorhanden.
- US-Ertragslabels: ≈ 112–123 RY-Labels (BARC-Feldzuordnung unsicher) aus nur ≈ 11 Standort-Jahren; KBS-Ertragstrend +0,087 t/ha/Jahr → RY-Normalwert muss festgelegt werden.
- INVEKOS: ~63 % der steirischen Körnermais-Schläge < 1 ha; CCM (Code 106) so häufig wie Silomais.
- Feuchtebasen der Quellen verschieden (14 / 15 / 15,5 % / nass); CY-Bench-Erträge AT enden 2020.

## [0.0.5] – 2026-10-15
### Added
- Trainingsdaten: **One Acre Fund** (14.773 Maisfelder, Afrika, inkl. gemeldeter Schäden) und **YieldSAT** (303 Maisfelder mit Mähdrescher-Karten, Argentinien/Brasilien); Nachbar-relativer Ertrag `RY_nb`; Stichtag-Übertragung über Wärmesumme seit Saisonbeginn; zweite Satelliten-Basis (S2).
- **SSURGO** als US-Boden-Ertragspotenzial (Analysemodell M-B+).
- Österreich-Test **V2 lokal**: Versuchsberichte Hatzendorf + LK-OÖ-Praxisversuche (`YAS_site`); Bodenklimazahl optional.
- Prüfung der Ursachen-Zuordnung an den gemeldeten Schäden (Phase 3).
- `ANFRAGEN.md`: alle Anfragen des Projektinhabers mit Textentwürfen.
- `DATA_SOURCES.md`: Einträge 9–13 (Status geplant/angefragt).

## [0.0.4] – 2026-10-15
### Changed
- `PLAN.md` neu geordnet: **Österreich ist nur noch Testfall (Beweis).** Phasen: 0 Setup → 1 alle Ertragsdaten aufbereiten → 2 Basismodelle „Was bestimmt den Ertrag?“ → 3 Problemfelder erkennen → 4 „Stark genug?“ + Einfrieren → 5 CY-Bench (parallel) → 6 Österreich-Daten → 7 Test in Österreich → 8 Zusatz (optional) → 9 Demo → 10 Abgabe.
- Forschungsfragen neu: F0 Ertragsvorhersage, F1 Ertragsfaktoren, F2 Problemfelder, F3 Beweis Österreich, F4 CY-Bench-Gegenprobe, F5 Zusatz.
- GO/NO-GO mit österreichischen Daten entfällt; Stressindikator K1–K5 wird nur mit US-Daten gewählt; selbstüberwachtes Feldmodell, Radar und Few-Shot sind optionaler Zusatz (Phase 8).
- `AGENTS.md`: Versionstabelle (v0.1.0 … v0.10.0, v1.0.0), Österreich-Regel in der Datenkritik, Stopp-Bedingung, Pflicht-Test `test_freeze.py`.

### Added
- Modellfamilie je Merkmalsgruppe (Satellit, Wetter, Boden/Gelände, Kombination), Faktorenanalyse, Modell innerhalb der Felder (Problemzonen aus Ertragskarten).
- Referenzkurve „gesunder Mais“, Gefährdet-Klassifikation, vorab festgelegte Ursachen-Regeln.
- Vorab festgelegtes Kriterium „stark genug“, Freeze mit Prüfsummen und vorab registriertem Österreich-Testprotokoll.
- Datenerweiterung: KBS-Jahre vor 2013 über Landsat 5/7 (nach Harmonisierungsprüfung); GDD-Zeitachse.

## [0.0.3] – 2026-10-15
### Changed
- `PLAN.md` neu aufgebaut: nach dem Setup zuerst der **Ertrags-Datensatz** (KBS LTER, USDA BARC, Colorado; Mead nach Klärung) mit HLS- und Sentinel-2-Saisonkurven; danach Steiermark-Pilot, Ertragsbezug in Österreich (GO/NO-GO), CY-Bench parallel, dann Phasen 5–11.
- Satellitenbasis: HLS v2 (30 m, ab 2013) für lange Reihen + Sentinel-2 (10 m) parallel.
- GO-Bedingung (a) wird jetzt mit gemessenem Feldertrag (relativer Ertrag RY) in Phase 1 geprüft.
- One Acre Fund vom Validierungsweg in den Ausblick verschoben (nur ein Jahr je Feld).
- `AGENTS.md`: Versionstabelle für 12 Phasen (v0.1.0 … v0.11.0, v1.0.0); Pflicht-Tests für Ertrags-Datensatz und LOFYO-Splits.

### Added
- Forschungsfrage F0 (Kurve ↔ gemessener Ertrag, ab wann?) und F4c (Transfer US-Ertragsmodell → Österreich).
- Definitionen: Feld-Ertrag, Umrechnung auf 15,5 % Feuchte, relativer Ertrag RY, „gefährdet“ (RY < 0,85), Pixel-Paare innerhalb der Felder.
- Validierungssplits LOFYO / LOFO / Leave-One-Dataset-Out.
- Aufgaben für den Projektinhaber: Erlaubnis-Anfrage an KBS, AmeriFlux-Konto.

## [0.0.2] – 2026-10-15
### Changed
- `PLAN.md`: neue Phasenreihenfolge (0 Setup → 1 Pilot → 2 Zielgrößen-Check GO/NO-GO → 3 CY-Bench parallel → 4–10 Pipeline, Modelle, Demo, Abgabe).
- Zielgröße ist jetzt ein Kandidatensatz K1–K5 (Kalender- und phänologische Fenster) mit vorab festgelegter Auswahl- und GO/NO-GO-Regel.
- Frühernte-Regel: abrupter Abfall auf Boden-Niveau wird als Ernte markiert, nicht als Stress.
- `AGENTS.md`: Versionstabelle an die neuen Phasen angepasst (v0.1.0 … v0.10.0, v1.0.0).

### Added
- Drei Validierungswege für den Ertragsbezug (V1 regional AT, V2 Feld international, V3 Feld AT über Landwirt:innen).
- Forschungsfrage F0 (taugt die Satelliten-Zielgröße als Ertrags-Stellvertreter?).
- Klarstellung im Plan: Training erfolgt pro Feld, regionale Mittel dienen nur der Kontrolle.
- Aufgabe für den Projektinhaber: Feld-Ertragsdaten bei Landwirt:innen anfragen.

## [0.0.1] – 2026-10-15
### Added
- Projektplan (`PLAN.md`) mit Forschungsfragen, technischen Festlegungen, Definitionen und Phasen 0–8.
- Agenten-Arbeitsanweisung (`AGENTS.md`) mit Arbeitszyklus, Datenkritik-Prüfliste, Versionierungs- und Testregeln.
- Repository-Grundgerüst (README, CHANGELOG, DECISIONS, SUPPORT, .gitignore).
