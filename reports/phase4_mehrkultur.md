# Etappe 4 – Mehr-Kulturen-Experimente (h = 30) und Gate G3

Stand 2026-10-16. Rohzahlen: `results/2026-10-16_mehrkultur_h030/` (metrics.csv, criteria.json, controls.json, oof_*.parquet). Festlegungen vorab in DECISIONS.md (2026-10-16). Eine Modellrunde, nichts nachträglich geändert. Österreich nicht berührt.

## Daten
Stufe S2, Prognose 30 Tage vor der Ernte, HLS-Satellit (30-m-Kreis). Zeilen mit Wetter: 474 (Winterweizen 196, Erbse 169, Mais 109); mit gültiger Satellitenkurve (Hauptlauf): 235 Standort-Jahre, 210 Wetterzellen-Jahre (Weizen 89 / Mais 70 / Erbse 51, alle ≥ 40). Gate G1 ✓. **Gate G2 ✓ nach der vorab festgelegten Regel** (Mais und Winterweizen; `reports/data_review/w33_kurvenpruefung.md`), aber die Zusammenhänge zwischen Kurvenmerkmalen und RY sind mit |ρ| ≤ 0,08 sehr schwach: formal bestanden, inhaltlich knapp.

## Ergebnis: „Stark genug (Mehrkultur)“ – **nicht bestanden (G3 ✗)**
| Kriterium | Ergebnis |
|---|---|
| 1 schlägt B0 und B1 auf Mais und ≥ Hälfte der Kulturen | **✗** – keine Kultur: RMSE-Differenz zu B0 ≥ 0 oder KI schließt 0 ein (Mais M-Kultur +0,002 [0,000; 0,006]) |
| 2 ρ gepoolt ≥ 0,4 und Mais ≥ 0,3 | **✗** – ρ gepoolt −0,17, Mais −0,56 |
| 3 Kultur-Transfer (M-Pool-ohne-Mais → Mais) ρ > 0, KI ohne 0 | **✗** – ρ = 0,01 [−0,26; 0,32], n = 85 (nur Winterweizen → Mais: 0,02 [−0,23; 0,27]) |
| 4 Label-Shuffle fällt auf Baseline | **✗** – eine von drei Wiederholungen hat ρ = −0,13 [−0,25; −0,02] (Artefakt, siehe unten) |
| 5 Kulturen < 40 Zellen-Jahre | keine betroffen |

Hauptmodell nach der Vorab-Regel: M-Kultur.

## Warum ρ negativ ist (Artefakt, kein Signal)
Auch die Baselines haben gepooltes ρ < 0 (B0 −0,11, B1 −0,18). Ursache: Im Leave-Jahr-und-Gruppe-Out liegt der Trainingsmittelwert niedriger, wenn die Testgruppe viele gute Jahre enthält; Vorhersage und Ziel laufen dadurch gegenläufig. Der Wert ist keine Evidenz für eine verkehrte Beziehung, verhindert aber, dass Kriterium 2 (ρ ≥ 0,4) erreichbar wird. Aussagekräftiger ist die RMSE-Differenz: Sie ist ≈ 0 (|Δ| ≤ 0,01 bei RY ≈ 1), die Modelle sind **nicht besser als der Mittelwert**. Gegen B1 (nur `cwb_30d`) sind sie teils besser (M-Pool −0,010 [−0,017; −0,002]), weil B1 selbst schlechter als der Mittelwert ist. Das Kriterium wird nicht nachträglich geändert.

## Kontrollen (E4/E5, `controls.json`)
- Koordinaten-Ablation: gepoolt ρ −0,23 ohne, −0,23 mit Koordinaten, also kein Ortsgedächtnis.
- Leave-One-Dataset-Out: g2f 0,01, invite −0,11, peas_fr −0,13.
- Adversarial Validation (Wetter, Mais gegen Rest): AUC 1,00. Die Kulturen liegen in völlig anderen Wetterbereichen (andere Saisonfenster und Klimaräume); das Pooling teilt den Wettereffekt nur über die Standardisierung je Kultur.
- Mit S3 (776 Zeilen) bzw. S3+S4 (1 042 Zeilen), nur Wetter: M-Kultur schlechter als B0 (+0,009 bis +0,010, KI > 0), M-Pool ≈ B0. Mehr Zeilen helfen nicht.

## Einordnung
- Mit Versuchsparzellen-Mitteln, Ridge und den gewählten Wetter-/Satellitenmerkmalen ist **kein vorhersagbares Signal für den relativen Ertrag erkennbar**, für alle drei Kulturen und im Kultur-Transfer.
- Mögliche Gründe (nicht bewiesen): RY aus Sortenversuchsmitteln ist verrauscht (wechselnde Sortensätze, Parzellen statt Felder); der 30-m-Kreis liefert nur 1–3 HLS-Pixel, und nur 235 von 474 Zeilen haben eine gültige Kurve; nur eine Maisquelle; keine Boden- und Sortenmerkmale (TAW fest 150 mm); RY schwankt kaum (Median 1,0; 5. Perzentil 0,6–0,7).
- **Konsequenz laut Plan (G3 ✗):** nicht nach Österreich. Optionen stehen in DECISIONS.md: Feldkarten abwarten (YIPEEO, SwissYield), spätere Horizonte, Phase 5 (CY-Bench, Regionalebene) als Hauptergebnis. Eine weitere Modellrunde braucht eine neue Entscheidung des Projektinhabers.
