#!/usr/bin/env python3
"""BucharestUA read-only SEO audit. No external dependencies or credential access."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import Request, urlopen
from sitemap import BASE, parse_sitemap, sitemap_locations, text_sitemap
import json
import sys
import xml.etree.ElementTree as ET

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


def diagnose_public_sitemap():
    """Check the actual deployed XML, including a Googlebot-like user agent.

    This is not a verified Google crawler and cannot replace the Google
    Search Console live test.
    """
    url = BASE + "sitemap.xml"
    req = Request(url, headers={
        "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "Accept": "application/xml,text/xml,*/*",
    })
    try:
        with urlopen(req, timeout=18) as response:
            data = response.read(52_428_801)
            result = {
                "url": url, "http_status": response.status,
                "content_type": response.headers.get("Content-Type", ""), "bytes": len(data),
                "final_url": response.geturl(), "remote_xml_valid": False, "ok": False,
                "note": "Googlebot-like request; not proof of a real Googlebot crawl."
            }
            if len(data) > 52_428_800:
                return {**result, "error": "Deployed sitemap exceeds 50 MB"}
            try:
                root = parse_sitemap(data)
            except (ValueError, ET.ParseError) as error:
                return {**result, "error": str(error)}
            result.update(remote_xml_valid=True, remote_urls=len(root))
            if response.status != 200 or response.geturl() != url:
                return {**result, "error": "Sitemap does not return a direct HTTP 200"}
            if response.headers.get_content_type() not in {"application/xml", "text/xml"}:
                return {**result, "error": "Sitemap is not served as XML"}
            return {**result, "ok": True}
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return {"url": url, "ok": False, "error": str(error)[:350]}


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
            target = path_for_url(urljoin(BASE + page.name, href))
            if target and not (ROOT / target).is_file():
                issues.append(f"{page.name}: broken internal link {href}")

    for title, count in titles.items():
        if count > 1:
            warnings.append(f"Repeated page title ({count} pages): {title}")

    sitemap_urls = []
    try:
        root = parse_sitemap((ROOT / "sitemap.xml").read_bytes())
        sitemap_urls = sitemap_locations(root)
        for url in sitemap_urls:
            p = path_for_url(url)
            if not (ROOT / p).is_file():
                issues.append(f"Sitemap points to missing page: {url}")
            elif info.get(p, {}).get("canonical") != url:
                issues.append(f"Sitemap URL differs from page canonical: {url}")
        in_sitemap = {path_for_url(u) for u in sitemap_urls}
        for page in pages:
            if page.name not in in_sitemap:
                warnings.append(f"{page.name}: absent from sitemap")
        plain_path = ROOT / "sitemap.txt"
        if not plain_path.is_file() or plain_path.read_text(encoding="utf-8") != text_sitemap(root):
            issues.append("sitemap.txt does not match sitemap.xml")
    except (OSError, ValueError, ET.ParseError) as e:
        issues.append(f"Cannot parse sitemap.xml: {e}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "https://t.me/bucharest_info" not in home:
        issues.append("Main Telegram link missing from homepage")
    if '765918B6A3C148EF876365034C34DFEE' not in home:
        issues.append("Bing verification meta tag missing")
    robots_lines = (ROOT / "robots.txt").read_text(encoding="utf-8").splitlines()
    if not any(line.partition(":")[0].strip().lower() == "sitemap" and
               line.partition(":")[2].strip() == BASE + "sitemap.xml" for line in robots_lines):
        warnings.append("robots.txt does not advertise sitemap.xml")

    urls_to_check = [
        BASE,
        BASE + "sitemap.xml",
        BASE + "robots.txt",
        BASE + "russian-speaking-chat-bucharest.html",
        BASE + "city-needs.html",
        BASE + "explore-bucharest.html",
        BASE + "community.html",
        BASE + "assets/covers/community.jpg",
    ]
    queue_path = ROOT / "content-queue" / "articles.json"
    if queue_path.is_file():
        try:
            entries = json.loads(queue_path.read_text(encoding="utf-8"))
            slugs = [item["slug"] for item in entries]
            for slug, count in Counter(slugs).items():
                if count > 1:
                    issues.append(f"Duplicate slug in editorial queue: {slug}")
            for title, count in Counter(item["title"] for item in entries).items():
                if count > 1:
                    issues.append(f"Duplicate headline in editorial queue: {title}")
            for date, count in Counter(item["publish_date"] for item in entries).items():
                if count < 2 or count > 3:
                    warnings.append(f"Editorial calendar has {count} entries on {date}, expected 2–3")
            for item in entries:
                slug = item["slug"]
                sections = item.get("sections", [])
                if not sections or len(sections) < 3:
                    warnings.append(f"{slug}: fewer than 3 content sections")
                if len(item.get("intro", "")) < 100:
                    warnings.append(f"{slug}: editorial introduction too short")
                if len(item.get("description", "")) > 170:
                    warnings.append(f"{slug}: meta description longer than 170 characters")
                if item["publish_date"] >= "2026-12-09" and not item.get("sources"):
                    warnings.append(f"{slug}: no linked research source")
                for source in item.get("sources", []):
                    if not source.get("url", "").startswith("https://"):
                        issues.append(f"{slug}: non-HTTPS source URL")
            # Keep HTTP monitoring bounded as the library grows: core URLs
            # and the 12 most recently published entries, not every article.
            live_entries = [
                item for item in entries
                if (ROOT / (item["slug"] + ".html")).is_file()
            ]
            latest = sorted(live_entries, key=lambda item: (item["publish_date"], item["slug"]), reverse=True)[:12]
            for item in latest:
                urls_to_check.append(BASE + item["slug"] + ".html")
        except (ValueError, KeyError, TypeError) as e:
            issues.append(f"Could not validate scheduled editorial queue: {e}")
    web_checks = [check_web(url) for url in dict.fromkeys(urls_to_check)]
    for c in web_checks:
        if not c["ok"]:
            warnings.append(f"Public URL unavailable during check: {c['url']} ({c.get('http_status', c.get('error', 'unknown'))})")

    # Google Search Console may report a fetch failure even when the local
    # XML is syntactically valid. Test deployed bytes and content type separately.
    public_sitemap_diagnostic = diagnose_public_sitemap()
    if not public_sitemap_diagnostic.get("ok"):
        warnings.append("Deployed sitemap failed independent XML/Googlebot-like check: " +
                        str(public_sitemap_diagnostic.get("error", "Unexpected response")))

    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "site": BASE,
        "html_pages": len(pages),
        "sitemap_urls": len(sitemap_urls),
        "issues": sorted(set(issues)),
        "warnings": sorted(set(warnings)),
        "public_http_checks": web_checks,
        "public_sitemap_diagnostic": public_sitemap_diagnostic,
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
