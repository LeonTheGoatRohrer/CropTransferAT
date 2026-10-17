# Plan: Innerhalb-Feld-Karte über mehrere Standorte

Stand 2026-10-17. **Entwurf, gilt erst nach Bestätigung durch den Projektinhaber (Schritt I0).** Dieser Plan ersetzt `PLAN.md` nicht. Laut `DECISIONS.md` (2026-10-16, G3, H2) braucht jede weitere Modellrunde eine neue Entscheidung; dieser Plan ist die Vorlage dafür. Österreich wird nicht berührt.

---

## 0. Kurzfassung

1. **Nur ein Baustein, aber gründlich:** Wo innerhalb eines Feldes fehlt Ertrag? Es ist das stärkste Ergebnis (BARC, Median-ρ 0,68, 41 Feld-Jahre), aber es stammt von **einem** Standort mit interpolierten Ertragskarten. Der Plan prüft, ob es woanders hält, und ob Training überhaupt mehr bringt als der rohe NDVI.
2. **Testschema nach Wunsch des Projektinhabers:** zuerst jeder Standort einzeln, danach „auf Standort A trainieren, auf Standort B prüfen“ für alle Paare (Transfer-Matrix) und Leave-One-Site-Out.
3. **Korrektur zur Datenlage:** YIPEEO eignet sich dafür **nicht**, denn es enthält nur Feldmittel, keine Karten innerhalb des Feldes (und die CZ/SK-Erträge sind ohnehin gesperrt). Geeignet sind Quellen mit Mähdrescher- oder Monitor-Punkten (Abschnitt 1).
4. **Ehrliche Erwartung:** Realistisch sind 3 bis 6 Standorte, davon nur BARC groß. Aussagen über „Standort A → Standort B“ sind bei wenigen Feld-Jahren beschreibend, nicht bewiesen. Das steht vorab fest.
5. **Entscheidungsregel vorab:** Training wird nur behalten, wenn es den untrainierten NDVI auf fremden Standorten messbar schlägt. Sonst bleibt der rohe NDVI das Produkt, und das ist ein vollwertiges Ergebnis (sehr einfach, erklärbar, kein Überanpassen).
6. **Umfang:** 6 Etappen (I0–I5), 3 Gates (J1–J3), eine Modellrunde, Bericht auch bei negativem Ergebnis.

---

## 1. Datenlage (aus `reports/data_search.md`, `DATA_SOURCES.md`, `ANFRAGEN.md`)

| Quelle | Kultur | Innerhalb-Feld-Information | Umfang | Status | Rolle |
|---|---|---|---|---|---|
| **BARC, Maryland** | Mais | Kriging-Raster 10 m + Punkte | 41 Feld-Jahre, 27 Felder, 2017–2021 | lokal vorhanden | Referenz, größter Standort |
| **Kayad et al., Italien** (Zenodo 14216165) | Mais | Monitor-Punkte (>20 000/Saison) + Kriging-Raster | 1 Feld, 22 ha, 3 Jahre | öffentlich, nicht geladen | zweiter Maisstandort, aber klein |
| **ETH CH-TAN, Tänikon** (10.3929/ethz-c-000807633) | Winterweizen | Mähdrescher-Shapefile | 2 Parzellen, 1 Jahr | öffentlich, nicht geladen | andere Kultur, sehr klein |
| **Akron, Colorado** (Poss et al.) | Mais (Trockenfeld) | nur ~30-m-Stichprobenpunkte, 10–26 je Teilfläche | 10 Teilflächen-Jahre | lokal vorhanden | schwach, nur ergänzend |
| **DWFI** (Zenodo-Anfrage, Nr. 10) | Mais | Ertragskarten | 3 Felder (MN, IA, NE) 2021–2024 | Anfrage offen | wichtigster Zusatz |
| **SwissYield Witzwil** (Anfrage Nr. 11) | Weizen, Gerste, Triticale | Mähdrescher-Karten | 5 Jahre | Anfrage offen | Kulturvergleich |
| **ZALF patchCROP**, **Booßen** (Nr. 12) | verschieden | Patch- bzw. Rasterertrag | je klein | Anfrage offen | nur wenn Zusage |
| YIPEEO | – | **keine** (Feldmittel) | – | nicht geeignet | entfällt hier |

Konsequenz: Heute stehen **3 Standorte** bereit (BARC, Kayad, CH-TAN; Colorado nur als Stichproben). Ohne Antwort auf Nr. 10/11 bleibt der Test eine Pilotstudie mit sehr wenigen Fremdfeldern. Das wird im Bericht so benannt.

---

## 2. Frage, Ziel, Kennzahlen (Vorschlag)

- **Eine Fragestellung:** Wie gut ordnet ein Satellitenmerkmal die Pixel eines Feldes nach ihrem relativen Ertrag, und gilt das über Standorte?
- **Ziel:** relativer Pixelertrag = Pixelertrag / Mittel desselben Feld-Jahres. **Problemzone:** relativer Ertrag < 0,85 (wie bisher, `targets.at_risk_threshold`).
- **Einheit der Auswertung:** Feld-Jahr (Pixel sind räumlich abhängig). Alle Konfidenzintervalle: Cluster-Bootstrap über Feld-Jahre (1 000 Ziehungen, Seed 42); wo Felder mehrfach vorkommen, über Felder.
- **Hauptkennzahl:** Median-ρ (Spearman, innerhalb Feld-Jahr, dann Median über Feld-Jahre).
- **Zweitkennzahlen:** PR-AUC für Problemzonen, **Lift** des untersten Viertels (Anteil Problemzonen darin ÷ Anteil insgesamt), Recall der Problemzonen.
- **Berichtsregel:** Standorte mit weniger als 10 Feld-Jahren (Kayad, CH-TAN, Colorado) bekommen nur Punktwerte und Vorzeichen, **kein** Bestanden/Nicht-bestanden.

---

## 3. Modelle (Vorschlag, in I0 zu bestätigen)

Alle Merkmale werden **innerhalb des Feld-Jahres standardisiert** (z-Wert), damit Standort- und Jahresniveau nicht mitlernen. Nur Satellit, kein Wetter, keine Standortkoordinaten.

| ID | Modell | Training | Zweck |
|---|---|---|---|
| **B0** | NDVI im festen Fenster 16.7.–15.8. (Zahlenwert = Karte) | keines | Stand von Phase 2.3, Basis |
| **B1** | NDVI im **Spitzenfenster**: ±15 Tage um das Maximum des Feldmittel-NDVI (geglättet) | keines | Fenster ohne Kalender, nötig für andere Kulturen und Klimaräume |
| **B2** | Wiederkehr: relativer Ertrag derselben Pixel im Vorjahr bzw. Mittel anderer Jahre | keines | Obergrenze für „dauerhafte Zonen“ (Boden, Fahrgasse); nur wo ≥ 2 Jahre |
| **M1** | Ridge auf z-NDVI und z-NDRE in 3 Fenstern (Spitze −30 / Spitze / Spitze +30) | ja | die Frage „bringt Training etwas“ |
| **M2** | M1 + Gelände (Höhe, Neigung, TPI) | ja | bisher Satellit 0,70 vs. Gelände 0,29 (Phase 2.3); Kontrolle gegen Geländeeffekt |

Kein Radar, keine Temperatur, kein LightGBM in der Hauptrunde (Radar brachte in der Feinjustierung −0,014; ein Boosting auf wenigen Standorten würde nur überanpassen). LightGBM nur als Sensitivität, nicht zur Auswahl.

---

## 4. Testschema

1. **Einzelstandort (E):** Je Standort trainieren und mit **Leave-One-Field-Out** prüfen (Gruppe = Feld, weil Jahre desselben Feldes zusammenhängen). Gilt nur, wo mehr als ein Feld vorhanden ist (BARC).
2. **Transfer-Matrix (T):** Training auf Standort i, Test auf Standort j, alle Paare mit i ≠ j. Beide Richtungen werden berichtet. Die verlässliche Richtung ist **BARC → andere**; „andere → BARC“ (z. B. Training auf Kayad mit 3 Feld-Jahren) ist ein Stresstest, kein Beleg.
3. **Leave-One-Site-Out (L):** Training auf allen übrigen Standorten, Test auf dem ausgelassenen.
4. **Kulturtransfer (K, nur beschreibend):** Mais → Weizen (CH-TAN) und, falls eingetroffen, SwissYield. Fenster nach B1, nicht nach Kalender.
5. **Österreich:** nicht in diesem Plan. Siehe I5.

---

## 5. Kontrollen und Fallen (vorab)

| Kontrolle | Frage | Erwartung / Regel |
|---|---|---|
| Label-Shuffle (20×) | trägt das Modell Information aus den Labels? | ρ ≈ 0 (|ρ| ≤ 0,10); sonst Leakage-Verdacht |
| Randabstand | Ränder und Vorgewende | Wiederholung nur mit Pixeln ≥ 20 m vom Rand (`interior_min_dist_m`) |
| Wiederkehr B2 | Karte zeigt Boden/Fahrgassen statt Jahresstress? | berichten: Anteil der Leistung von B0, den B2 allein erklärt; ab 2 Jahren |
| Rohkarte vs. Interpolation | Kriging glättet Ertragskarten | Wiederholung nur mit Original-Monitorpunkten (BARC, Kayad), wo vorhanden |
| Fließverzögerung des Mähdreschers | Karten sind räumlich verschoben | prüfen, ob die Ertragspunkte verschoben besser passen (Kreuzkorrelation); nur dokumentieren |
| Wolken und Szenenauswahl | gleiche Datenmenge je Standort | Mindestanzahl gültiger Szenen je Fenster vorab; sonst Feld-Jahr entfällt und wird gelistet |
| Auflösung | Sentinel-2 (10 m) vs. HLS (30 m) | gleiche Quelle an allen Standorten (Sentinel-2); Ertrag auf das Pixelraster mitteln, Mindestpunkte je Pixel vorab |
| Monitor-Kalibrierung | absolute Werte unsicher | unerheblich, weil nur **relativ** gemessen wird |

---

## 6. Gates und Entscheidungsregel (Vorschlag)

- **J1 – Datenlage (Ende I1):** Mindestens 3 Standorte mit geprüftem Innerhalb-Feld-Ertrag **und** BARC-Reproduktion von B0 (Median-ρ 0,676 ± 0,02). Sonst Pause, bis Anfragen beantwortet sind.
- **J2 – Regel überträgt (nach I4):** B0 oder B1 hat an **jedem** Standort mit ≥ 10 Feld-Jahren, außer BARC, Median-ρ ≥ 0,30 mit KI-Untergrenze > 0. Gibt es keinen solchen Fremdstandort, ist J2 „nicht prüfbar“ (nicht „bestanden“).
- **J3 – Training lohnt (nach I4):** M1 minus B0 ≥ +0,03 Median-ρ mit KI-Untergrenze > 0 auf den Fremdstandorten in Transfer- und Leave-One-Site-Out-Test, und Label-Shuffle ≈ 0. Sonst: Produkt bleibt B0/B1 ohne Training. M2 wird nur als Kontrolle berichtet, nicht gewählt.
- Alle Schwellen sind **nicht** nachträglich änderbar (AGENTS.md §1.3). Ein gutes Ergebnis auf einem Fremdstandort ist zuerst ein Verdachtsfall (§1.2).

Ausgang jeder Kombination ist verwertbar: J2 ✓ + J3 ✗ → „einfacher NDVI genügt und gilt an mehreren Orten“; J2 ✗ → „Karte ist standortabhängig“, ehrliche Grenze für Österreich; beides ✓ → Baustein für ein größeres Modell.

---

## 7. Arbeitsplan

Aufwand: S unter ½ Tag, M 1 Tag, L 2–3 Tage. Branch `phase-if-innerfeld`, Tag `v0.N.0` nach Abschluss, Push nach jedem großen Schritt (AGENTS.md §2). Datenkritik nach jedem Datensatz (§3), `SUPPORT.md` und `DECISIONS.md` fortlaufend.

| ID | Schritt | Wer | Aufwand | Ergebnis |
|---|---|---|---|---|
| **I0** | Plan bestätigen: Modellliste (Abschn. 3), Kennzahlen (2), Gates (6); Anfragen Nr. 10 (DWFI) und 11 (SwissYield) tatsächlich absenden | Projektinhaber | S | `DECISIONS.md`-Eintrag |
| I1.1 | Kayad (Zenodo 14216165) und CH-TAN (ETH) laden, Lizenz und Einheiten prüfen | Claude | S | `data/raw/`, Datenkritik `reports/data_review/if_*.md` |
| I1.2 | Gemeinsames Schema `gt_pixels` (Standort, Feld, Jahr, x, y, Ertrag, relativer Ertrag, Kultur, Quelle) für alle Standorte, BARC übernommen | Claude | M | Parquet + Tests |
| I1.3 | **Gate J1** | Claude / Projektinhaber | S | Bericht |
| I2.1 | Sentinel-2-Extraktion (GEE) für Kayad, CH-TAN, Colorado nach BARC-Muster; Konto und Quota liegen beim Projektinhaber | Claude (Projektinhaber startet) | M | `data/interim/pixels/` |
| I2.2 | Merkmale: z-Standardisierung, Spitzenfenster (B1), Fensterzahl, Mindestszenen; Tests | Claude | M | `features_innerfeld.parquet` |
| I2.3 | Datenkritik Merkmale (Abdeckung, Wolken, Randpixel, Verteilungen je Standort) | Claude | S | `reports/data_review/if_merkmale.md` |
| **I3** | **Vorab-Festlegungen committen** (`reports/innerfeld_vorab.md`: Modelle, Fenster, Seeds, Schwellen, Mindestanzahlen) – vor jedem Lauf | Claude, Projektinhaber liest | S | Commit-Hash |
| I4.1 | Einzelstandort-Läufe (E) und B0/B1/B2 | Claude | M | `results/<datum>_innerfeld_E/` |
| I4.2 | Transfer-Matrix (T) und Leave-One-Site-Out (L), M1/M2 | Claude | M | `results/<datum>_innerfeld_T/` |
| I4.3 | Kontrollen (Abschn. 5), Kulturtransfer K | Claude | M | `controls.json` |
| I4.4 | **Gates J2, J3** | Claude | S | Entscheidung nach Vorab-Regel |
| I5.1 | Bericht `reports/innerfeld_ergebnis.md`, Datenkritik der Ergebnisse, Abbildungen (Transfer-Matrix, Beispielkarten mit Fehlern), Website-Eintrag | Claude | M | Bericht |
| I5.2 | Entscheidung des Projektinhabers: M1 als Baustein ins große Modell oder bei B0/B1 bleiben | Projektinhaber | S | `DECISIONS.md` |
| I5.3 | Österreich: nur über **Landwirt:innen-Ertragskarten** (Anfrage V3 in `ANFRAGEN.md` §5). Testprotokoll und Freeze davor, Zugriff erst nach Freigabe | Projektinhaber, danach Claude | – | nicht Teil dieses Plans |

Zeitrahmen grob: I1–I3 etwa 3 Tage Arbeit, I4–I5 etwa 3 Tage, abhängig von Antwortzeiten der Datenanfragen (die nicht beschleunigt werden können).

---

## 8. Was dieser Plan nicht leistet (ehrlich)

- Er sagt **nicht** den Ertrag des Feldes voraus, sondern wo im Feld es schlechter steht.
- Er beweist **nicht**, dass die Karte in Österreich gilt. Dafür bräuchte es Ertragskarten aus der Steiermark.
- Bei 3 Standorten und wenigen Fremdfeldern kann ein „gilt überall“ nicht belegt werden; höchstens ein „gilt an den geprüften Orten“ oder ein „gilt dort nicht“.
- Wiederkehrende Zonen können Boden, Fahrgassen oder Ränder sein; B2 und die Randkontrolle trennen das nur teilweise.
