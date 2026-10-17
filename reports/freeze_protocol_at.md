# Freeze- und Testprotokoll Österreich (erster Test, explorativ)

**Stand:** 2026-10-17, geschrieben und festgeschrieben **vor** jeder Auswertung österreichischer Satelliten- oder Ertragswerte.
Tag: `freeze-at-1`. Nach dem Tag wird an Modellen, Auswahl, Metriken und Kriterien nichts mehr geändert; ein dokumentierter Fehler
führt zu einem neuen Freeze, beide Ergebnisse werden berichtet (AGENTS §8).

## 0. Einordnung (bitte ehrlich lesen)

- Das ist ein **erster, explorativer Test**, kein „Beweis“. Das vorab festgelegte Phase-4-Kriterium „stark genug“ wurde von **keinem** Feldmodell
  erfüllt (`reports/phase4_stark_genug.md`, `reports/phase4_mehrkultur.md`, `reports/feinjustierung_ergebnis.md`). PLAN Phase 4 sagt in diesem
  Fall „nicht nach Österreich gehen“. Der Projektinhaber hat am 2026-10-17 im Chat ausdrücklich entschieden, trotzdem einen Test mit
  den vorhandenen eingefrorenen Modellen durchzuführen („Schauen wir einfach“; „Nummer eins passt für mich“ = beide Modelle einfrieren, **keinen Sieger**
  auf österreichischen Daten wählen). Diese Abweichung steht in `DECISIONS.md`.
- **Es wird kein Sieger gewählt.** Beide Modelle (A und B) werden nebeneinander berichtet. Ein Modellwechsel auf Grund dieses Tests ist ein neuer
  Freeze mit eigenem Ergebnis; beide Ergebnisse stehen in der Doku.
- Aussage, die der Test höchstens stützen kann: *Erkennt das eingefrorene Modell in Österreich gute und schlechte Jahre bzw. Standorte
  (Rangfolge)?* Er sagt nichts über t/ha-Genauigkeit und nichts über einzelne Praxisfelder.

## 1. Eingefrorene Modelle und Vergleichswerte

**A – Stress-Score (Feldebene).** Pro Feld-Jahr und Stichtag *t*: Median-NDVI der HLS-Beobachtungen je Dekade (Dekade 0 = 1.–10. April, nur gültige
Szenen mit `clear_frac ≥ 0,7`, nur beobachtete Dekaden, keine Interpolation); `score = mean(min(NDVI_d − Ref_d, 0))` über die beobachteten Dekaden
`6 … k` (k = letzte Dekade, die vor *t* endet). Referenz `Ref` = Median-NDVI je Dekade über alle gesunden US-Feld-Jahre
(`RY_descr ≥ 0,95`, HLS-Ära, 77 Feld-Jahre; KBS, BARC, Colorado) → `reports/freeze_at/stress_reference_hls_ndvi.csv`. Code: `croptransfer.stress`.
Je größer (weniger negativ) der Score, desto weniger Stress; erwartetes Vorzeichen der Korrelation mit Ertrag: **positiv**. Es gibt keine weitere Anpassung,
keine Schwelle (Rangvergleich).

**B – Regionales Ertragsmodell (CY-Bench EU).** Unverändert `freeze-cybench-1`: LightGBM je Stichtag, sagt `YAS` (Ertrag / olympischer Durchschnitt der
5 Vorjahre derselben Region) aus Wetter, Bodenfeuchte, fPAR, NDVI (Regionsebene) voraus. Österreich war nie im Training. Prüfsummen:
`reports/freeze_protocol_cybench.md` (14 Dateien, vor dem Test per `verify_freeze` erneut geprüft). Eingabe für Österreich: CY-Bench-Prädiktoren AT
(NUTS-2 = Bundesland), Jahre 2018–2023 (die Prädiktoren enden 2023).

**Vergleichswerte (keine Modelle):** `YAS = 1` („normales Jahr“); **B-NDVI**: mittleres beobachtetes HLS-NDVI der Dekaden 9–14 (Juni/Juli–Aug.), ohne jedes Lernen
(zeigt, ob der Stress-Score mehr leistet als „grün ist gut“).

**Nicht eingefroren, nicht Teil des Tests:** das Feld-Ertragsmodell (Ridge, Phase 2/Runde 3) – es hat Phase 4 in allen Runden verfehlt und bräuchte
Boden-/Wettermerkmale, die für österreichische Felder erst gebaut werden müssten. Das wird als Grenze ausgewiesen, nicht verschwiegen.

## 2. Österreichische Daten und Auswahl

- **Standorte (Versuchsstellen):** 13 Standort-Cluster laut `config.yaml: at_test.sites` (Namensvarianten aus den Berichten zusammengefasst). Standortposition =
  Schwerpunkt der Gemeinde(n); in den Berichten stehen keine genaueren Koordinaten (`loc_precision = municipality`). Hatzendorf → Gemeinde Fehring,
  Kalsdorf bei Ilz → Gemeinde Ilz, Katzenberg → Kirchdorf am Inn + Geinberg (Zuordnung aus dem Namen, nicht verifiziert), Linden → Steinerkirchen an der Traun.
  Positionen: `reports/freeze_at/site_centroids.json`.
- **Jahre:** 2018–2025 (HLS + INVEKOS verfügbar). Versuchsjahre vor 2018 und 2026 (kein INVEKOS 2026) bleiben außen vor.
- **Felder:** INVEKOS-Schläge der Nutzungsart `SNAR_CODE = 105` (Körnermais), Fläche ≥ 1,0 ha, gültige Geometrie, Schwerpunkt im Umkreis
  **5 km** um die Standortposition. Pro Standort-Jahr höchstens **100** Felder (zufällig, Seed 42, Kandidaten nach Koordinaten sortiert).
  Innenpuffer −10 m. Feld-Jahr gültig, wenn ≥ 4 beobachtete HLS-Dekaden in `6 … k`. Standort-Jahr gültig mit ≥ 10 gültigen Feld-Jahren, sonst ausgeschlossen
  und aufgelistet. Keine weitere Filterung (auch keine Frühernte-/Silomais-Bereinigung, sie wird nur beschreibend ausgewertet).
- **Standort-Ertrag `Y(c,y)`** (nur für Test, erst nach diesem Freeze geöffnet): Versuchsarten `sorten` und `praxisversuch_sorten`; je Versuchsart die Zeile
  `Standortmittel`/`Versuchsmittel`, sonst das Mittel der Varianten; dann Mittel der Versuchsarten; dann Mittel der Namensvarianten desselben Cluster-Jahres.
  Ertrag in t/ha, 14 % Feuchte (Quotient daher unabhängig von der Feuchtebasis).
- **`YAS_site(c,y)`:** `Y(c,y)` / olympischer Durchschnitt von `Y(c,y−5 … y−1)`, wenn alle 5 Vorjahre vorliegen; sonst `Y(c,y)` / Mittel **aller anderen** Jahre des
  Clusters (mind. 3 andere Jahre; als `baseline_short` gekennzeichnet; sonst kein Wert). Alle Jahre des Clusters (auch vor 2018) dürfen als Basis dienen.
- **Regionalertrag:** Statistik Austria, Körnermais, Bundesland, 2013–2023; `YAS` wie in B. Regionen (nur Maisländer): AT11 Burgenland, AT12 Niederösterreich,
  AT21 Kärnten, AT22 Steiermark, AT31 Oberösterreich.

## 3. Testwege und Metriken (alle Stichtage 07-15, 08-01, 08-15, 09-01 werden berichtet; Hauptstichtag **09-01**)

| Weg | Vorhersage | Ziel | Einheit der Zählung |
|---|---|---|---|
| **V2-A (lokal)** | Mittel des Scores A über die Felder des Standort-Jahrs | `YAS_site` | Standort-Jahr |
| **V2-B (lokal)** | YAS-Vorhersage des Regionalmodells für das Bundesland des Standorts (OÖ = AT31, Stmk = AT22) | `YAS_site` | Standort-Jahr |
| **V1 (regional)** | YAS-Vorhersage des Regionalmodells (B) | Statistik-Austria-`YAS` | Region-Jahr |
| **V1-A** | Mittel des Scores A über alle gezogenen Felder der Region und des Jahres | Statistik-Austria-`YAS` | Region-Jahr (nur Regionen/Jahre mit Felddaten) |

Metriken: Spearman ρ mit 95-%-Konfidenzintervall (Cluster-Bootstrap über **Jahre**, 1000 Wiederholungen, Seed 42; `croptransfer.evaluate.spearman_ci`);
n immer angeben. V1 zusätzlich RMSE gegen `YAS = 1` (Differenz mit Cluster-Bootstrap-KI). Beschreibend: Spearman **innerhalb** der Standorte mit
≥ 6 Jahren (je Standort, Median über Standorte), Spearman innerhalb eines Jahres, Vergleich mit B-NDVI.

## 4. Vorab festgelegte Erfolgskriterien

- **V2-A bestanden:** ρ(Score, `YAS_site`) > 0 mit 95-%-KI ohne 0 am 09-01 – nur **auswertbar**, wenn ≥ 15 Standort-Jahre vorliegen (sonst nur beschreibend).
- **V2-B bestanden:** dieselbe Regel für B auf V2.
- **V1 bestanden:** ρ(B, Statistik-Austria-`YAS`) > 0 mit KI ohne 0 am 09-01. **V1 stark:** zusätzlich RMSE kleiner als `YAS = 1`, KI der Differenz ohne 0.
- Mit nur 6 Jahren (V1) bzw. 8 Jahren (V2) als Cluster ist ein KI ohne 0 schwer zu erreichen; ein Verfehlen heißt „nicht belegt“, nicht „widerlegt“.
- **Nicht** Teil der Kriterien: Wahl eines besseren Modells, Wahl des besten Stichtags, Anpassung von Schwellen.

## 5. Datenkritik und Fehleranalyse (verpflichtend, `reports/data_review/at_test.md`)

Maisähnlichkeit der Kurven (Stichprobe, Anteil nicht maistypischer Kurven), Frühernte-/Silomais-Verdacht (abrupter Abfall in Dekade 9–15), Anzahl gültiger
Dekaden je Jahr (Wolken-Bias), Felder je Standort-Jahr und Anteil < 1,5 ha, Wasserfeld/Bewässerung (Marchfeld ist nicht Teil der Standorte), Jahreseffekt vs. Standorteffekt
(ρ innerhalb Jahr / innerhalb Standort), Einfluss einzelner Standorte und Jahre (Leave-one-year-out-ρ), Vorzeichen-Plausibilität, Fehlermuster (Hagel 2018/2023,
Trockenheit 2018/2022, Fehlalarme). Der Befund „Score markiert immer dieselben späten Aussaaten“ (KBS-T4) wird auf Österreich geprüft: Streuung des Scores
innerhalb Standort-Jahr vs. zwischen Jahren.

## 6. Offengelegte Punkte

1. **Versehen:** Beim Ansehen der Metadaten von `data/raw/at_trials.csv` wurden 15 Notiz-Texte ausgegeben, in denen einzelne Versuchsmittel in kg/ha stehen
   (Oberösterreich und Steiermark, verschiedene Jahre). Es wurde nichts ausgewertet; Modelle, Auswahl, Metriken und Kriterien wurden nicht daran angepasst.
2. Die Referenzkurve von A beruht auf nur 77 US-Feld-Jahren (hauptsächlich KBS) und US-Phänologie.
3. Feldzahlen je Standort-Jahr in INVEKOS wurden vor dem Freeze **nicht** angesehen.
4. Der Stress-Score markiert bei KBS in jedem Jahr die Bio-Parzellen T4 (späte Saat); dass er in Österreich Wetterstress und nicht Saatzeit misst, ist offen.
5. Das Feld-Ertragsmodell (Ridge) ist nicht Teil des Tests (siehe oben).

## 7. Prüfsummen

Ausführung: `python -m croptransfer.austria_freeze` (liest nur US-Daten und Gemeindegrenzen). Code-Stand: Commit der Freeze-Tag-Revision.

| Datei | SHA-256 |
|---|---|
| `reports/freeze_at/stress_reference_hls_ndvi.csv` | `f9907c085e0611d496e84fc739ce7048aade902e9a962417e8345e35f074967f` |
| `reports/freeze_at/site_centroids.json` | `961eeffe2fc3acb32fb8ae8ff85efffeaed6f39808f5cf164e14a06c38820ae8` |
| `reports/freeze_at/at_test_config.json` | `770d807909fa21b5e51e11df20f09c37ad14326fa40802c7a258d7c1cb9db4c0` |

Regionalmodell: 14 Dateien in `reports/freeze_protocol_cybench.md` (Prüfung durch `verify_freeze` bestanden am 2026-10-17).
