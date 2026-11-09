# Österreich-Test IV: Maisfelder 2026 der Hagelversicherung – Ergebnis

Stand 2026-11-09. Protokoll: `reports/freeze_protocol_at4.md` (Tag `freeze-at-4`, vor jedem Satellitenwert der Testfelder festgeschrieben).
Lauf: `results/2026-11-09_at_test4/` (`metrics.json`, `config_at_test4.yaml`, `git_commit.txt`). Feldgenaue Tabellen nur lokal unter `data/interim/at4/`.
Datenkritik: `reports/data_review/at_test4.md` (⚠️ weiter mit Einschränkung). Ein Auswertungslauf, nichts nachträglich geändert, kein Sieger.

> **Kurz: Das vorab festgelegte Kriterium ist deutlich bestanden. ρ = 0,84 [0,78; 0,88], n = 635 Felder in 125 Zellen.**
> Der eingefrorene, an US-Feldern abgeleitete Stress-Score reiht die Körnermaisfelder 2026 fast so wie ihr Ertrag. Das ist der erste Test **zwischen Feldern innerhalb eines Jahres**, und die Scores waren blind.
> **Aber:** Einfaches NDVI schafft dasselbe, sogar etwas mehr (0,87; Unterschied −0,03 [−0,05; −0,01]). Und es ist ein einziges Jahr, ein extremes Trockenjahr.

## 1. Hauptergebnis (Stichtag 1.9.)

| Auswertung | ρ [95-%-KI] | n / Zellen | Urteil |
|---|---|---|---|
| **Stress-Score → Ertrag (t/ha)** | **0,84 [0,78; 0,88]** | 635 / 125 | **bestanden** |
| Vergleich: mittleres NDVI (ohne Lernen) | 0,87 [0,81; 0,90] | 635 / 125 | beschreibend |
| Score minus NDVI (gepaart) | −0,03 [−0,05; −0,01] | 635 | NDVI leicht besser |
| Innerhalb 20-km-Zellen, Median (Score / NDVI) | 0,71 / 0,70 | 25 Zellen ≥ 8 Felder | beschreibend |
| Sensitivität: Ertrag auf 14 % Feuchte | 0,84 [0,79; 0,88] | 622 / 120 | beschreibend |
| Sensitivität: ohne Felder mit abruptem Abfall | 0,87 [0,80; 0,91] | 444 / 114 | beschreibend |
| Sensitivität: mit den 41 unplausiblen Erträgen | 0,76 [0,63; 0,86] | 676 / 129 | beschreibend |

Stichtage (Hauptauswertung): 15.7. 0,55 [0,43; 0,65] (n = 226, die meisten Felder haben bis dahin zu wenige Dekaden), 1.8. 0,77 [0,70; 0,82], 15.8. 0,84 [0,78; 0,88], 1.9. 0,84. Der Stichtag war vorab festgelegt.

## 2. Was das praktisch heißt
- **Ertrag je Score-Fünftel:** 3,1 → 4,9 → 6,1 → 8,4 → 11,6 t/ha (je 127 Felder). Das Fünftel mit dem tiefsten Score erntete im Mittel knapp ein Viertel dessen, was das höchste erntete.
- **Problemfelder:** Von den 127 Feldern mit dem tiefsten Score (unterste 20 %) gehören **70 %** auch zu den 20 % mit dem tiefsten Ertrag. Zufällig wären es 20 %.
- Schon am **1. August** liegt ρ bei 0,77, also rund sechs Wochen vor der Ernte.

## 3. Ist das zu gut, um wahr zu sein? (Prüfungen, Details in der Datenkritik)
- **Fläche ist kein Artefakt:** Der Ertrag je ha entsteht durch Teilen durch die Fläche, aber Score und Fläche hängen nicht zusammen (ρ −0,03). Ohne Flächeneinfluss bleibt ρ 0,84; in den Größenklassen 1–2, 2–4 und > 4 ha: 0,85 / 0,85 / 0,81.
- **Nicht nur Region:** In allen vier Ost-West-Streifen 0,79–0,84, innerhalb der 20-km-Zellen im Median 0,71. Im Westen ernteten die Felder im Mittel 9,0 t/ha, im Osten 4,6 t/ha; der Score erkennt aber auch die Unterschiede *innerhalb* der Gegend.
- **Label-Shuffle:** Mit zufällig vertauschten Erträgen fällt ρ auf 0,00.
- **Leakage ist ausgeschlossen:** Der Score benutzt keinen Ertrag und keinen österreichischen Wert. Referenzkurve und Regeln stammen aus `freeze-at-1` (2026-10-17).
- **Offen und wichtig:** Ob die Hagelversicherung Erträge teilweise selbst aus Satellitenbildern geschätzt hat, ist nicht geklärt. Dann wäre der Zusammenhang teilweise zirkulär. Erntefeuchte und krumme Mengen sprechen für echte Wiegungen. Vor Zitaten beim Lieferanten nachfragen.

## 4. Warum der Zusammenhang 2026 so stark ist
2026 war ein Hitze- und Trockensommer (Test III). Die Erträge streuen deshalb extrem (1,5–16 t/ha), und die Schäden zeigen sich direkt im Grün: Felder, die im August früh braun wurden, brachten wenig.
30 % der Felder haben einen abrupten Abfall (früh abgereift oder früh geerntet), sie ernteten im Mittel 5,8 statt 7,3 t/ha. Bei großer Streuung ist eine hohe Rangkorrelation leichter.
In einem normalen Jahr wären die Unterschiede kleiner und ρ vermutlich deutlich tiefer.

## 5. Was sich damit sagen lässt – und was nicht

**Belastbar:**
- Der eingefrorene, nur an US-Daten abgeleitete Score unterscheidet in Österreich **Felder innerhalb eines Jahres**: ρ 0,84 bei 635 blinden Feldern, auch innerhalb einzelner Gegenden. Das war in den Tests I–III nie prüfbar.
- Er funktioniert früh genug, um vor der Ernte zu warnen (1.8.: 0,77).

**Nicht belegt, ausdrücklich nicht behaupten:**
- Dass der Score mehr kann als einfaches NDVI. Hier ist NDVI sogar knapp, aber statistisch erkennbar besser.
- Dass das in normalen Jahren genauso gut klappt (ein Jahr, Extremjahr).
- Dass die Feldkarte (innerhalb eines Feldes) bestätigt ist. Geprüft ist nur das Feldmittel.
- Dass der Score die *Ursache* erkennt (Trockenheit, Hagel, Boden, Sorte): Er misst, wie viel grüner Bestand fehlt.

## 6. Grenzen
- Ein Jahr, ein Extremjahr. Versicherte Betriebe, rund 1 % der Maisfläche, Schwerpunkt Niederösterreich.
- Erträge nicht qualitätskontrolliert; Einheit „Gesamt-kg je Feldstück“ aus dem Verhältnis zur Fläche erschlossen; nass oder trocken gewogen ist offen (die 14-%-Rechnung ändert nichts).
- Die Erträge waren dem KI-Assistenten vorher bekannt (Protokoll §1). Blind waren die Scores.
- 8 der 676 abgefragten Felder überschneiden sich mit Schlägen aus Test III (dort nur Mittelwerte, keine Feldertrag-Zuordnung).
- **Offengelegt:** Der erste Auswertungslauf brach ab, bevor eine Kennzahl entstand. Beim Wiedereinlesen der Bereinigungstabelle wurde das leere Feld „behalten“ als fehlend gelesen, die Tabelle war leer. Behoben nur beim Einlesen; Regeln, Felder und Metriken unverändert.
