"""Page 'Vergleich': interactive benchmark across runs, models, bases and cutoffs."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from app.ui.common import CUTOFFS, cutoff_label, data_problem, fmt, glossary, lead, load_versions

METRICS = {
    "rho": ("Rangkorrelation ρ (höher = besser)", "rho_lo", "rho_hi"),
    "median_within_year_rho": ("ρ innerhalb eines Jahres (höher = besser)", None, None),
    "skill_b0": ("Skill gegenüber „normales Jahr“ (höher = besser, 0 = gleich)", None, None),
    "rmse": ("Fehler RMSE (kleiner = besser)", None, None),
    "r2": ("R² (höher = besser; negativ = schlechter als Mittelwert)", None, None),
}


def _labels(reg: dict, b: pd.DataFrame) -> pd.DataFrame:
    b = b.copy()
    b["Modell"] = b["model"].map(lambda m: f"{m} – {reg['model_names'].get(m, m)}")
    b["Verfahren"] = b["kind"].map(lambda k: reg["kind_names"].get(k, k))
    b["Basis"] = b["basis"].map(lambda k: reg["basis_names"].get(k, k))
    b["Stichtag"] = b["cutoff"].map(cutoff_label)
    b["Konfiguration"] = b["run_label"] + " · " + b["model"] + " · " + b["kind"] + " · " + b["basis"]
    return b


def stages_chart(stages: list[dict]) -> alt.Chart:
    df = pd.DataFrame(stages)
    df["label"] = df["stage"]
    base = alt.Chart(df).encode(x=alt.X("label:N", title=None, sort=None, axis=alt.Axis(labelAngle=0, labelLimit=200)))
    bars = base.mark_bar(size=40).encode(
        y=alt.Y("rho:Q", title="ρ am 1. September", scale=alt.Scale(domain=[-0.5, 1])),
        color=alt.condition(alt.datum.passed, alt.value("#2e9e4f"), alt.value("#999999")),
        tooltip=[alt.Tooltip("stage:N", title="Stufe"), alt.Tooltip("model:N", title="Modell"),
                 alt.Tooltip("rho:Q", title="ρ", format=".2f"), alt.Tooltip("rho_lo:Q", title="KI unten", format=".2f"),
                 alt.Tooltip("rho_hi:Q", title="KI oben", format=".2f"), alt.Tooltip("n:Q", title="n")])
    err = base.mark_rule(color="black").encode(y="rho_lo:Q", y2="rho_hi:Q")
    goal = alt.Chart(pd.DataFrame({"y": [0.4]})).mark_rule(color="#d62728", strokeDash=[6, 4]).encode(y="y:Q")
    zero = alt.Chart(pd.DataFrame({"y": [0.0]})).mark_rule(color="#888").encode(y="y:Q")
    return (bars + err + goal + zero).properties(height=320)


def curve_chart(b: pd.DataFrame, metric: str, lo: str | None, hi: str | None) -> alt.Chart:
    order = [cutoff_label(c) for c in CUTOFFS]
    x = alt.X("Stichtag:N", sort=order, title="Stichtag (bis wann das Modell schauen darf)")
    color = alt.Color("Konfiguration:N", legend=alt.Legend(orient="bottom", columns=1, labelLimit=600))
    line = alt.Chart(b).mark_line(point=True).encode(
        x=x, y=alt.Y(f"{metric}:Q", title=METRICS[metric][0]), color=color,
        tooltip=["Konfiguration:N", "Stichtag:N", alt.Tooltip(f"{metric}:Q", format=".3f"),
                 alt.Tooltip("n:Q", title="n"), alt.Tooltip("clusters:Q", title="Standort-Jahre")])
    layers = [line]
    if lo and hi and lo in b and hi in b:
        band = alt.Chart(b).mark_area(opacity=0.12).encode(x=x, y=f"{lo}:Q", y2=f"{hi}:Q", color=color)
        layers = [band, line]
    if metric in ("rho", "skill_b0", "median_within_year_rho", "r2"):
        layers.append(alt.Chart(pd.DataFrame({"y": [0.0]})).mark_rule(color="#888").encode(y="y:Q"))
    if metric == "rho":
        layers.append(alt.Chart(pd.DataFrame({"y": [0.4]})).mark_rule(color="#d62728", strokeDash=[6, 4]).encode(y="y:Q"))
    return alt.layer(*layers).properties(height=380)


def page(data: dict | None) -> None:
    st.title("Vergleich der Modelle")
    lead("Hier kannst du selbst vergleichen: Welche Modellvariante, welcher Satellit, welcher Stichtag? "
         "Alle Zahlen sind Out-of-Sample (Feld und Jahr ungesehen). Die rote Linie ist das Ziel ρ ≥ 0,4.")
    problem = data_problem(data)
    if problem:
        st.error(problem)
        return
    reg = load_versions()
    b = data.get("benchmarks")
    if b is None or b.empty:
        st.error("`data/app/benchmarks.csv` fehlt. Bitte `python app/precompute.py` ausführen.")
        return

    st.subheader("Die Meilensteine auf einen Blick")
    st.markdown("Je Stufe das vorab nach Regel gewählte Modell am 1. September, mit Vertrauensbereich. "
                "Grün wäre „stark genug“ – keine Stufe hat es geschafft.")
    if data.get("stages"):
        st.altair_chart(stages_chart(data["stages"]), width="stretch")
        rows = [{"Stufe": s["stage"], "Modell": f"{s['model']} ({s['kind']}, {s['basis']})",
                 "ρ 1.9.": fmt(s["rho"]), "95-%-KI": f"{fmt(s['rho_lo'])} … {fmt(s['rho_hi'])}",
                 "Krit. 1 (RMSE < B0/B1)": "✓" if s["c1"] else "✗", "Krit. 2 (ρ ≥ 0,4)": "✓" if s["c2"] else "✗",
                 "Krit. 3 (Übertragung Standorte)": "✓" if s["c3"] else "✗", "Krit. 4 (Shuffle ≈ 0)": "✓" if s["c4"] else "✗",
                 "stark genug": "ja" if s["passed"] else "nein"} for s in data["stages"]]
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info("Keine Meilenstein-Daten (`stages.json`).")

    st.markdown("---")
    st.subheader("Eigener Vergleich")
    b = _labels(reg, b)
    c1, c2, c3 = st.columns([1.2, 1, 1])
    runs = c1.multiselect("Läufe", sorted(b["run_label"].unique(), key=lambda s: s), default=sorted(b["run_label"].unique()))
    bases = c2.multiselect("Satellit", sorted(b["basis"].unique()), default=["S2"] if "S2" in set(b["basis"]) else sorted(b["basis"].unique()),
                           format_func=lambda k: reg["basis_names"].get(k, k))
    kinds = c3.multiselect("Verfahren", sorted(b["kind"].unique()), default=sorted(b["kind"].unique()),
                           format_func=lambda k: reg["kind_names"].get(k, k))
    sub = b[b["run_label"].isin(runs) & b["basis"].isin(bases) & b["kind"].isin(kinds)]
    if "variant" in sub:
        variants = sorted(sub["variant"].dropna().unique())
        if len(variants) > 1:
            var = st.multiselect("Variante", variants, default=[v for v in variants if v in ("main", "-")] or variants)
            sub = sub[sub["variant"].isin(var)]
    models = sorted(sub["model"].unique())
    default_models = [m for m in models if m in ("M-S", "M-alle", "M-Srel", "M-alle-rel", "B1")] or models[:4]
    chosen = st.multiselect("Modelle", models, default=default_models,
                            format_func=lambda m: f"{m} – {reg['model_names'].get(m, m)}")
    sub = sub[sub["model"].isin(chosen)]
    metric = st.selectbox("Kennzahl", list(METRICS), format_func=lambda k: METRICS[k][0])

    if sub.empty:
        st.info("Keine Daten für diese Auswahl.")
        return
    _, lo, hi = METRICS[metric]
    st.altair_chart(curve_chart(sub, metric, lo, hi), width="stretch")
    st.caption("Band = 95-%-Vertrauensbereich (nur bei ρ). Graue Linie = 0, rote gestrichelte Linie = Ziel 0,4.")

    cut = st.select_slider("Tabelle für Stichtag", options=[c for c in CUTOFFS if c in set(sub["cutoff"])],
                           value="09-01" if "09-01" in set(sub["cutoff"]) else None, format_func=cutoff_label)
    t = sub[sub["cutoff"] == cut].sort_values(metric, ascending=(metric == "rmse"))
    table = pd.DataFrame({
        "Lauf": t["run_label"], "Modell": t["Modell"], "Verfahren": t["Verfahren"], "Satellit": t["basis"],
        "n": t["n"], "Standort-Jahre": t["clusters"],
        "ρ": [fmt(v) for v in t["rho"]], "95-%-KI ρ": [f"{fmt(a)} … {fmt(c)}" for a, c in zip(t["rho_lo"], t["rho_hi"])],
        "ρ innerhalb Jahr": [fmt(v) for v in t["median_within_year_rho"]],
        "RMSE": [fmt(v, 3) for v in t["rmse"]], "Skill vs. B0": [fmt(v) for v in t["skill_b0"]],
    })
    st.dataframe(table, hide_index=True, width="stretch")
    st.caption("ρ innerhalb Jahr = Median der Rangkorrelation zwischen Feldern desselben Jahres (Kontrolle gegen „das Modell kennt nur das Jahr“).")

    glossary(["ρ (Rangkorrelation)", "95-%-KI", "RMSE", "Skill", "B0 / B1", "LOFYO", "Stichtag"])
