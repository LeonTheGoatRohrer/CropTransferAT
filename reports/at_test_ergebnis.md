# Österreich-Test (erster, explorativ) – Ergebnis

Stand 2026-10-17. Protokoll: `reports/freeze_protocol_at.md` (Tag `freeze-at-1`, vor der Auswertung festgeschrieben); Läufe: `results/2026-10-17_at_test/` (`metrics.json`, `site_year.csv`, `region_year.csv`, `qc.json`), `results/2026-10-17_at_retrain/`. Datenkritik: `reports/data_review/at_test.md` (⚠️ weiter mit Einschränkung).

> **Einordnung:** Erster Test mit eingefrorenen Modellen, **explorativ**, weil das Phase-4-Kriterium „stark genug“ von keinem Feldmodell erfüllt war (Entscheidung des Projektinhabers, `DECISIONS.md`). Es wurde **kein Sieger** gewählt, am Protokoll nichts geändert.
> **Der lokale Test (V2) ist faktisch nur Oberösterreich:** 5 Standorte, 7 Jahre, n = 34 Standort-Jahre. Die Steiermark-Standorte (Wagna, Kalsdorf, Hatzendorf) haben nur Düngungs- und Bodenbearbeitungsversuche, keine Sortenversuche; der vorab registrierte Filter (`sorten`, `praxisversuch_sorten`) hat sie ausgeschlossen. Das Jahr 2019 fehlt aus demselben Grund.

## Kurzfassung

1. **Stress-Score (A) erkennt in Oberösterreich gute und schlechte Jahre:** ρ = 0,50 [0,19; 0,68] am 1.9. (n = 34 Standort-Jahre, 7 Jahre als Cluster) → Kriterium V2-A **bestanden**. Auch an den drei früheren Stichtagen bestanden (0,46 / 0,55 / 0,65).
2. **Aber nicht besser als einfaches Grün:** Der NDVI-Vergleichswert ohne jedes Lernen erreicht ρ = 0,50 [0,09; 0,65]. Der Score ist fast dasselbe wie NDVI (ρ = 0,83 auf Standort-Jahren, 0,88 auf den Feldern).
3. **Der Gewinn kommt aus den Jahren, nicht aus den Standorten:** Mittel je Jahr ρ = 0,79 (7 Punkte); nach Abzug der Jahresmittel bleibt ρ = 0,31 (explorativ); Rangfolge der Standorte **innerhalb** eines Jahres: Median −0,10 (6 Jahre mit je 4–5 Standorten). Innerhalb der Standorte über die Jahre: Median 0,60 (5 Standorte, Linden −0,5).
4. **Regionalmodell (B) auf Bundesländern (V1):** ρ = 0,52 [0,13; 0,75] am 1.9. (n = 30 Region-Jahre, 6 Jahre) → **bestanden**, aber **nicht „stark“**: RMSE 0,121 gegenüber 0,101 für „normales Jahr“ (YAS = 1), Differenz +0,019 [−0,016; +0,043]. Am 15.7. ist ρ = −0,14 (nicht belegt).
5. **Regionalmodell auf die Versuchsstandorte (V2-B):** ρ = 0,03 [−0,70; 0,70], n = 24 → nicht belegt (kaum aussagekräftig).
6. **Nachtrainieren mit österreichischen Erträgen (Zusatz, 45 Region-Jahre, Leave-one-year-out):** Das eingefrorene Modell hat die Rangfolge, aber eine zu große Schwankungsbreite. Eine Neukalibrierung mit **zwei Zahlen** (R1) senkt den Fehler von 0,125 auf 0,095 und liegt damit erstmals knapp unter „normales Jahr“ (0,119). Die zweite Variante (R2) verbessert R0 ebenfalls, bleibt aber bei „normales Jahr“.

## 1. Lokaler Test V2 (Standort-Jahre, nur Oberösterreich)

n = 34 Standort-Jahre (Innviertel 6; Linden, Mauthausen, Walding, Bad Wimsbach je 7), 7 Jahre (2018, 2020–2025); Cluster-Bootstrap über Jahre.

| Stichtag | V2-A Stress-Score ρ [95-%-KI] | Urteil | V2-B Regionalmodell ρ [KI] (n = 24) | Urteil |
|---|---|---|---|---|
| 15.7. | 0,46 [0,11; 0,65] (n = 30) | bestanden | 0,44 [−0,36; 0,82] | nicht belegt |
| 1.8. | 0,55 [0,21; 0,67] | bestanden | 0,15 [−0,65; 0,70] | nicht belegt |
| 15.8. | 0,65 [0,40; 0,70] | bestanden | 0,15 [−0,65; 0,70] | nicht belegt |
| **1.9. (Haupt)** | **0,50 [0,19; 0,68]** | **bestanden** | 0,03 [−0,70; 0,70] | nicht belegt |

Vergleichswert B-NDVI (nur 1.9.): ρ = 0,50 [0,09; 0,65].

Zerlegung am 1.9. (beschreibend, nicht Teil der Kriterien):

| Sicht | ρ |
|---|---|
| Leave-one-year-out (je ein Jahr weglassen) | 0,41 – 0,55 (stabil, kein einzelnes Jahr trägt das Ergebnis) |
| Jahresmittel (7 Punkte) | 0,79 |
| nach Abzug der Jahresmittel (explorativ) | 0,31 |
| nach Abzug der Standortmittel (explorativ) | 0,46 |
| innerhalb eines Jahres, Median über 6 Jahre | −0,10 |
| innerhalb eines Standorts, Median über 5 Standorte | 0,60 (Innviertel 0,60; Linden −0,50; Mauthausen 0,54; Walding 0,82; Bad Wimsbach 0,71) |

## 2. Regionaler Test V1 (Bundesländer, n = 30 Region-Jahre, 2018–2023)

| Stichtag | ρ [95-%-KI] | Urteil | RMSE Modell / „normales Jahr“ | RMSE-Differenz [KI] |
|---|---|---|---|---|
| 15.7. | −0,14 [−0,64; 0,47] | nicht belegt | 0,144 / 0,101 | +0,042 [−0,013; +0,090] |
| 1.8. | 0,41 [0,06; 0,70] | bestanden | 0,122 / 0,101 | +0,021 [−0,019; +0,047] |
| 15.8. | 0,51 [0,18; 0,75] | bestanden | 0,117 / 0,101 | +0,016 [−0,019; +0,039] |
| **1.9.** | **0,52 [0,13; 0,75]** | **bestanden** (nicht „stark“) | 0,121 / 0,101 | +0,019 [−0,016; +0,043] |

ρ innerhalb der Jahre (5 Regionen): Median 0,2 (2018: 0,9; 2019: −0,6; 2023: 1,0). V1-A (Mittelwert des Stress-Scores je Region, nur Oberösterreich und Steiermark, n = 12): ρ = 0,38 [−0,37; 0,72], nicht belegt.

## 3. Zusatz: Nachtrainieren (`reports/plan_at_nachtraining.md`, Leave-one-year-out, 2015–2023, n = 45)

| Variante (1.9.) | ρ [KI] | RMSE | Δ zu R0 [KI] | Δ zu „normales Jahr“ [KI] |
|---|---|---|---|---|
| R0 eingefroren | 0,63 [0,34; 0,79] | 0,125 | – | +0,006 [−0,023; +0,034] |
| R1 lineare Neukalibrierung | 0,60 [0,31; 0,77] | **0,095** | **−0,030 [−0,047; −0,009]** | **−0,024 [−0,051; −0,001]** |
| R2 EU-Training + Österreich (Gewicht 20) | 0,63 [0,42; 0,78] | 0,111 | −0,014 [−0,019; −0,010] | −0,008 [−0,038; +0,019] |

„Normales Jahr“ RMSE = 0,119. Am 1.8. verbessert R2 das Modell R0 (−0,007 [−0,013; −0,004]), R1 nicht ganz (−0,022 [−0,039; +0,001]); beide bleiben nicht klar besser als „normales Jahr“. Für 2018–2023 allein ist R0 ρ = 0,52 (dasselbe wie V1).
**Lesart:** Die Rangfolge der Jahre war schon vorher da (ρ 0,6). Was fehlte, war die richtige Größenordnung der Schwankung. Das ist ein Hinweis, kein Beweis: 45 Zeilen, 9 Jahre, die Testjahre waren am Anpassen der anderen Jahre beteiligt (Leave-one-year-out nutzt auch spätere Jahre).

## 4. Was sich damit sagen lässt – und was nicht

**Belastbar genug für eine vorsichtige Aussage:**
- Mit einem aus US-Feldern abgeleiteten, nie auf Österreich angepassten Grün-Maß (Stress-Score) lässt sich in Oberösterreich die Rangfolge guter und schlechter Jahre erkennen (ρ ≈ 0,5, KI über 0).
- Das EU-Regionalmodell erkennt in den österreichischen Bundesländern die Rangfolge der Jahre ab dem 1.8. (ρ ≈ 0,4–0,5), ohne dort je trainiert worden zu sein.
- Zwei Zahlen lokal angepasst machen das Regionalmodell klar besser als das unangepasste (Zusatz).

**Nicht belegt, ausdrücklich nicht behaupten:**
- Dass der Stress-Score mehr kann als einfaches NDVI.
- Dass er **Felder oder Standorte innerhalb eines Jahres** unterscheiden kann (Median −0,10).
- Dass der Test für die Steiermark gilt – dafür liegen keine passenden Versuchsdaten vor.
- Dass das Regionalmodell in absoluten Zahlen besser als „normales Jahr“ ist (ohne Anpassung nicht).
- Alles auf Feldebene (V3 fehlt).

## 5. Offene Punkte

1. Steiermark: Düngungs- oder Bodenbearbeitungsversuche als weitere Zielgröße zu nehmen wäre eine **nachträgliche** Ausweitung und müsste als eigener, getrennter Zusatz ausgewiesen werden.
2. Genauere Standortkoordinaten (Anfrage Hatzendorf) und Praxis-Felderträge (V3).
3. Die Frage, ob der Score Stress oder frühe Reife misst: In den Jahren mit sehr vielen abrupten Abfällen in Juli/August (2018: 43 %, 2024: 49 %, 2022: 18 % der Felder) liegen durchschnittliche bis gute Erträge (relativ 1,04 bzw. 1,08) neben den niedrigsten Scores. Der Score könnte also auch frühe Reife oder Hitze-Abreife anzeigen statt Ertragsverlust.
