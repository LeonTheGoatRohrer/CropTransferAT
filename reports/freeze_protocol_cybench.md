# Freeze-Protokoll CY-Bench-Regionalmodell (Phase 5, EU-Freeze)

**Status:** EU-Freeze durchgeführt am 2026-10-16. **Der Zero-Shot-Test Österreich ist gesperrt**, bis der Projektinhaber
dieses Protokoll gelesen und freigegeben hat (`DECISIONS.md`, Arbeitsgrenze Freeze). Nach der Freigabe wird am Modell nichts
mehr geändert; ein dokumentierter Fehler führt zu einem neuen Freeze, beide Ergebnisse werden berichtet.

- Code-Stand (Git-Commit beim Freeze): `6c5c693ef48851e3a764872ba727a3c21467bfde`
- Erzeugt von `python -m croptransfer.regional_cybench` (Seed 42, `config.yaml` Abschnitt `cybench`).
- Datengrundlage: CY-Bench v1.10 (Zenodo 10.5281/zenodo.17279151), Mais, 16 EU-Länder (BE, BG, CZ, DE, EL, ES, FR, HR, HU, IT, LT, NL, PL, PT, RO, SK); **kein Österreich**
  (Länderliste ohne AT, `assert "AT" not in countries`, Test `test_austria_is_excluded`). Ausgeschlossen: EE, FI, IE, LV (nur Nullerträge);
  DK und SE liefern nach der 5-Vorjahre-Regel keine Region-Jahre.
- Österreich-Regel eingehalten: **Es wurde keine österreichische Datei gelesen** (weder Erträge noch Prädiktoren), nichts an Training, Merkmalen,
  Hyperparametern oder Modellwahl hängt von Österreich ab.

## 1. Zielgröße und Vorverarbeitung
- Ziel: `YAS = Ertrag / olympischer Durchschnitt (ohne Max/Min) der 5 Vorjahre derselben Region` (PLAN 3.4). Alle 5 Kalenderjahre `y-5…y-1`
  müssen einen gültigen Ertrag (> 0) haben, sonst entfällt das Region-Jahr. Trainingsjahre 2003–2021.
- Vorverarbeitung: **keine** (keine Imputation, keine Skalierung); fehlende Werte behandelt LightGBM nativ. Statische Merkmale: `awc`, `bulk_density`.
- Prädiktoren je Region-Jahr und Stichtag: Monatsmittel/-min/-max (zusätzlich Monatssumme für `prec`, `cwb`) von `tmax, tmin, prec, cwb, rsm, ssm, fpar, ndvi`
  für die Monate April bis Stichtagsmonat. **As-of-Regel:** nur Beobachtungen, die am Stichtag bekannt sind (Datum ≤ Stichtag); fPAR (Dekade, Etikett = Beginn)
  zählt ab Etikett + 9 Tage, NDVI (8-Tage-Fenster) ab Etikett + 7 Tage. Der Stichtagsmonat enthält nur die Tage bis zum Stichtag.
- Keine Koordinaten, keine Landes- oder Regions-ID, kein Jahr als Merkmal.

## 2. Modell und Hyperparameter
- LightGBM (Regression, L2), flache Bäume (`max_depth ≤ 3`, `num_leaves = 2^max_depth`), `learning_rate 0.05`, `subsample 0.8`, `colsample_bytree 0.5`,
  `reg_lambda 1.0`, deterministisch, 1 Thread, Seed 42.
- Hyperparameter-Suchraum (nur über Leave-One-Country-Out innerhalb der Trainingsländer): `max_depth` [2, 3], `min_child_samples` [50, 200, 600], `n_estimators` [50, 100, 200].
- Gewählte Hyperparameter des finalen Modells (Tuning per LOCO über alle 16 EU-Länder):

| Stichtag | max_depth | min_child_samples | n_estimators | Trainings-Region-Jahre |
|---|---|---|---|---|
| 06-01 | 2 | 600 | 50 | 8371 |
| 06-15 | 3 | 200 | 50 | 8371 |
| 07-01 | 3 | 600 | 50 | 8371 |
| 07-15 | 3 | 600 | 50 | 8371 |
| 08-01 | 2 | 600 | 100 | 8371 |
| 08-15 | 3 | 600 | 50 | 8371 |
| 09-01 | 3 | 600 | 100 | 8371 |

## 3. Merkmalsliste
Anzahl je Stichtag: 06-01: 74, 06-15: 80, 07-01: 100, 07-15: 106, 08-01: 126, 08-15: 132, 09-01: 152. Die Namen folgen `<variable>_<statistik>_m<MM>` (Statistik ∈ mean, min, max, sum; Monat MM = 04 … Stichtagsmonat).
Vollständige Liste des letzten Stichtags (die früheren Stichtage verwenden die Teilmenge der Monate bis zu ihrem Stichtagsmonat; Merkmale ohne Beobachtung am Stichtag entfallen):

```
tmax_mean_m04, tmax_min_m04, tmax_max_m04, tmax_mean_m05, tmax_min_m05, tmax_max_m05, tmax_mean_m06, tmax_min_m06, tmax_max_m06, tmax_mean_m07, tmax_min_m07, tmax_max_m07, tmax_mean_m08, tmax_min_m08, tmax_max_m08, tmax_mean_m09, tmax_min_m09, tmax_max_m09, tmin_mean_m04, tmin_min_m04, tmin_max_m04, tmin_mean_m05, tmin_min_m05, tmin_max_m05, tmin_mean_m06, tmin_min_m06, tmin_max_m06, tmin_mean_m07, tmin_min_m07, tmin_max_m07, tmin_mean_m08, tmin_min_m08, tmin_max_m08, tmin_mean_m09, tmin_min_m09, tmin_max_m09, prec_mean_m04, prec_min_m04, prec_max_m04, prec_sum_m04, prec_mean_m05, prec_min_m05, prec_max_m05, prec_sum_m05, prec_mean_m06, prec_min_m06, prec_max_m06, prec_sum_m06, prec_mean_m07, prec_min_m07, prec_max_m07, prec_sum_m07, prec_mean_m08, prec_min_m08, prec_max_m08, prec_sum_m08, prec_mean_m09, prec_min_m09, prec_max_m09, prec_sum_m09, cwb_mean_m04, cwb_min_m04, cwb_max_m04, cwb_sum_m04, cwb_mean_m05, cwb_min_m05, cwb_max_m05, cwb_sum_m05, cwb_mean_m06, cwb_min_m06, cwb_max_m06, cwb_sum_m06, cwb_mean_m07, cwb_min_m07, cwb_max_m07, cwb_sum_m07, cwb_mean_m08, cwb_min_m08, cwb_max_m08, cwb_sum_m08, cwb_mean_m09, cwb_min_m09, cwb_max_m09, cwb_sum_m09, rsm_mean_m04, rsm_min_m04, rsm_max_m04, rsm_mean_m05, rsm_min_m05, rsm_max_m05, rsm_mean_m06, rsm_min_m06, rsm_max_m06, rsm_mean_m07, rsm_min_m07, rsm_max_m07, rsm_mean_m08, rsm_min_m08, rsm_max_m08, rsm_mean_m09, rsm_min_m09, rsm_max_m09, ssm_mean_m04, ssm_min_m04, ssm_max_m04, ssm_mean_m05, ssm_min_m05, ssm_max_m05, ssm_mean_m06, ssm_min_m06, ssm_max_m06, ssm_mean_m07, ssm_min_m07, ssm_max_m07, ssm_mean_m08, ssm_min_m08, ssm_max_m08, ssm_mean_m09, ssm_min_m09, ssm_max_m09, fpar_mean_m04, fpar_min_m04, fpar_max_m04, fpar_mean_m05, fpar_min_m05, fpar_max_m05, fpar_mean_m06, fpar_min_m06, fpar_max_m06, fpar_mean_m07, fpar_min_m07, fpar_max_m07, fpar_mean_m08, fpar_min_m08, fpar_max_m08, ndvi_mean_m04, ndvi_min_m04, ndvi_max_m04, ndvi_mean_m05, ndvi_min_m05, ndvi_max_m05, ndvi_mean_m06, ndvi_min_m06, ndvi_max_m06, ndvi_mean_m07, ndvi_min_m07, ndvi_max_m07, ndvi_mean_m08, ndvi_min_m08, ndvi_max_m08, awc, bulk_density
```
Die exakte Liste je Stichtag steht in `lgbm_<MMTT>_meta.json` (mit Prüfsumme unten).

## 4. EU-Ergebnisse (äußere Leave-One-Country-Out-Evaluation, Zusammenfassung)
| Stichtag | n Region-Jahre | R² [95-%-KI] | ρ [95-%-KI] | ρ innerhalb Jahr | Skill vs. YAS=1 [95-%-KI] |
|---|---|---|---|---|---|
| 06-01 | 8371 | -0.02 [-0.03; -0.01] | 0.03 [0.01; 0.05] | -0.05 | -0.00 [-0.01; 0.00] |
| 06-15 | 8371 | -0.02 [-0.02; -0.01] | 0.09 [0.07; 0.11] | -0.01 | -0.00 [-0.01; 0.01] |
| 07-01 | 8371 | -0.02 [-0.03; -0.01] | 0.16 [0.14; 0.18] | 0.05 | -0.00 [-0.01; 0.01] |
| 07-15 | 8371 | 0.03 [0.02; 0.04] | 0.33 [0.31; 0.35] | 0.21 | 0.04 [0.03; 0.06] |
| 08-01 | 8371 | 0.05 [0.03; 0.07] | 0.36 [0.34; 0.38] | 0.21 | 0.06 [0.05; 0.08] |
| 08-15 | 8371 | 0.03 [0.02; 0.05] | 0.37 [0.35; 0.39] | 0.23 | 0.05 [0.03; 0.06] |
| 09-01 | 8371 | 0.06 [0.04; 0.07] | 0.38 [0.36; 0.40] | 0.22 | 0.07 [0.06; 0.09] |

Einordnung (ehrlich): Das Modell ist **schwach**. Am Stichtag 09-01 erklärt es R² = 0.058 [0.043; 0.074] der Varianz von YAS, ρ = 0.38 [0.36; 0.40] über alle Region-Jahre,
aber nur ρ = 0.22 [0.12; 0.30] **innerhalb eines Jahres** (der größere Teil des ρ ist das Jahressignal). Vor dem 15.7. besteht kein Skill gegenüber YAS = 1.
Das vorab festgelegte Kriterium „ρ > 0 mit KI ohne 0“ ist ein niedriger Maßstab; es wird deshalb **nicht** nachträglich verschärft oder gelockert, und die Zusatzkennzahlen unten
(Skill, ρ innerhalb eines Jahres, Cluster-KI) werden immer mit berichtet.

Vollständige Kennzahlen (inkl. ohne Deutschland, länderbalanciert, innerhalb eines Jahres, Label-Shuffle): `results/2026-10-16_cybench_eu/metrics.json`.

## 5. Prüfsummen (SHA-256) der eingefrorenen Dateien
Ablage: `results/models/cybench_freeze/` (nicht in Git; mit `python -m croptransfer.regional_cybench` reproduzierbar, die Prüfung
`verify_freeze` vergleicht gegen diese Tabelle).

| Datei | SHA-256 |
|---|---|
| `lgbm_0601.txt` | `b85470e8be1c75a3dd4abdbaf6467e7fdc3f2537360cc379ef4e604d51489746` |
| `lgbm_0601_meta.json` | `7a711d1c973d9935e96d9cfab654ec94b3cd2efed16f2d87cb787277fc5e3b6a` |
| `lgbm_0615.txt` | `ff6f19500a4d02ee759932d9d0bdebcd09f5e3057ab3c6690abc0581e616db0c` |
| `lgbm_0615_meta.json` | `6a1c1bde315ca858746f6b506757cc0334ea6dcb48d46e52067aa179a620fa6b` |
| `lgbm_0701.txt` | `0a9552e71cc376c4580490e38d7215b9cea84d3a6f9347425ba9fbece68f07c4` |
| `lgbm_0701_meta.json` | `8f1052dc527b91fe24320226c89362a8f4903e603242ef0beff2c37c20102cca` |
| `lgbm_0715.txt` | `a3f0f2cdd6be23f70e5eca89f6b7e9d1d53a4b802fb9b6f3cf973168fc4a998d` |
| `lgbm_0715_meta.json` | `7fc81fe8f1f338d90a322996a1dca29d910b64ff3260627d6a4889b2b6753f4d` |
| `lgbm_0801.txt` | `4293e4f279df880b7910502eef309edf01d0ad33263d419f2a8045286f62913f` |
| `lgbm_0801_meta.json` | `385d03e73508817e06dd8000e029f477393d8c5d617c72bcf5d6d1a70d4ad195` |
| `lgbm_0815.txt` | `0b4914ee50ee2fcbdb39d18aef47f319373155454d9aea30067c90d9ede0a4b0` |
| `lgbm_0815_meta.json` | `7d3de12816bee584a118be60b792b80ffdcf7070c9a16d67cdcc49af01a05fb9` |
| `lgbm_0901.txt` | `9f988615c9da3ca28d9bfc8579110107e0dd1025af4badef87bcd52dd8558af8` |
| `lgbm_0901_meta.json` | `6e8b8107827869f755691c840c2f130b3fb29bb1d4ebc9d5426f3cc47d95a21f` |

## 6. Vorab registriertes Zero-Shot-Testprotokoll Österreich (gilt erst nach Freigabe)
**Ziel:** Messen, ob das eingefrorene EU-Modell die Ertragsanomalie österreichischer Bundesländer ohne jede Anpassung vorhersagt (Weg V1 in PLAN Phase 7, Gegenprobe zum Feldmodell).

**Testdaten:** CY-Bench v1.10, Mais, Österreich (NUTS-2 = Bundesländer), Prädiktoren mit derselben Pipeline (`build_country(..., allow_austria=True)`, aktuell nirgends aufgerufen).
- Region-Jahre **2006–2020** (die Erträge in CY-Bench enden 2020). Ausgeschlossen: Wien (AT13), Salzburg (AT32), Tirol (AT33), Vorarlberg (AT34) (< 250 ha Mais, Rundungsartefakte).
  Es verbleiben AT11 Burgenland, AT12 Niederösterreich, AT21 Kärnten, AT22 Steiermark, AT31 Oberösterreich → erwartet **n = 5 × 15 = 75 Region-Jahre**.
- Zielgröße `YAS` exakt wie oben (Vorjahre aus CY-Bench, auch 2001–2005 für 2006).
- Vorhersage: `predict_zero_shot(features, cutoff, freeze_dir, protocol_path)` – prüft zuerst alle Prüfsummen aus Abschnitt 5, wendet das Modell unverändert an;
  keine Rekalibrierung, keine Verschiebung des Mittelwerts, kein Nachtrainieren, kein Zurücklegen von Österreich in irgendeinen Trainings- oder Tuningschritt.
- **Offen, Projektinhaber entscheidet vor dem Test:** Ergänzung der Jahre 2021–2023 aus Statistik Austria (Prädiktoren 2021–2023 sind in CY-Bench vorhanden, Erträge nicht).
  Vorschlag: Hauptergebnis nur 2006–2020 (CY-Bench), die Erweiterung zusätzlich und klar getrennt berichten. Die Entscheidung wird **vor** dem ersten Lauf schriftlich in `DECISIONS.md` festgehalten.

**Metriken (je Stichtag 06-01, 06-15, 07-01, 07-15, 08-01, 08-15, 09-01):** Spearman ρ(vorhergesagter YAS, beobachteter YAS); RMSE des Modells und der Baseline YAS = 1 und deren Differenz; R², Skill gegenüber YAS = 1 und gegenüber der
Trendfortschreibung; ρ innerhalb eines Jahres (Jahres-Proxy-Kontrolle). Konfidenzintervalle: Bootstrap über Region-Jahre, 1000 Ziehungen, Perzentil-95-%-KI, Seed 42
(`bootstrap_metrics`, dieselbe Funktion wie in der EU-Evaluation). Zusätzlich (Sensitivität) Bootstrap über ganze Jahre (Cluster), da Bundesländer im selben Jahr korreliert sind.

**Erfolgskriterien (wie PLAN Phase 7, V1):**
- **Bestanden (regional):** am Stichtag **09-01** ρ > 0 und die untere Grenze des 95-%-KI von ρ > 0.
- **Stark (regional):** zusätzlich RMSE(Modell) < RMSE(YAS = 1), d. h. das 95-%-KI der Differenz `RMSE_Modell − RMSE_Baseline` liegt vollständig unter 0.
- **Alle Stichtage werden berichtet**, nicht nur der beste; die übrigen Stichtage sind beschreibend (kein zweites Erfolgskriterium, keine Auswahl).
- Liegt nur das Cluster-KI (Jahre) bei 0 oder darüber, wird „bestanden“ mit der Einschränkung „nicht robust gegen gemeinsame Jahreseffekte“ berichtet.
- Bei n = 75 sind die Intervalle breit; das Ergebnis wird mit n und KI berichtet, auch wenn das Kriterium nicht erfüllt ist.
- Vergleichswert: publizierte CY-Bench-Baseline AT (R² 0,13, Datenversion v1.8, In-Domain-LOYO) – anderer Aufbau, nur als Einordnung.

**Nicht Teil dieses Tests (getrennt, Phase 5b / F5):** In-Domain AT (LOYO), Pooled, Few-Shot.

## 7. Eigenerklärung zur Österreich-Regel
- Vor dem Freeze wurden keine österreichischen Daten ausgewertet oder genutzt (Training, Merkmalsauswahl, Schwellen, Modellwahl, Hyperparameter): **ja, eingehalten**.
- Nach dem Freeze wurde nichts am Modell geändert: Prüfsummen siehe Abschnitt 5.
