# Freeze- und Testprotokoll Österreich II: Steiermark (explorativ)

**Stand:** 2026-10-17, festgeschrieben **vor** der Auswertung steirischer Versuchserträge. Tag: `freeze-at-2`. Danach wird an Auswahl, Definitionen, Metriken und Kriterien nichts
mehr geändert; jede Änderung wäre ein neuer Test (`freeze-at-3`), beide Ergebnisse würden berichtet.

## 0. Einordnung
- **Zweiter Test, nicht Verbesserung des ersten.** Der erste Test (`freeze-at-1`, `reports/at_test_ergebnis.md`) konnte die Steiermark nicht prüfen, weil dort nur Düngungs- und Bodenbearbeitungsversuche
  vorliegen und der damals registrierte Filter (Sortenversuche) sie ausschloss. Dieser Test holt das nach; das Ergebnis des ersten Tests bleibt unverändert.
- **Modelle unverändert:** Stress-Score (A) und EU-Regionalmodell (B) aus `freeze-at-1`. Die Scores, Regionalvorhersagen und Standortpositionen werden **nicht neu berechnet**, sondern aus
  `results/2026-10-17_at_test/site_year.csv` übernommen (SHA-256 unten). Es kommen nur die steirischen Standorterträge neu hinzu.
- **Explorativ**, Phase-4-Kriterium „stark genug“ weiterhin von keinem Feldmodell erfüllt (Entscheidung des Projektinhabers, DECISIONS 2026-10-17). **Kein Sieger.**
- **Erwartung ehrlich vorab:** Etwa 15 Standort-Jahre (Wagna ca. 7, Kalsdorf ca. 5, Hatzendorf ca. 3). Das liegt an der Schwelle von 15; wahrscheinlich ist das Ergebnis nur beschreibend.

## 1. Daten (vorab festgelegt)
- **Standorte:** `wagna`, `kalsdorf`, `hatzendorf` (Cluster und Gemeindeschwerpunkte wie in `freeze-at-1`).
- **Jahre:** 2018–2025. Die 100 gezogenen INVEKOS-Felder je Standort-Jahr und deren HLS-Scores sind dieselben wie im ersten Test (alle 24 steirischen Standort-Jahre sind berechnet).
- **Standortertrag `Y(c,y)`:** Versuchsarten **`duengung` und `bodenbearbeitung`**: je Versuchsart die Zeile `Versuchsmittel` (Mittel über die Varianten des Versuchs), dann Mittel der Versuchsarten, dann Mittel der Namensvarianten
  des Clusters im Jahr (Regel wie im ersten Test; die Code-Funktion `at_test.trial_yields` wird unverändert verwendet, nur mit dieser Versuchsartenliste).
- **Sensitivitätsrechnung (nur beschreibend):** zusätzlich `duengung_alternativen` und `fruchtfolge_begruenung`.
- **`YAS_site`:** wie im ersten Test (5 vollständige Vorjahre, olympischer Durchschnitt, sonst Mittel von ≥ 3 anderen Jahren des Clusters, gekennzeichnet `baseline_short`; alle Jahre des Clusters dürfen als Basis dienen, auch vor 2018).
- **Regionalmodell:** Vorhersage für AT22 (Steiermark), nur Jahre ≤ 2023 (Wetter-Eingaben enden 2023).

## 2. Tests und Metriken (Stichtage 07-15, 08-01, 08-15, 09-01; Hauptstichtag 09-01)
| Weg | Vorhersage | Ziel |
|---|---|---|
| **S-A** | Stress-Score (Mittel über die Felder des Standort-Jahrs) | `YAS_site` |
| **S-B** | Regionalmodell AT22 | `YAS_site` |
| Vergleich | mittleres NDVI Dekaden 9–14 (ohne Lernen) | `YAS_site` (nur 09-01) |
| **Zusammen (beschreibend, nicht unabhängig)** | Stress-Score, Oberösterreich (erster Test) + Steiermark | `YAS_site` |

Spearman ρ mit 95-%-Cluster-Bootstrap über Jahre (1000, Seed 42, `at_test.rho_ci`), n und Anzahl der Jahre immer angeben. Beschreibend: ρ innerhalb der Standorte mit ≥ 5 Jahren, innerhalb der Jahre
(mind. 3 Standorte), Leave-one-year-out.

## 3. Kriterien (vorab)
- **S-A bestanden:** ρ > 0 mit KI ohne 0 am 09-01, **nur auswertbar bei ≥ 15 Standort-Jahren**; sonst „nicht auswertbar“ (nur beschreibend). Dasselbe für S-B.
- Der Verbund „Oberösterreich + Steiermark“ wird nie als Test gewertet (Oberösterreich ist aus dem ersten Test bekannt).
- Kein Sieger, keine Stichtagswahl, keine Anpassung von Versuchsarten nach dem Ergebnis.

## 4. Grenzen (vorab)
Düngungs- und Bodenbearbeitungsversuche sind keine reinen Wettereffekt-Messungen (Stickstoffstufe, Verfahren beeinflussen den Ertrag); Versuchsmittel; `YAS_site` meist mit kurzer Basis; Hatzendorf hat nur wenige Jahre;
Gemeindeschwerpunkt statt Parzelle; höchstens 3 Standorte, ≤ 7 Jahre als Cluster.

## 5. Offengelegt
- Beim Ansehen der Metadaten von `at_trials.csv` wurden vor dem ersten Test 15 Notiztexte mit Versuchsmitteln gesehen (Protokoll 1 §6); ob steirische darunter waren, ist nicht gesondert festgehalten.
- Erträge der Steiermark wurden bisher **nicht ausgewertet**; die Auswahl der Versuchsarten (oben) wurde aus der Versuchsart-Liste der Metadaten und nicht aus Erträgen abgeleitet.

## 6. Prüfsummen
| Datei | SHA-256 |
|---|---|
| `reports/freeze_at/at_test_stmk_config.json` | `c706de842720d7b5e044eb1e8d31fc73850bb75ff5f2a1298427732f8fae0376` |
| `results/2026-10-17_at_test/site_year.csv` | `1bd7852706a1551e31316b328504daf9dc422aa547e95845fd6477f93ddf8e73` |
