# Phase 4 – „Stark genug?“

Automatisch erzeugt mit `python -m croptransfer.phase4_report` aus den Kriterien-Dateien der Läufe. Kriterium und Auswahlregel: PLAN.md Phase 4, Konkretisierung DECISIONS.md (2026-10-15/16). Alle Werte LOFYO, Stichtag 1.9., 95-%-KI per Cluster-Bootstrap über Datensatz-Jahre.

| Stufe | gewähltes Modell | ρ 1.9. [KI] (n) | 1 schlägt B0/B1 ab 1.8. | 2 ρ ≥ 0,4 | 3 LODO KBS→BARC / BARC→KBS | 4 Label-Shuffle | stark genug |
|---|---|---|---|---|---|---|---|
| Phase 2 | M-S ridge S2 | -0,04 [-0,29; 0,37] (89) | ✗ | ✗ | 0,42 / -0,19 ✗ | -0,00 ✓ | **nein** |
| Runde 1 | M-Srel ridge S2 | 0,37 [-0,01; 0,70] (89) | ✗ | ✗ | 0,47 / 0,40 ✓ | 0,03 ✓ | **nein** |
| Runde 2 | M-Srel-einfach ridge S2 | -0,01 [-0,21; 0,59] (89) | ✗ | ✗ | -0,21 / 0,18 ✗ | 0,13 ✓ | **nein** |
| Runde 3 | M-alle-rel ridge S2 | 0,37 [-0,02; 0,68] (89) | ✗ | ✗ | 0,77 / 0,53 ✓ | -0,00 ✓ | **nein** |

## Entscheidung

**Keine Stufe erfüllt das Kriterium.** Nach PLAN Phase 4 („Nicht stark genug? Nicht nach Österreich gehen“) wird **nicht eingefroren** und **kein Österreich-Test** vorbereitet. Weitere Runden sind nach der Vorab-Festlegung (höchstens 3) nicht erlaubt; jede weitere Änderung braucht eine neue Entscheidung des Projektinhabers.

Woran es scheitert: Kriterium 1 (RMSE besser als RY = 1) und Kriterium 2 (ρ ≥ 0,4). Die Rangfolge der Feld-Jahre wird mit relativen Merkmalen besser (ρ ≈ 0,37, beide LODO-Richtungen > 0), aber die Höhe der Abweichung vom Normaljahr trifft das Modell nicht genauer als „normales Jahr“. Ursache ist vor allem die kleine Zahl unabhängiger Standort-Jahre (8 in der S2-Basis).
