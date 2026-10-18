# Delta Green – Web-Frontend

Präsentations- und Demo-Website für die BWKI-Jury (React 19, TypeScript, Vite, Tailwind CSS 4, MapLibre GL, Terra Draw, D3, Motion).
Läuft **nur lokal / privat** (KBS-Daten dürfen nur mit schriftlicher Erlaubnis veröffentlicht werden). Die Streamlit-App unter `app/` bleibt das interne Projektprotokoll.

## Starten

```
.venv\Scripts\python.exe web\scripts\export_web_data.py   # echte Daten -> web/public/data/*.json (nach jedem neuen Lauf)
.venv\Scripts\python.exe web\scripts\export_hero.py       # Feld der Startseite (BARC 2018) -> web/public/data/hero.json
cd web
npm install
npm run dev        # http://localhost:5180
npm run build      # Produktions-Build nach web/dist, Vorschau: npm run preview (Port 5181)
```

`web/public/data/` ist nicht im Repository (abgeleitet aus `data/` und `results/`); ohne den Export zeigen die Seiten einen Hinweis statt Zahlen.
Karten-Kacheln (Esri, EOX Sentinel-2 cloudless, OpenTopoMap) und die Ortssuche (OSM Nominatim) brauchen Internet; alles andere läuft offline.

## Woher die Zahlen kommen

| Inhalt | Quelle | Art |
|---|---|---|
| Benchmarks, Model card, Experimente, Österreich-Test | `web/public/data/evidence.json` ← `results/**` | echte Ergebnisse |
| Fünf vorbereitete Felder (Analyse-Seite, Startseite) | `fields.json` ← `data/app`, `data/processed`, `data/interim` (nur US-Standorte) | echte, nicht zum Training des bewertenden Modells genutzte Feld-Jahre (out-of-fold) |
| Datenexplorer | `explorer.json` ← `gt_field_years`, `features_0901`, `gt_dekads` | echte Trainingsdaten |
| Selbst gezeichnete Felder | `src/data/demo/simulatedAnalysis.ts` | **Simulation**, in der Oberfläche überall als „Simulated · backend not connected“ markiert |
| Texte zu Quellen, Pipeline, Grenzen, Roadmap | `src/data/content/project.ts` | aus `app/versions.yaml`, `reports/results.md`, `DATA_SOURCES.md` übernommen, mit Quellpfad |

Der Export liest keine österreichischen Roh- oder Merkmalsdaten; vom Österreich-Test werden nur die aggregierten Ergebnisse nach `freeze-at-1` gezeigt.

## Aufbau

```
src/
  api/          client.ts (fetch + Cache, VITE_API_BASE), types.ts (alle Datenformen)
  services/     fieldService.ts (vorbereitete Felder, runAnalysis), evidenceService.ts, geocodeService.ts
  state/        analysisMachine.ts (idle → fieldSelected → loadingSatellite … runningModel → completed | error)
  data/demo/    simulatedAnalysis.ts  – nur für gezeichnete Felder, klar markiert
  data/content/ project.ts            – statische Texte mit Quellenangaben
  components/   ui/ (Design-System), charts/ (SVG-Diagramme), field/ (Pixel-Feld, Pipeline, Ergebnisse), map/ (MapLibre + Terra Draw), layout/
  pages/        Home, Analyse, Evidence, ModelCard, Data, Method, About
scripts/        export_web_data.py
```

## Backend später anbinden

1. `VITE_API_BASE` auf den Server setzen; er liefert `fields.json`, `evidence.json`, `explorer.json` im gleichen Format (`src/api/types.ts`).
2. In `services/fieldService.ts` → `runAnalysis` den Simulationszweig durch einen Job-Aufruf ersetzen (POST Polygon, Fortschritt als Ereignisse) und die Ereignisse auf `onStage` / `onStageDone` abbilden. Die Zustandsmaschine und alle Komponenten bleiben unverändert.
3. Der Server liefert für ein Polygon ein `FieldAnalysis`-Objekt (Sentinel-2-Dekaden, ERA5-Land, SoilGrids, Stress-Score, optional 10-m-Zellen).

## Contribution backend (local)

The "Add your field" page posts to `/api/contributions`. Run the backend next to the dev server:

    python -m croptransfer.contrib_server        # http://127.0.0.1:8787, SQLite in data/contributions/

Vite proxies `/api` to it. Without the backend the entry is kept in the visitor's browser instead.
For a domain: `npm run build`, then run the same server with `--host 0.0.0.0` and `CT_ADMIN_TOKEN=<secret>`; it also serves `web/dist`.
Listing entries (`GET /api/contributions`) works from localhost, or with header `X-Admin-Token`.
