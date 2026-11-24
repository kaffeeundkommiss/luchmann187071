#!/usr/bin/env python3
"""Erzeugt alle Seiten der Luchmann-Website aus werkzeuge/daten.py.
Aufruf im Repo-Ordner: python3 werkzeuge/bau.py
Grundkarte neu: cd werkzeuge && npm i d3-geo topojson-client world-atlas && node grundkarte.mjs (Natural-Earth-Flüsse siehe grundkarte.mjs)."""
import json, os, re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
import sys; sys.path.insert(0, str(ROOT / "werkzeuge"))
from daten import SRC, BEL, STEPS, PERSONS, GLOSSAR

BASE = "https://kaffeeundkommiss.github.io/luchmann187071/"
E = lambda t: html.escape(str(t), quote=True)
SUBSTYLE = (ROOT / "werkzeuge" / "seiten.css").read_text()
INDEXSTYLE = (ROOT / "werkzeuge" / "karte.css").read_text()

PAGES = [("index.html", "Übersicht"), ("karte-1866.html", "Karte 1866"), ("karte-1870.html", "Karte 1870/71"), ("abgleich.html", "Abgleich"), ("personen.html", "Personen"), ("tagebuch.html", "Tagebuch")]
NAMES = json.load(open("werkzeuge/orte-namen.json"))

PFAD_A = '<nav class="kk-pfad" aria-label="Pfad"><div class="kk-in"><a href="https://kaffeeundkommiss.github.io/geschichte/">Geschichte</a> › <a href="https://kaffeeundkommiss.github.io/geschichte/einigungskriege/">Einigungskriege 1864–1871</a> › '
VORSCHAU = re.compile(r'<!-- Vorschau für Linkvorschauen, erzeugt mit werkzeuge/vorschau\.js -->\n(?:<meta (?:property="og:image|name="twitter:)[^>]*>\n)*')
def close_idx(s,start,tag='div'):
    # start = index of opening tag; return index of matching closing tag
    depth=0
    for m in re.finditer(r'<(/?)%s\b[^>]*>'%tag,s[start:]):
        if m.group(1): depth-=1
        else: depth+=1
        if depth==0: return start+m.start(), start+m.end()
    raise SystemExit('unbalanced')
def _umbau(s):
    i=s.find('<div class="wrap">')
    if i>=0:
        a,b=close_idx(s,i)
        s=s[:a]+'</main>'+s[b:]
        s=s[:i]+'<main class="wrap" id="inhalt">'+s[i+len('<div class="wrap">'):]
    if '<h2 class="evtitle">' in s and re.search(r'<h1>',s):
        s=re.sub(r'<h1>(.*?)</h1>',r'<p class="h1">\1</p>',s,count=1)
        s=re.sub(r'<h2 class="evtitle">(.*?)</h2>',r'<h1 class="evtitle">\1</h1>',s,count=1)
    s=s.replace('\nh1 { font:','\nh1, .h1 { font:')
    s=s.replace('.evhead h2.evtitle {','.evhead .evtitle {')
    s=s.replace('summary,h1,h2,h3,nav,','summary,h1,.h1,h2,h3,nav,')
    return s

# Glossar: Seitentitel als h1 wie auf der Richthofen-Seite
def schreib(fn, h):
    h = _umbau(h)
    """Schreibt eine Seite und übernimmt den Vorschau-Block (og:image) aus der bisherigen Datei.
    Er wird von werkzeuge/vorschau.js erzeugt; nach Änderungen an Titel oder Beschreibung dort neu ausführen."""
    alt = Path(fn)
    m = VORSCHAU.search(alt.read_text(encoding="utf-8")) if alt.exists() else None
    if m:
        h = re.sub(r'(<meta property="og:url"[^>]*>\n)', lambda x: x.group(1) + m.group(0), h, count=1)
    Path(fn).write_text(h)

def pfad(fn):
    """Pfad zur Themenübersicht unter der Leiste."""
    letzt = '<span aria-current="page">Feldwebel Luchmann</span>' if fn == "index.html" else '<a href="./">Feldwebel Luchmann</a>'
    return PFAD_A + letzt + "</div></nav>\n"

def head(fn, title, desc, style, breit=False):
    return f"""<!doctype html>
<html lang="de" class="kk-b-gesch{' kk-breit' if breit else ''}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{'' if fn == 'index.html' else fn}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Geschichte">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{BASE}{'' if fn == 'index.html' else fn}">
<meta name="theme-color" content="#23211C" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#12110E" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Luchmann 1866–71">
<link rel="icon" href="icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="site.css">
<title>{E(title)}</title>
<link rel="stylesheet" href="https://kaffeeundkommiss.github.io/schriften/schriften.css">
<link rel="stylesheet" href="basis.css">
<style>{style}</style>
<link rel="stylesheet" href="bereich.css">
</head>
<body>
<div class="kk-leiste"><div class="kk-in">
  <a class="kk-haus" href="https://kaffeeundkommiss.github.io/"><img src="kk-tasse.svg" alt="" width="22" height="22"><span>Kaffee und Kommiss</span></a>
  <nav class="kk-bereiche" aria-label="Bereiche"><a href="https://kaffeeundkommiss.github.io/geschichte/" aria-current="true">Geschichte</a><a href="https://kaffeeundkommiss.github.io/sicherheitspolitik/"><span class="kk-lang">Sicherheitspolitik</span><span class="kk-kurz">Sicherheit</span></a><a href="https://kaffeeundkommiss.github.io/politik/">Politik</a></nav>
</div></div>
{pfad(fn)}<div class="kk-kopf"><div class="kk-in">
  <a class="kk-schild" href="https://kaffeeundkommiss.github.io/geschichte/einigungskriege/"><img src="icons/favicon.svg" alt="" width="44" height="44"><span><span class="kk-name" style="display:block">Deutsche Einigungskriege</span><span class="kk-unter" style="display:block">Feldwebel Wilhelm Luchmann 1866 und 1870/71</span></span></a>
</div></div>
<div class="wrap">
"""

FOOT = """<footer class="kk-fuss"><div class="kk-in">
  <p><a href="https://kaffeeundkommiss.github.io/">Kaffee und Kommiss</a>: Geschichte, Sicherheitspolitik und Politik mit Quellen. Private, nichtkommerzielle Zusammenstellung. Fehler gefunden? Bitte mit Quelle melden.</p>
</div></footer>
</body>
</html>
"""

def nav(cur, current_attr="page"):
    return '    <nav class="pages" aria-label="Seiten">\n' + "\n".join(
        f'      <a href="{f}"' + (f' aria-current="{current_attr}"' if f == cur else "") + f">{n}</a>" for f, n in PAGES) + "\n    </nav>\n"

def brand():
    return """    <div class="brand">
      <div class="brand-text">
        <div class="eyebrow">Deutscher Krieg 1866 · Deutsch-Französischer Krieg 1870/71</div>
        <h1>Die Kriegserlebnisse des Feldwebels Luchmann</h1>
      </div>
    </div>
"""

def evhead(eyebrow, title, lede):
    return f"""    <div class="evhead">
      <div class="eyebrow">{eyebrow}</div>
      <h2 class="evtitle">{title}</h2>
    </div>
    <p class="lede">{lede}</p>
"""

def tail(qpage, extra=""):
    return f'  <p class="qnav"><a class="qbtn" href="{qpage}">Quellen</a></p>\n</div>\n<script src="site.js" defer></script>\n{extra}' + FOOT

BADGE = {"2": ("ok", "bestätigt"), "1": ("part", "Regimentsgeschichte"), "x": ("wid", "abweichend"), "s": ("self", "nur Tagebuch")}
SRC_KEYS = list(SRC.keys())
def srcno(k): return f"Q{SRC_KEYS.index(k) + 1}"

STATUS_LEGEND = """  <section class="sect" aria-labelledby="stH">
    <h2 id="stH">Abgleich</h2>
    <ul class="status">
      <li><span class="b ok">bestätigt</span>Regimentsgeschichte und eine zweite Quelle stimmen mit dem Tagebuch überein</li>
      <li><span class="b part">Regimentsgeschichte</span>nur die Regimentsgeschichte von 1875 bestätigt, nicht ausreichend belegt</li>
      <li><span class="b wid">abweichend</span>Datum, Ort oder Zahl weichen ab</li>
      <li><span class="b self">nur Tagebuch</span>nicht geprüft oder in keiner Quelle gefunden</li>
    </ul>
    <p class="note">Das Tagebuch ist ein Selbstzeugnis, Jahre nach den Ereignissen niedergeschrieben. Die Regimentsgeschichte von 1875 ist unabhängig davon entstanden, stützt sich aber auf Meldungen aus dem Regiment, zu denen auch Luchmanns gehört haben können. Schlachtdaten sind zusätzlich mit Wikipedia abgeglichen.</p>
  </section>
"""

# ---------- Kartendaten ----------
CONTROLS_PANEL_VORLAGE = """    <section class="controls" aria-label="Zeitleiste">
      <div class="btns">
        <div class="btns-main">
          <button type="button" id="prev" aria-label="Vorheriger Schritt">◀ Zurück</button>
          <button type="button" class="primary" id="play">▶ Abspielen</button>
          <button type="button" id="next" aria-label="Nächster Schritt">Weiter ▶</button>
        </div>
        <div class="btns-sub">
          <button type="button" id="reset">Anfang</button>
          <span class="nowdate" id="nowDate" aria-live="off" title="Dargestelltes Datum"></span>
          <label class="speed" for="speedSel">Tempo
            <select id="speedSel"><option value="5200">langsam</option><option value="3600" selected>normal</option><option value="2200">schnell</option></select>
          </label>
        </div>
      </div>
      <div class="ruler" id="ruler"><div class="axis"></div><div class="prog" id="prog"></div><div class="playhead" id="playhead"></div></div>
    </section>

    <section class="panel" id="panel" aria-label="Ausgewählter Schritt" aria-live="polite">
      <div class="count"><span id="pCount"></span><span id="pFront"></span></div>
      <h2 id="pName"></h2>
      <div class="sub" id="pSub"></div>
      <div class="dates" id="pDates"></div>
      <blockquote class="zitat" id="pQuote"></blockquote>
      <p id="pText"></p>
      <p class="check" id="pCheck"></p>
      <details class="belege" id="pBel">
        <summary>Quellen und Anmerkungen <span class="bel" id="pBelS"></span></summary>
        <div class="belin">
          <p class="note" id="pNote"></p>
          <div class="src" id="pSrc"></div>
        </div>
      </details>
    </section>
    <details class="legend-m" id="legendM"><summary>Legende</summary></details>
  </section>

  <section class="hinweise" aria-label="Hinweise zur Karte">
    {SO_LIEST}
  </section>

  <section>
    <details class="chron" id="chron">
    <summary><h3>Chronologie</h3><span class="cnt"><span id="chronN"></span> Einträge</span><span class="tgl" aria-hidden="true"><span class="op">Aufklappen</span><span class="cl">Zuklappen</span></span></summary>
    <div class="list">
      <table>
        <thead><tr><th>Nr.</th><th>Datum</th><th>Ereignis / Ort</th><th>Abgleich</th></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    </details>
  </section>

"""


MAPINFO = {
  "1866": dict(file="karte-1866.html", label="Karte 1866", feldzug="Feldzug 1866", jahre="1864–1867", minKm=100, vilKm=230,
    aria="Karte von Brandenburg, Sachsen, Böhmen und Mähren mit Wilhelm Luchmanns Weg 1864 bis 1867",
    lede="Von der Garnison Schrimm über den Einmarsch in Böhmen, Gitschin und Königgrätz bis vor Wien, dann zurück über Prag nach Sachsen und Sorau. Dazu die Jahre 1864 und 1865 vor dem Krieg.",
    other=("karte-1870.html", "Weiter zur Karte 1870/71")),
  "1870": dict(file="karte-1870.html", label="Karte 1870/71", feldzug="Feldzug 1870/71", jahre="1870–1871", minKm=120, vilKm=260,
    aria="Karte von Nordfrankreich und dem Rheinland mit Wilhelm Luchmanns Weg 1870 und 1871",
    lede="Mit der Bahn an die Saar, dann Spichern, Mars-la-Tour, die Belagerung von Metz, die Eilmärsche zur Loire, Beaune-la-Rolande, Orléans und der Winterfeldzug bis Le Mans.",
    other=("karte-1866.html", "Zurück zur Karte 1866")),
}
CAMP_STEPS = {c: [i for i, s in enumerate(STEPS) if s["camp"] == c] for c in MAPINFO}
def step_link(i):
    c = STEPS[i]["camp"]; return f'{MAPINFO[c]["file"]}#s{CAMP_STEPS[c].index(i) + 1}'

def build_data(camp):
    g = json.load(open(f"werkzeuge/karte-{camp}.json"))
    W, H = g["W"], g["H"]
    steps_c = [s for s in STEPS if s["camp"] == camp]
    inside = lambda p: -8 <= p[0] <= W + 8 and -8 <= p[1] <= H + 8
    route = [k for s in steps_c for k in s["moves"]]
    off = [k for k in route if not inside(g["pts"][k])]
    names = {k: NAMES[k] for k in set(route) | set(k for s in steps_c for k in s.get("via", []))}
    if off:
        # Orte außerhalb des Ausschnitts (1870: Sorau, Berlin, Braunschweig) laufen in einem Randpunkt zusammen
        j = max(route.index(k) for k in off)
        o, q = g["pts"][route[j]], g["pts"][route[j + 1]]
        m = 26; t0 = 0.0
        for n in range(1, 401):
            t = n / 400; p = [o[0] + (q[0] - o[0]) * t, o[1] + (q[1] - o[1]) * t]
            if m <= p[0] <= W - m and m <= p[1] <= H - m: t0 = t; break
        g["pts"]["rand"] = [round(o[0] + (q[0] - o[0]) * t0, 1), round(o[1] + (q[1] - o[1]) * t0, 1)]
        seen = []
        for k in off:
            if NAMES[k] not in seen: seen.append(NAMES[k])
        names["rand"] = ", ".join(seen) + " ↗"
    steps = []
    for s in steps_c:
        mv = []
        for k in s["moves"]:
            k = "rand" if k in off else k
            if not mv or mv[-1] != k: mv.append(k)
        d = {k: s[k] for k in ("camp", "date", "dl", "title", "sub", "text", "check", "bel", "src", "note")}
        d["moves"] = mv
        if s.get("quote"): d["quote"] = list(s["quote"])
        if s.get("dash"): d["dash"] = True
        if s.get("mark"): d["mark"] = list(s["mark"])
        if s.get("via"): d["lab"] = s["via"]
        steps.append(d)
    used = set(k for s in steps for k in s["moves"]) | set(k for s in steps for k in s.get("lab", []))
    g["pts"] = {k: v for k, v in g["pts"].items() if k in used}
    g["cities"] = [c for c in g["cities"] if c["k"] not in used]
    I = MAPINFO[camp]
    kd = {"map": g, "steps": steps, "names": names, "camp": camp, "minKm": I["minKm"], "vilKm": I["vilKm"], "qpage": "quellen-karte.html",
          "bel": BEL, "belShort": {k: v[1] for k, v in BADGE.items()},
          "srcNo": {k: srcno(k) for k in SRC}, "srcShort": {k: short_src(k) for k in SRC}}
    Path(f"karte-daten-{camp}.js").write_text("/* erzeugt mit werkzeuge/bau.py */\nwindow.KD = " + json.dumps(kd, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return g

def short_src(k):
    return {"tb": "Tagebuch Luchmann", "rg": "Mueller 1875, Regimentsgeschichte", "gw": "GenWiki", "wp-reg": "Wikipedia: Gren.-Rgt. 12"}.get(k, SRC[k][0].split(" (")[0].replace("Wikipedia (de): ", "Wikipedia: ").rstrip("."))

SO_LIEST = """<p class="how"><b>So liest du die Karte:</b> „Abspielen“ startet den Ablauf, „Weiter“ und „Zurück“ gehen Schritt für Schritt. Die rote Linie zeigt Luchmanns Weg, gestrichelt sind Bahnfahrten und unsichere Wege. ✕ markiert eine Verwundung, ◆ ein anderes Ereignis. Beim Heranzoomen erscheinen Dörfer in heutiger Schreibweise, braune Linien sind Höhenlinien. Grenzen sind heutige, die Landesnamen historisch, beides schematisch. Gepunktet unterstrichene Begriffe lassen sich antippen; alle stehen im <a href="glossar.html">Glossar</a>.</p>"""
MAP_SOURCES = "Grundkarte: Natural Earth (gemeinfrei), heutige Grenzen. Höhenlinien: Terrain Tiles (AWS Open Data, u. a. SRTM), geglättet. Dörfer: GeoNames über cities.json (CC BY 4.0), Auswahl nahe am Weg."

def build_map(camp):
    I = MAPINFO[camp]; g = build_data(camp); n = len(CAMP_STEPS[camp])
    other_c = "1870" if camp == "1866" else "1866"
    desc = f"{I['label']}: Feldwebel Wilhelm Luchmanns Weg {I['jahre']} in {n} Stationen, jede mit dem Abgleich gegen die Regimentsgeschichte von 1875."
    h = head(I["file"], f"{I['label']}: Feldwebel Luchmann", desc, INDEXSTYLE, breit=True)
    h += "  <header>\n" + brand() + nav(I["file"]) + "  </header>\n"
    h += f"""
  <details class="intro" id="intro" open>
    <summary><h2>{I['feldzug']}</h2><span class="tgl" aria-hidden="true"><span class="op">Einblenden</span><span class="cl">Ausblenden</span></span></summary>
    <p>{I['lede']} {n} Stationen, jede mit dem Abgleich gegen die Regimentsgeschichte von 1875. Worum es insgesamt geht, steht in der <a href="index.html">Übersicht</a>; der andere Feldzug hat eine eigene <a href="{MAPINFO[other_c]['file']}">{MAPINFO[other_c]['label']}</a>.</p>
  </details>

  <section class="stage">
    <div class="map" id="map">
      <svg id="svg" viewBox="0 0 {g['W']} {g['H']}" role="img" aria-label="{E(I['aria'])}">
        <rect x="-900" y="-900" width="{g['W'] + 1800}" height="{g['H'] + 1800}" fill="var(--sea)"/>
        <path class="grat" id="grat"/>
        <g id="countries"></g>
        <g id="relief" aria-hidden="true"><path class="cont-minor" id="contMinor"/><path class="cont-major" id="contMajor"/></g>
        <path class="borders" id="borders"/>
        <path class="river-s" id="riverS"/>
        <path class="river-l" id="riverL"/>
        <g id="rivLabels" aria-hidden="true"></g>
        <g id="clabels" aria-hidden="true"></g>
        <g id="villages" aria-hidden="true"></g>
        <path class="route-all" id="routeAll"/>
        <path class="trk-old" id="trkOld"/>
        <path class="trk-dash" id="trkDash"/>
        <path class="trk-solid" id="trkSolid"/>
        <g id="places"></g>
        <g id="events"></g>
        <g id="cur"><g class="sc"><circle class="pulse" r="9"/><circle class="cur-ring" r="7"/></g></g>
      </svg>
      <div class="massstab" id="massstab" aria-hidden="true"><span class="ms-lab" id="msLab"></span><span class="ms-bar" id="msBar"></span></div>
      <button class="mapbtn" id="zoomBtn" type="button" aria-pressed="true">Gesamtkarte</button>
    </div>

    <div class="legend legend-bar" aria-label="Legende">
      <span><i></i>Luchmanns Weg</span>
      <span><i class="d"></i>Bahnfahrt, unsicherer Weg</span>
      <span><b class="x w">✕</b>Verwundung</span>
      <span><b class="x">◆</b>Ereignis</span>
      <span><i class="h"></i>Höhenlinie</span>
      <span><i class="r"></i>Fluss</span>
      <span><i class="v"></i>Dorf (beim Zoomen)</span>
      <span><i class="b"></i>Grenze heute</span>
    </div>
"""
    # Bedienteil und Panel aus der bisherigen Vorlage
    h += CONTROLS_PANEL_VORLAGE.replace("{SO_LIEST}", SO_LIEST)
    oth = MAPINFO[other_c]
    h += f"""
  <section class="persons" aria-labelledby="weH">
    <h3 id="weH">{'Der Feldzug 1870/71' if camp == '1866' else 'Der Feldzug 1866'}</h3>
    <p class="more"><a href="{oth['file']}">{I['other'][1]}</a></p>
  </section>
  <section class="persons" aria-labelledby="abH">
    <h3 id="abH">Tagebuch und Regimentsgeschichte</h3>
    <p class="more">Alle geprüften Angaben in einer Übersicht, mit Fundstellen und Abweichungen: <a href="abgleich.html#{'f1866' if camp == '1866' else 'f1870'}">Seite „Abgleich“ öffnen</a></p>
  </section>

  <p class="sources">Datengrundlage: Luchmanns Tagebuch in der Abschrift von 1994 und die Regimentsgeschichte von Hugo von Mueller (1875), dazu Wikipedia für Schlachtdaten. Die Orte sind nach ihrer heutigen Lage eingetragen und auf etwa 1–2 km genau; Wege zwischen den Stationen sind gerade Linien und damit schematisch. {MAP_SOURCES}</p>
"""
    h += f'  <p class="qnav"><a class="qbtn" href="quellen-karte.html">Quellen</a></p>\n</div>\n<script src="karte-daten-{camp}.js"></script>\n<script src="karte.js"></script>\n<script src="site.js" defer></script>\n' + FOOT
    schreib(I["file"], h)

# ---------- Übersicht ----------
OV_PLACES = [("sorau", 6, -6, "start"), ("berlin", 6, 4, "start"), ("prag", -6, 4, "end"), ("koeniggraetz", 6, 4, "start"), ("wien", -6, 4, "end"),
  ("spichern", 6, 12, "start"), ("metz", -6, -4, "end"), ("paris", -6, 4, "end"), ("orleans", 6, 4, "start"), ("lemans", -6, 4, "end")]
OV_NAMES = {"koeniggraetz": "Königgrätz"}

def build_index():
    g = json.load(open("werkzeuge/grund.json")); P = g["pts"]
    desc = f"Feldwebel Wilhelm Luchmann im Deutschen Krieg 1866 und im Deutsch-Französischen Krieg 1870/71: Übersicht, zwei Karten mit {len(STEPS)} Stationen und der Abgleich mit der Regimentsgeschichte von 1875."
    h = head("index.html", "Feldwebel Luchmann 1866 und 1870/71", desc, INDEXSTYLE + OVSTYLE, breit=True)
    h += "  <header>\n" + brand() + nav("index.html") + "  </header>\n"
    h += """
  <section class="intro intro-ov" id="intro" aria-labelledby="woH">
    <h2 id="woH">Worum geht es?</h2>
    <p>Wilhelm Luchmann (1844–1907) aus Luckau diente von 1864 an in der 9. Kompanie des Grenadier-Regiments Prinz Carl von Preußen (2. Brandenburgisches) Nr. 12. Er zog 1866 gegen Österreich und 1870/71 gegen Frankreich. Später schrieb er seine Erlebnisse in einem Heft nieder: „Kriegs-Erlebnisse von 1866 und 1870/71“. Die Familie hat die Handschrift 1994 abgeschrieben und gebunden.</p>
    <p>Für jeden Feldzug gibt es eine eigene Karte, die seinem Text Schritt für Schritt folgt und jede Angabe der Regimentsgeschichte von 1875 gegenüberstellt. Darin wird Luchmann mehrfach namentlich genannt: für Spichern mit dem Eisernen Kreuz II. Klasse, für Mars-la-Tour als Sergeant, der die 9. Kompanie führte und von französischen Reitern umgeritten wurde. Viele Daten und Zahlen im Tagebuch weichen aber ab. Mehr dazu auf den Seiten <a href="abgleich.html">Abgleich</a> und <a href="tagebuch.html">Tagebuch</a>.</p>
  </section>

  <section class="ov" aria-labelledby="ovH">
    <h2 id="ovH" class="ov-h">Übersichtsplan</h2>
    <div class="map ov-map">
"""
    s = f'      <svg viewBox="0 0 {g["W"]} {g["H"]}" role="img" aria-label="Übersichtskarte Mitteleuropas mit Luchmanns Wegen 1866 und 1870/71 und den Ausschnitten der beiden Karten">\n'
    s += f'        <rect x="0" y="0" width="{g["W"]}" height="{g["H"]}" fill="var(--sea)"/>\n        <path class="grat" d="{g["grat"]}"/>\n'
    for c in g["shapes"]: s += f'        <path class="country g-{c["g"]}" d="{c["d"]}"/>\n'
    s += f'        <path class="borders" d="{g["borders"]}"/>\n        <path class="river-s" d="{g["riversSmall"]}"/>\n        <path class="river-l" d="{g["rivers"]}"/>\n'
    for c in g["cl"]: s += f'        <text class="clabel ov-cl" x="{c["p"][0]}" y="{c["p"][1]}" text-anchor="middle">{E(c["n"])}</text>\n'
    for camp in MAPINFO:
        rt = [k for s_ in STEPS if s_["camp"] == camp for k in s_["moves"]]
        s += f'        <path class="ov-route ov-{camp}" d="M' + "L".join(f'{P[k][0]},{P[k][1]}' for k in rt) + '"/>\n'
    for camp, I in MAPINFO.items():
        f = g["frames"][camp]
        lx, ly = f["nw"]
        s += f'        <a href="{I["file"]}" class="frame"><path d="{f["d"]}"/><text x="{lx + 8}" y="{ly + 22}">{E(I["label"])} ›</text></a>\n'
    for k, dx, dy, anc in OV_PLACES:
        x, y = P[k]
        s += f'        <g class="ov-pl"><circle cx="{x}" cy="{y}" r="3"/><text x="{x + dx}" y="{y + dy}" text-anchor="{anc}">{E(OV_NAMES.get(k, NAMES[k]))}</text></g>\n'
    s += "      </svg>\n"
    h += s + "    </div>\n"
    h += '    <p class="ov-note">Die roten Rahmen zeigen die Ausschnitte der beiden Karten; ein Klick öffnet sie. Wege als gerade Linien zwischen den Stationen, heutige Grenzen.</p>\n  </section>\n'
    h += '  <section class="feldzuege" aria-label="Die beiden Feldzüge">\n'
    for camp, I in MAPINFO.items():
        st = [STEPS[i] for i in CAMP_STEPS[camp]]
        nb = {k: sum(1 for x in st if x["bel"] == k) for k in BADGE}
        key = "Gitschin, Königgrätz, Parade auf dem Marchfeld, Besatzung in Sachsen" if camp == "1866" else "Spichern, Mars-la-Tour, Gravelotte, Metz, Beaune-la-Rolande, Orléans, Le Mans"
        h += f"""    <a class="fz" href="{I['file']}">
      <span class="fz-k">{I['feldzug']}</span>
      <span class="fz-t">{I['label']}</span>
      <span class="fz-d">{I['jahre']} · {len(st)} Stationen · {nb['2'] + nb['1']} bestätigt, {nb['x']} abweichend</span>
      <span class="fz-x">{E(I['lede'])}</span>
      <span class="fz-s">Schwerpunkte: {key}</span>
      <span class="fz-go">Karte öffnen ›</span>
    </a>
"""
    h += "  </section>\n"
    h += """
  <section class="persons" aria-labelledby="abH">
    <h3 id="abH">Tagebuch und Regimentsgeschichte</h3>
    <p class="more">Alle geprüften Angaben beider Feldzüge, mit Fundstellen und Abweichungen: <a href="abgleich.html">Seite „Abgleich“ öffnen</a></p>
  </section>
  <section class="persons" aria-labelledby="peH">
    <h3 id="peH">Personen</h3>
    <p class="more">Luchmanns Lebenslauf und die Offiziere und Kameraden, die er nennt: <a href="personen.html">Seite „Personen“ öffnen</a></p>
  </section>
  <section class="persons" aria-labelledby="tbH">
    <h3 id="tbH">Das Tagebuch</h3>
    <p class="more">Handschrift, Abschrift von 1994, die Bilder der Familienchronik und wie zuverlässig der Text ist: <a href="tagebuch.html">Seite „Tagebuch“ öffnen</a></p>
  </section>
"""
    n66 = len(CAMP_STEPS["1866"])
    h += f'  <p class="qnav"><a class="qbtn" href="quellen-karte.html">Quellen</a></p>\n</div>\n<script>\n/* frühere Verweise auf index.html#sN führen auf die passende Karte */\n(function () {{ var m = /^#s(\\d+)$/.exec(location.hash); if (!m) return; var n = +m[1]; location.replace(n <= {n66} ? "karte-1866.html#s" + n : "karte-1870.html#s" + (n - {n66})); }})();\n</script>\n<script src="site.js" defer></script>\n' + FOOT
    schreib("index.html", h)

OVSTYLE = """
.intro-ov { display: grid; gap: 8px }
.intro-ov h2 { margin: 0; font: 700 22px/1.1 var(--f-display); text-transform: uppercase; letter-spacing: .03em }
.intro-ov p { margin: 0 }
.ov { display: grid; gap: 8px }
.ov-h { margin: 0; font: 700 22px/1.1 var(--f-display); text-transform: uppercase; letter-spacing: .03em }
.ov-map svg { aspect-ratio: auto !important }
.ov-route { fill: none; stroke: var(--red); stroke-width: 2.2; vector-effect: non-scaling-stroke; stroke-linejoin: round; stroke-linecap: round }
.ov-1870 { stroke-dasharray: none }
.ov-cl { font-size: 14px; opacity: .45 }
.frame path { fill: var(--red-soft); fill-opacity: .25; stroke: var(--red); stroke-width: 2; vector-effect: non-scaling-stroke; transition: fill-opacity .2s }
.frame:hover path, .frame:focus path { fill-opacity: .7 }
.frame text { font: 700 18px var(--f-display); letter-spacing: .04em; text-transform: uppercase; fill: var(--red); paint-order: stroke; stroke: var(--paper); stroke-width: 4px; stroke-linejoin: round }
.ov-pl circle { fill: var(--ink); stroke: var(--paper); stroke-width: 1 }
.ov-pl text { font: 600 13px var(--f-display); fill: var(--ink); paint-order: stroke; stroke: var(--paper); stroke-width: 3px; stroke-linejoin: round }
.ov-note { margin: 0; font-size: 13.5px; color: var(--muted) }
.feldzuege { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr)); gap: 14px }
.fz { display: grid; gap: 6px; align-content: start; background: var(--panel); border: 1px solid var(--rule); border-top: 4px solid var(--red); border-radius: 3px; padding: 14px 16px; color: var(--ink); text-decoration: none; min-width: 0 }
.fz:hover { border-color: var(--border); border-top-color: var(--red) }
.fz-k { font: 600 12px/1 var(--f-display); letter-spacing: .14em; text-transform: uppercase; color: var(--red) }
.fz-t { font: 700 26px/1.05 var(--f-display); text-transform: uppercase; letter-spacing: .02em }
.fz-d { font: 500 13px/1.3 var(--f-mono); color: var(--muted) }
.fz-x { font-size: 15.5px }
.fz-s { font-size: 14px; color: var(--muted) }
.fz-go { font: 600 14px/1 var(--f-display); letter-spacing: .08em; text-transform: uppercase; margin-top: 4px }
"""

# ---------- Abgleich ----------
def build_abgleich():
    desc = "Luchmanns Tagebuch Schritt für Schritt mit der Regimentsgeschichte von 1875 abgeglichen: bestätigte Angaben, Abweichungen bei Daten und Zahlen, Stellen ohne Beleg."
    h = head("abgleich.html", "Abgleich: Tagebuch und Regimentsgeschichte", desc, SUBSTYLE)
    n = {k: sum(1 for s in STEPS if s["bel"] == k) for k in BADGE}
    h += "  <header>\n" + brand() + nav("abgleich.html") + evhead("Quellenkritik", "Tagebuch und Regimentsgeschichte",
        "Für jede Station der Karte ist geprüft, ob die Regimentsgeschichte von 1875 und, bei Schlachtdaten, Wikipedia das Tagebuch bestätigen. Luchmanns Erinnerung ist bei Orten und Abläufen meist genau, bei Daten und Zahlen oft nicht.") + "  </header>\n"
    h += f"""  <section class="sect" aria-label="Zahlen">
    <div class="stats">
      <div class="stat"><div class="num">{len(STEPS)}</div><div class="lbl">Stationen geprüft</div></div>
      <div class="stat"><div class="num">{n['2'] + n['1']}</div><div class="lbl">bestätigt, davon {n['2']} mit zweiter Quelle</div></div>
      <div class="stat red"><div class="num">{n['x']}</div><div class="lbl">mit Abweichungen bei Datum, Ort oder Zahl</div></div>
      <div class="stat"><div class="num">{n['s']}</div><div class="lbl">nur im Tagebuch</div></div>
    </div>
  </section>
""" + STATUS_LEGEND
    h += """  <section class="sect" aria-labelledby="muH">
    <h2 id="muH">Muster der Abweichungen</h2>
    <div class="theses">
      <div class="th lead"><h3>Daten um Tage oder Wochen verschoben</h3><p class="thtext">Ausmarsch „16. Juni“ statt 16. Mai 1866, Königgrätz „2. Juli“ statt 3. Juli, Beaune-la-Rolande „29.“ statt 28. November, Bellegarde „30. November“ statt 2. Dezember, Rückkehr „Juli“ statt Juni 1867.</p></div>
      <div class="th"><h3>Zahlen aufgerundet</h3><p class="thtext">Bei Spichern 300 statt 207 Mann Verlust des Bataillons, in Beaune-la-Rolande 600 statt etwa 400 Gefangene, in Göding 400 bis 500 statt 100 Zigarren je Mann.</p></div>
      <div class="th"><h3>Orte verwechselt oder zusammengezogen</h3><p class="thtext">Parade bei „Nikolsburg“ statt auf dem Marchfeld, der Elbübergang vor statt nach Königgrätz, Mobilmachung und Kriegserklärung am selben Tag.</p></div>
      <div class="th"><h3>Was sich bestätigt</h3><p class="thtext">Wege, Quartiere und Gefechte des Füsilier-Bataillons, die Namen der Offiziere (oft in eigener Schreibung) und Luchmanns eigene Rolle bei Spichern und Mars-la-Tour, die die Regimentsgeschichte namentlich nennt.</p></div>
    </div>
  </section>
"""
    for camp, I in MAPINFO.items():
      idx = CAMP_STEPS[camp]
      nb = {k: sum(1 for i in idx if STEPS[i]["bel"] == k) for k in BADGE}
      h += f"""  <section class="sect" aria-labelledby="f{camp}">
    <h2 id="f{camp}">{I['feldzug']}</h2>
    <p class="hint">{len(idx)} Stationen ({I['jahre']}): {nb['2'] + nb['1']} bestätigt, {nb['x']} abweichend, {nb['s']} nur im Tagebuch. <a href="{I['file']}">{I['label']} öffnen</a></p>
    <ol class="tl">
"""
      for i in idx:
        s = STEPS[i]
        cls, lab = BADGE[s["bel"]]
        h += f"""      <li{' class="key"' if s['bel'] == 'x' else ''}>
        <div class="t">{E(s['dl'])}</div><div class="rail"></div>
        <div class="card" id="s{i + 1}">
          <h3>{E(s['title'])}</h3>
          <p><b>Tagebuch:</b> {E(s['text'])}</p>
          <p class="zit">„{E(s['quote'][0].strip('„“'))}“ <span>({E(s['quote'][1])})</span></p>
          <p><b>Abgleich:</b> {E(s['check'])}</p>
          <div class="meta"><span class="b {cls}">{lab}</span>{''.join(f'<a href="quellen-abgleich.html#q-{k}">{srcno(k)}</a>' for k in s['src'])}<a href="{step_link(i)}">Karte</a></div>
          <p class="why">{E(s.get('note', ''))}</p>
        </div>
      </li>
"""
      h += "    </ol>\n  </section>\n"
    h += '  <p class="note">Die vollständige Belegmatrix mit Fundstellen liegt beim Herausgeber der Website. Wörtliche Zitate aus der Regimentsgeschichte sind in heutige Schreibung übertragen (ſ → s); die Schreibweise der Namen folgt dem Original.</p>\n'
    schreib("abgleich.html", h + tail("quellen-abgleich.html"))

# ---------- Personen ----------
def build_personen():
    desc = "Wilhelm Luchmann (1844–1907) und die Offiziere und Kameraden aus seinem Tagebuch, abgeglichen mit der Regimentsgeschichte von 1875."
    h = head("personen.html", "Personen: Luchmann und seine Kameraden", desc, SUBSTYLE)
    h += "  <header>\n" + brand() + nav("personen.html")
    h += """    <div class="evintro">
      <div class="evtext">
""" + evhead("1844 – 1907", "Wilhelm Luchmann und seine Kameraden",
        "Luchmann stammte aus Luckau in der Niederlausitz, stieg im Regiment vom Grenadier zum Feldwebel auf und wurde nach dem Krieg Bahnbeamter im Saarland. Sein Tagebuch nennt Dutzende Offiziere und Kameraden; viele finden sich in der Regimentsgeschichte wieder.") + """      </div>
      <figure class="evfoto">
        <img src="bilder/titelblatt.jpg" width="807" height="1100" alt="Handschriftliches Titelblatt: Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebel Wilhelm Luchmann bei der 9ten Compagnie Grenadier Regiment Prinz Carl von Preußen (2tes Brandenburgisches) No 12" decoding="async">
        <figcaption>Titelblatt der Handschrift. Ein Foto Luchmanns enthält die Chronik nicht. <a href="quellen-personen.html#f2">Bildnachweis</a></figcaption>
      </figure>
    </div>
  </header>
"""
    h += """  <section class="sect" aria-labelledby="lH">
    <h2 id="lH">Lebenslauf</h2>
    <ol class="tl">
"""
    life = [
      ("28.12.1844", "Geburt in Luckau", "Friedrich Wilhelm Luchmann wird in Luckau, Kreis Luckau, Regierungsbezirk Frankfurt (Oder), geboren. Den 28. Dezember bestätigt das Tagebuch selbst: In Beaugency feiert er am „4ten Feiertag“ Geburtstag.", "self", "nur Tagebuch", "T S. 6–7 und 49. Kein Kirchenbuch eingesehen."),
      ("1864", "Grenadier in Schrimm", "Nach einem Aufenthalt in Russland in die 9. Kompanie des Grenadier-Regiments Nr. 12 eingestellt.", "part", "Regimentsgeschichte", "Garnison bestätigt (RG S. 294, GenWiki); Eintrittsjahr nur Tagebuch."),
      ("1865–1869", "Gefreiter, Unteroffizier, Fourier", "Herbst 1865 Exerzier-Gefreiter, in Sachsen 1866/67 Unteroffizier, verpflichtet sich weiter. 1868 Reitlehrgang beim Dragoner-Regiment Nr. 12 in Frankfurt (Oder), 1869 Fourier beim Königsmanöver bei Berlin und Schwimmmeister.", "self", "nur Tagebuch", "T S. 7 und 17."),
      ("1870", "Sergeant, Eisernes Kreuz", "Bei Spichern unter den besonders Tapferen genannt und mit dem Eisernen Kreuz II. Klasse ausgezeichnet. Bei Mars-la-Tour führt er die 9. Kompanie und wird umgeritten.", "part", "Regimentsgeschichte", "RG S. 442, 450, 466, 469."),
      ("1871", "Feldwebel", "Die Aufzeichnungen enden in Le Mans im Januar 1871. Der Titel nennt ihn „Feldwebel“.", "self", "nur Tagebuch", "T S. 4 und 57."),
      ("nach 1871", "Heirat und Bahndienst", "Rückkehr mit dem Bataillon nach Sorau, Heirat, Ausscheiden aus dem Militär mit Anspruch auf eine Beamtenstelle. Bahnbeamter im Saarland, mit Stationen in Merzig, Saarbrücken, Neunkirchen, Heimbach (Nahe), Stromberg und Völklingen; zuletzt Obergütervorsteher.", "self", "Familie", "Nachwort des Herausgebers der Chronik, S. 62."),
      ("20.01.1907", "Tod in Völklingen", "Luchmann stirbt in Völklingen (Saar).", "self", "Familie", "Nachwort der Chronik, S. 62. Kein Sterberegister eingesehen."),
    ]
    for t, ti, tx, cls, lab, why in life:
        h += f"""      <li>
        <div class="t">{t}</div><div class="rail"></div>
        <div class="card"><h3>{ti}</h3><p>{tx}</p><div class="meta"><span class="b {cls}">{lab}</span><a href="quellen-personen.html#q-tb">{srcno('tb')}</a>{'<a href="quellen-personen.html#q-rg">' + srcno('rg') + '</a>' if 'RG' in why else ''}</div><p class="why">{why}</p></div>
      </li>
"""
    h += "    </ol>\n  </section>\n" + STATUS_LEGEND.replace('id="stH">Abgleich', 'id="stH">Belegstatus')
    h += """  <section class="sect" aria-labelledby="pH">
    <h2 id="pH">Offiziere und Kameraden</h2>
    <p class="hint">In der Reihenfolge ihres Auftretens. Schreibweise nach der Regimentsgeschichte, abweichende Schreibung des Tagebuchs in Anführungszeichen.</p>
    <div class="theses">
"""
    for name, role, tb, chk, bel in PERSONS[1:]:
        cls, lab = BADGE[bel]
        h += f"""      <div class="th card">
        <h3>{E(name)}</h3><p class="who2">{E(role)}</p>
        <dl><dt>Tagebuch</dt><dd>{E(tb)}</dd></dl>
        <div class="meta"><span class="b {cls}">{lab}</span><a href="quellen-personen.html#q-tb">{srcno('tb')}</a>{'' if bel == 's' else '<a href="quellen-personen.html#q-rg">' + srcno('rg') + '</a>'}</div>
        <p class="why">{E(chk)}</p>
      </div>
"""
    h += "    </div>\n  </section>\n"
    h += '  <p class="note">Die Seite nennt aus der Familie nur Wilhelm Luchmann und die Herausgeber der Chronik. Die Personen aus dem Tagebuch sind Soldaten des 19. Jahrhunderts.</p>\n'
    schreib("personen.html", h + tail("quellen-personen.html"))

# ---------- Tagebuch ----------
def build_tagebuch():
    desc = "Die Handschrift „Kriegs-Erlebnisse von 1866 und 1870/71“ des Feldwebels Wilhelm Luchmann: Entstehung, Abschrift von 1994, Bilder der Familienchronik und Zuverlässigkeit."
    h = head("tagebuch.html", "Das Tagebuch des Feldwebels Luchmann", desc, SUBSTYLE)
    h += "  <header>\n" + brand() + nav("tagebuch.html") + evhead("Quelle", "Das Tagebuch und die Familienchronik",
        "Luchmanns Aufzeichnungen sind kein tägliches Kriegstagebuch, sondern eine spätere Erzählung in deutscher Schrift. Seine Familie hat sie 1994 in lateinische Schrift übertragen, mit Karten und Erläuterungen ergänzt und binden lassen.") + "  </header>\n"
    h += """  <section class="sect" aria-labelledby="hH">
    <h2 id="hH">Handschrift und Abschrift</h2>
    <div class="gal">
      <figure><img src="bilder/umschlag.jpg" width="825" height="1100" alt="Roter Bucheinband mit goldener Frakturschrift: Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebels Wilhelm Luchmann" loading="lazy" decoding="async"><figcaption>Einband der Familienchronik, 1994. <a href="quellen-tagebuch.html#f1">F1</a></figcaption></figure>
      <figure><img src="bilder/titelblatt.jpg" width="807" height="1100" alt="Vergilbtes handschriftliches Titelblatt in deutscher Schrift" loading="lazy" decoding="async"><figcaption>Titelblatt der Handschrift. <a href="quellen-tagebuch.html#f2">F2</a></figcaption></figure>
      <figure><img src="bilder/handschrift-1866.jpg" width="808" height="1100" alt="Erste Textseite der Handschrift in deutscher Schrift" loading="lazy" decoding="async"><figcaption>Erste Seite: Geburt in Luckau, Eintritt 1864 in Schrimm. <a href="quellen-tagebuch.html#f3">F3</a></figcaption></figure>
      <figure><img src="bilder/handschrift-1870.jpg" width="808" height="1100" alt="Handschriftseite mit der Überschrift Der Feldzug 1870/71" loading="lazy" decoding="async"><figcaption>Beginn des Teils „Der Feldzug 1870/71“. <a href="quellen-tagebuch.html#f4">F4</a></figcaption></figure>
    </div>
    <div class="theses">
      <div class="th lead"><h3>Die Handschrift</h3><p class="thtext">Ein Heft in deutscher Schreibschrift mit dem Titel „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebel Wilhelm Luchmann“. Wann Luchmann es schrieb, ist unbekannt. Es muss nach 1871 entstanden sein: Er nennt Ereignisse „nach Rückkehr in die Garnison“ und spricht vom Kaiser. Das Original kam 1991 aus dem Nachlass eines Verwandten an den Herausgeber.</p></div>
      <div class="th"><h3>Die Abschrift von 1994</h3><p class="thtext">Gertrud Luchmann übertrug den Text im Sommer 1994 von Hand in lateinische Schrift, nach Angabe des Herausgebers ohne Korrekturen. Einzelne Namen und Wörter waren unleserlich oder verblasst. Gerd Luchmann gab die Abschrift im November 1994 in Trier als gebundene Familienchronik heraus, mit Marschrouten, zwei Karten aus Atlanten, zwei Gemälden und kurzen Texten aus Geschichtsbüchern.</p></div>
      <div class="th"><h3>Was Luchmann erzählt</h3><p class="thtext">Gefechte, Märsche und Quartiere, aber vor allem Episoden: Streiche, Wein, Kartenspiel, Mädchen, Hunger. Er schildert auch Gewalt gegen Zivilisten: angezündete Gehöfte, einen erschossenen Bauern, einen misshandelten Geistlichen, den Straßenkampf in Parigné. Diese Stellen gibt die Seite wieder, ohne sie zu übernehmen.</p></div>
      <div class="th"><h3>Wie zuverlässig?</h3><p class="thtext">Wege, Quartiere, Gefechte und Namen stimmen meist mit der Regimentsgeschichte überein, oft bis in Einzelheiten. Daten liegen häufig Tage oder Wochen daneben, Zahlen sind aufgerundet. Seine eigene Rolle bei Spichern und Mars-la-Tour bestätigt die Regimentsgeschichte namentlich. Viele Anekdoten lassen sich nicht prüfen. Siehe <a href="abgleich.html">Abgleich</a>.</p></div>
    </div>
  </section>
  <section class="sect" aria-labelledby="bH">
    <h2 id="bH">Bilder der Chronik</h2>
    <p class="hint">Die Chronik ordnet zwei farbige Gemälde den Marschrouten zu: „Belagerung von Metz (siehe Bild)“ und „Schlacht von Orleans (siehe Bild)“. Maler, Titel und Herkunft der Bilder nennt sie nicht; sie konnten nicht ermittelt werden. Ob die Bilder diese Ereignisse zeigen, ist deshalb offen.</p>
    <div class="gal gal2">
      <figure><img src="bilder/gemaelde-metz.jpg" width="825" height="1100" alt="Gemälde: brennendes Gebäude bei Nacht, davor Infanterie im Gefecht, Gefallene im Vordergrund" loading="lazy" decoding="async"><figcaption>Der „Belagerung von Metz“ zugeordnet. Maler nicht ermittelt. <a href="quellen-tagebuch.html#f5">F5</a></figcaption></figure>
      <figure><img src="bilder/gemaelde-orleans.jpg" width="1100" height="825" alt="Gemälde: preußische Infanterie mit Fahne stürmt an einem Waldrand vor, Verwundete am Boden" loading="lazy" decoding="async"><figcaption>Der „Schlacht von Orleans“ zugeordnet, doppelseitig. Maler nicht ermittelt. <a href="quellen-tagebuch.html#f6">F6</a></figcaption></figure>
    </div>
    <p class="note">Nicht übernommen wurden die beiden Karten der Chronik, eine Schulatlas-Karte zu 1866 und eine Straßenkarte zu 1870/71: Sie stammen aus gedruckten Atlanten. Die Karten dieser Website sind neu gezeichnet.</p>
  </section>
  <section class="sect" aria-labelledby="zH">
    <h2 id="zH">Kostproben</h2>
    <div class="theses">
      <div class="th"><p class="zit">„… da tritt auch schon der König Wilhelm dicht neben mir und bleibt stehen, seine Suite hinter ihm.“</p><p class="who2">Brünn, 15. Juli 1866 (T S. 14)</p></div>
      <div class="th"><p class="zit">„Da standen die Haare wie Besenreiser in die Höhe und das Testament war schon gemacht, doch Unkraut vergeht nicht.“</p><p class="who2">Reiterangriff bei Mars-la-Tour, 16. August 1870 (T S. 26)</p></div>
      <div class="th"><p class="zit">„Kein Auge blieb trocken …“</p><p class="who2">Feldgottesdienst am Abend nach Mars-la-Tour (T S. 27)</p></div>
      <div class="th"><p class="zit">„… welcher Contrast von vor 8 Tagen und heute, damals Braten, Kuchen, Wein die Hülle und Fülle und Sprungfederbett …“</p><p class="who2">Vendôme, 6. Januar 1871 (T S. 49)</p></div>
    </div>
    <p class="note">Zitate in der Schreibung der Abschrift von 1994. Die Texterkennung des eingescannten Buchs kann einzelne Zeichen verfälscht haben; die Zitate sind mit dem Bild der Seite verglichen.</p>
  </section>
"""
    schreib("tagebuch.html", h + tail("quellen-tagebuch.html"))

# ---------- Glossar ----------
def build_glossar():
    desc = "Begriffe zu Luchmanns Kriegserlebnissen 1866 und 1870/71: Dienstgrade, Waffen, Truppen und Lagerleben."
    h = head("glossar.html", "Glossar: Begriffe zu 1866 und 1870/71", desc, SUBSTYLE + "\n.gloss { display: grid; gap: 12px; margin: 0 } .gloss > div { background: var(--panel); border: 1px solid var(--rule); border-radius: 3px; padding: 10px 14px } .gloss dt { font: 700 18px/1.2 var(--f-display); text-transform: uppercase; letter-spacing: .03em } .gloss dd { margin: 4px 0 0 } .gloss .gsrc { font-size: 13.5px; color: var(--muted) } .gloss .gsrc a { color: var(--ink) } .gloss > div:target { outline: 3px solid var(--red-soft) }\n")
    h += "  <header>\n" + brand().replace("Deutscher Krieg 1866 · Deutsch-Französischer Krieg 1870/71", "Begriffe und Abkürzungen").replace("Die Kriegserlebnisse des Feldwebels Luchmann", "Glossar") + nav("glossar.html") + '    <p class="lede">Kurze Erklärungen der Fachbegriffe, die auf den Seiten vorkommen. Auf den anderen Seiten lassen sich die Begriffe beim ersten Vorkommen antippen.</p>\n  </header>\n'
    h += '  <section class="sect" aria-labelledby="gH">\n    <h2 id="gH">Begriffe</h2>\n    <dl class="gloss glnone" id="gloss">\n'
    for gid, t, re_, d in sorted(GLOSSAR, key=lambda g: g[1].lower()):
        h += f'      <div id="{gid}"><dt>{E(t)}</dt><dd>{E(d)}</dd><dd class="gsrc">Worterklärung ohne Einzelbeleg</dd></div>\n'
    h += "    </dl>\n  </section>\n"
    schreib("glossar.html", h + tail("quellen-glossar.html"))

# ---------- Quellenseiten ----------
FIG = [
  ("f1", "Einband der Familienchronik „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebels Wilhelm Luchmann“, Trier 1994 (Chronik S. 1)."),
  ("f2", "Titelblatt der Handschrift Wilhelm Luchmanns, nach 1871 (Chronik S. 4)."),
  ("f3", "Erste Textseite der Handschrift (Chronik S. 6)."),
  ("f4", "Handschriftseite „Der Feldzug 1870/71“ (Chronik S. 20)."),
  ("f5", "Farbiges Gemälde, in der Chronik der Belagerung von Metz zugeordnet (Chronik S. 32). Maler, Titel und Vorlage nicht angegeben und nicht ermittelt."),
  ("f6", "Farbiges Gemälde über zwei Seiten, in der Chronik der Schlacht von Orléans zugeordnet (Chronik S. 41). Maler, Titel und Vorlage nicht angegeben und nicht ermittelt."),
]
FIG_NOTE = "Fotos der Seiten aus dem Exemplar der Familie, zugeschnitten und verkleinert. Veröffentlichung mit Zustimmung der Familie (November 2026)."
FIG_NOTE_GEMAELDE = " Für die beiden Gemälde ist die Rechtelage offen, weil Maler und Vorlage unbekannt sind; Hinweise bitte mit Quelle melden."

def build_quellen(fn, page, title, keys, figs=()):
    desc = f"Quellenverzeichnis zur Seite „{title}“ der Website zu Wilhelm Luchmanns Kriegserlebnissen 1866 und 1870/71."
    h = head(fn, f"Quellen: {title}", desc, SUBSTYLE)
    h += "  <header>\n" + brand() + nav(page, "true") + evhead("Quellen", f"Quellen: {title}",
        f'Quellenverzeichnis zur Seite „{title}“. Die Nummern entsprechen den Verweisen auf der Seite. <a href="{page}">Zurück zur Seite</a>') + "  </header>\n"
    h += '  <section class="sect" aria-label="Quellenverzeichnis">\n    <p class="hint">Alle Quellen am 14.11.2026 eingesehen. Die Regimentsgeschichte wurde im Volltext nach jeder Station und jedem Namen durchsucht; die Belegmatrix mit den Originalpassagen liegt im Projektordner (luchmann/belegmatrix.md).</p>\n    <ol class="srcs">\n'
    for k in keys:
        t, u, dep = SRC[k]
        link = f' <a href="{u}">{E(re.sub(r"^https?://", "", u).split("/")[0]) if u.startswith("http") else "Seite „Tagebuch“"}</a>'
        h += f'      <li id="q-{k}"><span class="id">{srcno(k)}</span><span>{E(t)}{link} <span class="dep">{E(dep)}</span></span></li>\n'
    h += "    </ol>\n  </section>\n"
    if figs:
        h += f'  <section class="sect" aria-labelledby="bildH">\n    <h2 id="bildH">Bildnachweis</h2>\n    <p class="hint">{FIG_NOTE}{FIG_NOTE_GEMAELDE if any(f in ("f5", "f6") for f, _ in figs) else ""}</p>\n    <ol class="srcs">\n'
        for fid, t in figs:
            h += f'      <li id="{fid}"><span class="id">{fid.upper()}</span><span>{E(t)}</span></li>\n'
        h += "    </ol>\n  </section>\n"
    if page == "index.html":
        h += '  <section class="sect" aria-labelledby="kH">\n    <h2 id="kH">Grundkarte</h2>\n    <p class="hint">Grenzen und Küsten: Natural Earth, Admin 0 Countries 1:50 Mio., über das Paket world-atlas (gemeinfrei). Flüsse: Natural Earth, Rivers and Lake Centerlines und Rivers Europe 1:10 Mio. (gemeinfrei). Projektion: konforme Kegelprojektion nach Lambert. Es sind heutige Grenzen; die Landesnamen 1866/1870 sind schematisch gesetzt. Ortskoordinaten: heutige Lage der Orte, eigene Zuordnung.</p>\n    <p class="hint">Detailkarten 1866 und 1870/71: Höhenlinien aus den Terrain Tiles von Mapzen auf AWS Open Data (Zoomstufe 8, Datengrundlage u. a. SRTM), geglättet, Abstand 100 bis 200 m. Dörfer: GeoNames (CC BY 4.0) über die Sammlung cities.json (lutangar/cities.json auf GitHub), automatisch ausgewählt nahe am Weg und in heutiger Schreibweise; erzeugt mit werkzeuge/detail.mjs.</p>\n  </section>\n'
    h += f'  <p class="qnav"><a class="qbtn" href="{page}">Zurück zu „{title}“</a></p>\n</div>\n<script src="site.js" defer></script>\n' + FOOT
    schreib(fn, h)

# ---------- site.js ----------
def build_sitejs():
    s = Path("werkzeuge/site-vorlage.js").read_text()
    gl = ",\n".join(f'  {{ id: {json.dumps(g)}, t: {json.dumps(t, ensure_ascii=False)}, re: {json.dumps(r, ensure_ascii=False)}, src: [],\n    d: {json.dumps(d, ensure_ascii=False)} }}' for g, t, r, d in GLOSSAR)
    s = re.sub(r"const GSRC = \{.*?\n\};", 'const GSRC = {\n  web: ["Angaben dieser Website (Karte und Unterseiten mit eigenen Quellen)", "quellen-karte.html"]\n};', s, flags=re.S)
    s = re.sub(r"const GLOSSAR = \[.*?\n\];", "const GLOSSAR = [\n" + gl + "\n];", s, flags=re.S)
    s = s.replace("Ernst Jünger an der Westfront 1914–1918. Neu im Thema?", "Feldwebel Wilhelm Luchmann 1866 und 1870/71. Neu im Thema?")
    s = re.sub(r"// Quellen der Glossar-Erklärungen.*\n", "// Glossar: reine Worterklärungen ohne Einzelbeleg.\n", s)
    s = re.sub(r"// Begriffe\. re = .*\n// Die Quellen g1.*\n", "// Begriffe (aus werkzeuge/daten.py). re = Suchmuster im Text.\n", s)
    s = s.replace('SKIP = "script,', 'SKIP = "blockquote,.zitat,.zit,script,')
    Path("site.js").write_text(s)

if __name__ == "__main__":
    build_map("1866"); build_map("1870"); build_index(); build_abgleich(); build_personen(); build_tagebuch(); build_glossar(); build_sitejs()
    build_quellen("quellen-karte.html", "index.html", "Übersicht und Karten", ["tb", "rg", "gw", "wp-reg", "wp-gitschin", "wp-kg", "wp-dk", "wp-dfk", "wp-spichern", "wp-mlt", "wp-grav", "wp-metz", "wp-beaune", "wp-orleans", "wp-lemans"])
    build_quellen("quellen-abgleich.html", "abgleich.html", "Abgleich", ["tb", "rg", "gw", "wp-reg", "wp-gitschin", "wp-kg", "wp-dk", "wp-dfk", "wp-spichern", "wp-mlt", "wp-grav", "wp-metz", "wp-beaune", "wp-orleans", "wp-lemans"])
    build_quellen("quellen-personen.html", "personen.html", "Personen", ["tb", "rg"], [FIG[1]])
    build_quellen("quellen-tagebuch.html", "tagebuch.html", "Tagebuch", ["tb", "rg"], FIG)
    build_quellen("quellen-glossar.html", "glossar.html", "Glossar", ["tb", "rg"])
    print("fertig")
