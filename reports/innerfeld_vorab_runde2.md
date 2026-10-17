# Innerhalb-Feld Runde 2 – Aufbereitung und Glättung: Vorab-Festlegungen (vor jedem Lauf)

Stand 2026-10-17. Folgt auf `reports/innerfeld_ergebnis.md` und `reports/innerfeld_obergrenze.md`. Alles hier wird **committet, bevor** die Varianten dieser Runde gerechnet werden. Spätere Änderungen sind verboten (AGENTS §1.3). Die Festlegungen von `reports/innerfeld_vorab.md` (Modelle B0/M1, Merkmale, Seeds, Schemata) bleiben unverändert. Es gibt genau **eine** Rechnung dieser Runde.

Entscheidung des Projektinhabers (Chat 2026-10-17): „Plane das im Vorhinein und führe es dann auch aus.“ Der Projektinhaber hat diese Datei nicht einzeln gelesen; sie bleibt zur Prüfung offen (KI-Entwurf, `SUPPORT.md`).

Gesehen vor diesem Dokument (aus der Obergrenzen-Analyse, explorativ): ρ nach Blockmittelung für B0, B1, M1 auf BARC und Kayad (Mittelwerte über 20–30 m lagen höher). Daraus folgt die **Vermutung**, dass Glättung hilft; sie ist hier der Test, nicht das Ergebnis.

---

## 1. Frage

1. Verbessert eine **Glättung der Vorhersage** (Mittel über Nachbarzellen), gemessen weiter an den **ungeglätteten 10-m-Zellen**, die Rangordnung, und zwar an **beiden** Standorten (BARC und Kayad)?
2. Ändert eine **Aufbereitung der Kayad-Rohpunkte** (Start-/Stopp- und Spurendeffekte) das Bild?

## 2. Varianten (fest, keine Suche)

### 2.1 Glättung der Vorhersage (Standorte BARC und Kayad)

- **S0:** keine Glättung (Stand der Hauptrunde).
- **S1 (Haupt):** Mittelwert der Vorhersage über das 3×3-Fenster der Nachbarzellen (30 m, gleiche Gewichte, Zelle selbst eingeschlossen).
- **S2 (Nebenvariante):** Mittelwert über 5×5 (50 m).
- Gitter: Zellindex `floor(x/10)`, `floor(y/10)` je Feld-Jahr. Fehlende Zellen zählen nicht; Fenster mit weniger als 3 gültigen Zellen behalten den eigenen Wert (fehlt auch der: NaN). Die Glättung wird **nach** der Vorhersage angewendet (Modelle werden nicht neu trainiert).
- **Bewertet wird immer gegen die ungeglätteten 10-m-Zellen** (gleiche Aufgabe wie in der Hauptrunde, keine leichtere).
- Modelle: **B0** (untrainiert, NDVI Dekaden 10–13) und **M1** (Ridge wie festgelegt, Leave-One-Field-Out auf BARC, Leave-One-Year-Out auf Kayad). Kein weiteres Modell.

### 2.2 Aufbereitung der Ertragskarte (nur Kayad, Rohpunkte)

- **P0:** wie bisher (`gt_pixels`).
- **P1:** aus den Rohpunkten werden vor der Zellmittelung entfernt: (a) alle Punkte unter 3,0 t/ha (Start-/Stopp-/Wendeflächen), (b) je Fahrspur die **ersten 8 und letzten 3 Punkte** (etwa 12 m und 4,5 m bei 1,5 m Punktabstand; übliche Förderverzögerung des Mähdreschers). Fahrspur = neue Spur, wenn der nächste Punkt der Reihenfolge über 6 m entfernt ist (wie in `innerfeld_ceiling.py`). Danach Zellmittel, Mindestanzahl 10 Punkte je Zelle, relativer Ertrag je Feld-Jahr neu. Werte der Zahlen 3,0 / 8 / 3 sind **nicht** aus den Daten abgeleitet.
- **Nicht enthalten:** Korrektur von Unterschieden zwischen Fahrspuren, Umgang mit dem 18-t/ha-Deckel (Zellen bleiben, `frac_cap` unverändert).
- BARC: nicht anwendbar (nur interpolierte Raster). Colorado: nicht anwendbar (Einzelpunkte im Abstand von 30 m), bleibt unverändert und wird nicht ausgewertet.

### 2.3 Kombinationen

Alle Kombinationen aus {S0, S1, S2} × {B0, M1} auf **BARC (P0)** und **Kayad (P0 und P1)**. Das sind 6 Zellen auf BARC und 12 auf Kayad. Es wird kein Parameter gewählt; die Zahlen 3×3, 5×5, 3,0 t/ha, 8, 3 stehen oben.

## 3. Kennzahlen

- **Hauptkennzahl:** Median über Feld-Jahre des Spearman-ρ (Vorhersage, relativer Ertrag der 10-m-Zelle), Feld-Jahre mit ≥ 10 Zellen. KI nur bei ≥ 10 Feld-Jahren (BARC), Cluster = Feld, 1 000 Ziehungen, Seed 42.
- **Δ** je Feld-Jahr gepaart: ρ(S1) − ρ(S0), Median der Differenzen; analog S2.
- **Zusätzlich beschreibend:** Lift des untersten Viertels und ρ auf 30-m-Blöcken (Vorhersage und Messung gemittelt), damit sichtbar bleibt, was eine leichtere Aufgabe wäre.
- Kayad hat 3 Feld-Jahre: nur Punktwerte, Vorzeichen je Jahr.

## 4. Gates (endgültig)

- **R2-BARC:** Für **B0 und M1 jeweils** Δρ(S1 − S0) ≥ +0,02 und KI-Untergrenze > 0.
- **R2-Kayad (beschreibend, P0):** Für B0 und M1 jeweils Median Δρ(S1 − S0) ≥ +0,02 und Δρ > 0 in allen 3 Feld-Jahren.
- **Glättung hilft** nur, wenn **beide** Gates erfüllt sind. Sonst gilt die Hauptrunde unverändert (kein Glätten im Produkt).
- Sind beide erfüllt, ist **S1** die Glättung für das Produkt. S2 wird nur berichtet, nicht gewählt, auch wenn es höher liegt.
- **Aufbereitung P1:** kein Gate. Berichtet wird, ob ρ unter P1 steigt, fällt oder gleich bleibt (B0, M1, S0). Ein höheres ρ unter P1 bedeutet nur, dass die Karte sauberer ist, nicht dass das Modell besser ist; es ändert das Produkt nicht.

## 5. Kontrollen

1. **Zufalls-Vorhersage:** eine räumlich unabhängige Zufallsvorhersage (Standard-Normal je Zelle, Seed 42) wird mit S1 geglättet und gegen die 10-m-Zellen gemessen: erwartetes ρ ≈ 0. Bestätigt, dass die Glättung allein keinen Zusammenhang erzeugt.
2. **Positionsmodell K-Raum** (Ridge auf x, y, x², y², xy wie in der Hauptrunde) mit S0/S1: zeigt, ob Glättung generell ρ hebt, weil die Messung räumlich glatt ist. Ein ähnlicher Gewinn wie bei B0 spräche dafür, dass der Effekt nicht vom Satelliten kommt.
3. **Randabstand:** Wiederholung mit Zellen ≥ 20 m vom Rand (BARC, Kayad).
4. **Beide Fenster:** Die Aussage gilt nur, wenn sie für B0 und M1 gleichzeitig zutrifft.

## 6. Vorab festgelegte Gesamtaussagen

- R2-BARC ✓ und R2-Kayad ✓: „Glättung der Vorhersage über 30 m verbessert die Rangordnung an beiden Standorten; sie wird (S1) ins Produkt übernommen. Bestätigung an neuen Standorten steht aus.“
- Nur ein Gate ✓: „Glättung hilft nur an einem Standort; sie wird nicht übernommen.“
- Beide ✗: „Glättung bringt gegen die 10-m-Zellen keinen belastbaren Gewinn; der Gewinn der Blockmittelung beruht auf der leichteren Aufgabe.“
- Kontrolle 2 mit ähnlichem Gewinn wie B0: der Gewinn wird als „Eigenschaft der glatten Ertragskarte“ gekennzeichnet, nicht als Verbesserung des Satellitenverfahrens.

## 7. Nicht Teil dieser Runde

Neue Merkmale, weitere Modelle, Hyperparameter, andere Fenstergrößen, Korrektur der Fahrspur-Offsets, DWFI/SwissYield (noch nicht verfügbar), Österreich.
