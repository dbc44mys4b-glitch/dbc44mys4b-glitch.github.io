#!/usr/bin/env python3
"""Prepare and verify a single manually approved BucharestUA release."""

import argparse
from datetime import date, datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from editorial_media import AI_CREDIT, AI_KIND, cover_alt, cover_problem, cover_src, decorate_html
from prepublish_check import HTMLInspector, check_article
from sitemap import BASE, NS, parse_sitemap, update_sitemaps
from social_feed import write_rss

ROOT = Path(__file__).resolve().parents[1]
TELEGRAM = "https://t.me/bucharest_info"
QUEUE = ROOT / "content-queue/articles.json"
RELEASES = Path("editorial/releases")
MANIFEST = Path("media/assigned-images.json")
START = "<!-- BUCHARESTUA_EDITORIAL_START -->"
END = "<!-- BUCHARESTUA_EDITORIAL_END -->"


def text(x):
    return escape(str(x), quote=True)


def build_page(entry, cover):
    slug = entry["slug"]
    title = entry["title"]
    desc = entry["description"]
    url = BASE + slug + ".html"
    date = entry["publish_date"]
    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc, "inLanguage": "ru",
        "datePublished": date, "dateModified": entry.get("date_modified", date),
        "image": BASE + cover_src(slug, cover),
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "BucharestUA"},
        "publisher": {"@type": "Organization", "name": "BucharestUA", "url": BASE}
    }, ensure_ascii=False).replace("</", "<\\/")
    parts = [
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>' + text(title) + ' | BucharestUA</title>',
        '<meta name="description" content="' + text(desc) + '">',
        '<link rel="canonical" href="' + text(url) + '">',
        '<meta property="og:type" content="article">',
        '<meta property="og:title" content="' + text(title) + '">',
        '<meta property="og:description" content="' + text(desc) + '">',
        '<meta property="og:url" content="' + text(url) + '">',
        '<link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg">',
        '<script type="application/ld+json">' + schema + '</script></head><body>',
        '<header class="site-header"><nav class="wrap nav" aria-label="Навигация">',
        '<a class="logo" href="index.html"><span class="brand-icon">✦</span>BUCHARESTUA</a>',
        '<div class="navlinks"><a href="articles.html">Статьи</a><a href="guides.html">Справочник</a>',
        '<a href="about.html">О проекте</a></div>',
        '<a class="cta-small" href="' + TELEGRAM + '" rel="noopener noreferrer" target="_blank">Telegram ↗</a>',
        '</nav></header><main><div class="wrap guide-layout"><div class="guide-hero">',
        '<span class="kicker">BUCHARESTUA · ГОРОДСКОЙ СПРАВОЧНИК</span>',
        '<h1 style="font-size:clamp(32px,4.3vw,50px)">' + text(title) + '</h1>',
        '<p style="font-size:17px;color:#536079;line-height:1.8">' + text(entry["intro"]) + '</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '" rel="noopener noreferrer" target="_blank">',
        'Обсудить в Telegram ↗</a></div><article class="prose">',
        '<p class="editor-note">BucharestUA · ' + text(date) + ' · Практический материал</p>'
    ]
    for sec in entry["sections"]:
        parts.append('<section class="guide-panel"><h2>' + text(sec["heading"]) + '</h2>')
        for p in sec.get("paragraphs", []):
            if p.strip() == entry["intro"].strip():
                continue
            parts.append('<p>' + text(p) + '</p>')
        bullets = sec.get("bullets", [])
        if bullets:
            parts.append('<ul>')
            for bullet in bullets:
                parts.append('<li>' + text(bullet) + '</li>')
            parts.append('</ul>')
        parts.append('</section>')
    if entry.get("romanian_terms"):
        parts.append('<section class="guide-panel"><h2>Как искать эту услугу по-румынски</h2>')
        parts.append('<p>Для поиска на картах и общения с местными исполнителями могут пригодиться румынские названия. Используйте их вместе с вашим районом или ближайшей станцией метро; это подсказки, а не рейтинг поставщиков услуг.</p><ul>')
        for term in entry["romanian_terms"]:
            parts.append('<li lang="ro">' + text(term) + '</li>')
        parts.append('</ul></section>')
    parts += [
        '<section class="guide-panel"><h2>Полезные материалы по теме</h2><ul>'
    ]
    for item in entry.get("related", []):
        href = item["href"]
        if not re.fullmatch(r"[a-z0-9-]+\.html", href):
            raise ValueError("Only internal .html links are permitted in related")
        if not (ROOT / href).is_file():
            continue  # a future article must not become a broken link
        parts.append('<li><a href="' + text(href) + '">' + text(item["text"]) + '</a></li>')
    if entry.get("sources"):
        parts.append('</ul></section><section class="guide-panel"><h2>Где проверить актуальные сведения</h2><ul>')
        parts.append('<li>Источники проверены ' + text(entry["fact_checked_on"]) + '.</li>')
        for source in entry["sources"]:
            address = source.get("url", "")
            if not address.startswith("https://"):
                raise ValueError("Sources must use HTTPS URLs")
            parts.append('<li><a href="' + text(address) + '" rel="noopener noreferrer" target="_blank">' + text(source["label"]) + '</a></li>')
    parts += [
        '</ul></section><section class="guide-panel"><h2>Спросить жителей Бухареста</h2>',
        '<p>В BucharestUA обсуждают вопросы города и делятся личным опытом. Уточняйте условия, цены и рекомендации самостоятельно; не размещайте паспортные, банковские и другие чувствительные данные.</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '" rel="noopener noreferrer" target="_blank">',
        'Открыть городской чат ↗</a></section>',
        '<p><a href="articles.html">← К списку статей</a></p></article></div></main>',
        '<footer><div class="wrap footer-inner"><strong>BucharestUA</strong>',
        '<a href="' + TELEGRAM + '" rel="noopener noreferrer" target="_blank">Telegram ↗</a>',
        '</div></footer></body></html>'
    ]
    return "\n".join(parts) + "\n"


def required_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: expected nonempty text")
    return value


def iso_date(value, field):
    try:
        parsed = date.fromisoformat(required_text(value, field))
    except ValueError as error:
        raise ValueError(f"{field}: expected YYYY-MM-DD") from error
    if parsed.isoformat() != value:
        raise ValueError(f"{field}: expected YYYY-MM-DD")
    return parsed


def prepare(draft, staging, today):
    entry = json.loads(draft.read_text(encoding="utf-8"))
    if not isinstance(entry, dict):
        raise ValueError("Draft must be a JSON object")
    for field in ("slug", "title", "description", "intro", "category", "image"):
        required_text(entry.get(field), field)
    slug = entry["slug"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", slug) or not 5 <= len(slug) <= 90:
        raise ValueError("Invalid article slug")
    page = f"{slug}.html"
    site_path = ROOT / page
    old_page = site_path.read_bytes() if site_path.is_file() else None
    published = iso_date(entry.get("publish_date"), "publish_date")
    checked = iso_date(entry.get("fact_checked_on"), "fact_checked_on")
    modified = iso_date(entry.get("date_modified", entry["publish_date"]), "date_modified")
    if not checked <= modified or not published <= modified or checked > today:
        raise ValueError("Publication, revision or fact-check dates are inconsistent")
    if old_page is not None:
        if "date_modified" not in entry:
            raise ValueError("Existing page: review as a revision and specify date_modified")
        catalog = (ROOT / "articles.html").read_text(encoding="utf-8")
        if f'href="{page}"' not in catalog:
            raise ValueError("Existing URL is outside the article catalog")
    elif "date_modified" in entry:
        raise ValueError("New articles use publish_date only")

    sections = entry.get("sections")
    if not isinstance(sections, list) or len(sections) < 3:
        raise ValueError("At least three substantive sections are required")
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("Each section must be a JSON object")
        required_text(section.get("heading"), "section heading")
        paragraphs = section.get("paragraphs", [])
        bullets = section.get("bullets", [])
        if not isinstance(paragraphs, list) or not isinstance(bullets, list) or not (paragraphs or bullets):
            raise ValueError("Each section needs paragraphs or bullets")
        for item in paragraphs + bullets:
            required_text(item, "paragraph or bullet")

    sources = entry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("At least one verified primary source is required")
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be a JSON object")
        required_text(source.get("label"), "source label")
        link = required_text(source.get("url"), "source URL")
        parsed = urlsplit(link)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or any(c.isspace() for c in link):
            raise ValueError("Source URL must be a valid HTTPS address")

    cover = entry.get("cover")
    if not isinstance(cover, dict):
        raise ValueError("A rights-cleared cover is required")
    image = Path(entry["image"])
    if image.is_absolute():
        raise ValueError("Use an image path relative to the draft")
    source_image = (draft.parent / image).resolve()
    if not source_image.is_relative_to(draft.parent):
        raise ValueError("Keep the image beside the draft or in a subdirectory")
    cover_path = Path(cover_src(slug, cover))
    staged_image = staging / cover_path
    staged_image.parent.mkdir(parents=True)
    shutil.copyfile(source_image, staged_image)
    problem = cover_problem(staging, slug, cover)
    if problem:
        raise ValueError(problem)

    html = decorate_html(build_page(entry, cover), entry, cover)
    parser = HTMLInspector()
    parser.feed(html)
    errors = check_article(parser, slug, cover, cover_root=staging)
    if errors:
        raise ValueError("\n".join(errors))

    fingerprint = sha256(json.dumps({
        "entry": entry,
        "html_sha256": sha256(html.encode("utf-8")).hexdigest(),
        "image_sha256": sha256(staged_image.read_bytes()).hexdigest(),
        "replaces_sha256": sha256(old_page).hexdigest() if old_page is not None else None,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    (staging / page).write_text(html, encoding="utf-8")
    return entry, cover, fingerprint


def write_catalog(output, entry, cover):
    path = ROOT / "articles.html"
    before, cards = path.read_text(encoding="utf-8").split(START, 1)
    cards, after = cards.split(END, 1)
    grid = '<div class="m-story-grid">'
    if not cards.startswith(grid):
        raise ValueError("Article card grid missing")
    slug = entry["slug"]
    credit = (AI_CREDIT if cover.get("kind") == AI_KIND
              else cover["author"] + " · " + cover["license"])
    card = (
        f'<a class="m-card" href="{slug}.html"><div class="m-card-visual m-visual-0">'
        f'<img src="{cover_src(slug, cover)}" alt="{text(cover_alt(cover))}" loading="lazy">'
        f'<span class="m-image-credit">{text(credit)}</span></div>'
        f'<div class="m-card-body"><span class="m-meta">{text(entry["category"])} · '
        f'{entry["publish_date"]}</span><h3>{text(entry["title"])}</h3>'
        f'<p>{text(entry["description"])}</p><span class="m-read">Читать историю ↗</span></div></a>'
    )
    existing = re.compile(r'<a class="m-card\b[^"]*" href="' + re.escape(slug) + r'\.html">.*?</a>', re.S)
    cards, count = existing.subn(lambda _: card, cards)
    if count > 1:
        raise ValueError("Duplicate cards for the selected article")
    if count == 0:
        cards = grid + card + cards[len(grid):]
        total = len(re.findall(r'<a class="m-card\b', cards))
        before = re.sub(r"(?<=<h2>Все публикации</h2><span>)\d+", str(total), before, count=1)
    (output / path.name).write_text(before + START + cards + END + after, encoding="utf-8")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_release(staging, entry, cover, version, approval_ref, today):
    slug = entry["slug"]
    write_catalog(staging, entry, cover)
    url = BASE + slug + ".html"
    pages = parse_sitemap((ROOT / "sitemap.xml").read_bytes())
    lastmod = entry.get("date_modified", entry["publish_date"])
    for item in pages:
        if item.findtext(NS + "loc") == url:
            tag = item.find(NS + "lastmod")
            if tag is None:
                tag = ET.SubElement(item, NS + "lastmod")
            tag.text = lastmod
    # Starting from the validated source tree, always serialize both sitemap formats.
    ET.register_namespace("", NS[1:-1])
    sitemap = staging / "sitemap.xml"
    sitemap.write_bytes(ET.tostring(pages, encoding="UTF-8", xml_declaration=True) + b"\n")
    update_sitemaps(sitemap, pages, {url: lastmod})
    write_rss(staging / "feed.xml", ROOT / "feed.xml", entry)
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest[slug] = cover
    write_json(staging / MANIFEST, manifest)
    write_json(staging / RELEASES / (slug + ".json"), {
        "slug": slug,
        "version": version,
        "approval_ref": approval_ref,
        "fact_checked_on": entry["fact_checked_on"],
        "released_on": today.isoformat(),
        "page_sha256": sha256((staging / (slug + ".html")).read_bytes()).hexdigest(),
        "image_sha256": sha256((staging / cover_src(slug, cover)).read_bytes()).hexdigest(),
        "image_path": cover_src(slug, cover),
    })


def status():
    archive = json.loads(QUEUE.read_text(encoding="utf-8"))
    with_page = sum((ROOT / (item["slug"] + ".html")).is_file() for item in archive)
    print(f"Историческая очередь: {len(archive)} тем, {len(archive) - with_page} без страницы в репозитории.")
    print("Рабочие черновики, замечания и решения владельца ведутся в чате.")
    for path in sorted((ROOT / RELEASES).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        print(f'{record["released_on"]} {record["slug"]} {record["version"][:12]} — есть запись выпуска; HTTP отдельно')


def verify(slug):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", slug):
        raise ValueError("Invalid article slug")
    record = json.loads((ROOT / RELEASES / (slug + ".json")).read_text(encoding="utf-8"))
    for path, label, accept in [
        (slug + ".html", "page_sha256", "text/html"),
        (record["image_path"], "image_sha256", "image/"),
    ]:
        url = BASE + path
        with urlopen(url, timeout=20) as response:
            if response.status != 200 or response.url != url or not response.headers.get_content_type().startswith(accept):
                raise ValueError(f"Unexpected public response: {url}")
            if sha256(response.read()).hexdigest() != record[label]:
                raise ValueError(f"Public content differs from the approved release: {url}")
        print(f"HTTP 200, approved bytes: {url}")
    with urlopen(BASE + "sitemap.xml", timeout=20) as response:
        sitemap = parse_sitemap(response.read())
        if response.status != 200 or BASE + slug + ".html" not in [item.findtext(NS + "loc") for item in sitemap]:
            raise ValueError("Published URL missing from live sitemap")
    print("URL present in public sitemap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    verification = commands.add_parser("verify")
    verification.add_argument("slug")
    for command in ("preview", "publish"):
        action = commands.add_parser(command)
        action.add_argument("draft", type=Path)
        action.add_argument("--output", type=Path, required=True)
        if command == "publish":
            action.add_argument("--approved", required=True)
            action.add_argument("--approval-ref", required=True)
    args = parser.parse_args()
    try:
        if args.command == "status":
            status()
            return
        if args.command == "verify":
            verify(args.slug)
            return
        output = args.output.resolve()
        if output.is_relative_to(ROOT) or output.exists():
            raise ValueError("Output must be a new directory outside the site checkout")
        today = datetime.now(ZoneInfo("Europe/Bucharest")).date()
        with TemporaryDirectory(dir=output.parent) as temp:
            staging = Path(temp) / "bundle"
            entry, cover, version = prepare(args.draft.resolve(), staging, today)
            if args.command == "publish":
                approval_ref = required_text(args.approval_ref, "approval reference")
                if args.approved != version:
                    raise ValueError("Prepared text or cover differs from the version approved by the owner")
                effective_date = entry.get("date_modified", entry["publish_date"])
                if effective_date > today.isoformat():
                    raise ValueError("The approved article date is still in the future in Bucharest")
                write_release(staging, entry, cover, version, approval_ref, today)
            else:
                for name in ("styles.css", "favicon.svg"):
                    shutil.copyfile(ROOT / name, staging / name)
            staging.rename(output)
        print(f'{entry["slug"]} {version}')
        print(output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Blocked: {error}\n")


if __name__ == "__main__":
    main()
