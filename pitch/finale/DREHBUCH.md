# Delta Green – Drehbuch Finale-Video (5:00)

**Fassung 1, 2026-11-06.** Zum Lesen und Probesprechen. Annahmen, bis du etwas anderes sagst: deine eigene Stimme, dunkler Delta-Green-Look, Deutsch.

**Roter Faden:** Der Mähdrescher misst im Herbst. Der Satellit hat es im Sommer schon gesehen.

## Grundregeln

1. **Echt bleibt echt:** Alles, was wie ein Messwert aussieht, kommt aus echten Daten und wird im Code animiert. Generiert wird nie eine Karte, Kurve oder Zahl.
2. **KI nur für Stimmung:** Higgsfield-Clips zeigen Drohne, Satellit oder Mähdrescher, sind unten klein als „KI-generiert“ markiert und stehen in `SUPPORT.md`.
3. **Jede Zahl mit Quelle:** Die Spalte „Beleg“ nennt die Datei. Ändert sich dort etwas, ändert sich auch der Text.

---

## 1 · Einstieg (0:00–0:25)

**Bild:** Schwarz, nur Motorgeräusch. Echte Mähdrescher-Punkte eines BARC-Feldes (Public Domain) zeichnen sich in der echten Fahrreihenfolge Spur für Spur und ergeben eine Karte von rot bis grün. Einblendung „Herbst · Mähdrescher“. Ab 0:14 legt sich das echte Satellitenbild desselben Feldes darüber, „Hochsommer · Sentinel-2“. Danach stehen beide Karten nebeneinander, und eine weiße Linie zeigt auf beiden die schwachen Zonen laut Mähdrescher. Ein tiefer Ton, Titel „Delta Green“.

**Sprecher (ab 0:06):**

> Das hier hat ein Mähdrescher im Herbst gemessen.

> Und das hier hat ein Satellit gesehen. Aus 786 Kilometern Höhe, mitten im Sommer.

> Beide wussten nichts voneinander.

**Beleg:** `EastFarm_5_12` 2021, ρ 0,68, 1.338 Zellen, 8.472 Rohpunkte, Ernte 27.09.2021 (`data/raw/barc/2021.zip`). Nach Regel gewählt: ρ am Median, praktisch keine Messlücke (`reports/data_review/within_field_coverage.md`). Umsetzung: `pitch/finale/render/opener.py`.

## 2 · Problem (0:25–0:55)

**Bild:** KI-Clip Drohnenflug über Mais. Dann du vor der Kamera (ca. 8 s). Danach zerfällt das Feld in sein Ertragsspektrum, und alle Farben fallen zu einer einzigen Zahl zusammen.

**Sprecher:**

> Ich bin Leon Rohrer, und das ist Delta Green.

> Kein Feld ist überall gleich. Auf diesem reicht der Ertrag von 40 bis fast 140 Prozent des Mittels. Am Ende bleibt davon oft nur eine Zahl: der Durchschnitt.

> Wo genau Ertrag fehlt, zeigt nur eine Ertragskarte. Die gibt es längst nicht für jedes Feld. Und in Österreich gibt es keine öffentlichen Erträge einzelner Felder.

**Beleg:** Streuung von `EastFarm_5_12` 2021 (relativer Ertrag je Zelle 0,39–1,39). Österreich: `reports/doku/01_motivation.md`, `DATA_SOURCES.md`.

## 3 · Idee (0:55–1:20)

**Bild:** KI-Clip Satellit im Orbit, Kamera kippt auf Europa. Zoom bis auf echte 10-m-Pixel eines Feldes.

**Sprecher:**

> Aber über jedes Feld in Europa fliegt alle paar Tage derselbe Satellit: Sentinel-2. Zehn Meter pro Pixel, frei für alle.

> Meine Frage war einfach: Reicht dieses Bild, um zu sehen, wo im Feld Ertrag fehlt? Ohne Sensor auf der Maschine, ohne Kosten für den Betrieb.

## 4 · Der Beweis (1:20–2:02)

**Bild:** Die 41 Feld-Jahre erscheinen als kleine Karten-Paare, je Ertrag neben Satellit. Jedes bekommt einen grünen Haken, bis die Wand voll ist. Dann große Zahl 0,68 mit Skala von 0 bis 1. Danach das schwächste Viertel eines Feldes rot markiert, zwei Balken 58 % und 27 %.

**Sprecher:**

> Ich habe das an 41 Feld-Jahren aus den USA geprüft, jeweils gegen die Ertragskarte vom Mähdrescher.

> Satellit und Mähdrescher reihen die Stellen im Feld sehr ähnlich. Die Rangkorrelation liegt bei 0,68. Null wäre Zufall, eins wäre perfekt. Und sie ist in allen 41 Fällen positiv.

> Markiere ich das schwächste Viertel der Pixel, liegen 58 Prozent davon wirklich in einer Problemzone. Zufällig wären es 27.

> Belastbar ist das bisher an diesem einen Standort. In Italien und Colorado zeigt es in dieselbe Richtung, dort aber nur mit wenigen Feldern.

**Beleg:** `reports/doku/hauptergebnis.md` §1 (0,68 [0,54; 0,71], 41 Feld-Jahre, 27 Felder), `reports/innerfeld_ergebnis.md`. Hält auch nur auf Zellen nahe echter Messpunkte (0,68, 58 %): `reports/data_review/within_field_coverage.md`.

## 5 · 782 Modelle (2:02–2:32)

**Bild:** Eine Wand aus 782 Kacheln, beschriftet mit Merkmalen wie Wetter, Boden, Radar, Wärmebild. Sie erlöschen in Wellen, bis drei übrig sind. Zwei davon tragen das Schild „kein Training“.

**Sprecher:**

> Natürlich wollte ich wissen, ob KI das besser kann. Also habe ich 782 Modellvarianten trainiert und bewertet, immer auf Feldern, Jahren oder Ländern, die das Modell nie gesehen hatte.

> Das Überraschende: Die einfachen Methoden haben sich durchgesetzt. Auf neuen Standorten war ein trainiertes Modell nicht besser als die einfache Regel. Von den drei Ergebnissen, die übrig blieben, sind zwei gar kein gelerntes Modell.

**Beleg:** `reports/doku/hauptergebnis.md` §5, `reports/innerfeld_ergebnis.md` Punkt 5.

## 6 · Die Regel (2:32–3:02)

**Bild:** Ein Protokoll wird geschrieben, ein Stempel mit echter Prüfsumme rastet ein, Überschrift „Erst den Test festlegen. Dann einmal durchführen.“ Die gescheiterten Versuche laufen als Liste durch: Radar, Wärmebild, Temperatursumme, Begrünungsdatum.

**Sprecher:**

> Bei so vielen Versuchen sieht immer irgendetwas gut aus. Deshalb gilt bei mir eine Regel: erst den Test festlegen, dann ein einziges Mal durchführen.

> Modelle werden mit Prüfsumme eingefroren. Zur Kontrolle vertausche ich die Erträge, dann muss das Modell auf Zufall fallen. Und was gescheitert ist, steht genauso im Bericht: Radar, Wärmebild und drei Runden Jahresvorhersage haben nicht gereicht.

**Beleg:** `reports/doku/hauptergebnis.md` §4, `reports/feinjustierung_ergebnis.md`, `reports/freeze_protocol_*.md`.

## 7 · Österreich (3:02–3:32)

**Bild:** Großes „0“ mit „österreichische Werte im Training“. Karte Oberösterreichs, die fünf Standorte leuchten auf. Zahl 0,50, darunter drei kurze Zeilen: Jahre ja, Standorte im selben Jahr nein, einfaches Grün ähnlich gut.

**Sprecher:**

> Im Training steckt kein einziger österreichischer Wert. Österreich ist nur die Prüfung.

> In Oberösterreich, an 34 Standort-Jahren, erkennt der Stress-Score gute und schlechte Jahre, mit 0,50. Einzelne Standorte im selben Jahr unterscheidet er nicht, und ein einfacher Grünwert schafft fast dasselbe.

> In der Steiermark reichten die Daten gar nicht für einen Test. So stand es, als ich abgegeben habe.

**Beleg:** `reports/at_test_ergebnis.md` (0,50 [0,19; 0,68], n = 34), `reports/at_test_stmk_ergebnis.md` (12 statt 15).

## 8 · Produkt (3:32–3:54)

**Bild:** Bildschirmaufnahme der Website, nur Feld D und seine Karte. Kein eigenes Feld live einzeichnen, das läuft nur als Simulation.

**Sprecher:**

> Daraus ist ein Prototyp entstanden. Dieses US-Feld kannte das Verfahren nicht. Im Juli bleibt die Kurve unter der Referenz, der Alarm schlägt an, geerntet wurde rund ein Viertel unter dem Üblichen. Das Nachbarfeld blieb knapp unter der Schwelle. Eine Warnung zeigt, wo man hinschauen sollte, nicht warum.

**Beleg:** `web/public/data/fields.json` (Feld D, Feld E).

## 9 · Nach der Abgabe – der Höhepunkt (3:54–4:50)

**Bild, Teil A (3:54–4:10):** Schwarz, eine Mail-Zeile tippt sich: „So, 18.10. Abgabe“, dann „Mo, 19.10., 09:44“. Karte Mitteleuropas, Punkte leuchten nacheinander auf: ETH Zürich, ZALF in Brandenburg, Versuchsstation Hatzendorf.

**Bild, Teil B (4:10–4:37):** Das echte Streudiagramm (`at_test3_scatter.png`) baut sich Punkt für Punkt in Grau auf. Rund 2 Sekunden Stille ohne Sprecher. Dann fallen zwei rote Punkte weit links ins Bild. Dazu die NDVI-Kurve 2026, die früh abstürzt. Große Zahl 0,77.

**Bild, Teil C (4:37–4:50):** Dieselbe Zahl wandert klein nach oben, darunter drei gut lesbare Zeilen: „13 von 15 Punkten vorher bekannt“, „ein blindes Jahr“, „einfaches Grün: 0,72“.

**Sprecher:**

> Am Sonntag habe ich abgegeben. Am Montag um 9 Uhr 44 antwortete die ETH Zürich. Dann kam eine Ertragskarte aus Brandenburg mit fast 28.000 Messpunkten, und aus der Steiermark bis zu 20 Jahre Versuchsreihen.

> Damit war der Test möglich, der vorher an den Daten gescheitert war. Festgeschrieben, bevor ich die Satellitenwerte für 2026 berechnet hatte. Der Sommer war dort der heißeste seit 2018.

> Das Ergebnis: in Wagna und Kalsdorf die tiefsten Werte seit 2018. Und die Versuche lagen tatsächlich weit unter dem Üblichen. Über alle 15 Standort-Jahre: 0,77. Kriterium bestanden.

> Das ist ein einziges blindes Jahr. Die meisten Punkte kannte ich schon, und frühes Braunwerden heißt nicht immer Ertragsverlust. Genau dafür kommen jetzt die Daten der Hagelversicherung.

**Beleg:** `reports/at_test3_ergebnis.md`, `reports/data_review/at_test3_ergebnis.md`, `results/2026-10-28_at_test3/`. ETH: Mail Perich, Mo 19.10., 09:44. ZALF: 27.811 Punkte. Hatzendorf: Wagna 2007–2026, Kalsdorf 2009–2026.

**Nicht sagen:** „Das Modell sagt Einbrüche voraus“, „trifft zu 77 Prozent“, „das Modell war vor dem Sommer eingefroren“ oder „Trainingsdaten für Österreich“.

## 10 · Schluss (4:50–5:00)

**Bild:** Die Karte aus dem Einstieg, langsam Rückzug bis zum Feldermuster aus dem Orbit. Logo.

**Sprecher:**

> Ein Satellitenbild, das allen gehört. Und ein ehrlicher Blick in jedes Feld. Das ist Delta Green.

---

## Higgsfield-Clips (Stimmung, noch nicht generiert)

Vor dem Generieren nenne ich die Kosten. Erst Entwürfe in niedriger Auflösung, dann nur die guten Clips final. Alle: 16:9, ohne Text, Logos und Menschen.

| # | Szene | Inhalt |
|---|---|---|
| A | 2 | Niedriger Drohnenflug über Maisfeld im Hochsommer, oststeirisches Hügelland, warmes Abendlicht, ruhige Vorwärtsfahrt |
| B | 2 | Nahaufnahme Maisreihen, Kamera gleitet tief hindurch, Staub im Gegenlicht |
| C | 3 | Erdbeobachtungssatellit mit einem Solarflügel im Orbit über Mitteleuropa, Kamera kippt auf die Erde |
| D | 3 | Sinkflug aus dem Orbit auf ein Feldermuster, Übergang in den Datenzoom |
| E | 1/10 | Mähdrescher bei Dämmerung von oben, Staubfahne, als kurzer Übergang |
| F | 9 | Maisfeld in Sommerhitze, Blätter vergilben vom Rand her, Hitzeflimmern; klar als Stimmungsbild, nicht als Wagna oder Kalsdorf |

## Was vor der Aufnahme geklärt sein muss

| Punkt | Warum | Wer |
|---|---|---|
| **Christoph Hödl fragen:** Dürfen Wagna, Kalsdorf und die relativen Erträge im Video gezeigt werden? | Der Höhepunkt zeigt diese nicht öffentlichen Daten vor Publikum. Ohne Zusage bleiben nur zusammengefasste Werte ohne Ortsnamen. | du |
| Pablo Rosso und Gregor Perich fragen, ob ihre Einrichtung genannt werden darf; Pablo auch nach der Karte | In den Anfragen stand „nicht veröffentlicht“ bzw. „nur zusammengefasste Ergebnisse“. Im Drehbuch nur Ort und Punktzahl, keine Karte. | du |
| Hagelversicherung | Der letzte Satz stimmt nur, wenn die Vereinbarung bei der Aufnahme steht. Sonst: „Die Daten der Hagelversicherung sind angefragt.“ | du |
| Abgabe wirklich Sonntag, 18.10.? Pablos Mail nach der Abgabe? | Der Teil lebt von dieser Reihenfolge. | du |
| Regeln des Finales | Dürfen Ergebnisse nach der Einreichung vorkommen? Format, Sprache, Deadline? | du |
| `SUPPORT.md` | KI-Hilfe bei Drehbuch, Bildern und Schnitt muss drinstehen. | ich |
