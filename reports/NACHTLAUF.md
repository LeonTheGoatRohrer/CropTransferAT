# Nachtlauf 15./16.10.2026 – Bericht für den Projektinhaber

Autonomer Lauf (Claude Code, Opus 5.5; Teilaufgaben durch Claude-Sonnet-Unteragenten) nach `PLAN.md` und `AGENTS.md`.
**Private Fortschrittsseite (nur für dich):** https://claude.ai/artifact/9jHSjkKD4W2iyHgo7hHAG6

## Kurzfassung

- **Phasen 0–3 abgeschlossen** und nach `main` gemergt. **Phase 4: nicht bestanden** → kein Freeze, kein Österreich-Test (wie vereinbart).
- **Phase 5 bis zum EU-Freeze** fertig (Tag `freeze-cybench-1`); der Österreich-Zero-Shot-Test wartet auf deine Freigabe.
- **Phase 9 vorgezogen:** Streamlit-App mit Reiter „US-Ertragsfelder“ und „Fortschritt“ läuft lokal ohne GEE.
- **Was funktioniert:** Innerhalb eines Feldes sieht Sentinel-2 die Ertragszonen gut (ρ = 0,68). Relative Satellitenmerkmale übertragen sich zwischen KBS und BARC (LODO beide Richtungen > 0). Der einfachste Stress-Score (Abstand zur Kurve „gesunder Mais“) erkennt gefährdete Feld-Jahre am 1.9. mit PR-AUC 0,71 (Zufall 0,33).
- **Was nicht reicht:** Die Unterschiede **zwischen Jahren** lassen sich aus nur 8–11 US-Standort-Jahren nicht verlässlich lernen. Bestes vorab gewähltes Modell: ρ = 0,37 [−0,02; 0,68], nicht besser als „normales Jahr“ im RMSE.

## Tags und Branches

| Tag | Inhalt |
|---|---|
| `v0.1.0` | Phase 0 Setup & Datenzugang (+ deine Entscheidungen vom Abend in `DECISIONS.md`) |
| `v0.1.1` | Korrektur aus der Session „Phase 0 starten“ (Notebook ausgeführt, BARC-Zählung, `.claude/worktrees/` ignoriert) |
| `v0.2.0` | Phase 1 Ertragsdaten aufbereiten |
| `v0.3.0` | Phase 2 Basismodelle (F0, F1) |
| `v0.4.0` | Phase 3 Problemfelder (F2) + Phase-4-Urteil „nicht stark genug“ |
| `freeze-cybench-1` | Phase 5: eingefrorene EU-Regionalmodelle (Prüfsummen in `reports/freeze_protocol_cybench.md`) |

Kein `v0.5.0` (Phase 4 nicht bestanden), kein `v0.6.0` (AT-Zero-Shot fehlt). Offener Branch: `phase-9-demo` (App-Fix, noch nicht gemergt).

## Kernergebnisse (alle LOFYO, 95-%-KI per Cluster-Bootstrap über Standort-Jahre)

| Frage | Ergebnis | n |
|---|---|---|
| Daten | 365 Mais-Feld-Jahre (KBS 294, BARC 61, Colorado 10); RY in der HLS-Zeit: 123 Feld-Jahre aus **11 Standort-Jahren** | – |
| Satellit ↔ RY (Phase 1) | EVI-Integral K4 ρ = 0,44 [0,10; 0,75] | 74 / 9 |
| Phase 2, gewähltes Modell (M-S Ridge S2) | ρ(1.9.) = −0,04 [−0,29; 0,37]; mit gesehenem Jahr (LOFO) 0,65 | 89 / 8 |
| Runde 1 (relative Merkmale) | ρ = 0,37 [−0,01; 0,70]; Median-ρ innerhalb Jahr 0,50 | 89 / 8 |
| Runde 2 (einfacher) | ρ = −0,01 [−0,21; 0,59] | 89 / 8 |
| Runde 3 (stärker regularisiert) | ρ = 0,37 [−0,02; 0,68]; RMSE ≈ B0; LODO 0,77 / 0,53 | 89 / 8 |
| Innerhalb der Felder (BARC) | NDVI 16.7.–15.8. vs. Pixel-Ertrag Median-ρ 0,68 [0,54; 0,72]; Problemzonen PR-AUC 0,66 (Prävalenz 0,28); Zonen wiederkehrend (ρ 0,67) | 41 Feld-Jahre |
| Gefährdet (Phase 3) | Stress-Score Referenzkurve ρ = 0,43 [0,24; 0,72], PR-AUC 0,71 (Prävalenz 0,33); Modell-Schwelle PR-AUC 0,40 | 89 / 8 |
| Stressindikator | EVI-K4 gewählt (Median-ρ 0,49 über KBS/BARC) | – |
| CY-Bench EU (Phase 5) | ρ(1.9.) = 0,38 [0,36; 0,40], R² 0,06, Skill vs. YAS = 1 0,07 [0,06; 0,09]; vor 15.7. kein Skill | 8371 Region-Jahre, 16 Länder |

Vollständig: `reports/results.md`, `reports/phase4_stark_genug.md`, `reports/data_review/*.md`.

## Datenkritik-Befunde (Auswahl)

1. **Landsat-Harmonisierung nicht bestanden** (NDVI-RMSD 0,073 > vorab 0,07; Bias nur −0,016). Damit keine KBS-Satellitenjahre vor 2013.
2. **KBS 2014/2017 ohne HLS-Sommertermine**; Datenqualitätsregel verhindert, dass Aprilwerte fortgeschrieben werden.
3. **Jahres-/Standort-Proxy:** KBS und BARC sind in den Merkmalen zu 100 % unterscheidbar (Adversarial AUC 1,0); absolute Merkmale lernen gesehene Jahre (LOFO 0,65 vs. LOFYO ≈ 0).
4. **„Gefährdet“ bei KBS = vor allem Bio-Parzellen (T4)** (13 von 23; T2 Direktsaat 0 %). Viele „Ursache unklar“ sind Bewirtschaftung, nicht Wetter.
5. **Label-Shuffle** fällt in allen Läufen auf Zufallsniveau → keine Leakage-Spur. Nichts war „zu gut“.
6. **Phase 5:** Deutschland 31 % der Region-Jahre; starker Jahres-Proxy (ρ der Jahresmittel 0,86, innerhalb Jahr 0,22); das Hyperparameter-Raster wurde nach einem Pilotlauf erweitert, als äußere EU-Ergebnisse schon sichtbar waren (dokumentiert in DECISIONS) – die EU-Gütezahlen sind dadurch leicht optimistisch; der Österreich-Test ist davon unberührt.
7. **Österreich-Regel eingehalten:** In der Nacht wurde keine österreichische Datei ausgewertet (INVEKOS, Statistik Austria, Versuchsberichte, CY-Bench-AT nicht geöffnet).

## Fragen für morgen

1. **Landsat-Erweiterung.** *Befund:* Grenze knapp verfehlt (RMSD 0,073 statt ≤ 0,07), auch gleiche-Tag-Paare 0,074 → eher Mischpixel kleiner Parzellen als Kalibrierung. *Optionen:* (a) bei der Regel bleiben; (b) neue, **vorher** festgelegte Prüfung (z. B. nur Felder ≥ 3 ha bzw. BARC-Felder, gleiche Grenze); (c) Landsat nur für Normalwerte. *Empfehlung:* (b) ist vertretbar, weil die Prüfung methodisch verbessert wird und die Grenze gleich bleibt – du musst aber ausdrücklich entscheiden, dass das keine Lockerung im Nachhinein ist. Sonst (a).
2. **Wie weiter nach „nicht stark genug“?** *Optionen nach PLAN Phase 4:* mehr Daten (Mead/AmeriFlux-Konto, YieldSAT-Zugang – beides bei dir), engere Frage (z. B. nur „innerhalb des Feldes“ bzw. Stress-Score statt Jahresvorhersage), Phase 5 als Hauptergebnis. *Empfehlung:* Anfragen YieldSAT + Mead jetzt stellen (ANFRAGEN Nr. 1, 3) und als **neue** Frage „Problemzonen im Feld + Stress-Score“ prüfen – das ist das stärkste Ergebnis der Nacht. Jede weitere Modellrunde braucht deine neue Entscheidung (die 3 vorab festgelegten Runden sind aufgebraucht).
3. **Phase 5 freigeben?** Bitte `reports/freeze_protocol_cybench.md` lesen. Offen: AT 2021–2023 aus Statistik Austria ergänzen (ja/nein) – **vor** dem Test entscheiden. Erst danach führe ich den Zero-Shot-Test aus.
4. **CCM (Code 106)** als Körnermais zählen? (vor Phase 6, unverändert offen)
5. **Phase-5-Raster-Erweiterung:** reicht dir die Offenlegung, oder soll die EU-Auswertung mit dem ursprünglichen Raster zusätzlich berichtet werden (ändert das Freeze nicht)?

## Nächste Schritte

- Deine Entscheidungen zu Frage 1–3; dann ggf. Phase-5-Zero-Shot-Test AT.
- ANFRAGEN Nr. 1 (YieldSAT), 3 (Mead), 7 (One Acre Fund Koordinaten) abschicken.
- Doku-Entwürfe unter `reports/doku/` lesen und in eigenen Worten überarbeiten (BWKI: alles erklären können).
- Notebooks 02/03 (Deliverables Phase 2/3) aus den vorhandenen Ergebnisdateien bauen.

## App starten

```
.venv\Scripts\python.exe app\precompute.py
.venv\Scripts\streamlit.exe run app\streamlit_app.py
```
Danach im Browser http://localhost:8501. Läuft aus `data/app/` (lokal, nicht in Git), ohne GEE. Die Karte braucht Internet für Hintergrundkacheln.

## Budget

Wochenkontingent („all models“): Start 28 %, Ende siehe unten. 5-Stunden-Fenster nie über 90 %.
