# Plan: Feinjustierung – Stress-Erkennung statt Jahresvorhersage

> **Status 2026-10-16:** F0.1 bestätigt; F1 umgesetzt (Gate H1 ✓); F2–F3 umgesetzt, **Gate H2 ✗** (kein Merkmal behalten) – F4/F5 entfallen laut Plan. Ergebnis: `reports/feinjustierung_ergebnis.md`. F0.2/F0.3 (Hagel, Feldkarten) liegen beim Projektinhaber.

Stand 2026-10-16. Entwurf. Dieser Plan ersetzt `PLAN.md` nicht. Alle Festlegungen sind **Vorschläge** und gelten erst, wenn der Projektinhaber sie in Schritt F0 bestätigt. Laut `DECISIONS.md` (2026-10-16, G3) braucht jede weitere Modellrunde eine neue Entscheidung; dieser Plan ist die Vorlage dafür.

---

## 0. Kurzfassung

1. **Neu ausgerichtet wird das Ziel, nicht die Methode.** Unsere stärksten Ergebnisse sind die Erkennung innerhalb eines Feldes (ρ 0,68) und der einfache Stress-Score (PR-AUC 0,71 bei Zufall 0,33). Schwach ist die Vorhersage, *welches Jahr* schlecht wird (zu wenige unabhängige Wetter-Jahre). Der Plan baut das Starke aus und behandelt das Schwache als Nebenfrage.
2. **Mehr Kulturen sind nur noch Nebeneffekt** (Entscheidung des Projektinhabers im Chat, 2026-10-16): kein Training zusätzlich auf Weizen, Erbse oder Gerste im Hauptmodell. Vorhandene Ergebnisse bleiben als Dokumentation.
3. **Neue Datenquellen werden einzeln getestet** (Radar, Oberflächentemperatur, Entwicklungsstadium, Aussaattermin) und nur behalten, wenn sie nach vorab festgelegter Regel messbar helfen.
4. **Die Hagelversicherung liefert Österreich-Daten.** Sie werden ungeöffnet abgelegt und erst nach dem Freeze verwendet (Österreich-Regel).
5. **Der Plan hat 5 Etappen, 19 Schritte und 3 Gates.** Es gibt höchstens eine Modellrunde je Etappe 2–3, danach Bericht.
6. **Vom Projektinhaber gebraucht:** vier Entscheidungen (F0.1), die Hagel-Datenübergabe (F0.2), Anfragen für Feldkarten (F0.3, Texte in `reports/data_search.md`).

---

## 1. Ausgangslage (aus Dateien, nicht neu gerechnet)

| Aufgabe | Bestes Ergebnis | Quelle |
|---|---|---|
| Innerhalb eines Feldes (BARC, NDVI Mitte Juli–Mitte Aug. vs. Pixel-Ertrag) | Median-ρ 0,68 [0,54; 0,72], 41 Feld-Jahre | `reports/results.md` |
| Gefährdete Felder (RY < 0,85) per Stress-Score, 1.9. | PR-AUC 0,71 (Zufall 0,33), ρ 0,43 [0,24; 0,72], n = 89 / 8 Cluster | `reports/results.md` |
| Absoluter Ertrag Y, Satellit | ρ 0,52 [0,22; 0,76], R² 0,32 | `reports/results.md` |
| Regional EU (CY-Bench) | Skill 0,07, ρ 0,38 [0,36; 0,40], 8 371 Region-Jahre | `reports/results_phase5.md` |
| Jahresvorhersage (Phase 4 „stark genug“) | **nicht bestanden**, auch Mehr-Kulturen (G3 ✗) | `reports/phase4_mehrkultur.md` |

Engpass: 8–11 unabhängige US-Standort-Jahre (Wetter-Vielfalt), nicht die Zahl der Felder. Hinweis zur Kennzahl: gepooltes Spearman-ρ ist im Leave-Jahr-Out für Baselines negativ (Trainingsmittel-Effekt, `phase4_mehrkultur.md`); deshalb wird in diesem Plan **innerhalb** von Jahr und Region gemessen (F1.2).

---

## 2. Neue Zielhierarchie (Vorschlag, in F0.1 zu bestätigen)

| Rang | Frage | Kennzahl | Warum |
|---|---|---|---|
| **A** (Hauptziel) | Welche Felder einer Region fallen im Jahr auf (gefährdet RY < 0,85)? | PR-AUC, Recall bei 20 % FPR, je Jahr gruppiert (Cluster = Standort-Jahr) | Hier liegt das stärkste Signal; vergleichende Aussage braucht keine Jahres-Wettervielfalt. |
| **B** | Wo *innerhalb* eines Feldes ist der Ertrag niedrig? | Median-ρ über Feld-Jahre | Stärkstes Einzelergebnis (0,68). |
| **C** (Nebenfrage) | Wie stark weicht das Jahr vom Normalen ab? | RMSE-Differenz zu B0/B1, Skill (Regionalmodell) | Bleibt dokumentiert, wird nicht verbessert, solange Daten fehlen. |

---

## 3. Maßnahmen und Entscheidungsregel

Jede neue Datenquelle ist ein **Zusatzmerkmal**, das gegen den Stand von Phase 3 (Stress-Score, Referenzkurve) und Phase 2.3 (within-field) verglichen wird. Behalten wird sie nur, wenn **beide** Bedingungen gelten (Vorschlag):

1. ΔPR-AUC (Ziel A) ≥ +0,02 **oder** Δ Median-ρ (Ziel B) ≥ +0,02, jeweils mit Cluster-Bootstrap-KI (1 000, Seed 42), dessen Untergrenze > 0 liegt;
2. keine Verschlechterung des jeweils anderen Ziels um mehr als 0,02.

Sonst: verworfen und als negatives Ergebnis dokumentiert (AGENTS.md §7.1).

| ID | Maßnahme | Idee | Konkret | Grenzen (ehrlich) |
|---|---|---|---|---|
| **M1** | Sentinel-1 Radar | wolkenunabhängig, füllt Lücken (in Mehr-Kulturen hatten nur 235 von 474 Zeilen eine gültige Kurve) | `COPERNICUS/S1_GRD`, VV, VH, VH/VV, RVI; Median im Feldpolygon je Szene; Dekaden-Komposit wie bei HLS; ab 2017 | nur ab 2017, daher weniger US-Jahre; Radar reagiert auf Feuchte und Struktur, nicht direkt auf Grün |
| **M2** | Oberflächentemperatur (Landsat 8/9 ST_B10, 30 m, 16 Tage), MODIS LST (1 km) und Verdunstung (MODIS MOD16, ERA5-Land) | Trockenstress zeigt sich oft früher in der Temperatur als im Grünindex | Mittel der Kronentemperatur minus Lufttemperatur (ERA5-Land) je klarer Szene; Anomalie gegen Nachbarfelder desselben Tages | wenige klare Szenen pro Saison; ECOSTRESS nicht in GEE; MODIS zu grob für Einzelfelder |
| **M3** | Entwicklungsstadium (GDD-Achse) | Jahre mit früher/später Saat vergleichbar machen | `gdd_axis.py` existiert; neu: Stress-Score und Referenzkurve auf GDD-Achse; Phase 2.4 zeigte für das Jahresmodell keinen robusten Unterschied, für den Stress-Score noch nicht getestet | Aussaat ungenau (siehe M4) |
| **M4** | Aussaat-/Auflaufdatum aus der Kurve. **Sorte ist nicht ableitbar**: nur wo die Quelle sie nennt (KBS), sonst als bekannte Störgröße benannt | größte unbekannte Störgröße | Begrünungsbeginn (NDVI-Schwellendurchgang, Schwelle vorab) als Merkmal; Prüfung gegen KBS-Saattermine, wo bekannt | HLS-Lücken im Frühjahr; Sorte bleibt unbekannt |
| **M5** | Regionalmodell als Merkmal | Jahrescharakter aus Feldern der Umgebung und Region | CY-Bench-Vorhersage (YAS) als Merkmal, **nur wenn** CY-Bench US-Regionen für die Trainingsjahre enthält (prüfen in F1.4) | sonst entfällt; in Österreich später möglich |
| **M6** | Feldkarten | löst den Engpass der unabhängigen Jahre | YIPEEO (CZ/SK), SwissYield Witzwil, Booßen; Anfragen laufen parallel | nur nach Freigabe |

---

## 3b. Zuordnung Ihrer sieben Punkte

| Punkt | Schritt |
|---|---|
| 1 Fokus auf Innerhalb-Feld und Stress-Score als Hauptergebnis | Abschnitt 2, F1.1, F3.4 |
| 2 Sentinel-1 Radar | M1, F2.1 |
| 3 Temperatur und Verdunstung | M2, F2.2, F2.5 (ECOSTRESS nicht in GEE, ersetzt durch Landsat-Temperatur) |
| 4 Entwicklungsstadium (GDD) | M3, F2.3 |
| 5 Aussaattermin und Sorte | M4, F2.4 (Sorte nur wo bekannt) |
| 6 Regionalmodell als Merkmal | M5, F1.4 (erst Machbarkeit prüfen) |
| 7 Mehr Feldkarten | M6, F0.3 |

## 4. Arbeitsplan

Aufwand: S = unter ½ Tag, M = 1 Tag, L = 2–3 Tage. „Claude“ = KI-Agent im Repo; Projektinhaber prüft und kann jede Zeile erklären (AGENTS.md §1). Jede Abweichung in `DECISIONS.md`, jede Hilfe in `SUPPORT.md`, je großem Schritt ein Website-Eintrag (`app/versions.yaml`).

### Etappe F0 – Entscheiden und anfragen (Projektinhaber)

| Nr | Wer | Was | Abnahme |
|---|---|---|---|
| **F0.1** | Projektinhaber | Vier Entscheidungen: (1) Zielhierarchie A/B/C (Abschnitt 2); (2) Entscheidungsregel für neue Merkmale (Abschnitt 3); (3) Mehr-Kulturen nur als Nebeneffekt bestätigen; (4) erlaubt der Plan **eine** neue Modellrunde (F4.2) | Antworten in `DECISIONS.md` (trägt Claude ein) |
| **F0.2** | Projektinhaber | Hagelversicherung: Daten nach Eingang **ungeöffnet** unter `data/raw/hagel_at/` ablegen und nicht an Claude weitergeben, bis das Freeze-Protokoll steht. Gewünschte Spalten: Schadendatum, Schlag oder Koordinate (oder Gemeinde), Kultur, Schadenshöhe in Prozent, Schadensursache (Hagel/Sturm), Versicherungsjahr | Datei vorhanden, Eintrag in `ANFRAGEN.md` |
| **F0.3** | Projektinhaber | Anfragen Feldkarten senden (Reihenfolge und Texte: `reports/plan_mehrkultur.md` §8) | Datum je Anfrage in `ANFRAGEN.md` |

### Etappe F1 – Messlatte neu festlegen (Claude, vor jedem Modelllauf)

| Nr | Wer | Was | Ergebnis | Aufwand |
|---|---|---|---|---|
| **F1.1** | Claude | Ausgangswerte der Ziele A und B aus den bestehenden Ergebnissen reproduzieren (Phase 2.3, Phase 3), mit Cluster-KI | `results/<datum>_feinjust_baseline/` | M |
| **F1.2** | Claude | Auswertung **innerhalb** von Standort-Jahr bzw. Region festlegen (kein gepooltes ρ über Folds), Schwellen für Ziel A (Recall bei 20 % FPR) | Eintrag in `DECISIONS.md` vor Lauf | S |
| **F1.3** | Claude | Test: neues Merkmal darf nur Daten bis zum Stichtag nutzen (`test_no_leakage.py` auf Radar, Temperatur, Saatdatum erweitern) | grüne Tests | M |
| **F1.4** | Claude | Prüfen, ob CY-Bench US-Regionen und -Jahre für M5 enthält (nur Zählung) | Notiz in `DATA_SOURCES.md` | S |

**Gate H1:** Ausgangswerte reproduziert (innerhalb 0,02 der berichteten) und Messregel committet. Sonst Ursache klären, nicht weitermachen.

### Etappe F2 – Neue Merkmale einzeln (nur US-Trainingsdaten, nie Österreich)

| Nr | Wer | Was | Ergebnis | Aufwand |
|---|---|---|---|---|
| **F2.1** | Claude | M1 Radar: GEE-Extraktion für alle US-Feld-Jahre ab 2017, Komposit, Qualitätsregeln (Wertebereiche, Sensorwechsel S1A/S1B/S1C), Datenkritik | `data/interim/obs_s1/`, `reports/data_review/f2_radar.md` | L |
| **F2.2** | Claude | M2 Temperatur: Landsat-8/9-Oberflächentemperatur je Feld-Szene, Anomalie gegen Nachbarfelder und gegen ERA5-Lufttemperatur | `data/interim/obs_lst/` | L |
| **F2.3** | Claude | M3 GDD-Achse für Stress-Score und Referenzkurve (`gdd_axis.py` erweitern) | Referenzkurve je Achse | M |
| **F2.4** | Claude | M4 Auflaufdatum aus der Kurve, Schwelle vorab; Plausibilität gegen bekannte Saattermine | Merkmal `emerge_doy` | M |
| **F2.5** | Claude | M2b Verdunstung: MODIS-Verdunstung (MOD16A2GF, 500 m) und ERA5-Land-Verdunstungsanomalie als Trockenstress-Merkmale, Verhältnis tatsächliche zu potenzieller Verdunstung | `data/interim/obs_et/` | M |

### Etappe F3 – Ablation (eine Runde, vorab festgelegt)

| Nr | Wer | Was | Ergebnis | Aufwand |
|---|---|---|---|---|
| **F3.1** | Claude | Je Merkmal M1–M4 einzeln zum Stand von Phase 3 hinzufügen (Ziel A und B), danach alle behaltenen zusammen; LOFYO wie in `DECISIONS.md` | `results/<datum>_feinjust_ablation/metrics.csv` | L |
| **F3.2** | Claude | Kontrollen: Label-Shuffle, Koordinaten-Ablation, Adversarial Validation, Lauf ohne KBS bzw. ohne BARC (Leave-One-Dataset-Out) | `controls.json` | M |
| **F3.3** | Claude | Bericht mit Tabelle „behalten/verworfen“ nach Regel aus Abschnitt 3 | `reports/feinjustierung_ergebnis.md` | M |
| **F3.4** | Claude | **Hauptergebnis formulieren (Ihr Punkt 1):** Stress-Score und Innerhalb-Feld-Karte als Produkt „Welches Feld und welcher Feldteil fällt auf?“ ausbauen: Rangliste der Felder je Region, Feldkarte mit auffälligen Zonen, Score-Erklärung (welche Kurvenphase löst den Alarm aus); Texte in `reports/doku/` und Website-Eintrag. Reihenfolge der Metrik im Bericht: A, B vor C | `reports/doku/hauptergebnis.md`, Website-Seite | M |

**Gate H2:** Mindestens ein Merkmal erfüllt die Regel **oder** der Plan endet mit einem negativen, vollständig dokumentierten Ergebnis. Keine nachträgliche Änderung der Regel. Bei Misserfolg Ziel A/B bleibt auf Stand von Phase 3, Mais-Jahresvorhersage bleibt „nicht stark genug“.

### Etappe F4 – Hauptmodell und Freeze-Vorbereitung (nur nach Gate H2)

| Nr | Wer | Was | Ergebnis | Aufwand |
|---|---|---|---|---|
| **F4.1** | Claude | Hauptmodell festlegen: Merkmalssatz aus F3, Schwellen, Conformal-Quantile; **Auswahl nach der in F1.2 festgelegten Regel** | `reports/freeze_protocol_feinjust.md` (Entwurf) | M |
| **F4.2** | Claude | Eine abschließende Prüfrunde gegen Kriterien H3 (unten) auf den US-Daten | `reports/phase4_feinjust.md` | M |
| **F4.3** | Claude + Projektinhaber | Österreich-Testprotokoll vorab: Hagel (Ziel A, abrupter Schaden), INVEKOS-Mais, Statistik Austria, Marchfeld, Hatzendorf, LK OÖ; Metriken und Erfolgskriterien je Quelle | im Freeze-Protokoll, committet **bevor** eine österreichische Zahl angesehen wird | M |

**Kriterien H3 („stark genug“ für Stress-Erkennung), Vorschlag:** (1) PR-AUC-KI-Untergrenze über der Zufallsrate (≈ 0,33) und Recall bei 20 % FPR ≥ 0,5; (2) Median-ρ innerhalb der Felder ≥ 0,5 mit KI-Untergrenze > 0,3; (3) Label-Shuffle fällt auf Zufallsniveau; (4) kein Verlust beim Leave-One-Dataset-Out um mehr als 0,15 gegenüber dem Gesamtlauf. Nicht-Erreichen heißt: nicht nach Österreich, Phase 5 bleibt Hauptergebnis.

### Etappe F5 – Freeze und Österreich (nur nach H3 ✓ und Freigabe des Protokolls durch den Projektinhaber)

| Nr | Wer | Was | Ergebnis |
|---|---|---|---|
| **F5.1** | Claude | Einfrieren, Prüfsummen, Tag `freeze-3` | `test_freeze.py` grün |
| **F5.2** | Claude | Österreich-Auswertung wie vorab registriert, Hagel zuerst für den Test „abrupter Schaden“ | `reports/at_test_*.md` |

**Gate H3** gilt für F4.2, **Gate H4** vor F5: Protokoll committet, Freeze-Tag gesetzt, Projektinhaber hat das Protokoll gelesen und freigegeben (DECISIONS 2026-10-15, Arbeitsgrenze Freeze).

---

## 5. Hagelversicherung – Regeln

- Behandlung als **reine Testdaten**. Nicht anschauen, nicht auswerten, nicht zur Schwellenwahl nutzen, bis F5.2.
- Zugehörige Schadensursachen („Hagel“) testen die vorab festgelegte Regel „abrupter NDVI-Abfall im Juli/August“ aus Phase 3.
- Lizenz und Weitergabe klären (Versicherungsdaten sind personenbezogen: Aggregierung auf Gemeinde oder Schlag ohne Namen), Eintrag in `DATA_SOURCES.md`; Rohdaten nie ins Repository (AGENTS.md §4.5).

---

## 6. Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Radar und Temperatur helfen nicht (wahrscheinlich bei kleiner Stichprobe) | Entscheidungsregel Abschnitt 3 vorab; negatives Ergebnis ist ein Ergebnis |
| Radar nur ab 2017: weniger US-Jahre als bei HLS | Vergleich immer auf derselben Teilmenge (HLS-only gegen HLS+Radar auf Jahren ≥ 2017) |
| Mehrere Tests an wenigen Clustern: zufällige „Treffer“ | Vorab festgelegte Merkmale M1–M4, eine Runde, Cluster-Bootstrap, keine Mehrfachauswahl |
| Temperatur: wenige klare Landsat-Szenen | Qualitätsregel: ≥ 3 klare Szenen bis Stichtag, sonst Merkmal fehlt (kein Auffüllen) |
| Saattermin aus Kurve ungenau | Nur als Merkmal geprüft, nicht als Wahrheit |
| Österreich-Regel verletzt, weil Hagel-Daten schon vorliegen | Ungeöffnet ablegen, Eintrag in `ANFRAGEN.md`, Agent öffnet die Datei nicht vor F5 |
| Zu viele Quellen, zu wenig Zeit | Reihenfolge M3 (billig) → M1 → M4 → M2; M5/M6 nur bei Verfügbarkeit |

---

## 7. Welche Dateien sich ändern

| Datei | Änderung | Schritt |
|---|---|---|
| `config.yaml` | Blöcke `s1:`, `lst:`, `emerge:` mit Schwellen | F2 |
| `src/croptransfer/extract_s1.py` (neu) | Radar-Extraktion | F2.1 |
| `src/croptransfer/extract_lst.py` (neu) | Oberflächentemperatur | F2.2 |
| `src/croptransfer/gdd_axis.py`, `stress.py` | GDD-Referenzkurve | F2.3 |
| `src/croptransfer/features.py` | Radar, Temperatur, `emerge_doy` | F2 |
| `src/croptransfer/phase3.py` | Ablation je Merkmal | F3.1 |
| `tests/` | Leakage je neuem Merkmal, Schema, Ablation | F1.3 |
| `DATA_SOURCES.md`, `DECISIONS.md`, `SUPPORT.md`, `CHANGELOG.md`, `ANFRAGEN.md`, `app/versions.yaml` | Einträge | laufend |

---

## 8. Checkliste für den Projektinhaber

1. F0.1 beantworten (vier Entscheidungen) – danach beginnt Claude mit F1.
2. Hagel-Daten nach Eingang **ungeöffnet** ablegen (F0.2).
3. Anfragen für Feldkarten senden (F0.3).
4. Vor F5: Freeze-Protokoll lesen und freigeben.
