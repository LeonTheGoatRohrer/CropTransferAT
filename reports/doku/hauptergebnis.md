# Hauptergebnis: Welches Feld und welcher Feldteil fällt auf?

Stand 2026-10-16. Entwurf für die Projektdoku (Feinjustierung F3.4). Alle Zahlen aus `results/2026-10-16_feinjust_ablation/` (`product.json`, `metrics.json`, `sensitivity_T4.json`) und `results/2026-10-16_within_field/`. Reihenfolge wie im Plan: Ziel A (Felder), Ziel B (Feldteile), dann Ziel C (Jahre).

## Die Idee in einem Satz

Ein gesundes Maisfeld hat eine typische Grünkurve. Das Programm vergleicht die Kurve jedes Feldes bis zum Stichtag mit dieser Referenz und zeigt **erstens**, welche Felder einer Region auffallen, und **zweitens**, wo im Feld die schwachen Zonen liegen.

## A – Welche Felder fallen auf?

**Produkt:** eine Rangliste der Felder je Region und Jahr nach Risiko, mit einer Alarmschwelle (`reports/figures/fj_ranking.png`).

- **Wie gut?** Am 1.9. findet der Stress-Score gefährdete Feld-Jahre (Ertrag unter 85 % des Normalen) mit PR-AUC 0,69 [0,42; 0,89]; Zufall wäre 0,33 (89 US-Feld-Jahre, 8 Standort-Jahre, Bewertung immer auf Jahren und Feldgruppen, die das Modell nicht gesehen hat).
- **Alarmschwelle:** so gewählt, dass höchstens 20 % der nicht gefährdeten Felder Alarm bekommen (konforme Schwelle aus den US-Werten). Ergebnis in den US-Daten: 31 Alarme, davon 20 richtig (Präzision 0,65); 69 % der gefährdeten Felder bekommen Alarm; Fehlalarmrate 18 %.
- **Warum der Alarm?** Der Score zerlegt sich nach Monaten. Gefährdete Felder liegen vor allem im **Juli** unter der Referenzkurve (Summe −0,28 gegenüber −0,13 bei nicht gefährdeten), danach im August (`reports/figures/fj_score_phases.png`). 22 von 31 Alarmen kommen hauptsächlich aus dem Juli.
- **Ehrliche Grenze:** In den US-Versuchsdaten erkennt der Score zu einem großen Teil die **Bewirtschaftung**. Die Bio-Parzellen der Kellogg Biological Station (T4, Saat spät nach einer Zwischenfrucht) haben jedes Jahr das höchste Risiko, auch 2020, als sie normal geerntet haben. Ohne diese Parzellen ist der Nachweis nicht mehr gesichert (PR-AUC 0,60, Intervall [0,18; 0,95], Zufall 0,24). Ein Alarm heißt deshalb „Kurve auffällig“: Das kann Stress sein, aber auch späte Saat.

## B – Welcher Teil des Feldes fällt auf?

**Produkt:** eine Feldkarte mit auffälligen Zonen (`reports/figures/fj_field_map.png`, zwei BARC-Felder 2021).

- **Wie gut?** Innerhalb eines Feldes hängt der NDVI zwischen 16.7. und 15.8. mit dem gemessenen Pixel-Ertrag zusammen: Median-ρ 0,68 [0,54; 0,71] über 41 Feld-Jahre und 27 Felder; in allen 41 Feld-Jahren ist der Zusammenhang positiv.
- **Als Karte:** Markiert man das unterste Viertel der NDVI-Pixel als „auffällig“, liegen 58 % dieser Pixel tatsächlich in einer Problemzone (Ertrag < 85 % des Feldmittels); bei zufälliger Auswahl wären es 27 % (Faktor 2,3). 56 % der Problemzonen werden so gefunden.
- **Warum robust?** Dieses Ergebnis braucht kein Training (NDVI selbst ist das Maß), hängt nicht von wenigen Wetter-Jahren ab und hält die Kontrollen (wiederkehrende Zonen zwischen Jahren, Phase 2.3).
- **Grenze:** nur ein Standort (BARC, Maryland), Ertragskarten interpoliert (10-m-Blöcke), Randpixel mit 10 m Puffer entfernt.

## C – Wird das Jahr schlecht? (Nebenfrage)

Bleibt offen: Mit 8–11 unabhängigen US-Standort-Jahren war die Jahresvorhersage nicht „stark genug“ (Phase 4, Mehr-Kulturen). Auf Regionalebene (Phase 5, EU) gibt es ein schwaches, aber gesichertes Signal (ρ 0,38).

## Was nicht geholfen hat (Feinjustierung)

Radar (Sentinel-1), Oberflächentemperatur und Verdunstung, eine Temperatursummen-Achse und das Begrünungsdatum wurden einzeln nach einer vorher festgelegten Regel getestet. **Keines** verbesserte die Erkennung, alle machten Ziel A schlechter (Bericht `reports/feinjustierung_ergebnis.md`). Auch ein negatives Ergebnis ist ein Ergebnis: Mit den vorhandenen Daten ist die einfache Grünkurve das beste Signal.
