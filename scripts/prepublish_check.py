#!/usr/bin/env python3
"""Strict local pre-publication validation for BucharestUA.

Run after assembling HTML/media, BEFORE GitHub commit/push. Does not make
network calls or mistake delayed GitHub Pages deployment for a broken page.
Missing licensed covers hold new articles in the queue; never waive the gate.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from zoneinfo import ZoneInfo
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dbc44mys4b-glitch.github.io/"
TG = "https://t.me/bucharest_info"
OUT = ROOT / "reports"
OUT.mkdir(exist_ok=True)


class HTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_text = ""
        self.in_title = False
        self.h1 = 0
        self.h2 = 0
        self.meta = {}
        self.html_lang = ""
        self.canonical = ""
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "html":
            self.html_lang = attrs.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "h2":
            self.h2 += 1
        elif tag == "meta":
            if attrs.get("name"):
                self.meta[attrs["name"].lower()] = attrs.get("content", "")
            if attrs.get("property"):
                self.meta[attrs["property"].lower()] = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = attrs.get("href", "")
        elif tag == "img":
            self.images.append(attrs)
        elif tag == "a":
            self.links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data


def inspect_html(path):
    p = HTMLInspector()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def local_target(src):
    parsed = urlparse(src)
    if parsed.scheme in ("http", "https"):
        if parsed.netloc != urlparse(BASE).netloc:
            return None
        value = parsed.path.lstrip("/")
    else:
        value = src.split("#", 1)[0].split("?", 1)[0].lstrip("/")
    if value.startswith("../") or not value:
        return None
    return ROOT / unquote(value)


def jpeg_usable(path):
    if not path.is_file() or path.stat().st_size < 8_000:
        return False
    with path.open("rb") as f:
        return f.read(3) == b"\xff\xd8\xff"


def main():
    critical = []
    notices = []
    queue = json.loads((ROOT / "content-queue" / "articles.json").read_text(encoding="utf-8"))
    manifests = json.loads((ROOT / "media" / "assigned-images.json").read_text(encoding="utf-8"))
    today = datetime.now(ZoneInfo("Europe/Bucharest")).date().isoformat()
    slugs = [e["slug"] for e in queue]
    for slug, number in Counter(slugs).items():
        if number != 1:
            critical.append(f"Duplicate slug in queue: {slug}")
    for title, number in Counter(e["title"] for e in queue).items():
        if number != 1:
            critical.append(f"Duplicate title in queue: {title}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    sitemap_urls = {el.text for el in sitemap.getroot().iter() if el.tag.endswith("loc")}
    if not (ROOT / "styles.css").is_file():
        critical.append("Global CSS missing")
    if TG not in (ROOT / "index.html").read_text(encoding="utf-8"):
        critical.append("Telegram destination absent from homepage")

    published = []
    queued_due = []
    for entry in queue:
        slug = entry["slug"]
        path = ROOT / (slug + ".html")
        if entry["publish_date"] > today and path.is_file():
            critical.append(f"Article released before scheduled date: {slug}")
        if not path.exists():
            if entry["publish_date"] <= today:
                queued_due.append(slug)
            continue
        published.append(slug)
        cover = manifests.get(slug)
        cover_path = ROOT / "assets" / "covers" / (slug + ".jpg")
        if not cover or not jpeg_usable(cover_path):
            critical.append(f"Published article missing valid approved JPEG cover: {slug}")
        elif not all(cover.get(k) for k in ("alt", "author", "license", "license_url", "source_url", "commons_title")):
            critical.append(f"Missing image rights metadata: {slug}")

        parser = inspect_html(path)
        html = path.read_text(encoding="utf-8")
        expected = BASE + slug + ".html"
        if not parser.title_text.strip() or parser.h1 != 1 or not parser.meta.get("description"):
            critical.append(f"Incomplete title/H1/description: {slug}")
        if parser.h2 < 3:
            critical.append(f"Article too thin (fewer than three sections): {slug}")
        if parser.canonical != expected:
            critical.append(f"Wrong canonical: {slug}")
        if parser.html_lang != "ru":
            critical.append(f"Missing or unexpected language: {slug}")
        if not any(im.get("src") == "assets/covers/" + slug + ".jpg"
                   and im.get("alt", "").strip() for im in parser.images):
            critical.append(f"Visible photo or alt missing: {slug}")
        if parser.meta.get("og:image") != BASE + "assets/covers/" + slug + ".jpg":
            critical.append(f"Social preview photo missing/incorrect: {slug}")
        if "creativecommons.org/licenses/" not in html and "creativecommons.org/publicdomain/" not in html:
            critical.append(f"Photo attribution/license missing in article: {slug}")
        if not any("t.me/share/url?" in link for link in parser.links):
            critical.append(f"Telegram share button missing: {slug}")
        if not any(TG in link for link in parser.links):
            critical.append(f"Join Telegram call-to-action missing: {slug}")
        if expected not in sitemap_urls:
            critical.append(f"Published URL not in sitemap: {slug}")
        if len(entry.get("intro", "")) < 100:
            notices.append(f"Review short introduction before next editorial refresh: {slug}")

    # The community entry is a standalone hub, not part of queue.
    cfile = ROOT / "community.html"
    community_img = ROOT / "assets" / "covers" / "community.jpg"
    if not cfile.is_file() or not jpeg_usable(community_img):
        critical.append("Community page or local hero image missing")
    else:
        html = cfile.read_text(encoding="utf-8")
        parser = inspect_html(cfile)
        if parser.meta.get("og:image") != BASE + "assets/covers/community.jpg":
            critical.append("Community social preview image missing")
        if not any(im.get("src") == "assets/covers/community.jpg" and im.get("alt", "")
                   for im in parser.images):
            critical.append("Community visible photo or ALT missing")
        if not all(manifests.get("community", {}).get(k)
                   for k in ("author", "license", "source_url", "alt")):
            critical.append("Community photo lacks Commons attribution manifest")
        if TG not in html or "creativecommons.org/licenses/" not in html:
            critical.append("Community Telegram/credit missing")
        if BASE + "community.html" not in sitemap_urls:
            critical.append("Community missing from sitemap")

    # Validate visible internal image paths and local navigation of current
    # issue pages. Fail before deploying broken links, not after.
    for slug in published + ["community"]:
        path = ROOT / (slug + ".html")
        inspector = inspect_html(path)
        for im in inspector.images:
            src = im.get("src", "")
            target = local_target(src)
            if target is None:
                critical.append(f"Unapproved remote or unsafe image reference: {path.name} -> {src}")
            elif not target.is_file():
                critical.append(f"Missing local image: {path.name} -> {src}")
            if not im.get("alt", "").strip():
                critical.append(f"Missing image alt: {path.name} -> {src}")
        for href in inspector.links:
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            parsed = urlparse(href)
            if parsed.netloc and parsed.netloc != urlparse(BASE).netloc:
                continue
            local = local_target(href)
            if local is None:
                continue
            if href.endswith(".html") and not local.is_file():
                critical.append(f"Broken internal link: {path.name} -> {href}")

    status = {
        "checked_in_bucharest": today,
        "queue_size": len(queue),
        "published_articles": len(published),
        "approved_photo_assets": len(manifests),
        "community_cover_verified": jpeg_usable(community_img),
        "due_awaiting_review_or_photo": queued_due,
        "critical": sorted(set(critical)),
        "notices": sorted(set(notices)),
    }
    (OUT / "prepublish-check.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Pre-publish QA:", len(published), "articles;",
          len(manifests), "licensed photo assignments;",
          len(critical), "critical failures;",
          len(queued_due), "due articles held")
    if critical:
        for item in critical[:35]:
            print("FAIL:", item, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
