# AGENTS.md – Arbeitsanweisung für KI-Agenten in CropTransfer AT

Diese Datei gilt für **jeden** Agenten (Claude Code, Codex, …), der in diesem Repository arbeitet. Sie wird vor jeder Arbeitssitzung gelesen. `PLAN.md` sagt **was** gemacht wird, diese Datei sagt **wie**.

---

## 1. Grundhaltung

1. **Der Plan ist verbindlich.** Arbeite `PLAN.md` Phase für Phase ab. Keine Phase überspringen, keine Phase als fertig melden, bevor ihr Abnahmekriterium erfüllt ist.
2. **Skepsis gegenüber den eigenen Daten ist Teil der Aufgabe, nicht optional.** Ein gutes Ergebnis ist erst dann gut, wenn geklärt ist, dass es nicht aus Bias, Leakage oder fehlerhaften Daten kommt. Ein überraschend gutes Ergebnis ist zuerst ein Verdachtsfall.
3. **Ehrlichkeit vor Erfolg.** Schwache oder negative Ergebnisse werden genauso sauber berichtet wie gute. Niemals Schwellen, Splits, Features oder Metriken nachträglich so wählen, dass das Ergebnis besser aussieht.
4. **Nachvollziehbarkeit.** Jede Zahl in Doku/Abbildungen kommt aus Code im Repo. Jede Abweichung vom Plan steht in `DECISIONS.md`.
5. **Eigenständigkeit des Projektinhabers respektieren.** Jede KI-Unterstützung wird in `SUPPORT.md` protokolliert (BWKI-Pflicht). Code so schreiben und kommentieren, dass der Projektinhaber jede Zeile erklären kann.

---

## 2. Arbeitszyklus für jeden großen Schritt

Ein **großer Schritt** = eine Phase aus `PLAN.md` oder eine nummerierte Aufgabe darin, die ein eigenes Ergebnis erzeugt (z. B. „INVEKOS-Pipeline läuft“, „LightGBM-LOYO-Ergebnisse“).

```
1. Lesen        → PLAN.md (aktuelle Phase), DECISIONS.md, CHANGELOG.md, letzte Ergebnisse
2. Vorhaben     → kurz festhalten: Ziel, Dateien, erwartetes Ergebnis, Abnahmekriterium
3. Umsetzen     → kleine, testbare Einheiten; Konfiguration in config.yaml, keine Magic Numbers
4. Testen       → pytest muss grün sein (siehe §5)
5. Ausführen    → Pipeline/Experiment laufen lassen, Ergebnisse unter results/ ablegen (siehe §6)
6. DATENKRITIK  → Prüfliste §3 vollständig durchgehen und Ergebnis in reports/data_review/ dokumentieren
7. Dokumentieren→ CHANGELOG.md, ggf. DECISIONS.md, SUPPORT.md aktualisieren
8. Versionieren → Commit(s) + Push (siehe §4); bei Phasenabschluss Merge + Tag
9. Berichten    → dem Projektinhaber: was wurde gemacht, Ergebnis, Datenkritik-Befunde, offene Punkte
```

Schritt 6 wird **nie** übersprungen, auch nicht unter Zeitdruck. Wenn die Datenkritik ein ernstes Problem findet → **stoppen, berichten, Lösung vorschlagen**, nicht stillschweigend weiterarbeiten.

---

## 3. Datenkritik-Prüfliste (nach jedem großen Schritt)

Für jeden Punkt: *geprüft wie?* → *Befund* → *Konsequenz*. Ergebnis als `reports/data_review/<phase>_<schritt>.md`. Nicht relevante Punkte mit kurzer Begründung als „n/a“ markieren.

### 3.1 Sind die Trainingsdaten repräsentativ? (Auswahl-Bias)
- Welche Felder/Jahre/Regionen fallen durch Filter heraus (Mindestfläche, Wolken, fehlende Werte)? **Sind die Ausgeschlossenen systematisch anders?** (z. B. kleine Betriebe, Hanglagen, bestimmte Bezirke)
- **Wolken-Bias:** In trockenen Jahren gibt es weniger Wolken → mehr gültige Beobachtungen. Hängt die Anzahl gültiger Beobachtungen oder die Zielverfügbarkeit (`I_Aug` gültig?) mit dem Jahr / der Zielgröße zusammen? Wenn ja: quantifizieren.
- Ist die Verteilung der Zielgröße zwischen Trainings- und Testjahren vergleichbar? (Histogramm je Jahr)
- Sind schwere Stressfälle so selten, dass Metriken von wenigen Feldern abhängen? (Anzahl angeben)

### 3.2 Sind die Daten korrekt? (Messfehler, falsche Labels)
- **Wertebereiche:** Indizes in [−1, 1], Reflexionen plausibel, Temperaturen/Niederschlag physikalisch möglich, Datumsangaben innerhalb der Saison.
- **Plausible Kurvenform:** Stichprobe von ≥ 20 Feldern visuell prüfen – sieht das aus wie Mais (Aufgang Mai, Maximum Juli/Aug, Abreife Sep)? Felder, die nicht wie Mais aussehen → falsche Kulturangabe in INVEKOS? Anteil schätzen.
- **Frühe Ernte:** Wird ein Feld vor/während August geerntet (abrupter Abfall auf Boden-Niveau), ist ein niedriges `I_Aug` **kein Stress**, sondern Ernte/Silomais-Verwechslung. Erkennen und markieren.
- **Sensorwechsel:** Sentinel-2A/2B/2C und die L2A-Prozessierungsänderung ab 2022 (Offset) – sind Indexwerte über die Jahre konsistent? (Mittel je Jahr auf stabilen Referenzflächen vergleichen)
- **Wolkenmaske:** übersehene Dunst-/Schattenpixel? Ausreißer-Dekaden (plötzlicher Einbruch und sofortige Erholung) zählen und prüfen.
- **Auflösungs-Mismatch:** ERA5-Land (~9 km), SoilGrids (250 m) beschreiben nicht das einzelne Feld. Nie so interpretieren, als ob.
- **Feld-Matching über Jahre:** Stichprobe der IoU-Zuordnungen visuell prüfen.
- **Regionalstatistiken:** revidierte Werte, Lücken, Einheiten (t/ha vs. dt/ha), Harmonisierungsartefakte.

### 3.3 Sagen die Features wirklich etwas aus? (Scheinzusammenhänge)
- **Jahres-Proxy:** Lernt das Modell nur „welches Jahr ist das“ (z. B. über kumulierte GDD) statt Feldzustand? → zusätzlich Leistung **innerhalb eines Jahres** (Rangkorrelation zwischen Feldern) berichten.
- **Orts-Proxy / Auswendiglernen:** Koordinaten, Gemeinde-IDs, Feld-IDs können Felder wiedererkennen lassen. Mit und ohne diese Features vergleichen.
- **Label-Shuffle-Test:** Ziel zufällig permutieren → Modell muss auf Baseline-Niveau fallen. Tut es das nicht, ist irgendwo Leakage.
- **Adversarial Validation:** Kann ein Klassifikator Trainings- von Testdaten unterscheiden? Welche Features verraten das?
- Features mit nahezu null Varianz oder fast perfekter Korrelation zu anderen identifizieren; SHAP bei korrelierten Features vorsichtig interpretieren.
- **Konfundierung:** Bewässerung, Sorte, Saattermin, Düngung, Bodenbearbeitung sind unbekannt und können Effekte erklären, die das Modell z. B. dem Boden zuschreibt. In der Interpretation benennen.

### 3.4 Leakage (Zukunftswissen / Testwissen)
- Nutzt irgendein Feature Daten nach dem Stichtag? (`test_no_leakage.py` muss das abdecken)
- Werden Normalwerte (`I_normal`, YAS-Erwartung), Skalierungen, Imputationen oder Schwellen **ohne** das Testjahr berechnet?
- Hyperparameter nur in den Trainingsjahren getunt (verschachtelt)?
- Räumliche Nähe: Liegen Trainings- und Testfelder im selben Jahr direkt nebeneinander? (räumlicher Block-Split als Gegenprobe)

### 3.5 Ergebnis-Plausibilität
- Schlägt das Modell die Baselines B0/B1? Wenn nicht: warum?
- Ist ein Ergebnis **zu gut**? (z. B. R² > 0,9 bei Wochen Vorlaufzeit) → erst Leakage ausschließen, dann glauben.
- Konfidenzintervalle (Bootstrap) statt Einzelzahlen. Bei kleinen n (z. B. Region-Jahre) n explizit angeben.
- Fallstudien: 3 beste und 3 schlechteste Vorhersagen ansehen – verstehen, nicht nur zählen.

### 3.6 Entscheidung
Am Ende jeder Prüfung eine von drei Entscheidungen festhalten:
- ✅ **Weiter** – keine relevanten Probleme.
- ⚠️ **Weiter mit Einschränkung** – Problem dokumentiert, in Doku als Grenze aufnehmen.
- ⛔ **Stopp** – Problem verfälscht Ergebnisse; Projektinhaber informieren, Lösung vorschlagen, erst nach Klärung fortfahren.

---

## 4. Versionierung & GitHub

### 4.1 Repository
- GitHub-Repository: **privat**, bis der Projektinhaber ausdrücklich etwas anderes sagt (öffentlich machen nur auf seine Anweisung).
- Standard-Branch: `main` – enthält immer einen lauffähigen, getesteten Stand.

### 4.2 Branches
- Pro Phase ein Branch: `phase-<n>-<kurzname>` (z. B. `phase-2-field-pipeline`).
- Nach **jedem großen Schritt**: Commit(s) auf dem Phasen-Branch **und Push** (`git push -u origin <branch>`).
- Phasenabschluss (Abnahmekriterium erfüllt, Tests grün, Datenkritik ✅/⚠️): Merge nach `main` mit `--no-ff`, Tag setzen, `main` + Tag pushen.

### 4.3 Commits
- Klein und thematisch; Format **Conventional Commits**:
  `feat:` neue Funktion · `fix:` Fehlerbehebung · `data:` Datenpipeline/-schema · `exp:` Experiment/Ergebnis · `test:` · `docs:` · `refactor:` · `chore:`
- Betreff ≤ 72 Zeichen, im Body **was** und **warum**; bei Experimenten die Kernzahlen.
- KI-unterstützte Commits enden mit der Zeile
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (Transparenz, passt zu `SUPPORT.md`).
- Vor jedem Commit: `pytest` grün, keine Daten/Secrets im Diff (`git status` + `git diff --stat` prüfen).

### 4.4 Tags & Versionen (SemVer pro Phase)
| Tag | Bedeutung |
|---|---|
| `v0.1.0` | Phase 0 – Setup & Datenzugang |
| `v0.2.0` | Phase 1 – V0 Regionalmodell CY-Bench |
| `v0.3.0` | Phase 2 – Feld-Pipeline |
| `v0.4.0` | Phase 3 – Ziele & EDA |
| `v0.5.0` | Phase 4 – V1 Feldmodell |
| `v0.6.0` | Phase 5 – V2 Ablation/Radar/Unsicherheit |
| `v0.7.0` | Phase 6 – V3 Ertragsbrücke & Transfer |
| `v0.8.0` | Phase 7 – Demo |
| `v1.0.0` | Phase 8 – Abgabe |

Korrekturen innerhalb einer Phase nach dem Tag: Patch-Version (`v0.3.1`). Jeder Tag hat einen Eintrag in `CHANGELOG.md`.

### 4.5 Was niemals ins Repository kommt
- Rohdaten, große Zwischendateien, Modelle > 50 MB (`data/`, `results/**/models/` sind in `.gitignore`).
- Zugangsdaten, Tokens, `.env`, GEE-Credentials, Service-Account-Keys.
- Ausnahme: kleine Test-Fixtures (< 1 MB) unter `tests/fixtures/`.
- Stattdessen: `DATA_SOURCES.md` beschreibt exakt, woher jede Datei kommt und wie sie neu erzeugt wird.

---

## 5. Tests

- Framework: `pytest`; Tests unter `tests/`; laufen ohne Internet und ohne GEE (kleine Fixtures).
- **Pflicht-Tests** (sobald der jeweilige Code existiert):
  - `test_no_leakage.py` – Feature-Builder liefert für Stichtag *t* keine Werte mit Zeitstempel > *t*; Normalwerte enthalten nie das Testjahr.
  - `test_targets.py` – `I_Aug`, `I_normal`, `VAS`, `YAS` an Handbeispielen.
  - `test_field_matching.py` – IoU-Zuordnung an konstruierten Geometrien.
  - `test_schemas.py` – Spalten, Datentypen, Wertebereiche der Parquet-Dateien (Indizes in [−1,1], Datumsbereiche, keine doppelten Schlüssel).
  - `test_splits.py` – LOYO: kein Jahr gleichzeitig in Train und Test.
- Neue Logik mit Verzweigungen oder Rechenformeln → Test dazu. Reine Plot-Skripte brauchen keinen Test.
- Bugfix → zuerst Test, der den Fehler zeigt, dann Fix.
- Ab Phase 0: GitHub Actions führt `pytest` bei jedem Push aus.

---

## 6. Experimente & Ergebnisse

- Jeder Lauf schreibt nach `results/<YYYY-MM-DD>_<name>/`: verwendete `config.yaml`, Git-Commit-Hash, Metriken als `metrics.json`, Abbildungen.
- Zusammenfassung jedes relevanten Laufs als Zeile in `reports/results.md` (Datum, Commit, Experiment, Kernmetriken mit KI, Kommentar).
- Seeds fixiert; Ergebnisse müssen mit demselben Commit reproduzierbar sein.
- Metriken laut `PLAN.md` (RMSE, MAE, R², Skill vs. B0, PR-AUC, Recall bei 20 % FPR) – keine „Accuracy“ für unbalancierte Probleme.

---

## 7. Dokumentationsdateien (immer aktuell halten)

| Datei | Inhalt |
|---|---|
| `PLAN.md` | Was gemacht wird (nur auf Anweisung ändern) |
| `AGENTS.md` | Wie gearbeitet wird (diese Datei) |
| `CHANGELOG.md` | Was sich je Version geändert hat |
| `DECISIONS.md` | Jede Abweichung/Festlegung mit Datum, Grund, Alternativen |
| `DATA_SOURCES.md` | Quelle, Version, Lizenz, Abrufdatum, Download-/Erzeugungsschritte je Datensatz |
| `SUPPORT.md` | Jede Unterstützung (Personen, KI-Tools, Datensätze, Code Dritter) – BWKI-Pflicht |
| `reports/data_review/` | Datenkritik-Berichte (§3) |
| `reports/results.md` | Ergebnisübersicht |

---

## 8. Wann der Agent stoppen und fragen muss

- Datenkritik ergibt ⛔.
- Eine Änderung würde eine Forschungsfrage, Zielvariable, Region, Stichtage oder den Validierungsansatz aus `PLAN.md` ändern.
- Konten anlegen, Logins, Lizenzzustimmungen, kostenpflichtige Dienste → macht der Projektinhaber selbst.
- Repository öffentlich machen, Daten löschen, History umschreiben (`push --force`, `reset --hard` auf gepushte Commits).
- Ein Ergebnis wirkt zu gut, um wahr zu sein, und die Ursache ist nach §3.4 nicht geklärt.

---

## 9. Code-Stil

- Python 3.11, Pakete in `requirements.txt` mit fixierten Versionen.
- Module unter `src/croptransfer/`, Notebooks nur für Exploration/Abbildungen – Logik gehört in Module.
- Konfiguration ausschließlich über `config.yaml`; Pfade relativ zum Repo-Root.
- Docstrings und Kommentare englisch, kurz; Doku (`reports/doku/`) deutsch.
- Typ-Hinweise für öffentliche Funktionen.
