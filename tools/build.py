"""Build the 540X website from content/*.json into docs/ (GitHub Pages serves docs/).

    python tools/build.py

Edit content/site.json (projects) or content/pages.json (home, studio, services, contact),
put photos in docs/images/, run this, then commit and push.
"""
import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
IMG = OUT / "images"
THUMB = IMG / "thumbs"
DOMAIN = "540xpartners.com"
site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
pages = json.loads((ROOT / "content" / "pages.json").read_text(encoding="utf-8"))
contact = pages["contact"]
e = lambda s: html.escape(str(s or ""), quote=True)

NAV = [("Architecture", "/architecture/"), ("Interior", "/interior/"), ("Visual Narratives", "/visual-narratives/"),
       ("Studio", "/studio/"), ("Services", "/services/"), ("Contact", "/contact/")]


# ---------- images ----------
_size = {}


def size(name):
    if name not in _size:
        with Image.open(IMG / name) as im:
            _size[name] = im.size
    return _size[name]


def thumb(name, width=1000):
    """Smaller copy for grids, so listing pages load fast."""
    THUMB.mkdir(parents=True, exist_ok=True)
    dst = THUMB / name
    if not dst.exists():
        with Image.open(IMG / name) as im:
            im = im.convert("RGB")
            im.thumbnail((width, width * 2))
            im.save(dst, "JPEG", quality=80, optimize=True, progressive=True)
    return "/images/thumbs/" + name


def picture(name, alt="", cls="", eager=False, grid=False):
    w, h = size(name)
    src = thumb(name) if grid else "/images/" + name
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{cls}" src="{src}" width="{w}" height="{h}" alt="{e(alt)}" {load} decoding="async">'


# ---------- page shell ----------
def shell(title, body, desc="", path="/", og=None, home=False):
    full = f"{title} — 540X Partners" if title else "540X Partners — Architecture, Interior & Visual Narratives, Rajkot"
    desc = desc or "540X is a collaborative design practice in Rajkot, India, founded by five principal partners: architecture, interior design and visual narratives."
    og_img = f"https://{DOMAIN}/images/{og}" if og else f"https://{DOMAIN}/images/og.jpg"
    nav = "".join(f'<a href="{u}"{" aria-current=page" if path.startswith(u) else ""}>{n}</a>' for n, u in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc[:300])}">
<link rel="canonical" href="https://{DOMAIN}{path}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc[:300])}">
<meta property="og:image" content="{og_img}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#f7f6f3">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head>
<body class="{'home' if home else ''}">
<header class="top">
  <a class="logo" href="/" aria-label="540X home">540X<span>.</span></a>
  <nav class="nav" id="nav">{nav}</nav>
  <button class="menu" aria-label="Menu" aria-controls="nav" aria-expanded="false"><span></span><span></span></button>
</header>
<main>
{body}
</main>
<footer class="foot">
  <div class="foot-grid">
    <div><a class="logo" href="/">540X<span>.</span></a><p>Architecture · Interior · Visual Narratives</p></div>
    <div><h4>Studio</h4><p>{'<br>'.join(e(a) for a in contact['address'])}</p></div>
    <div><h4>Contact</h4><p><a href="mailto:{contact['email']}">{contact['email']}</a><br><a href="tel:{contact['phone'].replace(' ', '')}">{contact['phone']}</a></p></div>
    <div><h4>Follow</h4><p><a href="{contact['instagram']}" target="_blank" rel="noopener">Instagram</a><br><a href="{contact['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></p></div>
  </div>
  <p class="fine">© 540X Partners · Rajkot, India</p>
</footer>
<script src="/site.js" defer></script>
</body>
</html>
"""


def write(path, text):
    f = OUT / path.strip("/") / "index.html" if not path.endswith(".html") else OUT / path.strip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


def place_year(p):
    parts = [x.strip() for x in (p.get("place_year") or "").split("|")]
    return (parts[0] if parts else ""), (parts[1] if len(parts) > 1 else "")


def card(p, section, big=False):
    place, year = place_year(p)
    cover = p["images"][0] if p["images"] else None
    img = picture(cover, p["title"], grid=True) if cover else ""
    meta = " · ".join(x for x in (place, year) if x)
    return f"""<a class="card{' big' if big else ''}" href="/projects/{p['slug']}/">
  <div class="frame">{img}</div>
  <div class="cap"><span class="t">{e(p['title'])}</span><span class="m">{e(section['label'] if big else meta)}</span></div>
</a>"""


# ---------- pages ----------
def build_home():
    all_p = [(s, p) for s in site["sections"] for p in s["projects"] if p["images"]]
    arch = [x for x in all_p if x[0]["key"] == "architecture"]
    inte = [x for x in all_p if x[0]["key"] == "interior"]
    featured = [x for pair in zip(arch[:3], inte[:3]) for x in pair]   # alternate architecture / interior
    slides = "".join(
        f'<a class="slide{" on" if i == 0 else ""}" href="/projects/{p["slug"]}/">{picture(p["images"][0], p["title"], eager=i == 0)}'
        f'<span class="slide-cap"><b>{e(p["title"])}</b>{e(place_year(p)[0])}</span></a>'
        for i, (s, p) in enumerate(featured[:5]))
    intro = pages["home"]["intro"]
    principles = "".join(f'<li><span class="n">{i + 1:02d}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></li>'
                         for i, x in enumerate(pages["home"]["principles"]))
    disciplines = "".join(
        f'<a class="disc" href="/{s["key"]}/"><span>{e(s["label"])}</span><small>{len(s["projects"])} projects</small></a>'
        for s in site["sections"])
    body = f"""
<section class="hero" aria-label="Selected projects">{slides}
  <div class="hero-ui"><span class="count"><b>01</b> / {len(featured[:5]):02d}</span></div>
</section>
<section class="wrap intro reveal">
  <p class="lead">{e(intro[0])}</p>
  <p class="sub">{e(intro[1])}</p>
</section>
<section class="wrap reveal">
  <div class="head"><h2>Selected work</h2><a class="more" href="/architecture/">All projects →</a></div>
  <div class="grid feature">{''.join(card(p, s, big=True) for s, p in featured)}</div>
</section>
<section class="wrap reveal">
  <div class="head"><h2>How we work</h2></div>
  <ol class="principles">{principles}</ol>
</section>
<section class="wrap reveal"><div class="discs">{disciplines}</div></section>
<section class="cta reveal">
  <p>Have a site, a space or a brand in mind?</p>
  <a class="big-link" href="/contact/">Start a project →</a>
</section>"""
    write("/", shell("", body, home=True, og=featured[0][1]["images"][0] if featured else None))


def build_section(s):
    projects = [p for p in s["projects"] if p["images"]]
    body = f"""
<section class="wrap page-head reveal"><h1>{e(s['label'])}</h1><p class="count-l">{len(projects)} projects</p></section>
<section class="wrap"><div class="grid list">{''.join(card(p, s) for p in projects)}</div></section>"""
    write(f"/{s['key']}/", shell(s["label"], body, path=f"/{s['key']}/", og=projects[0]["images"][0] if projects else None))


def gallery(images, title):
    """Wide photos run full width; tall ones sit in pairs."""
    out, pend = [], []
    for name in images:
        w, h = size(name)
        if h > w * 1.05:
            pend.append(name)
            if len(pend) == 2:
                out.append('<div class="pair">' + "".join(f'<figure>{picture(n, title, "zoom")}</figure>' for n in pend) + "</div>")
                pend = []
        else:
            out.append(f'<figure class="wide">{picture(name, title, "zoom")}</figure>')
    if pend:
        out.append('<div class="pair single">' + "".join(f'<figure>{picture(n, title, "zoom")}</figure>' for n in pend) + "</div>")
    return "".join(out)


def split_facts(line):
    """'Interior Design Residential 1,100 SQ. FT. Completed' -> type, area, status."""
    line = line or ""
    status = next((w for w in ("Completed", "Ongoing", "Proposal", "Unbuilt") if line.endswith(w)), "")
    line = line[: len(line) - len(status)].strip()
    m = re.search(r"([\d,]+)\s*SQ\.?\s*FT\.?", line, re.I)
    area = f"{m.group(1)} sq ft" if m else ""
    kind = (line[: m.start()] if m else line).strip()
    return kind, area, status


def build_project(s, p, prev, nxt):
    place, year = place_year(p)
    kind, area, status = split_facts(p.get("facts"))
    facts = [("Location", place), ("Year", year), ("Type", kind), ("Area", area), ("Status", status)]
    facts_html = "".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in facts if v)
    text = "".join(f"<p>{e(t)}</p>" for t in p["text"])
    hero, rest = p["images"][0], p["images"][1:]
    nav = (f'<a class="pn prev" href="/projects/{prev["slug"]}/"><small>Previous</small>{e(prev["title"])}</a>' if prev else "<span></span>") + \
          (f'<a class="pn next" href="/projects/{nxt["slug"]}/"><small>Next</small>{e(nxt["title"])}</a>' if nxt else "<span></span>")
    body = f"""
<section class="p-hero">{picture(hero, p['title'], 'zoom', eager=True)}</section>
<section class="wrap p-info reveal">
  <div class="p-title"><a class="back" href="/{s['key']}/">← {e(s['label'])}</a><h1>{e(p['title'])}</h1></div>
  <dl class="facts">{facts_html}</dl>
  <div class="p-text">{text}</div>
</section>
<section class="wrap gallery">{gallery(rest, p['title'])}</section>
<nav class="wrap pnav">{nav}</nav>
<div class="lightbox" hidden><button class="lb-x" aria-label="Close">×</button><button class="lb-p" aria-label="Previous">‹</button><img alt=""><button class="lb-n" aria-label="Next">›</button></div>"""
    desc = (p["text"][0] if p["text"] else f"{p['title']}, {place} — {s['label']} by 540X Partners.")
    write(f"/projects/{p['slug']}/", shell(p["title"], body, desc=desc, path=f"/projects/{p['slug']}/", og=hero))


def build_studio():
    st = pages["studio"]
    team = "".join(f"""<article class="member reveal">
  {picture(m['photo'], m['name'], grid=True) if m.get('photo') else ''}
  <h3>{e(m['name'])}</h3><p class="role">{e(m['role'])}</p>
  <details><summary>Read bio</summary><p>{e(m['bio'])}</p></details>
</article>""" for m in st["team"])
    people = "".join(f"<li><span>{e(x['name'])}</span><small>{e(x['role'])}</small></li>" for x in st["people"])
    former = "".join(f"<li><span>{e(x['name'])}</span><small>{e(x['role'])} · {e(x['year'])}</small></li>" for x in st["former"])
    body = f"""
<section class="wrap page-head reveal"><h1>Studio &amp; people</h1></section>
<section class="wrap two reveal">{''.join(f'<p>{e(t)}</p>' for t in st['firm'])}</section>
<section class="wrap"><div class="head"><h2>Principal partners</h2></div><div class="team">{team}</div></section>
<section class="wrap two-lists reveal">
  <div><h2>Team</h2><ul class="names">{people}</ul></div>
  <div><h2>Former team</h2><ul class="names">{former}</ul></div>
</section>"""
    write("/studio/", shell("Studio", body, desc=st["firm"][0] if st["firm"] else "", path="/studio/"))


def build_services():
    groups = "".join(f"""<section class="wrap svc reveal">
  <div class="head"><h2>{e(g['title'])}</h2></div>
  <div class="svc-grid">{''.join(f'<div><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p></div>' for i in g['items'])}</div>
</section>""" for g in pages["services"])
    body = f'<section class="wrap page-head reveal"><h1>Services</h1></section>{groups}' \
           f'<section class="cta reveal"><p>Tell us about your project.</p><a class="big-link" href="/contact/">Get in touch →</a></section>'
    write("/services/", shell("Services", body, desc="Architecture, interior design, master planning, furniture, turnkey, 3D visualisation, landscape and brand design.", path="/services/"))


def build_contact():
    c = contact
    maps = "https://www.google.com/maps/search/?api=1&query=" + "+".join(re.sub(r"[^A-Za-z0-9]+", "+", " ".join(c["address"][:3])).split("+"))
    body = f"""
<section class="wrap page-head reveal"><h1>Contact</h1></section>
<section class="wrap contact reveal">
  <a class="big-link" href="mailto:{c['email']}">{c['email']}</a>
  <a class="big-link" href="tel:{c['phone'].replace(' ', '')}">{c['phone']}</a>
  <div class="c-grid">
    <div><h4>Studio</h4><p>{c['firm']}<br>{'<br>'.join(e(a) for a in c['address'])}</p><p><a href="{maps}" target="_blank" rel="noopener">Open in Google Maps →</a></p></div>
    <div><h4>Follow</h4><p><a href="{c['instagram']}" target="_blank" rel="noopener">Instagram</a><br><a href="{c['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></p></div>
  </div>
</section>"""
    write("/contact/", shell("Contact", body, desc="Contact 540X Partners, Rajkot: " + c["email"] + ", " + c["phone"], path="/contact/"))


def build_redirects():
    """Old Squarespace-copy addresses keep working (Google results, shared links)."""
    old = {"about.html": "/studio/", "services.html": "/services/", "contact.html": "/contact/", "portfolio-1.html": "/architecture/",
           "portfolio-1-1.html": "/interior/", "visual-narratives.html": "/visual-narratives/", "cart.html": "/"}
    for s in site["sections"]:
        for p in s["projects"]:
            if p.get("old_url"):
                old[p["old_url"]] = f"/projects/{p['slug']}/"
    for src, dst in old.items():
        write(src, f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="https://{DOMAIN}{dst}">'
                   f'<meta http-equiv="refresh" content="0; url={dst}"><a href="{dst}">This page has moved.</a>')


def build_misc():
    urls = ["/", "/studio/", "/services/", "/contact/"] + [f"/{s['key']}/" for s in site["sections"]] + \
           [f"/projects/{p['slug']}/" for s in site["sections"] for p in s["projects"] if p["images"]]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                     + "".join(f"<url><loc>https://{DOMAIN}{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n", encoding="utf-8")
    (OUT / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "404.html").write_text(shell("Not found", '<section class="wrap page-head"><h1>Page not found</h1><p><a class="more" href="/">Back to home →</a></p></section>', path="/404"), encoding="utf-8")
    first = next((p["images"][0] for s in site["sections"] for p in s["projects"] if p["images"]), None)
    if first and not (IMG / "og.jpg").exists():
        with Image.open(IMG / first) as im:
            im = im.convert("RGB"); im.thumbnail((1200, 1200)); im.save(IMG / "og.jpg", "JPEG", quality=82)
    for f in ("style.css", "site.js", "favicon.svg"):
        shutil.copy(ROOT / "tools" / "assets" / f, OUT / f)


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.iterdir():   # clear old generated pages, keep photos
        if old.name != "images":
            shutil.rmtree(old) if old.is_dir() else old.unlink()
    build_home()
    for s in site["sections"]:
        build_section(s)
        ps = [p for p in s["projects"] if p["images"]]
        for i, p in enumerate(ps):
            build_project(s, p, ps[i - 1] if i else None, ps[i + 1] if i + 1 < len(ps) else None)
    build_studio(); build_services(); build_contact(); build_redirects(); build_misc()
    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"built {n} pages into {OUT}")


if __name__ == "__main__":
    main()
