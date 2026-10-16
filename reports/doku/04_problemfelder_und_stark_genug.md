Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 4 Problemfelder erkennen und „Stark genug?“ (F2; Phase 3 und 4)

**Kurzantwort:** Problemzonen innerhalb eines Feldes findet der Satellit gut (Kapitel 3). Ganze **gefährdete Felder** früh zu erkennen gelingt nur schwach bis mäßig. Keine der vier Stufen (Phase 2 und drei Verbesserungsrunden) hat das vorab festgelegte Kriterium „stark genug“ erfüllt. Deshalb gibt es **keinen Freeze** und **keinen Test in Österreich**.

## 4.1 Was geprüft wurde (Phase 3)

Alle Auswertungen mit LOFYO, Sentinel-2-Basis, **89 Feld-Jahre aus 8 Standort-Jahren**, Anteil „gefährdet“ (RY < 0,85) = 0,33. Der Kandidat ist nach der vorab festgelegten Regel das gewählte Modell der letzten Runde (M-alle-rel, Ridge) und ausdrücklich ein **Kandidat ohne Freeze-Freigabe**.

Drei Werkzeuge:

- (a) Schwelle auf dem vorhergesagten RY; (b) direkter Klassifikator (flaches LightGBM).
- **Referenzkurve „gesunder Mais“:** Median-NDVI-Kurve der Trainings-Feld-Jahre mit RY ≥ 0,95. Der **Stress-Score** ist die mittlere negative Abweichung der eigenen Kurve von dieser Referenz bis zum Stichtag.
- **Ursachen-Regeln** (feste Faustwerte, vorab festgelegt): Trockenstress (Wasserstress-Index zur Blüte ≥ 0,30 oder Wasserbilanz der letzten 30 Tage < −60 mm), Hitze (mindestens 5 Tage über 32 °C zwischen 10.7. und 20.8.), Nässe (Frühjahrsniederschlag ≥ 250 mm), abrupter Schaden (NDVI-Einbruch ≥ 0,15 im Juli/August ohne Erholung; Verdacht auf Hagel/Sturm/Lager). Greift keine Regel, heißt die Antwort „Ursache unklar“. Krankheiten und Schädlinge werden **nicht** behauptet.

## 4.2 Ergebnisse (Stichtage; Auszug aus `phase3_problem_fields.md`)

| Stichtag | (a) Schwelle: PR-AUC [KI] | (b) Klassifikator: PR-AUC [KI] | Stress-Score: ρ mit RY [KI] · PR-AUC |
|---|---|---|---|
| 1.7. | 0,35 [0,21; 0,58] | 0,29 [0,23; 0,48] | 0,19 [−0,10; 0,64] · 0,60 |
| 1.8. | 0,44 [0,33; 0,80] | 0,32 [0,24; 0,59] | 0,21 [0,02; 0,67] · 0,62 |
| 15.8. | 0,40 [0,27; 0,80] | 0,37 [0,22; 0,75] | 0,29 [0,12; 0,64] · 0,64 |
| **1.9.** | 0,40 [0,32; 0,82] | 0,38 [0,28; 0,67] | **0,43 [0,24; 0,72] · 0,71** |

*In einfachen Worten:* PR-AUC misst, wie gut gefährdete Felder vor den gesunden gereiht werden; **Zufall entspricht der Prävalenz 0,33**.

- Die gelernten Modelle liegen bis Mitte Juli auf Zufallsniveau und ab August knapp darüber; die KI berühren die Prävalenz.
- Das **einfachste Werkzeug ist das beste:** der Abstand zur Referenzkurve am 1.9. (ρ = 0,43, PR-AUC 0,71). Das passt zum Ergebnis innerhalb der Felder.
- **Stressindikator:** EVI-Integral (K4) mit Median-ρ 0,49 über KBS und BARC (gepoolt 0,44 [0,10; 0,75]); die vorab festgelegte Voraussetzung ρ ≥ 0,4 ist erfüllt. Die KBS-Zahl stammt aus nur 2 Jahren.

## 4.3 Ursachen und eine wichtige Grenze

Von 30 gefährdeten Feld-Jahren der HLS-Zeit (Mehrfachzuordnung möglich, daher addieren sich die Zahlen auf mehr als 30): Ursache unklar 16, Nässe 9, Hitze 5, Trockenstress 3, abrupter Schaden 2. Die Zuordnung ist plausibel zu bekannten Ereignissen (z. B. BARC 2018: Nässe, passend zum Rekordregen in Maryland), aber eine **Plausibilitätszuordnung, kein Kausalbeweis**.

**Bio-Parzellen bei KBS:** 13 von 23 gefährdeten KBS-Feld-Jahren sind Bio-Parzellen (T4); Anteil gefährdet je Behandlung: T4 54 %, T1 29 %, T3 12 %, T2 (Direktsaat) 0 %. „Gefährdet“ misst bei KBS also zu einem großen Teil, **in welchem Jahr die Bio-Bewirtschaftung schwächelt** (Unkraut, Stickstoff), nicht Wetterstress. Das erklärt die vielen „Ursache unklar“ und begrenzt die Übertragung auf konventionelle Praxisfelder. Fallstudien (1.9., Regel a): richtig erkannt KBS T4R6/T4R4/T4R5 2017; verpasst T4R1 2017, T4R4 2023, T4R2 2023; Fehlalarme T4R1 2020, T1R4 2017, T2R1 2017.

Die Prüfung der Regeln an den von Landwirt:innen gemeldeten Schäden (One Acre Fund) ist nur tabellarisch möglich: Trockenheit steckt dort in `pest`/`disease`, Hagel hat keine eigene Spalte (`DATA_SOURCES.md` §9). Das Ergebnis ist in den Berichten nicht enthalten: **[ergänzen]**.

## 4.4 Phase 4: „Stark genug?“ – das vorab festgelegte Kriterium

Alle vier Bedingungen mussten erfüllt sein (LOFYO, Stichtag 1.9. bzw. ab 1.8., 95-%-KI per Cluster-Bootstrap über Datensatz-Jahre):

1. Das Hauptmodell schlägt B0 und B1 an mindestens einem Stichtag ab 1.8. signifikant (KI der RMSE-Differenz ohne 0).
2. Spearman ρ ≥ 0,4 am 1.9.
3. Leave-One-Dataset-Out: ρ > 0 in beiden Richtungen (KBS → BARC und BARC → KBS).
4. Label-Shuffle fällt auf Zufallsniveau.

| Stufe | gewähltes Modell | ρ 1.9. [KI] (n) | Bed. 1 | Bed. 2 | Bed. 3 (KBS→BARC / BARC→KBS) | Bed. 4 | stark genug |
|---|---|---|---|---|---|---|---|
| Phase 2 | M-S Ridge S2 | −0,04 [−0,29; 0,37] (89) | nein | nein | 0,42 / −0,19 (nein) | ja | **nein** |
| Runde 1 (relative Satellitenmerkmale) | M-Srel Ridge S2 | 0,37 [−0,01; 0,70] (89) | nein | nein | 0,47 / 0,40 (ja) | ja | **nein** |
| Runde 2 (einfachere Merkmale) | M-Srel-einfach Ridge S2 | −0,01 [−0,21; 0,59] (89) **[Zahl prüfen: results.md nennt −0,02]** | nein | nein | −0,21 / 0,18 (nein) | ja | **nein** |
| Runde 3 (stärkere Regularisierung) | M-alle-rel Ridge S2 | 0,37 [−0,02; 0,68] (89) | nein | nein | 0,77 / 0,53 (ja) | ja | **nein** |

Die drei Verbesserungsrunden waren **vorab** mit Reihenfolge und Abbruchregel festgelegt (höchstens 3, alle werden vollständig berichtet, auch wenn schlechter). **Alle Runden sind ehrlich berichtet.**

**Warum es scheitert:** Mit relativen Merkmalen (Abweichung vom Normalniveau des Standortes bzw. der Nachbarfelder) wird die Rangfolge der Feld-Jahre besser (ρ ≈ 0,37, beide LODO-Richtungen > 0 in Runde 1 und 3). Die **Höhe** der Abweichung vom Normaljahr trifft das Modell aber nicht genauer als die Annahme „normales Jahr“ (Bedingung 1; Skill gegen B0 in Runde 3: −0,02). Ursache ist vor allem die kleine Zahl unabhängiger Standort-Jahre (8 in der Sentinel-2-Basis).

## 4.5 Entscheidung

Nach dem Plan („Nicht stark genug? Nicht nach Österreich gehen“) wird **nicht eingefroren** und **kein Österreich-Test** vorbereitet; weitere Runden sind nach der Vorab-Festlegung nicht erlaubt. Jede weitere Änderung braucht eine neue Entscheidung des Projektinhabers (z. B. mehr Daten wie Mead, die offene Landsat-Frage, YieldSAT, siehe Kapitel 6). Das ist ein **gültiges, ehrliches Ergebnis**: Das Kriterium hat genau das getan, wofür es gedacht war, und ein schwaches Modell nicht als Beweis nach Österreich gelassen.
