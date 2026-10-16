"""Page 'Ziel': what the project wants, in plain language."""
from __future__ import annotations

import streamlit as st

from app.ui.common import big, figure, glossary, lead, load_versions, status_badge


def page() -> None:
    st.title("🌽 CropTransfer AT")
    big("Kann ein Computer vom Satelliten aus erkennen, welchem Maisfeld es schlecht geht – "
        "und zwar schon im Sommer, nicht erst bei der Ernte?")
    lead("Das ist die Frage dieses Projekts. Diese Website zeigt, wie wir vorgehen, welche Daten wir nutzen "
         "und was bisher herausgekommen ist – ehrlich, auch wenn ein Ergebnis schwach ist.")

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 1 · Der Satellit schaut zu")
        st.markdown("Alle paar Tage fotografiert ein Satellit jedes Feld. Aus dem Grün der Pflanzen entsteht "
                    "eine **Kurve über die Saison**: Im Mai geht der Mais auf, im Juli/August ist er am dichtesten, "
                    "im September reift er ab.")
    with c2:
        st.markdown("### 2 · Gesund oder gestresst?")
        st.markdown("Ein gesundes Feld hat eine hohe, breite Kurve. Bei **Trockenheit, Hitze, Nässe oder Hagel** "
                    "bleibt die Kurve flach oder bricht ein. Der Computer lernt diesen Zusammenhang an Feldern, "
                    "deren Ernte wirklich gewogen wurde.")
    with c3:
        st.markdown("### 3 · Der Beweis in Österreich")
        st.markdown("Gelernt wird **nur an Feldern in den USA**. Dann wird das Modell „eingefroren“ und ohne "
                    "jede Anpassung in der **Steiermark** geprüft. Erst wenn es dort funktioniert, ist es ein Ergebnis.")

    st.markdown("---")
    st.subheader("So sehen die Daten aus")
    figure("overview_s2_gallery_barc.png",
           "Dasselbe Feld in Maryland (USA) in einem schlechten (oben, 2018) und einem guten Jahr (unten, 2021). "
           "Links: Satellitenfotos Juni bis September. Mitte: Grünindex NDVI (rot = wenig, grün = viel). "
           "Rechts: der gemessene Ertrag des Mähdreschers. Im schlechten Jahr blieb das Feld blass – und die Ernte war halb so groß.")

    st.markdown("---")
    st.subheader("Wo stehen wir?")
    versions = load_versions()["versions"]
    main = [v for v in versions if v["id"] in ("v0.4.0", "freeze-cybench-1", "v0.3.0", "v0.2.0")]
    for v in main:
        st.markdown(f"{status_badge(v['status'])} **{v['phase']} – {v['title']}**  \n{v['changed']}",
                    unsafe_allow_html=True)
    st.markdown("")
    st.info(
        "**Stand in einem Satz:** Innerhalb eines Feldes sieht der Satellit sehr gut, wo Ertrag fehlt. "
        "Ob ein ganzes Jahr gut oder schlecht wird, kann das Modell aus den bisherigen Daten noch nicht "
        "verlässlich sagen – dafür fehlen unabhängige Standort-Jahre. Deshalb wurde das Modell **nicht** eingefroren "
        "und Österreich **noch nicht** getestet."
    )

    st.markdown("---")
    st.subheader("Wem das nützen könnte")
    st.markdown(
        "- **Landwirt:innen:** Welche meiner Felder sind in diesem Jahr gefährdet – und seit wann?\n"
        "- **Hagelversicherung:** Welche Felder sind betroffen, wie groß ist der Schaden?\n"
        "- **Landwirtschaftskammer:** Wo sollte Beratung ansetzen?\n"
        "- **Behörden:** Eine frühe Einschätzung der Ernte, nicht erst im Herbst.\n\n"
        "Das Projekt zeigt eine Methode und prüft ehrlich, wie weit sie trägt. Es ist noch **kein fertiges Frühwarnsystem**."
    )
    glossary(["RY (relativer Ertrag)", "gefährdet", "Standort-Jahr", "Einfrieren (Freeze)", "Österreich-Regel"])
