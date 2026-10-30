"""One-time: pull the content of the old 540xpartners.com (a static copy of a Squarespace site)
into content/site.json and download every project photo at web size into site/images/.
"""
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://540xpartners.com/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
      "Accept": "text/html,image/avif,image/webp,*/*;q=0.8"}
FILLER = ["turn a hobby into something more", "creative project to share with the world",
          "the way you tell your story online", "Whatever it is,"]
IMG_DIR = ROOT / "site" / "images"


def fetch(url):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception:
            time.sleep(2)
    raise RuntimeError("could not fetch " + url)


def page(path):
    raw = fetch(BASE + path)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def text(fragment):
    t = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", t).replace(" ,", ",").strip()


def clean(paragraph):
    """Drop Squarespace template filler sentences left on some pages."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    keep = [s for s in sentences if not any(f.lower() in s.lower() for f in FILLER)]
    return " ".join(keep).strip()


def listing(path, folder):
    s = page(path)
    out, seen = [], set()
    for href, inner in re.findall(r'<a[^>]+href="(' + folder + r'/[^"]+\.html)"[^>]*>(.*?)</a>', s, re.S):
        if href in seen:
            continue
        seen.add(href)
        cover = re.search(r'data-image="([^"]+)"', inner)
        out.append({"href": href, "title": text(inner), "cover": cover.group(1) if cover else None})
    return out


def project(href):
    s = page(href)
    art = s[s.find("<article"):s.find("</article>")]
    paras = [text(p) for p in re.findall(r"<(?:h1|h2|h3|p)[^>]*>(.*?)</(?:h1|h2|h3|p)>", art, re.S)]
    paras = [p for p in paras if p]
    images = []
    for tag in re.findall(r"<img[^>]+>", art):
        m = re.search(r'data-image="([^"]+)"', tag) or re.search(r'data-src="([^"]+)"', tag)
        if m:
            u = urllib.parse.urljoin(BASE + href, html.unescape(m.group(1)))
            if u not in images and "logo" not in u.lower():
                images.append(u)
    name = paras[0] if paras else ""
    place_year = paras[1] if len(paras) > 1 else ""
    facts = paras[2] if len(paras) > 2 else ""
    body = [clean(p) for p in paras[3:]]
    return {"name": name, "place_year": place_year, "facts": facts, "text": [p for p in body if p], "images": images}


def save_image(url, slug, n):
    """Download at 2500 px wide (Squarespace resizes for us) and keep a 2400 px JPEG."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    dst = IMG_DIR / f"{slug}-{n:02d}.jpg"
    if dst.exists():
        return dst.name
    src = url + ("&" if "?" in url else "?") + "format=2500w" if "squarespace-cdn" in url else url
    try:
        im = Image.open(io.BytesIO(fetch(src)))
    except Exception:
        im = Image.open(io.BytesIO(fetch(url)))
    im = im.convert("RGB")
    im.thumbnail((2400, 2400))
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    return dst.name


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main():
    site = {"sections": []}
    for key, label, path, folder in [("architecture", "Architecture", "portfolio-1.html", "portfolio-1"),
                                     ("interior", "Interior", "portfolio-1-1.html", "portfolio-1-1"),
                                     ("visual-narratives", "Visual Narratives", "visual-narratives.html", "visual-narratives")]:
        section = {"key": key, "label": label, "projects": []}
        for item in listing(path, folder):
            p = project(item["href"])
            title = item["title"] or p["name"]
            slug = slugify(title)
            urls = ([item["cover"]] if item["cover"] else []) + [u for u in p["images"] if u != item["cover"]]
            files = []
            for n, u in enumerate(urls):
                try:
                    files.append(save_image(u, slug, n))
                except Exception as e:
                    print("   image failed", u[-60:], e)
            section["projects"].append({"slug": slug, "title": title, "name": p["name"], "place_year": p["place_year"],
                                        "facts": p["facts"], "text": p["text"], "images": files, "old_url": item["href"]})
            print(f"{label:18} {title:32} {len(files):3} photos  {len(p['text'])} paragraphs")
        site["sections"].append(section)
    out = ROOT / "content" / "site.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(site, indent=1, ensure_ascii=False), encoding="utf-8")
    print("saved", out)


if __name__ == "__main__":
    main()
