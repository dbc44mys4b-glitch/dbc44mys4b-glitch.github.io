# Independent QA · P05 kids classes · 2026-11-14

**Decision: BLOCK.** Reviewer role: independent QA only; no changes to candidate HTML or publication in this run.

Candidate: `editorial/candidates/P05-kids-classes-bucharest.html`
Exact UTF-8 SHA-256: `49c59d8247acf91048d366ebc2bcb031ad67a988cc4b930ffa73bf6d42a35b87`
Git blob SHA: `101d03edc80a9ef411077fbc2f36d287ff765fa4`.
Prior candidate commit: `e188353b50435da1e0d44e99db6910df2380cff0`.
Checked 2026-11-14 Europe/Bucharest. Source verification is limited to the directly opened official pages listed below; do not infer other links were rechecked.

## Ten criteria (0–10, all >=8 required)
1. Official source facts and recency: **4/10 BLOCK**. Candidate identifies `ARCUB · Școala de Artă` and asserts 2026–27 September admission; linked `https://sarta.ro/` identifies itself as **Școala de Artă București / Primăria Municipiului București**, not ARCUB, and the homepage admission notice visible on 2026-11-14 says **2025–2026**, not 2026–2027. Primary evidence: https://sarta.ro/ (homepage headings and admission notice).
2. Factual accuracy: **5/10 BLOCK**. Wrong organizer attribution and unsupported current-year intake for item 02; other details have not all been freshly revalidated.
3. Local usefulness: **8/10**. Six specific providers, geographic hints and practical selection questions. Sector 6 source https://www.asistentasociala6.ro/dgaspc6/dsc/crdpcgg confirms its 2026–27 courses and September enrollment; it also states eligibility criteria that the candidate omits.
4. Clarity: **9/10**. Good distinctions between closed enrollment, unknown availability and one-off events.
5. Originality: **9/10**. Original explanatory text and inline geometric SVG, no third-party artwork.
6. Search intent: **8/10**. Addresses family search for classes and selection questions.
7. SEO metadata: **7/10 BLOCK**. Article JSON-LD has `datePublished: 2026-11-14` while this is an unpublished candidate; replace with actual release date at publication or omit until release. Canonical and OG refer to intended public URL; existence of `/og-image.png` not checked.
8. Accessibility/mobile: **8/10 provisional**. Responsive grid, viewport and focus styles present by static inspection; no real browser viewport test performed, so not verified as deployed.
9. Illustration and rights: **9/10**. Original inline SVG/CSS visual in candidate, no external photo; generic OG image existence/provenance not independently confirmed.
10. CTA and technical: **8/10 provisional**. Telegram CTA present and external links have rel protections; internal links and live behavior not independently verified.

## Maximum three actionable corrections for EDITOR run
1. **Fix item 02 from the primary source.** Do not call `sarta.ro` ARCUB; identify the actual institution accurately and remove or substantiate the 2026–27 admissions claim with an official dated notice. Recheck that the school offers age-appropriate programs before describing it as a children's option.
2. **Add Sector 6 eligibility caveat** to Conacul Golescu-Grant card (ages 4–18, residency/foreign-child conditions and course terms per official page); do not suggest universal access. Source: https://www.asistentasociala6.ro/dgaspc6/dsc/crdpcgg .
3. **Correct publication metadata for candidate/release**: no false `datePublished` before release; ensure the actual public date and OG asset are validated at release.

Next run: EDITOR fixes these specific defects in candidate, recomputes SHA-256 and marks READY_FOR_QA. Subsequent separate run: independent QA for NEW SHA only. Do not publish this SHA.
