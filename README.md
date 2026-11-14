# Feldwebel Wilhelm Luchmann 1866 und 1870/71

Seite im Bereich Geschichte von [Kaffee und Kommiss](https://kaffeeundkommiss.github.io/geschichte/):
https://kaffeeundkommiss.github.io/luchmann187071/

Grundlage sind die „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebels Wilhelm Luchmann“
(Familienchronik, hg. von Gerd Luchmann, Trier 1994; Abschrift Gertrud Luchmann 1994).
Veröffentlichung mit Zustimmung der Familie.

## Aufbau

| Seite | Inhalt |
|---|---|
| `index.html` | Übersicht mit Übersichtsplan beider Feldzüge |
| `karte-1866.html` | Animierte Karte Feldzug 1866 (mit 1864/65), 13 Stationen |
| `karte-1870.html` | Animierte Karte Feldzug 1870/71, 18 Stationen |
| `abgleich.html` | Abgleich je Station, getrennt nach Feldzügen, Muster der Abweichungen |
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

Alle HTML-Seiten, `karte-daten-1866.js`, `karte-daten-1870.js` und `site.js` werden erzeugt; Inhalte nur in `werkzeuge/daten.py` ändern.

```
python3 werkzeuge/bau.py
```

Die Grundkarte (`werkzeuge/grund.json`) erzeugt `werkzeuge/grundkarte.mjs` mit d3-geo, topojson-client,
world-atlas (countries-50m) und Natural-Earth-Flüssen. Ortskoordinaten stehen in `werkzeuge/orte.json`.

Die beiden Detailkarten (`werkzeuge/karte-1866.json`, `karte-1870.json`) erzeugt `werkzeuge/detail.mjs`:
Höhenlinien aus Terrain Tiles (AWS Open Data, Zoom 8), Flüsse aus Natural Earth 10m, Dörfer aus GeoNames (cities.json, CC BY 4.0).
`werkzeuge/schritte.json` (Orte je Feldzug) vorher aus `daten.py` erzeugen; Aufruf und Datenquellen stehen im Kopf von `detail.mjs`.

## Rechte und Namen

- Aus der Familie werden nur Wilhelm Luchmann und die Herausgeber genannt.
- Die Atlaskarten der Chronik sind nicht übernommen; die Karte ist eine eigene Darstellung.
- Die beiden Schlachtengemälde der Chronik sind ohne Maler- und Rechteangabe; Herkunft offen.
