"""Page 'Projektlog': changelog, data reviews, open questions, support (BWKI)."""
from __future__ import annotations

import re

import streamlit as st

from app.ui.common import ROOT, lead, read_markdown

OPEN_QUESTIONS = [
    ("Landsat-Erweiterung", "Die Prüfung alter Satellitenbilder ist knapp gescheitert (0,073 statt ≤ 0,07). "
     "Regel beibehalten, oder eine neue, vorher festgelegte Prüfung nur mit großen Feldern?"),
    ("Wie weiter nach „nicht stark genug“?", "Mehr Daten (YieldSAT, Mead, Hagelversicherung), engere Frage "
     "(Stress-Score und Zonen im Feld als eigener Freeze), oder das EU-Regionalmodell als Hauptergebnis?"),
    ("EU-Regionaltest freigeben?", "Das Freeze-Protokoll ist fertig. Vorher entscheiden: Statistik Austria "
     "2021–2023 ergänzen (getrennt berichtet) oder nur CY-Bench 2006–2020?"),
    ("CCM als Körnermais?", "Corn-Cob-Mix (INVEKOS-Code 106) zählt die Statistik Austria zum Körnermais. Mitnehmen?"),
]


def _section(md: str, heading_prefix: str = "## ") -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    title, buf = None, []
    for line in md.splitlines():
        if line.startswith(heading_prefix) and not line.startswith(heading_prefix + "#"):
            if title is not None:
                parts.append((title, "\n".join(buf)))
            title, buf = line[len(heading_prefix):].strip(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        parts.append((title, "\n".join(buf)))
    return parts


def page(data: dict | None) -> None:
    st.title("Projektlog")
    lead("Alles, was für den Wettbewerb nachvollziehbar sein muss: Versionen, Datenkritik, offene Entscheidungen "
         "und wer bzw. was geholfen hat.")

    tabs = st.tabs(["Offene Entscheidungen", "Änderungsprotokoll", "Datenkritik", "Unterstützung (BWKI)", "Anfragen"])

    with tabs[0]:
        st.markdown("Diese Fragen muss der Projektinhaber entscheiden, bevor es weitergeht:")
        for t, q in OPEN_QUESTIONS:
            st.markdown(f'<div class="ct-card"><b>{t}</b><br>{q}</div>', unsafe_allow_html=True)
        st.caption("Quelle: `reports/NACHTLAUF.md`, Abschnitt „Fragen für morgen“.")

    with tabs[1]:
        md = read_markdown("CHANGELOG.md")
        if md:
            for title, body in _section(md):
                m = re.match(r"\[([^\]]+)\](?:\s+[–-]\s+(\S+))?(?:\s+[–-]\s+(.*))?", title)
                label = f"{m.group(1)} · {m.group(2) or ''} · {m.group(3) or ''}".strip(" ·") if m else title
                with st.expander(label, expanded=False):
                    st.markdown(body)
        else:
            st.info("CHANGELOG.md nicht gefunden.")

    with tabs[2]:
        st.markdown("Nach jedem großen Schritt wird eine feste Prüfliste abgearbeitet: Sind die Daten repräsentativ? "
                    "Korrekt? Gibt es Scheinzusammenhänge? Leakage? Ist das Ergebnis plausibel? "
                    "Am Ende steht ✅ weiter, ⚠️ weiter mit Einschränkung oder ⛔ Stopp.")
        reviews = sorted((ROOT / "reports" / "data_review").glob("*.md"))
        for p in reviews:
            text = p.read_text(encoding="utf-8")
            first = next((ln for ln in text.splitlines() if ln.startswith("# ")), p.stem).lstrip("# ")
            verdict = "⛔" if "⛔ **Stopp" in text else "⚠️" if "⚠️ **Weiter" in text else "✅" if "✅ **Weiter" in text else "·"
            with st.expander(f"{verdict} {first}"):
                st.markdown(text)

    with tabs[3]:
        md = read_markdown("SUPPORT.md")
        st.markdown(md or "SUPPORT.md nicht gefunden.")

    with tabs[4]:
        md = read_markdown("ANFRAGEN.md")
        if md:
            head = md.split("\n## ", 1)[0]
            st.markdown(head)
            with st.expander("Alle Anfragetexte"):
                st.markdown(md)
        else:
            st.info("ANFRAGEN.md nicht gefunden.")
