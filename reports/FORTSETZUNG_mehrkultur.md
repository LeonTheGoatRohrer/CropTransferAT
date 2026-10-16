# Fortsetzung Mehr-Kulturen-Plan (Übergabe bei Kontingentende)

Branch: `phase-mk-mehrkultur`. Plan: `reports/plan_mehrkultur.md`. Start 2026-10-16, Weiterarbeit ab 17:00.
Auftrag des Projektinhabers: Plan umsetzen, soweit das Kontingent reicht. D1–D12 gelten **vorläufig** (W0.1 steht aus; in DECISIONS.md vermerkt).
Python: `.venv/Scripts/python` (Modul per `-m croptransfer.<name>`; `pytest` mit derselben venv).

## Erledigt
- [x] W1.1 `fetch_open_sets.py` + Test; Pakete invite, briwecs, peas_fr, nordic_barley in `data/raw/` (mit MANIFEST.json)
- [x] W1.2 DATA_SOURCES.md §16
- [x] W1.3 Datenkritik `reports/data_review/phase1b_mehrkultur.md` (⚠️ weiter mit Einschränkung)
- [x] W2.1/W2.2/W2.3 `groundtruth_multi.py` (+ `review_multi.py`), Test; `data/processed/gt_site_years.parquet`; Zählung: WW S2 202, Erbse S2 257, Gerste S4 711, Mais 0 Zellen-Jahre
- [x] Doku: CHANGELOG, SUPPORT, DECISIONS, `app/versions.yaml` (Eintrag `mehrkultur-etappe1`), alle Tests grün

## Offen, als Nächstes (in dieser Reihenfolge)
1. Offene Prüfpunkte aus der Datenkritik: Nordic-Einheit gegen README (DataverseNO IZ3EFE) prüfen; Bedeutung `Y0/Y2` (INVITE Frankreich) klären; Querduplikate suchen; 0,5°-Sensitivität in `count_cells`.
2. A4 Bernburg (BonaRes API, Mais/WW/WG/Raps), A7 Grignon (10.57745/5TJJZA, Mais 6 Standort-Jahre), A6 Iowa/UGA — Loader in `groundtruth_multi.py` ergänzen (Mais ist die Zielkultur!).
3. W3.1 `config.yaml` Block `crops:` (D6) + Regressionstest Mais — **erst nach W0.1**.
4. Etappe 3/4 erst nach Bestätigung durch den Projektinhaber und nach Mais-Daten (G2F).

## Nicht ohne Projektinhaber
W0.1 (Entscheidungen D1–D12), W0.2 (Anfragen), W0.3 (G2F/CyVerse-CAPTCHA), Rothamsted-Formular. Österreich-Daten nie ansehen.
