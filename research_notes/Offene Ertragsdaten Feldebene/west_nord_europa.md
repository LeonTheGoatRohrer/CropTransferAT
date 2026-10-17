# Offene Ertragsdaten Feldebene – West- und Nordeuropa (UK, IE, FR, BE, NL, LU, DK, SE, NO, FI)

Stand: 2026-10-16. Recherche per WebFetch/WebSearch/curl (DataCite-API, ICOS-SPARQL, Luke-PxWeb-API). "bestätigt" = Link geöffnet und Daten/Metadaten gesehen; "unbestätigt" = Link nicht erreichbar oder nur über Dritte (Suchtreffer, Paper) belegt. Alle DOIs stammen aus geöffneten Seiten/API-Antworten, keine erfunden.

Wichtige technische Hinweise für den Report-Writer:
- `entrepot.recherche.data.gouv.fr` (= data.inrae.fr-Nachfolger) blockiert automatisierte Abrufe (Anubis-Bot-Schutz, "Access Denied"). Die dortigen Datensätze wurden über die **DataCite-API** (api.datacite.org) und **B2FIND** verifiziert; die Landing Pages müssen im normalen Browser geöffnet werden.
- `glten.org` hat ein **abgelaufenes TLS-Zertifikat** (WebFetch bricht ab; curl -k funktioniert). Das Portal ist eine reine Angular-App mit Metadaten; ein öffentlicher Daten-API-Endpunkt wurde nicht gefunden.
- figshare- und DOAJ-Landing-Pages liefern 403 für Bots; die figshare-API (`api.figshare.com/v2/articles/<id>`) funktioniert.

---

## Key Question 0: Gesamtkatalog aller gefundenen Datensätze (Feldliste exakt wie vorgegeben)

### Takeaway
Es gibt in der Region nur wenige wirklich offene Datensätze mit **Feldpolygon/Koordinate + Jahr ≥2013 + gemessenem Ertrag**; die besten Kandidaten sind die ICOS-Ackerstationen (BE-Lon, FR-Gri, FR-Lam, FR-EM2, FR-Aur, DK-Vng; Felder 10–20 ha, CC BY 4.0, Ertrag als Ancillary-Daten noch zu verifizieren), die nordische Sortenversuchs-Datenbank (DataverseNO, CC BY 4.0, Standort je Versuch), die schwedischen Bodenfruchtbarkeitsversuche R3-9001 (CC0, 9 Standorte bis 2022), Rothamsted e-RA (CC BY 4.0, bis 2022/2024) sowie INRAE-Systemversuche (Grignon 2009–2020, EFELE 2012–2020, Rés0Pest 2013–2023, Etalab 2.0). Große Combine-Yield-Map-Sammlungen existieren (UKCEH ASSIST/CYCleSS, 934 Felder), sind aber anonymisiert (10-km-Raster) bzw. nur unter NDA erhältlich.

### Cited Findings – Datensatz-Katalog

Format je Eintrag: **Name** | Link | Crop(s) | Country/region | Location precision | Area per unit | Years (≥2013) | Number of sites/fields | Est. independent site-years ≥2013 | Yield measure/unit/moisture | Extra info | License | Access | Preparation effort | Rating 1–5 | Status

#### UK / Irland

1. **Rothamsted e-RA: Broadbalk Wheat annual grain and straw yields 1968–2022** | https://doi.org/10.23637/rbk1-yld6822-01 (→ https://www.era.rothamsted.ac.uk/dataset/rbk1/01-YLD6822) | Winterweizen | UK, Harpenden (Hertfordshire) | named station findable (Broadbalk field, Rothamsted) | Plots = Streifen×Sektion, Größe nicht angegeben, <1 ha → **only site mean** | 1968–2022 (≥2013: 2013–2022 = 10 Jahre) | 1 Feld, 10 Sektionen, Streifen 1–22 | ~10 (ein Feld; Sektionen nicht satellitenunabhängig) | Korn- und Strohertrag je Plot, bei 85 % TM (Einheit auf Seite nicht genannt, Excel/CSV) | Dünger-/Mistgaben (N,P,K,Na,Mg), Saat- und Erntedaten, Sorten, Brachejahre | CC BY 4.0 + Pflichttext "Contains data supplied by Rothamsted Research" + Acknowledgement (https://www.era.rothamsted.ac.uk/info/conditions) | Download nach Ausfüllen eines End-User-Agreement-Formulars (Name, Organisation, Zweck), kein Passwort; Kontakt era@rothamsted.ac.uk (Kuratorinnen Sarah Perryman, Margaret Glendining) | low | 3 | **bestätigt**
2. **Rothamsted e-RA – weitere Complete Open Access Datasets mit Jahren ≥2013** | https://www.era.rothamsted.ac.uk/info/datasets | Broadbalk Hafer 1996–2022 (10.23637/rbk1-oatyld9622-01), Broadbalk Silomais 1997–2017 (10.23637/rbk1-fmyield9717-01), Broadbalk Ackerbohne 1968–2022 (10.23637/rbk1-beanyld6822-01), Broadbalk Wheat Section 1 yields+N uptake 2001–2015 (10.23637/rbk1-yldS10115-01), Exhaustion Land P-test yields 1986–2023 (10.23637/REX4-PTESTYLD78623-1), Woburn Ley-arable Weizen 1976–2018 (10.23637/wrn3-wheat7618-01), Park Grass Heuerträge 1965–2024 (10.23637/rpg5-PGYields19652024-2, Grünland), Hoosfield Mittelwerte Sommergerste 1852–2015 (10.23637/KeyRefOAHByields, Summary) | UK, Harpenden/Woburn (Bedfordshire) | named station findable | Kleinparzellen → only site mean | s. o.; ≥2013 bei allen genannten | 1 Feld je Experiment (Broadbalk, Hoosfield, Exhaustion Land, Woburn Ley-arable, Park Grass) | ca. 5 Felder × 3–10 Jahre ≈ 30–40 | Korn/Stroh t/ha bei 85 % TM (Weizen); Hoosfield nur Mittelwerte | Behandlungen, Saat-/Erntedaten, Sorten (Frictionless-Pakete) | CC BY 4.0 | wie 1. (Formular, direkt) | low | 3 | **bestätigt** (Liste geöffnet; Einzel-DOIs nicht alle geöffnet)
3. **Rothamsted e-RAdata (vollständige Plot-Rohdaten, Data Extraction Tool)** | https://www.era.rothamsted.ac.uk/ | alle LTE-Kulturen | UK | named station | Plots → only site mean | alle Jahre | alle e-RA-Experimente | wie 2. | Plot-Erträge | ohne Metadaten | nicht angegeben (vermutlich wie OAD) | Registrierung/Passwort, Kontakt era@rothamsted.ac.uk | medium | 2 | **bestätigt** (Beschreibung gesehen, Tool nicht genutzt)
4. **North Wyke Farm Platform Data Portal (Rothamsted)** | https://nwfp.rothamsted.ac.uk/ | Grünland (Weide/Silage), 3 Farmlets à ~21 ha, 15 Einzugsgebiete | UK, Devon | field polygons (Catchments) | 1–8 ha je Catchment | ab 2011 (Portal nennt keine Jahre) | 15 Catchments | n/a für Ackerbau | Grünlandproduktion/Silage; **keine Ackererträge auf Portalseite bestätigt** | Wasser/Luft/Boden 15-min-Daten | nicht genannt; "publicly available" | Registrierung erforderlich (Vorschau ohne Account) | medium | 1 (für Ackerkulturen) | **bestätigt** (Portal), Ackererträge unbestätigt
5. **GLTEN Metadata Portal** | https://glten.org/ (TLS-Zertifikat abgelaufen; curl -k) | alle | weltweit, 346 Experimente | Site Location ist Metadatenfeld | – | – | 346 LTEs | – | **keine Ertragsdaten, nur Metadaten** (Design, Kulturen, Faktoren, "Related Resources") | Kontakt glten@rothamsted.ac.uk; Hilfe https://gltenhelp.readthedocs.io/ ("Documentation for the API will appear here") | nicht genannt | frei lesbar; Login nur für Editor | high (Browser nötig, Zertifikatswarnung) | 1 (als Datenquelle), 3 (als Findehilfe) | **teilweise bestätigt** (Startseite per curl; Liste der 346 Experimente nicht durchgesehen)
6. **CYCleSS – Crop Yields, Climate, Soils and Satellites (UK)** | https://doi.org/10.6084/m9.figshare.27225807 (figshare, Paper: https://doi.org/10.1038/s41597-025-06528-x, PMC13035921) | Winterweizen, Winterraps, Sommer- und Wintergerste, Bohnen | England | **nur 10-km-Raster** (Feldlage von UKCEH entfernt; Umweltdaten auf 1 km² ausgerichtet) → **erfüllt Standortkriterium nicht** | "934 fields"/"934 areas of 1 km²" (Paper uneinheitlich); Feldfläche nicht angegeben | 2015–2017 | 934 (201/292/443 Rasterzellen 2015/16/17) | ~936 Feld-Jahre, aber ohne Feldlage | Mittlerer Ertrag t/ha je Feld aus Mähdrescher-Ertragsmonitoren (ASSIST Precision Yield Dataset); Feuchtebasis nicht genannt | Sentinel-1-Bänder, Tageswetter, Bodentyp bereits beigefügt | Datensatz CC0 1.0; Paper CC BY 4.0 | direkter Download (ZIP 5,6 MB); Rohdaten nur über UKCEH-Autoren (Pywell, Redhead) unter NDA | low | 2 (Lage zu grob; gut als Benchmark/Transfer-Test) | **bestätigt**
7. **UKCEH ASSIST Precision Yield Dataset (Rohdaten, Combine-Ertragskarten)** | genannt im CYCleSS-Paper (s. 6); EIDC-Sammlung ASSIST: https://catalogue.ceh.ac.uk/documents/d15f6fc4-10a3-411d-a8c9-6bddd5c492ba | Weizen, Raps, Gerste, Bohnen | England | field polygons/Yield-Maps (nicht öffentlich) | ganze Schläge | 2015–2017 (ggf. mehr) | 934+ Felder | hoch, aber NDA | Combine-Yield-Monitor | – | NDA mit Landwirten | **on request**: UKCEH (R. Pywell, J. Redhead; enquiries@ceh.ac.uk); EIDC-Sammlung selbst enthält nur das Wheat-yield-resilience-Produkt (10-km-Raster, 2008–2017, aus Defra-Erhebung) | high | 2 (Realismus der Freigabe gering) | **unbestätigt** (kein eigener Datensatz-Eintrag gefunden)
8. **Hillesden Experimental Platform arable yields 2006–2011** | https://catalogue.ceh.ac.uk/documents/e54069b6-71a9-4b36-837f-a5e3ee65b4de | Weizen, Raps, Ackerbohne | England, Buckinghamshire | Feldebene (BNG), keine Koordinaten auf Seite | ganze Schläge | 2006–2011 (**kein Jahr ≥2013**) | n. g. (Blockversuch, 3 Behandlungen) | 0 | Gesamtertrag je Feld per Combine-Yield-Meter, t/ha, Verhältnis zum Regionsmittel | ELS-Behandlungen | OGL | direkter ZIP-Download | low | 1 (Jahre) | **bestätigt**
9. **Winter barley field trial with microplastics, Abergwyngregyn 2020–2021 (EIDC)** | https://catalogue.ceh.ac.uk/documents/a5410834-1c38-455b-a850-3fb3434d4bb0 | Wintergerste | Wales | named station (Henfaes) | Parzellen → only site mean | 2020–2021 | 1 | 2 | Kornertrag (Einheit nicht gesehen) | N2O, Boden | OGL (üblich bei EIDC, nicht geprüft) | direkt | low | 1 | **bestätigt** (nur Katalogeintrag)
10. **AHDB Recommended Lists – Harvest Results (Excel-Ertragstabellen aller geernteten Versuche)** | https://ahdb.org.uk/harvestresults ; Service-Beschreibung https://ahdb.org.uk/knowledge-library/about-the-rl-harvest-results-service | Winter-/Sommerweizen, Winter-/Sommergerste, Hafer, Winterraps (+ Beschreibende Listen Sommerraps, Lein, Triticale, Roggen) | UK (GB-weit) | Versuchsorte benannt (Betrieb/Ort); Koordinaten nicht gesehen → **unbestätigt** | Sortenparzellen → only site mean | jährlich; "Harvest results archive" für Vorjahre (Umfang nicht gesehen) | geschätzt 20–40 Versuchsorte/Jahr je Kultur (nicht verifiziert) | unbekannt | Kornertrag t/ha (behandelt/unbehandelt), Qualität, Krankheiten | Sorten, Fungizidbehandlung | © AHDB "All Rights Reserved", AGB nicht gelesen → nicht-kommerzielle Nutzung anfragen | Web/Excel-Download, E-Mail-Alerts | medium–high | 3 (falls Standorte lokalisierbar) | **teilweise bestätigt** (Seiten geöffnet, Excel nicht geöffnet)
11. **James Hutton Institute – Centre for Sustainable Cropping (Balruddery Farm)** | https://bio4ag.hutton.ac.uk/contact.html (Hutton-Facility-URL 404) | Rotation Gerste/Weizen/Raps/Kartoffel/Ackerbohne (lt. Projektbeschreibung, nicht verifiziert) | Schottland, Invergowrie/Dundee | named station | Großparzellen/Feldhälften | ab 2009 | 1 Farm (~6 Felder) | unbekannt | – | – | nicht genannt | **on request**: Cathy Hawes, cathy.hawes@hutton.ac.uk | medium | 2 | **unbestätigt**
12. **Teagasc Oak Park – Crop establishment and rotation trials (seit 2014) / Open Data** | https://data.gov.ie/dataset?q=teagasc+yield ; Teagasc-Open-Data-URL (teagasc.ie/about/research--innovation/open-data) **404** | Winterweizen u. a. (Agriland-Bericht) | Irland, Carlow | named station | Parzellen | seit 2014 | 1 | unbekannt | – | – | data.gov.ie-Datensätze (AYAF Grünland Athenry 2018–2022) CC-BY-NC; Ackerversuche nicht publiziert | **on request**: Teagasc Crops Research Centre Oak Park (keine Personenangabe gefunden) | medium | 2 | **unbestätigt**
13. **DIVINE Pilot 2 Yield Data 2023–2025 (UCD Lyons Farm)** | https://zenodo.org/records/19219514 (DOI 10.5281/zenodo.19219515) | Gerste | Irland, Celbridge, Co. Dublin | named station ("Field 62"), keine Koordinaten | ein Feld (Größe n. g.) | 2023–2025 | 1 | 3 | nicht beschrieben (Excel 35,6 kB) | – | CC BY 4.0 | direkt | low | 2 | **bestätigt**

#### Frankreich

14. **EFELE long-term site: crop yields and C,N,P,K,Mg exports over 9 years** | https://doi.org/10.57745/MZ79D8 (Landing Page bot-geschützt; Metadaten über https://b2find.eudat.eu/dataset/e92ef2db-f563-5288-903a-c513734b3224) | Silomais, Weizen, Senf-Zwischenfrucht | Frankreich, SOERE-PRO-Standort EFELE (Bretagne; Koordinaten nicht im Record) | named station findable | Parzellen → only site mean | 2012–2020 (≥2013: 8) | 1 Standort, Experimente "PROs" und "TS/MO" | ~8 | Erträge (Einheit n. g.) + Nährstoffexporte | Bewirtschaftung, org./min. Düngung, Tageswetter | Etalab 2.0 (Open) | direkt (TSV, PDF); Kontakt Thierry Morvan (INRAE) | low | 3 | **bestätigt** (via B2FIND/DataCite)
15. **Innovative cropping systems trial Grignon 2009–2020 (ICC-Versuch, 4 Systeme)** | https://doi.org/10.57745/5TJJZA (Data in Brief: https://pmc.ncbi.nlm.nih.gov/articles/PMC11043882/) | Weizen, Gerste, Hafer, Triticale, Winterraps, Lein, Erbse, Ackerbohne, Soja, Mais, Hanf | Frankreich, Grignon (48.84 N, 1.95 E) | coordinates ≤100 m | 12 Parzellen auf 6,2 ha (~0,5 ha) → only site mean / ggf. Parzelle | 2009–2020 (≥2013: 8) | 1 Standort, 12 Parzellen | ~8 (×4 Systeme) | Combine-Ernte 75–140 m², q/ha bei 0 % TM (Hanf t TM/ha), Ertragskomponenten | Wachstumsstadien, Biomasse, N-Gehalt, Energie/TFI | Etalab 2.0 | direkt; Kontakt caroline.colnenne-david@inrae.fr | low | 4 | **bestätigt** (Paper + DataCite; Landing Page nicht geöffnet)
16. **PROspective long-term field experiment (INRAE Colmar) – Agronomic management + plant data 2000–2019** | DataCite: 10.57745/4byxtk (Beschreibung), 10.57745/77afbh (agronomic management), 10.57745/bpb34g (plant data) | Mais, Winterweizen, Zuckerrübe, Gerste (Rotation) | Frankreich, Colmar (48°03′33″ N, 7°19′42″ E) | coordinates ≤100 m | 24 Parzellen à 10 m × 9 m auf 2 ha → only site mean | 2000–2019 (≥2013: 7) | 1 | ~7 | Erträge "not explicitly stated" in Metadaten (in Plant-/Management-Dateien zu prüfen) | org. Düngemittel, 0–170 kg N/ha | nicht angegeben | Recherche Data Gouv (Browser); Kontakt Aurélia Michaud, Florent Levavasseur, Sabine Houot (INRAE) | medium | 2 | **teilweise bestätigt** (DataCite-Metadaten)
17. **French SOERE soil monitoring dataset with management (LANDMARK datamart: QualiAgro + PROspective)** | DataCite 10.15454/jtve46 | Rotation Mais/Weizen (QualiAgro, Paris Basin, 450-m²-Parzellen) und Colmar | Frankreich | named station | Parzellen → only site mean | 2010–2015 (QualiAgro), 2014–2018 (PROspective) | 2 | ~8 | Erträge + Management | Bodenprofile | nicht angegeben | Recherche Data Gouv; Kontakt Nicolas Saby (INRAE) | medium | 2 | **teilweise bestätigt**
18. **Rés0Pest – Synthèses annuelles 2013–2023 (pestizidfreie Systemversuche, INRAE-Netzwerk)** | DataCite 10.57745/0q0hnz (Teil von 10.57745/msnv7m) | n. g. (Ackerkulturen) | Frankreich, mehrere Versuchsstationen (Standorte im Record nicht genannt) | unbekannt | Parzellen/Systemversuche | 2013–2023 | mehrere (n. g.) | unbekannt | Parzellenerträge laut Abstract erklärt | Anbauentscheidungen | **keine Lizenz eingetragen** | Recherche Data Gouv; Kontakt Vincent Cellier (INRAE) | medium | 2–3 | **unbestätigt** (Inhalt)
19. **Pea_dataset – 4,450 site×genotype×year combinations across France 2002–2024** | DataCite 10.57745/fw78re | Körnererbse (Winter/Sommer, 117 Genotypen) | Frankreich, 158 Standorte | Standortnamen; Koordinaten im Record nicht genannt | Sortenparzellen → only site mean | 2002–2024 (≥2013 enthalten) | 158 Standorte | geschätzt mehrere hundert Standort-Jahre (nicht verifiziert) | Ertrag, Proteingehalt | Management, Boden, Tageswetter | nicht angegeben | Recherche Data Gouv; Kontakt Abdourahmane Diallo (INRAE Agroécologie Dijon) | medium | 3 (Kultur nicht prioritär) | **teilweise bestätigt**
20. **ALLIANCE – 79 Feldversuche 2009–2016 (Raps/Weizen mit Leguminosen-Begleitpflanzen)** | DataCite 10.15454/bjqllk | Winterraps, Winterweizen | Frankreich | n. g. | Parzellen | 2009–2016 (≥2013: 4) | 79 Versuche | unbekannt (ggf. nur Synthese) | Ertrag | – | CC BY 4.0 | Recherche Data Gouv | medium | 2 | **teilweise bestätigt**
21. **Cover-crop mulch / spring barley three-site trial Burgundy 2021–2022** | DataCite 10.57745/g6os9z | Sommergerste | Corbigny, Gemeaux, Simandre (Burgund) | Ortsnamen | 192 Parzellen → only site mean | 2021–2022 | 3 | 3 | Kornertrag, Protein | Zwischenfrucht-Biomasse, N_min | nicht angegeben | Recherche Data Gouv; Kontakt Stéphane Cordeau (INRAE) | low | 2 | **teilweise bestätigt**
22. **Sunflower varieties × verticillium wilt, 9 French platforms 2016** | DataCite 10.15454/vg4e-mk17 | Sonnenblume | Frankreich, 9 Plattformen | n. g. | Parzellen | 2016 | 9 | 9 | Ertragsverlust je Krankheitsklasse | – | CC BY 4.0 (lt. Listing) | Recherche Data Gouv | medium | 1–2 | **unbestätigt**
23. **SOERE/IR ACBB (Lusignan Grünland-Acker, Estrées-Mons Ackerbau seit 2009/2010)** | kein offenes Portal gefunden; Tutorial https://vsoil.inrae.fr/repo/external/user_doc/tuto-SOERE-ACBB.pdf ; ICOS FR-EM2 s. 29 | Erbse/Weizen/Raps/Gerste/Mais (Mons), Grünland-Acker (Lusignan) | Frankreich | named station | Großparzellen | seit 2009 | 2 Ackerstandorte | unbekannt | Erträge in ACBB-Datenbank (Abfragetool mit Authentifizierung) | Boden, Klima, N | nicht genannt | **on request** über ACBB-Datenbank/ANAEE-France; kein Kontakt verifiziert | high | 2 | **unbestätigt**
24. **Weitere französische Treffer, ausgeschlossen wegen Jahren <2013**: Kerbernez Futterbau 1978–2005 (10.57745/p8nnzk), Soil compaction LTE Nordfrankreich 1989–2007 (10.15454/j2kcxm), Mitigating crop yield losses through weed diversity (10.15454/en10-2v70, 3 Jahre, 54 Zonen, Jahre n. g., CC BY 4.0).
25. **ARVALIS / Terres Inovia / Chambres d'agriculture / DEPHY**: keine offenen Parzellen-Ertragsdatensätze gefunden (DEPHY-Ergebnisse nur als PDF-Synthesen, z. B. https://ecophytopic.fr/sites/default/files/2021-08/Synth%C3%A8se%20essais%20syst%C3%A8mes%202-VF_0.pdf). **unbestätigt/Gap**.

#### Belgien / Niederlande / Luxemburg

26. **ICOS BE-Lon Lonzée – ETC L2 ARCHIVE 2017–2025** | Station: https://meta.icos-cp.eu/resources/stations/ES_BE-Lon ; Archiv (aktuell): https://meta.icos-cp.eu/objects/1C47QsmFVk5ECiOXWS2JOEyF ; ältere Version https://meta.icos-cp.eu/objects/99gAK7xqcSkk7SRKDwZz1KJT | Zuckerrübe / Winterweizen / Kartoffel / Winterweizen (4-jährige Rotation) | Belgien, Hesbaye, Prov. Namur | coordinates ≤100 m (50.55162 N, 4.746234 E) | **11,8 ha Feld** | 2017–2025 (ältere Daten 2004–2016 über FLUXNET2015) | 1 Feld | 9 | Archiv enthält "continuous fluxes, meteorological data, ancillary data and metadata"; **Ertrags-/Biomassevariable (Cropland Ancillary Vegetation Measurements) nicht im Archiv geöffnet** | Management/Phänologie laut ICOS-Instruktion "Ancillary Vegetation Measurements in Cropland" (https://www.icos-etc.eu/icos/documents/instructions) | ICOS CC BY 4.0 Data Licence | direkter Download (114 MB ZIP, 204 Downloads); PI Benjamin Dumont (ULiège Gembloux), info@icos-ri.eu | medium | 4 (falls Ertrag enthalten, sonst 3) | **teilweise bestätigt**
27. **Agricultural yield database Flanders (ILVO/KU Leuven, PEILIMPACT)** | https://zenodo.org/records/8017476 (v2; v1 10.5281/zenodo.7541363) | Mais, Winterweizen, Zuckerrübe, Kartoffel, Gras | Belgien, Flandern | **nicht angegeben** (Quellen: ILVO-Forschungsabteilungen, Sortenversuche, Behörden) | n. g. | n. g. (Beschreibung nennt keine Jahre) | n. g. | unbekannt | t/ha; Feuchte n. g.; Saat- und Erntedaten "when available", Schnittzeitpunkte Gras | CSV 186 kB + Doku | **CC BY-NC-SA 2.0**, nur nicht-kommerziell | direkt; kommerziell via Sarah Garré (ILVO) | low | 2–3 (Lagegenauigkeit prüfen) | **bestätigt**
28. **LTM_AC_crop – long-term crop yield monitoring in alley cropping fields, Belgium** | https://zenodo.org/records/10692761 (10.5281/zenodo.10692760) | Mais, Weizen, Gerste, Kartoffel | Belgien (Flandern), 6 Agroforst-Felder | n. g. | Transekte 2/5/12 m vom Baum → Teilflächen | 2015–laufend | 6 | ≥ 6×8 ≈ 48 (nicht verifiziert) | TM-Ertrag, Qualität | – | n. g. | **Restricted** (Zenodo-Anfrage an ILVO/UGent) | medium | 2 | **bestätigt** (Record), Daten gesperrt
29. **ICOS-Ackerstationen mit ETC-L2-ARCHIVE (SPARQL-Abfrage meta.icos-cp.eu, Ökosystemtyp "cropland")** | https://data.icos-cp.eu/ (Filter Station) | diverse Ackerrotationen | BE-Lon Lonzée 2017–2025; **FR-Gri Grignon 2021–2025**; **FR-Lam Lamasquère 2020–2024**; **FR-EM2 Estrées-Mons A28 2017–2025**; **FR-Aur Auradé 2019–2025**; **DK-Vng Voulundgaard 2020–2023** (Station heißt DK-Vng, nicht "DK-Vou"); (DE-Geb, DE-Kli, DE-RuS, DE-Brs, IT-BCi außerhalb Scope) | coordinates ≤100 m (Stationsseiten) | Felder ~10–20 ha (FR-Gri ~19 ha lt. FLUXNET-Seite https://fluxnet.org/sites/siteinfo/FR-Gri) | s. Station | 6 Stationen im Scope | ca. 6 Stationen × 4–9 Jahre ≈ 35 | Ancillary-Daten im Archiv (Ertrag zu verifizieren) | Flüsse, Meteo, Phenocam | ICOS CC BY 4.0 | direkt | medium | 4 | **teilweise bestätigt** (Objektliste per SPARQL gesehen); **FI-Jok, FI-Qvd, SE-Lnn: keine ETC-L2-ARCHIVE-Objekte als Cropland gefunden**
30. **BASIS long-term tillage experiment Lelystad 2009–2022 (WUR Open Teelten)** | https://data.4tu.nl/datasets/5708634c-05b4-40e2-9d3e-9c12fcad7882 (10.4121/5708634c-05b4-40e2-9d3e-9c12fcad7882) | Ackerfrüchte (Wurzel-/Hackfrüchte, feinsamige Kulturen; Einzelkulturen nicht gelistet – in Excel prüfen) | Niederlande, Lelystad (Flevoland) | named station; keine Koordinaten im Record | 5 Felder (3 bio, 2 konventionell), Größe n. g.; 4 Bodenbearbeitungssysteme (PL, RT, RTS, RT/SPL) → Teilflächen | 2009–2022 (≥2013: 10) | 5 | ~50 Feld-Jahre | Ertrag, marktfähiger Ertrag (Data_yield_BASIS.xlsx), Einheit n. g. | Boden chem./phys. | CC BY 4.0 | direkt (ZIP 2,2 MB) | low–medium | 3 | **bestätigt**
31. **Agronomic dataset on potato growth and yield in the Netherlands (WUR)** | https://dataverse.harvard.edu/citation?persistentId=doi:10.7910/DVN/1LC6W7 | Kartoffel | Lelystad (Ton), Vredepeel (Sand) | named station | Parzellen → only site mean | 2019–2020 | 2 | 4 | Knollenbiomasse/Marktfähigkeit bei Ernte, NPK | Wetter, Bodenfeuchte, LAI, Reflexion, Phänologie | **CC BY-NC-SA 4.0** | direkt; Kontakt Sander.Janssen@wur.nl | low | 2 | **bestätigt**
32. **Biomass, yield and light interception in cereal-legume intercropping, Wageningen 2022–2024 (DANS)** | DataCite 10.17026/ls/gacetg | Gerste, Roggen, Triticale, Weizen, Erbse, Ackerbohne | Niederlande, Wageningen | named station | Kleinparzellen | 2022–2024 | 1 | 3 | Ertrag | LAI/Licht | n. g. | DANS Data Station | low | 1 | **unbestätigt**
33. **WUR NPPL / Boerderij van de Toekomst / Farm of the Future** | https://www.wur.nl/nl/onderzoek/plant/precisielandbouw | – | NL | – | – | – | – | – | "yield per m² determination" vorhanden, **keine Veröffentlichung gefunden** | – | – | ggf. on request WUR Precision Agriculture | – | – | **unbestätigt/Gap**
34. **CRA-W Gembloux Dauerversuche (SYCBio, SYCMa, SPOT) / Livre Blanc Céréales** | https://www.cra.wallonie.be/uploads/2023/11/asbio2023-presacraw.pdf | Getreide, Ackerbau | Belgien, Wallonien | – | – | – | – | – | nur Jahresberichte (Livre Blanc) | – | – | on request info@cra.wallonie.be | – | 1 | **unbestätigt**
35. **Luxemburg**: keine Treffer (LIST/ASTA nicht gefunden) – **Gap**.

#### Dänemark

36. **Landsforsøgene / Nordic Field Trial System – WebTrial Einzelversuchs-Viewer** | https://webtrial.dlbr.dk/TrialView?country=DK (Portal https://nfts.dlbr.dk/ ; Tabellenanhänge https://nfts.dlbr.dk/tabelbilag.aspx – 404 bei Abruf) | Winter-/Sommerweizen, Gerste, Roggen, Triticale, Hafer, Erbse, Ackerbohne, Lupine, Soja, Kartoffel, Raps/Saaten, Futter | Dänemark (+ Norwegen, Schweden) | Versuchsorte mit Karte ("ForsogPlacering") – Koordinatengenauigkeit **nicht verifiziert** | Parzellenversuche → only site mean | Filter Erntejahr 2018–2027 (Ergebnistabellen getrennt ab 2018 / bis 2017) | mehrere hundert Versuche/Jahr (nicht gezählt) | potenziell > 1000, aber nur per Web-Viewer | hkg Korn/ha (Standard 85 % TM lt. Berechnungsnotiz https://www.landbrugsinfo.dk/-/media/landbrugsinfo/public/d/6/f/planter_kval_landsfors_bere_formler_til_beregning_af_landsforsog.pdf) mit Konfidenzintervallen | Sorten, Fungizid, Saatzeit, Düngung, Bodenbearbeitung | **nicht genannt** (SEGES Innovation) | öffentlich lesbar, Login für Berater; **kein Bulk-Download gesehen** | high (Scraping/Anfrage an SEGES) | 3 | **teilweise bestätigt**
37. **BioBase long-term field trial, AU Foulum – Yield data 2013–2021** | https://doi.org/10.6084/m9.figshare.25593516 (api.figshare.com/v2/articles/25593516) | 14 Anbausysteme (Biomasse-/Ackerkulturen, nicht einzeln gelistet) | Dänemark, Foulum | named station (keine Koordinaten) | Parzellen (Block/Row/Column) → only site mean | 2013–2021 (Datei "2013–2022") | 1 | 9 | TM-Ertrag und Rohproteinertrag je Parzelle (Einheit n. g.) | – | CC BY 4.0 | direkt (xls 104 kB); Autor Søren Ugilt Larsen | low | 2 | **bestätigt**
38. **Askov Long-Term Experiments (AU, seit 1894)** | https://agro.au.dk/en/about-the-department/long-term-experiments ; Report DCA 151 https://dcapub.au.dk/djfpublikation/djfpdf/DCArapport151.pdf | Winterweizen, Sommergerste, Rotation | Dänemark, Askov | named station | Parzellen → only site mean | bis 2019/2021 (Publikationen) | 1–2 Felder | ~8 | Erträge in Reports/Papern, **kein Download-Datensatz** | – | – | **on request**: Jørgen Eriksen (jorgen.eriksen@agro.au.dk), Bent T. Christensen; Abteilungsleiter J. E. Olesen jeo@agro.au.dk | medium | 2 | **unbestätigt**
39. **Weitere AU-LTEs (Foulum, Flakkebjerg, Jyndevad: CENTS Bodenbearbeitung, Arable crop rotation, Organic dairy rotation, P-Depletion, Biochar)** | wie 38 | diverse | DK | named station | Parzellen | laufend | ~6 | unbekannt | keine Datenangaben auf Seite | – | – | on request (comm@agro.au.dk) | medium | 2 | **unbestätigt**
40. **Nordic/Baltic wheat fungicide efficacy trials 2012–2016 (weather, development stage, yield)** | https://doi.org/10.6084/m9.figshare.19203377.v4 | Winter- und Sommerweizen | DK, FI, LT, NO, SE | nur Regionen/Wetterstationen, **keine Versuchsorte** | Parzellen | 2012–2016 (≥2013: 4) | n. g. | unbekannt | Yield.xlsx (Einheit n. g.) | Entwicklungsstadien, Wetter | CC BY 4.0 | direkt; Autor Björn Andersson (SLU) | medium | 2 | **bestätigt**

#### Schweden

41. **SLU long-term field experiments: Swedish soil fertility experiments R3-9001, 1962–2022** | https://researchdata.se/en/catalogue/dataset/2024-462 (DOI 10.5878/eqj9-j270) | Rotationen Getreide/Raps/Zuckerrübe/Leguminosen (Kulturen im Record nicht gelistet) | Schweden: 9 aktive Standorte in Skåne, Västra Götaland, Östergötland, Uppland | Standortnamen in `locations.tsv` (Koordinaten unbekannt) → named station findable | Parzellen → only site mean | 1962–2022 (≥2013: 10) | 9 | ~90 | jährliche Erträge (Einheit/Feuchte in units.tsv) | Behandlungen, Bodenanalysen | **CC0 1.0** | direkter Download (R39001_data.tsv 21,6 MB + Doku); Kontakt soilnutrientcycling@slu.se | low–medium | 4 | **bestätigt**
42. **SLU frame trial R3-RAM56 Ultuna 1956–2023** | https://researchdata.se/en/catalogue/dataset/2024-468/1 (DOI 10.5878/7f5n-vp94) | Getreide | Uppsala | named station | Rahmenparzellen (sehr klein) → only site mean | 1956–2023 | 1 | ~10 | Erträge, Nährstoffgehalte | – | vermutlich CC0 | direkt | low | 1–2 | **unbestätigt** (nur Suchtreffer)
43. **Data on effects of crop rotational diversity and N fertilisation on cereal yields (32 LTEs, Smith & Bommarco)** | https://doi.org/10.5878/8af1-0q60 | Getreide | Europa/Nordamerika | Standortmittel | – | 1958–2020 | 32 | – | **standardisierte** Erträge (relativ zum Standortmittel) → als Label ungeeignet | – | keine Lizenz genannt | direkt (SND) | – | 1 | **bestätigt**
44. **Determinants of yield variation of organic cereals (Lund/SLU), 2020** | https://researchdata.se/catalogue/dataset/2025-366 (DOI 10.5878/z95f-6h51) | Sommergerste (52 Felder), Winterweizen (29) | Skåne, Halland, Västergötland | **nur Region** | ganze Schläge | 2020 | 81 Felder / 56 Betriebe | 81 (ohne Lage) | Ertrag landwirtsberichtet; Feldmessungen Unkraut/Boden aus 4 Plots | Management | CC0 | direkt; Kontakt melanie.karlsson@cec.lu.se | low | 1–2 | **bestätigt**
45. **Dryad-Datensätze Schweden (Raps 15 Felder 10.5061/dryad.8g3j2; Rotklee-Samen 50 Felder 10.5061/dryad.1h5717p; Gerste 2017 10.5061/dryad.m0cfxpp3k)** | DataCite-Treffer | Raps, Rotklee, Gerste | Südschweden | Region/anonymisiert | Felder | 2017 ff. | 15–50 | gering | gemessen/landwirtsberichtet | – | CC0 (Dryad) | direkt | low | 1 | **unbestätigt**
46. **SLU Fältforsk / Sortprovning / Lantmet** | https://www.slu.se/faltforsk | Sortenversuche, Feldversuche | Schweden | – | Parzellen | laufend | – | – | Ergebnisse über NFTS (Schweden im WebTrial-Viewer, s. 36) | – | nicht genannt | Kontakte: NFTS Lotta Tuoremaa nfts.ffe@slu.se; LTE-Koordination Johanna Wetterlind johanna.wetterlind@slu.se; Leitung Anneli Lundkvist | medium | 3 | **bestätigt** (Seite), Daten nicht gesehen
47. **Vertical agrivoltaic barley Kärrbo Prästgård 2023** | 10.5281/zenodo.12655140 | Gerste | Schweden | named | 50 Plots à 0,25 m² | 2023 | 1 | 1 | kg TM/ha | Wetter | CC BY (Zenodo) | direkt | low | 1 | **unbestätigt**

#### Norwegen / Finnland / Nordisch

48. **A multi-environment dataset of official field trials for three major crops in the Nordic countries (NordBalFoodSec)** | https://dataverse.no/citation?persistentId=doi:10.18710/IZ3EFE (Paper Sci Data 13, 1219 (2026), 10.1038/s41597-026-07801-3; Luke-Repo https://jukuri.luke.fi/items/952101b8-68c0-440c-9194-3e505c6d2bd6/full) | **Sommergerste**, Rotklee, Kartoffel | DK, NO, SE, IS, FI | "location of each trial is reported" – Koordinaten vs. Ortsnamen **nicht verifiziert** | Sortenparzellen → only site mean | 1970–2024 (NO Gerste 2014–2024, NO Kartoffel 2018–2024) | n. g. (01_BarleyData.csv 16,5 MB → viele Versuche) | geschätzt mehrere hundert Standort-Jahre ≥2013 (nicht gezählt) | Ertrag (Einheit in README) | Sorten, VCU-Daten | CC BY 4.0 | direkter Download (ZIP 22,3 MB, Guestbook), API; Kontakt Silius M. Vandeskog (Norsk Regnesentral) | medium | 4 | **bestätigt**
49. **Luke – Viralliset lajikekokeet (offizielle Sortenversuche) PxWeb-Datenbank** | https://px.luke.fi/PxWeb/pxweb/fi/maatalous/maatalous__lajikekokeet/ ; API z. B. https://px.luke.fi/PxWeb/api/v1/fi/maatalous/lajikekokeet/julkaisuvuosi_2025/sato/ohra/140500sato_koepaikka_ohra.px | Gerste, Hafer, Sommer-/Winterweizen, Roggen, Triticale, Sommerraps, Erbse, Ackerbohne, Timothe, Schwingel, Raigras, Rotklee | Finnland, 12 Versuchsstandorte (Inkoo, Loviisa, Iitti, Lieto, Jokioinen, Hauho, Jyväskylä, Isokyrö/Ylistaro, Maaninka, Ruukki, Sotkamo, Tervola/Rovaniemi) | named station findable | Parzellen → only site mean | 2018–2025 (Publikationsjahre 2016–2025) | 12 | **nur gepoolte Schätzwerte**: Tabellen "koepaikoittain" (je Standort über 2018–2025) und "vuosittain" (je Jahr über alle Standorte) – **kein Standort×Jahr** | Sato kg/ha (Mischmodell-Estimate, Anzahl Versuche, Differenz, P-Wert), Wuchszeit, Lager, TKG, HL, Protein | Boden-/Zonenklassifikation | nicht angegeben (Luke-Statistik i. d. R. CC BY 4.0 – zu prüfen); Luke-Prospekt nennt Versuche als kundenfinanziert/vertraulich | frei per PxWeb/API (JSON, CSV); Rohdaten je Versuch **on request** varietytesting@luke.fi | medium | 2 (Aggregation), 4 falls Rohdaten | **bestätigt**
50. **NIBIO Apelsvoll (Systemversuch seit 1989) / Møystad** | https://nibio.no/en/about-eng/addresses/apelsvoll | Getreide, Kartoffel, Futter | Norwegen | named station | Großparzellen/Modellbetriebe | seit 1989 | 1 | – | **kein offener Datensatz gefunden** (NIBIO kuratiert Datensätze in DataverseNO) | – | – | on request NIBIO Apelsvoll (Leitung früher Audun Korsæth) | high | 2 | **unbestätigt**
51. **Luke Open Data / Etsin (Fairdata)** | https://etsin.fairdata.fi/datasets?facet_organization=Luonnonvarakeskus (JS-Seite, nicht auswertbar) | – | Finnland | – | – | – | – | – | keine Ertrags-Feldversuche verifiziert | – | CC BY 4.0 (Portal) | – | – | – | **unbestätigt/Gap**

#### EU-weit / mehrere Länder

52. **Database of field experiments on organic farming yield and stability in European arable land (EJP SOIL ARTEMIS)** | https://zenodo.org/records/14258149 | Winterweizen, Roggen, Sommergerste, Sommerweizen, Hafer | 50 Experimente/45 Standorte in 15 Ländern (SE 7, DK 4, FI 2, NO 2, UK 2, NL 1, FR 1 …) | n. g. | Parzellen | 3–30 Jahre je Versuch (Kalenderjahre n. g.) | 45 | unbekannt | Ertrag | – | CC BY 4.0 | **Embargo bis 2027-10-31** | – | 1 (derzeit) | **bestätigt**
53. **Global dataset of 37 field experiments cereal-legume intercrops and sole crops (2001–2017)** | https://zenodo.org/records/14160885 | Gerste, Hart-/Weichweizen, Erbse, Ackerbohne, Lupine, Linse, Kichererbse | FR, DK, England, DE, IT | keine Koordinaten im Record | Parzellen | 2001–2017 (Anteil ≥2013 unbekannt) | 37 Experimente, 607 Einheiten | gering | Ertrag (Einheit in metadata.xlsx) | Management, Klima | CC BY 4.0 | direkt | medium | 2 | **bestätigt**
54. **Metadata of agricultural LTEs in Europe excl. Germany (BonaRes)** | https://pmc.ncbi.nlm.nih.gov/articles/PMC8408514/ (DOI 10.20387/bonares-eff3-0mb4) | – | 186 LTEs in 22 Ländern (BE, DK, FI, FR, GB, NO, SE; **nicht NL, IE**) | Standortmetadaten | – | – | 186 | – | **nur Metadaten/Kontakte**, keine Erträge | – | open access | direkt | – | 2 (Findehilfe) | **bestätigt**
55. **Cover crop dataset France, 37 experiments 2004–2022 (Data in Brief 2025)** | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12337125/ | Zwischenfrüchte (33 Arten) | Frankreich | – | – | 2004–2022 | 37 | – | Zwischenfrucht-Biomasse, **keine Hauptfruchterträge** | – | – | – | – | 1 | **unbestätigt** (nicht geöffnet)

### Inferences
- Für das BWKI-Ziel (Satellit → Ertragsverlust auf Schlagebene) sind die ICOS-Ackerstationen die einzigen offenen Quellen mit großen, polygon-fähigen Einzelfeldern (10–20 ha) und CC BY 4.0; der Nachweis, dass Ertrag/Erntebiomasse im ETC-L2-ARCHIVE (Ancillary) steckt, muss durch Öffnen eines Archivs erfolgen (ICOS-Instruktion "Ancillary Vegetation Measurements in Cropland" existiert).
- Alle Dauerversuche (Rothamsted, SLU, INRAE, AU) liefern nur Standortmittel kleiner Parzellen; sie taugen als "Site-mean"-Labels mit Standortkoordinate, nicht für Pixel-Training.
- Sortenversuchsnetze (AHDB, NFTS/Landsforsøgene, Luke, nordische DataverseNO-Sammlung) sind zahlenmäßig die größte Quelle an Standort-Jahren ≥2013; Hürden sind Lizenz (AHDB), fehlender Bulk-Download (NFTS) und Aggregation (Luke PxWeb).

### Gaps
- Inhalt der ICOS-Ancillary-Dateien (Variable für Kornertrag) nicht geöffnet.
- Recherche-Data-Gouv-Landing-Pages (Lizenzen von 10.57745/fw78re, 4byxtk, 0q0hnz) nicht einsehbar (Bot-Schutz).
- GLTEN-Experimentliste (346) nicht nach Ländern durchgesehen (Zertifikat/JS).
- AHDB-Excel-Dateien (Standortangaben) und AGB nicht geöffnet.
- NFTS-Kartenansicht/Koordinaten und Nutzungsbedingungen nicht verifiziert.

---

## Key Question 1: UK & Irland (Rothamsted e-RA, North Wyke, GLTEN, AHDB, CEH/EIDC, Hutton, Teagasc, Yield-Map-Datensätze)

### Takeaway
Rothamsted e-RA bietet CC-BY-4.0-Plot-Erträge bis 2022/2024 für Broadbalk (Weizen, Hafer, Silomais, Bohnen), Exhaustion Land, Woburn Ley-arable und Park Grass; Download nach kurzem Formular. Der einzige große Combine-Yield-Map-Datensatz (UKCEH ASSIST → CYCleSS, 934 Felder 2015–2017) ist offen (CC0), aber auf 10-km-Raster anonymisiert. GLTEN ist reines Metadatenportal; AHDB-RL-Ergebnisse sind urheberrechtlich geschützt; Teagasc hat keine offenen Ackerertragsdaten.

### Cited Findings
- e-RA unterscheidet Summary OADs, Complete OADs ("full plot-level data … in Frictionless format, including treatments, agronomic information and yields") und e-RAdata (Passwort) — [e-RA](https://www.era.rothamsted.ac.uk/)
- Liste der Datensätze mit Jahren ≥2013: Broadbalk Weizen 1968–2022, Hafer 1996–2022, Silomais 1997–2017, Ackerbohne 1968–2022, Exhaustion Land P test 1986–2023, Woburn Ley-arable Weizen 1976–2018, Park Grass 1965–2024, Hoosfield Mittel 1852–2015 — [e-RA Datasets](https://www.era.rothamsted.ac.uk/info/datasets)
- Lizenz: "available under a Creative Commons Attribution 4.0 Licence (CC BY 4.0)" mit Pflicht-Attribution "Contains data supplied by Rothamsted Research" und Acknowledgement UKRI-BBSRC — [e-RA Conditions](https://www.era.rothamsted.ac.uk/info/conditions)
- Broadbalk-Datensatz: Erträge bei 85 % TM, Dünger, Saat-/Erntedaten, Sorten; Download erst nach End-User-Agreement-Formular — [10.23637/rbk1-yld6822-01](https://www.era.rothamsted.ac.uk/dataset/rbk1/01-YLD6822)
- North Wyke: drei Farmlets à ~21 ha mit 15 Catchments, 15-min-Daten Wasser/Luft/Boden, Registrierung zur Nutzung; keine Ackererträge genannt — [NWFP Portal](https://nwfp.rothamsted.ac.uk/)
- GLTEN: "Search matched 346 of 346 experiments", Kontakt glten@rothamsted.ac.uk; Hilfe-API-Seite leer — [glten.org via curl -k](https://glten.org/), [GLTEN Help API](https://gltenhelp.readthedocs.io/en/latest/api.html)
- CYCleSS: 934 Felder/1-km²-Flächen England, 2015–2017, Winterweizen/Raps/Sommer-/Wintergerste/Bohnen, Combine-Yield-Monitor-Daten der UKCEH (ASSIST Precision Yield Dataset) unter NDA, Lage auf 10-km-BNG-Quadrate reduziert, figshare 10.6084/m9.figshare.27225807, Code github.com/alan-turing-institute/CYCLeSS-dataset-code — [Europe PMC Volltext PMC13035921](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13035921/fullTextXML); figshare-Record CC0, ZIP 5,6 MB — [figshare API](https://api.figshare.com/v2/articles/27225807)
- EIDC-Suche "crop yield": Hillesden 2006–2011 (OGL, Combine-Yield-Meter, Weizen/Raps/Bohnen), Wintergerste Abergwyngregyn 2020–2021, Wheat yield resilience 10-km 2008–2017 (Defra-Erhebung) — [EIDC Suche](https://catalogue.ceh.ac.uk/eidc/documents?term=crop+yield), [Hillesden](https://catalogue.ceh.ac.uk/documents/e54069b6-71a9-4b36-837f-a5e3ee65b4de)
- ASSIST-Datensammlung enthält nur das 10-km-Weizenresilienz-Produkt als Ertragsdatensatz — [EIDC ASSIST collection](https://catalogue.ceh.ac.uk/documents/d15f6fc4-10a3-411d-a8c9-6bddd5c492ba)
- AHDB Harvest Results: Winter-/Sommerweizen, -gerste, -hafer, Winterraps + Beschreibende Listen; "Yield tables contain yield results from all harvested trials (fungicide treated and untreated)", Excel-Format; © AHDB All Rights Reserved — [AHDB harvestresults](https://ahdb.org.uk/harvestresults), [About the service](https://ahdb.org.uk/knowledge-library/about-the-rl-harvest-results-service)
- Hutton CSC: Kontakt Cathy Hawes, cathy.hawes@hutton.ac.uk (Balruddery, Invergowrie) — [Bio4Ag contact](https://bio4ag.hutton.ac.uk/contact.html)
- Teagasc data.gov.ie: nur Grünland-Datensätze (AYAF Athenry 2018–2022, CC-BY-NC); Oak Park Rotationsversuche seit 2014 nur in Presse — [data.gov.ie](https://data.gov.ie/dataset?q=teagasc+yield), [Agriland](https://www.agriland.ie/?p=570080)
- DIVINE Pilot 2 Gerste UCD Lyons Farm 2023–2025, CC BY 4.0 — [Zenodo 19219514](https://zenodo.org/records/19219514)

### Inferences
- UK-Yield-Maps mit Feldlage sind praktisch nur über UKCEH-Kooperation (NDA) erreichbar; für ein Schülerprojekt unrealistisch.
- Rothamsted ist der sicherste UK-Einstieg (Lizenz klar, Daten sofort), aber nur 1–5 Standorte.

### Gaps
- Harper Adams, Leeds University Farm, Agri-EPI, SRUC: nicht recherchiert (Zeit).
- Teagasc-Open-Data-Seite (404) – aktuelle URL unbekannt.

---

## Key Question 2: Frankreich (INRAE Data Portal, SOERE PRO/ACBB, La Cage, CA-SYS, ICOS FR-Gri/FR-Lam/FR-EM2, ARVALIS)

### Takeaway
Recherche Data Gouv enthält mehrere Etalab-2.0-Datensätze mit gemessenen Parzellenerträgen ≥2013 (Grignon 12-Jahres-Systemversuch 2009–2020 mit Koordinaten, EFELE 2012–2020, PROspective Colmar 2000–2019, Rés0Pest 2013–2023, Pea_dataset 158 Standorte 2002–2024); das Portal blockiert aber automatisierte Zugriffe. ICOS-Archive für FR-Gri (2021–2025), FR-Lam (2020–2024), FR-EM2 (2017–2025), FR-Aur (2019–2025) sind frei (CC BY 4.0). SOERE ACBB und ARVALIS haben keine offenen Ertragsdaten.

### Cited Findings
- Grignon-Versuch: 48.84 N/1.95 E, 2009–2020, 4 Systeme (PHEP, No-Pest, L-EN, L-GHG), 12 Parzellen auf 6,2 ha, Combine-Ernte 75–140 m², Ertrag in q/ha bei 0 % TM, Repository DOI 10.57745/5TJJZA, Etalab 2.0, Kontakt caroline.colnenne-david@inrae.fr — [Data in Brief PMC11043882](https://pmc.ncbi.nlm.nih.gov/articles/PMC11043882/)
- EFELE: Silomais/Weizen/Senf 2012–2020, Erträge + C,N,P,K,Mg-Exporte, Etalab 2.0, TSV, Kontakt Thierry Morvan — [B2FIND](https://b2find.eudat.eu/dataset/e92ef2db-f563-5288-903a-c513734b3224)
- PROspective: Colmar 48°03′33″ N 7°19′42″ E, 2 ha, 24 Parzellen 10×9 m, Rotation Mais/Winterweizen/Zuckerrübe/Gerste 2000–2019, Kontakte Michaud/Levavasseur/Houot — [DataCite 10.57745/4byxtk](https://api.datacite.org/dois?query=doi:(10.57745/fw78re%20OR%2010.57745/4byxtk%20OR%2010.15454/jtve46%20OR%2010.57745/qwc7kv%20OR%2010.57745/0twhma%20OR%2010.15454/bjqllk%20OR%2010.15454/en10-2v70%20OR%2010.15454/f4gk-gx62%20OR%2010.57745/g6os9z%20OR%2010.57745/hpemyw)&fields[dois]=doi,titles,publicationYear,descriptions,rightsList,contributors,geoLocations&page[size]=20)
- Pea_dataset: 158 Standorte, 2002–2024, 4.450 Standort×Genotyp×Jahr, Ertrag + Protein, Kontakt A. Diallo — gleiche DataCite-Quelle
- Rés0Pest Synthèses annuelles 2013–2023, Kontakt Vincent Cellier, keine Lizenz eingetragen — [DataCite 10.57745/0q0hnz](https://api.datacite.org/dois/10.57745/0q0hnz)
- LANDMARK-Datamart QualiAgro/PROspective mit Erträgen 2010–2018 — [DataCite 10.15454/jtve46] (s. o.)
- ALLIANCE 79 Versuche 2009–2016 Raps/Weizen, CC BY 4.0 — DataCite 10.15454/bjqllk (s. o.)
- Übersicht aller INRAE-Treffer (Präfixe 10.57745/10.15454) mit Ertragsbezug — [DataCite-Suche 1](https://api.datacite.org/dois?query=(titles.title:rendement%20OR%20titles.title:yield%20OR%20descriptions.description:%22crop%20yield%22%20OR%20descriptions.description:rendement)%20AND%20(prefix:10.57745%20OR%20prefix:10.15454)&page[size]=60&fields[dois]=doi,titles,publicationYear,descriptions), [DataCite-Suche 2 (long-term)](https://api.datacite.org/dois?query=(descriptions.description:%22long-term%20experiment%22%20OR%20descriptions.description:%22longue%20dur%C3%A9e%22%20OR%20descriptions.description:%22long-term%20field%22%20OR%20descriptions.description:%22cropping%20systems%22)%20AND%20(prefix:10.57745%20OR%20prefix:10.15454)%20AND%20types.resourceTypeGeneral:Dataset&page[size]=60&fields[dois]=doi,titles,publicationYear,descriptions)
- Recherche Data Gouv liefert "Access Denied" (Anubis) für API und Citation-Seiten — [Entrepot API](https://entrepot.recherche.data.gouv.fr/api/search?q=rendement+AND+%28essai+OR+parcelle%29&type=dataset&per_page=30&sort=date&order=desc)
- SOERE ACBB: Standorte Lusignan (Grünland/Acker), Estrées-Mons (Acker seit 2009/2010), Theix; Datenzugriff über Abfragetool mit Authentifizierung — [ACBB-Tutorial](https://vsoil.inrae.fr/repo/external/user_doc/tuto-SOERE-ACBB.pdf), [INRA 2013 Präsentation](https://appgeodb.nancy.inra.fr/donnees/sioea/reunions/2013-03-25_AG/5_Pole_Observatoire.pdf)
- FR-Gri: Cropland, ~19 ha Feld bei 48.84 N 1.95 E — [FLUXNET FR-Gri](https://fluxnet.org/sites/siteinfo/FR-Gri)
- ICOS-Archive: FR-Gri 15 Objekte 2021–2025, FR-Lam 11 Objekte 2020–2024, FR-EM2 8 Objekte 2017–2025, FR-Aur 8 Objekte 2019–2025 — SPARQL meta.icos-cp.eu (eigene Abfrage, s. Katalog 29)

### Inferences
- La Cage (Versailles) und CA-SYS (Dijon) tauchen nur indirekt auf (CA-SYS: 16S-Daten 10.57745/lo2kif und Indikatoren 10.57745/znrmzx 2020–2023 ohne explizite Erträge); eigene Ertragsdatensätze wurden nicht gefunden.
- Der Grignon-Systemversuch liegt ~150 m von der Wetterstation und nahe FR-Gri; Kombination mit ICOS-Daten denkbar.

### Gaps
- La Cage, CA-SYS, Auzeville, Lusignan: keine offenen Ertragsdatensätze identifiziert.
- data.gouv.fr "rendement parcelle" nicht separat durchsucht; API-AGRO nicht geprüft.

---

## Key Question 3: Belgien / Niederlande / Luxemburg

### Takeaway
Belgien: BE-Lon (11,8 ha, Rotation Zuckerrübe/Weizen/Kartoffel/Weizen) hat ein frei ladbares ICOS-L2-Archiv 2017–2025; ILVO publiziert eine Flandern-Ertragsdatenbank (CC BY-NC-SA, Lagegenauigkeit unklar) und einen gesperrten Agroforst-Ertragsdatensatz. Niederlande: BASIS Lelystad 2009–2022 (CC BY 4.0) und Kartoffel-Versuche Lelystad/Vredepeel 2019–2020 (CC BY-NC-SA); NPPL/Farm of the Future ohne offene Ertragskarten. Luxemburg: nichts gefunden.

### Cited Findings
- BE-Lon: 50.55162 N, 4.746234 E, 11,8 ha, 4-jährige Rotation Zuckerrübe/Winterweizen/Kartoffel/Winterweizen, PI Benjamin Dumont — [ICOS Station BE-Lon](https://meta.icos-cp.eu/resources/stations/ES_BE-Lon)
- ETC L2 ARCHIVE BE-Lon 2017–2025: "most complete data collection … continuous fluxes, meteorological data, ancillary data", ICOS CC BY 4.0, 114 MB, Download-Button — [ICOS object](https://meta.icos-cp.eu/objects/99gAK7xqcSkk7SRKDwZz1KJT)
- Lonzée-Rotation 2004–2016 über drei Zyklen beobachtet (Flussstudie, Buysse et al.) — [ORBi](https://orbi.uliege.be/handle/2268/203085)
- Flandern-Ertragsdatenbank: Mais, Winterweizen, Zuckerrübe, Kartoffel, Gras in t/ha; Pflanz-/Erntedaten; CC BY-NC-SA 2.0; Kontakt Sarah Garré — [Zenodo 8017476](https://zenodo.org/records/8017476)
- LTM_AC_crop: 6 Alley-cropping-Felder, Mais/Weizen/Gerste/Kartoffel ab 2015, Restricted — [Zenodo 10692761](https://zenodo.org/records/10692761)
- BASIS: 5 Felder (3 bio/2 konv.), 4 Bodenbearbeitungssysteme, 2009–2022, CC BY 4.0, Data_yield_BASIS.xlsx — [4TU](https://data.4tu.nl/datasets/5708634c-05b4-40e2-9d3e-9c12fcad7882)
- Kartoffel Lelystad/Vredepeel 2019–2020, CC BY-NC-SA 4.0, Kontakt Sander.Janssen@wur.nl — [Harvard Dataverse API](https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/1LC6W7)
- WUR-Precision-Seite: NPPL und Boerderij van de Toekomst mit "yield per m² determination", keine Datenveröffentlichung — [WUR](https://www.wur.nl/nl/onderzoek/plant/precisielandbouw)
- 4TU-Suche "crop yield" rendert nicht ohne JS; LGN2018 ist Landnutzung, nicht Ertrag — [4TU LGN2018](https://data.4tu.nl/datasets/8738f896-f49e-4ae7-8671-50ef893a2cee)
- CRA-W: Dauerversuche SYCBio/SYCMa/SPOT; Getreide-Ergebnisse nur im jährlichen "Livre Blanc Céréales" — [CRA-W PDF](https://www.cra.wallonie.be/uploads/2023/11/asbio2023-presacraw.pdf)

### Inferences
- BE-Lon ist der beste einzelne Kandidat der Region: großes Feld, Koordinaten, offene Lizenz, 9 Jahre ≥2017.

### Gaps
- Hooibeekhoeve, Proefhoeve Bottelare, KU Leuven: nicht recherchiert.
- Luxemburg (LIST, ASTA, IBLA): keine Suche ergab Treffer.

---

## Key Question 4: Dänemark (Landsforsøgene/NFTS, AU-Dauerversuche, DK-Vou)

### Takeaway
Landsforsøgene-Einzelversuche sind über den NFTS-WebTrial-Viewer (DK/NO/SE, Erntejahre 2018+) öffentlich einsehbar, aber ohne erkennbaren Bulk-Download und ohne genannte Lizenz; AU-Dauerversuche (Askov u. a.) haben keine Download-Datensätze außer BioBase Foulum 2013–2021 (CC BY 4.0). Die ICOS-Ackerstation heißt DK-Vng (Voulundgaard) mit L2-Archiv 2020–2023.

### Cited Findings
- NFTS-Startseite verlinkt Forsøgsplaner, Forsøgsplacering (Kartenlage), Enkeltforsøg (Einzelversuche), Tabelbilag (ab 2018 / bis 2017), WebTrial-Viewer; nur in IE getestet — [nfts.dlbr.dk](https://nfts.dlbr.dk/)
- WebTrial-Viewer: Filter Erntejahr 2018–2027, Länder DK/NO/SE, Fachbereiche Getreide/Leguminosen, Öko, Futter, Kartoffel/Gemüse, Saaten, Düngung, Bodenbearbeitung, Pflanzenschutz; Kulturen u. a. Winter-/Sommerweizen, Gerste, Roggen, Triticale, Hafer, Erbse, Ackerbohne, Lupine, Soja — [WebTrial](https://webtrial.dlbr.dk/TrialView?country=DK)
- Ertrag in Landsforsøgene als hkg Korn/ha mit Konfidenzintervall und Relativertrag — [SEGES Berechnungsformeln](https://www.landbrugsinfo.dk/-/media/landbrugsinfo/public/d/6/f/planter_kval_landsfors_bere_formler_til_beregning_af_landsforsog.pdf)
- AU-Dauerversuche: 11 Experimente (Askov Mist/Mineraldünger, CENTS, Organic dairy rotation, P-Depletion, Biochar, Arable crop rotation, Jyndevad …), keine Datenangaben; Kontakt jeo@agro.au.dk — [AU Agro LTE](https://agro.au.dk/en/about-the-department/long-term-experiments)
- Askov 1894–2019 Report DCA 151 und Ertragsreihen 1932–2019 nur in Publikationen — [DCA 151](https://dcapub.au.dk/djfpublikation/djfpdf/DCArapport151.pdf), [JPNSS 2022](https://pure.au.dk/ws/files/333391057/Journal_of_Plant_Nutrition_and_Soil_Science_2022_Christensen.pdf)
- BioBase Foulum 2013–2021: 14 Systeme, TM- und Proteinertrag je Parzelle, CC BY 4.0 — [figshare API](https://api.figshare.com/v2/articles/25593516)
- DK-Vng Voulundgaard: 6 ETC-L2-Archive 2020–2023 (Cropland) — SPARQL meta.icos-cp.eu (eigene Abfrage)
- Zenodo-Treffer "Denmark field-performance predictions 2017–2024" (10.5281/zenodo.23010548) sind **Modelloutput** → ausgeschlossen — DataCite-Suche (s. Katalog)

### Inferences
- Landsforsøgene wären mit Koordinaten die ergiebigste dänische Quelle (hunderte Versuche/Jahr); Nutzung erfordert Anfrage bei SEGES Innovation (Lizenz) und Scraping oder Datenexport.

### Gaps
- ForsogPlacering.aspx und tabelbilag.aspx liefern 404 über WebFetch; Koordinatengenauigkeit unbekannt.
- Keine dänischen Yield-Map-Datensätze gefunden.

---

## Key Question 5: Schweden / Norwegen / Finnland (SLU, Fältforsk, NIBIO, Luke, SITES)

### Takeaway
Schweden hat mit R3-9001 (9 Standorte, 1962–2022, CC0) den besten offenen Dauerversuchs-Datensatz der Region; Finnland publiziert Sortenversuche nur aggregiert (PxWeb, 12 Standorte, 2018–2025); die nordische DataverseNO-Sammlung (CC BY 4.0) liefert Gerste/Kartoffel/Rotklee-Versuche aller fünf Länder 1970–2024 mit Standortangabe. Für NIBIO wurde kein offener Ertragsdatensatz gefunden.

### Cited Findings
- R3-9001: 9 aktive Standorte in Östergötland, Skåne, Västra Götaland, Uppland; Erträge jährlich 1962–2022; CC0; R39001_data.tsv 21,6 MB + locations.tsv; Kontakt soilnutrientcycling@slu.se — [researchdata.se 2024-462](https://researchdata.se/en/catalogue/dataset/2024-462)
- Frame trial R3-RAM56 Ultuna 1956–2023 (DOI 10.5878/7f5n-vp94) — [researchdata.se 2024-468](https://researchdata.se/en/catalogue/dataset/2024-468/1) (nur Suchtreffer)
- Smith & Bommarco: 32 LTEs, **standardisierte** Erträge, 1958–2020 — [B2FIND](https://b2find.eudat.eu/dataset/326af1ea-2a25-535e-9f4b-813d2c12be45)
- Lund organische Getreide 2020: 81 Felder, Region, Ertrag landwirtsberichtet, CC0 — [researchdata.se 2025-366](https://researchdata.se/catalogue/dataset/2025-366)
- SLU Fältforsk: Koordination nationaler Feldversuche, "bearbetning av resultat och datalagring"; Kontakte NFTS nfts.ffe@slu.se, LTE-Koordinatorin johanna.wetterlind@slu.se — [SLU Fältforsk](https://www.slu.se/faltforsk)
- Nordische Sortenversuchs-DB: DK/NO/SE/IS/FI, Sommergerste/Rotklee/Kartoffel, 1970–2024, "location of each trial is reported", CC BY 4.0, 01_BarleyData.csv 16,5 MB, Kontakt Silius M. Vandeskog — [DataverseNO](https://dataverse.no/citation?persistentId=doi:10.18710/IZ3EFE), [Luke Jukuri](https://jukuri.luke.fi/items/952101b8-68c0-440c-9194-3e505c6d2bd6/full)
- Luke PxWeb: Ordner "lajikekokeet" → Publikationsjahre 2016–2025 → "sato" → 13 Kulturen; Gerste-Tabellen: Gesamt, nach Zone, Bodenart, Jahr (2018–2025), **Versuchsstandort (12 Orte)**, Ertragsniveau; Merkmale Sato kg/ha, Wuchszeit, Lager, TKG, HL, Protein; Größen Kokeita/Estimaatti/Erotus/Suhdeluku/P-arvo — [PxWeb API](https://px.luke.fi/PxWeb/api/v1/fi/maatalous/lajikekokeet/julkaisuvuosi_2025/sato/ohra/), [PxWeb UI](https://px.luke.fi/PxWeb/pxweb/fi/maatalous/maatalous__lajikekokeet/)
- Luke-Prospekt: Versuche kundenfinanziert, vertraulich berichtet, Zusammenfassungen in PxWeb; Kontakt varietytesting@luke.fi — [Luke Prospekt](https://www.luke.fi/fi/documents/viralliset-lajikekokeet-esitepdf)
- Nordic Weizen-Fungizidversuche 2012–2016 (DK/FI/LT/NO/SE), Yield.xlsx, CC BY 4.0, ohne Versuchsorte — [figshare API 19203377](https://api.figshare.com/v2/articles/19203377)
- NIBIO Apelsvoll: Systemversuch seit 1989 (konv./integriert/öko), keine Datensätze gefunden — [orgprints 7056](https://orgprints.org/7056/), [NIBIO Apelsvoll](https://nibio.no/en/about-eng/addresses/apelsvoll)
- FI-Jok, FI-Qvd, SE-Lnn: keine ETC-L2-ARCHIVE-Objekte mit Ökosystemtyp Cropland in der ICOS-SPARQL-Abfrage (eigene Abfrage meta.icos-cp.eu/sparql)

### Inferences
- Luke-PxWeb liefert nur Standort- ODER Jahresmittel (kein Standort×Jahr), daher für Jahres-Labels nur über Rohdatenanfrage nutzbar.
- Die nordische DataverseNO-Sammlung enthält vermutlich einen Großteil der finnischen/schwedischen Gersten-Rohversuche – zu prüfen, ob Standort×Jahr enthalten (sehr wahrscheinlich, da Multi-Environment-Design).

### Gaps
- SITES (Swedish Infrastructure for Ecosystem Science, z. B. Lönnstorp SE-Lnn) nicht direkt geprüft.
- NIBIO DataverseNO nicht durchsucht; Møystad nicht gefunden.
- Luke Etsin/Open-Data-Portal (JS) nicht auswertbar.

---

## Key Question 6: ICOS Carbon Portal – welche Ackerstationen im Scope publizieren Ancillary-/Ertragsdaten?

### Takeaway
Per SPARQL auf meta.icos-cp.eu haben folgende als "cropland" klassifizierte Stationen im Scope ETC-L2-ARCHIVE-Produkte (die laut Objektbeschreibung Flüsse, Meteo **und Ancillary-Daten** enthalten): BE-Lon (2017–2025), FR-Gri (2021–2025), FR-Lam (2020–2024), FR-EM2 (2017–2025), FR-Aur (2019–2025), DK-Vng (2020–2023). FI-Jok, FI-Qvd, SE-Lnn und "DK-Vou" tauchen nicht auf. Ob die Ancillary-Dateien den Kornertrag enthalten, ist nicht geöffnet worden; ICOS schreibt eine Instruktion "Ancillary Vegetation Measurements in Cropland" vor.

### Cited Findings
- SPARQL (Spec etcArchiveProduct, Ökosystemtyp regex "crop"): BE-Lon 25 Objekte 2017–2026; DK-Vng 6 (2020–2023); FR-Aur 8 (2019–2026); FR-EM2 8 (2017–2026); FR-Gri 15 (2021–2026); FR-Lam 11 (2020–2024); dazu DE-Brs, DE-Geb, DE-Kli, DE-RuS, IT-BCi — eigene Abfrage https://meta.icos-cp.eu/sparql (Ergebnis im Arbeitsprotokoll)
- BE-Lon-Objektspezifikationen umfassen u. a. "ETC L2 ARCHIVE", "ETC L2 AuxData", "Daily phenocam image set", "ICOS ETC Ancillary Raw BIF" (Spec existiert) — eigene SPARQL-Abfrage
- Archiv-Beschreibung: "continuous fluxes, meteorological data, ancillary data, and the associated metadata", ICOS CC BY 4.0 — [ICOS object](https://meta.icos-cp.eu/objects/99gAK7xqcSkk7SRKDwZz1KJT)
- ICOS-ETC-Instruktionen: "Ancillary Vegetation Measurements in Cropland (20240325)", "Plant Species Reporting", "The ICOS BADM use" — [ICOS ETC instructions](https://www.icos-etc.eu/icos/documents/instructions)
- Data-Portal-Filterseite ist JS-basiert und per WebFetch nicht auswertbar — [ICOS Data Portal](https://data.icos-cp.eu/portal/)

### Inferences
- Für ICOS-Felder ist die Feldgeometrie über Stationsmetadaten (Koordinate + Feldgröße) ableitbar; Ertrag wäre je Feld und Jahr eine Zahl (Site-Jahr), zusammen ~35 Site-Jahre im Scope.

### Gaps
- Ancillary-Dateien (z. B. `*_ANCILLARY_*.csv` im ZIP) nicht entpackt; Variable für Kornertrag (BADM "GRP"/AG_BIOMASS_CROP) nicht bestätigt.

---

## Key Question 7: EU-Projekte und Repositorien (LANDMARK, SoilCare, DIVERSify, Diverfarming, Zenodo/Dryad/figshare/PANGAEA)

### Takeaway
Gefunden wurden eine (noch bis 31.10.2027 embargierte) EJP-SOIL-Datenbank zu Öko-Erträgen (50 Versuche, 15 Länder), ein Intercrop-Datensatz (37 Versuche 2001–2017, CC BY 4.0, ohne Koordinaten) sowie das LANDMARK-Datamart (QualiAgro/PROspective). Zenodo-Suchen nach "yield map" + Combine lieferten für die Zielregion keine Treffer; DataCite-Suchen nach Ertragsdatensätzen 2015+ in den Zielländern ergaben überwiegend Parzellen- oder Betriebsumfragedaten ohne Koordinaten.

### Cited Findings
- EJP SOIL ARTEMIS Öko-Ertragsdatenbank: 50 Experimente, 45 Standorte, 15 Länder (SE 7, DK 4, FI/NO/UK je 2, NL/FR je 1), Winterweizen/Roggen/Sommergerste/Sommerweizen/Hafer, CC BY 4.0, **Embargo bis 2027-10-31** — [Zenodo 14258149](https://zenodo.org/records/14258149)
- Intercrop-Datensatz: 37 Experimente (FR, DK, IT, DE, England) 2001–2017, 607 Einheiten, CC BY 4.0 — [Zenodo 14160885](https://zenodo.org/records/14160885)
- Zenodo-API "yield map" AND combine/harvester AND Kultur: einziger Treffer Indien 2017 — [Zenodo API](https://zenodo.org/api/records?q=%22yield%20map%22%20AND%20%28combine%20OR%20harvester%29%20AND%20%28wheat%20OR%20maize%20OR%20barley%20OR%20rapeseed%29&size=25&sort=mostrecent)
- Zenodo-API "Lonzée": nur HYPERNETS-Reflektanzdaten 2023–2025 (CC BY 4.0), keine Erträge — [Zenodo API](https://zenodo.org/api/records?q=Lonz%C3%A9e%20AND%20%28yield%20OR%20crop%29&size=15)
- DataCite-Suche (Titel "yield", Zielländer, Dataset, >2014): relevante Treffer u. a. ILVO Flandern, LTM_AC_crop, BioBase Foulum, Lund organische Getreide, DIVINE Irland, Nordic Weizen-Fungizid, Dryad Schweden, Red clover ploidy ILVO (Futter) — [DataCite-Suche](https://api.datacite.org/dois?query=(titles.title:%22yield%22%20AND%20(descriptions.description:Belgium%20OR%20descriptions.description:Netherlands%20OR%20descriptions.description:Denmark%20OR%20descriptions.description:Sweden%20OR%20descriptions.description:Norway%20OR%20descriptions.description:Finland%20OR%20descriptions.description:Ireland%20OR%20descriptions.description:%22United%20Kingdom%22%20OR%20descriptions.description:England%20OR%20descriptions.description:Scotland%20OR%20descriptions.description:Flanders%20OR%20descriptions.description:Wallonia))%20AND%20types.resourceTypeGeneral:Dataset%20AND%20publicationYear:%3E2014&page[size]=80&fields[dois]=doi,titles,publicationYear,descriptions,publisher)
- BonaRes-Metadaten zu 186 europäischen LTEs (ohne DE), Länder u. a. BE, DK, FI, FR, GB, NO, SE; DOI 10.20387/bonares-eff3-0mb4 — [PMC8408514](https://pmc.ncbi.nlm.nih.gov/articles/PMC8408514/)

### Inferences
- Im Zielraum existiert offenbar kein offener, georeferenzierter Combine-Yield-Map-Datensatz auf Zenodo/Dryad/figshare/4TU/DANS; Feldebene mit Polygon ist nur über ICOS, Rothamsted/North Wyke (Catchments) oder NDA-Daten (UKCEH) erreichbar.

### Gaps
- SoilCare, DIVERSify, Diverfarming, NIVA: nicht gezielt gesucht.
- PANGAEA, Mendeley Data: nicht durchsucht.
- Scientific Data/ESSD-Volltextsuche nur punktuell (CYCleSS, Nordic trials gefunden).
