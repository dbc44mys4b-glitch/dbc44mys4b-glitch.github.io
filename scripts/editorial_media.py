#!/usr/bin/env python3
"""Validate, credit and render a local BucharestUA cover."""

from html import escape
import re
import struct
import zlib
from urllib.parse import unquote, urlsplit

BASE = "https://dbc44mys4b-glitch.github.io/"
AI_KIND = "ai_illustration"
AI_CREDIT = "AI-иллюстрация BucharestUA"
EDITORIAL_COVER_MARKER = "BUCHARESTUA_EDITORIAL_COVER"
PHOTO_RIGHTS_FIELDS = ("license", "license_url", "source_url", "commons_title", "permission")
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


def image_dimensions(path):
    """Read dimensions and check the file's basic PNG/JPEG structure."""
    data = path.read_bytes()
    if data.startswith(PNG_SIGNATURE):
        offset = len(PNG_SIGNATURE)
        dimensions = None
        has_pixels = False
        while offset + 12 <= len(data):
            size, kind = struct.unpack_from(">I4s", data, offset)
            end = offset + 8 + size
            if end + 4 > len(data):
                break
            crc, = struct.unpack_from(">I", data, end)
            if crc != zlib.crc32(data[offset + 4:end]):
                break
            if kind == b"IHDR" and offset == 8 and size == 13:
                dimensions = struct.unpack_from(">II", data, offset + 8)
            if kind == b"IDAT" and size:
                has_pixels = True
            if kind == b"IEND" and size == 0 and end + 4 == len(data) and dimensions and has_pixels:
                return dimensions
            offset = end + 4
    elif data.startswith(JPEG_SIGNATURE) and data.endswith(b"\xff\xd9"):
        offset = 2
        dimensions = None
        while offset + 4 < len(data) and data[offset] == 0xff:
            offset += 1
            if data[offset] == 0xff:
                continue
            marker = data[offset]
            size, = struct.unpack_from(">H", data, offset + 1)
            if size < 2 or offset + 1 + size >= len(data):
                break
            if marker in (0xc0, 0xc1, 0xc2) and size >= 11:
                height, width = struct.unpack_from(">HH", data, offset + 4)
                dimensions = (width, height)
            if marker == 0xda and dimensions and offset + 3 + size < len(data):
                return dimensions
            offset += 1 + size
    raise ValueError("Unreadable or incomplete local cover")


def https_url(value):
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and parsed.hostname and not parsed.username and not any(c.isspace() for c in value)
    except ValueError:
        return False


def cover_problem(root, slug, cover, *, for_release=False):
    """Return the reason a cover fails editorial requirements, or None."""
    if not isinstance(cover, dict):
        return "missing cover assignment"
    kind = cover.get("kind", "photo")
    fields = {
        "photo": ("license", "license_url", "source_url", "commons_title"),
        "licensed": ("license", "source_url"),
        "original": ("provenance",),
        AI_KIND: (),
    }
    if kind not in fields:
        return "unknown cover kind"
    required = ("author", "alt", *fields[kind])
    if for_release and kind == AI_KIND:
        required += ("provenance",)
    if not all(isinstance(cover.get(key), str) and cover[key].strip() for key in required):
        return "incomplete cover attribution or provenance"
    for key in ("source_url", "license_url"):
        if key in cover and (not isinstance(cover[key], str) or not https_url(cover[key])):
            return f"{key}: expected a public HTTPS link"
    for key in ("changes", "permission"):
        if key in cover and (not isinstance(cover[key], str) or not cover[key].strip()):
            return f"{key}: expected nonempty text"
    if "illustrative" in cover and not isinstance(cover["illustrative"], bool):
        return "illustrative: expected true or false"
    if kind == AI_KIND:
        if cover["author"] != "BucharestUA" or any(key in cover for key in PHOTO_RIGHTS_FIELDS):
            return "AI cover must be an original BucharestUA illustration with no photo attribution"
    if kind == "licensed" and not (cover.get("permission") or (not for_release and cover.get("permission_recorded") is True) or
            valid_photo_license(cover["license"], cover.get("license_url", ""))):
        return "record a supported open license and URL or an explicit grant of publication rights"
    if kind == "photo":
        if not valid_photo_license(cover["license"], cover["license_url"]):
            return "unapproved photo license or mismatched license URL"
        source = urlsplit(cover["source_url"])
        title = cover["commons_title"].replace("_", " ")
        source_title = unquote(source.path.removeprefix("/wiki/")).replace("_", " ")
        if (source.netloc != "commons.wikimedia.org" or not source.path.startswith("/wiki/")
                or not title.startswith("File:") or source_title != title):
            return "photo source must match the attributed Wikimedia Commons file"

    image_file = root / cover_src(slug, cover)
    signature = PNG_SIGNATURE if kind == AI_KIND else JPEG_SIGNATURE
    if not image_file.is_file() or image_file.stat().st_size < 8_000:
        return "missing or undersized local cover"
    with image_file.open("rb") as image:
        if image.read(len(signature)) != signature:
            return "local cover does not match its image format"
    if for_release:
        if image_file.stat().st_size > 4_000_000:
            return "cover exceeds 4 MB; optimize it for mobile"
        try:
            width, height = image_dimensions(image_file)
        except ValueError as error:
            return str(error)
        if width < 1200 or height < 630 or width <= height:
            return "use a horizontal cover at least 1200 × 630 pixels"
    return None


def cover_credit(cover):
    if cover.get("kind") == AI_KIND:
        return AI_CREDIT
    if cover.get("license"):
        return f'{cover["author"]} · {cover["license"]}'
    return cover["author"]


def cover_link(href, label, rel="noopener noreferrer"):
    return f'<a target="_blank" rel="{rel}" href="{escape(href)}">{escape(label)}</a>'


def cover_markup(entry, cover, *, dimensions=None):
    src = cover_src(entry["slug"], cover)
    size = f'width="{dimensions[0]}" height="{dimensions[1]}" ' if dimensions else ""
    kind = cover.get("kind", "photo")
    if kind == AI_KIND:
        caption = escape(AI_CREDIT) + "."
    else:
        author = cover_link(cover["source_url"], cover["author"]) if cover.get("source_url") else escape(cover["author"])
        caption = "Фото: " + author
        if cover.get("license"):
            license_name = cover["license"]
            caption += " · " + (cover_link(cover["license_url"], license_name, "license noopener noreferrer")
                                 if cover.get("license_url") else escape(license_name))
        caption += "."
        if cover.get("illustrative", kind == "photo"):
            caption += " Иллюстративное фото."
        if cover.get("changes"):
            caption += " " + escape(cover["changes"])
    return (
        '<!-- BUCHARESTUA_MEDIA -->'
        '<figure class="journal-cover">'
        '<img src="' + escape(src) + '" '
        + size + 'loading="eager" decoding="async" '
        'fetchpriority="high" alt="' + escape(cover_alt(cover)) + '">'
        '<figcaption>' + caption + '</figcaption></figure>'
    )


def decorate_html(html, entry, cover=None, *, dimensions=None):
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
        figure = cover_markup(entry, cover, dimensions=dimensions)
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
