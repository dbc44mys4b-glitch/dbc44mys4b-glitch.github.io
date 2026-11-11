#!/usr/bin/env python3
"""Publish only prewritten, reviewed BucharestUA editorial queue entries due today.

This script uses no paid services, no LLM API, and never overwrites existing
articles. Safe to rerun: no publish, sitemap or index changes when up-to-date.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
from pathlib import Path
from editorial_media import cover_problem, decorate_html
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


def main():
    entries = json.loads(QUEUE.read_text(encoding="utf-8"))
    manifest_path = ROOT / "media/assigned-images.json"
    covers = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    slugs = [e["slug"] for e in entries]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Editorial queue contains duplicate slugs")
    dates = [e["publish_date"] for e in entries]
    for d in dates:
        datetime.strptime(d, "%Y-%m-%d")
    today = datetime.now(ZoneInfo("Europe/Bucharest")).date().isoformat()
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
        # A local cover with verified attribution is required for publication.
        cover = covers.get(slug)
        problem = cover_problem(ROOT, slug, cover)
        if problem:
            print(f"HOLD: {slug}: {problem}")
            continue
        html = decorate_html(build_page(entry), entry, cover)
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

    # A topical directory makes actual published guides discoverable without
    # exposing scheduled pages that do not exist yet.
    categories = {
        "Районы и соседи": [], "Автомобили и транспорт": [],
        "Врачи и здоровье": [], "Семья и дети": [],
        "Техника, покупки и связь": [], "Дом и бытовые услуги": [],
        "Работа, документы и деньги": [], "Отдых и знакомства": []
    }
    for e in live:
        cat = e.get("category", "Отдых и знакомства")
        categories.setdefault(cat, []).append(e)
    body = [
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Услуги и жизнь в Бухаресте: городской справочник | BucharestUA</title>',
        '<meta name="description" content="Где найти врача, СТО, мастера, кружок, сервис телефона и соседей в Бухаресте: тематический справочник с вопросами и подсказками.">',
        '<link rel="canonical" href="' + BASE + 'city-needs.html">',
        '<link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg">',
        '</head><body><header class="site-header"><nav class="wrap nav">',
        '<a class="logo" href="index.html"><span class="brand-icon">✦</span> BUCHARESTUA</a>',
        '<div class="navlinks"><a href="community.html">Сообщество</a><a href="guides.html">Справочник</a><a href="articles.html">Статьи</a></div>',
        '<a class="cta-small" href="' + TELEGRAM + '">Наш Telegram ↗</a></nav></header>',
        '<main><div class="wrap guide-layout"><div class="guide-hero">',
        '<span class="kicker">ГОРОДСКАЯ ЖИЗНЬ · БУХАРЕСТ И ИЛФОВ</span>',
        '<h1>Нужен врач, мастер, ремонт авто или компания по району?</h1>',
        '<p>Собрали практические путеводители по повседневным запросам. Выбирайте тему, проверяйте варианты и спрашивайте жителей города в BucharestUA. Мы не продаём услуги и не гарантируем рекомендации участников.</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '">Задать вопрос в Telegram ↗</a>',
        '</div>'
    ]
    for category, items in categories.items():
        if not items:
            continue
        body.append('<section class="guide-panel"><h2>' + text(category) + '</h2><div class="guide-links">')
        for e in sorted(items, key=lambda x: x["title"]):
            body.append('<a class="guide-link" href="' + text(e["slug"]) + '.html"><strong>' + text(e["title"]) + ' →</strong><span>' + text(e["description"]) + '</span></a>')
        body.append('</div></section>')
    body += [
        '<section class="guide-panel"><h2>Не нашли тему?</h2>',
        '<p>Уточните район, бюджет и желаемый язык общения. Для медицинских, юридических и других важных решений проверяйте квалификацию и первоисточники.</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '">Спросить жителей Бухареста ↗</a></section>',
        '</div></main><footer><div class="wrap footer-inner"><strong>BucharestUA</strong>',
        '<a href="index.html">Главная</a></div></footer></body></html>'
    ]
    (ROOT / "city-needs.html").write_text("\n".join(body) + "\n", encoding="utf-8")
    sitemap_text = sitemap.read_text(encoding="utf-8")
    url = BASE + "city-needs.html"
    if "<loc>" + url + "</loc>" not in sitemap_text:
        sitemap_text = sitemap_text.replace("</urlset>", "<url><loc>" + url + "</loc><lastmod>" + today + "</lastmod></url>\n</urlset>")
        ET.fromstring(sitemap_text)
        sitemap.write_text(sitemap_text, encoding="utf-8")

    # Maintain a dedicated leisure directory from actually published guides.
    # Future scheduled articles must never appear as broken links.
    leisure_categories = [
        "Маршруты", "Куда сходить", "Музеи и история",
        "Семья и дети", "Отдых за городом", "Еда и культура"
    ]
    leisure = [e for e in live if e.get("category") in leisure_categories]
    explore_parts = [
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Что посмотреть в Бухаресте: маршруты, места и выходные | BucharestUA</title>',
        '<meta name="description" content="Бухарест для своих: прогулки на день и выходные, музеи, парки, отдых с детьми, поездки в горы и рестораны. Оригинальные маршруты и советы жителей.">',
        '<link rel="canonical" href="' + BASE + 'explore-bucharest.html">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="Бухарест: куда сходить и чем заняться | BucharestUA">',
        '<meta property="og:url" content="' + BASE + 'explore-bucharest.html">',
        '<link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg">',
        '</head><body><header class="site-header"><nav class="wrap nav">',
        '<a class="logo" href="index.html"><span class="brand-icon">✦</span> BUCHARESTUA</a>',
        '<div class="navlinks"><a href="community.html">Сообщество</a><a href="city-needs.html">Услуги и районы</a>',
        '<a href="articles.html">Все статьи</a><a href="index.html">Главная</a></div>',
        '<a class="cta-small" href="' + TELEGRAM + '" target="_blank" rel="noopener noreferrer">Telegram ↗</a></nav></header>',
        '<main><div class="wrap guide-layout"><div class="guide-hero">',
        '<span class="kicker">BUCHARESTUA · ПРОГУЛКИ И ОТКРЫТИЯ</span>',
        '<h1>Бухарест, в котором хочется задержаться</h1>',
        '<p>Не очередной список красивых фасадов: маршруты по настроению, небольшие музеи, выходные с детьми, гастрономия и поездки по Румынии. Выбирайте программу, учитывайте сезон и делитесь опытом с городским сообществом.</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '" target="_blank" rel="noopener noreferrer">Спросить местных в Telegram ↗</a>',
        '</div>',
        '<section class="guide-panel"><h2>С чего начать знакомство с городом</h2>',
        '<p>Если у вас только день, начните с исторического центра и Calea Victoriei. С детьми выберите музей или ближайший парк; для взрослой компании оставьте время на архитектуру и разговор. У музеев есть собственные расписания — проверяйте их перед визитом.</p>',
        '<div class="guide-links"><a class="guide-link" href="family-activities-bucharest.html"><strong>Куда пойти с ребёнком →</strong><span>Простой семейный план, который можно изменить под погоду</span></a>',
        '<a class="guide-link" href="sports.html"><strong>Спорт и прогулки →</strong><span>Город для активного досуга</span></a>',
        '<a class="guide-link" href="events.html"><strong>Городские события →</strong><span>Где искать актуальную афишу и встречи</span></a></div></section>'
    ]
    for category in leisure_categories:
        section = sorted(
            [e for e in leisure if e.get("category") == category],
            key=lambda e: (e["publish_date"], e["title"]), reverse=True
        )
        if not section:
            continue
        explore_parts.append('<section class="guide-panel"><h2>' + text(category) + '</h2>')
        explore_parts.append('<div class="guide-links">')
        for e in section:
            explore_parts.append(
                '<a class="guide-link" href="' + text(e["slug"]) + '.html">'
                '<strong>' + text(e["title"]) + ' →</strong>'
                '<span>' + text(e["description"]) + '</span></a>'
            )
        explore_parts.append('</div></section>')
    explore_parts += [
        '<section class="guide-panel"><h2>Не нашли подходящую идею?</h2>',
        '<p>Спросите у жителей Бухареста, куда они ходят сами, а не только водят туристов. Перед поездкой проверяйте билеты, транспорт и время работы по официальным источникам.</p>',
        '<a class="btn btn-primary" href="' + TELEGRAM + '" target="_blank" rel="noopener noreferrer">Обсудить выходные в BucharestUA ↗</a>',
        '</section></div></main><footer><div class="wrap footer-inner">',
        '<strong>BucharestUA · независимое городское сообщество</strong>',
        '<a href="' + TELEGRAM + '">Telegram ↗</a></div></footer></body></html>'
    ]
    (ROOT / "explore-bucharest.html").write_text("\n".join(explore_parts) + "\n", encoding="utf-8")
    sitemap_text = sitemap.read_text(encoding="utf-8")
    url = BASE + "explore-bucharest.html"
    if "<loc>" + url + "</loc>" not in sitemap_text:
        sitemap_text = sitemap_text.replace("</urlset>", "<url><loc>" + url + "</loc><lastmod>" + today + "</lastmod></url>\n</urlset>")
        ET.fromstring(sitemap_text)
        sitemap.write_text(sitemap_text, encoding="utf-8")

    print("Published: " + ", ".join(new_pages))


if __name__ == "__main__":
    main()
