# 540xpartners.com

The 540X Partners website. Free hosting on GitHub Pages, served from the `docs/` folder, on the domain 540xpartners.com.

## How to change something
1. **Text and projects** live in two files:
   - `content/site.json`: every project (Architecture, Interior, Visual Narratives): title, "place | year", details line, paragraphs, photos in order.
   - `content/pages.json`: home intro and principles, studio text and team, services, contact details.
2. **Photos** go in `docs/images/` (JPG, about 2400 px wide). List their file names in the project's `images`; the first one is the cover.
3. Rebuild the pages: `python tools/build.py`
4. Publish: `git add -A && git commit -m "what changed" && git push`. The live site updates in about a minute.

Or just ask Claude: "add project X with these photos", "change the phone number", and it does steps 1-4.

## What's where
- `docs/`: the finished website (generated, apart from `docs/images/`). Don't edit the HTML by hand; it is rebuilt.
- `tools/build.py`: turns the content into pages. `tools/assets/`: the look (style.css), behaviour (site.js), icon.
- `tools/extract_old_site.py`, `tools/extract_pages.py`: one-time copy of the old site (Oct 2026).
- Old addresses (e.g. `/portfolio-1-1/project-one-f5w4d-bl9jz.html`) forward to the new pages, so Google links keep working.

## Preview before launch
- Branch `preview` holds a build made with `python tools/build.py --preview`: every link starts with
  `/540x-site/` and there is no CNAME, so it works at https://303karan-glitch.github.io/540x-site/
- GitHub Pages: Settings → Pages → Branch `preview`, folder `/docs` (no custom domain yet). Share that link with friends.
- Launch: build normally (`python tools/build.py`, which writes the CNAME), merge into `main`, switch Pages to `main` /docs,
  set the custom domain 540xpartners.com, then change the DNS at GoDaddy (see below).

## Domain
DNS for 540xpartners.com points at GitHub Pages (A records 185.199.108.153, .109.153, .110.153, .111.153; `www` CNAME to the GitHub Pages address).
Email records (MX, SPF) are left exactly as they were.

## Change log
- 31 Oct 2026: new site built from the old Squarespace copy: all projects, photos moved off Squarespace's servers, cleaner design, template filler text removed (Nirvana), pincode 360005.

## Copyright
© 540X Partners. All rights reserved. The text, photographs, drawings and design in this repository belong to
540X Partners and the respective photographers. The repository is public only so GitHub Pages can host the site
for free; no licence is granted to copy, reuse or redistribute any of it.
