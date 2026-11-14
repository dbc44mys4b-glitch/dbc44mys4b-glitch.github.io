"""Refresh the homepage's latest-publication cards from an approved release."""

import re


START = "<!-- BUCHARESTUA_LATEST_START -->"
END = "<!-- BUCHARESTUA_LATEST_END -->"
CARD_LIMIT = 8
CARD = re.compile(r'<a class="m-card\s*" href="([a-z0-9-]+)\.html">.*?</a>', re.S)


def write_home(root, output, slug, card):
    """Stage the homepage, leaving its hand-picked features and links alone."""
    page = (root / "index.html").read_text(encoding="utf-8")
    before, latest = page.split(START, 1)
    latest, after = latest.split(END, 1)
    if CARD.sub("", latest).strip():
        raise ValueError("Latest-publication cards have unexpected markup")
    matches = list(CARD.finditer(latest))
    existing = {match[1]: match[0] for match in matches}
    if len(existing) != len(matches):
        raise ValueError("Duplicate links in latest-publication cards")
    candidate = CARD.fullmatch(card)
    if not candidate or candidate[1] != slug:
        raise ValueError("Latest-publication card must link to the approved article")
    if slug in existing:
        existing[slug] = card
    else:
        existing = {slug: card, **existing}
    cards = list(existing.values())[:CARD_LIMIT]
    (output / "index.html").write_text(before + START + "".join(cards) + END + after, encoding="utf-8")
