# Offene Feld-/Standort-Ertragsdaten USA & Kanada (Versuchsstationen, Langzeitversuche, Sortenversuche, On-Farm-Netzwerke, Flux-Standorte)

Stand: 2026-10-16. Recherchiert mit WebSearch/WebFetch; "bestätigt" = Link geöffnet und Daten/Metadaten gesehen, "unbestätigt" = nur über Suchtreffer/Sekundärquelle bekannt oder Seite nicht ladbar (403/404/JS). Ausgeschlossen laut Auftrag (nicht erneut gelistet): KBS LTER, BARC Beltsville, Colorado Akron dryland (Poss et al.), Mead US-Ne1/2/3, One Acre Fund, YieldSAT, CY-Bench.

Format pro Datensatz (exakt wie gefordert):
Name | Link | Crop(s) | Country/region | Location precision | Area per unit | Years covered (≥2013) | Number of sites/fields | Est. independent site-years ≥2013 | Yield measure/unit/moisture | Extra info | License | Access | Preparation effort | Rating 1–5 | Status

---

## KQ1: USDA Ag Data Commons / LTAR / ARS-Forschungsfarmen / AgCROS – welche Datensätze enthalten Feld-/Parzellenerträge mit Koordinaten ≥2013?

### Takeaway
Die LTAR-Common-Experiment-Ertragsmessung ist über protocols.io standardisiert (Yield-Monitor-Protokolle mit DOI), aber die eigentlichen LTAR-Ertragsdatensätze auf Ag Data Commons konnten in dieser Sitzung NICHT per API/Fetch aufgelöst werden (Ag Data Commons-Seiten liefern 403 für WebFetch, data.gov-API 404, Figshare-Suche ignoriert Suchbegriff). Verifiziert wurden nur zwei ARS-Datensätze: der Akron-Colorado-Datensatz (= bereits ausgeschlossener Poss-et-al.-Datensatz, DOI hier zur Zuordnung) und ein Ames-Iowa-Maisversuch 2010–2013 (nur 1 Jahr ≥2013). Das ist die größte offene Lücke dieser Recherche.

### Cited Findings
- LTAR Common Experiment: Protokoll "Grain yield data collection with a yield monitor" DOI 10.17504/protocols.io.rm7vzjm1rlx1/v1 und Post-Processing-Protokoll DOI 10.17504/protocols.io.4r3l2qmy3l1y/v1; übergeordnete Protokollsammlung DOI 10.17504/protocols.io.14egn9m5ql5d/v2 — [protocols.io LTAR Common Experiment](https://www.protocols.io/view/usda-ars-long-term-agroecosystem-research-ltar-com-g6mnbzc5f.html) (Suchtreffer; Protokolle, keine Daten).
- Ag Data Commons "Data from: Topographic position index predicts within-field yield variation in a dryland cereal production system": DOI 10.15482/USDA.ADC/28914434.v1; USDA-ARS Central Great Plains Research Station, 6,4 km östlich Akron CO (40.155 N, 103.135 W); Winterweizen, Mais, Rispenhirse; 2019–2022; 18 Bewirtschaftungseinheiten à 2,6–4,3 ha; Ertrag aus Yield-Monitor-Kornfluss auf 5-m-Raster aggregiert; CC0; Dateien Modeling_data.csv, Data_dictionary.csv, Study_site_DEM.tif; publiziert 27.05.2025 — [Figshare API 28914434](https://api.figshare.com/v2/articles/28914434) (bestätigt). **Identisch mit dem ausgeschlossenen "Colorado Akron dryland (Poss et al.)"** – nur zur DOI-Zuordnung.
- Ag Data Commons "Agricultural Research Service (ARS) Corn, Ames, Iowa": DOI 10.15482/USDA.ADC/1212382; Jerry Hatfield; vierjähriger Regenfeld-Maisversuch 2010-01-01 bis 2013-12-31; AgMIP-Format (agmip_download_0.zip, 33 kB); U.S. Public Domain; Geo-Polygon deckt grob ganz Iowa ab (40,56–43,50 N, 96,63–90,14 W), Textort Ames — [Figshare API 24660255](https://api.figshare.com/v2/articles/24660255) (bestätigt).
- Nashua, Iowa (data.gov): "measured and simulated data for corn and soybean yields, tileflow, N ... by plot, year, treatment ... from 36 1-acre plots at a farm near Nashua, Iowa" — [data.gov Nashua](https://catalog-beta.data.gov/dataset/nashua-data-access-an-agricultural-water-quality-study-in-nashua-iowa) (Suchtreffer; Jahre nicht gesehen, vermutlich vor 2013; unbestätigt).
- AgCROS-Portal https://agcros-usdaars.opendata.arcgis.com/ lieferte HTTP 404 (nicht erreichbar in dieser Sitzung).
- Ag Data Commons-Artikelseiten (agdatacommons.nal.usda.gov/articles/...) liefern für WebFetch HTTP 403; nur die Figshare-API (api.figshare.com/v2/articles/{id}) funktioniert bei bekannter ID.

### Datensatz-Einträge
- **ARS Corn Ames Iowa (AgMIP)** | https://agdatacommons.nal.usda.gov/articles/dataset/Agricultural_Research_Service_ARS_Corn_Ames_Iowa/24660255 (DOI 10.15482/USDA.ADC/1212382) | Mais | USA, Iowa (Ames) | named station findable (Polygon zu grob) | Parzellen, Größe nicht angegeben → only site mean | 2010–2013 (≥2013: nur 2013) | 1 Standort | ~1 | Kornertrag, Einheit/Feuchte nicht angegeben (AgMIP-Format) | Management-/Wetterdaten im AgMIP-Format | U.S. Public Domain | direct download (zip) | medium (AgMIP-Format parsen) | 1 | bestätigt
- **TPI/Akron CO (Poss et al.)** | https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_Topographic_position_index_predicts_within-field_yield_variation_in_a_dryland_cereal_production_system/28914434 (DOI 10.15482/USDA.ADC/28914434.v1) | Winterweizen, Mais, Rispenhirse | USA, Colorado | coordinates (40.155 N, 103.135 W) + DEM | 2,6–4,3 ha je Einheit | 2019–2022 | 18 Einheiten | ~72 (18×4, aber Rotation → ca. 1/3 je Kultur) | Yield-Monitor, 5-m-Raster an Bodenpunkten; Einheit nicht angegeben | Boden, Topographie (RTK), Wetter | CC0 | direct download | low | – (ausgeschlossen, bereits bekannt) | bestätigt
- **Nashua IA 36×1-acre plots** | https://catalog-beta.data.gov/dataset/nashua-data-access-an-agricultural-water-quality-study-in-nashua-iowa | Mais, Soja | USA, Iowa | named farm findable | ~0,4 ha je Parzelle → only site mean | unbekannt (vermutlich 1990er–2000er) | 1 Standort / 36 Parzellen | unbekannt, vermutlich 0 | Kornertrag by plot/year/treatment | Drainage, N-Austrag, Bodenbearbeitung | unbekannt | Access-DB/Download | medium | 1 | unbestätigt
- **LTAR Common Experiment Ertragsdaten (alle 18 Standorte)** | https://ltar.ars.usda.gov (Datensätze auf agdatacommons.nal.usda.gov; konkrete DOIs NICHT verifiziert) | Mais, Soja, Weizen, Baumwolle, Sorghum u.a. je Standort | USA, 18 LTAR-Standorte | i.d.R. Feldpolygone (Yield-Monitor-Protokoll) | Feldgröße standortabhängig (mehrere ha) | Common Experiment läuft seit ca. 2014/2015 | 18 Standorte, davon ~12 Ackerbau | potenziell >100 | Yield-Monitor-Kornertrag, standardisiertes Protokoll | Management, Boden, Wetter nach LTAR-Protokoll | i.d.R. CC0/US Public Domain (Ag Data Commons-Standard) | direct download (wenn gefunden) oder Anfrage an LTAR-Site-Datenmanager | medium | 4 (falls Daten auffindbar) | unbestätigt

### Inferences
- Da LTAR Yield-Monitor-Protokolle standardisiert hat, sollten pro Ackerbau-LTAR-Standort (Platte River–High Plains Aquifer/Nebraska, Upper Mississippi/Morris, Central Mississippi/Columbia MO, Northern Plains/Mandan, Eastern Corn Belt/Indiana, Lower Chesapeake, Lower Mississippi/Stoneville, Southern Plains/El Reno, Texas Gulf/Riesel, Gulf Atlantic/Tifton, Cook Agronomy Farm/Pullman) Feldpolygon-Erträge existieren; der Nachweis auf Ag Data Commons muss manuell (Browser, Suche "Common Experiment" + "yield") erfolgen.
- Der einzige verifizierte Ag-Data-Commons-Felddatensatz mit Yield-Monitor-Raster (Akron) ist bereits im Projekt bekannt.

### Gaps
- Keine DOIs für LTAR-Common-Experiment-Ertragsdatensätze verifiziert (technische Zugangsprobleme: 403/404). Manuelle Nachrecherche nötig: agdatacommons.nal.usda.gov Suche "LTAR" "Common Experiment" "yield"; Figshare-API mit POST /articles/search (GET ignoriert search_for).
- Cook Agronomy Farm (Pullman) Ertragsdaten: nur AmeriFlux-Flux-DOIs gefunden (US-RC1 10.17190/AMF/1498748, US-RC2 10.17190/AMF/1498747), kein Ertragsdatensatz.
- Hinweis (nicht verifiziert, Suche durch Hook blockiert): ARS-Mais-N-Raten-Datenbank Kitchen/Ransom et al. (49 Standortjahre, 8 Bundesstaaten, 2014–2016) soll auf Ag Data Commons liegen — DOI nicht ermittelt, nicht erfinden.

---

## KQ2: Genomes to Fields (G2F) – Ertrag pro Parzelle, Koordinaten, Jahre, Lizenz, Download

### Takeaway
G2F ist der am besten dokumentierte offene US-Datensatz: jährliche Releases 2014–2023 auf CyVerse mit DOI, Phänotyp (inkl. "estimated grain yield", plot weight, grain moisture, test weight), Feld-Metadaten mit GPS-Koordinaten je Standort, Wetter- und Bodendaten; Lizenz CC0 (2014–2017 laut Datenpaper) bzw. ODC-PDDL (2022 laut CyVerse). Nachteil: Kleinparzellen (Zuchtparzellen) → für Sentinel-2 nur Standortmittel pro Feld/Jahr nutzbar; Parzellenmaße auf den geöffneten Seiten nicht angegeben.

### Cited Findings
- Release-DOIs (CyVerse): 2014 10.25739/9wjm-eq41; 2015 10.25739/erxg-yn49; 2016 10.25739/yjnh-kt21; 2017 10.25739/w560-2114; 2018 10.25739/anqq-sg86; 2019 10.25739/t651-yy97; 2020 10.25739/hzzs-a865; 2021 10.25739/5ae3-sw62; 2022 10.25739/3d3g-pe51; 2023 10.25739/rzzy-3n27; Genotypen 2014–2023 10.25739/ragt-7213; Maize GxE Prediction Competition 2022 10.25739/tq5e-ak26, 2024 10.25739/78mn-4394 — [genomes2fields.org/resources](https://www.genomes2fields.org/resources/) (bestätigt).
- 2022-Datensatz (CyVerse DC): "2022 phenotypic evaluations, field-level weather data, agronomic information" + Metadaten + Bodendaten; Ordner a. phenotypic, b. weather, c. soil, z. supplemental, readme.txt; Lizenz "Open Data Commons Public Domain Dedication and License (PDDL)"; anonym herunterladbar; Contributor Dayane Cristina Lima — [dc.cyverse.org G2F 2022](https://dc.cyverse.org/dataset/genomes_to_fields_2022_dataset) (bestätigt).
- Datenpaper 2014–2017 (BMC Res Notes 2020): "over 55,000 plots across 68 unique locations"; Feldstandort-Codes mit GPS-Koordinaten (können zwischen Jahren wegen Rotation abweichen); Standard-Traits u.a. "estimated grain yield", plot weight, grain moisture, test weight; Bodendaten ab 2015 (pH, OM, Textur, N/P/K/S); Daten CC0; Sammlung DOI 10.25739/frmv-wj25; Kontakt Natalia de Leon (UW Madison) — [PMC7017475](https://pmc.ncbi.nlm.nih.gov/articles/PMC7017475/) (bestätigt).
- Zweites Datenpaper 2018–2019 existiert (BMC Genomic Data 2023) — [PMC10214680](https://pmc.ncbi.nlm.nih.gov/articles/PMC10214680) (Suchtreffer, nicht geöffnet).
- Das Datenpaper nennt Parzellengröße/Reihenzahl und die Ertragseinheit (bu/ac bei 15,5 %?) auf der geöffneten Seite nicht explizit.

### Datensatz-Eintrag
- **Genomes to Fields (G2F) Maize GxE, Jahresreleases 2014–2023** | https://www.genomes2fields.org/resources/ ; z.B. https://dc.cyverse.org/dataset/genomes_to_fields_2022_dataset (DOI 10.25739/3d3g-pe51) | Mais (Hybriden, Inzuchtlinien) | USA (Corn Belt bis Südstaaten), einzelne Standorte Kanada (Ontario) | coordinates ≤100 m (GPS je Feldstandort in Metadaten; Feld wechselt jährlich) | Zuchtparzellen (<0,01 ha) → only site mean; Versuchsfeld je Standort typischerweise 1–5 ha | 2014–2023 (alle ≥2013) | 68 unique locations 2014–2017; ca. 20–30 Umwelten je Jahr | grob 200–250 Standortjahre 2014–2023 (Inferenz) | "estimated grain yield", plot weight, grain moisture, test weight; Einheit/Feuchtebasis im Readme prüfen | Saat-/Erntedaten in Metadaten, Feldwetterstation, Boden ab 2015, Genotypen | CC0 (2014–2017, Paper) / ODC-PDDL (2022, CyVerse) | direct download, anonym | medium (Readme je Jahr, Standortmittel bilden, Feldpolygon aus Koordinate+Feldgröße rekonstruieren) | 4 | bestätigt

### Inferences
- Für das Projekt nutzbar als Feld-Mittelertrag je Standort und Jahr (Durchschnitt aller Hybrid-Parzellen oder nur Checks), mit bekannter Saat-/Ernte-Phänologie; Trockenstressjahre (z.B. 2023 Mittlerer Westen) sind enthalten.
- Maize-GxE-Kaggle/Competition-Subsets (2022, 2024) sind nur Teilmengen derselben CyVerse-Daten; dieselbe Lizenzlage.

### Gaps
- Parzellenabmessungen und exakte Ertragseinheit/Feuchtebasis nicht aus geöffneten Seiten belegt (im readme.txt der Releases prüfen).
- Exakte Zahl der Standortjahre je Jahr 2018–2023 nicht ausgezählt.

---

## KQ3: Universitäts-Sortenversuche und On-Farm-Netzwerke (Iowa/ISA, Nebraska, IL/Purdue/OSU/WI/MN/KS/MI/NDSU/PSU, DIFM)

### Takeaway
On-Farm-Netzwerke (Nebraska, ISA Iowa, Ohio eFields) liefern feldgroße Streifenversuche mit Yield-Monitor-Erträgen pro Behandlung, aber öffentlich nur auf County-Ebene ohne Feldgeometrie und ohne Roh-CSV → Feldkoordinaten nur auf Anfrage. Sortenversuche sind Kleinparzellen (nur Standortmittel), Standorte meist als Ort/County benannt; Rohdaten je Standort gibt es als Excel bei NDSU, Penn State, Wisconsin, Ontario (GoCrops). DIFM (Bullock, Illinois; Versuche 10–100 ha) publiziert keine offenen Daten – nur auf Anfrage.

### Cited Findings
- Nebraska On-Farm Research Network "Results Finder": Felder je Studie = Jahr, Titel, Study-ID, County, Bewässerungstyp, Kultur, Thema, PDF-Link, Yield difference, Signifikanz; Behandlungserträge in bu/ac; Standort nur County; kein CSV-Export; Jahresfilter 1990–2024; 59 Seiten Ergebnisse — [resultsfinder.unl.edu](https://resultsfinder.unl.edu/) (bestätigt). Erträge werden "typically gathered with the yield monitor, or with weigh wagons"; 2025 Results Book mit 105 Studien; Programmseite on-farm-research.unl.edu — [CropWatch 2025 Results Book](https://cropwatch.unl.edu/news/nebraska-farm-research-network-releases-2025-results-book/) (Suchtreffer).
- Iowa Soybean Association ISOFAST ("Interactive Summaries of On-Farm Strip Trials"): zeigt je Kategorie "trial locations, weather conditions, yield comparisons ... scouting data"; Einzelberichte in Online-Datenbank seit 2012 — [ISA interactive summaries PDF](https://www.iasoybeans.com/PDFLibraryUploads/interactive-summaries-on-farm-trials.pdf) (Suchtreffer); Tool-Seite https://analytics.iasoybeans.com/cool-apps/ISOFAST/ lud nur Navigationsfragment (unbestätigt).
- Ohio State eFields: 2024-Report mit 260 On-Farm-Feldversuchen in 42 Counties; durchsuchbare Datenbank 2017–2024 auf kx.osu.edu/efields (Redirect, nicht geöffnet); je Projekt County, Management, County-Wetter; Kontakt digitalag@osu.edu — [OSU Agronomic Crops Newsletter 2024 eFields](https://agcrops.osu.edu/newsletter/corn-newsletter/2025-01/2024-efields-report-available-now) (Suchtreffer).
- DIFM-Projektseite: keine Erwähnung öffentlicher Daten/Download/Data-Policy; "Use of the cyber-infrastructure is free of cost"; Personen David Bullock (Projektleiter, University of Illinois), Bob Dunker (Field Trials Coordinator), Carli Miller/Jones (Project Coordinator); Kulturen Mais, Soja, Baumwolle, Weizen; Partner in 17 US-Staaten, Argentinien, Südafrika — [publish.illinois.edu DIFM](https://publish.illinois.edu/data-intensive-farm-managment/) (bestätigt). 2019: >120 Versuche à 10–100 ha in 8 US-Staaten + AR/BR/ZA — [Bullock et al. 2019 via AGRIS](https://agris.fao.org/search/en/records/65de446a0f3e94b9e5ccb073) (Suchtreffer).
- NDSU Corn Hybrid Testing: Excel-Dateien 2016 (.xlsx), 2018, 2020; 2017 PDF, 2019 HTML; 12 Standorte 2024 (Ransom, Richland ×2, Sargent, Cass, Steele, Traill, Clay MN, Grand Forks ×2, Ramsey, Marshall MN – als Counties); Kontakte Clair Keene clair.keene@ndsu.edu, Darin Eisinger darin.eisinger@ndsu.edu, Joel Ransom joel.ransom@ndsu.edu — [NDSU Corn Hybrid Testing](https://www.ag.ndsu.edu/fss/cornhybridtesting) (bestätigt).
- Illinois Variety Testing: Kulturen Mais, Soja, Weizen, Hafer, Hanf; Kontakt varietytesting@illinois.edu; Download-Formate/Standorte auf Startseite nicht genannt — [vt.cropsci.illinois.edu](https://vt.cropsci.illinois.edu/) (bestätigt, Details offen).
- Kansas State Crop Performance Tests: Kulturen Canola, Mais, Baumwolle, Erbse, Futter, Sorghum, Soja, Sonnenblume, Weizen; Formate/Standorte auf Startseite nicht genannt — [K-State Crop Performance Tests](https://www.agronomy.k-state.edu/services/crop-performance-tests/) (bestätigt, Details offen).
- Penn State 2024 Corn Grain Hybrid Testing Report: PDF + "data in tabular format as an Excel (.xlsx) file" — [extension.psu.edu](https://extension.psu.edu/2024-corn-grain-hybrid-testing-report) (Suchtreffer).
- Wisconsin Corn Hybrid Performance Trials: PDF+Excel (2012 belegt), Tabellen unter corn.aae.wisc.edu/HT/2020/T11.pdf — [ipcm.wisc.edu](https://ipcm.wisc.edu/?p=2690) (Suchtreffer).
- Ohio Corn Performance Trials nach Region (SW/WC/C, NW, NC/NE Ohio) — [ohiocroptest.cfaes.osu.edu](https://ohiocroptest.cfaes.osu.edu/corntrials/cornperformance.asp) (Suchtreffer).
- University of Minnesota varietytrials.umn.edu lieferte HTTP 403. Purdue/Michigan nicht erreicht.
- WSU Pullman Sortenversuchs-PDFs (Hard Red Spring, Barley, 2012–2018) — [WSU 2018 Pullman HRS](https://wpcdn.web.wsu.edu/cahnrs/uploads/sites/16/2018_Pullman_HRS.pdf) (Suchtreffer).

### Datensatz-Einträge
- **Nebraska On-Farm Research Network (Results Finder + Results Books)** | https://resultsfinder.unl.edu/ ; https://on-farm-research.unl.edu | Mais, Soja, Weizen, Sorghum u.a. | USA, Nebraska | County-Ebene öffentlich; Feldpolygon nur auf Anfrage | Feldstreifen in Produktionsfeldern (typ. 10–60 ha Feld; nicht angegeben) | 1990–2024 (≥2013: 2013–2024, ~100 Studien/Jahr) | >1000 Studien gesamt | grob 800–1200 Feldjahre ≥2013 (Inferenz, ~100/Jahr) | Behandlungsertrag bu/ac (Yield-Monitor/Wiegewagen), Standardfeuchte (vermutl. 15,5 % Mais) | Bewässerungstyp, Behandlung, Studien-PDF mit Saat-/Erntedatum, Hybrid, Boden | nicht angegeben (Universitätspublikation) | online einsehbar; Rohdaten/Feldlage auf Anfrage beim Programm (on-farm-research.unl.edu, UNL Extension) | high (PDF-Parsing, Feldlage anfragen) | 3 | bestätigt
- **Iowa Soybean Association On-Farm Network / ISOFAST** | https://analytics.iasoybeans.com/cool-apps/ISOFAST/ ; https://www.iasoybeans.com | Soja, Mais | USA, Iowa | Trial locations in Karte (Präzision unklar; vermutl. County/Ort) | Feldstreifen | Berichte seit 2012; ≥2013 ja | hunderte Streifenversuche | unbekannt (mehrere hundert Feldjahre) | Ertragsdifferenz/Ertrag bu/ac | Wetter, Scouting-Daten, Ökonomie | nicht angegeben | online; Rohdaten auf Anfrage ISA Research Center for Farming Innovation (iasoybeans.com) | high | 2–3 | unbestätigt
- **Ohio State eFields On-Farm Research** | https://digitalag.osu.edu (Reports), https://kx.osu.edu/efields (DB 2017–2024) | Mais, Soja, Weizen | USA, Ohio | County | feldgroße Versuche ("field scale") | 2017–2024 | 2024: 260 Versuche in 42 Counties | grob 1000+ Feldjahre 2017–2024 (Inferenz) | Ertrag bu/ac je Behandlung | Management, County-Wetter, Saat-/Erntedaten in Berichten | nicht angegeben | PDF-Reports frei; Feldlage auf Anfrage digitalag@osu.edu | high | 2–3 | unbestätigt
- **DIFM – Data-Intensive Farm Management (On-Farm Precision Experimentation)** | https://publish.illinois.edu/data-intensive-farm-managment/ | Mais, Soja, Weizen, Baumwolle, Gerste | USA (~20 Staaten) + CA/AR/BR/ZA | Feldpolygon + Yield-Monitor-Raster (intern) | 10–100 ha je Versuch | 2016–laufend | >120 Versuche allein 2019 | potenziell mehrere hundert | Yield-Monitor-Ertrag (bu/ac bzw. t/ha), Input-Raten-Karten | Saatstärke-/N-Raten-Karten, Boden, Wetter | keine öffentliche Lizenz; Betriebsdaten | nur auf Anfrage: David Bullock, Dept. of Agricultural & Consumer Economics, University of Illinois (Projektseite nennt keine E-Mail); alternativ Taro Mieno (UNL) | high | 2 (5 falls Zugang) | bestätigt (dass keine offenen Daten vorliegen)
- **NDSU Corn Hybrid Testing (Excel)** | https://www.ag.ndsu.edu/fss/cornhybridtesting | Mais | USA, ND + MN | County/Ort (named station findable) | Kleinparzellen → only site mean | 2015–2020 (+2023/2024 angekündigt) | ~12 Standorte/Jahr | ~60–70 Standortjahre | Kornertrag bu/ac (Feuchtebasis nicht angegeben) | Reifegruppe, Feuchte, Standfestigkeit | nicht angegeben | direct download (xlsx/PDF) | medium | 2 | bestätigt
- **Penn State Corn Hybrid Testing (xlsx)** | https://extension.psu.edu/2024-corn-grain-hybrid-testing-report | Mais | USA, Pennsylvania | Ort/County | Kleinparzellen → only site mean | 2024 (frühere Jahre analog) | mehrere Zonen/Standorte | unbekannt | bu/ac | Zonenauswertung | nicht angegeben | direct download | medium | 2 | unbestätigt
- **Wisconsin Corn Hybrid Performance Trials** | https://ipcm.wisc.edu/?p=2690 ; https://corn.aae.wisc.edu | Mais (Korn, Silage, Bio) | USA, Wisconsin | Ort | Kleinparzellen → only site mean | 2011–2025 | ~10+ Standorte/Jahr | ~120+ | bu/ac | Feuchte, Standfestigkeit | nicht angegeben | direct download (PDF; Excel teils) | medium–high | 2 | unbestätigt
- **Illinois Variety Testing** | https://vt.cropsci.illinois.edu/ | Mais, Soja, Weizen, Hafer | USA, Illinois | Ort (Regionen) | Kleinparzellen → only site mean | laufend (≥2013 ja) | mehrere Standorte je Kultur | unbekannt | bu/ac | – | nicht angegeben | online; Rohdaten/Koordinaten: varietytesting@illinois.edu | medium | 2 | bestätigt (Seite), Formate unbestätigt
- **Kansas State Crop Performance Tests** | https://www.agronomy.k-state.edu/services/crop-performance-tests/ | Weizen, Mais, Sorghum, Soja, Sonnenblume, Canola, Baumwolle, Erbse | USA, Kansas | Ort/County | Kleinparzellen → only site mean | laufend | mehrere Standorte je Kultur | unbekannt | bu/ac | – | nicht angegeben | online (PDF) | medium | 2 | bestätigt (Seite), Details unbestätigt
- **Ohio Corn Performance Trials** | https://ohiocroptest.cfaes.osu.edu/corntrials/cornperformance.asp | Mais | USA, Ohio | Ort | Kleinparzellen → only site mean | laufend | Regionen SW/WC/C, NW, NC/NE | unbekannt | bu/ac | – | nicht angegeben | online | medium | 2 | unbestätigt

### Inferences
- Für Satelliten-Labels sind die On-Farm-Netzwerke (NE, IA, OH) wertvoller als Sortenversuche, weil Feldgröße >10 ha; ohne Feldgeometrie aber nicht nutzbar → Anfrage an die Programme ist der entscheidende Schritt (Betriebsdatenschutz: Freigabe eher für aggregierte/anonymisierte Feldmittel mit Zentroid realistisch).
- Sortenversuche liefern nur Standortmittel kleiner Versuchsflächen; nutzbar höchstens als "Station" mit Koordinate des Versuchsfelds (muss erfragt werden).

### Gaps
- Purdue, Michigan State, Minnesota Sortenversuche nicht erreicht (403/kein Fetch).
- Ob ISOFAST/eFields Feldkoordinaten anzeigen, nicht verifiziert.
- DIFM-Kontakt-E-Mail nicht auf der Projektseite; Institut (ACE, University of Illinois) ist belegt.

---

## KQ4: AmeriFlux-Ackerstandorte (außer Mead) mit offenen Erträgen

### Takeaway
AmeriFlux-Standardprodukte (BASE/FLUXNET) enthalten keine Ertragsvariable; die BADM-Standards listen eine Gruppe DM_AGRICULTURE (Crop Management) sowie DM_PLANTING/DM_TILL/DM_FERT, aber keine Yield-Gruppe. Erträge der Ackerstandorte erscheinen nur in Publikationen oder Begleitdatensätzen (z.B. Dryad-Datensatz Moore & Bernacchi 2025 für Bondville/UIUC-Energy-Farm, Ertrag in g C m⁻²). Rosemount-Seite (US-Ro1) nennt keine Erträge; Kontakte John Baker/Tim Griffis (UMN).

### Cited Findings
- BADM-Standards: Gruppen DM_AGRICULTURE (Crop Management), DM_PLANTING, DM_TILL, DM_FERT_M, DM_FERT_O, BIOMASS; keine Gruppe AG_BIOMASS_CROP/AG_PROD/Yield auf der Seite; "Some BADM types (e.g., Biomass ...) are scheduled for update"; Kontakt ameriflux-support@lbl.gov — [AmeriFlux BADM Standards](https://ameriflux.lbl.gov/data/badm/badm-standards/) (bestätigt).
- US-Ro1 Rosemount-G21: 44.7143, −93.0898; Mais/Soja-Rotation; Daten 2004–2016 (BASE DOI 10.17190/AMF/1246092, FLUXNET DOI 10.17190/AMF/1881588); CC-BY-4.0; PIs John Baker jbaker@umn.edu, Timothy Griffis tgriffis@umn.edu; Datenmanager Ke Xiao xiaox224@umn.edu; keine Ertragsangaben auf der Seite — [AmeriFlux US-Ro1](https://ameriflux.lbl.gov/sites/siteinfo/US-Ro1) (bestätigt).
- Dryad "Final eddy covariance dataset to support lessons from long-term monitoring of carbon gains and losses in cropping systems" (Moore & Bernacchi, 23.09.2025, DOI 10.5061/dryad.kd51c5bjt): Standorte US-UiA (Switchgrass), US-UiB (Miscanthus), US-UiC (Mais-Soja), US-UiD (Prärie), US-Bo (Bondville); Variablen jährlich NEE, Yield, NECB; Maize_CT_Yield/Maize_NT_Yield in g C m⁻² (Trockenmasse × 0,45 für Korn); Dateien README.md, UIUC_Final_Data.csv (3 kB); Jahre auf Seite nicht genannt — [Dryad kd51c5bjt](https://datadryad.org/dataset/doi:10.5061/dryad.kd51c5bjt) (bestätigt).
- US-Bo2 Bondville: 400 m nördlich von US-Bo1, Gegenkultur in Mais/Soja-Rotation; BASE DOI 10.17190/AMF/1246037, CC-BY-4.0 — [AmeriFlux US-Bo2 DOI](https://ameriflux.lbl.gov/doi/AmeriFlux/US-Bo2/) (Suchtreffer). US-Br3 Brooks Field Site 11 Ames DOI 10.17190/AMF/1246039; US-Ro3 Rosemount G19 DOI 10.17190/AMF/1246093 — [data.gov Rosemount](https://catalog.data.gov/dataset/ameriflux-ecosystem-observation-datasets-rosemount-agricultural-research-service) (Suchtreffer).
- US-CRT Curtice Walter-Berger cropland: CC-BY-4.0 — [AmeriFlux US-CRT](https://ameriflux.lbl.gov/sites/siteinfo/US-CRT) (Suchtreffer; Ertrag nicht erwähnt). Neue gepaarte Ackerstandorte US-SD1/US-VT2 (Mais/Soja, mit/ohne Zwischenfrucht) mit Daten 2023–2025 — [AmeriFlux US-SD1](https://ameriflux.lbl.gov/sites/siteinfo/US-SD1) (Suchtreffer).
- US-MN3 Morris Corn-Soybean Conventional Tillage (USDA-ARS Morris/Swan Lake) existiert als AmeriFlux-Standort — [AmeriFlux US-MN3](https://ameriflux.lbl.gov/sites/siteinfo/US-MN3) (Suchtreffer; Ertrag nicht geprüft).

### Datensatz-Einträge
- **Dryad: UIUC Energy Farm + Bondville Jahreserträge (Moore & Bernacchi 2025)** | https://datadryad.org/dataset/doi:10.5061/dryad.kd51c5bjt | Mais (CT/NT), Miscanthus, Switchgrass, Prärie; Bondville Mais/Soja | USA, Illinois (Urbana Energy Farm; Bondville 40.006 N, −88.29 W) | coordinates via AmeriFlux-Site-Koordinaten (≤100 m) | Energy-Farm-Felder ~4 ha je System (Inferenz, nicht auf Seite); Bondville ~ Feldgröße | Jahre auf Seite nicht genannt (Energy Farm ab 2008; Bondville ab 1996) | 5 Systeme/2 Standorte | grob 10–25 Standortjahre ≥2013 (Inferenz) | Ertrag g C m⁻² (Trockenmasse × 0,45 Korn / 0,48 Biomasse) → rückrechenbar | NEE, NECB | Dryad-Standard (CC0 üblich; Seite nennt Lizenz nicht) | direct download | low | 3 | bestätigt
- **AmeriFlux-Ackerstandorte (US-Bo1/Bo2, US-Ro1/Ro3/Ro5/Ro6, US-Br1/Br3, US-CRT, US-MN3, US-IB1, US-ARM, US-KL1/2, US-Tw3, US-Uif, CA-ER1 …)** | https://ameriflux.lbl.gov/sites/site-search | Mais, Soja, Weizen, Reis (Tw3) u.a. | USA/Kanada | coordinates ≤100 m (Tower) | Feld um Tower, meist 10–60 ha | je Standort; viele ≥2013 | ~30+ Ackerstandorte | Erträge: unbekannt/nicht in Standardprodukten | kein Yield-Feld in BASE/BADM-Standards | Management (DM_AGRICULTURE/PLANTING/TILL/FERT) in BADM, Flux, Meteo | CC-BY-4.0 (bzw. Legacy) | Flux direct download (Registrierung); Erträge nur über PI-Anfrage / Papers | high | 2 (Ertrag) | bestätigt (dass kein Yield-Standardfeld existiert)

### Inferences
- Für AmeriFlux-Standorte sind die Tower-Koordinaten und Feldgrenzen gut bekannt; Erträge müssen aus Papers (z.B. Bernacchi-Gruppe Bondville, Baker/Griffis Rosemount, Hatfield/Prueger Brooks Field, Suyker Mead) oder per PI-Anfrage beschafft werden → aufwändig, geringe Standortjahr-Zahl.

### Gaps
- Nicht geprüft: US-IB1 (Fermi), US-ARM, US-KL1/2, US-Tw3, US-Uif, CA-ER1 Seiten; keine offenen Ertragstabellen gefunden.
- Dryad-Datensatz: Jahre und Lizenz nicht auf Seite, README nicht geöffnet.

---

## KQ5: Kanada – AAFC Open Data, Provinz-Sortenversuche, Langzeitrotationen (Elora, Swift Current, Lethbridge), Prärie-Ertragsdaten

### Takeaway
Auf open.canada.ca wurden (in ~70 gesichteten Treffern zweier Suchanfragen) nur aggregierte StatCan-/Provinz-Ertragsstatistiken gefunden, keine Parzellen-/Feld-Ertragsdatensätze der AAFC-Langzeitversuche. Lethbridge Rotation ABC (seit 1911), Swift Current Old Rotation (1966)/New Rotation (1987) und Breton Plots (U Alberta, >90 Jahre) existieren und AAFC arbeitet laut Fachpresse an der Zugänglichmachung – Daten derzeit nur auf Anfrage. Ontario-Sortenversuche (GoCrops.ca: OCC Mais, OCCC Getreide, OSACC Soja/Canola, OPCC Hülsenfrüchte) bieten Tabellen/Spreadsheets je Standort.

### Cited Findings
- open.canada.ca API "crop yield plot": 87 Treffer, gesichtete 11: StatCan "Estimated areas, yield and production ... by Small Area Data Regions" (Open Government Licence – Canada), StatCan GM-Mais/Soja-Schätzungen, Alberta Major Crops – Yield 1963–2015 (provinzweit), Forst-Plots BC – kein Feld-/Parzellenertrag — [open.canada.ca API](https://open.canada.ca/data/api/action/package_search?q=crop+yield+plot&rows=40) (bestätigt, Teilsicht).
- open.canada.ca API "agroecosystem long-term experiment": 60 Treffer, gesichtete 12 ohne Bezug zu Ackerertrag — [open.canada.ca API](https://open.canada.ca/data/api/action/package_search?q=agroecosystem+long-term+experiment&rows=20) (bestätigt, Teilsicht).
- AAFC LTAEs: Lethbridge RDC seit 1910/1911, Rotation ABC (A kontinuierlich Weizen, B Brache–Weizen, C Brache–Weizen–Weizen); Swift Current Old Rotation seit 1966, New Rotation seit 1987; "an effort is underway to ensure this ... dataset of long-term experiments remains an accessible resource" — [Top Crop Manager 2021](https://www.topcropmanager.com/a-valuable-research-legacy/), [Top Crop Manager 2024](https://magazine.topcropmanager.com/article/Long-term+agroecosystem+experiments+on+the+Prairies/4770166/821513/article.html) (Suchtreffer).
- Lethbridge "Other long-term experiments" Publikation auf AAFC-Profilseite — [profils-profiles.science.gc.ca](https://profils-profiles.science.gc.ca/en/publication/other-long-term-experiments-lethbridge-research-centre) (Suchtreffer, nicht geöffnet).
- Möglicher Datenpaper-Lead: Scientific Data (Okt 2024) Treffer in derselben Suche — [PMC11487249](https://pmc.ncbi.nlm.nih.gov/articles/PMC11487249) (nicht geöffnet; Inhalt unbekannt – prüfen, ob kanadische LTAE-Daten).
- AAFC "Crop Rotations in Canada" (Kartenprodukt aus Crop Inventory, letzte 4 Saisons; Kontakt agri-geomatics-agrog@agr.gc.ca) – kein Ertrag — [donnees.iriu.ca Mirror](https://donnees.iriu.ca/dataset/31226205-3654-4462-b50a-10ba53d7f362) (Suchtreffer).
- GoCrops.ca vereint gocorn.net, gocereals.ca, gobeans.ca, gosoy.ca; Komitees OCCC (Getreide), OCC (Mais), OPCC (Hülsenfrüchte), OSACC (Soja/Canola) — [gocrops.ca](https://gocrops.ca/) (bestätigt). "Tables (Spreadsheets) for All Locations" unter Performance Trial Results; Gebiete z.B. "Area 3 East: Bainsville, Iroquois, Winchester" — [Field Crop News 2025 OCC](https://fieldcropnews.com/?p=25389), [Farmtario](https://farmtario.com/crops/new-website-offers-simpler-way-to-access-crop-performance-trial-data) (Suchtreffer).

### Datensatz-Einträge
- **AAFC Lethbridge Rotation ABC / Rotation U (seit 1911)** | https://profils-profiles.science.gc.ca/en/publication/other-long-term-experiments-lethbridge-research-centre (kein Datenportal gefunden) | Weizen (Sommerweizen), Brache-Systeme | Kanada, Alberta (Lethbridge RDC, 49.70 N, −112.78 W) | named station findable | Kleinparzellen → only site mean | 1911–laufend (≥2013 ja) | 1 Standort, mehrere Rotationen | ~10–13 Standortjahre ≥2013 | Kornertrag (kg/ha), Feuchte unbekannt | Management, Boden, Klima über >100 Jahre | keine offene Lizenz gefunden | on request: AAFC Lethbridge Research and Development Centre (Kontakt über agriculture.canada.ca / science.gc.ca-Profile) | medium | 2 | unbestätigt
- **AAFC Swift Current Old Rotation (1966) / New Rotation (1987)** | https://www.topcropmanager.com/a-valuable-research-legacy/ (Sekundärquelle) | Weizen, Brache, Leguminosen | Kanada, Saskatchewan (Swift Current RDC, 50.27 N, −107.73 W) | named station findable | Kleinparzellen → only site mean | 1966/1987–laufend | 1 Standort | ~10–13 | Kornertrag kg/ha | Protein, Bodenwasser, Boden | keine | on request: AAFC Swift Current RDC | medium | 2 | unbestätigt
- **Breton Plots (University of Alberta, seit 1930)** | Sekundärquelle Top Crop Manager (kein Datenlink) | Weizen, Gerste, Hafer, Raps, Futterleguminosen | Kanada, Alberta (Breton, 53.09 N, −114.44 W) | named station findable | Kleinparzellen → only site mean | 1930–laufend | 1 Standort | ~10–13 | kg/ha | Boden (Gray Luvisol), Düngung | keine | on request: U of Alberta, Dept. Renewable Resources (Breton Plots Manager) | medium | 2 | unbestätigt
- **Ontario Performance Trials (GoCrops.ca: OCC/OCCC/OSACC/OPCC)** | https://gocrops.ca/ | Mais, Soja, Canola, Winterweizen, Gerste, Hafer, Bohnen | Kanada, Ontario | Ort (Area-Listen, z.B. Bainsville, Iroquois, Winchester; Elora/Ridgetown nicht verifiziert) | Kleinparzellen → only site mean | mehrjährig (≥2013 ja; Jahre nicht auf Startseite) | ca. 10–30 Standorte je Kultur und Jahr | grob 100+ je Kultur (Inferenz) | bu/ac bzw. t/ha, Feuchte angegeben | Wärmeeinheiten, Feuchte, Lager | Terms & Conditions (nicht gelesen) | direct download (Spreadsheets je Area) | medium | 2 | bestätigt (Portal), Spreadsheets unbestätigt
- **StatCan / Alberta provinzielle Ertragsstatistiken** | https://open.canada.ca (slugs d909f35e-…, 6fb545d2-…) | alle Feldfrüchte | Kanada | Region/Provinz (kein Feld) | – | lange Reihen | – | – | aggregiert | – | Open Government Licence | direct | – | 0 (keine Feldebene) | bestätigt

### Inferences
- Für Kanada ist derzeit kein offener Feld-/Parzellen-Ertragsdatensatz ≥2013 auffindbar; realistisch sind Anfragen bei AAFC-Zentren (Lethbridge, Swift Current, Harrow, Ottawa CEF) und U Alberta (Breton). Manitoba MCVET, Saskatchewan Seed Guide, Alberta Regional Variety Trials sind analog zu GoCrops (Standortmittel, Ort benannt) – nicht geprüft.

### Gaps
- Elora (U Guelph) Langzeitrotation, Harrow (AAFC) und Manitoba/Saskatchewan/Alberta-Sortenversuche nicht recherchiert (Zeit/Toolbudget).
- open.canada.ca-Treffer nur zu ~12 % gesichtet (Antworten >230 kB abgeschnitten).

---

## KQ6: Langzeitversuche Morrow Plots, Sanborn Field, Magruder Plots, Old Rotation (Auburn) – Jahreserträge ≥2013 offen?

### Takeaway
Nur die Morrow Plots (Illinois) sind offen und maschinenlesbar verfügbar (Illinois Data Bank DOI + CRAN-Paket morrowplots, 1888–2021). Sanborn Field, Magruder Plots und Old Rotation: keine offenen Jahresertragsdateien ≥2013 gefunden – nur auf Anfrage bei den Universitäten. Alle vier sind Kleinparzellen auf Campusflächen (<1 ha) → nur Standortmittel, Satellitennutzen gering.

### Cited Findings
- CRAN-Paket morrowplots v0.2.0 (08.01.2025, MIT): "Agricultural data for 1888-2021 from the Morrow Plots"; 3216 Zeilen, 26 Variablen (Jahr, Plot, Phase, Saatinfo, Jahreserträge Mais kontinuierlich/Rotation, gedüngt/ungedüngt) — [CRAN morrowplots](https://stat.ethz.ch/CRAN/web/packages/morrowplots/index.html) (Suchtreffer-Snippets mehrerer Mirrors; bestätigt über Experts-Seite).
- Illinois Data Bank "Morrow Plots Treatment and Yield Data": DOI 10.13012/B2IDB-7865141_V1; "planting, treatment, and yield data ... since 1888"; wird aktualisiert; Codebook vorhanden; Lizenz auf der Experts-Seite nicht genannt — [experts.illinois.edu](https://experts.illinois.edu/en/datasets/morrow-plots-treatment-and-yield-data/) (bestätigt); databank.illinois.edu lieferte 403.
- Sanborn Field (MU, 1888, National Historic Landmark): keine Datenbank gefunden; nur Archivalien ("Sanborn Field: historical perspective") — [MOspace](https://mospace.umsystem.edu/xmlui/handle/10355/53308?show=full) (Suchtreffer).
- Magruder Plots (OSU, 1892, Winterweizen): offizielle Seite ohne Datendownload — [agresearch.okstate.edu/magruder-plots](https://agresearch.okstate.edu/magruder-plots) (Suchtreffer).
- Old Rotation (Auburn, 1896): 13 Parzellen auf 1 acre; seit 2003 Hälfte jeder Parzelle bewässert; Baumwolle, Mais, Soja, Weizen; Kurator historisch Charles Mitchell; USDA-ARS National Soil Dynamics Laboratory Auburn beteiligt — [Wikipedia Old Rotation](https://en.wikipedia.org/wiki/Old_Rotation), [Balkcom 2008](https://ars.usda.gov/ARSUserFiles/60100500/csr/ResearchPubs/balkcom/balkcom_08a.pdf) (Suchtreffer).

### Datensatz-Einträge
- **Morrow Plots (University of Illinois)** | https://doi.org/10.13012/B2IDB-7865141_V1 ; CRAN https://cran.r-project.org/package=morrowplots | Mais (kontinuierlich, 2- und 3-jährige Rotation), Soja/Hafer/Klee in Rotation | USA, Illinois (Urbana, Campus, ca. 40.104 N, −88.226 W) | named station findable (Campusfläche, Umriss bekannt) | Parzellen ca. 0,02–0,1 ha → only site mean (Gesamtfläche <1,5 ha) | 1888–2021 (≥2013: 2013–2021) | 1 Standort, ~24 Teilparzellen | ~9 | Kornertrag bu/ac (Mais), Feuchtebasis im Codebook | Saatinfo, Düngung/Treatment, Phase | MIT (CRAN); Data Bank-Lizenz nicht gesehen | direct download | low | 2 | bestätigt
- **Sanborn Field (University of Missouri)** | https://cafnr.missouri.edu (keine Datenseite gefunden) | Mais, Weizen, Soja, Futter | USA, Missouri (Columbia, Campus, ~38.942 N, −92.320 W) | named station findable | Kleinparzellen → only site mean | 1888–laufend | 1 | ~10–13 | bu/ac | Treatment | keine | on request: MU School of Natural Resources / Sanborn Field Superintendent | medium | 1 | unbestätigt
- **Magruder Plots (Oklahoma State University)** | https://agresearch.okstate.edu/magruder-plots | Winterweizen | USA, Oklahoma (Stillwater, ~36.12 N, −97.09 W) | named station findable | Kleinparzellen → only site mean | 1892–laufend | 1 | ~10–13 | bu/ac | Düngung (N, P, K, Kalk, Mist) | keine | on request: OSU Dept. Plant & Soil Sciences | medium | 1 | unbestätigt
- **Old Rotation (Auburn University)** | https://en.wikipedia.org/wiki/Old_Rotation ; https://aaes.auburn.edu | Baumwolle, Mais, Soja, Weizen | USA, Alabama (Auburn, Campus, ~32.59 N, −85.49 W) | named station findable | 13 Parzellen auf 0,4 ha → only site mean | 1896–laufend | 1 | ~10–13 | lb lint/ac, bu/ac | Bewässert/unbewässert seit 2003, Winterleguminosen | keine | on request: Auburn AAES / Dept. Crop, Soil & Environmental Sciences; USDA-ARS NSDL Auburn | medium | 1 | unbestätigt

### Inferences
- Historische Campus-Langzeitversuche sind für ein Sentinel-2-Projekt wegen Parzellengröße <1 ha praktisch wertlos außer als Einzelpunkt-Standortmittel; nur Morrow Plots sind ohne Anfrage nutzbar.

### Gaps
- Lizenz des Illinois-Data-Bank-Datensatzes und exakte Ertragseinheit nicht gesehen (403).

---

## KQ7: NEON-Agrarstandorte – gibt es Erträge?

### Takeaway
Nicht gezielt recherchiert (Toolbudget); in keiner der durchgeführten Suchen tauchte ein NEON-Ertragsprodukt auf. Kein Nachweis von Ertragsdaten → nicht aufnehmen.

### Cited Findings
- Keine (keine Quelle gefunden/geöffnet).

### Inferences
- NEON-Datenprodukte sind ökologisch (Phänologie, Biomasse-Plots, Flux), keine Ernteerträge; keine Belege gesammelt.

### Gaps
- NEON vollständig offen; falls gewünscht, NEON-Datenportal nach "harvest"/"crop" durchsuchen.

---

## Zusammenfassende Bewertung (für den Reportschreiber)

Rangfolge nach Nutzen für Satelliten-Ertragsverlust-Labels (USA/Kanada, ohne ausgeschlossene Datensätze):
1. **G2F (4/5, bestätigt)** – einziger großer, offener, geokodierter Mehrstandort-Datensatz ≥2014 mit Saat-/Erntedaten; Nutzung als Feld-/Standortmittel.
2. **LTAR Common Experiment Ertragsdaten (4/5 potenziell, unbestätigt)** – Yield-Monitor-Feldpolygone an ~12 Ackerstandorten; DOIs müssen manuell auf Ag Data Commons ermittelt werden (Zugangsprobleme in dieser Sitzung).
3. **On-Farm-Netzwerke Nebraska/Iowa/Ohio (2–3/5)** – hunderte Feldjahre ≥2013, Erträge bu/ac je Behandlung öffentlich, aber Feldlage nur County → Anfrage nötig.
4. **DIFM (2/5, 5 bei Zugang)** – ideale Feldgröße 10–100 ha mit Yield-Monitor-Rastern, aber keine offenen Daten; Anfrage David Bullock (U Illinois) / Taro Mieno (UNL).
5. **Dryad Moore & Bernacchi (3/5)** – wenige Standortjahre, aber sofort nutzbar; AmeriFlux allgemein ohne Yield-Standardfeld.
6. **Sortenversuche (NDSU, PSU, WI, IL, KS, OH, Ontario GoCrops) (2/5)** – Standortmittel, Ort benannt, Excel teils vorhanden.
7. **Langzeitversuche Morrow (2/5, offen), Sanborn/Magruder/Old Rotation/Lethbridge/Swift Current/Breton (1–2/5, nur auf Anfrage)**.

Offene Punkte mit höchster Priorität für Nachrecherche: (a) LTAR-Ertragsdatensätze + DOIs auf Ag Data Commons manuell im Browser; (b) G2F-Readme für Parzellenmaße/Einheit; (c) Anfragen an Nebraska On-Farm Research, ISA, OSU eFields, DIFM nach Feldzentroiden/Polygonen; (d) Kanada: Elora/Harrow/Manitoba MCVET/Saskatchewan/Alberta RVT und Scientific-Data-Paper PMC11487249 prüfen.
