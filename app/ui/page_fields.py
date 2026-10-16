"""Page 'Felder ansehen': one US field-year with map, season curve and prediction (the original demo)."""
from __future__ import annotations

from datetime import date

import altair as alt
import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from app.ui.common import AMPEL, ampel, cutoff_date, data_problem, dekad_date, fmt, glossary, lead

MAX_MAP_POINTS = 1500
INDEX_LABELS = {"ndvi": "NDVI", "evi": "EVI", "ndmi": "NDMI", "gndvi": "GNDVI", "ndre": "NDRE"}


# ---------------------------------------------------------------- map
def build_map(geom, points: pd.DataFrame, color: str) -> folium.Map:
    minx, miny, maxx, maxy = geom.bounds
    m = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=16, control_scale=True,
                   tiles=None)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery", name="Satellit").add_to(m)
    folium.TileLayer("OpenStreetMap", name="Karte").add_to(m)
    fill = 0.05 if len(points) else 0.25
    folium.GeoJson(geom.__geo_interface__, name="Feld",
                   style_function=lambda _f: {"color": color, "weight": 3, "fillOpacity": fill,
                                              "fillColor": color}).add_to(m)
    if len(points):
        if len(points) > MAX_MAP_POINTS:
            points = points.iloc[:: int(np.ceil(len(points) / MAX_MAP_POINTS))]
        for r in points.itertuples():
            if r.problem:
                c = "#d62728"
            elif r.rel_yield < 0.95:
                c = "#f5d90a"
            else:
                c = "#2e9e4f"
            folium.CircleMarker([r.lat, r.lon], radius=2, color=c, weight=0, fill=True, fill_color=c,
                                fill_opacity=0.85,
                                tooltip=f"{fmt(r.yield_t_ha)} t/ha (relativ {fmt(r.rel_yield)})").add_to(m)
    m.fit_bounds([[miny, minx], [maxy, maxx]])
    folium.LayerControl(collapsed=True).add_to(m)
    return m


# ---------------------------------------------------------------- charts
def season_chart(curve: pd.DataFrame, ref: pd.DataFrame, label: str, year: int) -> alt.Chart:
    ref = ref.dropna(subset=["median"]).assign(datum=lambda d: [dekad_date(year, k) for k in d["dekad"]])
    curve = curve.assign(datum=[dekad_date(year, k) for k in curve["dekad"]])
    x = alt.X("datum:T", title="Datum", axis=alt.Axis(format="%d.%m."))
    band = alt.Chart(ref).mark_area(opacity=0.25, color="#2e9e4f").encode(
        x=x, y=alt.Y("p25:Q", title=label), y2="p75:Q")
    med = alt.Chart(ref).mark_line(color="#2e9e4f", strokeDash=[5, 3]).encode(x=x, y="median:Q")
    line = alt.Chart(curve).mark_line(color="#1f4e9c").encode(x=x, y="value:Q")
    pts = alt.Chart(curve).mark_point(filled=True, color="#1f4e9c", size=45).encode(
        x=x, y="value:Q", opacity=alt.condition(alt.datum.is_observed, alt.value(1), alt.value(0.25)),
        tooltip=[alt.Tooltip("datum:T", title="Datum", format="%d.%m."),
                 alt.Tooltip("value:Q", title=label, format=".3f"),
                 alt.Tooltip("is_observed:N", title="beobachtet")])
    return (band + med + line + pts).properties(height=280)


def prediction_chart(pred: pd.DataFrame, measured: float, year: int, asof: date) -> alt.Chart:
    lo = float(min(0.5, np.nanmin([measured, *pred["pred"]])) - 0.05)
    hi = float(max(1.3, np.nanmax([measured, *pred["pred"]])) + 0.05)
    edges = [lo, 0.75, 0.85, 0.95, hi]
    bands = pd.DataFrame({"lo": edges[:-1], "hi": edges[1:], "farbe": [a[3] for a in AMPEL[::-1]]})
    bg = alt.Chart(bands).mark_rect(opacity=0.14).encode(
        y=alt.Y("lo:Q", scale=alt.Scale(domain=[lo, hi]), title="relativer Ertrag (RY)"), y2="hi:Q",
        color=alt.Color("farbe:N", scale=None))
    x = alt.X("datum:T", title="Stichtag",
              scale=alt.Scale(domain=[date(year, 5, 15).isoformat(), date(year, 10, 15).isoformat()]),
              axis=alt.Axis(format="%d.%m."))
    pred = pred.assign(datum=[cutoff_date(year, c) for c in pred["cutoff"]])
    line = alt.Chart(pred).mark_line(color="#1f4e9c").encode(x=x, y="pred:Q")
    pts = alt.Chart(pred).mark_point(filled=True, color="#1f4e9c", size=70).encode(
        x=x, y="pred:Q", tooltip=[alt.Tooltip("datum:T", title="Stichtag", format="%d.%m."),
                                  alt.Tooltip("pred:Q", title="Vorhersage RY", format=".2f")])
    rule = alt.Chart(pd.DataFrame({"y": [measured]})).mark_rule(color="black", strokeDash=[6, 4]).encode(y="y:Q")
    return (bg + rule + line + pts).properties(height=280)


def page(data: dict | None) -> None:
    st.title("Felder ansehen")
    lead("Wähle ein US-Feld und ein Jahr. Mit dem Datumsregler siehst du, was das Modell <b>zu diesem Zeitpunkt</b> "
         "gewusst hätte – und was am Ende wirklich geerntet wurde.")
    problem = data_problem(data)
    if problem:
        st.error(problem)
        return
    fields, oof, spec = data["fields"], data["oof"], data["spec"]
    status = spec.get("status_text")
    if status:
        st.warning(f"**Hinweis zur Modellgüte:** {status}")
    else:
        st.warning("**Hinweis:** Für dieses Modell ist kein Eignungsurteil („stark genug“) hinterlegt.")
    st.caption(f"Modell: {spec['model']} ({spec['kind']}, Basis {spec['basis']}, Variante {spec['variant']}) · "
               f"Lauf `{spec['run_dir']}` · nur Out-of-Sample-Vorhersagen.")
    avail = fields[fields["fy_key"].isin(oof["fy_key"])]
    if avail.empty:
        st.info("Keine Out-of-Sample-Vorhersagen für die gewählte Modellkonfiguration vorhanden.")
        return

    c1, c2, c3 = st.columns(3)
    dataset = c1.selectbox("Datensatz", sorted(avail["dataset"].unique()))
    sub = avail[avail["dataset"] == dataset]
    field_uid = c2.selectbox("Feld", sorted(sub["field_uid"].unique()))
    sub = sub[sub["field_uid"] == field_uid]
    year = int(c3.selectbox("Jahr", sorted(int(y) for y in sub["year"].unique())))
    row = sub[sub["year"] == year].iloc[0]
    fy = row["fy_key"]

    asof = st.slider("Datum („nur was zu diesem Datum bekannt war“)", min_value=date(year, 5, 1),
                     max_value=date(year, 10, 15), value=date(year, 9, 1), format="DD.MM.YYYY",
                     key=f"asof_{fy}")
    pred_all = oof[oof["fy_key"] == fy].sort_values("cutoff")
    pred = pred_all[[cutoff_date(year, c) <= asof for c in pred_all["cutoff"]]]
    measured = float(pred_all["y"].iloc[0])
    last_pred = float(pred["pred"].iloc[-1]) if len(pred) else float("nan")
    emoji, label, color = ampel(last_pred)
    m_emoji, m_label, _ = ampel(measured)

    k1, k2, k3 = st.columns(3)
    k1.metric("Vorhersage RY (letzter Stichtag bis Datum)", f"{emoji} {fmt(last_pred)}" if len(pred) else "–",
              help=label if len(pred) else "Zu diesem Datum liegt noch keine Vorhersage vor.")
    k2.metric("Gemessener RY (erst nach der Ernte bekannt)", f"{m_emoji} {fmt(measured)}", help=m_label)
    k3.metric("Gemessener Ertrag", f"{fmt(row['Y_t_ha'])} t/ha")
    if pred.empty:
        st.info(f"Bis {asof.strftime('%d.%m.%Y')} gibt es keinen Vorhersage-Stichtag "
                f"(vorhanden: {', '.join(pred_all['cutoff'])}).")

    left, right = st.columns(2)
    with left:
        st.subheader("Karte")
        pts = data["points"]
        pts = pts[pts["fy_key"] == fy]
        m = build_map(row.geometry, pts, color if len(pred) else "#888888")
        st_folium(m, height=420, use_container_width=True, returned_objects=[], key=f"map_{fy}")
        if len(pts):
            share = 100 * int(pts["problem"].sum()) / len(pts)
            st.caption("Gemessene Ertragspixel (10 m): 🟢 ≥ 0,95 · 🟡 0,85–0,95 · 🔴 Problemzone (< 0,85 des "
                       f"Feldmittels) – {fmt(share, 1)} % der {len(pts)} Pixel. Feldumriss: Ampelfarbe der Vorhersage.")
        else:
            st.caption("Für diesen Datensatz gibt es keine Ertragspixel (nur Feldmittel). "
                       "Feldumriss: Ampelfarbe der Vorhersage.")
    with right:
        st.subheader("Saisonkurve gegen „gesunden Mais“")
        idx = st.selectbox("Index", list(INDEX_LABELS), format_func=INDEX_LABELS.get)
        basis = spec["basis"]
        d = data["dekads"]
        curve = d[(d["fy_key"] == fy) & (d["index"] == idx) & (d["basis"] == basis)].sort_values("dekad")
        curve = curve[[dekad_date(year, k) <= asof for k in curve["dekad"]]]
        r = data["reference"]
        ref = r[(r["index"] == idx) & (r["basis"] == basis)].sort_values("dekad")
        if curve.empty:
            st.info("Keine Satellitenwerte bis zu diesem Datum.")
        else:
            st.altair_chart(season_chart(curve, ref, INDEX_LABELS[idx], year), width="stretch")
            n_ref = int(ref["n_fieldyears"].iloc[0]) if len(ref) else 0
            st.caption(f"Blau: dieses Feld ({basis}; blasse Punkte = aus der letzten Beobachtung fortgeschrieben). "
                       f"Grün: Median und 25/75-%-Band der Feld-Jahre mit RY ≥ 0,95 (n = {n_ref}).")

    st.subheader("Vorhersage über die Stichtage")
    if pred.empty:
        st.caption("Noch keine Vorhersage zu diesem Datum.")
    else:
        st.altair_chart(prediction_chart(pred, measured, year, asof), width="stretch")
        st.caption("Blau: Vorhersage des relativen Ertrags (RY) je Stichtag. Schwarz gestrichelt: gemessener RY. "
                   "Hintergrund: 🟢 ≥ 0,95 · 🟡 0,85–0,95 · 🟠 0,75–0,85 · 🔴 < 0,75. "
                   "Ein Unsicherheitsband ist noch nicht berechnet.")
    glossary(["RY (relativer Ertrag)", "Stichtag", "NDVI / EVI", "LOFYO"])
