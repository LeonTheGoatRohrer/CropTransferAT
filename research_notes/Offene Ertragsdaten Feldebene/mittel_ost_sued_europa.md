# Offene Ertragsdaten auf Feld-/Standortebene – Mittel-, Ost- und Südeuropa (CZ, SK, HU, PL, SI, HR, RS, RO, BG, UA, Baltikum, IT, ES, PT, GR)

Stand: 2026-10-16. Recherche per Websuche + Öffnen der Links (WebFetch / PDF-Textextraktion). "bestätigt" = Link geöffnet und Daten/Metadaten gesehen; "unbestätigt" = nur über Suchtreffer/Snippets belegt oder Link nicht öffenbar. Keine DOIs erfunden; alle DOIs stammen aus geöffneten Seiten oder Suchtreffern (dann als unbestätigt markiert).

Feldliste pro Datensatz (exakt wie vorgegeben):
Name | Link | Crop(s) | Country/region | Location precision | Area per unit | Years covered (≥2013) | Number of sites/fields | Est. independent site-years ≥2013 | Yield measure, unit, moisture | Extra info | License | Access | Preparation effort | Rating 1–5 | Status

---

## KQ 0 – Pan-regionale Quellen (mehrere Länder, LTE-Netzwerke, Flux, EU-Projekte)

### Takeaway
Der mit Abstand wertvollste Fund ist ein im Juni 2026 auf Zenodo (CC BY 4.0) veröffentlichter ICASA-formatierter Datensatz der amtlichen Weizen-Wertprüfungen (VCU) aus Tschechien, Ungarn, Frankreich und der Schweiz 2003–2018 (ÚKZÚZ und NÉBIH als Datenlieferanten). Daneben existieren nur Metadaten-Kataloge (BonaRes/EJP SOIL) mit Kontaktpersonen für Anfragen; offene Ertragskarten (Mähdrescher) wurden in keinem der Zielländer gefunden.

### Cited Findings (Datensatz-Records)

**D-PAN-1**
- Name: Wheat Registration Trial Data for Czech Republic, Hungary, France, and Switzerland in ICASA Format (2003–2018) – INVITE-Projekt
- Link: https://zenodo.org/records/20786880 (DOI 10.5281/zenodo.20786880) — [Zenodo](https://zenodo.org/records/20786880)
- Crop(s): Winterweizen (amtliche VCU/Wertprüfung)
- Country/region: CZ, HU, FR, CH (CZ und HU relevant; FR/CH von anderen abgedeckt)
- Location precision: ICASA-Format enthält i. d. R. Standortkoordinaten; auf der Zenodo-Seite nicht explizit genannt → vermutlich Stationskoordinaten, zu prüfen in ReadMe.txt
- Area per unit: Parzellenversuche (<1 ha) → „only site mean"
- Years covered: 2003–2018; ≥2013: 2013–2018 (6 Jahre)
- Number of sites/fields: nicht angegeben (ÚKZÚZ betreibt ~25 Weizen-Standorte; NÉBIH ~10–12)
- Est. independent site-years ≥2013: grob 100–200 (CZ+HU), Schätzung aus Netzgröße × 6 Jahre; muss nach Download verifiziert werden
- Yield measure: Kornertrag (ICASA-Standardvariable HWAH o. ä.), Einheit/Feuchtebasis auf der Seite nicht genannt (ÚKZÚZ-Standard: 14 % Feuchte)
- Extra info: Versuchsbeschreibung, Management (Saat/Ernte), Boden, Wetter, Phänologie, Ertrag; Dateien Dataset.zip (49,9 MB) + ReadMe.txt; Kontakt Pierre Martre (INRAE); 19 Creators inkl. ÚKZÚZ (Central Institute for Supervising and Testing in Agriculture) und NÉBIH (National Food Chain Safety Office); zugehörige Publikation DOI 10.1016/j.fcr.2026.110420 („Is source of")
- License: CC BY 4.0
- Access: direkter Download
- Preparation effort: medium (ICASA-Parsing, Standortzuordnung)
- Rating: 5 (für Weizen CZ/HU; einziger wirklich offener, strukturierter Multi-Site-Ertragsdatensatz der Region)
- Status: bestätigt (Zenodo-Seite geöffnet, Metadaten/Lizenz/Dateiliste gesehen; Inhalt der ZIP nicht geprüft)

**D-PAN-2**
- Name: An experimental dataset on yields of pulses across Europe (Antichi et al. 2023, Scientific Data)
- Link: Daten https://doi.org/10.6084/m9.figshare.c.6573760.v1 (Redirect auf springernature.figshare.com → HTTP 403 beim Abruf); Beschreibung https://agrostacwiki.containers.wur.nl/index.php/Legumes_Antichi_et_al_2023 ; Paper DOI 10.1038/s41597-023-02606-0 — [AgroStac-Wiki](https://agrostacwiki.containers.wur.nl/index.php/Legumes_Antichi_et_al_2023)
- Crop(s): Kichererbse, Ackerbohne, Erbse, Linse, Sojabohne
- Country/region: 21 europäische Länder (welche Zielländer enthalten sind, nicht verifiziert)
- Location precision: laut Wiki „records without location info removed" → Koordinaten vorhanden, Genauigkeit unbekannt
- Area per unit: Parzellen → „only site mean"
- Years covered: nicht gesehen (Datensatz 2023 publiziert; Anteil ≥2013 unbekannt)
- Number of sites/fields: 177 Feldexperimente, 5 229 Ertragsbeobachtungen (aus Suchtreffer)
- Est. independent site-years ≥2013: unbekannt
- Yield measure: Kornertrag (Einheit nicht gesehen)
- Extra info: CSV „European Grain Legume Dataset.csv"
- License: nicht gesehen (Springer-Nature-figshare üblich CC BY 4.0, nicht verifiziert)
- Access: direkter Download (figshare) – Abruf hier blockiert (403)
- Preparation effort: low–medium
- Rating: 3 (Soja relevant; nur Parzellen; Länderabdeckung offen)
- Status: unbestätigt (figshare nicht öffenbar; Wiki-Seite geöffnet)

**D-PAN-3**
- Name: BonaRes LTE-Overview / „Metadata of agricultural long-term experiments in Europe" (Donmez et al. 2022, Data in Brief; Grosse et al. 2020)
- Link: https://tools.bonares.de/ltfe (Redirect von lte.bonares.de) ; Paper https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9117531/ ; Datensatz-DOI laut Paper 10.20387/bonares-eff3-0mb4 bzw. 10.20387/bonares-r56g-fgrw — [BonaRes LTE tool](https://tools.bonares.de/ltfe)
- Crop(s): alle (Metadaten zu >570 Dauerversuchen, Ackerland/Grünland)
- Country/region: ~38 Länder, inkl. IOSDV, NLFT (Ungarn), RetiBio 2 (Italien), EJP SOIL, GLTEN
- Location precision: Standortangaben pro LTE (Karte), i. d. R. Koordinaten
- Area per unit: n/a (Metadaten)
- Years covered: Versuche ≥20 Jahre Laufzeit, Status „ongoing/finished"
- Number of sites/fields: >570 LTEs (616 im Paper)
- Est. independent site-years ≥2013: n/a – KEINE Ertragsdaten, nur Metadaten
- Yield measure: keine
- Extra info: Filter nach Land, Landnutzung, Thema (Düngung/Fruchtfolge/Bodenbearbeitung); „Metadata Download"; Kontakt für Ergänzungen: Cenk Dönmez (ZALF)
- License: nicht angegeben (BonaRes-Repository: offen)
- Access: direkt (Metadaten)
- Preparation effort: low (als Adressbuch für Anfragen)
- Rating: 2 (nur Wegweiser, aber bester Einstieg für „on request"-LTEs in CZ/HU/PL/SI/IT/ES)
- Status: bestätigt (Tool-Seite geöffnet)

**D-PAN-4**
- Name: EJP SOIL MTE/LTE-Metadatensatz v1.0.1 (Task 7.3) + EJP-SOIL-Länderseiten „Partner countries with LTEs"
- Link: https://zenodo.org/record/7598122 (DOI 10.5281/zenodo.7598122) ; Länderseiten: https://projects.au.dk/ejpsoil/visiting-scientists-support-access-to-infrastructure/partner-countries-with-ltes (Unterseiten für Estonia, Hungary, Italy, Lithuania, Poland, Spain) — [Zenodo](https://zenodo.org/record/7598122)
- Crop(s): alle
- Country/region: 22 Länder, darunter CZ, HU, PL, SI, SK, IT, ES, PT, EE, LV, LT
- Location precision: pro Versuch Standort/Institution
- Area per unit: n/a
- Years covered: n/a (Metadaten, 240 MTE/LTE)
- Number of sites/fields: 240 Versuche
- Est. independent site-years ≥2013: n/a
- Yield measure: keine Erträge, nur Metadaten (lte-db-v1.0.1.zip, 9,3 MB)
- Extra info: Nationale Koordinatoren/LTE-Eigner namentlich: CZ Ladislav Menšík; HU Tóth Eszter, István Henzsel, Sándor Koós, Balázs Madarász, Mariann Makádi, László Radimszky, Péter Ragályi, Anita Szabó, Melinda Tar, Nikolett Uzinger; PL Jacek Niedźwiecki; SK Jaroslava Sobocka; SI Rok Mihelič; IT Roberto Barbetti, Gianluca Carboni, Mariangela Diacono, Paolo Mulé, Gaio Cesare Pacini, Silvia Baronti, Vincenzo Tabaglio, Domenico Ventrella, Nadia Vignozzi, Laura Zavattaro; ES Jorge Álvaro-Fuentes, José A. Gómez, Carlos García Izquierdo, César Plaza, Inés Santín-Montanyá; PT Nadia Castanheira, Raquel Mano; EE Alar Astover, Karin Kauer, Liina Talgre; LV Janis Vigovskis; LT Virginijus Feiza, Grazina Kadziene, Danute Karcauskiene, Virmantas Povilaitis
- License: nicht angegeben
- Access: direkt (Metadaten); Erträge nur auf Anfrage bei den genannten Personen
- Preparation effort: low (Kontaktliste)
- Rating: 2
- Status: bestätigt (Zenodo-Seite und EJP-Indexseite geöffnet)

**D-PAN-5**
- Name: ICOS Ecosystem Station IT-BCi Borgo Cioffi (Cropland, Class 1)
- Link: https://meta.icos-cp.eu/resources/stations/ES_IT-BCi ; Steckbrief https://www.icos-italy.it/wp-content/uploads/2021/03/borgocioffi.pdf ; FLUXNET https://fluxnet.org/sites/siteinfo/IT-BCi — [ICOS CP](https://meta.icos-cp.eu/resources/stations/ES_IT-BCi)
- Crop(s): Mais, Luzerne, Winter-Futtergräser (Büffelfarm)
- Country/region: Italien, Kampanien (Eboli, Sele-Ebene)
- Location precision: Koordinaten 40.52375 N, 14.957444 E, 10 m ü. NN (≤100 m)
- Area per unit: 15 ha Pivot-bewässertes Feld (≥1 ha)
- Years covered: Flux seit 2004 (ICOS-Label 2023-05-23); FLUXNET2015 2004–2014, FLUXNET-CH4 2017–2018; ≥2013 ja
- Number of sites/fields: 1
- Est. independent site-years ≥2013: ~10 (ein Feld, Mais-Kampagnen)
- Yield measure: Ertrag NICHT als Datenprodukt bestätigt; ICOS verlangt für Class-1-Cropland Above-ground-Biomass (destruktiv) und Ernte-Residuen (ancillary data)
- Extra info: PI Paul Di Tommasi (seit 2023), vormals Vincenzo Magliulo (CNR); BM-Dateien (IT-BCi_BM_…csv) im ICOS-Portal vorhanden (Suchtreffer); Nutzungsbedingungen FLUXNET Tier 2 für ältere Daten
- License: ICOS Data Licence (Seite verlinkt, Text nicht angezeigt; ICOS-Standard ist CC BY 4.0 – hier nicht verifiziert)
- Access: direkt über data.icos-cp.eu (Registrierung für Download)
- Preparation effort: medium–high (Ertrag aus Biomasse-Ancillary ableiten)
- Rating: 2 (einzelnes Feld, Ertrag unsicher)
- Status: bestätigt (Metadaten gesehen; Ertragsvariable nicht gesehen)

**D-PAN-6 (Hinweis, kein Ertrag)**
- Name: In-situ start/end of growing season of major European crops – 17 Feldstandorte Bulgarien + 2 Frankreich
- Link: https://zenodo.org/record/8067432 ; Paper https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10562679/
- Crop(s): Weizen, Mais, Sonnenblume, Raps
- Country/region: Bulgarien
- Location precision: Feldstandorte
- Area per unit: Felder (Größe nicht gesehen)
- Years covered: nicht gesehen
- Number of sites/fields: 17 (BG)
- Est. independent site-years ≥2013: n/a (keine Erträge)
- Yield measure: keine – nur Auflauf-/Erntetermine
- Extra info: nützlich als Phänologie-Label, nicht als Ertragslabel
- License: offen (laut Snippet)
- Access: direkt
- Preparation effort: low
- Rating: 1 (kein Ertrag)
- Status: unbestätigt (nicht geöffnet)

**D-PAN-7 (Spur, hohe Priorität zum Nachprüfen)**
- Name: EODC Feature Collection „pub_yipeeo_yield_fl" (YIPEEO – Feldpolygone mit Ertrag, u. a. Ukraine Winterweizen)
- Link: https://features.dev.services.eodc.eu/collections/pub_yipeeo_yield_fl/items?f=json (nur Suchtreffer; Beispiel-Feature: common winter wheat, 2020, yield 7.6)
- Crop(s): Winterweizen (ggf. weitere)
- Country/region: Ukraine (ggf. weitere Länder)
- Location precision: Feldpolygone
- Area per unit: Felder (≥1 ha wahrscheinlich)
- Years covered: mind. 2020
- Number of sites/fields: unbekannt
- Est. independent site-years ≥2013: unbekannt
- Yield measure: yield (t/ha vermutlich)
- Extra info: Herkunft/Lizenz nicht ermittelt; „dev"-Endpunkt (evtl. nicht stabil)
- License: unbekannt
- Access: offener OGC-API-Endpunkt (unbestätigt)
- Preparation effort: medium
- Rating: ? (potenziell 4–5, falls offen)
- Status: unbestätigt (nicht geöffnet)

**D-PAN-8 (Spur)**
- Name: Data and code for „Functionally rich crop rotations increase calorie and macronutrient outputs across Europe" (Europäische LTEs)
- Link: https://researchdata.se/en/catalogue/dataset/2025-225
- Crop(s): Fruchtfolgen (Getreide u. a.)
- Country/region: Europa (Standorte nicht gesehen)
- Location precision / Area / Years / Sites: nicht gesehen
- Yield measure: Erträge aus LTEs (aggregiert?)
- License / Access: SND, vermutlich offen
- Preparation effort: medium
- Rating: ?
- Status: unbestätigt

**D-PAN-9 (Spur, Paper-basiert)**
- Name: Wheat fields across Europe – aphid abundance, crop morphology and yield from 84 wheat fields (UK, SE, PL, DE, NL)
- Link: https://researchdata.reading.ac.uk/136
- Crop(s): Weizen
- Country/region: u. a. Polen
- Location precision: Felder (Koordinaten?)
- Area per unit: Praxisfelder (≥1 ha wahrscheinlich)
- Years covered: nicht gesehen (Ecosystems-Paper)
- Number of sites/fields: 84 (Anteil PL unbekannt)
- Yield measure: Feldertrag
- License / Access: Reading Research Data Archive (offen)
- Preparation effort: low
- Rating: 2
- Status: unbestätigt

### Inferences
- Offene, strukturierte Mehrstandort-Ertragsdaten existieren für die Region praktisch nur als Nebenprodukt von EU-Projekten (INVITE → D-PAN-1). Für alle Dauerversuche gilt „on request" – die EJP-SOIL-Koordinatorenliste (D-PAN-4) und der BonaRes-Katalog (D-PAN-3) sind der realistische Weg.
- ICOS-Cropland-Stationen liefern in den Zielländern nur einen Standort (IT-BCi); CZ hat laut Suchtreffern keine ICOS-Cropland-Station (CZ-KrP/KRE ist eine Atmosphärenstation), ES-Cnd ist ein Olivenhain.

### Gaps
- Inhalt (Standortkoordinaten, Standortanzahl, Feuchtebasis) der ZIP von D-PAN-1 nicht geprüft.
- Länderliste/Lizenz des Hülsenfrucht-Datensatzes (D-PAN-2) wegen figshare-403 nicht gesehen.
- Herkunft und Lizenz der YIPEEO-Feature-Collection (D-PAN-7) ungeklärt.
- Keine Mähdrescher-Ertragskarten mit offener Lizenz in CZ, HU, PL, IT, ES, RO, UA gefunden (Suchen auf Zenodo/Mendeley/RepOD in EN + Landessprachen ergebnislos; nur FI-Workflow https://zenodo.org/record/7852638 und UK-CYCleSS, beide außerhalb des Scopes).

---

## KQ 1 – Tschechien (ÚKZÚZ, VÚRV/Czech Agrofood Research Centre, CZU, Mendelu, Precision Farming)

### Takeaway
ÚKZÚZ veröffentlicht jährlich pro Kultur „Výsledky zkoušek užitné hodnoty ze sklizně YYYY" (PDF auf mze.gov.cz/eagri.cz) mit Stationstabellen (Höhe, Temperatur, Niederschlag, Bodentyp) und Relativerträgen je Lokalität (Bezug: Mittel der Kontrollsorten am Standort; Korn auf 14 % Feuchte); zusätzlich sind CZ-Weizen-VCU-Daten 2003–2018 als ICASA-Datensatz offen (D-PAN-1). Dauerversuche (Ruzyně seit 1955, IOSDV Ivanovice/Lukavec seit 1983/84) sind nur über Publikationen bzw. Anfrage zugänglich; offene Ertragskarten gibt es nicht.

### Cited Findings (Datensatz-Records)

**D-CZ-1**
- Name: ÚKZÚZ / Národní odrůdový úřad – „Výsledky zkoušek užitné hodnoty ze sklizně YYYY" (ZUH/SDO-Ergebnisberichte je Kultur) und Seznam doporučených odrůd (SDO)
- Link: Beispiele geöffnet: SDO Pšenice ozimá 2026 (Leaflet) https://mze.gov.cz/public/portal/mze/-a92518---x67Q_BEI/psenice-ozima ; weitere Berichte (nur Suchtreffer): Pšenice ozimá v režimu EZ (Ergebnis Ernte 2025, Zkušební stanice-Tabelle u. a. Žabčice ZAB) https://mze.gov.cz/public/portal/mze/-a84280---_5Uf8B8y/psenice-ozima-v-rezimu-ez ; Pšenice jarní SDO https://mze.gov.cz/public/portal/mze/-a91950---dQJNRIFx/psenice-jarni-sdo ; Oves nahý (Stationen Hradec n. Svit., Chrastava, Lípa, Pusté Jakartice, Staňkov, Vysoká) https://mze.gov.cz/public/portal/mze/-a87274---_Mn2Xf1c/oves-nahy ; Len SDO https://mze.gov.cz/public/portal/mze/-a89684---zK0YvZxV/len-sdo ; Cukrovka SDO https://eagri.cz/public/portal/en/-q430995---1lraG0tA/cukrovka-sdo ; Methodik-Präsentation (ÚKZÚZ, 2018) https://mze.gov.cz/public/portal/-q9777---5npfPWvB/lze-vyuzit-vysledky-odrudovych-pokusu — [SDO Pšenice ozimá 2026](https://mze.gov.cz/public/portal/mze/-a92518---x67Q_BEI/psenice-ozima)
- Crop(s): Winter-/Sommerweizen, Gerste, Roggen, Triticale, Hafer, Mais (Korn/Silage), Raps, Zuckerrübe, Kartoffel, Lein, Erbse, Soja u. v. m. (alle registrierten Ackerkulturen)
- Country/region: Tschechien, landesweit
- Location precision: benannte Versuchsstationen (Dorf-/Stadtname, Höhe ü. NN, Bodentyp) → „named station findable"; Koordinaten nicht publiziert; Adressen einzelner Stationen im ÚKZÚZ Bulletin 1/2026 „adresář" (https://mze.gov.cz/public/portal/mze/-a92434---p71HYRBF/bulletin-1-2026 ; Snippet: Hradec nad Svitavou 483, 569 01; Přerov nad Labem 420, 289 16; Dobřichovice, Pražská 586; Chrlice, U jezu 390/3 – 2014) 
- Area per unit: Parzellen (3 (2) Wiederholungen) → „only site mean"
- Years covered: jährlich; Berichte online mind. für Ernten ~2015–2025 (Ernte 2025: Len, Konopí, Pšenice jarní, Oves nahý, Peluška, Brambory, Pšenice ozimá EZ gesehen in Suchtreffern)
- Number of sites/fields: Winterweizen SDO: „každoročně … na 25 lokalitách ÚKZÚZ a spolupracujících privátních subjektů" (Leaflet 2026); Stationsnamen laut Snippets u. a. Domanínek, Jaroměřice nad Rokytnou, Lednice na Moravě, Staňkov, Šumperk, Hradec nad Svitavou, Chrastava, Lípa, Pusté Jakartice, Vysoká, Žabčice
- Est. independent site-years ≥2013: Weizen allein ~25 Standorte × 13 Jahre ≈ 300; über alle Kulturen >1 000 (Schätzung)
- Yield measure: Kornertrag t/ha bei 14 % Feuchte (Ölsaaten 12 %/Stängel 15 % lt. Methodik); Relativertrag % zum Standortmittel der Kontrollsorten; MD 0,05 angegeben
- Extra info: Vorfrucht je Station, Höhe/Temperatur/Niederschlag/Bodentyp je Station, Krankheits-/Lager-Boniturnoten 9–1, Qualitätsparameter; Leaflet verweist auf „podrobné ročníkové výsledky a nově i interaktivní vizualizaci výsledků SDO pšenice ozimé" auf der ÚKZÚZ-Website; Versuche mit Schäden werden ausgeschlossen (kein Schadens-Label)
- License: keine explizite Lizenz (amtliche Veröffentlichung, Ministeriumsportal); nichtkommerzielle Nutzung mit Quellenangabe unproblematisch, formal zu klären
- Access: direkter Download (PDF); strukturierte Rohdaten ggf. auf Anfrage: ÚKZÚZ Národní odrůdový úřad, Hroznová 63/2, 603 00 Brno, ukzuz@ukzuz.cz (Adresse aus Jahresbericht/Snippet)
- Preparation effort: high (PDF-Tabellen je Kultur/Jahr parsen; Stationen georeferenzieren)
- Rating: 4 (dichtes Netz nahe Österreich, lange Reihen; Aufwand hoch)
- Status: bestätigt (SDO-Leaflet 2026 und Methodik-PDF geöffnet; Ertragstabellen je Station nicht direkt gesehen, nur Methodik „relativní výnos … k průměru … na lokalitě")

**D-CZ-2**
- Name: VÚRV Ruzyně (heute Czech Agrofood Research Centre) – Dauerdüngungsversuch Prag-Ruzyně (RFE, seit 1955/1959) und IOSDV Ivanovice na Hané / Lukavec (seit 1983/84)
- Link: Paper Winterweizen 60 Jahre https://www.agriculturejournals.cz/artkey/pse-201603-0002_winter-wheat-results-of-long-term-fertilizer-experiment-in-prague-ruzyne-over-the-last-60-years.php (DOI 10.17221/746/2015-PSE) ; IOSDV-Paper 2025 https://ideas.repec.org/a/caa/jnlpse/vpreprintid310-2025-pse.html — [PSE 2016](https://www.agriculturejournals.cz/artkey/pse-201603-0002_winter-wheat-results-of-long-term-fertilizer-experiment-in-prague-ruzyne-over-the-last-60-years.php)
- Crop(s): Winterweizen, Wintergerste, Zuckerrübe (Ivanovice), Kartoffel (Lukavec), Luzerne (Ruzyně)
- Country/region: CZ – Praha-Ruzyně; Ivanovice na Hané (Südmähren, nahe AT); Lukavec (Vysočina)
- Location precision: benannte Versuchsstationen (findbar; Koordinaten in Papern)
- Area per unit: Parzellen → „only site mean"
- Years covered: Ruzyně 1955/59–heute; IOSDV 1984–2024 (Zyklen 2016–18, 2019–21, 2022–24 im 2025-Paper)
- Number of sites/fields: 3 Standorte
- Est. independent site-years ≥2013: ~3 × 12 ≈ 36 (je Kultur-Behandlung mehr)
- Yield measure: Korn t/ha (Paper 2004–2013: 7,01–8,88 t/ha je nach Düngung)
- Extra info: Düngungsvarianten mineralisch/organisch; P/K seit 2020 ausgesetzt; Ertragsreihen nur in Papern (Tabellen/Abbildungen)
- License: keine (Publikationen); Rohdaten nicht veröffentlicht
- Access: auf Anfrage – Czech Agrofood Research Centre, Praha-Ruzyně; EJP-SOIL-Koordinator CZ Ladislav Menšík (D-PAN-4)
- Preparation effort: high (Anfrage + Digitalisierung)
- Rating: 2
- Status: unbestätigt (nur Paper-Landingpages aus Suchtreffern; Daten nicht gesehen)

**D-CZ-3 (Negativbefund)**
- Name: Czech precision-farming yield maps (z. B. Rostěnice a.s., Feld „Pivovárka", Masaryk-Univ.; VÚRV Ertragskartierung seit 2003)
- Link: https://is.muni.cz/publication/1577857/cs ; https://starfos.tacr.cz/en/vysledky-vyzkumu/RIV%2F00027006%3A_____%2F07%3A1893
- Crop(s): Getreide
- Country/region: CZ (Rostěnice bei Vyškov)
- Location precision: Feld
- Area per unit: Praxisfelder
- Years covered: 2017–2021 (Thesis), 2003–2006 (VÚRV)
- Yield measure: Mähdrescher-Ertragsmonitor
- License / Access: nicht veröffentlicht; nur in Papern/Abschlussarbeiten
- Preparation effort: n/a
- Rating: 1
- Status: unbestätigt (keine Datenveröffentlichung gefunden)

### Inferences
- Für ein Satelliten-Label sind die ÚKZÚZ-Stationsmittel brauchbar (Standort findbar, Jahr, Kultur, Ertrag, Vorfrucht), aber Parzellenversuche zeigen nicht den Ertrag des umgebenden Schlags; Nutzung nur als „site mean"-Proxy. Georeferenzierung über Ortsnamen + Luftbild (Versuchsstationen sind als Parzellenmuster erkennbar) ist realistisch.

### Gaps
- Keine offizielle Liste aller ÚKZÚZ-Versuchsstationen mit Koordinaten gefunden (nur Teil-Adressen im Bulletin 1/2026; Stationsliste für Mais/Raps/Zuckerrübe nicht geprüft).
- Ertragstabellen je Station in einem ZUH-Bericht nicht direkt eingesehen (PDFs mit Verschlüsselung/Bildern; Textextraktion lieferte nur Leaflet-Text).
- CZU-Dauerversuche (Červený Újezd, Lukavec, Humpolec, Suchdol), Mendelu Žabčice, CzechGlobe-Cropland: keine Datenveröffentlichung gefunden (nicht gezielt weiter verfolgt).
- data.gov.cz nicht nach ÚKZÚZ-Datensätzen durchsucht.

---

## KQ 2 – Slowakei (ÚKSÚP, NPPC-VÚRV Piešťany, SPU Nitra)

### Takeaway
ÚKSÚP publiziert „Výsledky skúšok registrovaných odrôd" (PDF) mit Erträgen je Versuchsstation (Kürzel wie VME Veľký Meder, HAN Haniska, JAK Jakubovany, SBE Spišská Belá, BEL Beluša, VIG Vígľaš, ZLZ, VRV, BOD) in t/ha und % zum Versuchsmittel; 14 Stationen landesweit. Dauerversuchsdaten (NPPC) nur auf Anfrage.

### Cited Findings

**D-SK-1**
- Name: ÚKSÚP – Výsledky skúšok registrovaných odrôd (pšenica letná ozimná/jarná; Raps; Kartoffel etc.)
- Link: Weizen (Dokument vom 19.8.2026) https://www.uksup.sk/storage/app/uploads/public/6a9/017/c08/6a9017c0864d6548232032.pdf ; Raps 2009 (Stationserträge-Beispielstruktur) https://www.uksup.sk/storage/app/uploads/public/5b9/267/b4e/5b9267b4e17fa129840296.doc ; Methodik MP 8/2016 https://www.uksup.sk/storage/app/uploads/public/5d9/348/204/5d9348204459c152243848.pdf — [ÚKSÚP Weizen 2026](https://www.uksup.sk/storage/app/uploads/public/6a9/017/c08/6a9017c0864d6548232032.pdf)
- Crop(s): Weizen, Raps, Kartoffel, weitere registrierte Arten (jeweils Sorten der letzten 3 Jahre)
- Country/region: Slowakei, 4 Produktionsgebiete
- Location precision: benannte Stationen (Kürzel; Ortsnamen auflösbar) → „named station findable"
- Area per unit: Parzellen → „only site mean"
- Years covered: Berichte 2009–2026 (Snippets); ≥2013 vorhanden
- Number of sites/fields: 14 Versuchsstationen (Stand 2025)
- Est. independent site-years ≥2013: pro Kultur ~5–8 Stationen × 13 Jahre ≈ 60–100
- Yield measure: úroda t/ha und % k priemeru pokusu
- Extra info: Vorfrucht/Management meist knapp; neue Kartoffelstation Belža (2024)
- License: keine explizite
- Access: direkter PDF-Download; Rohdaten auf Anfrage ÚKSÚP, Odbor odrodového skúšobníctva (Bratislava)
- Preparation effort: high (PDF/DOC parsen)
- Rating: 3
- Status: unbestätigt (PDFs nicht geöffnet; Struktur nur aus Snippets)

**D-SK-2 (Spur)**
- Name: NPPC-VÚRV Piešťany / NPPC-VÚPOP Dauerversuche (EJP-SOIL-Koordinatorin SK: Jaroslava Sobocka)
- Link: siehe D-PAN-4
- Access: auf Anfrage
- Rating: ? ; Status: unbestätigt (keine konkreten Versuchsdaten gefunden)

### Gaps
- Keine Stationsliste mit Koordinaten; keine SPU-Nitra-Daten gefunden; ÚKSÚP-Ergebnis-PDFs inhaltlich nicht geprüft.

---

## KQ 3 – Ungarn (NÉBIH, GOSZ-VSZT-NAK Posztregisztráció, Látókép, Martonvásár, Keszthely, Ertragskarten)

### Takeaway
Die GOSZ-VSZT-NAK-Posztregisztrációs-Fajtakísérletek (durchgeführt von NÉBIH) publizieren jährlich Erträge je Versuchsort in t/ha mit Erntefeuchte, getrennt bewässert/unbewässert – für Mais 2022 verifiziert (10 Orte, 43 Hybride). Amtliche NÉBIH-Weizen-VCU-Daten 2003–2018 sind im ICASA-Datensatz D-PAN-1 enthalten. Látókép (seit 1983), Martonvásár (14 LTEs, ~20 ha, >400 Parzellen) und Keszthely-IOSDV (seit 1983) sind nur auf Anfrage zugänglich; offene Hozamtérkép-Daten existieren nicht.

### Cited Findings

**D-HU-1**
- Name: GOSZ-VSZT-NAK Kukorica Posztregisztrációs Fajtakísérletek 2022 (Ausführung: NÉBIH Mezőgazdasági Genetikai Erőforrások Igazgatóság, Szántóföldi Fajtakísérleti Osztály)
- Link: https://gabonatermesztok.hu/sites/default/files/2023-01/Posztregisztr%C3%A1ci%C3%B3s%20Fajtak%C3%ADs%C3%A9rletek.pdf — [PDF](https://gabonatermesztok.hu/sites/default/files/2023-01/Posztregisztr%C3%A1ci%C3%B3s%20Fajtak%C3%ADs%C3%A9rletek.pdf)
- Crop(s): Körnermais (FAO 200–500)
- Country/region: Ungarn, landesweit
- Location precision: benannte Versuchsorte: Hajdúböszörmény, Hanságliget, Iregszemcse, Jászboldogháza, Páski, Székkutas, Szombathely, Tordas, Bóly, Gyulatanya (2022) → „named station findable"; keine Koordinaten im PDF
- Area per unit: Parzellen → „only site mean"
- Years covered: Reihe seit ca. 2007 (2022 = 16. Veröffentlichung); PDFs online mind. 2014–2024
- Number of sites/fields: 10 Orte (2022); 12 Orte (2015: Bábolna, Tordas, Szombathely, Kaposvár, Iregszemcse, Eszterágpuszta, Jászboldogháza, Jánoshalma, Székkutas, Mezőhegyes, Debrecen, Nyíregyháza)
- Est. independent site-years ≥2013: ~10–12 × 10 Jahre ≈ 100–120 (Mais); plus Weizen/Raps-Reihen ähnlich
- Yield measure: Szemtermés t/ha (Tabellen „Szemtermés (t/ha) – Betakarításkori szemnedvesség (%)"; Feuchte-Normierung im PDF-Text nicht geprüft, üblich 14 %) ; Relativ-% zum Versuchsmittel; „Éréscsoport termésátlagok kísérleti helyenként" (S. 17)
- Extra info: Erntefeuchte je Ort, Anfangsentwicklung, Tage Saat–Blüte, Lager/Stängelbruch, Wasserabgabe-Dynamik, FAO-Berechnung; öntözetlen/öntözött getrennt (Páski, Gyulatanya bewässert); Hybride vor der Saat codiert
- License: Nutzungsvorbehalt: „A jelen kiadvány kizárólag eredeti formában a ‚GOSZ-VSZT-NAK Kukorica Posztregisztrációs Fajtakísérletek 2022' hivatkozással használható fel" → Weiterverwendung nur in Originalform mit Zitat; Datenextraktion für Forschung sollte mit GOSZ abgestimmt werden
- Access: direkter Download; Kontakt Gabonatermesztők Országos Szövetsége (www.gabonatermesztok.hu), VSZT (www.vszt.hu), NAK
- Preparation effort: high (PDF-Tabellen, Orte georeferenzieren)
- Rating: 4 (Mais! Westungarn nahe AT: Szombathely, Hanságliget, Tordas, Iregszemcse)
- Status: bestätigt (PDF geöffnet und Text extrahiert; Tabellenköpfe je Ort gesehen)

**D-HU-2**
- Name: GOSZ-VSZT-NAK Őszi búza / Őszi káposztarepce Posztregisztrációs Fajtakísérletek (jährlich)
- Link: Őszi búza 2024 https://gabonatermesztok.hu/sites/default/files/2024-08/gosz_vszt_nak_%C5%91szi%20_b%C3%BAza_2024.pdf ; Repce 2024 https://gabonatermesztok.hu/sites/default/files/2024-08/gosz_vszt_nak_repce_2024.pdf ; Repce 2021 https://gabonatermesztok.hu/sites/default/files/2021-09/gosz_vszt_nak_repce_2021.pdf ; Kalászos-Koordination 2019 https://www.nebih.gov.hu/documents/10182/726910/Kal_koord_20190904_GOSZ.pdf/4a80cc99-381f-9f82-7c6b-711807d99fc1
- Crop(s): Winterweizen, Winterraps
- Country/region: Ungarn; Weizen 2019/20 an 10 Orten: Tordas, Szombathely, Eszterágpuszta, Iregszemcse, Jászboldogháza, Székkutas, Szarvas, Abaújszántó, Mezőfalva, Mosonmagyaróvár
- Location precision: benannte Orte
- Area per unit: Parzellen → „only site mean"
- Years covered: 2014–2024 (PDF-Jahrgänge laut Treffern)
- Number of sites/fields: ~10
- Est. independent site-years ≥2013: ~100 je Kultur
- Yield measure: t/ha je Ort (analog D-HU-1, nicht geprüft)
- Extra info: Durchführende 2024: Gabonakutató Nonprofit Kft., HUN-REN Mezőgazdasági Intézet, Isterra Közép-Európa Kft. u. a.; Qualitätsanalysen
- License: wie D-HU-1 (nur Originalform mit Zitat)
- Access: direkter Download
- Preparation effort: high
- Rating: 3–4
- Status: unbestätigt (PDFs nicht geöffnet)

**D-HU-3**
- Name: Universität Debrecen – Látókép Dauerversuch (multifaktoriell, Mais, seit 1983/84, kalkhaltige Tschernosem)
- Link: Paper Pepó 2021 https://pse.agriculturejournals.cz/pdfs/pse/2021/08/03.pdf ; Nagy 2011 https://reference-global.com/article/10.2478/v10098-011-0005-9 ; Thesis-Repo https://dea.lib.unideb.hu/items/8f4fb1ae-b641-4152-be21-e17cb30d3e6d
- Crop(s): Mais (Mono-/Bi-/Trikultur mit Weizen, Erbse), Winterweizen
- Country/region: HU, Hajdúság, Debrecen-Látókép
- Location precision: benannter Versuchsstandort (findbar)
- Area per unit: Parzellen (split-split-plot) → „only site mean"
- Years covered: 1983–2024 (2024-Saison lt. Poster)
- Number of sites/fields: 1 Standort (mehrere Versuche: Düngung, Bodenbearbeitung, Bewässerung, Saatdichte)
- Est. independent site-years ≥2013: 12 (× Behandlungen)
- Yield measure: t/ha (2019: 8–14 t/ha je nach Fruchtfolge/Düngung)
- Extra info: Bewässerungs- und Bodenbearbeitungsvarianten → interessant für Stress-Labels
- License: keine
- Access: auf Anfrage – Institute of Land Use, Engineering and Precision Farming Technology, Univ. Debrecen; Korrespondenzautoren lt. Suchtreffer János Nagy (nagyjanos@agr.unideb.hu), Péter Pepó (pepopeter@agr.unideb.hu) – E-Mails nicht verifiziert
- Preparation effort: high
- Rating: 2
- Status: unbestätigt

**D-HU-4**
- Name: HUN-REN ATK Martonvásár – 14 Dauerversuche (seit 1958/60; ~20 ha, >400 Parzellen)
- Link: https://atk.hun-ren.hu/?p=9798 ; Paper Berzsenyi & Dang 2008 https://link.springer.com/article/10.1556/CRC.36.2008.1.17
- Crop(s): Mais (Monokultur seit 1959/60), Weizen, Fruchtfolgen
- Country/region: HU, Martonvásár (Fejér)
- Location precision: Versuchsgelände findbar
- Area per unit: Parzellen → „only site mean"
- Years covered: 1958–heute
- Number of sites/fields: 1 Standort, 14 Versuche
- Est. independent site-years ≥2013: 12 (× Versuche)
- Yield measure: t/ha
- License: keine; Access: auf Anfrage (Department of Crop Production, ATK; EJP-SOIL-HU-Kontakte D-PAN-4)
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-HU-5**
- Name: IOSDV Keszthely (seit 1983; Mais–Winterweizen–Wintergerste; MATE Georgikon)
- Link: Paper 2013 https://agris.fao.org/search/en/records/65df2a280f3e94b9e5d5bd5c ; weitere https://real.mtak.hu/11662/
- Crop(s): Mais, Winterweizen, Wintergerste
- Country/region: HU, Keszthely (Balaton, ~100 km von AT)
- Location precision: findbar
- Area per unit: Parzellen → „only site mean"
- Years covered: 1983–heute (?)
- Number of sites/fields: 1
- Est. independent site-years ≥2013: ≤12
- Yield measure: t/ha
- License: keine; Access: auf Anfrage (Kismányoky/Tóth, MATE Keszthely)
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-HU-6 (Spur)**
- Name: NLFT – Hungarian National Long-term Fertilisation Trials (im BonaRes-LTE-Tool als Netzwerk geführt)
- Link: https://tools.bonares.de/ltfe (Filter Hungary)
- Crop(s): Getreide/Mais; Country: HU, mehrere Standorte; Access: auf Anfrage (ATK TAKI; EJP-SOIL-HU-Kontakte)
- Rating: 2; Status: unbestätigt

**D-HU-7 (Negativbefund)**
- Name: Ungarische Hozamtérkép-/Ertragskarten-Datensätze
- Link: nur Abschlussarbeiten (z. B. https://stud.mater.uni-mate.hu/8451/1/814339313.pdf)
- Status: unbestätigt – keine offenen Daten gefunden

### Gaps
- NÉBIH-eigene VCU-Ergebnisse je Standort (Fajtakísérleti állomások) für andere Kulturen als Weizen (Mais, Sonnenblume, Raps, Soja) nicht gefunden – evtl. in NÉBIH „Leíró fajtajegyzék"/Jahresberichten.
- HU-Flux-Standorte (HU-He, HU-Bug) sind Grünland – nicht verfolgt.

---

## KQ 4 – Polen (COBORU PDO, IUNG, Precision Farming, Poznań)

### Takeaway
COBORU publiziert jährlich „Wyniki PDO" je Artengruppe als PDF (z. B. Zboża ozime 2022, 116 S.): Parzelle 16,5 m², Ertrag bei 14 % Feuchte, zwei Intensitätsstufen (a1/a2), Stationsliste mit Wetterdaten (SDOO/ZDOO: Karzniczka, Wyczechy, Białogard, Rarwino …), aber Ertragstabellen im nationalen Heft nach Regionen (Abweichung vom Standard in dt/ha) – stationsgenaue Erträge erscheinen in den Wojewodschafts-Publikationen der einzelnen SDOO. IUNG hat zwei LTE-Ertragsdatensätze (Grabów 2010–2023, Osiny 1994–2023) auf Zenodo unter CC BY 4.0 hinterlegt, aber bis 31.12.2030 embargiert. Offene Ertragskarten: keine.

### Cited Findings

**D-PL-1**
- Name: COBORU – Wyniki Porejestrowych Doświadczeń Odmianowych (WPDO) / Wstępne wyniki (WWPO), jährlich je Artengruppe
- Link: Zboża ozime 2022 (geöffnet, 116 S.) https://coboru.gov.pl/Publikacje_COBORU/Wyniki_PDO/WPDO_Zbozaozime_2022.pdf ; Zboża jare 2019 https://coboru.gov.pl/Publikacje_COBORU/Wyniki_PDO/WPDO_Zbozajare_2019.pdf ; Zboża ozime 2020 https://coboru.gov.pl/Publikacje_COBORU/Wyniki_PDO/WPDO_Zbozaozime_2020.pdf ; Kukurydza 2022 (wstępne) https://coboru.gov.pl/Publikacje_COBORU/Wstepne_wyniki_PDO/WWPO_Kukurydza_porejestrowe2022.pdf ; Bobowate 2022 https://coboru.gov.pl/Publikacje_COBORU/Wstepne_wyniki_PDO/WWPO_Bobowate_2022.pdf ; Ziemniak 2024 https://coboru.gov.pl/Publikacje_COBORU/Wyniki_PDO/WPDO_214_Ziemniak_2024.pdf — [WPDO Zboża ozime 2022](https://coboru.gov.pl/Publikacje_COBORU/Wyniki_PDO/WPDO_Zbozaozime_2022.pdf)
- Crop(s): Wintergetreide (Weizen, Gerste, Roggen, Triticale), Sommergetreide, Mais, Leguminosen, Kartoffel, Raps, Zuckerrübe (Listy opisowe)
- Country/region: Polen, landesweit (16 Wojewodschaften, Rejony)
- Location precision: Stationen benannt (SDOO/ZDOO-Ortsnamen; Adressen auf Stations-Subdomains, z. B. Wrócikowo 16, 11-010 Barczewo; Sulejów ul. Polna 10; Seroczyn ul. Koszarowa 4; Przecław ul. Podzamcze 2; Pawłowice ul. Wiejska 25, Toszek) → „named station findable"; offizielle Netzseite https://coboru.gov.pl/SDOO/indexsiecdosw.aspx (beim Abruf 404)
- Area per unit: Parzelle ~16,5 m² → „only site mean"
- Years covered: PDO seit 1998; PDFs online ~2015–2024; ≥2013 ja
- Number of sites/fields: Wintergetreide 2022: Dutzende Punkte (Wettertabelle listet >50 SDOO/ZDOO); Kartoffel 2024: 148 Versuche an 38 Orten
- Est. independent site-years ≥2013: Getreide >50 Punkte × 10 Jahre ≈ 500+ (stationsgenaue Werte aber nur in Regionalheften)
- Yield measure: Kornertrag dt/ha bei 14 % Feuchte; Tabellen „Plon ziarna odmian w rejonach (odchylenia od wzorca w dt z ha)", zwei Intensitätsstufen a1/a2
- Extra info: Je Versuchsjahr: Saat-/Auflauf-/Erntetermine (Mittel/früheste/späteste), Vorfruchtverteilung, N-Düngung min/mittel/max, Fungizid-/Wachstumsregler-Anteile, Bodenklasse/pH-Verteilung, Wintersterblichkeit, Lager, Krankheiten; Wetter je Station monatlich (Niederschlag/Temperatur) – Tabela 1 „Dane meteorologiczne. Rok zbioru 2022" mit Zeilen je SDOO/ZDOO
- License: keine explizite (amtliche Publikation; Zitierpflicht üblich)
- Access: direkter PDF-Download; Rohdaten je Station auf Anfrage COBORU Centrala, Słupia Wielka (sekretariat@coboru.gov.pl – nicht verifiziert) oder Wojewódzkie Zespoły PDO
- Preparation effort: high
- Rating: 3 (sehr dichtes Netz, aber Regionsaggregation im Nationalheft; Südpolen klimatisch noch vergleichbar)
- Status: bestätigt (PDF 2022 geöffnet und Text extrahiert; stationsgenaue Ertragstabelle im Nationalheft NICHT gefunden)

**D-PL-2**
- Name: IUNG-PIB – Organic yield data from Grabów LTE, three organic crop rotations (2010–2023)
- Link: https://zenodo.org/records/15773262 (DOI 10.5281/zenodo.15773262); orgprints https://orgprints.org/id/eprint/55929 ; Variablendefinition DOI 10.5281/zenodo.15276082 — [Zenodo](https://zenodo.org/records/15773262)
- Crop(s): Silomais/Körnermais, Wintertriticale, Sommergerste, Sommerweizen, Leguminosen, Kleegras, Getreide-Leguminosen-Gemenge
- Country/region: PL, RZD Grabów (Gmina Przyłęk, Powiat Zwoleń, Mazowieckie)
- Location precision: Versuchsstation benannt (findbar); keine Koordinaten auf der Seite
- Area per unit: nicht angegeben (Rotationsfelder; vermutlich <1 ha → „only site mean")
- Years covered: 2010–2023; ≥2013: 11 Jahre
- Number of sites/fields: 1 Station, 3 Rotationen × 5 Felder
- Est. independent site-years ≥2013: 11 (× 15 Felder = 165 Feldjahre)
- Yield measure: Ertrag (Einheit in Variablendefinition; nicht gesehen)
- Extra info: detaillierte Managementdaten (Saat, Ernte, Düngung) laut Beschreibung; OrganicYieldsUP (HE 101137068)
- License: CC BY 4.0
- Access: EMBARGO bis 31.12.2030 („Time needed to publish scientific papers"); vorher nur auf Anfrage: Adam Kleofas Berbeć (Data curator, ORCID 0000-0002-4609-081X), Jarosław Stalenga (IUNG-PIB Puławy)
- Preparation effort: low (nach Freigabe) / high (Anfrage)
- Rating: 2 (bis 2030 gesperrt; ökologisch)
- Status: bestätigt (Zenodo-Seite geöffnet, Embargo gesehen)

**D-PL-3**
- Name: IUNG-PIB – Long-Term Comparison of Organic and Conventional Crop Production Systems (1994–2023) in Osiny
- Link: https://zenodo.org/records/15773519 (DOI 10.5281/zenodo.15773520 lt. Seite); orgprints https://orgprints.org/id/eprint/55930/ — [Zenodo](https://zenodo.org/records/15773519)
- Crop(s): Öko: Kartoffel, Sommerweizen+Rotklee-Untersaat, Rotklee (2 J.), Winterweizen; Konventionell: Winterraps, Winterweizen, Sommerweizen
- Country/region: PL, Osiny (Kępa-Osiny Experimental Farm bei Puławy, Lubelskie)
- Location precision: Versuchsbetrieb benannt (findbar); keine Koordinaten
- Area per unit: 8 ha gesamt, 1 ha je Rotationsfeld (≥1 ha!) – ohne Wiederholung
- Years covered: 1995/96–2022/23; ≥2013: 10 Saisons
- Number of sites/fields: 1 Standort, 8 Felder à 1 ha
- Est. independent site-years ≥2013: 10 × 8 = 80 Feldjahre
- Yield measure: Ertrag (Einheit in Variablendefinition)
- Extra info: Management-Daten; Satelliten-tauglich wegen 1-ha-Feldern
- License: CC BY 4.0
- Access: EMBARGO bis 31.12.2030; vorher Anfrage Berbeć/Stalenga (IUNG-PIB)
- Preparation effort: low (nach Freigabe)
- Rating: 3 (1-ha-Felder ideal, aber gesperrt)
- Status: bestätigt (Zenodo-Seite geöffnet)

**D-PL-4 (Negativbefund)**
- Name: Polnische Ertragskarten (mapy plonu) auf RepOD/Zenodo/Mendeley; IUNG-Baborówko; Poznań Brody/Złotniki
- Link: RepOD https://www.re3data.org/repository/r3d100011903 ; IUNG-Versuchsbetriebe https://lcagri.iung.pl/en/monitoring/iung-experimental-farms
- Status: unbestätigt – keine offenen Ertragskarten-Datensätze gefunden; Baborówko/Brody/Złotniki-Daten nicht gefunden

### Gaps
- Stationsgenaue PDO-Ertragstabellen: in den Wojewodschafts-Publikationen der SDOO (z. B. „Lista odmian zalecanych", regionale „Wyniki PDO") vermutet, nicht geöffnet.
- COBORU-Stationsnetzseite nicht erreichbar (404); vollständige Stationsliste mit Koordinaten fehlt (statische Karte in Listy opisowe, z. B. https://coboru.gov.pl/Publikacje_COBORU/Listy_opisowe/LOORR%20-%20zbozowe%202021.pdf).

---

## KQ 5 – Slowenien, Kroatien, Serbien

### Takeaway
KIS (Slowenien) veröffentlicht jährlich PDF-Ergebnisse der Sortenversuche (Mais an 6 Orten: Rakičan, Maribor, Jablje, Novo mesto, Ajdovščina, Bilje; Weizen je Ort, Hülsenfrüchte inkl. Soja) mit Erträgen in t/ha bei 14 % Feuchte – Standorte in direkter Nachbarschaft zu Österreich. HAPIH (Kroatien) publiziert Postregistrations-Versuche (Osijek u. a.) als PDF. Serbische LTE-Daten (Rimski Šančevi, seit 1946/47) nur auf Anfrage.

### Cited Findings

**D-SI-1**
- Name: Kmetijski inštitut Slovenije (KIS) – Rezultati preizkušanja hibridov koruze za zrnje in silažo (jährlich; Autoren 2024: Aleš Kolmanič, Simon Ograjšek)
- Link: 2024 https://www.kis.si/f/docs/Koruza/KORUZA_REZULTATI_PPS_2024.pdf (Abruf 404 → ggf. temporär) ; 2020 https://www.kis.si/f/docs/Koruza/KORUZA_2020_KONCNA.pdf ; 2019 https://www.kis.si/f/docs/Koruza/KORUZA_2019_1.pdf ; 2017 https://www.kis.si/f/docs/Koruza/REZULTATI_PPS_KORUZA__2017.pdf ; 2016 https://www.kis.si/f/docs/Koruza/REZULTATI_PPS_KORUZA_ZA_ZRNJE_2016_koncna_2.pdf ; 2015 https://www.kis.si/f/docs/Koruza/Rezultati_sortnih_poskusov_KORUZA_ZA_ZRNJE_2015_1.pdf — [KIS Koruza 2020](https://www.kis.si/f/docs/Koruza/KORUZA_2020_KONCNA.pdf)
- Crop(s): Körnermais (FAO 100–700), Silomais
- Country/region: Slowenien – Rakičan (Prekmurje), Maribor, Jablje (Ljubljana), Novo mesto, Ajdovščina, Bilje (Vipava)
- Location precision: benannte Versuchsorte (KIS-Infrastrukturzentren, findbar) → „named station findable"
- Area per unit: Parzellen → „only site mean"
- Years covered: PDFs 2015–2024 (jährlich); ≥2013 ja
- Number of sites/fields: 6 Orte (Korn 4 + 2; Silage 2)
- Est. independent site-years ≥2013: ~6 × 10 ≈ 60
- Yield measure: pridelek zrnja t/ha „preračunan na 14-% vlago"; Silage TM-Ertrag
- Extra info: Abschnitt „Lokacija in zasnova poskusa", Entwicklungsmerkmale; Finanzierung MKGP (javna služba)
- License: keine explizite („vsi rezultati so objavljeni na www.kis.si")
- Access: direkter PDF-Download; Rohdaten auf Anfrage KIS, Oddelek za poljedelstvo (Kolmanič)
- Preparation effort: medium–high (PDF)
- Rating: 4 (Mais, grenznah zu Steiermark/Kärnten)
- Status: unbestätigt – die oben genannten kis.si-PDF-Links (2024 und 2020) lieferten am 16.10.2026 per curl die HTML-Fehlerseite „Strani ni mogoče najti" (Seite nicht gefunden); die Dokumente sind in Suchindizes nachgewiesen, die KIS-Website wurde offenbar umstrukturiert → Berichte über die KIS-Startseite (www.kis.si → Poljedelstvo → Sortni poskusi/PPS) neu suchen oder bei KIS anfragen

**D-SI-2**
- Name: KIS – Sortni poskusi žita (Winterweizen etc.) je Standort; Zrnate stročnice (Soja etc.); Krompir
- Link: PPS Pšenica A Rakičan 2024 https://www.kis.si/f/docs/Zita/PPS_PSENICA_A_Rakican_2024.pdf ; PPS Pšenica C Rakičan 2024 https://www.kis.si/f/docs/Zita/PPS_PSENICA_C_Rakican_2024.pdf ; Ozimna pšenica Rakičan 2023 https://www.kis.si/f/docs/Zita/Ozimna_psenica_Sortni_poskus_A_zgodnje_sorte_Rakican2023.pdf ; Zrnate stročnice 2016 (26 Sojasorten) https://www.kis.si/f/docs/Zrnate_strocnice_1/REZULTATI_zrnate_strocnice_2016.pdf ; Makroposkusi žita 2020/21 https://www.kis.si/f/docs/Demonstracijski_makroposkusi/MAKROPOSKUSI_ZITA_2020-2021_TJE_2.pdf ; Krompir 2024 https://www.kis.si/f/docs/Krompir/Krompir-predgovor_2024.pdf
- Crop(s): Winterweizen, Gerste, Soja, Erbse, Ackerbohne, Lupine, Kartoffel
- Country/region: Slowenien (Rakičan, Jablje u. a.)
- Location precision: benannte Orte
- Area per unit: Parzellen („only site mean"); Makroposkusi = Streifen-/Großparzellen (Größe nicht gesehen)
- Years covered: 2016–2024
- Number of sites/fields: 2–4 je Kultur
- Est. independent site-years ≥2013: ~30–50
- Yield measure: t/ha (Feuchtebasis nicht gesehen)
- License / Access: wie D-SI-1
- Preparation effort: medium–high; Rating: 3; Status: unbestätigt

**D-HR-1**
- Name: HAPIH – Postregistracijski pokusi ozimih žitarica (OZP/OZJ/OZDP/OZZ/OZR) 2023/24, 2024/25 (Centar za sjemenarstvo i rasadničarstvo, Osijek)
- Link: 2024/25 https://www.hapih.hr/wp-content/uploads/2025/09/Postregistracijski-pokusi-OZP-OZJ-OZDP-OZZ-OZR-2024-25.pdf ; 2023/24 https://www.hapih.hr/wp-content/uploads/2024/09/Postregistracijski-pokusi-OZP-i-OZJ-2023-24.pdf ; Sortna lista RH https://www.hapih.hr/wp-content/uploads/2026/03/Sortna-lista-Republike-Hrvatske.pdf
- Crop(s): Winterweizen (25 Sorten, 3 Wdh.), Wintergerste (15), Durum (3), Hafer, Roggen
- Country/region: Kroatien – Lokationen Osijek und Kutjevo (2024/25)
- Location precision: benannte Orte („Rezultati ispitivanja – lokacija Osijek, Tablica 3"; Klimadaten CSR Osijek)
- Area per unit: Parzellen (75 Grundparzellen OZP je Ort) → „only site mean"
- Years covered: 2023/24, 2024/25 (ältere nicht gefunden)
- Number of sites/fields: 2 (Osijek, Kutjevo)
- Est. independent site-years ≥2013: <10
- Yield measure: KEIN Ertrag in den Tabellen – Spalten sind Wuchshöhe, Ährenschieben-Datum, Winterfestigkeit, Mäuseschaden, Lager, Kornfeuchte bei Ernte, HL-Gewicht, Protein, Stärke, Gluten, Zeleny; das Wort „prinos" kommt im 14-seitigen PDF nicht vor
- Extra info: Klimatabelle Vegetationsperiode; Sortenanmelder (z. B. Poljoprivredni institut Osijek, Bc Institut)
- License: keine explizite; Access: direkter Download; Kontakt HAPIH Centar za sjemenarstvo i rasadničarstvo, Osijek
- Preparation effort: n/a; Rating: 1 (ohne Ertragsspalte unbrauchbar als Label; Ertragsdaten ggf. auf Anfrage bei HAPIH)
- Status: bestätigt (PDF 2024/25 heruntergeladen und Text extrahiert)

**D-RS-1**
- Name: Institut za ratarstvo i povrtarstvo Novi Sad (IFVCNS) – LTE „Crop Rotation" Rimski Šančevi (seit 1946/47, umgestaltet 1969/70)
- Link: FiVeR-Record https://fiver.ifvcns.rs/handle/123456789/1614?show=full ; Institut https://ifvcns.rs/
- Crop(s): Winterweizen (Monokultur und Fruchtfolgen), Mais, Soja, Sonnenblume (Fruchtfolgen)
- Country/region: Serbien, Vojvodina, Rimski Šančevi (N 45°19', E 19°50')
- Location precision: Koordinaten (Minutengenau) + benannter Versuchsbetrieb
- Area per unit: Parzellen → „only site mean"
- Years covered: 1946–heute
- Number of sites/fields: 1
- Est. independent site-years ≥2013: ≤13 (× Varianten)
- Yield measure: t/ha (nur in Publikationen)
- License: keine; Access: auf Anfrage IFVCNS (Repository FiVeR für Publikationen)
- Preparation effort: high; Rating: 2; Status: unbestätigt

### Gaps
- KIS-PDF-Inhalte (Standortkoordinaten, Saat-/Erntetermine) nicht geprüft; 2024-Mais-PDF beim Abruf 404.
- Kroatien: Poljoprivredni institut Osijek Mikro-/Makroversuche nur als Paper; HAPIH-Mais/Soja-Postregistration nicht gefunden.
- Serbien: keine weiteren offenen Daten; kommerzielle NS-Seme-Ortsergebnisse nicht geprüft.

---

## KQ 6 – Rumänien, Bulgarien, Ukraine, Baltikum

### Takeaway
In RO/BG existieren Dauerversuche (Fundulea seit 1966/67; Dobrudzha-Institut) und amtliche Sortenprüfnetze (ISTIS-CTS; IASAS-Bulletin), aber keine offenen Standort-Ertragsdaten; UA-Feldertragsdaten (481 Felder, Kyiv/Cherkasy, 2020–22) liegen bei UHMI/EOS Data Analytics und sind nicht veröffentlicht („Not applicable"). Estland (METK) und Litauen (VATŽŪM) veröffentlichen jährliche Sortenversuchsberichte mit Erträgen je Versuchszentrum.

### Cited Findings

**D-RO-1**
- Name: INCDA Fundulea (NARDI) – Dauerdüngungsversuche (Weizen/Mais, seit 1966/67, NP-5×5-Faktoriell)
- Link: Weizen 1967–2015 https://www.incda-fundulea.ro/anale/83/83.11.pdf ; Mais 1967–1995 https://www.incda-fundulea.ro/rar/nr56/rar5_12.pdf ; FAIRDOM-Eintrag https://urgi.versailles.inrae.fr/fairdom/countries/RO
- Crop(s): Winterweizen, Mais
- Country/region: Rumänien, Fundulea (Călărași)
- Location precision: Versuchsfeld benannt (findbar)
- Area per unit: Parzellen → „only site mean"
- Years covered: 1967–2015 (+ laufend)
- Number of sites/fields: 1
- Est. independent site-years ≥2013: ≤13
- Yield measure: kg/ha (in Papern als 5-Jahres-Mittel)
- License: keine; Access: auf Anfrage INCDA Fundulea (incda-fundulea.ro)
- Preparation effort: high; Rating: 1–2; Status: unbestätigt

**D-RO-2 (Negativbefund)**
- Name: ISTIS – Centre pentru Testarea Soiurilor (CTS), amtliche Sortenprüfung
- Link: Gesetzesgrundlage https://legeaz.net/legea-266-din-2002-republicata/art-34-testarea-inregistrarea-si-protectia-soiurilor-de-plante ; istis.ro (nicht geöffnet)
- Status: unbestätigt – keine je-Zentrum-Ertragsveröffentlichung gefunden

**D-BG-1**
- Name: IASAS (Изпълнителна агенция по сортоизпитване, апробация и семеконтрол) – Официален бюлетин: резултати от сортоизпитването (2020)
- Link: https://www.iasas.government.bg/att/Ofic-biuletin-rezultati-za-vpisvane-sortove-2020.pdf
- Crop(s): alle geprüften Arten
- Country/region: Bulgarien
- Location precision: unbekannt (vermutlich Prüfstationen benannt)
- Area per unit: Parzellen
- Years covered: 2020 (weitere Jahrgänge vermutlich)
- Yield measure: zusammengefasste Erträge je Sorte
- License: keine; Access: direkt (PDF)
- Preparation effort: high; Rating: 1–2; Status: unbestätigt

**D-BG-2 (Spur)**
- Name: Dobrudzha Agricultural Institute General Toshevo – Bodenbearbeitungs-/Sortenversuche (z. B. 2014–2016, 7 Bodenbearbeitungssysteme, Weizen)
- Link: https://doaj.org/article/3abb4e828c81489ea2aaccf86d2d5a68
- Access: auf Anfrage; Rating: 1; Status: unbestätigt

**D-UA-1**
- Name: Kryvoshein, Kryvobok, Zhylchenko (2024) – „Yield prediction at field level", 481 Felder, Kyiv & Cherkasy, 2020–2022 (UHMI + EOS Data Analytics)
- Link: https://ujrs.org.ua/ujrs/article/view/275 (DOI 10.36023/ujrs.2024.11.4.275) — [UJRS](https://ujrs.org.ua/ujrs/article/view/275)
- Crop(s): Mais, Sonnenblume, Winterweizen
- Country/region: Ukraine, Oblaste Kyiv und Cherkasy
- Location precision: Feldpolygone (bei den Autoren)
- Area per unit: Praxisfelder (≥1 ha)
- Years covered: 2020–2022
- Number of sites/fields: 481 Felder
- Est. independent site-years ≥2013: bis 481 (Feld-Jahre über 3 Jahre)
- Yield measure: Feldertrag t/ha (RMSE Mais 1,5 t/ha)
- Extra info: Saattermine und Feldfläche als Prädiktoren vorhanden
- License: Artikel CC BY 4.0; Daten: „Data availability: Not applicable" → NICHT offen
- Access: nur auf Anfrage – Oleksandr Kryvoshein / Oleksii Kryvobok (Ukrainian Hydrometeorological Institute), Dmytro Zhylchenko (EOS Data Analytics); Erfolgsaussicht unklar (kommerzielle Herkunft)
- Preparation effort: high
- Rating: 2 (Daten existieren, aber nicht zugänglich)
- Status: bestätigt (Artikelseite geöffnet; Daten nicht verfügbar)

**D-UA-2 (Spur)**
- Name: UIPVE / Український інститут експертизи сортів рослин – Kwalifikationsprüfung an Prüfpunkten (Steppe/Waldsteppe/Polesien), Erträge je Punkt in Fachartikeln (z. B. 34 Winterweizensorten 2022–23, 5,4–8,4 t/ha)
- Link: https://journal.sops.gov.ua/article/download/64487/59870/132926 ; https://doaj.org/article/ed6ac16d5033428e8e737c2ca8eb7761
- Crop(s): Winterweizen, Roggen, Kartoffel u. a.
- Location precision: Prüfpunkte benannt
- Area per unit: Parzellen (Kartoffel 25 m²) → „only site mean"
- Years covered: 2021–2023 in Papern
- License: Artikel offen; Rohdaten auf Anfrage (sops.gov.ua)
- Rating: 1–2; Status: unbestätigt
- Siehe auch D-PAN-7 (YIPEEO-Feldpolygone Ukraine)

**D-EE-1**
- Name: METK (Maaelu Teadmuskeskus) – „Riiklike sordivõrdluskatsete tulemused ja kvaliteet" (jährlich; Katsekeskused Kuusiku, Jõgeva, Viljandi, Võru)
- Link: 2023 https://metk.agri.ee/sites/default/files/documents/2024-05/Sordiv%C3%B5rlduskatsete%20tulemused%202023_0.pdf ; 2021 https://test.pikk.ee/wp-content/uploads/2022/04/Sordivordluskatsete-tulemused-ja-kvaliteet-2021.pdf ; Studie Winterweizen 2017–2024 https://dspace.emu.ee/items/a0e76a90-506c-4b49-9f7b-71cf6a3bfe37
- Crop(s): Winterweizen, Winterroggen, Triticale, Sommer-/Wintergerste, Hafer, Sommerweizen, Winter-/Sommerraps (Tabelle „KULTUUR × VILJANDI KK / VÕRU KK / KUUSIKU KK / JÕGEVA")
- Country/region: Estland – Versuchszentren Viljandi (71065 Viljandimaa, viljandi@metk.agri.ee), Võru (65566 Võrumaa, rein.peedel@metk.agri.ee), Kuusiku (Kuuseheki tn 6, Kuusiku alevik), Jõgeva
- Location precision: benannte Versuchszentren mit Adresse → „named station findable"
- Area per unit: Parzellen (Katselapid, getrocknet/gewogen) → „only site mean"
- Years covered: jährlich, 2023 = 25. Ausgabe (Reihe seit ~1999); 2021 und 2023 PDFs gefunden; ≥2013 ja
- Number of sites/fields: 4 Zentren
- Est. independent site-years ≥2013: ~40 (je Kultur 2–4 Orte × 11 Jahre)
- Yield measure: „Arvestuslik saak / Yield, kg/ha ja % st.keskmisest" (kg/ha und % des Standardmittels) je Zentrum; Feuchtebasis nicht gesehen
- Extra info: je Zentrum Bodentyp, Vorfrucht, Saatdatum, Saatstärke, NPKS-Düngung mit Datum, Monatswetter (Temperatur/Niederschlag), Winterhärte, Qualität; zweisprachig EE/EN; „Sordivõrdluskatsete tulemused on digitaalselt kättesaadavad" (digital verfügbar)
- License: keine explizite; Access: direkter PDF-Download; Rohdaten auf Anfrage METK Viljandi katsekeskus; EJP-SOIL-EE-Kontakte (Astover, Kauer, Talgre)
- Preparation effort: medium–high (saubere, zweisprachige Tabellen); Rating: 2–3 (gut strukturiert, aber boreales Klima); Status: bestätigt (PDF 2023 heruntergeladen, Tabellen gesehen)

**D-LT-1**
- Name: VATŽŪM (Valstybinė augalininkystės tarnyba) – „Augalų veislių ūkinio vertingumo tyrimų duomenys" (jährliche Publikation; 5 Abteilungen + LAMMC Rumokai; 3 Boden-Klima-Zonen)
- Link: Übersicht https://vatzum.lrv.lt/public/canonical/1699343103/18474/ ; 2017-Publikation https://vatzum.lrv.lt/uploads/documents/augalu_veisles/2017_duomenu_leidinys_pilnas_spaustuvei_20170324_2.pdf ; 2011 (DOC) https://vatzum.lrv.lt/uploads/documents/augalu_veisles/ukinio_vertingumo_duomenys/uvt_2011_m..doc
- Crop(s): Winterweizen, Gerste, Raps, Zuckerrübe, Kartoffel u. a.
- Country/region: Litauen
- Location precision: benannte Stationen
- Area per unit: Parzellen → „only site mean"
- Years covered: Publikationen 2005–2019 gefunden
- Number of sites/fields: 5–6
- Est. independent site-years ≥2013: ~40
- Yield measure: grūdų derlius t/ha; TKG, Vegetationsdauer, Winterhärte, Lager, Qualität
- License: keine explizite; Access: direkter Download
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-LT-2 (Spur)**
- Name: LAMMC Dauerversuche (Dotnuva, Valinava-Fruchtfolge, Bodenbearbeitung seit 1956)
- Link: https://projects.au.dk/ejpsoil/visiting-scientists-support-access-to-infrastructure/partner-countries-with-ltes/ltes-lithuania
- Access: auf Anfrage (Grazina Kadziene, Virmantas Povilaitis, Virginijus Feiza)
- Rating: 1–2; Status: unbestätigt

### Gaps
- Lettland: keine Daten gefunden (nur EJP-Kontakt Janis Vigovskis, AREI).
- Bulgarien/Rumänien: keine strukturierten Standort-Erträge.
- Ukraine: keine offene Feld-Ertragsquelle außer der unverifizierten YIPEEO-Spur.

---

## KQ 7 – Italien (CREA-Netze, LTEs, ICOS, Ertragskarten)

### Takeaway
Die CREA-„Rete nazionale di confronto varietale" (Frumento duro/tenero, Mais, Orzo) publiziert Standort-Erträge jährlich in Fachzeitschriften (L'Informatore Agrario, Terra e Vita, Contoterzista) und Regionalberichten (z. B. Sizilien 5 Umwelten, 30 Sorten 2022/23) – keine strukturierten offenen Daten. Das IC-FAR-Netz (7 LTE-Standorte: Torino, Padova, Bologna, Ancona, Pisa, Perugia, Foggia) hat eine AgMIP/MACSUR-kompatible Datenbank, Zugang nur auf Anfrage. Einzige offene Flux-Cropland-Station: IT-BCi (D-PAN-5). Ertragskarten: keine.

### Cited Findings

**D-IT-1**
- Name: CREA – Rete nazionale di confronto varietale frumento duro / frumento tenero / mais (Ergebnisse je Standort in Fachpresse)
- Link: Mais 2022 (Contoterzista, 12+8+5 Versuche) https://contoterzista.edagricole.it/wp-content/uploads/sites/14/2023/02/COLTURE-PRIMAVERILI_TAB1.pdf ; Frumento duro Sizilien 2022/23 https://terra.regione.sicilia.it/wp-content/uploads/2023/06/Il-documento.pdf ; Rete nazionale 2008/09 (47 Versuche, 16 Regionen) https://terraevita.edagricole.it/agri24/img/specialeFrumentoDuro_TV200938.pdf ; Veneto (Lonigo, Mogliano, Ceregnano) https://www.provincia.vicenza.it/ente/la-struttura-della-provincia/servizi/agricoltura/agricoltura-sostenibile/frumento_duro_orzo.pdf ; CREA-Journal https://journals-crea.4science.it/index.php/dalseme/article/view/1510/1024
- Crop(s): Durum, Weichweizen, Mais (Korn FAO 200–700, Silage), Gerste
- Country/region: Italien, 6 Areale (Sicilia, Sardegna, Sud, Centro tirrenico/adriatico, Nord)
- Location precision: Standorte benannt (Gemeinde/Azienda) → „named station findable"
- Area per unit: Parzellen → „only site mean"
- Years covered: jährlich seit 1973 (Durum, 36. Jahr 2008/09); ≥2013 ja
- Number of sites/fields: Durum ~40–50 Versuche/Jahr; Mais 2022: 25 Versuche
- Est. independent site-years ≥2013: Durum ~500, Mais ~250 (Schätzung)
- Yield measure: t/ha bzw. q/ha (Mais 2022 Mittel 132 q/ha mittel-spät, 90,2 q/ha früh); Feuchtebasis nicht gesehen (üblich 13 % Weizen / 15,5 % Mais)
- Extra info: regionale Berichte mit Saat/Ernte, Niederschlag; Koordination CREA-CI (Cerealicoltura e Colture Industriali), früher CRA-QCE Roma / Sant'Angelo Lodigiano
- License: Fachpresse (urheberrechtlich); Rohdaten auf Anfrage CREA-CI
- Access: Artikel teils frei (PDF), teils Abo; Daten „on request"
- Preparation effort: high
- Rating: 3
- Status: unbestätigt (PDF-Links aus Suchtreffern, nicht geöffnet)

**D-IT-2**
- Name: IC-FAR – Italian Long-Term Agro-ecosystem Experiments network (Datenbank; Standorte Torino, Padova/Legnaro, Bologna/Cadriano, Ancona, Pisa, Perugia, Foggia); später MAGGnet/MACSUR
- Link: Poster https://scisoc.confex.com/crops/2016am/webprogram/Handout/Paper102444/2016-POSTER-%20Iocola%20et%20al%20ROGGERO.pdf ; Bologna-LTE https://amsacta.unibo.it/6669/1/2020_08_NL.pdf ; www.icfar.it (nicht öffenbar)
- Crop(s): Weizen, Mais, Fruchtfolgen
- Country/region: Italien (Norditalien: Padova, Bologna, Torino)
- Location precision: Versuchsstationen findbar
- Area per unit: Parzellen → „only site mean"
- Years covered: Legnaro seit 1962, Bologna seit 1966 u. a.; laufend
- Number of sites/fields: 7 Standorte, 16 LTEs
- Est. independent site-years ≥2013: ~7 × 12 ≈ 84
- Yield measure: t/ha
- License: keine; Access: auf Anfrage (Projektleitung Pier Paolo Roggero, Univ. Sassari; Bologna: Guido Baldoni/Loretta Triberti, DISTAL UniBo; EJP-SOIL-IT-Kontakte D-PAN-4)
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-IT-3 (Negativbefund)**
- Name: Italienische Ertragskarten (mappe di resa) auf Zenodo/IRIS
- Link: nur Sentinel-2-Produkte Bonifiche Ferraresi 2015 https://zenodo.org/record/7058860 (keine Erträge)
- Status: unbestätigt – keine Ertragskarten-Datensätze gefunden

### Gaps
- Aktuelle (2023–2025) CREA-Netzergebnisse je Standort nicht geöffnet (L'Informatore Agrario hinter Paywall).
- RetiBio 2 (BonaRes-Tool) nicht geprüft.

---

## KQ 8 – Spanien, Portugal, Griechenland

### Takeaway
GENVCE betreibt einen offenen „Mapa de resultados" (genvce.org) mit 14 Kulturen (Getreide, Raps, Sonnenblume, Mais FAO 400–700, Durum, Triticale) für die Kampagnen 2023–2026, filterbar nach Agroklimazone/Ort, mit „Datos Abiertos GENVCE"-Nutzungsbedingungen (Quellenangabe); 2026: 87 Sorten, 134 Versuche in 10 Autonomen Gemeinschaften. Regionalberichte (IRIAF, ITACyL, IRTA, Madrid) geben Erträge je Ort. Portugal: INIAV/ANPOC-LVR mit Beja/Elvas. Griechenland: nichts gefunden (Suche blockiert).

### Cited Findings

**D-ES-1**
- Name: GENVCE – Mapa de resultados / Datos Abiertos GENVCE (Grupo para la Evaluación de Nuevas Variedades de Cultivos Extensivos en España)
- Link: https://genvce.org/mapa-de-resultados/ ; Informes https://genvce.org/productos-genvce/informes/ ; Fichas https://genvce.org/productos/fichas/ ; Presse 2026 https://www.agronewscastillayleon.com/genvce-87-variedades-cereal-invierno-ensayos-2026 — [GENVCE Mapa](https://genvce.org/mapa-de-resultados/)
- Crop(s): Hafer, Winter-/Sommergerste, Roggen, Raps, Sonnenblume, Mais FAO 400–500 und 600–700, Weichweizen Winter/Sommer (auch öko), Durum, Triticale
- Country/region: Spanien, 10 Autonome Gemeinschaften
- Location precision: Filter „Ciudad" + Agroklimazone (Niederschlag/Temperatur-Klassen) → Versuchsorte benannt; Koordinaten nicht gesehen
- Area per unit: Parzellen → „only site mean"
- Years covered: Karte 2023–2026; Informes/Fichas ab ~2010 (Vida Rural 2010/2011)
- Number of sites/fields: 134 Wintergetreideversuche 2026 (19 % annulliert); Mais 16 Versuche 2024
- Est. independent site-years ≥2013: Wintergetreide ~100/Jahr × 13 ≈ 1 000+; Mais ~15/Jahr
- Yield measure: Ertrag kg/ha (t/ha) je Sorte und Ort, Relativwerte; Feuchtebasis nicht gesehen
- Extra info: Annullierungsgründe (Hagel, Nässe, Wild) dokumentiert → Hinweis auf Schadensereignisse; Fichas mit Verhalten je Zone; DBCERES-Datenbank (Login)
- License: „Datos Abiertos GENVCE" – Bedingungen: Integrität, keine Sinnentstellung, Quellenangabe „Fuente: Datos Abiertos GENVCE" + URL + Downloaddatum, Ley 18/2015 (Reuse of public sector information)
- Access: direkt (Webkarte; CSV-Download nicht gesehen); Kontakt info@genvce.org
- Preparation effort: medium–high (Web-Scraping oder Anfrage)
- Rating: 3 (sehr dicht, aber mediterranes Klima; Parzellen)
- Status: bestätigt (Startseite und Karten-Filterseite geöffnet; Ergebnistabelle/Download nicht gesehen)

**D-ES-2**
- Name: Regionale GENVCE-/Sortenversuchsberichte: IRIAF Castilla-La Mancha (Hoja 88, Kampagne 2024: Albaladejito, Alcázar del Rey, Ciudad Real), CIAG Chaparrillo 2021/2022, Comunidad de Madrid (Finca La Chimenea, Aranjuez, 2021/22 und 2023/24), ITACyL Castilla y León (Zamadueñas, Zael – 14 Versuche an 5 Orten 2024/25), IRTA Catalunya (Repositori)
- Link: https://iriaf.castillalamancha.es/sites/default/files/2024-09/iriaf_hoja_88.pdf ; https://chaparrillo.castillalamancha.es/sites/default/files/2022-10/CIAG_cultivos_invierno_2022.pdf ; https://www.comunidad.madrid/sites/default/files/doc/medio-ambiente/ensayo_cereales_de_invierno_genvce_campana_2023-2024.pdf ; https://www.interempresas.net/Grandes-cultivos/609764-Evaluacion-de-variedades-de-cereales-de-invierno-en-Castilla-y-Leon.html ; https://repositori.irta.cat/handle/20.500.12327/3779
- Crop(s): Wintergetreide (Weich-/Durumweizen, Gerste, Triticale, Hafer, Roggen)
- Country/region: ES – Kastilien-La Mancha, Madrid, Kastilien-León, Katalonien
- Location precision: benannte Fincas/Orte
- Area per unit: Parzellen → „only site mean"
- Years covered: 2021–2025
- Number of sites/fields: 1–5 je Region
- Est. independent site-years ≥2013: ~50–100
- Yield measure: kg/ha (Zael 2024/25 Mittel 6 910 kg/ha)
- License: regionale Verwaltungspublikationen (keine explizite Lizenz); Access: direkter PDF-Download
- Preparation effort: high; Rating: 2–3; Status: unbestätigt (PDFs nicht geöffnet)

**D-ES-3**
- Name: Universitat de Lleida – Agramunt LTE (seit 1996; Bodenbearbeitung × N; seit 2015 bewässerter Mais) und Selvanera (19 Jahre)
- Link: DISOSMED-Datensatz (Zersetzung, CC BY-NC 4.0) https://b2find.eudat.eu/dataset/f4f087a8-4929-5982-acd0-050704ab25b0 ; FCR-Paper https://recercat.cat/handle/10459.1/56727
- Crop(s): Gerste/Weizen (Trockenland), Mais (bewässert ab 2015)
- Country/region: ES, Lleida (Agramunt, Selvanera)
- Location precision: Versuchsfelder findbar
- Area per unit: Parzellen → „only site mean"
- Years covered: 1996–heute
- Number of sites/fields: 2–3
- Est. independent site-years ≥2013: ~30
- Yield measure: kg/ha (nur Paper); DISOSMED enthält keine Ertragsreihe
- License: DISOSMED CC BY-NC 4.0; Erträge: keine
- Access: Erträge auf Anfrage (Carlos Cantero-Martínez, Jorge Lampurlanés, UdL)
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-ES-4 (Spur)**
- Name: Xunta de Galicia / AGACAL „Millopreciso" – bereinigte Ertragskarten Silomais (Häcksler-Ertragsmonitor), Projekt 2022
- Link: https://agacal.xunta.gal/sites/default/files/1.%202022-001B_Memoria_libre_REVISADA%20E%20LISTA.pdf
- Crop(s): Silomais; Country: ES, Galicien; Area: Praxisfelder; Years: ~2020–2022; Access: nicht veröffentlicht (Projektbericht); Rating: 1; Status: unbestätigt

**D-PT-1**
- Name: INIAV / ANPOC – Lista de Variedades Recomendadas (LVR) Trigo mole 2025 (10+ Jahre multilokale Versuche; Standorte Beja und Elvas)
- Link: https://www.iniav.pt/images/Noticias/LVR_-Trigo_mole_2025.pdf ; 2022 https://www.iniav.pt/images/Noticias/LVR_-Trigo_mole_2022.pdf ; 2021 https://www.iniav.pt/images/Noticias/LVR_Trigo_Mole_2021.pdf ; 2019 https://www.agroportal.pt/wp-content/uploads/2019-LVR-Trigo-Mole-v.final_.pdf ; INIAV-Elvas-Studie 2021–23 https://iniav.pt/images/publicacoes/2025/Producao_e_qualidade_panificavel_do_trigo-mole_Vida_Rural.pdf
- Crop(s): Weichweizen (LVR auch Durum, Gerste – PDFs nicht gefunden)
- Country/region: Portugal, Alentejo (Beja, Elvas); neu ab 2024 Mirandela (Quinta do Valongo, LIFE SOS Pygargus)
- Location precision: benannte Versuchsorte (INIAV-Polos)
- Area per unit: Parzellen → „only site mean"
- Years covered: ~2014–2025
- Number of sites/fields: 2–3
- Est. independent site-years ≥2013: ~25
- Yield measure: Produktivität relativ zum Versuchsmittel (kg/ha in Studien, z. B. 2 139 kg/ha Trockenland)
- License: keine explizite; Access: direkter PDF-Download; Rohdaten auf Anfrage INIAV Elvas (EJP-SOIL-PT-Kontakte Castanheira/Mano)
- Preparation effort: high; Rating: 2; Status: unbestätigt

**D-GR-1 (Negativbefund)**
- Name: ELGO-Dimitra (Institute of Plant Breeding & Genetic Resources, Thermi) Sortenversuche
- Link: nur archäobotanisches Experiment https://giap.icac.cat/2025/02/03/experimental-cultivations-of-wheat-sowing-the-seeds-to-strengthen-and-extend-our-new-methodology-in-archeobotany/
- Status: unbestätigt – keine Ertragsdaten gefunden (griechischsprachige Suche durch Tool-Hook blockiert)

### Gaps
- GENVCE: Ob die Karte Einzelorte mit Koordinaten und CSV-Export bietet, nicht gesehen (JS-Anwendung); Anfrage an info@genvce.org nötig.
- Spanische/portugiesische Mähdrescher-Ertragskarten: keine offenen Datensätze.
- Griechenland komplett offen.

---

## Gesamtbewertung / Priorisierung für das BWKI-Projekt

1. **D-PAN-1 Zenodo 20786880** (Weizen-VCU CZ+HU 2003–2018, CC BY 4.0, ICASA) – sofort nutzbar, Rating 5.
2. **D-HU-1/D-HU-2 GOSZ-VSZT-NAK** (Mais/Weizen/Raps je Ort, Westungarn) – offen als PDF, Nutzungsvorbehalt beachten, Rating 4.
3. **D-CZ-1 ÚKZÚZ ZUH/SDO** (25 Weizenorte u. v. m., 14 % Feuchte, Vorfrucht) – PDF-Parsing, Rating 4.
4. **D-SI-1/2 KIS** (Mais an 6 grenznahen Orten, Soja) – PDF, Rating 4 (unbestätigt).
5. **D-PL-1 COBORU** (sehr dicht; Regionalhefte für Stationswerte) – Rating 3.
6. **D-ES-1 GENVCE** (offene Datenpolitik, mediterran) – Rating 3.
7. On-request-Kandidaten mit 1-ha-Feldern: **D-PL-3 Osiny** (embargiert bis 2030, Anfrage möglich).
8. Zu klärende Spuren: **D-PAN-7 YIPEEO Feldpolygone (UA)**, **D-PAN-2 Hülsenfrucht-Datensatz** (Soja), **D-PAN-8 researchdata.se**.

Generelle Einschränkung: Alle offenen Quellen der Region sind Parzellenversuche (Standortmittel); echte Feld-/Schlagerträge (≥1 ha) wurden nur bei IUNG-Osiny (embargiert) und in nicht veröffentlichten Datensätzen (UA 481 Felder, CZ Rostěnice) gefunden.
