/* Gemeinsame Funktionen aller Seiten:
   1. Glossar: erklärt Fachbegriffe beim ersten Vorkommen je Seite per Antippen (funktioniert ohne Hover, also auch am Handy).
   2. Kontextzeile auf Seiten ohne Einführungskasten.
   3. Belege in Ablaufkarten und Zahlenkästen einklappbar machen (Inhalt zuerst). */
(() => {
"use strict";

// Glossar: reine Worterklärungen ohne Einzelbeleg.
const GSRC = {
  web: ["Angaben dieser Website (Karte und Unterseiten mit eigenen Quellen)", "quellen-karte.html"]
};

// Begriffe (aus werkzeuge/daten.py). re = Suchmuster im Text.
const GLOSSAR = [
  { id: "fues", t: "Füsilier-Bataillon", re: "Füsilier-Bataillon(?:s)?", src: [],
    d: "Das dritte Bataillon eines preußischen Infanterie-Regiments, ursprünglich leichte Infanterie. Beim Grenadier-Regiment Nr. 12 bestand es aus der 9. bis 12. Kompanie; Luchmann diente in der 9." },
  { id: "fourier", t: "Fourier", re: "Fouriere?", src: [],
    d: "Unteroffizier, der für Unterkunft und Verpflegung seiner Einheit sorgt und dem Truppenteil als Quartiermacher vorausreist." },
  { id: "feldwebel", t: "Feldwebel", re: "Feldwebel", src: [],
    d: "Ranghöchster Unteroffizier einer Kompanie, zuständig für Innendienst, Listen und Verwaltung. Nach Mars-la-Tour führten Feldwebel und Sergeanten mehrere Kompanien des Bataillons." },
  { id: "sergeant", t: "Sergeant", re: "Sergeant(?:en)?", src: [],
    d: "Unteroffiziersdienstgrad über dem Unteroffizier und unter dem Feldwebel." },
  { id: "ek", t: "Eisernes Kreuz", re: "Eiserne[ns]? Kreuz(?:es)?", src: [],
    d: "Preußische Kriegsauszeichnung in zwei Klassen, für den Krieg 1870/71 neu gestiftet. Die II. Klasse wurde am Band im Knopfloch getragen." },
  { id: "chassepot", t: "Chassepot", re: "Chass?epots?", src: [],
    d: "Französisches Hinterladergewehr, dem preußischen Zündnadelgewehr in der Reichweite überlegen." },
  { id: "zuendnadel", t: "Zündnadelgewehr", re: "Zündnadel(?:gewehr)?e?", src: [],
    d: "Preußisches Hinterladergewehr von Dreyse; 1866 der wichtigste Vorteil gegenüber den österreichischen Vorderladern." },
  { id: "mitrailleuse", t: "Mitrailleuse", re: "Mitrailleusen?", src: [],
    d: "Französische Salvengeschütze mit vielen Läufen, Vorläufer des Maschinengewehrs." },
  { id: "franktireur", t: "Franktireur", re: "Franktireurs?", src: [],
    d: "Französische Freischärler 1870/71, die außerhalb der regulären Armee kämpften. Deutsche Truppen antworteten oft mit Vergeltung gegen Ortschaften." },
  { id: "mobilgarde", t: "Mobilgarde", re: "Mobilgarden?", src: [],
    d: "Garde nationale mobile, französische Reserve aus Wehrpflichtigen; 1870 meist schlecht ausgebildet." },
  { id: "turco", t: "Turcos und Zuaven", re: "Turcos|Zuaven", src: [],
    d: "Truppen der französischen Afrika-Armee; Turcos waren algerische Schützen, Zuaven ursprünglich ebenfalls in Nordafrika aufgestellte Infanterie." },
  { id: "avantgarde", t: "Avantgarde", re: "Avantgarde|Vorhut", src: [],
    d: "Vorausmarschierende Abteilung, die den Hauptteil der Truppe sichert." },
  { id: "kantonnement", t: "Kantonnement", re: "Kantonnements?|Cantonements?", src: [],
    d: "Unterbringung von Truppen in Ortschaften, im Gegensatz zum Biwak unter freiem Himmel." },
  { id: "biwak", t: "Biwak", re: "Biwaks?", src: [],
    d: "Lager unter freiem Himmel ohne Zelte oder Gebäude." },
  { id: "erbswurst", t: "Erbswurst", re: "Erbswurst", src: [],
    d: "Gepresste Suppenkonserve aus Erbsmehl und Fett, 1870/71 als Notverpflegung ausgegeben; bei Luchmann und in der Regimentsgeschichte wenig beliebt." },
  { id: "landwehr", t: "Landwehr", re: "Landwehr", src: [],
    d: "Ältere Jahrgänge der Reservisten. Vor Metz lag nach dem Tagebuch die „Landwehrdivision Kummer“ neben Luchmanns Bataillon." }
];
window.GLOSSAR = GLOSSAR; window.GSRC = GSRC;

const BY_ID = Object.fromEntries(GLOSSAR.map(g => [g.id, g]));
let RX = null;
try {
  RX = new RegExp("(?<![\\p{L}\\p{N}])(" + GLOSSAR.map(g => "(?<" + g.id + ">" + g.re + ")").join("|") + ")(?![\\p{L}\\p{N}])", "gu");
} catch (e) { RX = null; } // sehr alte Browser ohne Lookbehind: keine Markierung, Seite bleibt lesbar

// Bereiche, in denen nichts markiert wird
const SKIP = "blockquote,.zitat,.zit,script,style,svg,a,button,select,label,summary,h1,.h1,h2,h3,nav,.b,.chip,.uchip,.bel,.legend,.count,.t,.day,.eyebrow,.ruler,.nowdate,ol.srcs,ol.srclist,.sources,.src,.glpop,.glnone,thead,.dates,.num";

function markIn(root, used, excl) {
  if (!RX || !root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      if (!n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      const p = n.parentElement;
      if (!p || p.closest(SKIP) || p.closest("[hidden]")) return NodeFilter.FILTER_REJECT;
      if (excl && p.closest(excl)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  const nodes = []; let n;
  while ((n = walker.nextNode())) nodes.push(n);
  for (const node of nodes) {
    const text = node.nodeValue; RX.lastIndex = 0;
    let m, last = 0, frag = null;
    while ((m = RX.exec(text))) {
      const id = Object.keys(m.groups).find(k => m.groups[k] !== undefined);
      if (!id || used.has(id)) continue;
      used.add(id);
      frag = frag || document.createDocumentFragment();
      frag.append(text.slice(last, m.index));
      const b = document.createElement("button");
      b.type = "button"; b.className = "gl"; b.dataset.g = id; b.textContent = m[0];
      b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-haspopup", "dialog");
      frag.append(b); last = m.index + m[0].length;
    }
    if (frag) { frag.append(text.slice(last)); node.replaceWith(frag); }
  }
}

// Erklärfeld
let pop = null, popFor = null;
function closePop(focusBack) {
  if (!pop) return;
  pop.remove(); pop = null;
  if (popFor) { popFor.setAttribute("aria-expanded", "false"); if (focusBack) popFor.focus(); }
  popFor = null;
}
function openPop(btn) {
  const g = BY_ID[btn.dataset.g]; if (!g) return;
  closePop(false);
  pop = document.createElement("div");
  pop.className = "glpop"; pop.setAttribute("role", "dialog"); pop.setAttribute("aria-label", g.t);
  const onGlossar = /glossar\.html$/.test(location.pathname);
  pop.innerHTML = `<b></b><p></p><span class="glmore">${onGlossar ? "" : `<a href="glossar.html#${g.id}">Alle Begriffe im Glossar</a>`}</span><button type="button" class="glx" aria-label="Schließen">×</button>`;
  pop.querySelector("b").textContent = g.t;
  pop.querySelector("p").textContent = g.d;
  document.body.appendChild(pop);
  const r = btn.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
  let x = r.left + scrollX, y = r.bottom + scrollY + 6;
  x = Math.max(scrollX + 16, Math.min(x, scrollX + document.documentElement.clientWidth - w - 16));
  if (r.bottom + h + 12 > innerHeight && r.top - h - 6 > 0) y = r.top + scrollY - h - 6;
  pop.style.left = x + "px"; pop.style.top = y + "px";
  btn.setAttribute("aria-expanded", "true"); popFor = btn;
  pop.querySelector(".glx").addEventListener("click", () => closePop(true));
}
document.addEventListener("click", e => {
  const b = e.target.closest && e.target.closest("button.gl");
  if (b) { e.preventDefault(); e.stopPropagation(); if (popFor === b) closePop(false); else openPop(b); return; }
  if (pop && !pop.contains(e.target)) closePop(false);
}, true);
document.addEventListener("keydown", e => { if (e.key === "Escape" && pop) closePop(true); });
addEventListener("resize", () => closePop(false));

// Kontextzeile auf Seiten ohne Einführungskasten
function addContext() {
  if (document.getElementById("intro") || document.querySelector(".ctx")) return;
  const header = document.querySelector("header"); if (!header) return;
  const navs = header.querySelectorAll("nav"); const after = navs[navs.length - 1]; if (!after) return;
  const p = document.createElement("p"); p.className = "ctx";
  p.innerHTML = 'Feldwebel Wilhelm Luchmann 1866 und 1870/71. Neu im Thema? <a href="index.html#intro">Worum es geht</a> · <a href="glossar.html">Glossar</a>';
  after.after(p);
}

// Belege einklappen: Inhalt zuerst, Belegstatus und Quellen auf Wunsch
const ORDER = ["wid", "self", "one", "part", "ok"];
function foldEvidence() {
  const boxes = document.querySelectorAll(".card, .stat");
  let count = 0;
  boxes.forEach(box => {
    const items = [...box.children].filter(c => c.matches(".meta, .why"));
    if (!items.length) return;
    const d = document.createElement("details"); d.className = "belege";
    const s = document.createElement("summary");
    s.append("Belege");
    const kinds = new Set();
    items.forEach(it => it.querySelectorAll(".b").forEach(b => ORDER.forEach(k => b.classList.contains(k) && kinds.add(k))));
    ORDER.filter(k => kinds.has(k)).forEach(k => {
      const src = items.map(it => it.querySelector(".b." + k)).find(Boolean);
      const c = src.cloneNode(true); c.setAttribute("aria-hidden", "false"); s.append(c);
    });
    const inner = document.createElement("div"); inner.className = "belin";
    items.forEach(it => inner.appendChild(it));
    d.append(s, inner); box.appendChild(d); count++;
  });
  if (!count) return;
  // Legende „Belegstatus“ einklappen
  const st = document.getElementById("stH");
  if (st) {
    const sec = st.closest("section");
    const d = document.createElement("details"); d.className = "statuslegend";
    const s = document.createElement("summary"); s.textContent = "Wie die Aussagen belegt sind";
    d.appendChild(s);
    [...sec.children].filter(c => c !== st).forEach(c => d.appendChild(c));
    st.remove(); sec.appendChild(d);
    sec.removeAttribute("aria-labelledby"); sec.setAttribute("aria-label", "Belegstatus");
  }
  // Schalter „Alle Belege zeigen“ am Ablauf
  const tl = document.getElementById("tlH");
  if (tl) {
    const head = document.createElement("div"); head.className = "belhead";
    tl.replaceWith(head); head.appendChild(tl);
    const btn = document.createElement("button"); btn.type = "button"; btn.className = "beltoggle";
    btn.textContent = "Alle Belege zeigen"; btn.setAttribute("aria-pressed", "false");
    btn.addEventListener("click", () => {
      const on = btn.getAttribute("aria-pressed") !== "true";
      document.querySelectorAll("details.belege").forEach(x => x.open = on);
      btn.setAttribute("aria-pressed", String(on)); btn.textContent = on ? "Belege ausblenden" : "Alle Belege zeigen";
    });
    head.appendChild(btn);
  }
  // Sprung zu einem Beleg: zugehöriges Feld öffnen
  const openFor = () => { const t = location.hash && document.getElementById(location.hash.slice(1)); const d = t && t.closest("details"); if (d) d.open = true; };
  addEventListener("hashchange", openFor); openFor();
}

function init() {
  addContext();
  foldEvidence();
  const wrap = document.querySelector(".wrap") || document.body;
  // Kartenpanel und dynamische Listen werden neu gefüllt: dort bei jeder Änderung neu markieren
  const panel = document.getElementById("panel");
  markIn(wrap, new Set(), "#panel, [data-gl-dynamic]");
  const dyn = [...document.querySelectorAll("[data-gl-dynamic]")];
  if (panel) dyn.push(panel);
  dyn.forEach(el => {
    const run = () => { mo.disconnect(); markIn(el, new Set()); mo.observe(el, { childList: true, subtree: true }); };
    const mo = new MutationObserver(() => { clearTimeout(run.t); run.t = setTimeout(run, 30); });
    run();
  });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
