# Datenkritik – Feldkarte: Wie viel der „gemessenen“ Ertragskarte liegt weit weg von Messpunkten?

Anlass: Beim Bau des Video-Einstiegs (2026-11-06) fiel auf, dass im Feld `CentralFarm_1_1` 2020 ein großer Teil keine Mähdrescher-Punkte hat, die USDA-Kriging-Karte dort aber gefüllt ist.
Lauf: `python -m croptransfer.within_field_coverage` → `results/2026-11-06_within_field_coverage/` (`metrics.json`, `per_field_year.csv`). Beschreibend; dieselben 41 Feld-Jahre, dieselbe NDVI-Regel, nichts neu gewählt.
Entscheidung: ✅ **weiter**, die Kernzahl hält. Mit einem Hinweis für die Darstellung.

## Geprüft wie
Für jede 10-m-Zelle der 41 Feld-Jahre: Abstand zum nächsten bereinigten Mähdrescher-Punkt (USDA-Ordner `3A`, Eingabe des Krigings). Danach Spearman-ρ und Feldkarte (unterstes NDVI-Viertel) auf allen Zellen und nur auf Zellen nahe einem Punkt.

## Befund

| | Alle Zellen | nur ≤ 15 m | nur ≤ 30 m |
|---|---|---|---|
| Median-ρ (41 Feld-Jahre) | 0,68 | 0,68 | 0,68 |
| 95-%-KI (Bootstrap über Feld-Jahre) | [0,54; 0,72] | [0,59; 0,73] | [0,59; 0,73] |
| Anteil Feld-Jahre mit ρ > 0 | 100 % | 100 % | 100 % |
| Treffer im untersten NDVI-Viertel (Median) | 58 % | 58 % | 58 % |
| Problemzonen-Anteil (Median) | 27 % | 27 % | 27 % |

- **Weit entfernt sind nur 1,5 %** aller Zellen (> 15 m) bzw. 0,9 % (> 30 m). In den meisten Feld-Jahren sind es 0 %.
- **Betroffen sind 4 von 41 Feld-Jahren** (> 2 % der Zellen): `APU_1` 2021 (25 %), `CentralFarm_1_1` 2020 (20 %), `CentralFarm_1_15` 2021 (5 %), `EastFarm_5_23` 2019 (4 %).
- **In zwei davon senkt die interpolierte Lücke den Wert:** `APU_1` 2021 ρ 0,06 auf allen Zellen, aber 0,63 nahe den Punkten; `CentralFarm_1_1` 2020 0,68 gegenüber 0,77. Interpolierte Flächen lassen den Wert hier also eher fallen, als dass sie ihn künstlich erhöhen.
- **Nebenbefund:** Die Datei `USDA_EastFarm_5_3A_2019_CORN_ptfinal_utm` ist als UTM-Zone 10 beschriftet, die Werte sind aber Zone 18. Das Modul liest deshalb die gespeicherten Koordinaten und nicht die Beschriftung. Die Hauptpipeline nutzt das Kriging-Raster dieses Feldes und ist nicht betroffen.

## Grenzen
- Auch nahe den Punkten bleibt die Karte eine Kriging-Interpolation (geglättet); das steht schon im Hauptergebnis.
- Die Rangkorrelation ist vor allem eine Aussage für BARC, einen Standort.

## Folge für die Darstellung
- „Gegen den gemessenen Ertrag“ ist für die Kernzahl vertretbar. Genauer ist: „gegen Ertragskarten aus Mähdrescher-Messungen“.
- Das Feld im Video-Einstieg wurde nach Regel gewählt, nicht nach Aussehen: ρ am Median (0,68) und praktisch keine Lücke (`EastFarm_5_12` 2021: 0,4 % der Zellen > 15 m, ρ 0,68).
- `CentralFarm_1_1` 2020 steht als Median-Beispiel in `reports/figures/phase2_within_field_maps.png`. Dort sollte die Lücke bei der nächsten Überarbeitung genannt oder das Feld getauscht werden. Hier nichts geändert.
