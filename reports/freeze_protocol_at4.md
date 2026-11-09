# Freeze- und Testprotokoll Österreich IV: Maisfelder 2026 der Hagelversicherung (Feldebene)

**Stand:** 2026-11-09, festgeschrieben **bevor** ein Satellitenwert der Testfelder gelesen oder ein Score berechnet wird. Tag: `freeze-at-4`.
Danach wird an Auswahl, Definitionen, Metriken und Kriterium nichts mehr geändert. Jede Änderung wäre ein neuer Test (`freeze-at-5`), und alle Ergebnisse würden berichtet.
Entscheidung des Projektinhabers (Chat 2026-11-09): „Österreich-Beweis jetzt starten.“

## 0. Einordnung
- **Erster Test zwischen Feldern innerhalb eines Jahres.** Die Tests I–III prüften nur, ob gute und schlechte *Jahre* erkannt werden; „Standorte im Jahr“ war nie prüfbar.
  Hier wird geprüft: Reiht der eingefrorene Stress-Score die Körnermaisfelder **2026** so wie ihr tatsächlicher Ertrag?
- **Modell unverändert:** Stress-Score A aus `freeze-at-1`, Referenzkurve `reports/freeze_at/stress_reference_hls_ndvi.csv`, HLS-Regeln, Innenpuffer −10 m, Mindestdekaden 4,
  Wolkenregel `clear_frac ≥ 0,7`, Funktionen `at_test.field_table` und `at_extract._stats` unverändert. Nichts wird an österreichischen Daten eingestellt.
- Tests I–III bleiben unverändert stehen. Dieser Test ersetzt nichts.
- **Weizen wird nicht geprüft:** Die Referenzkurve und die Dekaden des Scores sind für Mais festgelegt. Ein Weizentest wäre ein neues Modell.

## 1. Was vor dem Freeze schon gesehen wurde (ehrlich offengelegt)
- Der KI-Assistent hat am 2026-11-09 die Ertragsdateien geöffnet und beschrieben: Verteilungen, Einheiten (Gesamt-kg je Feldstück statt kg/ha), Ausreißer, Feuchte,
  doppelte IDs und Regionen. **Die Erträge sind also nicht blind.**
- **Blind sind die Scores:** Für keines der Testfelder wurde je ein Satellitenwert gelesen oder ein Score berechnet. Einzige mögliche Ausnahme: Test III hat 2026 bis zu 100
  INVEKOS-Schläge im Umkreis von 5 km um Wagna und Kalsdorf ausgewertet, nur als Mittelwert und ohne Feldertrag. Überschneidungen werden im Bericht gezählt.
- **Eine Regel wurde vor dem Freeze korrigiert, ohne Scores:** Die erste Fassung schloss alle Felder aus, deren Gesamtertrag exakt einem anderen Feld glich (129 Felder).
  Die Prüfung zeigte, dass das fast nur runde Werte (z. B. 5.000 kg) in verschiedenen Regionen sind (95 % der Gruppen in verschiedenen 10-km-Zellen).
  Endgültig gilt: Ausschluss nur bei gleichem Gesamtertrag **in derselben 10-km-Zelle** (aufgeteilte Betriebssumme, 6 Felder).
- Die Schwelle für Körnermais (≥ 90 % Fläche Code 105) wurde nach einer reinen Geometrieprüfung gewählt: 781 Felder liegen über 90 %, 45 unter 25 %, dazwischen keines.

## 2. Daten und Bereinigung (vorab festgelegt, `config.yaml: at_test4`, Code `src/croptransfer/at_test4.py`)
- **Erträge:** `data/raw/hagel_at/Mais_2026.xlsx` (Hagelversicherung, erhalten 2026-11-09, laut Lieferant **nicht qualitätskontrolliert**). Spalten nach Position:
  `field_id`, Gesamtertrag in kg je Feldstück (der Spaltenkopf „kg/ha“ stimmt nicht, siehe §1), Erntefeuchte (Anteil).
- **Polygone:** `data/raw/hagel_at/ama_2026_mais_epsg_3416.gpkg` (AMA-Feldstücke 2026, nur `field_id`). Fläche = Polygonfläche in EPSG:3416.
- **Regeln in dieser Reihenfolge** (jedes Feld erhält die erste zutreffende): exakte Doppelzeilen zählen einmal → widersprüchliche Doppel-IDs raus →
  gleicher Gesamtertrag in derselben 10-km-Zelle raus → ohne Polygon raus → **Körnermais**: < 90 % der Fläche von INVEKOS-2026-Schlägen Code 105
  (`INSPIRE_SCHLAEGE_2026-1_POLYGON`) bedeckt → raus → Fläche < 1,0 ha raus (Regel aus `freeze-at-1`) → kein Ertrag raus →
  **Ertrag `y_t_ha` = Gesamtertrag / Fläche / 1000** außerhalb 1,5–16 t/ha raus.
- **Ergebnis der Bereinigung** (vor dem Freeze ausgeführt, `data/interim/at4/yields_clean.csv`): 826 Feldstücke → **635 behalten**; ausgeschlossen: Fläche < 1 ha 100,
  kein Körnermais 44, unplausibler Ertrag 41, gleiche Betriebssumme 6.
- **Scores:** HLS 1. April–1. November 2026, abgefragt je 10-km-Zelle. Ein Feld ohne gültigen Score (< 4 beobachtete Dekaden) zählt als fehlend und wird nicht ersetzt.

## 3. Auswertung (Stichtage 07-15, 08-01, 08-15, 09-01; Hauptstichtag 09-01)

| Auswertung | Inhalt | Rolle |
|---|---|---|
| **Haupt** | Spearman ρ zwischen Stress-Score und `y_t_ha` über alle behaltenen Felder | Kriterium unten |
| NDVI-Vergleich | mittleres NDVI Dekaden 9–14 (ohne Lernen) und ρ(Score) − ρ(NDVI), gepaarter Bootstrap | beschreibend |
| Innerhalb der Region | ρ je 20-km-Zelle mit ≥ 8 Feldern, Median über die Zellen (Score und NDVI) | beschreibend |
| Problemfelder | Anteil der 20 % Felder mit tiefstem Score, die auch zu den 20 % mit tiefstem Ertrag gehören (Zufall: 20 %) | beschreibend |
| Ertrag je Score-Fünftel | mittlerer Ertrag in den fünf Score-Gruppen | beschreibend |
| Sensitivität Feuchte | Ertrag auf 14 % umgerechnet, nur Feuchte 0,10–0,40 | beschreibend |
| Sensitivität Abreife | ohne Felder mit abruptem Abfall (`abrupt_drop`, z. B. frühe Ernte) | beschreibend |
| Sensitivität Plausibilität | zusätzlich die 41 Felder mit unplausiblem Ertrag | beschreibend |

95-%-Intervalle: Cluster-Bootstrap über 10-km-Zellen (benachbarte Felder teilen Wetter und Boden), 1000 Wiederholungen, Seed 42 (`at_test.rho_ci`). n und Anzahl Zellen immer angeben.

## 4. Kriterium (vorab)
- **Bestanden:** ρ > 0 und die untere Grenze des 95-%-KI über 0 am Stichtag 09-01, nur auswertbar bei **≥ 200 Feldern mit gültigem Score**; sonst „nicht auswertbar“.
- „Besser als NDVI“ ist **kein** Kriterium. Es wird beschreibend berichtet und nur behauptet, wenn das Intervall von ρ(Score) − ρ(NDVI) über 0 liegt.
- Kein Sieger, keine Stichtagswahl, keine Änderung der Regeln nach dem Ergebnis. Schlechte Ergebnisse werden genauso berichtet.

## 5. Grenzen (vorab)
- **Ein Jahr.** 2026 war in der Steiermark ein Hitze- und Trockensommer (Test III). Ob das Ergebnis in normalen Jahren hält, bleibt offen.
- **Erträge nicht kontrolliert, Einheit erschlossen:** Gesamt-kg je Feldstück wurde aus dem Verhältnis zur Fläche abgeleitet (Steigung log Ertrag zu log Fläche 0,88).
  Ob die Versicherung dieselbe Fläche verwendet, ob nass oder trocken gewogen wurde und wie gemischte Einheiten entstanden, ist beim Lieferanten nicht geklärt.
- **Auswahl:** Versicherte Betriebe, rund 1 % der österreichischen Maisfläche, Schwerpunkt Niederösterreich. Keine Zufallsstichprobe.
- Zwischen Feldern wirken Boden, Sorte, Saattermin, Bewässerung und Düngung. Der Score kann einen Teil davon über das Grün mitmessen. Ursachen sind nicht ablesbar.
- Nur Feldmittel. Die Feldkarte (innerhalb des Feldes) wird hier **nicht** geprüft.
- Die feldgenauen Erträge bleiben außerhalb des Repositorys (`data/`). Ins Repository kommen nur zusammengefasste Kennzahlen.

## 6. Prüfsummen (SHA-256)
| Datei | SHA-256 |
|---|---|
| `config.yaml` | `53f943827716d69f8c5ec11c65368a665da27fc64b62c8adb5cca9f006a18920` |
| `src/croptransfer/at_test4.py` | `e70bbd2562997284b61f65ed4f91a3bcdbc8c749fa74f5e6978bef04279c2b75` |
| `reports/freeze_at/stress_reference_hls_ndvi.csv` | `f9907c085e0611d496e84fc739ce7048aade902e9a962417e8345e35f074967f` |

Nicht im Repository (Rohdaten, `DATA_SOURCES.md` §19):

| Datei | SHA-256 |
|---|---|
| `data/raw/hagel_at/Mais_2026.xlsx` | `1fb0be24a4fd599a9bc4d526a5d3c3d73ecf8b6b424bb554f29b78a8affb0ebe` |
| `data/raw/hagel_at/ama_2026_mais_epsg_3416.gpkg` | `94c28bb3e31140b51946feae7c7eb925df0ebcab11a3f03ce02d81a422eb1741` |
| `data/interim/at4/yields_clean.csv` | `324c72a97efb992570e9903d1b7cf13d7695fa1800229545d77e0cecb2f7df9e` |
