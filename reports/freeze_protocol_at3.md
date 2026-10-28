# Freeze- und Testprotokoll Österreich III: Steiermark mit den Hatzendorf-Excel-Reihen (explorativ)

**Stand:** 2026-10-28, festgeschrieben **bevor** die Scores für 2026 berechnet werden. Tag: `freeze-at-3`. Danach wird an Auswahl, Definitionen, Metriken und Kriterien nichts mehr geändert;
jede Änderung wäre ein neuer Test (`freeze-at-4`), alle Ergebnisse würden berichtet. Entscheidung des Projektinhabers (Chat 2026-10-28): „Mit 2026“.

## 0. Einordnung
- **Dritter Test, ersetzt nichts.** `at-test-1` (Oberösterreich) und `at-test-2` (Steiermark, n = 12, nicht auswertbar) bleiben unverändert stehen.
- **Neu ist nur die Ertragsseite:** Die Versuchsstation Hatzendorf (Christoph Hödl) hat am 2026-10-28 die langen Reihen der Körnermais-Stickstoffversuche **Wagna (2007–2026)** und **Kalsdorf/Ilz (2009–2026)** als Excel geschickt.
  Damit kommen Wagna 2025, Kalsdorf 2020 und **2026** für beide Standorte dazu, und alle Jahre haben eine einheitliche Quelle (statt aus Berichten abgeschrieben).
- **Modelle unverändert** (Stress-Score A aus `freeze-at-1`, Referenzkurve `reports/freeze_at/stress_reference_hls_ndvi.csv`). Scores 2018–2025 werden **nicht neu berechnet**, sondern aus
  `results/2026-10-17_at_test/site_year.csv` übernommen (SHA-256 unten). Das Regionalmodell (Weg B) wird nicht geprüft: Wetter-Eingaben enden 2023, und auf Standortebene zeigte es in beiden Tests nichts.
- **Explorativ**, kein Sieger, keine Modell- oder Stichtagswahl.

## 1. Was vor dem Freeze schon gesehen wurde (ehrlich offengelegt)
- **Fast alles außer 2026 ist nicht blind.** Die Scores 2018–2025 und die alten Erträge wurden in `at-test-2` ausgewertet. Beim Vorbereiten dieses Tests hat der KI-Assistent zusätzlich
  `results/2026-10-17_at_test_stmk/site_year.csv` (Scores aller steirischen Standort-Jahre) **und** die neuen Excel-Erträge gesehen, auch die beiden neuen Punkte **Wagna 2025**
  (niedrigster Score aller steirischen Standort-Jahre, Ertrag eingebrochen) und **Kalsdorf 2020**. Sie stehen als `seen_new_points` in der Konfiguration.
- Ebenfalls gesehen: die Excel-Erträge und `YAS_site` für **2026** (Wagna 0,48, Kalsdorf 0,62). **Nicht gesehen und nicht berechnet: die Scores 2026.** Nur diese zwei Standort-Jahre sind blind.
- Folge: Das Ergebnis ist eine **Neubewertung mit besserer Ertragsquelle plus zwei blinden Punkten**, kein unabhängiger Beweis. So steht es auch im Ergebnisbericht.

## 2. Daten (vorab festgelegt)
- **Standorte:** `wagna`, `kalsdorf` (Cluster und Gemeindeschwerpunkte wie in `freeze-at-1`). Hatzendorf: keine neuen Daten.
- **Jahre:** 2018–2026.
- **Erträge:** Excel-Blätter `Daten Ertrag RP N 2007-2022` (Wagna) und `Daten Ertrag RP N` (Kalsdorf), Kopfzeile 5, Spalten „Ertrag JJJJ“ (dt/ha, 14 % Feuchte; Spalten „t/ha“ werden nicht gelesen),
  Variantenkürzel aus Spalte 59 bzw. 63. Bei wiederholtem Kürzel zählt nur die erste Zeile (weiter unten im Blatt stehen Hilfstabellen). Tabelle: `data/raw/at_trials_hatzendorf_excel.csv`, erzeugt mit
  `python -m croptransfer.at_test3 --yields-only`.
- **Ausschlüsse:** Kalsdorf 2023 (RWA-Feldtag, „nicht mitgewertet“) und 2025 („Problem Sämaschine“); Kalsdorf 2017 und 2019 waren Körnersorghum (keine Spalte). Wagna: kein Ausschluss.
- **Standortertrag `Y(c,y)`:** Mittel über die **Kernvarianten** = Varianten mit Ertrag in **jedem** gezählten Jahr ab 2013 (Kalsdorf 17: 0, A, B, D, E, F, G, H, K, L, M, N, R, T, U, W, X;
  Wagna alle 12). Damit ändert sich die Zusammensetzung des Mittels über die Jahre nicht. Erträge vor 2013 werden nicht verwendet.
- **`YAS_site`:** Regel aus `freeze-at-1` unverändert (`at_test.yas_site`: 5 vollständige Vorjahre, olympischer Durchschnitt; sonst Mittel von ≥ 3 anderen Jahren, gekennzeichnet `baseline_short`).
  Kalsdorf hat wegen der Lücken 2017/2019/2023/2025 überall `baseline_short` (das Mittel enthält auch spätere Jahre).
- **Scores 2026** – exakt nach den Regeln von `freeze-at-1`, nichts neu gewählt:
  INVEKOS-Schläge **2026, Fassung 1** (`inspire_schlaege_2026-1_polygon`, die einzige am 2026-10-28 veröffentlichte Fassung), Code 105, ≥ 1 ha, gültige Geometrie, Schwerpunkt ≤ 5 km um den
  Standortschwerpunkt, höchstens 100 Felder je Standort-Jahr mit dem Zufallsstartwert `42 + Jahr·1000 + k` (k = Position des Standorts in der sortierten Liste **aller** Standorte von `at_test.sites`,
  wie in `at_fields.select_year`), Innenpuffer −10 m; HLS 1. April–1. November über `at_extract`; Score, Mindestfelder (10) und Mindestdekaden (4) wie in `at_test`. Ergebnis:
  `results/2026-10-28_at_test3/site_year_scores_2026.csv`.
  - Gegenprobe vor der Auswertung: Dieselbe Rechnung für ein Jahr aus 2018–2025 muss die Scores aus `at-test-1` exakt wiederholen; sonst Stopp.
  - Ist 2026 nicht berechenbar (z. B. < 10 gültige Felder), zählt das Standort-Jahr als fehlend. Es wird **nicht** durch eine andere Fassung oder ein anderes Jahr ersetzt.

## 3. Tests und Metriken (Stichtage 07-15, 08-01, 08-15, 09-01; Hauptstichtag 09-01)
Dieselbe Auswertungsfunktion wie `freeze-at-2` (`at_test_stmk.evaluate`), damit die Zahlen vergleichbar sind:

| Auswertung | Inhalt | Rolle |
|---|---|---|
| **S-A (Haupt)** | Stress-Score → `YAS_site`, Kernvarianten, 2018–2026 | Kriterium unten |
| Vergleich | mittleres NDVI Dekaden 9–14 (ohne Lernen) | beschreibend |
| Sensitivität 1 | alle Varianten des Jahres statt Kernvarianten | beschreibend |
| Sensitivität 2 | ohne die gesehenen neuen Punkte (Wagna 2025, Kalsdorf 2020) | beschreibend |
| Blinde Punkte | Wagna 2026, Kalsdorf 2026 einzeln aufgelistet (Score, `YAS_site`) | beschreibend |
| Verbund mit Oberösterreich | wie in `freeze-at-2`, nicht unabhängig | beschreibend |

Spearman ρ mit 95-%-Cluster-Bootstrap über Jahre (1000, Seed 42), n und Anzahl Jahre immer angeben; innerhalb der Standorte (≥ 5 Jahre), innerhalb der Jahre (≥ 3 Standorte – hier nie erfüllt),
Leave-one-year-out. Die Regionalmodell-Spalten, die `evaluate` mitrechnet, werden im Bericht nicht gewertet.

## 4. Kriterium (vorab)
- **S-A bestanden:** ρ > 0 mit KI ohne 0 am 09-01, nur auswertbar bei **≥ 15 Standort-Jahren** (Schwelle aus `freeze-at-2`); sonst „nicht auswertbar“.
  Erwartet: Wagna 9 + Kalsdorf 6 = **15**, wenn beide 2026-Scores gültig sind; fehlt einer, ist der Test nicht auswertbar.
- Auch bei „bestanden“ wird im Bericht ausdrücklich gesagt, dass 13 der 15 Punkte vorher bekannt waren (§1). Sensitivität 2 wird daneben gestellt.
- Kein Sieger, keine Stichtagswahl, keine Änderung der Kernvarianten oder Ausschlüsse nach dem Ergebnis.

## 5. Grenzen (vorab)
- **Standort ≠ Parzelle:** Der Score ist das Mittel von bis zu 100 Körnermais-Schlägen im Umkreis von 5 km um die Gemeinde, nicht die Versuchsfläche (Parzellen 12,6 m², ganze Anlage ≈ 0,2 ha).
  Gemessen wird also, ob gute und schlechte Versuchsjahre mit dem Zustand der Maisfelder der Umgebung zusammenfallen.
- Stickstoffversuche messen nicht nur Wetter; das Kernvarianten-Mittel enthält die 0-N-Kontrolle.
- **Wagna-Strukturbruch:** Ab 2021 liegt Wagna deutlich tiefer, auch in der 0-N-Kontrolle. Die Ursache (Fläche, Sorte, Bewirtschaftung, Wetter) ist offen und bei Hödl angefragt.
- Wagna 2025 (Ertrag 2,4 t/ha) ist ein Extremwert; Ursache (Trockenheit oder anderes) offen.
- Zwei Standorte, 9 Jahre als Cluster, je Jahr höchstens 2 Standort-Jahre; „innerhalb eines Jahres“ ist nicht prüfbar.
- INVEKOS 2026 ist die erste Fassung (frühere Jahre teils zweite Fassung); kleine Unterschiede bei den Schlägen sind möglich.

## 6. Prüfsummen
| Datei | SHA-256 |
|---|---|
| `reports/freeze_at/at_test3_config.json` | `247834325755fdcf656251fc63e6b9e4dc6aae314f7ff0f57b6f699619b19aeb` |
| `results/2026-10-17_at_test/site_year.csv` | `1bd7852706a1551e31316b328504daf9dc422aa547e95845fd6477f93ddf8e73` |

Nicht im Repository (Rohdaten, `DATA_SOURCES.md` §12c), Prüfsummen zur Nachverfolgung:

| Datei | SHA-256 |
|---|---|
| `data/raw/at_trials/hatzendorf_excel/KM-Wagna-2008-2026.xlsx` | `62e561d9ab6e6b519b8af1e1af81f7b06736f18f0804181455d1c41a367f89f8` |
| `data/raw/at_trials/hatzendorf_excel/KM-Kalsdorf-Kornertrag-(alle-Varianten)-2009-2026 vers.xlsx` | `3ac61886937232c897f782befa0dde18c5454806902a3061c9100c00e17aef88` |
| `data/raw/at_trials_hatzendorf_excel.csv` | `13f56d060bc8146511d4be28b3ea86fa04a82ee933bd4589c8d5d5c6a4c0e9a5` |
