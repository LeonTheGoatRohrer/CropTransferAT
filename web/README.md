# CropTransfer AT – Web-Frontend

Präsentations- und Demo-Website für die BWKI-Jury (React 19, TypeScript, Vite, Tailwind CSS 4, react-i18next, MapLibre GL, Terra Draw, D3, Motion).
Sprachen: **Deutsch (Standard)**, Englisch, Spanisch, Französisch (Umschalter in der Navigation; Spanisch und Französisch sind KI-Übersetzungen und vor einer Veröffentlichung von einer sprachkundigen Person zu prüfen).
Läuft **nur lokal / privat** (KBS-Daten dürfen nur mit schriftlicher Erlaubnis veröffentlicht werden). Die Streamlit-App unter `app/` bleibt das interne Projektprotokoll.

## Starten

```
.venv\Scripts\python.exe web\scripts\export_web_data.py   # echte Daten -> web/public/data/*.json (nach jedem neuen Lauf)
cd web
npm install
npm run dev        # http://localhost:5180
npm run build      # Produktions-Build nach web/dist, Vorschau: npm run preview (Port 5181)
```

### Lokales Backend („Dein Feld, dein Verlauf“, Seite /konzept und gezeichnete Felder)

```
set PYTHONPATH=src
.venv\Scripts\python.exe -m croptransfer.webapi      # http://127.0.0.1:8765, API-Doku unter /docs
```

FastAPI + SQLite (`data/app_local/fields.sqlite`, nicht im Repository), nur auf 127.0.0.1, ohne Konten; Felder pseudonym.
Weg B ruft Google Earth Engine auf (HLS, ERA5-Land, SoilGrids); dafür muss der GEE-Zugang des Projektinhabers eingerichtet sein.
Läuft das Backend nicht, rechnet die Konzept-Seite Weg A im Browser (localStorage) und die Analyse-Seite zeigt für gezeichnete Felder die gekennzeichnete Simulation.

`web/public/data/` ist nicht im Repository (abgeleitet aus `data/` und `results/`); ohne den Export zeigen die Seiten einen Hinweis statt Zahlen.
Karten-Kacheln (Esri, EOX Sentinel-2 cloudless, OpenTopoMap) und die Ortssuche (OSM Nominatim) brauchen Internet; alles andere läuft offline.

## Woher die Zahlen kommen

| Inhalt | Quelle | Art |
|---|---|---|
| Benchmarks, Model card, Experimente, Österreich-Test | `web/public/data/evidence.json` ← `results/**` | echte Ergebnisse |
| Fünf vorbereitete Felder (Analyse-Seite, Startseite) | `fields.json` ← `data/app`, `data/processed`, `data/interim` (nur US-Standorte) | echte, nicht zum Training des bewertenden Modells genutzte Feld-Jahre (out-of-fold) |
| Datenexplorer | `explorer.json` ← `gt_field_years`, `features_0901`, `gt_dekads` | echte Trainingsdaten |
| Selbst gezeichnete Felder, Backend läuft | `src/croptransfer/field_pipeline.py` über `webapi.py` | echte Werte, eingefrorener Score (`freeze-at-1`), eingefrorene Warnlogik |
| Selbst gezeichnete Felder, ohne Backend | `src/data/demo/simulatedAnalysis.ts` | **Simulation**, überall als „Simulation · Backend nicht verbunden“ markiert |
| Warnlogik, Trefferquoten | `evidence.json` ← `results/2026-10-17_alert_calibration/` | echte Kalibrierung (US-Daten, out-of-fold) |
| Texte aller Sprachen | `src/i18n/locales/{de,en,es,fr}.ts` | Deutsch ist die Vorlage; Zahlen darin stammen aus `app/versions.yaml` / `reports/results.md` |

Der Export liest keine österreichischen Roh- oder Merkmalsdaten; vom Österreich-Test werden nur die aggregierten Ergebnisse nach `freeze-at-1` gezeigt.

## Aufbau

```
src/
  api/          client.ts (fetch + Cache, VITE_API_BASE), types.ts (alle Datenformen)
  i18n/         index.ts (i18next, useContent), lang.ts, locales/{de,en,es,fr}.ts
  services/     fieldService.ts (vorbereitete Felder, runAnalysis), backendService.ts (lokales Backend), fieldStore.ts (Backend oder Browser), evidenceService.ts, geocodeService.ts
  state/        analysisMachine.ts (idle → fieldSelected → loadingSatellite … runningModel → completed | error)
  data/demo/    simulatedAnalysis.ts  – nur für gezeichnete Felder, klar markiert
  components/   ui/ (Design-System), charts/ (SVG-Diagramme), field/ (Pixel-Feld, Pipeline, Ergebnisse), map/ (MapLibre + Terra Draw), layout/
  lib/          format.ts (Intl), baseline.ts (Weg A im Browser, gleich wie fielddb.py), dekads.ts, geo.ts
  pages/        Home, Analyse, Evidence, ModelCard, Data, Method, Concept, About
scripts/        export_web_data.py
```

## Backend

Die Analyse-Seite und die Konzept-Seite prüfen `GET /api/health` (Timeout 1,5 s). Endpunkte: `POST /api/fields`, `PUT /api/fields/{id}/yields`,
`PUT /api/fields/{id}/alert`, `POST /api/fields/{id}/analyses` (Hintergrundjob, Fortschritt über `GET /api/analyses/{id}`),
`GET /api/notifications`, `GET /api/calibration`. Ein späteres Hosting ist nicht Teil dieses Stands.
