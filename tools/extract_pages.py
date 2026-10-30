"""One-time: home / studio / services / contact text + team photos from the old site into content/pages.json."""
import io, json, re, html, urllib.request
from pathlib import Path
from PIL import Image
from extract_old_site import page, text, fetch, ROOT

IMG = ROOT / "site" / "images"

def blocks(s):
    body = s[s.find("<main"):s.find("</main>")]
    return [b for b in (text(x) for x in re.findall(r"<(?:h1|h2|h3|h4|p)[^>]*>(.*?)</(?:h1|h2|h3|h4|p)>", body, re.S)) if b]

def strip_css(t):
    return re.sub(r"^.*\}\s*", "", t) if "{" in t else t

def save(url, name):
    dst = IMG / name
    if not dst.exists():
        im = Image.open(io.BytesIO(fetch(url + "?format=1500w"))).convert("RGB"); im.thumbnail((1500, 1500))
        im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    return name

home = blocks(page("index.html")); home = [strip_css(b) for b in home]
i = next(k for k, b in enumerate(home) if b.startswith("540X is"))
intro = [home[i], home[i + 1]]
principles = []
for k in range(len(home)):
    if home[k] in ("Experience", "Interactive Spaces", "Details", "Playful", "Articulation", "Climate", "Context"):
        principles.append({"title": home[k], "text": home[k + 1]})

sv = blocks(page("services.html"))
groups, cur = [], None
for k, b in enumerate(sv):
    if b in ("Architecture & Design", "Strategic Visual Narratives"):
        cur = {"title": b, "items": []}; groups.append(cur)
    elif cur is not None and k + 1 < len(sv) and len(b) < 60 and len(sv[k + 1]) > 60:
        cur["items"].append({"title": b, "text": re.sub(r"\s+,", ",", sv[k + 1].replace(" ,", ","))})

ab = page("about.html")
at = blocks(ab)
firm = [b for b in at if b.startswith("At 540X") or b.startswith("At the core")]
photos = {m.group(1).lower(): m.group(2) for m in re.finditer(r'data-image="(https://images\.squarespace-cdn\.com/[^"]+/web\+(\w+)\.jpg)"', ab) for _ in [0]} if False else {}
for m in re.finditer(r'data-image="(https://images\.squarespace-cdn\.com/[^"]+?/web\+(\w+)\.jpg)"', ab):
    photos[m.group(2).lower()] = m.group(1)
team = []
for name, role, key in [("Karmaraj Rana", "Co-Founder & Principal Architect", "karmaraj"), ("Abhishek Patel", "Co-Founder & Principal Architect", "abhi"),
                        ("Zenil Mahendi Ali", "Co-Founder & Principal Designer", "zenil"), ("Jeet Gajera", "Co-Founder & Principal Architect", "jeet"),
                        ("Karan Solanki", "Co-Founder & Creative Head", "karan")]:
    bio = next((b for b in at if (b.startswith("is ") or b.startswith(name.split()[0] + " is") or b.startswith("Ar. " + name)) and len(b) > 120 and b not in firm and name.split()[0] in b), "")
    if bio.startswith("is "): bio = "Ar. " + name + " " + bio
    bio = bio.replace("architecture, He is known", "architecture, he is known")
    photo = save(photos[key], f"team-{key}.jpg") if key in photos else None
    team.append({"name": name, "role": role, "bio": bio, "photo": photo})

pages = {"home": {"intro": intro, "principles": principles}, "studio": {"firm": firm, "team": team,
         "people": [{"name": "Mehul Jagatiya", "role": "Senior Architect"}, {"name": "Yashi Punjabi", "role": "Intern"}],
         "former": [{"year": "2024", "role": "Interior Designer", "name": "Kuldeep Fefar"}, {"year": "2023", "role": "Project Architect", "name": "Dhruvi Satodiya"},
                    {"year": "2022", "role": "Senior Architect", "name": "Mehul Jagatiya"}, {"year": "2021", "role": "Intern Designer", "name": "Yash Rathod"}]},
         "services": groups,
         "contact": {"firm": "540X Partners", "address": ["1303, Space Odyssey", "150ft Ring Road", "Rajkot, Gujarat 360005", "India"],
                     "email": "mail@540xpartners.com", "phone": "+91 9099 527627",
                     "instagram": "https://www.instagram.com/540xpartners", "linkedin": "https://www.linkedin.com/company/540x-partners"}}
(ROOT / "content" / "pages.json").write_text(json.dumps(pages, indent=1, ensure_ascii=False), encoding="utf-8")
print("intro", len(intro), "| principles", len(principles), "| service groups", [(g["title"], len(g["items"])) for g in groups])
print("team", [(t["name"], len(t["bio"]), t["photo"]) for t in team])
