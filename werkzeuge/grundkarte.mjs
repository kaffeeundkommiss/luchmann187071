// Grundkarte Mitteleuropa für die Luchmann-Karte (1866 und 1870/71).
// Heutige Grenzen (world-atlas 10m), Flüsse Natural Earth 10m. Ausgabe: grund.json mit Pfaden und Ortskoordinaten.
import * as d3 from "d3-geo";
import {feature, mesh} from "topojson-client";
import fs from "fs";

const W = 1000, H = 640;
const pr = d3.geoConicConformal().parallels([47, 52]).rotate([-9, 0]);
const bbox = {type: "MultiPoint", coordinates: [[-0.6, 47.0], [18.0, 47.0], [-0.6, 53.0], [18.0, 53.0], [8.7, 53.3], [8.7, 46.4]]};
pr.fitExtent([[18, 14], [W - 18, H - 14]], bbox);
pr.clipExtent([[-200, -200], [W + 200, H + 200]]);
const path = d3.geoPath(pr).digits(1);

const topo = JSON.parse(fs.readFileSync("node_modules/world-atlas/countries-50m.json"));
const fc = feature(topo, topo.objects.countries);
// g: Gruppe für die Färbung. fr = Frankreich, oe = Österreich (Kaiserreich 1866), de = Deutscher Bund/Preußen und Nachbarn, n = neutral
const IDS = {"250": "fr", "276": "de", "203": "oe", "040": "oe", "703": "oe", "348": "oe", "705": "oe", "191": "oe",
  "616": "de", "056": "n", "442": "n", "528": "n", "756": "n", "208": "n", "380": "n", "826": "n", "440": "n", "643": "n", "804": "n"};
const shapes = [];
for (const f of fc.features) { const g = IDS[f.id]; if (!g) continue; const d = path(f); if (d) shapes.push({id: f.id, g, d}); }
const borders = path(mesh(topo, topo.objects.countries, (a, b) => a !== b));
const coast = path(mesh(topo, topo.objects.countries, (a, b) => a === b));

const pick = (file, names) => {
  const f = JSON.parse(fs.readFileSync(file));
  const out = [];
  for (const x of f.features) { const n = x.properties.name; if (!names.includes(n)) continue; const g = x.geometry; out.push(...(g.type === "LineString" ? [g.coordinates] : g.coordinates)); }
  return out;
};
const big = pick("ne_10m_rivers_lake_centerlines.json", ["Rhein", "Rhine", "Rhin", "Elbe", "Oder", "Donau", "Danube", "Mosel", "Loire", "Seine", "Marne", "Main", "Morava", "Vltava", "Maas", "Weser"]);
const small = pick("ne_10m_rivers_europe.json", ["Sarre", "Spree", "Saale", "Cher", "Sarthe", "Dyje", "Bóbr", "Luzicka Nisa", "Loir", "Eger", "Aube", "Mulde", "Zwickauer Mulde", "Schwarze Elster", "Nysa Kłodzka", "Svratka"]);
const rivers = path({type: "MultiLineString", coordinates: big});
const riversSmall = path({type: "MultiLineString", coordinates: small});
const grat = path(d3.geoGraticule().step([2, 2])());

// Orte [Länge, Breite]; heutige Lage, auf etwa 1–2 km genau
const PL = JSON.parse(fs.readFileSync("orte.json"));
const pts = {};
for (const [k, v] of Object.entries(PL)) pts[k] = pr([v[1], v[0]]).map(n => +n.toFixed(1));
// Flussbeschriftungen [Name, Länge, Breite, Winkel]
const RL = [["Elbe", 14.5, 50.45, -20], ["Oder", 15.9, 52.45, 70], ["Donau", 15.7, 48.32, 0], ["March", 16.95, 48.58, -70], ["Moldau", 14.5, 49.6, -70],
  ["Rhein", 7.55, 50.35, -45], ["Mosel", 6.5, 49.55, -45], ["Loire", 1.35, 47.55, 25], ["Seine", 3.2, 48.42, 5], ["Main", 9.9, 49.88, 10], ["Saar", 6.92, 49.45, 70]]
  .map(([n, lo, la, a]) => ({n, p: pr([lo, la]).map(v => +v.toFixed(1)), a}));
// Länderbeschriftungen 1866/1870 (historisch, schematisch)
const CL = [["FRANKREICH", 2.3, 48.75], ["PREUSSEN", 13.8, 52.6], ["SACHSEN", 13.2, 50.95], ["BÖHMEN", 14.2, 49.75], ["MÄHREN", 16.65, 49.55],
  ["ÖSTERREICH", 15.1, 48.0], ["UNGARN", 17.6, 47.6], ["BAYERN", 11.3, 49.0], ["HESSEN", 8.9, 50.55], ["BELGIEN", 4.6, 50.55], ["LUX.", 6.08, 49.72], ["SCHWEIZ", 8.0, 46.9]]
  .map(([n, lo, la]) => ({n, p: pr([lo, la]).map(v => +v.toFixed(1))}));
// Rahmen der beiden Detailkarten (Kernausschnitte aus detail.mjs)
const FR = {"1866": [12.25, 48.0, 17.55, 52.35], "1870": [-0.35, 46.95, 8.35, 51.1]};
const frames = {};
for (const [k, [w, s, e, n]] of Object.entries(FR)) {
  const ring = [];
  for (let t = 0; t <= 20; t++) ring.push([w + (e - w) * t / 20, n]);
  for (let t = 1; t <= 20; t++) ring.push([e, n - (n - s) * t / 20]);
  for (let t = 1; t <= 20; t++) ring.push([e - (e - w) * t / 20, s]);
  for (let t = 1; t <= 20; t++) ring.push([w, s + (n - s) * t / 20]);
  frames[k] = {d: "M" + ring.map(p => pr(p).map(v => v.toFixed(1)).join(",")).join("L") + "Z", nw: pr([w, n]).map(v => +v.toFixed(1)), sw: pr([w, s]).map(v => +v.toFixed(1))};
}
// Maßstab: Kartenpixel je 100 km auf 50° N
const a = pr([10, 50]), b = pr([10 + 100 / (111.32 * Math.cos(50 * Math.PI / 180)), 50]);
const km100 = +Math.hypot(b[0] - a[0], b[1] - a[1]).toFixed(2);
fs.writeFileSync("grund.json", JSON.stringify({W, H, shapes, borders, coast, rivers, riversSmall, grat, pts, rl: RL, cl: CL, km100, frames}));
console.error("shapes", shapes.length, "rivers", rivers.length, riversSmall.length, "pts", Object.keys(pts).length, "km100", km100);
