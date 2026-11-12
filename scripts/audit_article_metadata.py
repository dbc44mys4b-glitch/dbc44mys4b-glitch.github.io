#!/usr/bin/env python3
"""BucharestUA read-only editorial HTML audit. Never grants publication approval.

Usage: python3 scripts/audit_article_metadata.py massage-bucharest.html
       python3 scripts/audit_article_metadata.py --json massage-bucharest.html
Exit 0 only if all supplied files pass the checked metadata conditions.
This is a TECHNICAL preflight, not independent factual/editorial QA.
"""
import argparse
import json
import pathlib
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

BASE = "https://dbc44mys4b-glitch.github.io/"

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.links = []
        self.images = []
        self.scripts = []
        self.in_ld = False
        self.ld_text = ""
        self.title_on = False
        self.title = ""
        self.h1 = 0
        self.telegram = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append(a)
        elif tag == "a":
            self.telegram |= a.get("href", "").startswith("https://t.me/bucharest_info")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self.in_ld = True
            self.ld_text = ""
        elif tag == "title":
            self.title_on = True
        elif tag == "h1":
            self.h1 += 1

    def handle_data(self, data):
        if self.in_ld:
            self.ld_text += data
        if self.title_on:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "script" and self.in_ld:
            self.in_ld = False
            self.scripts.append(self.ld_text)
        elif tag == "title":
            self.title_on = False

def audit(path):
    issues = []
    p = Page()
    try:
        p.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as e:
        return [f"read error: {e}"]
    expected = BASE + path.name
    canonical = [x.get("href", "") for x in p.links if x.get("rel", "").lower() == "canonical"]
    if canonical != [expected]:
        issues.append(f"canonical mismatch: {canonical!r}, expected {expected}")
    if len(p.title.strip()) < 20:
        issues.append("missing/short title")
    if p.h1 != 1:
        issues.append(f"expected exactly one h1, got {p.h1}")
    for field in ("description", "og:title", "og:description", "og:url", "og:image"):
        if not p.meta.get(field, "").strip():
            issues.append(f"missing {field}")
    if p.meta.get("og:url") != expected:
        issues.append("og:url mismatch")
    if p.meta.get("description") != p.meta.get("og:description"):
        issues.append("description / og:description mismatch")
    if not p.telegram:
        issues.append("missing community Telegram CTA")
    for i, img in enumerate(p.images, 1):
        if not img.get("alt", "").strip():
            issues.append(f"img #{i}: missing alt")
    if not p.scripts:
        issues.append("missing JSON-LD")
    for i, raw in enumerate(p.scripts, 1):
        try:
            ld = json.loads(raw)
        except json.JSONDecodeError as e:
            issues.append(f"JSON-LD #{i}: invalid JSON: {e}")
            continue
        if isinstance(ld, dict) and ld.get("@type") == "Article":
            if ld.get("mainEntityOfPage") != expected:
                issues.append("Article JSON-LD mainEntityOfPage mismatch")
            if ld.get("description") != p.meta.get("description"):
                issues.append("Article JSON-LD description mismatch")
    if p.meta.get("og:image") and not urlparse(p.meta["og:image"]).scheme == "https":
        issues.append("og:image must be HTTPS")
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("files", nargs="+", type=pathlib.Path)
    args = parser.parse_args()
    results = {str(f): audit(f) for f in args.files}
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for file, errors in results.items():
            print(f"{file}: {'PASS (metadata only)' if not errors else 'FAIL'}")
            for error in errors:
                print(f"  - {error}")
    return 1 if any(results.values()) else 0

if __name__ == "__main__":
    sys.exit(main())
