# Datenkritik F3 – Ablation und Kontrollen (Feinjustierung)

Stand 2026-10-16. Zahlen: `results/2026-10-16_feinjust_ablation/` (`metrics.json`, `controls.json`, `product.json`, `sensitivity_T4.json`). Bericht: `reports/feinjustierung_ergebnis.md`.

## 3.1 Repräsentativität
- Ziel A: 89 Feld-Jahre in nur **8 Standort-Jahren**; 4 Standort-Jahre haben beide Klassen. BARC 2017 (4/4) und 2018 (2/2) sind ganz gefährdet, BARC 2020/2021 gar nicht – dort gibt es nur Jahresunterschiede. Gefährdete Fälle: 29, davon 12 KBS-T4-Parzellen (je 6 in 2017 und 2023) → **Ergebnis hängt stark von einer Behandlung ab**.
- Fehlende Merkmalswerte (LST 47 %) werden im Fold mit dem Median aufgefüllt; alle Varianten haben dieselben Zeilen.

## 3.2 Korrektheit
- Siehe `f2_merkmale.md`. Keine neuen Datenfehler gefunden. Gate H1 reproduziert die berichteten Werte exakt.

## 3.3 Scheinzusammenhänge
- **Bewirtschaftung als Proxy (neu, wichtig):** KBS-T4 bekommt in allen drei Jahren das höchste Risiko (0,86–0,94), unabhängig vom Ertrag; 2020 sind die sechs höchsten Werte Fehlalarme (T4, RY 0,86–1,15). Innerhalb derselben Behandlung × Jahr: Median-ρ −0,29 (12 Gruppen à 6). Ohne T4: PR-AUC 0,60 [0,18; 0,95] bei Prävalenz 0,24.
- **Label-Shuffle A:** 0,47 ± 0,09 statt 0,33 – der Score enthält label-freie Information (Abweichung von einer typischen Kurve; die Referenz aus zufälligen Feldern bleibt eine typische Kurve). Keine Leakage, aber auch kein Nachweis, dass das gelernte Kombinationsmodell mehr als der Score kann.
- **Label-Shuffle B:** bei einem einzigen linearen Merkmal nicht aussagekräftig (ρ hängt nur vom Vorzeichen des Koeffizienten ab). Das Innerhalb-Feld-Signal kommt aus NDVI selbst, ohne Training (B-roh 0,676).
- **Koordinaten:** Δ +0,006 – kein Ortsgedächtnis. **Adversarial Validation:** Median-AUC 0,61, Jahresunterschiede sichtbar.
- **Konfundierung:** Saattermin, Sorte, Bio-Bewirtschaftung (KBS T4), Zwischenfrucht. Das Begrünungsdatum (M4) sollte Saatunterschiede abbilden, verschlechterte aber Ziel A – vermutlich, weil es T4 nur ein zweites Mal kodiert.

## 3.4 Leakage
- Referenzkurven, Labels (RY im Fold), Imputation und Standardisierung nur aus Trainingszeilen; Merkmale as-of (Tests). LODO ohne Verlust (KBS → BARC 0,86, BARC → KBS 0,79).
- **Österreich-Regel:** nicht berührt; keine österreichischen Daten geladen.

## 3.5 Plausibilität
- Kein Ergebnis ist „zu gut“. Alle neuen Merkmale schaden; plausibel bei ≈ 70 Trainingszeilen je Fold und Merkmalen, die vor allem das Jahr messen.
- Fallstudien: Treffer = T4 2017/2023 (späte Begrünung, Juli-Defizit); Fehlalarme = T4 2020 (gleiche Kurvenform, aber normaler Ertrag); T1 2020 (August-Defizit) wird hinter T4 eingereiht, aber 5 von 6 gefährdeten T1-Parzellen liegen noch über der Schwelle; verpasst = BARC 2017 (alle gefährdet, Risiko 0,35–0,54, nur einer über der Schwelle), BARC 2019 und KBS T1R3 2020.

## 3.6 Entscheidung
⚠️ **Weiter mit Einschränkung (nur Dokumentation).** Das negative Ergebnis der Ablation ist belastbar. Die Aussage von Ziel A muss eingeschränkt werden: In den US-Daten trennt der Score vor allem Bewirtschaftung und Jahre, nicht gleich bewirtschaftete Felder. Ziel B (innerhalb des Feldes) bleibt das robusteste Ergebnis. Keine weitere Modellrunde (Gate H2).
