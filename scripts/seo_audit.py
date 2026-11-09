#!/usr/bin/env python3
"""BucharestUA read-only SEO audit. No external dependencies or credential access."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen
import json
import posixpath
import sys
import xml.etree.ElementTree as ET

BASE = "https://dbc44mys4b-glitch.github.io/"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
OUT.mkdir(exist_ok=True)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1_count = 0
        self.description = None
        self.canonical = None
        self.links = []
        self.lang = None
        self.robots = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta":
            if a.get("name", "").lower() == "description":
                self.description = a.get("content")
            if a.get("name", "").lower() == "robots":
                self.robots = a.get("content")
        if tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonical = a.get("href")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def path_for_url(url):
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != urlparse(BASE).netloc:
        return None
    p = unquote(parsed.path)
    if p in ("", "/"):
        return "index.html"
    if p.endswith("/"):
        p += "index.html"
    return p.lstrip("/")


def check_web(url):
    req = Request(url, headers={"User-Agent": "BucharestUA-SEO-Monitor/1.0"})
    try:
        with urlopen(req, timeout=18) as response:
            return {"url": url, "http_status": response.status, "ok": 200 <= response.status < 400}
    except HTTPError as e:
        return {"url": url, "http_status": e.code, "ok": False}
    except (URLError, TimeoutError, OSError) as e:
        return {"url": url, "error": str(e), "ok": False}


def main():
    issues = []
    warnings = []
    pages = [
        p for p in sorted(ROOT.glob("*.html"))
        if not (
            p.name.startswith("google")
            and p.stat().st_size < 512
            and p.read_text(encoding="utf-8").lstrip().startswith("google-site-verification:")
        )
    ]
    info = {}
    titles = Counter()

    for page in pages:
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"{page.name}: HTML parser error: {e}")
            continue
        info[page.name] = {
            "title": parser.title.strip(),
            "description": parser.description,
            "canonical": parser.canonical,
            "h1_count": parser.h1_count,
            "language": parser.lang,
        }
        if not parser.title.strip():
            issues.append(f"{page.name}: missing title")
        else:
            titles[parser.title.strip()] += 1
        if not parser.description:
            warnings.append(f"{page.name}: missing meta description")
        if parser.h1_count != 1:
            warnings.append(f"{page.name}: expected one H1; found {parser.h1_count}")
        if not parser.canonical:
            warnings.append(f"{page.name}: missing canonical URL")
        if not parser.lang:
            warnings.append(f"{page.name}: missing HTML lang")
        if "noindex" in (parser.robots or "").lower():
            warnings.append(f"{page.name}: noindex directive")
        for href in parser.links:
            if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            parsed = urlparse(href)
            if parsed.scheme and parsed.scheme not in ("http", "https"):
                continue
            if parsed.netloc and parsed.netloc != urlparse(BASE).netloc:
                continue
            if not parsed.path:
                continue
            if parsed.netloc:
                target = path_for_url(href)
            else:
                target = posixpath.normpath(posixpath.join(page.parent.relative_to(ROOT).as_posix(), unquote(parsed.path)))
                if target == ".":
                    target = "index.html"
                if target.endswith("/"):
                    target += "index.html"
            if target and not (ROOT / target).is_file():
                issues.append(f"{page.name}: broken internal link {href}")

    for title, count in titles.items():
        if count > 1:
            warnings.append(f"Repeated page title ({count} pages): {title}")

    sitemap_urls = []
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        sitemap_urls = [n.text for n in tree.getroot().iter() if n.tag.endswith("loc") and n.text]
        for url in sitemap_urls:
            p = path_for_url(url)
            if p is None:
                warnings.append(f"External URL in sitemap: {url}")
            elif not (ROOT / p).is_file():
                issues.append(f"Sitemap points to missing page: {url}")
        in_sitemap = {path_for_url(u) for u in sitemap_urls}
        for page in pages:
            if page.name not in in_sitemap:
                warnings.append(f"{page.name}: absent from sitemap")
    except Exception as e:
        issues.append(f"Cannot parse sitemap.xml: {e}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "https://t.me/bucharest_info" not in home:
        issues.append("Main Telegram link missing from homepage")
    if '765918B6A3C148EF876365034C34DFEE' not in home:
        issues.append("Bing verification meta tag missing")
    if "sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        warnings.append("robots.txt does not advertise sitemap.xml")

    web_checks = [
        check_web(BASE),
        check_web(BASE + "sitemap.xml"),
        check_web(BASE + "russian-speaking-chat-bucharest.html"),
    ]
    for c in web_checks:
        if not c["ok"]:
            warnings.append(f"Public URL unavailable during check: {c['url']} ({c.get('http_status', c.get('error', 'unknown'))})")

    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "site": BASE,
        "html_pages": len(pages),
        "sitemap_urls": len(sitemap_urls),
        "issues": sorted(set(issues)),
        "warnings": sorted(set(warnings)),
        "public_http_checks": web_checks,
        "page_metadata": info,
    }
    (OUT / "seo-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# BucharestUA daily SEO audit",
        "",
        f"- UTC: {result['checked_at_utc']}",
        f"- HTML pages: **{len(pages)}**",
        f"- Sitemap URLs: **{len(sitemap_urls)}**",
        f"- Critical issues: **{len(result['issues'])}**",
        f"- Warnings: **{len(result['warnings'])}**",
        "",
        "## Public HTTP checks",
    ]
    for c in web_checks:
        lines.append(f"- {'OK' if c['ok'] else 'CHECK'}: {c['url']} — {c.get('http_status', c.get('error', '?'))}")
    lines += ["", "## Critical issues"]
    lines += [f"- {x}" for x in result["issues"]] or ["- None"]
    lines += ["", "## Warnings (first 60)"]
    lines += [f"- {x}" for x in result["warnings"][:60]] or ["- None"]
    (OUT / "seo-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if result["issues"]:
        print("SEO validation failed; see audit report.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
