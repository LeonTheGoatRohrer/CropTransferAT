# Datenkritik I2 – Satellitenmerkmale für die Innerhalb-Feld-Studie

Stand 2026-10-17. Plan: `reports/plan_innerfeld.md` (I2). Code: `src/croptransfer/innerfeld_extract.py`, `src/croptransfer/innerfeld_features.py`, Tests `tests/test_innerfeld_features.py`. Ergebnisse: `data/interim/pixels_dekad/` (54 Feld-Jahre), `data/processed/features_innerfeld.parquet`, `features_innerfeld_fy.csv`.

**Es wurden in I2 keine Ertragswerte mit Merkmalen verglichen** (kein ρ, keine Modelle). Die Auswahl der Parameter (Suchbereich des Maximums, Fensterbreite) ist damit unabhängig vom Ergebnis; endgültig festgelegt wird sie in I3 (`reports/innerfeld_vorab.md`), vor dem ersten Lauf.

## Was gebaut wurde

- **Dekaden-Komposite** (Sentinel-2 L2A, Cloud Score+ cs_cdf ≥ 0,60, wie in Phase 2.3): je Zelle und 10-Tage-Abschnitt von 1.4. bis 27.10. (21 Dekaden) Median von NDVI und NDRE sowie Anzahl klarer Beobachtungen; dazu Gelände (Höhe, Neigung, TPI aus Copernicus DEM, 150 m).
- **Warum Dekaden statt fester Fenster:** Das Spitzenfenster (B1) und das Dreifenster-Modell (M1) hängen vom Maximum der Feld-NDVI-Kurve ab. Die festen Fenster aus Phase 2.3 (16.7.–15.8.) bleiben für B0 unverändert aus dem alten Zwischenspeicher.
- **Abweichung vom Plan (offengelegt):** Der Plan nannte die Extraktion nur für neue Standorte. Für B1/M1 und die Transfer-Matrix musste **auch BARC** (41 Feld-Jahre, 23 912 Zellen) mit Dekaden extrahiert werden, damit alle Standorte dieselben Merkmale haben.
- **Merkmale** (nur Satellit, je Feld-Jahr z-standardisiert): `b1_ndvi` (Median über Maximum ±1 Dekade), `m1_ndvi_w1..3` und `m1_ndre_w1..3` (Maximum −4…−2, −1…+1, +2…+4 Dekaden), Gelände.
- **Maximum:** Spitze der über 3 Dekaden geglätteten Feld-NDVI-Kurve in den Dekaden 6–17 (31.5.–18.9.); eine Dekade zählt nur, wenn ≥ 50 % der Zellen gültig sind.

## Prüfungen (AGENTS §3)

| Prüfung | Befund | Konsequenz |
|---|---|---|
| **Fehler gefunden und behoben** | Die erste Extraktion lieferte nur Geländebänder, weil `normalizedDifference` den Zeitstempel verliert und der Dekaden-Filter danach alles entfernte. Aufgefallen beim Lesen der Spalten, vor jeder Auswertung | Zeitstempel wird kopiert; alle 54 Feld-Jahre komplett neu extrahiert |
| **Räumliche Ausrichtung** | Eigene Dekade um den 4.8. gegen das von den Autoren mitgelieferte Sentinel-2-Bild vom 4.8. (Kayad, 3 Jahre): Spearman-ρ der NDVI-Werte je Zelle **0,91–0,97** (B4/B8A-Reihenfolge) | Kein Versatz; Abruf und Zellraster stimmen |
| Vollständigkeit | Alle 54 Feld-Jahre extrahiert, Zellenzahl je Feld-Jahr gleich der Eingangstabelle (Assertion). Alle 54 haben ein gültiges Maximum und ≥ 80 % Zellen im B1-Fenster | Kein Feld-Jahr fällt aus |
| Klare Beobachtungen | Im Hochsommer meist **1–3 klare Aufnahmen je Dekade** (Median); Anteil leerer Zellen je Dekade bei BARC 0–38 %, Kayad 0–36 % (dann fehlt meist die ganze Szene, weil sie wolkig war), Colorado 0–28 % | Dekadenwerte sind wenig robust, deshalb Median über je 3 Dekaden (B1, M1). Lücken werden nicht aufgefüllt |
| **Kayad 2016 (L2A-Lücke)** | Nur 13 L2A-Szenen gegenüber 77 L1C (die Europa-Aufbereitung beginnt 2017); nur **9 gültige Dekaden**, Maximum bei Dekade 7 (10.6.) gegenüber 8–9 in 2017/2018 | Maximum 2016 unsicher. In I3 festlegen: Kayad mit und ohne 2016 berichten. L1C wurde nicht beigemischt (anderer Offset) |
| Lage des Maximums | BARC Dekade 9–14 (Median 12 = 30.7.), Colorado 12–13, Kayad 7–9 (Mitte Juni bis Anfang Juli) | Plausibel (Aussaat im April in der Po-Ebene). Kein Feld liegt am Rand des Suchbereichs (6 oder 17) |
| **NDVI-Sättigung** | Kayad-Maximum 0,90–0,95, BARC 0,74–0,90 (Median 0,84), Colorado 0,33–0,78 | Bei Kayad liegt NDVI nahe der Sättigung, das Signal zwischen Zellen ist klein. NDRE (M1) hilft dort eher. Als Grenze für die Deutung notieren |
| Colorado-Ausfälle | Maximum-NDVI der vier Ausfälle (Mittel ≤ 1,04 t/ha) 0,33–0,48, der übrigen sechs 0,46–0,78 (die drei mit 2,5–3,7 t/ha liegen bei 0,46–0,51) | Das Niveau ist für den Innerhalb-Feld-Vergleich unerheblich (z-Wert); die Ausfälle werden in I3 getrennt behandelt |
| Gelände | BARC 25–61 m, Neigung bis 25°, TPI −13…+6; Kayad Neigung ≤ 0,6°, TPI ±0,4 m; Colorado Neigung ≤ 2° | Kayad und Colorado sind praktisch eben: M2 (Gelände) kann dort kaum etwas leisten. Erwartung: M2 nur auf BARC aussagekräftig |
| Zellraster | Kayad-Zellen liegen auf dem Sentinel-2-Raster (Mittelpunkte auf 5 m, Vielfache von 10 m). BARC-Blöcke sind um 2,5 m versetzt: der Mittelpunkt trifft einen Pixel, der Block überlappt zwei | Kleine Unschärfe nur bei BARC wie in Phase 2.3; nicht ändern, sonst bricht die Vergleichbarkeit |
| Veraltetes Asset | `COPERNICUS/DEM/GLO30` ist als veraltet markiert (Nachfolger `…/GLO30_2024_1`) | Bewusst unverändert (Vergleichbarkeit mit Phase 2.3); betrifft nur Gelände (M2-Kontrolle) |
| Leakage | z-Standardisierung nutzt nur die Zellen des eigenen Feld-Jahres; Test: zwei Feld-Jahre mit verschobenem NDVI-Niveau ergeben identische z-Werte. Es wurden keine Ertragswerte verwendet | ✅ |

## Entscheidung

⚠️ **Weiter mit Einschränkung (I3 starten).** Einschränkungen: Kayad 2016 (nur 9 gültige Dekaden), wenige klare Aufnahmen je Dekade, NDVI-Sättigung bei Kayad, Gelände auf Kayad und Colorado ohne Aussagekraft. In den Vorab-Festlegungen (I3) zu entscheiden: Suchbereich des Maximums, ob Kayad 2016 in der Hauptauswertung bleibt, Mindestanzahl klarer Aufnahmen und die Behandlung der Totalausfälle in Colorado.
