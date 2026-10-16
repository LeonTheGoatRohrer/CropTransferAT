"""Shared helpers for the website: data loading, formatting, glossary, styling.

Everything reads only data/app/ (written by app/precompute.py), app/versions.yaml,
reports/figures/ and a few Markdown files. No GEE, no raw data, no Austrian data.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
APP_DATA = ROOT / "data" / "app"
FIG_DIR = ROOT / "reports" / "figures"
VERSIONS_FILE = APP_DIR / "versions.yaml"

SEASON_START = (4, 1)  # dekad 0 = 1 April, dekad d = 1 April + 10*d days
CUTOFFS = ["06-01", "06-15", "07-01", "07-15", "08-01", "08-15", "09-01"]

# Traffic light after PLAN.md Phase 9 (lower bound inclusive, checked top-down).
AMPEL = [
    (0.95, "🟢", "gesund (RY ≥ 0,95)", "#2e9e4f"),
    (0.85, "🟡", "leicht unterdurchschnittlich (0,85–0,95)", "#e6c200"),
    (0.75, "🟠", "deutlich unterdurchschnittlich (0,75–0,85)", "#f08c00"),
    (-np.inf, "🔴", "Problemfeld (RY < 0,75)", "#d62728"),
]
UNKNOWN = ("⚪", "unbekannt", "#888888")

STATUS = {
    "abgeschlossen": ("✅", "abgeschlossen", "#2e9e4f"),
    "eingeschraenkt": ("⚠️", "abgeschlossen mit Einschränkung", "#e6a700"),
    "nicht_bestanden": ("⛔", "Kriterium nicht bestanden", "#d62728"),
    "eingefroren": ("🧊", "eingefroren – Test wartet auf Freigabe", "#1f77b4"),
    "zwischenstand": ("🔧", "Zwischenstand", "#888888"),
}

# Plain-language glossary (shown via "Was heißt das?" expanders).
GLOSSARY = {
    "ρ (Rangkorrelation)": "Spearman-Rangkorrelation zwischen Vorhersage und gemessenem Wert. 0 = Zufall, 1 = perfekte "
                           "Reihenfolge, negativ = verkehrt herum. Ab etwa 0,4 beginnt es nützlich zu werden.",
    "95-%-KI": "Vertrauensbereich: Wiederholt man die Auswertung mit anderen Jahren, läge die Zahl in 95 von 100 "
               "Fällen in diesem Bereich. Enthält der Bereich die 0, ist der Effekt nicht gesichert.",
    "RY (relativer Ertrag)": "Ertrag dieses Jahres geteilt durch das Normalniveau desselben Feldes in anderen Jahren. "
                             "1,0 = normal, 0,8 = 20 % weniger, 1,2 = 20 % mehr.",
    "gefährdet": "Ein Feld-Jahr mit RY unter 0,85, also mindestens 15 % unter dem eigenen Normalniveau.",
    "Standort-Jahr": "Ein Ort in einem Jahr. Felder am selben Ort im selben Jahr erleben dasselbe Wetter und zählen "
                     "deshalb nur als EIN unabhängiger Fall.",
    "Feld-Jahr": "Ein Feld in einem Jahr mit gemessenem Ertrag – die kleinste Einheit der Daten.",
    "Stichtag": "Das Datum, bis zu dem das Modell schauen darf. Am 1. Juli kennt es nur Daten bis zum 1. Juli.",
    "LOFYO": "Leave-one-field-year-out: Beim Bewerten hat das Modell weder das Feld noch das Jahr gesehen. Die "
             "strengste Prüfung.",
    "PR-AUC": "Güte beim Erkennen gefährdeter Felder. Zufälliges Raten ergibt den Anteil der gefährdeten Felder "
              "(hier 0,33); 1,0 wäre perfekt.",
    "RMSE": "Mittlerer Fehler der Vorhersage. Kleiner ist besser.",
    "Skill": "Um wie viel Prozent der Fehler kleiner ist als bei der einfachen Annahme „normales Jahr“. "
             "0 = gleich gut, negativ = schlechter.",
    "B0 / B1": "Vergleichsmaßstäbe. B0 = „jedes Jahr ist normal“ (RY = 1). B1 = nur eine einzige Zahl "
               "(das NDVI-Maximum bis zum Stichtag).",
    "NDVI / EVI": "Grünindizes aus den Satellitenbildern: Wie dicht und grün ist der Bestand? Werte etwa 0,2 "
                  "(nackter Boden) bis 0,9 (dichter Mais).",
    "Einfrieren (Freeze)": "Modell, Merkmale, Schwellen und Testregeln werden mit Prüfsummen festgehalten, BEVOR "
                           "der Test läuft. Danach wird nichts mehr geändert – sonst wäre der Test kein Beweis.",
    "Österreich-Regel": "Bis zum Einfrieren wird keine österreichische Zahl ausgewertet. Österreich ist der Test, "
                        "nicht das Training.",
}


def ampel(ry: float | None) -> tuple[str, str, str]:
    """Map a relative yield (RY) to (emoji, label, hex colour)."""
    if ry is None or not np.isfinite(ry):
        return UNKNOWN
    for lower, emoji, label, color in AMPEL:
        if ry >= lower:
            return emoji, label, color
    return UNKNOWN


def fmt(x: float | None, digits: int = 2) -> str:
    """German number format (decimal comma); NaN -> en dash."""
    if x is None or not np.isfinite(x):
        return "–"
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def cutoff_date(year: int, cutoff: str) -> date:
    month, day = (int(p) for p in cutoff.split("-"))
    return date(year, month, day)


def dekad_date(year: int, dekad: int) -> date:
    return date(year, *SEASON_START) + timedelta(days=10 * int(dekad))


def cutoff_label(cutoff: str) -> str:
    """'09-01' -> '1.9.'"""
    month, day = (int(p) for p in cutoff.split("-"))
    return f"{day}.{month}."


# ---------------------------------------------------------------- loading
@st.cache_data(show_spinner=False)
def load_versions(path: str = str(VERSIONS_FILE)) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_app_data(path: str = str(APP_DATA)) -> dict:
    """Load all precomputed files; returns {'error': text} if files are missing."""
    base = Path(path)
    if not base.exists():
        return {"error": "Keine App-Daten gefunden (`data/app/` fehlt)"}
    needed = ["fields.parquet", "dekads.parquet", "reference.parquet", "yield_points.parquet",
              "oof.parquet", "metrics.csv", "progress.json", "model_spec_used.json"]
    missing = [f for f in needed if not (base / f).exists()]
    if missing:
        return {"error": "Fehlende Dateien in data/app/: " + ", ".join(missing)}
    import geopandas as gpd

    data = {
        "fields": gpd.read_parquet(base / "fields.parquet"),
        "dekads": pd.read_parquet(base / "dekads.parquet"),
        "reference": pd.read_parquet(base / "reference.parquet"),
        "points": pd.read_parquet(base / "yield_points.parquet"),
        "oof": pd.read_parquet(base / "oof.parquet"),
        "metrics": pd.read_csv(base / "metrics.csv", dtype={"cutoff": str}),
        "progress": json.loads((base / "progress.json").read_text(encoding="utf-8")),
        "spec": json.loads((base / "model_spec_used.json").read_text(encoding="utf-8")),
    }
    bench = base / "benchmarks.csv"
    data["benchmarks"] = pd.read_csv(bench, dtype={"cutoff": str}) if bench.exists() else None
    stages = base / "stages.json"
    data["stages"] = json.loads(stages.read_text(encoding="utf-8")) if stages.exists() else None
    return data


def data_problem(data: dict | None) -> str | None:
    """Readable message if the app data cannot be used, else None."""
    if data is None or "error" in data:
        msg = data["error"] if data else "Keine App-Daten gefunden (`data/app/` fehlt)"
        return msg + ". Bitte `python app/precompute.py` ausführen."
    return None


def read_markdown(rel_path: str) -> str | None:
    p = ROOT / rel_path
    return p.read_text(encoding="utf-8") if p.exists() else None


# ---------------------------------------------------------------- UI pieces
CSS = """
<style>
html, body, [class*="css"] { font-size: 17px; }
.block-container { max-width: 1100px; padding-top: 1.5rem; }
h1 { font-size: 2.1rem !important; }
h2 { font-size: 1.55rem !important; margin-top: 1.2rem !important; }
h3 { font-size: 1.2rem !important; }
.ct-big { font-size: 1.35rem; line-height: 1.5; font-weight: 600; margin: 0.4rem 0 0.8rem 0; }
.ct-lead { font-size: 1.15rem; line-height: 1.6; }
.ct-badge { display:inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; color: white;
            font-weight: 600; font-size: 0.9rem; margin-right: 0.4rem; }
.ct-card { border: 1px solid rgba(128,128,128,0.25); border-radius: 12px; padding: 1rem 1.2rem;
           margin-bottom: 1rem; background: rgba(128,128,128,0.04); }
.ct-step { border-left: 5px solid #2e9e4f; padding: 0.3rem 0 0.3rem 1rem; margin: 0.6rem 0; }
.ct-step.off { border-left-color: #bbbbbb; color: #777; }
.ct-step.now { border-left-color: #e6a700; }
.ct-muted { color: #777; font-size: 0.95rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return f'<span class="ct-badge" style="background:{color}">{text}</span>'


def status_badge(status: str) -> str:
    emoji, label, color = STATUS.get(status, STATUS["zwischenstand"])
    return badge(f"{emoji} {label}", color)


def big(text: str) -> None:
    st.markdown(f'<div class="ct-big">{text}</div>', unsafe_allow_html=True)


def lead(text: str) -> None:
    st.markdown(f'<div class="ct-lead">{text}</div>', unsafe_allow_html=True)


def glossary(keys: list[str] | None = None, title: str = "Was heißt das? (Begriffe)") -> None:
    keys = keys or list(GLOSSARY)
    with st.expander(title):
        for k in keys:
            if k in GLOSSARY:
                st.markdown(f"**{k}** – {GLOSSARY[k]}")


def figure(name: str, caption: str | None = None) -> bool:
    p = FIG_DIR / name
    if not p.exists():
        st.caption(f"Abbildung fehlt: `reports/figures/{name}`")
        return False
    st.image(str(p), caption=caption or name, width="stretch")
    return True


def repo_link(label: str, rel_path: str) -> str:
    """Markdown for a repository path (no web link – the site is local and private)."""
    exists = (ROOT / rel_path).exists()
    return f"`{rel_path}`" + ("" if exists else " (fehlt)") + f" – {label}"
