# Unterstützung (BWKI-Pflichtangabe)

Laut Teilnahmebedingungen muss jede Unterstützung (Personen, Institutionen, Datensätze, Computer, bestehende Algorithmen) mit Art der Hilfe angegeben werden.

## KI-Werkzeuge

| Datum | Werkzeug | Art der Unterstützung |
|---|---|---|
| 2026-10-16 | Claude (Anthropic), Claude Code (Fable 5.1) – KI-Recherche mit Unteragenten | Weltweite Recherche offener Ertragsdatensätze auf Feld-/Standortebene (Repositorien-APIs, Browser, Download-Verifikation von 12 Datensätzen); Bericht `reports/data_search.md` (Tabelle, Top 10, Standort-Jahre je Kultur, Anfragetexte) |
| 2026-10-16 | Claude (Anthropic), Claude Code (Opus 5.5 / Fable 5.1) | Zusammenfassung des Nachtlaufs für den Projektinhaber; Sentinel-2-Galerien der Trainingsfelder (`gallery.py`); mehrseitige Website (`app/ui/`, `app/versions.yaml`, Vergleich, Trainingsaufträge), Tests und Doku; Entwurf eines Recherche-Prompts für weitere Ertragsdatensätze |
| 2026-10-16 | Claude (Anthropic), Claude Code (Opus 5.5) – autonomer Nachtlauf | Phase 1–4 nach PLAN.md: Ertrags-Datensatz, GEE-Extraktion, Merkmale, Modellfamilie, Kontrolltests, Datenkritik; Notebooks 01–03, Streamlit-App, Innerhalb-Feld-Analyse, One-Acre-Fund-Tabellenanalyse, Phase-5-Regionalmodell und Doku-Entwürfe durch KI-Unteragenten (Claude Sonnet); private Fortschrittsseite (Claude-Artifact) |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Phase 0: Download und Sichtung One Acre Fund (`one_acre_fund.py`), SSURGO-Abfrage über Soil Data Access (`soil_ssurgo.py`), Suche, Download und Abschreiben der Versuchsberichte Hatzendorf/LK OÖ durch KI-Unteragenten (`at_trials.py`, nur Sammeln); Tests, Datenkritik-Nachtrag |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Recherche weiterer Ertrags- und Bodenquellen (One Acre Fund, YieldSAT, SSURGO, Versuchsberichte Hatzendorf/LK OÖ, Bodenklimazahl), Einbau in PLAN.md, Entwürfe der Anfragen in ANFRAGEN.md |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Umbau von PLAN.md/AGENTS.md nach Vorgabe des Projektinhabers (erst US-Modelle + Faktoren + Problemfelder, Einfrieren, Österreich nur als Test) |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Abschluss Phase 0: INVEKOS-Sichtung (Download und Zählung durch KI-Unteragenten, Modul `invekos.py`), Verwaltungsgrenzen, Notebook 00, Vervollständigung von `DATA_SOURCES.md` und Datenkritik, Umsetzung der Österreich-Regel in der Doku |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Phase 5 bis EU-Freeze: Modul `regional_cybench.py` (CY-Bench-Mais EU, YAS, LOCO, LightGBM, Freeze), Tests, Datenkritik, Freeze-Protokoll mit vorab registriertem AT-Testprotokoll (ohne Österreich-Daten) |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Phase 0: Python-Umgebung, Paketgerüst, `config.yaml`, Tests, GitHub Actions; GEE-Zugangstest inkl. Fehlerdiagnose (HLS-Footprints, TLS); Recherche, Download und Sichtung der Datenquellen durch KI-Unteragenten; Entwurf von `DATA_SOURCES.md`, Datenkritik-Bericht und Notebook 00 |
| 2026-10-15 | Claude (Anthropic), Claude Code | Diskussion und Verfeinerung der Projektidee, Recherche zu Datenquellen (u. a. Feld-Ertragsdatensätze KBS, BARC, Colorado, Mead), Entwurf und Überarbeitung von PLAN.md und AGENTS.md, Repository-Grundgerüst |

## Datensätze
Details, Lizenzen und Zitate in `DATA_SOURCES.md`.

| Datensatz | Anbieter | Nutzung |
|---|---|---|
| KBS LTER Agronomic Yields, Precision Ag, Scale-up | Kellogg Biological Station LTER (NSF DEB 2224712) | Feld-Ertragslabels (Veröffentlichung nur mit schriftlicher Erlaubnis) |
| BARC Gridded Yield Data Archive | USDA-ARS Beltsville (Dulaney et al., DOI 10.15482/USDA.ADC/28950746.v2) | Feld-Ertragslabels |
| One Acre Fund – Maize management and yield 2016–2022 | One Acre Fund; Aramburu-Merlos et al. 2024 (DOI 10.5281/zenodo.11115815, CC BY 4.0) | Querschnitt-Trainingsdaten (Nutzung offen, siehe DATA_SOURCES §9) |
| SSURGO (Soil Data Access) | USDA NRCS | US-Boden-Ertragspotenzial (NCCPI Mais, Mais-Ertragsschätzung) |
| Versuchsberichte Versuchsstation Hatzendorf; Praxisversuche Körnermais | Land Steiermark (Landwirtschaftliche Fachschulen); Landwirtschaftskammer Oberösterreich | Österreich-Test V2 (nur nach dem Freeze ausgewertet) |
| Akron Dryland Yield/TPI | USDA-ARS Akron (Poss et al., DOI 10.15482/USDA.ADC/28914434.v1) | Ergänzende Ertragspunkte |
| CY-Bench v1.10 | Kallenberg et al. 2026 (DOI 10.5281/zenodo.17279151) | Regionalmodell EU → AT |
| Feldfruchternte | Statistik Austria; Eurostat | Regionalerträge Österreich |
| INVEKOS Schläge, Verwaltungsgrenzen | AMA; Statistik Austria | Feldgrenzen Österreich |
| HLS v2, Sentinel-2, Cloud Score+ (über Google Earth Engine) | NASA, ESA/Copernicus, Google | Satellitenzeitreihen |

## Personen / Institutionen / KI-Advisors
_(keine bisher)_

## Code Dritter / Bibliotheken
Open-Source-Pakete laut `requirements.txt` (u. a. earthengine-api, geemap, geopandas, pandas, scikit-learn, LightGBM, PyTorch, SHAP, Streamlit); keine fremden Codeteile übernommen.
