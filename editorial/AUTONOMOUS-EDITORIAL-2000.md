# BucharestUA · Autonomous editorial operating plan (v1)
Date: 2026-11-12. Status: **DESIGNED, NOT YET AUTOMATED OR VALIDATED**.

## Step 0 · editorial choice
- **Niche:** practical, source-verified Bucharest/Romania living guides for newcomers, especially Ukrainian and Russian-speaking residents.
- **Primary language:** Russian; Ukrainian, Romanian and English versions only when accurately localized and reviewed. Do not publish empty or machine-unchecked translations.
- **Audience:** newcomers, families, residents needing verified local services and civic information.
- **Single publishing platform:** existing GitHub Pages site https://dbc44mys4b-glitch.github.io/ in this repository. Telegram https://t.me/bucharest_info is a disclosed community CTA, not a second publishing platform.
- **Why:** existing domain, editorial history and audience; avoids opening a duplicate site and creating cannibalization. Demand, traffic and rankings remain unverified until measured.
- **Target:** 2,000 distinct, quality-approved, published articles with rights-cleared relevant original images. This is a target, **not** a publication count.

## Non-negotiable publication contract
An article counts only when its exact-content SHA-256 has a recorded independent QA pass, all six gates below pass, the reviewed image has a rights record and alt text, and the public URL is verified after Pages deployment. No synthetic QA approvals, fabricated citations, photos, rankings or metrics.
Gates: local utility and specificity; primary-source factual accuracy (every numerical/date claim cited); originality/plagiarism review; honest disclosure; editorial readability and >=8/10; relevant image with provenance/rights and alt text. Missing reviewer, broken source or unverified image = BLOCK.

## Nine specialist roles and handoffs
1. **Topic strategist:** own unique intent registry; propose one query cluster and differentiate against every existing URL. Output slug, intent, audience, priority and cannibalization check.
2. **Researcher:** collect official local primary URLs, claim-level evidence, verification date; never infer addresses, schedules or prices.
3. **Author:** produce original, useful narrative and practical steps using only evidence ledger; mark uncertainty rather than fill gaps.
4. **Fact-checker:** independently open cited URLs; verify every numeric, dated, location and safety-sensitive claim; delete unsupported statements.
5. **Editor:** reject filler, repeated phrasing, misleading claims and robotic tone; score against published rubric.
6. **Visual editor:** generate original image only with an available licensed generation workflow, or use properly licensed image with documented attribution; verify topical relevance, alt, crop and rights. No image = hold.
7. **SEO editor:** unique title/description, semantic headings, canonical, hreflang when applicable, sitemap/RSS, internal links, OG and honest CTA.
8. **Independent QA auditor:** separate review from author; check exact SHA, source ledger, image provenance, all gates and device QA; sign pass/fail with evidence. Never self-certify.
9. **Blocker resolver:** classify failure, inspect logs/docs, attempt at most 3 compliant fixes, record outcomes; then quarantine article and advance queue.

## State machine
IDEA -> RESEARCHED -> DRAFT -> FACTCHECKED -> EDITED -> VISUAL_READY -> SEO_READY -> QA_PENDING -> QA_PASS -> DEPLOY_PENDING -> VERIFIED_PUBLIC.
Any failed gate -> NEEDS_FIX (up to 3 attempts) -> QA_PENDING; after 3 failures -> QUARANTINED and move on. QA missing is actionable QA_PENDING, not an approval or a global stop.
Only the independent auditor may set QA_PASS. Fingerprint invalidates approval on any content/image change. Publishing gate remains fail-closed.

## Topic architecture, not yet 2,000 approved article briefs
Proposed capacity **20 clusters x 100 distinct intents = 2,000 candidate slots**, not 2,000 verified unique topics. Each slot must be researched and deduplicated before acceptance. Clusters:
1 residency and documents; 2 public transport; 3 airports and travel; 4 family doctors; 5 hospitals and emergency care; 6 pharmacies; 7 kindergartens; 8 schools; 9 children's activities; 10 sports and tennis; 11 housing and tenancy; 12 utilities; 13 neighborhoods and sectors; 14 banking and payments; 15 mobile and internet; 16 car ownership; 17 car repair; 18 employment administration; 19 parks and culture; 20 local consumer services.
For each cluster, strategist creates distinct intent families (how-to, eligibility, documents, location, comparison, accessibility, cost with verification date, appointment, common mistakes, family-specific use), and records canonical target URL. **Never mechanically multiply a query into 100 near-duplicate articles.** Merge overlapping intents into one authoritative guide. A realistic map of 2,000+ individually differentiated briefs remains outstanding and must be generated in batches with deduplication evidence.
Priority now: existing weak massage, children's classes and hospitals guides; improve existing URLs before creating competing URLs.

## Blocker protocol
Log one-line failure, evidence/log link, 2-3 compliant remedies, one-article test, result and changed agent prompt. At most three attempts. No captcha bypass, scraping around controls, borrowed credentials, unlicensed assets, fake reviews or unapproved spend. If external data/access cannot be obtained, quarantine and continue independent work.

## Audit and cost controls
Every 50 **verified** articles: randomly select 10 and log scores, factual and originality issues, remediation and new sample. Every 100: report verified public URLs, rejected count, average QA score, measured resource use (or unknown), blocker fixes. If trailing 100 reviewed articles average <7.5, stop publication and repair pipeline. At 80% of a measurable allocated resource budget, pause and report; unknown quotas must never be represented as zero cost.
No promise of continuous execution unless a scheduled task actually runs and can access the necessary tools. The existing hourly automation must be checked separately; this document alone does not create autonomous agents or execution.

## First implementation backlog
A. Inspect current GitHub Actions and QA review schema, then implement an independent QA job that produces actual source-backed reviews without changing the fail-closed publisher.
B. Pilot on massage guide, with real official sources and licensed relevant imagery; record all failures and rerun.
C. Verify Pages, canonical, sitemap, RSS, CTA, language switch and 360/390/430px mobile views for pilot.
D. Create a machine-readable topic registry and first 50 individually differentiated briefs, check against live URLs, then scale only after audit.
E. Integrate counters and reporting from verified published URLs and QA records, not draft counts.

## Execution evidence
2026-11-12: Plan file created; **no claim** that any article passed QA, any agent was deployed, or 2,000 topics were validated. Existing QA remains blocking until real reviews exist.
