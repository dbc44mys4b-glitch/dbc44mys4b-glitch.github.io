#!/usr/bin/env python3
"""Publish only prewritten, reviewed BucharestUA editorial queue entries due today.

This script uses no paid services, no LLM API, and never overwrites existing
articles. Safe to rerun: no publish, sitemap or index changes when up-to-date.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dbc44mys4b-glitch.github.io/"
TELEGRAM = "https://t.me/bucharest_info"
QUEUE = ROOT / "content-queue" / "articles.json"
START = "<!-- BUCHARESTUA_EDITORIAL_START -->"
END = "<!-- BUCHARESTUA_EDITORIAL_END -->"


def text(x):
    return escape(str(x), quote=True)


def build_page(entry):
    slug = entry["slug"]
    title = entry["title"]
    desc = entry["description"]
    url = BASE + slug + ".html"
    date = entry["publish_date"]
    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc, "inLanguage": "ru",
        "datePublished": date, "dateModified": date,
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
            parts.append('<p>' + text(p) + '</p>')
        bullets = sec.get("bullets", [])
        if bullets:
            parts.append('<ul>')
            for bullet in bullets:
                parts.append('<li>' + text(bullet) + '</li>')
            parts.append('</ul>')
        parts.append('</section>')
    parts += [
        '<section class="guide-panel"><h2>Полезные материалы по теме</h2><ul>'
    ]
    for item in entry.get("related", []):
        href = item["href"]
        if not re.fullmatch(r"[a-z0-9-]+\.html", href):
            raise ValueError("Only internal .html links are permitted in related")
        if not (ROOT / href).is_file():
            raise ValueError("Related page does not exist: " + href)
        parts.append('<li><a href="' + text(href) + '">' + text(item["text"]) + '</a></li>')
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


def main():
    entries = json.loads(QUEUE.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date().isoformat()
    new_pages = []
    for entry in sorted(entries, key=lambda x: x["publish_date"]):
        slug = entry["slug"]
        if not re.fullmatch(r"[a-z0-9-]{5,90}", slug):
            raise ValueError("Invalid slug: " + slug)
        if entry["publish_date"] > today:
            continue
        path = ROOT / (slug + ".html")
        if path.exists():
            continue
        html = build_page(entry)
        path.write_text(html, encoding="utf-8")
        new_pages.append(path.name)
    if not new_pages:
        print("No queued article due for publication.")
        return

    sitemap = ROOT / "sitemap.xml"
    content = sitemap.read_text(encoding="utf-8")
    ET.fromstring(content)
    for entry in entries:
        name = entry["slug"] + ".html"
        if not (ROOT / name).exists():
            continue
        url = BASE + name
        if "<loc>" + url + "</loc>" not in content:
            line = "<url><loc>" + url + "</loc><lastmod>" + entry["publish_date"] + "</lastmod></url>"
            content = content.replace("</urlset>", line + "\n</urlset>")
    ET.fromstring(content)
    sitemap.write_text(content, encoding="utf-8")

    catalog = ROOT / "articles.html"
    current = catalog.read_text(encoding="utf-8")
    live = [e for e in entries if (ROOT / (e["slug"] + ".html")).is_file()]
    links = "".join(
        '<a class="guide-link" href="' + text(e["slug"]) + '.html"><strong>' +
        text(e["title"]) + ' →</strong><span>' + text(e["description"]) +
        '</span></a>' for e in sorted(live, key=lambda x: x["publish_date"], reverse=True)
    )
    block = START + '<section class="guide-panel"><h2>Новые темы о жизни и общении в Бухаресте</h2>' + \
        '<div class="guide-links">' + links + '</div></section>' + END
    if START in current and END in current:
        left = current.split(START, 1)[0]
        right = current.split(END, 1)[1]
        current = left + block + right
    else:
        anchor = '<section class="guide-panel"><h2>Документы</h2>'
        if anchor not in current:
            raise ValueError("Could not find insertion anchor in articles.html")
        current = current.replace(anchor, block + anchor, 1)
    catalog.write_text(current, encoding="utf-8")
    print("Published: " + ", ".join(new_pages))


if __name__ == "__main__":
    main()
