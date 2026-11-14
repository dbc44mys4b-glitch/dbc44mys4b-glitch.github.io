import json
from pathlib import Path
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import zlib

ROOT = Path(__file__).resolve().parents[1]
SLUG = "unpublished-fixture-article"


def png(pixel):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 100, 100, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress((b"\0" + bytes(range(pixel, pixel + 100))) * 100, level=0))
            + chunk(b"IEND", b""))


class ManualReleaseTests(unittest.TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.work = Path(workspace.name)
        self.image = self.work / "cover.png"
        self.image.write_bytes(png(0))
        today = datetime.now(ZoneInfo("Europe/Bucharest")).date().isoformat()
        self.entry = {
            "slug": SLUG, "title": "Local guide example", "description": "A local guide example.",
            "intro": "Introduction to a local guide.", "category": "City", "publish_date": today,
            "fact_checked_on": today, "image": self.image.name,
            "sections": [{"heading": heading, "paragraphs": ["Practical local detail."]}
                         for heading in ("Where", "When", "What to bring")],
            "sources": [{"label": "City Hall", "url": "https://www.pmb.ro/"}],
            "cover": {"kind": "ai_illustration", "author": "BucharestUA", "alt": "City park illustration"},
        }
        self.draft = self.work / "draft.json"
        self.save_draft()

    def save_draft(self):
        self.draft.write_text(json.dumps(self.entry), encoding="utf-8")

    def run_cli(self, mode, directory=None, *flags):
        command = [sys.executable, str(ROOT / "scripts/publish_queue.py"), mode]
        if directory:
            command += [str(self.draft), "--output", str(self.work / directory), *flags]
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    def preview_version(self):
        preview = self.run_cli("preview", "preview")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        return preview.stdout.splitlines()[0].split()[1]

    def publish(self, version, output="release"):
        return self.run_cli("publish", output, "--approved", version, "--approval-ref", "test-confirmation")

    def test_approved_bundle_contains_exact_preview_and_site_indexes(self):
        version = self.preview_version()
        release = self.publish(version)
        self.assertEqual(release.returncode, 0, release.stderr)
        preview_dir, release_dir = self.work / "preview", self.work / "release"
        page = SLUG + ".html"
        self.assertEqual((release_dir / page).read_bytes(), (preview_dir / page).read_bytes())
        for file in ("articles.html", "sitemap.xml", "sitemap.txt", "feed.xml"):
            self.assertIn(page, (release_dir / file).read_text(encoding="utf-8"))
        record = json.loads((release_dir / "editorial/releases" / (SLUG + ".json")).read_text())
        self.assertEqual(record["version"], version)
        self.assertEqual(record["approval_ref"], "test-confirmation")
        self.assertTrue((release_dir / record["image_path"]).is_file())
        self.assertFalse((ROOT / page).exists())

    def test_stale_approval_rejected_for_changed_text_and_image(self):
        version = self.preview_version()
        self.entry["intro"] = "New article text."
        self.save_draft()
        self.assertNotEqual(self.publish(version, "edited").returncode, 0)
        self.assertFalse((self.work / "edited").exists())
        self.entry["intro"] = "Introduction to a local guide."
        self.save_draft()
        self.image.write_bytes(png(1))
        self.assertNotEqual(self.publish(version, "replaced").returncode, 0)
        self.assertFalse((self.work / "replaced").exists())

    def test_legacy_default_and_drafts_without_sources_or_rights_are_blocked(self):
        self.assertNotEqual(self.run_cli("").returncode, 0)
        sources = self.entry.pop("sources")
        self.save_draft()
        self.assertNotEqual(self.run_cli("preview", "no-sources").returncode, 0)
        self.entry["sources"] = sources
        self.entry["cover"]["author"] = "Unknown"
        self.save_draft()
        self.assertNotEqual(self.run_cli("preview", "no-rights").returncode, 0)


if __name__ == "__main__":
    unittest.main()
