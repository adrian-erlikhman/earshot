# EARSHOT — everything needed to write the abstract

- **For:** Adrian Erlikhman — **prepared** 12 September 2026
- **Venue:** AI for Peace workshop @ NeurIPS 2026, Paris, 12–13 December
- **Deadline:** Mon 21 Sept AoE = **Tue 22 Sept, 05:00 Pacific**
- **Repo:** https://github.com/adrian-erlikhman/earshot (public)

---

## 1. The container you are writing into

| | |
|---|---|
| Submission mechanism | **Google Form. Pasted text. No file upload.** |
| Abstract field | **2,500 characters max** (~380 words). References count against it. |
| TL;DR field | **300 characters max**, separate |
| Figures | **Cannot be submitted.** The hero figure exists only for the Paris poster. |
| Review | Single-blind |
| Work status | Published, novel, and in-progress all accepted |
| Attendance | Gating question on the form; no travel funding. Adrian attends, presents solo. |

**Budget your characters.** At 2,500 you get roughly: 2 sentences of setup,
3 of method, 2 of results, 2 of limits. **Four numbers maximum.** Every number
you add costs a clause of argument.

---

## 2. The one-sentence version

> We linked 127,851 NLP papers to the 9,048 patents citing them and classified
> what those patents are for — and the honest finding is both a number and a
> limit on what the number can mean.

---

## 3. Numbers that are LOCKED — safe to use

Each has a script and a results file behind it in `CLAIMS.md`.

| # | Number | Detail |
|---|---|---|
| 1 | **127,851** | ACL Anthology papers ingested, 1,719 volumes, 1952–2026 |
| 2 | **69,327** | resolve to OpenAlex — 98.9% of all DOI-bearing papers |
| 3 | **26,085** | patent→paper citation links |
| 4 | **9,048** | distinct USPTO patents citing ≥1 ACL paper |
| 5 | **5,008** | distinct ACL papers cited by ≥1 patent |
| 6 | **24,829 vs 24,821** | our Zhang replication vs Zhang's own count — **eight apart** |
| 7 | **91.6%** | of our links are front-page-only (vs **62.3%** file-wide) |
| 8 | **99.998%** | of all 34.8M citation rows are applicant-added, not examiner |
| 9 | **2,748,170** | distinct patents in RoS v65 — so ACL-citing patents are **0.33%** of all science-citing patents |
| 10 | **1.02%** | **of NLP-citing patents classified `surveillance`** — 10 of 978, CI **[0.53%, 1.81%]** |
| 11 | **0.2%** | classified `dual_use_ambiguous`; **98.8%** `neither` |

### The replication is your credibility anchor

Restricted to Zhang's venues and years, our pipeline returns **24,829 papers
against his 24,821**. Say this in the abstract. It is one clause and it
pre-empts the obvious reviewer question about whether our numbers can be trusted.

---

## 4. Numbers that are WITHDRAWN — do not use

| Withdrawn | Why |
|---|---|
| "88.1% of core venues" | `venue_key` bug excluded every pre-2020 ACL/EMNLP/NAACL paper |
| "13.7% vs 7.2%" speech vs text | a 6,000-per-query cap in my own code; truncation is relevance-ordered, so it enriched for heavily-cited papers in exactly the inflating direction |
| pooled 7.23% subfield ranking | right-censored — recent papers cannot yet have been cited |
| "positive control 6/7" | circular; cases came from the rubric the model was handed |

---

## 5. The headline result, and what it actually supports

**1.02% of NLP-citing patents are classified `surveillance`** (10/978, CI
[0.53%, 1.81%]). That is a **low** rate, and the low rate is the story.

### The ten, because they are the evidence

| Assignee | Patent |
|---|---|
| **HRL Laboratories** (defense lab) | Social media mining for **early detection of civil unrest events** |
| Microsoft | Intelligent assistant — determines identity and tracks a person in an environment |
| Microsoft | Computationally-efficient **human-identifying** smart assistant |
| Microsoft | **Entity-tracking** computing system, across sensors |
| NEC Corporation | Video system for environments with "safety concerns" |
| NEC Labs America | Video camera system predicting future events |
| Conduent | Neural networks for **target identification from text**, incl. hate speech |
| IBM | Neural mapping — monitors and compares neural activity between users |
| Educational Testing Service | Detecting **plagiarized spoken responses** |
| Arizona Board of Regents | Fake-news detection via user embeddings |

These are not false positives. A defense laboratory doing civil-unrest
prediction from social media is precisely the transition the workshop's call
describes. **Consider naming HRL in the abstract** — one concrete instance does
more rhetorical work than a percentage.

---

## 6. THE MISSING EXPERIMENT — now running

Michael was right that something was missing, and it is in our own
pre-registered plan:

> **Baseline/control (required):** the same surveillance-classification rate
> over patents citing a matched set of non-NLP papers. **Without this control,
> any rate we report is uninterpretable** — patents in general cite
> security-adjacent work.

**Do not write the results sentence until this lands.** "1.02% of NLP-citing
patents are surveillance" is meaningless alone. If science-citing patents in
general are also ~1%, we have no finding. If they are 0.2%, we have a 5×
enrichment and a real result.

**Status:** 2,500 control patents sampled uniformly from the 2,739,122 that cite
science but cite no ACL paper. Same file, same grant-year window, same
classifier, same rubric — only the field of the cited science differs. Metadata
fetching now, ~75 minutes, then classification (~$0.35).

**Caveat to state:** this is "the average science-citing USPTO patent," **not**
a field-matched control. A non-NLP-computer-science arm would be stronger and
needs OpenAlex subject queries we have not run. List as a limitation.

---

## 7. THE POWER PROBLEM — read before drafting

At a 1.02% base rate, detecting a difference against the control needs:

| If the control rate is | n needed per arm |
|---|---|
| 0.05% | 885 ✅ |
| 0.10% | 1,029 ✅ |
| 0.20% | 1,409 ⚠️ |
| 0.50% | 4,343 ❌ |

2,500 per arm covers a control rate down to ~0.25%. **If the control comes back
near 0.5%, the comparison will be underpowered and we must say so rather than
report a non-significant difference as if it were a null.**

**Consequence for H1.** With **10** surveillance patents in the treatment arm,
the pre-registered subfield ordering cannot be tested. Even classifying all
9,048 yields only ~92 surveillance cases across ten subfields. **H1 is
underpowered and should not be claimed.** Do not put a subfield ranking in the
abstract; say the distribution is reported and that cell sizes preclude
per-subfield inference.

---

## 8. The two limits — these are load-bearing, put them early

1. **91.6% of our links are applicant-added front-page citations.** These
   evidence prior-art disclosure, not demonstrated use. We measure **proximity,
   not transmission**. Note this is *worse* for us than patents generally, where
   front-page-only is 62.3% — NLP citations are unusually disclosure-shaped.
2. **Patent abstracts are drafted to avoid naming an application.** So a low
   measured rate bounds *what the public record can show*, not what the field
   does.

**Limit 2 is the second finding, and at a 1% rate it may be the primary one:**
the citation trail that both critics and defenders of this research appeal to
cannot currently settle the question, and we quantify how far short it falls.

---

## 9. The framing decision — fixed in advance, do not revisit

If the control shows no enrichment, **that is still the paper.** The finding
becomes: the public patent record cannot settle whether NLP research feeds
surveillance, and here is the measured size of that gap.

This was decided before the numbers existed. It matters because at a venue whose
first line rejects the normalisation of AI for surveillance, a null presented
badly reads as exoneration. Presented as a measurement of evidentiary
insufficiency, it is a contribution.

---

## 10. What the method paragraph must contain

Non-negotiable, because these are the contribution:

- **Operator vs subject** — where the person analysed is also the user and the
  beneficiary, it is not surveillance.
- **Authentication vs identification** — verifying a claimed identity is not
  determining who someone is from a population.

These two distinctions are why this is not Kalluri's keyword list. A
call-centre voiceprint verification and a fraud-database voice match are the
same technology on opposite sides of the line. **Speech patents sit on that line
constantly.**

Also mention: **two human coders, the authors**, labelling a stratified sample
independently, blind to the model and to each other, from the same inputs the
model receives. Disclose that the coders are the authors — human–human agreement
is internal consistency, not independent validation.

---

## 11. Reliability reporting — say it this way

Cohen's κ alone is **uninterpretable** here. At 95% prevalence of one class, two
coders each 95% accurate score κ≈0.54 while raw agreement stays at 0.93.
Verified by simulation; the pre-registered κ gate was withdrawn on 11 Sept,
before any labelling.

Report: confusion matrix, raw agreement, **per-class F1 on `surveillance` (the
gate, threshold 0.60)**, **Gwet's AC1**, and κ with its caveat. One clause in
the abstract: *"we report per-class F1 and a prevalence-robust coefficient
alongside κ, since one class dominates."*

---

## 12. Still outstanding

- [ ] **Control classification** — running. **Blocks the results sentence.**
- [ ] Gold set + agreement stats — Sunday, both coders
- [ ] Michael's 50 RoS link hand-check — sheet built
- [ ] Speech arm re-pull with cursor paging — OpenAlex rate-limited
- [ ] IPC convergent validity — codes captured, needs the fetch
- [ ] Open the two `RECHECK` citations in `refs.bib` (Widder et al., de Rassenfosse)

---

## 13. Titles

1. **Authentication Is Not Identification: Classifying the Patents That Cite
   Language-Technology Research** ← recommended
2. Proximity, Not Transmission: What the Patent Record Can and Cannot Show About
   NLP's Path Into Surveillance ← use if the rate is low / control is null
3. Earshot: What Are the Patents Citing NLP Research Actually For?

## 14. TL;DR (278 of 300 chars — fits)

> We linked 127,851 ACL Anthology papers to the patents citing them, then asked
> what those patents are for. The distinction that decides it for speech:
> verifying a claimed identity is not the same as picking someone out of a
> population.

---

## 15. Citations to use (all verified — see `refs.bib`)

- **Kalluri et al., *Nature* 2025** — the template. CV papers → surveillance
  patents. **Retitled from the arXiv preprint; cite the Nature title.** They
  hand-coded 100 papers + 100 patents and scaled with a 30-keyword lexicon —
  *not* 19,000 by hand. Our bar is lower than it looks.
- **Zhang, ACL 2025 Short 488–494** — linked ACL papers to patents already.
  **Never claim to be first.** Correct framing: prior work measured *whether*
  NLP reaches patents; we ask *what those patents do*.
- **Alcácer, Gittelman & Sampat, *Research Policy* 2009** — examiner citations.
  Cite the table figures, not the abstract.
- **Marx & Fuegi** — Reliance on Science v65.
- **Srivastava et al., AI for Peace @ ICLR 2026** — "From Speech Recognition to
  Algorithmic Triage." Accepted at this workshop's own first edition. Cite it.
- **Garcia & Katirai, FAccT 2026** — the CV version via conference sponsorship.
  **Noa Garcia is this workshop's General Chair.** Every adjacent claim must be exact.

---

## 16. Spend

**$0.14** of $50. Control classification adds ~$0.35.
