Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 6 Fehlerquellen, Grenzen und Ausblick

Dieses Kapitel sammelt, was die Ergebnisse einschränkt. Alle Punkte stammen aus den Datenkritik-Berichten (`reports/data_review/`) und `DECISIONS.md`.

## 6.1 Grenzen der Daten

1. **Sehr wenige Standort-Jahre.** Die Feld-Ertragsdaten ergeben 123 Feld-Jahre mit RY, aber nur 11 Standort-Jahre (Sentinel-2-Basis: 8). Felder im selben Jahr teilen Wetter und Bewirtschaftung und sind keine unabhängigen Fälle. Das ist die Hauptursache dafür, dass sich der Jahreseffekt nicht lernen lässt (Kapitel 3 und 4). Alle KI sind entsprechend breit. KBS-Ergebnisse stützen sich teils auf nur 2 Jahre.
2. **Landsat-Harmonisierung nicht bestanden.** Die KBS-Jahre vor 2013 (Landsat 5/7) durften für Satellitenmerkmale nicht verwendet werden (NDVI-RMSD 0,073 gegenüber der vorab festgelegten Grenze 0,07; EVI-RMSD 0,080). Die Diagnostik legt nahe, dass die Streuung eher von kleinen Parzellen und Mischpixeln als von der Kalibrierung kommt (gleiche-Tag-Paare: RMSD 0,074). Ob eine andere Prüfung zulässig ist, entscheidet der Projektinhaber; die Grenze wurde nicht nachträglich gelockert.
3. **Bio-Parzellen bei KBS.** Mehr als die Hälfte der „gefährdeten“ KBS-Feld-Jahre (13 von 23) sind Bio-Parzellen. „Gefährdet“ misst dort zum Teil die Bio-Bewirtschaftung und nicht Wetterstress. Das schwächt die Übertragung auf konventionelle Felder.
4. **US ≠ Österreich.** Klima, Sorten, Anbaukalender und Feldgrößen unterscheiden sich. Die US-Längsschnittdaten stammen von nur drei Standorten (Michigan, Maryland, Colorado), wobei KBS und BARC an den Merkmalen vollständig trennbar sind (Adversarial AUC 1,0). Ob der Zusammenhang Kurve → Ertrag in Österreich gilt, ist Frage F3 und **bisher nicht getestet**. Gegenmaßnahmen im Plan: relativer Ertrag RY, nur übertragbare Merkmale, Wärmesummen-Achse (noch nicht umgesetzt: Phase 3 rechnet auf Kalender-Dekaden, `DECISIONS.md` 2026-10-16).
5. **Grobe Wetter- und Bodendaten.** ERA5-Land hat 0,1° (rund 9 km) Auflösung: Alle 24 KBS-Parzellen teilen einen Wetterpunkt, Wetter erklärt dort nur Jahresunterschiede. SoilGrids (250 m) und TWI (90 m) beschreiben keine Zonen innerhalb eines Feldes; das 30-m-Geländemodell ist ein Oberflächenmodell. „Gelände erklärt wenig“ heißt nicht „Gelände wirkt nicht“.
6. **Ertragsdaten selbst.** Ertragsmonitore sind nicht auf Wiegewagen kalibriert (KBS: 0,87 bis 1,01-fach, einzelne Parzellen 0,67 bis 1,6); BARC-Karten sind gekriged, mit versetzten Jahresgittern (bis 7,5 m) und unbekanntem Lagefehler; Einheitenfehler und wechselnde Feuchtebasis (14 %, 15 %, 15,5 %); Colorado sind nur Stichprobenpunkte. Die Sentinel-2-Indizes mit Band B8A bzw. B5 (NDVI, NDRE) sind effektiv ~20 m grob.
7. **Wolken.** Die Zahl klarer Beobachtungen schwankt stark von Jahr zu Jahr (KBS 2014 und 2017 ohne HLS-Sommertermine). Das wird durch die Datenqualitätsregel behandelt, kann aber Ergebnisse einzelner Jahre trotzdem beeinflussen.
8. **One Acre Fund und YieldSAT:** One Acre Fund hat keine Feldgrößen, Koordinaten auf 0,001° gerundet und keine Feuchtebasis; die Daten sind nur als Tabelle nutzbar, nicht im Hauptmodell (Entscheidung des Projektinhabers). YieldSAT-Zugang liegt nicht vor. Ein Training mit vielen Feldern in Afrika und Südamerika (die Idee der Querschnittsdaten) ist daher nicht umgesetzt.

## 6.2 Grenzen der Aussagen

- **Vegetationszustand ≠ Ertrag.** Der Satellit sieht Blattfläche und Chlorophyll, nicht das Korn.
- **Korrelation ≠ Kausalität.** SHAP, Ablation und die Ursachen-Regeln zeigen, was das Modell nutzt bzw. was plausibel passt. Sorte, Saattermin, Düngung, Verdichtung, Bewässerung und Bodenart sind unbekannt und können Effekte erklären, die dem Boden oder Wetter zugeschrieben werden. „Wiederkehrende“ Problemzonen können Boden, aber auch Fahrgassen oder Randeffekte sein.
- **Keine Krankheits- oder Schädlingsdiagnose.** Dafür gibt es keine passenden Labels; die Ursachen-Regeln kennen nur Trockenstress, Hitze, Nässe und abrupten Schaden, sonst „Ursache unklar“.
- **Die Modelle sind nicht „stark genug“** (Kapitel 4); es gibt kein einsatzreifes Frühwarnsystem. Die Unsicherheitsintervalle sind formal kalibriert, aber praktisch zu breit.
- **EU-Regionalmodell:** schwach, vor dem 15.7. ohne Skill, Länder- statt Jahres-Hold-out, Hyperparameter-Raster nach Pilotlauf erweitert (offen berichtet, Kapitel 5).
- **Österreich-Test:** Bundesland-Ebene bedeutet wenige Region-Jahre (n = 75 geplant); INVEKOS-Felder unter 1 ha (rund 63 % der steirischen Körnermais-Schläge) fallen durch den Filter; CCM wird vom Filter (Code 105) nicht mitgezählt, die Statistik Austria zählt es zum Körnermais; die Entscheidung steht aus.
- **Versuchsparzellen ≠ Praxisfelder:** Deshalb sollen nur Jahresanomalien je Standort verglichen werden, nicht absolute Erträge.

## 6.3 Ausblick

1. **Mehr Standort-Jahre sind der wichtigste Hebel.** Mead (AmeriFlux, viele Mais-Jahre je Feld; Konto und Prüfung der Erträge ausstehend) und YieldSAT (303 Maisfelder, Zugang beantragt) sind die nächsten Schritte.
2. **Landsat-Entscheidung:** Neue Prüfung oder Verzicht auf die KBS-Jahre vor 2013 (Entscheidung des Projektinhabers). Davon hängt ab, ob die KBS-Reihe mit Satellit verdreifacht werden kann.
3. **Österreichische Felddaten (V3):** Erträge pro Feld von Landwirt:innen, Landwirtschaftskammer oder Maschinenring ab 2018 (schon 20 bis 50 Feld-Jahre wären wertvoll; nur mit Zustimmung, anonymisiert). Sie dürfen erst nach dem Freeze angesehen werden.
4. **Weitere Daten:** europäische Mähdrescher-Ertragsdaten aus Studien (Autor:innen anfragen), Kalibrierung auf absolute t/ha, österreichische Versuchs- und Bodendaten (Bodenklimazahl, Koordinaten der Hatzendorfer Standorte).
5. **Methodische Lücken schließen:** räumlicher Block-Split, Wärmesummen-Achse statt Kalender-Dekaden, Leave-One-Year-Out für das EU-Modell, Boden im Pixelmodell, 10-m-Auflösung der Red-Edge-Bänder prüfen.
6. **Erst nach dem Beweis (getrennt als Zusatz F5):** Anpassung mit österreichischen Daten (Few-Shot, selbstüberwachtes Feldmodell, Sentinel-1-Radar, SPARTACUS 1 km statt ERA5-Land).
7. **Kooperationen** (Landwirtschaftskammer, Hatzendorf, KBS-Erlaubnis zur Veröffentlichung abgeleiteter Ergebnisse): **[konkrete Zusagen ergänzen]**.
8. **Diagnose von Krankheiten/Schädlingen** bräuchte eigene Labels und liegt außerhalb dieses Projekts.
