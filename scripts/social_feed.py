#!/usr/bin/env python3
"""Update the RSS feed for an explicitly approved article."""

from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
import xml.etree.ElementTree as ET

from sitemap import BASE


def rss_sort_key(item):
    pub_date = item.findtext("pubDate")
    dt = parsedate_to_datetime(pub_date) if pub_date else datetime.min
    return dt.replace(tzinfo=dt.tzinfo or timezone.utc), item.findtext("link").removesuffix(".html")


def write_rss(feed_path, source, entry):
    items = {
        item.findtext("link"): item
        for item in ET.parse(source).findall("./channel/item")
    }
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    for tag, text in [
        ("title", "BucharestUA — городской журнал"),
        ("link", BASE),
        ("description", "Полезные и интересные истории о жизни, культуре и прогулках в Бухаресте"),
        ("language", "ru-RO"),
        ("generator", "BucharestUA"),
    ]:
        ET.SubElement(channel, tag).text = text
    item = ET.Element("item")
    url = BASE + entry["slug"] + ".html"
    ET.SubElement(item, "title").text = entry["title"]
    ET.SubElement(item, "link").text = url
    ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
    ET.SubElement(item, "description").text = entry.get("telegram_teaser") or entry["description"]
    dt = datetime.strptime(entry["publish_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    ET.SubElement(item, "pubDate").text = format_datetime(dt)
    ET.SubElement(item, "category").text = entry.get("category", "Городское медиа")
    items[url] = item
    latest_items = sorted(items.values(), key=rss_sort_key, reverse=True)[:40]
    channel.extend(latest_items)
    ET.indent(rss, space="  ")
    feed_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(rss, encoding="unicode") + "\n",
        encoding="utf-8"
    )
