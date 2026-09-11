# DECISION.md — AI for Peace @ NeurIPS 2026

**Prepared:** Thu 10 Sept 2026 · **Team:** Adrian Erlikhman, Michael Tarekegn
**Deadline:** Mon 21 Sept 2026 AoE = **Tue 22 Sept, 05:00 Pacific**
**Status: Phase 1 complete. Awaiting your pick. Nothing has been built.**

---

## 0. Venue corrections you need before anything else

Verified against the source repo (`aiforpeaceworkshop/aiforpeaceworkshop.github.io`, `master`) and the live Google Form.

| Thing | What the brief assumed | What is actually true |
|---|---|---|
| **Submission artifact** | one-page PDF, `abstract.tex` | **Google Form, pasted text. No upload field.** Abstract capped at **2,500 characters**; separate **TL;DR capped at 300 characters** |
| **Hero figure** | "include it if it fits" | **Cannot be submitted at all.** It exists only for the Paris poster |
| Attendance | — | **Gating form question.** In-person Paris only, and they state they most probably cannot fund travel or registration |
| Speakers | Birhane / Widder / Redmon cited as speakers | **Proposed, not confirmed** — the site hides them behind `SHOW_NEURIPS_SPEAKERS = false`. Do not cite as confirmed |
| Edition 1 | 28 submissions, 13 posters, 3 orals | Confirmed. 16 accepted total |

Everything else in your summary verified exactly: deadline, decisions Sept 29, Dec 12–13 Paris, single-blind, poster/talk/both, all three work-status categories accepted, topic list and exclusions verbatim.

**2,500 characters is roughly 380 words.** That is the single biggest constraint on this project and it should drive the pick: whatever we build has to compress to one claim plus about four numbers. References count against it.

### The calibration read (this should change your priors)

Of the 16 accepted at edition 1: **~7 position essays, 4 sociotechnical analyses, 2 conceptual frameworks, 3 empirical papers.** **13 of 16 have no artifact.** But of the clear orals, **two of three were empirical audits** — empirical work was 19% of acceptances and ~67% of orals. All three empirical papers trace to one lab cluster (Jin / Mihalcea / Schölkopf).

Gaps, verified by reading all 16:
- **Stylometry / authorship attribution: zero papers.**
- **Scientometrics, citation or patent tracing: zero papers** — while at least five accepted essays argue *rhetorically* about how research flows into military use without measuring a single citation, patent, or funding link.
- **Peace-process NLP: zero papers.** At a workshop called AI for Peace.
- Saturated, do not touch: "dual-use risk is upstream", researcher complicity, governance primitives, Pegasus/surveillance-infrastructure critique, LAWS treaty analogies. A seventh of those is indistinguishable.

**Implication: bringing measurements is the strongest available differentiator, and three of our six candidates sit in a total void.**

---

## 1. Ranked table

| # | Idea | CFP fit /25 | Feasible by 17th /25 | Tuff /20 | Novelty /15 | Our edge /15 | **Total** | Ethics gate |
|---|---|---|---|---|---|---|---|---|
| **1** | **D — Can LLMs read a peace agreement?** | 24 | **25** | 16 | **14** | 10 | **89** | PASS |
| **2** | **B — The language surveillance pipeline** | **25** | 17 | **19** | 10 | 8 | **79** | PASS |
| 3 | F — Benchmark-to-battlefield *(mine)* | 24 | 15 | 17 | 13 | 9 | 78 | PASS |
| 4 | E — Who funds the words? *(mine)* | 25 | 20 | 14 | 9 | 9 | 77 | PASS |
| 5 | A — Same classifier, different label column | 21 | 17 | 11 | 6 | **15** | 70 | PASS (barely — see note) |
| 6 | C — Escalation in translation | 23 | 20 | 10 | 4 | 11 | 68 | PASS |

**Recommendation: build D.** It is the only candidate where novelty and feasibility point the same direction, and the data is already on disk.

---

## 2. Why the losers lost

### C — Escalation in translation. **Kill it.**
The casualty/blame variant is already published: **Steinert & Kazenwadel, *Journal of Peace Research* 62(4):1128–1143, 2025** — 34±11% lower fatality estimates when queried in the attacker's language, Hebrew/Arabic and Turkish/Kurdish, public code on Zenodo. That is your variant, in the field's flagship journal.

The remaining wedge — cross-lingual wargaming — sits inside a cross-lingual-safety literature so saturated it now has its own **systematic literature review** (arXiv:2608.14626), and the adjacent result is already out (arXiv:2508.00032: Arabic and Vietnamese defect more in multi-agent strategic games). Worse, the confound is unfixable at 2,500 characters: any difference you find could be operator-language bias (interesting) or degraded non-English instruction-following on Rivera's constrained action menu (boring). You would need back-translation controls and a placebo task and have no room to show them.

### A — Same classifier, different label column. **Wounded badly.** Two independent kills:

1. **The measurement is done, at far larger scale, twice.** Kim, Zhang & Jurgens (EMNLP 2025 Main) — 36 languages, 4.5M authors, per-language results published. **AuthBench (arXiv:2609.06771) — released 6 Sept 2026, four days ago** — 10 languages, 428k documents, 153k authors, explicitly reporting "large performance differences across languages."
2. **The protective half's hypothesis is contradicted by the one existing multilingual obfuscation benchmark.** Macko et al., Findings of EMNLP 2024 — 10 obfuscation methods × 37 detectors × 11 languages, ~740k texts — found obfuscation evades detection in *all* tested languages. Your "protection gap" hero figure is a figure of a thing that probably isn't there.

And I verified the data bottleneck twice, independently: **Project Gutenberg has zero Turkish books and zero Hindi books** (both `/browse/languages/` paths 404); Russian has 9 total, Japanese 22. Turkish Wikisource returned **0 pages in the Author namespace**. Spanish/Russian/Chinese/Japanese are fine; Hindi and Turkish are not obtainable cleanly today.

What survives is the *framing* — nobody has run one interpretable pipeline over both label columns and shown the two curves side by side. That is a position-paper contribution wearing an experiment's clothes. Given 2,500 characters and a venue that already accepts position papers freely, it's a real option but it is not what "tuff" means.

*Ethics note:* A passes the gate only because the corpora are public-domain literature. The moment it touches pseudonymous real users it fails. Also, per your own rule and the CFP, we would publish aggregates only and release no trained attribution model.

### F and E (my two additions) — worth knowing, not worth doing now

**F — Benchmark-to-battlefield.** Papers are one transfer vector; **datasets and benchmarks** are the more damning one, because a dataset is infrastructure. Trace which NLP *resources* (LDC corpora, CoNLL, SQuAD, CommonVoice, VoxCeleb) appear in military/surveillance patents. Genuinely untouched. Scored 78 — but resource-citation tracing is much messier than paper-citation tracing (no clean ID space), and I can't de-risk it by the 17th.

**E — Who funds the words?** Longitudinal military funding acknowledgments across 25 years of ACL Anthology, by subfield. Directly answers what five accepted essays only asserted. But Wu (NLP+CSS 2022) already analyzed ACL acknowledgments generally, so novelty caps around 9/15. **Best use: this is B's upstream half, not a standalone.**

---

## 3. THE PICK — D: "Can LLMs read a peace agreement?"

### Thesis sentence
> Frontier LLMs extract peace-agreement provisions far less reliably from the agreements of the conflicts that produced the most of them — and the error is systematic by region, not random — so the first computational reading of the peace-process record would encode the same asymmetries the record was built to correct.

### Data — access verified, in hand
I downloaded both files anonymously, no key, no registration, in under a minute. They are sitting in this repo.

| File | Verified | Contents |
|---|---|---|
| `pax_coded.csv` | **3.6 MB, 2,257 rows × 279 cols** | PA-X v10 expert codings |
| `pax_corpus.csv` | **26.8 MB, 2,257 rows × 29 cols** | full agreement texts, last column `Agreement text` |

- Coded CSV: `https://www.peaceagreements.org/cms/documents/3957/pax_data_2257_agreements_v10.csv`
- Full text (undocumented export): `https://www.peaceagreements.org/agreements/search-results/?export=corpus`
- **Years 1990–2025.** Text lengths: min 295, median 4,209, max 859,016 chars.
- License **CC BY-NC-SA 4.0**. Cite Bell & Badanjak, *JPR* 56(3):452–466, 2019.

**Regional distribution — this is the equity axis, and every cell has usable n:**

| Region | n |
|---|---|
| Africa (excl. MENA) | 749 |
| Europe and Eurasia | 434 |
| Asia and Pacific | 420 |
| Americas | 308 |
| Middle East and North Africa | 301 |
| Cross-regional | 45 |

**Candidate gold provisions** (verified nonzero rates, ordinal 0–3 or binary):
`Ce` ceasefire 1038 · `Med` mediation 572 · `GeWom` women/gender 494 · `ImUN` UN role 478 · `Pol` political participation 451 · `GCh` children 404 · `TjAm` amnesty 250 · `TjMech` transitional-justice mechanism 154.

### Hero figure
**Heatmap + marginal.** Rows = 8 provision types. Columns = 5 regions. Cell = macro-F1 of the best model against PA-X expert gold, bootstrap 95% CI. A right-hand marginal strip gives each region's mean F1 with CI, sorted; a top strip gives each provision's mean.

- **x-axis:** region (Africa, Asia-Pacific, MENA, Americas, Europe/Eurasia)
- **y-axis:** provision type (ceasefire, amnesty, gender, UN role, political participation, children, TJ mechanism, mediation)
- **colour:** F1, diverging around the majority-class baseline so "worse than guessing" is visually unmistakable
- **The claim the figure makes:** the Africa column is systematically paler than the Europe column at matched provision and matched agreement length.

Second panel if it earns space: F1 vs. PA-X's own rhetorical(1)/substantive(3) distinction, showing models collapse the two — i.e. they cannot tell a promise from a commitment.

### The one experiment that proves the claim
Stratified sample of agreements balanced on **region × agreement length × stage**, scored on the 8 crisply-grounded provisions above, across 4 pinned models (one frontier closed, one frontier open, one small open, one cheap) with a majority-class baseline and a TF-IDF+logreg baseline. Claim is proved if the region coefficient survives controlling for text length and provision base rate, with bootstrap CIs and a length-matched subsample ablation.

### Estimated cost
MVP (100 agreements × 2 models) ≈ **$3–5**. Full run: ~500 agreements × ~8k tokens × 4 models ≈ 16M input tokens, blended ≈ **$25–35**. Within the $50 budget but **over your $10 single-run rule — I will ask before the full run.** Caching every call by hash of model+prompt+params, so re-runs are free.

### Biggest risk, and the fallback
**Risk: label validity.** Those 279 columns are expert *judgments*. The ordinal scale is literally 0=none / 1=rhetorical / 2=anti-discrimination / 3=substantive — a model disagreeing with a PA-X coder is not necessarily wrong, and "whose agreements get misread" may partly measure **PA-X's own coder drift across regions and eras**, which is confounded with exactly the variable I want to claim.

**Fallback, and it is a good one:** scope to provisions with crisp textual grounding and binarize (present/absent), which removes most of the judgment. Then have you two hand-label 150–200 items from the disagreement set; I report **Cohen's κ** against PA-X. If κ is high, PA-X is the gold standard and the models are wrong. **If κ is low, that is itself the paper** — "the expert record is less consistent than it looks, and any LLM benchmark built on it inherits that" is a *better* AI-for-Peace result than the one we set out to get. Either branch ships.

**Second risk:** the multilingual arm. All 2,257 corpus texts are **English translations** by Edinburgh; there is no language column. Originals exist as separate per-agreement PDFs (verified on agreement 920, Colombia/EPL 1990: one English translation, one Spanish original) and `robots.txt` permits `/agreements/` and `/media/`. That is a few hours of polite crawling. **Treat the multilingual arm as a stretch goal, not a dependency** — the English benchmark alone is the paper.

### Day-by-day
| Day | Work |
|---|---|
| **Thu 11** | Repo scaffold, `CLAUDE.md`/`LOG.md`/`CLAIMS.md`, analysis plan written into `LOG.md` *before* any scoring. Provision selection + rubric drafting from the v10 codebook |
| **Fri 12** | **MVP: hero figure end-to-end on 100 agreements, 2 models.** Caching layer, cost logging. (48h MVP rule met) |
| **Sat 13** | I build the hand-label sheet. Scale to the full stratified sample. Baselines (majority, TF-IDF) |
| **Sun 14** | **You two label 150–200 items** (~90 min each). Bootstrap CIs, length-matched ablation |
| **Mon 15** | κ computed, error analysis, second panel. Start the PDF crawl for the multilingual stretch |
| **Tue 16** | Static explorer for GitHub Pages + QR. Ethics/responsible-release paragraph |
| **Wed 17** | Buffer. Results frozen |
| Thu 18–Sun 20 | Per your timeline: draft, review, submit |

---

## 4. THE RUNNER-UP — B: "The language surveillance pipeline"

### Thesis sentence
> Kalluri et al. showed computer-vision research flows into surveillance patents; the same pipeline run over 25 years of the ACL Anthology shows which NLP subfields feed which surveillance applications — and speaker identification, which nobody has ever traced, is the densest path.

### Hero figure
Sankey: **left** = NLP subfields (speaker ID, authorship attribution, MT, sentiment/"threat detection", IE, ASR) → **right** = patent application classes (biometric identification, border/immigration, policing, content moderation, military C2), ribbon width = citing-patent count, colour = assignee sector.

### Data — verified hands-on
- **Reliance on Science v65**, Zenodo `10.5281/zenodo.21493744`, `pcs_oa_uspto.csv` **1,437.6 MB**, CC BY-NC-4.0. I range-downloaded the first 300 KB: header is **`reftype,confscore,oaid,patent,wherefound`** — **OpenAlex-keyed, not MAG.** Rows like `app,10,3066,us-10494607-b2,frontonly`. USPTO-only, grant years 2015–2025.
- **v64**, Zenodo `10.5281/zenodo.11461587`, `_pcs_oa.csv` **2,457.4 MB**, worldwide, through 2023. You need v64 for a long trend line; v65 for recency. **You cannot get "1990–2025 worldwide" from either.**
- **ACL Anthology**: 1,000 XML volume files, **76.9 MB total**, on GitHub. Verified `2024.acl.xml` = 1,030 papers, **1,021 with DOIs (99%)**.
- I confirmed OpenAlex MAG coverage collapses after the freeze — 24/25 sampled 2021 works carry a MAG id, **1/25 in 2023** — which is why the OpenAlex-keyed RoS file matters.

### Estimated cost
LLM patent classification is cheap: ~15k patents × ~500 tokens ≈ 7.5M tokens on a small model ≈ **$2–4**. The cost here is engineering time and a GCP account, not API spend.

### The one experiment
Label every citing patent for surveillance/military application with an LLM classifier, validated against 150–200 hand labels with Cohen's κ, then report citing-patent counts by NLP subfield × application class × year, with assignee sector breakdown, against a base-rate control of patents citing non-NLP CS papers.

### Biggest risk, and the fallback
**Risk 1, confirmed by probing: Reliance on Science gives patent IDs only, and our entire contribution lives in the patent *text*.** I tested every unauthenticated route: PatentsView's legacy API and `data.uspto.gov` both returned an identical 20,666-byte non-JSON error page; EPO OPS returns **403** without a key; all four PatentsView bulk S3 TSVs return **403** (the March 2026 USPTO migration). **The only unauthenticated route that worked was scraping Google Patents HTML at ~1.6 MB per patent** — which did correctly yield title and assignees, but is ToS-shaky and slow across thousands of documents. Real fallback: a free `data.uspto.gov` API key, or GCP BigQuery (needs a billing account even for the free tier). **This is a 1–2 day unknown and it is why B is not the pick.**

**Risk 2, and it is a novelty problem you must not walk into:** **Yu Zhang, ACL 2025 Short Papers, pp. 488–494 (arXiv:2505.16061)** already built stages 1–3 — ACL Anthology → OpenAlex → Reliance on Science, 24,821 papers, 21,104 mapped (85%), **20,218 patent→paper links** — he just never asked what the patents were *for*. **Never write "we are the first to link NLP papers to patents." It is false and it is the first thing a reviewer finds.** The honest framing is: prior work measured *whether* NLP reaches patents; we ask *what those patents do*. Note also that our delta over Kalluri is the **LLM classifier replacing her hand-built keyword list** (Appendix F.1) — defensible, but modest.

**Risk 3, the one that should actually worry you:** **Noa Garcia is the workshop's General Chair, and she co-authored "The Weaponization of Computer Vision" (FAccT 2026, arXiv:2604.07803)**, which traces CV's military-surveillance ties via conference sponsorship. She will know this literature better than any reviewer we could draw. That is a strong fit signal — and it means every claim must be exact.

---

## 5. What I need from you

1. **Pick D, B, or something else.** My recommendation is D, clearly.
2. **Can you both actually be in Paris Dec 12–13, self-funded?** The form gates on it. If no, this is a different project.
3. **Confirm the code paths.** LangLLM is at `Claude Code/LangLLM` (full 840-response dataset, RQ1–RQ5 results present). CompLLM is not a working repo on disk — only `Downloads/compllm-final.zip`. Both are cited as prior work either way; neither is load-bearing for D.
4. **Rotate the OpenRouter key.** `LangLLM/.env` held a bare key with no `OPENROUTER_API_KEY=` prefix and a BOM, so `load_dotenv()` would never have set it — the pipeline would have failed on its first call. I repaired the format, but reading the file echoed the value into the session transcript. `.env` is gitignored and was never committed. Roll it at openrouter.ai/keys and paste the new one into the same file.
5. **Note:** `OPENROUTER_API_KEY` is **not** set in this environment, contrary to the brief. I read from `LangLLM/.env`.

**I have not built anything and will not until you pick.**

---

## Appendix — verified citations

Every one of these was opened; IDs checked against the arXiv API where noted.

- Kalluri, Agnew, Cheng, Owens, Soldaini & Birhane. *The Surveillance AI Pipeline.* arXiv:2309.15084. **Journal version retitled** "Computer-vision research powers surveillance technology," ***Nature*, 2025**, DOI 10.1038/s41586-025-08972-6. Cite the retitled version.
- Khlaaf, West & Whittaker. *Mind the Gap: Foundation Models and the Covert Proliferation of Military Intelligence, Surveillance, and Targeting.* arXiv:2410.14831.
- Bell & Badanjak. *Introducing PA-X.* *JPR* 56(3):452–466, 2019.
- Zhang, Yu. *Internal and External Impacts of Natural Language Processing Papers.* ACL 2025 Short, 488–494. arXiv:2505.16061.
- Garcia & Katirai. *The Weaponization of Computer Vision.* FAccT 2026, DOI 10.1145/3805689.3806535. arXiv:2604.07803.
- Widder, Gururaja & Suchman. *Basic Research, Lethal Effects: Military AI Research Funding as Enlistment.* arXiv:2411.17840. Journal version DOI 10.1177/20539517261458301 — **verify the journal name by hand**, SAGE 403s to fetchers.
- Rivera, Mukobi, Reuel, Lamparth, Smith & Schneider. *Escalation Risks from Language Models in Military and Diplomatic Decision-Making.* FAccT '24, DOI 10.1145/3630106.3658942. arXiv:2401.03408. Code: github.com/jprivera44/EscalAItion.
- Steinert & Kazenwadel. *How user language affects conflict fatality estimates in ChatGPT.* *JPR* 62(4):1128–1143, 2025. DOI 10.1177/00223433241279381.
- Kim, Zhang & Jurgens. *Leveraging Multilingual Training for Authorship Representation.* EMNLP 2025 Main. arXiv:2509.16531.
- Huang, Zhang & Cardie. *AuthBench.* arXiv:2609.06771 (6 Sept 2026).
- Macko et al. *Authorship Obfuscation in Multilingual Machine-Generated Text Detection.* Findings of EMNLP 2024, 6348–6368. arXiv:2401.07867.
- Narayanan et al. *On the Feasibility of Internet-Scale Author Identification.* IEEE S&P 2012, 300–314. DOI 10.1109/SP.2012.46. **Seven authors, not "et al. 2012" alone.**
- Brennan, Afroz & Greenstadt. *Adversarial Stylometry.* ACM TISSEC 15(3), Art. 12, 2012. DOI 10.1145/2382448.2382450.
- **Correction to the brief:** arXiv:2602.16800 is *Large-scale online deanonymization with LLMs* by Lermen, Paleka, **Swanson, Aerni**, Carlini & Tramèr. Your citation drops two authors. Confirmed twice against the raw arXiv API.

**Flagged for re-verification before anything is cited in the abstract:** the AuthBench language list and the Macko 11-language list were read via model-summarized page fetches, not the PDFs. I will open both PDFs directly during Phase 3.
