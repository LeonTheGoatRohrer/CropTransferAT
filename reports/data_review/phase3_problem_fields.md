# Datenkritik Phase 3 – Problemfelder erkennen (F2)

Datum: 2026-10-16 · Branch `phase-3-problem-fields` · Lauf: `python -m croptransfer.phase3 --run results/2026-10-16_round3 --model M-alle-rel --kind ridge --basis S2 --variant round3` → `results/2026-10-16_round3/phase3.json`, `phase3_cases.csv`, Abbildung `reports/figures/phase3_earlywarning_risk.png`.

**Kandidat:** nach der vorab festgelegten Regel (DECISIONS 2026-10-16) das gewählte Modell der letzten Runde, **M-alle-rel Ridge S2** – ein Kandidat **ohne** Freeze-Freigabe (Phase 4 nicht bestanden). Ursachen-Regeln wurden vor der Auswertung festgelegt (DECISIONS 2026-10-16).

## Ergebnisse (LOFYO, S2-Basis, n = 89 Feld-Jahre / 8 Standort-Jahre, Prävalenz „gefährdet“ 0,33)

| Stichtag | (a) Schwelle auf vorhergesagtem RY: PR-AUC [KI] · Recall bei 20 % FPR | (b) direkter Klassifikator PR-AUC [KI] | Stress-Score Referenzkurve: ρ mit RY [KI] · PR-AUC |
|---|---|---|---|
| 1.6. | 0,35 [0,25; 0,67] · 0,24 | 0,38 [0,27; 0,73] | – (keine Sommertermine) |
| 15.6. | 0,31 [0,23; 0,56] · 0,03 | 0,36 [0,29; 0,73] | 0,23 [−0,53; 0,56] · 0,58 |
| 1.7. | 0,35 [0,21; 0,58] · 0,21 | 0,29 [0,23; 0,48] | 0,19 [−0,10; 0,64] · 0,60 |
| 15.7. | 0,32 [0,23; 0,51] · 0,21 | 0,35 [0,24; 0,63] | 0,28 [0,07; 0,64] · 0,54 |
| 1.8. | 0,44 [0,33; 0,80] · 0,52 | 0,32 [0,24; 0,59] | 0,21 [0,02; 0,67] · 0,62 |
| 15.8. | 0,40 [0,27; 0,80] · 0,38 | 0,37 [0,22; 0,75] | 0,29 [0,12; 0,64] · 0,64 |
| **1.9.** | 0,40 [0,32; 0,82] · 0,21 | 0,38 [0,28; 0,67] | **0,43 [0,24; 0,72] · 0,71** |

- Die gelernten Modelle liegen bis Mitte Juli auf Zufallsniveau (PR-AUC ≈ Prävalenz 0,33), ab August knapp darüber; KI berühren die Prävalenz.
- Am besten ist das **einfachste Werkzeug**: der Abstand der eigenen S2-NDVI-Kurve zur Referenzkurve „gesunder Mais“ (nur aus Trainingsfolds) – ρ = 0,43 [0,24; 0,72] am 1.9., PR-AUC 0,71. Das passt zum Ergebnis innerhalb der Felder (Phase 2.3) und zum gewählten Stressindikator.
- **Stressindikator (PLAN 3.5):** EVI-K4 (Integral), Median-ρ über KBS/BARC 0,49 (KBS 0,47 [0,44; 0,47] aus nur 2 Jahren, BARC 0,50 [−0,04; 0,87], gepoolt 0,44 [0,10; 0,75]); Voraussetzung ρ ≥ 0,4 erfüllt → festgelegt.
- **Problemzonen im Feld (PLAN 3.3):** siehe `phase2_within_field.md` – PR-AUC 0,66 [0,55; 0,71] bei Prävalenz 0,28 (NDVI 16.7.–15.8.).

## Ursachen (30 gefährdete Feld-Jahre der HLS-Zeit, Regeln vorab festgelegt)

| Standort-Jahr | Zuordnung |
|---|---|
| BARC 2017 | Hitze (4) |
| BARC 2018 | Nässe (2) – passt zum Rekordregen in Maryland 2018 |
| BARC 2019 | Hitze (1) |
| KBS 2020 | Nässe (5), davon Trockenstress + Nässe (3), Nässe + abrupter Schaden (2) |
| KBS 2014, 2017, 2023 | **Ursache unklar** (16) |

Gesamt: Ursache unklar 16, Nässe 9, Hitze 5, Trockenstress 3, abrupter Schaden 2. Krankheiten/Schädlinge werden nicht behauptet.

**Fallstudien (1.9., Regel a):** richtig erkannt: KBS T4R6/T4R4/T4R5 2017; verpasst: KBS T4R1 2017, T4R4 2023, T4R2 2023; Fehlalarme: KBS T4R1 2020, T1R4 2017, T2R1 2017 (`phase3_cases.csv`).

## Prüfliste AGENTS §3

- **3.1 Repräsentativität:** „Gefährdet“ hängt an wenigen Standort-Jahren. **Bei KBS sind 13 von 23 gefährdeten Feld-Jahren Bio-Parzellen (T4)**; Anteil gefährdet je Behandlung: T4 54 %, T1 29 %, T3 12 %, T2 (Direktsaat) 0 %. Bei KBS misst „gefährdet“ also zu einem großen Teil, **in welchem Jahr die Bio-Bewirtschaftung schwächelt** (Unkraut, Stickstoff) – nicht Wetterstress. Das erklärt die vielen „Ursache unklar“ und ist eine echte Grenze für die Übertragung auf konventionelle Praxisfelder.
- **3.2 Korrektheit:** Abrupt-Schaden-Regel nur auf beobachteten Dekaden; bei S2-Lücken unterschätzt sie Ereignisse. Nässe-Regel beruht auf ERA5-Land (9 km).
- **3.3 Scheinzusammenhänge:** Die Referenzkurve ist absolut (nicht relativ) und kann Standortniveaus enthalten; ihr Vorteil ist trotzdem plausibel, weil sie keine Parameter an die wenigen Jahre anpasst. Ursachen sind Plausibilitäts-Zuordnungen, keine Kausalbeweise.
- **3.4 Leakage:** Referenzkurve je Fold nur aus Trainings-Feld-Jahren mit RY ≥ 0,95; Stress-Score nur aus Dekaden, die vor dem Stichtag enden (Test `test_stress_score_as_of`); Klassifikator mit In-Fold-Labels; keine österreichischen Daten.
- **3.5 Plausibilität:** Nichts ist zu gut; Phase-3-Ergebnisse sind schwach bis mäßig, mit breiten KI (8 Standort-Jahre).
- **3.6 Entscheidung:** ⚠️ **Weiter mit Einschränkung.** Abnahme Phase 3 erfüllt (alle Metriken mit KI, Ursachen-Regeln vorab festgelegt). Die One-Acre-Fund-Prüfung der Ursachen (3.4a) ist nur tabellarisch möglich (`phase2_oaf_tabular.md`).
