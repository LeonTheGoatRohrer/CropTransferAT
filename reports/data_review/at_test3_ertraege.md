# Datenkritik – Hatzendorf-Excel-Reihen (Wagna, Kalsdorf) für den Österreich-Test III

Zu `reports/freeze_protocol_at3.md` (`freeze-at-3`). Geprüft ist nur die **Ertragsseite** vor dem Freeze; die Satellitenseite 2026 wird nach der Berechnung der Scores im Ergebnisbericht geprüft.
Entscheidung: ⚠️ **weiter mit Einschränkung.**

## 3.1 Auswahl / Repräsentativität
- **Geprüft wie:** Varianten je Standort und Jahr gezählt (`at_test3.tidy_yields`).
- **Befund:** Wagna 12 Varianten in allen 20 Jahren 2007–2026 (240 Werte). Kalsdorf 29 Variantenkürzel 2009–2026 (288 Werte), davon 17 in jedem gezählten Jahr ab 2013 (Kernvarianten).
  Nicht dauerhaft: C, I, P, S (bis 2015/2016), Z1–Z4 (2016–2020), Z5–Z8 (ab 2021). Kalsdorf ohne Mais 2017 und 2019 (Sorghum), 2023 nicht gewertet (Feldtag), 2025 leer (Sämaschine).
- **Konsequenz:** Standortertrag = Mittel der Kernvarianten, damit keine Zusammensetzungs-Sprünge entstehen; „alle Varianten“ nur als Sensitivität. Für den Test zählen Wagna 9 und Kalsdorf 6 Standort-Jahre (2018–2026).

## 3.2 Sind die Daten korrekt?
- **Gegenprobe mit der alten Quelle** (`data/raw/at_trials.csv`, aus den Versuchsberichten abgeschrieben, Versuchsart `duengung`): Das Mittel über **alle** Varianten der Excel-Reihe stimmt
  für Wagna 2013–2023 und Kalsdorf 2014–2024 auf ≤ 0,005 t/ha mit den Berichtswerten überein. Abweichungen: Wagna 2024 7,338 statt 7,292 t/ha (+0,6 %, vermutlich nachträglich korrigiert),
  Kalsdorf 2013 10,157 statt 10,072. Damit sind Einlesen, Einheit (dt/ha → t/ha) und Feuchtebasis (14 %, wie in den Berichten) bestätigt.
- **Einlese-Fehler gefunden und behoben (vor dem Freeze):** Zuerst wurde die Beschreibungs- statt der Kürzelspalte gelesen (Wagna: „2x KAS“ für A, B und K zusammengelegt), und eine Hilfstabelle weiter
  unten im Wagna-Blatt verwendet das Kürzel „0“ erneut (Werte bis 6451). Jetzt: Kürzelspalte 59/63, je Kürzel nur die erste Zeile; Test `tests/test_at_test3.py`. Wertebereich danach 8,2–185,3 dt/ha.
- **Extremwerte:** Wagna 2013 2,8 t/ha, **2025 2,4 t/ha**, 2026 3,3 t/ha; Kalsdorf 2026 8,0 t/ha. Alle Varianten einschließlich der Kontrolle fallen gemeinsam, also kein Einzelfehler.
  Die Ursache (Trockenheit, Hagel, Technik) ist nicht in den Daten; Anfrage an die Station.
- **Strukturbruch Wagna ab 2021:** Mittel 2018–2020 ≈ 10,3 t/ha, 2021–2024 ≈ 6,9 t/ha; auch die 0-N-Kontrolle fällt (≈ 5,0 → 2,3–3,0 t/ha). Ein Wechsel von Fläche oder Sorte ist möglich;
  `YAS_site` (Bezug auf die 5 Vorjahre) kann deshalb 2021–2023 zum Teil Versuchsdesign statt Wetter messen. Bleibt als Grenze im Protokoll.
- n/a: Indizes, Wolken, Feldzuordnung (keine Satellitendaten in diesem Schritt).

## 3.3 Scheinzusammenhänge
- Die Versuchsfläche ist nicht die Fläche des Scores (bis zu 100 Maisschläge im Umkreis von 5 km). Stickstoffstufen, Sorte, Saattermin und Hagel sind Störgrößen.
- Mit höchstens 2 Standorten je Jahr ist nur die Unterscheidung der **Jahre** prüfbar.

## 3.4 Leakage / Österreich-Regel
- Das Modell wird nicht verändert; die Excel-Erträge gehen nur als Testziel ein.
- **Blindheit:** Vor dem Freeze wurden die Scores 2018–2025 (aus `at-test-2`) und die neuen Erträge gemeinsam gesehen, auch Wagna 2025 und Kalsdorf 2020. Blind sind nur die Scores 2026.
  Offengelegt im Protokoll §1; Sensitivität ohne die beiden gesehenen neuen Punkte ist vorab festgelegt.
- `YAS_site` Kalsdorf ist überall `baseline_short` (Mittel der anderen Jahre, auch späterer). Das ist die unveränderte Regel aus `freeze-at-1`, aber für Kalsdorf ein Vergleich mit Zukunftsjahren.

## 3.5 Plausibilität
- `YAS_site` 2018–2026: Wagna 0,34–1,14, Kalsdorf 0,62–1,28. Keine Rechenartefakte (Basis 6,8–12,9 t/ha). Fallbeispiele: Wagna 2020 1,14 (bestes), Wagna 2025 0,34 (schlechtestes).

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung:** Daten sind korrekt eingelesen und mit der alten Quelle stimmig. Grenzen: Strukturbruch Wagna, offene Ursache der Extremjahre, nur 2 blinde Standort-Jahre.
