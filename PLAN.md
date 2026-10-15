# CropTransfer AT – Arbeitsplan

> Früherkennung von Stress und Ertragsverlust auf einzelnen Maisfeldern aus Satelliten-Zeitreihen: **gelernt an Feldern mit gemessenem Ertrag** (USA, viele Jahre), **übertragen auf die Steiermark**, abgesichert durch ein selbstüberwachtes Feldmodell und offizielle österreichische Regionalerträge.

Dieser Plan ist so geschrieben, dass er Schritt für Schritt abgearbeitet werden kann. Jede Phase hat: **Ziel → Aufgaben → Ergebnis (Deliverable) → Abnahmekriterium**. Alle technischen Entscheidungen sind in Abschnitt 2 festgelegt; Abweichungen werden in `DECISIONS.md` begründet. Wie gearbeitet wird, regelt `AGENTS.md`.

---

## 0. Kernidee

1. Ein Maisfeld „sieht man“ im Satelliten als **Kurve über die Saison** (NDVI, NDRE, Wassergehalt …) – gesund = grün, dicht, chlorophyllreich; Stress = Kurve bleibt flach oder fällt früh ab.
2. **Zuerst wird gelernt, was die Kurve über den Ertrag verrät** – an Feldern, deren Ertrag über viele Jahre mit dem Mähdrescher gemessen wurde (USA: Kellogg Biological Station, USDA Beltsville, Colorado, ggf. Mead). Wenige Felder × viele Jahre: Von Jahr zu Jahr ändern sich vor allem Wetter und Stress – genau das Signal, das wir brauchen. Getestet wird immer mit **ganzen ausgelassenen Feldern und Jahren**.
3. In Österreich gibt es keine öffentlichen Feld-Erträge. Deshalb zwei Wege:
   - **Transfer:** Das an US-Feldern gelernte Ertragsmodell wird auf steirische INVEKOS-Maisfelder angewendet (Zero-Shot).
   - **Selbstüberwacht:** Ein Feldmodell sagt aus Kurve + Wetter + Boden bis zu einem Stichtag voraus, wie stark der Bestand zur Kornfüllung sein wird; die „richtige Antwort“ liefern spätere Satellitenbilder vergangener Jahre. Welche Satelliten-Zielgröße dafür taugt, entscheidet der Ertragsbezug aus Schritt 2.
4. Beide werden gegen **offizielle österreichische Regionalerträge** geprüft (feinste verfügbare Ebene) und – falls beschaffbar – gegen **Erträge österreichischer Landwirt:innen**. Ein Regionalmodell (CY-Bench) testet parallel den Transfer andere EU-Länder → Österreich.

> **Wichtig:** Trainiert wird **pro Feld** – nichts wird dafür gemittelt. Lokale Unterschiede (Dürre im einen Tal, nicht im Nachbartal) stecken direkt in den Feld-Daten. Regionale Mittelwerte dienen in Österreich nur der **Kontrolle**.

---

## 1. Forschungsfragen

| ID | Frage | Haupt-Experiment | Phase |
|---|---|---|---|
| **F0** | Wie gut sagt die Satelliten-Saisonkurve den **gemessenen Feldertrag** voraus – und ab welchem Zeitpunkt der Saison erkennt man gefährdete Felder? | Ertrags-Datensatz USA, Test mit ausgelassenen Feldern + Jahren | 1 |
| **F1** | Wie früh lässt sich die Bestandsstärke eines steirischen Maisfeldes zur Kornfüllung vorhersagen? | Frühwarnkurve, selbstüberwachtes Feldmodell | 7 |
| **F2** | Welche Datenquellen tragen wie viel bei (optisch, Radar, Wetter, Bodenfeuchte, Boden, Feldhistorie)? | Ablation | 8 |
| **F3** | Sagen die Vorhersagen echte Ertragsverluste in Österreich voraus – regional und (wo Daten vorhanden) pro Feld? Ab welchem Stichtag? | Vorhersage ↔ Ertrag je Stichtag | 9 |
| **F4** | Transfer ohne Labels aus der Zielregion: **(a)** EU → AT regional (CY-Bench), **(b)** Steiermark → andere Bundesländer, **(c)** US-Feld-Ertragsmodell → Österreich. Wie viele lokale Daten braucht es (Few-Shot)? | Zero-Shot + Few-Shot | 4, 9 |

**Ehrliche Grenzen (stehen so in der Doku):** Der Zusammenhang Kurve → Ertrag wird an US-Feldern gemessen; ob er in Österreich gilt, ist selbst eine Forschungsfrage (F4c) und wird nur so weit behauptet, wie die österreichischen Prüfungen es stützen.

---

## 2. Festgelegte technische Entscheidungen

| Thema | Entscheidung | Begründung | Später optional |
|---|---|---|---|
| **Ertrags-Datensatz (Feld-Labels)** | **KBS LTER** (MCSE-Parzellen + Scale-up, Mähdrescher 2012–2025), **USDA BARC** (40+ Felder, Ertragskarten 2014, 2016–2021), **Colorado-Trockenfarm** (18 Teilflächen, 2019–2022); **Mead US-Ne1/2/3** (2001–2024) nach Klärung der Ertragsdaten | offen, Mähdrescher-gemessen, viele Jahre pro Feld | Erträge österreichischer Landwirt:innen (V3), One Acre Fund |
| Region Österreich (Feldebene) | **Steiermark** | viel Körnermais, kaum Bewässerung, Hagel + Trockenstress | – |
| Region Österreich (Validierung) | **ganz Österreich, Stichprobe** | Steiermark allein = zu wenige Region-Jahre | – |
| Kultur | **nur Körnermais**; in Österreich Silomais ausgeschlossen | Silomais früh geerntet → verfälscht Spätsaison | Silomais als Vergleich |
| Jahre | Ertrags-Datensatz **2013–2025**; Österreich **2018–2025** | HLS ab 2013; stabile S2-Abdeckung AT ab 2018 | 2017 |
| Satellit lange Reihen | **HLS v2** (`NASA/HLS/HLSL30/v002` + `NASA/HLS/HLSS30/v002`), 30 m, Fmask-Wolkenmaske | Landsat 8/9 + Sentinel-2 harmonisiert → 10+ Jahre, ~2–3 Tage | Landsat 5/7 für vor 2013 |
| Satellit hochaufgelöst | **Sentinel-2 L2A** `COPERNICUS/S2_SR_HARMONIZED` (10–20 m) + **Cloud Score+** `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`, `cs_cdf ≥ 0.60` | Red-Edge (NDRE) nur bei S2; kleine Felder | Schwelle tunen |
| Gemeinsame Basis für Transfer | **HLS-Merkmale** werden für US- **und** österreichische Felder berechnet | gleiches Sensorprodukt → US-Modell direkt auf AT anwendbar | – |
| Radar | **Sentinel-1 GRD** `COPERNICUS/S1_GRD` (VV, VH) – ab Phase 8 | wolkenunabhängig | – |
| Wetter | **ERA5-Land Daily** `ECMWF/ERA5_LAND/DAILY_AGGR` – für US- und AT-Felder gleich | global konsistent, inkl. Bodenwasser | GeoSphere **SPARTACUS** 1 km für AT (Ablation) |
| Boden | **SoilGrids 250 m** + nutzbare Feldkapazität (Saxton & Rawls 2006) | global konsistent | österreichische eBOD |
| Gelände | **Copernicus DEM GLO-30** → Höhe, Neigung, Nord-/Ostexposition | in GEE | 10-m-DGM Österreich, TWI |
| Felder Österreich | **INVEKOS Schläge** (AMA, GeoPackage, CC BY 4.0) | offizielle Feldgrenzen + Kultur | – |
| Regionalerträge | **CY-Bench** (AT + EU) + **Statistik Austria** (Körnermais, Bundesland) | harmonisiert / offiziell | – |
| Rechenplattform | **Google Earth Engine** (Python API), Export CSV → Google Drive | serverseitig | – |
| Zeitraster | **Dekaden** (10 Tage), 1. April – 31. Oktober | glättet Wolkenlücken; Mais ändert sich in Wochen | – |
| Indizes | NDVI, EVI, GNDVI, NDMI, SAVI (HLS + S2); **NDRE** nur S2 | Red-Edge fehlt bei Landsat | MTCI |
| Ertrags-Zielgröße (US) | **relativer Ertrag RY** (3.6) primär; absoluter Ertrag t/ha sekundär | RY entfernt Standortniveau (Boden, Bewässerung) → übertragbar | – |
| „Gefährdet“ | **RY < 0,85** bzw. **VAS < 0,85** | ≥ 15 % unter eigenem Normalniveau | – |
| Satelliten-Zielgröße (AT, selbstüberwacht) | Kandidaten **K1–K5** (3.3); **Auswahl in Phase 3** nach vorab festgelegter Regel | erst Ertragsbezug nachweisen | Seneszenz-Datum |
| Stichtage | Ertragsmodell: **1.6., 15.6., 1.7., 15.7., 1.8., 15.8., 1.9.**; selbstüberwachtes Modell: **15.5., 1.6., 15.6., 1.7., 15.7.** | Ertrag am Saisonende → Stichtage bis Sept.; Selbstüberwachung: alle vor Zielfenster | – |
| Hauptmodell | **LightGBM** (CPU); bei wenigen Daten flach (max_depth ≤ 3) + **Ridge**-Vergleich | robust bei kleinen Stichproben | – |
| Zeitreihenmodell | **GRU** (PyTorch, CPU) – nur für das große österreichische Feldmodell | braucht viele Beispiele | kleiner Transformer |
| Validierung Ertrags-Datensatz | **LOFYO** (Feld *und* Jahr ungesehen) primär; LOFO, LOYO, Leave-One-Dataset-Out sekundär | verhindert Auswendiglernen von Feldern/Jahren | – |
| Validierung Österreich | **LOYO** primär + räumliche Blöcke (10 km) | neue Saison vorhersagen | – |
| Unsicherheit | **Split-Conformal** + LightGBM-Quantile (q10/q50/q90) | kalibrierte Intervalle | – |
| Erklärbarkeit | **SHAP** (TreeExplainer) | Faktoren pro Feld | – |
| Demo | **Streamlit + Folium/PyDeck** mit Datums-Slider | einfach, interaktiv | – |
| Sprache | Python 3.11; Code-Kommentare & README englisch, Doku deutsch | – | – |

---

## 3. Definitionen (verbindlich)

### 3.1 Feld & Feldhistorie
- **Österreich:** Feld-Jahr = INVEKOS-Schlag mit Körnermais in Jahr *y*. Filter: Fläche ≥ 1,0 ha; nach Innenpuffer −10 m mindestens 50 S2-Pixel; Geometrie gültig. Feld-ID über Jahre per Geometrie-Überlappung (**IoU ≥ 0,7**) → `field_uid`, inkl. Fruchtfolge.
- **Ertrags-Datensatz:** Feld-Jahr = Feld/Parzelle/Teilfläche mit Mais in Jahr *y* und gemessenem Ertrag. Feldgrenze aus den Quell-Geodaten; falls nicht vorhanden: konvexe Hülle der Ertragspunkte. Immer Innenpuffer −10 m (Vorgewende, Randeffekte). Mindestens 5 HLS-Pixel (30 m) nach Puffer, sonst nur S2-Auswertung.

### 3.2 Satellitenbeobachtung pro Feld
- Pro Szene: Median aller klaren Pixel im gepufferten Feld je Band + `clear_frac`.
- Gültig, wenn `clear_frac ≥ 0.7`.
- **Dekaden-Komposit:** Median der gültigen Beobachtungen je Dekade; fehlende Dekaden linear interpoliert innerhalb der Saison, plus `is_observed` und `days_since_last_obs`.
- HLS und S2 werden **getrennt** gespeichert (`sensor`-Spalte); Merkmale mit Suffix `_hls` / `_s2`.

### 3.3 Satelliten-Zielgrößen (Kandidaten, für Selbstüberwachung in AT)

| Kürzel | Definition | Gültig, wenn | Anwendbar |
|---|---|---|---|
| K1 `I_Aug` | Mittel des Index in den Dekaden 1.8.–31.8. | ≥ 2 der 3 Dekaden beobachtet | Regionen mit ähnlichem Anbaukalender (AT, US-Mais-Standorte) |
| K2 `I_postpeak` | Mittel in den 40 Tagen nach dem Maximum der geglätteten Saisonkurve | ≥ 2 Beobachtungen im Fenster | überall |
| K3 `peak` | Maximum der geglätteten Kurve | Beobachtung ±15 Tage um das Maximum | überall |
| K4 `I_season` | Integral über Grundniveau vom Aufgang bis zur Abreife | ≥ 60 % der Saisondekaden beobachtet | überall |
| K5 | K1–K4 mit anderem Index (NDVI, EVI; NDRE wo S2) | wie dort | überall |

- `Z` = gewählte Zielgröße; `Z_normal(field, y)` = Median von `Z` aller Körnermais-Feld-Jahre derselben **Gemeinde** in den **anderen** Jahren → `VAS = Z / Z_normal`.
- **Frühernte-Regel:** abrupter Abfall auf Boden-Niveau vor/im Zielfenster → `harvested_early`, **nicht** als Stress gewertet.

### 3.4 Regionaler Ertrags-Anomalie-Score
- `YAS(region, y) = Ertrag(y) / Erwartung(y)`, Erwartung = **olympischer Durchschnitt der 5 Vorjahre** (ohne Max/Min). Nur Vorjahre → kein Leakage.

### 3.5 As-of-Regel (Leakage-Schutz)
Für Stichtag *t* darf ein Feature nur Daten mit Zeitstempel ≤ *t* nutzen. Durchgesetzt durch `features.build(cutoff=t)` mit Assertion **und** Unit-Test.

### 3.6 Feld-Ertrag (Ertrags-Datensatz)
- **Einheit:** Körnermais in **t/ha bei 15,5 % Kornfeuchte** (US-Standard); jede Quelle wird darauf umgerechnet, Umrechnung in `DATA_SOURCES.md`.
- **Feld-Ertrag `Y`:** Mittel der bereinigten Ertragspunkte im gepufferten Feld. Bereinigung (falls Quelle nicht schon bereinigt): Punkte außerhalb 1–25 t/ha und außerhalb ±3 SD je Feld-Jahr entfernen; Anteil entfernter Punkte protokollieren.
- **Relativer Ertrag `RY(field, y)` = `Y(field, y)` / Mittel `Y` desselben Feldes in seinen **anderen** Mais-Jahren**; nur definiert, wenn ≥ 2 andere Mais-Jahre existieren. (Normalisierung nutzt nur Label-Information desselben Feldes, nie Merkmale → kein Feature-Leakage.)
- **Gefährdet:** `RY < 0.85`.
- **Innerhalb des Feldes:** Ertragspunkte werden auf das HLS-Raster (30 m) und das S2-Raster (10 m) gemittelt → Pixel-Paare (Index, Ertrag) für die räumliche Auswertung.
- **Bewässerung** (z. B. Mead US-Ne1/Ne2) als Spalte `irrigated`; wird getrennt ausgewertet.

---

## 4. Projektstruktur

```
CropTransferAT/
├─ PLAN.md  AGENTS.md  CLAUDE.md  README.md
├─ CHANGELOG.md  DECISIONS.md  DATA_SOURCES.md  SUPPORT.md
├─ requirements.txt  config.yaml
├─ .github/workflows/tests.yml
├─ data/                       # nicht in Git
│  ├─ raw/  interim/  processed/
├─ src/croptransfer/
│  ├─ groundtruth.py           # KBS, BARC, Colorado, Mead laden → einheitliches Schema
│  ├─ invekos.py               # INVEKOS laden, filtern, Feld-IDs über Jahre
│  ├─ gee_extract.py           # HLS, S2, S1, ERA5-Land, SoilGrids, DEM → Exporte
│  ├─ timeseries.py            # Wolkenfilter, Indizes, Dekaden, Interpolation
│  ├─ features.py              # As-of-Feature-Builder
│  ├─ targets.py               # Y, RY, K1–K5, Z_normal, VAS, YAS
│  ├─ splits.py                # LOFYO, LOFO, LOYO, Leave-One-Dataset-Out, räumliche Blöcke
│  ├─ models/
│  │  ├─ baselines.py
│  │  ├─ lgbm.py
│  │  └─ gru.py
│  ├─ evaluate.py              # Metriken, Bootstrap-KI, Frühwarnkurven, Ablation
│  ├─ explain.py               # SHAP
│  ├─ uncertainty.py           # Conformal, Quantile
│  └─ regional_cybench.py
├─ notebooks/                  # Exploration & Abbildungen (Logik gehört in src/)
├─ app/streamlit_app.py
├─ results/  reports/figures/  reports/data_review/  reports/doku/
└─ tests/
   ├─ fixtures/
   ├─ test_no_leakage.py
   ├─ test_targets.py
   ├─ test_groundtruth_schema.py
   ├─ test_field_matching.py
   ├─ test_schemas.py
   └─ test_splits.py
```

---

## 5. Phasen

**Reihenfolge-Prinzip:** Erst lernen, was die Satellitenkurve über **echten Ertrag** verrät (Phase 1). Dann prüfen, ob die Daten in der Steiermark das hergeben (Phase 2) und ob der Ertragsbezug auch in Österreich sichtbar ist (Phase 3, GO/NO-GO). Erst danach skalieren und modellieren. Das Regionalmodell (Phase 4) läuft als Sicherheitsnetz parallel, sobald Phase 0 fertig ist.

```
Phase 0 Setup ─┬─► 1 Ertrags-Datensatz USA ─► 2 Steiermark-Pilot ─► 3 Ertragsbezug AT (GO/NO-GO) ─► 5 … 11
               └─► 4 CY-Bench-Regionalmodell (parallel) ──────────────────────────────────────────┘
```

### Phase 0 – Setup & Datenzugang
**Ziel:** Umgebung steht, jede Datenquelle ist nachweislich erreichbar.

Aufgaben:
1. Python-Umgebung: `python -m venv .venv`; Pakete `earthengine-api geemap geopandas pyogrio shapely rasterio pandas numpy scipy pyarrow lightgbm scikit-learn shap torch matplotlib seaborn streamlit folium streamlit-folium pyyaml pytest tqdm` → `requirements.txt` mit fixierten Versionen.
2. Paketstruktur `src/croptransfer/`, `config.yaml`, erster Test, **GitHub Actions** (`pytest` bei jedem Push).
3. **GEE:** Konto + Cloud-Projekt (*Projektinhaber*), dann `earthengine authenticate`. Test: Anzahl HLS- und S2-Szenen über Graz und über Hickory Corners (KBS) im Juli 2022.
4. **Ertrags-Datensätze herunterladen und sichten:**
   - KBS: geo-referenzierte Erträge (Datatables 828, 185; Scale-up 163), Parzellen-Erträge (51), Parzellen-/Feldgrenzen (KBS-GIS), Nutzungsbedingungen.
   - BARC: Ertragsarchiv 2014, 2016–2021 + `BARCFarmMgmt.zip` (Kultur je Feld und Jahr), Rasterauflösung, Feldgrenzen.
   - Colorado: Ag-Data-Commons-Datensatz (18 Teilflächen, 2019–2022).
   - Mead: prüfen, ob AmeriFlux-BADM Erträge enthalten (*AmeriFlux-Konto: Projektinhaber*); sonst Status „angefragt“.
   - Je Datensatz in `DATA_SOURCES.md`: Lizenz, Jahre, Anzahl **Mais**-Feld-Jahre, Feldgrößen, Koordinatensystem, Messmethode, Einheit/Feuchte.
5. **INVEKOS** Schläge 2018–2025; Spalte der Nutzungsart verifizieren (vermutlich `SNAR_BEZEICHNUNG` = `KÖRNERMAIS`).
6. **Verwaltungsgrenzen** AT (Bundesländer, Bezirke, Gemeinden).
7. **CY-Bench** (Zenodo, 6,2 GB): Ebene von AT (NUTS-2/3?), Jahre, Prädiktoren.
8. **Statistik Austria:** Körnermais-Hektarerträge je Bundesland 2010–2025 → `data/raw/stat_at_maize.csv`; feinere Ebenen prüfen.

**Deliverable:** `notebooks/00_data_access.ipynb`, `DATA_SOURCES.md` vollständig.
**Abnahme:** Jede Quelle liefert Daten oder ist begründet als „nicht verfügbar / angefragt“ markiert; Tests laufen in GitHub Actions.

---

### Phase 1 – Ertrags-Datensatz & Saisonkurven (F0)
**Ziel:** Ein einheitlicher Datensatz „Maisfeld × Jahr × gemessener Ertrag × Satelliten-Saisonkurve“ und die Antwort auf F0: **Welche Kurve bedeutet welchen Ertrag – und ab wann erkennt man gefährdete Felder?**

Aufgaben:
1. `groundtruth.py`: KBS, BARC, Colorado (+ Mead sobald verfügbar; + österreichische Landwirt:innen-Daten sobald verfügbar) in ein Schema überführen:
   - `gt_field_years`: `dataset, field_id, year, crop, geometry, Y_t_ha, n_points, irrigated, source`
   - `gt_yield_points`: `dataset, field_id, year, x, y, yield_t_ha` (innerhalb des Feldes)
   Nur Mais-Feld-Jahre; Umrechnung auf 15,5 % Feuchte; Bereinigung nach 3.6.
2. `RY` berechnen (3.6); Verteilung je Datensatz; Anteil „gefährdet“ angeben.
3. Satellitenkurven je Feld-Jahr über GEE: **HLS 2013–2025** und **S2 2017–2025**; ERA5-Land für dieselben Felder.
4. **Ansehen:** Je Datensatz Kurven der besten und schlechtesten RY-Jahre desselben Feldes übereinanderlegen – sieht man den Unterschied, und ab wann?
5. **Zusammenhang messen (Feld-Ebene):** Spearman ρ zwischen K1–K5 (je Index, je Sensor) und `Y` bzw. `RY` – je Datensatz und gepoolt, mit Bootstrap-KI über Felder. Bewässert/unbewässert getrennt.
6. **Zusammenhang innerhalb des Feldes:** Pixel-Paare (Index ↔ Ertrag) je Feld-Jahr; Median-ρ über alle Feld-Jahre, je Zeitpunkt der Saison.
7. **Frühwarn-Test:** `RY` aus Merkmalen bis Stichtag *t* (Stichtage siehe Abschnitt 2) vorhersagen.
   - Merkmale: Dekadenwerte bis *t*, Steigungen, Maximum bis *t*, Fläche unter Kurve, Wetter-Aggregate bis *t* (GDD, Niederschlag, Wasserbilanz, Hitzetage), Boden.
   - Modelle: B0 `RY = 1`; B1 Ridge auf einem Index-Merkmal; M Ridge + flaches LightGBM.
   - Splits: **LOFYO** (primär), LOFO, LOYO, **Leave-One-Dataset-Out** (Vorgeschmack auf Transfer).
   - Metriken: Spearman ρ, RMSE auf RY, R²; „gefährdet“: PR-AUC, Recall bei 20 % Fehlalarmrate; Bootstrap-KI.
   - **Frühwarnkurve:** Güte vs. Stichtag.
8. Kontrolltests nach AGENTS.md §3.3: Label-Shuffle-Test, Leistung innerhalb eines Jahres, Modell mit/ohne Feld-Kennungen.

**Deliverable:** `data/processed/gt_*.parquet`, `notebooks/01_groundtruth.ipynb`, Tabellen + Frühwarnkurve, Datenkritik-Bericht.
**Abnahme:** Datensatz reproduzierbar per Befehl; Anzahl Mais-Feld-Jahre je Datensatz dokumentiert; alle Auswertungen mit KI; Ergebnis zu **GO-Bedingung (a)** (Phase 3) festgehalten.

---

### Phase 2 – Pilot Steiermark
**Ziel:** Prüfen, ob Satellitendaten auf steirischen Maisfeldern das zeigen, was wir brauchen – bevor skaliert wird.

Aufgaben:
1. `invekos.py`: Körnermais Steiermark filtern (3.1), Innenpuffer.
2. **200 Felder**, stratifiziert über Bezirke und Höhenlagen, **2 Jahre** – vorab anhand der Statistik-Austria-Erträge gewählt (ein deutlich schwaches, ein normales Jahr), **bevor** Satellitendaten angesehen werden.
3. HLS **und** S2 je Feld (gleiche Pipeline wie Phase 1).
4. Prüfungen:
   - **Kurvenform:** maistypisch? Anteil unplausibler Felder (falsche Kulturangabe, Frühernte).
   - **Datenabdeckung:** Anteil beobachteter Dekaden je Monat/Jahr.
   - **Lokale Unterschiede:** Varianz der Kandidaten K1–K5 **innerhalb** vs. **zwischen** Bezirken; Paare naher Felder (< 10 km) mit stark unterschiedlicher Entwicklung als Fallbeispiele.
   - **Jahresunterschied:** Ist das schwache Jahr sichtbar schwächer?
   - **Vergleichbarkeit mit US-Feldern:** Liegen steirische HLS-Kurven im Wertebereich der US-Trainingsdaten? (Verteilungsvergleich – Voraussetzung für Transfer F4c)

**Deliverable:** `notebooks/02_pilot.ipynb`, Datenkritik-Bericht.
**Abnahme:** ≥ 80 % der Felder maistypisch; ≥ 70 % der Feld-Jahre mit ausreichend beobachteten Dekaden für mindestens einen Kandidaten. Sonst Stopp und Klärung.

---

### Phase 3 – Ertragsbezug in Österreich & Entscheidung (GO / NO-GO)
**Ziel:** Prüfen, ob der in Phase 1 gefundene Ertragsbezug auch in Österreich sichtbar ist, und die Satelliten-Zielgröße für das selbstüberwachte Modell festlegen.

Validierungswege in Österreich:

| Weg | Daten | Ebene |
|---|---|---|
| **V1 – regional** | Statistik Austria (Bundesland) + CY-Bench (feinste verfügbare Ebene) | Region-Jahr |
| *V2 – Feld, international* | *= Ertrags-Datensatz USA, ausgewertet in Phase 1* | *Feld-Jahr* |
| **V3 – Feld** | Erträge österreichischer Landwirt:innen, **falls beschafft** | Feld-Jahr (Goldstandard) |

Aufgaben:
1. Österreich-Stichprobe: je Bundesland mit relevantem Körnermais (u. a. Stmk, OÖ, NÖ, Bgld, Ktn) und Jahr mit Ertragsstatistik bis zu 300 Felder durch die Pilot-Pipeline.
2. **V1a – Kandidaten:** flächengewichteter Mittelwert von K1–K5 je Region-Jahr ↔ YAS; Pearson + Spearman, Bootstrap-95-%-KI, n angeben.
3. **V1b – US-Modell (Vorgeschmack F4c):** das Phase-1-Modell (Stichtag 1.9.) auf die Stichprobe anwenden, vorhergesagten RY regional mitteln ↔ YAS.
4. **V3:** wenn Daten vorliegen – wie Phase 1 auswerten.
5. Entscheidung nach Regel unten; Ergebnis in `DECISIONS.md`, Zielgröße in `config.yaml`.

**Vorab festgelegte Entscheidungsregel** (nicht nachträglich ändern):
- **GO**, wenn mindestens eine Kandidaten-Zielgröße
  **(a)** in Phase 1 mit dem Feldertrag (`RY`) Spearman **ρ ≥ 0,4** erreicht (gepoolt oder in mindestens einem Datensatz, KI angeben) **und**
  **(b)** in Österreich (V1a) einen **positiven Zusammenhang mit 95-%-KI ohne 0** zeigt.
- **Wahl der Zielgröße:** höchster Median-ρ über Phase 1 (je Datensatz) und V1a, sofern in Österreich berechenbar. Bei Gleichstand (Differenz < 0,05) die einfachere (K1 < K3 < K2 < K4; NDVI < EVI < NDRE).
- **NO-GO:** Stopp, Projektinhaber informieren. Optionen: andere Indizes/Fenster, Radar früher einbinden, Schwerpunkt auf US-Ertragsmodell + Regionalmodell (Phase 4) verlagern.

**Deliverable:** `notebooks/03_target_check_at.ipynb`, Korrelationstabellen + Streudiagramme, Entscheidung.
**Abnahme:** GO/NO-GO dokumentiert; Zielgröße festgelegt.

---

### Phase 4 – V0: Regionales Transfermodell (CY-Bench) — *Sicherheitsnetz, parallel ab Phase 0*
**Ziel:** Ein vollständiges Ergebnis unabhängig von der Feldpipeline. Beantwortet F4a.

Aufgaben:
1. Mais-Daten EU laden (alle EU-Länder + AT); Prädiktoren je Region-Jahr und Stichtag aggregieren (Mittel/Min/Max/Summe je Monat: tmax, tmin, prec, cwb, rsm, ssm, fpar, ndvi; statisch: awc, Lagerungsdichte).
2. Zielvariable **YAS** (3.4).
3. Baselines: YAS = 1; lineare Trendfortschreibung.
4. LightGBM: **In-Domain AT** (LOYO), **Zero-Shot AT** (Training EU ohne AT), **Pooled**, **Few-Shot** (EU + k AT-Jahre, k = 0, 2, 4, 6, 8, alle; 10 Wiederholungen).
5. Vergleich mit publizierter CY-Bench-Baseline für AT (bestes Modell R² 0,13, LOYO).

**Deliverable:** Tabelle + Few-Shot-Kurve + Frühwarnkurve.
**Abnahme:** reproduzierbar per `python -m croptransfer.regional_cybench`.

---

### Phase 5 – Volle Felddaten-Pipeline Steiermark
**Voraussetzung:** Phase 3 = GO.
**Ziel:** Saubere Dekaden-Zeitreihen + statische Features für alle Körnermais-Feld-Jahre 2018–2025.

Aufgaben:
1. `invekos.py`: alle Jahre, Feld-IDs über Jahre (IoU), Fruchtfolge.
2. `gee_extract.py`: S2 + HLS für alle Felder (erst **5.000 Felder/Jahr** stratifiziert nach Bezirk, dann alle); ERA5-Land täglich am Feldzentroid (Tmin/Tmax/Tmean, Niederschlag, Strahlung, Taupunkt → VPD, Verdunstung, potenzielle Verdunstung, Bodenwasser Schicht 1–3); SoilGrids + DEM je Feld.
3. Wetter-Ableitungen je Dekade: GDD (Basis 10 °C, Deckel 30 °C), Hitzetage > 30 °C / > 32 °C, Niederschlag 10/30 Tage, klimatische Wasserbilanz, VPD.
4. **Wurzelzonen-Wasserstress-Index (RZWSI):** FAO-56-Bucket mit nutzbarer Feldkapazität und ET0.
5. Qualitätsbericht.

**Deliverable:** `data/processed/fields_dekads.parquet`, `fields_static.parquet`.
**Abnahme:** ≥ 70 % der Feld-Jahre mit gültiger Zielgröße; Pipeline per Befehl.

---

### Phase 6 – Ziele, Stress-Score & explorative Analyse
Aufgaben:
1. `targets.py`: `Z`, `Z_normal`, `VAS`.
2. VAS-Verteilung je Jahr; Schwelle „gefährdet“ (0,85) bestätigen oder begründet anpassen.
3. **Gesundheit jetzt:** z-Score des Feld-Index je Dekade gegenüber (a) Körnermais-Feldern im Umkreis von 10 km (nur Daten ≤ t) und (b) eigener Historie.
4. Karten + Fallstudien: 5 abrupte Einbrüche (Hagelverdacht), 5 langsame Abfälle (Trockenheit).

**Deliverable:** `notebooks/06_eda.ipynb`.
**Abnahme:** Abbildungen zeigen Jahreseffekt **und** lokale Unterschiede innerhalb eines Jahres.

---

### Phase 7 – V1: Selbstüberwachtes Feld-Vorhersagemodell (F1)
Feature-Gruppen (as-of *t*): S2/HLS-Dekaden, Steigungen, Maximum, Fläche unter Kurve, Abweichung zum Nachbar-Median; Wetter (GDD, Niederschlag, Wasserbilanz, Hitzetage, VPD, RZWSI); Bodenfeuchte; Boden & Gelände; Feldhistorie (Vorfrucht, frühere `Z` ohne Testjahr); Kontext (Gemeinde-`Z_normal`, Höhe).

| Code | Modell |
|---|---|
| B0 | Klimatologie: `Z_pred = Z_normal` |
| B1 | Persistenz: aktuelle Anomalie bleibt bis zum Zielfenster gleich |
| B2 | LightGBM nur Wetter + Boden |
| M1 | LightGBM alle Features |
| M2 | GRU über Dekadensequenz + statische Features |

Metriken: RMSE, MAE, R² auf `Z`; R² auf VAS; Rangkorrelation innerhalb jedes Jahres; „gefährdet“: PR-AUC, Recall bei 20 % Fehlalarmrate; Skill = 1 − RMSE/RMSE_B0. Validierung LOYO + räumliche Blöcke.

**Deliverable:** Ergebnistabelle Modell × Stichtag; Frühwarnkurve.
**Abnahme:** M1 schlägt B0 und B1 in mindestens den späten Stichtagen signifikant (Bootstrap, 95-%-KI).

---

### Phase 8 – V2: Ablation, Radar, Unsicherheit, Erklärbarkeit (F2)
1. **Sentinel-1** (VV, VH, VH/VV in dB, Dekaden-Mittel; Orbit als Feature).
2. **Ablation** – M1 (und das US-Ertragsmodell, soweit Merkmale vorhanden) neu trainiert:

| Variante | Features |
|---|---|
| A | Wetter |
| B | Wetter + Boden |
| C | Wetter + Bodenfeuchte/RZWSI |
| D | Wetter + optisch (S2/HLS) |
| E | Wetter + S1 |
| F | Wetter + S1 + optisch |
| G | alles ohne Bodenfeuchte |
| H | alles ohne Feldhistorie |
| I | alles |

3. **Unsicherheit:** Quantil-LightGBM + Split-Conformal; Coverage-Plot.
4. **SHAP:** global + Top-3-Faktoren je Feld als Text.
5. Optional: SPARTACUS 1 km statt ERA5-Land (lokale Unterschiede zwischen Tälern).

**Abnahme:** Jede Variante mit KI; Coverage innerhalb ±5 Prozentpunkte.

---

### Phase 9 – V3: Ertragsbezug der Vorhersagen & Transfer (F3, F4b, F4c)
1. **F3:** vorhergesagter VAS (Phase 7) je Stichtag, regional gemittelt ↔ YAS; bei V3-Daten feldweise.
2. **F4c – US-Ertragsmodell → Österreich:** Phase-1-Modell (HLS-Merkmale + Wetter) zu jedem Stichtag auf steirische und österreichische Felder anwenden (Zero-Shot) → regional ↔ YAS; bei V3-Daten feldweise. Few-Shot mit V3-Daten (k = 5, 10, 20, alle Feld-Jahre), falls vorhanden.
3. **Vergleich der beiden Wege:** US-Ertragsmodell vs. selbstüberwachtes Modell vs. Kombination (selbstüberwachte Vorhersage als Merkmal) – welcher Weg sagt österreichische Ertragsverluste besser und früher voraus?
4. **F4b:** M1 nur Steiermark → andere Bundesländer (Zero-Shot), Few-Shot k = 50, 100, 250, 500 Felder.
5. Fehleranalyse: Bewässerung (Marchfeld), kleine Felder, Hanglagen, wolkenreiche Jahre, Verteilungsunterschiede US ↔ AT.

**Abnahme:** Ergebnisse so berichtet, wie sie sind – auch schwache Zusammenhänge (n und KI angeben).

---

### Phase 10 – Demo-App
- Streamlit-Karte der Steiermark, Felder eingefärbt: 🟢 ≥ 0,95 · 🟡 0,85–0,95 · 🟠 0,75–0,85 · 🔴 < 0,75 (vorhergesagter VAS bzw. RY).
- **Datums-Slider** – nur, was zu diesem Datum bekannt war (vorberechnete as-of-Vorhersagen).
- Klick auf Feld: Kurve vs. Normal, Vorhersage mit Unsicherheitsband über die Stichtage, Wetter/RZWSI, Top-3-SHAP-Faktoren, S2-Echtfarb-Thumbnail.
- Zweiter Reiter: **US-Ertragsfelder** – Kurve, Vorhersage und tatsächlich gemessener Ertrag nebeneinander („so sieht das Modell einen echten Ertragsverlust kommen“).
- Jahr wählbar (nur Out-of-Sample-Vorhersagen).

**Abnahme:** `streamlit run app/streamlit_app.py` läuft aus vorberechneten Dateien, ohne GEE-Zugang.

---

### Phase 11 – Wissenschaftliche Aufbereitung & Abgabe
1. **Dokumentation** entlang der Bewertungskriterien:
   - Motivation & Relevanz (Landwirte, Kammer, Versicherung, AMA, Ministerium)
   - Stand der Forschung: CY-Bench, JRC MARS, SCYM, Feldertrags-Studien mit Mähdrescherdaten + Sentinel-2, Leave-One-Country-Out-Studien; Abgrenzung
   - Daten & Lizenzen, Pipeline, Definitionen, Leakage-Schutz
   - **Kapitel F0:** Was verrät die Satellitenkurve über echten Ertrag, und ab wann? (Phase 1)
   - Experimente F1–F4 mit Konfidenzintervallen
   - **Fehlerquellen & Grenzen** (US ≠ AT, Vegetationszustand ≠ Ertrag, Wolken, 9-km-Wetter, Bewässerung, Korrelation ≠ Kausalität)
   - Ausblick: mehr österreichische Feld-Erträge, Kooperationen, Kalibrierung auf t/ha
   - Unterstützung (aus `SUPPORT.md`)
2. **Video-Pitch** 3–5 min: Problem (10 %) → Idee (20 %) → Demo mit Zeitreise (35 %) → Hauptergebnisse Frühwarnkurve + Ertragsbezug (25 %) → Ausblick (10 %).
3. **Code:** README mit Reproduktionsschritten, Tests grün, Lizenz.

---

## 6. Qualitätsregeln (gelten immer)

1. **Kein zufälliger Split** von Feld-Jahren – immer LOFYO/LOFO/LOYO oder räumliche Blöcke.
2. **Keine Normalwerte, Schwellen oder Hyperparameter aus Testdaten.** Tuning nur verschachtelt innerhalb der Trainingsdaten.
3. Jede Zahl in der Doku kommt aus einem Skript; Abbildungen per Code.
4. Zufalls-Seeds fixiert in `config.yaml`.
5. Jede Abweichung → `DECISIONS.md`. Jede Hilfe → `SUPPORT.md`. Datenkritik nach jedem großen Schritt (`AGENTS.md` §3).

---

## 7. Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Wenige Mais-Feld-Jahre im Ertrags-Datensatz (Fruchtfolge: Mais nur jedes 2.–3. Jahr) | mehrere Datensätze poolen; Punkte innerhalb der Felder nutzen; einfache Modelle (Ridge, flaches LightGBM); KI immer angeben |
| Modell lernt Felder/Jahre auswendig | LOFYO als primärer Split; Label-Shuffle-Test; mit/ohne Feld-Kennungen |
| US-Felder ≠ steirische Felder (Klima, Sorten, Bewässerung, Feldgröße) | relativer Ertrag RY statt t/ha; bewässert getrennt; Verteilungsvergleich (Phase 2); Transfer als eigene Forschungsfrage, nicht als Annahme |
| HLS 30 m bei 1-ha-Parzellen knapp | Mindestpixelzahl (3.1); S2 10 m parallel; Parzellen ggf. nur S2 |
| KBS-Daten nur mit Erlaubnis veröffentlichbar | Anfrage früh stellen; bis dahin nur aggregierte Ergebnisse, keine Rohdaten im Repo |
| BARC: Kultur je Feld unklar | Bewirtschaftungsdateien auswerten; unklare Feld-Jahre ausschließen |
| Mead-Erträge nicht verfügbar | Phase 1 läuft ohne Mead; Mead als Ergänzung |
| Wolken in der Steiermark | Dekaden + Interpolation + Masken; HLS erhöht Beobachtungsdichte; Radar ab Phase 8 |
| Satelliten-Zielgröße hängt in AT nicht mit Ertrag zusammen | GO/NO-GO in Phase 3, **vor** dem Modellbau |
| Bundesland-Mittel zu grob | Training pro Feld; Validierung auf feinster Regionalebene + V3 |
| Wenige Region-Jahre für V1/F3 | ganz Österreich + Bootstrap-KI; CY-Bench-Regionen wo möglich |
| Modell lernt nur „Jahr“ statt Feld | Vergleich mit B0/B1; Rangkorrelation innerhalb eines Jahres |
| GEE-Exporte langsam / Quoten | Stichproben zuerst; Export je Jahr/Datensatz getrennt |
| Feld-IDs über Jahre unsauber (AT) | IoU-Matching + Test; Feldhistorie optional (Ablation H) |

---

## 8. Was der Projektinhaber selbst erledigen muss
- Anmeldung zum Wettbewerb.
- Google-Earth-Engine-Konto + Cloud-Projekt anlegen, `earthengine authenticate` im Browser bestätigen.
- **E-Mail an die Kellogg Biological Station (KBS LTER):** Bitte um Erlaubnis, die MCSE-Ertragsdaten in einem Schülerwettbewerbsprojekt zu verwenden und daraus abgeleitete Ergebnisse zu veröffentlichen (keine Weitergabe der Rohdaten).
- **AmeriFlux-Konto** anlegen (für Mead); ggf. Standort nach Ertragsdaten fragen.
- **Feld-Ertragsdaten in Österreich anfragen (V3)** – parallel zu allem: Landwirt:innen, Landwirtschaftskammer Steiermark, Maschinenring. Gesucht: Körnermais-Erträge pro Feld (Mähdrescher-Ertragskarte oder Wiegeschein + Feldlage) ab 2018. Schon 20–50 Feld-Jahre sind wertvoll. Nur mit Zustimmung, anonymisiert, Rohdaten nie ins Repository.

## 9. Bewusst *nicht* Teil dieses Plans (Ausblick)
- One Acre Fund (Afrika): viele Felder, aber je nur ein Jahr – passt nicht zum Ansatz „wenige Felder, viele Jahre“; ggf. später als zusätzlicher Transfertest.
- Europäische Mähdrescher-Ertragsdaten aus Studien (Autor:innen anfragen).
- Kalibrierung auf absolute t/ha in Österreich mit größeren Feld-Ertragsdaten (Kooperationen).
- Kausalanalyse der Stressursachen; Klassifikation der Stressart (nur Fallstudien in Phase 6).
