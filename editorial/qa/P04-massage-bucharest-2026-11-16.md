# P04 independent QA — 2026-11-16

Candidate: editorial/candidates/P04-massage-bucharest.html
SHA-256 (UTF-8): e085a5efa704221d3e38e3814ce05e4a76ddf76b2dbbe646cd8c4aefca15fa69
Git blob SHA: 68aa05192d1a21e3c14caeb2ca48970cdbe3261b
Decision: BLOCK. This QA run did not edit or publish candidate.

## Ten criteria
1. Source facts/recency: PASS with caveat — Elisara 250 lei in text, 260 lei booking widget, both explicitly disclosed; SIS Spa 340 lei couples 60m and 270 lei fusion 90m; TotalKinetic 100 lei therapeutic back confirmed 2026-11-16.
2. Accuracy: PASS for these three checked providers; others were verified in previous QA.
3. Local utility: PASS — addresses, durations, contact links and Romanian message.
4. Clarity: PASS — comparable treatments and booking caveat.
5. Originality: PASS — independently written guide and inline authored SVG.
6. Search intent: PASS — six options and prices.
7. SEO metadata: BLOCK — og:image points to /assets/massage-bucharest-social.svg, which does not exist in public root; staged SVG exists only at editorial/candidates/assets/massage-bucharest-social.svg. SVG OG support is also inconsistent across social platforms.
8. Accessibility/mobile: PASS in source inspection — viewport, mobile single-column CSS, labelled SVGs; browser/device visual QA not confirmed.
9. Imagery rights: PASS — inline original vector art; staged OG artwork original SVG, no third-party rights needed.
10. CTA/technical: PASS in source — canonical, JSON-LD, internal links, Telegram CTA. Public release not verified.

## Corrections (max 3)
1. Replace OG image with a publicly deployable PNG/JPEG asset (1200x630), ensure correct final /assets/ path, and include it in the release package. Keep original artwork provenance.
2. Confirm visual mobile rendering and OG image URL with actual HTTP checks before release; if unavailable record UNVERIFIED rather than claiming success.

Evidence: https://elisara.ro/masaj-de-relaxare ; https://sis-spa.ro/masaj/ ; https://totalkinetic.ro/preturi-kineto/ ; GitHub paths above.

Next role: EDITOR, corrections only. No publication count increment.
