# Österreich-Test III: Steiermark mit den Hatzendorf-Excel-Reihen – Ergebnis

Stand 2026-11-06. Protokoll: `reports/freeze_protocol_at3.md` (Tag `freeze-at-3`, vor der Berechnung festgeschrieben). Lauf: `results/2026-10-28_at_test3/` (`metrics.json`, `site_year.csv`, `site_year_scores_2026.csv`, `review_2026.json`, `git_commit.txt`).
Datenkritik: `reports/data_review/at_test3_ergebnis.md` (⚠️ weiter mit Einschränkung). Ein Auswertungslauf, nichts nachträglich geändert, kein Sieger.

> **Kurz: Das vorab festgelegte Kriterium ist bestanden. ρ = 0,77 [0,30; 0,97], n = 15 Standort-Jahre, 9 Jahre.** Der eingefrorene Stress-Score erkennt in der Steiermark die Rangfolge guter und schlechter Jahre, und die zwei blinden Punkte 2026 haben die niedrigsten Scores aller 15 Standort-Jahre.
> **Das ist kein unabhängiger Beweis:** 13 der 15 Punkte waren vorher bekannt, die zwei blinden Punkte stammen aus demselben Jahr, und einfaches NDVI liegt fast gleichauf (0,72).

## 1. Hauptergebnis (S-A, Stichtag 1.9.)

| Auswertung | ρ [95-%-KI] | n / Jahre | Urteil |
|---|---|---|---|
| **S-A Stress-Score → `YAS_site`, Kernvarianten** | **0,77 [0,30; 0,97]** | 15 / 9 | **bestanden** |
| Vergleich: mittleres NDVI (ohne Lernen) | 0,72 [0,27; 0,95] | 15 / 9 | beschreibend |
| Sensitivität 1: alle Varianten des Jahres | 0,77 [0,30; 0,97] | 15 / 9 | beschreibend |
| Sensitivität 2: ohne die gesehenen neuen Punkte (Wagna 2025, Kalsdorf 2020) | 0,69 [0,03; 0,96] | 13 / 8 | beschreibend (unter der Schwelle von 15) |
| Verbund mit Oberösterreich (nicht unabhängig) | 0,52 [0,25; 0,73] | 49 / 9 | beschreibend |
| Nachträglich, nicht im Protokoll: ohne 2026 und ohne die gesehenen neuen Punkte | 0,49 [−0,33; 0,98] (NDVI 0,37 [−0,18; 0,89]) | 11 / 7 | beschreibend |

Stichtage (S-A): 15.7. 0,11 (n = 12, nicht auswertbar), 1.8. 0,45 [−0,20; 0,82] (nicht belegt), 15.8. 0,70 [0,16; 0,91] (bestanden), 1.9. 0,77 (bestanden). Der Stichtag war vorab festgelegt und wurde nicht gewählt.
Innerhalb der Standorte (1.9.): Kalsdorf 0,83 (6 Jahre), Wagna 0,72 (9 Jahre). Leave-one-year-out: 0,66–0,89. Innerhalb eines Jahres ist nicht prüfbar (höchstens 2 Standorte je Jahr).

## 2. Die zwei blinden Punkte 2026

| Standort-Jahr | Score 1.9. | Rang Score (von 15, niedrigster = 1) | Ertrag | `YAS_site` | Rang `YAS_site` (niedrigster = 1) |
|---|---|---|---|---|---|
| Kalsdorf 2026 | −0,052 | 1 | 8,0 t/ha | 0,62 | 3 |
| Wagna 2026 | −0,050 | 2 | 3,3 t/ha | 0,48 | 2 |

Der Score beider Punkte ist etwa doppelt so tief wie der bisher tiefste (Wagna 2025, −0,023). Das niedrigste `YAS_site` hat weiterhin Wagna 2025 (0,33). In absoluten t/ha liegt Kalsdorf 2026 nur auf Rang 7 von 15, weil Kalsdorf insgesamt höher liegt als Wagna. Die zwei Punkte sind **ein** unabhängiges Jahr, nicht zwei.
Ohne 2026 ergibt sich ρ = 0,66 [0,15; 1,00] (n = 13, alle vorher bekannt). Ohne 2026 und ohne die zwei gesehenen neuen Punkte sind es nur noch ρ = 0,49 [−0,33; 0,98] (n = 11, nachträglich gerechnet). **Das Ergebnis trägt sich also stark über wenige Extremjahre** und ist keine allgemeine Trefferquote.

„Blind“ heißt hier: Die Scores 2026 wurden erst nach dem Festschreiben berechnet und danach nicht verändert. Sie standen vor dem Auswertungslauf bereits auf der Konsole, und die Erträge waren bekannt (Details in der Datenkritik §3.4).

## 3. Warum 2026 so tief liegt

Die Maisschläge rund um beide Standorte waren 2026 bis Anfang August normal grün und reiften dann rund drei Dekaden früher ab als üblich (`reports/figures/at_test3_curves.png`). Fast der ganze Score entsteht zwischen dem 9. und dem 28. August.
ERA5-Land passt dazu: 2026 hat an beiden Standorten den heißesten Sommer und den heißesten August seit 2018 (Tagesmaximum August 29,6–29,9 °C), und der August ist der trockenste (28–38 mm). Die Prüfung auf Artefakte steht in der Datenkritik.

## 4. Was sich damit sagen lässt – und was nicht

**Belastbar genug für eine vorsichtige Aussage:**
- Der eingefrorene, an US-Feldern abgeleitete Score reiht in der Steiermark gute und schlechte Jahre (ρ 0,77, KI über 0), wie schon in Oberösterreich (0,50).
- Im Hitze- und Trockensommer 2026 schlug er blind deutlich aus, und die Versuche brachen tatsächlich ein.

**Nicht belegt, ausdrücklich nicht behaupten:**
- Dass der Score mehr kann als einfaches NDVI (0,77 gegen 0,72 bei überlappenden Intervallen).
- Dass er Felder oder Standorte innerhalb eines Jahres unterscheidet. Das ist hier gar nicht prüfbar.
- Dass die Feldkarte in Österreich bestätigt ist. Der Score beschreibt bis zu 100 Maisschläge im Umkreis von 5 km, nicht die 0,2-ha-Versuchsfläche.
- Dass ein tiefer Score immer Ertragsverlust heißt: In Oberösterreich lagen 2018 mehrere Standorte auf ähnlichem oder tieferem Niveau bei normalem Ertrag (Innviertel −0,083 mit `YAS_site` 0,99; Mauthausen −0,055 mit 1,05). Frühe Abreife ist nicht dasselbe wie Verlust.
- Dass 2026 überall so stark einbrach wie in Wagna und Kalsdorf: In Oberösterreich liegen die vier Versuche bei `YAS_site` 0,65–0,97 (Datenkritik §3.3).

## 5. Grenzen

- 13 von 15 Punkten waren vorher bekannt (Protokoll §1); Sensitivität 2 ändert daran nichts Grundsätzliches.
- Nur 2 Standorte, Intervalle weit. Nur die Unterscheidung der Jahre ist geprüft.
- Wagna: Strukturbruch ab 2021, Ursache offen. Kalsdorf: `YAS_site` überall `baseline_short`, das Mittel enthält spätere Jahre.
- Stickstoffversuche messen nicht nur Wetter. Die Ursache von Wagna 2025 und 2026 ist nicht aus den Daten ablesbar.
- INVEKOS 2026 ist Fassung 1 (Stand Mai 2026); frühere Jahre teils Fassung 2.
