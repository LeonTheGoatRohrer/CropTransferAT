# Datenkritik F2 – neue Merkmale M1–M4 (Feinjustierung)

Stand 2026-10-16. Zahlen aus `results/2026-10-16_feinjust_review/review.json` (`python -m croptransfer.fj_review`), Kurvenbild `reports/figures/fj_emergence_check.png`. Geprüft **bevor** ein Merkmal mit Erträgen verglichen wurde (Ablation F3 lief danach). Zeilen: 123 HLS-Feld-Jahre ab 2017, davon 89 mit RY (Ziel A).

## Extraktion

| Quelle | Umfang | Befund |
|---|---|---|
| Sentinel-1 GRD (IW, VV+VH) | 12 Datensatz-Jahre, 41 BARC-Pixel-Feld-Jahre | alle Jobs ok; 4–19 gültige Szenen je Feld 1.7.–1.9. (Median 5) |
| Landsat 8/9 ST_B10 | 12 Datensatz-Jahre | alle Jobs ok; Median 1–3 klare Szenen je Feld 15.6.–1.9. |
| MOD16A2GF ET/PET | 12 Datensatz-Jahre | alle Jobs ok |
| ERA5-Land Verdunstung | 6 Jahre (2017–2022 bzw. 2023) | alle Jobs ok |

## 3.1 Repräsentativität

- **Fehlende Werte (Ziel-A-Zeilen):** Radar 0 %, MODIS/ERA5 0 %, Auflaufdatum 3,4 %, **Oberflächentemperatur 47 %**. LST fehlt vollständig in BARC 2017, 2018, 2019, 2021 und KBS 2017 (< 3 klare Szenen, Regel aus Plan §6). M2-LST wird deshalb überwiegend imputiert; ein Effekt von M2 kann fast nur aus BARC 2020, KBS 2020 und KBS 2023 kommen.
- **Wolken-Bias:** Spearman zwischen Zahl klarer Landsat-Szenen und RY innerhalb der Standort-Jahre: −0,71 (BARC 2020, n = 5), 0,00, 0,31, 0,11 – kein einheitliches Muster, aber die Fehlquote ist **jahresabhängig** (Wetter). ⚠️ Grenze.
- **Radar-Sensorwechsel:** S1B fiel Ende 2021 aus; 2022–2023 nur S1A (KBS 2023: 18 Szenen in der Saison statt 43–120). Weniger Szenen ⇒ rauschigere Mittel in KBS 2023.

## 3.2 Korrektheit

- **Wertebereiche:** VV −22,6 … −3,0 dB, VH −33,2 … −13,0 dB (innerhalb der Regeln); RVI 0,48–1,01 (RVI > 1 ist möglich, wenn VH > VV, selten). LST klarer Szenen 4,8–54,7 °C; 54,7 °C ist hoch, aber für Boden zwischen jungen Maisreihen möglich. MODIS-ET/PET 0,09–0,87; ERA5-Verhältnis 0,12–0,47.
- **Kurvenform / Auflaufdatum (≥ 20 Kurven angesehen, `fj_emergence_check.png`):** Die erste, vorab festgelegte Regel nahm bei Parzellen mit Zwischenfrucht (KBS T4, einige BARC-Felder) das **Frühjahrs-Grün der Zwischenfrucht** als Maximum (z. B. KBS T4R5 2020: Tag 107). **Korrigiert vor jedem Ertragsvergleich** (DECISIONS 2026-10-16): Maximum erst ab 1.6. (Mais-Saisonmitte aus `crops.maize`), Datum = letzter Anstieg über die Schwelle vor dem Maximum. Danach sitzen alle 24 Markierungen am Anstieg der Hauptkultur; Werte Tag 146–202 (Ende Mai bis Juli).
- **Bedeutung von M4:** 20 % der Amplitude wird etwa 3–4 Wochen **nach** dem Auflaufen erreicht; `emerge_doy` ist ein **Begrünungsdatum**, kein Auflaufdatum. Prüfung gegen Saattermine nicht möglich (keine Saattermine in den Quellen). KBS 2017 hat nur 2–4 klare S2-Szenen bis 1.9. → unsicher.
- **Auflösung:** KBS-Parzellen 0,57 ha (≈ 6 Landsat-30-m-Pixel, < 1 natives 100-m-Thermalpixel, ≈ 0 eigene MODIS-Pixel): LST und MODIS-ET beschreiben bei KBS **nicht** die einzelne Parzelle. ERA5-Verdunstung ist innerhalb eines KBS- oder BARC-2017-Standort-Jahres konstant (SD 0) – reine Jahresinformation.
- **Doppelte Szenen:** überlappende Landsat-Zeilen und S1-Slices am selben Tag werden je Feld und Tag gemittelt (Median).

## 3.3 Scheinzusammenhänge

- **Korrelationen:** `s1_rvi_anom` und `s1_vhvv_anom` ρ = 0,99 (praktisch dasselbe Merkmal), mit `s1_rvi_mean` 0,81. `lst_dt_mean` und `era5_et_ratio` ρ = 0,89 – beide messen vor allem das **Jahr** (Wetter), nicht das Feld. Jahres-Proxy-Gefahr bei M2 hoch.
- Label-Shuffle, Koordinaten, Adversarial Validation: siehe Ablationsbericht (F3.2).

## 3.4 Leakage

- Alle Merkmale as-of Stichtag (Tests `test_no_leakage.py`: Radar, LST, MODIS, ERA5, GDD-Klassen, Auflaufdatum). MODIS-Komposite zählen nur, wenn ihr **Ende** vor dem Stichtag liegt.
- Nachbaranomalien nutzen nur Satellitenwerte anderer Felder desselben Tages bzw. Jahres, nie Labels.
- **Österreich-Regel:** keine österreichischen Daten geladen oder angesehen; `data/raw/hagel_at/` existiert noch nicht.

## 3.5 Plausibilität

n/a vor der Ablation (keine Ertragsvergleiche in diesem Schritt).

## 3.6 Entscheidung

⚠️ **Weiter mit Einschränkung.** M2-LST ist zu 47 % leer und bei KBS räumlich zu grob; M2-ET ist überwiegend Jahresinformation; M4 ist ein Begrünungs-, kein Auflaufdatum. Diese Grenzen gehen in den Bericht. Die Korrektur der Auflaufregel ist offengelegt und geschah ohne Kenntnis eines Ertragsvergleichs.
