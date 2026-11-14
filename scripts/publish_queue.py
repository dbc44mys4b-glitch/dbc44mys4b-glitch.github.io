#!/usr/bin/env python3
"""Prepare and verify a single manually approved BucharestUA release."""

import argparse
from datetime import date, datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import shutil
import ssl
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from audit_article_metadata import audit
from editorial_article import build_page
from editorial_home import write_home
from editorial_media import cover_alt, cover_credit, cover_problem, cover_src, decorate_html, image_dimensions
from prepublish_check import HTMLInspector, check_article
from sitemap import BASE, NS, parse_sitemap, update_sitemaps
from social_feed import write_rss

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "content-queue/articles.json"
RELEASES = Path("editorial/releases")
MANIFEST = Path("media/assigned-images.json")
START = "<!-- BUCHARESTUA_EDITORIAL_START -->"
END = "<!-- BUCHARESTUA_EDITORIAL_END -->"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+")
STYLES = ("styles.css", "favicon.svg")


def text(x):
    return escape(str(x), quote=True)


def required_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: expected nonempty text")
    return value


def iso_date(value, field):
    try:
        parsed = date.fromisoformat(required_text(value, field))
    except ValueError as error:
        raise ValueError(f"{field}: expected YYYY-MM-DD") from error
    if parsed.isoformat() != value:
        raise ValueError(f"{field}: expected YYYY-MM-DD")
    return parsed


def prepare(draft, staging, today, *, check_target=True):
    entry = json.loads(draft.read_text(encoding="utf-8"))
    if not isinstance(entry, dict):
        raise ValueError("Draft must be a JSON object")
    for field in ("slug", "title", "description", "intro", "category", "image"):
        required_text(entry.get(field), field)
    slug = entry["slug"]
    if not SLUG.fullmatch(slug) or not 5 <= len(slug) <= 90:
        raise ValueError("Invalid article slug")
    page = f"{slug}.html"
    site_path = ROOT / page
    old_page = site_path.read_bytes() if site_path.is_file() else None
    published = iso_date(entry.get("publish_date"), "publish_date")
    checked = iso_date(entry.get("fact_checked_on"), "fact_checked_on")
    modified = iso_date(entry.get("date_modified", entry["publish_date"]), "date_modified")
    if not checked <= modified or not published <= modified or checked > today:
        raise ValueError("Publication, revision or fact-check dates are inconsistent")
    if check_target and old_page is not None:
        if "date_modified" not in entry:
            raise ValueError("Existing page: review as a revision and specify date_modified")
        catalog = (ROOT / "articles.html").read_text(encoding="utf-8")
        if f'href="{page}"' not in catalog:
            raise ValueError("Existing URL is outside the article catalog")
        original = re.search(rb'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', old_page)
        if original and original[1].decode() != entry["publish_date"]:
            raise ValueError("Preserve the existing publication date for revisions")
    elif check_target and "date_modified" in entry:
        raise ValueError("New articles use publish_date only")

    kind = entry.get("type", "guide")
    if kind not in ("guide", "news"):
        raise ValueError("type: use guide or news")
    if kind == "news":
        iso_date(entry.get("event_date"), "event_date")
        required_text(entry.get("event_context"), "event_context")
    minimum = 1 if kind == "news" else 3
    sections = entry.get("sections")
    if not isinstance(sections, list) or len(sections) < minimum:
        raise ValueError(f"At least {minimum} substantive section(s) required for {kind}")
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("Each section must be a JSON object")
        required_text(section.get("heading"), "section heading")
        paragraphs = section.get("paragraphs", [])
        bullets = section.get("bullets", [])
        if not isinstance(paragraphs, list) or not isinstance(bullets, list) or not (paragraphs or bullets):
            raise ValueError("Each section needs paragraphs or bullets")
        for item in paragraphs + bullets:
            required_text(item, "paragraph or bullet")

    sources = entry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("At least one verified primary source is required")
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be a JSON object")
        required_text(source.get("label"), "source label")
        link = required_text(source.get("url"), "source URL")
        parsed = urlsplit(link)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or any(c.isspace() for c in link):
            raise ValueError("Source URL must be a valid HTTPS address")

    for term in entry.get("romanian_terms", []):
        required_text(term, "Romanian term")
    for item in entry.get("related", []):
        href = required_text(item.get("href"), "related link")
        required_text(item.get("text"), "related label")
        if not re.fullmatch(r"[a-z0-9-]+\.html", href) or not (ROOT / href).is_file():
            raise ValueError(f"Related link must point to an existing site page: {href}")

    cover = entry.get("cover")
    if not isinstance(cover, dict):
        raise ValueError("A rights-cleared cover is required")
    image = Path(entry["image"])
    if image.is_absolute():
        raise ValueError("Use an image path relative to the draft")
    source_image = (draft.parent / image).resolve()
    if not source_image.is_relative_to(draft.parent):
        raise ValueError("Keep the image beside the draft or in a subdirectory")
    cover_path = Path(cover_src(slug, cover))
    staged_image = staging / cover_path
    staged_image.parent.mkdir(parents=True)
    shutil.copyfile(source_image, staged_image)
    problem = cover_problem(staging, slug, cover, for_release=True)
    if problem:
        raise ValueError(problem)

    dimensions = image_dimensions(staged_image)
    html = decorate_html(build_page(entry, cover), entry, cover, dimensions=dimensions)
    parser = HTMLInspector()
    parser.feed(html)
    (staging / page).write_text(html, encoding="utf-8")
    errors = check_article(parser, slug, cover, cover_root=staging) + audit(staging / page)
    if errors:
        raise ValueError("\n".join(errors))

    fingerprint = sha256(json.dumps({
        "entry": entry,
        "html_sha256": sha256(html.encode("utf-8")).hexdigest(),
        "image_sha256": sha256(staged_image.read_bytes()).hexdigest(),
        "assets_sha256": {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in STYLES},
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    replaced = sha256(old_page).hexdigest() if old_page is not None else None
    return entry, cover, fingerprint, replaced


def write_catalog(output, entry, cover):
    path = ROOT / "articles.html"
    before, cards = path.read_text(encoding="utf-8").split(START, 1)
    cards, after = cards.split(END, 1)
    grid = '<div class="m-story-grid">'
    if not cards.startswith(grid):
        raise ValueError("Article card grid missing")
    slug = entry["slug"]
    credit = cover_credit(cover)
    category = "Новости · " + entry["category"] if entry.get("type") == "news" else entry["category"]
    card = (
        f'<a class="m-card" href="{slug}.html"><div class="m-card-visual m-visual-0">'
        f'<img src="{cover_src(slug, cover)}" alt="{text(cover_alt(cover))}" loading="lazy">'
        f'<span class="m-image-credit">{text(credit)}</span></div>'
        f'<div class="m-card-body"><span class="m-meta">{text(category)} · '
        f'{entry["publish_date"]}</span><h3>{text(entry["title"])}</h3>'
        f'<p>{text(entry["description"])}</p><span class="m-read">Читать историю ↗</span></div></a>'
    )
    existing = re.compile(r'<a class="m-card\b[^"]*" href="' + re.escape(slug) + r'\.html">.*?</a>', re.S)
    cards, count = existing.subn(lambda _: card, cards)
    if count > 1:
        raise ValueError("Duplicate cards for the selected article")
    if count == 0:
        cards = grid + card + cards[len(grid):]
        total = len(re.findall(r'<a class="m-card\b', cards))
        before = re.sub(r"(?<=<h2>Все публикации</h2><span>)\d+", str(total), before, count=1)
    (output / path.name).write_text(before + START + cards + END + after, encoding="utf-8")
    return card


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_release(staging, entry, cover, version, approval_ref, today):
    slug = entry["slug"]
    card = write_catalog(staging, entry, cover)
    write_home(ROOT, staging, slug, card)
    url = BASE + slug + ".html"
    pages = parse_sitemap((ROOT / "sitemap.xml").read_bytes())
    lastmod = entry.get("date_modified", entry["publish_date"])
    for item in pages:
        if item.findtext(NS + "loc") == url:
            tag = item.find(NS + "lastmod")
            if tag is None:
                tag = ET.SubElement(item, NS + "lastmod")
            tag.text = lastmod
    # Starting from the validated source tree, always serialize both sitemap formats.
    ET.register_namespace("", NS[1:-1])
    sitemap = staging / "sitemap.xml"
    sitemap.write_bytes(ET.tostring(pages, encoding="UTF-8", xml_declaration=True) + b"\n")
    update_sitemaps(sitemap, pages, {url: lastmod})
    write_rss(staging / "feed.xml", ROOT / "feed.xml", entry)
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    manifest[slug] = {key: cover[key] for key in (
        "kind", "author", "alt", "license", "license_url", "source_url", "commons_title", "illustrative", "changes"
    ) if key in cover}
    if cover.get("permission"):
        manifest[slug]["permission_recorded"] = True
    write_json(staging / MANIFEST, manifest)
    write_json(staging / RELEASES / (slug + ".json"), {
        "slug": slug,
        "version": version,
        "approval_ref_sha256": sha256(approval_ref.encode("utf-8")).hexdigest(),
        "type": entry.get("type", "guide"),
        "fact_checked_on": entry["fact_checked_on"],
        "released_on": today.isoformat(),
        "page_sha256": sha256((staging / (slug + ".html")).read_bytes()).hexdigest(),
        "image_sha256": sha256((staging / cover_src(slug, cover)).read_bytes()).hexdigest(),
        "image_path": cover_src(slug, cover),
    })


def private_path(path):
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT):
        raise ValueError("Keep drafts, previews, decisions and release bundles outside the public checkout")
    return resolved


def review_record(entry, cover, version, replaced):
    return {"slug": entry["slug"], "title": entry["title"], "type": entry.get("type", "guide"),
            "version": version, "replaces_sha256": replaced, "fact_checked_on": entry["fact_checked_on"],
            "sources": entry["sources"], "cover": cover}


def status(workspace, today):
    deployed = {}
    for path in sorted((ROOT / RELEASES).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        deployed[record["slug"]] = record["version"]
        print(f'{record["released_on"]} {record["slug"]} {record["version"][:12]} — есть запись выпуска; HTTP отдельно')
    if workspace is not None:
        if not workspace.is_dir():
            raise ValueError("Approval workspace must be an existing directory")
        print("Частная очередь согласования")
        drafts = sorted(workspace.glob("*/draft.json"))
        if not drafts:
            print("Очередь пуста.")
        for draft in drafts:
            try:
                with TemporaryDirectory() as temp:
                    entry, cover, version, replaced = prepare(private_path(draft), Path(temp), today, check_target=False)
                slug = entry["slug"]
                if slug != draft.parent.name:
                    raise ValueError("Workspace folder must match article slug")
                decision = "В работе"
                if deployed.get(slug) == version:
                    print(f"{slug} {version[:12]} — В main · проверьте публичный URL")
                    continue
                current = review_record(entry, cover, version, replaced)
                for review_path in sorted(draft.parent.glob("preview-*/review.json")):
                    review = json.loads(private_path(review_path).read_text(encoding="utf-8"))
                    if review["slug"] != slug:
                        raise ValueError("Review slug does not match draft")
                    if review == current:
                        approval = review_path.with_name("approval.json")
                        if approval.is_file():
                            record = json.loads(private_path(approval).read_text(encoding="utf-8"))
                            if record["version"] == version and record.get("approval_ref"):
                                decision = "Одобрена · пакет выпуска готов"
                                break
                        decision = "На согласовании · отправьте предпросмотр или дождитесь ответа"
                    elif decision == "В работе":
                        decision = "Правки · нужен новый предпросмотр"
                print(f"{slug} {version[:12]} — {decision}")
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                print(f"{draft.parent.name} — В работе · {error}")
    archive = json.loads(QUEUE.read_text(encoding="utf-8"))
    with_page = sum((ROOT / (item["slug"] + ".html")).is_file() for item in archive)
    print(f"Историческая очередь: {len(archive)} тем, {len(archive) - with_page} без страницы в репозитории.")


def verify(slug, context):
    if not SLUG.fullmatch(slug):
        raise ValueError("Invalid article slug")
    record = json.loads((ROOT / RELEASES / (slug + ".json")).read_text(encoding="utf-8"))
    for path, label, accept in [
        (slug + ".html", "page_sha256", "text/html"),
        (record["image_path"], "image_sha256", "image/"),
    ]:
        url = BASE + path
        with urlopen(url, timeout=20, context=context) as response:
            if response.status != 200 or response.url != url or not response.headers.get_content_type().startswith(accept):
                raise ValueError(f"Unexpected public response: {url}")
            if sha256(response.read()).hexdigest() != record[label]:
                raise ValueError(f"Public content differs from the approved release: {url}")
        print(f"HTTP 200, approved bytes: {url}")
    with urlopen(BASE + "sitemap.xml", timeout=20, context=context) as response:
        sitemap = parse_sitemap(response.read())
        if response.status != 200 or BASE + slug + ".html" not in [item.findtext(NS + "loc") for item in sitemap]:
            raise ValueError("Published URL missing from live sitemap")
    print("URL present in public sitemap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status").add_argument("--workspace", type=Path)
    verification = commands.add_parser("verify")
    verification.add_argument("slug")
    verification.add_argument("--ca-file", type=Path, help="Optional path to a trusted CA bundle")
    for command in ("preview", "publish"):
        action = commands.add_parser(command)
        action.add_argument("draft", type=Path)
        action.add_argument("--output", type=Path, required=True)
        if command == "publish":
            action.add_argument("--preview", type=Path, required=True)
            action.add_argument("--approved", required=True)
            action.add_argument("--approval-ref", required=True)
    args = parser.parse_args()
    try:
        today = datetime.now(ZoneInfo("Europe/Bucharest")).date()
        if args.command == "status":
            status(private_path(args.workspace) if args.workspace else None, today)
            return
        if args.command == "verify":
            ca_file = args.ca_file
            system_bundle = Path("/etc/ssl/cert.pem")
            if ca_file is None and not ssl.get_default_verify_paths().cafile and system_bundle.is_file():
                ca_file = system_bundle
            verify(args.slug, ssl.create_default_context(cafile=ca_file))
            return
        output = private_path(args.output)
        draft = private_path(args.draft)
        if output.exists():
            raise ValueError("Output must be a new directory")
        with TemporaryDirectory(dir=output.parent) as temp:
            staging = Path(temp) / "bundle"
            entry, cover, version, replaced = prepare(draft, staging, today)
            review = review_record(entry, cover, version, replaced)
            if args.command == "publish":
                approval_ref = required_text(args.approval_ref, "approval reference").strip()
                preview = private_path(args.preview)
                saved_review = json.loads(private_path(preview / "review.json").read_text(encoding="utf-8"))
                if args.approved != version or saved_review != review:
                    raise ValueError("Prepared article differs from the preview approved by the owner")
                for name in (entry["slug"] + ".html", cover_src(entry["slug"], cover), *STYLES):
                    expected = ROOT / name if name in STYLES else staging / name
                    if (preview / name).read_bytes() != expected.read_bytes():
                        raise ValueError(f"Approved preview differs from the prepared release: {name}")
                effective_date = entry.get("date_modified", entry["publish_date"])
                if effective_date > today.isoformat():
                    raise ValueError("The approved article date is still in the future in Bucharest")
                write_release(staging, entry, cover, version, approval_ref, today)
            else:
                for name in STYLES:
                    shutil.copyfile(ROOT / name, staging / name)
                write_json(staging / "review.json", review)
            staging.rename(output)
        if args.command == "publish":
            with TemporaryDirectory(dir=preview) as temp:
                approval = Path(temp) / "approval.json"
                write_json(approval, {"version": version, "approval_ref": approval_ref})
                approval.replace(preview / "approval.json")
        print(f'{entry["slug"]} {version}')
        print(output)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ET.ParseError) as error:
        parser.exit(1, f"Blocked: {error}\n")


if __name__ == "__main__":
    main()
