# Österreich-Test II: Steiermark – Ergebnis

Stand 2026-10-17. Protokoll: `reports/freeze_protocol_at2.md` (Tag `freeze-at-2`, vor der Auswertung festgeschrieben). Lauf: `results/2026-10-17_at_test_stmk/` (`metrics.json`, `site_year.csv`).
Datenkritik: `reports/data_review/at_test_stmk.md`. Ein Lauf, nichts nachträglich geändert, kein Sieger. Modelle und Scores unverändert aus `freeze-at-1`; neu nur die steirischen Standorterträge.

> **Kurz: Die Steiermark liefert zu wenige Standort-Jahre für einen Test (12 statt mindestens 15). Die Zahlen sind nur beschreibend.** Die Richtung ist wie in Oberösterreich positiv, aber nicht belegt.

## Ergebnis (Stichtag 1.9., Versuchsarten Düngung + Bodenbearbeitung)

| Weg | ρ [95-%-KI] | n (Zeilen / Jahre) | Urteil |
|---|---|---|---|
| **S-A** Stress-Score → `YAS_site` | 0,47 [−0,32; 0,95] | 12 / 7 | **nicht auswertbar** (< 15), nur beschreibend |
| S-B Regionalmodell (AT22) → `YAS_site` | −0,13 [−0,59; 0,56] | 10 / 6 | nicht auswertbar, kein Signal |
| Vergleich: mittleres NDVI Juni–Aug. | 0,39 [−0,16; 0,88] | 12 / 7 | beschreibend |
| Verbund Oberösterreich + Steiermark (Score; **nicht unabhängig**) | 0,43 [0,15; 0,63] | 46 / 8 | nur beschreibend |

Standort-Jahre: Wagna 7 (2018–2024), Kalsdorf 5 (2018, 2019, 2021, 2022, 2024), **Hatzendorf 0** (nur 3 Jahre mit Versuch und kein Vorjahres-Mittel, daher kein `YAS_site`).
Stichtage (S-A): 15.7. −0,07, 1.8. 0,07, 15.8. 0,33, 1.9. 0,47; bei allen nicht auswertbar. Mit allen vier Versuchsarten (Sensitivität) ändert sich nichts: 12 Standort-Jahre, ρ = 0,42 [−0,47; 0,93].
Beschreibend am 1.9.: innerhalb der Standorte Kalsdorf 0,5 (5 Jahre), Wagna 0,43 (7 Jahre); Leave-one-year-out 0,26–0,75; die beiden schwächsten Wagna-Jahre 2021/2022 haben auch niedrige Scores (−0,012 / −0,019).

## Was das heißt
- **Nicht belegt, nicht widerlegt.** 12 Standort-Jahre von nur 2 Standorten tragen keine Aussage; die Intervalle reichen von deutlich negativ bis fast perfekt.
- **Die Richtung passt zu Oberösterreich** (Score höher = Ertrag höher, ρ ≈ 0,4–0,5), und das einfache NDVI liegt wieder auf ähnlichem Niveau (0,39). Der Verbund (n = 46) ist nicht unabhängig, weil Oberösterreich schon im ersten Test ausgewertet wurde.
- **Das EU-Regionalmodell zeigt für die Steiermark nichts** (ρ = −0,13), wie schon in Oberösterreich auf Standortebene.
- **Warum so wenig Daten:** Düngungs-/Bodenbearbeitungsversuche liegen nur für wenige Jahre vor, und `YAS_site` braucht mindestens 3 andere Jahre desselben Standorts.

## Nächste Schritte (Vorschläge, nichts davon gelaufen)
1. Mehr steirische Versuchsjahre oder -standorte digitalisieren (frühere Hatzendorf-Berichte, LK Steiermark); dann ein neuer Test mit eigenem Freeze.
2. Praxis-Felderträge aus der Steiermark (V3, `ANFRAGEN.md` Nr. 5): damit wäre ein Feldvergleich überhaupt erst möglich.
