# Datenkritik – Österreich-Test II: Steiermark

Zu `reports/at_test_stmk_ergebnis.md`; Protokoll `reports/freeze_protocol_at2.md`. Entscheidung: ⚠️ **weiter mit Einschränkung** (Ergebnis nur beschreibend berichten).

## 3.1 Auswahl / Repräsentativität
- **Nur 12 von 24 steirischen Standort-Jahren haben ein `YAS_site`**: Hatzendorf 0 (3 Versuchsjahre, Basis aus ≥ 3 anderen Jahren nicht erreichbar), Kalsdorf 5 von 8, Wagna 7 von 8 (2025 ohne Ertrag). Alle 24 haben einen Score.
- Die Steiermark ist damit durch **zwei** Standorte vertreten (Wagna, Kalsdorf); es sind 7 Jahre als Cluster, mit 1–2 Standorten je Jahr.
- Basis von `YAS_site`: 9 von 12 mit fünf Vorjahren, 3 mit „Mittel der anderen Jahre“.

## 3.2 Sind die Daten korrekt?
- **Versuchsart statt Sorte:** Düngungs-/Bodenbearbeitungsversuche, Mittel über Varianten (Stickstoffstufen/Verfahren), keine reinen Wettereffekt-Messungen.
- **Ertragsniveau und Brüche:** Die Standortmittel liegen sehr verschieden (Kalsdorf 11,1–15,5 t/ha, Wagna 6,3–11,0 t/ha); bei Wagna fällt das Mittel ab 2021 von etwa 10 auf 6–7 t/ha. Ein Strukturbruch im Versuch (andere Varianten/Anlage) kann das miterklären; er ist aus den Zahlen allein nicht zu trennen. Ein Teil des `YAS_site` bei Wagna 2021–2024 (0,65–0,90) kann daher Versuchsdesign statt Wetter sein.
- Satellitenseite unverändert zum ersten Test (siehe `reports/data_review/at_test.md`): Felder je Standort-Jahr ≥ 96 gültig, maistypische Kurven; Standortposition = Gemeindemitte.

## 3.3 Scheinzusammenhänge
- Mit 1–2 Standort-Jahren je Jahr lässt sich „innerhalb eines Jahres“ nicht beurteilen. Der Jahres-Proxy-Effekt aus dem ersten Test (Score unterscheidet vor allem Jahre) ist hier nicht prüfbar.
- Der Score-≈-NDVI-Befund bleibt: S-A 0,47 gegen NDVI 0,39 (beide mit KI, die 0 einschließt).
- Konfundierung: Düngungsstufen, Sorten, Aussaat, Hagel unbekannt.

## 3.4 Leakage
- Österreich-Regel: Scores und Regionalvorhersagen stammen unverändert aus `freeze-at-1` (Datei per SHA-256 im Protokoll); neu nur steirische Erträge, geöffnet nach `freeze-at-2`. Die Versuchsarten wurden vor dem Blick auf Erträge festgelegt. Nach dem Lauf wurde nichts geändert.
- Offengelegt (Protokoll §5): 15 Notizzeilen mit Versuchsmitteln wurden vor dem ersten Test gesehen; ob steirische darunter waren, ist nicht dokumentiert.
- Der Verbund Oberösterreich + Steiermark enthält Oberösterreich, das im ersten Test schon ausgewertet wurde; er zählt nicht als Test.

## 3.5 Plausibilität
- Ergebnisse nicht zu gut (ρ 0,47, Intervall −0,32 bis 0,95; nicht auswertbar). Die Konfidenzintervalle sind bei n = 12 sehr breit.
- Fallstudie Wagna: 2022 niedrigster Ertrag (0,65) und niedrigster Score der Jahre mit Ertrag (−0,019) – passend; 2023 niedriger Ertrag (0,78) bei neutralem Score (−0,002) – nicht passend.

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Nur beschreibend berichten; keine Aussage „bestanden“ oder „nicht bestanden“.
