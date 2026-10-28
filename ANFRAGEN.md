# Anfragen, die der Projektinhaber selbst stellen muss

Konten, Formulare, Lizenzzustimmungen und E-Mails erledigt der Projektinhaber selbst (AGENTS.md §8). Die Texte unten sind Entwürfe – vor dem Absenden lesen, anpassen, `[Name]` ersetzen. Jede erhaltene Zusage bzw. jeden Datensatz in `DATA_SOURCES.md` und `SUPPORT.md` eintragen.

| # | Was | An wen / wo | Wozu im Plan | Dringlichkeit | Status |
|---|---|---|---|---|---|
| 1 | **YieldSAT-Zugang** | Formular auf https://yieldsat.github.io/ | Trainingsdaten (~300 Maisfelder mit Mähdrescher-Karten) | hoch | offen |
| 2 | **Erlaubnis KBS-Daten** | Kellogg Biological Station LTER, Kontakt laut https://lter.kbs.msu.edu/data/terms-of-use/ | Veröffentlichung von Ergebnissen aus KBS-Daten | hoch | offen |
| 3 | **AmeriFlux-Konto + Mead-Erträge** | Konto auf https://ameriflux.lbl.gov; bei fehlenden Erträgen PI Andy Suyker (UNL) über die Seite https://ameriflux.lbl.gov/sites/siteinfo/US-Ne1 | Trainingsdaten (3 Felder × ~20 Jahre) | mittel | offen |
| 4 | **Versuchsstandorte Hatzendorf** | Versuchsstation für Pflanzenbau Hatzendorf, versuchlwschulen@stmk.gv.at (laut Versuchsbericht 2025) | Österreich-Test V2 (lokale Erträge) | mittel | beantwortet 2026-10-28: Excel-Reihen Wagna/Kalsdorf + Koordinaten; Rückfragen offen (Ursache Wagna 2025, Strukturbruch Wagna ab 2021, Lage der Versuchsfläche je Jahr, Feldpläne früherer Jahre) |
| 5 | **Feld-Erträge Landwirt:innen (V3)** | Landwirt:innen, LK Steiermark, Maschinenring | Österreich-Test V3 (bester Test) | mittel, läuft parallel | offen |
| 6 | **Bodenklimazahl** (optional) | Amt der Stmk. Landesregierung, Abteilung 17, Referat Statistik und Geoinformation (Kontakt über https://www.landesentwicklung.steiermark.at); ggf. BEV | Österreich-Test: Plausibilitätsprüfung Boden | niedrig | offen |
| 7 | **One Acre Fund: ungerundete Koordinaten + Feldgröße** | Autor:innen Juan Aramburu-Merlos / Patricio Grassini (University of Nebraska–Lincoln, Kontakt laut Artikel PMC11130130) bzw. One Acre Fund (Zenodo 10.5281/zenodo.11115815) | Satellitenkurven für One-Acre-Fund-Felder (bis dahin nur Tabellenanalyse, DECISIONS 2026-10-15) | mittel | offen |
| 8 | **Hagelversicherung: Schadensdaten Österreich** (Feinjustierung F0.2) | Österreichische Hagelversicherung, Kontakt über https://www.hagel.at (Ansprechperson vorher auf der Seite suchen) | nur Österreich-Test nach dem Freeze; Datei **ungeöffnet** unter `data/raw/hagel_at/` ablegen, nicht an Claude geben. Gewünschte Spalten: Schadendatum, Schlag/Koordinate oder Gemeinde, Kultur, Schadenshöhe %, Ursache, Versicherungsjahr; ohne Namen | mittel | offen |
| 9 | **YIPEEO: Erträge CZ/SK auf Feldebene** | Emanuel Büechi, TU Wien (emanuel.bueechi@geo.tuwien.ac.at laut YIPEEO-Deliverable D4.2) | Praxisfelder statt Versuchsparzellen für Ziel A (gegen den KBS-T4-Effekt); 411 Körnermais-Feld-Jahre 2017–2022 | **hoch** | offen |
| 10 | **DWFI: Mais-Ertragskarten MN/IA/NE** | Zenodo-Anfrageformular https://zenodo.org/records/15367430 | Ertragskarten an drei weiteren Standorten: prüft, ob die Karte innerhalb des Feldes (Hauptergebnis) auch außerhalb von BARC hält | **hoch** | offen |
| 11 | **SwissYield Witzwil (ETH)** | Gregor Perich, ETH Zürich (gregor.perich@usys.ethz.ch laut Codex-Recherche) | Mähdrescher-Karten 2017–2021 (Weizen, Gerste, Triticale): Robustheit der Feldkarte über Kulturen (Nebeneffekt) | mittel | offen |
| 12 | **Booßen Roggenkarte (ZALF)** | Pablo Rosso, ZALF (pablo.rosso@zalf.de laut Codex-Recherche) | 1 Feld-Jahr (70 ha, Roggen 2021): zusätzlicher Standort für die Feldkarte | niedrig | offen |

**Ohne Anfrage** (lädt der Agent selbst): One Acre Fund (Zenodo, CC BY 4.0), SSURGO (Soil Data Access), Versuchsberichte Hatzendorf und LK-OÖ-Praxisversuche (öffentliche PDFs).

---

## 1. YieldSAT – Formular

Im Formular als Verwendungszweck z. B.:

> I am a high-school student in Austria preparing a project for the Austrian National AI Competition for students (BWKI Österreich). I would like to use the YieldSAT corn fields (Argentina, Brazil) to train a model that relates Sentinel-2 season curves, weather and soil to measured field yield, and then test it – without retraining – on maize fields in Styria, Austria. The data will only be used for this non-commercial project, raw data will not be redistributed, and YieldSAT will be cited. Could you also tell me under which license results derived from the data may be published?

Vorher die Nutzungsbedingungen im Formular selbst lesen.

## 2. Kellogg Biological Station (KBS LTER)

**Betreff:** Permission to use KBS LTER yield data in a student research project

> Dear KBS LTER team,
>
> I am a high-school student in Austria working on a project for the Austrian National AI Competition (BWKI Österreich). The project learns how satellite time series, weather and soil relate to measured maize yield and then tests the model on maize fields in Austria.
>
> I would like to use the following KBS LTER data: Agronomic Yields (data table 51), Precision Ag Yield Monitoring (tables 185, 828) and MCSE Scale-up (tables 145, 163, 254). Following your terms of use, I am asking for written permission to use these data and to publish results derived from them (figures, statistics, model performance) in the competition report, video and a code repository. Raw data will not be redistributed, and KBS LTER will be acknowledged as requested (NSF DEB 2224712).
>
> Thank you very much for considering my request.
>
> Best regards,
> [Name]

## 3. Mead (AmeriFlux) – nur falls die BADM-Dateien keine Erträge enthalten

**Betreff:** Annual grain yields for US-Ne1, US-Ne2, US-Ne3 – student project

> Dear Dr. Suyker,
>
> I am a high-school student in Austria preparing a project for the Austrian National AI Competition. I am studying how satellite time series and weather relate to measured maize yield on fields with many years of data. The Mead sites would be very valuable for this.
>
> Could you tell me whether annual grain yields (and crop per year) for US-Ne1, US-Ne2 and US-Ne3 are available, and if so, under which conditions I could use them? I would cite the sites and the AmeriFlux data policy, and I would not redistribute raw data.
>
> Thank you very much and best regards,
> [Name]

## 4. Versuchsstation Hatzendorf

**Betreff:** Anfrage Standortdaten Körnermais-Versuche für ein Schülerprojekt (Bundeswettbewerb KI)

> Sehr geehrtes Team der Versuchsstation für Pflanzenbau Hatzendorf,
>
> ich bin [Schüler/Schülerin] und nehme mit einem Projekt am Bundeswettbewerb Künstliche Intelligenz Österreich teil. Ich entwickle ein Modell, das aus Satellitendaten, Wetter und Boden früh in der Saison erkennt, ob ein Maisfeld weniger Ertrag bringen wird. Das Modell wird an ausländischen Feldern trainiert und soll dann in der Steiermark überprüft werden.
>
> Für diese Überprüfung möchte ich die Körnermais-Ergebnisse aus Ihren veröffentlichten Versuchsberichten verwenden. Dazu zwei Fragen:
> 1. Könnten Sie mir für die Körnermais-Versuche (z. B. Wagna, Kalsdorf bei Ilz und weitere Standorte) die **ungefähre Lage der Versuchsflächen** (Gemeinde und Koordinate oder Grundstücksnummer, auf etwa 1 km genau reicht) nennen?
> 2. Gibt es die **Standortmittel der Erträge je Jahr** (mit Feuchtebasis, Aussaat- und Erntedatum) auch als Tabelle (z. B. Excel)? Sonst übertrage ich sie selbst aus den Berichten.
>
> Die Daten werden nur für dieses nicht-kommerzielle Projekt verwendet und als Quelle genannt; Betriebsdaten werden nicht veröffentlicht.
>
> Vielen Dank und freundliche Grüße
> [Name]

## 5. Feld-Erträge von Landwirt:innen (V3)

Kurzer Text für Gespräch, Kammer oder Maschinenring:

> Ich suche für ein Schülerprojekt (Bundeswettbewerb KI) Körnermais-Erträge einzelner Felder in der Steiermark ab 2018 – als Ertragskarte vom Mähdrescher oder als Wiegeschein + Feldlage. Schon 20–50 Feld-Jahre helfen sehr. Die Daten werden anonymisiert, nie weitergegeben und nur mit Ihrer Zustimmung verwendet. Sie dienen nur dazu zu prüfen, ob mein Modell Ertragsverluste richtig vorhersagt.

## 6. Bodenklimazahl (optional)

**Betreff:** Anfrage Bodenschätzungsdaten (Bodenklimazahl) Steiermark für ein Schülerprojekt

> Sehr geehrte Damen und Herren,
>
> für ein Projekt beim Bundeswettbewerb Künstliche Intelligenz Österreich prüfe ich, ob ein Modell zur Früherkennung von Ertragsverlusten im Maisanbau plausible Ergebnisse liefert. Dafür würde ich gerne die **Bodenklimazahl bzw. Ertragsmesszahlen der Finanzbodenschätzung** für die Ackerflächen der Steiermark verwenden (als Flächen-Datensatz, z. B. Shapefile/GeoPackage, oder als WMS/WFS-Dienst).
>
> Liegen diese Daten bei Ihnen vor, und unter welchen Bedingungen könnte ich sie für ein nicht-kommerzielles Schülerprojekt nutzen? Falls nicht Sie zuständig sind, wäre ich für einen Hinweis auf die richtige Stelle dankbar.
>
> Freundliche Grüße
> [Name]

## 7. One Acre Fund – Koordinaten und Feldgröße

**Betreff:** Request: unrounded field coordinates and field size for the One Acre Fund maize dataset (student project)

> Dear Dr. Aramburu-Merlos, dear Prof. Grassini,
>
> I am a high-school student in Austria preparing a project for the Austrian National AI Competition for students (BWKI Österreich). I am using your dataset "Maize management and yield data from One Acre Fund 2016–2022" (Zenodo 10.5281/zenodo.11115815) to study how weather, soil, management and – if possible – Sentinel-2 time series relate to measured maize yield.
>
> In the public file the coordinates are rounded to 0.001° and the field size is not included. For small fields this means that a satellite pixel window around the published point often lies outside the field. Would it be possible to receive, for the fields with farm-level GPS position only,
> 1. the unrounded coordinates (or coordinates rounded to ~10 m), and
> 2. the reported field size?
>
> The data would only be used for this non-commercial student project, never redistributed, and only aggregated results would be shown. If sharing is not possible, a flag "field size ≥ 0.5 ha" would already help a lot.
>
> Thank you very much for publishing this dataset and for considering my request.
>
> Best regards,
> [Name]

---

## Versandfertig ab 2026-10-16 (Hauptergebnis und Feinjustierung)

**Reihenfolge:** zuerst 9 YIPEEO und 10 DWFI (hoch), dann 8 Hagel, danach 11 und 12. Vor dem Senden die Platzhalter `[…]` ersetzen und die E-Mail-Adresse auf der Seite der Institution prüfen; Adressen aus Recherchen können veraltet sein. Nach dem Senden hier das Datum eintragen und Antworten in `DATA_SOURCES.md` vermerken. Erhaltene Daten **nie** ins Repository legen (AGENTS §4.5).

## 8. Österreichische Hagelversicherung – Schadensdaten (nur für den Österreich-Test)

**Wichtig für die Österreich-Regel:** Die Datei nach Eingang **ungeöffnet** unter `data/raw/hagel_at/` ablegen und nicht an Claude geben, bis das Testprotokoll committet und freigegeben ist. Sie dient nur dem Test, nie dem Training oder dem Einstellen von Schwellen.

**Betreff:** Anfrage anonymisierter Schadensdaten Körnermais für ein Schülerforschungsprojekt (BWKI Österreich)

> Sehr geehrte Damen und Herren,
>
> ich heiße [Name] und besuche die [Klasse, Schule, Ort]. Für den Bundeswettbewerb Künstliche Intelligenz Österreich (BWKI) arbeite ich am Projekt „CropTransfer AT“. Ein Verfahren erkennt aus Satellitenbildern (Sentinel-2), welche Maisfelder im Sommer auffällig schwach wachsen und wo innerhalb eines Feldes Ertrag fehlt. Entwickelt wird es ausschließlich mit Daten aus den USA; danach wird es unverändert in Österreich geprüft. Für diese Prüfung bräuchte ich unabhängige Angaben zu tatsächlichen Schäden.
>
> Darf ich Sie fragen, ob Sie mir für die nicht-kommerzielle Forschung **anonymisierte** Schadensmeldungen für Körnermais in der Steiermark (gerne auch Niederösterreich, Burgenland und Oberösterreich) aus den Jahren 2018–2025 zur Verfügung stellen könnten? Hilfreich wären je Schadensfall:
> - Schadensdatum und Schadensursache (z. B. Hagel, Sturm, Dürre, Überschwemmung),
> - Schadensausmaß in Prozent,
> - Lage: Schlag (z. B. INVEKOS-Feldstück-Nummer) oder Koordinate; falls das nicht möglich ist, Katastralgemeinde oder Gemeinde,
> - Kultur und Versicherungsjahr,
> - wenn möglich auch Felder **ohne** Schaden in denselben Gemeinden (nur Lage und Jahr), damit sich Treffer und Fehlalarme zählen lassen.
>
> Namen oder Betriebsdaten brauche ich nicht. Die Daten werden nur innerhalb des Projekts verwendet, nicht weitergegeben und nicht veröffentlicht. Im Wettbewerbsbeitrag erscheinen nur zusammengefasste Ergebnisse (z. B. „x % der Hagelflächen wurden erkannt“) ohne Einzelfälle. Ihre Institution nenne ich gerne in der von Ihnen gewünschten Form als Datenquelle. Eine Nutzungsvereinbarung unterschreiben ich und meine betreuende Lehrkraft gerne.
>
> Vielen Dank für Ihre Zeit.
>
> Mit freundlichen Grüßen
> [Name, Schule, E-Mail, betreuende Lehrkraft]

## 9. YIPEEO – Erträge Tschechien/Slowakei auf Feldebene

**An:** Emanuel Büechi, TU Wien (laut YIPEEO-Deliverable D4.2; Projektleitung Wouter Dorigo). **Betreff:** Zugang zu den YIPEEO-Felderträgen (CZ/SK) für ein Schülerforschungsprojekt (BWKI Österreich)

> Sehr geehrter Herr Büechi,
>
> ich heiße [Name] und besuche die [Klasse, Schule, Ort]. Für den Bundeswettbewerb Künstliche Intelligenz Österreich (BWKI) arbeite ich am Projekt „CropTransfer AT“. Aus Sentinel-2-Zeitreihen soll erkannt werden, welche Maisfelder in einem Jahr auffällig schwach sind. Trainiert wird außerhalb Österreichs; danach wird das Verfahren unverändert in der Steiermark getestet.
>
> Bisher habe ich nur US-Versuchsparzellen mit gemessenem Ertrag. Dabei zeigt sich, dass mein Verfahren vor allem Bewirtschaftungsunterschiede zwischen den Versuchsvarianten erkennt (z. B. späte Bio-Saat), nicht den Stress auf Praxisfeldern. Die YIPEEO-Felder aus Südmähren wären dafür ideal: echte Praxisfelder in Maisgröße, nahe an Österreich und aus den Sentinel-2-Jahren.
>
> In der öffentlichen Sammlung `pub_yipeeo_yield_fl` sind die Erträge für Tschechien und die Slowakei leer; sie liegen in `prv_yipeeo_yield_field`. Wäre es möglich, mir für die nicht-kommerzielle Forschung Zugang zu diesen Erträgen zu geben, zumindest für Körnermais (gerne auch Silomais) 2017–2022? Dazu hätte ich drei kurze Fragen:
> 1. Unter welcher Lizenz darf ich die Daten nutzen? DataCite nennt „proprietary“, die EODC-Collection „public“.
> 2. Auf welche Kornfeuchte beziehen sich die t/ha-Werte?
> 3. Lassen sich Felder über die Jahre zuordnen (Feld-ID), oder gibt es Saat- und Erntedaten?
>
> Die Daten werden nicht weitergegeben und nicht veröffentlicht; im Beitrag erscheinen nur abgeleitete Ergebnisse. YIPEEO und die beteiligten Institutionen zitiere ich in der gewünschten Form. Eine Nutzungsvereinbarung unterschreibe ich gerne.
>
> Vielen Dank und freundliche Grüße
> [Name, Schule, E-Mail, betreuende Lehrkraft]

## 10. DWFI – Mais-Ertragskarten (Zenodo-Anfrageformular)

**Wo:** „Request access“ auf https://zenodo.org/records/15367430. Das Formular verlangt eine Begründung und die Zustimmung zu den Bedingungen (Vertraulichkeit, Danksagung, keine Veröffentlichung ohne schriftliche Zustimmung). Lesen Sie die Bedingungen selbst und stimmen Sie nur zu, wenn sie für Sie passen.

**Begründung (Formularfeld):**

> I am a secondary-school student in Austria working on "CropTransfer AT" for the Austrian national AI competition for students (BWKI Österreich). The project shows from Sentinel-2 imagery where yield is missing inside maize fields. At one site (USDA BARC, Maryland, 41 field-years), mid-summer NDVI ranks within-field yield well (median Spearman 0.68). I would like to use the DWFI yield maps 2021–2024 (Morris MN, Williams IA, Mead NE) only as independent held-out validation, to test whether this holds at other sites; no model will be trained on them. I agree to keep the data confidential, to acknowledge DWFI and ARPA-E (DE-AR0001226), and not to publish or share the data or maps without DWFI's written consent. Only aggregated statistics would appear in the competition entry, and only with your consent. The crop per field and year, the yield unit and the moisture basis would be very helpful.

## 11. SwissYield Witzwil (ETH Zürich)

**An:** Gregor Perich, ETH Zürich (Adresse auf der ETH-Seite prüfen). **Betreff:** Use of the Witzwil yield maps in a student research project (BWKI Österreich)

> Dear Mr Perich,
>
> I am a secondary-school student in Austria working on "CropTransfer AT" for the Austrian national AI competition for students (BWKI Österreich). The project shows from Sentinel-2 imagery where yield is missing inside fields; at a US maize site, mid-summer NDVI ranks within-field yield well (median Spearman 0.68). I would like to test whether this also holds for other crops and in a Central European climate, and your Witzwil combine yield maps 2017–2021 would be an ideal test.
>
> Could you tell me whether I may use the SwissYield/Witzwil yield maps (ETH Research Collection) for this non-commercial project, and how I can access them? It would also help to know the field boundaries, the yield unit and moisture basis, and the crop per field and year. The data would be used only as held-out validation and would not be redistributed; only aggregated results would be shown. I will cite your dataset and paper as you prefer.
>
> Thank you very much, and best regards,
> [Name, school, e-mail, supervising teacher]

## 12. Booßen Roggenkarte (ZALF)

**An:** Pablo Rosso, ZALF (Adresse auf der ZALF-Seite prüfen). **Betreff:** Gemessene Ertragskarte Booßen 2021 für ein Schülerforschungsprojekt (BWKI Österreich)

> Sehr geehrter Herr Rosso,
>
> ich heiße [Name] und besuche die [Klasse, Schule, Ort]. Für den Bundeswettbewerb Künstliche Intelligenz Österreich (BWKI) prüfe ich, wie gut Sentinel-2 innerhalb eines Feldes zeigt, wo Ertrag fehlt; an einem US-Maisstandort gelingt das gut (Median-Spearman 0,68). In Ihrem Artikel (Precision Agriculture 2025, doi 10.1007/s11119-025-10274-w) beschreiben Sie eine gemessene Mähdrescherkarte des 70-ha-Roggenfeldes bei Booßen aus 2021.
>
> Dürfte ich die **gemessenen** Ertragspunkte bzw. das Raster 2021 mit Feldgrenze für mein nicht-kommerzielles Projekt nutzen, ausschließlich als unabhängige Prüfung? Hilfreich wären Einheit, Feuchtebasis und Angaben zur Kalibrierung. Die Daten werden nicht weitergegeben und nicht veröffentlicht; ich zitiere Ihren Artikel und das ZALF in der gewünschten Form.
>
> Vielen Dank und freundliche Grüße
> [Name, Schule, E-Mail, betreuende Lehrkraft]
