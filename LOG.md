# LOG.md — daily progress and API spend

Running total API spend: **$0.00** of $50 budget.
No LLM calls have been made yet.

---

## Pre-registered analysis plan

**Written 2026-09-10, before any scoring or classification was run.** The point
is to fix the hypotheses and decision rules now so that what follows is testing,
not fishing. Deviations get logged below with a reason.

### The object

Two directed flows around one corpus of 127,851 ACL Anthology papers (1952–2026):

- **Upstream (money in):** which papers acknowledge military funders, by subfield and year.
- **Downstream (patents out):** which papers are cited by patents, what those
  patents are for, and who owns them, by subfield and year.

### Subfield assignment

Papers are assigned to subfields by a transparent, auditable rule — title/abstract
keyword rules over a hand-written taxonomy in `configs/subfields.yaml`, **not** an
opaque topic model, so a reviewer can check any assignment. Target subfields,
chosen before looking at outcomes:

`speech_asr`, `speaker_id_voice`, `authorship_attribution`, `machine_translation`,
`sentiment_emotion`, `information_extraction`, `dialogue`, `summarization`,
`question_answering`, `parsing_syntax`, `multimodal_vision_language`, `other`.

Papers may hold multiple labels; all rates are reported per-label with the
multi-label caveat stated.

### Hypotheses

- **H1 (primary).** The share of a subfield's papers cited by surveillance-classified
  patents varies significantly across subfields, and `speaker_id_voice` and
  `authorship_attribution` rank in the top tercile.
  *Directional, pre-specified. This is the paper's claim.*
- **H2.** Surveillance-classified citing patents grow as a share of all citing
  patents over time (mirroring Kalluri et al.'s ~5× finding in computer vision).
- **H3.** Military funding acknowledgment rate varies by subfield, and subfields
  high on H1 are also high on H3 — i.e. the two ends of the pipeline agree.
  *If H3 fails, that is a reportable null and arguably the more interesting result:
  the money and the patents point at different subfields.*

### Decision rules, fixed in advance

- **Primary test for H1:** χ² across subfields on surveillance-citation rate, then
  per-subfield rates with **bootstrap 95% CIs (10,000 resamples, clustered by paper)**.
  H1 is supported only if the CI for `speaker_id_voice` excludes the corpus mean.
- **H2:** logistic regression `is_surveillance ~ grant_year`, patent-clustered SEs.
  Report the odds ratio with CI. We do **not** claim a trend if the CI spans 1.
- **H3:** Spearman ρ between per-subfield military-funding rate and per-subfield
  surveillance-citation rate, n = number of subfields. Reported with CI regardless of sign.
- **Baseline/control (required):** the same surveillance-classification rate over
  patents citing a matched set of **non-NLP computer-science papers**. Without this
  control, any rate we report is uninterpretable — patents in general cite security-adjacent work.
- **Ablation (required):** re-run H1 restricted to `confscore >= 5` and to
  `wherefound == 'in-text'` citations only, to show conclusions are not an artifact
  of weak or front-page-only linkage.
- **Multiple comparisons:** Benjamini–Hochberg across the per-subfield tests, q = 0.05.

### The LLM label, and how it gets validated

An LLM classifies each citing patent (title + abstract + assignee + CPC codes)
into: `surveillance`, `military_defense`, `dual_use_ambiguous`, `neither`,
with a one-sentence rationale and a confidence.

- The rubric is written **before** any labeling and lives in `configs/patent_rubric.md`.
- **Gold set:** a stratified random sample of **200 patents**, labeled independently
  by Adrian and Michael using the same rubric, blind to the model's label.
- Report **Cohen's κ** for human–human and for human–model agreement.
- **Kill rule:** if human–model κ < 0.6, the LLM label does not carry a headline
  number. We fall back to reporting the human-labeled sample only, with its own CIs,
  and say so plainly.
- Kalluri et al. used a keyword list; we additionally report the keyword-list
  result as a comparison so the methodological delta is visible.

### What would falsify the paper

If surveillance-classified patents are not concentrated in any subfield (H1 null),
and the time trend is flat (H2 null), the honest result is: *"NLP's patent
footprint is diffuse; the surveillance concentration found in computer vision does
not replicate in language technology."* **That is a publishable finding at this
venue and we will report it as the headline rather than hunting for a subgroup.**

### Scope discipline

The abstract is capped at 2,500 characters. At most **four numbers** make it in.
Everything else lives on the poster and in the explorer.

---

## 2026-09-10 (Thu) — Phase 1 + scaffold

**Done**
- Verified every venue fact against the source repo and the live Google Form.
  Found three material corrections: submission is pasted text not PDF (2,500 char
  cap), the hero figure cannot be submitted, in-person attendance is gating.
- Read all 16 edition-1 accepted papers. Established that measurement is the
  differentiator (empirical = 19% of acceptances, ~67% of orals) and that
  scientometrics/stylometry/peace-process NLP are all at zero.
- Novelty + feasibility checks on 4 seeds + 2 of my own. `DECISION.md` written.
  Seed C killed (Steinert & Kazenwadel, JPR 2025 already published the variant).
  Seed A badly wounded (AuthBench, released 4 days ago; Macko et al. contradict
  the protective-half hypothesis; Gutenberg has zero Turkish and zero Hindi books).
- Hands-on feasibility (not vibes): range-downloaded the Reliance on Science
  header and confirmed it is **OpenAlex-keyed**; verified ACL Anthology DOI
  coverage; downloaded PA-X in full; confirmed LangLLM's `extract()` runs on all
  7 languages unmodified at $0 API cost.
- **Corrected my own error:** I first reported USPTO/PatentsView as dead. They
  return a byte-identical block page — that is the sandbox's egress filter, not
  USPTO. Logged in `CLAUDE.md`.
- Adrian picked a B-flavoured meld (upstream funding + downstream patents),
  explicitly not another LLM benchmark. Adrian attends Paris solo.
- Scaffolded the repo. **Stage 1 shipped:** `src/ingest_acl.py` →
  **127,851 papers, 1,719 volumes, 1952–2026, 54.8% with DOIs.**
  DOI coverage by era confirms the pre-2015 cliff: 21.3% (1979–99), 12.3% (2000–09),
  14.7% (2010–14), 65.8% (2015–19), 74.6% (2020–26).

**Spend:** $0.00.

**Blocked / needs Adrian**
- Rotate the OpenRouter key (it was echoed into the session transcript; the file
  was also malformed — bare key, no `OPENROUTER_API_KEY=` prefix — so the LangLLM
  pipeline would have failed on its first call. Format repaired).
- `OPENROUTER_API_KEY` is not set in the environment; reading from `LangLLM/.env`.
- Confirm whether `api.patentsview.org` / `bulkdata.uspto.gov` resolve from
  Adrian's own machine. This determines whether stage 4 uses a clean bulk route
  or a polite Google Patents crawl.

**Next**
- Stage 2b: title+year fallback for the no-DOI tail (bulk-pull ACL venue sources,
  match locally). This is now a dependency, not a nicety — see 09-11.
- Stage 3: download Reliance on Science, join on `oaid`.
- Write `configs/subfields.yaml` and `configs/patent_rubric.md` before any labeling.

## 2026-09-11 (Fri) — stage 2 complete

**Done**
- **Stage 2 shipped:** `src/join_openalex.py`. **69,327 of 70,124 DOI-bearing
  papers matched to OpenAlex = 98.9%; 39,006/44,266 core-venue papers = 88.1%**,
  above Zhang 2025's ~85% benchmark. CLAIMS C3 ✅.
- First full run lost 232 consecutive batches (11,600 DOIs) to an OpenAlex
  rate-limit burst around batches 950–1150, silently — the run still "succeeded"
  at 82.4%. The per-batch cache made recovery a free re-run. **Lesson: the script
  reports failed-batch counts for a reason; never read the headline rate without
  checking that line.**
- Per-era match rates now track DOI availability almost exactly (19.3% vs 21.3%
  available in 1979–99; 14.7% vs 14.7% in 2010–14; 74.3% vs 74.6% in 2020–26),
  which confirms the join is saturated: everything joinable by DOI is joined.

**Open issue — stage 2b is now load-bearing.**
58,524 papers have no DOI, concentrated pre-2015. Patents granted 2015–2025 cite
1990s work heavily, and the DARPA-era speech literature is exactly the material
most likely to appear in voice-biometrics patents. Leaving that tail unmatched
would bias H1 *against* our own hypothesis, so this is a correctness issue rather
than a coverage nicety. Plan: bulk-pull the ACL venue sources from OpenAlex by
source-id + year and match on normalised title, rather than one query per paper.

**Spend:** $0.00.

## 2026-09-11 (Fri, later) — Michael's counter-proposal, tested

Michael proposed swapping the whole project for an SBIR/STTR adoption-lag study
(defence vs civilian time-to-adoption of AI methods, plus a Llama-licence case
study). He named the test that would decide it. I ran it.

**Test 1 — does the Llama second result exist? No. Zero.**
Downloaded the full award CSV (`src/fetch_sbir.py`): **367.6 MB** (he estimated
290 MB), **207,731 rows** (he said 219,651), award years **1983–2024 but 2024 has
only 23 rows in the entire file** (he said 1983–2026). Defence 99,253 / four
civilian agencies 96,724, close to his split.

Word-boundary grep over all 99,253 defence abstracts (`src/probe_sbir.py`):
**llama 0, mistral 0**, gpt 6, bert 4, large language model 7, foundation model 2.
His own decision rule was "thousands = two findings, thirty = case study." It is
zero. And independently, the corpus effectively ends in 2023, while Meta's
national-security exception was November 2024 — so there is no post-announcement
data even in principle.

**Test 2 — abstract coverage.** He was right to demand this first, and it is worse
than he feared. Defence abstracts missing: **2000: 96.2%, 1999: 78.8%**, and
24–40% missing across 1983–1996. 2001–2020 is clean (<1%).

**Test 3 — does the lag design have data at all?** (`src/probe_sbir2.py`)
Only for ~4 pre-2018 families. `deep learning` is genuinely clean and points the
right way (defence 5th mention 2013 vs civilian 2015; 100th 2019 vs 2020).
Everything post-2018 is single digits.

**But naive keyword dating is badly contaminated, worse than the order-statistic
problem Michael flagged.** My probe dates `generative adversarial` to 1990 and
`bert` to 1994 (actual: 2014 and 2018); `GloVe` matches *gloves*; `transformer`
matches electrical transformers to 1984; `CNN` matches the news network. False
positives dominate exactly at small k, which is precisely the quantity the
time-to-k-th-mention estimator headlines.

**Verdict: do not swap.** His critique of the current project is largely right,
but the replacement is in worse shape and we would have found that out on day 3.

**Adopted from his email regardless:**
1. **Applicant-only citations become the headline number.** Examiner citations
   only mean a patent office employee judged our paper relevant prior art. RoS
   ships `reftype` (observed value `app`), so this is a filter, not a rebuild.
   Pulling the count now rather than on day 8. This is the best point in his email.
2. **Cut to speech / speaker ID.** We cannot match a six-person hand-coding effort.
3. **Upstream half demotes to a framing paragraph**, positioned against Wu 2022
   explicitly, not co-headlined.

**Own-error note:** the `raw` column in `probe_sbir.py` is meaningless for
multi-word terms — it tests only the first token, so "large language model" scored
14,582 on the word *large*. The `boundary` and `strict` columns are regex-correct
and are the ones quoted above.

**Spend:** $0.00.

## 2026-09-11 (Fri, evening) — patents joined; hypothesis broke then recovered

**C4 landed.** `src/join_patents.py` scanned all 34,825,379 RoS citation rows:
**26,085 links, 9,048 distinct patents, 5,008 distinct ACL papers (7.2% of the
matched corpus).** Comparable in shape to Kalluri's ~23k patents from 19k CV papers.

**reftype is degenerate, and that is fine.** Verified on our own copy across
25.9M rows: `app` 99.997%, `exm` 0.003%, no `unk`. RoS v65 ships effectively
applicant-only. So Michael's examiner-inflation objection does not apply to this
file — but we must SAY the file is pre-filtered, not imply we filtered it.
`wherefound` on our subset is 91.6% frontonly, so the in-text ablation retains
only ~8% — weaker than the 42% the full file suggested. Report that honestly.

**H1 broke.** Speaker ID in the ACL corpus: **1 paper, 1 patent.** Speaker
identification publishes at Interspeech/ICASSP, not ACL. The pre-registered
directional prediction named a subfield that is essentially absent from the
corpus we built. My error, caught by testing rather than by assuming.
What IS in the ACL data: dialogue/QA 1,537 patents, parsing 1,223, MT 1,198.

**H1 recovered on the right corpus.** `src/probe_speaker_id.py` pulled 16,686
speaker-ID/speech works from OpenAlex irrespective of venue and joined them to
RoS: **17,565 links, 7,071 distinct patents, 2,284 distinct papers, 13.7% of
works cited by >=1 patent** vs 7.2% for ACL. Speech is ~2x more patent-proximate
than text NLP — the predicted direction, on the corpus that actually contains
the subfield.

**Design change, for the better.** The paper becomes a TWO-ARM comparison, text
NLP vs speech, measured identically. That is a stronger design than ACL-only and
it converts today's error into the study's control arm.

**Caveats that must not be lost:**
- The 6,000-per-query cap makes 16,686 a floor, not a census.
- Search terms pulled in general speech processing (spectral subtraction, PLP)
  alongside speaker ID proper. These must be separated before any claim.
- 13.7% vs 7.2% is NOT yet matched on era or venue type (journals vs
  conferences). Unmatched, it is not publishable.

**Spend:** $0.00.
