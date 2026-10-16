"""Page 'Ergebnisse': one card per version from app/versions.yaml."""
from __future__ import annotations

import streamlit as st

from app.ui.common import STATUS, figure, glossary, lead, load_versions, repo_link, status_badge


def version_card(v: dict, expanded: bool) -> None:
    emoji, label, color = STATUS.get(v["status"], STATUS["zwischenstand"])
    head = f"{emoji} {v['date']} · {v['phase']} · {v['title']}"
    with st.expander(head, expanded=expanded):
        st.markdown(status_badge(v["status"]) + f' <span class="ct-muted">Version `{v["id"]}`</span>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="ct-big">Was wurde geändert: {v["changed"]}</div>', unsafe_allow_html=True)
        st.markdown(v["plain"])

        metrics = v.get("metrics") or []
        if metrics:
            st.markdown("**Die wichtigsten Zahlen**")
            cols = st.columns(min(3, len(metrics)))
            for i, m in enumerate(metrics):
                with cols[i % len(cols)]:
                    st.metric(m["label"], m["value"], help=m.get("plain"))
                    sub = " · ".join(x for x in [m.get("ci", ""), m.get("n", "")] if x)
                    if sub:
                        st.caption(sub)
                    st.markdown(f'<div class="ct-muted">{m.get("plain", "")}</div>', unsafe_allow_html=True)

        if v.get("found"):
            st.markdown("**Was wir gelernt haben**")
            st.markdown("\n".join(f"- {t}" for t in v["found"]))
        if v.get("limits"):
            st.markdown("**Grenzen**")
            st.markdown("\n".join(f"- {t}" for t in v["limits"]))

        figs = v.get("figures") or []
        if figs:
            st.markdown("**Abbildungen**")
            for f in figs:
                figure(f["file"], f.get("caption"))

        if v.get("links"):
            st.markdown("**Nachlesen im Repository**")
            st.markdown("\n".join(f"- {repo_link(l['label'], l['path'])}" for l in v["links"]))


def page() -> None:
    st.title("Ergebnisse – Version für Version")
    lead("Jede Karte ist ein abgeschlossener Schritt. Groß oben steht, <b>was geändert wurde</b>, darunter die Zahlen "
         "in einfacher Sprache, die Befunde und die Grenzen. Neueste zuerst.")
    reg = load_versions()
    versions = reg["versions"]

    only = st.multiselect("Nur bestimmte Stände zeigen", [v["id"] for v in versions], default=[],
                          placeholder="Alle Versionen")
    shown = [v for v in versions if not only or v["id"] in only]

    st.markdown("**Überblick**")
    rows = [{"Datum": v["date"], "Version": v["id"], "Phase": v["phase"], "Titel": v["title"],
             "Status": STATUS.get(v["status"], STATUS["zwischenstand"])[1]} for v in versions]
    st.dataframe(rows, hide_index=True, width="stretch")

    for i, v in enumerate(shown):
        version_card(v, expanded=(i == 0 or bool(only)))

    glossary(["ρ (Rangkorrelation)", "95-%-KI", "RY (relativer Ertrag)", "PR-AUC", "Standort-Jahr", "LOFYO"])
