# Datenkritik Phase 1b – Mehr-Kulturen-Pakete (W1.3, vorläufig)

Stand 2026-10-16. Zahlen: `reports/data_review/phase1b_mehrkultur_zahlen.md` (erzeugt mit `python -m croptransfer.review_multi`). Pakete: A1 INVITE, A2 BRIWECS, A9 Erbsen FR, A11 Nordic Gerste. Mais (A3 G2F) kam per figshare-Kopie nachträglich dazu (CC BY 4.0, nur PHENO/ECOV entpackt; kein CAPTCHA nötig).

## 3.1 Repräsentativität
- Gezählte Standort-Jahre ab 2013 (Code): INVITE S2 177, INVITE S3 412, BRIWECS 25, Erbsen 318, Nordic 715. Die Plan-Schätzungen (428 / 28 / 266 / 772) weichen ab, weil der Plan Dateizeilen und Versuche zählt, der Code Standort × Jahr × Kultur (Winter- und Sommererbse getrennt). **Die Code-Zahlen gelten.**
- INVITE endet 2020, Nordic läuft bis 2024: 2021–2024 sind nur durch Gerste und Erbse vertreten. Kein Jahr ist von allen Kulturen abgedeckt (`per_year` in der Zahlendatei).
- Sortenversuche: Sortenmenge und Parzellenzahl wechseln (INVITE Median 37 bzw. 15 Parzellen, BRIWECS 1 320 Parzellen je Station-Jahr). Das ist Rauschen in RY, kein Bias; Sensitivität in E5.
- Alle Quellen sind Versuchsparzellen. Stufe S1 (Feld ≥ 1 ha) enthält keines der vier Pakete.

## 3.2 Korrektheit
- Einheiten aus den Dateien: INVITE `grain_dry_wt_at_maturity` kg Trockenmasse/ha → /1000; BRIWECS `Seedyield` dt/ha bei 100 % TM (README) → /10; Erbsen `yield_14` q/ha bei 14 % Feuchte → /10; Nordic `dry_matter_yield` hkg/ha **bei 15 % Feuchte** (README `00_README_BARLEY.txt`, geprüft) → /10; die Feuchtebasis ist daher 15 %, nicht Trockenmasse (im Code korrigiert).
- **Zwei Versuchstypen je französischem Standort-Jahr** (INVITE Nord/Süd-Frankreich, Suffix z. B. `NA1Y2` / `NA1Y0`): 312 Zeilen hatten einen Zwilling. Sie sind jetzt getrennte Standorte, damit RY Gleiches mit Gleichem vergleicht. Selbstkontrolle (nach Lesen der INVITE-Codes): `Y0`/`Y2` bezeichnet sehr wahrscheinlich das Prüfjahr der Sorten in der Wertprüfung (Spalte `year_vcu_evaluation`), also verschiedene Sortensätze auf demselben Feld und mit demselben Wetter. Die Trennung ist deshalb konservativ (RY vergleicht gleiche Sortensätze); für die Zählung (Zelle × Jahr) ändert sie nichts.
- Feuchtebasis: INVITE, BRIWECS Trockenmasse, Nordic 15 %, Erbsen 14 %, G2F 15,5 %. Absolute Erträge sind deshalb nicht poolbar; RY wird je Quelle gebildet (D1), das ist unkritisch.
- Koordinaten: INVITE CZ/HU/CH volle Genauigkeit (S2); Frankreich auf 0,1° gerundet (S3); Erbsen 0,001°.
- Duplikate nach Schlüssel (dataset, Kultur, Variante, Standort, Land, Jahr): 0 nach der Korrektur. Querduplikate zwischen Quellen (z. B. INVITE-CH und Agroscope) noch nicht gesucht.
- Ertragsfilter je Parzelle: INVITE 1–15 t/ha, Erbse 0,2–9 t/ha (aus Wertebereichen der Dateien, nicht an Ergebnissen).

## 3.3 Merkmale / Scheinzusammenhänge
Noch keine Merkmale (Etappe 3). Vormerken: `cell_id` nie als Merkmal; Sortenwechsel konfundiert RY.

## 3.4 Leakage
Keine Modelle trainiert. Österreich: kein Paket enthält österreichische Daten; `assert_no_austria` prüft die Ausgabe (`tests/test_groundtruth_multi.py`).

## 3.5 Zielgröße RY
Median RY 0,98–1,02; Anteil gefährdet (RY < 0,85): BRIWECS 12 %, INVITE S2 19,9 %, INVITE S3 12,9 %, Nordic S4 23,4 %, Erbse 26,7 %. Genug Stressfälle in Weizen und Erbse; Nordic ist modelliert (S4).

## 3.6 Zählung gegen Gate G1 (D2: Wetterzelle 0,1° × Jahr)
| Kultur | Stufe | Zellen-Jahre |
|---|---|---|
| Winterweizen | S2 | 202 |
| Winterweizen | S3 | 224 |
| Körnererbse | S2 | 257 |
| Sommergerste | S4 | 711 |
| Körnermais (G2F) | S2 | 104 (S3: 1) |

**G1 vorläufig:** gepoolt ≥ 90 S2-Zellen-Jahre ✓ (459); je Kultur ≥ 40 ✓ für Winterweizen und Erbse. Mais hat 104 S2-Zellen-Jahre (G2F, der Plan zählte 103) – ausreichend für G1, aber nur eine Quelle (Leave-One-Dataset-Out für Mais nicht möglich). Die 0,5°-Sensitivität ist noch offen.

## Entscheidung
⚠️ **Weiter mit Einschränkung.** A1/A2/A9/A11 sind nutzbar. Offen: Querduplikate suchen; G2F-Koordinaten teils geschätzt (laut Plan), Mais hat nur eine Quelle.
