# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [SemVer](https://semver.org/lang/de/) – ein Minor-Release pro Phase (siehe AGENTS.md §4.4).

## [Unreleased]

## [0.0.3] – 2026-10-15
### Changed
- `PLAN.md` neu aufgebaut: nach dem Setup zuerst der **Ertrags-Datensatz** (KBS LTER, USDA BARC, Colorado; Mead nach Klärung) mit HLS- und Sentinel-2-Saisonkurven; danach Steiermark-Pilot, Ertragsbezug in Österreich (GO/NO-GO), CY-Bench parallel, dann Phasen 5–11.
- Satellitenbasis: HLS v2 (30 m, ab 2013) für lange Reihen + Sentinel-2 (10 m) parallel.
- GO-Bedingung (a) wird jetzt mit gemessenem Feldertrag (relativer Ertrag RY) in Phase 1 geprüft.
- One Acre Fund vom Validierungsweg in den Ausblick verschoben (nur ein Jahr je Feld).
- `AGENTS.md`: Versionstabelle für 12 Phasen (v0.1.0 … v0.11.0, v1.0.0); Pflicht-Tests für Ertrags-Datensatz und LOFYO-Splits.

### Added
- Forschungsfrage F0 (Kurve ↔ gemessener Ertrag, ab wann?) und F4c (Transfer US-Ertragsmodell → Österreich).
- Definitionen: Feld-Ertrag, Umrechnung auf 15,5 % Feuchte, relativer Ertrag RY, „gefährdet“ (RY < 0,85), Pixel-Paare innerhalb der Felder.
- Validierungssplits LOFYO / LOFO / Leave-One-Dataset-Out.
- Aufgaben für den Projektinhaber: Erlaubnis-Anfrage an KBS, AmeriFlux-Konto.

## [0.0.2] – 2026-10-15
### Changed
- `PLAN.md`: neue Phasenreihenfolge (0 Setup → 1 Pilot → 2 Zielgrößen-Check GO/NO-GO → 3 CY-Bench parallel → 4–10 Pipeline, Modelle, Demo, Abgabe).
- Zielgröße ist jetzt ein Kandidatensatz K1–K5 (Kalender- und phänologische Fenster) mit vorab festgelegter Auswahl- und GO/NO-GO-Regel.
- Frühernte-Regel: abrupter Abfall auf Boden-Niveau wird als Ernte markiert, nicht als Stress.
- `AGENTS.md`: Versionstabelle an die neuen Phasen angepasst (v0.1.0 … v0.10.0, v1.0.0).

### Added
- Drei Validierungswege für den Ertragsbezug (V1 regional AT, V2 Feld international, V3 Feld AT über Landwirt:innen).
- Forschungsfrage F0 (taugt die Satelliten-Zielgröße als Ertrags-Stellvertreter?).
- Klarstellung im Plan: Training erfolgt pro Feld, regionale Mittel dienen nur der Kontrolle.
- Aufgabe für den Projektinhaber: Feld-Ertragsdaten bei Landwirt:innen anfragen.

## [0.0.1] – 2026-10-15
### Added
- Projektplan (`PLAN.md`) mit Forschungsfragen, technischen Festlegungen, Definitionen und Phasen 0–8.
- Agenten-Arbeitsanweisung (`AGENTS.md`) mit Arbeitszyklus, Datenkritik-Prüfliste, Versionierungs- und Testregeln.
- Repository-Grundgerüst (README, CHANGELOG, DECISIONS, SUPPORT, .gitignore).
