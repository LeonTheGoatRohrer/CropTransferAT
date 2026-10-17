# Regionales Nachtrainieren mit österreichischen Bundesland-Erträgen (Zusatz F5, explorativ)

**Stand:** 2026-10-17, festgeschrieben **vor** der Auswertung des Österreich-Tests (`reports/freeze_protocol_at.md`, `freeze-at-1`) und vor jedem Blick auf dessen Ergebnis.
Entscheidung des Projektinhabers (Chat 2026-10-17): nach dem Test auch noch das regionale Nachtrainieren, „wenn es sich ausgeht“.

## Einordnung
- **Nicht Teil des Beweises.** Der Transfertest mit dem eingefrorenen EU-Modell bleibt das Hauptergebnis. Hier kommen österreichische Daten ins Training;
  die Aussage ist nur: *Wie viel bringt lokale Anpassung gegenüber dem reinen Übertrag?*
- **Sehr kleine Datenmenge:** 5 Maisländer × 9 Jahre = 45 Region-Jahre. Ein Ergebnis ist höchstens ein vorsichtiger Hinweis. Verfehlen heißt „nicht belegt“.
- Es wird **kein Sieger gewählt** und nichts am eingefrorenen Modell geändert; jede Variante wird berichtet.

## Daten
- Ziel `YAS`: Statistik Austria, Körnermais, 5 Bundesländer (AT11, AT12, AT21, AT22, AT31), Ertrag / olympischer Durchschnitt der 5 Vorjahre (wie im Test).
- Jahre 2015–2023 (YAS ab 2015, Prädiktoren bis 2023). Merkmale wie im eingefrorenen Modell (CY-Bench-AT-Prädiktoren, as-of je Stichtag).
- Stichtage: **09-01** (Haupt) und 08-01.
- Zusätzlich zu 2018–2023 aus dem Test enthält die Auswertung 2015–2017; das eingefrorene Modell R0 wird dort ebenfalls bewertet (Zusatzbewertung, ändert V1 nicht).

## Varianten (alle Parameter vorab festgelegt)
| Kürzel | Beschreibung |
|---|---|
| **R0** | eingefrorenes EU-Modell, unverändert (Referenz) |
| **R1** | lineare Neukalibrierung: `YAS ≈ a + b · Vorhersage_R0`, `a, b` per OLS auf den Trainingsjahren |
| **R2** | Neutraining des Modells auf EU-Daten **plus** österreichische Zeilen der Trainingsjahre mit Gewicht **20** (Hyperparameter, Merkmale und Seed unverändert aus `lgbm_<stichtag>_meta.json`) |

Validierung: **Leave-one-year-out** über 2015–2023 (Testjahr aus dem österreichischen Training herausgenommen; die EU-Zeilen bleiben immer drin). Bewusst nicht
„nur Vorjahre“, weil sonst für die frühen Jahre fast nichts zum Anpassen bleibt – die Nutzung künftiger Jahre als Training wird deshalb gekennzeichnet.

## Metriken (Cluster-Bootstrap über Jahre, 1000, Seed 42)
Spearman ρ gepoolt (mit 95-%-KI); RMSE gegen `YAS = 1`; RMSE-Differenz zu R0 (negativ = besser als R0, mit KI); ρ innerhalb der Jahre (beschreibend); n angeben.

## Kriterium (nur beschreibend, keine Modellwahl)
Eine Variante „verbessert“ R0, wenn die RMSE-Differenz zu R0 am Stichtag 09-01 ein 95-%-KI **ohne 0** hat und negativ ist. Sonst: „nicht belegt“. Die Variante mit dem kleinsten RMSE wird **nicht** zum
neuen Modell erklärt; ein neuer Freeze wäre eine eigene Entscheidung mit neuer Testgrundlage.

## Grenzen (stehen so im Bericht)
45 Region-Jahre, 9 Jahre als Cluster; jedes Jahr trifft alle Regionen gemeinsam (starker Jahreseffekt); R2 kann wegen 20× Gewicht auf wenigen Zeilen überanpassen; die Statistik-Austria-Erträge sind
dieselben, die im Test als Ziel dienen (daher kein unabhängiger Test, nur Leave-one-year-out).
