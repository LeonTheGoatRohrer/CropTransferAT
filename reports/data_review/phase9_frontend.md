# Datenkritik Phase 9 – Web-Frontend (`web/`)

Stand 2026-10-17. Kein neues Modell, kein neuer Lauf: Das Frontend zeigt vorhandene Ergebnisse. Geprüft wurde, ob die Darstellung die Daten korrekt und ehrlich wiedergibt.

| Punkt | Geprüft wie? | Befund | Konsequenz |
|---|---|---|---|
| 3.1 Repräsentativität | n/a – keine neue Stichprobe | Die fünf Demo-Felder sind bewusst gewählt (stark, gefährdet und erkannt, normal, Fehlalarm T4, verpasster Verlust) | Auswahl wird auf der Seite als „prepared fields“ mit Rolle benannt, nicht als Zufallsstichprobe |
| 3.2 Korrektheit | Exportwerte gegen Ergebnisdateien verglichen | Pixel-ρ je Feld-Jahr reproduziert `results/2026-10-17_innerfeld/per_fy.csv` (B0) exakt: 0,544 / 0,753 / 0,757; Risiko, Alarm und Score aus `ranking.csv` bzw. `oof.parquet` (A_roh) | ✅ |
| 3.2 Einheiten | Code-Review Export | ERA5 K → °C, m → mm, GDD mit `features.daily_weather` (10/30 °C) | ✅ |
| 3.3 Scheinzusammenhänge | n/a | Der Datenexplorer zeigt gepoolte Rangkorrelationen; die Seite weist darauf hin, dass sie Standort- und Jahresunterschiede enthalten | Hinweistext unter der Matrix |
| 3.4 Leakage / Österreich-Regel | Export-Skript gelesen | Es werden keine österreichischen Roh- oder Merkmalsdateien geöffnet; nur aggregierte Ergebnisse des bereits ausgewerteten Tests (`results/2026-10-17_at_test`, `_at_retrain`) | ✅ |
| 3.5 Plausibilität / Ehrlichkeit | Seiten durchgesehen | Jede Kennzahl mit KI und n; negative Ergebnisse (Phase 4, Mehr-Kulturen, Feinjustierung, Glättung) eigene Abschnitte; Österreich-Test als explorativ und „nicht besser als NDVI“ dargestellt; simulierte Ergebnisse für gezeichnete Felder überall markiert | ✅ |
| Darstellung | Abweichung bewusst | Die Saison-Animation trägt bei Dekaden ohne klare Aufnahme den letzten Wert weiter (nur Anzeige, im Bild vermerkt); Merkmale und Score nutzen weiterhin nur beobachtete Dekaden | dokumentiert |
| Veröffentlichung | – | KBS-Daten nur mit schriftlicher Erlaubnis veröffentlichen | Seite bleibt lokal/privat, `noindex`; `web/public/data/` nicht im Repository |

**Entscheidung:** ✅ Weiter.
