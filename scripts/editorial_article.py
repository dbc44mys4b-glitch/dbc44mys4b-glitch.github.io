"""Render guides and news in the same BucharestUA article layout."""

from html import escape
import json

from editorial_media import cover_src
from sitemap import BASE

TELEGRAM = "https://t.me/bucharest_info"


def link(href, label):
    return f'<a href="{escape(href)}">{escape(label)}</a>'


def date_markup(value):
    return f'<time datetime="{value}">{value}</time>'


def build_page(entry, cover):
    slug = entry["slug"]
    title = escape(entry["title"])
    desc = escape(entry["description"])
    url = BASE + slug + ".html"
    published = entry["publish_date"]
    modified = entry.get("date_modified", published)
    news = entry.get("type") == "news"
    label = "Новости Бухареста" if news else "Городской справочник"
    schema = {
        "@context": "https://schema.org", "@type": "NewsArticle" if news else "Article",
        "headline": entry["title"], "description": entry["description"], "inLanguage": "ru",
        "datePublished": published, "dateModified": modified,
        "image": BASE + cover_src(slug, cover), "mainEntityOfPage": url,
        "articleSection": entry["category"], "citation": [source["url"] for source in entry["sources"]],
        "author": {"@type": "Organization", "name": "BucharestUA"},
        "publisher": {"@type": "Organization", "name": "BucharestUA", "url": BASE},
    }
    ld = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    byline = f'Редакция BucharestUA · {date_markup(published)}'
    if modified != published:
        byline += f' · Обновлено {date_markup(modified)}'
    parts = [
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="theme-color" content="#f7f5f0">',
        f'<title>{title} | BucharestUA</title>',
        f'<meta name="description" content="{desc}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="article:published_time" content="{published}">',
        f'<meta property="article:modified_time" content="{modified}">',
        f'<link rel="alternate" type="application/rss+xml" title="BucharestUA" href="{BASE}feed.xml">',
        '<link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg">',
        f'<script type="application/ld+json">{ld}</script></head><body class="editorial-story">',
        '<header class="site-header"><nav class="wrap nav editorial-nav" aria-label="Навигация">',
        f'<a class="logo" href="{BASE}index.html">BucharestUA</a>',
        link(BASE + "articles.html", "Лента") + link(BASE + "guides.html", "Справочник"),
        '</nav></header><main><div class="wrap guide-layout"><header class="guide-hero">',
        f'<span class="kicker">{label} · {escape(entry["category"])}</span>',
        f'<h1>{title}</h1>',
        f'<p>{escape(entry["intro"])}</p>',
        f'<div class="editorial-byline">{byline}</div></header>',
        '<article class="prose">',
    ]
    if news:
        parts.append(f'<p class="editorial-event">Дата события · {date_markup(entry["event_date"])}. '
                     f'Первичный источник · {link(entry["sources"][0]["url"], entry["sources"][0]["label"])}</p>')
    for section in entry["sections"]:
        parts.append(f'<section class="guide-panel"><h2>{escape(section["heading"])}</h2>')
        for paragraph in section.get("paragraphs", []):
            parts.append(f'<p>{escape(paragraph)}</p>')
        if section.get("bullets"):
            parts.append('<ul>')
            parts.extend(f'<li>{escape(item)}</li>' for item in section["bullets"])
            parts.append('</ul>')
        parts.append('</section>')
    if news:
        parts.append('<section class="guide-panel"><h2>Что это значит для жителей</h2>'
                     f'<p>{escape(entry["event_context"])}</p></section>')
    if entry.get("romanian_terms"):
        parts.append('<section class="guide-panel"><h2>Термины на румынском</h2><ul>')
        parts.extend(f'<li lang="ro">{escape(term)}</li>' for term in entry["romanian_terms"])
        parts.append('</ul></section>')
    parts.append('<section class="guide-panel editorial-sources"><h2>Источники</h2>'
                 f'<p>Проверено {date_markup(entry["fact_checked_on"])}</p><ul>')
    parts.extend(f'<li>{link(source["url"], source["label"])}</li>' for source in entry["sources"])
    parts.append('</ul></section>')
    if entry.get("related"):
        parts.append('<section class="guide-panel"><h2>По теме</h2><ul>')
        parts.extend(f'<li>{link(BASE + item["href"], item["text"])}</li>' for item in entry["related"])
        parts.append('</ul></section>')
    parts.extend([
        '<div class="editorial-footer-links">',
        f'<a href="{TELEGRAM}">Городской чат в Telegram ↗</a>',
        link(BASE + "articles.html", "Все публикации") + '</div></article></div></main>',
        '<footer><div class="wrap footer-inner"><strong>BucharestUA</strong></div></footer></body></html>',
    ])
    return "\n".join(parts) + "\n"
