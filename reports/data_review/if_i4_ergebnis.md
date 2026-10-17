# Datenkritik I4 – Ergebnisse der Innerhalb-Feld-Studie

Stand 2026-10-17. Ergebnisse: `reports/innerfeld_ergebnis.md`; Lauf `results/2026-10-17_innerfeld/`. Prüfliste nach AGENTS §3.

## 3.1 Repräsentativität

| Frage | Befund | Konsequenz |
|---|---|---|
| Was fällt heraus? | Colorado: 4 von 10 Teilflächen-Jahren (Mittel ≤ 1,04 t/ha) nach vorab festgelegter Regel nicht in der Hauptauswertung. Kayad 2017: 829 statt ~1 400 Zellen (Erntelücken, mindestens 10 Punkte je Zelle verlangt). BARC: Randpuffer und Doppelkulturen wie in Phase 2.3 | Bei Colorado ändert der Einschluss aller 10 das Bild nicht grundlegend (B0 0,548 [0,23; 0,74]); Ausfälle stehen in der Sensitivität |
| Selektion nach Wolken | Zellen ohne klare Aufnahme im Fenster: nur im Merkmal 0 gesetzt (Modelle) bzw. entfernt (B0/B1). Auf BARC korreliert die Anzahl klarer Aufnahmen kaum mit dem Feld-Jahr-ρ (0,18) | kein Wolken-Bias erkennbar; Jahrestrend 0,51 → 0,76 (2017 → 2021) bleibt **unerklärt** |
| Verteilung der Zielgröße | SD des relativen Ertrags: BARC 0,26, Kayad 0,14, Colorado 0,16; Problemzonen-Anteil 28 / 12 / 15 % (Median je Feld-Jahr) | Kennzahlen daneben berichtet; Lift bei Kayad wegen Anteil 12 % höchstens 4 |
| Wenige Fälle | Kayad 3, Colorado 6 Feld-Jahre; 1 Feld bzw. 6 Teilflächen | nur beschreibend, im Bericht so benannt |

## 3.2 Korrektheit der Daten

Siehe `if_i1_daten.md` (Ertragsdaten) und `if_i2_merkmale.md` (Merkmale). Neu in I4: Das **alte Kalenderfenster auf BARC reproduziert 0,676** (berichtet 0,676), das Dekaden-Äquivalent B0 liefert 0,674. Das Dekadenraster ist also kein Qualitätsverlust gegenüber Phase 2.3.

## 3.3 Scheinzusammenhänge

- **Jahres-Proxy:** Alle Merkmale sind innerhalb des Feld-Jahres z-standardisiert und alle Kennzahlen innerhalb des Feld-Jahres berechnet. Jahresniveau kann nicht eingehen.
- **Orts-Proxy:** Kein Koordinatenmerkmal in M1/M2. Das Positionsmodell K-Raum (nur x, y) erreicht auf BARC 0,03 und im Transfer −0,22…0,33. Das Satellitensignal ist keine glatte räumliche Tendenz.
- **Label-Shuffle:** Mittelwert der 20 Wiederholungen +0,03 (BARC) und −0,03 (BARC → Kayad), innerhalb ±0,10. Einzelne Wiederholungen bis 0,45/0,52 im Betrag, weil Ridge bei stark verwandten Merkmalen ein zufälliges Vorzeichen wählt. Der Vorab-Wortlaut ist mehrdeutig (Mittelwert oder jede Wiederholung); beide Lesarten sind im Bericht offengelegt, Urteil „✓ mit Vorbehalt“. Das echte M1 (0,70) liegt über allen 20 Wiederholungen.
- **Adversarial Validation:** nicht durchgeführt (die Testzellen sind in Leave-One-Field-Out und Leave-One-Site-Out vom Training räumlich getrennt; Feld-Jahre desselben Feldes werden gemeinsam ausgelassen).
- **Konfundierung:** variable Stickstoffgabe (Kayad), unbekannte Sorten/Aussaat, Fahrgassen. Auf Kayad zeigen die Karten Fahrstreifenmuster; der Median-ρ von 0,60 kann teils darauf beruhen. Das ist in der Abbildung sichtbar und im Bericht genannt, aber nicht aufgelöst.
- **Merkmalskorrelation:** NDVI und NDRE der drei Fenster sind stark verwandt; Ridge (α = 1, Gewichte = 1/Zellen je Feld-Jahr) stabilisiert, aber Koeffizienten werden nicht gedeutet.

## 3.4 Leakage

- Test-Feld/-Jahr/-Standort nie im Training (Leave-One-Field-Out über `field_cluster`, Leave-One-Year-Out nur bei Kayad, Leave-One-Plot-Out bei Colorado, Transfer und Leave-One-Site-Out über ganze Standorte). Test `test_innerfeld_run.py` prüft Gewichtung und Shuffle, `test_innerfeld_features.py` die Lokalität der z-Werte.
- **Kayad Leave-One-Year-Out ist optimistisch:** dieselben Zellen kommen in allen drei Jahren vor, das Modell kann Ortsmuster lernen. Deshalb als „beschreibend, optimistisch“ markiert; das Positionsmodell (K-Raum) ist dort 0,27, M1 0,60.
- **B2 (Wiederkehr) nutzt Erträge anderer Jahre** und ist kein Satellitenmodell; nur als Orientierung berichtet.
- Parameter (Suchbereich, Fenster, α, Gewichte, Schwellen) vor dem Lauf committet (`ca0f987`); nur die Ausgabe der Einzelwerte des Label-Shuffle wurde nach dem ersten Lauf ergänzt (alle anderen Zahlen unverändert, verglichen). Österreichische Daten nicht verwendet.

## 3.5 Plausibilität und Fälle

- Schlägt M1 die Basis? Auf BARC +0,046 (B1) und +0,037 (B0), klein, mit KI > 0. Kein Wert „zu gut“: alle ρ liegen zwischen 0,5 und 0,8, keine Auffälligkeit wie ρ > 0,9.
- **Beste BARC-Feld-Jahre:** EastFarm_5_3B 2019 (ρ 0,88), EastFarm_5_23 2019 (0,82), CentralFarm_1_14 2020 (0,82). **Schlechteste:** APU_1 2021 (0,06), CentralFarm_2_71 2019 (0,12), CentralFarm_2_68B 2018 (0,37). Für die zwei schwächsten gibt es keine auffälligen Datenmerkmale (Zellzahl, klare Aufnahmen); Ursache offen.
- **Colorado S2 2019** (ρ = −0,08, B0): einziges negatives Feld-Jahr; mit 13 Punkten und dem höchsten Mittelertrag (6,35 t/ha) und SD des relativen Ertrags 0,12 liegt kaum Variation vor.
- **Kayad 2018** hat das schwächste ρ (0,43; B1 0,11): das Maximum der Kurve liegt in Dekade 8 (20.–29.6.); warum das Spitzenfenster dort schwächer ist als das Kalenderfenster, wurde nicht untersucht (vermutlich anderes Entwicklungsstadium, nicht geprüft).
- Streifenmuster und Lücken in den Kayad-Karten (2017) stammen vermutlich von Ernte und Düngung, nicht vom Satelliten (nicht geprüft).

## 3.6 Entscheidung

⚠️ **Weiter mit Einschränkung.** Belastbar: BARC (K1 ✓, J3a ✓ mit Vorbehalt). Nicht prüfbar: J2, J3b. Offen für die Deutung: Label-Shuffle-Wortlaut, Jahrestrend auf BARC, zwei schwache BARC-Feld-Jahre, Fahrstreifen/N-Düngung auf Kayad. Folgeschritt: Standorte mit ≥ 10 Feld-Jahren beschaffen (DWFI, SwissYield), danach J2/J3b mit unveränderten Vorab-Regeln.
