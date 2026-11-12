# BucharestUA · Roadmap to verified 9/10
Updated: 2026-11-12 22:47 Europe/Bucharest. This is a tracked improvement program, **not** a claim that any score is already achieved.

## Rules
- Scores are assigned only after independent evidence-based review. A target score is not a current score.
- Do not publish new articles without a QA record for the exact content SHA-256, all 10 dimensions >=8, external evidence and a distinct reviewer.
- For a **9/10 media-wide** target, review representative pages across all types, languages and devices. Report failures, not averages that hide defects.
- Search visibility and conversion must be measured; neither can be guaranteed.

## Work packages (ordered, with acceptance tests)
| ID | Owner role | Work | Evidence / definition of done | Status |
|---|---|---|---|---|
| P00 | TECH | Stop recursive editorial triggers and report commits | workflow scheduled/manual, audits in Actions artifacts, Pages deploy succeeds | VERIFIED: Pages build succeeded for 183498d6 |
| P01 | OPS | Prevent stale queue metadata from replacing hand-edited pages | edited titles/cover match homepage, catalog, RSS, OG; regression test | PARTIAL |
| P02 | QA | Enforce independent review before scheduled publication | 10 scores, evidence, SHA fingerprint; missing review blocks | GATE HARDENED; independent reviews still missing |
| P03 | EDITOR | Audit all published long-form articles | per-slug review with actionable findings in editorial/qa-reviews | TODO |
| P04 | FACT | Rewrite massage guide | verified local providers, qualifications, price verification date, primary sources | TODO |
| P05 | FACT | Rewrite children classes guide | verified clubs by age and area, registration details and source links | TODO |
| P06 | FACT | Rewrite hospitals guide | named facilities, departments, verified addresses, 112 triage, source links | TODO |
| P07 | EDITOR | Rewrite other weak guides in priority order | concrete local facts, original angles, no generic template | TODO |
| P08 | VIS | Audit article photography and licensing | image exists, topic matches, credits/license logged, mobile crop checked | TODO |
| P09 | UX | Mobile QA on 360/390/430/768px | no overflow, working menu, accessible links, readable body | TODO |
| P10 | SEO | Validate canonical, titles, sitemap, structured data, redirects | automated checks and sample manual inspection | PARTIAL |
| P11 | LOC | RU/UA/RO/EN equivalence audit | translations complete, hreflang reciprocal, language switch keeps context | TODO |
| P12 | NAV | Improve taxonomy and related-article links | topic clusters with no dead ends or orphan guides | TODO |
| P13 | TRUST | Editorial transparency and corrections policy | named responsibility, sources, dated updates and correction log | TODO |
| P14 | ANALYTICS | Search Console + click/conversion measurement | impressions, clicks, indexing, Telegram outbound events baseline | BLOCKED ON ACCESS/DATA |
| P15 | GEO | AI discoverability evidence | cited answers and measured referrals, no invented rankings | TODO |
| P16 | COMMUNITY | Improve Telegram CTAs without clickbait | tracked CTA events and useful natural placement | TODO |
| P17 | GROWTH | Earn legitimate relevant external mentions | documented outreach and real links, no paid spam | TODO |
| P18 | REVENUE | Define ethical monetization and disclosure | documented sponsor/affiliate policy and verified attribution | TODO |
| P19 | RELEASE | Independent final audit of all 20 criteria | evidence pack, scores and known limits; >=9 on every criterion | TODO |

## Content QA checklist
For every article: (1) intent (2) unique local utility (3) verified official source URLs (4) time-sensitive facts checked (5) original writing (6) photo rights and relevance (7) accurate title/description (8) mobile usability (9) meaningful internal links (10) share-worthy takeaway. A missing critical fact, unsafe health/legal advice, false attribution or broken image is a BLOCK regardless of average.

## Release protocol
1. Author and fact-check draft; retain citations and check date.
2. Independent reviewer documents evidence and scores; block any dimension <8.
3. Verify the content fingerprint; approve only the exact reviewed revision.
4. Publish and verify public HTTP, page image, catalog, RSS, sitemap and link targets.
5. Log Search Console metrics separately from editorial scores.
6. Report counts of passed, blocked, and unreviewed items. Never label unreviewed items 9/10.

## Immediate editorial priority
- massage-bucharest.html (sample content score 3/10)
- kids-classes-bucharest.html (4/10)
- hospital-bucharest.html (4/10)
- first-month-bucharest-checklist.html (7/10; update catalog and photo attribution)
- airport-otopeni-guide.html (8/10; revalidate changing transit facts)

## Execution log · 2026-11-12 22:47 Europe/Bucharest
- GitHub Actions API: Pages build completed successfully at commit `183498d6b` (this confirms build, not per-page visual QA).
- Commit `1841c230ebc88eeb9b4ac6d59722d0e9b4313627`: publication QA parser now safely rejects malformed JSON review shapes rather than crashing; held due articles are reported explicitly, no longer mislabeled as 'no article due'.
- P02 remains blocked for new articles until independent, source-backed reviews are actually recorded. No reviews or article approvals fabricated.
- P04 massage article inspected: currently generic and not ready for a 9/10 editorial rating; requires verified local businesses, source citations, prices/qualification checks and substantive rewrite.
- Next: P04 factual sourcing and rewrite; verify this commit's workflow/Pages run separately.
