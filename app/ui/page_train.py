"""Page 'Eigenes Modell': plan a training run (crop, data, features). Preview – runs are not started here yet."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from app.ui.common import APP_DATA, lead

CROPS = {
    "Mais (Körnermais)": {"ready": True, "note": "Vorhanden: KBS, BARC, Colorado (365 Feld-Jahre). Pipeline fertig."},
    "Soja": {"ready": False, "note": "KBS und BARC bauen Soja in der Fruchtfolge an – dieselben Felder, andere Jahre. Pipeline: Saisonkurve und Stichtage anpassen."},
    "Winterweizen": {"ready": False, "note": "KBS/BARC-Weizenjahre; Dauerversuche (Rothamsted, BonaRes) als Kandidaten. Saison Mai–Juli."},
    "Gerste / Roggen / Triticale": {"ready": False, "note": "Noch keine Ertragsquelle aufbereitet."},
}
DATASETS = [
    ("KBS LTER (Michigan)", True), ("USDA BARC (Maryland)", True), ("Colorado Trockenfarm", True),
    ("One Acre Fund (Afrika, nur Tabelle)", True), ("YieldSAT (Südamerika) – Zugang beantragt", False),
    ("Mead (Nebraska) – Konto nötig", False), ("Hagelversicherung Österreich – nur nach Freeze, Phase 8", False),
]
FEATURES = ["Satellit (S)", "Satellit relativ zum eigenen Feld (S-rel)", "Wetter (W)", "Boden / Gelände (B)",
            "US-Bodenpotenzial SSURGO (B+, nur Analyse)"]


def page() -> None:
    st.title("Eigenes Modell trainieren")
    lead("Hier planst du einen neuen Trainingslauf: Kultur, Datensätze, Merkmale. "
         "Der Auftrag wird gespeichert und in der nächsten Arbeitssitzung umgesetzt – "
         "<b>das Training selbst läuft noch nicht aus der Website.</b>")
    st.info("Warum nicht sofort? Ein Lauf dauert Stunden (Satelliten-Export, verschachtelte Prüfung mit "
            "Vertrauensbereichen) und jede Änderung an Kultur oder Daten ist laut Plan eine Entscheidung, die "
            "in `DECISIONS.md` begründet wird. Der Auftrag hier ist genau diese Entscheidung – sauber dokumentiert.")

    with st.form("train"):
        crop = st.radio("Kultur", list(CROPS), horizontal=True)
        st.caption(CROPS[crop]["note"])
        st.markdown("**Datensätze**")
        ds = [name for name, avail in DATASETS
              if st.checkbox(name + ("" if avail else " (nicht verfügbar)"), value=avail, disabled=not avail)]
        feats = st.multiselect("Merkmalsgruppen", FEATURES, default=FEATURES[:4])
        basis = st.radio("Satellit", ["S2 (10 m, ab 2017)", "HLS (30 m, ab 2013)", "beide"], horizontal=True, index=2)
        target = st.radio("Zielgröße", ["relativer Ertrag RY (Hauptziel)", "absoluter Ertrag t/ha"], horizontal=True)
        kinds = st.multiselect("Verfahren", ["Ridge (linear)", "LightGBM (flache Bäume)"], default=["Ridge (linear)", "LightGBM (flache Bäume)"])
        note = st.text_area("Begründung / Erwartung (kommt so in DECISIONS.md)", placeholder="Warum dieser Lauf? Was erwarte ich?")
        submitted = st.form_submit_button("Auftrag speichern")

    st.markdown("**Immer gleich, nicht wählbar:** Prüfung LOFYO (Feld und Jahr ungesehen), Stichtage 1.6.–1.9., "
                "Vertrauensbereiche per Cluster-Bootstrap, Label-Shuffle-Kontrolle, keine österreichischen Daten vor dem Freeze.")

    if submitted:
        req = {"created": datetime.now().isoformat(timespec="seconds"), "crop": crop, "datasets": ds,
               "features": feats, "basis": basis, "target": target, "kinds": kinds, "note": note,
               "fixed": "LOFYO, Stichtage 06-01..09-01, Cluster-Bootstrap, Label-Shuffle, Österreich-Regel"}
        out = Path(APP_DATA) / "train_requests"
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{crop.split(' ')[0].lower()}.json"
        path.write_text(json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
        st.success(f"Gespeichert unter `{path.relative_to(APP_DATA.parent.parent)}`. "
                   "Sag Claude in der nächsten Sitzung: „Setze den Trainingsauftrag um.“")
        st.json(req)

    st.markdown("---")
    st.subheader("Was ein neuer Lauf braucht (Checkliste)")
    st.markdown(
        "1. **Ertragsdaten** mit Feldumriss (oder Koordinaten) und mindestens einem Jahr ab 2013.\n"
        "2. **Saisonkurve der Kultur** festlegen: Wann Aufgang, Maximum, Ernte? (Mais: Mai / Juli–Aug / Sept–Okt.)\n"
        "3. **Stichtage** passend zur Kultur (Winterweizen endet schon im Juli).\n"
        "4. **Eintrag in `DECISIONS.md`** (Kultur, Daten, Grund) – vor dem ersten Ergebnis.\n"
        "5. Lauf starten: `python -m croptransfer.run_phase2` (Mais) – für andere Kulturen folgt ein Parameter `--crop`."
    )
    existing = sorted((Path(APP_DATA) / "train_requests").glob("*.json")) if (Path(APP_DATA) / "train_requests").exists() else []
    if existing:
        st.subheader("Gespeicherte Aufträge")
        for p in existing[::-1]:
            r = json.loads(p.read_text(encoding="utf-8"))
            st.markdown(f"- `{p.name}` – {r['crop']}, {len(r['datasets'])} Datensätze, Ziel: {r['target']}")
