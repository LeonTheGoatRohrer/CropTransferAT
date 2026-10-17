# Datenkritik I1 – Innerhalb-Feld-Daten (Kayad, CH-TAN, Colorado, BARC)

Stand 2026-10-17. Plan: `reports/plan_innerfeld.md` (I1). Code: `src/croptransfer/innerfeld.py`, Tests `tests/test_innerfeld.py`. Ergebnis: `data/processed/gt_pixels.parquet` (+ `gt_pixels_summary.json`). Österreich nicht berührt. Es wurde nichts trainiert und keine Schwelle festgelegt; alle Filter folgen in I3.

## Ergebnis in Kürze

| Standort | Status | Feld-Jahre | Zellen je Feld-Jahr | Bewertung |
|---|---|---|---|---|
| **BARC** (Maryland) | lokal, unverändert aus Phase 2.3 | 41 (27 Felder, 2017–2021) | median 532 | ✅ Referenz. Median-ρ NDVI 16.7.–15.8. aus der neuen Tabelle neu berechnet: **0,676** (= berichteter Wert) |
| **Kayad** (Italien) | geladen (Zenodo 14216165, CC BY 4.0, 11 MB) | **3 (1 Feld)**, 2016–2018 | 829–1351 | ⚠️ gut messbar, aber nur ein Feld in drei Jahren |
| **Colorado** (Akron) | lokal | 10 Teilflächen-Jahre | 10–26 Stichprobenpunkte | ⚠️ keine Karte, 3 von 10 fast Totalausfall |
| **CH-TAN** (ETH) | **nicht erhalten** | – | – | ⛔ Datensatz unter **Embargo bis 2028-01-01** |

**Gate J1 (Plan): ⚠️ weiter mit Einschränkung.** BARC-Reproduktion ✓. Formal gibt es drei Standorte, tatsächlich nutzbar als Karte aber nur zwei (BARC, Kayad). Folgen: (1) Die Transfer-Matrix besteht aus einem Paar BARC ↔ Kayad (plus Colorado nur beschreibend). (2) **Gate J2 ist mit diesen Daten „nicht prüfbar“**, weil kein Fremdstandort 10 Feld-Jahre erreicht (Kayad 3). Das ändert sich nur, wenn die Anfragen DWFI und SwissYield Daten bringen. (3) Lieber Etappe I2 mit Kayad und Colorado beginnen als warten; die Planlogik bleibt unverändert.

## 1. CH-TAN (Tänikon, ETH Research Collection)

- Die Datensatzseite (doi:10.3929/ethz-c-000807633) zeigt „EMBARGO BIS 2028-01-01“. Der Download `data_raw.zip` (28,3 MB, mit Ertragskarte) liefert keine Daten; es kam nur eine kleine HTML-Seite (782 Byte) zurück. Skriptzugriff auf `research-collection.ethz.ch` wird zudem durch Bot-Schutz blockiert; er wurde nicht umgangen.
- Auch ohne Embargo wäre der Wert gering: **1 Feld, 1 Jahr, 2 Parzellen mit unterschiedlicher N-Düngung** (betriebsüblich vs. teilflächenspezifisch). Das ist dieselbe Art Störgröße wie KBS-T4 (Behandlung statt Stress).
- **Konsequenz:** CH-TAN entfällt in Plan I1 bis auf Weiteres. Option für den Projektinhaber: Mail an Fabio Turco (Ansprechperson, ETH) mit der Bitte um frühen Zugang für ein Schülerprojekt (Text bei Bedarf in `ANFRAGEN.md` ergänzen). Erwartung gering.

## 2. Kayad et al. (Po-Ebene, Italien)

Quelle: Kayad, Sozzi, Gatto, Marinello, Pirotti, *Remote Sensing* 11(23):2873 (2019); Zenodo 14216165, CC BY 4.0. Ein Körnermais-Feld (22 ha), 2016–2018; Mähdrescher-Monitor, 18 444–22 616 Punkte je Jahr, Abstand median **1,4–1,5 m**; Kriging-Raster 2,2 m; Sentinel-2 nur ein Tag je Jahr (4.8.).

| Prüfung (AGENTS §3) | Befund | Konsequenz |
|---|---|---|
| Koordinaten/CRS | 2016 und 2017: EPSG:32632. **2018: Gauss-Boaga (Roma40), Geometrie dort verschoben.** Die mitgelieferte Datei `yield2018_epsg32632.gpkg` passt zu 2016/2017 (Bounding-Box deckungsgleich) | 2018 aus der EPSG:32632-Datei gelesen, per Assertion abgesichert |
| Einheit | `YIELD` in kg/ha (Mittel 13,9–14,5 t/ha), `HUMID` in %, Feuchtebasis **nicht angegeben** | Nur relativ verwendet. Gegenprobe: relativer Ertrag mit Umrechnung auf 15,5 % Feuchte korreliert mit dem ohne Umrechnung zu ρ = 0,975–0,996. Unerheblich |
| **Sättigung des Monitors** | Exakt **18 000 kg/ha** bei 1,7 % (2016), 7,4 % (2017), 6,3 % (2018) der Punkte; auf Zellen: Anteil Zellen mit ≥ 50 % gedeckelten Punkten 0,1 % / 4,0 % / 2,0 % | Obere Ertragswerte sind abgeschnitten, Streuung nach oben unterschätzt. Spalte `frac_cap` bleibt in der Tabelle; Wiederholung ohne diese Zellen in I4 |
| Niedrige Ausreißer | 76 / 185 / 238 Punkte unter 3 t/ha (Start-/Stopp-Effekte, Wenden); Zellen mit relativem Ertrag < 0,5: 0,2 / 1,1 / 0,9 % | Nicht gelöscht; in I3 per Regel behandeln |
| Rand | Randabstand aus der konvexen Hülle der Punkte (kein Polygon mitgeliefert): 15–17 % der Zellen < 20 m vom Rand (BARC: 47 % wegen kleiner Felder) | `dist_edge_m` in der Tabelle |
| Interpolation | Zellmittel der Punkte vs. Kriging-Raster: ρ = 0,970–0,974 | Kriging ändert die Rangordnung kaum; Rohpunkte genügen |
| Lücken | 2017: nur 829 Zellen mit ≥ 10 Punkten (2016: 1351, 2018: 1532) | Erntelücken, ungleiche Fläche; Zellen-Schnitt über Jahre nur 540 |
| **Bewirtschaftung im Feld** | Die Publikation nennt **variable Stickstoffgabe** durch den Landwirt (gleiche Düngekarte 2016 und 2017). Die Karte liegt nicht vor | Mögliche Störgröße wie „Behandlung“: ein Teil der Zonen kann Düngung statt Stress sein. Benennen, nicht auflösbar |
| Streuung | SD des relativen Ertrags 0,10 / 0,14 / 0,15 (BARC: 0,26); Problemzonen-Anteil (< 0,85) nur **10,6 %** (BARC 27,9 %) | Das Feld ist homogener. Problemzonen-PR-AUC wird dort leichter instabil; Median-ρ bleibt die Hauptkennzahl |
| Wiederkehr | Spearman-ρ des relativen Ertrags derselben Zelle zwischen Jahren: 0,22–0,26 (540 Zellen in allen 3 Jahren) | Deutlich schwächer als BARC (0,67, Phase 2.3). Zonen sind hier weniger dauerhaft |
| Sorte, Saat, Aussaatdatum, Wasser | in den Dateien nicht enthalten | unbekannte Störgrößen |
| Unabhängigkeit | 3 Feld-Jahre desselben Feldes | **n_Feld = 1**; Cluster-Bootstrap über Felder ist nicht möglich. Nur Punktwerte und Vorzeichen |

⚠️ **Weiter mit Einschränkung.**

## 3. Colorado (Akron, USDA-ARS)

Bereits in `DATA_SOURCES.md` §5 beschrieben. Neu geprüft für die Innerhalb-Feld-Tabelle (nur Körnermais, 188 Punkte, 10 Teilflächen-Jahre, ~30 m Abstand):

| Teilfläche-Jahr | Punkte | mittlerer Ertrag (t/ha) | Nullerträge |
|---|---|---|---|
| S2 2019 | 13 | 6,35 | 0 |
| SB5 2019 | 22 | 3,91 | 0 |
| SCD3 2019 | 22 | 4,13 | 0 |
| S4 2021 | 10 | 3,69 | 0 |
| SB4 2021 | 20 | 2,71 | 0 |
| SCD2 2021 | 23 | 2,52 | 0 |
| SB7 2020 | 26 | 0,53 | 5 |
| SCD5 2020 | 16 | 0,88 | 0 |
| SB1 2022 | 20 | 0,29 | 8 |
| SCD6 2022 | 16 | 1,04 | 4 |

- **Vier von zehn Teilflächen-Jahren sind fast Totalausfälle** (Mittel ≤ 1,04 t/ha, 17 Nullwerte). Dort misst der „relative Ertrag“ vor allem, welche Punkte noch etwas gebracht haben (SD des relativen Ertrags 0,46–1,32 statt 0,10–0,34). Sie verändern den Median-ρ stark.
- Keine Polygone, keine Randinformation. Ein 10-m-Pixel enthält höchstens einen Punkt; 10–26 Punkte je Teilfläche sind keine Karte.
- **Konsequenz:** Colorado bleibt in der Tabelle (`kind = sparse_points`), wird aber nur beschreibend und getrennt für die sechs normalen Teilflächen-Jahre berichtet. Die Regel dazu kommt in I3 (nicht nachträglich).

## 4. BARC (Referenz)

Unverändert aus Phase 2.3 (`within_field.load_pixels`): 23 912 Zellen, 41 Feld-Jahre, 27 Felder, 10 m Randpuffer, Kriging-Raster (10 m Blöcke). Prüfung: Zeilenzahl und Verteilung des relativen Ertrags stimmen mit der Tabelle überein; **Median-ρ NDVI 16.7.–15.8. = 0,676 (Phase 2.3: 0,676)**. Bekannte Grenzen: interpolierte Karten, wechselnde Feuchtebasis, Doppelkulturen (`DATA_SOURCES.md` §4).

## 5. Vergleichbarkeit der Standorte (für spätere Schlüsse)

| | BARC | Kayad | Colorado |
|---|---|---|---|
| Quelle der Karte | Kriging 10 m | Rohpunkte → 10-m-Zelle | Einzelpunkte |
| Klima | feucht-gemäßigt (MD) | Po-Ebene | Trockenfeld |
| SD des relativen Ertrags (Median) | 0,26 | 0,14 | 0,28 (0,10–1,32) |
| Anteil Zellen < 0,85 | 27,9 % | 10,6 % | 30,9 % |
| Fläche je Feld-Jahr | klein (Median 532 Zellen) | 22 ha | < 4,3 ha, 10–26 Punkte |

Unterschiedliche Streuung heißt: dasselbe ρ bedeutet an verschiedenen Standorten nicht dasselbe Maß an Nutzen. Deshalb werden Median-ρ **und** der Lift berichtet, und die Streuung steht neben jeder Zahl.

## 6. Entscheidung

⚠️ **Weiter mit Einschränkung (I2 starten).** Offene Punkte für den Projektinhaber: (a) DWFI- und SwissYield-Anfrage absenden (Nr. 10 und 11, bereits fertig in `ANFRAGEN.md`); sie sind jetzt der Engpass für J2. (b) Optional Mail an F. Turco (ETH) wegen frühem CH-TAN-Zugang.
