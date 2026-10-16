# Anfragen, die der Projektinhaber selbst stellen muss

Konten, Formulare, Lizenzzustimmungen und E-Mails erledigt der Projektinhaber selbst (AGENTS.md §8). Die Texte unten sind Entwürfe – vor dem Absenden lesen, anpassen, `[Name]` ersetzen. Jede erhaltene Zusage bzw. jeden Datensatz in `DATA_SOURCES.md` und `SUPPORT.md` eintragen.

| # | Was | An wen / wo | Wozu im Plan | Dringlichkeit | Status |
|---|---|---|---|---|---|
| 1 | **YieldSAT-Zugang** | Formular auf https://yieldsat.github.io/ | Trainingsdaten (~300 Maisfelder mit Mähdrescher-Karten) | hoch | offen |
| 2 | **Erlaubnis KBS-Daten** | Kellogg Biological Station LTER, Kontakt laut https://lter.kbs.msu.edu/data/terms-of-use/ | Veröffentlichung von Ergebnissen aus KBS-Daten | hoch | offen |
| 3 | **AmeriFlux-Konto + Mead-Erträge** | Konto auf https://ameriflux.lbl.gov; bei fehlenden Erträgen PI Andy Suyker (UNL) über die Seite https://ameriflux.lbl.gov/sites/siteinfo/US-Ne1 | Trainingsdaten (3 Felder × ~20 Jahre) | mittel | offen |
| 4 | **Versuchsstandorte Hatzendorf** | Versuchsstation für Pflanzenbau Hatzendorf, versuchlwschulen@stmk.gv.at (laut Versuchsbericht 2025) | Österreich-Test V2 (lokale Erträge) | mittel | offen |
| 5 | **Feld-Erträge Landwirt:innen (V3)** | Landwirt:innen, LK Steiermark, Maschinenring | Österreich-Test V3 (bester Test) | mittel, läuft parallel | offen |
| 6 | **Bodenklimazahl** (optional) | Amt der Stmk. Landesregierung, Abteilung 17, Referat Statistik und Geoinformation (Kontakt über https://www.landesentwicklung.steiermark.at); ggf. BEV | Österreich-Test: Plausibilitätsprüfung Boden | niedrig | offen |
| 7 | **One Acre Fund: ungerundete Koordinaten + Feldgröße** | Autor:innen Juan Aramburu-Merlos / Patricio Grassini (University of Nebraska–Lincoln, Kontakt laut Artikel PMC11130130) bzw. One Acre Fund (Zenodo 10.5281/zenodo.11115815) | Satellitenkurven für One-Acre-Fund-Felder (bis dahin nur Tabellenanalyse, DECISIONS 2026-10-15) | mittel | offen |
| 8 | **Hagelversicherung: Schadensdaten Österreich** (Feinjustierung F0.2) | Österreichische Hagelversicherung (Kontakt durch den Projektinhaber) | nur Österreich-Test nach dem Freeze; Datei **ungeöffnet** unter `data/raw/hagel_at/` ablegen, nicht an Claude geben. Gewünschte Spalten: Schadendatum, Schlag/Koordinate oder Gemeinde, Kultur, Schadenshöhe %, Ursache, Versicherungsjahr; ohne Namen | mittel | offen |
| 9 | **Feldkarten YIPEEO, SwissYield, Booßen** (Feinjustierung F0.3) | Texte und Reihenfolge in `reports/plan_mehrkultur.md` §8 bzw. `reports/data_search.md` | mehr unabhängige Standort-Jahre (Option b nach Gate H2) | hoch | offen |

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
