# Innerhalb-Feld über Standorte – Vorab-Festlegungen (I3, vor jedem Modelllauf)

Stand 2026-10-17. Gehört zu `reports/plan_innerfeld.md`. Alles hier wird **committet, bevor** ein Modell mit Erträgen trainiert oder Merkmale mit Erträgen verglichen werden. Spätere Änderungen sind verboten (AGENTS §1.3); Abweichungen werden in `DECISIONS.md` begründet und im Bericht genannt.

Bestätigt vom Projektinhaber (Chat 2026-10-17): Plan `plan_innerfeld.md` und „mache weiter mit allen Punkten“ (I3 bis I5 ohne weitere Rückfrage). Der Projektinhaber hat diese Datei **nicht vor** dem Lauf einzeln gelesen; sie ist deshalb als KI-Entwurf gekennzeichnet (`SUPPORT.md`) und bleibt zur Prüfung offen.

Vor diesem Dokument wurden angesehen: Verteilungen des relativen Ertrags je Standort (I1), Merkmalsabdeckung und Lage des NDVI-Maximums (I2). **Nicht** angesehen: irgendein Zusammenhang zwischen Satellitenmerkmal und Ertrag außer dem schon berichteten BARC-Wert von Phase 2.3 (NDVI 16.7.–15.8., Median-ρ 0,676).

---

## 1. Zeilen und Ziel

| Standort | Hauptauswertung | Sensitivität |
|---|---|---|
| BARC | alle 41 Feld-Jahre, 23 912 Zellen | nur Zellen ≥ 20 m vom Rand |
| Kayad | alle 3 Feld-Jahre (1 Feld) | ohne 2016 (nur 9 gültige Dekaden); ohne Zellen mit ≥ 50 % gedeckelten Punkten (`frac_cap`); nur Zellen ≥ 20 m vom Rand |
| Colorado | die **6 regulären** Teilflächen-Jahre (Mittelertrag ≥ 2,0 t/ha) | alle 10; Grenze 2,0 t/ha liegt in der Lücke zwischen 1,04 und 2,52 t/ha, gesetzt nach Ansicht der I1-Ertragsmittel (nicht der Merkmale) |

- **Ziel:** relativer Ertrag `rel` = Zellertrag / Mittel des Feld-Jahres (aus `gt_pixels`). **Problemzone:** `rel` < 0,85.
- **Trainingsziel:** `rel`, z-standardisiert innerhalb des Feld-Jahres (maßstabsfrei, damit Standorte mit SD 0,10 und 0,26 vergleichbar sind).
- **Zellen mit fehlendem Merkmal:** Merkmal = 0 (Feldmittel nach z-Standardisierung) für die Modelle; für B0/B1 werden Zellen ohne Wert ausgeschlossen. Feld-Jahre mit weniger als 10 auswertbaren Zellen entfallen.
- Keine Zelle wird nach ihrem Ertrag entfernt (keine Ausreißerregel).

## 2. Modelle (Parameter endgültig)

Alle Merkmale kommen aus `features_innerfeld.parquet` (I2) mit den dort festgelegten Parametern: Maximum der 3-Dekaden-geglätteten Feld-NDVI-Kurve in den Dekaden 6–17, gültige Dekade ab 50 % gültiger Zellen, B1 = Dekaden Maximum ±1, M1-Fenster Maximum −4…−2 / −1…+1 / +2…+4. **Diese Werte werden nicht mehr angepasst.**

| ID | Beschreibung |
|---|---|
| **B0** | z-NDVI, Median der Dekaden 10–13 (10.7.–17.8.; nächste Dekaden-Entsprechung des festen Fensters 16.7.–15.8.), keine Anpassung, Vorzeichen +. Auf BARC zusätzlich **B0-alt** (altes Fenster, Zwischenspeicher aus Phase 2.3) zur Kontrolle: Median-ρ muss 0,676 ± 0,02 treffen |
| **B1** | `z_b1_ndvi` (Spitzenfenster), Vorzeichen +, keine Anpassung |
| **B2** | Wiederkehr: mittlerer `rel` derselben Zelle in den **anderen** Jahren desselben Feldes; nur Feld-Jahre mit ≥ 1 anderem Jahr und ≥ 50 zugeordneten Zellen. Enthält Ertragswissen aus anderen Jahren, ist also kein reiner Satellitenwert, nur Orientierung (Obergrenze für „dauerhafte Zonen“) |
| **M1** | Ridge (α = 1,0, `sklearn.linear_model.Ridge`) auf `z_m1_ndvi_w1..3`, `z_m1_ndre_w1..3` (6 Merkmale), Zielgröße z-`rel`, Zeilengewicht = 1 / (Zellen des Feld-Jahres), damit jedes Feld-Jahr gleich zählt |
| **M2** | M1 + `z_elev`, `z_slope`, `z_tpi` (Kontrolle gegen Geländeeffekt) |
| **K-Raum** | Kontrollmodell nur aus Position: Ridge (α = 1) auf z-x, z-y, z-x², z-y², z-x·z-y innerhalb des Feld-Jahres. Zeigt, wie viel eine glatte räumliche Tendenz erklärt, ohne Satellit |

Kein LightGBM, kein anderes Modell, keine Hyperparametersuche.

## 3. Testschemata

| Schema | Beschreibung |
|---|---|
| **E (Einzelstandort)** | BARC: Leave-One-Field-Out (27 Folds). Kayad: Leave-One-Year-Out (**optimistisch**, weil dieselben Zellen in allen Jahren vorkommen; nur beschreibend). Colorado: Leave-One-Plot-Out |
| **T (Transfer)** | Training auf allen Zellen von Standort i, Test auf Standort j, alle Paare i ≠ j (6 Richtungen). Colorado-Training nur mit den 6 regulären Feld-Jahren |
| **L (Leave-One-Site-Out)** | Training auf den beiden anderen Standorten, Test auf dem ausgelassenen |
| **K (Kulturtransfer)** | entfällt (CH-TAN fehlt, keine zweite Kultur) |

Seeds überall 42. Bootstrap: 1 000 Ziehungen, 95 %, Percentile, Cluster = Feld (BARC), Feld-Jahr (Colorado), Jahr (Kayad); wo nur 1 Cluster bleibt, gibt es kein KI.

## 4. Kennzahlen

- **Hauptkennzahl:** Median über Feld-Jahre des Spearman-ρ (Vorhersage, `rel`), nur Feld-Jahre mit ≥ 10 Zellen.
- **Lift:** Anteil Problemzonen im Viertel mit der niedrigsten Vorhersage ÷ Anteil Problemzonen insgesamt; Median über Feld-Jahre mit Problemzonen-Anteil zwischen 0,05 und 0,95.
- **PR-AUC − Prävalenz** für Problemzonen, Median über dieselben Feld-Jahre.
- **Differenzen Δ** gepaart auf denselben Feld-Jahren (Median der Einzeldifferenzen), KI per Cluster-Bootstrap derselben Ziehungen.
- Standorte mit weniger als 10 Feld-Jahren (Kayad 3, Colorado-Hauptmenge 6): nur Punktwerte, Anteil positiver Feld-Jahre und Vorzeichen, **kein** Bestanden/Nicht-bestanden.

## 5. Gates (endgültig)

- **J2 – Regel überträgt:** B0 oder B1 hat an jedem Fremdstandort mit ≥ 10 Feld-Jahren Median-ρ ≥ 0,30 und KI-Untergrenze > 0. Mit der Hauptmenge aus §1 hat **kein** Fremdstandort 10 Feld-Jahre (Kayad 3, Colorado 6): **J2 = „nicht prüfbar“ ist vorab festgelegt.** Berichtet wird beschreibend (Median-ρ, Anteil positiver Feld-Jahre, Vorzeichen).
- **K1 – Fensterwahl (neu, auf BARC prüfbar):** B1 ist nicht schlechter als B0: Δ Median-ρ (B1 − B0) auf BARC ≥ −0,03 mit gepaartem Feld-Cluster-Bootstrap-KI, dessen Untergrenze ≥ −0,06 liegt. Erfüllt: das Spitzenfenster ist ein gleichwertiger Ersatz des Kalenderfensters.
- **J3a – Training lohnt (BARC, intern):** M1 (Leave-One-Field-Out) minus B1 und minus B0: jeweils Δ Median-ρ ≥ +0,03 und KI-Untergrenze > 0 (Feld-Cluster). Beide Vergleiche müssen bestehen.
- **J3b – Training lohnt (fremd):** wie J3a im Transfer T und L auf Fremdstandorten; mangels ≥ 10 Feld-Jahre „nicht prüfbar“, nur beschreibend.
- **Label-Shuffle (Kontrolle zu J3):** Training mit innerhalb jedes Feld-Jahres gemischtem Ziel (20 Wiederholungen), Test auf echten Labels: Median-ρ muss im Betrag ≤ 0,10 liegen. Sonst Leakage-Verdacht, J3 gilt als verfehlt.
- **Gesamtaussage der Studie** (vorab festgelegte Formulierungen, je nach Ausgang):
  - K1 ✓ und J3a ✗: „Das einfache NDVI-Spitzenfenster genügt; Training bringt auf BARC nichts.“
  - K1 ✗: „Das Kalenderfenster ist dem Spitzenfenster auf BARC überlegen; für andere Klimaräume ist die Fensterwahl offen.“
  - J3a ✓ und Label-Shuffle ok: „Training bringt auf BARC etwas; Übertragbarkeit nicht geprüft.“
  - J2 bleibt in jedem Fall „nicht prüfbar“, bis Daten mit ≥ 10 Feld-Jahren an einem Fremdstandort vorliegen. Aussagen über andere Standorte sind beschreibend.

## 6. Kontrollen

1. **Label-Shuffle** (siehe §5), für M1, im Schema E-BARC und T (Training BARC, Test Kayad).
2. **Randabstand:** Wiederholung von B0, B1, M1 nur mit Zellen ≥ 20 m vom Rand (BARC, Kayad).
3. **Wiederkehr B2** (ab 2 Jahren; BARC, Kayad) und **K-Raum**: berichten, wie viel davon B1 erklärt; kein Gate.
4. **Gelände M2** vs. M1: nur BARC aussagekräftig (Kayad, Colorado praktisch eben).
5. **Fenstervergleich:** auf Kayad zusätzlich B0 (Juli/August, Kalenderfenster) vs. B1 beschreibend, weil das Maximum dort im Juni liegt.
6. **Kayad ohne 2016**, **Kayad ohne gedeckelte Zellen**, **Colorado alle 10 Feld-Jahre** (Sensitivitäten aus §1).
7. **Streuungsvergleich:** neben jeder Zahl die SD des relativen Ertrags des Standorts (BARC 0,26, Kayad 0,10–0,15, Colorado 0,10–1,32).

## 7. Nicht Teil dieses Laufs

Radar, Temperatur, GDD, Begrünungsdatum (in der Feinjustierung getestet); Österreich (Freeze und Freigabe fehlen); zusätzliche Standorte (DWFI, SwissYield warten auf Antwort); CH-TAN (Embargo).

## 8. Eine Runde

Es gibt genau **eine** Modellrunde mit diesen Festlegungen. Fehler im Code dürfen behoben werden, wenn sie die Ausgabe ändern, aber nur mit Begründung in `DECISIONS.md`; Parameter und Schwellen werden nicht geändert.
