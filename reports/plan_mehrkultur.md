# Plan: Mehr-Kulturen-Training (Mais, Getreide, Soja) – Schritt für Schritt

Stand 2026-10-16. Grundlage: unsere Recherche (`reports/data_search.md`, 118 Quellen) und der Codex-Katalog (`reports/extern/codex_2026-10-16/Ertragsdaten_Katalog.csv`, 39 Quellen mit eigener Zählung). Dieser Plan ersetzt `PLAN.md` nicht. Er beschreibt, wie das Modell zusätzlich auf Weizen, Gerste, Raps, Soja und weiteren Kulturen trainiert wird und wie wir prüfen, ob das Mais-Ergebnis dadurch besser wird.

Status der Vorschläge: Alle Festlegungen in Abschnitt 4 sind **Vorschläge**. Sie gelten erst, wenn der Projektinhaber sie in Schritt W0.1 bestätigt. Phase 4 hat schon drei Runden verbraucht (`reports/phase4_stark_genug.md`); jede weitere Runde braucht laut DECISIONS.md eine neue Entscheidung.

---

## 0. Kurzfassung

1. **Ziel:** Das Modell lernt aus vielen Kulturen, wie Wetter, Satellitenkurve und Boden mit dem relativen Ertrag zusammenhängen. Getestet wird, ob dieses Wissen auf Mais und später auf Österreich übertragbar ist.
2. **Engpass bleibt die Zahl unabhängiger Wetter-Jahre,** nicht die Zahl der Felder. Phase 4 ist an 8–11 solchen Standort-Jahren gescheitert. Deshalb zählt der Plan ab jetzt Wetterzellen-Jahre (Abschnitt 4, D2).
3. **Offen und ohne Anfrage ladbar** sind nach unserer Prüfung etwa 110 gezählte Mais-Standort-Jahre (fast nur Genomes to Fields), etwa 460 gezählte Winterweizen-Standort-Jahre in Europa (INVITE, BRIWECS, Grignon) und 266 Erbsen-Jahre in Frankreich. Fast alles sind Versuchsparzellen-Mittel, keine Felder ab 1 ha.
4. **Soja ist dünn:** nur rund 30–40 offene Standort-Jahre, fast alle in den USA. Mehr gibt es nur auf Anfrage (Minnesota, Wisconsin).
5. **Felder ab 1 ha mit Umriss** sind offen kaum vorhanden. Die vielversprechendste Quelle (YIPEEO) hat die tschechischen Erträge nur in einer geschützten Sammlung. Sie muss angefragt werden.
6. **Vorgehen in zwei Spuren:** Spur A trainiert sofort auf den offenen Versuchs-Standortmitteln kulturübergreifend. Spur B nimmt Feldkarten (YIPEEO, SwissYield, Booßen) dazu, sobald sie freigegeben sind. Anfragen laufen parallel und blockieren nichts.
7. **Der Plan hat 6 Etappen, 25 Schritte und 4 Gates.** Ein Gate sagt vorab, wann weitergemacht wird und wann nicht. Österreich bleibt bis zum Freeze unberührt.
8. **Vom Projektinhaber gebraucht:** drei Entscheidungen (W0.1), acht Anfragen (W0.2) und einmal die Freischaltung des CyVerse-Zugangs im Browser (W0.3).

---

## 1. Was der Abgleich der beiden Kataloge ändert

| Punkt | Unser Bericht (vorher) | Codex-Katalog | Ergebnis nach Nachprüfung |
|---|---|---|---|
| YIPEEO CZ/SK | 1 954 Feld-Jahre mit Ertrag, ohne Login | nicht gefunden | **Nur 119 Feld-Jahre (NL 86, UA 33) haben öffentlich einen Ertrag.** Bei den 1 835 CZ/SK-Einträgen ist `yield` leer. Die Erträge liegen in `prv_yipeeo_yield_field` („access only for users belonging to YIPEEO"). Anfrage nötig. |
| Nordische Gerste | Rohmittel, Bewertung 4 | als bereinigt ausgeschlossen | **Codex hat recht.** DK/SE/FI liefern BLUPs, Island OLS-bereinigt, Norwegen teils BLUP (Sci. Data 2026). Zusatzquelle, Stufe S4, Bewertung 3. |
| Genomes to Fields | 250–280 Standort-Jahre (Schätzung) | 103 gezählt aus `PHENO.csv` | **103 gilt.** Zählung aus Datei schlägt Schätzung. |
| SwissYield Witzwil | fehlte | 5 Jahre, Ø 12,8 ha, 54 Mähdrescher-Karten | Neu, wertvoll (Feldmaßstab, Schweiz). Daten bei ETH, Zugang über Autor Perich. |
| Westerfeld Bernburg (BonaRes) | fehlte | Mais, WW, WG, Raps, ca. 11 Jahre | Neu. DataCite bestätigt CC BY 4.0, Hauptparzellen 1,2 ha, Ernte auf 6 × 12 m. |
| NVT Australien (veröffentlichte Kopie) | nur Anfrage-Weg | 1 807 Zellen-Jahre, Weizen 693 | Neu. figshare 16610449, CC BY 4.0, 423 MB. GRDC hat der Veröffentlichung widersprochen, die Lizenz blieb. Südhalbkugel. |
| Französische Erbsen | „Pea_dataset hunderte" | 266 Standort-Jahre gezählt | Gleicher Datensatz (10.57745/FW78RE). Gezählte Zahl gilt. |
| European Grain Legume Dataset | fehlte | 47 Soja-Jahre | **Koordinaten nur auf 2 Dezimalen (~1 km).** Für Pixel-Training ungeeignet, nur als Wetterzellen-Label (S3). |
| IWIN (CIMMYT-Weizen) | fehlte | 280 Stations-Erntejahre | Neu. Koordinaten nur in Bogenminuten, CIMMYT-Sonderbedingungen. Optional. |
| US-Landessortenversuche (MN, WI, KS, OH, KY, ON) | fehlte | benannte Stationen | Neu, alle nur auf Anfrage für Modellnutzung. Minnesota hat 10 GPS-Orte pro Jahr. |
| Nordic Field Trial System (DK) | Scraping, Bewertung 4 | nicht im Katalog | Bleibt: GPS auf 14 Stellen je Versuch, Roh-Erträge je Prüfglied, Nutzung nur nach SEGES-Regeln. |
| Zählweise | Feld-Jahre und Standort-Jahre | Ort × Erntejahr, gleiche Wetterzellen zusammengeführt | **Codex-Zählung gilt** (Abschnitt 4, D2). |

Zahlen beider Kataloge sind Schätzungen, außer wo „gezählt" steht. Gezählt heißt: Eine Datei wurde geöffnet und ausgewertet.

---

## 2. Datenpakete und Label-Stufen

**Label-Stufen** (bestimmen, wie ein Datensatz verwendet wird):

| Stufe | Bedeutung | Verwendung |
|---|---|---|
| **S1** | Feld oder Feldkarte ab 1 ha mit Umriss oder Mähdrescher-Punkten | Pixel- und Feld-Training, höchstes Gewicht |
| **S2** | Versuchs-Standortmittel, Koordinate ≤ 100 m, Kleinparzellen | Feld-Training mit 30-m-Umkreis, als verrauscht behandelt |
| **S3** | Station mit Ortsname oder Koordinate gröber als 100 m | nur Wetter- und Bodenmerkmale, nie Satelliten-Pixel |
| **S4** | modellierte oder bereinigte Werte (BLUP) | nur Zusatz, nie als einziges Label |

**Pakete:**

| Paket | Inhalt | Kulturen | Stufe | Zugang | Gezählt / belegt (Standort-Jahre ab 2013) | Verweis |
|---|---|---|---|---|---|---|
| **A1** | INVITE Sortenprüfungen CZ/HU/CH/FR (Zenodo 20786880) | Winterweizen | S2 (CZ/HU/CH, 182), S3 (FR, 246) | offen, Lizenzwiderspruch klären | 428 gezählt | data_search 5.2 |
| **A2** | BRIWECS, 6 deutsche Stationen (figshare 27910269) | Winterweizen | S2 | offen | 28 gezählt | 5.3 |
| **A3** | Genomes to Fields (figshare 22776806, CyVerse) | Körnermais | S2/S3 (Koordinaten teils geschätzt) | offen, CyVerse mit CAPTCHA | 103 gezählt (2014–2021) | 5.6, Codex N01 |
| **A4** | Westerfeld Bernburg (BonaRes `10.20387/bonares-w669-gdsd`) | Mais, WW, WG, Raps | S2 | offen, Portal blockiert, API geht | ca. 11 je Kultur (belegt) | Codex E06 |
| **A5** | Rothamsted e-RA: Broadbalk, Woburn | WW, Hafer, Silomais | S2, ein Wetterstandort | offen, Formular | ca. 31 (belegt) | 5.12, Codex E01–E04 |
| **A6** | USDA Iowa Stover, Brookings, Bushland, UGA | Mais, Soja, Weizen, Hafer | S2 (Bushland 4,4-ha-Felder: S1) | offen | Iowa 8, Brookings ca. 8, Bushland 6, UGA ca. 36–48 (belegt) | 5.8, Codex N02 |
| **A7** | Grignon 12-Jahres-System (Recherche Data Gouv 10.57745/5TJJZA) | Mais, WW, Raps, Soja | S2 | offen | 96 Parzellen-Jahre, Mais 6 Standort-Jahre (gezählt) | 5.14 |
| **A8** | SLU Bodenfruchtbarkeit R3-9001 (CC0) | Gerste, WW, Raps, Rübe | S3, bis geokodiert | offen | 79 gezählt | 5.13 |
| **A9** | Französische Erbsen (Recherche Data Gouv 10.57745/FW78RE) | Körnererbse | S2 (0,001°) | offen | 266 gezählt | 5.15, Codex G01 |
| **A10** | NVT-Kopie Australien (figshare 16610449) | Weizen, Gerste, Raps u. a. | S2, Südhalbkugel | offen, GRDC-Vorbehalt | 1 807 Kandidaten-Zellenjahre | 5.17, Codex R05 |
| **A11** | Nordische Sortenversuche (DataverseNO) | Sommergerste | S4 | offen | 772 gezählt | 5.4 |
| **A12** | IWIN CIMMYT | Sommerweizen | S3, optional | offen, Sonderbedingungen | 280 | 5.22, Codex G02–G05 |
| **B1** | Nordic Field Trial System DK/SE/NO (SEGES) | WW, WG, SG, Raps, Silomais u. a. | S2 (GPS je Versuch) | Scraping nach SEGES-Regeln, Anfrage | mehrere hundert Versuche pro Jahr (Schätzung) | 5.5 |
| **B2** | Landessortenversuche DE, ÚKZÚZ CZ, GOSZ HU | Weizen, Mais, Raps | S3 (PDF, Stationsnamen) | offen als PDF, Rohdaten anfragen | DE ca. 1 300, CZ ca. 300, HU ca. 100 (Schätzung) | 5.9, 5.10 |
| **C1** | YIPEEO CZ/SK (geschützte Sammlung) | Mais 411, Silomais 112, WW 315, Gerste 536, Raps 265, Soja 46 (Feld-Jahre) | **S1** | Anfrage TU Wien / CzechGlobe | 19 Wetterzellen-Jahre in 3 Zellen à 0,5° für Mais | 5.1 mit Korrektur |
| **C2** | SwissYield Witzwil (ETH) | WW, WG, Triticale | **S1** (Ø 12,8 ha) | Anfrage G. Perich | 5 Jahre | Codex R01 |
| **C3** | Booßen Roggenkarte (ZALF), DIFM, DWFI, GRDC Hyper Yielding Crops | Roggen, Mais, Soja, Weizen | **S1** | Anfrage | je 1 bis wenige Felder bis Netze | 5.23, Codex R06 |
| **C4** | US-Sortenversuche MN, WI, KS, OH, KY, ON; DRIVES | Soja, Mais, Weizen | S2/S3 | Anfrage (Modellnutzung) | MN 10 Orte/Jahr; DRIVES ca. 150 (Schätzung) | 5.7, Codex N03–N08 |
| **T** | Österreich: Marchfeld, Erosionsparzellen, Hatzendorf, LK OÖ, AGES-Sortenliste, INVEKOS, Statistik Austria | alle | Test | **nicht ansehen bis zum Freeze** | Marchfeld 15, Erosion 15 | PLAN §0 |

---

## 3. Zählung je Kultur (Standort × Erntejahr, ab 2013, außerhalb Österreich)

Gezählt = Datei ausgewertet. Belegt = Beschreibung oder API gelesen, Zahl aus Zeitraum und Standortzahl. Anfrage = erst nach Freigabe. Zahlen sind noch nicht auf Wetterzellen zusammengeführt (Schritt W2.3 macht das).

| Kultur | gezählt | belegt, nicht gezählt | nach Anfrage | davon S1 (Feld ≥ 1 ha) offen / nach Anfrage |
|---|---|---|---|---|
| **Körnermais** | 112 (G2F 103, Iowa +3, Grignon 6) | ca. 50 (Bernburg 11, Bushland 6, Brookings ≤ 8, Dedelow 9, DROPS 8, Dürnast 7) | YIPEEO 411 Feld-Jahre, US-Sortenversuche ca. 9, GOSZ HU ca. 100 (PDF), DRIVES | 6 / 411 |
| **Silomais** | 0 | Broadbalk 5, UGA ca. 20 | YIPEEO 112 | 0 / 112 |
| **Winterweizen (Europa)** | 464 (INVITE 428, BRIWECS 28, Grignon 8) | ca. 110 (Bernburg 11, Broadbalk 10, Woburn 6, SwissYield 5, Dedelow 9, SLU ca. 40, ICOS/TERENO 5, Iowa 6 …) | NFTS > 1 000, LSV DE ca. 1 300, ÚKZÚZ ca. 300, YIPEEO 315 | 0 / 320 |
| **Weizen (Australien)** | 693 (NVT-Kopie) | – | aktuelle NVT-Daten | 0 / unbekannt |
| **Gerste** | 772 S4 (Nordic) + 382 (NVT Australien) | Bernburg 11, SLU ca. 40 | YIPEEO 536, NFTS | 0 / 536 |
| **Raps** | 308 (NVT Australien) | Bernburg 11, Grignon 8, SLU 10 | YIPEEO 265, GOSZ ca. 100 | 0 / 265 |
| **Soja** | 4 (Grignon) | Iowa 8, UGA ca. 20, ZALF Müncheberg 7, Brookings 4, CMREC 3, EGLD 47 (nur S3) | MN, WI, YIPEEO 46 | 3 / 46 |
| **Körnererbse** | 266 (Frankreich) | – | YIPEEO 39 | 0 / 39 |
| **Zuckerrübe** | 27 (YIPEEO NL, öffentlich) | SLU ca. 15, BASIS Lelystad 9 | YIPEEO SK 14 | 27 / 14 |

**Lesehilfe:**
- **Mais** hat offen nur G2F als größeren Block. In Europa gibt es offen kaum Mais-Standort-Jahre, nur Bernburg, Grignon, Dedelow und DROPS. Der Feldmaßstab hängt fast ganz an YIPEEO.
- **Winterweizen in Europa** ist die größte offene, ortsgenaue Quelle für neue Wetter-Jahre in Mitteleuropa: etwa 180 INVITE-Jahre mit Feldkoordinate in CZ/HU/CH plus BRIWECS plus Bernburg.
- **Soja** bleibt klein. Soja-Modelle sind frühestens nach den US-Anfragen sinnvoll. Bis dahin ist Soja nur Testfall im Kultur-Transfer.
- Keine Kultur erreicht offen allein die in Gate G1 verlangten 90 Wetterzellen-Jahre als Feldlabel ab 1 ha. Das Mehr-Kulturen-Training ist deshalb eher ein **Transfer-Experiment mit Versuchs-Standortmitteln** als ein Feld-Training.

---

## 4. Entscheidungen (Vorschläge, vom Projektinhaber in W0.1 zu bestätigen)

| ID | Festlegung (Vorschlag) | Grund | Alternative |
|---|---|---|---|
| **D1** | Zielgröße bleibt **RY** = Ertrag / Mittel der anderen Jahre **desselben Standorts und derselben Kultur** (mindestens 2 andere Jahre). Sekundär **RY_nb** gegen andere Standorte derselben Kultur im selben Jahr (mindestens 10). Absolute Erträge werden nicht gepoolt. | RY entfernt Kultur-, Standort- und Einheitsunterschiede. Feuchte und Einheiten müssen nur **innerhalb** einer Quelle stimmen. | absolute t/ha mit Kultur-Faktor |
| **D2** | **Zähleinheit = ERA5-Land-Zelle (0,1°) × Erntejahr.** Derselbe Ort mit mehreren Kulturen zählt pro Kultur einmal, aber im Gesamtpool ist die Zelle nur einmal unabhängig. | Phase 4 ist an unabhängigen Wetter-Jahren gescheitert. Mehrere Kulturen am selben Ort erzeugen keine neue Witterung. | Zählung nach Ortsnamen (zu optimistisch) |
| **D3** | Label-Stufen S1–S4 wie in Abschnitt 2. S3 nie als Satelliten-Pixel, S4 nie allein. | Verhindert, dass grobe oder modellierte Werte als Messung erscheinen. | alle Stufen gleich |
| **D4** | S2-Punkte: Auswertungsfläche = Kreis 30 m um die Koordinate (S2 10 m, HLS 30 m). Nur Punkte, deren Kurve zu einer Ackerkultur passt (Kurvenprüfung W3.3). Schwellen **vor** dem Ansehen der Kurven festgelegt. | Versuchsparzellen sind kleiner als ein HLS-Pixel; Nachbarflächen verfälschen sonst das Signal. | Polygon aus INVEKOS (nur Österreich) |
| **D5** | **Prognosehorizont h** = Tage vom Stichtag bis zur Ernte. Hauptauswertung h = 30 Tage; zusätzlich h = 60 und 90. Erntedatum aus der Quelle, sonst Kultur-Median. Mais behält seine Kalender-Stichtage (Hauptstichtag 1.9.) als Vergleich. | Winterweizen reift im Juli, Mais im Oktober. Gleiche Kalendertage wären für beide falsch. | feste Kalender-Stichtage pro Kultur |
| **D6** | Neuer Block `crops:` in `config.yaml` mit Kultur, Winter-/Sommerkultur, Saisonfenster, GDD-Basis und Deckel, Kc-Tabelle. Werte aus FAO-56 und Literatur, **vor** den Experimenten festgelegt und in DECISIONS.md belegt. | `features.py` rechnet bisher fest mit Mais (GDD 10/30 °C, Mais-Kc, Saison April–Oktober). | Werte aus den Daten schätzen (Leakage-Risiko) |
| **D7** | Modellfamilie: **M-Kultur** (ein Ridge je Kultur), **M-Pool** (alle Kulturen, Kultur als Faktor und Wechselwirkung), **M-Pool-ohne-Mais** (für den Kultur-Transfer). Flaches LightGBM (Tiefe ≤ 3) nur als Vergleich. | Wenige Zell-Jahre: einfache Modelle, wie in PLAN Abschnitt 2. | tiefe Netze (zu wenig Daten) |
| **D8** | Satellitenmerkmale **kulturrelativ:** Index geteilt durch die Referenzkurve der Kultur (Median der Standort-Jahre mit RY ≥ 0,95, ohne das Testjahr). | gleiches Verfahren wie Phase 3 (DECISIONS 2026-10-16); macht Weizen- und Maiskurven vergleichbar. | rohe Indexwerte |
| **D9** | Validierung: **LOFYO** bleibt Hauptweg. Zusätzlich (a) Blockvalidierung nach 0,5°-Zelle, (b) **Leave-One-Crop-Out**, (c) Leave-One-Dataset-Out. Bootstrap über Wetterzelle-Jahr als Cluster. | Verhindert, dass Nachbarstandorte desselben Wetters Trainings- und Testdaten sind. | zufälliger Split (verboten, PLAN §6) |
| **D10** | **„Stark genug (Mehrkultur)":** (1) Hauptmodell schlägt B0 und B1 bei h = 30 auf Mais **und** auf mindestens der Hälfte der Kulturen mit ≥ 40 Zell-Jahren (Bootstrap-KI der RMSE-Differenz ohne 0). (2) ρ ≥ 0,4 gepoolt und ρ ≥ 0,3 auf Mais. (3) **Kultur-Transfer:** M-Pool-ohne-Mais erreicht auf Mais ρ > 0 mit KI ohne 0. (4) Label-Shuffle fällt auf Baseline. (5) Kulturen mit < 40 Zell-Jahren gelten als „nicht beurteilbar", nie als bestanden. | Gleiche Logik wie Phase 4, erweitert um den Kultur-Transfer. | Kriterien nach den Ergebnissen anpassen (verboten) |
| **D11** | Österreich-Regel bleibt unverändert. Der AT-Test wird **je Kultur** im Freeze-Protokoll vorab festgelegt (W5.2). | PLAN §0, §6 | – |
| **D12** | Rohdaten nie ins Repository. Quellen mit „Confidential", „ND" oder ungeklärter Lizenz nur lokal, in Veröffentlichungen nur aggregierte Ergebnisse. | AGENTS.md 4.5, Lizenzwidersprüche bei INVITE und YIPEEO | – |

**Begründung der Mindestzahl in Gate G1 (90 Zell-Jahre):** Mit der Fisher-Transformation hat ein Spearman-Wert ρ ≈ 0,4 eine untere KI-Grenze von etwa 0,2 erst ab n ≈ 90 unabhängigen Beobachtungen (Rechnung: z(0,4) − z(0,2) ≈ 0,22 und 1,96 / √(n − 3) ≤ 0,22 ergibt n ≈ 82–90). Mit n = 89 hatte Phase 4 ein KI von −0,02 bis 0,68, und das ohne Cluster-Korrektur. Mit weniger Daten lässt sich die Hypothese nicht entscheiden.

---

## 5. Arbeitsplan

Jeder Schritt hat **Wer**, **Was**, **Ergebnis** und **Abnahme**. Aufwand: S = unter ½ Tag, M = 1 Tag, L = 2–3 Tage. „Claude" bedeutet: ein KI-Agent im Repo, der Projektinhaber prüft und kann jede Zeile erklären (AGENTS.md §1). Jede Abweichung kommt in `DECISIONS.md`, jede Hilfe in `SUPPORT.md`.

### Etappe 0 – Entscheiden und anfragen (Projektinhaber, Tag 0)

| Nr | Wer | Was | Ergebnis | Abnahme |
|---|---|---|---|---|
| **W0.1** | Projektinhaber | D1–D12 durchgehen und je „ja", „ändern" oder „nein" antworten. Besonders D2, D5, D10. | Eintrag in `DECISIONS.md` (trägt Claude ein) | Alle zwölf Zeilen haben eine Antwort. Erst danach starten W2–W4. |
| **W0.2** | Projektinhaber | Acht Anfragen senden, Reihenfolge in Abschnitt 8. Texte stehen in `data_search.md` Abschnitt 4. Jede Anfrage in `ANFRAGEN.md` eintragen (Claude ergänzt auf Zuruf). | gesendete Mails, Datum in `ANFRAGEN.md` | Datum und Empfänger je Anfrage notiert. Ohne Antwort nach 3 Wochen: einmal nachfragen. |
| **W0.3** | Projektinhaber | G2F: Auf `https://dc.cyverse.org` die IP einmal im Browser freischalten (CAPTCHA) und die Releases 2014–2023 herunterladen. Alternativ die figshare-Kopie nutzen. | `data/raw/g2f/` | Dateien 2014–2023 vorhanden. |

### Etappe 1 – Offene Pakete holen und prüfen (Claude)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **W1.1** | Claude | Modul `fetch_open_sets.py` mit einer Funktion je Paket A1–A12. Speichert nach `data/raw/<name>/`, schreibt SHA-256, Größe und Lizenztext in `data/raw/<name>/MANIFEST.json`. Bekannte Quellen: INVITE `https://zenodo.org/api/records/20786880/files/Dataset.zip/content` (Ordner `SiriusQyality/` mit .exe nicht entpacken), BRIWECS `https://ndownloader.figshare.com/files/50832927`, NVT-Kopie `https://ndownloader.figshare.com/files/30742573`, Nordic `https://dataverse.no/api/access/datafile/268105`, Erbsen `https://entrepot.recherche.data.gouv.fr/api/access/datafile/764684` sowie 764683 und 764685. Rothamsted e-RA braucht ein Formular (Projektinhaber, 5 Minuten). | Rohdaten lokal, Manifeste | Jeder Download hat ein Manifest. Ein Test lädt je Paket eine Fixture (< 1 MB). | L |
| **W1.2** | Claude | `DATA_SOURCES.md` um Einträge #16 ff. ergänzen: Quelle, Version, Lizenz, Abrufdatum, Dateien, Neu-Download, Auffälligkeiten. | Dokumentation | Jeder Eintrag aus W1.1 hat einen Text. | M |
| **W1.3** | Claude | Datenkritik je Paket nach AGENTS.md §3: Einheiten, Feuchtebasis, Ausreißer, Duplikate (G2F ↔ Iowa 2014 und 2016–2019, Broadbalk ↔ Woburn, INVITE-Sorten), fehlende Koordinaten, BLUP-Flag. | `reports/data_review/phase1b_mehrkultur.md` mit Entscheidung ✅/⚠️/⛔ je Paket | Jede Zahl aus Code; Entscheidung je Paket. | L |

### Etappe 2 – Einheitliches Schema und Zählung (Claude)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **W2.1** | Claude | `groundtruth_multi.py`: Loader je Paket, Ausgabe `data/processed/gt_site_years.parquet`. Spalten wie `gt_field_years` (dataset, field_id, year, crop, Y_t_ha, area_ha, geometry …) plus **tier** (S1–S4), **label_type** (Feldkarte / Parzellenmittel / BLUP / Stationsmittel), **lat, lon, coord_digits**, **sow_date, harvest_date**, **moisture_basis**, **cell_id** (0,1°). | Parquet | Test prüft Pflichtspalten, Wertebereiche je Kultur, keine Österreich-Zeilen. | L |
| **W2.2** | Claude | RY und RY_nb pro Standort und Kultur (bestehendes `targets.py` erweitern), Anteil „gefährdet" (RY < 0,85) je Kultur. | Spalten im Parquet | Verteilung je Kultur in `phase1b_mehrkultur.md`. | M |
| **W2.3** | Claude | `count_cells.py`: zählt je Kultur und Stufe die **Zellen-Jahre** (D2), zusätzlich Sensitivität mit 0,5°-Zellen. | `reports/data_review/zellen_zaehlung.md` | Tabelle Kultur × Stufe × Zellen-Jahre. **Gate G1.** | S |

### Etappe 3 – Satellit und Merkmale (Claude)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **W3.1** | Claude | `config.yaml` Block `crops:` (D6) und Test, dass Mais dieselben Werte wie bisher ergibt. | Konfiguration | Bestehende Mais-Ergebnisse unverändert (Regressionstest). | M |
| **W3.2** | Claude | GEE-Extraktion (`gee_extract.py`) für S2-Punkte (30-m-Kreis): HLS ab 2013, S2 ab 2017. Winterkulturen mit Saisonfenster Oktober (Vorjahr) bis Juli. Export je Paket und Jahr getrennt (Quoten). | `data/interim/obs/` | Je Paket Anteil Punkte mit ≥ 5 HLS- bzw. ≥ 12 S2-Pixeln und `clear_frac ≥ 0,7`. | L |
| **W3.3** | Claude | Kurvenprüfung (Phase 1.6): beste und schlechteste RY-Jahre desselben Standorts übereinander, je Kultur. Schwelle „Kurve passt zur Kultur" vorab in DECISIONS.md. | Abbildungen, Anteil brauchbarer Kurven | **Gate G2.** | M |
| **W3.4** | Claude | `features.py`: kulturspezifische GDD, Kc, Saisonfenster; Stichtage über Horizont h (D5); kulturrelative Satellitenmerkmale (D8). `test_no_leakage.py` auf alle Kulturen erweitern. | Merkmalstabellen `features_h030.parquet` usw. | Leakage-Test grün für jede Kultur und jeden Horizont. | L |

### Etappe 4 – Experimente (nur Trainingsdaten, nie Österreich)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **W4.1** | Claude | **E1 Mais-Basis neu:** bisheriger Mais-Pool plus neue Mais-Standortmittel (G2F, Bernburg, Grignon, Iowa, Bushland …), Ridge, LOFYO, h = 30. | `results/mehrkultur/E1/` | Kriterien-Datei mit ρ, RMSE, KI. | M |
| **W4.2** | Claude | **E2 je Kultur:** ein Ridge je Kultur mit ≥ 40 Zell-Jahren (voraussichtlich Winterweizen, Mais, Erbse). | `E2/` | wie E1 | M |
| **W4.3** | Claude | **E3 Pool:** M-Pool über alle Kulturen, Kultur als Faktor mit Wechselwirkungen. | `E3/` | wie E1 | M |
| **W4.4** | Claude | **E4 Kultur-Transfer:** M-Pool-ohne-Mais trainieren, auf Mais testen. Zusätzlich: nur Winterweizen → Mais. | `E4/` | ρ mit Cluster-KI | M |
| **W4.5** | Claude | **E5 Kontrollen:** Label-Shuffle (3 Wiederholungen), Koordinaten-Ablation, Adversarial Validation (Datensatz, Kultur), Lauf ohne S3 und ohne S4, Lauf ohne die größte Quelle (Leave-One-Dataset-Out). | `E5/` | Shuffle auf Baseline. Sonst ⛔ und Leakage suchen. | L |
| **W4.6** | Claude | **E6 Feldkarten (nur wenn C1/C2 freigegeben):** Pixel-Ebene, Mehrjahres-Felder, RY je Feld. Zusätzlich Wirkung auf E3/E4. | `E6/` | wie E1 | L |
| **W4.7** | Claude | Bericht und Gate-Auswertung: `python -m croptransfer.phase4_report --mehrkultur` (Erweiterung der bestehenden Tabelle um D10). | `reports/phase4_mehrkultur.md` | **Gate G3:** je Kriterium 1–5 ✓ oder ✗, Kulturen mit < 40 Zell-Jahren als „nicht beurteilbar". | M |

### Etappe 5 – Freeze und Österreich (nur nach Gate G3 ✓)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **W5.1** | Claude | Freeze wie PLAN Phase 4: Modelle, Merkmale, Schwellen, Conformal-Quantile, Kulturliste, SHA-256, Tag `freeze-2`. | `reports/freeze_protocol_mehrkultur.md` | `test_freeze.py` grün. | M |
| **W5.2** | Claude + Projektinhaber | **Österreich-Testprotokoll je Kultur vorab:** Mais (INVEKOS 105, Statistik Austria, Hatzendorf, LK OÖ), Winterweizen (INVEKOS Winterweizen, Statistik Austria, Marchfeld 4 Jahre, Erosionsparzellen 6, AGES-Sortenliste), Soja (INVEKOS Soja, Marchfeld 3, Statistik Austria). Metriken und Erfolgskriterien je Kultur. | im Freeze-Protokoll | Protokoll committet **bevor** eine österreichische Zahl angesehen wird. | M |
| **W5.3** | Claude | Phase 6 und 7 nach PLAN, je Kultur. | `reports/at_test_*.md` | wie PLAN Phase 7 | L |

### Parallelspur R – Regionalmodell für Weizen (optional, unabhängig von den Labels)

| Nr | Wer | Was | Ergebnis | Abnahme | Aufwand |
|---|---|---|---|---|---|
| **WR.1** | Claude | CY-Bench enthält laut Zenodo-Beschreibung auch Weizen (29 Länder); im Repo liegt bisher nur der Ordner `maize`. Weizen herunterladen (Zenodo 10.5281/zenodo.17279151), `regional_cybench.py` auf Kultur parametrieren. | Weizen-Regionalmodell, LOCO ohne AT | `results/cybench_wheat/` | M |
| **WR.2** | Claude | Zero-Shot-Protokoll für Weizen wie bei Mais vorab registrieren (Statistik Austria Winterweizen je Bundesland). | `reports/freeze_protocol_cybench_wheat.md` | Protokoll vor dem Test. | S |

---

## 6. Gates

| Gate | Nach | Bedingung | Wenn ja | Wenn nein |
|---|---|---|---|---|
| **G1** | W2.3 | ≥ 90 Zellen-Jahre in S2 für die Hauptauswertung (gepoolt) **und** ≥ 40 für jede Kultur, die einzeln ausgewiesen wird | Etappe 3 starten | Nur Kulturen mit ≥ 40 modellieren; Anfragen priorisieren; Bericht mit „nicht beurteilbar". |
| **G2** | W3.3 | In mindestens 2 Kulturen mit ≥ 40 Zellen-Jahren zeigt die Kurve in den schlechtesten RY-Jahren einen sichtbaren und im Spearman-Wert positiven Unterschied (K1–K5 gegen RY) | Etappe 4 starten | Betroffene Kultur ausschließen und in der Doku als Grenze nennen (⚠️). Sind es weniger als 2 Kulturen: ⛔ und Projektinhaber informieren. |
| **G3** | W4.7 | Kriterien D10 (1)–(5) | Etappe 5 | Nicht stark genug: **nicht** nach Österreich. Optionen in DECISIONS.md: Feldkarten (C1/C2) abwarten, nur späte Horizonte, Phase 5 als Hauptergebnis. Weitere Runde nur mit neuer Entscheidung. |
| **G4** | W5.2 | Testprotokoll committet und Freeze-Tag gesetzt | Österreich-Daten ansehen | Nichts ansehen. |

Obergrenze: höchstens **eine** Modellrunde in Etappe 4 mit nachträglicher Änderung (nur nach Bericht und Eintrag in DECISIONS.md). Kein Tuning an Testfalten.

---

## 7. Risiken speziell für Mehr-Kulturen

| Risiko | Gegenmaßnahme |
|---|---|
| Sortenversuchs-Mittel sind keine Feldmittel; Sortenmenge wechselt zwischen Jahren und erzeugt Rauschen in RY | Nur Kontrollsorten oder gemeinsame Sorten je Standort verwenden, wo möglich; sonst Standortmittel mit Flag; Lauf mit und ohne (E5) |
| 30-m-Kreis liegt auf Nachbarfläche | Kurvenprüfung W3.3, Mindestpixel, Lauf ohne die schlechtesten 20 % der Kurven als Sensitivität |
| Mehrere Kulturen am selben Ort täuschen unabhängige Witterung vor | Zähleinheit D2; Cluster-Bootstrap; Leave-One-Dataset-Out |
| BLUP- und Bereinigungswerte (Nordic, Teile von IWIN) glätten gerade Extremjahre | Stufe S4, nur als Zusatz, Lauf ohne S4 |
| NVT Australien: andere Jahreszeit, Winterregen-Klima, GRDC-Vorbehalt | Getrennt auswerten, nicht in den Kern-Pool, nur wenn GRDC schriftlich zustimmt oder die CC-BY-Lizenz der Kopie unwidersprochen bleibt |
| INVITE: Lizenz CC BY (Zenodo) gegen „Confidential" im Datei-Kopf | Pierre Martre (INRAE) fragen; bis zur Antwort nur lokal |
| Winterkulturen brauchen Daten ab Oktober des Vorjahres; HLS-Lücken im Winter | Winterfenster mit eigenem `is_observed`-Anteil; Horizonte h = 60/90 bevorzugen; Wetter-Modell ohne Satellit als Vergleich |
| Kulturen verwechselt (Sommer-/Winterweizen, Silo-/Körnermais) | Spalte `crop_variant`; Silomais nie als Körnermais |
| Zu wenig Soja für ein eigenes Modell | Soja nur im Kultur-Transfer als Testfall; eigenes Soja-Modell erst nach C4 |
| Österreich-Regel verletzt, weil Marchfeld und Erosionsparzellen schon offen liegen | Dateien nicht öffnen, nicht in `data/raw` ablegen, bis W5.2 |

---

## 8. Checkliste für den Projektinhaber (Anfragen in dieser Reihenfolge)

Kontaktwege sind aus den beiden Katalogen übernommen. E-Mail-Adressen aus Papers oder Berichten können veraltet sein; vor dem Senden auf der Seite prüfen.

| Prio | Wer | Warum zuerst | Was anfragen | Textvorlage |
|---|---|---|---|---|
| 1 | TU Wien / CzechGlobe (YIPEEO), Kontakt laut D4.2: Emanuel Büechi | größter Feldmaßstab mit Mais, WW, Gerste, Raps, Soja in Südmähren | Zugang zu `prv_yipeeo_yield_field` oder Ertragstabelle CZ/SK; Klärung „proprietary" vs. „public" | `data_search.md` §4, Zusatz YIPEEO |
| 2 | ETH Zürich, Gregor Perich | Mähdrescher-Karten 5 Jahre, Schweiz | Daten Witzwil 2017–2021 und Nutzungserlaubnis | §4 generisch |
| 3 | SEGES Innovation (Landsforsøgene) | GPS-genaue Versuche DK, viele Kulturen | Erlaubnis für Abruf aller Endergebnisse ab 2013 und Modellnutzung | §4, Zusatz SEGES/NFTS |
| 4 | DRIVES (USDA-ARS), Anfrageformular laut Ag-Data-Commons-Record 28654694 | 21 Langzeitversuche, Mais/Soja/Weizen | Datenpaket und Koordinaten | §4, Zusatz DRIVES |
| 5 | Universität Minnesota, Aaron Lorenz | Soja, 10 GPS-Orte pro Jahr | Workbook-Archiv ab 2013, Feuchtebasis, Modellnutzung | Codex-Bericht §4 |
| 6 | ÚKZÚZ, Vladimíra Horáková | Stationen nahe Österreich, Weizen, Mais, Raps | Jahresmittel je Station ab 2013 mit Koordinaten | §4, Zusatz ÚKZÚZ |
| 7 | ZALF, Pablo Rosso | 70-ha-Roggenkarte | Rohkarte 2021 | §4 generisch |
| 8 | Bereits offen aus `ANFRAGEN.md`: KBS, YieldSAT, Mead | Kern-Datensätze | wie dort | `ANFRAGEN.md` |

Zusätzlich offen: INVITE-Lizenz (Pierre Martre, INRAE, bestätigt CC-BY-Nutzung) und Rothamsted-Formular (selbst ausfüllen).

---

## 9. Welche Dateien sich ändern

| Datei | Änderung | Schritt |
|---|---|---|
| `config.yaml` | Block `crops:`, Pfade `data/raw/<paket>` | W3.1 |
| `src/croptransfer/fetch_open_sets.py` (neu) | Downloads Pakete A | W1.1 |
| `src/croptransfer/groundtruth_multi.py` (neu) | Schema `gt_site_years` | W2.1 |
| `src/croptransfer/targets.py` | RY, RY_nb pro Kultur | W2.2 |
| `src/croptransfer/count_cells.py` (neu) | Zellen-Zählung | W2.3 |
| `src/croptransfer/features.py` | kulturspezifische GDD, Kc, Horizont | W3.4 |
| `src/croptransfer/splits.py` | Block- und Kultur-Splits | W4.1 |
| `src/croptransfer/phase4_report.py` | Kriterien D10 | W4.7 |
| `tests/` | Leakage je Kultur, Schema, Mais-Regression | W2.1, W3.1, W3.4 |
| `DATA_SOURCES.md`, `DECISIONS.md`, `SUPPORT.md`, `CHANGELOG.md`, `ANFRAGEN.md` | Einträge | laufend |

---

## 10. Quellen dieses Plans

- Unser Bericht: `reports/data_search.md` (mit Korrekturblock vom 2026-10-16) und Rohnotizen in `research_notes/Offene Ertragsdaten Feldebene/`.
- Codex-Katalog und -Bericht: `reports/extern/codex_2026-10-16/` (Kopie aus `C:\Users\mario\Documents\Codex\2026-10-16\deep-research-app-connector-openai-deep\outputs\`; die JSON-Protokolle bleiben dort).
- Nachprüfungen am 2026-10-16: EODC-API (Collections `pub_yipeeo_yield_fl`, `prv_yipeeo_yield_field`), DataverseNO 10.18710/IZ3EFE samt README, Nordic-Paper (Sci. Data 2026), DataCite-Einträge für BonaRes `10.20387/bonares-w669-gdsd` und ETH `10.3929/ethz-b-000581023`, figshare-API für 16610449 und 23634822.
- Grundlage der Mindeststichprobe: Fisher-Transformation, hier ohne Cluster-Korrektur gerechnet; die tatsächliche KI-Breite berechnet `phase4_report.py` per Cluster-Bootstrap.
