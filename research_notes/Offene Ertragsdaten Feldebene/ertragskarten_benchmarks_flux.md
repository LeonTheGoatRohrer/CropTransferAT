# Offene Ertragskarten / Yield-Monitor-Daten, ML-Benchmarks und Flux-Tower-Ertragsdaten (Repository-/Benchmark-Sweep)

Stand: 2026-10-16. Methode: WebSearch (teilweise durch Hook blockiert), direkte API-Abfragen (Zenodo REST, DataCite, Dryad, Harvard Dataverse, figshare, Mendeley research-data, Crossref, HuggingFace, GitHub, AmeriFlux site API, ICOS SPARQL, EODC OGC-API-Features) und WebFetch der Landing-Pages. Felder je Datensatz exakt wie vorgegeben:
Name | Link | Crop(s) | Country/region | Location precision | Area per unit (ha) | Years covered (≥2013) | Number of fields/sites | Est. independent site-years ≥2013 | Yield measure/unit/moisture | Extra info | License | Access | Preparation effort | Rating 1–5 | Status.
Ausgeschlossen (bereits bekannt): KBS LTER, USDA BARC gridded yield archive, Colorado Akron (Poss et al.), Mead US-Ne1/2/3, One Acre Fund, YieldSAT, CY-Bench.

---

## Key Question 1: Generische Repositories (Zenodo / Dryad / figshare / Mendeley / PANGAEA / Dataverse / 4TU / OSF / ScienceDB) – Yield-Map- / Yield-Monitor-Datensätze

### Takeaway
Echte offene Mähdrescher-Ertragskarten mit echten Koordinaten und ≥2013 sind in generischen Repositories Einzelstücke (meist 1–2 Felder pro Record); die mit Abstand größte offene Feldebene-Quelle ist die ESA/YIPEEO-Sammlung (1.954 Feld-Jahre mit Polygonen, s. KQ 2). Mehrere größere Sammlungen (DWFI Minnesota/Iowa/Nebraska, GRDC Hyper Yielding Crops, DTI Dänemark, DIFM) sind auf Zenodo zwar registriert, aber zugriffsbeschränkt (schriftliche Begründung/Data Access Agreement).

### Cited Findings (Datensatz-Blöcke)

- **Name:** Yield data from field measurements and satellite imagery from Sentinel-2 for three consecutive years (Kayad, Sozzi, Gatto, Marinello, Pirotti; Univ. Padova)
  **Link:** https://zenodo.org/records/14216165 (geöffnet)
  **Crop(s):** Körnermais
  **Country/region:** Norditalien (Paper: Venetien; Record nennt keine Koordinaten, Daten sind georeferenzierte Punkte)
  **Location precision:** Punkt-Koordinaten je Monitor-Record (>20.000 Punkte/Saison laut Paper) → Feldpolygon ableitbar
  **Area per unit (ha):** 22 ha (1 Feld)
  **Years covered:** 2016, 2017, 2018 (alle ≥2013)
  **Number of fields/sites:** 1 Feld
  **Est. independent site-years ≥2013:** 3
  **Yield measure:** Harvester-Yield-Monitor-Punkte + Kriging-Raster; Einheit/Feuchtebasis im Record nicht angegeben
  **Extra info:** Sentinel-2-Ausschnitte im ZIP (FIELD_YIELD.zip, 11 MB); Paper: GNDVI R² 0,48, RF R² ≈0,6, bestes Fenster 105–135 Tage nach Saat
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Preparation effort:** low–medium (Shapefile/CSV-Formate prüfen)
  **Rating:** 3 (kleiner, aber sauberer Mehrjahres-Mais-Testfall mit Innerfeld-Variabilität)
  **Status:** bestätigt — [Zenodo 14216165](https://zenodo.org/records/14216165); Paper-Abstract [Crossref 10.3390/rs11232873](https://api.crossref.org/works/10.3390/rs11232873)

- **Name:** Spatial Dataset from a Minnesota Farm / Iowa Research Farm / Nebraska Research Farm, 2021–2024 (Davidson, Ritzema, Neale; Daugherty Water for Food Global Institute, Univ. Nebraska; ARPA-E DE-AR0001226)
  **Link:** https://zenodo.org/records/15367430 (geöffnet; weitere Records: 15367447, 8299288, 15367414 [MN]; 15367233, 15367284, 15367312, 8209353 [IA]; 15367355, 15367371, 8206609, 15367393 [NE])
  **Crop(s):** nicht angegeben (Corn Belt; vermutlich Mais/Soja)
  **Country/region:** USA – Praxisfeld bei Morris, MN (rainfed); ISU-Station bei Williams, IA (rainfed); UNL ENREC bei Mead, NE (bewässert – Nähe zu ausgeschlossenen US-Ne-Sites, aber eigenes Feld)
  **Location precision:** Karten (Yield + Pflanzdichte) → Feldpolygon; Details erst nach Freigabe
  **Area per unit (ha):** nicht angegeben
  **Years covered:** 2021, 2022, 2023, 2024 je Standort
  **Number of fields/sites:** 3 Felder
  **Est. independent site-years ≥2013:** 12
  **Yield measure:** "maps of yield and planting density" (Format/Einheit nicht angegeben)
  **Extra info:** ARPA-E-Projekt (Bewässerungs-/Sensorik-Kontext)
  **License:** CC BY 4.0 (Metadaten); Daten "restricted"
  **Access:** on request via Zenodo-Request-Formular: schriftliche Begründung, Danksagung an DWFI/ARPA-E, Vertraulichkeit, keine Weitergabe/Publikation ohne schriftliche Zustimmung von DWFI
  **Preparation effort:** medium
  **Rating:** 2 (für Schülerprojekt realistisch anfragbar, aber Vertraulichkeitsklausel)
  **Status:** bestätigt (Metadaten; Dateien gesperrt) — [Zenodo 15367430](https://zenodo.org/records/15367430)

- **Name:** Eddy covariance N2O/CH4/CO2 fluxes, crop and soil nitrogen measurements, and as-applied fertilization and yield maps of a winter wheat field under two nitrogen fertilization strategies (CH-TAN, Switzerland, 2023–2024) (Turco & Buchmann, ETH Zürich)
  **Link:** https://doi.org/10.3929/ethz-c-000807633 (DataCite-Metadaten geöffnet; Research-Collection-Seite lieferte HTTP 500)
  **Crop(s):** Winterweizen
  **Country/region:** Tänikon, Thurgau, Schweiz (ICOS/ETH-Station CH-Tnk/CH-TAN, 47.4806 N, 8.9118 E laut ICOS-Stationsliste)
  **Location precision:** Shapefiles (Yield-Map des Mähdreschers, As-applied-Düngekarte) → exakte Feldgeometrie, zwei Parzellen (betriebsüblich vs. Variable-Rate)
  **Area per unit (ha):** nicht angegeben
  **Years covered:** Saison 2023/24
  **Number of fields/sites:** 1 Feld (2 Parzellen)
  **Est. independent site-years ≥2013:** 1
  **Yield measure:** Mähdrescher-Kornertragskarte + Plot-Handernte (Korn- und Stroh-Trockenmasse, TKG, Ährendichte, N-Gehalte)
  **Extra info:** halbstündliche EC-Flüsse, LAI, Bestandeshöhe, Biomasse, Nmin, Management; Code auf GitHub (fabioturc/n2o-precision-fertilization); Formate ZIP/CSV/Shapefile
  **License:** in DataCite nicht angegeben (ETH Research Collection: i. d. R. CC BY 4.0 – prüfen)
  **Access:** direkter Download (ETH Research Collection)
  **Preparation effort:** low
  **Rating:** 3 (einziges gefundenes offenes Mähdrescher-Yield-Map-Shapefile aus dem DACH-Raum ≥2023; nur 1 Feld-Jahr)
  **Status:** bestätigt (DataCite-Metadaten; Datei-Download nicht getestet) — [DataCite 10.3929/ethz-c-000807633](https://api.datacite.org/dois/10.3929/ethz-c-000807633)

- **Name:** Processing of combine harvester yield monitor data in QGIS (SYKE, Carbon Action community) – Beispieldatensatz
  **Link:** https://zenodo.org/record/7852638 (geöffnet)
  **Crop(s):** nicht angegeben (finnisches Feld "Lammensivu")
  **Country/region:** Finnland (aus Dateinamen/Affiliation; nicht explizit)
  **Location precision:** Shapefile mit Monitor-Punkten ("corrected_points") → Feldpolygon
  **Area per unit (ha):** 1 Feld, Größe nicht angegeben
  **Years covered:** nicht angegeben (Record 2023)
  **Number of fields/sites:** 1
  **Est. independent site-years ≥2013:** 1
  **Yield measure:** Yield-Monitor-Punkte (Feuchtebasis nicht dokumentiert)
  **Extra info:** NDVI-Raster, Grundwasser/DEM-Raster, PDF-Workflow; 42,7 MB
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Preparation effort:** low
  **Rating:** 1 (Demo)
  **Status:** bestätigt — [Zenodo 7852638](https://zenodo.org/record/7852638)

- **Name:** Dataset used in Macdonald et al. 2025 – Topographic position index predicts within-field yield variation in a dryland cereal production system (USDA-ARS / Colorado State Univ.)
  **Link:** https://zenodo.org/records/15519945 (geöffnet)
  **Crop(s):** Hard Red Winter Wheat (Langin), Mais, Rispenhirse (proso millet)
  **Country/region:** Dryland-Forschungsfarm Nordost-Colorado, USA (keine Koordinaten im Record; DEM in UTM 13N → Lage rekonstruierbar; Achtung: wahrscheinlich dieselbe USDA-ARS-Farm Akron wie der ausgeschlossene Poss-et-al.-Datensatz – Dublettenprüfung nötig)
  **Location precision:** DEM 5 m (georeferenziert), Modelling-CSV
  **Area per unit (ha):** 18 Management-Einheiten à 2,6–4,3 ha
  **Years covered:** 2019–2022
  **Number of fields/sites:** 18 Einheiten
  **Est. independent site-years ≥2013:** ~72 Einheit-Jahre (ein Standort)
  **Yield measure:** Innerfeld-Ertrag (Quelle/Einheit im Record nicht genannt, im Data_dictionary.csv)
  **Extra info:** RTK-Topografie, Bodentextur/-chemie, Wetterstation
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Preparation effort:** medium
  **Rating:** 2 (Überschneidung mit ausgeschlossenem Akron-Datensatz wahrscheinlich)
  **Status:** bestätigt — [Zenodo 15519945](https://zenodo.org/records/15519945)

- **Name:** Data for "Site-Specific Management Zones Delineation Based on Apparent Soil Electrical Conductivity in Two Contrasting Fields of Southern Brazil" (Bottega & Safanelli)
  **Link:** https://zenodo.org/records/13770031 (geöffnet)
  **Crop(s):** Sojabohne
  **Country/region:** Südbrasilien, zwei Betriebe ("Cachoeira", "Curitibanos" laut Dateinamen; keine Koordinaten im Record)
  **Location precision:** 50 × 50 m Rasterpunkte je Feld (Koordinaten in CSV vermutlich enthalten – zu prüfen)
  **Area per unit (ha):** nicht angegeben
  **Years covered:** nicht angegeben (Paper 2022)
  **Number of fields/sites:** 2 Felder
  **Est. independent site-years ≥2013:** ~2
  **Yield measure:** Soja-Ertrag an Rasterpunkten (Einheit nicht angegeben)
  **Extra info:** ECa, Bodenchemie/-textur
  **License:** CC BY 4.0
  **Access:** direkter Download (CSV 7 kB / 5 kB)
  **Preparation effort:** low
  **Rating:** 1–2
  **Status:** bestätigt — [Zenodo 13770031](https://zenodo.org/records/13770031)

- **Name:** Precision agricultural data and ecosystem services: can we put the pieces together? (Robinson, Schwinghamer, Carcamo, Galpern; Univ. Calgary / AAFC)
  **Link:** https://datadryad.org/dataset/doi:10.5061/dryad.5x69p8d90 (geöffnet)
  **Crop(s):** nicht angegeben (kanadische Prärie)
  **Country/region:** Kanada (vermutlich Alberta)
  **Location precision:** **anonymisiert** ("absolute location … anonymized for privacy") → nicht satellitentauglich
  **Area per unit (ha):** n/a
  **Years covered:** nicht angegeben
  **Number of fields/sites:** Beispiel-Yield-Monitor-Datei (examplePYD.csv, 824 kB)
  **Est. independent site-years ≥2013:** 0 nutzbar
  **Yield measure:** Yield-Monitor-Punkte
  **License:** CC0
  **Access:** direkter Download
  **Preparation effort:** n/a
  **Rating:** 1 (nur Methodik)
  **Status:** bestätigt — [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.5x69p8d90)

- **Name:** Soil Health and Nutrient Flows with Enhanced Cover Cropping and Soil Management: Corn and Soybean Yields During 3 Years of Cover Crop and Nitrogen Management (Stefun & Weil; Ag Data Commons)
  **Link:** https://doi.org/10.15482/usda.adc/28291097 (DataCite-Metadaten geöffnet; Landing-Page 403)
  **Crop(s):** Mais, Soja
  **Country/region:** CMREC Beltsville, Maryland, USA (zwei Felder unterschiedlicher Bodentextur) – räumlich nahe am ausgeschlossenen BARC-Archiv, aber eigener Datensatz
  **Location precision:** Feld benannt; Koordinaten in Metadaten leer
  **Area per unit (ha):** nicht angegeben
  **Years covered:** 3 Jahre (nicht benannt; Publikation 2025 → vermutlich ~2020–2023)
  **Number of fields/sites:** 2 Felder
  **Est. independent site-years ≥2013:** ~6
  **Yield measure:** Mähdrescher-Yield-Monitor + Handernte
  **Extra info:** Zwischenfrucht- und N-Stufen-Treatments; ergänzende Records 28303823, 28314515
  **License:** CC BY 4.0
  **Access:** direkter Download (Ag Data Commons)
  **Preparation effort:** medium
  **Rating:** 2
  **Status:** bestätigt (Metadaten) — [DataCite](https://api.datacite.org/dois/10.15482/usda.adc/28291097)

- **Name:** Data from: Interseeded cover crop mixtures influence soil water storage during the corn phase of corn-soybean-wheat no-till cropping systems (Ag Data Commons 10.15482/usda.adc/1528716; ICPSR-Kopie 10.3886/e250828)
  **Link:** https://doi.org/10.15482/usda.adc/1528716 (Redirect gesehen, Landing-Page nicht gelesen)
  **Crop(s):** Mais (im Corn-Soy-Wheat-System)
  **Country/region:** USA (Standort nicht geprüft)
  **Yield measure:** Mais-Ertrag kg/ha aus Mähdrescher-Yield-Monitor je Wiederholung/Treatment (laut DataCite-Beschreibung)
  **License:** vermutlich CC0/CC BY (USDA)
  **Access:** direkter Download
  **Rating:** 1–2 (Parzellenversuch)
  **Status:** unbestätigt (nur DataCite-Kurzbeschreibung) — [DataCite-Suche](https://api.datacite.org/dois?query=%22yield%20monitor%22%20AND%20types.resourceTypeGeneral:Dataset&page[size]=50)

- **Name:** Yields and field management data from 13 organic farms in Germany (Paulsen, Schmid, Klinkmann, Hülsbergen; Thünen/TUM; OrganicYieldsUP WA1)
  **Link:** https://zenodo.org/records/15632460 (geöffnet); Variablendefinitionen https://zenodo.org/records/15276083 (geöffnet)
  **Crop(s):** Ackerkulturen ökologischer Fruchtfolgen (nicht spezifiziert)
  **Country/region:** Deutschland – Bayern, Brandenburg, Mecklenburg-Vorpommern, NRW, Schleswig-Holstein
  **Location precision:** **keine Koordinaten/Geometrien angegeben** (nur Bundesland) → Schläge vermutlich anonymisiert
  **Area per unit (ha):** Praxisschläge (nicht angegeben)
  **Years covered:** 2008/2009–2017 (2013–2017 = 5 Jahre)
  **Number of fields/sites:** 526 Felder / 13 Betriebe
  **Est. independent site-years ≥2013:** mehrere hundert Feld-Jahre (nicht lokalisierbar)
  **Yield measure:** Betriebsaufzeichnungen, plausibilisiert über Nährstoff-/Massenbilanzen; Einheit in SQLite-Schema
  **Extra info:** SQLite (10,5 MB) mit Management (Fruchtfolge, Düngung)
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Preparation effort:** high (ohne Geometrien nur über Betriebsanfrage satellitentauglich)
  **Rating:** 2
  **Status:** bestätigt — [Zenodo 15632460](https://zenodo.org/records/15632460), [Orgprints 55954](https://orgprints.org/id/eprint/55954/)

- **Name:** 2022 & 2023 Hyper Yielding Crops Paddock Data (GRDC / FAR Australia / CeRDI)
  **Link:** https://zenodo.org/records/16255157 (geöffnet)
  **Crop(s):** Weizen, Gerste
  **Country/region:** Südaustralien – SA, TAS, VIC, WA
  **Location precision:** "site ID, location" – nur Regionsebene sichtbar; Koordinaten unklar
  **Area per unit (ha):** Praxisschläge (nicht angegeben)
  **Years covered:** 2022, 2023
  **Number of fields/sites:** >330 Paddocks
  **Est. independent site-years ≥2013:** >330 Paddock-Jahre
  **Yield measure:** Paddock-Ertrag + Ertragskomponenten, Kornqualität (Einheiten im Read-Me-Tab)
  **Extra info:** Inputs, Management, Boden
  **License:** "Other" – nur nach Vereinbarung mit den Daten-Miteigentümern
  **Access:** restricted; Zenodo-Request-Formular
  **Preparation effort:** high
  **Rating:** 2 (groß, aber Freigabe unsicher und Lage evtl. nur Ort)
  **Status:** bestätigt (Metadaten; Dateien gesperrt) — [Zenodo 16255157](https://zenodo.org/records/16255157)

- **Name:** DTI farmer's field yields (Danish Technological Institute; GATE-Plattform)
  **Link:** https://zenodo.org/records/23340318 (geöffnet; ältere Version 22894802)
  **Crop(s):** nicht genannt (dänische Praxisbetriebe; Keywords: crop type, sowing, harvesting)
  **Country/region:** Dänemark
  **Location precision:** CRS "in Metadaten dokumentiert" → Feldgeometrien wahrscheinlich, aber gesperrt
  **Years covered:** nicht genannt
  **Number of fields/sites:** nicht genannt
  **Yield measure:** Feld-Erträge aus Betriebsaufzeichnungen
  **License:** CC BY 4.0 nur für Metadaten/Data Dictionary (15 kB); Daten ohne öffentliche Lizenz
  **Access:** on request – schriftliches Data Access Agreement über GATE (https://app.dev.data-gate.io/), kein Kontakt genannt
  **Preparation effort:** high
  **Rating:** 2
  **Status:** bestätigt (nur Metadaten-Record) — [Zenodo 23340318](https://zenodo.org/records/23340318)

- **Name:** DIFM – Data-Intensive Farm Management On-Farm Precision Experiments (Bullock, Univ. Illinois)
  **Link:** https://publish.illinois.edu/data-intensive-farm-managment/ (Suchtreffer); OSF-API-Suche nach "DIFM"/"precision experiment" ergab 0 Treffer
  **Crop(s):** Mais, Soja, Weizen, Baumwolle, Gerste
  **Country/region:** USA (8 Staaten), Argentinien, Brasilien, Südafrika
  **Location precision:** Yield-Monitor auf ganzen Praxisfeldern; **keine offene Freigabe gefunden**
  **Area per unit (ha):** 10–100 ha je Versuch
  **Years covered:** 2016–heute (>120 Versuche 2019)
  **Yield measure:** Mähdrescher-Yield-Monitor, randomisierte N-/Saatstärken
  **License:** unbekannt
  **Access:** on request (D. S. Bullock, Univ. Illinois)
  **Preparation effort:** high
  **Rating:** 2
  **Status:** unbestätigt — [AGRIS Bullock et al. 2019](https://agris.fao.org/search/en/records/65de446a0f3e94b9e5ccb073)

- **Name:** Arable crop yield data for the Hillesden Experimental Platform, UK, 2006–2011 (UKCEH/EIDC)
  **Link:** https://catalogue.ceh.ac.uk/id/e54069b6-71a9-4b36-837f-a5e3ee65b4de
  **Crop(s):** Winterweizen, Raps, Ackerbohne
  **Country/region:** Buckinghamshire, UK
  **Years covered:** 2006–2011 → **kein Jahr ≥2013** (Ausschluss)
  **Yield measure:** Mähdrescher-Yield-Meter, t/ha
  **License:** UKCEH OGL
  **Rating:** 1
  **Status:** bestätigt (Metadaten) — [NERC catalogue](https://data-search.nerc.ac.uk/geonetwork/srv/api/records/e54069b6-71a9-4b36-837f-a5e3ee65b4de)

- **Name:** Hunt et al. 2019, High resolution wheat yield mapping using Sentinel-2 (RSE 233) – 39 Weizenfelder, >8.000 Yield-Monitor-Punkte, UK
  **Link:** https://nora.nerc.ac.uk/id/eprint/525234/ (geöffnet) – **kein Daten-DOI**; Daten nicht veröffentlicht
  **Status:** unbestätigt / nicht offen — [NORA](https://nora.nerc.ac.uk/id/eprint/525234/)

- **Name:** Rostěnice-Farm Yield-Monitor-Daten (Masaryk Univ./CzechGlobe; CASE-IH) – **sind über YIPEEO (KQ 2) offen verfügbar**: YIPEEO-D4.2 nennt "field-level data from Czechia (Rostenice farm)" und Polkovice als Feldebene-Referenz
  **Status:** bestätigt via YIPEEO — [MUNI publication](https://is.muni.cz/publication/1577857/cs), [YIPEEO D4.2](https://yipeeo.czechglobe.cz/documents/deliverables/D4.2_ExperimentalDatasetDescription.pdf)

- **Name:** R-Paket-Beispieldaten (nur Historie, <2013): agridat::gartner.corn (Mais, Mankato MN, 2011, Monitor-Rohpunkte) — [CRAN](https://search.r-project.org/CRAN/refmans/agridat/html/gartner.corn.html); agridat::lasrosas.corn / ArgentinAPI::corn_nitrogen_df (Mais, Las Rosas, Córdoba, Argentinien, 1999/2001, 3.443 Monitorpunkte mit lat/lon, N-Stufen) — [CRAN ArgentinAPI](https://cran.r-project.org/web/packages/ArgentinAPI/refman/ArgentinAPI.html). Rating 1, Status bestätigt (Dokumentation).

- **Nicht geeignet / Modellausgaben (geöffnet, ausgeschlossen):** NortheastChinaMaizeYield10m (Zenodo 21542062, WOFOST-trainiert) — [Zenodo](https://zenodo.org/records/21542062); SCYM Maize Yield Maps US Corn Belt 1999–2018 (Zenodo 4267589, Landsat-Modell) — [Zenodo](https://doi.org/10.5281/zenodo.4267589); GATE Annual crop yield predictions Denmark 2017–2024 (Zenodo 23010549, XGBoost, "not ground truth") — [Zenodo](https://doi.org/10.5281/zenodo.23010549); national 30-m China yield 2024 (Zenodo 22023328, GPP-Modell); CSIRO AgriYieldz (simuliert, kostenpflichtig) — [CSIRO](https://agdatashop.csiro.au/agriyieldz-the-wheat-crop-production-estimator); CropNet (County) — [HF](https://huggingface.co/datasets/CropNet/CropNet); Mendeley hz75rs73yt Soja Brasilien (regional) — [Mendeley](https://data.mendeley.com/datasets/hz75rs73yt/2); Zingg et al. 2024 Dryad hmgqnk9nf (7.727 Schlag-Erträge CH 2012–2016, aber nur Landschafts-ID, keine Koordinaten) — [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.hmgqnk9nf).

- **Repository-API-Ergebnisse (Trefferzahlen):** Dryad API "yield monitor" OR "yield map": 0 Treffer — [Dryad API](https://datadryad.org/api/v2/search?q=%22yield+monitor%22+OR+%22yield+map%22&per_page=50); Harvard Dataverse: 2 Treffer, 1 relevant (DANS PVCRIL, Äthiopien) — [Dataverse API](https://dataverse.harvard.edu/api/search?q=%22yield+monitor%22+OR+%22yield+map%22&type=dataset&per_page=50); figshare API: keine relevanten Datasets — [figshare API](https://api.figshare.com/v2/articles?search_for=%22yield%20monitor%22%20OR%20%22yield%20map%22&page_size=50&item_type=3); DataCite "yield monitor" Datasets: 17 Treffer (BARC-Archiv, Beltsville Cover Crop, Interseeded Cover Crop, Dryad 5x69p8d90, figshare Zuckerrohr 11452206, AgroIBIS Iowa State) — [DataCite](https://api.datacite.org/dois?query=%22yield%20monitor%22%20AND%20types.resourceTypeGeneral:Dataset&page[size]=50); Mendeley Data research-data-API ignorierte Suchbegriffe (keine verwertbaren Treffer); PANGAEA: nur ein kenianischer Maisversuch 2019/20 (10.1594/pangaea.923246) — [DataCite PANGAEA](https://api.datacite.org/dois?query=publisher:PANGAEA%20AND%20(%22crop%20yield%22%20OR%20%22grain%20yield%22)%20AND%20(field%20OR%20farm)&page[size]=40); 4TU und ScienceDB: nur JS-Oberflächen, nicht abfragbar; Zenodo REST: Phrasensuche "yield monitor" 2.326 Treffer (überwiegend irrelevant), "yield map(s)" 57.643 (Volltext) – relevante Records oben gelistet.

### Inferences
- Für Österreich-nahe Übertragung sind YIPEEO (CZ/SK) und der ETH-CH-TAN-Datensatz die einzigen offenen Quellen mit echter Feldgeometrie im mitteleuropäischen Klimaraum; alles andere aus Repositories ist Einzelfeld-Demo oder anonymisiert.
- Zugriffsbeschränkte Zenodo-Records (DWFI, GRDC, DTI) sind für ein nicht-kommerzielles Schülerprojekt anfragbar, aber mit Vertraulichkeitsklauseln – Daten dürften nicht weitergegeben/publiziert werden.

### Gaps
- Nicht gefunden (trotz Zenodo-/DataCite-/Mendeley-Suche in EN/DE/ES/PT/FR): "Yield maps from 7 Danish fields", KU-Leuven-Ertragskarten, Agroscope-Ertragskarten (nur CH-TAN/ETH), Mato-Grosso-/Paraná-Yield-Maps, Ohio/Indiana-Mais-Yield-Maps auf Mendeley, offene Daten zu Leroux/Vega-Filterpapieren, Kasachstan/Ukraine-Feldebene außer YIPEEO-UA.
- Mendeley Data konnte nur über eine unzuverlässige API abgefragt werden; Kaggle-Datasets-API erfordert Login (nicht geprüft).

---

## Key Question 2: ML-Benchmarks / Competitions mit gemessenen Feld-Erträgen und Koordinaten

### Takeaway
Die meisten Benchmarks sind County-/Regionsebene (SustainBench, CropNet, CY-Bench). Mit echten Feldpolygonen und gemessenen Erträgen existiert offen vor allem die ESA/YIPEEO-Sammlung "Yield Data at Field Level" (1.954 Feld-Jahre, CZ/SK/NL/UA, 2015–2023, 14 Kulturen); daneben Plot-/Standortebene: G2F (Mais, PDDL), Dryad Multistate Maize Trials 2022, SICKLE (Indien, auf Anfrage), figshare Haridwar (Indien, Smallholder), DANS Äthiopien (restricted). Syngenta Crop Challenge ist anonymisiert.

### Cited Findings

- **Name:** YIPEEO – Yield Data at Field Level (ESA Open Science Catalog / EarthCODE; TU Wien, CzechGlobe, EODC; ESA EXPRO+)
  **Link:** STAC-Metadaten https://esa-earthcode.github.io/open-science-catalog-metadata/products/yield-data-field-level/collection.json (geöffnet); Daten-Endpunkt https://features.services.eodc.eu/collections/pub_yipeeo_yield_fl (geöffnet, 1.954 Items, ohne Login als GeoJSON geladen); DOI 10.83395/zc92-3t58 (DataCite geöffnet)
  **Crop(s):** Sommergerste 487, Körnermais/CCM 411, Winterweichweizen 373, Winterraps 282, Silomais 112, Wintergerste 94, Soja 50, Zuckerrübe 41, Futtererbse 39, sonstige Ölsaaten 20, Kartoffel 18, Sommerweizen 12, Durum 8, Zwiebel 7 (Feld-Jahre; aus GeoJSON gezählt)
  **Country/region:** Tschechien 1.715 Feld-Jahre (Lon 16,8–17,1, Lat 48,9–49,3 → Rostěnice/Südmähren + Polkovice), Slowakei 120, Niederlande 86, Ukraine 33 (bei 31,0 E / 50,3 N)
  **Location precision:** MultiPolygon-Feldgeometrien in CRS84 (echte Koordinaten; 1.551 verschiedene Geometrien)
  **Area per unit (ha):** Median 14,2 ha; P10 1,7 ha; P90 43 ha; max 164 ha (aus Polygonen berechnet)
  **Years covered:** 2015 (3), 2016 (12), 2017 (101), 2018 (189), 2019 (283), 2020 (401), 2021 (438), 2022 (507), 2023 (20) – alle ≥2013; CZ 2017–2022, SK 2017–2023, NL 2016–2022, UA 2015–2022
  **Number of fields/sites:** 1.551 Feldgeometrien (CZ ~1.380, SK ~75, NL ~70, UA ~30); 4 Länder
  **Est. independent site-years ≥2013:** 1.954 Feld-Jahre (Felder mit 1–7 Jahren)
  **Yield measure:** Attribut `yield` (Feldmittel; Werte 1,8–117,8 → t/ha; Silomais/Zuckerrübe als Frischmasse; Feuchtebasis nicht dokumentiert – D4.2 nennt t/ha); Attribute: c_year, crop_id (EU-Code, z. B. C1111), crop_type, country_code, yield; **keine Feld-ID, keine Saat-/Erntedaten**
  **Extra info:** Companion "YIPEEO features" (vorprozessierte Sentinel-1/2-Features 2015–2022) https://opensciencedata.esa.int/products/yipeeo-features/collection ; Modellvalidierung im D4.2 (XGB field-level CZ: R² bis 0,86 Körnermais, RMSE 0,44 t/ha bei LT1); Austria nur auf NUTS4-Ebene im Projekt
  **License:** **Widerspruch**: DataCite/OSC-Metadaten "proprietary", EODC-Collection heißt "(public)" und ist ohne Authentifizierung abrufbar → Nutzungsrecht vor Verwendung bei TU Wien klären (Kontakt laut D4.2: Emanuel Büechi, emanuel.bueechi@geo.tuwien.ac.at; Projektleitung Wouter Dorigo)
  **Access:** direkter Download (OGC API Features, GeoJSON, limit=1000/offset)
  **Preparation effort:** low (bereits Polygone + Jahr + Kultur + Ertrag)
  **Rating:** 5 (größte offene Feldebene-Quelle Mitteleuropas; Lizenz klären)
  **Status:** bestätigt — [EODC collection](https://features.services.eodc.eu/collections/pub_yipeeo_yield_fl), [OSC STAC](https://esa-earthcode.github.io/open-science-catalog-metadata/products/yield-data-field-level/collection.json), [DataCite 10.83395/zc92-3t58](https://api.datacite.org/dois/10.83395/zc92-3t58), [YIPEEO project](https://yipeeo.czechglobe.cz/), [EarthCODE forum](https://discourse-earthcode.eox.at/t/yield-data-at-field-level-is-now-available-on-earthcode/55)

- **Name:** Genomes to Fields (G2F) – Maize G×E, Jahresreleases 2014–2023 + GxE Prediction Competitions 2022 und 2024 (CyVerse Data Commons)
  **Link:** https://www.genomes2fields.org/resources/ (geöffnet; DOIs: 2023 10.25739/rzzy-3n27, 2022 10.25739/3d3g-pe51, 2021 10.25739/5ae3-sw62, 2020 10.25739/hzzs-a865, 2019 10.25739/t651-yy97, 2018 10.25739/anqq-sg86, 2017 10.25739/w560-2114, 2016 10.25739/yjnh-kt21, 2015 10.25739/erxg-yn49, 2014 10.25739/9wjm-eq41; 2024-Competition 10.25739/78mn-4394 geöffnet; 2022-Competition 10.25739/tq5e-ak26)
  **Crop(s):** Mais (Hybride)
  **Country/region:** USA + Kanada, ~45 Standorte/Jahr; >280 Umwelten gesamt
  **Location precision:** Standort-Metadaten (Versuchsstation; Koordinaten in Metadaten-Dateien laut 2022-Competition-Paper; auf CyVerse-Seite nicht explizit)
  **Area per unit (ha):** Plots (<0,01 ha) – nur als Standort-Mittel satellitentauglich (Versuchsfelder oft wenige ha)
  **Years covered:** 2014–2024
  **Number of fields/sites:** ~280 Standort-Jahre, >180.000 Plots
  **Est. independent site-years ≥2013:** ~280
  **Yield measure:** Kornertrag (bu/ac bzw. Mg/ha bei 15,5 % Feuchte – aus 2022-Competition-Paper; auf CyVerse-Seite nicht genannt)
  **Extra info:** Saat-/Erntedatum, Boden, Wetter, Genotypen; MLCAS 2021 Challenge basierte auf G2F-Genotyp×Wetter (eval.ai 1251)
  **License:** Open Data Commons PDDL (2024-Competition-Record); Website-Footer "All Rights Reserved"
  **Access:** direkter Download (CyVerse anonymous)
  **Preparation effort:** medium (Plots → Standortmittel; Standorte klein)
  **Rating:** 3
  **Status:** bestätigt — [G2F resources](https://www.genomes2fields.org/resources/), [CyVerse 2024 competition](https://dc.cyverse.org/dataset/genomes_to_fields_2024_maize_genotype_by_environment_prediction_competition), [BMC Res Notes 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10353085)

- **Name:** Crop performance, aerial, and satellite data from multistate maize yield trials (Shrestha, Powadi, Davis et al.; UNL / Iowa State; Dryad)
  **Link:** https://datadryad.org/dataset/doi:10.5061/dryad.905qftttm (geöffnet)
  **Crop(s):** Mais (>80 Hybride)
  **Country/region:** USA – Scottsbluff NE, Lincoln NE, Missouri Valley IA, Ames IA, Crawfordsville IA (North Platte ohne Bilder); keine Koordinaten im Record
  **Location precision:** Plot-Ebene mit Pléiades-Neo-Ausschnitten; Standorte benannt (Versuchsstationen findbar)
  **Area per unit (ha):** Plots; einige Standorte 2 Felder
  **Years covered:** 2022
  **Number of fields/sites:** 5–6 Standorte, >20.000 Plot-Bilder
  **Est. independent site-years ≥2013:** ~7 Feld-Jahre (Standortmittel)
  **Yield measure:** bu/ac bei 15,5 % Feuchte
  **Extra info:** Pléiades Neo 30 cm, 6 Bänder, 6 Termine; UAV-RGB 3 Termine; Saatdatum, Bestandeszahl, Anthese-GDD; 3,2 GB
  **License:** Dryad-Standard (CC0 üblich; Pléiades-PNGs © Airbus DS 2022)
  **Access:** direkter Download
  **Preparation effort:** medium
  **Rating:** 2 (Plotebene, 1 Jahr)
  **Status:** bestätigt — [Dryad 905qftttm](https://datadryad.org/dataset/doi:10.5061/dryad.905qftttm)

- **Name:** MLCAS 2024 "Corn Yield Prediction Using Satellite Data" (EvalAI Challenge 2332; Iowa State Univ.)
  **Link:** https://github.com/igorkf/MLCAS2024 (README geöffnet; Daten via ISU-Box-Link, EvalAI-Seite lädt nur per JS)
  **Crop(s):** Mais (Hybrid-Plots, vermutlich G2F-Standorte)
  **Country/region:** USA, Standorte nicht im README
  **Years covered:** 2022 (Train), 2023 (Train/Val/Test)
  **Yield measure:** Plot-Ertrag (Einheit nicht genannt)
  **Extra info:** Multispektral-Satellitenbilder je Plot
  **License:** nicht angegeben (Challenge-Bedingungen)
  **Access:** Box-Download über Challenge
  **Rating:** 2
  **Status:** unbestätigt (Datensatzbeschreibung nicht einsehbar) — [GitHub igorkf/MLCAS2024](https://github.com/igorkf/MLCAS2024), [MLCAS 2024 workshop](https://aiinstitutes.org/events/2024-10-07)

- **Name:** SICKLE – multi-sensor satellite + ground data, Cauvery Delta, Tamil Nadu (Sani et al.)
  **Link:** https://github.com/Depanshu-Sani/SICKLE (geöffnet)
  **Crop(s):** Reis (paddy-fokussiert; 21 Kulturtypen annotiert)
  **Country/region:** Cauvery-Delta, Tamil Nadu, Indien
  **Location precision:** Parzellen (Geometrien nicht auf Seite beschrieben)
  **Area per unit (ha):** Ø 0,38 acre ≈ 0,15 ha
  **Years covered:** Satellit 2018–03/2021; Feldaufnahme 01/2021–02/2022
  **Number of fields/sites:** 388 Parzellen, 2.370 Zeitreihen
  **Est. independent site-years ≥2013:** ~400–800 Parzellen-Saisons
  **Yield measure:** Parzellenertrag (Einheit nicht genannt)
  **Extra info:** Landsat-8, Sentinel-1, Sentinel-2; Annotationen 3/10/30 m
  **License:** nicht angegeben
  **Access:** on request (Formular; Testset zurückgehalten)
  **Preparation effort:** medium
  **Rating:** 2 (Reis, Kleinstparzellen)
  **Status:** bestätigt — [GitHub SICKLE](https://github.com/Depanshu-Sani/SICKLE)

- **Name:** DATASET: Field area, not canopy greenness, governs object-based crop yield models in fragmented smallholder systems (Akash Kumar; figshare)
  **Link:** https://doi.org/10.6084/m9.figshare.33158120 (DataCite-Metadaten geöffnet; figshare-Seite 403)
  **Crop(s):** Reis (Kharif 2024), Weizen (Rabi 2024/25)
  **Country/region:** Gummawala, Roorkee, Haridwar, Uttarakhand, Indien (29,95 N, 77,92 E; ~485 ha)
  **Location precision:** 1.983 Feldpolygone (SAM 2.1 auf superaufgelöstem Sentinel-2, GeoPackage EPSG:4326) + GPS-Referenzpolygone der 17 Reis-/47 Weizen-Erhebungsfelder
  **Area per unit (ha):** Smallholder (<1 ha; Bigha-Umrechnung)
  **Years covered:** 2024, 2024/25
  **Number of fields/sites:** 64 erhobene Felder
  **Est. independent site-years ≥2013:** 64
  **Yield measure:** Crop-Cut 3–5 Quadrate à 2×2 m, auf Standardfeuchte korrigiert, auf Feld skaliert
  **Extra info:** Sentinel-1/2-Zeitreihen, Phänologie-Features, Skripte
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Preparation effort:** low–medium
  **Rating:** 2
  **Status:** bestätigt (DataCite) — [DataCite 10.6084/m9.figshare.33158120](https://api.datacite.org/dois/10.6084/m9.figshare.33158120)

- **Name:** Field Data Collection Methods Strongly Affect Satellite-Based Crop Yield Estimation – Supplemental data (Tiedeman et al.; CIMMYT/UC Davis)
  **Link:** https://zenodo.org/records/6471977 (geöffnet)
  **Crop(s):** Mais (laut Paper)
  **Country/region:** Äthiopien
  **Location precision:** nur aggregierte CSV (140 kB); Koordinaten nicht ersichtlich
  **Years covered:** nicht genannt (Publikation 2022)
  **Number of fields/sites:** 196 Felder, 8 Erhebungsmethoden
  **Yield measure:** Crop-Cut/Farmer-Report etc.
  **Extra info:** aggregierte Sentinel-2-VIs
  **License:** CC BY 4.0
  **Access:** direkter Download
  **Rating:** 2
  **Status:** bestätigt — [Zenodo 6471977](https://zenodo.org/records/6471977)

- **Name:** Crop Growth and Yield Monitoring in Smallholder Agricultural Systems: A Multi-Sensor Data Fusion Approach (DANS Data Station)
  **Link:** https://phys-techsciences.datastations.nl/citation?persistentId=doi:10.17026/PT/PVCRIL (geöffnet)
  **Crop(s):** Reis, Mais
  **Country/region:** Tana-Becken, Äthiopien
  **Years covered:** 2019–2020
  **Yield measure:** Crop-Cut + Farmer-Angaben
  **License:** CC BY 4.0, aber 6 von 7 Dateien restricted (Anfrage nötig)
  **Rating:** 1–2
  **Status:** bestätigt — [DANS PVCRIL](https://phys-techsciences.datastations.nl/citation?persistentId=doi:10.17026/PT/PVCRIL)

- **Name:** Syngenta Crop Challenge in Analytics (INFORMS) – z. B. 2018: 2.267 Hybride, 2.247 Standorte, 2008–2016, 148.452 Ertragsproben
  **Link:** https://www.syngenta-us.com/newsroom/2018-syngenta-crop-challenge-in-analytics-winner-announced
  **Location precision:** **anonymisiert/normalisiert** → ungeeignet
  **Status:** bestätigt als Beschreibung; ausgeschlossen — [arXiv 1902.02860](https://arxiv.org/pdf/1902.02860)

- **Name:** Datensatz Zuckerrohr São Paulo (Barbosa et al., Data in Brief 2026; HuggingFace lafbarbosa/sugarcane_dataset_northeast_sao_paulo_state_brazil)
  **Link:** https://huggingface.co/datasets/lafbarbosa/sugarcane_dataset_northeast_sao_paulo_state_brazil (geöffnet)
  **Crop(s):** Zuckerrohr (keine Priorität)
  **Country/region:** Nordost-São Paulo, Brasilien, kommerzielle Felder
  **Yield measure:** Feld-Ertrag + Umwelt + Wetter + Sentinel-2-Bilder; Anzahl/Jahre nicht sichtbar (gated)
  **License:** CC BY-NC 4.0
  **Access:** Registrierung + Kontaktfreigabe (gated)
  **Rating:** 1 (Kultur außerhalb Priorität)
  **Status:** bestätigt (Metadaten) — [HF dataset](https://huggingface.co/datasets/lafbarbosa/sugarcane_dataset_northeast_sao_paulo_state_brazil), [Crossref DIB 2026.112549](https://api.crossref.org/works/10.1016/j.dib.2026.112549)

- **HuggingFace-Sweep (API, "crop yield", 60 Treffer):** keine Feldebene mit gemessenen Erträgen und Koordinaten; County/Regional: CropNet, notadib/usa-corn-belt-crop-yield, onef1shy/Crop-Yield-Prediction-MODIS, torchgeo/sustainbench_crop_yield, 0x365/crop-yield-eu (NUTS2), hkaman/california-crop-yield-benchmark; mindweave/agricultural-crop-yields ist **simuliert** — [HF API](https://huggingface.co/api/datasets?search=crop%20yield&limit=60&full=false)
- **Scientific Data (Crossref-Suche):** keine Yield-Monitor-Datensätze; Feld-/Standortebene nur: "A century-scale dataset of crop yield and agronomic trait evolution under field management in China" (22.017 georeferenzierte Einträge, 802 Standorte, Reis/Weizen/Mais/Soja/Raps, überwiegend Langzeitversuche) — [10.1038/s41597-026-07545-0](https://doi.org/10.1038/s41597-026-07545-0); Bushland-TX-Lysimeter-Sammlungen (Mais 1989–2018, 4,4-ha-Felder, Stationskoordinaten) — [10.1038/s41597-025-04539-2](https://doi.org/10.1038/s41597-025-04539-2) (Mais nur 2013, 2016, 2018 ≥2013; Status unbestätigt für Feldgeometrie)
- **Data in Brief (Crossref):** keine Yield-Monitor-Datensätze mit Koordinaten außer Zuckerrohr São Paulo (oben) — [Crossref DIB](https://api.crossref.org/works?query=%22yield+monitor%22+OR+%22yield+map%22+combine+harvester+dataset&filter=container-title:Data+in+Brief&rows=25&select=title,DOI,issued,abstract)

### Inferences
- YIPEEO deckt genau die Zielkulturen (Mais, Winterweizen, Gerste, Raps, Soja, Zuckerrübe) in einem an Österreich angrenzenden Klimaraum (Südmähren) ab und liefert sofort nutzbare Polygone; die ungeklärte Lizenz ("proprietary" vs. "public") ist das Hauptrisiko und sollte per E-Mail an TU Wien geklärt werden.
- G2F ist der einzige große offene US-Benchmark mit Standortinformation; die Plotgröße erzwingt Aggregation auf Standort-Jahr.

### Gaps
- MLCAS-2024-Datensatz (Standorte, Lizenz) nicht einsehbar (EvalAI nur JS, Box-Link).
- Kaggle und Source Cooperative konnten nicht programmatisch durchsucht werden (Login/JS); keine Feldebene-Yield-Benchmarks dort bekannt.

---

## Key Question 3: Flux-Tower-Netzwerke – Ertragsdaten als Zusatzdaten

### Takeaway
Weder AmeriFlux-BADM noch FLUXNET-BADM haben eine standardisierte Ertragsvariable (keine Gruppen AG_PROD/GRAIN_YIELD; DM_AGRICULTURE enthält nur Ereignistyp/Datum; BIOMASS-Gruppe erlaubt ORGAN="Seeds" in kgDM/m²). Erträge an Flux-Sites sind daher nur über Einzel-Datensätze (Ag Data Commons, ETH, Dryad) oder PI-Kontakt erreichbar. ICOS liefert für Cropland-Stationen per Protokoll AGB bei Ernte und Management; die Ertragsableitung erfordert Parsing der ETC-L2-ARCHIVE-Ancillary-Dateien (CC BY 4.0, ohne Login).

### Cited Findings

- **Name:** AmeriFlux – Cropland-Sites (IGBP CRO) und BADM
  **Link:** Site-API https://amfcdn.lbl.gov/api/v1/site_display/AmeriFlux (abgefragt: 849 Sites, **213 CRO**); BADM-Gruppenübersicht https://ameriflux.lbl.gov/data/badm/badm-standards/ (geöffnet); DM_AGRICULTURE https://ameriflux.lbl.gov/data/badm/badm-standards/DM_AGRICULTURE (geöffnet); BIOMASS https://ameriflux.lbl.gov/data/badm/badm-standards/BIOMASS (geöffnet); AG_PROD und AG_BIOMASS existieren **nicht** ("BADM Group Not Found")
  **Crop(s):** je Site (Mais/Soja-Rotationen Corn Belt, Weizen Montana/Washington/Idaho, Reis Arkansas/Kalifornien, Sorghum Oklahoma/Texas, Baumwolle, Luzerne, Zuckerrohr Hawaii)
  **Country/region:** USA (überwiegend), Kanada (CA-ER1/2 Elora, CA-KT1/2 Kenton, CA-MA1/2 Manitoba, CA-ST1/2 South Tobacco Creek, CA-CRB Carberry, CA-TPA), Argentinien (AR-Bal Balcarce, AR-CCa Carlos Casares), Brasilien (BR-CMT Capuaba Mato Grosso, BR-PRS, BR-SM1 Reis), Costa Rica (CR-Fsc, CR-Nmr)
  **Location precision:** Tower-Koordinaten exakt (Site-Seiten); Feld um Tower typ. 10–60 ha
  **Years covered:** je Site; viele ≥2013 (z. B. US-IS1/2/3 Illinois SmartFarm, US-UiC/UiG Illinois Maize-Soy, US-GZ1-3 Genesee ID, US-SZ1-3 St. John WA, US-MC1/2 Creston MT Sommerweizen, US-MH1/2 Huntley MT Gerste, US-MSR/MVW/Mj1 Montana Winterweizen, US-Ro1–Ro6/RSI/RSV Rosemount MN, US-Br1/2/3 Brooks IA, US-Bo1/Bo2 Bondville IL, US-ARM/OK1/OK2 Oklahoma, US-CRT Ohio, US-Tw2/Bi2/DS1/DS2 California Mais, US-MN1/2/3 Morris MN, US-NP1/NP2 Mandan ND, US-SD1/SD2 + US-VT1/VT2 Indiana paired croplands, US-CS1–CS8 Central Sands WI, US-RC1–RC5 Cook Agronomy Farm WA) – Datenzeiträume in der API-Antwort leer, auf Site-Seiten einsehbar
  **Number of fields/sites:** 213 CRO-Sites gelistet (Liste vollständig in Scratch-Auswertung; Auswahl oben)
  **Est. independent site-years ≥2013:** unbekannt – **BADM enthält keine Ertragsvariable**; Erträge nur, wenn PI sie als BIOMASS (ORGAN=Seeds, kgDM/m² oder gC/m²) meldet
  **Yield measure:** falls gemeldet: BIOMASS mit BIOMASS_ORGAN="Seeds"/"Reproductive bodies", Einheit kgDM m⁻² (Trockenmasse) oder gC m⁻²; keine Feuchtestandardisierung
  **Extra info:** DM_PLANTING, DM_AGRICULTURE (Harvest-Datum), DM_FERT_M/O, DM_TILL, DM_WATER, DM_EXT_WEATHER (Extremwetter-Ereignisse!), LAI, SOIL_*; Fluxdaten halbstündlich
  **License:** AmeriFlux CC-BY-4.0 (Registrierung, Nutzungsangabe)
  **Access:** Registrierung + Download (BIF-Datei je Site)
  **Preparation effort:** high
  **Rating:** 2 (als Ertragsquelle unsicher; DM_EXT_WEATHER + Flux als Stress-Kontext wertvoll)
  **Status:** bestätigt (Site-Liste, BADM-Struktur); Ertragsverfügbarkeit je Site **unbestätigt** — [AmeriFlux BADM standards](https://ameriflux.lbl.gov/data/badm/badm-standards/), [DM_AGRICULTURE](https://ameriflux.lbl.gov/data/badm/badm-standards/DM_AGRICULTURE), [BIOMASS](https://ameriflux.lbl.gov/data/badm/badm-standards/BIOMASS), [US-OK2 site](https://ameriflux.lbl.gov/sites/siteinfo/US-OK2), [US-NP2 site](https://ameriflux.lbl.gov/sites/siteinfo/US-NP2)

- **Name:** Data from: Carbon Fluxes from a Spring Wheat-Corn-Soybean Crop Rotation Under No-Tillage Management (Saliendra, Liebig, Archer; USDA-ARS Mandan ND; Ag Data Commons 10.15482/usda.adc/1528734; ICPSR-Kopie 10.3886/e250837) – entspricht AmeriFlux US-NP1/US-NP2 (Mandan "mandanh5"/"mandani2")
  **Link:** https://api.datacite.org/dois/10.15482/usda.adc/1528734 (geöffnet; Landing-Page 403)
  **Crop(s):** Sommerweizen, Mais, Soja
  **Country/region:** Mandan, North Dakota, USA (gepaarte Felder gleicher Bodenart)
  **Location precision:** Tower-Koordinaten über AmeriFlux US-NP1/NP2
  **Area per unit (ha):** nicht angegeben
  **Years covered:** 2016–2018 (laut DataCite-Suchtreffer)
  **Number of fields/sites:** 2 Felder
  **Est. independent site-years ≥2013:** 6
  **Yield measure:** Kornertrag + oberirdische Biomasse (Einheit nicht angegeben)
  **Extra info:** EC-CO2/H2O-Flüsse, Wetter, Bodenfeuchte, Phänologie, LAI
  **License:** nicht angegeben (USDA i. d. R. CC0)
  **Access:** direkter Download
  **Preparation effort:** low
  **Rating:** 2
  **Status:** bestätigt (Metadaten) — [DataCite](https://api.datacite.org/dois/10.15482/usda.adc/1528734)

- **Name:** ICOS Ecosystem – Cropland-Stationen und ETC-Produkte
  **Link:** SPARQL https://meta.icos-cp.eu/sparql (abgefragt); Stationsseite https://meta.icos-cp.eu/resources/stations/ES_DE-Kli (geöffnet); ETC L2 ARCHIVE Spezifikation https://meta.icos-cp.eu/resources/cpmeta/etcArchiveProduct (geöffnet); Ecosystem Release 2026-1 https://www.icos-cp.eu/data-products/ecosystem-release (geöffnet; DOI 10.18160/S6TB-567H, 42 Stationen, 5,9 GB); Lizenz https://www.icos-cp.eu/data-services/about-data-portal/data-license (geöffnet)
  **Crop(s):** Fruchtfolgen je Station (DE-Kli: Raps, Winterweizen, Silomais, Sommer-/Wintergerste)
  **Country/region:** Cropland-Stationen laut ICOS-Metadaten (inkl. Nicht-ICOS-Altstationen): BE-Lon Lonzée, BE-Wm2 Westmalle2, CH-For Forel, CH-Oe2 Oensingen, CH-Tnk Tänikon, CZ-KrP Křešín u Pacova, DE-Brs Braunschweig, DE-Geb Gebesee, DE-Hdn Heydenhof, DE-Kli Klingenberg (50,89306 N, 13,52238 E, 478 m), DE-Rns Reinshof, DE-RuM Merzenhausen, DE-RuS Selhausen Jülich, DE-Seh Selhausen, DK-Fou Foulum, DK-Vng Voulundgaard, FI-Jok Jokioinen, FI-Pap, FI-Qvd Qvidja, FI-Ruk Ruukki, FI-Sar, FR-Aur Auradé, FR-EM2 Estrées-Mons, FR-Gri Grignon, FR-Lam Lamasquère, IE-CaC/IE-CaN Carlow, IE-Gwr Gowran, IT-BCi Borgo Cioffi, IT-CA2 Castel d'Asso2 (+ CN-, JP-, BJ-Stationen) – **keine österreichische Cropland-Station** (AT-Mmg Wald, AT-Neu Grünland)
  **Location precision:** Tower-Koordinaten exakt; Feld um Tower typ. 10–30 ha
  **Years covered:** ICOS-Label ab 2018/2019 (DE-Kli 2019-05-22); EC seit 2004 (DE-Kli)
  **Number of fields/sites:** ~30 europäische Cropland-Stationen in den Metadaten; 42 labelled Stationen aller Ökosysteme im Release 2026-1
  **Est. independent site-years ≥2013:** grob 100–200 Stations-Jahre (Schätzung; Ertragsfelder nicht geprüft)
  **Yield measure:** laut Cropland-Protokoll und Labelling-Report: AGB bei Maximum/Ernte (destruktiv, Trockenmasse), Ernterückstände, Management (Saat, Düngung, Bodenbearbeitung, Ernte-Datum); **expliziter Kornertrag nicht als Pflichtvariable**; Ancillary-Objekte vom Typ "ICOS ETC Ancillary Raw BIF" waren per SPARQL nur für BE-Bra sichtbar → Ancillary-Daten stecken im ETC-L2-ARCHIVE-ZIP je Station
  **Extra info:** GAI/LAI, Bodenprofile, Flux, Meteorologie; DE-Kli-Report listet PAI/Biomasse 2005–2007, Düngung/Saat/Bodenbearbeitung
  **License:** CC BY 4.0 (kommerzielle Nutzung erlaubt; kein Account nötig, Lizenzakzeptanz beim Download; Datenlieferanten informieren)
  **Access:** direkter Download (Carbon Portal, Collection 10.18160/S6TB-567H)
  **Preparation effort:** high (ARCHIVE-ZIP je Station parsen; Trockenmasse-AGB → Kornertrag nur über Harvest-Index/Management-Angaben)
  **Rating:** 3 (Stationen in DE/CZ/CH klimatisch nahe; Ertrag indirekt)
  **Status:** teilweise bestätigt (Stationsliste, Lizenz, Produktstruktur; Ertragsvariablen im ARCHIVE nicht geöffnet) — [ICOS station DE-Kli](https://meta.icos-cp.eu/resources/stations/ES_DE-Kli), [ICOS release 2026-1](https://www.icos-cp.eu/data-products/ecosystem-release), [ICOS licence](https://www.icos-cp.eu/data-services/about-data-portal/data-license), [ICOS cropland protocol](https://b2find.eudat.eu/dataset/061dbe6a-9ca3-5e8d-873b-5169d266e1bf), [DE-Kli labelling report](https://www.icos-cp.eu/sites/default/files/cmis/DE-Kli%20Associated%20ICOS%20Ecosystem%20Station%20Labelling%20Report.pdf)

- **Name:** FLUXNET2015 BADM
  **Link:** https://fluxnet.org/data/badm-data-product/ (geöffnet); Templates https://fluxnet.org/data/badm-data-templates/ (geöffnet)
  **Yield measure:** **nur Site_General_Info und Disturbance_and_Management** verfügbar; Biomass-Template "being updated"; kein Ertrag
  **License:** FLUXNET2015 CC-BY-4.0 (Data Policies)
  **Rating:** 1 (als Ertragsquelle)
  **Status:** bestätigt — [FLUXNET BADM](https://fluxnet.org/data/badm-data-product/)

- **Name:** European Fluxes Database Cluster
  **Link:** http://www.europe-fluxdata.eu/home/data/data-policy (geöffnet); Sites-List nur JS
  **Access:** Registrierung; "Public" vs. "Restricted" (PI-Freigabe); keine Weitergabe erlaubt; Ancillary/Ertrag nicht erwähnt
  **Rating:** 1
  **Status:** bestätigt (Policy) — [EFDC data policy](http://www.europe-fluxdata.eu/home/data/data-policy)

- **Name:** OzFlux Cropland-Sites
  **Link:** https://www.ozflux.org.au/monitoringsites/index.html (geöffnet)
  **Sites:** AU-Cm1 Coleambally Mais/Weizen (2010–2011), AU-Cm2 Reis (2010–2011), Arcturus QLD (2011–2014, Kichererbse/Weizen), AU-Rgf Ridgefield WA (aktiv seit 2015, Dryland), AU-Rig Riggs Creek VIC (2010–2017, Dryland)
  **Yield measure:** keine Ertragsangaben auf der Seite
  **Rating:** 1
  **Status:** bestätigt (Siteliste; Erträge unbestätigt) — [OzFlux sites](https://www.ozflux.org.au/monitoringsites/index.html)

- **Name:** AsiaFlux: nicht geprüft (Gap).

- **Weitere Flux-Site-Ertragsdatensätze (DataCite "eddy covariance" + "crop/grain yield"):** Dryad 10.5061/dryad.224rg77 (KBS CRP→Bioenergie 2009–2016; **KBS = ausgeschlossen**); Harvard Dataverse 10.7910/DVN/23307 (IRRI, Reis/Mais 2011–2012, <2013) — [DataCite-Suche](https://api.datacite.org/dois?query=%22eddy%20covariance%22%20AND%20(%22crop%20yield%22%20OR%20%22grain%20yield%22)%20AND%20types.resourceTypeGeneral:Dataset&page[size]=40). Eine Kompilation "crop yields at flux sites" (Paper/Dataset) wurde **nicht gefunden**.

### Inferences
- Für Flux-Netzwerke ist der realistische Weg: Station auswählen (ICOS DE-Kli/DE-Geb/DE-RuS/CZ-KrP/CH-Oe2; AmeriFlux Montana/Washington-Weizen, Corn-Belt-Mais), ARCHIVE/BIF laden, Ertrag aus BIOMASS(Seeds)/AGB + Management ableiten oder PI anschreiben; der Aufwand pro Stations-Jahr ist hoch, die Anzahl (einige Dutzend bis ~200 Stations-Jahre) klein.

### Gaps
- Keine Site-genaue Liste, welche AmeriFlux-/ICOS-Stationen tatsächlich Kornerträge melden (erfordert BIF/ARCHIVE-Download mit Login bzw. Lizenzakzeptanz).
- AsiaFlux, FLUXNET-CH4 BADM nicht geprüft.

---

## Key Question 4: GitHub/HuggingFace-Repos mit Feldebene-Erträgen und Koordinaten

### Takeaway
GitHub enthält vor allem Werkzeuge zur Yield-Monitor-Bereinigung (cleanRfield, RITAS, pacu, YieldDataModels, IFAPA-Workflow) mit kleinen Beispieldateien, aber keine größeren offenen Feldebene-Ertragssammlungen; HuggingFace hat keine Feldebene-Yield-Benchmarks außer dem Zuckerrohr-Datensatz.

### Cited Findings
- GitHub-Suche "yield monitor data": filipematias23/cleanRfield (R-Paket, Filterung von Monitor-Punkten), luisdamiano/ritas-pkg (RITAS-Glättung), cldossantos/yield-monitor-simulations ("hosts the data and code" eines Methodenpapiers), BraulioIFAPA/Yield-monitor-data-cleaning (IFAPA, On-Farm-Trials, nach Vega et al.), PeterClaussenSDSU/YieldDataModels, Fayrouuzz/farm-timeseries-yield-egypt (Farm-Zeitreihen Ägypten, Labels unklar) — [GitHub API](https://api.github.com/search/repositories?q=%22yield+monitor%22+data&per_page=15&sort=stars). Keiner dieser Repos wurde auf Datenumfang/Lizenz geöffnet → Status unbestätigt.
- MLCAS-2024-Lösungsrepos (igorkf/MLCAS2024, xmba15, mingqianghan, Dudd3r) verweisen auf Box-Daten (s. KQ 2) — [GitHub igorkf](https://github.com/igorkf/MLCAS2024).
- pacu (R) nutzt ein 2012-Feld der Prairie-Strips-Studie als Vignette — [pacu vignette](https://cldossantos.r-universe.dev/pacu/doc/pacu_ym.html).

### Gaps
- cldossantos/yield-monitor-simulations und BraulioIFAPA könnten reale Monitor-Rohdaten (Iowa bzw. Andalusien) enthalten – nicht geöffnet.

---

## Key Question 5: Schadensereignisse (Hagel, Dürre, Frost, Überflutung) auf Feldebene mit Erträgen

### Takeaway
Offen gibt es keine Feldebene-Schadensdatenbank mit Erträgen; das Nächste sind gerasterte Versicherungs-Hagelschäden (Schweiz, 1–8 km, Anzahl geschädigter Felder, 2017–2021), County-Level-Versicherungsverluste (USA) und Parzellen-Lodging-Datensätze (Italien 2018, DANS).

### Cited Findings
- **Name:** Reported hail damage for 12 hail events in Switzerland (Portmann, Schmid, Villiger, Bresch, Calanca; Agroscope/ETH; CLIMADA)
  **Link:** https://zenodo.org/records/11064767 (geöffnet)
  **Crop(s):** Winterweizen, Mais (inkl. Silo), Wintergerste, Raps, Rebe; Aggregat "field crops"
  **Country/region:** Schweiz
  **Location precision:** Raster 1/2/4/8 km (keine Feldebene)
  **Years covered:** 2017–2021, 10–12 Hageltage
  **Yield measure:** kein Ertrag; Anzahl geschädigter Felder je Zelle (Schweizer Hagel-Versicherung)
  **Extra info:** Companion "Crop exposure Switzerland 2021" (Zenodo 11064756: Feldanzahl/Fläche je Zelle); EGUsphere-Preprint 2023-2598
  **License:** CC BY 4.0
  **Access:** direkter Download (2,5 MB)
  **Preparation effort:** medium (Kombination mit YIPEEO/INVEKOS-Feldern nur statistisch)
  **Rating:** 2 (Ereignisdaten mit Datum, aber ohne Feldzuordnung)
  **Status:** bestätigt — [Zenodo 11064767](https://zenodo.org/records/11064767), [Zenodo 11064756](https://doi.org/10.5281/zenodo.11064756)
- **Name:** Climatic damage cause variations of agricultural insurance loss, Pacific Northwest (Dryad 10.5061/dryad.hhmgqnknh): USDA-RMA-Claims 1989–2022, 24 Counties, Weizen/Äpfel, Dürre/Frost/Hagel – **County-Ebene**, Rating 1 — [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.hhmgqnknh)
- **Name:** Wheat lodging Ferrara 2018 (DANS 10.17026/dans-25w-q9zm closed; 10.17026/dans-xgf-267e): Feldbonituren Lagerung + Sentinel-1/2/RADARSAT-2, Italien, Mai–Juni 2018; EO4CerealStress Lodging-Karten Enschede 2023 (10.17026/pt/tfyjbn) – keine Erträge — [DataCite-Suche](https://api.datacite.org/dois?query=(%22crop%20damage%22%20OR%20%22hail%20damage%22%20OR%20%22frost%20damage%22%20OR%20lodging)%20AND%20(field%20OR%20parcel)%20AND%20(Sentinel%20OR%20yield)%20AND%20types.resourceTypeGeneral:Dataset&page[size]=40)
- **AmeriFlux BADM DM_EXT_WEATHER** (Extremwetter-Ereignisse mit Datum je Site) ist die einzige netzwerkweite, standardisierte Schadens-/Ereignisvariable, die mit Flux-Site-Erträgen kombinierbar wäre — [BADM groups](https://ameriflux.lbl.gov/data/badm/badm-standards/)
- Dryad/Zenodo-Suchen "hail/frost/flood + crop + field + yield" lieferten sonst nur Parzellenversuche mit Lodging-Scores (Pea CH 2022–23 Zenodo 23368412; WA subsoil acidity trials 10.83199/z04c-tz41) — [DataCite](https://api.datacite.org/dois?query=(%22crop%20damage%22%20OR%20%22hail%20damage%22%20OR%20%22frost%20damage%22%20OR%20lodging)%20AND%20(field%20OR%20parcel)%20AND%20(Sentinel%20OR%20yield)%20AND%20types.resourceTypeGeneral:Dataset&page[size]=40)

### Inferences
- Für Ertragsverlust-Labels bleibt der praktikable Weg, Schadensjahre aus Feld-Mehrjahresreihen (YIPEEO: Felder mit bis zu 7 Jahren) relativ abzuleiten, statt auf externe Schadensmeldungen zu hoffen.

### Gaps
- Keine offene Feldebene-Schadenskartei mit Erträgen gefunden (Versicherer-Daten bleiben verschlossen).

---

## Kurz-Ranking (für Tabelle)
1. YIPEEO Yield Data at Field Level (EODC/ESA) – Rating 5, bestätigt, Lizenz klären.
2. Kayad/Pirotti Mais Norditalien 2016–2018 (Zenodo 14216165) – 3, bestätigt.
3. ETH CH-TAN Winterweizen Yield-Map 2023/24 (10.3929/ethz-c-000807633) – 3, bestätigt (Metadaten).
4. G2F 2014–2024 (CyVerse, PDDL) – 3, bestätigt.
5. ICOS Cropland-Stationen ETC L2 ARCHIVE – 3, teilweise bestätigt.
6. DWFI MN/IA/NE Yield-Maps 2021–2024 (Zenodo, restricted) – 2; GRDC HYC >330 Paddocks (restricted) – 2; DTI Dänemark (DAA) – 2; AmeriFlux CRO-Sites – 2; Macdonald Colorado 2019–2022 – 2 (Akron-Dublette prüfen); figshare Haridwar – 2; SICKLE – 2; Dryad Multistate Maize 2022 – 2; German organic farms (ohne Geometrie) – 2; Swiss hail grid – 2.
