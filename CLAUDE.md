# CLAUDE.md — AI for Peace @ NeurIPS 2026

Project brief, decisions, and commands. Keep current so a fresh session picks up cold.

## What this is

Submission to the **AI for Peace workshop @ NeurIPS 2026** (2nd edition, Paris, Dec 12 or 13).
Team: **Adrian Erlikhman** (presenting author, attending in person) and **Michael Tarekegn**.

**Working title:** *Money In, Patents Out: tracing the language-technology pipeline from military funding to surveillance patents.*

**One-sentence thesis (working):** The AI-for-Peace community argues that basic
NLP research flows into military and surveillance use; we measure both ends of
that flow across 127,851 ACL Anthology papers — which subfields take military
funding, and which subfields' papers are cited by surveillance patents — and
find the densest, least-examined path runs through speech and speaker identification.

## Hard constraints (verified from source, 2026-09-10)

- **Submission is a Google Form with pasted text. There is NO file upload.**
  - Abstract field: **2,500 characters max** (~380 words). References count against it.
  - Separate TL;DR field: **300 characters max**.
  - **The hero figure cannot be submitted.** It exists only for the Paris poster.
- Deadline **Mon 21 Sept AoE = Tue 22 Sept 05:00 Pacific**. Decisions Sept 29.
- Single-blind. Poster / talk / both; every accepted piece is postered.
- Published, novel, and in-progress work all accepted.
- In-person attendance is a gating form question; they most probably cannot fund travel.
- Form URL is in `src/data/site.ts` of `aiforpeaceworkshop/aiforpeaceworkshop.github.io`.
- **We never submit, email, or post anything. Adrian and Michael do that.**

## Why this topic (Phase 1 outcome)

See `DECISION.md` for the full ranked comparison of six candidates. Short version:

- Edition 1 accepted 16 papers: ~7 position essays, 4 sociotechnical analyses,
  2 conceptual frameworks, **only 3 empirical**. 13 of 16 had no artifact.
  But **2 of the 3 clear orals were empirical audits.** Measurement is the differentiator.
- **Zero** edition-1 papers did scientometrics, citation tracing, or patent
  analysis — while at least five argued *rhetorically* about research flowing
  into military use without measuring a single citation, patent, or funding link.
- Adrian chose a B-flavoured meld over the benchmark-shaped option (D), to stay
  distinct from CompLLM/LangLLM.

## Claims we must NOT make

- ❌ "We are the first to link NLP papers to patents." **False.** Yu Zhang,
  ACL 2025 Short, pp. 488–494 (arXiv:2505.16061) built ACL→OpenAlex→Reliance-on-Science
  already: 24,821 papers, 21,104 mapped (85%), 20,218 patent→paper links. He just
  never asked what the patents were *for*.
- ✅ Correct framing: *prior work measured whether NLP reaches patents; we ask what those patents do.*
- Our delta over Kalluri et al. is an **LLM classifier replacing their hand-built
  keyword list** (their Appendix F.1), plus the speech/speaker-ID arm nobody has traced.
- **Noa Garcia, the workshop's General Chair, co-authored the computer-vision
  equivalent** (Garcia & Katirai, FAccT 2026, arXiv:2604.07803). She will know this
  literature better than any reviewer. Every claim must be exact.

## Ethics position

- Public data only. No PII. No deanonymization of real people.
- We **do not** build, optimize, or release any surveillance or attribution
  capability. We publish **aggregates only**, plus the classification rubric.
- The critical frame is mandatory, not decorative: the CFP explicitly rejects
  defense-oriented work without one, and rejects normalizing military/surveillance AI.
- Patent records are public documents about institutions, not individuals. We
  report **assignee organizations**, never named inventors.

## Data sources (all verified by download, 2026-09-10)

| Source | Access | Verified |
|---|---|---|
| ACL Anthology XML | `codeload.github.com/acl-org/acl-anthology/tar.gz/refs/heads/master` | **58.1 MB, 1,719 volumes, 127,851 papers, 1952–2026** |
| OpenAlex API | `api.openalex.org`, no key, polite pool via `mailto` | works; MAG ids collapse after 2021 (24/25 in 2021 → 1/25 in 2023) |
| Reliance on Science v65 | Zenodo `10.5281/zenodo.21493744`, `pcs_oa_uspto.csv` | **1,437.6 MB**, CC BY-NC-4.0, header `reftype,confscore,oaid,patent,wherefound` — **OpenAlex-keyed**, USPTO-only, 2015–2025 |
| Reliance on Science v64 | Zenodo `10.5281/zenodo.11461587`, `_pcs_oa.csv` | **2,457.4 MB**, worldwide, through 2023 |
| PA-X v10 (unused, kept) | `peaceagreements.org` | 2,257 agreements × 279 cols + 26.8 MB full text |

### Known environment gotcha

`api.patentsview.org`, `data.uspto.gov`, `bulkdata.uspto.gov` and
`search.patentsview.org` are **intercepted or DNS-blocked inside the Claude Code
sandbox** — the first two return a byte-identical 20,666-byte page (md5 `eaac942805`),
which is an egress block page, *not* a USPTO error. These may work fine from
Adrian's own machine. `patents.google.com` HTML **does** work from the sandbox
(~1.6 MB/patent, yields title + assignees).

## Commands

```bash
pip install -r requirements.txt

python -m src.ingest_acl                 # stage 1: Anthology -> data/interim/acl_papers.csv
python -m src.ingest_acl --limit 20      #          smoke test
```

Later stages land here as they are written (`src/join_openalex.py`,
`src/fetch_ros.py`, `src/classify_patents.py`, `src/funding.py`, `src/figures.py`).

## Conventions

- Every LLM call cached by hash of `model + prompt + params`; model IDs pinned; cost logged.
- Every number in the abstract maps to a script and a results file in `CLAIMS.md`.
- Every citation verified by opening the arXiv/DOI page; stored in `paper/refs.bib` with URL.
  **Never cite from memory.** Two citation errors were already found in the original brief
  (see `DECISION.md` appendix).
- Bootstrap 95% CIs, chance/majority baselines, ≥1 ablation, null results reported straight.
- Raw data is gitignored; `data/interim/` is regenerable from `src/`.

### Sampling gotcha (2026-09-12)

Never fetch patent metadata in sorted-id order and stop partway. As strings,
"US10..." sorts before "US9...", so a partial run silently drops whole grant years —
this made both classified arms unrepresentative. Fetch order is now randomized.
Before quoting any classified rate, check the grant-year mix of the classified set
against the population with `tools/check_abstract.py`.
