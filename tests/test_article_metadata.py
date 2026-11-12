#!/usr/bin/env python3
"""Regression tests for the read-only article metadata preflight.

Run: python3 -m unittest discover -s tests -p 'test_article_metadata.py'
These tests do not issue independent editorial approvals.
"""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("article_metadata", ROOT / "scripts" / "audit_article_metadata.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def html(name="sample.html", *, desc="Practical guide for Bucharest residents.", image_alt="Cover", telegram=True, jsonld=True):
    url = MODULE.BASE + name
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
          '"mainEntityOfPage":"' + url + '","description":"' + desc + '"}</script>') if jsonld else ""
    cta = '<a href="https://t.me/bucharest_info">Community</a>' if telegram else ""
    return (f'<html><head><title>Useful Bucharest local guide for newcomers</title>'
            f'<meta name="description" content="{desc}">'
            f'<meta property="og:title" content="Useful Bucharest local guide">'
            f'<meta property="og:description" content="{desc}">'
            f'<meta property="og:url" content="{url}">'
            f'<meta property="og:image" content="{MODULE.BASE}og-image.png">'
            f'<link rel="canonical" href="{url}">{ld}</head><body>'
            f'<h1>Useful Bucharest guide</h1><img src="cover.png" alt="{image_alt}">{cta}</body></html>')

class MetadataAuditTests(unittest.TestCase):
    def check(self, body, filename="sample.html"):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / filename
            path.write_text(body, encoding="utf-8")
            return MODULE.audit(path)

    def test_valid_page_passes_technical_preflight(self):
        self.assertEqual([], self.check(html()))

    def test_missing_telegram_cta_fails(self):
        self.assertTrue(any("Telegram CTA" in x for x in self.check(html(telegram=False))))

    def test_missing_alt_fails(self):
        self.assertTrue(any("missing alt" in x for x in self.check(html(image_alt=""))))

    def test_missing_jsonld_fails(self):
        self.assertTrue(any("missing JSON-LD" in x for x in self.check(html(jsonld=False))))

    def test_description_mismatch_fails(self):
        body = html().replace('property="og:description" content="Practical guide', 'property="og:description" content="Different guide')
        self.assertTrue(any("description / og:description mismatch" in x for x in self.check(body)))

    def test_wrong_canonical_fails(self):
        body = html().replace('rel="canonical" href="https://dbc44mys4b-glitch.github.io/sample.html"', 'rel="canonical" href="https://example.org/wrong"')
        self.assertTrue(any("canonical mismatch" in x for x in self.check(body)))

    def test_malformed_jsonld_fails(self):
        body = html().replace('"@context":"https://schema.org"', '"@context":INVALID')
        self.assertTrue(any("invalid JSON" in x for x in self.check(body)))

if __name__ == "__main__":
    unittest.main()
