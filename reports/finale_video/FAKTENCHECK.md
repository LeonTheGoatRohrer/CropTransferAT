# Faktencheck Finale-Video (Prototyp, 2026-11-06)

Jede Zahl aus Bild und Sprechtext, mit Quelle. **Automatisch** heißt: `pitch/finale/render/export_data.py` liest den Wert aus der Quelle und bricht ab, wenn er nicht mehr zum Film passt. **Von Hand** heißt: Ich habe den Wert beim Bau in der Quelle nachgelesen. Sprechtext: `pitch/finale/render/voice_lines.tsv`.

## Neuer Anfang (erste 30 s, Stand 2026-11-07)

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| „Ein Maisfeld siehst du nur vom Rand“, „oft zeigt es erst die Ernte“ | keine Zahl | Vorgabe des Projektinhabers, allgemeine Beschreibung des Problems. **Im Repository nicht quantifiziert** | nicht belegbar als Zahl |
| „Der Mähdrescher misst bei der Ernte, Meter für Meter“ | 8.472 Messpunkte in diesem Feld | echte Spur, `opener.py`; im Bild „Echte Spur. Echte Messwerte.“ Der Flug davor ist KI-generiert und gekennzeichnet | von Hand |
| „Dürre. Befall. Unwetter.“ | keine Zahl | Vorgabe des Projektinhabers: mögliche Ursachen. Das Verfahren erkennt die Ursache **nicht**; das sagt der Film später („wo, nicht warum“) | von Hand |
| Satellit alle paar Tage, frei für alle | – | Sentinel-2, `DATA_SOURCES.md`, Drehbuch §3 | von Hand |
| Unterzeile „Schon im Sommer sehen, wo im Feld Ertrag fehlt“ | 0,68, 41 Feld-Jahre | NDVI 16.7.–15.8. gegen Ernte-Ertrag, `hauptergebnis.md` §1. Gilt belastbar nur für BARC, das sagt der Film bei 1:45. Keine Vorhersage von Einbrüchen | von Hand |
| Eigenes Feld einstellen, Warnschwelle, Nachricht aufs Handy | Schwelle 10 % ist ein Beispiel | **Zielbild.** Die Benachrichtigung gibt es in der Website nicht, gezeichnete Felder laufen nur als Simulation (`web/src/pages/Analyse.tsx`). Im Bild steht „Zielbild: Die Benachrichtigung ist noch nicht umgesetzt“, die Stimme sagt „Das Ziel“ | im Code gesucht |
| Maisschlag im Handy | 2,9 ha, 2,85 ha gemessen | `pitch/intro/assets/map_ortho.json`, echter INVEKOS-Schlag 2024, Luftbild basemap.at 2024 (CC BY 4.0) | von Hand |
| Feldkarte in der Nachricht | Beispiel | Echte BARC-Daten, schwächstes Viertel der Pixel, nicht der Schlag aus dem Luftbild | im Bild als Beispiel gekennzeichnet |

## Einstieg und Problem

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| Satellitenhöhe (nur noch als Einblendung) | 786 km | Einstieg `render/opener.py`, Drehbuch §1. Bahnhöhe von Sentinel-2, **nicht aus einem Projektbericht** | von Hand, nur Drehbuch |
| GPS-Messpunkte des Beispielfeldes | 8.472 | `data/raw/barc/2021.zip`, `opener.py` | beim Rendern des Einstiegs berechnet |
| Zellen des Beispielfeldes | 1.338 | `export_data.py`, Feld `EastFarm_5_12` 2021 | automatisch berechnet |
| Rangkorrelation des Beispielfeldes | 0,68 | `opener.py`, Drehbuch §1 | beim Rendern berechnet |
| Ertrag reicht von „40 bis fast 140 %“ | 0,39 bis 1,39 relativ | Drehbuch §2, `export_data.py` (`field.min`, `field.max`) | automatisch berechnet |
| Keine öffentlichen Erträge einzelner Felder in Österreich | – | `reports/doku/01_motivation.md` Zeile 13 | von Hand |
| Ertragskarte „fehlt meist“ | keine Zahl | Vorgabe im Auftrag des Projektinhabers. **Im Repository nicht quantifiziert**, deshalb ohne Prozentwert | nicht belegbar als Zahl |

## Lösung

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| Median-Rangkorrelation | 0,68 [0,54; 0,71] | `reports/doku/hauptergebnis.md` §1 | automatisch: aus Rohwerten neu gerechnet 0,676 |
| Feld-Jahre, Felder | 41, 27 | `hauptergebnis.md` §1 | automatisch gezählt |
| In allen Fällen positiv | 41 von 41 | `hauptergebnis.md` §1 | automatisch gezählt |
| Skala der Rangkorrelation: „0 kein Zusammenhang“, „1 exakt dieselbe Reihenfolge“ | – | Definition der Rangkorrelation (Spearman), ersetzt „perfekt“. Bewusst nicht „100 % Genauigkeit“: Sie misst keine Genauigkeit | von Hand |
| Schwächstes Viertel trifft Problemzone, im Film „58 von 100“ | 58 % | `results/2026-10-16_feinjust_ablation/product.json`: 0,580 | von Hand |
| Zufallswert, im Film „27 von 100“ | 27 % | `product.json`: 0,275 (Bericht: 27 %) | von Hand |
| „Rund doppelt so oft getroffen“ (nur im Bild) | 0,580 / 0,275 = 2,1 | gerechnet aus `product.json`. Der Bericht `innerfeld_ergebnis.md` nennt für eine vergleichbare Größe einen Lift von 2,26 | von Hand |
| Problemzone | unter 85 % des Feldmittels | `hauptergebnis.md` §1 | von Hand |
| Modellvarianten | 782 in 11 Blöcken | `hauptergebnis.md` §5, **nur im Haupt-Checkout**, nicht auf diesem Branch | automatisch: Summe der Blöcke |
| Drei Ergebnisse, zwei ohne Training | 3, 2 | `hauptergebnis.md` §5, letzter Absatz | von Hand |
| Karte im Feld und Stress-Score nicht unter den 782 (Fußzeile) | – | `hauptergebnis.md` §5, „Was nicht mitgezählt ist“ | von Hand |
| Innerhalb des Feldes gelernt 0,70 statt 0,67, auf anderen Standorten nicht besser (Fußzeile) | 0,70 [0,64; 0,75], 0,67 [0,59; 0,74] | `reports/innerfeld_ergebnis.md`, Kurzfassung 1, 4, 5 | von Hand |
| Gescheitert: Radar, Wärmebild, drei Runden Jahresvorhersage | – | `hauptergebnis.md` §4 | von Hand |

Wärmebild steht für die im Bericht genannte Oberflächentemperatur.

## Daten und Österreich

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| 16 EU-Länder (ohne Österreich) | 16 | `hauptergebnis.md` §2 | von Hand |
| USA, Italien, Afrika | – | `SUPPORT.md`, `reports/data_review/if_i1_daten.md` | von Hand |
| Österreichische Werte im Training | 0 | `PLAN.md` §0, `reports/data_review/at_test3_ergebnis.md` §3.4. Gilt für die getesteten, eingefrorenen Regeln und Modelle, so auch die Fußzeile | von Hand |
| 5 der 782 Varianten als getrennter Zusatz mit österreichischen Erträgen (Fußzeile) | 5 | `hauptergebnis.md` §5, Block „Österreich, explorativ“ | von Hand |
| „Erster Test bestanden“, „Ohne jede Anpassung“ | Kriterium V2-A: bestanden | `reports/at_test_ergebnis.md` Kurzfassung 1, `reports/freeze_protocol_at.md` §0, §4. Explorativ, Kriterium nur ρ über 0 mit Intervall ohne 0; beides steht in der Fußzeile | von Hand |
| Geprüft ist der Stress-Score, nicht die Karte im Feld | – | `reports/freeze_protocol_at.md` §1; steht im Bild, weil die Stimme nur „die Regel“ sagt | von Hand |
| Oberösterreich, Rangkorrelation | 0,50 [0,19; 0,68] | `reports/at_test_ergebnis.md`, `metrics.json`: 0,496 | automatisch |
| Standort-Jahre, Jahre | 34, 7 | `reports/at_test_ergebnis.md` | von Hand |
| Standorte im selben Jahr: im Bild „nicht belegt“, gesprochen „noch nicht“ | Median −0,10 | `reports/at_test_ergebnis.md` | von Hand |
| Einfacher Grünwert „schafft dasselbe“ | 0,50 | `reports/at_test_ergebnis.md` | von Hand |
| Steiermark nicht auswertbar | 12 statt 15 | `reports/at_test_stmk_ergebnis.md` | automatisch: n = 12 |

## Prototyp

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| Feld D: Alarm | Risiko 0,536, Schwelle 0,532 (Film: 0,54 und 0,53) | `web/public/data/fields.json` | von Hand |
| Feld D: geerntet | 5,86 t/ha, 75 % des Üblichen | `fields.json` | von Hand |
| Feld D: im Juli unter der Referenz | `main_phase`: Juli | `fields.json` | von Hand |
| Feld E: kein Alarm, knapp unter der Schwelle | Risiko 0,519 | `fields.json` | von Hand |
| Feld E: geerntet | 6,01 t/ha, 77 % | `fields.json` | von Hand |

## Nach der Abgabe

| Aussage im Film | Wert | Quelle | Prüfung |
|---|---|---|---|
| Abgabe | So, 18.10.2026 | Auftrag des Projektinhabers; **kein Beleg im Repository** | nicht geprüft |
| ETH Zürich antwortete | Mo, 19.10., 09:44 | Auftrag, Drehbuch §9 (Mail Perich). **Mail nicht im Repository** | nicht geprüft |
| ZALF, Brandenburg, Ertragskarte | 27.811 Punkte, gesprochen „fast achtundzwanzigtausend“ | Auftrag, Drehbuch §9. **Kein Beleg im Repository** | nicht geprüft |
| Hatzendorf-Daten | 28.10.2026 | `reports/freeze_protocol_at3.md`, `SUPPORT.md` | von Hand |
| Zehn Tage nach der Abgabe | 18.10. bis 28.10. | gerechnet | von Hand |
| Wagna | 2007–2026, 20 Jahre | `reports/data_review/at_test3_ertraege.md`. Der Dateiname sagt 2008, die Daten beginnen 2007 | von Hand |
| Kalsdorf, Lücken 2017, 2019, 2023, 2025 | 2009–2026 | `DATA_SOURCES.md` | von Hand |
| Test festgeschrieben | Tag `freeze-at-3`, Commit `5c716a9`, 28.10.2026 | `git log freeze-at-3` | von Hand |
| Test III | 0,77 [0,30; 0,97], n = 15 | `results/2026-10-28_at_test3/metrics.json`: 0,768 [0,303; 0,975] | automatisch |
| Kriterium bestanden | – | `metrics.json` | automatisch |
| Zwei neue Punkte („blind“ im Bericht): niedrigste Scores aller 15 | −0,052 und −0,050 | `site_year.csv`. Der Film sagt „neu“ statt „blind“, weil „blinde Punkte“ nach einem Mangel klang | automatisch |
| Scores 2026 entstanden erst nach dem Festschreiben, die Erträge 2026 waren schon bekannt | – | `reports/freeze_protocol_at3.md` §1; Fußzeile im Film „keine Vorhersage“ | von Hand |
| Score: bis zu 100 Maisfelder im Umkreis von 5 km, tiefer Score heißt nicht immer Verlust (Fußzeile) | – | `reports/at_test3_ergebnis.md` §4 | von Hand |
| Ertrag dieser Punkte, im Film „62 % und 48 %“ | 0,62 und 0,48 des Üblichen | `reports/at_test3_ergebnis.md` §2 | von Hand |
| Beim Festschreiben bekannt (nur noch Fußzeile) | 13 von 15 | `reports/at_test3_ergebnis.md` | von Hand |
| Neue Jahre, „ein einziges neues Jahr“ (nur noch Fußzeile) | 1 | `reports/at_test3_ergebnis.md` | von Hand |
| Einfaches Grün (NDVI) | 0,72 | `metrics.json`: 0,721 | automatisch |
| Hagelversicherung | „angefragt“ | Vorgabe im Auftrag: keine Vereinbarung belegt. `ANFRAGEN.md` Nr. 8: Status „offen“ | zu klären |

## Bewusst nicht gesagt

Geprüft gegen die Liste „Nicht sagen“ im Drehbuch und die Vorgaben im Auftrag: keine Vorhersage von Einbrüchen, keine „Trefferquote 77 %“, keine „Trainingsdaten für Österreich“, nicht „das Modell war vor dem Sommer eingefroren“, nicht „besser als NDVI“, nicht „Feldkarte in Österreich bestätigt“. ETH und ZALF: nur „angekommen“, ausdrücklich „für diesen Film nicht ausgewertet“. In den Berichten gibt es keine Auswertung dieser beiden Datensätze.

## Abweichungen vom Drehbuch

- **Sprechtext überarbeitet (2026-11-07, Abend), auf Wunsch des Projektinhabers:** Zeilen c02, c03, c04, d03, f04, f06 verständlicher und positiver. Maßgeblich ist `voice_lines.tsv`. Die harten Einschränkungen zu Oberösterreich und zu „13 von 15“ stehen nicht mehr groß im Bild, sondern in einem kurzen Satz und in den Fußzeilen; im Bericht bleiben sie unverändert.
- **Unabhängige Prüfung der neuen Aussagen (2026-11-07):** drei Prüfer gegen die Berichte. Keine falsche Zahl. Missverständliche Stellen wurden im Bild korrigiert. Im Ton bleiben zwei Stellen, die nur das Bild auffängt, weil das Stimm-Guthaben aufgebraucht ist: „noch nicht“ (Bild: „nicht belegt“) und „die Regel“ (Bild: „Geprüft: der Stress-Score“).
- **Satelliten-Wiederholung gestrichen (2026-11-07):** Der Satz „Aber über jedes Feld in Europa fliegt alle paar Tage derselbe Satellit: Sentinel-2.“ im Kapitel „Die Lösung“ entfällt, weil der neue Anfang das schon sagt und der Film sonst über 5:00 läge.
- **Anfang (2026-11-07) auf Wunsch des Projektinhabers neu:** erklärt Problem, vorhandene Daten und Zielbild, der Titel fällt erst bei 37 s. Die gesprochenen Sätze „Der Mähdrescher misst im Herbst …“ sind entfallen; die echte Mähdrescher- und Satellitenkarte bleibt im Bild, nur gekürzt.
- **Schlusssatz:** „Ein ehrlicher Blick in jedes Feld“ wurde zu „Ein ehrlicher Blick auf das, was es kann“, weil belastbar bisher nur ein Standort ist und die Feldkarte in Österreich nicht bestätigt ist.
- **Ablauf:** nach dem Auftrag umgestellt. Der gesprochene Satz „bis zu 20 Jahre“ ersetzt „aus der Steiermark“ in der Zeitfolge; die Hatzendorf-Daten stehen jetzt korrekt beim 28.10.
- **Selbst vor der Kamera (ca. 8 s):** entfällt im Prototyp, es gibt keine Aufnahme. Der Satz „Ich bin Leon Rohrer“ wird von der KI-Stimme gesprochen.
- **„Der Sommer war der heißeste seit 2018“:** aus Zeitgründen nicht im Sprechtext; der Beleg bleibt in `reports/at_test3_ergebnis.md` §3.
