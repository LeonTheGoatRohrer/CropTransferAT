Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 3 Was bestimmt den Ertrag? (F0 und F1; Phase 1 und 2)

**Kurzantwort:** Zwischen **Feldern** und **innerhalb eines Feldes** sieht der Satellit den Ertrag gut. Die Unterschiede **zwischen Jahren** (Wetterjahr) kann ein Modell mit nur 8 bis 11 Standort-Jahren nicht auf neue Jahre übertragen.

## 3.1 Die Datenbasis ist klein

Mais steht auf den KBS-Parzellen nur jedes dritte Jahr (Fruchtfolge Mais–Soja–Weizen). In der HLS-Zeit (ab 2013) gibt es 168 Mais-Feld-Jahre (KBS 96, BARC 62, Colorado 10; `DATA_SOURCES.md`; PLAN nennt „~170“ **[Zahl prüfen]**). Einen relativen Ertrag RY haben davon **123 Feld-Jahre**, und sie stammen aus nur **11 Standort-Jahren** (KBS 2014/17/20/23, BARC 2014 und 2016–2021). Feld-Jahre desselben Standort-Jahres teilen das Wetter und sind keine unabhängigen Fälle; wichtig ist also die Zahl der **Jahre**, nicht der Felder.

Weitere Einschränkungen (Datenkritik Phase 1):

- KBS 2014 hat in HLS keinen klaren Termin von Juli bis September, KBS 2017 kaum einen. Nach der vorab festgelegten Datenqualitätsregel fehlen dort die Kurvenmerkmale, statt Aprilwerte fortzuschreiben. Mit der HLS-Basis haben nur 2 von 4 KBS-Jahren eine Sommerkurve.
- Die Prüfung, ob Landsat 5/7 für die KBS-Jahre vor 2013 verwendbar wäre, wurde **nicht bestanden**: NDVI-Median-Differenz −0,016 (Grenze ≤ 0,03, erfüllt), aber RMSD 0,073 (Grenze ≤ 0,07, verfehlt); EVI −0,021 / 0,080 (n = 413 Dekaden-Paare, 133 Feld-Jahre). Die Grenze war vorab festgelegt und wird nicht nachträglich gelockert. Daher gibt es keine Satellitenmerkmale vor 2013 (Wetter- und Bodenmodelle dürfen die langen KBS-Reihen nutzen, Variante „W-lang“).
- Bewertet wird immer auf den 123 Feld-Jahren der HLS-Zeit (HLS-Basis) bzw. 89 Feld-Jahren aus 8 Standort-Jahren (Sentinel-2-Basis).

## 3.2 Erster Blick (Phase 1): Es gibt ein Signal

Der Spearman-Zusammenhang zwischen dem Stressindikator „Integral des EVI über die Saison“ (K4) und RY liegt gepoolt bei ρ = 0,44 (KI 0,10 bis 0,75; n = 74 Feld-Jahre, 9 Cluster). Für KBS allein ist ρ ≈ 0,64, beruht aber nur auf zwei Jahren (2020, 2023) und ist daher vor allem ein Jahresvergleich. Kurven der besten und schlechtesten Jahre unterscheiden sich sichtbar (z. B. BARC 2018 mit RY 0,52 und Rekordniederschlag in Maryland).

## 3.3 Zwischen Jahren: nicht übertragbar (Phase 2)

Aufbau: 9 Modelle (Satellit, Wetter, Boden, Kombinationen) × Ridge/LightGBM × 7 Stichtage × 2 Satelliten-Basen = 238 Läufe, Validierung LOFYO, Tuning verschachtelt.

Ergebnis am Stichtag 1.9. (Auswahl; `reports/data_review/phase2_models.md`):

| Modell | ρ gepoolt [95-%-KI] | RMSE | Skill vs. B0 |
|---|---|---|---|
| B0 („normales Jahr“) | – | HLS 0,27 / S2 0,29 | 0 |
| M-S Ridge S2 (nach Regel gewählt) | −0,04 [−0,29; 0,37] | 0,61 | −1,13 |
| M-alle Ridge S2 | 0,23 [0,05; 0,43] | 0,55 | −0,91 |
| M-B (nur Boden/Gelände) Ridge HLS | 0,03 [−0,17; 0,31] | 0,28 | −0,03 |
| M-W (nur Wetter, „W-lang“) LightGBM HLS | −0,06 [−0,48; 0,31] | 0,35 | −0,30 |

- **Kein Modell schlägt „normales Jahr“ (B0) im RMSE** an irgendeinem Stichtag. Ein früher Stichtag hilft nicht; die Frühwarnkurve bleibt um null.
- **Auswendiglernen statt Verstehen:** Für das gewählte Modell ist ρ bei ungesehenem Feld, aber **gesehenem Jahr** (LOFO) 0,65 [0,31; 0,75], bei ungesehenem Jahr (LOYO) 0,00 [−0,32; 0,48]. Das Modell überträgt also ein bekanntes Jahr auf neue Felder, aber keine neuen Jahre. Der Jahreseffekt macht den größten Teil der RY-Streuung aus.
- **Standort-Kennungen statt Ursachen:** Datensätze sind an den Merkmalen perfekt trennbar (Adversarial AUC KBS gegen BARC = 1,00). Die wichtigsten Einzelmerkmale (nutzbare Feldkapazität, organischer Kohlenstoff, Strahlung) kennzeichnen den Standort, sie erklären nicht den Ertrag.
- **Kontrollen bestanden:** Label-Shuffle ρ = 0,00 [−0,22; 0,35] (Zufallsniveau); keine Leakage-Spur.
- **Unsicherheit:** Split-Conformal-Intervalle erreichen die Soll-Abdeckung (79 % bei Soll 80 %; 89 % bei Soll 90 %), sind aber mit halber Breite 0,78 bzw. 0,97 RY praktisch nutzlos breit.

*In einfachen Worten:* Wenn man dem Modell das Jahr schon einmal gezeigt hat, rät es neue Felder gut. Muss es ein ganz neues Wetterjahr einschätzen, ist es nicht besser als die Annahme „alles normal“, weil es aus 8 bis 11 Jahren keine allgemeine Regel lernen kann.

## 3.4 Welche Faktoren zählen? (F1)

- **Aufteilung:** In den Modellen verteilen sich die SHAP-Beiträge auf Satellit (0,22), Boden (0,14) und Wetter (0,13) (Einheit **[prüfen]**). SHAP zeigt nur, was das Modell benutzt, keine Ursachen; bei korrelierten Merkmalen ist es vorsichtig zu lesen.
- Wetter allein erklärt RY über die Jahre nicht, auch nicht mit den langen KBS-Reihen (14 Mais-Jahre, „W-lang“).
- Der Boden erklärt zwischen den KBS-Parzellen nichts: Alle 24 liegen in derselben SSURGO-Karteneinheit (NCCPI Mais überall 0,664); dort wirkt SSURGO nur als Standort-Kennung. Wetter (ERA5-Land, 0,1°) ist für alle KBS-Parzellen derselbe Punkt, erklärt also nur Jahresunterschiede.
- Der Einfluss von Bewirtschaftung (Dünger, Saatdichte, Sorte) mit One-Acre-Fund-Daten sollte laut Plan getrennt analysiert werden. Diese Analyse ist in den vorliegenden Berichten nicht dokumentiert: **[ergänzen]**.

## 3.5 Innerhalb der Felder: stark (BARC)

Frage: Welche Feldteile bringen weniger Ertrag, und warum? Daten: 41 BARC-Feld-Jahre (27 Felder, 2017–2021), 23 912 Ertragspixel (10 m) nach −10-m-Puffer; Sentinel-2 (NDVI, NDRE) und Copernicus-DEM. KI über Feld-Jahre.

| Zeitfenster (Sentinel-2) | Median-ρ NDVI mit relativem Pixel-Ertrag [KI] | NDRE |
|---|---|---|
| 15.6.–15.7. | 0,45 [0,34; 0,53] | 0,49 [0,37; 0,57] |
| **16.7.–15.8.** | **0,68 [0,54; 0,72]** | **0,68 [0,62; 0,73]** |
| 16.8.–15.9. | 0,35 [0,27; 0,52] | 0,40 [0,34; 0,55] |

- **Problemzonen** (relativer Pixel-Ertrag < 0,85) findet der Satellit mit PR-AUC 0,66 [0,55; 0,71] bei Prävalenz (Zufallsniveau) 0,275. Das Ergebnis hält ohne die äußeren 20 m (ρ 0,71), kommt also nicht vom Feldrand.
- **Pixelmodell** (Stichtag 15.8., ganzes Feld ausgelassen): nur Satellit ρ 0,70, nur Gelände 0,22 [0,07; 0,29], beides 0,70. Das Modell ist kaum besser als ein einzelner Index (0,68).
- **Zonen kehren wieder:** Zwischen Jahren desselben Feldes ρ = 0,67 [0,58; 0,75] (9 Felder mit mindestens 2 Jahren, 19 Jahrespaare). Schwache Zonen liegen meist jedes Jahr am selben Ort.
- **Gelände (30 m) erklärt wenig** (Höhe ρ −0,23, Neigung −0,12, TPI −0,01; tiefere Lagen bringen etwas mehr). Das heißt nicht „Gelände wirkt nicht“: Die Auflösung ist grob, und Boden (250 m SoilGrids, 90 m TWI) wurde im Pixelmodell nicht untersucht.

*Grenzen dieses Ergebnisses:* nur ein Standort (BARC) und 41 Feld-Jahre; die Ertragskarten sind aus Mähdrescherpunkten gekriged (versetzte Jahresgitter bis 7,5 m, unbekannter Lagefehler); NDVI und NDRE sind mit B8A/B5 effektiv ~20 m grob; Randeffekte (der Ertrag fällt zum Rand); Konfundierung durch unbekannte Bewirtschaftung (Sorte, Verdichtung, Fahrgassen); kein räumlicher Block-Split. „Wiederkehrend“ kann Boden bedeuten, aber ebenso gleiche Bewirtschaftungsspuren.

## 3.6 Antwort auf F0 und F1

- **F0:** Für ungesehene Jahre nicht verlässlich; für bekannte Jahre auf neue Felder gut (LOFO 0,65); innerhalb eines Jahres ordnet ein Satellitenmodell die Felder teilweise richtig (Median-ρ bis 0,40 auf Sentinel-2).
- **F1:** Innerhalb des Feldes dominiert der Satellitenbefund im Hochsommer (Mitte Juli bis Mitte August); zwischen Feldern und Jahren lässt sich mit den vorhandenen Daten keine verallgemeinerbare Faktorenrangfolge belegen.
- Die Antwort ist schwach, aber ehrlich: Mit mehr Standort-Jahren (Ausblick, Kapitel 6) könnte sie sich ändern.
