# Feldwebel Wilhelm Luchmann 1866 und 1870/71

Seite im Bereich Geschichte von [Kaffee und Kommiss](https://kaffeeundkommiss.github.io/geschichte/):
https://kaffeeundkommiss.github.io/luchmann187071/

Grundlage sind die „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebels Wilhelm Luchmann“
(Familienchronik, hg. von Gerd Luchmann, Trier 1994; Abschrift Gertrud Luchmann 1994).
Veröffentlichung mit Zustimmung der Familie.

## Aufbau

| Seite | Inhalt |
|---|---|
| `index.html` | Animierte Karte mit Zeitleiste und 31 Stationen |
| `abgleich.html` | Abgleich Tagebuch und Regimentsgeschichte je Station, Muster der Abweichungen |
| `personen.html` | Im Tagebuch genannte Offiziere und Kameraden |
| `tagebuch.html` | Die Quelle, Handschrift und Abbildungen |
| `glossar.html` | Militärische Begriffe |
| `quellen-*.html` | Quellenverzeichnis je Seite |

## Belegstand

- **bestätigt**: Regimentsgeschichte und eine zweite Quelle
- **Regimentsgeschichte**: nur durch die Regimentsgeschichte (Müller 1875) belegt
- **abweichend**: Tagebuch weicht bei Datum, Ort oder Zahl ab
- **nur Tagebuch**: keine zweite Quelle

Seitenangaben „T S. n“ zählen die Scanseiten des PDF, nicht die gedruckten Seitenzahlen der Abschrift.

## Bauen

Alle HTML-Seiten, `karte-daten.js` und `site.js` werden erzeugt; Inhalte nur in `werkzeuge/daten.py` ändern.

```
python3 werkzeuge/bau.py
```

Die Grundkarte (`werkzeuge/grund.json`) erzeugt `werkzeuge/grundkarte.mjs` mit d3-geo, topojson-client,
world-atlas (countries-50m) und Natural-Earth-Flüssen. Ortskoordinaten stehen in `werkzeuge/orte.json`.

## Rechte und Namen

- Aus der Familie werden nur Wilhelm Luchmann und die Herausgeber genannt.
- Die Atlaskarten der Chronik sind nicht übernommen; die Karte ist eine eigene Darstellung.
- Die beiden Schlachtengemälde der Chronik sind ohne Maler- und Rechteangabe; Herkunft offen.
