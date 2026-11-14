#!/usr/bin/env python3
"""Validate one candidate locally or audit existing BucharestUA pages."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from zoneinfo import ZoneInfo
from editorial_media import (
    AI_CREDIT, AI_KIND, EDITORIAL_COVER_MARKER, cover_alt, cover_problem, cover_src,
)
from sitemap import BASE, parse_sitemap, sitemap_locations
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
TG = "https://t.me/bucharest_info"
OUT = ROOT / "reports"


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
        self.in_cover = False
        self.in_cover_caption = False
        self.cover_images = []
        self.cover_caption = ""
        self.cover_caption_links = []
        self.editorial_cover = False
        self.editorial_cover_label = ""

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
        elif tag == "div" and "editorial-cover-fallback" in attrs.get("class", "").split():
            if attrs.get("role") == "img":
                self.editorial_cover_label = attrs.get("aria-label", "").strip()
        elif tag == "figure":
            self.in_cover = "journal-cover" in attrs.get("class", "").split()
        elif tag == "figcaption" and self.in_cover:
            self.in_cover_caption = True
        elif tag == "img":
            self.images.append(attrs)
            if self.in_cover:
                self.cover_images.append(attrs)
        elif tag == "a":
            href = attrs.get("href", "")
            self.links.append(href)
            if self.in_cover_caption:
                self.cover_caption_links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "figcaption":
            self.in_cover_caption = False
        elif tag == "figure":
            self.in_cover = False

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data
        if self.in_cover_caption:
            self.cover_caption += data

    def handle_comment(self, data):
        if data.strip() == EDITORIAL_COVER_MARKER:
            self.editorial_cover = True


def inspect_html(path):
    p = HTMLInspector()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def local_target(src):
    parsed = urlparse(src)
    if parsed.scheme not in ("", "http", "https"):
        return None
    if parsed.netloc != urlparse(BASE).netloc and (parsed.scheme or parsed.netloc):
        return None
    value = unquote(parsed.path).lstrip("/")
    if not value or ".." in Path(value).parts:
        return None
    return ROOT / value


def check_cover(parser, slug, cover, *, cover_root=ROOT):
    if parser.editorial_cover:
        if cover is not None or parser.cover_images or not parser.editorial_cover_label:
            return [f"Invalid editorial text cover: {slug}"]
        if (parser.meta.get("og:image") != BASE + "og-image.png"
                or not parser.meta.get("og:image:alt", "").strip()
                or not (ROOT / "og-image.png").is_file()):
            return [f"Invalid site social preview for editorial text cover: {slug}"]
        return []

    problem = cover_problem(cover_root, slug, cover)
    if problem:
        return [f"Invalid cover for {slug}: {problem}"]

    errors = []
    src = cover_src(slug, cover)
    alt = cover_alt(cover)
    if (len(parser.cover_images) != 1 or parser.cover_images[0].get("src") != src
            or parser.cover_images[0].get("alt") != alt):
        errors.append(f"Visible cover or expected alt missing: {slug}")
    if parser.meta.get("og:image") != BASE + src or parser.meta.get("og:image:alt") != alt:
        errors.append(f"Social preview cover or expected alt missing: {slug}")

    caption = parser.cover_caption.strip()
    if cover.get("kind") == AI_KIND:
        if caption != AI_CREDIT + "." or parser.cover_caption_links:
            errors.append(f"AI illustration credit missing or incorrect: {slug}")
    else:
        required_links = {cover["source_url"], cover["license_url"]}
        if (not required_links.issubset(parser.cover_caption_links)
                or cover["author"] not in caption or cover["license"] not in caption):
            errors.append(f"Photo attribution/license missing in cover caption: {slug}")
    return errors


def check_article_markup(parser, slug):
    errors = []
    if not parser.title_text.strip() or parser.h1 != 1 or not parser.meta.get("description", "").strip():
        errors.append(f"Incomplete title/H1/description: {slug}")
    if parser.h2 < 3:
        errors.append(f"Article too thin (fewer than three sections): {slug}")
    if parser.canonical != BASE + slug + ".html":
        errors.append(f"Wrong canonical: {slug}")
    if parser.html_lang != "ru":
        errors.append(f"Missing or unexpected language: {slug}")
    if not any(link.startswith("https://t.me/share/url?") for link in parser.links):
        errors.append(f"Telegram share button missing: {slug}")
    if not any(link.rstrip("/") == TG for link in parser.links):
        errors.append(f"Join Telegram call-to-action missing: {slug}")
    return errors


def check_local_references(parser, slug, *, staged_cover=None):
    errors = []
    filename = slug + ".html"
    for image in parser.images:
        src = image.get("src", "")
        target = local_target(src)
        if target is None:
            errors.append(f"Unapproved remote or unsafe image reference: {filename} -> {src}")
        elif src != staged_cover and not target.is_file():
            errors.append(f"Missing local image: {filename} -> {src}")
        if not image.get("alt", "").strip():
            errors.append(f"Missing image alt: {filename} -> {src}")
    for href in parser.links:
        parsed = urlparse(href)
        if parsed.scheme not in ("", "http", "https") or not parsed.path.endswith(".html"):
            continue
        if parsed.netloc and parsed.netloc != urlparse(BASE).netloc:
            continue
        target = local_target(href)
        if target is None or not target.is_file():
            errors.append(f"Broken internal link: {filename} -> {href}")
    return errors


def check_article(parser, slug, cover, *, cover_root=ROOT) -> list[str]:
    """Validate the selected candidate before its image enters the live tree."""
    if parser.editorial_cover:
        cover_errors = [f"An attributed photograph or original illustration is required: {slug}"]
    else:
        cover_errors = check_cover(parser, slug, cover, cover_root=cover_root)
    staged_cover = None if cover_errors else cover_src(slug, cover)
    return cover_errors + check_article_markup(parser, slug) + check_local_references(
        parser, slug, staged_cover=staged_cover,
    )


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

    sitemap = parse_sitemap((ROOT / "sitemap.xml").read_bytes())
    sitemap_urls = set(sitemap_locations(sitemap))
    if not (ROOT / "styles.css").is_file():
        critical.append("Global CSS missing")
    if TG not in (ROOT / "index.html").read_text(encoding="utf-8"):
        critical.append("Telegram destination absent from homepage")

    published = []
    for entry in queue:
        slug = entry["slug"]
        path = ROOT / (slug + ".html")
        if not path.is_file():
            continue
        published.append(slug)
        parser = inspect_html(path)
        critical.extend(check_cover(parser, slug, manifests.get(slug)))
        critical.extend(check_article_markup(parser, slug))
        critical.extend(check_local_references(parser, slug))
        if BASE + slug + ".html" not in sitemap_urls:
            critical.append(f"Published URL not in sitemap: {slug}")
        if len(entry.get("intro", "")) < 100:
            notices.append(f"Review short introduction before next editorial refresh: {slug}")

    # The community entry is a standalone hub, not part of queue.
    cfile = ROOT / "community.html"
    community_cover_verified = False
    if not cfile.is_file():
        critical.append("Community page missing")
    else:
        parser = inspect_html(cfile)
        cover_errors = check_cover(parser, "community", manifests.get("community"))
        critical.extend(cover_errors)
        critical.extend(check_local_references(parser, "community"))
        community_cover_verified = not cover_errors
        if TG not in parser.links:
            critical.append("Community Telegram destination missing")
        if BASE + "community.html" not in sitemap_urls:
            critical.append("Community missing from sitemap")

    ai_count = sum(isinstance(cover, dict) and cover.get("kind") == AI_KIND for cover in manifests.values())
    photo_count = sum(isinstance(cover, dict) and cover.get("kind", "photo") == "photo"
                      for cover in manifests.values())
    status = {
        "checked_in_bucharest": today,
        "queue_size": len(queue),
        "published_articles": len(published),
        "photo_assignments": photo_count,
        "ai_illustration_assignments": ai_count,
        "community_cover_verified": community_cover_verified,
        "unpublished_queue_entries": len(queue) - len(published),
        "critical": sorted(set(critical)),
        "notices": sorted(set(notices)),
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "prepublish-check.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Site audit:", len(published), "published queue articles;",
          len(manifests), "cover assignments;",
          len(critical), "critical failures")
    if critical:
        for item in critical[:35]:
            print("FAIL:", item, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
