#!/usr/bin/env python3
"""Acquire appropriately licensed, relevant Commons photos for BucharestUA.

No image is used without a recognized freely reusable license and attribution.
Only a small number of already-due articles is processed per run.
"""
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
from html import escape, unescape
from html.parser import HTMLParser
import json
import re
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dbc44mys4b-glitch.github.io/"
QUEUE = ROOT / "content-queue/articles.json"
SEEDS = ROOT / "media/verified-photo-seeds.json"
INDEX = ROOT / "media/assigned-images.json"
COVERS = ROOT / "assets/covers"
REPORT = ROOT / "reports/media-report.json"
USER_AGENT = "BucharestUAEditorial/1.0 (https://dbc44mys4b-glitch.github.io/; Wikimedia Commons licensed media)"
API = "https://commons.wikimedia.org/w/api.php"
MAX_PER_RUN = 8


class StripHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def plain(html):
    p = StripHTML()
    p.feed(str(html))
    return " ".join(unescape(" ".join(p.parts)).split())[:200]


def json_request(url):
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=22) as response:
        data = response.read(2_000_000)
    return json.loads(data)


def info_for_file(file_title):
    params = {
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": "File:" + file_title,
        "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": "1200",
    }
    data = json_request(API + "?" + urlencode(params))
    pages = list(data.get("query", {}).get("pages", {}).values())
    return [dict(p, **p["imageinfo"][0]) for p in pages if p.get("imageinfo")]


def search_files(query):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": "12",
        "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": "1200",
    }
    data = json_request(API + "?" + urlencode(params))
    pages = list(data.get("query", {}).get("pages", {}).values())
    return [dict(p, **p["imageinfo"][0]) for p in pages if p.get("imageinfo")]


def license_details(item):
    m = item.get("extmetadata", {})
    name = m.get("LicenseShortName", {}).get("value", "").strip()
    lic_url = m.get("LicenseUrl", {}).get("value", "").strip()
    # Fail closed: no unidentified, non-commercial or no-derivatives licenses.
    allowed = (
        re.fullmatch(r"CC BY(?:-SA)?\s+[234]\.0(?:\s+(?:ro|de|fr))?", name, re.I)
        or name.upper() in {"CC0", "CC0 1.0", "PUBLIC DOMAIN", "PD"}
    )
    if not allowed:
        return None
    if name.upper() not in {"CC0", "CC0 1.0", "PUBLIC DOMAIN", "PD"} and not lic_url.startswith("https://creativecommons.org/licenses/"):
        return None
    if item.get("mime", "") != "image/jpeg":
        return None
    if item.get("width", 0) < 700 or item.get("height", 0) < 450:
        return None
    link = item.get("thumburl") or item.get("url")
    if not link or not link.startswith(("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")):
        return None
    author = plain(m.get("Artist", {}).get("value", ""))
    if not author:
        return None
    return {"author": author, "license": name, "license_url": lic_url or "https://creativecommons.org/publicdomain/zero/1.0/", "src": link}


def photo_query(entry):
    s = (entry["slug"] + " " + entry.get("title", "")).lower()
    cases = [
        (["antipa"], "Grigore Antipa Museum Bucharest"),
        (["peles", "sinaia"], "Peles Castle Sinaia"),
        (["bran-castle"], "Bran Castle Romania"),
        (["brasov", "brașov"], "Brasov old town"),
        (["athenaeum", "ateneu"], "Romanian Athenaeum Bucharest"),
        (["parliament", "parlament"], "Palace of the Parliament Bucharest"),
        (["herastrau", "king-michael"], "Herastrau Park Bucharest"),
        (["victoriei"], "Calea Victoriei Bucharest"),
        (["old-town", "lipscani", "stavropoleos"], "Bucharest Old Town Lipscani"),
        (["botanical"], "Bucharest Botanical Garden"),
        (["tineretului"], "Tineretului park Bucharest"),
        (["cismigiu"], "Cismigiu park Bucharest"),
        (["cotroceni"], "Cotroceni Bucharest"),
        (["therme"], "Therme Bucharest"),
        (["caru-cu-bere"], "Caru cu bere Bucharest"),
        (["papanasi", "food", "sarmale", "ciorba", "mici"], "Romanian traditional food"),
        (["phone", "laptop"], "mobile phone repair"),
        (["auto", "tire", "car", "rca", "itp"], "car service workshop"),
        (["health", "doctor", "dentist", "endocrin", "hospital", "pediatric"], "doctor medical consultation clinic"),
        (["kids", "child", "family", "parents", "baby", "stroller"], "children playground Bucharest"),
        (["sector", "ilfov", "cosmopolis", "pipera", "voluntari"], "Bucharest Romania city residential streets"),
    ]
    for needles, query in cases:
        if any(n in s for n in needles):
            return query
    category = entry.get("category", "")
    if "Районы" in category:
        return "Bucharest Romania residential"
    if "Семья" in category:
        return "Bucharest park family"
    if "здоров" in category.lower():
        return "medical clinic consultation"
    return "Bucharest Romania city architecture"


def seed_for(entry, seeds):
    s = (entry["slug"] + " " + entry["title"]).lower()
    choices = [
        (["auto-service-bucharest", "tire-service-bucharest"], "carworkshop"),
        (["sports-partners-bucharest", "kids-tennis"], "tennis"),
        (["antipa-museum", "antipa-short", "antipa-sensory"], "antipa"),
        (["cismigiu", "cișmigiu"], "cismigiu"),
        (["tineretului"], "tineretului"),
        (["village-museum", "muzeul-satului"], "village"),
        (["peles", "sinaia"], "peles"),
        (["bran-castle"], "bran"),
        (["parliament"], "parliament"),
        (["athenaeum", "ateneu"], "athenaeum"),
        (["victoriei"], "victoriei"),
        (["stavropoleos"], "stavropoleos"),
        (["lipscani", "old-town"], "oldtown"),
        (["herastrau", "king-michael"], "herastrau"),
    ]
    for parts, key in choices:
        if any(k in s for k in parts):
            return next((x for x in seeds if x["key"] == key), None)
    return None


def pick(entry, seeds, used_titles):
    pinned = seed_for(entry, seeds)
    if pinned:
        # License, author and subject have been independently verified on the
        # exact Commons file description page, including the filename.
        results = info_for_file(pinned["file"])
        for item in results:
            image_url = item.get("thumburl") or item.get("url", "")
            if (item.get("mime") == "image/jpeg"
                and item.get("width", 0) >= 700
                and image_url.startswith(("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/"))
                and item.get("title", "").removeprefix("File:") == pinned["file"]):
                return item, {
                    "author": pinned["author"], "license": pinned["license"],
                    "license_url": pinned["license_url"], "src": image_url
                }, pinned["alt"]
        raise ValueError("Commons metadata unavailable for " + pinned["file"] + " / " + repr([(x.get("title"), x.get("mime"), x.get("width"), (x.get("thumburl") or x.get("url") or "")[:40]) for x in results])[:250])
    else:
        results = search_files(photo_query(entry))
    # Unknown image licenses or subjects are rejected.
    candidates = []
    query_words = {
        w for w in re.findall(r"[a-z]{4,}", photo_query(entry).lower())
        if w not in {"romania", "bucharest", "city", "image", "photo"}
    }
    for x in results:
        rights = license_details(x)
        if not rights:
            continue
        if not pinned:
            filename = x.get("title", "").lower().replace("_", " ")
            # Commons search can return historical trains or unrelated files.
            if not any(w in filename for w in query_words):
                continue
        candidates.append((x, rights))
    if not candidates:
        return None
    ranked = sorted(candidates, key=lambda c: (
        c[0].get("title", "") in used_titles,
        c[0].get("height", 0) > c[0].get("width", 0),
        c[0].get("title", "")
    ))
    x, rights = ranked[0]
    alt = "Иллюстративное фото по теме: " + entry["title"].split(":")[0]
    return x, rights, alt


def download(url, path):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=25) as response:
        if "image/jpeg" not in response.headers.get("Content-Type", ""):
            raise ValueError("Image is not JPEG")
        content = response.read(1_500_001)
    if len(content) > 1_500_000 or len(content) < 8_000:
        raise ValueError("Image too large or too small")
    # Basic JPEG signature check prevents accidental HTML error pages.
    if not content.startswith(b"\xff\xd8\xff"):
        raise ValueError("Not a JPEG file")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return len(content)


def cover_markup(entry, cover):
    src = "assets/covers/" + entry["slug"] + ".jpg"
    return (
        '<!-- BUCHARESTUA_MEDIA -->'
        '<figure class="journal-cover">'
        '<img src="' + escape(src, quote=True) + '" '
        'width="1200" height="750" loading="eager" decoding="async" '
        'fetchpriority="high" alt="' + escape(cover["alt"], quote=True) + '">'
        '<figcaption>Фото: <a target="_blank" rel="noopener noreferrer" href="' +
        escape(cover["source_url"], quote=True) + '">' +
        escape(cover["author"]) + '</a> · <a target="_blank" rel="license noopener noreferrer" href="' +
        escape(cover["license_url"], quote=True) + '">' +
        escape(cover["license"]) + '</a>. Иллюстрация или фрагмент кадра.</figcaption></figure>'
    )


def decorate_html(html, entry, cover=None):
    from urllib.parse import quote as quote_url
    slug = entry["slug"]
    title = entry["title"]
    url = BASE + slug + ".html"
    if "<!-- BUCHARESTUA_SHARE -->" not in html:
        social_copy = (entry.get("telegram_teaser") or entry.get("description") or title)
        social_copy = " ".join(social_copy.split())[:180]
        share = "https://t.me/share/url?url=" + quote_url(url, safe="") + "&text=" + quote_url(social_copy + " — BucharestUA", safe="")
        link = (
            '<!-- BUCHARESTUA_SHARE -->'
            '<div class="journal-sharebar"><span class="journal-label">BUCHARESTUA · ГОРОДСКОЙ ЖУРНАЛ</span>'
            '<a class="journal-share" target="_blank" rel="noopener noreferrer" aria-label="Поделиться статьёй в Telegram" href="' +
            escape(share, quote=True) + '">↗ Поделиться в Telegram</a></div>'
        )
        marker = '<article class="prose">'
        if marker in html:
            html = html.replace(marker, marker + link, 1)
    if cover:
        figure = cover_markup(entry, cover)
        if "<!-- BUCHARESTUA_MEDIA -->" in html:
            html = re.sub(
                r'<!-- BUCHARESTUA_MEDIA --><figure class="journal-cover">.*?</figure>',
                lambda match: figure, html, count=1, flags=re.S
            )
        else:
            marker = '<article class="prose">'
            if marker in html:
                html = html.replace(marker, figure + marker, 1)
    if cover and 'property="og:image"' in html:
        local_image_url = BASE + 'assets/covers/' + slug + '.jpg'
        html = re.sub(
            r'(<meta property="og:image" content=")[^"]*(">)',
            lambda match: match.group(1) + local_image_url + match.group(2),
            html, count=1
        )
        html = re.sub(
            r'(<meta property="og:image:alt" content=")[^"]*(">)',
            lambda match: match.group(1) + escape(cover["alt"], quote=True) + match.group(2),
            html, count=1
        )
    if not cover and "<!-- BUCHARESTUA_MEDIA -->" in html:
        html = re.sub(
            r'<!-- BUCHARESTUA_MEDIA --><figure class="journal-cover">.*?</figure>',
            "", html, count=1, flags=re.S
        )
        html = re.sub(r'<meta property="og:image"[^>]*>', "", html)
        html = re.sub(r'<meta property="og:image:alt"[^>]*>', "", html)
        html = re.sub(r'<meta name="twitter:card"[^>]*>', "", html)
    if cover and 'property="og:image"' not in html:
        tags = (
            '<meta property="og:image" content="' + BASE + 'assets/covers/' + slug + '.jpg">'
            '<meta property="og:image:alt" content="' + escape(cover["alt"], quote=True) + '">'
            '<meta name="twitter:card" content="summary_large_image">'
        )
        html = html.replace("</head>", tags + "</head>", 1)
    return html


def main():
    today = datetime.now(ZoneInfo("Europe/Bucharest")).date().isoformat()
    entries = json.loads(QUEUE.read_text(encoding="utf-8"))
    seeds = json.loads(SEEDS.read_text(encoding="utf-8"))["photos"]
    current = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.is_file() else {}
    due = sorted([e for e in entries if e["publish_date"] <= today], key=lambda e: (e["publish_date"], e["slug"]))
    # Site community hub is not part of the article queue; it still needs
    # the same Commons attribution and a locally served cover image.
    if (ROOT / "community.html").is_file():
        due.append({
            "slug": "community", "publish_date": "2026-11-09",
            "title": "Romanian Athenaeum Bucharest community"
        })
    used = {x.get("commons_title") for x in current.values()}
    changes = []
    errors = []
    for entry in due:
        slug = entry["slug"]
        path = COVERS / (slug + ".jpg")
        if slug in current and path.is_file():
            continue
        if len(changes) >= MAX_PER_RUN:
            break
        try:
            result = pick(entry, seeds, used)
            if not result:
                errors.append({"slug": slug, "problem": "No verified relevant freely licensed photo"})
                continue
            item, rights, alt = result
            count = download(rights["src"], path)
            current[slug] = {
                "alt": alt, "author": rights["author"], "license": rights["license"],
                "license_url": rights["license_url"],
                "commons_title": item["title"],
                "source_url": item.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + quote(item["title"].replace(" ", "_")),
                "bytes": count
            }
            used.add(item["title"])
            changes.append(slug)
            print("Photo licensed, downloaded: " + slug + " / " + item["title"])
        except Exception as exc:
            errors.append({"slug": slug, "problem": str(exc)[:180]})
            print("Photo not imported " + slug + ": " + str(exc)[:180])

    # Remove stale covers that have no approved attribution in the manifest.
    for entry in due:
        slug = entry["slug"]
        previous_file = COVERS / (slug + ".jpg")
        if slug not in current and previous_file.exists():
            previous_file.unlink()
    INDEX.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Backfill articles that have already been published; future articles are
    # enriched during the standard publish step using the same manifest.
    backfilled = []
    for entry in due:
        path = ROOT / (entry["slug"] + ".html")
        if not path.is_file():
            continue
        before = path.read_text(encoding="utf-8")
        after = decorate_html(before, entry, current.get(entry["slug"]))
        if after != before:
            path.write_text(after, encoding="utf-8")
            backfilled.append(entry["slug"])
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps({
        "checked": today, "new_photo_covers": changes,
        "articles_enriched": backfilled, "photo_count": len(current),
        "warnings": errors[:40],
        "note": "An article without a verified photo is published without an image; never substitute unlicensed material."
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Media: new photos=", len(changes), "covered=", len(current),
          "backfilled=", len(backfilled), "warnings=", len(errors))


if __name__ == "__main__":
    main()
