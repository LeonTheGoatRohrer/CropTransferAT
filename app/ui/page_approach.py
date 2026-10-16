"""Page 'Vorgehen & Quellen': the plan as a timeline, the rules, the data sources."""
from __future__ import annotations

import streamlit as st

from app.ui.common import glossary, lead

# (phase, title, plain description, state) – state: done | now | off
STEPS = [
    ("Phase 0", "Daten finden und prüfen", "Welche Daten gibt es, wem gehören sie, dürfen wir sie nutzen?", "done"),
    ("Phase 1", "Ertragsdaten aufbereiten", "Jedes Feld-Jahr bekommt: gemessener Ertrag, Satellitenkurve, Wetter, Boden.", "done"),
    ("Phase 2", "Was bestimmt den Ertrag?", "Modelle lernen aus Satellit, Wetter und Boden – einzeln und kombiniert.", "done"),
    ("Phase 3", "Problemfelder erkennen", "Gefährdete Felder früh finden und die wahrscheinliche Ursache eingrenzen.", "done"),
    ("Phase 4", "Stark genug? → Einfrieren", "Vorab festgelegtes Kriterium. Bestanden → Modell einfrieren. Nicht bestanden → nicht nach Österreich.", "now"),
    ("Phase 5", "Gegenprobe: EU-Regionalmodell", "Ein zweites Modell auf Bundesland-Ebene aus 16 EU-Ländern (eingefroren, Test wartet).", "done"),
    ("Phase 6", "Österreich-Daten aufbereiten", "INVEKOS-Feldgrenzen der Steiermark, Satellitenkurven, Regionalerträge.", "off"),
    ("Phase 7", "Der Beweis: Test in Österreich", "Eingefrorenes Modell ohne Anpassung auf steirische Felder anwenden und gegen echte Erträge prüfen.", "off"),
    ("Phase 8", "Zusatz: mit Österreich-Daten verbessern", "Erst nach dem Beweis: österreichische Daten (z. B. Hagelversicherung) ins Training.", "off"),
    ("Phase 9–10", "Demo und Abgabe", "Diese Website, Dokumentation, Video.", "off"),
]

SOURCES = [
    ("Erträge", "KBS LTER (Michigan, USA)", "24 Versuchsparzellen, Mais seit 1989, Ertrag mit Mähdrescher gewogen",
     "294 Feld-Jahre", "Erlaubnis für Veröffentlichung angefragt"),
    ("Erträge", "USDA BARC (Maryland, USA)", "Ertragskarten des Mähdreschers, 10 m fein, 2014–2021",
     "61 Feld-Jahre, 46 000 Ertragspunkte", "frei (US Public Domain)"),
    ("Erträge", "Colorado Trockenfarm (USA)", "Stichprobenpunkte, 2019–2022", "10 Feld-Jahre", "frei (CC0)"),
    ("Erträge", "One Acre Fund (Afrika)", "14 773 Kleinbauern-Felder mit gemeldeten Schäden – nur als Tabelle",
     "10 204 Felder", "frei (CC BY 4.0)"),
    ("Erträge", "CY-Bench (EU)", "Amtliche Ernte-Statistik je Region, 16 EU-Länder", "8 371 Region-Jahre", "frei (EUPL)"),
    ("Erträge", "YieldSAT (Südamerika), Mead (Nebraska)", "Ertragskarten bzw. lange Reihen – Zugang beantragt", "offen", "auf Anfrage"),
    ("Satellit", "Sentinel-2 (ESA)", "10-m-Bilder alle 2–5 Tage, ab 2017, mit Wolkenfilter (Cloud Score+)", "", "frei"),
    ("Satellit", "HLS = Landsat 8/9 + Sentinel-2 (NASA)", "30-m-Bilder, harmonisiert, ab 2013", "", "frei"),
    ("Wetter", "ERA5-Land (ECMWF)", "Tägliche Temperatur, Regen, Bodenfeuchte, 9-km-Raster, weltweit gleich", "", "frei"),
    ("Boden", "SoilGrids (250 m), SSURGO (USA)", "Bodenart, Wasserspeicher; SSURGO: amtliches Ertragspotenzial je Bodeneinheit", "", "frei"),
    ("Gelände", "Copernicus DEM (30 m)", "Höhe, Neigung, Ausrichtung, Senken/Kuppen", "", "frei"),
    ("Österreich (nur Test)", "INVEKOS-Schläge (AMA)", "Offizielle Feldgrenzen mit Kultur, 2018–2025", "34–39 Tsd. Körnermais-Schläge/Jahr Stmk", "frei (CC BY 4.0)"),
    ("Österreich (nur Test)", "Statistik Austria, Versuchsstation Hatzendorf, LK OÖ", "Regionalerträge; Erträge fester Versuchsstandorte", "150 Standort-Jahre", "öffentlich"),
]


def page() -> None:
    st.title("Vorgehen und Quellen")
    lead("Der Plan steht fest, bevor gerechnet wird. Jede Phase hat ein Ziel und ein vorab festgelegtes "
         "Kriterium, wann sie als erledigt gilt. Was abweicht, wird mit Datum und Grund aufgeschrieben.")

    st.subheader("Die Schritte")
    for phase, title, text, state in STEPS:
        mark = {"done": "✅", "now": "🟡", "off": "⏳"}[state]
        st.markdown(f'<div class="ct-step {state}"><b>{mark} {phase} – {title}</b><br>{text}</div>',
                    unsafe_allow_html=True)
    st.caption("✅ erledigt · 🟡 hier stehen wir (Kriterium nicht bestanden) · ⏳ noch nicht begonnen")

    st.markdown("---")
    st.subheader("Drei Regeln, die alles zusammenhalten")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🇦🇹 Österreich ist der Test, nicht das Training")
        st.markdown("Bis das Modell eingefroren ist, wird **keine einzige österreichische Zahl** angesehen. "
                    "Sonst könnte man das Modell unbemerkt an die Testdaten anpassen.")
    with c2:
        st.markdown("#### 🧊 Einfrieren vor dem Test")
        st.markdown("Modell, Merkmale, Schwellen und Testregeln werden mit **Prüfsummen** festgehalten. "
                    "Danach wird nichts mehr geändert. Wie bei einer Prüfung: Antworten abgeben, dann erst die Lösung sehen.")
    with c3:
        st.markdown("#### 🔍 Jedes Ergebnis wird angezweifelt")
        st.markdown("Nach jedem Schritt eine **Datenkritik**: Sind die Daten repräsentativ? Ist etwas zu gut, um wahr zu sein? "
                    "Lernt das Modell nur „welches Jahr ist das“? Ein überraschend gutes Ergebnis ist zuerst ein Verdachtsfall.")

    st.markdown("---")
    st.subheader("So wird ein Modell geprüft")
    st.markdown(
        "- **Strenge Prüfung (LOFYO):** Das Feld **und** das Jahr, das bewertet wird, hat das Modell nie gesehen. "
        "So merkt man, ob es wirklich etwas gelernt hat oder nur Felder und Jahre auswendig kennt.\n"
        "- **Stichtage:** Am 1. Juni, 15. Juni, 1. Juli, … 1. September. Am 1. Juli darf das Modell nur Daten bis zum 1. Juli nutzen – "
        "das ist im Code erzwungen und getestet.\n"
        "- **Vergleichsmaßstäbe:** Jedes Modell muss besser sein als die Annahme „dieses Jahr ist normal“ (B0) und als eine einzige "
        "Zahl aus dem Satellitenbild (B1). Sonst bringt es nichts.\n"
        "- **Vertrauensbereiche:** Jede Zahl bekommt einen Bereich (95-%-KI). Bei wenigen Jahren ist der Bereich breit – das wird ehrlich gezeigt.\n"
        "- **Label-Shuffle:** Die Erträge werden zufällig vertauscht. Danach muss jedes Modell auf Zufall fallen. Tut es das nicht, ist ein Fehler im Aufbau."
    )

    st.markdown("---")
    st.subheader("Die Datenquellen")
    st.markdown("Was wir nutzen, woher es kommt, und ob es erlaubt ist. Rohdaten liegen nie im Code-Repository; "
                "wie man sie neu herunterlädt, steht in `DATA_SOURCES.md`.")
    rows = [{"Art": a, "Quelle": q, "Was ist drin?": w, "Umfang": u, "Nutzung": n} for a, q, w, u, n in SOURCES]
    st.dataframe(rows, hide_index=True, width="stretch")
    st.caption("Österreichische Quellen wurden bisher nur gesammelt und gezählt, nicht ausgewertet (Österreich-Regel).")

    glossary(["LOFYO", "Stichtag", "B0 / B1", "95-%-KI", "Einfrieren (Freeze)", "Österreich-Regel"])
