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

PAGES = [("index.html", "Karte"), ("abgleich.html", "Abgleich"), ("personen.html", "Personen"), ("tagebuch.html", "Tagebuch")]
NAMES = json.load(open("werkzeuge/orte-namen.json"))

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="basis.css">
<style>{style}</style>
<link rel="stylesheet" href="bereich.css">
</head>
<body>
<div class="kk-leiste"><div class="kk-in">
  <a class="kk-haus" href="https://kaffeeundkommiss.github.io/"><img src="kk-tasse.svg" alt="" width="22" height="22"><span>Kaffee und Kommiss</span></a>
  <nav class="kk-bereiche" aria-label="Bereiche"><a href="https://kaffeeundkommiss.github.io/geschichte/" aria-current="true">Geschichte</a><a href="https://kaffeeundkommiss.github.io/sicherheitspolitik/"><span class="kk-lang">Sicherheitspolitik</span><span class="kk-kurz">Sicherheit</span></a><a href="https://kaffeeundkommiss.github.io/politik/">Politik</a></nav>
</div></div>
<div class="kk-kopf"><div class="kk-in">
  <a class="kk-schild" href="index.html"><img src="icons/favicon.svg" alt="" width="44" height="44"><span><span class="kk-name" style="display:block">Deutsche Einigungskriege</span><span class="kk-unter" style="display:block">Feldwebel Wilhelm Luchmann 1866 und 1870/71</span></span></a>
</div></div>
<div class="wrap">
"""

FOOT = """<footer class="kk-fuss"><div class="kk-in">
  <p><a href="https://kaffeeundkommiss.github.io/">Kaffee und Kommiss</a>: Politik, Geschichte und Sicherheitspolitik mit Quellen. Private, nichtkommerzielle Zusammenstellung. Fehler gefunden? Bitte mit Quelle melden.</p>
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
def build_data():
    g = json.load(open("werkzeuge/grund.json"))
    used = set(k for s in STEPS for k in s["moves"]) | set(k for s in STEPS for k in s.get("via", []))
    big = ["berlin", "wien", "prag", "paris", "dresden", "leipzig", "muenchen", "frankfurt", "strassburg", "metz", "koeln", "luckau"]
    keep = used | set(big)
    g["pts"] = {k: v for k, v in g["pts"].items() if k in keep}
    steps = []
    for s in STEPS:
        d = {k: s[k] for k in ("camp", "date", "dl", "moves", "title", "sub", "text", "check", "bel", "src", "note")}
        if s.get("quote"): d["quote"] = list(s["quote"])
        if s.get("dash"): d["dash"] = True
        if s.get("mark"): d["mark"] = list(s["mark"])
        if s.get("via"): d["lab"] = s["via"]
        steps.append(d)
    kd = {"map": g, "steps": steps, "names": {k: NAMES[k] for k in keep}, "big": big,
          "bel": BEL, "belShort": {k: v[1] for k, v in BADGE.items()},
          "srcNo": {k: srcno(k) for k in SRC}, "srcShort": {k: short_src(k) for k in SRC}}
    Path("karte-daten.js").write_text("/* erzeugt mit werkzeuge/bau.py */\nwindow.KD = " + json.dumps(kd, ensure_ascii=False, separators=(",", ":")) + ";\n")

def short_src(k):
    return {"tb": "Tagebuch Luchmann", "rg": "Mueller 1875, Regimentsgeschichte", "gw": "GenWiki", "wp-reg": "Wikipedia: Gren.-Rgt. 12"}.get(k, SRC[k][0].split(" (")[0].replace("Wikipedia (de): ", "Wikipedia: ").rstrip("."))

# ---------- index ----------
def build_index():
    desc = f"Karte zu den Kriegserlebnissen des Feldwebels Wilhelm Luchmann 1866 und 1870/71: {len(STEPS)} Stationen vom Einmarsch in Böhmen bis Le Mans, jede mit dem Abgleich gegen die Regimentsgeschichte von 1875."
    h = head("index.html", "Feldwebel Luchmann 1866 und 1870/71", desc, INDEXSTYLE, breit=True)
    h += "  <header>\n" + brand() + nav("index.html") + "  </header>\n"
    h += """
  <details class="intro" id="intro" open>
    <summary><h2>Worum geht es?</h2><span class="tgl" aria-hidden="true"><span class="op">Einblenden</span><span class="cl">Ausblenden</span></span></summary>
    <p>Wilhelm Luchmann (1844–1907) aus Luckau diente von 1864 an in der 9. Kompanie des Grenadier-Regiments Prinz Carl von Preußen (2. Brandenburgisches) Nr. 12. Er zog 1866 gegen Österreich und 1870/71 gegen Frankreich. Später schrieb er seine Erlebnisse in einem Heft nieder: „Kriegs-Erlebnisse von 1866 und 1870/71“. Die Familie hat die Handschrift 1994 abgeschrieben und gebunden.</p>
    <p>Die Karte folgt seinem Text Schritt für Schritt und stellt jede Angabe der Regimentsgeschichte von 1875 gegenüber. Darin wird Luchmann mehrfach namentlich genannt: für Spichern mit dem Eisernen Kreuz II. Klasse, für Mars-la-Tour als Sergeant, der die 9. Kompanie führte und von französischen Reitern umgeritten wurde. Viele Daten und Zahlen im Tagebuch weichen aber ab. Mehr dazu auf den Seiten <a href="abgleich.html">Abgleich</a> und <a href="tagebuch.html">Tagebuch</a>.</p>
    <p class="how"><b>So liest du die Karte:</b> „Abspielen“ startet den Ablauf, „Weiter“ und „Zurück“ gehen Schritt für Schritt. Die rote Linie zeigt Luchmanns Weg, gestrichelt sind Bahnfahrten und unsichere Wege. Der Weg von 1866 bleibt 1870 blass sichtbar. ✕ markiert eine Verwundung, ◆ ein anderes Ereignis. Die Karte zeigt heutige Grenzen und historische Landesnamen, beides schematisch. Gepunktet unterstrichene Begriffe lassen sich antippen; alle stehen im <a href="glossar.html">Glossar</a>.</p>
  </details>

  <section class="stage">
    <div class="map" id="map">
      <svg id="svg" viewBox="0 0 1000 640" role="img" aria-label="Karte Mitteleuropas mit Wilhelm Luchmanns Weg 1866 und 1870/71">
        <rect x="-400" y="-400" width="1800" height="1440" fill="var(--sea)"/>
        <path class="grat" id="grat"/>
        <g id="countries"></g>
        <path class="borders" id="borders"/>
        <path class="river-s" id="riverS"/>
        <path class="river-l" id="riverL"/>
        <g id="rivLabels" aria-hidden="true"></g>
        <g id="clabels" aria-hidden="true"></g>
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
      <span><i class="o"></i>Weg 1866 (blass)</span>
      <span><b class="x w">✕</b>Verwundung</span>
      <span><b class="x">◆</b>Ereignis</span>
      <span><i class="b"></i>Grenze heute (schematisch)</span>
      <span><i class="r"></i>Fluss</span>
    </div>

    <section class="controls" aria-label="Zeitleiste">
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

    <aside class="panel" id="panel" aria-live="polite">
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
    </aside>
    <details class="legend-m" id="legendM"><summary>Legende</summary></details>
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

  <section class="persons" aria-labelledby="abH">
    <h3 id="abH">Tagebuch und Regimentsgeschichte</h3>
    <p class="more">Alle geprüften Angaben in einer Übersicht, mit Fundstellen und Abweichungen: <a href="abgleich.html">Seite „Abgleich“ öffnen</a></p>
  </section>
  <section class="persons" aria-labelledby="peH">
    <h3 id="peH">Personen</h3>
    <p class="more">Luchmanns Lebenslauf und die Offiziere und Kameraden, die er nennt: <a href="personen.html">Seite „Personen“ öffnen</a></p>
  </section>
  <section class="persons" aria-labelledby="tbH">
    <h3 id="tbH">Das Tagebuch</h3>
    <p class="more">Handschrift, Abschrift von 1994, die Bilder der Familienchronik und wie zuverlässig der Text ist: <a href="tagebuch.html">Seite „Tagebuch“ öffnen</a></p>
  </section>

  <p class="sources">Datengrundlage: Luchmanns Tagebuch in der Abschrift von 1994 und die Regimentsgeschichte von Hugo von Mueller (1875), dazu Wikipedia für Schlachtdaten. Die Orte sind nach ihrer heutigen Lage eingetragen und auf etwa 1–2 km genau; Wege zwischen den Stationen sind gerade Linien und damit schematisch. Grundkarte: Natural Earth (gemeinfrei), heutige Grenzen.</p>
"""
    h += '  <p class="qnav"><a class="qbtn" href="quellen-karte.html">Quellen</a></p>\n</div>\n<script src="karte-daten.js"></script>\n<script src="karte.js"></script>\n<script src="site.js" defer></script>\n' + FOOT
    Path("index.html").write_text(h)

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
      <div class="th lead"><h3>Daten um Tage oder Wochen verschoben</h3><dl><dd>Ausmarsch „16. Juni“ statt 16. Mai 1866, Königgrätz „2. Juli“ statt 3. Juli, Beaune-la-Rolande „29.“ statt 28. November, Bellegarde „30. November“ statt 2. Dezember, Rückkehr „Juli“ statt Juni 1867.</dd></dl></div>
      <div class="th"><h3>Zahlen aufgerundet</h3><dl><dd>Bei Spichern 300 statt 207 Mann Verlust des Bataillons, in Beaune-la-Rolande 600 statt etwa 400 Gefangene, in Göding 400 bis 500 statt 100 Zigarren je Mann.</dd></dl></div>
      <div class="th"><h3>Orte verwechselt oder zusammengezogen</h3><dl><dd>Parade bei „Nikolsburg“ statt auf dem Marchfeld, der Elbübergang vor statt nach Königgrätz, Mobilmachung und Kriegserklärung am selben Tag.</dd></dl></div>
      <div class="th"><h3>Was sich bestätigt</h3><dl><dd>Wege, Quartiere und Gefechte des Füsilier-Bataillons, die Namen der Offiziere (oft in eigener Schreibung) und Luchmanns eigene Rolle bei Spichern und Mars-la-Tour, die die Regimentsgeschichte namentlich nennt.</dd></dl></div>
    </div>
  </section>
  <section class="sect" aria-labelledby="tlH">
    <h2 id="tlH">Stationen</h2>
    <ol class="tl">
"""
    for i, s in enumerate(STEPS):
        cls, lab = BADGE[s["bel"]]
        h += f"""      <li{' class="key"' if s['bel'] == 'x' else ''}>
        <div class="t">{E(s['dl'])}</div><div class="rail"></div>
        <div class="card" id="s{i + 1}">
          <h3>{E(s['title'])}</h3>
          <p><b>Tagebuch:</b> {E(s['text'])}</p>
          <p class="zit">„{E(s['quote'][0].strip('„“'))}“ <span>({E(s['quote'][1])})</span></p>
          <p><b>Abgleich:</b> {E(s['check'])}</p>
          <div class="meta"><span class="b {cls}">{lab}</span>{''.join(f'<a href="quellen-abgleich.html#q-{k}">{srcno(k)}</a>' for k in s['src'])}<a href="index.html#s{i + 1}">Karte</a></div>
          <p class="why">{E(s.get('note', ''))}</p>
        </div>
      </li>
"""
    h += "    </ol>\n  </section>\n"
    h += '  <p class="note">Die vollständige Belegmatrix mit Fundstellen liegt beim Herausgeber der Website. Wörtliche Zitate aus der Regimentsgeschichte sind in heutige Schreibung übertragen (ſ → s); die Schreibweise der Namen folgt dem Original.</p>\n'
    Path("abgleich.html").write_text(h + tail("quellen-abgleich.html"))

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
        <figcaption>Titelblatt der Handschrift. Ein Foto Luchmanns enthält die Chronik nicht. <a href="quellen-personen.html#f1">Bildnachweis</a></figcaption>
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
    Path("personen.html").write_text(h + tail("quellen-personen.html"))

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
      <div class="th lead"><h3>Die Handschrift</h3><dl><dd>Ein Heft in deutscher Schreibschrift mit dem Titel „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebel Wilhelm Luchmann“. Wann Luchmann es schrieb, ist unbekannt. Es muss nach 1871 entstanden sein: Er nennt Ereignisse „nach Rückkehr in die Garnison“ und spricht vom Kaiser. Das Original kam 1991 aus dem Nachlass eines Verwandten an den Herausgeber.</dd></dl></div>
      <div class="th"><h3>Die Abschrift von 1994</h3><dl><dd>Gertrud Luchmann übertrug den Text im Sommer 1994 von Hand in lateinische Schrift, nach Angabe des Herausgebers ohne Korrekturen. Einzelne Namen und Wörter waren unleserlich oder verblasst. Gerd Luchmann gab die Abschrift im November 1994 in Trier als gebundene Familienchronik heraus, mit Marschrouten, zwei Karten aus Atlanten, zwei Gemälden und kurzen Texten aus Geschichtsbüchern.</dd></dl></div>
      <div class="th"><h3>Was Luchmann erzählt</h3><dl><dd>Gefechte, Märsche und Quartiere, aber vor allem Episoden: Streiche, Wein, Kartenspiel, Mädchen, Hunger. Er schildert auch Gewalt gegen Zivilisten: angezündete Gehöfte, einen erschossenen Bauern, einen misshandelten Geistlichen, den Straßenkampf in Parigné. Diese Stellen gibt die Seite wieder, ohne sie zu übernehmen.</dd></dl></div>
      <div class="th"><h3>Wie zuverlässig?</h3><dl><dd>Wege, Quartiere, Gefechte und Namen stimmen meist mit der Regimentsgeschichte überein, oft bis in Einzelheiten. Daten liegen häufig Tage oder Wochen daneben, Zahlen sind aufgerundet. Seine eigene Rolle bei Spichern und Mars-la-Tour bestätigt die Regimentsgeschichte namentlich. Viele Anekdoten lassen sich nicht prüfen. Siehe <a href="abgleich.html">Abgleich</a>.</dd></dl></div>
    </div>
  </section>
  <section class="sect" aria-labelledby="bH">
    <h2 id="bH">Bilder der Chronik</h2>
    <p class="hint">Die Chronik ordnet zwei farbige Gemälde den Marschrouten zu: „Belagerung von Metz (siehe Bild)“ und „Schlacht von Orleans (siehe Bild)“. Maler, Titel und Herkunft der Bilder nennt sie nicht; sie konnten nicht ermittelt werden. Ob die Bilder diese Ereignisse zeigen, ist deshalb offen.</p>
    <div class="gal gal2">
      <figure><img src="bilder/gemaelde-metz.jpg" width="825" height="1100" alt="Gemälde: brennendes Gebäude bei Nacht, davor Infanterie im Gefecht, Gefallene im Vordergrund" loading="lazy" decoding="async"><figcaption>Der „Belagerung von Metz“ zugeordnet. Maler nicht ermittelt. <a href="quellen-tagebuch.html#f5">F5</a></figcaption></figure>
      <figure><img src="bilder/gemaelde-orleans.jpg" width="1100" height="825" alt="Gemälde: preußische Infanterie mit Fahne stürmt an einem Waldrand vor, Verwundete am Boden" loading="lazy" decoding="async"><figcaption>Der „Schlacht von Orleans“ zugeordnet, doppelseitig. Maler nicht ermittelt. <a href="quellen-tagebuch.html#f6">F6</a></figcaption></figure>
    </div>
    <p class="note">Nicht übernommen wurden die beiden Karten der Chronik, eine Schulatlas-Karte zu 1866 und eine Straßenkarte zu 1870/71: Sie stammen aus gedruckten Atlanten. Die Karte dieser Website ist neu gezeichnet.</p>
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
    Path("tagebuch.html").write_text(h + tail("quellen-tagebuch.html"))

# ---------- Glossar ----------
def build_glossar():
    desc = "Begriffe zu Luchmanns Kriegserlebnissen 1866 und 1870/71: Dienstgrade, Waffen, Truppen und Lagerleben."
    h = head("glossar.html", "Glossar: Begriffe zu 1866 und 1870/71", desc, SUBSTYLE + "\n.gloss { display: grid; gap: 12px; margin: 0 } .gloss > div { background: var(--panel); border: 1px solid var(--rule); border-radius: 3px; padding: 10px 14px } .gloss dt { font: 700 18px/1.2 var(--f-display); text-transform: uppercase; letter-spacing: .03em } .gloss dd { margin: 4px 0 0 } .gloss .gsrc { font-size: 13.5px; color: var(--muted) } .gloss .gsrc a { color: var(--ink) } .gloss > div:target { outline: 3px solid var(--red-soft) }\n")
    h += "  <header>\n" + brand() + nav("glossar.html") + '    <p class="lede">Kurze Erklärungen der Fachbegriffe, die auf den Seiten vorkommen. Auf den anderen Seiten lassen sich die Begriffe beim ersten Vorkommen antippen.</p>\n  </header>\n'
    h += '  <section class="sect" aria-labelledby="gH">\n    <h2 id="gH">Begriffe</h2>\n    <dl class="gloss glnone" id="gloss">\n'
    for gid, t, re_, d in sorted(GLOSSAR, key=lambda g: g[1].lower()):
        h += f'      <div id="{gid}"><dt>{E(t)}</dt><dd>{E(d)}</dd><dd class="gsrc">Worterklärung ohne Einzelbeleg</dd></div>\n'
    h += "    </dl>\n  </section>\n"
    Path("glossar.html").write_text(h + tail("quellen-glossar.html"))

# ---------- Quellenseiten ----------
FIG = [
  ("f1", "Einband der Familienchronik „Kriegs-Erlebnisse von 1866 und 1870/71 des Feldwebels Wilhelm Luchmann“, Trier 1994 (Chronik S. 1)."),
  ("f2", "Titelblatt der Handschrift Wilhelm Luchmanns, nach 1871 (Chronik S. 4)."),
  ("f3", "Erste Textseite der Handschrift (Chronik S. 6)."),
  ("f4", "Handschriftseite „Der Feldzug 1870/71“ (Chronik S. 20)."),
  ("f5", "Farbiges Gemälde, in der Chronik der Belagerung von Metz zugeordnet (Chronik S. 32). Maler, Titel und Vorlage nicht angegeben und nicht ermittelt."),
  ("f6", "Farbiges Gemälde über zwei Seiten, in der Chronik der Schlacht von Orléans zugeordnet (Chronik S. 41). Maler, Titel und Vorlage nicht angegeben und nicht ermittelt."),
]
FIG_NOTE = "Fotos der Seiten aus dem Exemplar der Familie, zugeschnitten und verkleinert. Veröffentlichung mit Zustimmung der Familie (November 2026). Für die beiden Gemälde ist die Rechtelage offen, weil Maler und Vorlage unbekannt sind; Hinweise bitte mit Quelle melden."

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
        h += f'  <section class="sect" aria-labelledby="bildH">\n    <h2 id="bildH">Bildnachweis</h2>\n    <p class="hint">{FIG_NOTE}</p>\n    <ol class="srcs">\n'
        for fid, t in figs:
            h += f'      <li id="{fid}"><span class="id">{fid.upper()}</span><span>{E(t)}</span></li>\n'
        h += "    </ol>\n  </section>\n"
    if page == "index.html":
        h += '  <section class="sect" aria-labelledby="kH">\n    <h2 id="kH">Grundkarte</h2>\n    <p class="hint">Grenzen und Küsten: Natural Earth, Admin 0 Countries 1:50 Mio., über das Paket world-atlas (gemeinfrei). Flüsse: Natural Earth, Rivers and Lake Centerlines und Rivers Europe 1:10 Mio. (gemeinfrei). Projektion: konforme Kegelprojektion nach Lambert. Es sind heutige Grenzen; die Landesnamen 1866/1870 sind schematisch gesetzt. Ortskoordinaten: heutige Lage der Orte, eigene Zuordnung.</p>\n  </section>\n'
    h += f'  <p class="qnav"><a class="qbtn" href="{page}">Zurück zu „{title}“</a></p>\n</div>\n<script src="site.js" defer></script>\n' + FOOT
    Path(fn).write_text(h)

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
    build_data(); build_index(); build_abgleich(); build_personen(); build_tagebuch(); build_glossar(); build_sitejs()
    build_quellen("quellen-karte.html", "index.html", "Karte", ["tb", "rg", "gw", "wp-reg", "wp-gitschin", "wp-kg", "wp-dk", "wp-dfk", "wp-spichern", "wp-mlt", "wp-grav", "wp-metz", "wp-beaune", "wp-orleans", "wp-lemans"])
    build_quellen("quellen-abgleich.html", "abgleich.html", "Abgleich", ["tb", "rg", "gw", "wp-reg", "wp-gitschin", "wp-kg", "wp-dk", "wp-dfk", "wp-spichern", "wp-mlt", "wp-grav", "wp-metz", "wp-beaune", "wp-orleans", "wp-lemans"])
    build_quellen("quellen-personen.html", "personen.html", "Personen", ["tb", "rg"], [FIG[1]])
    build_quellen("quellen-tagebuch.html", "tagebuch.html", "Tagebuch", ["tb", "rg"], FIG)
    build_quellen("quellen-glossar.html", "glossar.html", "Glossar", ["tb", "rg"])
    print("fertig")
