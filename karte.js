/* Karte: Wilhelm Luchmanns Weg 1864–1871. Daten in karte-daten.js (erzeugt mit werkzeuge/bau.py). */
(() => {
"use strict";
const D = window.KD, M = D.map, S = D.steps, N = S.length;
const NS = "http://www.w3.org/2000/svg";
const $ = id => document.getElementById(id);
const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const pt = k => { const p = M.pts[k]; if (!p) throw new Error("Ort fehlt: " + k); return p; };
const svg = $("svg");

// ---------- statische Karte ----------
$("grat").setAttribute("d", M.grat);
for (const s of M.shapes) el("path", { d: s.d, class: "country g-" + s.g }, $("countries"));
$("borders").setAttribute("d", M.borders);
$("riverL").setAttribute("d", M.rivers);
$("riverS").setAttribute("d", M.riversSmall);
for (const r of M.rl) { const t = el("text", { class: "riv-lab", transform: `translate(${r.p[0]},${r.p[1]}) rotate(${r.a})` }, $("rivLabels")); t.textContent = r.n; }
for (const c of M.cl) { const t = el("text", { class: "clabel", x: c.p[0], y: c.p[1], "text-anchor": "middle" }, $("clabels")); t.textContent = c.n; }

// ---------- Weg aus den Schritten ----------
const TP = [];
S.forEach((st, i) => st.moves.forEach(k => TP.push({ s: i, k, p: pt(k), dash: !!st.dash, camp: st.camp })));
const T = S.map(st => Date.parse(st.date));
$("routeAll").setAttribute("d", "M" + TP.map(q => q.p.join(",")).join("L"));

// Orte: Punkt und Beschriftung; Großstädte immer sichtbar (blass)
const PLACE = D.names, BIG = D.big;
const placeEls = {};
const firstStep = {}; TP.forEach(q => { if (!(q.k in firstStep)) firstStep[q.k] = q.s; });
for (const k of new Set([...BIG, ...TP.map(q => q.k), ...S.flatMap(st => st.lab || [])])) {
  const p = pt(k);
  const g = el("g", { class: "pl" + (k in firstStep ? " pl-route" : " pl-big"), transform: `translate(${p[0]},${p[1]})` }, $("places"));
  const sc = el("g", { class: "sc" }, g);
  el("circle", { r: k in firstStep ? 3.6 : 2.4 }, sc);
  const t = el("text", { x: 6, y: 4 }, sc); t.textContent = PLACE[k] || k;
  if (k in firstStep) { g.style.cursor = "pointer"; g.addEventListener("click", () => go(firstStep[k])); const tt = el("title", {}, g); tt.textContent = PLACE[k]; }
  placeEls[k] = { g, t, p, w: (PLACE[k] || k).length * 6.4 + 8 };
}

// Ereignismarken
const markEls = S.map((st, i) => {
  if (!st.mark) return null;
  const p = pt(st.moves[st.moves.length - 1]);
  const g = el("g", { class: "mk mk-" + st.mark[0], transform: `translate(${p[0]},${p[1]})` }, $("events"));
  const sc = el("g", { class: "sc" }, g);
  const sy = el("text", { class: "mk-sym", x: -5, y: -7, "text-anchor": "end" }, sc); sy.textContent = st.mark[0] === "w" ? "✕" : "◆";
  const tt = el("title", {}, g); tt.textContent = st.mark[1];
  g.addEventListener("click", () => go(i));
  return g;
});

// ---------- Ansicht ----------
const FULL = [0, 0, M.W, M.H];
let overview = false;
function aspect() { const r = svg.getBoundingClientRect(); return r.width && r.height ? r.width / r.height : M.W / M.H; }
function fit(pts, minW) {
  const A = aspect();
  let x0 = Math.min(...pts.map(p => p[0])), x1 = Math.max(...pts.map(p => p[0]));
  let y0 = Math.min(...pts.map(p => p[1])), y1 = Math.max(...pts.map(p => p[1]));
  let w = Math.max(x1 - x0, minW), h = Math.max(y1 - y0, minW / A);
  w *= 1.35; h *= 1.35;
  if (w / h > A) h = w / A; else w = h * A;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  return [cx - w / 2, cy - h / 2, w, h];
}
function fullBox() { const A = aspect(); let w = M.W, h = M.H; if (w / h > A) h = w / A; else w = h * A; return [(M.W - w) / 2, (M.H - h) / 2, w, h]; }
function targetBox(i) {
  if (overview) return fullBox();
  const own = TP.filter(q => q.s === i).map(q => q.p);
  const prev = TP.filter(q => q.s < i).slice(-1).map(q => q.p);
  const lab = (S[i].lab || []).map(pt);
  return fit([...own, ...prev, ...lab], 150);
}
let box = fullBox(), anim = null;
function setBox(b) { box = b; svg.setAttribute("viewBox", b.map(v => v.toFixed(1)).join(" ")); }

// ---------- Zeichnen ----------
const segLen = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
function draw(v) {
  // v ganzzahlig: Schritt v vollständig; v = i-1+f während der Animation zu Schritt i
  const i = Math.ceil(v - 1e-9), f = Math.abs(v - Math.round(v)) < 1e-9 ? 1 : v - Math.floor(v);
  const rw = svg.getBoundingClientRect().width || 1000;
  const s = box[2] / rw * 0.95;  // Beschriftungen auf dem Bildschirm etwa gleich groß, egal wie stark vergrößert
  svg.style.setProperty("--s", s.toFixed(4));
  // Weg bis v
  let solid = "", dash = "", old = "";
  const curCamp = S[Math.min(i, N - 1)].camp;
  const own = TP.filter(q => q.s === i);
  const ownStart = TP.indexOf(own[0]);
  let total = 0; for (let j = Math.max(ownStart, 1); j < ownStart + own.length && j > 0; j++) total += segLen(TP[j - 1].p, TP[j].p);
  let budget = total * f, head = null;
  for (let j = 1; j < TP.length; j++) {
    const a = TP[j - 1], b = TP[j];
    if (b.s > i) break;
    let to = b.p;
    if (b.s === i && f < 1) {
      const L = segLen(a.p, b.p);
      if (budget <= 0) break;
      if (budget < L) { const t = budget / L; to = [a.p[0] + (b.p[0] - a.p[0]) * t, a.p[1] + (b.p[1] - a.p[1]) * t]; budget = 0; }
      else budget -= L;
    }
    const seg = `M${a.p[0]},${a.p[1]}L${to[0].toFixed(1)},${to[1].toFixed(1)}`;
    if (b.camp !== curCamp) old += seg; else if (b.dash) dash += seg; else solid += seg;
    head = to;
  }
  $("trkSolid").setAttribute("d", solid); $("trkDash").setAttribute("d", dash); $("trkOld").setAttribute("d", old);
  // aktueller Ort
  const target = TP.filter(q => q.s <= i).slice(-1)[0];
  const cp = f > 0 && head ? head : (target ? target.p : TP[0].p);
  $("cur").setAttribute("transform", `translate(${cp[0]},${cp[1]})`);
  // Orte: sichtbar ab erstem Besuch; Beschriftung mit einfacher Kollisionsprüfung
  const shown = [];
  const vis = k => (k in firstStep) ? firstStep[k] <= i : true;
  const prio = [];
  S[i].moves.forEach(k => prio.push(k)); (S[i].lab || []).forEach(k => prio.push(k));
  for (let j = i - 1; j >= 0; j--) for (const k of [...S[j].moves].reverse()) prio.push(k);
  BIG.forEach(k => prio.push(k));
  const seen = new Set(), boxes = [];
  for (const [k, e] of Object.entries(placeEls)) { e.g.classList.toggle("on", vis(k) || (S[i].lab || []).includes(k)); e.t.style.display = "none"; }
  for (const k of prio) {
    if (seen.has(k) || !placeEls[k]) continue; seen.add(k);
    const e = placeEls[k]; if (!e.g.classList.contains("on")) continue;
    const bx = [e.p[0] - 4 * s, e.p[1] - 9 * s, e.p[0] + e.w * s, e.p[1] + 6 * s];
    if (boxes.some(b => bx[0] < b[2] && bx[2] > b[0] && bx[1] < b[3] && bx[3] > b[1])) continue;
    boxes.push(bx); e.t.style.display = "";
  }
  markEls.forEach((m, j) => m && m.classList.toggle("on", j <= i));
  // Maßstab
  const pxPerUnit = svg.getBoundingClientRect().width / box[2];
  const kmPerPx = 100 / M.km100 / pxPerUnit;
  const nice = [5, 10, 20, 50, 100, 200, 300].find(n => n / kmPerPx >= 60) || 300;
  $("msLab").textContent = nice + " km"; $("msBar").style.width = (nice / kmPerPx).toFixed(0) + "px";
}

// ---------- Panel ----------
const CAMP = { "1866": "Feldzug 1866", "1870": "Feldzug 1870/71" };
const esc = t => String(t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
let cur = 0;
function render(i) {
  const st = S[i];
  $("pCount").textContent = `Schritt ${i + 1} von ${N}`;
  $("pFront").textContent = CAMP[st.camp];
  $("pName").textContent = st.title;
  $("pSub").textContent = st.sub || "";
  $("pDates").textContent = st.dl;
  $("pQuote").innerHTML = st.quote ? `„${esc(st.quote[0].replace(/^„|“$/g, ""))}“<cite>${esc(st.quote[1])}</cite>` : "";
  $("pQuote").hidden = !st.quote;
  $("pText").textContent = st.text;
  $("pCheck").innerHTML = `<b>Abgleich:</b> ${esc(st.check)}`;
  $("pBelS").textContent = D.belShort[st.bel]; $("pBelS").className = "bel bel-" + st.bel;
  $("pNote").textContent = D.bel[st.bel] + ". " + (st.note || "");
  $("pSrc").innerHTML = '<div class="refs">' + st.src.map(k => `<span><a href="quellen-karte.html#q-${k}">${esc(D.srcNo[k])}</a> ${esc(D.srcShort[k])}</span>`).join("") + "</div>";
  $("nowDate").textContent = st.dl;
  document.querySelectorAll("#tbody tr").forEach((tr, j) => tr.classList.toggle("cur", j === i));
  ticks.forEach((t, j) => { t.classList.toggle("visited", j <= i); t.setAttribute("aria-current", j === i ? "step" : "false"); });
  const x = pos(i) * 100;
  $("playhead").style.left = x + "%"; $("prog").style.width = x + "%";
  $("prev").disabled = i === 0; $("next").disabled = i === N - 1;
}

function animate(i, dur) {
  const from = cur, b0 = box.slice(), b1 = targetBox(i);
  cancelAnimationFrame(anim);
  if (reduce || dur === 0) { setBox(b1); draw(i); return; }
  const t0 = performance.now();
  const step = now => {
    const t = Math.min(1, (now - t0) / dur), e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    setBox(b0.map((v, k) => v + (b1[k] - v) * e));
    draw(i === from + 1 ? from + e : i);
    if (t < 1) anim = requestAnimationFrame(step); else draw(i);
  };
  anim = requestAnimationFrame(step);
}
function go(i, dur = 1100) {
  i = Math.max(0, Math.min(N - 1, i));
  render(i); animate(i, dur); cur = i;
  try { history.replaceState(null, "", "#s" + (i + 1)); } catch (e) {}
}

// ---------- Zeitleiste ----------
const t0 = T[0], t1 = T[N - 1];
const pos = i => 0.45 * i / (N - 1) + 0.55 * (T[i] - t0) / (t1 - t0);
const ticks = S.map((st, i) => {
  const b = document.createElement("button"); b.type = "button"; b.className = "tick"; b.style.left = pos(i) * 100 + "%";
  b.title = `${st.dl}: ${st.title}`; b.setAttribute("aria-label", `Schritt ${i + 1}: ${st.title}, ${st.dl}`);
  b.addEventListener("click", () => { setPlaying(false); go(i); }); $("ruler").appendChild(b); return b;
});
const years = {}; S.forEach((st, i) => { const y = st.date.slice(0, 4); if (!(y in years)) years[y] = i; });
let lastY = -1;
for (const [y, i] of Object.entries(years)) { if (pos(i) - lastY < 0.07) continue; lastY = pos(i); const m = document.createElement("span"); m.className = "month y"; m.style.left = pos(i) * 100 + "%"; m.textContent = y; $("ruler").appendChild(m); }
for (const c of ["1866", "1870"]) { const i = S.findIndex(st => st.camp === c); const m = document.createElement("span"); m.className = "month"; m.style.left = pos(i) * 100 + "%"; m.textContent = CAMP[c].replace("Feldzug ", "▸ "); $("ruler").appendChild(m); }

// ---------- Chronologie ----------
S.forEach((st, i) => {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td class="n">${i + 1}</td><td class="d">${esc(st.dl)}</td><td><b>${esc(st.title)}</b><br>${esc(D.names[st.moves[st.moves.length - 1]])}</td><td><span class="bel bel-${st.bel}">${esc(D.belShort[st.bel])}</span></td>`;
  tr.addEventListener("click", () => { setPlaying(false); go(i); scrollTo({ top: $("map").getBoundingClientRect().top + scrollY - 10, behavior: reduce ? "auto" : "smooth" }); });
  $("tbody").appendChild(tr);
});
$("chronN").textContent = N;

// ---------- Bedienung ----------
let timer = null;
function setPlaying(on) {
  clearInterval(timer); timer = null;
  $("play").textContent = on ? "❚❚ Pause" : "▶ Abspielen"; $("play").setAttribute("aria-pressed", String(on));
  if (!on) return;
  if (cur >= N - 1) go(0, 0);
  const tick = () => { if (cur >= N - 1) return setPlaying(false); go(cur + 1); };
  timer = setInterval(tick, +$("speedSel").value);
}
$("play").addEventListener("click", () => setPlaying(!timer));
$("prev").addEventListener("click", () => { setPlaying(false); go(cur - 1); });
$("next").addEventListener("click", () => { setPlaying(false); go(cur + 1); });
$("reset").addEventListener("click", () => { setPlaying(false); go(0); });
$("speedSel").addEventListener("change", () => { if (timer) setPlaying(true); });
$("zoomBtn").addEventListener("click", () => {
  overview = !overview; $("zoomBtn").setAttribute("aria-pressed", String(!overview));
  $("zoomBtn").textContent = overview ? "Ausschnitt" : "Gesamtkarte"; animate(cur, 700);
});
document.addEventListener("keydown", e => {
  if (e.target.closest("input,select,textarea")) return;
  if (e.key === "ArrowRight") { setPlaying(false); go(cur + 1); } else if (e.key === "ArrowLeft") { setPlaying(false); go(cur - 1); }
});
let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => { setBox(targetBox(cur)); draw(cur); }, 120); });

// Legende auch mobil (aufklappbar)
const lb = document.querySelector(".legend-bar"); if (lb) { const c = lb.cloneNode(true); c.className = "legend"; $("legendM").appendChild(c); }
// Einführung merken
const it = $("intro");
if (it) { try { if (localStorage.getItem("lmIntroClosed") === "1") it.open = false; } catch (e) {}
  it.addEventListener("toggle", () => { try { localStorage.setItem("lmIntroClosed", it.open ? "0" : "1"); } catch (e) {} }); }

const h = /^#s(\d+)$/.exec(location.hash);
const start = h ? Math.min(N, Math.max(1, +h[1])) - 1 : 0;
setBox(targetBox(start)); cur = start; render(start); draw(start);
})();
