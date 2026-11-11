# BucharestUA — Brand & Newsroom Standard v2
Updated: 2026-11-12
Owner: BucharestUA editorial operation

## Brand
BucharestUA is an independent, premium, multilingual city publication for people living in and discovering Bucharest. Its voice is intelligent, lively, practical and humane. Do not claim to be the official or biggest Bucharest news source without evidence. Never fabricate a reporting team, interviews, ratings, facts or real-time coverage.

## Visual direction
Editorial minimalism, quiet confidence, generous whitespace, refined typography, a restrained warm-neutral palette with muted blue accents. No cartoon skyline, fake photo, random gradient or enormous CTA. Headlines and genuine visual storytelling lead; Telegram is a secondary but visible conversion.
Use one design system across homepage, feed, story, guide and localized pages. Design QA at 375, 390, 768, 1024 and 1440px; check overflow, tap targets, navigation, visual hierarchy, images, typography and Core Web Vitals.

## Article standards
- 250–500 words for most stories; longer only when the subject needs it.
- One strong, truthful hook and one specific reason to read.
- No generic filler, repetitive template paragraphs or unverified superlatives.
- Prefer real local details: addresses, neighborhoods, prices, dates, primary sources, useful maps and practical context.
- News: timestamp of reporting and event, verified primary source, fresh angle, avoid speculation and duplication.
- Events: confirmed dates, location, ticketing/price if known, organizer source; never recycle expired listings.
- Separate reporting, opinion, sponsored content and illustration; no undisclosed paid endorsements.
- Editorial review before publication; broken, thin, inaccurate or generic articles must be held for revision.

## Media policy
- Photo relevance is mandatory. Valid copyright license alone is insufficient.
- Check the *actual image content*, not just title or alt. The previously used military medical mission photograph for a massage article is an explicit QA failure.
- Prefer verified relevant real Bucharest photos with legally required credit.
- If no suitable real photo, commission/generate an original topical illustration with explicit AI labeling, or hold the image pending approval. Do not imply an AI-generated image documents an actual event, person, business or location.
- Never put a text-only category block on the homepage as a permanent replacement for an image. Temporary editorial fallbacks are tracked as issues, not counted as finished assets.
- For every published image record: topic, source, author, license, alt, rights verification, editorial relevance and visual QA status.

## Language and discovery
- Four target languages: Russian (ru), Ukrainian (uk), Romanian (ro), English (en).
- Every translated article requires a separate working URL, correct HTML lang, localized title, meta description, body, navigation and relevant CTAs. Include hreflang reciprocal links and x-default only when those actual pages exist. Include each URL in sitemap.
- A language toggle must not imply the article is translated when only a translated homepage exists. Never send readers to a different-language article without indicating fallback.
- Translation must preserve accuracy and read naturally to native speakers; localize search intent, not just keywords. Use Romanian terms when helpful. Avoid stuffing keywords or claiming search rankings.
- Search engine and AI discovery: crawlable HTML, canonical, semantic headings, structured data matching real content, RSS, sitemap, internal links, honest author/publisher attribution and reputable citations.

## Roles and workflow
1. **News scout**: scan authoritative city sources for significant changes; timestamp and triage.
2. **Editor-in-chief**: choose angle, commission article, prioritize urgent news.
3. **Fact-checker**: verify dates, claims, sources and sensitive information.
4. **Creative editor**: write distinctive headline, short lead and shareable teaser without deception.
5. **Photo editor**: source or generate relevant, rights-cleared imagery; visual check.
6. **Localization editor**: RU/UA/RO/EN complete, natural translations and language QA.
7. **SEO/GEO analyst**: search intent, links, schema, indexing evidence, performance.
8. **Brand director / design QA**: keep visual consistency and check responsive breakpoints.

These are responsibility roles within the existing automation unless separate working agents with independent execution are actually configured.

## Release gate
1. Story is accurate, current, concise and genuinely useful.
2. Hero image is on-topic, high quality, rights-cleared and credited.
3. The displayed language matches the entire article; hreflang references only published versions.
4. Links, metadata, canonical, RSS, sitemap and Telegram CTA are correct.
5. Mobile and desktop visual review passed.
6. GitHub commit and public page HTTP verified before reporting 'published'.

## Escalation
If an image or translation cannot be safely completed, do not fabricate. Log the blocker, continue other work and report only material problems. Do not claim a QA test was performed without evidence. Never overwrite verification tags or the Telegram destination.
