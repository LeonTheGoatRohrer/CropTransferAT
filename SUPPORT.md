# Unterstützung (BWKI-Pflichtangabe)

Laut Teilnahmebedingungen muss jede Unterstützung (Personen, Institutionen, Datensätze, Computer, bestehende Algorithmen) mit Art der Hilfe angegeben werden.

## KI-Werkzeuge

| Datum | Werkzeug | Art der Unterstützung |
|---|---|---|
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Umbau von PLAN.md/AGENTS.md nach Vorgabe des Projektinhabers (erst US-Modelle + Faktoren + Problemfelder, Einfrieren, Österreich nur als Test) |
| 2026-10-15 | Claude (Anthropic), Claude Code (Opus 5.5) | Phase 0: Python-Umgebung, Paketgerüst, `config.yaml`, Tests, GitHub Actions; GEE-Zugangstest inkl. Fehlerdiagnose (HLS-Footprints, TLS); Recherche, Download und Sichtung der Datenquellen durch KI-Unteragenten; Entwurf von `DATA_SOURCES.md`, Datenkritik-Bericht und Notebook 00 |
| 2026-10-15 | Claude (Anthropic), Claude Code | Diskussion und Verfeinerung der Projektidee, Recherche zu Datenquellen (u. a. Feld-Ertragsdatensätze KBS, BARC, Colorado, Mead), Entwurf und Überarbeitung von PLAN.md und AGENTS.md, Repository-Grundgerüst |

## Datensätze
Details, Lizenzen und Zitate in `DATA_SOURCES.md`.

| Datensatz | Anbieter | Nutzung |
|---|---|---|
| KBS LTER Agronomic Yields, Precision Ag, Scale-up | Kellogg Biological Station LTER (NSF DEB 2224712) | Feld-Ertragslabels (Veröffentlichung nur mit schriftlicher Erlaubnis) |
| BARC Gridded Yield Data Archive | USDA-ARS Beltsville (Dulaney et al., DOI 10.15482/USDA.ADC/28950746.v2) | Feld-Ertragslabels |
| Akron Dryland Yield/TPI | USDA-ARS Akron (Poss et al., DOI 10.15482/USDA.ADC/28914434.v1) | Ergänzende Ertragspunkte |
| CY-Bench v1.10 | Kallenberg et al. 2026 (DOI 10.5281/zenodo.17279151) | Regionalmodell EU → AT |
| Feldfruchternte | Statistik Austria; Eurostat | Regionalerträge Österreich |
| INVEKOS Schläge, Verwaltungsgrenzen | AMA; Statistik Austria | Feldgrenzen Österreich |
| HLS v2, Sentinel-2, Cloud Score+ (über Google Earth Engine) | NASA, ESA/Copernicus, Google | Satellitenzeitreihen |

## Personen / Institutionen / KI-Advisors
_(keine bisher)_

## Code Dritter / Bibliotheken
Open-Source-Pakete laut `requirements.txt` (u. a. earthengine-api, geemap, geopandas, pandas, scikit-learn, LightGBM, PyTorch, SHAP, Streamlit); keine fremden Codeteile übernommen.
