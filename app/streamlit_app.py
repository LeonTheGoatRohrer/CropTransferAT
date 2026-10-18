"""Delta Green – Website (Streamlit, lokal und privat).

Run from the repository root:  streamlit run app/streamlit_app.py
Reads ONLY data/app/ (made by app/precompute.py), app/versions.yaml, reports/ and a few
Markdown files. No GEE, no raw data, no Austrian data.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # `streamlit run` puts app/ on sys.path, not the repo root
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from app.ui import page_approach, page_benchmarks, page_fields, page_home, page_log, page_train, page_versions  # noqa: E402
from app.ui.common import (  # noqa: E402,F401  (re-exported for tests)
    APP_DATA, ampel, cutoff_date, data_problem, dekad_date, fmt, inject_css, load_app_data,
)

PAGE_TITLES = ["Ziel", "Vorgehen & Quellen", "Ergebnisse", "Vergleich", "Felder ansehen", "Eigenes Modell", "Projektlog"]


def main() -> None:
    st.set_page_config(page_title="Delta Green", page_icon="🌽", layout="wide")
    inject_css()
    data = load_app_data(str(APP_DATA))

    pages = [
        st.Page(page_home.page, title=PAGE_TITLES[0], icon="🎯", default=True),  # default page = "/"
        st.Page(page_approach.page, title=PAGE_TITLES[1], icon="🧭", url_path="vorgehen"),
        st.Page(page_versions.page, title=PAGE_TITLES[2], icon="📊", url_path="ergebnisse"),
        st.Page(lambda: page_benchmarks.page(data), title=PAGE_TITLES[3], icon="⚖️", url_path="vergleich"),
        st.Page(lambda: page_fields.page(data), title=PAGE_TITLES[4], icon="🗺️", url_path="felder"),
        st.Page(page_train.page, title=PAGE_TITLES[5], icon="🧪", url_path="modell"),
        st.Page(lambda: page_log.page(data), title=PAGE_TITLES[6], icon="📒", url_path="log"),
    ]
    with st.sidebar:
        st.markdown("## 🌽 Delta Green")
        st.caption("Früherkennung von Stress auf Maisfeldern – gelernt in den USA, geprüft in Österreich.")
        problem = data_problem(data)
        if problem:
            st.error(problem)
        else:
            st.caption("Lokal und privat. Keine österreichischen Ergebnisse vor dem Freeze.")
    nav = st.navigation(pages, position="sidebar")
    nav.run()


if __name__ == "__main__":
    main()
else:  # `streamlit run` executes the file as __main__; AppTest also runs it as a script
    pass
