# Datenkritik – Österreich-Test III, Satellitenseite 2026 und Ergebnis

Zu `reports/at_test3_ergebnis.md`. Die Ertragsseite ist in `at_test3_ertraege.md` geprüft. Zahlen: `results/2026-10-28_at_test3/review_2026.json`, erzeugt mit `python -m croptransfer.at_test3_review`. Alles hier ist beschreibend und ändert weder Test noch Modell.
Entscheidung: ⚠️ **weiter mit Einschränkung.**

## 3.1 Auswahl / Repräsentativität
- **Geprüft wie:** Auswahl nach `freeze-at-1` (Code 105, ≥ 1 ha, 5 km, Zufallsstart wie `at_fields.select_year`, Position in der Liste aller Standorte).
- **Befund:** je 100 Schläge, davon am 1.9. 100 gültig. Am 15.7. nur 29 (Kalsdorf) bzw. 83 (Wagna) gültig; dieser Stichtag ist mit n = 12 nicht auswertbar.
- **Konsequenz:** kein Ausschluss am Hauptstichtag.

## 3.2 Sind die Daten korrekt?
- **Vorab verlangte Gegenprobe (Protokoll §2):** 2024 mit denselben Regeln neu gerechnet, frisch aus Earth Engine. Dieselben 200 Schläge, alle Scores und NDVI-Werte gleich (Toleranz 10⁻⁹). **Bestanden**, also kein Stopp (`results/2026-10-28_at_test3/replication_2024.json`).
- **Einzelne schlechte Szene?** Nein. Im August 2026 fällt das Median-NDVI über viele Szenen stetig (Wagna 0,83 am 2.8. → 0,68 am 19.8.; Kalsdorf 0,80 → 0,69 am 24.8.).
- **Ein Sensor?** Nein. Score nur Sentinel/nur Landsat: Wagna −0,051 / −0,036, Kalsdorf −0,052 / −0,073. Die Landsat-Werte beruhen auf weniger Szenen.
- **Mais?** Anteil Schläge mit NDVI-Maximum unter 0,6: 0 %. Die Kurvenform passt zu Mais (`reports/figures/at_test3_curves.png`).
- **Frühe Ernte:** Der abrupte Abfall betrifft 2026 48 % (Wagna) und 27 % (Kalsdorf) der Schläge; sie drücken den Score. Ohne sie bleibt 2026 am tiefsten (−0,029 / −0,036, sonst höchstens −0,021). Die Ernte der Versuche war laut Feldplan am 1.9. (Wagna) und 15.9. (Kalsdorf). Frühe Ernte, Silomais-ähnliche Nutzung und Notreife lassen sich aus den Bildern nicht trennen.
- **Sensordichte:** Seit 2025 gibt es deutlich mehr Szenen (2026: 99 und 119; 2018–2024: 49–82). Das treibt den Effekt aber nicht: Die Dekade 14 (19.–28.8.) ist in fast allen Jahren voll beobachtet.
  **Die Ausnahme ist 2022** (Wagna 13 %, Kalsdorf 8 % beobachtet). Der Score 2022 ist deshalb vermutlich zu mild: Wagna 2022 läge mit nur voll beobachteten Schlägen bei −0,047 statt −0,019. Mit dieser Variante ist ρ = 0,75 [0,30; 0,95], n = 14 (Kalsdorf 2022 fällt weg). Das Ergebnis hängt also nicht daran.
- **Wetter als unabhängige Gegenprobe (ERA5-Land):** 2026 ist an beiden Standorten der heißeste Sommer seit 2018 (Tagesmaximum Juni–August 27,7–28,2 °C) mit dem heißesten und trockensten August (29,6–29,9 °C, 28–38 mm). ERA5 hat ~9 km Auflösung und beschreibt nicht das einzelne Feld.
- **Fassung:** INVEKOS 2026-1 (Stand Mai 2026, ZIP-SHA-256 in `DATA_SOURCES.md`) enthält Anträge, keine Prüfung der späteren Nutzung.

## 3.3 Scheinzusammenhänge
- **Jahres-Effekt:** Der Score ist 2026 auch in Oberösterreich tief (Kontrolle ohne Protokollrolle, siehe Tabelle). Bei Linden, Mauthausen und Bad Wimsbach ist es der tiefste Wert seit 2018, bei Walding und Innviertel nicht. 2026 ist also ein großräumiges Signal, kein steirisches. Das passt zur Hitze, zeigt aber auch: Der Test misst Jahre, nicht einzelne Standorte.
- **Gegenprobe Oberösterreich (nachträglich, außerhalb des Protokolls, nicht im Kriterium).** Linden und Mauthausen waren vorab gewählt; Walding, Bad Wimsbach und Innviertel kamen nach Hinweis der Protokollprüfung dazu, weil sie die übrigen Standorte mit Versuch 2026 sind:

  | Standort 2026 | Score 1.9. | `YAS_site` | Ertrag |
  |---|---|---|---|
  | Bad Wimsbach | −0,079 | 0,81 | 11,3 t/ha |
  | Linden | −0,078 | 0,65 | 8,2 t/ha |
  | Mauthausen | −0,065 | kein Versuch | – |
  | Walding | −0,043 | 0,84 | 10,6 t/ha |
  | Innviertel | −0,035 | 0,97 | 12,3 t/ha |

  Alle vier Versuche liegen unter dem üblichen Niveau, aber nur Linden bricht ähnlich stark ein wie die Steiermark. Das sind Sortenversuche, also eine andere Versuchsart, und n = 4 trägt keine Korrelation.
- **Fehlalarm-Muster bleibt:** 2018 hatten Innviertel (−0,083, `YAS_site` 0,99), Mauthausen (−0,055; 1,05), Bad Wimsbach (−0,046; 1,02) und Linden (−0,030; 1,19) tiefe Scores bei normalem bis überdurchschnittlichem Ertrag. Innviertel 2018 liegt sogar tiefer als alle Werte 2026. Ein tiefer Score kann frühe Abreife ohne Verlust sein, wie schon in `at_test_ergebnis.md` §5 vermutet. Die Blindpunkte dürfen deshalb nicht als allgemeine Trefferquote gelesen werden.
- **Score ≈ NDVI:** ρ 0,77 gegen 0,72. Ein Mehrwert gegenüber einfachem Grün ist nicht gezeigt.
- Label-Shuffle: n/a, es wird nichts trainiert.

## 3.4 Leakage / Österreich-Regel
- **Modell nach dem Freeze verändert?** Nein. Prüfsummen von Konfiguration, Ausgangsscores und Excel-Tabelle vor dem Lauf nachgerechnet und gleich; `tests/test_at_test3.py` prüft sie weiter.
- **Code nach dem Freeze:** `at_test.py` hat einen optionalen Ordner-Parameter bekommen (Standard unverändert; die Gegenprobe bestätigt gleiche Werte). In `at_test3.py` kamen Parzellenauswahl, Gegenprobe und der im Protokoll §3 verlangte, zuvor fehlende Verbund mit Oberösterreich dazu. Kein Eingriff in Auswahl, Definitionen, Metriken oder Kriterien.
- **Blindheit, genau genommen:** Die Scores 2026 wurden erst nach dem Festschreiben berechnet und danach nicht verändert. Sie waren aber nicht bis zuletzt verdeckt: `--scores-2026` gab sie um 12:49:33 auf der Konsole aus, sichtbar für den KI-Assistenten, also vor dem Code-Commit `8710b8f` (12:50:07) und dem Auswertungslauf (`metrics.json` 12:50:44). Die Erträge 2026 waren schon vorher bekannt (Protokoll §1). Zwischen Ausgabe und Auswertung wurde nichts an Code, Konfiguration oder Scores geändert; der Commit enthält genau den Stand, mit dem die Scores gerechnet wurden. Die Auswertung folgt festgelegten Regeln ohne Wahlmöglichkeit. Blind ist also: Die Satellitenseite wurde festgelegt, bevor sie berechnet wurde.
- Österreichische Daten wurden nicht für Training oder Modellwahl genutzt.

## 3.5 Plausibilität
- **Zu gut?** ρ 0,77 ist höher als in Oberösterreich (0,50) und wurde deshalb als Verdachtsfall geprüft. Kein Artefakt gefunden. Die weiten Intervalle bei n = 15 reichen bis 0,30; der wahre Wert kann also deutlich niedriger liegen. 13 Punkte waren bekannt, und die zwei Blindpunkte sind ein einziges Jahr. Ohne 2026 und die zwei gesehenen neuen Punkte bleibt ρ = 0,49 [−0,33; 0,98], n = 11 (nachträglich): Das Ergebnis trägt sich stark über wenige Extremjahre.
- **Fallbeispiele:** Beste Übereinstimmung Kalsdorf 2020 (Score fast 0, Ertrag hoch), Wagna 2025/2026. Schlechteste: Wagna 2023 (Score fast 0, `YAS_site` 0,78; 7,0 t/ha trotz guter Kurve, im Strukturbruch ab 2021) und Wagna 2018 (−0,014, Ertrag normal, 23 % abrupter Abfall).

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Das Ergebnis ist korrekt gerechnet, und das Signal 2026 ist real im Sinn von „die Felder wurden früh braun“. Aussagen nur auf Ebene der Jahre, nie als allgemeine Trefferquote, immer mit den Hinweisen „13 von 15 bekannt“, „ein blindes Jahr“ und „NDVI fast gleichauf“.

**Unabhängige Protokollprüfung (zweite Claude-Sitzung, 2026-11-06):** Urteil und Kernzahlen bestätigt, `YAS_site` direkt aus den Excel-Dateien nachgerechnet. Aufgrund ihrer Hinweise korrigiert: Rundung der KI-Obergrenze (0,97 statt 0,98), Blindheitsaussage, vollständige Oberösterreich-Kontrolle, Beschriftung des Rangs. Zusätzlich korrigiert: Leave-one-year-out-Untergrenze (0,66).
