# CropTransfer AT – Arbeitsplan

> Früherkennung von Stress und Ertragsverlust auf einzelnen steirischen Maisfeldern aus Sentinel-2-Zeitreihen – ohne Feld-Ertragsdaten, validiert gegen offizielle Regionalerträge und ergänzt um einen internationalen Transfer-Test.

Dieser Plan ist so geschrieben, dass er Schritt für Schritt abgearbeitet werden kann. Jede Phase hat: **Ziel → Aufgaben → Ergebnis (Deliverable) → Abnahmekriterium**. Alle technischen Entscheidungen sind in Abschnitt 2 festgelegt; Abweichungen werden im `DECISIONS.md` begründet.

---

## 0. Kernidee in drei Sätzen

1. Ein Maisfeld „sieht man“ im Satelliten als **Kurve über die Saison** (NDVI, NDRE, Wassergehalt …) – gesund = grün, dicht, chlorophyllreich; Stress = Kurve bleibt flach oder fällt früh ab.
2. Weil es in Österreich keine öffentlichen Feld-Erträge gibt, lernt das Modell **aus den Bildern selbst**: Aus der Kurve bis zu einem Stichtag + Wetter + Boden sagt es voraus, **wie stark der Bestand in der Kornfüllung (August) sein wird**. Die „richtige Antwort“ liefern die späteren Satellitenbilder vergangener Jahre (selbstüberwachtes Lernen).
3. Dass diese Vorhersage mit **echtem Ertrag** zusammenhängt, wird geprüft, indem man die Feldwerte pro Region mittelt und mit den offiziellen Ertragsstatistiken vergleicht. Zusätzlich testet ein Regionalmodell, ob Wissen aus anderen EU-Ländern **ohne österreichische Labels** auf Österreich übertragbar ist.

---

## 1. Forschungsfragen (final)

| ID | Frage | Haupt-Experiment |
|---|---|---|
| **F1** | Wie früh in der Saison lässt sich die Bestandsstärke eines einzelnen Maisfeldes in der Kornfüllung vorhersagen? | Vorhersagegüte vs. Stichtag (Frühwarnkurve) |
| **F2** | Welche Datenquellen tragen wie viel bei (Satellit optisch, Radar, Wetter, Bodenfeuchte, Boden, Feldhistorie)? | Ablation |
| **F3** | Hängen die feldbasierten Stress-Scores (regional gemittelt) mit offiziellen Ertragsanomalien zusammen? | Korrelation Feld-Score ↔ Regionalertrag |
| **F4** | Lässt sich ein Modell ohne Labels aus der Zielregion übertragen? (a) Regional: andere EU-Länder → Österreich. (b) Feld: Steiermark → andere Bundesländer. Wie viele lokale Daten braucht es (Few-Shot)? | Zero-Shot + Few-Shot-Kurven |

**Ehrliche Grenze (steht so in der Doku):** Das System sagt *Vegetationszustand* voraus, nicht direkt t/ha. Der Bezug zum Ertrag wird über F3 *gemessen*, nicht angenommen.

---

## 2. Festgelegte technische Entscheidungen

| Thema | Entscheidung | Begründung | Später optional |
|---|---|---|---|
| Region (Feldebene) | **Steiermark** | viel Körnermais, kaum Bewässerung, Hagel + Trockenstress | – |
| Region (Validierung F3/F4b) | **ganz Österreich, Stichprobe** | Steiermark allein = zu wenige Region-Jahre für Statistik | – |
| Kultur | **nur Körnermais** (Silomais ausgeschlossen) | Silomais wird früher geerntet → verfälscht August-Signal | Silomais als Vergleich |
| Jahre | **2018–2025** (8 Saisons) | stabile Sentinel-2-L2A-Abdeckung | 2017 |
| Satellit optisch | **Sentinel-2 L2A** `COPERNICUS/S2_SR_HARMONIZED` | 10–20 m, ~5 Tage | – |
| Wolkenmaske | **Cloud Score+** `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`, `cs_cdf ≥ 0.60` | aktueller Standard in GEE | Schwelle tunen |
| Radar | **Sentinel-1 GRD** `COPERNICUS/S1_GRD` (VV, VH) – ab Version V2 | wolkenunabhängig | – |
| Wetter | **ERA5-Land Daily** `ECMWF/ERA5_LAND/DAILY_AGGR` | in GEE, inkl. Bodenwasser 4 Schichten | GeoSphere **SPARTACUS** 1 km (Ablation „bringt feineres Wetter etwas?“) |
| Boden | **SoilGrids 250 m** (Ton, Sand, Schluff, SOC, Lagerungsdichte, pH) + nutzbare Feldkapazität per Pedotransferfunktion (Saxton & Rawls 2006) | in GEE, global konsistent | österreichische eBOD |
| Gelände | **Copernicus DEM GLO-30** `COPERNICUS/DEM/GLO30` → Höhe, Hangneigung, Nord-/Ostexposition | in GEE | 10-m-DGM Österreich, TWI |
| Felder | **INVEKOS Schläge** (AMA, GeoPackage, CC BY 4.0), je Jahr | offizielle Feldgrenzen + Kultur | – |
| Regionalerträge | **CY-Bench** (AT + EU) + **Statistik Austria** Feldfruchternte (Körnermais, Bundesland) | harmonisiert / offiziell | – |
| Rechenplattform Satellit | **Google Earth Engine** (Python API), Export als CSV nach Google Drive | Tausende Felder serverseitig | – |
| Zeitraster | **Dekaden** (10-Tages-Schritte), 1. April – 30. September = 18 Schritte | glättet Wolkenlücken, Standard in Agrarmonitoring | – |
| Ziel-Index | **NDRE** = (B8A − B5)/(B8A + B5) als Hauptindex; NDVI parallel | NDVI sättigt bei dichtem Mais | MTCI |
| Zielvariable | **I_Aug** = mittlerer NDRE der Felddekaden **1.–31. August** (Kornfüllung) | definierte, messbare Bestandsstärke | Seneszenz-Datum |
| Stress-Score | **VAS** (Vegetation Anomaly Score) = I_Aug / I_normal | Feld-Gegenstück zum YAS | – |
| Stichtage | **15.5., 1.6., 15.6., 1.7., 15.7.** | alle vor dem Zielfenster → echte Vorhersage | – |
| Hauptmodell | **LightGBM** (CPU) | stark, schnell, erklärbar | – |
| Zeitreihenmodell | **GRU** (PyTorch, CPU) über Dekadensequenz + statische Features | echtes Temporalmodell | kleiner Transformer |
| Unsicherheit | **Split-Conformal** (nach Jahr) + LightGBM-Quantile (q10/q50/q90) | kalibrierte Intervalle | – |
| Erklärbarkeit | **SHAP** (TreeExplainer) | Faktoren pro Feld | – |
| Validierung | **Leave-One-Year-Out** (primär) + räumliche Blöcke (10 km) (sekundär) | Vorhersage einer *neuen* Saison | – |
| Demo | **Streamlit + Folium/PyDeck** Karte mit Datums-Slider | einfach, interaktiv | – |
| Sprache | Python 3.11, Code-Kommentare & README englisch, Doku deutsch | – | – |

---

## 3. Definitionen (verbindlich)

### 3.1 Feld & Feldhistorie
- **Feld-Jahr** = ein INVEKOS-Schlag mit Kultur Körnermais in Jahr *y*.
- **Filter:** Fläche ≥ 1,0 ha; nach Innenpuffer −10 m mindestens 50 Sentinel-2-Pixel (10 m); Geometrie gültig.
- **Feld-ID über Jahre:** INVEKOS-IDs sind nicht jahresstabil → Zuordnung per Geometrie-Überlappung (**IoU ≥ 0,7**) zu einer `field_uid`. Für jede `field_uid` wird die **Fruchtfolge** (Kultur je Jahr) gespeichert.

### 3.2 Satellitenbeobachtung pro Feld
- Pro Szene: Median aller klaren Pixel im gepufferten Feld für Bänder B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12 + `clear_frac` (Anteil klarer Pixel).
- Beobachtung gültig, wenn `clear_frac ≥ 0.7`.
- Indizes: NDVI, NDRE, EVI, GNDVI, NDMI (B8,B11), SAVI.
- **Dekaden-Komposit:** Median der gültigen Beobachtungen je Dekade; fehlende Dekaden **linear interpoliert innerhalb der Saison**, plus Maskenspalte `is_observed` und `days_since_last_obs`.

### 3.3 Zielvariable & Score
- `I_Aug(field, y)` = Mittel der NDRE-Dekaden 1.8.–31.8. — nur gültig, wenn ≥ 2 der 3 August-Dekaden **beobachtet** (nicht interpoliert).
- `I_normal(field, y)` = Median von `I_Aug` aller Körnermais-Feld-Jahre in derselben **Gemeinde** in den **anderen** Jahren (≠ *y*) → kein Leakage.
- `VAS = I_Aug / I_normal`.
- **Schwerer Stress:** `VAS < 0.85` (Schwelle nach Verteilungsanalyse in Phase 3 bestätigen, nicht nach Modellergebnis wählen).

### 3.4 Regionaler Ertrags-Anomalie-Score (für F3/F4a)
- `YAS(region, y) = Ertrag(y) / Erwartung(y)`, Erwartung = **olympischer Durchschnitt der 5 Vorjahre** (ohne Max/Min). Nur Vorjahre → kein Leakage.

### 3.5 As-of-Regel (Leakage-Schutz)
Für Stichtag *t* darf ein Feature nur Daten mit Zeitstempel ≤ *t* nutzen. Durchgesetzt durch `features.build(cutoff=t)` mit Assertion **und** Unit-Test.

---

## 4. Projektstruktur

```
CropTransferAT/
├─ PLAN.md               # dieser Plan
├─ DECISIONS.md          # jede Abweichung vom Plan + Grund
├─ SUPPORT.md            # Protokoll jeder Unterstützung (Personen, KI-Tools, Datensätze) – Pflicht laut BWKI
├─ README.md
├─ requirements.txt
├─ config.yaml           # Region, Jahre, Stichtage, Schwellen, Pfade
├─ data/                 # nicht in Git
│  ├─ raw/  interim/  processed/
├─ src/croptransfer/
│  ├─ invekos.py         # Laden, Filtern, Feld-IDs über Jahre
│  ├─ gee_extract.py     # S2, S1, ERA5-Land, SoilGrids, DEM → Exporte
│  ├─ timeseries.py      # Wolkenfilter, Indizes, Dekaden, Interpolation
│  ├─ features.py        # As-of-Feature-Builder
│  ├─ targets.py         # I_Aug, I_normal, VAS, YAS
│  ├─ splits.py          # LOYO, räumliche Blöcke
│  ├─ models/
│  │  ├─ baselines.py    # Klimatologie, Persistenz, Wetter-only
│  │  ├─ lgbm.py
│  │  └─ gru.py
│  ├─ evaluate.py        # Metriken, Frühwarnkurve, Ablation
│  ├─ explain.py         # SHAP
│  ├─ uncertainty.py     # Conformal, Quantile
│  └─ regional_cybench.py
├─ notebooks/            # Exploration & Abbildungen
├─ app/streamlit_app.py
├─ reports/figures/  reports/doku/
└─ tests/
   ├─ test_no_leakage.py
   ├─ test_targets.py
   └─ test_field_matching.py
```

---

## 5. Phasen

### Phase 0 – Setup & Datenzugang prüfen
**Ziel:** Alles installiert, alle Datenquellen nachweislich erreichbar.

Aufgaben:
1. Ordner + Git-Repo anlegen, `.gitignore` (data/, .venv/).
2. `python -m venv .venv`, Pakete: `earthengine-api geemap geopandas pyogrio shapely pandas numpy pyarrow lightgbm scikit-learn shap torch matplotlib seaborn streamlit folium streamlit-folium pyyaml pytest tqdm`.
3. **GEE:** Konto + Cloud-Projekt (nicht-kommerziell) anlegen, `earthengine authenticate` – *macht der Projektinhaber selbst*. Test: Anzahl S2-Szenen über Graz im Juli 2024 abfragen.
4. **INVEKOS** Schläge 2018–2025 (GeoPackage) herunterladen; Spalte für Nutzungsart identifizieren (vermutlich `SNAR_BEZEICHNUNG`, Wert `KÖRNERMAIS`) – verifizieren.
5. **Steiermark-Grenze** (Verwaltungsgrenzen data.gv.at) + **Gemeindegrenzen** laden.
6. **CY-Bench** (Zenodo, 6,2 GB) laden; prüfen: Verwaltungsebene von AT (NUTS2/3?), Jahre mit Ertrag, Prädiktoren vorhanden.
7. **Statistik Austria**: Körnermais-Hektarerträge je Bundesland 2010–2025 in `data/raw/stat_at_maize.csv` (Tabellen aus Feldfruchternte-Berichten/STATcube).
8. `SUPPORT.md` anlegen und ab jetzt führen.

**Deliverable:** `notebooks/00_data_access.ipynb` mit je einem erfolgreichen Abruf pro Quelle.
**Abnahme:** Jede Quelle liefert Daten; Spaltennamen + Lizenzen in `DATA_SOURCES.md` dokumentiert.

---

### Phase 1 – V0: Regionales Transfermodell (CY-Bench) — *Sicherheitsnetz*
**Ziel:** Ein vollständiges, publizierbares Ergebnis unabhängig von der Feldpipeline. Beantwortet F4a.

Aufgaben:
1. Mais-Daten EU laden (alle EU-Länder + AT), Prädiktoren zu Features je Region-Jahr und Stichtag aggregieren (Mittel/Min/Max/Summe je Monat: tmax, tmin, prec, cwb, rsm, ssm, fpar, ndvi; statisch: awc, Lagerungsdichte).
2. Zielvariable **YAS** (3.4).
3. Baselines: (a) YAS = 1 (Erwartung), (b) lineare Trendfortschreibung.
4. LightGBM-Experimente:
   - **In-Domain AT:** nur AT, LOYO.
   - **Zero-Shot AT:** Training alle EU-Länder ohne AT → Test AT.
   - **Pooled:** EU inkl. AT, LOYO auf AT-Jahren.
   - **Few-Shot:** EU + k AT-Jahre (k = 0, 2, 4, 6, 8, alle), Test auf übrigen AT-Jahren, 10 Wiederholungen mit zufälliger Jahresauswahl.
5. Vergleich mit publizierter CY-Bench-Baseline für AT (R² 0,13 bestes Modell, LOYO).

**Deliverable:** Tabelle + Few-Shot-Kurve + Frühwarnkurve (Stichtage) für Regionen.
**Abnahme:** Ergebnisse reproduzierbar per `python -m croptransfer.regional_cybench`.

---

### Phase 2 – Felddaten-Pipeline Steiermark
**Ziel:** Saubere Dekaden-Zeitreihen + statische Features für jedes Körnermais-Feld-Jahr.

Aufgaben:
1. `invekos.py`: Körnermais Steiermark je Jahr filtern (3.1), Innenpuffer, Feld-IDs über Jahre (IoU), Fruchtfolge.
2. **Pilot:** 200 Felder × 1 Jahr komplett durch die Pipeline → Kurven visuell prüfen (sehen sie wie Mais aus? Aufgang Mai, Maximum Juli/August, Abreife September).
3. `gee_extract.py`:
   - S2 pro Szene & Feld (3.2) via `reduceRegions`, Export je Jahr als CSV nach Drive.
   - ERA5-Land täglich am Feldzentroid: Tmin/Tmax/Tmean, Niederschlag, Strahlung, Taupunkt (→ VPD), Verdunstung, potenzielle Verdunstung, Bodenwasser Schicht 1–3.
   - SoilGrids (0–30 cm Mittel) + DEM-Ableitungen je Feld (einmalig).
   - Skalierung: erst **5.000 Felder/Jahr** (stratifiziert nach Bezirk), danach alle.
4. `timeseries.py`: Gültigkeitsfilter, Indizes, Dekaden, Interpolation + Masken.
5. Wetter-Ableitungen je Dekade: GDD (Basis 10 °C, Deckel 30 °C), Hitzetage Tmax > 30 °C / > 32 °C, Niederschlag 10/30 Tage, klimatische Wasserbilanz (P − ET0), VPD.
6. **Wurzelzonen-Wasserstress-Index (RZWSI):** einfache Tages-Wasserbilanz (FAO-56-Bucket) mit nutzbarer Feldkapazität aus Boden und ET0 → Anteil pflanzenverfügbares Wasser.
7. Qualitätsbericht: Anteil beobachteter Dekaden je Monat/Jahr, Felder ohne gültiges Ziel.

**Deliverable:** `data/processed/fields_dekads.parquet` (Feld-Jahr × Dekade × Features), `fields_static.parquet`.
**Abnahme:** ≥ 70 % der Feld-Jahre haben ein gültiges `I_Aug`; Pilotkurven plausibel; Pipeline läuft per Befehl durch.

---

### Phase 3 – Ziele, Stress-Score & explorative Analyse
**Ziel:** Verstehen, wie die Daten aussehen, bevor modelliert wird.

Aufgaben:
1. `targets.py`: `I_Aug`, `I_normal`, `VAS` (3.3).
2. Verteilung von VAS je Jahr → Dürrejahre müssen sichtbar sein; Schwelle „schwerer Stress“ festlegen und in `DECISIONS.md` begründen.
3. **Stufe A – Gesundheit jetzt:** zu jeder Dekade z-Score des Feld-NDRE gegenüber (a) allen Körnermais-Feldern im Umkreis von 10 km in derselben Dekade (nur Daten ≤ t) und (b) der eigenen Historie (frühere Maisjahre desselben Feldes, falls vorhanden).
4. Karten: VAS je Feld für 2–3 Jahre; Fallstudien: 5 Felder mit abruptem NDRE-Einbruch (Hagelverdacht) + 5 mit langsamem Abfall (Trockenheit).

**Deliverable:** `notebooks/03_eda.ipynb` mit Abbildungen.
**Abnahme:** VAS-Schwelle festgelegt; mindestens eine Abbildung zeigt einen klaren Jahreseffekt.

---

### Phase 4 – V1: Feld-Vorhersagemodell (F1)
**Ziel:** Vorhersage von `I_Aug` bzw. `VAS` je Feld zu jedem Stichtag.

Feature-Gruppen (as-of *t*):
- **S2:** Dekadenwerte aller Indizes bis *t*; Steigung der letzten 3 Dekaden; Maximum bis *t*; Fläche unter Kurve bis *t*; Abweichung zum Nachbar-Median (Stufe A).
- **Wetter:** kumulierte GDD, Niederschlagssumme, Wasserbilanz, Hitzetage, VPD, RZWSI (je bis *t* und letzte 30 Tage).
- **Bodenfeuchte:** ERA5-Land Schichten 1–3, Anomalie zum Klimamittel der Dekade.
- **Boden & Gelände:** statisch.
- **Feldhistorie:** Vorfrucht, Mittel `I_Aug` früherer Maisjahre (ohne Testjahr), Anzahl Maisjahre.
- **Kontext:** Gemeinde-`I_normal`, Höhe, Lage.

Modelle (alle mit LOYO):
| Code | Modell |
|---|---|
| B0 | Klimatologie: `I_pred = I_normal` |
| B1 | Persistenz: aktuelle Anomalie zum Stichtag bleibt bis August gleich |
| B2 | LightGBM nur Wetter + Boden |
| M1 | LightGBM alle Features |
| M2 | GRU über Dekadensequenz + statische Features |

Metriken: RMSE, MAE, R² auf `I_Aug`; R² auf VAS; für schweren Stress: PR-AUC, Recall bei 20 % Fehlalarmrate; **Skill** = 1 − RMSE_Modell / RMSE_B0.

**Deliverable:** Ergebnistabelle je Modell × Stichtag; **Frühwarnkurve** (Skill vs. Stichtag).
**Abnahme:** M1 schlägt B0 und B1 in mindestens den späten Stichtagen signifikant (Bootstrap über Felder, 95 %-KI).

---

### Phase 5 – V2: Ablation, Radar, Unsicherheit, Erklärbarkeit (F2)
Aufgaben:
1. **Sentinel-1** ergänzen (VV, VH, VH/VV in dB, Dekaden-Mittel; Orbit als Feature).
2. **Ablation** (M1 jeweils neu trainiert):

| Variante | Features |
|---|---|
| A | Wetter |
| B | Wetter + Boden |
| C | Wetter + Bodenfeuchte/RZWSI |
| D | Wetter + S2 |
| E | Wetter + S1 |
| F | Wetter + S1 + S2 |
| G | alles ohne Bodenfeuchte |
| H | alles ohne Feldhistorie |
| I | alles |

3. **Unsicherheit:** Quantil-LightGBM + Split-Conformal; prüfen, ob 80-%-Intervalle ~80 % abdecken (Coverage-Plot).
4. **SHAP:** globale Wichtigkeit + Top-3-Faktoren je Feld als Text („anhaltende Wurzelzonen-Trockenheit“, „NDRE-Rückgang letzte 3 Dekaden“, …).
5. Optional: SPARTACUS-1-km-Wetter statt ERA5-Land (Ablation „Wetterauflösung“).

**Deliverable:** Ablationsgrafik, Coverage-Plot, SHAP-Summary.
**Abnahme:** Jede Variante mit KI; Coverage innerhalb ±5 Prozentpunkte.

---

### Phase 6 – V3: Brücke zum Ertrag & Feld-Transfer (F3, F4b)
Aufgaben:
1. **Österreich-Stichprobe:** je Bundesland mit relevantem Körnermais (u. a. Stmk, OÖ, NÖ, Bgld, Ktn) und Jahr 2018–2025 bis zu 1.000 Felder durch dieselbe Pipeline.
2. **F3:** flächengewichteter Mittel-VAS je Bundesland-Jahr (und je CY-Bench-Region, wo Jahre überlappen) ↔ YAS aus Statistik Austria / CY-Bench. Pearson + Spearman, Bootstrap-KI, Streudiagramm. Zusätzlich: *vorhergesagter* VAS zum 1.7. ↔ YAS.
3. **F4b:** M1 nur auf Steiermark trainiert → Test auf anderen Bundesländern ohne Nachtraining (Zero-Shot); dann Few-Shot mit k = 50, 100, 250, 500 Feldern aus dem Zielbundesland.
4. Fehleranalyse: Bewässerung (Marchfeld), kleine Felder, Hanglagen, wolkenreiche Jahre.

**Deliverable:** Korrelationsgrafik Feld-Score ↔ Ertrag; Transfer-Tabelle; Fehleranalyse.
**Abnahme:** Ergebnis wird so berichtet, wie es ist — auch ein schwacher Zusammenhang ist ein Befund (n Region-Jahre und KI angeben).

---

### Phase 7 – Demo-App
- Streamlit-Karte der Steiermark, Felder eingefärbt nach Kategorie: 🟢 VAS ≥ 0,95 · 🟡 0,85–0,95 · 🟠 0,75–0,85 · 🔴 < 0,75 (vorhergesagt).
- **Datums-Slider** (Stichtage) – zeigt nur, was zu diesem Datum bekannt war (vorab berechnete as-of-Vorhersagen).
- Klick auf Feld: NDRE-Kurve vs. Normal, Vorhersage mit Unsicherheitsband über die Stichtage, Niederschlag/Temperatur/RZWSI, Top-3-SHAP-Faktoren, Sentinel-2-Echtfarb-Thumbnail (GEE `getThumbURL`).
- Jahr wählbar (Testjahre aus LOYO → ehrliche Out-of-Sample-Vorhersagen).

**Abnahme:** App startet mit `streamlit run app/streamlit_app.py` aus vorberechneten Dateien, ohne GEE-Zugang.

---

### Phase 8 – Wissenschaftliche Aufbereitung & Abgabe
1. **Dokumentation** entlang der Bewertungskriterien:
   - Motivation & Relevanz (Landwirte, Kammer, Versicherung, AMA, Ministerium)
   - Stand der Forschung: CY-Bench, JRC MARS (regionale EU-Prognosen), SCYM (Feldertrag aus Simulationen), Leave-One-Country-Out-Studien; Abgrenzung
   - Daten & Lizenzen, Pipeline, Definitionen (Abschnitt 3), Leakage-Schutz
   - Experimente F1–F4, Ergebnisse mit Konfidenzintervallen
   - **Fehlerquellen & Grenzen** (Vegetationszustand ≠ Ertrag, Wolken, 9-km-Wetter, Bewässerung, Korrelation ≠ Kausalität)
   - Ausblick: internationale Feld-Ertragsdaten (One Acre Fund, US-Yield-Monitor), Kooperation Hagelversicherung/BOKU für echte Feld-Labels, Few-Shot-Kalibrierung
   - Unterstützung (aus `SUPPORT.md`)
2. **Video-Pitch** 3–5 min: Problem (10 %) → Idee „Bilder lernen aus Bildern“ (20 %) → Demo mit Zeitreise (35 %) → Hauptergebnis Frühwarnkurve + Ertragsbezug (25 %) → Ausblick (10 %).
3. **Code:** README mit Reproduktionsschritten, Tests grün, Lizenz.

---

## 6. Qualitätsregeln (gelten immer)

1. **Kein zufälliger Split** von Feld-Jahren — immer LOYO oder räumliche Blöcke.
2. **Keine Normalwerte, Schwellen oder Hyperparameter aus dem Testjahr.** Hyperparameter-Tuning nur innerhalb der Trainingsjahre (verschachtelt).
3. Jede Zahl in der Doku kommt aus einem Skript; Abbildungen werden per Code erzeugt.
4. Zufalls-Seeds fixiert in `config.yaml`.
5. Jede Abweichung → `DECISIONS.md`. Jede Hilfe → `SUPPORT.md`.

---

## 7. Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Wolken in der Steiermark → Lücken | Dekaden + Interpolation + Masken; Radar ab V2; `I_Aug` nur bei ≥ 2 beobachteten Dekaden |
| GEE-Exporte langsam / Quoten | erst Stichprobe 5.000 Felder/Jahr; Export je Jahr getrennt |
| Feld-IDs über Jahre unsauber | IoU-Matching + Test; Feldhistorie ist optionales Feature (Ablation H) |
| NDVI-Sättigung | NDRE als Hauptindex |
| Zusammenhang Feld-Score ↔ Ertrag schwach (F3) | ehrlich berichten; Regionalmodell (Phase 1) liefert unabhängig ein Ertragsergebnis |
| Wenige Region-Jahre für F3 | ganz Österreich + Bootstrap-KI; CY-Bench-Regionen wo möglich |
| Modell lernt nur „Jahr“ statt Feld | Vergleich mit B0/B1; Auswertung *innerhalb* eines Jahres (Rang-Korrelation zwischen Feldern) zusätzlich berichten |

---

## 8. Was der Projektinhaber selbst erledigen muss
- Anmeldung zum Wettbewerb.
- Google-Earth-Engine-Konto + Cloud-Projekt anlegen und `earthengine authenticate` im Browser bestätigen.
- Ggf. Downloads bestätigen, für die eine Anmeldung nötig ist.

## 9. Bewusst *nicht* Teil dieses Plans (Ausblick)
- Internationale Feld-Ertragsdaten (One Acre Fund Afrika, USDA BARC, Kellogg Biological Station) als zweite Transferstufe.
- Echte österreichische Feld-Erträge (Kooperationen).
- Kausalanalyse der Stressursachen.
- Klassifikation der Stressart (Dürre/Hagel/Staunässe) – nur als Fallstudien in Phase 3.
