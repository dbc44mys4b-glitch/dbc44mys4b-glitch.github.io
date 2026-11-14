# Independent QA · P05 kids classes · revised candidate · 2026-11-14

**Decision: PASS for this exact candidate, subject to normal RELEASE checks.** This QA-only run did not edit the candidate or publish it. This PASS authorizes a separate release run to deploy only the unchanged SHA-256 below; it is NOT proof of deployment or live accessibility.

- Candidate: `editorial/candidates/P05-kids-classes-bucharest.html`
- Exact UTF-8 SHA-256: `8b9a81a3dc89a1f7e271e1e0e65c21b4fba3c516b0e50b3f239a3ac0a4215984`
- Git blob SHA: `f909588ea15fb976855ac43bd6c5c4582c8f9e83`
- Candidate editor commit: `ab9d7a95a0b70e86667ae57190865fb20a47374e`
- Reviewed 2026-11-14, independent QA role only. SHA-256 recomputed from fetched full UTF-8 file and matched queue value.

## Ten criteria (minimum 8/10 each)
1. **Official facts and recency: 8/10 PASS.** Opened all six organizer first-party sites. Școala de Artă București is now correctly attributed; the article explicitly warns that only 2025–26 enrollment notice is found, not an invented 2026–27 intake. https://sarta.ro/
2. **Factual accuracy: 8/10 PASS.** DGASPC6 confirms 4–18 age bracket, Sector 6 residence/foreign-child criteria, 2026–27 courses and expired September 2026 registration; source page contains contradictory September 15/20 cutoff language, so candidate wisely does not repeat a specific deadline. https://www.asistentasociala6.ro/dgaspc6/dsc/crdpcgg
3. **Local usefulness: 9/10 PASS.** Six named providers, geographic details where sourced, decision questions and Romanian contact script. Tennis school address is confirmed https://scoalaeuropeanadetenis.ro/ and Champion stadium address is confirmed https://www.scoalatenis.ro/ .
4. **Clarity: 9/10 PASS.** Explicitly distinguishes expired admissions, unknown open places, ongoing classes and one-off activities.
5. **Originality: 9/10 PASS.** Original explanatory text and inline hand-authored geometric SVG; no externally hosted photo or third-party art in candidate.
6. **Search intent: 9/10 PASS.** Answers Russian-speaking parents' search for kids' activities in Bucharest with provider links and practical enrollment questions.
7. **SEO metadata: 8/10 PASS.** Unique title/description, canonical and OG URL consistent with intended slug, Article JSON-LD valid-looking by static inspection; no false datePublished and no unverified og:image. Release must validate actual public canonical and structured-data parse.
8. **Accessibility/mobile: 8/10 PASS (static).** viewport, responsive two-column-to-one-column CSS, visible keyboard focus, semantic headings, SVG accessible label. Browser-based mobile screenshot not available in this QA run; release must check actual page at mobile viewport before counting publication.
9. **Image provenance/rights: 9/10 PASS.** Inline geometric SVG and CSS are original candidate assets; no third-party images or licenses required. No OG image falsely asserted.
10. **CTA/technical: 8/10 PASS (static).** Correct Telegram link https://t.me/bucharest_info, noreferrer/noopener external links, internal related links. Release must verify internal URLs and actual HTTP 200, sitemap/RSS where used, Pages/Actions and mobile behavior; unverified items cannot count as live.

## Specific first-party evidence (reopened in this QA run)
- https://sarta.ro/ — Școala de Artă București; site displays children's painting program and admission 2025–2026.
- https://www.asistentasociala6.ro/dgaspc6/dsc/crdpcgg — eligibility, school-year 2026–27, course list and enrollment caveat.
- https://mimamuzica.ro/educatie-muzicala/mima-bucuresti/atelier-one-time/ — 10-workshop modules and one-time reservation subject to availability.
- https://studio-creativ.ro/ — drawing/painting age groups and September 2026–June 2027 courses.
- https://scoalaeuropeanadetenis.ro/ — children's tennis and Strada Carpați 100, Sector 1.
- https://www.scoalatenis.ro/ — Champion tennis for children and Primo Nebiolo 2, Sector 1.

**Next run: RELEASE only**, if the candidate SHA remains identical. Publish to `kids-classes-bucharest.html`, check live URL and metadata, sitemap/RSS/CTA/internal links, real Pages status and mobile; do not count a publication if any essential verification is unavailable. Do not modify candidate in this QA run.
