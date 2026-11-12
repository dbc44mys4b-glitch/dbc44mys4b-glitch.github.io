"""Read and update the XML sitemap and its plain-text counterpart."""

from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

BASE = "https://dbc44mys4b-glitch.github.io/"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS = f"{{{NAMESPACE}}}"


def parse_sitemap(data):
    root = ET.fromstring(data)
    if root.tag != NS + "urlset":
        raise ValueError("Expected a sitemap urlset in the standard namespace")
    if (root.text or "").strip():
        raise ValueError("Unexpected text inside sitemap urlset")
    if not 1 <= len(root) <= 50_000:
        raise ValueError("Sitemap must have between 1 and 50,000 URL entries")

    urls = set()
    for entry in root:
        if entry.tag != NS + "url" or (entry.tail or "").strip():
            raise ValueError("Expected only URL entries and whitespace inside sitemap urlset")
        if (entry.text or "").strip() or any((child.tail or "").strip() for child in entry):
            raise ValueError("Unexpected text inside sitemap URL entry")
        locations = entry.findall(NS + "loc")
        if len(locations) != 1 or len(locations[0]):
            raise ValueError("Each sitemap URL entry must have one loc element")
        url = locations[0].text or ""
        parsed = urlsplit(url)
        if not url.startswith(BASE) or parsed.fragment or any(char.isspace() for char in url):
            raise ValueError(f"Invalid sitemap location: {url!r}")
        if url in urls:
            raise ValueError(f"Duplicate sitemap location: {url}")
        urls.add(url)
    return root


def sitemap_locations(root):
    return [entry.findtext(NS + "loc") for entry in root]


def text_sitemap(root):
    return "\n".join(sitemap_locations(root)) + "\n"


def update_sitemaps(path, root, pages):
    listed = set(sitemap_locations(root))
    added = False
    for url, date in pages.items():
        if url in listed:
            continue
        entry = ET.SubElement(root, NS + "url")
        ET.SubElement(entry, NS + "loc").text = url
        ET.SubElement(entry, NS + "lastmod").text = date
        entry.tail = "\n"
        added = True

    if added:
        ET.register_namespace("", NAMESPACE)
        xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        parse_sitemap(xml)
        path.write_bytes(xml + b"\n")

    plain_path = path.with_suffix(".txt")
    plain = text_sitemap(root)
    if not plain_path.is_file() or plain_path.read_text(encoding="utf-8") != plain:
        plain_path.write_text(plain, encoding="utf-8")
