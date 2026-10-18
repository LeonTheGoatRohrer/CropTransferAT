# Pitch-Intro – Storyboard (≈ 59 s)

Zweck: In knapp einer Minute zeigen, **welches Problem** Delta Green löst und **was die App macht**.
Die Details (Daten, Modell, Österreich-Test, Grenzen) erklärst du danach selbst vor der Kamera.

Datei: `index.html` (im Browser öffnen, Vollbild F11, Leertaste = Start, mit OBS/Xbox Game Bar aufnehmen).

| Zeit | Szene | Bild | Text im Bild |
|---|---|---|---|
| 0–4,5 s | Aufhänger | Drohnenflug über Maisreihen (Higgsfield-Clip) | „Manche Felder bringen weniger als sonst. Aber *wo* genau – und *wann*?“ |
| 4,5–9,6 s | 01 Feld wählen | Handy mit Luftbild, Finger tippt die Ecken, Feld wird umrandet. Finale Fassung: KI-Luftbild (`?map=ai`, Standard); Alternative `?map=ortho`: echtes Orthofoto basemap.at 2024 + echter INVEKOS-Körnermaisschlag bei Feldbach | „Feld auswählen“ |
| 9,6–13,8 s | 02 Erträge | Formular „What did it yield?“, 2021–2025 werden eingetippt, Start | „Alte Erträge eintragen“ |
| 13,8–20 s | 03 Satellit | Weltall, Erdkrümmung, Satellit zieht vorbei, Strahl aufs Feld, Zoom hinein | „Der Satellit schaut zu“ |
| 20–24,8 s | Jahre | Dasselbe Feld 2019 → 2025, jedes Jahr ein neues Bild (Scan-Effekt), Mini-Bilder unten | „Jahr für Jahr ein neues Bild“ |
| 24,8–31,3 s | 04 Punkte | Feld zerfällt in 10-m-Pixel, Farbskala, Markierungen auf schwachen Zonen. Neu: Zähler „Auffällige Pixel erkannt: 13 %“ (aus dem Pixelraster berechnet) | „Schwache Stellen markiert“ |
| 31,6–38,1 s | **05 Maßstab** (neu) | Balken Erträge 2021–2025 aus dem Ertragsformular (dt/ha), Durchschnittslinie Ø 104, 2022 rot markiert (−17 %) | „Dein Maßstab“ |
| 38,1–44,6 s | **06 Warnschwelle** (neu) | Handy-Einstellung: Regler, Schwelle 10 % der Feldfläche auffällig | „Du entscheidest, ab wann du gewarnt wirst“ |
| 44,6–53,8 s | **07 Benachrichtigung** (neu) | Sperrbildschirm, Banner „Dein Feld: 13 % auffällig“, Mini-Karte mit rot umrandeten auffälligen Pixeln | „Die App sagt dir, wo es hakt“ |
| 53,8–59 s | Abschluss | Logo (Pixel-Delta) + Satz | „Delta Green – Satellitendaten + KI: Stress im Maisfeld sichtbar machen“ |

**Änderungen (2026-10-18):** Die Szenen 0–4 und das Endbild sind unverändert. Neu sind nur die Zählung der auffälligen Pixel (Szene 04), die Szenen 05–07 und der Zeitversatz des Endbilds. Die Zahlen sind Illustration: Die auffälligen Pixel werden über die Schwelle `AUF_T = 0.55` auf dem Mittelwert des Musterfeldes gezählt (112 von 864 Pixeln, ca. 13 %), die Warnschwelle ist ein Beispielwert (`WARN_PCT = 10`, Bereich 10–15 %). Beides steht in `index.html` und wird dort berechnet, nicht von Hand eingetragen.

## Wo Higgsfield etwas bringt (optional)

Die HTML-Version funktioniert eigenständig. Mit Higgsfield kann man zwei Szenen durch echte Filmbilder ersetzen:

1. **Aufhänger (0–4,5 s):** Drohnenflug knapp über einem Maisfeld im Spätsommer, Hügelland wie in der Oststeiermark, einzelne vertrocknete, gelbbraune Flecken zwischen grünen Reihen, warmes Abendlicht, ruhige Vorwärtsfahrt. Kein Text, keine Menschen.
2. **Satellit (13,8–19 s):** Erdbeobachtungssatellit (Bauart wie Sentinel-2: ein Solarflügel, kastenförmiger Körper) im Orbit über Mitteleuropa am Tag, langsame Kamerafahrt mit dem Satelliten, Kamera kippt nach unten auf die Erde. Kein Text.

Einstellungen für beide: 16:9, 1080p, Ton aus, 5–6 s, Modell z. B. „Cinema Studio Video 3.0“ oder „Seedance 2.0“ (std).

Prompt 1 (Drohnenflug):
> Cinematic low drone flight just above a late-summer maize field in the rolling hills of south-eastern Austria (Styria), slow steady forward motion along the crop rows. Most plants are green, but scattered irregular patches are dry, yellow-brown and wilted. Warm low evening sun, light haze, realistic colors, documentary look, no people, no text, no logos.

Prompt 2 (Satellit):
> Photorealistic Earth observation satellite with a single long solar array and a box-shaped gold-foil body (similar to Sentinel-2) orbiting above Central Europe in daylight. The camera slowly tracks alongside the satellite, then tilts down past it towards the Earth, revealing a patchwork of green and brown farm fields far below. Thin blue atmosphere at the horizon, black space with faint stars, calm, no text, no logos.

**Nicht** generieren lassen: die Feldbilder über die Jahre und die Markierungen. Die sollen nach echten Daten aussehen
und sind im HTML bewusst als „schematische Darstellung“ gekennzeichnet. Noch besser wären echte Sentinel-2-Ausschnitte eines Feldes.

## Ehrlichkeit gegenüber der Jury

- Die App ist eine Web-App, sie wird hier in der Handyansicht gezeigt (keine eigene App aus dem Store).
- Feld, Zahlen und Pixel im Clip sind Illustrationen, keine Ergebnisse.
- Wenn KI-Bilder (Higgsfield) und KI-Code (Claude) verwendet werden, gehört das in `SUPPORT.md`.

## Sprecher (Version mit Ton)

**Umbenennung in „Delta Green“ (2026-10-18):** Name in App-Leiste, Benachrichtigung und Endbild sowie das Logo (Pixel-Delta statt 3×3-Raster) sind im Bild geändert. Neue Exporte: `export/DeltaGreen_Intro_1080p_stumm.mp4` und `export/DeltaGreen_Intro_1080p_Sprecher.mp4`. Zwei Sprechersätze nennen noch den alten Namen und müssen in ElevenLabs neu erzeugt werden (Helmut, Eleven v4, gleiche Einstellungen): Zeile 02 „Mit Delta Green wählst du dein Feld einfach auf der Karte aus.“ und Zeile 12 „Delta Green. Stress im Maisfeld sichtbar machen.“ (Texte in `voice/lines_v2.tsv`). Bis dahin ist die Sprecher-Fassung eine **Zwischenfassung**: Zeile 02 ist stumm, und von Zeile 12 bleibt nur „Stress im Maisfeld sichtbar machen.“ Die alten Dateien `export/CropTransfer_Intro_*` sind überholt.


**Aktuelle Fassung (2026-10-18): Stimme „Helmut – German Epic Trailer Voice“** (ElevenLabs, Eleven v4, Voice-ID `g1jpii0iyvtRs8fqXsd1`), in der ElevenLabs-Weboberfläche erzeugt und über den Verlauf geladen. Texte: `voice/lines_v2.tsv`, Dateien: `voice/lines_v2/NN.mp3` (Zweitvariante `NN_b.mp3`), Takt: `voice/timing_v2.tsv` (alle Zeilen Tempo 1,1). Zeile 07 („Daraus ergibt sich ein Anteil …“) ist erzeugt, aber nicht im Video, weil sie nicht ins Zeitfenster passt; der Zähler zeigt den Anteil ohnehin. Weil Helmut langsamer spricht, sind Szene 04 um 1,9 s und die neuen Szenen 05–07 länger. Ergebnis: `export/CropTransfer_Intro_1080p_v2_Sprecher.mp4` und stumm `export/CropTransfer_Intro_1080p_v2_stumm.mp4`.

Die folgende Tabelle gehört zur alten Fassung mit „Grady“ (36 s).

Stimme „Grady“, ElevenLabs v4 über Higgsfield, jeder Satz einzeln erzeugt (`voice/lines/`) und an den Szenenanfang gesetzt (`voice/timing.tsv`: Start in s, Tempofaktor).
Mischung: Kompressor + Lautheit −16 LUFS; Endbild um 1 s verlängert. Ergebnis: `export/CropTransfer_Intro_1080p_Sprecher.mp4` (36 s).

| Start | Text |
|---|---|
| 0,1 s | Manche Felder bringen weniger als sonst. Aber wo genau – und wann? |
| 5,15 s | Mit CropTransfer wählst du dein Feld einfach auf der Karte aus. |
| 9,9 s | Dann trägst du ein, was es in den letzten Jahren gebracht hat. |
| 14,2 s | Der Satellit Sentinel-2 fotografiert jedes Feld in Europa – alle paar Tage. |
| 19,9 s | So entsteht Jahr für Jahr ein neues Bild deines Feldes, in nassen wie in trockenen Jahren. |
| 25,6 s | Das Modell wertet jedes Pixel aus und markiert die Stellen, die immer wieder schwächeln. |
| 31,0 s | CropTransfer AT. Stress im Maisfeld sichtbar machen. |

## Was das Modell wirklich zeigt (für den Sprechertext)

Das Modell sagt den **relativen Ertrag** voraus (Ertrag im Vergleich zum eigenen Normalniveau des Feldes) bzw. misst, wie weit die Satellitenkurve von „gesundem Mais“ abweicht.
Es erkennt also, *dass* ein Feld oder Feldteil zurückbleibt, nicht *warum*: Trockenheit, Hitze, Nässe, Hagel, Boden oder Bewirtschaftung sind alles mögliche Ursachen.
Deshalb ist der Einstieg neutral formuliert und nennt keine Dürre.
