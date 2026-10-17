# Verifikation offener Feld-Ertragsdatensätze durch Download und Dateiinspektion

Stand: 2026-10-16. Alle Downloads liegen unter `C:\Users\mario\AppData\Local\Temp\claude\C--Users-mario\9c685241-e5c3-414f-abf8-47a6359fb8bc\scratchpad\verify\<name>\` (Auswertungsskripte unter `...\scratchpad\scripts\`, mit `python -I -X utf8` ausgeführt). Gesamtes Downloadvolumen ca. 430 MB (davon ICOS-Archive ~215 MB). Alles, was unten ohne "unbestätigt" steht, wurde direkt in den heruntergeladenen Dateien gesehen; Zahlen stammen aus eigenen Zählungen über die Dateien.

Hinweis zur Methodik: Zenodo/figshare/Dataverse/DataCite/CKAN-APIs wurden für Metadaten und Direktlinks genutzt; Dateien per `curl`; Archive nur gelistet/entpackt, niemals ausgeführt (das INVITE-Zip enthält eine SiriusQuality-GUI mit .exe/.dll – wurde beim Entpacken ausgeschlossen).

---

## 1. INVITE – Wheat Registration (VCU) Trials CZ/HU/FR/CH 2003–2018 in ICASA-Format (Zenodo 20786880)

### Takeaway
Bestätigt und sehr gut: 1 775 Versuchs-IDs (Trial = Standort × Jahr) mit Sorten-Mittelwerten (Trockenmasse-Kornertrag, kg DM/ha, 0 % Feuchte), Aussaat-/Erntedaten, Düngung, Boden, Wetter. 605 Trials ≥2013 (247 ≥2017). CZ/HU/CH haben Koordinaten mit 6–7 signifikanten Dezimalen (Feldgenauigkeit), Frankreich nur 1 Dezimale (~±5 km) plus PLZ/Ortsname. Nur Weizen.

### Cited Findings
- Zenodo-API: Dateien `ReadMe.txt` (5,7 kB) und `Dataset.zip` (49,9 MB), Lizenz `cc-by-4.0`, access_right `open` — [Zenodo API](https://zenodo.org/api/records/20786880)
- ReadMe: "Grain yield values were standardized to 0% moisture content"; Struktur: `ICASA Excel format/` (5 xlsx: UKZUZ_Czech_Republic, NEBIH_Hungary, GEVES_North_France, GEVES_South_France, AGRO_Switzerland), `csv/` (je Land 23–24 Tab-getrennte CSVs), `WeatherData/` (173 .wht-Dateien), `SiriusQyality/` (ausführbare Modell-GUI) — [ReadMe.txt](https://zenodo.org/api/records/20786880/files/ReadMe.txt/content)
- Zählung aus `6_INVITE_Experiment_description.csv` (HAYR = Erntejahr) und `*_Fields.csv`:
  - Tschechien (UKZUZ): 223 Trials 2003–2018 (13–14/Jahr), 14 Standorte, 84 Trials ≥2013, 28 ≥2017; Koordinaten 15 Dezimalstellen gespeichert (~7 signifikante), alle 223 Feldzeilen mit Koordinaten; Replikate 2 (150) oder 3 (73); 200 Trials mit ≥1 Ertragswert; Ertragsspalte GWAM kg[DM]/ha, 7 112 von 8 267 Sorten×Trial-Zeilen gefüllt; GWPCM (Kornfeuchte bei Reife, %) gefüllt (z. B. 12,5/13,3 %) – das ist die gemessene Feuchte, der Ertrag selbst ist auf 0 % bezogen.
  - Ungarn (NEBIH): 118 Trials, 12 Standorte, 46 ≥2013, 14 ≥2017; 4 Replikate; alle 118 mit Ertrag (3 476 Sorten×Trial-Zeilen).
  - Nordfrankreich (GEVES): 916 Trials 2000–2020 (!), 91 Standortcodes, 67 unterschiedliche Koordinatenpaare; 275 Trials ≥2013, 120 ≥2017; 163 Standort-Jahre ≥2013; Koordinaten nur 1 Dezimale (z. B. 49.2 / 4.2), aber Ortsname und PLZ (FL_LOC_3, FL_LOC_ZIP) vorhanden; PLTA (Plot-Fläche) in 211 von 916 Zeilen gefüllt (z. B. 10,8; 15; 8,625; 11,2 m²); 2 Replikate; 12 608 Sorten×Trial-Zeilen, alle mit GWAM.
  - Südfrankreich (GEVES): 386 Trials 2000–2020, 37 Standortcodes/34 Koordinaten (1 Dezimale), 148 ≥2013, 68 ≥2017, 83 Standort-Jahre ≥2013; PLTA in 117 Zeilen (8,5–23,1 m²).
  - Schweiz (Agroscope): 132 Trials, 12 Standorte, 52 ≥2013, 17 ≥2017; 3 Replikate; 131 mit Ertrag (3 335 Zeilen).
  - Summe: 1 775 Trials, 605 ≥2013, 247 ≥2017. Standort-Jahre ≥2013 (CZ 84 + HU 46 + NF 163 + SF 83 + CH 52) = 428.
- Standortlisten mit Koordinaten (aus `*_Fields.csv`, erste Zeile je Standort):
  - CZ: CAS Čáslav 49.9022/15.4147; CHR Chrlice 49.1247/16.6342; CHT Chrastava 50.8175/14.9586; HRA Hradec n. Svitavou 49.7322/16.4872; JAR Jaroměřice 49.1002/15.8769; LED Lednice 48.8083/16.7722; LIP Lípa 49.5559/15.5362; OBL Oblekovice 48.8177/16.0981; PJA Pusté Jakartice 49.9672/17.9483; STV Staňkov 49.5522/13.0689; UHO Uherský Ostroh 48.9904/17.4190; VER Věrovany 49.4735/17.2747; VYS Vysoká 49.6342/13.9525; ZAT Žatec 50.3034/13.5205.
  - HU: Aba Abaújszántó 48.2874/21.1975; Deb Debrecen 47.5764/21.5859; Esz Eszterágpuszta 45.9322/18.2340; Gyu Gyulatanya 48.0407/21.6094; Ire Iregszemcse 46.6891/18.1993; Jas Jászboldogháza 47.3628/19.9809; Kap Kaposvár 46.3790/17.8291; Kom Kompolt 47.7408/20.2356; Sza Szarvas 46.8687/20.5247; Sze Székkutas 46.5192/20.5211; Szo Szombathely 47.1941/16.6480; Tor Tordas 47.3273/18.7510.
  - CH: Asse Assens 46.6133/6.6227; Chan Changins 46.3805/6.2299; Dell Delley 46.9134/6.9677; Elli Ellighausen 47.6135/9.1356; Gran Grangeneuve 46.7701/7.1153; Lind Lindau 47.4428/8.6763; Moud Moudon 46.6503/6.7880; Oens Oensingen 47.2903/7.7159; Reck Reckenholz 47.4307/8.5118; Utze Utzenstorf 47.1533/7.5583; Vouv Vouvry 46.3382/6.8661; Zoll Zollikofen 46.9881/7.4633.
- Management: Planting_events (PDATE in 100 % der Trials, PLPOP Saatstärke, Replikate), Harvest_events (HADAT in 213/223 CZ, 107/118 HU, 844/916 NF, 364/386 SF, 130/132 CH), Fertilizer_events (CZ 802, HU 260, NF 2 793, SF 1 197, CH 396 Zeilen), Irrigation, Residue, Initial conditions, Soil profile layers (teils PTF-geschätzt), tägliche Wetterdaten je Standort — gesehen in `csv/<Land>/15_…`, `16_…`, `18_…`
- Obs_crop_summary_means enthält außerdem PLDAE, EEMD (Ährenschieben), MDAT, HDATE, Lager, Pflanzenhöhe, Ähren/m², TKG (GWGM), Protein (GPRCM), Hektolitergewicht, Krankheitsscores; NF/SF zusätzlich GWAMval-Validitätsflag (BUL/NDF/OBT/EXP) — [Definitions CSV in Dataset.zip]
- Lizenzwiderspruch: Zenodo-Lizenz CC BY 4.0, aber in allen fünf `5_INVITE_Dataset_description.csv` steht SUITE_DISTRIB = "Confidential, do not distribute" (vermutlich Relikt aus Projektphase) — gesehen in Dateien
- Zeitstempel im Zip: Juni 2026 (Dateien erstellt 2026-06-16 bis 2026-06-21); Version 1.0.

### Inferences
- Für Transfer-Zwecke sind CZ/HU/CH (38 Standorte, Feldkoordinaten) direkt nutzbar; Frankreich (128 Standortcodes) nur mit ~5–10 km Lagegenauigkeit bzw. PLZ-Geokodierung.
- Da je Trial Sorten-Mittel (nicht Einzelparzellen) vorliegen, ist die sinnvolle Einheit "Trial-Mittel über Sorten" oder "Sorte×Trial".
- Ein Ausreißer GWAM = 8,6 kg/ha (CZ) zeigt, dass eine Plausibilitätsfilterung nötig ist.

### Gaps
- Plot-Flächen für CZ/HU/CH nicht angegeben (PLTA leer); nur FR teilweise.
- Validitätsflag GWAMval wurde nicht ausgewertet (Anteil NDF unbekannt).

**Datensatz-Record 1:** INVITE Wheat VCU Trials (ICASA) | https://zenodo.org/records/20786880 (verifiziert via API, Dateien geladen) | Winterweizen (Weichweizen, VCU) | CZ, HU, FR (Nord+Süd), CH | CZ/HU/CH: Feldkoordinaten mit ≥6 Dezimalen; FR: 1 Dezimale (~5–10 km) + PLZ/Ort | Parzellenversuch, Plot 8,5–23 m² (nur FR angegeben), 2–4 Wdh.; Werte = Trial-Mittel je Sorte | 2013–2018 (FR bis 2020) | 14 CZ + 12 HU + 12 CH + 91 NF + 37 SF Standortcodes = 166 (CZ/HU/CH 38 mit Feldgenauigkeit) | 428 Standort-Jahre ≥2013 (605 Trial-IDs); davon CZ/HU/CH 182 | Kornertrag GWAM kg DM/ha bei 0 % Feuchte (Mittel je Sorte; TKG, Protein, Kornfeuchte GWPCM zusätzlich) | Saat-/Erntedatum, Saatstärke, N-Düngung (Datum/Menge), Bewässerung, Bodenprofil, Tageswetter, Phänologie, Krankheiten, Lager | CC BY 4.0 (Zenodo); in Dateien "Confidential, do not distribute" – Klärung empfohlen | Anonym, direkt | Mittel: Tab-CSV mit 3 Kopfzeilen, Excel-Serialdaten, 5 Länder zusammenführen, Datums-/ID-Harmonisierung | 5 (für CZ/HU/CH), 3 (FR) | bestätigt

---

## 2. BRIWECS – Multi-environment winter wheat trials Germany 2015–2020 (figshare 27910269)

### Takeaway
Bestätigt: 6 Standorte mit Koordinaten (7–8 Dezimalen), 28 Standort-Jahre, 34 683 Parzellenzeilen (34 355 mit Kornertrag), Ertrag in dt/ha bei 100 % TM, Aussaatdatum als Tag des Jahres je Zeile, Management-xlsx je Standort-Jahr inkl. Plotgröße (z. B. 10,5 m², Erntefläche 6,125 m²).

### Cited Findings
- figshare-API: Titel "Multi-environment field trials for wheat yield, stability and breeding progress in Germany", Lizenz CC BY 4.0, eine Datei `Briwecs_data.zip` 11,3 MB; Beschreibung: 6 Jahre (2015–2020), 6 Standorte, 9 Management-Szenarien, 228 Sorten, 526 751 Datenpunkte, 24 Merkmale — [figshare API](https://api.figshare.com/v2/articles/27910269), [Download](https://ndownloader.figshare.com/files/50832927)
- `metadata/BRIWECS_location_coordinates.csv`: KIE 9.98041391/54.3156846; GGE 8.5013496/49.9408858; KAL 6.9942357/50.6131046; QLB 11.145669/51.769213; HAN 9.81810808/52.2438183; RHH 8.875599/50.760497 (Long, Lat) — gesehen in Zip
- `output/BRIWECS_data_publication.csv` (Semikolon, 6,9 MB): 34 683 Zeilen; Spalten BRISONr, Treatment, Block, Row, Column, Year, Location, Sowing_date, Emergence_date, BBCH59, BBCH87, Seedyield, Seedyield_bio, Biomass_bio, Harvest_Index_bio, TGW, Krankheiten, Falling_number, Crude_protein, Sedimentation, Grain, Biomass, Straw, Protein_yield; Jahre 2015: 9 460, 2016: 9 900, 2017: 8 979, 2018: 2 444, 2019: 3 016, 2020: 884 Zeilen; Standort-Jahre mit Seedyield: 28 (GGE 2015–19, HAN 2015–19, KAL 2015–20, KIE 2015–19, QLB 2015–17, RHH 2015–17+2019); Plots je Standort-Jahr 400–2 340; Seedyield Median 66,3 (0–141,6); Sowing_date in 34 679 Zeilen (DOY, z. B. 301, 293, 265); 228 Sorten; Treatments HN_WF_RF (11 278), LN_NF_RF (8 423), HN_NF_RF (8 424), LN_WF_RF (3 370), plus IR (bewässert)/RO-Varianten.
- `metadata/Unit.xlsx`: "Seedyield – dt/ha @100% dry mass – whole plot"; "Seedyield_bio – g/m^2 @100% dry mass – biomass 50 cm cut" — gesehen
- `data/management/Management_information_KIE_2017.xlsx`: Farm "Versuchsgut Hohenschulen (CAU Kiel)", plot length 3.5 m, plot width 3 m, plot size 10.5 m², harvest size 6.125 m², Sowing density 300 K/m², Sowing date "20.-22.09.2017" [sic; Jahr vermutlich Vorjahr], Harvest "08.08.–15.08.2017", Bodenart, Vorfrucht, N-Gaben mit Datum/Menge je Treatment, Pflanzenschutz — gesehen; 32 solcher Dateien (je Standort-Jahr)
- README.md: "Part of data the traits in Location KAL, Phase II (2018-2020) is still under data-preparation"; Wetter: DWD-interpoliert 2014–2024 je Standort — gesehen

### Inferences
- Alle 28 Standort-Jahre liegen ≥2015, also vollständig im Zeitraum ≥2013; ≥2017: 16 Standort-Jahre.
- Parzellen-Einzelwerte (nicht Mittel) → feinste Auflösung aller geprüften Datensätze, aber nur Weizen und nur 6 Orte.

### Gaps
- Plotgrößen anderer Standorte nicht einzeln geprüft (nur KIE 2017 gelesen).

**Datensatz-Record 2:** BRIWECS Winterweizen-MET Deutschland | https://doi.org/10.6084/m9.figshare.27910269 (verifiziert) | Winterweizen (228 Sorten) | Deutschland: KIE (Hohenschulen/Kiel), GGE (49.94/8.50), KAL (50.61/6.99), QLB (51.77/11.15), HAN (52.24/9.82), RHH (50.76/8.88) – Ortsnamen außer KIE nicht aus den Dateien verifiziert | Standortkoordinaten 7–8 Dezimalen (Versuchsgut, nicht Einzelfeld) | Parzelle ~10,5 m² (Erntefläche ~6 m²; KIE 2017), Einzelparzellenwerte | 2015–2020 | 6 Standorte | 28 Standort-Jahre (16 ≥2017) | Seedyield dt/ha bei 100 % TM (whole plot); Seedyield_bio g/m² TM | Saat-/Auflauf-DOY je Zeile, BBCH59/87, N-/Fungizid-/Bewässerungs-Treatments, Management-xlsx mit Düngedaten, Boden, DWD-Wetter, Qualitätsmerkmale, Krankheiten | CC BY 4.0 | Anonym, direkt | Gering–mittel (Semikolon-CSV fertig; Management aus 32 xlsx extrahieren) | 4 | bestätigt

---

## 3. ZALF Dedelow Monokultur-Dauerversuch (DOI 10.4228/zalf-fpdk-tp92, BonaRes)

### Takeaway
Nur Metadaten bestätigt; Datendateien nicht erreichbar (BonaRes-Portal ist eine JS-Kartenanwendung ohne per curl auffindbaren Download-Endpunkt; GeoNetwork-CSW 503). Inhalt der Dateien (Ertragseinheiten, Jahre je Frucht, Plotgrößen) bleibt unbestätigt.

### Cited Findings
- DataCite: Titel "Yield development of 4 winter cereals and grain maize under permanent cultivation/monoculture (1984/1999-2021) on a north-eastern German site"; Formate xlsx, CSV, File-Geodatabase (gdb); Lizenz CC BY 4.0; Bounding box 53.37275–53.373304 N, 13.799549–13.801327 E (ca. 60 × 120 m, d. h. Feldgenauigkeit); Beschreibung: Wintergerste seit 1984, Winterweizen, Roggen, Triticale und Körnermais seit 1999, "Over 12 years, the crops were cultivated with 3 nitrogen levels. The grain yields were determined." — [DataCite](https://api.datacite.org/dois/10.4228/zalf-fpdk-tp92)
- BonaRes-Landingpage (schema.org-JSON-LD): temporalCoverage 1984-01-01/2021-12-31, Kontakt Gernot Verch (ZALF), Lizenz CC BY 4.0, conditionsOfAccess verlangt Acknowledgement "Data reused from the BonaRes Data Centre www.bonares.de…" und erwähnt mögliche Embargozeit — [BonaRes](https://maps.bonares.de/finder/resources/googleds/datasets/8f15befa-e299-4424-b891-530d6d046059.html)
- Download-Versuche: `maps.bonares.de/finder/resources/...` (404), GeoNetwork CSW/API (503), DOI-Landingpage ist map.apps-SPA ohne Dateilinks im HTML.

### Gaps
- Dateien nicht geladen → Ertragseinheit/Feuchtebasis, Plotgröße, Anzahl Parzellen, Jahre je Frucht ≥2013 unbestätigt. Manuelle Prüfung im Browser (BonaRes-Portal, "Download"-Button) nötig.

**Datensatz-Record 3:** ZALF Dedelow Monokultur (Wintergetreide + Körnermais) | https://doi.org/10.4228/zalf-fpdk-tp92 (DOI verifiziert, Dateien nicht) | Wintergerste, Winterweizen, Roggen, Triticale, Körnermais | Deutschland, Brandenburg, Dedelow (53.373 N, 13.800 E) | Feldgenau (Bounding box ~1 ha) | unbestätigt (Dauerversuchsparzellen) | 2013–2021 laut Metadaten | 1 Standort | ≤9 Standort-Jahre ×5 Früchte (unbestätigt) | unbestätigt ("grain yields") | 3 N-Stufen (12 Jahre) laut Beschreibung; Rest unbestätigt | CC BY 4.0 + BonaRes-Acknowledgement-Pflicht | Download nur über BonaRes-Webportal (JS); per Skript nicht erreichbar | unbekannt | 2 (nur 1 Standort, Zugang umständlich) | unbestätigt

---

## 4. Genomes to Fields (G2F) – CyVerse Data Commons 2014–2024

### Takeaway
Metadaten/Lizenz/Struktur bestätigt (ODC-PDDL, jährliche Releases 2014–2023 + Wettbewerbe 2022/2024, Ordner phenotypic/weather/soil/supplemental). Die Dateien selbst (readme, Feld-Metadaten mit Koordinaten, Ertragseinheit) konnten NICHT geladen werden: CyVerse Data Store blockiert anonyme Zugriffe mit Cloudflare-Turnstile ("CyVerse – Unblock Me", IP-Verifikation per CAPTCHA) – auch im eingebauten Browser. CAPTCHAs löse ich nicht.

### Cited Findings
- DataCite (DOIs von genomes2fields.org/resources): 10.25739/9wjm-eq41 (2014), kjsn-dz84 (2015), erxg-yn49 (2015 v2), w560-2114 (2017), frmv-wj25 (2014–2017), anqq-sg86 (2018), t651-yy97 (2019), hzzs-a865 (2020), 5ae3-sw62 (2021), 3d3g-pe51 (2022), rzzy-3n27 (2023), tq5e-ak26 (2022 Prediction Competition), 78mn-4394 (2024 Competition), ragt-7213 (Genotypen 2014–2023); Lizenz überall "ODC PDDL" — [DataCite](https://api.datacite.org/dois/10.25739/3d3g-pe51)
- CKAN-API dc.cyverse.org: "Genomes to Fields 2022 dataset", license_id odc-pddl, Beschreibung "2022 phenotypic evaluations, field-level weather data, agronomic information, metadata, and soil data from multi-location field trials … Maize GxE Project"; Ressourcen: readme.txt, a._2022_phenotypic_data, b._2022_weather_data, c._2022_soil_data, z._2022_supplemental_info (alle unter data.cyverse.org/dav-anon/…/GenomesToFields_G2F_data_2022/); analog 2021 und 2023 — [CKAN 2022](https://dc.cyverse.org/api/3/action/package_show?id=genomes_to_fields_2022_dataset), [2023](https://dc.cyverse.org/api/3/action/package_show?id=genomes_to_fields_2023_dataset)
- Alle dav-anon- und datacommons-Aufrufe (curl mit/ohne UA, PROPFIND, Browser) liefern die Seite "CyVerse - Unblock Me … complete the security check" (Cloudflare Turnstile) — gesehen

### Gaps
- Plotabmessungen, Ertragseinheit/Feuchte (vermutet bu/ac bei 15,5 %), Anzahl Standorte/Jahr mit Koordinaten, Standort-Jahre 2014–2023: alles unbestätigt. Manuelles Freischalten der IP im Browser (CAPTCHA) durch den Nutzer wäre nötig; danach sind die Dateien per WebDAV direkt ladbar.

**Datensatz-Record 4:** Genomes to Fields (G2F) Maize GxE | https://www.genomes2fields.org/resources/ bzw. https://dc.cyverse.org/dataset/genomes_to_fields_2022_dataset (DOIs verifiziert; Dateien nicht) | Mais (Hybriden) | USA/Kanada, viele Standorte | unbestätigt (Feld-Metadaten nicht lesbar) | unbestätigt | 2014–2023 (+2024 Competition) | unbestätigt (mehrere Dutzend Standorte/Jahr laut Titel "multi-location") | unbestätigt | unbestätigt (Erwartung bu/ac @15,5 %) | Wetter, Boden, Agronomie-Metadaten laut Ressourcenliste | ODC PDDL (Public Domain) | Anonym, aber Cloudflare-CAPTCHA blockiert Skripte; im Browser nach IP-Freischaltung | Mittel (CSV je Jahr, Harmonisierung über Jahre) | unbestätigt (potenziell 5) | unbestätigt

---

## 5. ICOS Carbon Portal – Ackerstationen (BE-Lon, FR-Gri, FR-EM2, FR-Lam, FR-Aur, DK-Vng, DE-Geb, DE-Kli, DE-RuS, CH-Oe2)

### Takeaway
Bestätigt: Das ETC L2 ARCHIVE enthält eine ANCILLARY-Datei im BADM/BIF-Format; es gibt KEINE Variable "GRAIN_YIELD"/"crop yield". BE-Lon liefert jedoch GRP_BIOMASS-Einträge mit BIOMASS_ORGAN = "Seeds"/"Tubers"/"Total AG" (kg DM m⁻², Mittel + SD über 2 CP- bzw. 14–20 SP-I-Plots) an Erntenahen Terminen 2018–2025 – eine Ertragsnäherung aus destruktiven Biomasseproben, keine Mähdrescher-Erträge. DK-Vng ANCILLARY enthält nur SPP/LAI/VEG_CHEM (keine Biomasse). Download anonym nach Lizenzakzeptanz (Cookie `CpLicenseAcceptedFor=<hash>` genügt), CC BY 4.0.

### Cited Findings
- SPARQL (meta.icos-cp.eu/sparql) für BE-Lon: Spezifikationen u. a. ETC L2 ARCHIVE (1 Objekt, 2017-01-01 bis 2026-09-01), ETC L2 AuxData, ETC L2 Fluxnet (HH), ETC L2 Meteo/Meteosens/Fluxes, NRT-Produkte, Phenocam; keine Objekte der Spezifikation "ICOS ETC Ancillary Raw BIF" für BE-Lon — [SPARQL](https://meta.icos-cp.eu/sparql)
- Archive der 10 Stationen (aktuelle Versionen): DK-Vng 70,9 MB, FR-Lam 83,5 MB, FR-Aur 98,7 MB, FR-Gri 104,2 MB, DE-Geb 108,8 MB, FR-EM2 113,6 MB, BE-Lon 140,9 MB, DE-RuS 141,1 MB, DE-Kli 208,2 MB; CH-Oe2 ohne ARCHIVE-Objekt in dieser Abfrage — SPARQL-Ergebnis `icos/crop_archives.csv`
- Produktbeschreibung (PDF im Archiv/Portal): "It includes also all the ancillary data (ANCILLARY), the general station information (SITEINFO), the information about the instruments used (INST) and the metadata … in the BIF (BADM Interchangeable Format) format" — [ICOSETC_Archive_product_description.pdf](https://meta.icos-cp.eu/objects/kxHPYpZF-l-VRFHaWpLrBlbadmfvPoDs1sUOmKe97Oc)
- `BIF_Ancillary_Variables.csv` (im Archiv): Variablengruppen BASAL_AREA, BIOMASS (BIOMASS, _ORGAN, _PHEN, _SPP, _UNIT, _DATE, _STATISTIC…), DBH, HEIGHTC, LAI, LITTER, PFCURVE, PHEN_EVENT, ROOT_DEPTH, SA, SOIL_CHEM/STOCK/TEX, SPP, SWC, TREES_NUM, VEG_CHEM, WTD – keine YIELD-/HARVEST-/GRAIN-Variable — gesehen
- `ICOSETC_BE-Lon_ANCILLARY_INTERIM_L2.csv` (690 kB, 9 468 Zeilen): Gruppen GRP_BIOMASS 2 792, GRP_HEIGHTC 2 436, GRP_LAI 1 750, GRP_VEG_CHEM 1 440, GRP_SOIL_CHEM 410, GRP_SOIL_STOCK 264, GRP_SOIL_TEX 280, GRP_SPP 96; BIOMASS-Records 321 (2017–2025), Organe Total AG 169, Foliage 92, Stems 20, Tubers 12, Seeds 12, Other 12, Fruits 4; Einheit kgDM m-2. Erntenahe Werte z. B. 2019-07-22 Seeds 0,798 (CP, n=2) bzw. 0,992 kg DM/m² (SP-I, n=14); 2022-07-13 Seeds 1,188/1,172; 2024-07-24 Seeds 0,641/0,663; Tubers 2018-08-09 0,98/0,83; 2023-08-25 0,67/0,58; 2025-10-24 3,18/3,06; Fruits 2021-10-15 0,154 — gesehen
- SITEINFO BE-Lon: LOCATION_LAT 50.5516198, LOCATION_LONG 4.7462339, ELEV 170, IGBP CRO, "cropland of 11.8 ha that has a 4-year rotation between sugar beet, winter wheat, potato, and winter wheat" — gesehen
- DK-Vng ARCHIVE: `ICOSETC_DK-Vng_ANCILLARY_L2.csv` 1 942 Zeilen, Gruppen nur GRP_SPP 42, GRP_LAI 1 680, GRP_VEG_CHEM 220; SITEINFO 56.0374765/9.16070962, IGBP CRO — gesehen
- ETC L2 AuxData (BE-Lon, 2,5 MB zip → 78 MB CSV) = halbstündliche Diagnosevariablen, keine Erträge — Objekt-Metadaten + Dateiliste gesehen
- Download: ohne Cookie liefert data.icos-cp.eu eine HTML-Lizenzseite; mit `-b "CpLicenseAcceptedFor=<objHash>"` kommt das Zip (200, application/zip); Lizenz "ICOS CCBY4 Data Licence" (CC BY 4.0) — [Objekt-Metadaten](https://meta.icos-cp.eu/objects/1C47QsmFVk5ECiOXWS2JOEyF)

### Inferences
- Für Ertrags-Groundtruth ist ICOS nur punktuell nutzbar (BE-Lon: ~6 Erntetermine 2018–2025 als Biomasse der Ernteorgane; andere Stationen müssten einzeln geprüft werden, DK-Vng liefert nichts).
- Kein Mais an BE-Lon (Rotation Rübe–Weizen–Kartoffel–Weizen).

### Gaps
- FR-Gri, FR-EM2, FR-Lam, FR-Aur, DE-Geb, DE-Kli, DE-RuS, CH-Oe2 ANCILLARY nicht geprüft (Archive 83–208 MB).
- Umrechnung Seeds-Biomasse (kg DM/m²) in Kornertrag ist nur näherungsweise möglich.

**Datensatz-Record 5:** ICOS ETC L2 ARCHIVE – Ackerstationen | https://data.icos-cp.eu/portal/ ; Beispiel BE-Lon Archiv https://meta.icos-cp.eu/objects/1C47QsmFVk5ECiOXWS2JOEyF (verifiziert, geladen) | BE-Lon: Zuckerrübe, Winterweizen, Kartoffel (kein Mais); andere Stationen unbestätigt | BE, FR, DK, DE, CH | Stationskoordinaten 7 Dezimalen; Flächenpolygon | Feld ~11,8 ha (BE-Lon); Biomasse aus 2 CP + 14–20 SP-I Plots | 2017–2025 (BE-Lon Biomasse) | 10 Ackerstationen; Biomasse-Erträge bisher nur bei BE-Lon bestätigt (DK-Vng: keine) | BE-Lon ca. 6 Ernte-Biomassewerte 2018–2025; übrige unbestätigt | BIOMASS Seeds/Tubers/Total AG in kg DM m⁻² (Mittel, SD, n); keine Kornertragsvariable | Flüsse, Meteo, LAI, Pflanzenhöhe, Bodenchemie, Phänologie(Phenocam) | CC BY 4.0 (ICOS-Lizenz) | Anonym nach Lizenzklick (Cookie), kein Login | Hoch (140 MB-Archive, BADM-Langformat parsen) | 2 (für Ertrag) | bestätigt (Struktur), teilweise unbestätigt (andere Stationen)

---

## 6. SLU R3-9001 Swedish Long-term Soil Fertility Experiments (researchdata.se 2024-462, DOI 10.5878/eqj9-j270)

### Takeaway
Bestätigt: Langformat-TSV mit 249 800 Zeilen, 1962–2022, 9 Standorte (10 IDs; Örja→Borgeby 2010), Ertrag als Trockenmasse kg/ha je Parzelle (63 Parzellen je Standort-Jahr), 79 Standort-Jahre ≥2013 mit Kornertrag; nur Ortsnamen, KEINE Koordinaten in den Dateien; kein Mais.

### Cited Findings
- Landingpage/API: 7 Dateien, 20,63 MiB; `R39001_data.tsv` 21,6 MB; Doku-TSVs (README, component/location/plot/units/variables) — [API](https://api.researchdata.se/dataset/2024-462/1), [Katalog](https://researchdata.se/en/catalogue/dataset/2024-462)
- README: Titel "SLU long-term field experiments: The Swedish soil fertility experiments (R3-9001), crop and soil data from 1962 and onwards"; DOI 10.5878/eqj9-j270; "License: CC0 1.0"; 15 Spalten, 249 801 Zeilen; Variable `yield` = "Total dry mass of the given component" — gesehen
- `R39001location_description.tsv`: M-4-1957/M-4-2010 Borgeby/Örja (Landskrona→Bjärred, Skåne), M-1-1957 Fjärdingslöv (Trelleborg), M-2-1957 Orupsgården (Höör), M-6-1957 Ekebo (Helsingborg), C-7-1963 Kungsängen (Uppsala), C-8-1963 Fors (Tierp), R-94-1966 Bjertorp (Skara), E-9-1966 Klostergården (Linköping), E-10-1966 Högåsa (Linköping) — nur Namen, keine Koordinaten — gesehen
- Daten: Jahre 1962–2022; Komponenten grain 76 291, straw, cut1/2, beet, seed, soil; Einheiten kg/ha ("kilograms of dry mass per hectare"), ton/ha (Rüben), %, mg/kg; Ertragszeilen (grain/seed/beet) 34 861; ≥2013: Standort-Jahre 79; Früchte ≥2013: winter_wheat 1 838, spring_barley 1 495, oats 933, sugar_beet 542, seed_flax 334, spring_wheat 174, spring_rapeseed 162 Zeilen; Jahre ≥2013 je Standort: M-1, M-4-2010, M-6 alle 2013–2022; E-9/E-10/M-2 2013–2022 außer 2016; C-8 8 Jahre; R-94 8 Jahre; C-7 6 Jahre; 63 Parzellen je Standort-Jahr (Ekebo 2015/2020); Faktoren: Fruchtfolge I/II, 4 PK-Stufen, 4 N-Stufen, Stallmist ja/nein — eigene Zählung
- Plot-Metadaten: "The design of these experiments are complex and differs between sites. Please visit the corresponding GLTEN metadata entry" — gesehen

### Gaps
- Koordinaten und Parzellengrößen nicht in den Dateien (GLTEN-Eintrag nicht geprüft).
- Kein Mais; keine Saat-/Erntedaten in den Dateien (nur Jahr).

**Datensatz-Record 6:** SLU Swedish Soil Fertility Experiments R3-9001 | https://doi.org/10.5878/eqj9-j270 (verifiziert; Dateien geladen) | Winterweizen, Sommergerste, Hafer, Sommerweizen, Zuckerrübe, Raps, Lein, Ley | Schweden (Skåne, Uppland, Västergötland, Östergötland) | Nur Ortsnamen (Hof/Gemeinde), keine Koordinaten in Dateien | Dauerversuchsparzellen, 63 Parzellen/Standort-Jahr, Größe unbestätigt | 2013–2022 | 9 Standorte (10 IDs) | 79 Standort-Jahre ≥2013 | yield kg TM/ha (Korn/Stroh/Rübe t/ha), Protein, TKG, Lager | N/PK/Stallmist-Faktoren, Bodenchemie (P-AL, K-AL, pH, C, N) | CC0 1.0 | Anonym, direkt (api.researchdata.se) | Gering–mittel (Langformat pivotieren) | 3 | bestätigt (Koordinaten unbestätigt)

---

## 7. Grignon 12-Jahres-Anbausystemversuch 2009–2020 (Recherche Data Gouv 10.57745/5TJJZA)

### Takeaway
Bestätigt: 19 Tab-Dateien, 4 Anbausysteme × 3 Wiederholungen = 12 Parzellen an einem Standort (48.84 N, 1.95 E; Bounding box angegeben), Mähdrusch-Ertrag bei 0 % Feuchte (t/ha? – Werte 0–149, Einheit nicht in Datei, Spaltenname "Total_yield_0_%_moisture"), Erntefläche je Probe ~160–275 m², 72 Mais-Zeilen (9 Jahre), 96 Parzellen-Jahre ≥2013, Lizenz etalab 2.0.

### Cited Findings
- Dataverse-API: Titel "Innovative cropping systems designed to reach both environmental and production targets: data set of biotic and abiotic variables from a twelve-year French field trial."; Lizenz "etalab 2.0"; Beschreibung "French (N 48.84°, E 1.95°) field trial, over a twelve-year period (2009-2020), in which four innovative cropping systems … yield harvested with a combine machine"; Geo: Thiverval-Grignon, Bounding box 1.893511–1.970748 E, 48.823062–48.860786 N; 19 .tab-Dateien (u. a. data_yield_combine_all_species_2023 73 kB, data_agricultural_practices_2023 139 kB, yield_components je Art, soil, climatic, growth_stage) — [API](https://entrepot.recherche.data.gouv.fr/api/datasets/:persistentId/?persistentId=doi:10.57745/5TJJZA)
- `data_yield_combine_all_species_2023`: 821 Zeilen; Spalten Year, CS, Replicate_number, Plot_number, Sample_number, Species, Date, Sample_area_m2, Sample_moisture_%_dry_matter, Thousand_kernels_weight_0_%_moisture, Total_yield_0_%_moisture; Systeme PHEP 216, No-Pest 199, L-EN 205, L-GHG 201; 12 Parzellen (CS×Rep×Plot); Species WW 270, WR 75, Maize 72, Tri 72, WF 72, SB 48, SF 49, WB 30 …; Sample_area_m2 typisch 203–207 (Mais 233–275, 'MD' = fehlend); Jahre 2009–2020 (57–75 Zeilen/Jahr); ≥2013: 535 Zeilen, 96 Parzellen-Jahre; Mais-Jahre 2009, 2011–2015, 2018–2020 (6–12 Zeilen/Jahr); Ertragswerte 0–148,7, Median 49,7 — eigene Zählung
- `data_agricultural_practices_2023`: 1 325 Zeilen; Practice_type Sowing 228, Harvest 133, Fertilization 137, Tillage 121, Herbizid 311, Fungizid 59 …; Spalten Date, Machine, Product, Variety, Quantity_ha, Dose_kgN_ha, Dose_kernel_m2 — gesehen
- `data_crop_sequence_2023`: Hauptfrüchte je Parzelle/Jahr (CR) inkl. Maize 12 Parzellen-Jahre — gesehen

### Gaps
- Einheit von Total_yield_0_%_moisture nicht in der Datei (Werte wie 66,4 für Sommergerste legen q/ha = dt/ha nahe; Glossar/Data-Paper nicht geprüft) → Einheit unbestätigt.
- Exakte Parzellenkoordinaten/-größen nicht in geladenen Dateien (nur Sample_area ~200 m² und Bounding box ~5 km).

**Datensatz-Record 7:** Grignon Innovative Cropping Systems 2009–2020 | https://doi.org/10.57745/5TJJZA (verifiziert; 3 Dateien geladen) | Winterweizen, Mais, Raps, Triticale, Ackerbohne, Erbse, Gerste, Soja u. a. | Frankreich, Thiverval-Grignon (48.84 N, 1.95 E) | Standort ±2–3 km (Bounding box), Parzellen nicht georeferenziert | Großparzellen; Ernteprobe ~160–275 m² | 2013–2020 | 1 Standort, 12 Parzellen (4 Systeme × 3 Wdh.) | 8 Standort-Jahre (96 Parzellen-Jahre, Mais 2013–15, 2018–20 = 6 Jahre × 1–2 Parzellen) | Mähdrusch-Ertrag bei 0 % Feuchte, Einheit unbestätigt (vermutl. q/ha), TKG, Erntefeuchte | Alle Maßnahmen mit Datum/Produkt/N-Dosis, Phänologie, Biomasse/N, Boden, Klima, TFI, Energie | etalab 2.0 (Licence Ouverte) | Anonym, direkt | Gering (saubere CSVs) | 3 | bestätigt (Einheit unbestätigt)

---

## 8. Cluster Marchfeld – Fuchsenbigl, Groß-Enzersdorf, Rutzendorf 2018–2022 (Zenodo 15212569)

### Takeaway
Bestätigt: 161 Ertragszeilen (kg TM/ha) für 3 Standorte × 5 Jahre × 3–4 Bodenbearbeitungsvarianten, 3–4 Wiederholungen; KEIN Mais-Ertrag (Fruchtfolge: Sorghum, Winterweizen, Soja, Wintergerste, Triticale, Raps, Erbse, Roggen, Luzerne); keine Koordinaten und keine Plotgrößen in den Dateien.

### Cited Findings
- Zenodo-API: 4 CSVs (CropYield 13 kB, SoilParameter 55 kB, DataDescription 2 kB, Agricultural_Management 11 kB), CC BY 4.0; Beschreibung: drei LTER-Standorte, Bodenbearbeitung reduziert (10–15 cm) vs. Pflug (25–30 cm), konventionell zusätzlich No-till und Minimum (5–8 cm); 1 153 Records — [Zenodo API](https://zenodo.org/api/records/15212569)
- `ClusterMarchfeld_Data_CropYield.csv` (Semikolon, Dezimalkomma): 161 Zeilen; Fuchsenbigl 45, Gross-Enzersdorf 76, Rutzendorf 40; Crop_Yield_Dry in "kg ha-1" (Trockenmasse); Standort×Jahr×Frucht: FB 2018 Sorghum, 2019 WW, 2020 Soja, 2021 WG, 2022 Triticale; GE 2018 Soja, 2019 WW, 2020 Soja, 2021 WW, 2022 Winterraps; Rutzendorf (organisch) 2018 Erbse, 2019 WW, 2020 Roggen, 2021/22 Luzerne; Tillage: Conventional 54, Reduced 54, Minimal 19, No till 19, Minimum 15; 45 Standort-Jahr-Frucht-Tillage-Kombinationen mit je 3–4 Zeilen (Wiederholungen) — eigene Zählung
- `ClusterMarchfeld_Agricultural_Management.csv`: 116 Zeilen (Tillage 47, Seeding 25, Fertilization 15, Harvest 8, Pflanzenschutz 13, Irrigation 4); Beispiel "Gross-Enzersdorf Seeding 22.04.2020 Maize; Seed sowing rate 80 000 grains/ha" – obwohl die Ertragsdatei für GE 2020 "Soy bean" führt (Inkonsistenz) — gesehen
- DataDescription: Site_Name "Fuchsenbigel (FB), Gross-Enzersdorf (GE) or Rutzendorf (MUBIL)"; keine Koordinaten-/Flächenspalten — gesehen

### Gaps
- Koordinaten, Plotgrößen: nicht in Dateien (Data Descriptor "under review").

**Datensatz-Record 8:** Cluster Marchfeld LTER (Zenodo) | https://zenodo.org/records/15212569 (verifiziert; alle CSVs geladen) | Sorghum, Winterweizen, Soja, Wintergerste, Triticale, Winterraps, Körnererbse, Roggen, Luzerne – kein Mais | Österreich, Marchfeld (NÖ) | Nur Standortnamen; keine Koordinaten in Dateien | Parzellen unbekannter Größe, 3–4 Wdh. | 2018–2022 | 3 Standorte | 15 Standort-Jahre (45 Varianten-Jahre, 161 Parzellen-Jahre) | kg TM/ha | Management mit Datum (Bodenbearbeitung, Saat, Düngung, Ernte, Bewässerung), Boden-C/N je Horizont | CC BY 4.0 | Anonym, direkt | Gering | 2 (AT-Test nur für Nicht-Mais) | bestätigt

---

## 9. GROW-Africa v2.0 (Zenodo 16544448)

### Takeaway
Bestätigt: Punktdaten mit expliziter Spalte SpatialPrecision_km_. Für Mais ≥2013 gibt es in `GROW-Africa_Point.xlsx` 38 464 Zeilen mit Präzision 0,03 km (OneAcre_survey 30 302 – Farmer-Survey, selbstberichtet; Niche_trial 8 162 – On-farm-Versuche Ruanda). Echte Crop-Cuts mit GPS: `GROW-Africa_LSMS_cropcut.xlsx` (Äthiopien 2012/2014/2016/2019; Mais ≥2013: 1 947 Zeilen, aber nur 374 unterschiedliche GPS-Punkte = EA-Ebene/versetzt). Regionalstatistiken separat in `GROW-Africa_Regional.xlsx`.

### Cited Findings
- Zenodo: CC BY 4.0; Dateien GROW-Africa-Database.zip 64,6 MB (4 xlsx), Spatial-Look-Up-Tables.zip, GADM-Look-Up-Tables.zip, Matlab-Code.zip, manuscript.pdf, readme.txt — [Zenodo API](https://zenodo.org/api/records/16544448)
- readme: LSMS_cropcut = Crop-Cut-Daten der Weltbank-LSMS (ETH2011/2013b/2015/2018); LSMS_survey = Farmer-Survey; Point = "point-based yield data (derived from either farmer surveys or crop cuts) … 'SpatialPrecision_km_' estimates the spatial precision associated with each reported Latitude/Longitude"; Regional = Ministeriumsstatistiken (FAOSTAT, HarvestStat, RCeA) — [readme.txt](https://zenodo.org/api/records/16544448/files/readme.txt/content)
- `GROW-Africa_Point.xlsx`: 131 812 Zeilen; Spalten Source, Crop, HarvestYear, Latitude, Longitude, SpatialPrecision_km_, L0–L3_GID, Country, SiteName, Area_ha_, Yield_ton_ha_, PlantDate, HarvestDate, Notes; Quellen OneAcre_survey 77 474, CEEPA_time_avg 20 933, Niche_trial 14 354, CEEPA_annual 14 104, USAID_Zimbabwe 2 852, Corbeels2020 2 095; Mais ≥2013: 58 495 Zeilen, 51 750 mit Koordinaten, 31 769 unterschiedliche Koordinatenpaare (5 Dez.), Präzision 0,03 km: 38 464, 1,85 km: 333 (Corbeels2020, Stationsversuche), 5 km: 13 073, fehlend 6 625 — eigene Zählung
  - OneAcre_survey Mais ≥2013: 43 129 (Kenia 23 319, Tansania 5 742, Burundi 5 265, Ruanda 5 104, Malawi 1 769, Sambia 1 686, Uganda 244), Jahre 2015–2020, Area_ha z. B. 0,1–0,8 ha, PlantDate/HarvestDate in ~33 000 Zeilen, 37 183 mit Koordinaten (29 811 unterschiedliche).
  - Niche_trial: 14 354 Zeilen nur Ruanda 2014–2021 (Saisons A/B), Präzision 0,03 km (8 162) bzw. 5 km (6 192), 1 921 unterschiedliche Koordinaten, keine Fläche, Plant/HarvestDate meist vorhanden.
  - Corbeels2020: 333 Zeilen 2013–2017, 37 Standorte (Stationsversuche, Präzision 1,85 km, Notes z. B. "ConventionalTillage").
- `GROW-Africa_LSMS_cropcut.xlsx`: 11 345 Zeilen; Spalten Country, Source, Year, GPS_lat, GPS_lon, GIDs, holder/household/parcel/field_id, Crop, cropCutDay/Month, freshWeightKg, dryWeightKg, Yield_ton_ha_; nur Äthiopien (ETH2011 2012, ETH2013b 2014, ETH2015 2016, ETH2018 2019); Mais ≥2013: 1 947 Zeilen (2014: 477, 2016: 810, 2019: 660), alle mit GPS, aber nur 374 unterschiedliche GPS-Punkte (typisch 2–8 Felder je Punkt → Haushalts-/EA-Koordinate) — eigene Zählung

### Inferences
- "≤100 m Präzision" bei Mais ≥2013: 38 464 Zeilen, aber praktisch alle Farmer-Survey-Erträge (selbstberichtet, Flächen 0,1–0,8 ha) oder On-farm-Niche-Trials; die einzigen Crop-Cuts (LSMS Äthiopien) sind auf wenige hundert Punkte aggregiert.

### Gaps
- `GROW-Africa_LSMS_survey.xlsx` (31 MB) und `Regional.xlsx` nicht inhaltlich ausgewertet.

**Datensatz-Record 9:** GROW-Africa v2.0 | https://zenodo.org/records/16544448 (verifiziert; Datenbank geladen) | Mais (68 174 Punktzeilen), Bohnen, Hirse, Erdnuss u. v. m. | Subsahara-Afrika (Punktdaten v. a. Kenia, Ruanda, Tansania, Burundi, Äthiopien) | Spalte SpatialPrecision_km_: 0,03 km (OneAcre, Niche), 1,85 km, 5 km; LSMS-GPS auf EA/Haushalt | Kleinbauernfelder 0,1–0,8 ha (OneAcre), Crop-Cut-Subplots (LSMS) | 2013–2021 | >30 000 Punkte (Mais ≥2013) | Mais ≥2013 mit ≤0,1 km: 38 464 Feld-Jahre (Survey/On-farm); Crop-Cuts 1 947 (374 Punkte) | Yield t/ha (Basis je Quelle; LSMS fresh/dry kg je Cut) | Plant-/HarvestDate (OneAcre, Niche), Fläche, Notes | CC BY 4.0 (GADM-Grenzen eigene Lizenz) | Anonym, direkt | Mittel (xlsx, heterogene Quellen filtern) | 3 (für Afrika-Transfer), 1 (für AT) | bestätigt

---

## 10. Dryad 10.5061/dryad.kd51c5bjt – Moore & Bernacchi 2025 (UIUC Energy Farm / US-Bo)

### Takeaway
Bestätigt (per Vorschau im eingebauten Browser): eine CSV mit 26 Jahreszeilen 1997–2022 und 15 Spalten (NEE, Yield, NECB) für Maize_CT, Maize_NT, Miscanthus, RestoredPrairie, Switchgrass; Ertrag in g C/m² (nicht kg/ha), keine Koordinaten in der Datei, CC0. Für Feld-Ertragsdaten praktisch unbrauchbar (Jahres-Standortsummen, C-Einheit).

### Cited Findings
- DataCite/Dryad: Lizenz CC0 1.0, Größe 6 558 Bytes, veröffentlicht 2025-09-23; Dateien README.md 3,5 kB und UIUC_Final_Data.csv 3,06 kB; Primärartikel doi 10.1111/gcb.70291 — [DataCite](https://api.datacite.org/dois/10.5061/dryad.kd51c5bjt), [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.kd51c5bjt)
- CSV-Vorschau: Kopfzeile Years, Maize_CT_NEE … Switchgrass_NECB; Einheitenzeile gC/m2/year bzw. gC/m2; Maize_NT 1997–2006 und 2011–2017 (US-Bo Bondville, NT), Maize_CT 2009–2022 (UIUC), Miscanthus 2009–2022, Prairie/Switchgrass 2009–2015; Beispiel 2014 Maize_CT_Yield 652,24 g C/m² — gesehen
- API-Download anonym blockiert (401 bzw. Anubis-JS-Challenge für curl); Browser-Vorschau funktioniert ohne Login.

**Datensatz-Record 10:** Moore & Bernacchi 2025 UIUC/US-Bo NEE-Yield-NECB | https://doi.org/10.5061/dryad.kd51c5bjt (verifiziert; Inhalt per Browser-Vorschau) | Mais (CT/NT, Mais-Soja-Rotation), Miscanthus, Switchgrass, Prärie | USA, Illinois (Urbana Energy Farm, Bondville) | Keine Koordinaten in Datei (AmeriFlux-Sites US-UiA/B/C/D, US-Bo) | Flux-Tower-Footprint (Feld) | 2013–2022 (Maize_CT), 2013–2017 (Maize_NT) | 2 Mais-Flächen | ~15 Feld-Jahre Mais ≥2013 | Yield in g C m⁻² (Trockenmasse × 0,45) | NEE, NECB jährlich | CC0 | Anonym im Browser; curl blockiert | Gering, aber Umrechnung nötig | 1 | bestätigt

---

## 11. DataverseNO 10.18710/IZ3EFE – Nordic multi-environment variety trials (Gerste, Rotklee, Kartoffel)

### Takeaway
Bestätigt: Gerste-Datei mit 59 910 Zeilen (Sorte×Trial), 2 663 Trials 1970–2024, 2 662 mit Koordinaten (meist 12–13 Dezimalen, einige nur 1–2), 772 Trials ≥2013 (DK 209, FI 153, IS 52, NO 132, SE 226) an 460 unterschiedlichen Standorten (3 Dez.); Ertrag "dry_matter_yield: hkg/ha at 15% moisture"; Saat-/Erntedatum teilweise; CC BY 4.0. Kein Mais.

### Cited Findings
- Dataverse-API: Titel "A multi-environment dataset consisting of official field trials for three major crops in the Nordic countries"; CC BY 4.0; Dateien 00_README(.txt) ×4, 01_BarleyData.csv 17,3 MB, 02_RedCloverData.csv 4,1 MB, 03_PotatoData.csv 2,0 MB; Zeitraum 1970–2024; Länder DK, FI, IS, NO, SE — [API](https://dataverse.no/api/datasets/:persistentId/?persistentId=doi:10.18710/IZ3EFE)
- README_BARLEY: Spalten trial, nfts_id, year, country, longitude, latitude ("decimal degrees"), region, variety, sowing_date, measure_date, "dry_matter_yield: Dry matter yield in hkg/ha reported at 15% moisture", treatment_group/treatment/experiment_design (nur DK/SE, verbatim aus NFTS) — gesehen
- Zählung 01_BarleyData.csv: 59 910 Zeilen; 2 663 Trials (DK 1 121, FI 1 065, IS 119, NO 132, SE 226); Jahre 1970–2024; ≥2013: 772, ≥2017: 509; Trials/Jahr 2014–2024 zwischen 55 und 78; Koordinaten in 2 662 Trials; Dezimalstellen Breite: 13 (2 092), 12 (243), 5 (154), 7 (67), 6 (50), 11 (37), 2 (10), 1 (7); 1 047 unterschiedliche Standorte (3 Dez.), 460 davon ≥2013; sowing_date in 32 640 Zeilen, measure_date in 51 397; Ertrag Median 53,9 hkg/ha; Beispiele: Dänemark 2013 55.0726/14.9032 "Split-plot, 2 faktorer, 4 gentagelser"; Schweden 2014 59.7162/17.3550 "Alpha-design, 2 upprepningar"; Island 2013 64.15121/-21.75269 — eigene Zählung
- README allgemein: DK/SE aus NFTS heruntergeladen, NO/FI/IS direkt von NIBIO/LUKE/LBHI kuratiert — gesehen

### Gaps
- Ob die Koordinaten Versuchsfeld oder Hof/Ort bezeichnen, ist nicht dokumentiert ("Longitude coordinate of the trial site"); Plotgrößen fehlen.
- Rotklee/Kartoffel nicht ausgewertet.

**Datensatz-Record 11:** Nordic VCU/National Variety Trials (Gerste, Rotklee, Kartoffel) | https://doi.org/10.18710/IZ3EFE (verifiziert; Gerste geladen) | Sommergerste (plus Rotklee, Kartoffel) | DK, FI, IS, NO, SE | Dezimalgrad, überwiegend ≥5 Dezimalen (Trial-Standort), wenige 1–2 Dez. | Parzellenversuche (Design in DK/SE angegeben; Größe nicht) ; Werte = Sorte×Trial | 2013–2024 | 460 Standorte ≥2013 (1 047 gesamt) | 772 Trial-Jahre ≥2013 (509 ≥2017) | hkg/ha (= dt/ha) bei 15 % Feuchte | Saat-/Erntedatum (teilweise), Sorte, Behandlung (Fungizid), Design | CC BY 4.0 | Anonym, direkt | Gering | 4 (Gerste), kein Mais | bestätigt

---

## 12. 4TU – BASIS Lelystad Bodenbearbeitungsversuch 2009–2022

### Takeaway
Bestätigt: Datensatz 10.4121/5708634c-05b4-40e2-9d3e-9c12fcad7882 (Dekkers et al. 2023, WUR Open Teelten), CC BY 4.0, 3 xlsx + README; Ertrags-xlsx mit 12 Frucht-Sheets (Kartoffel, Getreide, Zwiebel, Zuckerrübe, Möhre, Kohl, Gras-Klee, Kürbis, Bohnen, Erbsen, Gründünger), 5 Felder (J9-4, J9-6 konventionell "GA"; J10-3, J10-4, J10-6 ökologisch "BIO"), Tillage PL/NKG+/NKG-/OPL, Erträge kg/ha (Getreide auch "15% vocht"), Saat-/Erntedaten je Zeile; KEIN Mais, keine Koordinaten.

### Cited Findings
- 4TU-API (POST /v2/articles/search "BASIS"): "Data from: 'Effects of reduced tillage on (cash) crop yields, soil quality and other ecosystem services - Results from 2009 till 2022 of the long term experiment BASIS, the Netherlands'", DOI 10.4121/5708634c-05b4-40e2-9d3e-9c12fcad7882.v1, veröffentlicht 2023-12-13, CC BY 4.0, Geolocation "Lelystad, The Netherlands", Zeit 2009–2023, Dateien Data_soil_chemical_BASIS.xlsx 961 kB, Data_soil_physical_BASIS.xlsx 340 kB, Data_yield_BASIS.xlsx 873 kB, README.txt 11 kB — [4TU API](https://data.4tu.nl/v2/articles/5708634c-05b4-40e2-9d3e-9c12fcad7882), [Landing](https://data.4tu.nl/datasets/5708634c-05b4-40e2-9d3e-9c12fcad7882/1)
- README: "14-year-data on yield, yield quality, chemical and physical soil aspects of 5 fields (3 organic and 2 conventional fields) in 4 different tillage systems (PL, RT, RTS, RT/SPL)"; Variablen Bruto/Netto (kg/ha), Vers opbrengst, Drogestof %, "15% vocht = Yield (kg/ha) converted to 15% moisture", Vocht %, HL, DKG, Datum zaaien/poten/planten, Datum oogst; Bericht WPR-1033 — gesehen
- Data_yield_BASIS.xlsx: Sheets graan (254 Zeilen; Jahre 2009–2022 außer 2019; Felder J9-4/J9-6/J10-3/J10-4/J10-6; Spalten Vers opbrengst, Vocht %, 15% vocht, HL, DKG, Eiwit), aardappel (2009–2020), suikerbieten (2009–2021), zaaiuien, peen, kool, gras(klaver), pompoen, sperziebonen, conservenerwt, groenbemesters; Tillage NKG-/NKG+/PL/OPL; keine Lat/Lon-Spalten; kein Mais-Sheet — eigene Inspektion

### Gaps
- Feld-/Parzellengrößen und Koordinaten nicht in Dateien (nur "Lelystad", Edelhertweg 1); Bericht WPR-1033 nicht geprüft.

**Datensatz-Record 12:** BASIS Lelystad (WUR) reduzierte Bodenbearbeitung 2009–2022 | https://doi.org/10.4121/5708634c-05b4-40e2-9d3e-9c12fcad7882 (verifiziert; Dateien geladen) | Kartoffel, Getreide (Winter-/Sommerweizen, Gerste), Zuckerrübe, Zwiebel, Möhre, Kohl, Gras-Klee, Kürbis, Bohnen, Erbsen – kein Mais | Niederlande, Lelystad (Broekemahoeve) | Nur Ortsangabe, keine Koordinaten | 5 Felder, Parzellengröße unbestätigt | 2013–2022 | 5 Felder, 1 Standort | ~40 Feld-Jahre ≥2013 (je Feld 1 Frucht/Jahr) | kg/ha frisch, Getreide zusätzlich bei 15 % Feuchte, TM-% bei Gras | Saat-/Erntedatum, Sorte, Bodenbearbeitungssystem, Bodenchemie/-physik | CC BY 4.0 | Anonym, direkt | Mittel (niederländische Mehrsheet-xlsx mit Kopf-/Fußzeilen) | 2 | bestätigt

---

## Zusammenfassung der Verifikation

| # | Datensatz | Status | Kernbefund |
|---|-----------|--------|-----------|
| 1 | INVITE Weizen-VCU | bestätigt | 1 775 Trials, 605 ≥2013; 0 % TM; CZ/HU/CH feldgenau, FR 1 Dez.; "Confidential"-Hinweis in Dateien |
| 2 | BRIWECS | bestätigt | 6 Orte, 28 Standort-Jahre, 34 355 Parzellenerträge dt/ha 100 % TM, Plot 10,5 m² |
| 3 | ZALF Dedelow | unbestätigt | Dateien nicht per Skript erreichbar |
| 4 | G2F | unbestätigt | Cloudflare-CAPTCHA; nur Lizenz (PDDL)/Struktur bestätigt |
| 5 | ICOS | bestätigt | Keine Ertragsvariable; BE-Lon Biomasse Seeds/Tubers kg DM/m² 2018–2025; DK-Vng nichts |
| 6 | SLU R3-9001 | bestätigt | 79 Standort-Jahre ≥2013, kg TM/ha, keine Koordinaten |
| 7 | Grignon | bestätigt | 12 Parzellen, 96 Parzellen-Jahre ≥2013, Ertrag 0 % Feuchte (Einheit unbestätigt) |
| 8 | Marchfeld | bestätigt | kein Mais, keine Koordinaten, kg TM/ha |
| 9 | GROW-Africa | bestätigt | 38 464 Mais-Zeilen ≥2013 mit 0,03 km, aber Survey/On-farm; Crop-Cuts nur ETH |
| 10 | Dryad Moore | bestätigt | Jahreswerte g C/m², unbrauchbar für Feldskala |
| 11 | Nordic | bestätigt | 772 Gerste-Trials ≥2013 mit Koordinaten, hkg/ha @15 % |
| 12 | BASIS | bestätigt | kein Mais, keine Koordinaten, 5 Felder |
