> **Numbers superseded by paper/BRIEF.md (12 Sept 2026). Do not take figures from this file.**

# Earshot — abstract draft

**Submission format (verified against the live Google Form):** pasted text, no
file upload. Abstract field **2,500 characters max**. Separate TL;DR field **300
characters max**. References count against the 2,500. The hero figure cannot be
submitted — it exists only for the Paris poster.

Every `[bracket]` is a number that does not exist yet. Brackets stay brackets
until the script behind them has run. The claim id in each bracket maps to
`CLAIMS.md`.

---

## TL;DR (300 char limit)

> We linked 127,851 ACL Anthology papers to the patents citing them, then asked
> what those patents are for. The distinction that decides it for speech:
> verifying a claimed identity is not the same as picking someone out of a
> population.

**234 characters.** ✅ fits.

---

## Abstract (2,500 char limit)

> That NLP research is cited by patents is established. Zhang (2025) linked
> 24,821 ACL papers to 20,218 patent citations and ranked subfields by volume.
> What no one has asked is what those patents are for.
>
> We rebuild the linkage at corpus scale: 127,851 ACL Anthology papers,
> 1952–2026, of which 69,327 resolve to OpenAlex, joined against Reliance on
> Science v65. That yields 26,085 citation links to 9,048 distinct patents across
> 5,008 papers. Restricted to Zhang's venues and years our pipeline returns
> 24,829 papers against his 24,821, so the linkage reproduces published work.
>
> The contribution is the classification. Each citing patent is labelled
> surveillance, military, dual-use or neither against a written rubric built on
> two distinctions computer vision never had to make. Operator versus subject:
> where the person analysed is also the user and the beneficiary, it is not
> surveillance. Authentication versus identification: verifying a claimed
> identity is not the same as determining who someone is from a population.
> Speech patents sit on that second line constantly, and which side they fall on
> decides the answer.
>
> [C5 — classified rate with CI, and the subfield ordering it produces]
>
> Validation is human-anchored. Two coders — the authors — label a stratified
> sample independently, blind to the model and to each other, from the inputs the
> model receives. We report the confusion matrix, raw agreement, per-class F1 and
> a prevalence-robust coefficient alongside Cohen's κ, since one class dominates
> and κ alone is uninterpretable under skew. A rule fixed before the run: if
> agreement fails, only hand-labelled counts are reported. [C11/C12]
>
> Two limits are load-bearing and we state them first. 91.6% of these links are
> applicant-added front-page citations, which evidence prior-art disclosure
> rather than use, so we measure proximity and not transmission. And patent
> abstracts are drafted to avoid naming an application, so a low measured rate
> bounds what the public record can show rather than what the field does. That
> bound is the second finding: the citation trail both critics and defenders
> appeal to cannot currently settle the question, and we quantify how far short
> it falls.

**Current length with brackets unfilled: ~1,960 characters.** Leaves ~540 for
the results paragraph. Tight but workable — budget **four numbers maximum**.

---

## Numbers that are locked

Verified, reproducible, safe to use.

| id | value | source |
|---|---|---|
| C1 | 127,851 ACL Anthology papers, 1952–2026 | `src/ingest_acl.py` |
| C3 | 69,327 resolve to OpenAlex (98.9% of DOI-bearing) | `src/join_openalex.py` |
| C4 | 26,085 links · 9,048 patents · 5,008 papers | `src/join_patents.py` |
| — | Zhang replication: 24,829 vs his 24,821 | `src/analysis.py` |
| — | 91.6% front-page-only (vs 62.3% file-wide) | full-file scan |
| C6b | base patent-proximity 20.57% (papers ≤2019) | `src/subfields_acl.py` |

## Numbers that are WITHDRAWN — do not reuse

| withdrawn | why |
|---|---|
| "88.1% of core venues" | `venue_key` bug excluded pre-2020 ACL/EMNLP/NAACL |
| "13.7% vs 7.2%, speech vs text" | 6,000/query cap was mine; truncation is relevance-ordered, so it enriched for highly-cited papers in exactly the inflating direction |
| pooled 7.23% subfield ranking | right-censored; superseded by the ≤2019 specification |
| "positive control 6/7" | circular — cases came from the rubric the model was given |

## Still required before submission

- [ ] **C5** — classification over all 9,048 patents *(blocked on metadata fetch, running)*
- [ ] **C6c** — H1 proper: surveillance rate by subfield *(needs C5)*
- [ ] **C11/C12** — agreement stats *(needs Sunday)*
- [ ] speech arm re-pulled with cursor paging *(OpenAlex rate-limited; retry)*
- [ ] IPC convergent validity *(codes now captured; needs the fetch)*
- [ ] RoS link hand-check, 50 items *(sheet built)*
- [ ] every citation opened and stored in `paper/refs.bib` with URL
- [ ] three title options, two-sentence pitch, poster outline

## Framing decision, fixed in advance

If the classified rate comes back near zero, **that is still the paper**: the
citation trail both sides of this argument appeal to cannot settle it, and we
quantify how far short it falls. Deciding this before the numbers land is the
point of pre-registration — a null must not become a gift to the other side at a
venue whose stated position is that it rejects the normalisation of AI for
surveillance.
