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
  - 2026 ist vorläufig, und die Erträge sind extrem niedrig (Bgld 5,3, NÖ 5,2 t/ha).
- *Konsequenz:*
  - In Phase 4 AT 2021–2023 aus Statistik Austria ergänzen. Das muss vor Phase 4 entschieden und in `DECISIONS.md` begründet werden.
  - V1 (Phase 3) bleibt auf Bundesland-Ebene mit wenigen Region-Jahren, deshalb n und KI immer angeben.
  - 2026 erst nach endgültigen Zahlen verwenden (PLAN-Zeitraum ist ohnehin 2018–2025).

**d) Kleine Bundesländer**
- *Befund:* Wien, Salzburg, Tirol und Vorarlberg haben < 250 ha Körnermais. Die aus Eurostat-Rundungswerten berechneten Erträge 2010–2018 sind dort stark verzerrt (z. B. Vbg 2014: 13,0 statt 9,5 t/ha).
- *Konsequenz:* Diese vier Länder für V1/Phase 4 ausschließen oder nach Fläche gewichten. Für 2010–2018 dort CY-Bench-Werte verwenden.

**e) INVEKOS – Filter und Ausschlüsse**
- *Status:* Der Bericht des INVEKOS-Agenten steht noch aus. Dieser Abschnitt wird nach Abschluss ergänzt (Anteil Körnermais-Schläge ≥ 1 ha, Silomais, ungültige Geometrien, Steiermark je Jahr).

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
| **CY-Bench Nullerträge** | Zählung je Land | EE, FI, IE, LV nur Nullen; einzelne Nullen in EL, FR, LT, PT u. a. | in Phase 4 vor dem Training filtern |
| **BARC-Feld-IDs** | Dateinamen über Jahre | uneinheitliche Schreibweisen, zusammengelegte Felder, Doppelkulturen (17 Feld-Jahre) | Zuordnungstabelle in `groundtruth.py`; Doppelkultur-Jahre markieren und getrennt auswerten |

Nicht anwendbar in Phase 0 (n/a): Kurvenform, Frühernte, Sensorwechsel S2-Offset, Wolkenmaske, Feld-Matching IoU. Dafür gibt es noch keine Zeitreihen; das wird in Phase 1 und 2 geprüft.

## 3.3 Scheinzusammenhänge
n/a – noch keine Merkmale oder Modelle. Für später festgehalten: Bei KBS sind Behandlung (T1–T4) und Jahr die dominanten Ertragsfaktoren. Ein Modell könnte über Behandlungs- oder Parzellenkennungen „auswendig lernen“. Deshalb Kennungen nie als Merkmal verwenden und den Vergleich mit und ohne sie wie geplant durchführen.

## 3.4 Leakage
n/a – noch keine Features. Für später festgehalten: Der RY-Normalwert darf nur andere Jahre nutzen (§3.1 b); bei einem trendbereinigten Normalwert darf auch der Trend das Testjahr nicht enthalten.

## 3.5 Ergebnis-Plausibilität
Der GEE-Zugangstest ist nach Korrektur plausibel (Szenenzahlen HLS L30 + S30 entsprechen der erwarteten Wiederkehr von 2–3 Tagen). Sonst n/a.

---

## 3.6 Entscheidung

⚠️ **Weiter mit Einschränkung.** Die Datenquellen sind bis auf Mead erreichbar; die Befunde sind dokumentiert.

Vor bzw. in Phase 1 zu klären:
1. **RY-Normalwert** (welche Jahre / Trendbereinigung) – Entscheidung des Projektinhabers.
2. Kleine effektive Stichprobe (≈ 11 Standort-Jahre). Wird in der Doku als Grenze genannt; Mead hat hohe Priorität.
3. Behandlung des KBS-Bruchs 2014 (Osthälfte) und der BARC-Einheitenfehler.
