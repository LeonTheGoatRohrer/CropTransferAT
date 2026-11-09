# Datenkritik: Österreich-Test IV (Maisfelder 2026, Hagelversicherung)

Stand 2026-11-09. Lauf `results/2026-11-09_at_test4/`, Protokoll `reports/freeze_protocol_at4.md`. Alle Zahlen aus `data/interim/at4/evaluation_table.parquet` (lokal).

## 3.1 Repräsentativität (Auswahl-Bias)
- *Geprüft:* Ausschlussgründe gezählt. 826 → 635: Fläche < 1 ha 100, kein Körnermais 44 (CCM 26, Silomais 12, andere), unplausibler Ertrag 41, Betriebssumme 6.
- *Befund:* Kleine Felder (< 1 ha) fehlen wie in allen AT-Tests. Die 41 unplausiblen sind als Sensitivität mitgerechnet (ρ 0,76). Versicherte Betriebe, ~1 % der Maisfläche, Schwerpunkt NÖ.
- *Wolken-Bias:* Am 1.9. haben alle 635 Felder einen gültigen Score; Zahl der beobachteten Dekaden korreliert kaum mit dem Ertrag (ρ 0,00), leicht mit dem Score (0,14).
- *Konsequenz:* ⚠️ Keine Zufallsstichprobe Österreichs; Aussage gilt für Körnermais ≥ 1 ha, 2026.

## 3.2 Korrektheit
- *Einheiten:* Gesamt-kg je Feldstück aus dem Verhältnis zur Fläche erschlossen (log-log-Steigung 0,88; bei Weizen 1,03). Ein Einheitenmix bei Mais bleibt möglich; ρ(Score, Gesamtmenge ohne Teilen) ist nur 0,56, ρ(Score, Fläche) −0,03 → der Zusammenhang kommt vom Ertrag je ha, nicht von der Feldgröße.
- *Feuchte:* 0 bei 40 Feldern (fehlt), ein Wert 15,75 (vermutlich %). 14-%-Umrechnung ändert ρ nicht (0,84). Feuchte korreliert mit Ertrag (0,42) und Score (0,35): gesunde Felder reiften später ab, plausibel im Trockenjahr.
- *Kurvenform / frühe Ernte:* 30 % der Felder haben einen abrupten Abfall. Ohne sie steigt ρ auf 0,87 → frühe Ernte/Silomais-Verwechslung treibt das Ergebnis nicht. Code-105-Prüfung entfernt Silomais und CCM.
- *Offen:* Ob Erträge teils von der Versicherung satellitengestützt geschätzt wurden (wäre zirkulär). Krumme Mengen und Erntefeuchte sprechen für Wiegungen. Rückfrage nötig.
- *Konsequenz:* ⚠️

## 3.3 Scheinzusammenhänge
- *Region/Ort:* Ertrag fällt von West (9,0 t/ha) nach Ost (4,6 t/ha). ρ innerhalb der vier Ost-West-Streifen 0,79–0,84, innerhalb 20-km-Zellen Median 0,71 (25 Zellen) → nicht nur Region.
- *Label-Shuffle:* ρ = 0,00.
- *Fallstudien:* Größte Fehlreihung nach oben: drei Felder mit tiefem Score (−0,12 bis −0,15) und 7,5–9,7 t/ha, alle mit abruptem Abfall (früh abgereift oder früh geerntet, Ertrag trotzdem gut). Nach unten: drei Felder mit Score nahe 0 und 1,5–3,2 t/ha; zwei davon benachbarte IDs (556917/556918) – möglicher Erfassungsfehler oder Schaden nach dem 1.9. (Hagel, Lager).
- *Konfundierung:* Boden, Sorte, Saattermin, Bewässerung unbekannt; der Score misst fehlendes Grün, nicht die Ursache.
- *Konsequenz:* ✅

## 3.4 Leakage
- Score nutzt nur HLS bis zum Stichtag und die Referenzkurve aus `freeze-at-1`; kein Ertrag, keine AT-Anpassung. Protokoll und Code vor dem ersten Satellitenwert committet (Tag `freeze-at-4`, `000f0d8`).
- Österreich-Regel: AT-Daten wurden nicht für Training, Merkmale, Schwellen oder Modellwahl genutzt; am Modell wurde nichts geändert. ✅
- Bekannt vor dem Freeze: Erträge (Protokoll §1). Eine Bereinigungsregel wurde vor dem Freeze korrigiert (gleiche Betriebssumme nur in derselben 10-km-Zelle), ohne Score-Kenntnis.
- Ein Einlesefehler im ersten Auswertungslauf (leere Tabelle, Abbruch vor jeder Kennzahl) wurde behoben; keine Regel geändert.

## 3.5 Plausibilität
- ρ 0,84 ist hoch, aber im Trockenjahr mit Erträgen von 1,5–16 t/ha plausibel: Die Schäden zeigen sich direkt im Grün. NDVI 0,87 bestätigt, dass das Signal einfach sichtbar ist.
- Der Score ist **nicht** besser als NDVI (−0,03 [−0,05; −0,01]).
- KI mit Cluster-Bootstrap über 125 Zellen.

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung.** Ergebnis belastbar für „Felder innerhalb von 2026 unterscheiden“. Grenzen im Bericht: ein Extremjahr, NDVI gleich gut, Ertragsherkunft beim Lieferanten zu klären.
Hinweis Tests: `tests/test_at_retrain.py` schlägt im neuen Worktree fehl, weil die lokale, gitignorierte Modelldatei `results/models/cybench_freeze/` fehlt; im Worktree `at-test-3` grün. Kein Codeproblem dieses Tests.
