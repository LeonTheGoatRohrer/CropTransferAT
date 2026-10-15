# Datenquellen

Je Datensatz: Quelle, Version, Lizenz, Abrufdatum, Dateien, Neu-Download, Inhalt, Auffälligkeiten, Status.
Rohdaten liegen unter `data/raw/` und sind **nicht** im Repository (`.gitignore`). Abrufdatum aller Einträge: **2026-10-15**, sofern nicht anders angegeben.

Umrechnung Mais (gilt für alle US-Quellen): 1 bu/ac = 62,77 kg/ha (56 lb/bu). Auf 15,5 % Kornfeuchte: `Y_15.5 = Y_m × (1 − m) / (1 − 0,155)`.

## Übersicht

| # | Datensatz | Status | Kern-Kennzahl | Lizenz |
|---|---|---|---|---|
| 1 | KBS LTER – MCSE-Parzellen (DT 51) | ✅ verfügbar | 295 Mais-Parzellen-Jahre, davon **96 in der HLS-Zeit** (2014/17/20/23) | KBS-Nutzungsbedingungen – Veröffentlichung nur mit schriftlicher Erlaubnis |
| 2 | KBS LTER – Ertragspunkte (DT 185, 828) | ✅ verfügbar | Mais-Punkte 2005/08/11 (185), 2014/17/20/23 (828) | wie 1 |
| 3 | KBS LTER – Scale-up (DT 145, 163, 254) | ✅ verfügbar | 62 Mais-Feld-Jahre (27 Felder), nur 2006–2012 | wie 1 |
| 4 | USDA BARC Gridded Yield Archive | ✅ verfügbar | **62 Mais-Feld-Jahre** (~33 Felder), 2014, 2016–2021 | U.S. Public Domain |
| 5 | Colorado (Akron) Dryland | ✅ verfügbar (nur Stichprobenpunkte) | 10 Mais-Teilflächen-Jahre, 2019–2022 | CC0 |
| 6 | Mead US-Ne1/2/3 (AmeriFlux BADM) | ⏳ angefragt / Konto nötig | unbekannt | CC-BY-4.0 (nach Login) |
| 9 | One Acre Fund – Maize management and yield (Zenodo 10.5281/zenodo.11115815) | ⚠️ verfügbar; Filter §3.1 so nicht umsetzbar | 14 773 Maisfelder, 2016–2022 (ohne 2021), je 1 Jahr; 10 332 mit exakter Position; **keine Feldgröße**, Koordinaten auf 0,001° gerundet | CC BY 4.0 |
| 10 | YieldSAT (yieldsat.github.io) | ⏳ Zugang beim Projektinhaber (Formular) | Mais: 185 Felder AR + 118 BR, 2017–2024 | unklar – erst nach Zugang |
| 11 | SSURGO (USDA NRCS, Soil Data Access) | ✅ verfügbar (Ertragsschätzung ⚠️ lückenhaft) | NCCPI Mais KBS 0,664 (1 Map-Unit für alle 24 Parzellen), BARC 1-7 0,507; Mais-Ertragsschätzung KBS fehlt, BARC 1-7 116,5 bu/ac | U.S. Public Domain |
| 12 | Versuchsberichte Hatzendorf (Land Steiermark) + LK-OÖ-Sorten-/Praxisversuche | ✅ gesammelt (nicht ausgewertet); Koordinaten fehlen | `at_trials.csv`: 150 Zeilen – Stmk 44 (Wagna, Kalsdorf u. a., 2012–2024), OÖ 106 (13 Orte, 2013–2026) – **nur Österreich-Test** | öffentlich, Quellenangabe |
| 13 | Bodenklimazahl (Finanzbodenschätzung) | ⏳ optional, Anfrage beim Projektinhaber | Ertragsfähigkeit 1–100 je Fläche (AT) – nur Plausibilitätsprüfung | unklar |

---

## 1–3. KBS LTER (Kellogg Biological Station, Hickory Corners, Michigan)

**Quelle:** https://lter.kbs.msu.edu – Datentabellen als CSV ohne Login (`https://lter.kbs.msu.edu/datatables/<N>.csv`).
- Dataset 23 „Agronomic Yields 1989–2025“ (`knb-lter-kbs.20.93`) → Tabelle 51
- Dataset 40 „Precision Ag Yield Monitoring“ (`knb-lter-kbs.37.46`) → Tabellen 185, 828
- Dataset 61 „MCSE Scale-up 2006–2012“ (`knb-lter-kbs.56.60`) → Tabellen 145, 163, 254
- EDI (portal.edirepository.org) verweigerte am Abruftag anonymen Zugriff (HTTP 403) → nicht genutzt; ob EDI-Revisionen identisch sind, ist ungeprüft.

**Nutzungsbedingungen:** https://lter.kbs.msu.edu/data/terms-of-use/ – Verwendung in einer Veröffentlichung erfordert **schriftliche Erlaubnis** des Lead PI / Project Director; Danksagung KBS LTER (NSF DEB 2224712). → **E-Mail an KBS (Projektinhaber) ist Voraussetzung für die Veröffentlichung abgeleiteter Ergebnisse.** Rohdaten nie ins Repository.

**Dateien** (`data/raw/kbs/`): `kbs_datatable_{51,145,163,185,254,828}.csv` (zusammen ~112 MB), `kbs_dataset_{23,40,61}.eml.xml`, `gis/exp_plots_mainsite.zip`, `gis/plot_points_mainsite.zip`, `gis/KBS_boundary.zip` (+ FGDC-Metadaten).

**Neu-Download:**
```bash
curl -L -o kbs_datatable_<N>.csv https://lter.kbs.msu.edu/datatables/<N>.csv   # N = 51,145,163,185,254,828
curl -L -o kbs_dataset_<D>.eml.xml https://lter.kbs.msu.edu/datasets/<D>.eml   # D = 23,40,61
curl -L -O https://lter.kbs.msu.edu/maps/GIS/exp_plots_mainsite.zip
```
Server langsam (0,1–0,25 MB/s) – keine kurzen Timeouts setzen.

### Tabelle 51 – MCSE-Parzellenerträge (Haupt-Label-Quelle)
- 24 Parzellen = Behandlungen T1–T4 (konventionell, Direktsaat, reduzierter Input, biologisch) × Wiederholungen R1–R6; Fruchtfolge Mais–Soja–Weizen, seit 1993 alle Parzellen in derselben Phase → **Mais nur jedes 3. Jahr**.
- **295 gültige Mais-Parzellen-Jahre** (14 Mais-Jahre 1989–2023). In der HLS-Zeit: **2014, 2017, 2020, 2023 = 96** (2014 nur Landsat-8-Anteil von HLS).
- Mittlerer Maisertrag (kg/ha): 2014 8888 · 2017 7050 · 2020 8027 · 2023 9334.
- Parzellengröße 0,90–0,93 ha (Shapefile `plot_polygons_mainsite`, NAD83 / UTM 16N, Stand 2007).
- Messung: Mähdrescher mit GPS-Ertragsmonitor + Wiegewagen. **Bis 2016 nur Osthälfte der Parzelle geerntet, ab 2017 ganze Parzelle.**
- Einheit: bu/A und kg/ha, laut Metadaten 15,5 % Feuchte (56 lb/bu). ⚠ Korrekturnotiz von 2003: ab 2001 Basis 15 % → Unterschied 0,6 %. Umrechnung: `kg_ha / 1000` (bei 15-%-Basis × 1,0059).
- Seit 2019 Blühstreifen in T3/T4 → zwei Ertragswerte (`crop_only`, `whole_plot`); für Satellitenmittel passt `whole_plot`.
- Bewässerung: keine.

### Tabellen 185 / 828 – georeferenzierte Ertragspunkte
- **185** (2001–2012): Länge/Breite, Ertrag bu/ac, Kultur, Feuchte, Jahr – **keine Parzellen-ID** (Zuordnung über Polygone). Mais 2005 (25 856 Punkte), 2008 (23 500), 2011 (34 784); 2002 fehlt. Feuchtebasis ungeprüft. Ausreißer bis 28 136 bu/ac.
- **828** (2013–2025, John Deere): `yield_bu_ac` = **Nassertrag**, mit Feuchte, Trockenmasseanteil, Behandlung/Wiederholung. Mais 2014 (31 347), 2017 (31 623), 2020 (21 779), 2023 (46 651); Median 1100–1950 Punkte je Parzelle.
- Abgleich mit Tabelle 51: umgerechnete Punktmittel = 0,87–1,01 × Tabelle-51-Wert (einzelne Parzellen 0,67–1,6) → **Ertragsmonitor nicht auf Wiegewagen kalibriert. Label = Tabelle 51; Punkte nur für Muster innerhalb der Parzelle.**

### Scale-up (Tabellen 145, 163, 254)
- 27 Praxisfelder, 2006–2012; **62 Mais-Feld-Jahre**; Felder 1,3–7,3 ha (Median 5,4 ha); `mt_ha` bei 15,5 %.
- Punkte (163) ohne Feld-ID, **keine öffentlichen Feldpolygone**; Mais-Punkte nur 2007, 2008, 2010–2012.
- Liegt komplett vor der HLS-Zeit → für Phase 1 nur mit Landsat 5/7 nutzbar (laut PLAN.md optional).

**Auffälligkeiten KBS:** Feuchtebasis 15 vs. 15,5 %; Bruch 2017 (Osthälfte → ganze Parzelle); unerklärtes Label „T21“; früher korrigierte kg/ha-Fehler (2005, 2009, 2011, 2014); 2020 neuer Mähdrescher, unvollständig; extreme Ausreißer in Punktdaten (2023 bis 232 422 bu/ac, 1320 Punkte ≤ 0).

---

## 4. USDA BARC (Beltsville, Maryland)

**Quelle:** Ag Data Commons, „USDA BARC Gridded Yield Data Archive, version 1“ – Dulaney, Anderson, Gao et al., **DOI 10.15482/USDA.ADC/28950746.v2** (Version 2, 2026-01-22). Artikel: https://doi.org/10.1002/agg2.20474.
**Lizenz:** U.S. Public Domain, keine Zugriffsbeschränkung.

**Dateien** (`data/raw/barc/`, MD5 gegen figshare-API geprüft):

| Datei | Größe | figshare-ID |
|---|---|---|
| 2014.zip | 27 MB | 55969259 |
| 2016.zip | 97 MB | 55969274 |
| 2017.zip | 84 MB | 55969265 |
| 2018.zip | 171 MB | 55969277 |
| 2019.zip | 90 MB | 55969268 |
| 2020.zip | 96 MB | 55969271 |
| 2021.zip | 107 MB | 55969262 |
| BARCFarmMgmt.zip | 11 MB | 61146922 |

Neu-Download: `curl -L -o <Datei> https://ndownloader.figshare.com/files/<ID>`; Metadaten: `https://api.figshare.com/v2/articles/28950746`.

**Inhalt:** je Jahr Rohpunkte (1A–C), Ausschlussmasken (2A/B), bereinigte Punkte (3A–C), **Block-Kriging-Ertrag 5 m × 5 m als GeoTIFF** (6A–C), Kriging-Fehler (7A–C). Kultur steht im Dateinamen (z. B. `CentralFarm_1_7_2014_CORN_clip`).
- 180 Kriging-Raster, davon **62 Mais-Feld-Jahre**: 2014: 10 · 2016: 10 · 2017: 5 · 2018: 4 · 2019: 11 · 2020: 10 · 2021: 12; ~33 Felder (Namenszuordnung näherungsweise); einige Felder mit 4–5 Mais-Jahren, viele nur 1–2.
- Feldgröße (Kriging-Fläche nach 7-m-Innenpuffer): 3,3–16,5 ha, Median 6,7 ha.
- KBS: UTM 18N / WGS84, 5 m. **Keine Feldpolygone** – Rasterumriss (bereits 7 m Innenpuffer) dient als Feldgrenze.
- Messung: Ertragsmonitor (Ag Leader), Bereinigung (Mais > 17,3 Mg/ha entfernt, nur volle Schneidwerksbreite, Nachbarschaftsprüfung), Block-Kriging.
- Einheit: `Yld_Vol_Dr` = bu/ac „trocken“ auf Standardfeuchte; aus Rohwerten abgeleitete Basis: **2014, 2019, 2020 = 14 %; 2016–2018, 2021 = 15 %** (nie 15,5 %). Umrechnung t/ha bei 15,5 %: × 0,06389 (14 %) bzw. × 0,06314 (15 %).
- Bewässerung: Bericht in allen Bewirtschaftungs-PDFs fehlerhaft → keine Information (vermutlich unbewässert, ungeprüft).

**Auffälligkeiten BARC:** 2017 CentralFarm 4-7 Mais-Raster in anderer Einheit (Mittel 3,3 – vermutlich Mg/ha); negative Kriging-Werte; Rastermittel teils deutlich unter Median der bereinigten Punkte; Feuchtebasis wechselt je Jahr; 17 Feld-Jahre mit Doppelkultur; inkonsistente Feld-IDs (z. B. „5-03C“ vs. „5-3A“, zusammengelegte Felder 2020); 2015 fehlt; Bewirtschaftungs-PDFs mit verschobenem Layout → Kultur besser aus Dateinamen.

---

## 5. Colorado – USDA-ARS Central Great Plains Research Station (Akron)

**Quelle:** Ag Data Commons, „Data from: Topographic position index predicts within-field yield variation in a dryland cereal production system“ – Poss, Hardy, Macdonald et al., **DOI 10.15482/USDA.ADC/28914434.v1**. **Lizenz:** CC0.

**Dateien** (`data/raw/colorado/`): `Modeling_data.csv` (721 Zeilen; figshare 54132527), `Data_dictionary.csv` (54132539), `Study_site_DEM.tif` (54132677), `colorado_adc_metadata.json`.

**Inhalt:** 2019–2022, Trockenfeldbau (keine Bewässerung); Fruchtfolgen Weizen–Mais–Hirse und Weizen–Brache; 18 Teilflächen à 2,6–4,3 ha.
- **10 Mais-Teilflächen-Jahre** (2019: 3 · 2020: 2 · 2021: 3 · 2022: 2); 2020 und 2022 mit vielen Nullerträgen (Ursache ungeprüft).
- Nur **Stichprobenpunkte** (UTM 13N, ~30 m Abstand, 10–26 je Teilflächen-Jahr), **keine Polygone**.
- `yield_kg_ha` bei **15,5 %** für Mais → t/ha = Wert / 1000.

**Auffälligkeiten:** Punktmittel ≠ Feldmittel; nur 10 Fälle; Pseudoreplikation (vom Datensatz selbst angemerkt). → **Ergänzung, keine Haupt-Label-Quelle.**

---

## 6. Mead, Nebraska (AmeriFlux US-Ne1, US-Ne2, US-Ne3)

- Standorte: https://ameriflux.lbl.gov/sites/siteinfo/US-Ne1 (Ne2, Ne3 analog); PI Andy Suyker (UNL). Datenpolitik CC-BY-4.0.
- Ne1: Kreisberegnung, Mais jedes Jahr 2001–2021, ab 2022 Mais–Soja; Ne2: bewässert, Mais–Soja; Ne3: **unbewässert**, Mais–Soja.
- BADM (BIF) nur über `https://ameriflux.lbl.gov/data/download-data/` → leitet anonym auf `/login/` um → **Konto nötig** (legt Projektinhaber an). Ob BIF Kornerträge enthält: ungeprüft.
- **Status: angefragt / Konto nötig.** Nächster Schritt: BIF für US-Ne1/2/3 laden; falls keine Erträge enthalten, PI um jährliche Kornerträge bitten.

---

## Zusammenfassung Ertrags-Datensatz (HLS-Zeit, ab 2013)

| Quelle | Mais-Feld-Jahre | Jahre | Grenzen | Feuchtebasis original |
|---|---|---|---|---|
| KBS MCSE | 96 (24 Parzellen × 4 Jahre) | 2014, 2017, 2020, 2023 | Shapefile | 15,5 % (evtl. 15 %) |
| BARC | 62 (~33 Felder) | 2014, 2016–2021 | Rasterumriss | 14 % / 15 % je Jahr |
| Colorado | 10 | 2019–2022 | keine (Punkte) | 15,5 % |
| **Summe** | **168** | | | |

Folgerung für das Schema (`groundtruth.py`): Spalte `moisture_basis` je Feld-Jahr, Umrechnung aller Erträge auf 15,5 %.

---

## 7. CY-Bench (Regionalerträge + Prädiktoren, EU)

**Quelle:** Zenodo, CY-Bench **v1.10** (2025-10-06), **DOI 10.5281/zenodo.17279151** (Concept-DOI 10.5281/zenodo.11502142); Artikel: Kallenberg et al. 2026, ESSD 18, 3997–4018, doi:10.5194/essd-18-3997-2026; Code: github.com/WUR-AI/AgML-CY-Bench. **Lizenz:** EUPL-1.2.

**Dateien** (`data/raw/cybench/`):
- `cybench-data/maize/<CC>/*.csv` – **nur Mais, 23 EU-Länder** (207 Dateien, 834 MB entpackt), jede Datei per CRC32 + Größe gegen das Zip-Verzeichnis geprüft. Das Gesamtarchiv `cybench-data.zip` (6,23 GB, md5 `8ec510982f396469eca25a4f0fa8632e`) wurde nicht vollständig geladen (Zenodo drosselte auf ~100 KB/s, HTTP 429); stattdessen Einzeldateien per HTTP-Range-Request.
- `polygons.zip` (105 MB), `centroids.zip` (0,3 MB), `zenodo_record_17279151.json`, `cybench-data_v1.10_zip_listing.txt`.

**Neu-Download:**
```bash
curl -L -C - -o data/raw/cybench/cybench-data.zip "https://zenodo.org/api/records/17279151/files/cybench-data.zip/content"
# md5 prüfen, dann nur Mais entpacken:
unzip data/raw/cybench/cybench-data.zip "cybench-data/maize/*" -d data/raw/cybench/
```

**Österreich in CY-Bench:**
- Ebene **NUTS-2 = 9 Bundesländer** (AT11 … AT34).
- Ertrag **1975–2020** (414 Region-Jahre, lückenlos) – **keine Werte nach 2020**. Einheit t/ha. Herkunft: JRC-harmonisierte EU-Regionalstatistik (Quelle für AT: Statistik Austria); 2018–2020 identisch mit Statistik Austria.
- Prädiktoren (keine NaN): meteo (AgERA5, täglich, 2001–2023: tmin, tmax, tavg, prec, rad, et0, vpd, cwb), soil_moisture (GLDAS ssm/rsm, täglich ab 2003-02), fpar (JRC, Dekaden 2001–2023), ndvi (MOD09CMG, ~8-tägig, mit Lücken), soil (WISE: awc, bulk_density, drainage_class), crop_calendar (WorldCereal sos/eos, statisch), crop_mask (statisch), location.
- Nutzbares AT-Trainingsfenster: 2001–2020 (mit Bodenfeuchte 2003–2020); 2021–2023 ergänzbar mit Statistik-Austria-Erträgen (Prädiktoren vorhanden).

**Andere EU-Länder mit Mais (Ertrag > 0):** BE, BG, CZ, DE (372 NUTS-3-Regionen, 9 095 Region-Jahre), DK, EL, ES, FR, HR, HU, IT, LT, NL, PL, PT, RO, SE, SK – gemischt NUTS-2/NUTS-3; Ertragsjahre jeweils bis 2020 (DE bis 2021). EE, FI, IE, LV enthalten **nur Nullerträge**; einzelne Nullen auch in EL, FR, LT, PT u. a. Slowenien fehlt.

**Publizierte Baseline AT-Mais:** R² = 0,13 (SklearnRF, Median über LOYO-Folds) – **nicht im ESSD-Artikel**, sondern in `results_baselines/tables/tables_march2025_v1_8.md` des Code-Repos, berechnet auf **Datenversion v1.8**. Ältere Tabellen (2024) zeigten −0,20 → versionsabhängig. Naive Baseline (AverageYieldModel) −0,02.

**Auffälligkeiten:** AT-Erträge enden 2020 (Dürrejahre 2022/2024 fehlen); Wien, Sbg, Tirol, Vbg mit < 250 ha Mais zählen in LOYO-Metriken gleich viel → ausschließen oder flächengewichten; Länder mit Nullerträgen filtern; NUTS-2/3-Mischung (Skalenunterschied beim Transfer); JRC-Imputations-Flags fehlen in den CSVs; AT-2013-Regionalwerte auffällig rund (vermutlich Schätzungen an der Quelle); Kulturmaske und Anbaukalender statisch.

**Status: ✅ verfügbar.**

---

## 8. Statistik Austria – Körnermais je Bundesland

**Quellen:**
- Statistik Austria, Feldfruchternte: https://www.statistik.at/statistiken/land-und-forstwirtschaft/pflanzenbau/ackerbau-dauergruenland – Tabellen `Feldfr<Jahr>endg.ods` (Bundesland × Kultur: Fläche ha, Ernte t, Ertrag **dt/ha**), `Feldfr2026vorl.ods` (vorläufig, Stand Sept. 2026), `Feldfr1975bis2025.ods` (nur Österreich), Schnellberichte 2019–2025, `Statistik_der_Landwirtschaft_2018.pdf`, Methodenbeschreibung `std_r_ernteerhebung.pdf`.
- Eurostat: `apro_cpshr` (NUTS-2, Fläche + Produktion 2010–2024, Stand 2026-09-08), `apro_cpnh1` (national inkl. Feuchte, Stand 2026-09-28).
- **Lizenz/Nutzung:** Statistik Austria – Weiterverwendung mit Quellenangabe „STATISTIK AUSTRIA“ (bei Bearbeitung Hinweis); Eurostat – Weiterverwendung mit Quellenangabe (Beschluss 2011/833/EU).

**Dateien:** Originale unter `data/raw/statistik_austria/` (ODS, PDF, `eurostat/*.json`); erzeugt: **`data/raw/stat_at_maize.csv`** (`year, bundesland, area_ha, yield_t_ha, production_t, source, status, notes`; 170 Zeilen = 2010–2026 × 9 Länder + Österreich).

**Neu-Download:**
```bash
for y in 2019 2020 2021 2022 2023 2024 2025; do curl -sSLO https://www.statistik.at/fileadmin/pages/127/Feldfr${y}endg.ods; done
curl -sSLO https://www.statistik.at/fileadmin/pages/127/Feldfr2026vorl.ods
curl -sSL -o apro_cpshr_C1500_AT_nuts2.json "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpshr?crops=C1500&geo=AT11&geo=AT12&geo=AT13&geo=AT21&geo=AT22&geo=AT31&geo=AT32&geo=AT33&geo=AT34&format=JSON&lang=EN"
```
Erzeugung der CSV aus den Originalen: `python -m croptransfer.regional_stats` (Modul `src/croptransfer/regional_stats.py`, Tests in `tests/test_regional_stats.py`).

**Inhalt / Herkunft je Zeitraum:**
- **2019–2025:** Statistik Austria, endgültig (dt/ha ÷ 10 → t/ha). Keine Revisionen nach „endgültig“ festgestellt (Vergleich der Folgejahrestabellen 2018–2024).
- **2026:** vorläufig (Spalte `status`) – nicht für Auswertungen verwenden, bevor endgültig.
- **2010–2018 Bundesländer:** Eurostat `apro_cpshr` (Fläche/Produktion auf 10 gerundet, Ertrag = Produktion / Fläche); Zeilen mit Fläche < 1000 ha (**Sbg, Tirol, Vbg, Wien**) sind durch Rundung stark verzerrt und in `notes` markiert → dort CY-Bench-Werte verwenden.
- **2010–2018 Österreich:** ebenfalls `apro_cpshr` (geo = AT). Gegenprobe: Abweichung zur ersten explorativen Extraktion (mit `apro_cpnh1`) ≤ 0,005 t/ha.

| Jahr | Bgld | Ktn | NÖ | OÖ | Stmk | Österreich |
|---|---|---|---|---|---|---|
| 2018 | 8,82 | 10,08 | 9,44 | 10,56 | 11,55 | 10,15 |
| 2019 | 8,46 | 11,02 | 9,70 | 10,82 | 11,90 | 10,42 |
| 2020 | 9,45 | 12,34 | 10,36 | 11,83 | 12,97 | 11,35 |
| 2021 | 8,76 | 11,73 | 10,99 | 11,52 | 11,98 | 11,16 |
| 2022 | 6,81 | 8,97 | 8,56 | 11,65 | 11,49 | 9,82 |
| 2023 | 8,79 | 10,93 | 8,40 | 9,81 | 12,54 | 9,93 |
| 2024 | 7,47 | 11,19 | 8,65 | 10,55 | 11,67 | 9,90 |
| 2025 | 9,73 | 8,90 | 10,54 | 12,17 | 12,19 | 11,14 |

(t/ha; 2010–2017 und 2026 vorläufig siehe CSV.)

**Methodik / Definition:**
- **Feuchte 14 %** (laut Eurostat `apro_cpnh1` für AT-Körnermais in allen Jahren; Statistik Austria nennt nur „definierten Feuchtigkeitsgehalt“). Für YAS (Verhältnis) unerheblich; bei absolutem Vergleich mit US-Daten (15,5 %) umrechnen.
- Erträge aus der AMA-Ertragserhebung (Verwiegung auf repräsentativen INVEKOS-Kontrollschlägen), Flächen aus Mehrfachanträgen.
- Definition „Körnermais inkl. CCM und Saatmais“; Saatmais (~9–11 Tsd. ha) pauschal mit 35 dt/ha bewertet → senkt das Mittel leicht.

**Feinere Ebene (Bezirke):** **nicht veröffentlicht** – nur als Sonderauswertung auf Anfrage; Bezirkswerte sind ohnehin nicht gemessen, sondern über Ernteberichterstatter geschätzt. STATcube (`depflfeld`) am Abruftag überlastet → Inhalt ungeprüft, später erneut versuchen. OGD-Katalog enthält keinen Feldfrucht-Datensatz. LK Steiermark: nur Landessummen.

**Auffälligkeiten:** Einheit dt/ha in den Quellen; 2010–2018 nur gerundete Eurostat-Werte; Flächenkorrekturen 2024 (Hochwasser) und 2025 (Umwidmung Körner-/Silomais, Stmk/Ktn Richtung Silo); 2026 vorläufig mit extrem niedrigen Erträgen; Kleinst-Maisflächen in Wien/Sbg/Tirol/Vbg.

**Status: ⚠️ teilweise** (Bundesland 2010–2026 vorhanden, 2010–2018 nur über Eurostat; Bezirksebene nicht verfügbar).

<!-- INVEKOS und Verwaltungsgrenzen folgen. -->

---

## 9. One Acre Fund – Maize management and yield of smallholder farmers in Sub-Saharan Africa 2016–2022

**Quelle:** Zenodo, Concept-DOI 10.5281/zenodo.11115815 → einzige Version **10.5281/zenodo.11122388** (2024-05-06). Zugehöriger Artikel: Aramburu-Merlos et al. 2024, *Nature Communications* 15, doi:10.1038/s41467-024-48859-0 (Open Access, PMC11130130). **Lizenz:** CC BY 4.0 (Quellenangabe: One Acre Fund / Aramburu-Merlos et al.).

**Dateien** (`data/raw/one_acre_fund/`): `One_Acre_Fund_MEL_maize_survey_data_2016-2022.csv` (5 637 560 Byte, md5 `7856ff0693dce26817623bc73ac5fa7b` – geprüft gegen Zenodo), `zenodo_record_11115815.json` (Metadaten inkl. Variablenbeschreibung).

**Neu-Download:**
```bash
curl -L -o One_Acre_Fund_MEL_maize_survey_data_2016-2022.csv "https://zenodo.org/api/records/11122388/files/One_Acre_Fund_MEL_maize_survey_data_2016-2022.csv/content"
curl -L -o zenodo_record_11115815.json https://zenodo.org/api/records/11115815
```
Kennzahlen reproduzierbar mit `python -m croptransfer.one_acre_fund` (Modul `src/croptransfer/one_acre_fund.py`, Tests `tests/test_one_acre_fund.py`). **Satellitendaten wurden nicht angesehen** (Vorab-Filter, PLAN.md §3.1).

**Inhalt:** 14 773 Zeilen × 53 Spalten, je Zeile ein Feld in einer Saison (keine Feld-ID).
- Spaltengruppen: Ort/Zeit (`year, country, iso, season, cz` = GYGA-Klimazone, `strat` = Klimazone×Saison-Gruppe, `lon, lat`); Umwelt aus Fremdquellen (`avg_season_gdd/ai/tavg`, `season_prec`, `season_prec_1..3` aus CHIRP, `elev`, `twi`, `soil_rzpawhc, soil_clay, soil_pH, soil_orgC, soil_ECEC`); Bewirtschaftung (`plant_date, harvest_date, plant_date_dev, plant_doy, pl_m2, row_spacing, hybrid, hyb_type, hyb_mat, hyb_yor, hyb_tol_*`, `N/P/K_kg_ha, compost, comp_kg_ha, manure, fert_in_hole, lime_kg_ha, weeding, pesticide`); Schäden (`disease, pest, striga, water_excess`); Ziel `yield_kg_ha`.
- Felder je Land und Jahr (`year` = Erntejahr der Saison):

  | Land | 2016 | 2017 | 2018 | 2019 | 2020 | 2022 | Summe |
  |---|---|---|---|---|---|---|---|
  | Kenia | 1111 | 921 | 1180 | 1755 | 2291 | – | 7258 |
  | Tansania | 1184 | – | 985 | 1381 | 160 | – | 3710 |
  | Ruanda (2 Saisonen) | – | – | 556 | 608 | 916 | – | 2080 |
  | Sambia | – | – | 466 | 395 | – | – | 861 |
  | Burundi | 142 | 173 | – | 194 | 131 | – | 640 |
  | Nigeria | – | – | – | – | – | 115 | 115 |
  | Uganda | – | – | – | – | 109 | – | 109 |

  **2021 fehlt ganz**, 2022 nur Nigeria.
- Ertrag `yield_kg_ha`: Median 2714 kg/ha (0–11 139); **263 Nullerträge** (Kenia 144, Ruanda 61, Tansania 58).
- **Feuchtebasis: nicht angegeben** – weder in der CSV noch auf Zenodo noch im Artikel (dort nennt nur ein separater Sortenversuch in Ruanda „standard grain moisture content (15 %)“). Annahme bis zur Klärung: unbekannt, vermutlich 15 %. Für RY_nb (Verhältnis innerhalb Region-Jahr) unerheblich, für absolute Erträge nicht.
- **Feldgröße: nicht im Datensatz.** Beschreibung und Artikel erwähnen gemeldete/gemessene Feldgrößen, die CSV enthält aber keine Spalte dafür (nur daraus abgeleitete Raten je ha).
- **GPS-Genauigkeit: keine Spalte.** Die Bodenwerte (WISE/iSDA) wurden laut Beschreibung nur bei feldgenauer Position abgefragt → `soil_*` vorhanden = exakte Position: **10 332 Felder (69,9 %)**, passt zu den 70 % der Beschreibung. Alle fünf Bodenspalten fehlen immer gemeinsam.
- **Koordinaten auf 3 Nachkommastellen gerundet** (0,001° ≈ 111 m) → Lagefehler bis ±56 m je Achse, auch bei „exakten“ Positionen. 1254 exakte Felder teilen sich Punkt + Jahr + Saison mit anderen (bis zu 12 Felder an einem Punkt).
- Exakte Positionen je Jahr: Kenia 1084/921/1175/1739/2151 (2016–2020), Tansania 655/894/159 (2018–2020), Sambia 304/395, Ruanda 130/363 (2019/20), Burundi 138 (2017), Nigeria 115, Uganda 109 → **68 % der exakten Felder liegen in Kenia**.
- Aussaatdatum bei 11 179, Erntedatum bei 10 285 Feldern; frühestes Aussaatdatum 2015-03-25 (Saison 2016); bei 3296 Feldern liegt die Aussaat im Vorjahr von `year` (Saisonen über den Jahreswechsel: Tansania, Sambia, Burundi, Ruanda Saison A).
- **Kodierung der Schäden:** nur vier Spalten, alle von Landwirt:innen gemeldet, binär. `pest` und `disease` fassen laut Beschreibung viele Einzelursachen zusammen – **auch „drought“ wurde in `pest`/`disease` einsortiert**; **Hagel hat keine eigene Spalte** (nur im Fließtext erwähnt). `striga` ist bei 12 249 Feldern leer. Anteil 0,00 in ganzen Land-Jahren (z. B. `pest` Kenia/Tansania/Burundi 2016, `water_excess` in Tansania, Sambia, Burundi, Nigeria) → dort wurde die Frage vermutlich **nicht gestellt**, „False“ heißt dann „unbekannt“ (Tabelle `damage_likely_not_asked` im Modul).
- Gruppen für RY_nb: keine Bezirksspalte; feinste Gruppierung `cz` × `season` × `year`. Unter den exakten Feldern haben 76 solche Gruppen ≥ 11 Felder (10 204 Felder).

**Vorab-Filter PLAN.md §3.1:**

| Schritt | Felder |
|---|---|
| alle | 14 773 |
| exakte GPS-Position (Proxy: Bodenwerte vorhanden) | 10 332 |
| gemeldete Feldgröße ≥ 0,5 ha | **nicht anwendbar – Spalte fehlt** |

**Status: ⚠️ verfügbar, aber der geplante Filter (Feldgröße ≥ 0,5 ha, 20-m-Kreis um exakte Position) ist mit den veröffentlichten Daten nicht umsetzbar** (keine Feldgröße, Koordinaten auf ~111 m gerundet). Entscheidung des Projektinhabers nötig (Optionen in `reports/data_review/phase0_data_access.md`, Abschnitt „Neue Quellen“).

## 10. YieldSAT

**Quelle:** https://yieldsat.github.io/ (Code auf GitHub). **Zugang:** Anfrageformular (Projektinhaber, siehe `ANFRAGEN.md`). **Lizenz:** auf der Seite nicht angegeben.
**Inhalt laut Seite:** 2.173 Felder (AR 751, BR 551, UY 572, DE 299), 2016–2024; **Mais nur AR (185) und BR (118)**; Mähdrescher mit GPS-Ertragsmonitor (Nassertrag, Feuchte → Trockenertrag), > 12 Mio. Ertragspunkte, gerastert auf 10 m passend zu Sentinel-2; Sentinel-2 L2A (13 Bänder + SCL), ERA5-Land, SoilGrids 2.0, SRTM. Mais-Jahre pro Feld: unbekannt.
**Status: ⏳ Zugang beantragt.**

## 11. SSURGO (USDA NRCS Soil Survey Geographic Database)

**Zugang:** Soil Data Access (SDA), REST-Endpunkt `https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest` (POST, JSON `{"query": <SQL>, "format": "JSON+COLUMNNAME"}`), ohne Login. **Lizenz:** U.S. Public Domain. Stand der abgefragten Bodenkarten (`sacatalog.saverest`): MI077 2026-08-27, MD033 2026-09-13.

**Exakte Tabellen/Spalten:**

| Größe | Tabelle | Filter | Spalte | Einheit | Ebene |
|---|---|---|---|---|---|
| Mais-Ertragsschätzung ohne Bewässerung | `cocropyld` | `cropname = 'Corn'` | `nonirryield_r` (+ `_l`, `_h`; bewässert: `irryield_r`) | `yldunits` = `Bu` (bu/ac) | Komponente (`cokey`) |
| NCCPI Mais | `cointerp` | `mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)'` und `rulename = 'NCCPI - NCCPI Corn Submodel (I)'` | `interphr` | 0–1 | Komponente (`cokey`) |
| Anteil der Komponente | `component` | – | `comppct_r`, `majcompflag` | % | Komponente → `mukey` |
| Geometrie | `mupolygon` | `STIntersects` mit Feldpolygon (WGS84) | `mupolygongeo` | – | Map-Unit-Polygon |

Hinweise: Die Corn-Teilregel heißt in SDA „(I)“, nicht „(II)“ (nur Cotton/Small Grains haben „(II)“). Die Gesamt-NCCPI steht unter `rulename` = `mrulename`. Die alte Map-Unit-Tabelle `mucropyld` enthält für die Testflächen keine Mais-Werte.

**Aggregation** (`src/croptransfer/soil_ssurgo.py`, Tests `tests/test_soil_ssurgo.py`): Komponentenwerte mit `comppct_r` gewichtet je Map-Unit (Komponenten ohne Wert fallen heraus), dann flächengewichtet über die Map-Units im Feld. Zusätzlich `<wert>_comp_pct` = Anteil der Feldfläche, deren Bodenkomponenten einen Wert haben; liegt er unter **50 %** (`config.yaml: ssurgo.min_comp_pct_with_value`), ist der Feldwert NaN.

**Testabfrage** (`python -m croptransfer.soil_ssurgo`, ~50 s):

| Feld | Map-Units | Mais-Ertragsschätzung (bu/ac) | Abdeckung | NCCPI Mais | Abdeckung |
|---|---|---|---|---|---|
| KBS MCSE T1–T4 R1–R6 (alle 24 Parzellen) | 1 (`187069` KaB, Kalamazoo loam 2–6 %) | **NaN** (Wert 120 nur bei Nebenkomponente Sleeth, 1 %) | 1 % | **0,664** (alle Parzellen identisch) | 100 % |
| BARC CentralFarm 1-7 (Rasterumriss 2014) | 5 (Russett-Christiana-Komplexe u. a., MD033) | 116,5 | 76 % | 0,507 | 77 % |

**Abdeckung der Mais-Ertragsschätzung** (Hauptkomponenten mit `Corn`-Wert / alle Hauptkomponenten, SDA-Abfrage je Bodenkarte): MI077 Kalamazoo Co. (KBS) **10/50**, MD033 Prince George's Co. (BARC) 222/362, CO121 Washington Co. (Akron) 44/110, NE155 Saunders Co. (Mead) 37/65. NCCPI Mais ist für alle Hauptkomponenten vorhanden.

**Auffälligkeiten:** Mais-Ertragsschätzung lückenhaft (KBS komplett ohne); alle KBS-Parzellen liegen in **einer** Map-Unit → SSURGO unterscheidet die KBS-Parzellen nicht; Werte sind Schätzungen von Bodenkundler:innen, keine Messungen → nur Merkmal/Analyse (nur US), nie Label. Colorado (keine Polygone) und Mead (Daten fehlen) noch nicht abgefragt.

**Status: ✅ verfügbar** (NCCPI Mais vollständig; Mais-Ertragsschätzung ⚠️ lückenhaft).

## 12. Lokale Testerträge Österreich (nur nach dem Freeze auswerten)

**Österreich-Regel:** Die Werte wurden nur gesammelt und abgeschrieben. Es gab keine Auswertung, keine Anomalien und keine Vergleiche. Hier stehen deshalb nur Bestandszahlen, keine Ertragszahlen.

**Ziel-Datei:** `data/raw/at_trials.csv` – **150 Zeilen** (Steiermark 44, Oberösterreich 106), Spalten `site, bundesland, lat, lon, loc_precision, year, yield_t_ha, moisture_basis, trial_type, variant, sowing_date, harvest_date, source_pdf, page, notes`. Erzeugung: eine abgeschriebene Roh-CSV je Quelle (`data/raw/at_trials/hatzendorf.csv`, `data/raw/at_trials/lko_ooe.csv`), zusammengeführt und geprüft mit `python -m croptransfer.at_trials` (Schema, Einheiten, ISO-Daten, eindeutiger Schlüssel `site, year, trial_type, variant`; Tests `tests/test_at_trials.py`). Abgeschrieben haben KI-Unteragenten aus `pdftotext -layout`. Stichproben (je 2–3 Zeilen) wurden gegen die PDF-Seiten geprüft.

**Konventionen:**
- `yield_t_ha` steht auf der **berichteten** Feuchtebasis (nicht umgerechnet). `moisture_basis` = 0.14, wenn angegeben, sonst leer.
- Je Standort-Jahr und Versuch gibt es eine Zeile „Versuchsmittel“/„Standortmittel“ (Mittel aller Varianten bzw. Sorten), bei LK-OÖ-Versuchen mit Reifegruppen eine Zeile je Reifegruppe. Eine ortsübliche Standard-Variante ist nur eingetragen, wo der Bericht sie ausdrücklich nennt (Düngealternativen 2024 Wagna/Kalsdorf).
- Hat der Bericht kein Mittel genannt, wurde es aus der vollständigen Tabelle berechnet und in `notes` als „berechnet aus n …“ markiert (Stmk 32, OÖ 21 Zeilen; Stmk teils aus ganzzahligen Diagrammbeschriftungen).
- `lat/lon` sind leer und `loc_precision = municipality`, weil kein Bericht Koordinaten nennt (Standortkoordinaten fragt der Projektinhaber an, `ANFRAGEN.md` #4).

### 12a. Versuchsstation für Pflanzenbau Hatzendorf (Land Steiermark)
- **Quelle:** jährliche Versuchsberichte auf https://www.fachschulen.steiermark.at (`/cms/dokumente/…`), Berichtsjahre **2013–2019 und 2022–2025** als Gesamtbericht, dazu Einzelkapitel 2022/2024 (Körnermais-Düngung Wagna und Kalsdorf, Düngealternativen). Der als „Versuchsbericht 2020“ verlinkte Bericht enthält das Versuchsjahr 2019. Die Datei „Wagna 2024“ der Website ist byte-identisch mit der von 2023.
- **2012, 2020, 2021:** Auf der Website gibt es keinen Gesamtbericht. Einzelkapitel stammen aus dem Web-Archiv der früheren Seite versuchsreferat.com (`web.archive.org/web/<Zeitstempel>id_/…`). Die archivierten Gesamtberichte 2020/2021 sind bei 1 MB abgeschnitten und nicht lesbar.
- **Dateien:** `data/raw/at_trials/hatzendorf/` (27 PDFs, je eine `.txt` aus `pdftotext -layout`).
- **Bestand (44 Zeilen):**

  | Standort | Zeilen | Versuche |
  |---|---|---|
  | Wagna | 23 | N-Düngung 2013–2024; Großparzellen-Fruchtfolgeversuch 2012, 2015–2019, 2021; Düngealternativen 2022–2024 |
  | Kalsdorf bei Ilz | 14 | N-Düngung 2013–2016, 2018, 2021, 2022, 2024; Grubber/Pflug 2015, 2017, 2019; Düngealternativen 2022, 2024 |
  | Hatzendorf (Gütl, Bodenbearbeitung) | 3 | 2019, 2023, 2024 |
  | Unterhatzendorf, Wagendorf, Wollsdorf, Kühwiesen | je 1 | Gülle 2017, Düngung 2013, **Mischkultur mit Käferbohne** 2016/2017 |

- **Feuchte:** 41 Zeilen mit 14 % („14 % Feuchtigkeit“ bzw. „86 % TM“), 3 ohne Angabe.
- **Lücken:**
  - Hirse statt Mais: Kalsdorf 2017 und 2019, Wagendorf 2014.
  - Nur als Diagrammbild: Kalsdorf 2020, Gütl 2025, Wagna 2007–2012.
  - Ohne Zahlen: Wagna 2025, Kalsdorf 2025.
  - Vom Bericht ausgeschlossen: Kalsdorf 2023.
  - Nur kostenbereinigte Erträge: Wagendorf 2008–2012/2015, Kalkstickstoff-Versuch 2014.
- **Auffälligkeiten:**
  - Einzelne Jahreszuordnungen sind abgeleitet (Kalsdorf 2013; Großparzellen 2017–2019 über Mehrjahresmittel; Wagna 2014 aus dem Diagramm-Layout).
  - Wagna 2022 bekam laut Bericht 30 kg N zu viel.
  - Die Mischkultur-Zeilen (Mais nur Stützfrucht) sind an `trial_type = mischkultur_duengung` erkennbar. Ob sie in den Test kommen, wird im Österreich-Testprotokoll **vor** dem Freeze festgelegt.

### 12b. Landwirtschaftskammer Oberösterreich – Körnermais-Sorten- und Praxisversuche
- **Quellen:**
  - Jahresberichte „Versuchsergebnisse“ der Boden.Wasser.Schutz.Beratung mit der LK OÖ, Abt. Pflanzenbau, **2013–2025** (https://www.bwsb.at/versuchsberichte+2400+1789152, Download `media.php?filename=download%3D…`).
  - Einzelberichte **2023–2026** aus dem Versuchsportal https://ooe.lko.at/pflanzenbauliche-versuchsberichte+2500++2931746, PDF-Muster `https://ooe.lko.at/src_pages/versuchsberichte_pdfs/<Jahr>/<JJ>_<Kategorie>_<K|B>_<SV|PV|AV>_<Ort>_<PLZ>_<Bezirk>_EJ.pdf`.
  - Ältere Jahre fehlen im Portal (HTTP 410). Das Verzeichnis auf cms2.lko.at ist gesperrt (403).
- **Dateien:** `data/raw/at_trials/lko_ooe/` (74 PDFs, ~102 MB: 15 Jahresberichte, 59 Portal-PDFs).
- **Bestand (106 Zeilen, 2013–2026):** Walding 35, Mauthausen 22 (je Reifegruppe), Linden/Steinerkirchen an der Traun 13, Bad Wimsbach-Neydharting 11, Katzenberg/Kirchdorf am Inn 10, Leonding/Hörsching 5, Geinberg 3, Aistersheim 2, Eberstalzell, Dietach, Enns, Pasching und Nußbach je 1. `trial_type`: sorten 71, praxisversuch_sorten 29, sorten_bio 5, sorten_verfahrenstechnik 1.
- **Feuchte:** 79 Zeilen mit 14 % („Trockenertrag bei 14 % H2O“), 27 ohne Angabe (Übersichten 2020–2022, Geinberg 2026).
- **Lücken:** 2019 (Körnermais-Übersicht nur als Bild), 2010–2012 (nicht geladen), Walding 2013 (Überflutung, nicht ausgewertet).
- **Auffälligkeiten:**
  - **Ortsnamen uneinheitlich** (z. B. 6 Schreibweisen für Linden/Steinerkirchen) → vor jeder Verknüpfung vereinheitlichen.
  - Sortenwerte 2014–2017 sind „interpoliert“ (auf eine Standardsorte bezogen).
  - Mehrfach widersprechen sich Fließtext und Tabellenmittel. Übernommen wurde das Tabellenmittel, der abweichende Wert steht in `notes`.
  - Bad Wimsbach 2025/26: Eingetragen ist der Parzellenertrag. Die Übersichten verwenden den „Praxisertrag (−10 %)“.
  - Werte aus Niederösterreich in den Übersichten wurden nicht übernommen.

**Status: ✅ gesammelt** (150 Standort-Versuch-Jahre). ⚠️ Es fehlen Koordinaten, Ortsnamen sind nicht vereinheitlicht, die Feuchte ist teils unbekannt. **Auswertung erst nach dem Freeze.**

## 13. Bodenklimazahl (Finanzbodenschätzung, Österreich)

Verhältniszahl 1–100 für die natürliche Ertragsfähigkeit; im Kataster je Grundstück abfragbar, in GIS Steiermark als Layer vorhanden (in Landesplanungen verwendet), **offener Massendownload nicht gefunden**. eBOD (bodenkarte.at) frei einsehbar, kein Rohdatenexport.
**Status: ⏳ optional, Anfrage beim Projektinhaber.**

