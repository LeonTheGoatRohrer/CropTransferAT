# Datenkritik Phase 1 – Ertragsdaten aufbereiten

Datum: 2026-10-16 · Branch `phase-1-groundtruth` · Prüfliste nach `AGENTS.md` §3.
Zahlen aus `python -m croptransfer.groundtruth`, `python -m croptransfer.dataset_us`, `python -m croptransfer.explore_phase1` (Ergebnisordner `results/2026-10-16_phase1/`).

## Was entstanden ist

| Datei | Inhalt |
|---|---|
| `data/processed/gt_field_years.parquet` | 365 Mais-Feld-Jahre: KBS 294 (96 HLS-Zeit + 198 vor 2013), BARC 61, Colorado 10 |
| `gt_yield_points.parquet` | 46 504 BARC-Ertragspunkte (Kriging 5 m → 10 m) |
| `gt_dekads.parquet` | Dekaden-Kurven (HLS-Basis, S2-Basis) je Feld-Jahr |
| `gt_static.parquet` | SoilGrids 0–30 cm, nFK (Saxton & Rawls), Höhe, Neigung, Exposition, TPI, TWI, SSURGO NCCPI Mais |
| `features_<MMDD>.parquet` | As-of-Merkmale je Stichtag (Gruppen S, W, B, B+) |
| `gt_excluded.csv` | 7 ausgeschlossene Zeilen mit Grund |

RY-Labels (trendbereinigt, DECISIONS 2026-10-15): KBS 294 (alle Parzellen haben ≥ 2 andere Mais-Jahre), BARC 27 (7 Felder mit ≥ 3 Mais-Jahren), Colorado 0. Trend je Datensatz (feste Feldeffekte): KBS +0,119 t/ha/Jahr, BARC −0,147 t/ha/Jahr (nur 2014–2021, vom Wetter dominiert).

---

## 3.1 Repräsentativität

**a) Effektive Stichprobe.** *Geprüft wie:* Zählung je Datensatz-Jahr. *Befund:* In der HLS-Zeit gibt es RY für **123 Feld-Jahre aus nur 11 Standort-Jahren** (KBS 2014/17/20/23, BARC 2014/16–21). Davon haben nur 8 Standort-Jahre ≥ 5 Felder (für Rangkorrelation innerhalb eines Jahres). *Konsequenz:* Jeder Jahreseffekt beruht auf ≈ 8–11 unabhängigen Fällen. KI breit, Cluster-Bootstrap über Datensatz-Jahre (vorab festgelegt).

**b) Landsat-Erweiterung fällt weg.** *Geprüft wie:* vorab registrierte Harmonisierungsprüfung L7 vs. HLS (Dekaden, 413 Paare, 133 Feld-Jahre). *Befund:* NDVI Bias −0,016 (Grenze 0,03 ✓), **RMSD 0,073 (Grenze 0,07 ✗)**; EVI −0,021 / 0,080 ✗. Diagnostik mit Paaren am selben Tag (±1 Tag, 292 Paare): RMSD 0,074 – die Streuung entsteht also nicht durch unterschiedliche Aufnahmetage in der Dekade, sondern eher durch kleine Parzellen (≈ 12 Pixel), Mischpixel und Lagefehler. *Konsequenz:* Regel greift → **keine Satellitenmerkmale vor 2013**. Die KBS-Jahre 1989–2011 bleiben für Normalwerte (RY) und für Modelle ohne Satellit (Variante „W-lang“, DECISIONS 2026-10-16) nutzbar. Frage an den Projektinhaber (NACHTLAUF.md).

**c) Wolken-Bias.** *Geprüft wie:* Spearman zwischen Zahl klarer HLS-Termine bis 1.9. und RY. *Befund:* ρ = −0,09 (n = 123) – kein relevanter Zusammenhang. Aber die Abdeckung schwankt stark je Jahr: **KBS 2014 (nur L30) hat keinen klaren Termin von Juli bis September, KBS 2017 kaum einen**; BARC 2014 nur 3 Termine. *Konsequenz:* Datenqualitätsregel (DECISIONS 2026-10-16): Kurvenmerkmale fehlen, statt Aprilwerte fortzuschreiben. Für die HLS-Basis haben damit faktisch nur **2 von 4 KBS-Jahren** eine Sommerkurve. Die S2-Basis hat für KBS 2017 Sommertermine.

**d) Zielverteilung.** *Befund:* Anteil RY < 0,85: KBS 2017 9/24, 2020 7/24, 2023 6/24, 2014 1/24; BARC 2017 4/4, 2018 2/2, 2019 1/5. „Gefährdet“-Fälle hängen an wenigen Jahren. *Konsequenz:* PR-AUC in Phase 3 nur mit KI und n.

**e) Ausgeschlossene Zeilen.** 5 KBS-Zeilen ohne `whole_plot`-Ertrag (1991, 1996), 1 Zeile mit unerklärter Behandlung „T21“, 1 BARC-Raster mit unklarer Einheit (2017 CentralFarm 4-7, Mittel 3,3). Keine systematische Häufung → unkritisch.

## 3.2 Korrektheit

| Prüfpunkt | Geprüft wie | Befund | Konsequenz |
|---|---|---|---|
| Wertebereiche | Indizes nach Skalierung, `valid_obs` (NDVI/NDMI in [−1, 1], EVI in [−1, 2]) | 10 343 gültige Szenen-Feld-Werte (HLS 4031, S2 3620, L5 1293, L7 1399) | ✅ |
| Kurvenform | Glättung, Maximum zwischen Dekade 8 und 16 und NDVI ≥ 0,6 | BARC 98 % maistypisch; KBS HLS-Zeit 62 % (Ausfälle = KBS 2014/2017 ohne Sommertermine, keine falsche Kultur); KBS vor 2013 85 %; Colorado 30 % (Trockenfeld mit Totalausfällen, kleine Punktwolke) | Sichtprüfung `reports/figures/phase1_curve_sample.png`; Colorado nur für absoluten Ertrag |
| Frühe Ernte | NDVI < 0,35 vor 1.9. nach frühem Maximum | KBS HLS 15 % (Artefakt der Lücken 2014/2017), BARC 0 % | keine Feld-Jahre ausgeschlossen; Regel greift über fehlende Merkmale |
| Sensorwechsel | Landsat vs. HLS (s. 3.1 b); S2 über `S2_SR_HARMONIZED` (Offset 2022 korrigiert) | L7 nicht ausreichend harmonisiert | keine Landsat-Merkmale |
| Einheiten | Feuchte je Quelle (DATA_SOURCES) | BARC 14/15 % je Jahr umgerechnet, KBS/Colorado 15,5 % | ✅ |
| BARC-Feldzuordnung | IoU ≥ 0,7 der Rasterumrisse über Jahre | 33 Felder; IoU-Zuordnung = bereinigte Namen; „1_14“ (2020) ≠ „1_14B“ (2021) | ✅ (beantwortet die offene Frage 16 vs. 27 RY-Feld-Jahre: **27**) |
| KBS Osthälfte bis 2016 | Metadaten | Satellit über ganze Parzelle | dokumentiert (DECISIONS) |
| Auflösung | ERA5-Land 0,1° | alle 24 KBS-Parzellen teilen einen Wetterpunkt, BARC 1–2 | Wetter erklärt nur Jahresunterschiede, nie Unterschiede zwischen KBS-Parzellen |
| SSURGO | SDA je Feld | KBS eine Map-Unit (NCCPI konstant) | B+ nur als Analyse |

## 3.3 Scheinzusammenhänge (erste Zusammenhänge, PLAN 1.7)
- *Geprüft wie:* Spearman K1–K4 (NDVI/EVI/NDMI/GNDVI, HLS) mit RY je Datensatz und gepoolt, Cluster-Bootstrap.
- *Befund:* höchste gepoolte Werte EVI-K4 ρ = 0,44 (KI 0,10–0,75, n = 74, 9 Cluster), EVI-K1 0,43 (0,09–0,56); KBS-Werte (ρ ≈ 0,64) beruhen auf **nur 2 Jahren** (2020, 2023) und sind daher vor allem ein Jahresvergleich. BARC einzeln: K4-EVI 0,50 (KI −0,04–0,87).
- *Konsequenz:* Ein Signal ist sichtbar, aber auf sehr wenigen Jahren. Modelle mit vielen Merkmalen werden überanpassen → einfache Modelle und Leistung innerhalb eines Jahres berichten.

## 3.4 Leakage
- As-of: `dekad_composite` und Wettermerkmale filtern auf Datum ≤ Stichtag; Interpolation nur zwischen vergangenen Terminen (Tests `test_no_leakage.py`, inkl. „Lücke vor dem Stichtag“).
- RY: Trend nie mit Zieljahr; in der CV nur aus Trainingszeilen (`ry_in_fold`, Tests).
- Österreich-Regel: In Phase 1 wurde keine österreichische Datei geöffnet (nur US-Daten; Phase-5-Unteragent arbeitet ohne AT-Ordner).

## 3.5 Plausibilität
Kurven zeigen Aufgang Mai/Juni, Maximum Ende Juli–August, Abreife September; KBS-Aprilwerte 0,4–0,6 = Bewuchs vor der Saat (Deckfrucht/Unkraut). Schlechte Jahre (BARC 2018 RY 0,52: Rekordniederschlag Maryland; KBS 1996/1999/2008) fallen in den Kurven auf (`phase1_curves_best_worst.png`).

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Datensatz reproduzierbar per Befehl, jede ausgeschlossene Zeile protokolliert. Grenzen: effektive Stichprobe 8–11 Standort-Jahre; keine Landsat-Erweiterung; KBS 2014/2017 ohne HLS-Sommerkurve; Colorado ohne RY. Nicht umgesetzt in Phase 1 (bewusst verschoben): Pixel-Paare innerhalb der Felder mit S2 (`gt_pixels`), GDD-Achse der Merkmale, SSURGO je Ertragspixel – siehe NACHTLAUF.md.
