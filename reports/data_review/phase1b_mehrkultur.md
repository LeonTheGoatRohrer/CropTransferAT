# Datenkritik Phase 1b – Mehr-Kulturen-Pakete (W1.3, vorläufig)

Stand 2026-10-16. Zahlen: `reports/data_review/phase1b_mehrkultur_zahlen.md` (erzeugt mit `python -m croptransfer.review_multi`). Pakete: A1 INVITE, A2 BRIWECS, A9 Erbsen FR, A11 Nordic Gerste. **Mais fehlt noch** (G2F wartet auf W0.3).

## 3.1 Repräsentativität
- Gezählte Standort-Jahre ab 2013 (Code): INVITE S2 177, INVITE S3 412, BRIWECS 25, Erbsen 318, Nordic 715. Die Plan-Schätzungen (428 / 28 / 266 / 772) weichen ab, weil der Plan Dateizeilen und Versuche zählt, der Code Standort × Jahr × Kultur (Winter- und Sommererbse getrennt). **Die Code-Zahlen gelten.**
- INVITE endet 2020, Nordic läuft bis 2024: 2021–2024 sind nur durch Gerste und Erbse vertreten. Kein Jahr ist von allen Kulturen abgedeckt (`per_year` in der Zahlendatei).
- Sortenversuche: Sortenmenge und Parzellenzahl wechseln (INVITE Median 37 bzw. 15 Parzellen, BRIWECS 1 320 Parzellen je Station-Jahr). Das ist Rauschen in RY, kein Bias; Sensitivität in E5.
- Alle Quellen sind Versuchsparzellen. Stufe S1 (Feld ≥ 1 ha) enthält keines der vier Pakete.

## 3.2 Korrektheit
- Einheiten aus den Dateien: INVITE `grain_dry_wt_at_maturity` kg Trockenmasse/ha → /1000; BRIWECS `Seedyield` dt/ha bei 100 % TM (README) → /10; Erbsen `yield_14` q/ha bei 14 % Feuchte → /10; Nordic `dry_matter_yield` dt/ha → /10. ⚠️ Die Nordic-Einheit steht nicht in der Datei; abgeleitet aus dem Wertebereich (Median 5,7 t/ha nach Umrechnung, plausibel für Sommergerste). Mit dem README (DataverseNO IZ3EFE) abgleichen.
- **Zwei Versuchstypen je französischem Standort-Jahr** (INVITE Nord/Süd-Frankreich, Suffix z. B. `NA1Y2` / `NA1Y0`): 312 Zeilen hatten einen Zwilling. Sie sind jetzt getrennte Standorte, damit RY Gleiches mit Gleichem vergleicht. Was `Y0`/`Y2` bedeutet, ist nicht belegt – in der Datensatzbeschreibung klären.
- Feuchtebasis: INVITE, BRIWECS, Nordic Trockenmasse, Erbsen 14 %. Absolute Erträge sind deshalb nicht poolbar; RY wird je Quelle gebildet (D1), das ist unkritisch.
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
| Körnermais | – | **0** (G2F fehlt) |

**G1 vorläufig:** gepoolt ≥ 90 S2-Zellen-Jahre ✓ (459); je Kultur ≥ 40 ✓ für Winterweizen und Erbse. **Für Mais gibt es noch kein Label**, deshalb sind D10 (1)–(3) (Mais als Zielkultur, Kultur-Transfer) erst nach W0.3 prüfbar. Die 0,5°-Sensitivität ist noch offen.

## Entscheidung
⚠️ **Weiter mit Einschränkung.** A1/A2/A9/A11 sind nutzbar. Offen: Nordic-Einheit prüfen, Versuchstyp Y0/Y2 klären, Mais (G2F) beschaffen.
