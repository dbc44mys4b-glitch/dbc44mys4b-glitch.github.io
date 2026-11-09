#!/usr/bin/env python3
"""Prepare an RSS feed and honest, ready-to-post Telegram copy for the city journal.

No message is sent; publication to Telegram requires the owner's separate
bot/admin connection and consent.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "content-queue/articles.json"
BASE = "https://dbc44mys4b-glitch.github.io/"
TG = "https://t.me/bucharest_info"
OUT = ROOT / "social"
OUT.mkdir(exist_ok=True)


def live_articles():
    entries = json.loads(QUEUE.read_text(encoding="utf-8"))
    return sorted(
        [e for e in entries if (ROOT / (e["slug"] + ".html")).is_file()],
        key=lambda e: (e["publish_date"], e["slug"]), reverse=True
    )


def build_text(entry):
    summary = entry.get("telegram_teaser") or entry.get("description") or entry["intro"]
    summary = " ".join(summary.split()).strip()
    if len(summary) > 280:
        summary = summary[:277].rsplit(" ", 1)[0] + "…"
    url = BASE + entry["slug"] + ".html"
    title = entry["title"]
    return (
        "🗞 " + title + "\n\n" +
        summary + "\n\n" +
        "🔎 Полная статья: " + url + "\n\n" +
        "💬 А что вы думаете? Обсудим в BucharestUA: " + TG
    )


def create_rss(articles):
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for tag, text in [
        ("title", "BucharestUA — городской журнал"),
        ("link", BASE),
        ("description", "Полезные и интересные истории о жизни, культуре и прогулках в Бухаресте"),
        ("language", "ru-RO"),
        ("generator", "BucharestUA original editorial queue"),
    ]:
        ET.SubElement(channel, tag).text = text
    for entry in articles[:40]:
        item = ET.SubElement(channel, "item")
        url = BASE + entry["slug"] + ".html"
        ET.SubElement(item, "title").text = entry["title"]
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
        ET.SubElement(item, "description").text = entry.get("telegram_teaser") or entry["description"]
        dt = datetime.strptime(entry["publish_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_datetime(dt)
        ET.SubElement(item, "category").text = entry.get("category", "Городское медиа")
    ET.indent(rss, space="  ")
    (ROOT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(rss, encoding="unicode") + "\n",
        encoding="utf-8"
    )


def main():
    articles = live_articles()
    create_rss(articles)
    recent = articles[:14]
    data = [{
        "slug": e["slug"],
        "title": e["title"],
        "publish_date": e["publish_date"],
        "url": BASE + e["slug"] + ".html",
        "telegram_post": build_text(e),
        "has_approved_photo": (ROOT / "assets/covers" / (e["slug"] + ".jpg")).is_file()
    } for e in recent]
    (OUT / "telegram-posts.json").write_text(
        json.dumps({"site": BASE, "telegram": TG, "posts": data}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    lines = [
        "# BucharestUA — Telegram posts ready to copy",
        "",
        "These are editorial drafts, **not messages posted to the chat**.",
        "Review current facts, then publish no more often than suits the group.",
        "",
    ]
    for i, item in enumerate(data, 1):
        lines += ["## " + str(i) + ". " + item["title"], "", item["telegram_post"], "", "---", ""]
    (OUT / "telegram-drafts.md").write_text("\n".join(lines), encoding="utf-8")
    print("Prepared Telegram drafts:", len(data), "RSS items:", min(len(articles), 40))


if __name__ == "__main__":
    main()
