# Pitch-Intro – Storyboard (≈ 35 s)

Zweck: In einer halben Minute zeigen, **welches Problem** CropTransfer AT löst und **was die App macht**.
Die Details (Daten, Modell, Österreich-Test, Grenzen) erklärst du danach selbst vor der Kamera.

Datei: `index.html` (im Browser öffnen, Vollbild F11, Leertaste = Start, mit OBS/Xbox Game Bar aufnehmen).

| Zeit | Szene | Bild | Text im Bild |
|---|---|---|---|
| 0–4,5 s | Aufhänger | Drohnenflug über Maisreihen (Higgsfield-Clip) | „Manche Felder bringen weniger als sonst. Aber *wo* genau – und *wann*?“ |
| 4,5–9,6 s | 01 Feld wählen | Handy mit Luftbild, Finger tippt die Ecken, Feld wird umrandet. Finale Fassung: KI-Luftbild (`?map=ai`, Standard); Alternative `?map=ortho`: echtes Orthofoto basemap.at 2024 + echter INVEKOS-Körnermaisschlag bei Feldbach | „Feld auswählen“ |
| 9,6–13,8 s | 02 Erträge | Formular „What did it yield?“, 2021–2025 werden eingetippt, Start | „Alte Erträge eintragen“ |
| 13,8–20 s | 03 Satellit | Weltall, Erdkrümmung, Satellit zieht vorbei, Strahl aufs Feld, Zoom hinein | „Der Satellit schaut zu“ |
| 20–24,8 s | Jahre | Dasselbe Feld 2019 → 2025, jedes Jahr ein neues Bild (Scan-Effekt), Mini-Bilder unten | „Jahr für Jahr ein neues Bild“ |
| 24,8–29,4 s | 04 Punkte | Feld zerfällt in 10-m-Pixel, Farbskala, Markierungen auf schwachen Zonen | „Schwache Stellen markiert“ |
| 29,6–35 s | Abschluss | Logo + Satz | „CropTransfer AT – Satellitendaten + KI: Stress im Maisfeld sichtbar machen“ |

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
