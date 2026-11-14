// Detailkarten je Feldzug (1866 und 1870/71): Grundkarte, Höhenlinien, Flüsse, Dörfer.
// Aufruf: cd werkzeuge && node detail.mjs <geo-Ordner>
//   <geo-Ordner> enthält tiles/8_x_y.png (Terrain Tiles, Terrarium-Kodierung, AWS Open Data),
//   ne_10m_rivers_lake_centerlines.json, ne_10m_rivers_europe.json (Natural Earth 4.1) und cities.json (lutangar/cities.json, GeoNames).
// Benötigt: npm i d3-geo d3-contour topojson-client world-atlas pngjs
// Ausgabe: karte-1866.json und karte-1870.json in werkzeuge/
import * as d3 from "d3-geo";
import {contours} from "d3-contour";
import {feature, mesh} from "topojson-client";
import {PNG} from "pngjs";
import fs from "fs";

const G = (process.argv[2] || "../geo").replace(/\/$/, "") + "/";
const ORTE = JSON.parse(fs.readFileSync("orte.json"));
const DATEN = JSON.parse(fs.readFileSync("schritte.json")); // von bau.py: {camp: [orte des Wegs]}
const topo = JSON.parse(fs.readFileSync((fs.existsSync("node_modules") ? "" : G) + "node_modules/world-atlas/countries-50m.json"));
const countries = feature(topo, topo.objects.countries);
const IDS = {"250": "fr", "276": "de", "203": "oe", "040": "oe", "703": "oe", "348": "oe", "705": "oe", "191": "oe",
  "616": "de", "056": "n", "442": "n", "528": "n", "756": "n", "208": "n", "380": "n", "826": "n", "440": "n", "643": "n", "804": "n"};
const r1 = v => Math.round(v * 10) / 10;

const MAPS = {
  "1866": {
    core: [12.25, 48.0, 17.55, 52.35],          // Kernausschnitt [W, S, O, N]
    wide: [8.8, 47.0, 21.0, 53.2],              // Bereich für Grundkarte und Höhen (Seitenränder bei Querformat)
    rot: -15, par: [48, 52],
    thr: [100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1400],
    major: v => v % 400 === 0,
    rivDE: {Elbe: "Elbe", Oder: "Oder", Danube: "Donau", Donau: "Donau", Morava: "March", Vltava: "Moldau", Dyje: "Thaya", Svratka: "Schwarzach",
      "Luzicka Nisa": "Neiße", Spree: "Spree", Saale: "Saale", Mulde: "Mulde", "Schwarze Elster": "Schwarze Elster", Eger: "Eger", Ohre: "Eger", Bóbr: "Bober",
      Jizera: "Iser", Orlice: "Adler", Sázava: "Sazawa", Jihlava: "Iglawa", Odra: "Oder", Warta: "Warthe", Vah: "Waag", Thaya: "Thaya", Svitava: "Zwittawa"},
    cities: {berlin: "Berlin", dresden: "Dresden", prag: "Prag", wien: "Wien", leipzig: "Leipzig", breslau: "Breslau", olmuetz: "Olmütz", posen: "Posen",
      pressburg: "Pressburg", linz: "Linz", glogau: "Glogau", josefstadt: "Josefstadt", pardubitz: "Pardubitz", chemnitz: "Chemnitz"},
    cl: [["PREUSSEN", 14.6, 52.15], ["SACHSEN", 13.0, 50.75], ["BÖHMEN", 14.3, 49.55], ["MÄHREN", 16.9, 49.75], ["SCHLESIEN", 16.4, 51.0],
      ["ÖSTERREICH", 15.2, 48.25], ["UNGARN", 18.3, 48.2], ["BAYERN", 12.0, 49.3], ["POSEN", 17.5, 52.55]],
    country: ["CZ", "AT", "DE", "PL", "SK", "HU"],
  },
  "1870": {
    core: [-0.35, 46.95, 8.35, 51.1],
    wide: [-1.8, 46.0, 9.8, 51.9],
    rot: -4, par: [47, 50],
    thr: [100, 150, 200, 250, 300, 400, 500, 700, 900],
    major: v => v === 200 || v === 300 || v === 500 || v === 900,
    rivDE: {Rhine: "Rhein", Rhein: "Rhein", Rhin: "Rhein", Loire: "Loire", Seine: "Seine", Marne: "Marne", Moselle: "Mosel", Mosel: "Mosel", Meuse: "Maas", Maas: "Maas",
      Sarre: "Saar", Saar: "Saar", Loir: "Loir", Sarthe: "Sarthe", Cher: "Cher", Aube: "Aube", Yonne: "Yonne", Oise: "Oise", Aisne: "Aisne", Nahe: "Nahe", Main: "Main",
      Huisne: "Huisne", Loing: "Loing", Eure: "Eure", Indre: "Indre", Mayenne: "Mayenne", Ornain: "Ornain"},
    cities: {paris: "Paris", metz: "Metz", strassburg: "Straßburg", nancy: "Nancy", reims: "Reims", tours: "Tours", chartres: "Chartres",
      koeln: "Köln", mainz: "Mainz", trier: "Trier", luxemburg: "Luxemburg", chalons: "Châlons", sedan: "Sedan", frankfurt: "Frankfurt", amiens: "Amiens",
      dijon: "Dijon", bourges: "Bourges", rouen: "Rouen", karlsruhe: "Karlsruhe", mannheim: "Mannheim", bruessel: "Brüssel"},
    cl: [["FRANKREICH", 3.0, 49.2], ["BELGIEN", 4.6, 50.6], ["LUX.", 6.1, 49.75], ["PREUSSEN", 7.15, 50.45], ["BAYERN", 7.75, 49.35], ["BADEN", 8.35, 48.5], ["SCHWEIZ", 7.6, 47.15]],
    country: ["FR", "BE", "LU", "DE", "CH", "NL"],
  },
};
const EXTRA = {breslau: [51.108, 17.039], olmuetz: [49.594, 17.251], posen: [52.406, 16.925], pressburg: [48.148, 17.107], linz: [48.306, 14.286],
  glogau: [51.664, 16.084], josefstadt: [50.343, 15.919], pardubitz: [50.038, 15.779], chemnitz: [50.833, 12.917],
  reims: [49.258, 4.032], chartres: [48.446, 1.489], mainz: [49.993, 8.247], trier: [49.750, 6.637], luxemburg: [49.612, 6.130], chalons: [48.957, 4.363],
  sedan: [49.702, 4.940], amiens: [49.894, 2.296], dijon: [47.322, 5.041], bourges: [47.081, 2.399], rouen: [49.443, 1.099], karlsruhe: [49.007, 8.404],
  mannheim: [49.488, 8.466], bruessel: [50.847, 4.357]};
Object.assign(ORTE, EXTRA);

// Höhen: Kacheln einmal lesen
const Z = 8, T = 256, n2 = 2 ** Z;
const tileOf = (lo, la) => { const l = la * Math.PI / 180; return [(lo + 180) / 360 * n2, (1 - Math.log(Math.tan(l) + 1 / Math.cos(l)) / Math.PI) / 2 * n2]; };

for (const [camp, C] of Object.entries(MAPS)) {
  const pr = d3.geoConicConformal().parallels(C.par).rotate([C.rot, 0]);
  const [w0, s0, e0, n0] = C.core;
  const coreGeo = {type: "MultiPoint", coordinates: [[w0, s0], [e0, s0], [w0, n0], [e0, n0], [(w0 + e0) / 2, n0 + .05], [(w0 + e0) / 2, s0 - .05]]};
  // Breite 1000, Höhe aus dem Seitenverhältnis des Kerns
  pr.fitWidth(1000, coreGeo);
  const b = d3.geoPath(pr).bounds(coreGeo);
  const W = 1000, H = Math.round(b[1][1] - b[0][1]);
  pr.fitExtent([[0, 0], [W, H]], coreGeo);
  const M = 420;
  pr.clipExtent([[-M, -M], [W + M, H + M]]);
  const path = d3.geoPath(pr).digits(1);
  const P = (lo, la) => pr([lo, la]);
  const inWide = ([x, y]) => x > -M && x < W + M && y > -M && y < H + M;

  const shapes = [];
  for (const f of countries.features) { const g = IDS[f.id]; if (!g) continue; const d = path(f); if (d) shapes.push({id: f.id, g, d}); }
  // Grenze Deutschland–Polen fehlt absichtlich: beide Seiten gehörten 1866 und 1870 zu Preußen
  const borders = path(mesh(topo, topo.objects.countries, (a, bb) => a !== bb && !((a.id === "276" && bb.id === "616") || (a.id === "616" && bb.id === "276"))));
  const grat = path(d3.geoGraticule().step([1, 1])());

  // ---- Flüsse ----
  const [ww, ws, we, wn] = C.wide;
  const inb = (lo, la) => lo > ww && lo < we && la > ws && la < wn;
  const riv = [], rlab = {};
  for (const f of ["ne_10m_rivers_lake_centerlines", "ne_10m_rivers_europe"]) {
    const gj = JSON.parse(fs.readFileSync(G + f + ".json"));
    for (const ft of gj.features) {
      const geo = ft.geometry; if (!geo) continue;
      const big = f.includes("centerlines") && (ft.properties.scalerank ?? 9) <= 6;
      const ls = geo.type === "MultiLineString" ? geo.coordinates : [geo.coordinates];
      for (const l of ls) {
        let seg = [];
        const push = () => { if (seg.length > 1) riv.push([ft.properties.name, seg, big]); seg = []; };
        for (const [lo, la] of l) { if (inb(lo, la)) seg.push(P(lo, la)); else push(); }
        push();
      }
    }
  }
  let rivL = "", rivS = "";
  const inCore = ([x, y]) => x > 30 && x < W - 30 && y > 30 && y < H - 30;
  for (const [n, seg, big] of riv) {
    const d = "M" + seg.map(p => r1(p[0]) + "," + r1(p[1])).join("L");
    if (big) rivL += d; else rivS += d;
    const de = C.rivDE[n]; if (!de) continue;
    const inner = seg.filter(inCore); if (inner.length < 4) continue;
    const L = inner.length, m = inner[Math.floor(L / 2)], m2 = inner[Math.min(L - 1, Math.floor(L / 2) + 3)];
    if (!rlab[de] || rlab[de].L < L) rlab[de] = {L, p: [r1(m[0]), r1(m[1])], a: Math.round(Math.atan2(m2[1] - m[1], m2[0] - m[0]) * 180 / Math.PI)};
  }
  const rivLabels = Object.entries(rlab).map(([n, v]) => { let a = v.a; if (a > 90) a -= 180; if (a < -90) a += 180; return {n, p: v.p, a}; });

  // ---- Höhenlinien ----
  const [tx0, ty0] = tileOf(ww, wn), [tx1, ty1] = tileOf(we, ws);
  const X0 = Math.floor(tx0), X1 = Math.floor(tx1), Y0 = Math.floor(ty0), Y1 = Math.floor(ty1);
  const gw = (X1 - X0 + 1) * T, gh = (Y1 - Y0 + 1) * T;
  const el = new Float64Array(gw * gh);
  for (let x = X0; x <= X1; x++) for (let y = Y0; y <= Y1; y++) {
    const png = PNG.sync.read(fs.readFileSync(`${G}tiles/${Z}_${x}_${y}.png`));
    for (let j = 0; j < T; j++) for (let i = 0; i < T; i++) { const k = (j * T + i) * 4; const e = png.data[k] * 256 + png.data[k + 1] + png.data[k + 2] / 256 - 32768; el[((y - Y0) * T + j) * gw + (x - X0) * T + i] = e < 0 ? 0 : e; }
  }
  // glätten (5x5 Mittel), damit die Linien bei diesem Maßstab ruhig bleiben
  const gs = new Float64Array(gw * gh);
  for (let j = 0; j < gh; j++) for (let i = 0; i < gw; i++) { let s = 0, n = 0; for (let bb = -2; bb <= 2; bb++) for (let a = -2; a <= 2; a++) { const jj = j + bb, ii = i + a; if (jj >= 0 && jj < gh && ii >= 0 && ii < gw) { s += el[jj * gw + ii]; n++; } } gs[j * gw + i] = s / n; }
  const toLL = (px, py) => { const X = X0 + px / T, Y = Y0 + py / T; return [X / n2 * 360 - 180, Math.atan(Math.sinh(Math.PI * (1 - 2 * Y / n2))) * 180 / Math.PI]; };
  const inRelief = ([x, y]) => x > -320 && x < W + 320 && y > -40 && y < H + 40;
  const cont = {minor: "", major: ""};
  for (const c of contours().size([gw, gh]).thresholds(C.thr)(gs)) {
    let d = "";
    for (const poly of c.coordinates) for (const ring of poly) {
      const pts = ring.map(([px, py]) => P(...toLL(px, py)));
      let L = 0; for (let k = 1; k < pts.length; k++) L += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
      if (L < 40) continue;
      let seg = [], last = null;
      const flush = () => { if (seg.length > 2) d += "M" + seg.map(p => r1(p[0]) + "," + r1(p[1])).join("L"); seg = []; };
      for (const p of pts) { if (!inRelief(p)) { flush(); last = null; continue; } if (last && Math.hypot(p[0] - last[0], p[1] - last[1]) < 4) continue; seg.push(p); last = p; }
      flush();
    }
    cont[C.major(c.value) ? "major" : "minor"] += d;
  }

  // ---- Orte ----
  const pts = {};
  for (const [k, v] of Object.entries(ORTE)) pts[k] = P(v[1], v[0]).map(r1);
  const route = DATEN[camp].map(k => pts[k]).filter(p => inWide(p));
  const cities = Object.entries(C.cities).filter(([k]) => inWide(pts[k])).map(([k, n]) => ({k, n, p: pts[k]}));

  // ---- Dörfer (GeoNames) nahe am Weg ----
  const cj = JSON.parse(fs.readFileSync(G + "cities.json"));
  const near = p => { let m = 1e9; for (let k = 1; k < route.length; k++) { const a = route[k - 1], bb = route[k]; const dx = bb[0] - a[0], dy = bb[1] - a[1]; const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy || 1))); m = Math.min(m, Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)); } return m; };
  const named = [...Object.values(pts)];
  const cand = [];
  for (const c of cj) {
    if (!C.country.includes(c.country)) continue;
    const lo = +c.lng, la = +c.lat; if (!inb(lo, la)) continue;
    const p = P(lo, la); if (!inCore(p)) continue;
    const dn = near(p); if (dn > 22) continue;
    if (named.some(q => Math.hypot(q[0] - p[0], q[1] - p[1]) < 6)) continue;
    cand.push({n: c.name, p, dn});
  }
  cand.sort((a, bb) => a.dn - bb.dn);
  const keep = [];
  for (const c of cand) if (keep.every(k => Math.hypot(k.p[0] - c.p[0], k.p[1] - c.p[1]) > 9)) keep.push(c);
  const villages = keep.map(c => ({n: c.n, p: [r1(c.p[0]), r1(c.p[1])]}));

  const CL = C.cl.map(([n, lo, la]) => ({n, p: P(lo, la).map(r1)}));
  const cx = (w0 + e0) / 2, cy = (s0 + n0) / 2, a = P(cx, cy), bb = P(cx + 100 / (111.32 * Math.cos(cy * Math.PI / 180)), cy);
  const km100 = +Math.hypot(bb[0] - a[0], bb[1] - a[1]).toFixed(2);
  fs.writeFileSync(`karte-${camp}.json`, JSON.stringify({W, H, shapes, borders, grat, rivers: rivL, riversSmall: rivS, rivLabels, contours: cont, pts, cities, villages, cl: CL, km100}));
  console.error(camp, "H", H, "Flüsse", rivL.length + rivS.length, rivLabels.map(r => r.n).join(","), "Höhen", cont.minor.length, cont.major.length, "Dörfer", villages.length, "km100", km100);
}
