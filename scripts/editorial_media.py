#!/usr/bin/env python3
"""Validate, credit and render a local BucharestUA cover."""

from html import escape
import re
from urllib.parse import unquote, urlsplit

BASE = "https://dbc44mys4b-glitch.github.io/"
AI_KIND = "ai_illustration"
AI_CREDIT = "AI-иллюстрация BucharestUA"
EDITORIAL_COVER_MARKER = "BUCHARESTUA_EDITORIAL_COVER"
PHOTO_RIGHTS_FIELDS = ("license", "license_url", "source_url", "commons_title")
JPEG_SIGNATURE = b"\xff\xd8\xff"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def valid_photo_license(name, license_url):
    match = re.fullmatch(r"CC (BY(?:-SA)?)\s+([234]\.0)(?:\s+(ro|de|fr))?", name.strip(), re.I)
    if match:
        code, version, region = match.groups()
        expected = f"https://creativecommons.org/licenses/{code.lower()}/{version}"
        if region:
            expected += "/" + region.lower()
        return license_url.rstrip("/") == expected
    public_domain = "https://creativecommons.org/publicdomain/"
    if name.strip().upper() in {"CC0", "CC0 1.0"}:
        return license_url.rstrip("/") == public_domain + "zero/1.0"
    if name.strip().upper() in {"PUBLIC DOMAIN", "PD"}:
        return license_url.rstrip("/") in {public_domain + "zero/1.0", public_domain + "mark/1.0"}
    return False


def cover_src(slug, cover):
    extension = ".png" if cover.get("kind") == AI_KIND else ".jpg"
    return "assets/covers/" + slug + extension


def cover_alt(cover):
    alt = cover["alt"].strip()
    return "AI-иллюстрация: " + alt if cover.get("kind") == AI_KIND else alt


def cover_problem(root, slug, cover):
    """Return the reason a cover fails editorial requirements, or None."""
    if not isinstance(cover, dict):
        return "missing cover assignment"
    kind = cover.get("kind", "photo")
    if kind not in ("photo", AI_KIND):
        return "unknown cover kind"
    fields = ("author", "alt")
    if kind == "photo":
        fields += PHOTO_RIGHTS_FIELDS
    if not all(isinstance(cover.get(key), str) and cover[key].strip() for key in fields):
        return "incomplete cover attribution"
    if kind == AI_KIND:
        if cover["author"] != "BucharestUA" or any(key in cover for key in PHOTO_RIGHTS_FIELDS):
            return "AI cover must be an original BucharestUA illustration with no photo attribution"
    else:
        if not valid_photo_license(cover["license"], cover["license_url"]):
            return "unapproved photo license or mismatched license URL"
        try:
            source = urlsplit(cover["source_url"])
        except ValueError:
            return "invalid Commons photo source URL"
        title = cover["commons_title"].replace("_", " ")
        source_title = unquote(source.path.removeprefix("/wiki/")).replace("_", " ")
        if (source.scheme != "https" or source.netloc != "commons.wikimedia.org"
                or not source.path.startswith("/wiki/") or not title.startswith("File:")
                or source_title != title):
            return "photo source must match the attributed Wikimedia Commons file"

    image_file = root / cover_src(slug, cover)
    signature = PNG_SIGNATURE if kind == AI_KIND else JPEG_SIGNATURE
    if not image_file.is_file() or image_file.stat().st_size < 8_000:
        return "missing or undersized local cover"
    with image_file.open("rb") as image:
        if image.read(len(signature)) != signature:
            return "local cover does not match its image format"
    return None


def cover_markup(entry, cover):
    src = cover_src(entry["slug"], cover)
    if cover.get("kind") == AI_KIND:
        dimensions = ""
        caption = escape(AI_CREDIT) + "."
    else:
        dimensions = 'width="1200" height="750" '
        caption = (
            'Фото: <a target="_blank" rel="noopener noreferrer" href="' +
            escape(cover["source_url"], quote=True) + '">' +
            escape(cover["author"]) + '</a> · <a target="_blank" rel="license noopener noreferrer" href="' +
            escape(cover["license_url"], quote=True) + '">' +
            escape(cover["license"]) + '</a>. Иллюстрация или фрагмент кадра.'
        )
    return (
        '<!-- BUCHARESTUA_MEDIA -->'
        '<figure class="journal-cover">'
        '<img src="' + escape(src, quote=True) + '" '
        + dimensions + 'loading="eager" decoding="async" '
        'fetchpriority="high" alt="' + escape(cover_alt(cover), quote=True) + '">'
        '<figcaption>' + caption + '</figcaption></figure>'
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
    if cover:
        tags = (
            ('property="og:image"', BASE + cover_src(slug, cover)),
            ('property="og:image:alt"', cover_alt(cover)),
            ('name="twitter:card"', "summary_large_image"),
        )
        for attr, value in tags:
            tag = '<meta ' + attr + ' content="' + escape(value, quote=True) + '">'
            pattern = r'<meta ' + attr + r'[^>]*>'
            if re.search(pattern, html):
                html = re.sub(pattern, lambda match: tag, html, count=1)
            else:
                html = html.replace("</head>", tag + "</head>", 1)
    if not cover and "<!-- BUCHARESTUA_MEDIA -->" in html:
        html = re.sub(
            r'<!-- BUCHARESTUA_MEDIA --><figure class="journal-cover">.*?</figure>',
            "", html, count=1, flags=re.S
        )
        html = re.sub(r'<meta property="og:image"[^>]*>', "", html)
        html = re.sub(r'<meta property="og:image:alt"[^>]*>', "", html)
        html = re.sub(r'<meta name="twitter:card"[^>]*>', "", html)
    return html
