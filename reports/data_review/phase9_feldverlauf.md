# Datenkritik – Umbau „Dein Feld, dein Verlauf“ (Warnlogik, On-demand-Pipeline, AT-Machbarkeit, Website)

Stand 2026-10-17. Vorab-Festlegungen in `DECISIONS.md` (Commit `139bdab`, vor jeder Rechnung).

| Punkt | Geprüft wie? | Befund | Konsequenz |
|---|---|---|---|
| 3.1 Repräsentativität | Zählung `alert_calibration` | 123 US-HLS-Feld-Jahre aus 11 Standort-Jahren; Warnungen stammen aus 7–8 Standort-Jahren, 12 von 26 (15.8., X = 20 %) aus KBS-T4-Bio-Parzellen | Trefferquoten mit breitem KI und T4-Hinweis berichtet |
| 3.1 Wolken | `n_valid` je Stichtag | Vor 15.7. hat kein Feld-Jahr ≥ 4 beobachtete Dekaden ab Juni → kein Score; am 1.9. nur 67 von 123 gültig | „keine Aussage möglich“ statt Warnung; Prävalenz je Zelle berichtet |
| 3.2 Korrektheit | Code-Vergleich und Live-Abruf | On-demand-Dekaden = Trainingsdekaden: 167 Feld-Jahre / 1 861 Dekaden offline identisch (Abweichung 0); Live-GEE-Abruf BARC EastFarm 6-60 2018: 12 Dekaden identisch; fold-freie Referenzkurve reproduziert die eingefrorene bis 5·10⁻⁷ | Pipeline nutzt nur Trainingsfunktionen; Tests `test_field_pipeline.py`, `test_alert_calibration.py` |
| 3.3 Scheinzusammenhänge | Fallprüfung Warnungen | Der Score markiert Bewirtschaftung (späte Saat) | Oberfläche: „Kurve auffällig“, keine Ursache; Wetterhinweise nur aus vorab festgelegten Regeln |
| 3.4 Leakage | Kalibrierung | Referenzkurve und Schwelle je Fold nur aus den anderen Standort-Jahren; eingefrorene Schwellen aus allen Daten nur für die Anwendung | ✅ |
| 3.4 Österreich-Regel | Code-Review | Kalibrierung nutzt nur US-Daten; das US-Modell wird nicht verändert. Der AT-Machbarkeitstest nutzt nur die aggregierte, bereits ausgewertete Tabelle `results/2026-10-17_at_test/site_year.csv` und ist als eigenes Modell gekennzeichnet | ✅ |
| 3.5 Plausibilität | Ergebnisse | Kein früher Vorlauf (Aussage erst ab 15.8.); Fehlalarmrate out-of-fold 0,26–0,51 statt ≤ 0,20; AT-Modell ρ 0,01 [−0,44; 0,41] | so berichtet, nichts nachträglich angepasst |
| Nutzerdaten | Backend | Felder pseudonym, nur 127.0.0.1, keine Konten; Nutzererträge fließen nie in ein Modell | ✅ |
| Nicht geprüft | – | Kein echter Demonstrationsschlag mit mehreren Ertragsjahren; Weg B an österreichischen Praxisfeldern ohne Ertrag nicht überprüfbar; spanische und französische Texte nicht von Muttersprachlern geprüft | offen, in DECISIONS festgehalten |

**Entscheidung:** ⚠️ Weiter mit Einschränkung – Warnlogik und AT-Modell sind ehrlich schwach und werden als Konzept bzw. Machbarkeitstest gekennzeichnet.
