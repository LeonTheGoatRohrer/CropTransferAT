# Warnlogik „Dein Feld, dein Verlauf“ – Kalibrierung auf US-Daten

Stand 2026-10-17. Regeln vorab festgelegt in `DECISIONS.md` (Commit `139bdab`, vor dem Lauf). Code `src/croptransfer/alert_calibration.py`, Lauf `results/2026-10-17_alert_calibration/` (`calibration.json`, `oof.csv`). Notebook `notebooks/09_alert_calibration.ipynb`.

**Ziel:** Das Feld-Jahr endet mit einem Ertrag mehr als X % unter dem eigenen Normalniveau (`RY < 1 − X/100`). **Signal:** eingefrorener Stress-Score (`freeze-at-1`) am Stichtag. **Regel:** Warnung, wenn der Score höchstens so hoch ist wie die Schwelle, die in den Trainingsdaten höchstens 20 % der Feld-Jahre ohne Ereignis warnt. **Daten:** 123 US-Feld-Jahre (KBS, BARC, Colorado), 11 Standort-Jahre. Trefferquoten out-of-fold (Standort-Jahr weggelassen, Referenzkurve und Schwelle im Fold neu).

## Ergebnis

| Stichtag | X | Treffer / Warnungen | Präzision [95-%-KI] | Prävalenz | Recall | Fehlalarmrate (OOF) | Aussage |
|---|---|---|---|---|---|---|---|
| 1.6., 15.6., 1.7. | alle | – | – | – | – | – | keine Aussage (kein gültiger Score: < 4 Dekaden ab Juni) |
| 15.7. | alle | 3–10 / 23 | – | – | – | 0,72–0,80 | keine Aussage (Warnungen aus nur 1 Standort-Jahr) |
| 1.8. | alle | 3–9 / 11–19 | – | – | – | 0,19–0,40 | keine Aussage (Warnungen aus nur 1 Standort-Jahr) |
| 15.8. | 10 | 18 / 29 | 0,62 [0,48; 1,00] | 0,34 | 0,82 | 0,26 | ok |
| 15.8. | 15 | 13 / 26 | 0,50 [0,14; 1,00] | 0,25 | 0,81 | 0,27 | ok |
| 15.8. | 20 | 12 / 26 | 0,46 [0,14; 1,00] | 0,22 | 0,86 | 0,27 | ok |
| 15.8. | 25 / 30 | 10 / 28 | 0,36 [0,14; 0,75] | 0,17 | 0,91 | 0,33 | ok |
| 1.9. | 10 | 19 / 33 | 0,58 [0,44; 1,00] | 0,34 | 0,83 | 0,32 | ok |
| 1.9. | 15 | 13 / 26 | 0,50 [0,10; 1,00] | 0,25 | 0,76 | 0,26 | ok |
| 1.9. | 20 | 12 / 39 | 0,31 [0,14; 0,50] | 0,21 | 0,86 | 0,51 | ok |
| 1.9. | 25 / 30 | 10 / 29 | 0,34 [0,14; 0,89] | 0,16 | 0,91 | 0,34 | ok |

X = 25 und 30 ergeben dieselben Ereignisse (kein Feld-Jahr mit RY zwischen 0,70 und 0,75).

## Einordnung

- **Kein früher Vorlauf belegt:** Vor dem 15.8. ist keine Aussage möglich. Die Warnung kommt also frühestens Mitte August, wenige Wochen vor der Ernte.
- **Trefferquote knapp über dem Zufall:** z. B. 15.8., X = 20 %: 12 von 26 Warnungen (46 %) bei einer Prävalenz von 22 %. Die Intervalle sind breit (nur 7–8 Standort-Jahre tragen Warnungen).
- **Fehlalarmrate hält die 20 % außerhalb der Trainingsdaten nicht** (OOF 0,26–0,51): Die Schwelle überträgt sich nicht stabil zwischen Standort-Jahren.
- **Bewirtschaftung statt Stress:** 12 der 26 Warnungen (15.8., X = 20 %) betreffen die Bio-Parzellen KBS T4 (6 davon Treffer). Der bekannte T4-Befund gilt auch hier: Eine Warnung heißt „Kurve auffällig“, nicht „Stress diagnostiziert“.
- Startwerte der Stufen (Hinweis 20 %, Warnung 30 %) sind damit **auswertbar ab 15.8.**, aber nicht „bestätigt“ im Sinne guter Trennschärfe.
