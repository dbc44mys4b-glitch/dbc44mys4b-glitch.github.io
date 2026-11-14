# Independent QA · P04 massage Bucharest · 2026-11-14

Role: INDEPENDENT_QA ONLY. Candidate: `editorial/candidates/P04-massage-bucharest.html`. Exact UTF-8 SHA-256: `80b3bd401ce943bce0f4f4e18e2df085cd91f2a30ac7bddf33b111857eb612a5`. Git blob: `e3542fdf489ab97e25c976b697cf64a75d979040`. Candidate not edited or published in this run.

## Decision: BLOCK

10 concrete checks (score / 10): source facts and recency **7**; factual accuracy **7**; local utility **9**; clarity **9**; originality **9**; search intent **9**; SEO metadata **9**; accessibility/mobile **8** (static code review, no rendered-device claim); imagery rights **10** (original inline SVG); CTA/technical **8** (canonical, Article JSON-LD, Telegram CTA, responsive layout). No release until corrected and independently re-reviewed against a NEW hash.

Evidence: official price pages inspected 2026-11-14: Golden Spa https://goldenspa.ro/preturi/ (relax 50 min 150 lei; therapeutic 50 min 190 lei); Kinetoprof https://www.kinetoprof.ro/preturi/ (therapeutic 30 min 100 lei, kinetotherapy 60 min 100 lei); Amrita https://amritamasaj.ro/preturi (relax 60 min 230 lei, therapeutic 60 min 250 lei); SIS Spa https://sis-spa.ro/masaj/ (couples 60 min 340 lei, fusion 90 min 270 lei); TotalKinetic https://totalkinetic.ro/preturi-kineto/ (back therapeutic 100 lei, duration unspecified). Addresses confirmed on corresponding official pages where visible. Elisara https://elisara.ro/masaj-de-relaxare shows a price headline “de la 250 lei” but the dynamically selected price displayed in fetched content is 450 lei, not a clearly evidenced 250/260 lei contradiction for the same 60-minute option. Avoid publishing the unsubstantiated numeric pair.

## Actionable corrections (max 3)
1. **Elisara price**: remove the claim “60 мин — цена на странице противоречива (250/260 лей)” unless both prices and 60-minute applicability can be demonstrated with dated first-party evidence. Safer: “Цена и длительность выбранного сеанса — уточняйте при записи; динамический прайс”, and adjust the note below the cards accordingly.

All other listed prices checked against primary sources; no additional changes requested. Next distinct run: EDITOR fixes this single issue, recomputes SHA-256, queues revised HTML for fresh independent QA. No QA PASS or verified publication in this run.
