# CropTransfer AT – Arbeitsplan

> Früherkennung von Stress und Ertragsverlust auf einzelnen Maisfeldern aus Satelliten-Zeitreihen, Wetter und Boden: **vollständig gelernt an Feldern mit gemessenem Ertrag** (USA, viele Jahre), dann **eingefroren** und **ohne jede Anpassung in Österreich getestet**. Österreich ist der Beweis, ob der Algorithmus gut genug ist – nicht Trainingsgebiet.

Dieser Plan ist so geschrieben, dass er Schritt für Schritt abgearbeitet werden kann. Jede Phase hat: **Ziel → Aufgaben → Ergebnis (Deliverable) → Abnahmekriterium**. Alle technischen Entscheidungen sind in Abschnitt 2 festgelegt; Abweichungen werden in `DECISIONS.md` begründet. Wie gearbeitet wird, regelt `AGENTS.md`.

---

## 0. Kernidee

1. Ein Maisfeld „sieht man“ im Satelliten als **Kurve über die Saison** (NDVI, NDRE, Wassergehalt …) – gesund = grün, dicht, chlorophyllreich; Stress = Kurve bleibt flach oder fällt früh ab.
2. **Alle heruntergeladenen Ertragsdaten werden zuerst sauber aufbereitet** (Phase 1): Maisfeld × Jahr × gemessener Ertrag × Satellitenkurve × Wetter × Boden/Gelände. Quellen: Kellogg Biological Station (KBS), USDA Beltsville (BARC), Colorado, ggf. Mead. Wenige Felder × viele Jahre: Von Jahr zu Jahr ändern sich vor allem Wetter und Stress – genau das Signal, das wir brauchen.
3. **Darauf werden mehrere Basismodelle trainiert** (Phase 2), die je einen Blickwinkel haben – nur Satellit, nur Wetter, nur Boden/Gelände, Kombination – und gemeinsam beantworten: **Welche Faktoren bestimmen, wie viel geerntet wird?** Zusätzlich innerhalb der Felder: Wo im Feld fehlt Ertrag und warum (Ertragskarten)?
4. **Erst wenn das funktioniert, wird daraus Problemfeld-Erkennung** (Phase 3): gefährdete Felder und Problemzonen früh in der Saison finden und die wahrscheinliche Ursache eingrenzen (Trockenheit, Hitze, Nässe, abrupter Schaden).
5. **Einfrieren** (Phase 4): Erfüllen die Modelle das vorab festgelegte Kriterium „stark genug“, werden Modelle, Merkmale, Schwellen und das Österreich-Testprotokoll unveränderlich festgehalten (Git-Tag + Prüfsummen).
6. **Der Beweis in Österreich** (Phasen 6–7): Die eingefrorenen Modelle werden auf steirische und österreichische INVEKOS-Maisfelder angewendet und gegen **offizielle österreichische Regionalerträge** und – falls beschaffbar – **Erträge österreichischer Landwirt:innen** geprüft. Keine österreichische Zahl fließt vorher in Training, Merkmalsauswahl oder Schwellen ein.
7. Ein Regionalmodell (CY-Bench, Phase 5) prüft parallel und unabhängig den Transfer andere EU-Länder → Österreich.

> **Wichtig:** Trainiert wird **pro Feld** – nichts wird dafür gemittelt. Regionale Mittelwerte dienen in Österreich nur der **Kontrolle**.
> **Österreich-Regel:** Bis zum Einfrieren (Phase 4) werden keine österreichischen Satelliten- oder Ertragsdaten ausgewertet. Danach wird nichts mehr am Modell geändert (Ausnahme: dokumentierter Fehler → neuer Freeze, beide Ergebnisse werden berichtet).

---

## 1. Forschungsfragen

| ID | Frage | Haupt-Experiment | Phase |
|---|---|---|---|
| **F0** | Wie gut sagen Satellitenkurve, Wetter und Boden den **gemessenen Feldertrag** voraus – und ab welchem Zeitpunkt der Saison? | Basismodelle, Test mit ausgelassenen Feldern + Jahren | 2 |
| **F1** | **Welche Faktoren bestimmen den Ertrag** – zwischen Jahren, zwischen Feldern und innerhalb eines Feldes? Was trägt Satellit, Wetter, Boden/Gelände jeweils bei? | Modellfamilie + Ablation + SHAP; Ertragskarten | 2 |
| **F2** | Wie früh und wie zuverlässig erkennt man **gefährdete Felder und Problemzonen**, und lässt sich die wahrscheinliche Ursache eingrenzen? | Klassifikation „gefährdet“, Referenzkurve gesunder Mais, Ursachen-Zuordnung | 3 |
| **F3** | **Der Beweis:** Funktioniert das eingefrorene US-Modell in Österreich ohne Anpassung – regional und (wo Daten vorhanden) pro Feld? Ab welchem Stichtag? Steiermark und andere Bundesländer? | Vorhersage ↔ österreichischer Ertrag, vorab registriertes Protokoll | 7 |
| **F4** | Unabhängige Gegenprobe: regionaler Transfer EU → Österreich (CY-Bench), Zero-Shot. | Regionalmodell | 5 |
| *F5* | *Zusatz, nicht Teil des Beweises:* Wie viel bringt Anpassung mit österreichischen Daten (Few-Shot, selbstüberwachtes Feldmodell, Radar)? | Few-Shot, selbstüberwacht | 8 |

**Ehrliche Grenzen (stehen so in der Doku):** Der Zusammenhang Kurve → Ertrag wird an US-Feldern gelernt; ob er in Österreich gilt, ist genau die Frage F3 und wird nur so weit behauptet, wie die österreichischen Prüfungen es stützen. „Problemfeld“ heißt messbarer Ertragsverlust gegenüber dem eigenen Normalniveau – Krankheiten oder Schädlinge können ohne entsprechende Labels **nicht** von anderen Ursachen unterschieden werden.

---

## 2. Festgelegte technische Entscheidungen

| Thema | Entscheidung | Begründung | Später optional |
|---|---|---|---|
| **Ertrags-Datensatz (Feld-Labels)** | **KBS LTER** (MCSE-Parzellen, Ertragspunkte, Scale-up), **USDA BARC** (Ertragskarten 2014, 2016–2021), **Colorado-Trockenfarm** (2019–2022); **Mead US-Ne1/2/3** nach Klärung der Ertragsdaten | offen, Mähdrescher-gemessen, viele Jahre pro Feld | weitere öffentliche Ertragskarten; One Acre Fund |
| Trainingsgebiet | **ausschließlich Ertrags-Datensatz USA** (+ EU-Regionen für das Regionalmodell) | Österreich bleibt unberührter Testfall | – |
| Region Österreich (Test, Feldebene) | **Steiermark** (alle Körnermaisfelder) | viel Körnermais, kaum Bewässerung, Hagel + Trockenstress | – |
| Region Österreich (Test, regional) | **ganz Österreich, Stichprobe** | Steiermark allein = zu wenige Region-Jahre | – |
| Kultur | **nur Körnermais**; in Österreich Silomais ausgeschlossen | Silomais früh geerntet → verfälscht Spätsaison | Silomais als Vergleich |
| Jahre | Ertrags-Datensatz **2013–2025 (HLS)**, zusätzlich **KBS-Jahre vor 2013** über Landsat 5/7, falls die Harmonisierungsprüfung besteht (Phase 1); Österreich **2018–2025** | „alle Daten nutzen“: verdreifacht die KBS-Feld-Jahre; HLS ab 2013; stabile S2-Abdeckung AT ab 2018 | – |
| Satellit lange Reihen | **HLS v2** (`NASA/HLS/HLSL30/v002` + `NASA/HLS/HLSS30/v002`), 30 m, Fmask; vor 2013 **Landsat 5/7 Collection 2 L2**, auf HLS-L30 harmonisiert | Landsat 8/9 + Sentinel-2 harmonisiert → 10+ Jahre, ~2–3 Tage | – |
| Satellit hochaufgelöst | **Sentinel-2 L2A** `COPERNICUS/S2_SR_HARMONIZED` (10–20 m) + **Cloud Score+** `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`, `cs_cdf ≥ 0.60` | Red-Edge (NDRE) nur bei S2; kleine Felder; Problemzonen im Feld | Schwelle tunen |
| Gemeinsame Basis für Transfer | **Hauptmodell nutzt nur Merkmale, die in USA und Österreich identisch berechenbar sind** (HLS, ERA5-Land, SoilGrids, Copernicus-DEM) | gleiches Produkt → Modell direkt übertragbar | – |
| Radar | **Sentinel-1 GRD** `COPERNICUS/S1_GRD` (VV, VH) – nur Phase 8 | wolkenunabhängig | – |
| Wetter | **ERA5-Land Daily** `ECMWF/ERA5_LAND/DAILY_AGGR` – für US- und AT-Felder gleich | global konsistent, inkl. Bodenwasser | GeoSphere **SPARTACUS** 1 km für AT (Phase 8) |
| Boden | **SoilGrids 250 m** + nutzbare Feldkapazität (Saxton & Rawls 2006) | global konsistent | österreichische eBOD |
| Gelände | **Copernicus DEM GLO-30** → Höhe, Neigung, Nord-/Ostexposition, **TPI**, TWI | in GEE; TPI erklärt Ertragsmuster im Feld (Colorado-Studie) | 10-m-DGM Österreich |
| Felder Österreich | **INVEKOS Schläge** (AMA, GeoPackage, CC BY 4.0) | offizielle Feldgrenzen + Kultur | – |
| Regionalerträge | **CY-Bench** (AT + EU) + **Statistik Austria** (Körnermais, Bundesland) | harmonisiert / offiziell | – |
| Rechenplattform | **Google Earth Engine** (Python API), Export CSV → Google Drive | serverseitig | – |
| Zeitraster | **Dekaden** (10 Tage), 1. April – 31. Oktober; zusätzlich Variante mit **Wärmesummen-Achse (GDD)** | Dekaden glätten Wolkenlücken; GDD-Achse gleicht Unterschiede im Anbaukalender US ↔ AT aus | – |
| Indizes | NDVI, EVI, GNDVI, NDMI, SAVI (HLS + S2); **NDRE** nur S2 | Red-Edge fehlt bei Landsat | MTCI |
| Ertrags-Zielgröße | **relativer Ertrag RY** (3.6) primär; absoluter Ertrag t/ha sekundär (dort zählt Boden) | RY entfernt Standortniveau → übertragbar | – |
| „Gefährdet“ | **RY < 0,85** | ≥ 15 % unter eigenem Normalniveau | – |
| Satelliten-Stressindikator | Kandidaten **K1–K5** (3.3); Auswahl in **Phase 3 nur mit US-Daten** | Karte „Gesundheit jetzt“ + Phase 8 | Seneszenz-Datum |
| Stichtage | **1.6., 15.6., 1.7., 15.7., 1.8., 15.8., 1.9.** (Phase 8 selbstüberwacht: 15.5.–15.7.) | Ertrag am Saisonende → Stichtage bis Sept. | – |
| Modelle | **Modellfamilie** (Phase 2): je Merkmalsgruppe ein Modell + Kombination; **Ridge + flaches LightGBM** (max_depth ≤ 3) | wenige Feld-Jahre → einfache, robuste Modelle | GRU nur Phase 8 |
| Validierung USA | **LOFYO** (Feld *und* Jahr ungesehen) primär; LOFO, LOYO, Leave-One-Dataset-Out sekundär; Tuning verschachtelt | verhindert Auswendiglernen von Feldern/Jahren | – |
| Validierung Österreich | **eingefrorenes Modell, keine Anpassung**; vorab registriertes Protokoll (Phase 4) | echter Beweis statt nachträglicher Anpassung | – |
| Unsicherheit | **Split-Conformal** + LightGBM-Quantile (q10/q50/q90), **kalibriert auf US-Daten** | Coverage in AT ist selbst ein Testergebnis | – |
| Erklärbarkeit | **SHAP** (TreeExplainer) + Gruppen-Ablation | Faktoren global und pro Feld | – |
| Demo | **Streamlit + Folium/PyDeck** mit Datums-Slider | einfach, interaktiv | – |
| Sprache | Python 3.11; Code-Kommentare & README englisch, Doku deutsch | – | – |

---

## 3. Definitionen (verbindlich)

### 3.1 Feld & Feldhistorie
- **Österreich:** Feld-Jahr = INVEKOS-Schlag mit Körnermais in Jahr *y*. Filter: Fläche ≥ 1,0 ha; nach Innenpuffer −10 m mindestens 50 S2-Pixel; Geometrie gültig. Feld-ID über Jahre per Geometrie-Überlappung (**IoU ≥ 0,7**) → `field_uid`, inkl. Fruchtfolge.
- **Ertrags-Datensatz:** Feld-Jahr = Feld/Parzelle/Teilfläche mit Mais in Jahr *y* und gemessenem Ertrag. Feldgrenze aus den Quell-Geodaten; falls nicht vorhanden: konvexe Hülle der Ertragspunkte bzw. Rasterumriss. Immer Innenpuffer −10 m (Vorgewende, Randeffekte). Mindestens 5 HLS-Pixel (30 m) nach Puffer, sonst nur S2-Auswertung.

### 3.2 Satellitenbeobachtung pro Feld
- Pro Szene: Median aller klaren Pixel im gepufferten Feld je Band + `clear_frac`.
- Gültig, wenn `clear_frac ≥ 0.7`.
- **Dekaden-Komposit:** Median der gültigen Beobachtungen je Dekade; fehlende Dekaden linear interpoliert innerhalb der Saison, plus `is_observed` und `days_since_last_obs`.
- HLS, Landsat 5/7 und S2 werden **getrennt** gespeichert (`sensor`-Spalte); Merkmale mit Suffix `_hls` / `_s2`.

### 3.3 Satelliten-Stressindikatoren (Kandidaten K1–K5)

| Kürzel | Definition | Gültig, wenn | Anwendbar |
|---|---|---|---|
| K1 `I_Aug` | Mittel des Index in den Dekaden 1.8.–31.8. | ≥ 2 der 3 Dekaden beobachtet | Regionen mit ähnlichem Anbaukalender |
| K2 `I_postpeak` | Mittel in den 40 Tagen nach dem Maximum der geglätteten Saisonkurve | ≥ 2 Beobachtungen im Fenster | überall |
| K3 `peak` | Maximum der geglätteten Kurve | Beobachtung ±15 Tage um das Maximum | überall |
| K4 `I_season` | Integral über Grundniveau vom Aufgang bis zur Abreife | ≥ 60 % der Saisondekaden beobachtet | überall |
| K5 | K1–K4 mit anderem Index (NDVI, EVI; NDRE wo S2) | wie dort | überall |

- Verwendung: als Merkmale (bis Stichtag) in Phase 2, als gewählter Indikator `Z` für die Karte „Gesundheit jetzt“ und für Phase 8.
- `Z_normal(field, y)` = Median von `Z` aller Körnermais-Feld-Jahre derselben **Gemeinde** in den **anderen** Jahren → `VAS = Z / Z_normal` (nur Phase 8).
- **Frühernte-Regel:** abrupter Abfall auf Boden-Niveau vor/im Zielfenster → `harvested_early`, **nicht** als Stress gewertet.

### 3.4 Regionaler Ertrags-Anomalie-Score
- `YAS(region, y) = Ertrag(y) / Erwartung(y)`, Erwartung = **olympischer Durchschnitt der 5 Vorjahre** (ohne Max/Min). Nur Vorjahre → kein Leakage.

### 3.5 As-of-Regel (Leakage-Schutz)
Für Stichtag *t* darf ein Feature nur Daten mit Zeitstempel ≤ *t* nutzen. Durchgesetzt durch `features.build(cutoff=t)` mit Assertion **und** Unit-Test.

### 3.6 Feld-Ertrag (Ertrags-Datensatz)
- **Einheit:** Körnermais in **t/ha bei 15,5 % Kornfeuchte** (US-Standard); jede Quelle wird darauf umgerechnet, Umrechnung in `DATA_SOURCES.md`.
- **Feld-Ertrag `Y`:** Mittel der bereinigten Ertragspunkte im gepufferten Feld (bzw. offizieller Parzellenwert, z. B. KBS Tabelle 51). Bereinigung (falls Quelle nicht schon bereinigt): Punkte außerhalb 1–25 t/ha und außerhalb ±3 SD je Feld-Jahr entfernen; Anteil entfernter Punkte protokollieren.
- **Relativer Ertrag `RY(field, y)` = `Y(field, y)` / Mittel `Y` desselben Feldes in seinen **anderen** Mais-Jahren**; nur definiert, wenn ≥ 2 andere Mais-Jahre existieren.
- **Gefährdet:** `RY < 0.85`.
- **Innerhalb des Feldes:** Ertragspunkte werden auf das HLS-Raster (30 m) und das S2-Raster (10 m) gemittelt → Pixel-Paare; **relativer Pixel-Ertrag** = Pixel-Ertrag / Feldmittel desselben Feld-Jahres. **Problemzone** = zusammenhängende Pixel mit relativem Pixel-Ertrag < 0,85.
- **Bewässerung** (z. B. Mead US-Ne1/Ne2) als Spalte `irrigated`; wird getrennt ausgewertet.

### 3.7 „Stark genug“ und Einfrieren
- Das Kriterium „stark genug“ (Phase 4) ist **jetzt** festgelegt und wird nicht nachträglich geändert.
- **Freeze** = Modelldateien, Merkmalsliste, Vorverarbeitung, Schwellen, Conformal-Quantile, gewählter Indikator und Österreich-Testprotokoll mit SHA-256-Prüfsummen in `reports/freeze_protocol.md`, Git-Tag `freeze-<n>`.

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
│  ├─ gee_extract.py           # HLS, Landsat 5/7, S2, S1, ERA5-Land, SoilGrids, DEM → Exporte
│  ├─ timeseries.py            # Wolkenfilter, Indizes, Dekaden, GDD-Achse, Interpolation
│  ├─ features.py              # As-of-Feature-Builder (Merkmalsgruppen S, W, B, H)
│  ├─ targets.py               # Y, RY, Pixel-RY, K1–K5, Z_normal, VAS, YAS
│  ├─ splits.py                # LOFYO, LOFO, LOYO, Leave-One-Dataset-Out, räumliche Blöcke
│  ├─ models/
│  │  ├─ baselines.py
│  │  ├─ family.py             # Modellfamilie je Merkmalsgruppe + Kombination
│  │  ├─ within_field.py       # Pixel-Modell für Problemzonen
│  │  └─ gru.py                # nur Phase 8
│  ├─ stress.py                # gefährdet-Klassifikation, Referenzkurve, Ursachen-Zuordnung
│  ├─ freeze.py                # Einfrieren + Prüfsummen + Laden des eingefrorenen Modells
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
   ├─ test_splits.py
   └─ test_freeze.py
```

---

## 5. Phasen

**Reihenfolge-Prinzip:** Erst **alle** Ertragsdaten aufbereiten (Phase 1), dann lernen, **was den Ertrag bestimmt** (Phase 2), dann daraus **Problemfelder erkennen** (Phase 3). Erst wenn das Modell vorab festgelegt „stark genug“ ist, wird es **eingefroren** (Phase 4). Danach – und erst danach – kommt **Österreich als Beweis** (Phasen 6–7). Das Regionalmodell (Phase 5) läuft als unabhängige Gegenprobe parallel.

```
Phase 0 Setup ─┬─► 1 Daten aufbereiten ─► 2 Basismodelle: Was bestimmt den Ertrag? ─► 3 Problemfelder erkennen
               │                                                                              │
               │                                                       4 „Stark genug?“ ─► EINFRIEREN
               │                                                                              │
               │                                  6 Österreich-Daten aufbereiten ◄────────────┘
               │                                                │
               │                                  7 DER BEWEIS: Test in Österreich ─► 8 Zusatz (optional) ─► 9 Demo ─► 10 Abgabe
               └─► 5 CY-Bench-Regionalmodell (parallel, unabhängige Gegenprobe) ─────┘
```

### Phase 0 – Setup & Datenzugang
**Ziel:** Umgebung steht, jede Datenquelle ist nachweislich erreichbar.

Aufgaben:
1. Python-Umgebung: `python -m venv .venv`; Pakete `earthengine-api geemap geopandas pyogrio shapely rasterio pandas numpy scipy pyarrow lightgbm scikit-learn shap torch matplotlib seaborn streamlit folium streamlit-folium pyyaml pytest tqdm` → `requirements.txt` mit fixierten Versionen.
2. Paketstruktur `src/croptransfer/`, `config.yaml`, erster Test, **GitHub Actions** (`pytest` bei jedem Push).
3. **GEE:** Konto + Cloud-Projekt (*Projektinhaber*), dann `earthengine authenticate`. Test: Anzahl HLS- und S2-Szenen über Graz und über Hickory Corners (KBS) im Juli 2022.
4. **Ertrags-Datensätze herunterladen und sichten:** KBS (Tabellen 51, 185, 828, Scale-up 145/163/254, GIS), BARC (Ertragsarchiv + `BARCFarmMgmt.zip`), Colorado, Mead (AmeriFlux-BADM, *Konto: Projektinhaber*). Je Datensatz in `DATA_SOURCES.md`: Lizenz, Jahre, Anzahl **Mais**-Feld-Jahre, Feldgrößen, Koordinatensystem, Messmethode, Einheit/Feuchte.
5. **INVEKOS** Schläge 2018–2025; Spalte der Nutzungsart verifizieren. *(Nur Download und Schema – keine Auswertung, siehe Österreich-Regel.)*
6. **Verwaltungsgrenzen** AT (Bundesländer, Bezirke, Gemeinden).
7. **CY-Bench**: Ebene von AT (NUTS-2/3?), Jahre, Prädiktoren.
8. **Statistik Austria:** Körnermais-Hektarerträge je Bundesland 2010–2025 → `data/raw/stat_at_maize.csv`.

**Deliverable:** `notebooks/00_data_access.ipynb`, `DATA_SOURCES.md` vollständig.
**Abnahme:** Jede Quelle liefert Daten oder ist begründet als „nicht verfügbar / angefragt“ markiert; Tests laufen in GitHub Actions.

---

### Phase 1 – Alle Ertragsdaten aufbereiten (Grundlage)
**Ziel:** **Ein** sauberer, reproduzierbarer Datensatz aus **allen** heruntergeladenen Ertragsdaten: Maisfeld × Jahr × gemessener Ertrag × Satellitenkurve × Wetter × Boden/Gelände – plus Ertragskarten innerhalb der Felder.

Aufgaben:
1. `groundtruth.py`: KBS, BARC, Colorado (+ Mead sobald verfügbar) in ein Schema überführen:
   - `gt_field_years`: `dataset, field_id, year, crop, geometry, Y_t_ha, n_points, irrigated, moisture_basis, source`
   - `gt_yield_points`: `dataset, field_id, year, x, y, yield_t_ha` (innerhalb des Feldes; BARC: 5-m-Kriging-Raster)
   Nur Mais-Feld-Jahre; Umrechnung auf 15,5 % Feuchte; Bereinigung nach 3.6; alle Auffälligkeiten aus `DATA_SOURCES.md` (Einheitenfehler, Doppelkultur, Feld-ID-Wechsel, KBS-Ernte Osthälfte bis 2016) behandelt und protokolliert.
2. `RY` und relativer Pixel-Ertrag berechnen (3.6); Verteilung je Datensatz; Anteil „gefährdet“.
3. Satellitenkurven je Feld-Jahr über GEE: **HLS 2013–2025**, **S2 2017–2025**.
4. **Datenerweiterung „alle Daten“:** KBS-Mais-Jahre vor 2013 (MCSE 1989–2012, Scale-up 2006–2012) mit **Landsat 5/7**. Vorher Harmonisierungsprüfung: Landsat 7 vs. HLS-L30 auf denselben Feldern in den Überlappjahren 2013–2021 (Abweichung je Index). Nur wenn die Abweichung klein ist (Grenze vor der Prüfung in `DECISIONS.md` festlegen), werden diese Jahre aufgenommen – mit `sensor`-Spalte; Hauptergebnisse werden immer auch **nur mit HLS-Jahren** berichtet.
5. Wetter (ERA5-Land täglich am Feldzentroid → Dekaden: GDD Basis 10 °C/Deckel 30 °C, Hitzetage > 30/32 °C, Niederschlag, klimatische Wasserbilanz, VPD, Bodenwasser Schicht 1–3), **Wurzelzonen-Wasserstress-Index (RZWSI)** (FAO-56-Bucket mit nutzbarer Feldkapazität), SoilGrids, DEM (Höhe, Neigung, Exposition, TPI, TWI) – für Feld **und** Pixel.
6. **Ansehen:** Je Datensatz Kurven der besten und schlechtesten RY-Jahre desselben Feldes übereinander – sieht man den Unterschied, und ab wann?
7. Erste Zusammenhänge: Spearman ρ zwischen K1–K5 (je Index, je Sensor) und `Y` bzw. `RY`, je Datensatz und gepoolt, Bootstrap-KI über Felder; innerhalb der Felder Median-ρ Pixel-Index ↔ Pixel-Ertrag je Saisonzeitpunkt.

**Deliverable:** `data/processed/gt_field_years.parquet`, `gt_yield_points.parquet`, `gt_dekads.parquet`, `gt_static.parquet`, `gt_pixels.parquet`; `notebooks/01_groundtruth.ipynb`; Datenkritik-Bericht.
**Abnahme:** Datensatz reproduzierbar per Befehl (`python -m croptransfer.groundtruth`); Anzahl Mais-Feld-Jahre je Datensatz und Sensor dokumentiert; jede ausgeschlossene Zeile mit Grund protokolliert.

---

### Phase 2 – Basismodelle: Was bestimmt den Ertrag? (F0, F1)
**Ziel:** Auf **allen** aufbereiteten Daten mehrere Modelle trainieren, die je einen Blickwinkel haben, und daraus verstehen, welche Faktoren den Ertrag bestimmen. Ergebnis ist ein Hauptmodell-Kandidat für die Problemfeld-Erkennung.

**Merkmalsgruppen** (as-of Stichtag *t*):
- **S – Satellit:** Dekadenwerte bis *t* (Kalender- und GDD-Achse), Steigungen, Maximum bis *t*, Fläche unter Kurve, K1–K5 soweit bis *t* berechenbar.
- **W – Wetter:** GDD, Niederschlag, Wasserbilanz, Hitzetage (gesamt und um die Blüte), VPD, RZWSI, Bodenwasser – bis *t*.
- **B – Boden & Gelände:** SoilGrids (Textur, org. Kohlenstoff, nFK), Höhe, Neigung, Exposition, TPI, TWI.
- **H – Feldhistorie:** Vorfrucht (nur wo in US **und** AT verfügbar; sonst nicht im Hauptmodell).

**Modellfamilie** (jeweils Ridge + flaches LightGBM):

| Code | Modell | Frage, die es beantwortet |
|---|---|---|
| B0 | `RY = 1` | Baseline „normales Jahr“ |
| B1 | Ridge auf einem Index-Merkmal (NDVI-Maximum bis *t*) | Wie weit kommt man mit einer Zahl? |
| M-S | nur Satellit | Wie viel verrät die Kurve allein? |
| M-W | nur Wetter | Wie viel erklärt das Wetter allein? |
| M-B | nur Boden & Gelände | Erklärt der Standort den Ertrag? (v. a. für absoluten Ertrag `Y` und innerhalb des Feldes) |
| M-WB | Wetter + Boden | Erklärt das Zusammenspiel *warum* (ohne Satellit)? |
| M-alle | S + W + B (+ H) | Hauptmodell-Kandidat |

Aufgaben:
1. `features.py` mit Merkmalsgruppen und As-of-Regel; `models/family.py`.
2. Alle Modelle × alle Stichtage × Zielgrößen `RY` (primär) und `Y` (sekundär). Splits: **LOFYO** (primär), LOFO, LOYO, **Leave-One-Dataset-Out**. Hyperparameter nur verschachtelt.
3. **Innerhalb des Feldes** (`models/within_field.py`): relativer Pixel-Ertrag aus S2-Pixelkurve (10 m) + Gelände (TPI, TWI, Neigung) + SoilGrids; Validierung: ganzes Feld-Jahr ausgelassen. Frage: Welche Feldteile bringen weniger – und hängt das am Gelände, am Boden oder am Jahr?
4. **Faktorenanalyse:** Gruppen-Ablation (Modell ohne jeweils eine Gruppe), SHAP (global, je Datensatz, je Stichtag), Partial-Dependence für die wichtigsten 5 Faktoren; Kalender- vs. GDD-Achse vergleichen (Auswahl nach Leave-One-Dataset-Out, nur US).
5. Metriken: Spearman ρ, RMSE auf RY, R²; Skill = 1 − RMSE/RMSE_B0; **Frühwarnkurve** (Güte vs. Stichtag); Bootstrap-KI.
6. **Unsicherheit:** Quantil-LightGBM + Split-Conformal, kalibriert auf US-Daten; Coverage-Plot.
7. Kontrolltests nach AGENTS.md §3.3: Label-Shuffle-Test, Leistung innerhalb eines Jahres, mit/ohne Feld-Kennungen, Adversarial Validation zwischen Datensätzen.

**Deliverable:** `notebooks/02_drivers.ipynb`; Tabelle Modell × Stichtag × Split; Frühwarnkurve; Faktoren-Abbildungen (SHAP, Ablation); Ergebnis innerhalb der Felder; Datenkritik-Bericht.
**Abnahme:** Alle Modelle mit KI berichtet; Kontrolltests bestanden oder als Grenze dokumentiert; schriftliche Antwort auf F0 und F1 (auch wenn schwach).

---

### Phase 3 – Problemfelder erkennen (F2)
**Ziel:** Aus den Basismodellen ein Werkzeug machen, das **gefährdete Felder und Problemzonen früh findet** und die wahrscheinliche Ursache eingrenzt – weiterhin nur mit US-Daten.

Aufgaben:
1. **Gefährdet-Klassifikation** (`RY < 0,85`) je Stichtag: (a) Schwelle auf vorhergesagtem RY des Hauptmodell-Kandidaten, (b) direkter Klassifikator (flaches LightGBM). Metriken: PR-AUC (mit Prävalenz als Referenz), Recall bei 20 % Fehlalarmrate; LOFYO; Bootstrap-KI.
2. **Referenzkurve „gesunder Mais“:** Kurven der Feld-Jahre mit RY ≥ 0,95 (nur Trainingsfolds), auf GDD-Achse; Abweichung von der Referenz bis Stichtag *t* als **Stress-Score**. Test: Zeigt der Stress-Score spätere Ertragsverluste an (Spearman, PR-AUC)?
3. **Problemzonen im Feld:** Erkennt das Pixel-Modell (Phase 2.3) die Problemzonen aus den Ertragskarten? (PR-AUC je Pixel, Überlappung der Zonen); ab welchem Stichtag?
4. **Ursache eingrenzen** (`stress.py`): je gefährdetem Feld-Jahr Top-SHAP-Gruppen + vorab festgelegte, einfache Regeln: *Trockenstress* (RZWSI/Wasserbilanz auffällig), *Hitze* (Hitzetage um die Blüte), *Nässe* (Niederschlagsüberschuss im Frühjahr), *abrupter Schaden* (plötzlicher Einbruch der Kurve → Hagel-/Sturm-/Lager-Verdacht), sonst *Ursache unklar*. Krankheiten/Schädlinge werden **nicht** behauptet. Plausibilität an Fallstudien und Wetterarchiv prüfen.
5. **Satelliten-Stressindikator wählen** (K1–K5, nur US-Daten): höchster Median-ρ mit RY über die Datensätze; bei Differenz < 0,05 der einfachere (K1 < K3 < K2 < K4; NDVI < EVI < NDRE). Voraussetzung: ρ ≥ 0,4 (gepoolt oder in mindestens einem Datensatz, KI angeben) – sonst wird kein Indikator festgelegt und die Karte nutzt nur den vorhergesagten RY.

**Deliverable:** `notebooks/03_problem_fields.ipynb`; Frühwarnkurve „gefährdet“; Fallstudien (3 richtig erkannte, 3 verpasste, 3 Fehlalarme); Datenkritik-Bericht.
**Abnahme:** Alle Metriken mit KI; Ursachen-Regeln vor der Auswertung in `DECISIONS.md` festgelegt.

---

### Phase 4 – „Stark genug?“ und Einfrieren
**Ziel:** Vorab festgelegt entscheiden, ob die Modelle nach Österreich dürfen – und sie dann unveränderlich festhalten.

**Kriterium „stark genug“** (vorab festgelegt, nicht nachträglich ändern; alles LOFYO):
1. Das Hauptmodell schlägt **B0 und B1** an mindestens einem Stichtag ab 1.8. signifikant (Bootstrap-KI der RMSE-Differenz ohne 0).
2. **Spearman ρ ≥ 0,4** zwischen vorhergesagtem und gemessenem RY am Stichtag 1.9. (KI angeben).
3. **Leave-One-Dataset-Out:** ρ > 0 in beiden Richtungen KBS → BARC und BARC → KBS (Vorgeschmack auf Transfer).
4. Label-Shuffle-Test fällt auf Baseline-Niveau.

**Wahl des Hauptmodells:** höchster Median-ρ über die LOFYO-Folds am 1.9. unter den Modellen, die nur transferfähige Merkmale nutzen (Abschnitt 2); bei Differenz < 0,05 das einfachere (Ridge < LightGBM; weniger Gruppen < mehr Gruppen).

**Nicht stark genug?** Nicht nach Österreich gehen. Optionen (jede Runde in `DECISIONS.md`): mehr Daten (Mead, Landsat-5/7-Jahre), einfachere Merkmale, engere Frage (nur späte Stichtage), Phase 5 als Hauptergebnis. Weiterentwicklung ist mit US-Daten erlaubt – Österreich bleibt unberührt.

Aufgaben (bei „stark genug“):
1. `freeze.py`: Hauptmodell, Modellfamilie, Gefährdet-Klassifikator, Pixel-Modell, Merkmalsliste, Vorverarbeitung, Schwellen, Conformal-Quantile, Stressindikator speichern; SHA-256 je Datei.
2. **Österreich-Testprotokoll** in `reports/freeze_protocol.md` vorab registrieren: Jahre, Regionen, Stichtage, Metriken, Erfolgskriterien (siehe Phase 7), geplante Fehleranalysen.
3. `test_freeze.py`: geladenes Modell liefert auf Fixture identische Vorhersagen; Prüfsummen stimmen.
4. Git-Tag `freeze-1` (zusätzlich zum Phasen-Tag), Prüfsummen in `DECISIONS.md`.

**Deliverable:** `reports/freeze_protocol.md`, eingefrorene Modelldateien (nicht in Git, Prüfsummen schon).
**Abnahme:** Kriterium erfüllt und dokumentiert; Freeze reproduzierbar; Tag gepusht.

---

### Phase 5 – CY-Bench-Regionalmodell (F4) — *unabhängige Gegenprobe, parallel ab Phase 0*
**Ziel:** Ein vollständiges Ergebnis unabhängig von der Feldpipeline: regionaler Transfer EU → Österreich.

Aufgaben:
1. Mais-Daten EU laden; Prädiktoren je Region-Jahr und Stichtag aggregieren (Mittel/Min/Max/Summe je Monat: tmax, tmin, prec, cwb, rsm, ssm, fpar, ndvi; statisch: awc, Lagerungsdichte).
2. Zielvariable **YAS** (3.4).
3. Baselines: YAS = 1; lineare Trendfortschreibung.
4. LightGBM, trainiert auf **EU ohne Österreich**; Tuning nur innerhalb der EU-Länder (Leave-One-Country-Out). Einfrieren nach demselben Prinzip wie Phase 4, dann **Zero-Shot-Test AT** (Hauptergebnis).
5. Erst danach, klar getrennt (gehört zu F5): In-Domain AT (LOYO), Pooled, Few-Shot (EU + k AT-Jahre, k = 0, 2, 4, 6, 8, alle; 10 Wiederholungen).
6. Vergleich mit publizierter CY-Bench-Baseline für AT (bestes Modell R² 0,13, LOYO).

**Deliverable:** Tabelle + Frühwarnkurve (+ Few-Shot-Kurve als Zusatz).
**Abnahme:** reproduzierbar per `python -m croptransfer.regional_cybench`.

---

### Phase 6 – Österreich-Daten aufbereiten
**Voraussetzung:** Phase 4 abgeschlossen (Freeze).
**Ziel:** Für alle Testfelder dieselben Merkmale berechnen wie in den USA – mit genau der eingefrorenen Pipeline.

Aufgaben:
1. `invekos.py`: Körnermais Steiermark 2018–2025 filtern (3.1), Innenpuffer, Feld-IDs über Jahre (IoU), Fruchtfolge; Österreich-Stichprobe: je Bundesland mit relevantem Körnermais (u. a. Stmk, OÖ, NÖ, Bgld, Ktn) und Jahr bis zu 300 Felder, stratifiziert, Auswahl per Seed.
2. **Pilot zuerst:** 200 steirische Felder × 2 Jahre (vorab anhand Statistik Austria gewählt: ein schwaches, ein normales Jahr) durch die Pipeline; Prüfungen: Kurvenform maistypisch? Frühernte? Datenabdeckung je Monat/Jahr? Abbruch und Klärung, wenn < 80 % maistypisch oder < 70 % der Feld-Jahre ausreichend beobachtet.
3. Danach alle Felder: HLS (+ S2) je Feld, ERA5-Land, SoilGrids, DEM, Merkmale mit der **eingefrorenen** Merkmalsliste.
4. Qualitätsbericht. Filter dürfen nur Datenqualität betreffen (nie Ertrag oder Modellausgabe).

**Deliverable:** `data/processed/at_fields_dekads.parquet`, `at_fields_static.parquet`, `at_features_<stichtag>.parquet`.
**Abnahme:** Pilot-Kriterien erfüllt; Pipeline per Befehl; Abdeckung dokumentiert.

---

### Phase 7 – Der Beweis: Test in Österreich (F3)
**Ziel:** Ehrlich messen, ob das eingefrorene Modell in Österreich funktioniert. **Keine Anpassung.**

Validierungswege:

| Weg | Daten | Ebene |
|---|---|---|
| **V1 – regional** | Statistik Austria (Bundesland) + CY-Bench (feinste verfügbare Ebene) | Region-Jahr |
| **V3 – Feld** | Erträge österreichischer Landwirt:innen, **falls beschafft** | Feld-Jahr (Goldstandard) |

Aufgaben:
1. Eingefrorenes Modell laden (Prüfsummen-Check), für jeden Stichtag auf alle Testfelder anwenden: vorhergesagter RY, Gefährdet-Wahrscheinlichkeit, Unsicherheitsintervall, Ursachen-Zuordnung.
2. **V1:** vorhergesagten RY flächengewichtet je Region-Jahr mitteln ↔ YAS; Pearson + Spearman, Bootstrap-95-%-KI, n angeben; RMSE gegen Baseline YAS = 1; je Stichtag (Frühwarnkurve Österreich).
3. **V3:** wenn Daten vorliegen – wie Phase 2/3 feldweise auswerten (RY, gefährdet, Coverage der Intervalle).
4. **Steiermark vs. andere Bundesländer:** Ergebnis je Bundesland getrennt.
5. **Vergleich:** Feldmodell (regional gemittelt) vs. CY-Bench-Zero-Shot (Phase 5) vs. Baseline.
6. **Verteilungsvergleich US ↔ AT** (Merkmale außerhalb des Trainingsbereichs?) – nur zur Erklärung, nicht zur Anpassung.
7. Fehleranalyse: Bewässerung (Marchfeld), kleine Felder, Hanglagen, wolkenreiche Jahre, Hageljahre.

**Vorab registrierte Erfolgskriterien** (Teil von `freeze_protocol.md`):
- **Bestanden (regional):** Spearman ρ(regional gemittelter vorhergesagter RY, YAS) > 0 mit 95-%-KI ohne 0 am Stichtag 1.9.
- **Stark (regional):** zusätzlich RMSE kleiner als Baseline YAS = 1 (KI der Differenz ohne 0).
- **Bestanden (Feld, falls V3):** Spearman ρ mit Feld-RY > 0 mit KI ohne 0; **stark:** ρ ≥ 0,4.
- Alle Stichtage werden berichtet, nicht nur der beste.

**Deliverable:** `notebooks/07_austria_test.ipynb`; Ergebnistabelle nach Protokoll; Karten; Datenkritik-Bericht.
**Abnahme:** Ergebnisse genau nach Protokoll berichtet – auch wenn nicht bestanden (n und KI angeben).

---

### Phase 8 – Zusatz: Anpassung mit österreichischen Daten (F5, optional)
**Nicht Teil des Beweises** – in der Doku klar getrennt.
1. **Few-Shot** mit V3-Daten (k = 5, 10, 20, alle Feld-Jahre), falls vorhanden.
2. **Selbstüberwachtes Feldmodell** (Steiermark): sagt aus Kurve + Wetter + Boden bis Stichtag den Stressindikator `Z` zur Kornfüllung voraus (`VAS`, 3.3); Modelle B0 Klimatologie, B1 Persistenz, LightGBM, GRU; LOYO + räumliche Blöcke; Vergleich und Kombination mit dem US-Modell.
3. **Sentinel-1-Radar** (VV, VH, VH/VV) als zusätzliche Gruppe; Ablation.
4. **SPARTACUS** 1 km statt ERA5-Land.

**Abnahme:** Jede Variante mit KI; Vergleich zum eingefrorenen Modell.

---

### Phase 9 – Demo-App
- Streamlit-Karte der Steiermark, Felder eingefärbt: 🟢 ≥ 0,95 · 🟡 0,85–0,95 · 🟠 0,75–0,85 · 🔴 < 0,75 (vorhergesagter RY des eingefrorenen Modells).
- **Datums-Slider** – nur, was zu diesem Datum bekannt war (vorberechnete as-of-Vorhersagen).
- Klick auf Feld: Kurve vs. Referenz „gesunder Mais“, Vorhersage mit Unsicherheitsband über die Stichtage, Wetter/RZWSI, wahrscheinliche Ursache, Top-3-SHAP-Faktoren, S2-Echtfarb-Thumbnail.
- Zweiter Reiter: **US-Ertragsfelder** – Kurve, Vorhersage, Ertragskarte mit Problemzonen und tatsächlich gemessener Ertrag nebeneinander.
- Jahr wählbar (nur Out-of-Sample-Vorhersagen).

**Abnahme:** `streamlit run app/streamlit_app.py` läuft aus vorberechneten Dateien, ohne GEE-Zugang.

---

### Phase 10 – Wissenschaftliche Aufbereitung & Abgabe
1. **Dokumentation** entlang der Bewertungskriterien:
   - Motivation & Relevanz (Landwirte, Kammer, Versicherung, AMA, Ministerium)
   - Stand der Forschung: CY-Bench, JRC MARS, SCYM, Feldertrags-Studien mit Mähdrescherdaten + Sentinel-2, Leave-One-Country-Out-Studien; Abgrenzung
   - Daten & Lizenzen, Pipeline, Definitionen, Leakage-Schutz, **Freeze-Protokoll**
   - **Kapitel „Was bestimmt den Ertrag?“** (F0, F1) und **„Problemfelder erkennen“** (F2)
   - **Kapitel „Der Beweis in Österreich“** (F3) + Gegenprobe CY-Bench (F4); Zusatz F5 getrennt
   - **Fehlerquellen & Grenzen** (US ≠ AT, Vegetationszustand ≠ Ertrag, Wolken, 9-km-Wetter, Bewässerung, Korrelation ≠ Kausalität, keine Krankheitsdiagnose)
   - Ausblick: mehr österreichische Feld-Erträge, Kooperationen, Kalibrierung auf t/ha
   - Unterstützung (aus `SUPPORT.md`)
2. **Video-Pitch** 3–5 min: Problem (10 %) → Idee (20 %) → Demo mit Zeitreise (35 %) → Hauptergebnisse Faktoren + Beweis Österreich (25 %) → Ausblick (10 %).
3. **Code:** README mit Reproduktionsschritten, Tests grün, Lizenz.

---

## 6. Qualitätsregeln (gelten immer)

1. **Kein zufälliger Split** von Feld-Jahren – immer LOFYO/LOFO/LOYO oder räumliche Blöcke.
2. **Keine Normalwerte, Schwellen oder Hyperparameter aus Testdaten.** Tuning nur verschachtelt innerhalb der Trainingsdaten.
3. **Österreich-Regel:** keine österreichischen Daten in Training, Merkmalsauswahl, Schwellen oder Modellwahl; nach dem Freeze keine Änderung am Modell.
4. Jede Zahl in der Doku kommt aus einem Skript; Abbildungen per Code.
5. Zufalls-Seeds fixiert in `config.yaml`.
6. Jede Abweichung → `DECISIONS.md`. Jede Hilfe → `SUPPORT.md`. Datenkritik nach jedem großen Schritt (`AGENTS.md` §3).

---

## 7. Risiken & Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Wenige Mais-Feld-Jahre (~170 in der HLS-Zeit; Mais nur jedes 2.–3. Jahr) → Modell nicht „stark genug“ | alle Quellen poolen; KBS-Jahre vor 2013 über Landsat 5/7; Mead; Pixel-Ebene innerhalb der Felder; einfache Modelle; KI immer angeben |
| Modell lernt Felder/Jahre auswendig | LOFYO primär; Label-Shuffle-Test; mit/ohne Feld-Kennungen |
| Versuchung, nach dem Österreich-Test nachzubessern | Freeze mit Tag + Prüfsummen; vorab registriertes Protokoll; neuer Freeze nur bei dokumentiertem Fehler, beide Ergebnisse berichtet |
| US-Felder ≠ steirische Felder (Klima, Sorten, Anbaukalender, Feldgröße) | relativer Ertrag RY; GDD-Achse; nur transferfähige Merkmale; Leave-One-Dataset-Out als Vorgeschmack; Verteilungsvergleich in Phase 7 |
| Landsat 5/7 nicht mit HLS vergleichbar | Harmonisierungsprüfung mit vorab festgelegter Grenze; Ergebnisse immer auch nur mit HLS-Jahren |
| Ursachen-Zuordnung wird überinterpretiert | einfache, vorab festgelegte Regeln; „Ursache unklar“ erlaubt; keine Krankheitsdiagnose |
| HLS 30 m bei 1-ha-Parzellen knapp | Mindestpixelzahl (3.1); S2 10 m parallel |
| KBS-Daten nur mit Erlaubnis veröffentlichbar | Anfrage früh stellen; bis dahin nur aggregierte Ergebnisse, keine Rohdaten im Repo |
| BARC: Kultur/Feld-IDs unklar | Bewirtschaftungsdateien + Dateinamen; unklare Feld-Jahre ausschließen |
| Mead-Erträge nicht verfügbar | Phase 1–4 laufen ohne Mead |
| Wolken in der Steiermark | Dekaden + Interpolation + Masken; HLS erhöht Beobachtungsdichte |
| Wenige Region-Jahre für V1 | ganz Österreich + Bootstrap-KI; CY-Bench-Regionen wo möglich; V3 anfragen |
| Modell lernt nur „Jahr“ statt Feld | Vergleich mit B0/B1; Rangkorrelation innerhalb eines Jahres |
| GEE-Exporte langsam / Quoten | Stichproben zuerst; Export je Jahr/Datensatz getrennt |

---

## 8. Was der Projektinhaber selbst erledigen muss
- Anmeldung zum Wettbewerb.
- Google-Earth-Engine-Konto + Cloud-Projekt anlegen, `earthengine authenticate` im Browser bestätigen.
- **E-Mail an die Kellogg Biological Station (KBS LTER):** Bitte um Erlaubnis, die MCSE-Ertragsdaten in einem Schülerwettbewerbsprojekt zu verwenden und daraus abgeleitete Ergebnisse zu veröffentlichen (keine Weitergabe der Rohdaten).
- **AmeriFlux-Konto** anlegen (für Mead); ggf. Standort nach Ertragsdaten fragen.
- **Feld-Ertragsdaten in Österreich anfragen (V3)** – parallel zu allem: Landwirt:innen, Landwirtschaftskammer Steiermark, Maschinenring. Gesucht: Körnermais-Erträge pro Feld (Mähdrescher-Ertragskarte oder Wiegeschein + Feldlage) ab 2018. Schon 20–50 Feld-Jahre sind wertvoll. Nur mit Zustimmung, anonymisiert, Rohdaten nie ins Repository. *Diese Daten werden erst nach dem Freeze angesehen.*

## 9. Bewusst *nicht* Teil dieses Plans (Ausblick)
- One Acre Fund (Afrika): viele Felder, aber je nur ein Jahr – passt nicht zum Ansatz „wenige Felder, viele Jahre“; ggf. später als zusätzlicher Transfertest.
- Europäische Mähdrescher-Ertragsdaten aus Studien (Autor:innen anfragen).
- Kalibrierung auf absolute t/ha in Österreich mit größeren Feld-Ertragsdaten (Kooperationen).
- Diagnose von Krankheiten/Schädlingen (bräuchte eigene Labels); Kausalanalyse der Stressursachen über Fallstudien hinaus.
