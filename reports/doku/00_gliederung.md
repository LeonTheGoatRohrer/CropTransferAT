Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# Gliederung der wissenschaftlichen Dokumentation (PLAN.md, Phase 10, Punkt 1)

Stand: 16.10.2026. Grundlage sind nur die Projektdateien (PLAN, DECISIONS, DATA_SOURCES, SUPPORT, CHANGELOG, `reports/`). Jede Zahl in den Kapiteln steht in einer dieser Dateien; wo ich mir nicht sicher war, steht „[Zahl prüfen]“. Zahlen in der Endfassung müssen laut PLAN §6 aus Skripten kommen (Abbildungen per Code).

## Gliederung und Status

| Nr. | Kapitel | Datei | Status |
|---|---|---|---|
| 1 | Motivation und Relevanz (Landwirte, Kammer, Versicherung, AMA, Ministerium), Idee, Forschungsfragen; Abschnitt 1.5 Stand der Forschung und Abgrenzung | `01_motivation.md` | Entwurf vorhanden. Relevanz-Aussagen sind allgemein gehalten, Belege fehlen. **Stand der Forschung (1.5): Platzhalter.** CY-Bench ist belegt; JRC MARS, SCYM und Mähdrescher-Studien: „[Literatur ergänzen: …]“ |
| 2 | Daten und Lizenzen, Pipeline, Definitionen, Leakage-Schutz, Vorab-Festlegungen | `02_daten_pipeline.md` | Entwurf vorhanden. Lizenz der Satelliten-/Wetterprodukte steht nicht in den Quellen (`[Lizenz prüfen]`) |
| 2a | Freeze-Protokoll des Feldmodells | – | **Entfällt vorerst:** Es gab keinen Freeze des Feldmodells (Kriterium „stark genug“ nicht erfüllt). Vorhanden ist nur das Protokoll des EU-Modells (`reports/freeze_protocol_cybench.md`), siehe Kapitel 5 |
| 3 | Was bestimmt den Ertrag? (F0, F1; Phase 1 und 2, inkl. innerhalb der Felder) | `03_was_bestimmt_den_ertrag.md` | Entwurf vorhanden (Ergebnis: Jahre nicht übertragbar, innerhalb des Feldes stark). Bewirtschaftungsanalyse One Acre Fund: **[ergänzen]** |
| 4 | Problemfelder erkennen und „Stark genug?“ (F2; Phase 3 und 4) | `04_problemfelder_und_stark_genug.md` | Entwurf vorhanden (Ergebnis: keine Stufe bestanden, kein Freeze) |
| 5 | Regionalmodell EU → Österreich (F4; Phase 5) bis EU-Freeze | `05_regionalmodell_eu.md` | Entwurf vorhanden; **AT-Zero-Shot-Test ausstehend** (gesperrt bis zur Freigabe des Protokolls) |
| 6 | Fehlerquellen und Grenzen; Ausblick | `06_grenzen_ausblick.md` | Entwurf vorhanden |
| 7 | **Der Beweis in Österreich (F3)** | – | **Platzhalter: erst nach Freeze und Freigabe.** Es gibt keinen Freeze des Feldmodells; ohne neue Entscheidung des Projektinhabers (PLAN Phase 4, „Nicht stark genug?“) kein Test in Österreich. Das Kapitel bleibt leer, bis ein Freeze vorliegt und der Projektinhaber das Protokoll freigegeben hat. Gegenprobe F4 siehe Kapitel 5. Keine österreichische Zahl steht in diesen Entwürfen |
| 8 | Zusatz F5 (Anpassung mit österreichischen Daten) | – | Nicht begonnen; müsste klar getrennt vom Beweis stehen (PLAN Phase 8) |
| 9 | Unterstützung (BWKI-Pflicht) | – | Wird aus `SUPPORT.md` übernommen (KI-Werkzeuge, Datensätze, Bibliotheken). Dort ist „Personen / Institutionen / KI-Advisors“ leer: **[ergänzen]**, falls es Hilfe von Personen gab |
| 10 | Abbildungen | `reports/figures/` | Müssen aus Code stammen; Auswahl und Beschriftung **[ergänzen]** |

Nicht Teil von `reports/doku/`, aber Teil von Phase 10: Video-Pitch (3–5 min), README mit Reproduktionsschritten, Lizenz.

## Offene Prüfpunkte aus dem Quellenabgleich (für den Projektinhaber)

1. **Anzahl US-Feld-Jahre:** PLAN nennt „~170“, `DATA_SOURCES.md` summiert 168 (HLS-Zeit), mit RY-Label sind es 123 Feld-Jahre aus 11 Standort-Jahren. In den Kapiteln durchgehend 168 bzw. 123 verwendet. **[Zahl prüfen]**
2. **Trend KBS:** DECISIONS/Phase 0: +0,087 t/ha pro Jahr (Rohdaten); Phase-1-Bericht: +0,119 t/ha pro Jahr (Trend mit festen Feldeffekten). Beide Zahlen stehen mit Erklärung in Kapitel 3. **[Zahl prüfen]**
3. **Runde 2 (Phase 4):** `reports/phase4_stark_genug.md` nennt ρ = −0,01, `reports/results.md` nennt −0,02. **[Zahl prüfen]**
4. **Datei `phase2_oaf_tabular.md`** wird in `phase3_problem_fields.md` erwähnt, liegt aber nicht in `reports/data_review/`. Die Prüfung der Ursachen-Regeln an den von Landwirt:innen gemeldeten Schäden (One Acre Fund) ist daher in den Entwürfen nicht berichtet. **[ergänzen]**
5. **Reihenfolge „vorab festgelegt“:** DECISIONS enthält nur Datum, keine Uhrzeit. Für die Behauptung „vor jedem Modellergebnis festgelegt“ sollte die Reihenfolge der Git-Commits belegt werden. **[prüfen]**
6. **Offene Entscheidungen des Projektinhabers:** Landsat-5/7-Harmonisierung (Grenze knapp verfehlt), CCM als Körnermais, Testjahre 2021–2023 für den AT-Zero-Shot, Freigabe des EU-Freeze-Protokolls (`NACHTLAUF.md`, `DECISIONS.md`).
