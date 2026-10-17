# Datenkritik – Österreich-Test (erster Test, explorativ)

Stand 2026-10-17. Protokoll §5 (`reports/freeze_protocol_at.md`). Zahlen: `results/2026-10-17_at_test/qc.json`, `review.json`, `site_year.csv`. **Entscheidung: ⚠️ weiter mit Einschränkung** (die Ergebnisse dürfen berichtet werden, mit den Grenzen unten).

## 3.1 Repräsentativität / Auswahl
- **Steiermark fehlt im lokalen Test.** Die steirischen Standorte haben in den Berichten nur Düngungs-, Bodenbearbeitungs- und Begrünungsversuche; der registrierte Filter (`sorten`, `praxisversuch_sorten`) hat sie ausgeschlossen. V2 ist damit Oberösterreich (5 Standorte, 34 Standort-Jahre). Ich hatte in der Planungsphase ca. 15 steirische Standort-Jahre erwartet – das war ein Irrtum bei der Zählung der Standort-Jahre ohne Prüfung der Versuchsart. Konsequenz: keine Aussage für die Steiermark.
- **2019 fehlt** (keine oberösterreichischen Sortenversuche in den digitalisierten Berichten), 7 statt 8 Jahre als Cluster; 2022 hat nur 4 Standorte.
- **Fast alle Felder gültig:** 99,99 % der 10 160 Feld-Jahre haben ≥ 4 beobachtete HLS-Dekaden; in jedem der 104 Standort-Jahre waren ≥ 96 von 100 Feldern gültig, kein Standort-Jahr musste ausgeschlossen werden. Bewölkung verzerrt die Abdeckung damit kaum (mediane Zahl beobachteter Dekaden 16–20 je Jahr; am niedrigsten 2021 und 2022 mit 16, am höchsten 2018 mit 20, einem trockenen Jahr).

## 3.2 Sind die Daten korrekt?
- **Maisähnlichkeit:** Nur 0,01 % der Felder haben einen NDVI-Höchstwert unter 0,6; mediane Höchstwerte 0,86–0,90. INVEKOS-Körnermais (Code 105) sieht in den Kurven also wie Mais aus.
- **Frühe Reife / Ernte:** Der Anteil der Felder mit abruptem Abfall in Juli/August ist in 2018 (43 %), 2024 (49 %) und 2022 (18 %) hoch, sonst unter 5 %. Das sind heiße, trockene bzw. frühe Jahre. Der Stress-Score kann dort Abreife statt Stress messen (offen, siehe Ergebnisbericht).
- **Ties:** In manchen Jahren liegt ein großer Teil der Felder genau auf der Referenz (Score ≈ 0; 2020: 59 %, 2021: 38 %, 2022: 42 %, 2018: 5 %). Der Mittelwert über 100 Felder ist trotzdem stetig; die Auflösung ist aber gering.
- **Streuung:** Standardabweichung des Scores innerhalb eines Standort-Jahrs (0,017) ≈ Streuung der Standort-Jahr-Mittel (0,019): Unterschiede zwischen Feldern sind so groß wie zwischen Standort-Jahren. Das Mittel über 100 Felder dämpft das.
- **Standortposition:** nur Gemeindemitte; Katzenberg → Kirchdorf am Inn/Geinberg ist aus dem Namen abgeleitet. Unsicherheit bleibt.
- **Zielgröße:** `YAS_site` hat bei 28 von 34 Standort-Jahren die Basis „Mittel aller anderen Jahre“ (`baseline_short`), nur 6 haben fünf Vorjahre. Damit steckt ein Trend und zukünftige Jahre in der Basis; Versuchsmittel sind Sortenmittel verschiedener Sortensätze.
- **Statistik Austria:** Quotient aus Erträgen mit 14 % Feuchte, unverändert.

## 3.3 Scheinzusammenhänge
- **Jahres-Proxy:** Ja, großenteils. Jahresmittel ρ = 0,79; nach Abzug der Jahresmittel ρ = 0,31; innerhalb eines Jahres Median −0,10. Der Score unterscheidet Jahre, nicht Standorte im selben Jahr.
- **Gegenprobe NDVI:** B-NDVI (ohne Lernen) erreicht dasselbe ρ (0,50). Score und NDVI hängen stark zusammen (0,83 / 0,88). Der Score bringt hier keinen Zusatz.
- **Ohne die beiden belasteten Jahre:** Ohne 2018 und 2023 zusammen sinkt ρ (V2-A) auf 0,37, ohne zwei beliebige Jahre liegt es bei 0,35–0,60; bei V1 ohne 2018 und 2023 bei 0,35. Das Regionalmodell liegt im Mittel um +0,09 zu hoch (Vorhersage 1,08, Beobachtung 1,00).
- **Leave-one-year-out:** 0,41–0,55 – kein einzelnes Jahr trägt das Ergebnis (2018 mit dem extremsten Score eingeschlossen).
- Kein Modell wurde auf Österreich gefittet; Label-Shuffle entfällt für A. Für das Nachtrainieren gilt Leave-one-year-out.
- **Mehrfachvergleiche:** Zwei gleichrangige Haupttests (A und B) und vier Stichtage; keiner wurde als Sieger gewählt. Die Aussage stützt sich auf den vorab festgelegten Haupt-Stichtag 1.9.

## 3.4 Leakage
- Österreich-Regel eingehalten: Freeze vor der Auswertung (`freeze-at-1`), danach kein Modell, keine Schwelle und kein Kriterium geändert. Der Auswertungscode wurde nach dem Tag um (a) Datenkritik-Kennzahlen und (b) die Option einer Jahresspanne für die Regionalmerkmale ergänzt – beides ändert die Testmetriken nicht (Test `tests/test_at_test.py`).
- **Programmfehler im ersten Lauf:** Der erste Aufruf brach in der Datenkritik-Funktion ab (doppelte Spalte `year`), bevor eine Ertragsdatei geöffnet wurde; Behebung ohne Einsicht in Ergebnisse. Der Test lief danach einmal vollständig. (Eine zweite Sitzung desselben Projekts hat danach nur eine beschreibende Zerlegung auf dem fertigen Ergebnis erzeugt: `src/croptransfer/at_review.py`, `review.json`.)
- Zwei der 104 Satelliten-Abfragen scheiterten am Anfrage-Limit von Google Earth Engine und wurden unverändert wiederholt.
- Die Notizspalte von `at_trials.csv` wurde versehentlich vor dem Freeze teilweise angesehen (siehe Protokoll §6); keine Auswirkung auf Festlegungen.
- **Nachtrainieren:** Leave-one-year-out verwendet auch spätere Jahre als Training; die Ziele (Statistik Austria) sind dieselben wie im V1-Test, es ist daher kein unabhängiger Test.

## 3.5 Ergebnis-Plausibilität
- Ergebnisse sind **nicht zu gut**: ρ ≈ 0,5 mit breiten Intervallen, V1 RMSE schlechter als „normales Jahr“.
- 3 beste / schlechteste Fälle: nicht ausgewertet (Zeit); die Jahresmittel-Tabelle in `review.json` zeigt 2018 mit dem niedrigsten Score bei durchschnittlichem Ertrag (1,04) und 2022/2025 mit höchsten Erträgen (1,19 / 1,15) bei fast neutralem Score; 2023 (niedrigster Ertrag 0,95) hat den zweitniedrigsten Score.
- Wenige Cluster: 7 Jahre (V2), 6 Jahre (V1), 9 Jahre (Nachtrainieren) – Konfidenzintervalle sind entsprechend breit, ein Verfehlen hieße „nicht belegt“.

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Berichten dürfen: „In Oberösterreich lässt sich die Rangfolge der Jahre erkennen; der Score ist nicht besser als NDVI; Standorte im selben Jahr werden nicht unterschieden; die Steiermark ist nicht getestet.“
