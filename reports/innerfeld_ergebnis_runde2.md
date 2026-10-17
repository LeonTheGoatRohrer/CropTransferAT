# Innerhalb-Feld Runde 2 – Glättung und Aufbereitung: Ergebnis

Stand 2026-10-17. Vorab-Festlegungen: `reports/innerfeld_vorab_runde2.md` (Commit `de9a35f`, **vor** dem Lauf); Code `src/croptransfer/innerfeld_runde2.py` (Commit nach den Vorab-Festlegungen, siehe `git.txt`); Lauf `results/2026-10-17_innerfeld_runde2/` (`metrics.json`, `per_fy.csv`). Eine Rechnung, keine Parameter geändert, Österreich nicht berührt.

## Kurzfassung

1. **Glättung der Vorhersage über Nachbarzellen hilft nicht.** Gegen die ungeglätteten 10-m-Zellen gemessen, ändert sich das ρ kaum und sinkt meist: BARC B0 −0,013, M1 +0,004; Kayad B0 −0,015, M1 −0,009. Beide Gates (R2-BARC, R2-Kayad) sind **nicht erfüllt**. Nach der vorab festgelegten Regel gilt damit die Hauptrunde unverändert; im Produkt wird nicht geglättet.
2. **Der scheinbare Gewinn der Blockmittelung aus der Obergrenzen-Analyse (z. B. M1 0,70 → 0,76 bei 30 m) kam von der Messseite, nicht von der Vorhersage.** Dort wurden Vorhersage **und** Ertragskarte gemittelt; die Ertragskarte verliert dabei Rauschen, und die Aufgabe wird leichter. Mittelt man nur die Vorhersage, ist nichts zu gewinnen. Eine gröbere Karte wäre ein anderes, leichteres Produkt, keine Verbesserung des Verfahrens.
3. **Bereinigte Kayad-Ertragspunkte ändern das ρ nur wenig:** B0 0,604 → **0,623**, M1 0,596 → 0,605, Lift 2,54 → 2,86 (3 Feld-Jahre, kein Gate). Etwas Rauschen der Karte lag also in Start-, Stopp- und Spurenenden; viel ist es nicht.
4. **Kontrollen unauffällig:** Zufalls-Vorhersage bleibt nach Glättung bei ρ ≈ 0, das Positionsmodell ändert sich nicht.

## 1. Glättung (Gate R2)

Median-ρ über Feld-Jahre gegen die **ungeglätteten** 10-m-Zellen; S0 = keine Glättung, S1 = 3×3 (30 m, Haupt), S2 = 5×5 (50 m, Neben).

| Standort / Modell | S0 | S1 | S2 | Δ S1 − S0 | Δ S2 − S0 |
|---|---|---|---|---|---|
| **BARC** B0 (41 FJ) | 0,674 | 0,672 | 0,626 | **−0,013** [−0,017; +0,001] | −0,053 [−0,072; −0,038] |
| **BARC** M1 | 0,702 | 0,695 | 0,655 | **+0,004** [−0,007; +0,012] | −0,035 [−0,052; −0,025] |
| **Kayad** B0 (3 FJ) | 0,604 | 0,597 | 0,571 | **−0,015** | −0,031 |
| **Kayad** M1 | 0,596 | 0,582 | 0,562 | **−0,009** | −0,015 |

| Gate (vorab) | Ergebnis | Urteil |
|---|---|---|
| R2-BARC: B0 **und** M1 Δρ(S1 − S0) ≥ +0,02, KI-Untergrenze > 0 | B0 −0,013, M1 +0,004 | **✗** |
| R2-Kayad: B0 **und** M1 Median Δρ ≥ +0,02 und > 0 in allen 3 Jahren | B0 −0,015, M1 −0,009; nicht in allen Jahren positiv | **✗** |
| **Glättung hilft** (beide Gates) | – | **nein** |

**Gesamtaussage (vorab festgelegte Formulierung):** „Glättung bringt gegen die 10-m-Zellen keinen belastbaren Gewinn; der Gewinn der Blockmittelung beruht auf der leichteren Aufgabe.“

Beschreibend, wie vorab festgelegt: ρ auf **30-m-Blöcken** (Vorhersage und Messung gemittelt). Auch dort ändert die Glättung der Vorhersage wenig: BARC B0 0,693 → 0,688, M1 0,760 → 0,770; Kayad B0 0,664 → 0,662, M1 0,654 → 0,671. Der Sprung von 10 m auf 30 m (BARC M1 0,70 → 0,76) kommt also vom Mitteln der **Messung**, nicht von der Glättung der Vorhersage.

Mögliche Deutung (nicht geprüft): Das NDVI-Signal ist schon bei 10 m räumlich glatt (die Pixel sind größer als die Zellen, dazu Median über Aufnahmen). Nachbarmittel entfernt daher kaum Rauschen, verwischt aber echte kleine Zonen. Das Rauschen der Ertragskarte wird durch die Glättung der Vorhersage nicht berührt.

## 2. Aufbereitung der Kayad-Ertragspunkte (P1, kein Gate)

P1 = Punkte unter 3,0 t/ha und je Fahrspur die ersten 8 und letzten 3 Punkte entfernt, dann Zellmittel mit mindestens 10 Punkten. Zellen: 3 712 → 3 576.

| Kayad (3 FJ) | P0 (wie bisher) | P1 (bereinigt) |
|---|---|---|
| B0, ρ | 0,604 | **0,623** |
| M1, ρ (Leave-One-Year-Out) | 0,596 | 0,605 |
| B0, Lift | 2,54 | 2,86 |
| B0, ρ auf 30-m-Blöcken | 0,664 | 0,698 |
| Positionsmodell K-Raum, ρ | 0,266 | 0,321 |

Lesart: Bereinigte Karte → etwas höheres ρ für alle Verfahren, auch für das Positionsmodell. Es ist ein Zeichen für sauberere **Messung**, nicht für ein besseres Modell. Das Positionsmodell steigt ebenfalls (0,27 → 0,32), ein Teil davon ist also eine glattere Messkarte. Die Produktentscheidung ändert sich dadurch nicht. Zahlen 3,0, 8 und 3 wurden vorab gesetzt und nicht angepasst; ob andere Werte besser wären, ist nicht untersucht (und würde Überanpassung an drei Feld-Jahre bedeuten).

## 3. Kontrollen

| Kontrolle | Ergebnis |
|---|---|
| Zufalls-Vorhersage, geglättet (S1) | BARC −0,033, Kayad P0 +0,022, P1 +0,045 (S0: −0,004 / +0,008 / +0,022): Glättung allein erzeugt keinen Zusammenhang. Kleine Abweichungen von 0 sind Zufall bei 3 Feld-Jahren |
| Positionsmodell K-Raum S0 vs. S1 | BARC 0,028 → 0,027, Kayad 0,266 → 0,267: unverändert (das Modell ist schon glatt) |
| Randabstand ≥ 20 m | BARC B0 0,684 / 0,679 / 0,624 (S0/S1/S2), M1 0,731 / 0,732 / 0,693; Kayad B0 0,588 / 0,561 / 0,537: dieselbe Aussage |

## 4. Datenkritik (AGENTS §3, Kurzfassung)

- **Leakage:** Glättung wird nach der Vorhersage angewendet; die Trainingszeilen enthalten nie Testfelder (Leave-One-Field-Out, Leave-One-Year-Out wie in der Hauptrunde). Bei P1 werden Modelle auf den bereinigten Labels trainiert und getestet (Leave-One-Year-Out, optimistisch wie in der Hauptrunde, weil dieselben Zellen in allen Jahren vorkommen).
- **Mehrfachvergleiche:** 3 Glättungen × 2 Modelle × 2 Standorte plus P1, alle vorab festgelegt. Das Ergebnis ist negativ, es besteht kein Auswahlproblem. Die Vermutung „Glättung hilft“ kam aus der Obergrenzen-Analyse (explorativ) und wurde hier gegen eine strengere, vorab festgelegte Aufgabe getestet und nicht bestätigt.
- **Kayad:** drei Feld-Jahre eines Feldes; Gate R2-Kayad ist beschreibend. Nach Vorab-Regel zählen beide Standorte.
- **Offen:** Fahrspur-Offsets (Kalibrierung zwischen Spuren) und der 18-t/ha-Deckel wurden nicht behandelt; ob sie den Unterschied zwischen 0,62 und der Obergrenze erklären, ist unbekannt.

## 5. Was daraus folgt

- **Produkt:** keine Glättung der Vorhersage. Die Karte bleibt auf 10-m-Zellen (Hauptrunde, B0/B1/M1 unverändert).
- **Falls eine gröbere Karte (20–30 m) gewünscht ist,** dann als eigenes, ehrlich benanntes Produkt: Vorhersage **und** Messung auf 30-m-Blöcken, ρ 0,69 (B0) bis 0,77 (M1) auf BARC. Das ist leichter als 10 m und darf nicht mit dem 10-m-Wert verglichen werden.
- **Aufbereitung der Ertragskarte** ist ein ehrlicher kleiner Gewinn für die *Messung* auf Kayad (Lift 2,54 → 2,86). Wo Rohpunkte vorliegen, ist sie sinnvoll; sie verbessert das Satellitenverfahren selbst nicht.
- **Verbleibender Hebel:** neue Standorte (DWFI, SwissYield) und bessere Ertragskarten, nicht weitere Rechenschritte auf BARC und Kayad.
