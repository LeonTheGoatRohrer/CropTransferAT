Entwurf (Nachtlauf 16.10.2026) – vom Projektinhaber zu prüfen und in eigenen Worten zu überarbeiten

# 1 Motivation, Relevanz und Idee

## 1.1 Das Problem

Körnermais ist in Österreich eine wichtige Ackerkultur, in der Steiermark besonders (Steiermark: rund 34 000 bis 39 000 als Körnermais gemeldete Schläge pro Jahr, 2018–2025; `DATA_SOURCES.md` §14). Wie viel geerntet wird, hängt stark vom Wetter ab: In der Steiermark gibt es kaum Bewässerung, dafür **Hagel und Trockenstress** (`DECISIONS.md`, 2026-10-15). Ob ein Feld in einem Jahr Probleme hat, sieht man oft erst bei der Ernte.

Die amtliche Statistik hilft dabei wenig:

- Die Erträge werden nur **je Bundesland** veröffentlicht. Bezirkswerte gibt es nur als Sonderauswertung auf Anfrage und sind geschätzt (`DATA_SOURCES.md` §8). Ein trockenes Tal neben einem gut versorgten Nachbartal verschwimmt in einem Landesmittel.
- Sie liegt erst nach der Ernte vor. Für Entscheidungen *während* der Saison ist sie zu spät.
- Es gibt **keine öffentlich zugänglichen Ertragsdaten einzelner Felder** in Österreich (`DECISIONS.md`, 2026-10-15). Ein Modell direkt auf österreichischen Feldern zu lernen ist deshalb nicht möglich.

## 1.2 Wem es nützen könnte

(Allgemeine Aussagen nach PLAN.md Phase 10; **[Belege und Beispiele ergänzen, z. B. Gespräche mit Betroffenen]**)

| Gruppe | Mögliche Frage |
|---|---|
| Landwirt:innen | Welche meiner Felder sind in diesem Jahr gefährdet, und seit wann? |
| Landwirtschaftskammer | Wo sollten Beratung und Erhebungen ansetzen? |
| Versicherung | Welche Felder sind von Schäden betroffen (z. B. Hagel, Trockenheit)? |
| AMA (INVEKOS) | Die AMA veröffentlicht die Feldgrenzen (CC BY 4.0), die wir als Testfelder nutzen würden |
| Ministerium | Frühe Einschätzung der Ernte |

Wichtig für die ehrliche Einordnung: Das Projekt zeigt eine Methode und prüft, wie weit sie trägt. Es ist **kein einsatzreifes Frühwarnsystem** (siehe Kapitel 3 bis 6).

## 1.3 Die Idee in einfachen Worten

1. **Ein Maisfeld sieht man vom Satelliten als Kurve über die Saison** (z. B. der Grünindex NDVI). Gesunder Mais wird früh dicht und grün. Bei Stress bleibt die Kurve flach oder fällt früh ab.
2. **Zusammen mit Wetter und Boden** soll daraus der Ertrag des Feldes abgeschätzt werden.
3. **Lernen kann man das nur dort, wo der Ertrag pro Feld gemessen wurde.** Solche offenen Daten gibt es für Felder in den USA (mit vielen Jahren je Feld: Kellogg Biological Station KBS, USDA Beltsville BARC, Colorado), dazu viele Felder in Afrika (One Acre Fund) und Südamerika (YieldSAT; Zugang noch nicht vorhanden).
4. **Dann wird das Modell „eingefroren“.** Modelle, Merkmale, Schwellen und das Testprotokoll werden festgehalten (Prüfsummen), bevor irgendein österreichisches Feld angesehen wird.
5. **Österreich ist der Beweis, nicht das Training.** Das eingefrorene Modell wird ohne jede Anpassung auf steirische INVEKOS-Felder angewendet und gegen österreichische Erträge geprüft. Keine österreichische Satelliten- oder Ertragszahl fließt vorher in Training, Merkmalsauswahl oder Schwellen ein („Österreich-Regel“, PLAN.md §0).
6. **Unabhängige Gegenprobe:** Ein Regionalmodell aus CY-Bench-Daten (andere EU-Länder) wird nach demselben Prinzip eingefroren und später auf Österreich getestet (Kapitel 5).

Das ist ein *Transfer-Test*: Gilt, was auf einem Kontinent gelernt wurde, auch in einem anderen Klima? Ein vorab eingefrorenes Modell ist dafür die ehrlichste Prüfung, weil man danach nicht mehr „nachbessern“ kann (`DECISIONS.md`, 2026-10-15).

## 1.4 Forschungsfragen (PLAN.md §1)

| ID | Frage | Stand (16.10.2026) |
|---|---|---|
| F0 | Wie gut sagen Satellit, Wetter und Boden den gemessenen Feldertrag voraus, und ab wann in der Saison? | beantwortet: für ungesehene Jahre nicht verlässlich (Kapitel 3) |
| F1 | Welche Faktoren bestimmen den Ertrag (zwischen Jahren, zwischen Feldern, innerhalb eines Feldes)? | beantwortet: innerhalb des Feldes stark, zwischen Jahren nicht lernbar (Kapitel 3) |
| F2 | Wie früh und zuverlässig erkennt man gefährdete Felder und Problemzonen und deren wahrscheinliche Ursache? | beantwortet, schwach bis mäßig; Modell nicht „stark genug“ (Kapitel 4) |
| F3 | **Beweis:** Funktioniert das eingefrorene US-Modell in Österreich? | **nicht getestet**, da kein Freeze (Kapitel 7: Platzhalter) |
| F4 | Gegenprobe: regionaler Transfer EU → Österreich (CY-Bench), Zero-Shot | Modell eingefroren; **Test ausstehend** (Kapitel 5) |
| F5 | Zusatz: Anpassung mit österreichischen Daten | nicht begonnen |

**Ehrliche Grenze (steht so im Plan):** „Problemfeld“ heißt *messbarer Ertragsverlust gegenüber dem eigenen Normalniveau*. Krankheiten oder Schädlinge können ohne passende Labels **nicht** von anderen Ursachen unterschieden werden. Ob der Zusammenhang Kurve → Ertrag in Österreich gilt, ist genau Frage F3 und wird nur so weit behauptet, wie die Prüfungen es stützen.

## 1.5 Stand der Forschung und Abgrenzung

**Nur Platzhalter. Hier wird nur genannt, was in den Projektdateien schon belegt ist.**

- **CY-Bench** (Kallenberg et al. 2026, *Earth System Science Data* 18, 3997–4018, doi:10.5194/essd-18-3997-2026): harmonisierter Datensatz zu Regionalerträgen und Prädiktoren (Wetter, Bodenfeuchte, Vegetationsindizes) für Europa. Wir nutzen ihn in Phase 5. Die dort veröffentlichte Referenz für Österreich-Mais (R² = 0,13, Modell Random Forest, Median über Leave-One-Year-Out, Datenversion v1.8) steht im Code-Repository von CY-Bench, nicht im Artikel (`DATA_SOURCES.md` §7).
- **Feld-Ertragsdaten:** One Acre Fund (Aramburu-Merlos et al. 2024, *Nature Communications* 15, doi:10.1038/s41467-024-48859-0), BARC-Archiv (Dulaney, Anderson, Gao et al., Ag Data Commons, doi:10.15482/USDA.ADC/28950746.v2), Colorado-Studie zum Topographic Position Index (Poss, Hardy, Macdonald et al., doi:10.15482/USDA.ADC/28914434.v1), KBS LTER (NSF DEB 2224712).
- **Harmonisierung Landsat:** Roy et al. 2016 (verwendet für die Koeffizienten ETM+ → OLI; vollständige Angabe **[Literatur ergänzen]**).
- **Boden-Wasserspeicher:** Saxton & Rawls 2006 (nutzbare Feldkapazität; vollständige Angabe **[Literatur ergänzen]**).
- **[Literatur ergänzen: JRC MARS, europäisches Ernteüberwachungssystem]**
- **[Literatur ergänzen: SCYM, Scalable Crop Yield Mapper, Ertragsschätzung aus Satelliten]**
- **[Literatur ergänzen: Studien zur Ertragsschätzung mit Mähdrescherdaten und Sentinel-2]**
- **[Literatur ergänzen: Studien mit Leave-One-Country-Out bzw. Transfer zwischen Regionen]**
- **[Abgrenzung formulieren:** Was ist neu? Vorab eingefrorenes Modell, Transfer-Test mit Prüfsummen und Protokoll, Fokus auf einzelne Felder. Erst schreiben, wenn die Literatur gelesen ist.**]**
