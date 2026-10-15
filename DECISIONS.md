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
