Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 5 Gegenprobe: Regionalmodell EU → Österreich (F4; Phase 5 bis EU-Freeze)

**Kurzantwort:** Das EU-Regionalmodell ist **schwach, aber echt**: ab Mitte Juli besser als die Annahme „normales Jahr“, davor nicht. Es ist eingefroren (Prüfsummen). Der **Zero-Shot-Test in Österreich ist noch nicht gelaufen** und bis zur Freigabe durch den Projektinhaber gesperrt.

## 5.1 Aufbau

Dieses Modell ist von der Feldpipeline unabhängig und prüft dieselbe Grundidee auf **Regionsebene**: Wird etwas, das in anderen Ländern gelernt wurde, ohne Anpassung in einem neuen Land vorhergesagt?

- **Daten:** CY-Bench v1.10 (Kallenberg et al. 2026), nur Mais. Auswertbar sind **16 Länder** (BE, BG, CZ, DE, EL, ES, FR, HR, HU, IT, LT, NL, PL, PT, RO, SK), **8371 Region-Jahre** in 652 Regionen, Zieljahre 2003–2021. **Österreich ist ausgeschlossen** (Länderliste ohne AT, Test `test_austria_is_excluded`). Ausgeschlossen sind außerdem EE, FI, IE, LV (nur Nullerträge); DK und SE liefern wegen zu kurzer Reihen keine Region-Jahre. Deutschland stellt 30,6 % der Region-Jahre; 93,5 % der Region-Jahre sind NUTS-3, 6,5 % NUTS-2 (Bundesländer-Ebene).
- **Zielgröße YAS** (regionale Ertragsanomalie): Ertrag dividiert durch den olympischen Durchschnitt (ohne Höchst- und Tiefstwert) der 5 vorangehenden Jahre derselben Region. Nur Vorjahre, kein Zukunftswissen. YAS = 1 heißt „wie üblich“.
- **Prädiktoren** je Stichtag: Monatsmittel/-min/-max (bei Niederschlag und Wasserbilanz auch Summen) von Temperatur, Niederschlag, Wasserbilanz, Bodenfeuchte, fPAR und NDVI von April bis zum Stichtag; zwei statische Bodenmerkmale. Keine Koordinaten, keine Länder- oder Jahres-Kennung. As-of-Regel mit Verzug für Dekaden- und 8-Tage-Produkte.
- **Modell:** flaches LightGBM (Tiefe ≤ 3), je Stichtag ein Modell, Hyperparameter nur per **Leave-One-Country-Out (LOCO)** innerhalb der Trainingsländer gewählt. Bewertet wird mit äußerem LOCO: Jedes Land wird einmal komplett zurückgehalten, ein echter Länder-Transfer (Adversarial Validation unterscheidet Länder mit AUC 0,98 bis 1,00).
- **Baselines:** YAS = 1 und lineare Trendfortschreibung (letzte 10 Jahre).

## 5.2 Ergebnisse (äußeres LOCO, n = 8371 Region-Jahre, 95-%-KI)

| Stichtag | R² [KI] | ρ [KI] | ρ innerhalb eines Jahres [KI] | Skill vs. YAS = 1 [KI] |
|---|---|---|---|---|
| 1.6. | −0,02 [−0,03; −0,01] | 0,03 [0,01; 0,06] | −0,05 [−0,12; 0,04] | −0,00 [−0,01; 0,00] |
| 15.6. | −0,02 [−0,02; −0,01] | 0,09 [0,07; 0,11] | −0,01 [−0,07; 0,06] | −0,00 [−0,01; 0,01] |
| 1.7. | −0,02 [−0,03; −0,01] | 0,16 [0,14; 0,18] | 0,05 [−0,02; 0,12] | −0,00 [−0,01; 0,01] |
| 15.7. | 0,03 [0,02; 0,04] | 0,33 [0,31; 0,35] | 0,21 [0,15; 0,26] | 0,04 [0,03; 0,06] |
| 1.8. | 0,05 [0,03; 0,07] | 0,36 [0,34; 0,38] | 0,21 [0,13; 0,29] | 0,06 [0,05; 0,08] |
| 15.8. | 0,03 [0,02; 0,05] | 0,37 [0,35; 0,39] | 0,23 [0,15; 0,30] | 0,05 [0,03; 0,06] |
| 1.9. | 0,06 [0,04; 0,07] | 0,38 [0,36; 0,40] | 0,22 [0,12; 0,30] | 0,07 [0,06; 0,09] |

*In einfachen Worten:* R² nahe 0 heißt, das Modell erklärt kaum Streuung; Skill > 0 heißt, es ist etwas besser als „alles normal“. Die Frühwarnkurve zeigt: **Vor dem 15. Juli gibt es keinen Skill.**

**Einordnung (Datenkritik Phase 5):**

- **Großer Teil ist Jahressignal.** Die Jahresmittel der Vorhersage stimmen gut mit den echten (ρ der Jahresmittel 0,86 über 19 Jahre am 1.9.), innerhalb eines Jahres bleibt ρ = 0,22. Die Region-Jahr-KI sind zu eng, weil Regionen im selben Jahr abhängig sind. Maßgeblich ist das Jahres-Cluster-KI (1.9.: ρ [0,30; 0,45], Skill [0,02; 0,13]); an 15.7. und 15.8. schließt es die 0 knapp ein.
- **Gegen die Trendfortschreibung** (selbst schlecht, R² −0,06) ist der Skill 0,11 [0,03; 0,18], aber nicht robust gegen gemeinsame Jahreseffekte.
- **Kontrollen:** Label-Shuffle auf Zufallsniveau (Skill 0,003 / 0,009 / 0,006); ohne Deutschland ρ 0,32 [0,30; 0,35]; Training ohne Deutschland ρ 0,32 [0,30; 0,34]; länderbalanciert R² 0,08 [0,05; 0,11]. Koordinaten als Zusatz verbessern auf R² 0,13 (nur Kontrolle, nicht im Modell).
- **Nach Ländern (1.9.):** gut in SK, HU, CZ, BG, FR, DE; **kein Skill** in ES, IT, PT, EL und LT. Vermutung (nicht geprüft): Das Modell funktioniert dort, wo Niederschlag und Temperatur den Mais begrenzen, nicht wo Bewässerung die Wetterabhängigkeit entkoppelt.
- **Wichtige Merkmale (Gain-Anteile 1.9.):** Maximaltemperatur 0,29, Wasserbilanz 0,22, Niederschlag 0,18, Minimaltemperatur 0,15; Satellitenindizes (fPAR 0,06, NDVI 0,03) wenig. Das Wetter trägt das Signal; das ist keine Kausalaussage.
- **Zu gut?** Nein, eher das Gegenteil: R² ≤ 0,06. Kein Hinweis auf Leakage.

## 5.3 Der EU-Freeze

Am 2026-10-16 wurden 7 Modelle (je Stichtag eines) samt Merkmalslisten und Hyperparametern eingefroren; SHA-256 aller 14 Dateien in `reports/freeze_protocol_cybench.md` (Git-Stand `6c5c693`); die Prüfsummen wurden gegen das Protokoll kontrolliert (alle stimmen). Die Modelldateien liegen nicht im Repository.

## 5.4 Vorab registriertes Österreich-Testprotokoll (Zero-Shot) – **noch nicht ausgeführt**

- **Testdaten:** CY-Bench, Österreich auf Ebene der Bundesländer, Region-Jahre 2006–2020; ausgeschlossen Wien, Salzburg, Tirol, Vorarlberg (weniger als 250 ha Mais, Rundungsartefakte). Erwartet **n = 5 × 15 = 75 Region-Jahre** (Burgenland, Niederösterreich, Kärnten, Steiermark, Oberösterreich).
- **Vorhersage** ohne jede Anpassung (keine Rekalibrierung, kein Nachtrainieren); `predict_zero_shot` prüft vorher alle Prüfsummen.
- **Metriken:** ρ, RMSE (Modell gegen YAS = 1), R², Skill, ρ innerhalb eines Jahres; Bootstrap über Region-Jahre und zusätzlich über Jahre (Cluster).
- **Erfolgskriterien:** *Bestanden* = am 1.9. ρ > 0 mit KI-Untergrenze > 0. *Stark* = zusätzlich RMSE kleiner als die Baseline (KI der Differenz ganz unter 0). Alle Stichtage werden berichtet, nicht nur der beste. Bei n = 75 sind die Intervalle breit; das Ergebnis wird auch bei Nichterreichen mit n und KI berichtet.
- **Einordnung:** Die publizierte CY-Bench-Referenz für Österreich (R² = 0,13, Version v1.8, In-Domain-LOYO) ist ein anderer Aufbau und dient nur zur Einordnung.
- **Offene Entscheidungen des Projektinhabers vor dem Test:** (1) Freigabe des Protokolls, (2) ob die Jahre 2021–2023 aus Statistik Austria ergänzt werden (Vorschlag: Hauptergebnis nur 2006–2020, Ergänzung getrennt). Beides vor dem ersten Lauf schriftlich in `DECISIONS.md`.

**Erwartung (nur Einschätzung, kein Ergebnis):** Wegen n = 75 und dem hohen Jahresanteil hängt das Ergebnis überwiegend an Jahreseffekten. **[Ergebnisabschnitt wird erst nach der Freigabe und dem Test ergänzt: Zahlen einfügen]**

## 5.5 Offene Punkte und Abweichungen (offen berichtet)

- **Hyperparameter-Raster erweitert:** Das erste Raster (min_child_samples 20/100, n_estimators 100/300) wurde nach einem Pilotlauf (Stichtage 1.7., 1.9.) erweitert, weil die Randwerte gewählt wurden. Das Pilotergebnis der äußeren Evaluation war sichtbar; die Änderung ging in Richtung stärkerer Regularisierung und wurde nicht an der Güte der äußeren Länder ausgerichtet. Ein kleiner Optimismus der LOCO-Zahlen ist möglich (`DECISIONS.md`; Datenkritik 3.4).
- **Länder-, kein Jahres-Hold-out:** Die Trainingsländer enthalten dieselben Jahre wie das Testland. Die Zahlen zeigen also „Transfer über Länder bei bekannten EU-Jahren“, nicht „Vorhersage eines neuen Jahres“. Ein Leave-One-Year-Out-Zusatztest ist vorgeschlagen, aber nicht gemacht.
- **Datenqualität:** Nullerträge als „fehlend“ angenommen; Ausreißer in EL (YAS bis 4,57); keine Prüfung der Prädiktoren auf Produktbrüche; Produktlatenzen nicht nachgebildet („Wissensstand nach Datum“, nicht Echtzeit); statische Bodenmerkmale wirken als Länder-Fingerabdruck und verschlechtern das Ergebnis leicht (R² 0,075 ohne gegenüber 0,058 mit), bleiben aber wie registriert im Modell.
