# Delta Green

Früherkennung von Stress und Ertragsverlust auf einzelnen Maisfeldern aus Satelliten-Zeitreihen, Wetter und Boden – gelernt an Feldern mit gemessenem Ertrag (USA mit vielen Jahren je Feld, dazu Afrika und Südamerika), dann eingefroren und ohne Anpassung in Österreich (Steiermark) als Beweis getestet; ergänzt um einen regionalen Transfer-Test EU → Österreich (CY-Bench).

Projekt für den Bundeswettbewerb Künstliche Intelligenz (BWKI) Österreich.

- **Was gemacht wird:** [PLAN.md](PLAN.md)
- **Wie gearbeitet wird:** [AGENTS.md](AGENTS.md)
- **Änderungen:** [CHANGELOG.md](CHANGELOG.md) · **Entscheidungen:** [DECISIONS.md](DECISIONS.md) · **Unterstützung:** [SUPPORT.md](SUPPORT.md)

## Status

Phasen 0–3 abgeschlossen (v0.4.0), Phase 4 „stark genug“ **nicht bestanden** (kein Freeze, kein Österreich-Test), Phase 5 bis zum EU-Freeze (`freeze-cybench-1`), Feinjustierung ohne Verbesserung (Gate H2 ✗). **Hauptergebnis der Abgabe:** [reports/doku/hauptergebnis.md](reports/doku/hauptergebnis.md) – Karte innerhalb des Feldes (ρ 0,68) und EU-Regionalmodell (ρ 0,38). Offene Entscheidungen: [reports/NACHTLAUF.md](reports/NACHTLAUF.md). Offene Anfragen: [ANFRAGEN.md](ANFRAGEN.md).

## Website (lokal, privat)

Die Website zeigt Ziel, Vorgehen, Quellen, alle Ergebnisse Version für Version, einen interaktiven Modellvergleich, einzelne Felder und das Projektlog. Sie läuft nur lokal und liest keine österreichischen Daten.

```
.venv\Scripts\python.exe app\precompute.py          # einmal nach jedem neuen Lauf
.venv\Scripts\streamlit.exe run app\streamlit_app.py
```

Dann im Browser http://localhost:8501 öffnen. Inhalte der Seite „Ergebnisse“ stehen in [app/versions.yaml](app/versions.yaml) (ein Eintrag je Version: was geändert wurde, Zahlen, Befunde, Grenzen, Abbildungen); `tests/test_app.py` prüft, dass jede dort genannte Abbildung und jeder Pfad existiert.
