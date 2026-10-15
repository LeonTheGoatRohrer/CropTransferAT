# Datenkritik Phase 0 – Setup & Datenzugang

Datum: 2026-10-15 · Branch `phase-0-setup` · Prüfliste nach `AGENTS.md` §3.
Format je Punkt: *geprüft wie?* → *Befund* → *Konsequenz*. Kennzahlen stammen aus `notebooks/00_data_access.ipynb` bzw. den dort genannten Skripten.

In Phase 0 gibt es noch keine Merkmale und kein Modell. Geprüft wird deshalb, ob die **Rohdaten** für die geplanten Schritte taugen: Repräsentativität, Korrektheit, Einheiten.

---

## 3.1 Repräsentativität (Auswahl-Bias)

**a) Umfang der US-Ertragslabels in der HLS-Zeit**
- *Geprüft wie:* Mais-Feld-Jahre je Quelle aus den Rohdaten gezählt (Notebook §2–4); RY ist nur definiert, wenn ein Feld ≥ 3 Mais-Jahre hat.
- *Befund:*

  | Quelle | Mais-Feld-Jahre | davon mit RY | unabhängige Standort-Jahre |
  |---|---|---|---|
  | KBS MCSE | 96 | 96 | 4 (2014, 2017, 2020, 2023) |
  | BARC | 62 | 27 | 7 (2014, 2016–2021) |
  | Colorado | 10 | **0** | 4 |

  Das ergibt **≈ 123 RY-Labels aus nur ≈ 11 Standort-Jahren**. Die Felder einer Station im selben Jahr teilen Wetter und Bewirtschaftung, deshalb sind sie keine unabhängigen Fälle.
- *Konsequenz:*
  - Effektive Stichprobe für das Jahressignal ist klein. Daraus folgen breite Konfidenzintervalle, Bootstrap über Standort-Jahre und LOFYO als primärer Split (wie geplant).
  - Colorado liefert kein RY und dient nur der Ergänzung für absolute Erträge und Muster innerhalb der Felder.
  - Mead (AmeriFlux) wäre der wichtigste Zuwachs, weil es dort viele Mais-Jahre je Feld gibt.

**b) „Gefährdet“-Fälle hängen an wenigen Jahren und an der RY-Definition**
- *Geprüft wie:* RY für KBS (Tabelle 51, `whole_plot`) in zwei Varianten berechnet.
- *Befund:*
  - Der KBS-Ertrag steigt über 1989–2023 um **+0,087 t/ha pro Jahr** (Sorten, Bewirtschaftung).
  - **Variante 1, Normalwert aus allen anderen Mais-Jahren (1989–2023):**
    - RY-Mediane 2014/17/20/23 = 1,35 / 1,10 / 1,21 / 1,49. Moderne Jahre wirken also systematisch überdurchschnittlich.
    - Nur 12 Fälle haben RY < 0,85, und **11 davon sind Bio-Parzellen (T4)**. „Gefährdet“ würde dann eher die Bewirtschaftung als ein Stressjahr messen.
  - **Variante 2, Normalwert nur aus den HLS-Jahren:**
    - RY-Mediane 1,09 / 0,83 / 0,91 / 1,18.
    - 25 Fälle haben RY < 0,85, davon **13 im Jahr 2017**.
- *Konsequenz:*
  - `PLAN.md` §3.6 legt nicht fest, **welche** anderen Mais-Jahre in den Normalwert eingehen. Bei langen Reihen mit Trend verzerrt das RY.
  - Das ist eine Festlegung zur Zielgröße und damit eine **Entscheidung des Projektinhabers vor Phase 1** (`AGENTS.md` §8).
  - Vorschlag: Normalwert nur aus Mais-Jahren im Fenster der Satellitendaten (2013–2025) **oder** trendbereinigt. Die Entscheidung kommt in `DECISIONS.md`, ein Test in `test_targets.py`.
  - Die „gefährdet“-Metriken hängen an wenigen Jahren, deshalb wird die Leistung **innerhalb eines Jahres** immer mit berichtet.

**c) Österreich – zeitliche Abdeckung der Regionalerträge**
- *Geprüft wie:* Jahresbereiche in CY-Bench (AT) und in `stat_at_maize.csv`.
- *Befund:*
  - CY-Bench-Erträge für AT enden **2020**, die Prädiktoren laufen bis 2023. Die Dürrejahre 2022 und 2024 fehlen in CY-Bench.
  - Statistik Austria liefert nur die **Bundesland**-Ebene. Bezirke werden nicht veröffentlicht (nur Sonderauswertung, und auch dann geschätzt).
  - 2026 ist nur vorläufig.
- *Konsequenz:*
  - Im CY-Bench-Regionalmodell (Phase 5) AT 2021–2023 aus Statistik Austria ergänzen. Das muss vor Phase 5 entschieden und in `DECISIONS.md` begründet werden.
  - Der Österreich-Test (Phase 7) bleibt regional auf Bundesland-Ebene mit wenigen Region-Jahren, deshalb n und KI immer angeben.
  - 2026 erst nach endgültigen Zahlen verwenden (PLAN-Zeitraum ist ohnehin 2018–2025).

**d) Kleine Bundesländer**
- *Befund:* Wien, Salzburg, Tirol und Vorarlberg haben < 250 ha Körnermais. Die aus Eurostat-Rundungswerten berechneten Erträge 2010–2018 sind dort durch Rundung stark verzerrt (bis > 30 %; in `stat_at_maize.csv` markiert).
- *Konsequenz:* Diese vier Länder im Österreich-Test und in Phase 5 ausschließen oder nach Fläche gewichten. Für 2010–2018 dort CY-Bench-Werte verwenden.

**e) INVEKOS – Bestand und Filter (nur Zählung, Österreich-Regel)**
- *Geprüft wie:* `invekos.crop_code_counts` und `invekos.count_in_state` (Notebook 00 §7). Unabhängige Zweitzählung, die exakt mit dem Bericht des Download-Agenten übereinstimmt. Dateien vollständig verifiziert (Größe, `unzip -t`, alle Features lesbar).
- *Befund:*
  - Körnermais (Code 105): 107–115 Tsd. Schläge in Österreich, 34–39 Tsd. in der Steiermark je Jahr (2018–2025).
  - **Rund 63 % der steirischen Körnermais-Schläge sind < 1 ha** (Median 0,72–0,76 ha). Der Filter ≥ 1,0 ha (PLAN §3.1) behält 12–15 Tsd. Schläge pro Jahr, aber nur gut ein Drittel der Schläge. Kleinbetriebe und Hanglagen sind damit voraussichtlich unterrepräsentiert.
  - Der Anteil ≥ 1 ha steigt leicht von 36,4 % (2018) auf 37,5 % (2025). Das passt zur Flurbereinigung bzw. Betriebsvergrößerung, ist aber eine schwache Zeitabhängigkeit des Filters.
  - CCM (Code 106) hat in der Steiermark 7–10 Tsd. Schläge pro Jahr, also so viel wie Silomais. Die Statistik Austria zählt CCM zum Körnermais, der PLAN-Filter (nur Code 105) nicht.
  - Ungültige Geometrien bei Körnermais Steiermark: 0. Doppelte Schläge (gleiche `GEO_ID` + Geometrie) bei Körnermais Steiermark: nur 2021 und 2024 (je 2).
- *Konsequenz:*
  - Im Österreich-Test (Phase 6/7) berichten, welcher Anteil der Fläche bzw. der Schläge abgedeckt ist. Die Ergebnisse gelten für Felder ≥ 1 ha.
  - Ob CCM mitgezählt wird, entscheidet der Projektinhaber vor Phase 6. Wichtig für den Vergleich mit der Statistik Austria (Definition „inkl. CCM“). Der Eintrag kommt in `DECISIONS.md`, und zwar **vor** dem Ansehen österreichischer Daten.
  - Duplikate über `GEO_ID` + Geometrie entfernen; nach `SNAR_CODE` filtern, nicht nach Bezeichnung.

---

## 3.2 Korrektheit (Messfehler, Einheiten, falsche Labels)

| Prüfpunkt | Geprüft wie | Befund | Konsequenz |
|---|---|---|---|
| **Feuchtebasis** | Metadaten + Rückrechnung Nass/Trocken/Feuchte | KBS 15,5 % (laut Korrekturnotiz ab 2001 evtl. 15 %); KBS-828-Punkte nass; BARC 14 % bzw. 15 % je Jahr; Colorado 15,5 %; Österreich 14 % | Spalte `moisture_basis` im Schema; alles auf 15,5 % umrechnen (PLAN §3.6). RY und YAS sind Verhältnisse; dort hebt sich eine konstante Basis auf, eine **jahresweise wechselnde** (BARC) aber nicht → umrechnen ist Pflicht |
| **BARC-Einheitenfehler** | Rastermittel vs. Median der bereinigten Punkte | 2017 CentralFarm 4-7 Mais: Rastermittel 3,3 (vermutlich Mg/ha statt bu/ac); negative Kriging-Werte; Rastermittel teils deutlich unter den Punktmedianen | Rastermittel je Feld-Jahr gegen bereinigte Punkte prüfen (Test in `test_groundtruth_schema.py`); Ausreißer-Feld-Jahre ausschließen und dokumentieren |
| **KBS-Bruch 2017** | Datentabellen-Notizen | bis 2016 nur Osthälfte geerntet, ab 2017 ganze Parzelle | Satellitenmittel für 2014 nur über die Osthälfte bilden oder 2014 gesondert kennzeichnen; in Phase 1 entscheiden |
| **KBS-Ertragsmonitor** | Punktmittel (DT 828) vs. Wiegewagen (DT 51) | Faktor 0,87–1,01, einzelne Parzellen 0,67–1,6 | Label = Tabelle 51; Punkte nur für relative Muster innerhalb der Parzelle (je Feld-Jahr normieren) |
| **Feldgrenzen** | Geodaten gesichtet | KBS Shapefile (Stand 2007); BARC nur Rasterumriss; Colorado und KBS Scale-up ohne Polygone | KBS-Parzellen 0,9 ha → nach −10 m Puffer ≈ 6 HLS-Pixel mit vielen Mischpixeln; HLS-Mindestzahl (5) knapp erfüllt, S2 parallel auswerten |
| **HLS S30 in GEE** | Szenenzählung Graz/KBS Juli 2022 | `filterBounds` liefert ~200 statt ~12 Szenen: Granulen der MGRS-Kacheln in UTM-Zone 01/60 haben Footprints über die Datumsgrenze | behoben in `gee_extract.hls_collection()` (Kachel-Präfix T01/T60 entfernt), Test `test_gee_extract.py`; nach dem Filter plausibel (Graz S30 12 vs. S2 13) |
| **Regionalstatistik** | Abgleich Statistik Austria ↔ Eurostat ↔ CY-Bench | 2019–2024 Eurostat vs. Statistik Austria ≤ 5 ha/t; CY-Bench 2019/20 identisch; keine Revisionen nach „endgültig“; dt/ha → t/ha umgerechnet; AT-2013-Regionalwerte auffällig rund; Saatmais pauschal mit 35 dt/ha | dokumentiert in `DATA_SOURCES.md`; Erzeugung reproduzierbar per `python -m croptransfer.regional_stats` (getestet) |
| **CY-Bench Nullerträge** | Zählung je Land | EE, FI, IE, LV nur Nullen; einzelne Nullen in EL, FR, LT, PT u. a. | in Phase 5 vor dem Training filtern |
| **BARC-Feld-IDs** | Dateinamen über Jahre | uneinheitliche Schreibweisen, zusammengelegte Felder, Doppelkulturen (17 Feld-Jahre) | Zuordnungstabelle in `groundtruth.py`; Doppelkultur-Jahre markieren und getrennt auswerten |

Nicht anwendbar in Phase 0 (n/a): Kurvenform, Frühernte, Sensorwechsel S2-Offset, Wolkenmaske, Feld-Matching IoU. Dafür gibt es noch keine Zeitreihen; das wird in Phase 1 und 2 geprüft.

## 3.3 Scheinzusammenhänge
n/a – noch keine Merkmale oder Modelle. Für später festgehalten: Bei KBS sind Behandlung (T1–T4) und Jahr die dominanten Ertragsfaktoren. Ein Modell könnte über Behandlungs- oder Parzellenkennungen „auswendig lernen“. Deshalb Kennungen nie als Merkmal verwenden und den Vergleich mit und ohne sie wie geplant durchführen.

## 3.4 Leakage
n/a – noch keine Features. Für später festgehalten: Der RY-Normalwert darf nur andere Jahre nutzen (§3.1 b); bei einem trendbereinigten Normalwert darf auch der Trend das Testjahr nicht enthalten.

### Österreich-Regel (AGENTS.md §3.4)
- *Geprüft wie:* Alle Phase-0-Ausgaben zu österreichischen Daten durchgesehen (`DATA_SOURCES.md`, dieser Bericht, Notebook 00, Commits).
- *Befund:*
  - Die Österreich-Regel wurde während Phase 0 eingeführt (Commit `fab07f1`).
  - **Davor** enthielt `DATA_SOURCES.md` (Commit `2d3035b`) eine Tabelle der Statistik-Austria-Körnermaiserträge je Bundesland 2018–2025, und dieser Bericht nannte einzelne Werte (2026 vorläufig, Vbg 2014).
  - Der Download-Agent hat beim Plausibilisieren die Erträge ebenfalls gelesen.
  - Diese Werte wurden für **keine** Entscheidung, keinen Filter, keine Schwelle und kein Merkmal verwendet; es gibt auch noch kein Modell. Sie sind jetzt aus beiden Dokumenten entfernt. Notebook 00 zeigt für Österreich nur Schema und Abdeckung.
  - INVEKOS: nur Schema und Zählungen, keine Satellitendaten.
- *Konsequenz:*
  - Offen dokumentiert. Die Werte bleiben in der Git-History des Commits `2d3035b` sichtbar; History wird nicht umgeschrieben (AGENTS §8).
  - Ab jetzt keine österreichischen Ertragswerte in Doku oder Ausgaben bis zum Freeze.

## 3.5 Ergebnis-Plausibilität
Der GEE-Zugangstest ist nach Korrektur plausibel (Szenenzahlen HLS L30 + S30 entsprechen der erwarteten Wiederkehr von 2–3 Tagen). Sonst n/a.

---

## 3.6 Entscheidung

⚠️ **Weiter mit Einschränkung.** Alle Datenquellen aus PLAN.md Phase 0 liefern Daten oder sind begründet als „angefragt“ markiert (Mead, YieldSAT, Bodenklimazahl). Die Befunde sind dokumentiert.

Gesamtbild inklusive Nachtrag (N.6):
- KBS, BARC, Colorado, CY-Bench, Statistik Austria, INVEKOS, Verwaltungsgrenzen, SSURGO, AT-Versuchsberichte: ✅/⚠️.
- **One Acre Fund: ⛔ für die Feldauswertung mit Satellitenkurven**, bis der Projektinhaber entscheidet (N.6). Das blockiert den Abschluss von Phase 0 nicht, weil Phase 0 nur Datenzugang prüft. Es **muss aber vor Phase 1 geklärt sein**.

Offene Entscheidungen des Projektinhabers:

| # | Thema | spätestens vor |
|---|---|---|
| 1 | **RY-Normalwert:** nur Mais-Jahre 2013–2025 oder trendbereinigt (§3.1 b) | Phase 1 |
| 2 | **One Acre Fund:** Anfrage an Autoren / nur Tabellenanalyse / neuer Filter (N.6) | Phase 1 |
| 3 | `RY_nb`-Gruppierung für One Acre Fund (N.2) | Phase 1 |
| 4 | **CCM (Code 106)** als Körnermais zählen oder nicht (§3.1 e) | Phase 6, vor dem Ansehen österreichischer Daten |
| 5 | AT 2021–2023 im CY-Bench-Modell aus Statistik Austria ergänzen (§3.1 c) | Phase 5 |

Technisch in Phase 1 zu lösen: kleine effektive Stichprobe (≈ 11 Standort-Jahre, Mead hat hohe Priorität), KBS-Osthälfte bis 2016, BARC-Einheitenfehler, Feuchte-Umrechnung je Quelle.

---

# Nachtrag – neue Quellen aus PLAN.md v0.0.5 (One Acre Fund, SSURGO, AT-Versuchsberichte)

Datum: 2026-10-15. Kennzahlen aus `python -m croptransfer.one_acre_fund` und `python -m croptransfer.soil_ssurgo` (Details in `DATA_SOURCES.md` §9, §11, §12). Für One Acre Fund wurden **keine Satellitendaten angesehen** (Vorab-Filter PLAN.md §3.1). Die österreichischen Versuchsberichte wurden nur gesammelt und abgeschrieben, **nicht ausgewertet** (Österreich-Regel).

## N.1 Repräsentativität (Auswahl-Bias)

**a) One Acre Fund – wer fällt durch den GPS-Filter?**
- *Geprüft wie:* Exakte Position = alle fünf Bodenspalten vorhanden (laut Beschreibung nur bei feldgenauer Position abgefragt; 69,9 % ≈ die genannten 70 %). Zählung je Land/Jahr, Median-Ertrag exakt vs. nicht exakt.
- *Befund:*
  - 10 332 von 14 773 Feldern bleiben. Der Filter wirkt sehr ungleich: Kenia 97 % exakt, Uganda/Nigeria 100 %, Sambia 81 %, Tansania 46 %, Ruanda 24 %, Burundi 22 %. **68 % der verbleibenden Felder liegen in Kenia**; Tansania 2016, Ruanda 2018, Burundi außer 2017 fallen ganz weg.
  - Ausgeschlossene Felder haben **niedrigere Erträge**: Median Kenia 2028 vs. 2786 kg/ha, Tansania 2445 vs. 3004, Burundi 1565 vs. 2020, Sambia 2106 vs. 2445 (Ruanda ≈ gleich). Vermutung: Felder ohne GPS gehören eher zu Nicht-Programm-Bäuerinnen und -Bauern.
  - Gemeldete Schäden sind unter den exakten Feldern häufiger (`pest` 36 % vs. 21 %, `water_excess` 9 % vs. 5 %) – vor allem, weil Kenia überwiegt.
- *Konsequenz:* Der gefilterte Datensatz ist im Wesentlichen „Westkenia + etwas Tansania/Sambia“. Leave-One-Region-Out ist mit Burundi/Ruanda/Nigeria/Uganda nur mit sehr kleinem n möglich (n immer angeben). Ergebnisse auf One Acre Fund nicht als „Subsahara-Afrika“ verallgemeinern.

**b) One Acre Fund – Jahre und Sensor**
- *Befund:* 2021 fehlt; 2022 nur Nigeria (115). Saison 2016 wurde ab 2015-03 gesät (nur Sentinel-2A; L2A-Abdeckung Afrikas vor Ende 2018 ungeprüft). Bei 3296 Feldern liegt die Aussaat im Vorjahr von `year`.
- *Konsequenz:* In Phase 1 Abdeckung 2016–2018 prüfen (wie in PLAN.md 3 vorgesehen); `year` als Erntejahr behandeln, Saisonbeginn immer aus `plant_date`.

**c) SSURGO – Variation innerhalb der Standorte**
- *Befund:* Alle 24 KBS-Parzellen liegen in **einer** Map-Unit (KaB, Kalamazoo loam): NCCPI Mais überall 0,664. Am BARC-Testfeld 5 Map-Units.
- *Konsequenz:* M-B+ kann bei KBS nichts zwischen Parzellen erklären, SSURGO wirkt dort nur als Standort-Kennung (Orts-Proxy, §3.3). Bei Faktorenanalyse SSURGO-Effekte getrennt für „zwischen Standorten“ und „innerhalb BARC“ berichten.

**d) Österreichische Versuchsberichte (nur Bestand, keine Auswertung)**
- *Befund:*
  - 150 Standort-Versuch-Jahre. Steiermark: im Wesentlichen 2 Dauerversuchsstandorte (Wagna, Kalsdorf bei Ilz). Oberösterreich: 13 Orte, Schwerpunkt Walding/Mauthausen.
  - Jahreslücken: Stmk 2020/2021 nur teilweise, OÖ 2019 fehlt.
  - Die Lücken haben Ursachen, die mit dem Ertrag zusammenhängen können (Ausfall, Überflutung, technisches Gebrechen, Witterung). Fehlende Zeilen sind also nicht zufällig.
- *Konsequenz:*
  - Im Österreich-Testprotokoll (vor dem Freeze) festlegen, wie Ausfalljahre behandelt werden. Vorschlag: als „nicht verfügbar“ berichten, nicht stillschweigend weglassen.
  - Ebenfalls dort festlegen, ob Mischkultur-Zeilen in den Test kommen.
  - Versuchsparzellen sind gut gedüngt und betreut, deshalb kann `YAS_site` von Praxisfeldern abweichen. Das in der Interpretation nennen.

## N.2 Korrektheit (Messfehler, Einheiten, Labels)

| Prüfpunkt | Geprüft wie | Befund | Konsequenz |
|---|---|---|---|
| **OAF Feldgröße** | Spaltenliste der CSV, Zenodo-Beschreibung, Artikel | **Keine Feldgrößen-Spalte**, obwohl Feldgrößen erhoben wurden | Filter „≥ 0,5 ha“ (PLAN §3.1) **nicht anwendbar** → ⛔ für die geplante Feldauswertung, siehe N.6 |
| **OAF Koordinaten** | Nachkommastellen von `lon`/`lat` | auf **0,001° gerundet** (±56 m je Achse); 1254 exakte Felder teilen Punkt + Saison mit anderen (bis 12) | Ein 20-m-Kreis um den veröffentlichten Punkt liegt bei einem 0,5-ha-Feld (≈ 70 × 70 m) oft **nicht** im Feld → Satellitenkurve wäre häufig Nachbarfläche; siehe N.6 |
| **OAF Feuchtebasis** | CSV, Zenodo, Artikel (PMC11130130) | **nicht angegeben**; Artikel nennt 15 % nur für einen separaten Sortenversuch | Für `RY_nb` unerheblich (Verhältnis innerhalb Gruppe); absolute Erträge als „Feuchte unbekannt (≈ 15 %)“ markieren, nicht mit US-Werten mischen |
| **OAF Nullerträge** | Zählung | 263 Felder mit 0 kg/ha (Kenia 144, Ruanda 61, Tansania 58) | Totalausfall ist plausibel (Schäden), aber als eigene Klasse markieren; bei `RY_nb` bleibt 0 erhalten |
| **OAF Schadens-Kodierung** | Beschreibung + Anteile je Land-Jahr | nur `pest`, `disease`, `striga`, `water_excess`; **Trockenheit steckt in `pest`/`disease`**, **Hagel fehlt**; Anteil exakt 0 in ganzen Land-Jahren (z. B. `pest` 2016 in Kenia/Tansania/Burundi, `water_excess` außerhalb Kenia/Ruanda/Uganda) → „False“ heißt dort vermutlich „nicht gefragt“ | Phase 3 4a: Prüfung „Trockenheit/Hagel“ an gemeldeten Ursachen **nicht möglich**, nur „Nässe“ und „Schädling/Krankheit (inkl. Trockenheit)“; Land-Jahre mit Anteil 0 als fehlend behandeln |
| **OAF Gruppen für `RY_nb`** | Spaltenliste | keine Bezirksspalte; feinste Einheit Klimazone `cz` × `season` × `year`: 76 Gruppen mit ≥ 11 exakten Feldern (10 204 Felder) | Gruppierung festlegen (Vorschlag: `cz` × `season` × `year`) → `DECISIONS.md` vor Phase 1 |
| **SSURGO Mais-Ertragsschätzung** | SDA-Abfrage je Bodenkarte | Hauptkomponenten mit Wert: KBS-Gebiet 10/50, BARC 222/362, Akron 44/110, Mead 37/65; bei KBS hat nur eine 1-%-Nebenkomponente einen Wert | Feldwert nur bei ≥ 50 % Abdeckung (`config.yaml`), sonst NaN; KBS damit ohne Ertragsschätzung → **NCCPI Mais** ist das verlässlichere SSURGO-Merkmal |
| **SSURGO Regelname** | `cointerp`-Abfrage | Corn-Teilmodell heißt „NCCPI - NCCPI Corn Submodel (I)“ | in `config.yaml` festgehalten, Test vorhanden |

## N.3 Scheinzusammenhänge
- One Acre Fund: Programmteilnahme (≈ halbe Stichprobe) ist **nicht** als Spalte enthalten, korreliert aber mit Dünger/Sorte/GPS-Verfügbarkeit → Konfundierung bei der Bewirtschaftungsanalyse (Phase 2.4) benennen.
- Mehrere Felder am selben gerundeten Punkt teilen dieselbe Satellitenkurve, haben aber verschiedene Erträge → würde Rauschen bzw. bei zufälligem Split Leakage erzeugen. Punkt-Duplikate in Phase 1 gemeinsam in einen Fold legen.
- SSURGO bei KBS = konstante Standort-Kennung (siehe N.1 c).

## N.4 Leakage
n/a – noch keine Merkmale. Festgehalten: `RY_nb` darf das Feld selbst nicht im Gruppenmedian enthalten (wie PLAN §3.6).

## N.5 Österreich-Regel
- *Geprüft wie:* Arbeitsablauf der Digitalisierung (Unteragenten mit ausdrücklichem Auswertungsverbot); `at_trials.py` enthält nur Schema- und Einheitenprüfungen und gibt nur Zeilenzahlen je Standort/Jahr aus.
- *Befund:* Österreichische Erträge wurden **nur abgeschrieben**. Es wurden keine Mittel über Jahre, Anomalien, Trends oder Vergleiche mit Modellen oder Satellitendaten berechnet oder angesehen. Wo ein Bericht kein Standortmittel nennt, wurde das Mittel der Sorten bzw. Varianten aus der vollständigen Tabelle berechnet und in `notes` markiert. Das ist Digitalisierung, keine Auswertung.
- *Konsequenz:* Die Österreich-Regel ist eingehalten. `data/raw/at_trials.csv` wird bis zum Freeze nur auf Vollständigkeit erweitert (Koordinaten fragt der Projektinhaber an).

## N.6 Entscheidung (neue Quellen)

- **SSURGO:** ⚠️ **Weiter mit Einschränkung.** NCCPI Mais ist vollständig und wird als SSURGO-Hauptmerkmal verwendet. Die Mais-Ertragsschätzung ist lückenhaft und fehlt für KBS. Innerhalb von KBS gibt es keine Variation.
- **AT-Versuchsberichte:** ⚠️ **Weiter mit Einschränkung.** Die Daten sind gesammelt (Details `DATA_SOURCES.md` §12). Einschränkungen: Feuchtebasis teils nicht angegeben, Ortsnamen uneinheitlich, nur Gemeinde-Genauigkeit, einzelne Widersprüche zwischen Text und Tabelle (in `notes`).
- **One Acre Fund:** ⛔ **Stopp für die geplante Feld-Auswertung mit Satellitenkurven**, bis der Projektinhaber entscheidet. Der Filter aus PLAN.md §3.1 („Feldgröße ≥ 0,5 ha, 20-m-Kreis um exakte Position“) ist mit den veröffentlichten Daten nicht umsetzbar: Die Feldgröße fehlt, und die Koordinaten sind auf ±56 m gerundet. Satellitendaten wurden nicht angesehen, die Entscheidung ist also noch unbeeinflusst. Vorschläge:
  1. **Anfrage** (Projektinhaber) an One Acre Fund bzw. die Autoren (Aramburu-Merlos/Grassini, University of Nebraska–Lincoln): ungerundete Koordinaten und Feldgröße für die Felder mit exakter Position. *Empfohlen*, weil damit der Plan unverändert bleibt.
  2. Bis zur Antwort One Acre Fund **nur als Tabellendatensatz** nutzen, ohne Satellitenkurven: Phase 2.4 (Bewirtschaftung vs. Wetter) und Phase 3 4a nur mit Wetter/Boden. Merkmale wären dann nicht transferfähig und nur für die Analyse geeignet.
  3. **Neuer Filter vor dem Ansehen der Satellitendaten**, z. B. Kreis mit ≥ 60 m Radius um den gerundeten Punkt und nur Punkte ohne weitere Felder in derselben Saison. Das ist eine Planänderung und braucht einen Eintrag in `DECISIONS.md`. Die Mischpixel-Gefahr ist hoch, weil die Felder vermutlich klein sind.
  Außerdem festzulegen: die `RY_nb`-Gruppierung (Klimazone × Saison × Jahr statt Bezirk), und dass Phase 3 4a für Trockenheit und Hagel mit One Acre Fund nicht prüfbar ist.
