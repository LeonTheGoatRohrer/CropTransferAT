/**
 * Static project copy (German). Every number here is taken from the project's
 * curated result register app/versions.yaml / reports/results.md and points to
 * its source file. Live charts read the same numbers from evidence.json.
 */
import type { Strength } from '../../components/ui/Badge'

export const PROJECT = {
  name: 'CropTransfer AT',
  competition: 'Bundeswettbewerb Künstliche Intelligenz (BWKI) Österreich',
  question:
    'Können Satelliten-Zeitreihen, Wetter und Boden Stress und Ertragsverlust in einzelnen Maisfeldern noch vor der Ernte zeigen – gelernt dort, wo Erträge gemessen wurden, und dann unverändert in Österreich getestet?',
  fieldYears: 365,
  sites: 'KBS (Michigan), BARC (Maryland), Akron (Colorado)',
}

/* ------------------------------------------------------------------ */
/* Data sources                                                        */
/* ------------------------------------------------------------------ */

export type DataSource = {
  name: string
  provider: string
  role: string
  detail: string
  scale: string
  license: string
  group: 'yield' | 'satellite' | 'weather' | 'soil' | 'regional' | 'austria'
}

export const DATA_SOURCES: DataSource[] = [
  { group: 'yield', name: 'KBS LTER', provider: 'Kellogg Biological Station, Michigan', role: 'Gemessene Parzellenerträge (Labels)', detail: '294 Mais-Parzellen-Jahre inkl. Bio- und Zwischenfrucht-Varianten T1–T4', scale: '≈ 0,6-ha-Parzellen', license: 'Nutzung nur mit schriftlicher Erlaubnis' },
  { group: 'yield', name: 'BARC Gridded Yield Archive', provider: 'USDA-ARS Beltsville, Maryland', role: 'Mähdrescher-Ertragskarten (Labels, innerhalb des Felds)', detail: '61 Mais-Feld-Jahre, auf 10-m-Blöcke gekrigt', scale: 'Felder mit 2–14 ha', license: 'U.S. Public Domain' },
  { group: 'yield', name: 'Akron Dryland', provider: 'USDA-ARS, Colorado', role: 'Beprobte Ertragspunkte', detail: '10 Mais-Teilfeld-Jahre, 2019–2022', scale: 'Punkte', license: 'CC0' },
  { group: 'yield', name: 'Kayad-Maisfeld', provider: 'Kayad et al. 2019, Poebene, Italien', role: 'Zweiter Standort für Teilflächen', detail: '3 Feld-Jahre mit rohen Mähdrescherpunkten', scale: 'Feld mit 22 ha', license: 'CC BY 4.0' },
  { group: 'satellite', name: 'Sentinel-2 L2A', provider: 'ESA / Copernicus über Google Earth Engine', role: 'Vegetationsindizes je 10-Tage-Dekade', detail: 'NDVI, EVI, NDMI, NDRE, GNDVI · Maskierung mit Cloud Score+', scale: '10 m · seit 2017', license: 'Copernicus-Open-Lizenz' },
  { group: 'satellite', name: 'HLS v2', provider: 'NASA (Landsat 8/9 + Sentinel-2 harmonisiert)', role: 'Längere Indexreihe für kleine Parzellen', detail: 'Genutzt ab 2013; Landsat 5/7 hat die Harmonisierungsprüfung nicht bestanden', scale: '30 m', license: 'NASA Open Data' },
  { group: 'weather', name: 'ERA5-Land', provider: 'ECMWF / Copernicus', role: 'Tägliche Temperatur, Regen, Bodenfeuchte', detail: 'GDD (10/30 °C), Hitzetage, Wasserbilanz, VPD', scale: '≈ 9-km-Raster', license: 'Copernicus-Lizenz' },
  { group: 'soil', name: 'SoilGrids 2.0 + Copernicus DEM', provider: 'ISRIC · ESA', role: 'Bodenart, Kohlenstoff, Wasserspeicher, Gelände', detail: 'Ton, Sand, SOC, nFK (AWC), pH; Höhe, Hangneigung, TPI, TWI', scale: '250 m · 30 m', license: 'CC BY 4.0' },
  { group: 'soil', name: 'SSURGO', provider: 'USDA NRCS', role: 'US-Ertragsfähigkeitsindex (Kontrolle)', detail: 'NCCPI Mais', scale: 'Karteneinheiten', license: 'U.S. Public Domain' },
  { group: 'regional', name: 'CY-Bench v1.10', provider: 'Kallenberg et al.', role: 'Regionale Maiserträge in der EU + Prädiktoren', detail: '16 Länder, 8 371 Region-Jahre, ohne Österreich', scale: 'NUTS-2/3-Regionen', license: 'EUPL-1.2' },
  { group: 'austria', name: 'INVEKOS-Feldstücke, Statistik Austria, Versuche Hatzendorf', provider: 'AMA · Statistik Austria · Land Steiermark', role: 'Österreichische Testdaten – bis zum Freeze zurückgehalten', detail: 'Nie für Training, Merkmale, Schwellen oder Modellwahl genutzt. Nach freeze-at-1 einmal für den explorativen Test geöffnet.', scale: 'Feldstücke · Bundesländer · Versuchsstandorte', license: 'CC BY 4.0 / öffentlich' },
]

/* ------------------------------------------------------------------ */
/* Pipeline                                                            */
/* ------------------------------------------------------------------ */

export const PIPELINE_STEPS = [
  { key: 'field', title: 'Feld', body: 'Ein Feldumriss und eine Saison. Trainingsfelder haben einen gemessenen Ertrag.', meta: 'Umriss · Jahr' },
  { key: 'pixels', title: 'Satellitenpixel', body: 'Jede Sentinel-2-Szene der Saison. Szenen mit weniger als 70 % wolkenfreien Pixeln fallen weg.', meta: '≈ 35–45 Szenen' },
  { key: 'dekads', title: '10-Tage-Komposite', body: 'Median-Index je 10-Tage-Dekade ab 1. April. Fehlende Dekaden bleiben fehlend – keine Interpolation.', meta: '21 Dekaden' },
  { key: 'reference', title: 'Gesunde Referenz', body: 'Die Mediankurve gesunder Trainings-Feld-Jahre (≥ 95 % ihres üblichen Ertrags).', meta: '77 Feld-Jahre (HLS)' },
  { key: 'fusion', title: 'Wetter und Boden', body: 'Tageswetter aus ERA5-Land, SoilGrids und Gelände, zusammengefasst mit einer Stichtagsregel: nichts nach dem Prognosestichtag.', meta: '≈ 9 km · 250 m' },
  { key: 'model', title: 'Scores und Modelle', body: 'Stress-Score (Rückstand gegenüber der Referenz), Risikomodell, Teilflächenkarte und EU-Regionalmodell.', meta: 'vorab festgelegt' },
  { key: 'insight', title: 'Aussage auf Feldebene', body: 'Welcher Teil des Felds zurückfällt, ob das Feld ungewöhnlich ist und wie das Jahr der Region abschneidet.', meta: 'Karte · Alarm · Rang' },
]

export const FEATURE_GROUPS = [
  { title: 'Vegetationsindizes', items: ['NDVI, EVI, NDMI, NDRE, GNDVI je Dekade', 'Spitzenwert und Datum des Spitzenwerts', 'Saisonintegral (EVI-Fläche)'], source: 'Sentinel-2 / HLS' },
  { title: 'Relativ zur Referenz', items: ['Rückstand gegenüber der gesunden Referenz (Stress-Score)', 'Abweichung je Phase: Juni, Juli, August', 'Relativ zum selben Feld in anderen Jahren'], source: 'src/croptransfer/stress.py' },
  { title: 'Fenster innerhalb des Felds', items: ['Median-NDVI vom 10. Jul bis 18. Aug je 10-m-Zelle (Regel B0)', 'NDVI/NDRE-Fenster w1–w3 um den Spitzenwert (Modell M1)', 'z-standardisiert innerhalb jedes Feld-Jahrs'], source: 'innerfeld_features.py' },
  { title: 'Wettersummen', items: ['Wachstumsgradtage (10/30 °C)', 'Regen, 30-Tage-Regen, klimatische Wasserbilanz', 'Hitzetage > 32 °C während der Blüte', 'VPD und Höchsttemperatur im Juni'], source: 'features.daily_weather' },
  { title: 'Boden und Gelände', items: ['Ton, Sand, organischer Kohlenstoff, pH', 'Nutzbare Feldkapazität', 'Höhe, Hangneigung, TPI, Feuchteindex'], source: 'SoilGrids, Copernicus DEM' },
  { title: 'Bewusst ausgeschlossen', items: ['Koordinaten, Feld- oder Regions-IDs, Jahr', 'Alles, was nach dem Prognosestichtag beobachtet wurde', 'Jeder österreichische Wert vor dem Freeze'], source: 'tests/test_no_leakage.py' },
]

/* ------------------------------------------------------------------ */
/* Experiments (chronological)                                         */
/* ------------------------------------------------------------------ */

export type Experiment = {
  id: string
  date: string
  phase: string
  title: string
  changed: string
  result: string
  numbers: { label: string; value: string }[]
  status: Strength
  source: string
}

export const EXPERIMENTS: Experiment[] = [
  { id: 'v0.1.0', date: '2026-10-15', phase: 'Phase 0', title: 'Datenzugang und Regeln', changed: '13 Datenquellen gesichtet; Arbeitsregeln festgelegt, bevor irgendein Modell lief.', result: 'Die Österreich-Regel: Österreichische Daten bleiben verschlossen, bis ein Modell eingefroren ist.', numbers: [{ label: 'Quellen', value: '13' }, { label: 'Datenanfragen', value: '7' }], status: 'done', source: 'reports/data_review/phase0_data_access.md' },
  { id: 'v0.2.0', date: '2026-10-16', phase: 'Phase 1', title: 'Ground Truth zusammengestellt', changed: 'Alle Erträge in einem Schema (t/ha bei 15,5 % Feuchte), verknüpft mit Kurven, Wetter und Boden.', result: 'Ein erstes Signal ist da, aber nur auf sehr wenigen unabhängigen Standort-Jahren. Landsat 5/7 hat die Harmonisierungsprüfung nicht bestanden.', numbers: [{ label: 'Feld-Jahre', value: '365' }, { label: 'EVI-Integral vs. relativer Ertrag', value: 'ρ 0,44 [0,10; 0,75]' }], status: 'limited', source: 'results/2026-10-16_phase1/metrics.json' },
  { id: 'v0.3.0', date: '2026-10-16', phase: 'Phase 2', title: 'Basismodelle: Satellit, Wetter, Boden', changed: 'Modellfamilie je Merkmalsgruppe trainiert, geprüft an unbekanntem Feld und unbekanntem Jahr.', result: 'Unterschiede von Jahr zu Jahr lassen sich nicht auf unbekannte Jahre übertragen. Innerhalb eines Felds findet der Satellit die schwachen Zonen.', numbers: [{ label: 'Unbekanntes Feld + Jahr', value: 'ρ −0,04 [−0,29; 0,37]' }, { label: 'Innerhalb des Felds', value: 'ρ 0,68 [0,54; 0,72]' }], status: 'limited', source: 'results/2026-10-16_phase2/criteria_main.json' },
  { id: 'rounds', date: '2026-10-16', phase: 'Phase 4', title: 'Drei vorab festgelegte Verbesserungsrunden', changed: 'Relative Merkmale, weniger Merkmale, stärkere Regularisierung – vor dem Lauf schriftlich festgelegt.', result: 'Relative Merkmale helfen, aber keine Runde schlägt beim Fehler die „Normaljahr“-Baseline.', numbers: [{ label: 'Runde 1', value: 'ρ 0,37' }, { label: 'Runde 2', value: 'ρ −0,01' }, { label: 'Runde 3', value: 'ρ 0,37' }], status: 'failed', source: 'results/2026-10-16_round{1,2,3}/criteria.json' },
  { id: 'v0.4.0', date: '2026-10-16', phase: 'Phase 3 + 4', title: 'Problemfelder und das Urteil „stark genug?“', changed: 'Gefährdete Felder (≥ 15 % unter üblich) mit einem Stress-Score aus der Referenzkurve erkannt.', result: 'Die einfachste Methode gewinnt. Das vorab festgelegte Kriterium wird verfehlt, daher wurde das Feldmodell nicht eingefroren.', numbers: [{ label: 'Stress-Score PR-AUC', value: '0,71 (Zufall 0,33)' }, { label: 'Gelerntes Modell PR-AUC', value: '0,40' }], status: 'failed', source: 'results/2026-10-16_round3/phase3.json' },
  { id: 'freeze-cybench-1', date: '2026-10-16', phase: 'Phase 5', title: 'EU-Regionalmodell eingefroren', changed: 'Unabhängige Prüfung: LightGBM auf 16 EU-Ländern, ohne Österreich, Dateien mit Prüfsummen eingefroren.', result: 'Ein kleines, aber statistisch sicheres Signal dafür, welche Jahre schlechter ausfallen.', numbers: [{ label: 'Spearman ρ, 1. Sep', value: '0,38 [0,36; 0,40]' }, { label: 'Skill ggü. Normaljahr', value: '0,07' }], status: 'certain-small', source: 'results/2026-10-16_cybench_eu/metrics.json' },
  { id: 'side', date: '2026-10-16', phase: 'Nebenanalysen', title: 'Absoluter Ertrag, Zeitachse, afrikanische Felder', changed: 'Drei Nebenfragen mit der bestehenden Pipeline beantwortet.', result: 'Der Satellit sieht das Ertragsniveau eines Felds, aber nicht, ob dieses Jahr besser als üblich ist.', numbers: [{ label: 'Absoluter Ertrag (t/ha)', value: 'ρ 0,52 [0,22; 0,76]' }, { label: 'One Acre Fund R²', value: '0,05–0,07' }], status: 'limited', source: 'results/2026-10-16_phase2_Y/metrics.csv' },
  { id: 'multicrop', date: '2026-10-16', phase: 'Datenerweiterung', title: 'Training mit Mais, Weizen und Erbsen', changed: 'Vier offene Datensätze ergänzt; Modelle auf allen Kulturen und je Kultur trainiert.', result: 'Kein Signal über den Mittelwert hinaus; Wissen aus Weizen und Erbsen überträgt sich nicht auf Mais.', numbers: [{ label: 'Übertragung auf Mais', value: 'ρ 0,01 [−0,26; 0,32]' }], status: 'failed', source: 'results/2026-10-16_mehrkultur_h030/criteria.json' },
  { id: 'finetune', date: '2026-10-16', phase: 'Feinjustierung', title: 'Radar, Oberflächentemperatur, GDD-Achse, Ergrünungsdatum', changed: 'Jede Quelle einzeln ergänzt, nach einer vorab festgelegten Behalte-Regel.', result: 'Alle vier haben die Erkennung verschlechtert. Die Fallprüfung zeigte: Der Score markiert spät gesäte Bio-Parzellen.', numbers: [{ label: 'Radar', value: 'ΔPR-AUC −0,14' }, { label: 'Temperatur + ET', value: '−0,22' }], status: 'failed', source: 'results/2026-10-16_feinjust_ablation/metrics.csv' },
  { id: 'innerfeld', date: '2026-10-17', phase: 'Innerhalb des Felds', title: 'Die Teilflächenkarte an drei Standorten', changed: 'Karte in Italien und Colorado geprüft; trainiertes Modell M1 mit der einfachen NDVI-Regel verglichen.', result: 'An allen drei Standorten dieselbe Richtung (49 von 50 Feld-Jahren positiv); belastbar nur für BARC.', numbers: [{ label: 'BARC einfache Regel', value: 'ρ 0,67 [0,59; 0,74]' }, { label: 'Kayad · Colorado', value: '0,60 · 0,63' }], status: 'robust', source: 'results/2026-10-17_innerfeld/metrics.json' },
  { id: 'ceiling', date: '2026-10-17', phase: 'Innerhalb des Felds', title: 'Wie viel ist noch drin?', changed: 'Obergrenze geschätzt, die durch das Rauschen der Mähdrescher-Ertragskarte selbst entsteht.', result: 'Bei Kayad erreicht die Karte 0,60 bei einer Obergrenze von 0,72–0,94: etwas Luft, vermutlich wenige Hundertstel.', numbers: [{ label: 'Obergrenze Kayad', value: '0,72–0,94' }], status: 'limited', source: 'results/2026-10-17_innerfeld_ceiling/metrics.json' },
  { id: 'smoothing', date: '2026-10-17', phase: 'Innerhalb des Felds', title: 'Glätten hilft nicht', changed: '30-m-Glättung der Vorhersage unter vorab festgelegten Kriterien getestet.', result: 'Kein Gewinn; die Karte bleibt bei 10-m-Zellen. Frühere Gewinne durch Blockmittel kamen von der Messseite.', numbers: [{ label: 'BARC Δρ', value: '−0,013 [−0,017; 0,001]' }], status: 'failed', source: 'results/2026-10-17_innerfeld_runde2/metrics.json' },
  { id: 'freeze-at-1', date: '2026-10-17', phase: 'Phase 7', title: 'Österreich-Test eingefroren', changed: 'Stress-Score und EU-Modell nebeneinander eingefroren, Testregeln geschrieben, bevor ein österreichischer Wert geöffnet wurde.', result: 'Explorativer erster Test – auf österreichischen Daten wird kein Sieger gewählt.', numbers: [{ label: 'Tag', value: 'freeze-at-1' }], status: 'frozen', source: 'reports/freeze_protocol_at.md' },
  { id: 'at-test-1', date: '2026-10-17', phase: 'Phase 7', title: 'Erstes Ergebnis aus Österreich', changed: 'Das eingefrorene Protokoll lief einmal auf oberösterreichischen Sortenversuchen und auf der Bundesländer-Statistik.', result: 'Gute und schlechte Jahre werden richtig gereiht, aber der Score ist nicht besser als einfacher NDVI und trennt Standorte innerhalb eines Jahres nicht. Für die Steiermark gab es keine passenden Versuche.', numbers: [{ label: 'Stress-Score, Oberösterreich', value: 'ρ 0,50 [0,19; 0,68]' }, { label: 'EU-Modell, Bundesländer', value: 'ρ 0,52 [0,13; 0,75]' }], status: 'limited', source: 'results/2026-10-17_at_test/metrics.json' },
]

/* ------------------------------------------------------------------ */
/* Limitations and roadmap                                             */
/* ------------------------------------------------------------------ */

export const LIMITATIONS = [
  { title: 'Wenige unabhängige Saisonen', body: 'Die Felddaten umfassen nur 8–11 unabhängige Standort-Jahre. Das ist zu wenig, um zu lernen, wie sich ein Jahr vom anderen unterscheidet – deshalb hat das Feldmodell sein vorab festgelegtes Kriterium verfehlt.', next: 'Mehr Standort-Jahre: Datenanfragen an YIPEEO, DWFI, SwissYield, Mead und YieldSAT sind vorbereitet.' },
  { title: 'Nur ein belastbarer Standort für Teilflächen', body: 'Die Teilflächenkarte ist nur für BARC (41 Feld-Jahre) belastbar. Italien und Colorado zeigen in dieselbe Richtung, sind aber zu klein, um die Übertragbarkeit zu beurteilen.', next: 'Mit neuen Mähdrescher-Ertragskarten prüfen, sobald sie eintreffen.' },
  { title: 'Ein Alarm heißt „ungewöhnliche Kurve“', body: 'Der Stress-Score markiert die KBS-Bio-Parzellen jedes Jahr, auch 2020, als sie normal erbrachten – späte Saat nach einer Zwischenfrucht sieht aus wie Stress.', next: 'Saattermine ergänzen, wo bekannt; Alarme als „Kurve unter Referenz“ melden, nicht als Diagnose.' },
  { title: 'Österreich nur grob getestet', body: 'Der erste, explorative Test reiht Jahre in Oberösterreich (ρ 0,50), aber keine Standorte innerhalb eines Jahres, ist nicht besser als einfacher NDVI und hat keine steirischen Versuche. Auf Feldebene wurde in Österreich noch nichts getestet.', next: 'Österreichische Felderträge für einen Test auf Feldebene (V3); genaue Versuchskoordinaten für die Steiermark.' },
  { title: 'Grobe Umweltdaten', body: 'ERA5-Land (≈ 9 km) und SoilGrids (250 m) beschreiben die Umgebung, nicht das einzelne Feld. Sie werden nie als feldgenau interpretiert.', next: 'Für die Österreich-Prüfung nationale Bodenkarten (Bodenklimazahl) nutzen.' },
  { title: 'Wolken und Lücken', body: 'Im Hochsommer gibt es oft nur 1–3 wolkenfreie Sentinel-2-Szenen pro Dekade. Lücken bleiben Lücken; der Score nutzt nur beobachtete Dekaden.', next: 'Radar wurde getestet und hat nicht geholfen; vorerst nur optische Daten.' },
]

export const ROADMAP: { stage: 'Done' | 'Now' | 'Next' | 'Later'; title: string; body: string }[] = [
  { stage: 'Done', title: 'Ground Truth auf Feldebene (USA)', body: '365 Mais-Feld-Jahre mit Kurven, Wetter und Boden in einem Schema.' },
  { stage: 'Done', title: 'Karte schwacher Zonen im Feld', body: 'Median ρ 0,68 gegenüber gemessenen Ertragskarten, robust bei BARC.' },
  { stage: 'Done', title: 'EU-Regionalmodell eingefroren', body: 'LightGBM, 16 Länder, mit Prüfsummen (freeze-cybench-1).' },
  { stage: 'Done', title: 'Stress-Score mit Alarmschwelle', body: 'Höchstens 20 % Fehlalarme bei nicht gefährdeten Feldern (konforme Schwelle).' },
  { stage: 'Done', title: 'Erster Österreich-Test', body: 'Explorativ, freeze-at-1: Jahre werden gereiht (ρ ≈ 0,5), Felder noch nicht testbar.' },
  { stage: 'Next', title: 'Österreichische Felderträge', body: 'Erträge auf Feldebene und Versuchskoordinaten für einen Test auf Feldebene (V3).' },
  { stage: 'Next', title: 'Mehr gemessene Saisonen', body: 'Datenanfragen für Feld-Ertragskarten in Europa und den USA.' },
  { stage: 'Next', title: 'Analyse-Backend', body: 'Sentinel-2- und ERA5-Abruf auf Anfrage für jedes eingezeichnete Feld.' },
  { stage: 'Later', title: 'Mehr Kulturen, laufendes Monitoring', body: 'Erst wenn die Mais-Karte außerhalb von BARC bestätigt ist.' },
]
