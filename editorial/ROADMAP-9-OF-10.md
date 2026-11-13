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
| P13 | TRUST | Editorial transparency and corrections policy | named responsibility, sources, dated updates and correction log | PARTIAL: internal policy documented; public corrections route and actual log outstanding |
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

## Execution log · 2026-11-13 00:13 Europe/Bucharest
- P04/P10: found visibly truncated `description` metadata in `massage-bucharest.html` (HTML meta, Open Graph and JSON-LD). Replaced all three with a complete, accurate description; commit `11e36440d1a2bb2445f97517367a960518456da7`. The article's editorial body was not rewritten or independently approved.
- GitHub content read confirmed the planned 2000-article editorial architecture exists at `editorial/AUTONOMOUS-EDITORIAL-2000.md`; this is documentation, not running agent software.
- Public HTTP verification attempted for the massage URL but runtime DNS resolution failed. Do not claim this revision is live or Pages passed. Retry Pages/HTTP and independent QA on next run.
- P02 remains blocked for new scheduled articles without actual independent source-backed review; publication gate must remain fail-closed. Next actionable work: inspect actual workflow and QA review schema, implement review production and test with a single article; separately source-rewrite massage guide.

## Execution log · 2026-11-13 01:09 Europe/Bucharest
- P10: committed a new **read-only** article metadata preflight at `scripts/audit_article_metadata.py` (commit `b8971daa3f113be879689f4549c3e342d90165fb`). It checks canonical/OG/JSON-LD description alignment, basic title/h1, Telegram CTA and image alt. It does **not** replace independent editorial QA and does not grant publication approval.
- GitHub content API confirms the roadmap and current massage article are readable. Guessed workflow paths `.github/workflows/editorial.yml` and `.github/workflows/daily-editorial.yml` were absent; the real workflow path is not yet established. GitHub code search for `workflow_dispatch` and `qa-reviews` returned no matches; this is not proof no workflow exists.
- Public article fetch attempted again but web retrieval failed; deployment of the latest changes and mobile rendering remain **unverified**.
- Next: discover actual Actions workflow names and run preflight against repository content; inspect failures before integrating into CI. Independently source and rewrite massage article; do not waive QA gate.

## Execution log · 2026-11-13 01:49 Europe/Bucharest
- P10: added `tests/test_article_metadata.py` with seven focused regression cases for valid metadata, missing Telegram CTA, missing alt, absent/malformed JSON-LD, inconsistent descriptions and wrong canonical. Commit `a56454cbd8ef811cfcbbceb8811d13c158f9c013`; [source](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/blob/main/tests/test_article_metadata.py).
- Tests were **committed but not executed** in this run; CI integration and test results remain unverified. These tests do not replace independent source-backed editorial QA.
- Re-read live repository `massage-bucharest.html`: the body still has generic advice, and a text-only fallback cover. The article does not meet the desired local-source and original-image gate. No unsupported business names, prices or QA approvals added.
- Workflow lookup for `.github/workflows/pages.yml` and `.github/workflows/editorial.yml` returned 404; these guessed paths do not establish actual Actions configuration. Pages status and public deployment not verified in this run.
- Next: execute seven tests, fix failures, discover workflow by listing actual repository tree, and then independently source-rewrite massage guide. Keep fail-closed publication QA.

## Execution log · 2026-11-13 03:20 Europe/Bucharest
- P10: source inspection found a genuine fail-open **technical metadata** gap: any valid JSON-LD object (even WebSite rather than Article) was accepted as long as JSON-LD existed. Fixed the preflight to require an Article JSON-LD object; commit `e5f48774fae2dec1a1dde8dc4bacbf36893534e4`.
- Added regression `test_non_article_jsonld_fails` in `tests/test_article_metadata.py`; commit `aba7287300cba7f54694cf3d6e700cec2d341812`. Total defined focused test cases now eight, **not yet confirmed passing**.
- Attempted a shallow Git clone to run tests, but this execution environment failed DNS resolution for github.com. Therefore no actual test-run result or deployment verification is claimed. Source code and test were read/updated through authenticated GitHub contents API.
- Editorial QA remains fail-closed; this technical audit never approves articles. P04 massage rewrite, rights-cleared imagery and independent source-backed review remain open. Next: run tests in a GitHub Actions job or an environment with repository access; verify Pages deployment and audit public page. No new article published in this run.

## Execution log · 2026-11-13 03:48 Europe/Bucharest
- P10: improved technical metadata audit to inspect Article/NewsArticle/BlogPosting nodes inside JSON-LD `@graph` and top-level arrays, including multi-valued `@type`. Previously a valid article embedded in a schema.org graph would be incorrectly rejected; now each matching node's mainEntityOfPage and description are checked. Commit `99550385c24ddb7bf4b7e8d8a541ef683cbb8aed`.
- Added two regression cases for graph Article acceptance and incorrect graph Article URL rejection, bringing defined test cases to ten. Commit `d2eb199fd8fedbf16763d4d80606922b7294d969`. **Not executed in CI or locally in this run**; passing tests must not be inferred from committed code.
- Inspected source of massage guide and QA roadmap via authenticated GitHub API. Massage still uses a generic text cover and lacks verified local providers; no factual or image rights approval was issued.
- Workflow configuration and latest Pages build were not independently established; public HTTP/mobile validation remains outstanding. P02 independent QA still fail-closed. Next: execute tests, verify Pages, source and rewrite P04 with licensed image; if blocked, advance to P05/P06.

## Execution log · 2026-11-13 04:49 Europe/Bucharest
- P10: added a scoped GitHub Actions workflow `.github/workflows/article-metadata-tests.yml` to execute the existing ten metadata regression tests on changes to the auditor/tests/workflow, on pull requests, or manually. It has read-only `contents` permission, five-minute timeout, and does not publish or grant editorial QA approval. Commit [`5e5e2c2c0310fd74774bb395ff8c5b3d2ab61e24`](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/commit/5e5e2c2c0310fd74774bb395ff8c5b3d2ab61e24).
- GitHub Actions commit-workflow lookup returned an empty list for that commit; this endpoint filters to PR-triggered runs and is **not proof** that push CI did not execute. Tests are **not yet verified passing**. Do not claim CI green.
- Attempted public HTTP retrieval of `massage-bucharest.html`, but the retrieval tool reported inaccessible URL; Pages deployment and mobile QA remain unverified. Local git ls-remote also failed due to DNS resolution of github.com; authenticated GitHub contents API worked.
- P02 independent editorial QA remains fail-closed. No new source-backed reviews or approved articles created. Next: verify actual CI run result using Actions UI or suitable API, address any test failures, then rewrite P04 with primary sources and rights-cleared relevant image.

## Execution log · 2026-11-13 05:44 Europe/Bucharest
- P10: reviewed actual `.github/workflows/article-metadata-tests.yml`, metadata auditor, ten unit test definitions and current `massage-bucharest.html` via authenticated GitHub file reads. Found coverage gap: workflow ran unit tests but did **not** audit a real published article. Updated workflow to execute `python3 scripts/audit_article_metadata.py massage-bucharest.html` and trigger on massage article edits in both push and PR; commit [`7a1ca11614c897925de1ad509f3a7ac46cfc13a5`](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/commit/7a1ca11614c897925de1ad509f3a7ac46cfc13a5).
- This is read-only technical preflight, **not** independent editorial approval. P02 fail-closed QA unchanged. No new article approved or created.
- Public URL [massage-bucharest.html](https://dbc44mys4b-glitch.github.io/massage-bucharest.html) was attempted through web retrieval but tool reported inaccessible; deployment, live HTTP status, mobile screenshots and CI outcome remain **unverified**. Authenticated source is readable; the massage guide still lacks local verified provider sources and rights-cleared image.
- Next: verify actual Actions job and test result (the PR-filtered commit lookup cannot establish push-run status); independently source-rewrite P04, then image and separate QA; if sourcing blocked, advance to P05/P06. Do not equate a passing metadata test with article QA.


## Execution log · 2026-11-13 07:08 Europe/Bucharest
- Read the actual roadmap, metadata test workflow, audit script, and massage HTML through authenticated GitHub content API. Workflow exists at `.github/workflows/article-metadata-tests.yml` and calls ten unit tests plus a metadata preflight for the massage HTML; **workflow source inspection is not evidence that Actions ran successfully**.
- P04 remains blocked for publication: massage guide still lacks named locally verified providers and a relevant rights-cleared image; the current text-based fallback and generic `og-image.png` are not a substitute. No claims, prices or business listings invented.
- Advanced next independently actionable item P13: added [internal editorial standards and corrections policy](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/blob/main/editorial/EDITORIAL-STANDARDS-AND-CORRECTIONS.md), commit [`a0da2cc080ba06c68178672666d8cdf4ed9f70e0`](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/commit/a0da2cc080ba06c68178672666d8cdf4ed9f70e0). Covers primary-source rules, correction escalation, content hash reapproval, image licensing, commercial disclosures and privacy. This is an internal policy file, **not yet a public page or a verified monitored corrections channel**.
- No new article QA pass, public deployment, Pages status, mobile screenshot or analytics measurement claimed this run. Next: confirm actual Actions job status using an endpoint that lists push runs; complete source-backed P04/P05/P06 and visual QA; create verified public corrections route before marking P13 done.

## Execution log · 2026-11-13 08:11 Europe/Bucharest
- P10: authenticated GitHub reads confirmed the roadmap, massage HTML, metadata audit script and Actions workflow exist on the default branch. Workflow source defines 10 pre-existing unit tests and real massage HTML preflight; source alone does not prove a successful CI run.
- Fixed two technical audit edge cases: repeated `meta` keys previously overwrote each other silently (now flagged); canonical `rel` previously required an exact string rather than a whitespace-separated token (now parsed correctly). Commit [`a0f65b4d`](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/commit/a0f65b4d611b49ef33dbbe8b2cf883236072f5a4).
- Added two targeted regression tests, for duplicate description rejection and multi-token canonical acceptance; 12 defined tests total, **not yet verified passing in CI**. Commit [`c7ab8ee0`](https://github.com/dbc44mys4b-glitch/dbc44mys4b-glitch.github.io/commit/c7ab8ee0263149f77caa2ff0a2f99602910c86d2).
- P04/P05/P06 factual rewrites remain pending. No new article or editorial approval; independent publication QA unchanged. Latest Pages deployment, public HTTP, mobile screenshots and actual CI results **not verified** in this run. Next: verify Actions job result, inspect any failures; source-rewrite P04 with official local sources and licensed image, or advance P05/P06 if blocked.
