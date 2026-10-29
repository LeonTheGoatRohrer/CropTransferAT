# Delta Green (formerly CropTransferAT)

A scientific machine-learning project investigating early maize stress and yield-related signals from satellite time series, weather and soil data, with cross-region transfer as a research goal.

## Implemented features

- Field/time-series processing and yield-target construction in `src/croptransfer/`.
- Baselines, grouped validation, diagnostics and documented experiments.
- Streamlit project/result browser and a React/Vite presentation frontend.
- Versioned methodology, decisions, data provenance and assistance records.

## Technology

Python 3.11, scientific/geospatial Python dependencies from `requirements.txt`, Streamlit, React, TypeScript, Vite and MapLibre.

## Installation and local use

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\streamlit run app/streamlit_app.py
```

For the separate frontend: `cd web`, `npm ci --ignore-scripts`, then `npm run dev` or `npm run build`. Read `PLAN.md`, `DATA_SOURCES.md` and `DECISIONS.md` before running a data pipeline. A fresh checkout does not include the large local source datasets and models.

## Configuration and requirements

Obtain data through the documented providers and supply any required credentials locally. Do not commit `.env`, service-account keys, raw data or large trained models. The demo requires the corresponding locally generated outputs; it is not a complete online data service.

## Development status and limitations

Research prototype for BWKI Austria. Existing documentation records that the phase-4 strength gate was not passed, so there is no justified field-model freeze or Austrian field test. EU regional transfer and field-level mapping are separate documented results. Planned phases are not claimed as completed functionality. See `reports/doku/hauptergebnis.md`, `CHANGELOG.md` and the original German README for the detailed historical status.

## Contribution and attribution

Leon Rohrer: project owner and research/development contributor. AI and other assistance are recorded in `SUPPORT.md`; dataset and dependency attribution remains in `DATA_SOURCES.md` and the source notices.



## Publication notes

This portfolio copy includes project source and relevant documentation. Local credentials, private datasets, dependencies and generated build files are excluded. No deployment or paid service is configured by this publication. Existing copyright and license notices remain applicable; this publication does not introduce a new license.
