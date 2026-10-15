# Entscheidungen

Jede Festlegung oder Abweichung von `PLAN.md`: Datum, Entscheidung, Grund, verworfene Alternativen.

| Datum | Entscheidung | Grund | Alternativen |
|---|---|---|---|
| 2026-10-15 | Feldanalyse auf Steiermark fokussiert | viel Körnermais, kaum Bewässerung, Hagel + Trockenstress | NÖ/Bgld (Bewässerung verfälscht), ganz AT (zu heterogen für Start) |
| 2026-10-15 | Satellitendaten über Google Earth Engine | serverseitige Extraktion für Tausende Felder | Planetary Computer (langsamer, lokal) |
| 2026-10-15 | Selbstüberwachte Zielgröße (NDRE August) statt Feld-Ertrag | keine öffentlichen Feld-Erträge in AT | internationale Feld-Erträge (→ Ausblick) |
| 2026-10-15 | Internationale Feld-Ertragsdatensätze nur als Ausblick; Transfer-Test regional über CY-Bench | Datenlage/Domain-Shift; CY-Bench enthält AT + EU fertig aufbereitet | One Acre Fund, USDA BARC, KBS als Kern |
| 2026-10-15 | **Neue Phasenreihenfolge:** Pilot (Ph. 1) → Zielgrößen-Check als GO/NO-GO (Ph. 2) → volle Pipeline (ab Ph. 4); CY-Bench-Regionalmodell (Ph. 3) parallel ab Phase 0 | Ertragsbezug der Satelliten-Zielgröße muss feststehen, **bevor** ein Modell darauf gebaut wird; Pilot prüft billig, ob lokale Unterschiede überhaupt sichtbar sind | Ertragsbezug erst am Ende prüfen (alter Plan, Phase 6) – Risiko, ein Modell auf eine ungeeignete Zielgröße zu bauen |
| 2026-10-15 | **Drei Validierungswege** für den Ertragsbezug: V1 regional AT (Statistik Austria + CY-Bench feinste Ebene), V2 Feld international (One Acre Fund, KBS, BARC), V3 Feld AT (Landwirt:innen, falls beschaffbar) | Bundesland-Mittel allein zu grob – lokale Dürre (ein Tal ja, Nachbartal nein) würde verschwimmen | nur regionale Validierung |
| 2026-10-15 | Zielgröße wird aus Kandidaten K1–K5 nach **vorab fixierter Regel** gewählt (GO: ρ ≥ 0,4 in ≥ 1 Feld-Datensatz **und** regional positiver Zusammenhang mit 95-%-KI ohne 0) | verhindert nachträgliches Zurechtbiegen; phänologische Fenster (K2–K4) machen internationale Felddaten vergleichbar | fest I_Aug ohne Prüfung |
| 2026-10-15 | Pilot-Jahre werden **vor** Ansehen der Satellitendaten anhand der Statistik-Austria-Erträge gewählt (ein schwaches, ein normales Jahr) | kein Rosinenpicken | zufällige Jahre |
| 2026-10-15 | **Erster Schritt nach dem Setup: Ertrags-Datensatz USA** (KBS LTER, USDA BARC, Colorado sofort; Mead nach Klärung) mit HLS- und S2-Saisonkurven; Test mit ausgelassenen Feldern **und** Jahren (LOFYO) | Kernannahme „Kurve verrät Ertrag“ nur mit gemessenem Ertrag prüfbar; wenige Felder × viele Jahre liefern das Wetter-/Stress-Signal; Mähdrescherdaten zeigen zusätzlich Unterschiede innerhalb der Felder | Steiermark-Pilot ohne Ertrag zuerst (v0.0.2); One Acre Fund (nur 1 Jahr je Feld) |
| 2026-10-15 | **HLS v2 (Landsat 8/9 + Sentinel-2, 30 m)** für lange Reihen ab 2013; Sentinel-2 10 m parallel ab 2017 | Sentinel-2 allein liefert < 10 Saisons; HLS-Merkmale für US- und AT-Felder gleich → US-Modell auf AT anwendbar | nur Sentinel-2; Landsat 5/7 |
| 2026-10-15 | Ertrags-Zielgröße **relativer Ertrag RY** (Ertrag / Mittel desselben Feldes in anderen Mais-Jahren), „gefährdet“ = RY < 0,85 | entfernt Standortniveau (Boden, Bewässerung) → übertragbar auf Österreich | absoluter Ertrag t/ha (nur sekundär) |
| 2026-10-15 | Neue Phasenfolge: 0 Setup → 1 Ertrags-Datensatz → 2 Steiermark-Pilot → 3 Ertragsbezug AT (GO/NO-GO) → 4 CY-Bench parallel → 5–11; GO-Bedingung (a) jetzt aus Phase 1 (ρ ≥ 0,4 mit RY) | Ertragsbezug zuerst dort messen, wo Ertrag bekannt ist | – |
| 2026-10-15 | Neue Forschungsfrage F4c: Transfer US-Ertragsmodell → Österreich; Vergleich mit selbstüberwachtem Modell in Phase 9 | verbindet ursprüngliche Transfer-Idee mit dem Feldansatz | – |
