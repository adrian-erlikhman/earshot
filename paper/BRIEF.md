# EARSHOT — everything needed to write the abstract

- **For:** Adrian Erlikhman — **final numbers**, Saturday 12 September 2026
- **Venue:** AI for Peace workshop @ NeurIPS 2026, Paris, 12–13 December
- **Deadline:** Mon 21 Sept AoE = **Tue 22 Sept, 05:00 Pacific**
- **Repo:** https://github.com/adrian-erlikhman/earshot (public)

---

## 1. The container you are writing into

| | |
|---|---|
| Submission | **Google Form. Pasted text. No file upload.** |
| Abstract field | **2,500 characters max.** References count against it. |
| TL;DR field | **300 characters max**, separate |
| Figures | **Cannot be submitted.** Poster only. |
| Review | Single-blind |
| Attendance | Gating on the form; no travel funding. Adrian presents. |

---

## 2. Where the evidence landed — read this first

Surveillance-classified patents are **rare** among patents citing NLP research, and
once you compare like with like — patents granted in the same era — they are **not
distinguishable** from patents citing science in general. No NLP subfield stands out,
and there is no time trend. The earlier treatment-versus-control gap was produced by
grant era, not by NLP.

So the paper is about what the patent record can and cannot show — the framing we fixed
before any results existed — plus three method findings that anyone doing this kind of
analysis needs.

**Every number in this brief comes from a random sample and has been checked against
the results files by `tools/verify_brief.py`.** Numbers in earlier briefs came from a
sample truncated by grant date and are withdrawn (section 7).

---

## 3. Pipeline numbers — locked

| # | Number | Meaning |
|---|---|---|
| 1 | **127,851** | ACL Anthology papers, 1952–2026 |
| 2 | **69,327** | resolve to OpenAlex |
| 3 | **26,085** | patent-to-paper citation links |
| 4 | **9,048** | distinct USPTO records citing an ACL paper (8,553 granted patents, 487 pre-grant application publications, 8 other) |
| 5 | **24,829 vs 24,821** | our replication of Zhang's core-venue paper count — eight apart |
| 6 | **0.33%** | ACL-citing records as a share of the 2,748,170 science-citing records in Reliance on Science v65 |
| 7 | **91.6%** | of our citation links are front-page only (62.3% across all patents) |

**Correction.** Earlier material said v65 covers only 2015–2025 grants. That is wrong:
it includes patents granted before 1976 and pre-grant application publications.

---

## 4. Results — random samples, assignee hidden

**Treatment:** 2,500 drawn at random from the 9,048; **2,374 classified**. The other 126
are pre-grant application publications (125), which the text source does not serve, plus
1 fetch failure. **Control:** 2,500 drawn uniformly from records citing science but no ACL
paper; 2,241 classified.

| Measure | Value |
|---|---|
| Surveillance, NLP-citing patents | **11 of 2,374 = 0.46%** (95% CI 0.25–0.80%) |
| Dual-use / ambiguous | 3 = 0.13% |
| Military / defence | 1 = 0.04% |
| Surveillance, science-citing control (crude) | 6 of 2,241 = 0.27% |
| Control reweighted to the treatment's grant-era mix | **0.41%** |
| **Era-matched odds ratio (Mantel–Haenszel)** | **1.03 (95% CI 0.38–2.78), p = 0.95** |
| NLP subfields significant for surveillance | **0 of 10** (Benjamini–Hochberg q < 0.05) |
| By grant year | 0.00% (2015–17), 0.83% (2018–20), 0.66% (2021–23), 0.47% (2024–26) — no trend |

### Why era matching is necessary

| Grant era | NLP-citing | Science-citing |
|---|---|---|
| 1976–2014 | 0 of 417 | 2 of 1,110 |
| 2015 – May 2021 | 3 of 634 (0.47%) | 2 of 616 (0.32%) |
| May 2021 onward | 8 of 1,322 (0.61%) | 2 of 386 (0.52%) |

Surveillance-classified patents are recent. NLP-citing patents are recent: 58% were
granted May 2021 or later, against 26% of science-citing patents. A crude comparison
mostly measures that difference. **Never quote the crude ratio.**

The interval 0.38–2.78 is the honest bound: we cannot rule out a rate up to about 2.8
times higher, or well below. Say "not distinguishable", not "the same".

---

## 5. The three method findings — the heart of the abstract

**A. Applicant names sway LLM labels, in both directions.** We re-classified 99 patents
with the assignee shown and hidden (every non-neutral label plus every defence-sounding
applicant). **10 of 31 non-neutral labels (32%) changed.** Defence-sounding applicants
pulled labels toward military: 6 of the 7 labels that dropped to neutral when the name was
hidden had been military (a botulism antitoxin from a military medical academy was the
clearest). In the other direction, 9 patents called neutral with the applicant visible
were flagged once it was hidden, among them patents from large consumer-technology and
healthcare firms. The model is deterministic: the redacted re-call reproduced 99 of 99
labels. Hiding the assignee fixes this by construction.

**B. Technology classes are a poor proxy for surveillance.** Of **69** patents that
examiners placed in surveillance-related technology classes (speaker recognition,
biometrics, alarms, access control, CCTV), the rubric codes **2 as surveillance**, 3 as
dual-use and **64 as neither**. Nearly half of those 64 are voice or digital assistants.
The main class, G10L17, is speaker recognition, and one of its subgroups covers
interactive voice interfaces — so class-based or keyword-based counting, the approach
used in the computer-vision work, would sweep these in. Examiners never judged these
patents to be surveillance; the overcount is in using their classes as a proxy.
**Not yet human-validated — the gold set tests exactly these boundary cases.**

**C. The record is thin where it is most cited.** Under half of one percent, no subfield
concentration, no trend, and no detectable difference from science-citing patents of the
same era. The evidence the dual-use debate leans on cannot carry the weight put on it.

One concrete example is worth a clause if space allows: **HRL Laboratories' patent for
early detection of civil unrest from social media** is classified surveillance with the
assignee hidden.

---

## 6. The limits — put them early

1. **91.6% of links are front-page citations**, which show prior-art disclosure, not use.
   We measure proximity, not transmission.
2. **Patent abstracts often omit the application**, so a low rate bounds what the record
   can show, not what the field does.
3. **Granted patents only.** Pre-grant application publications (about 5% of NLP-citing
   records) could not be retrieved.
4. **Power.** With 11 events the comparison is a bound. The interval is the result.

---

## 7. Withdrawn — do not reuse any of these

| Withdrawn | Why |
|---|---|
| 0.69%, 1.02%, 0.81% surveillance | truncated-by-grant-date samples (fetched in sorted id order) |
| control 0.27% and risk ratio 1.95 or 2.11 | crude, era-confounded |
| "25% of labels flip, over-labelling" | computed on the truncated set; now 32%, both directions |
| "21 of 26 examiner-class patents" | truncated set; now 64 of 69 |
| "2015–2025 grants" | false description of the data |
| positive control 6 of 7; redaction 0 of 60 | circular; uninformative |
| in-text ablation as support | 0 of 292, upper bound 0.86%, above the overall rate |

---

## 8. What the method paragraph must contain

- **Operator vs subject** and **authentication vs identification**.
- **Assignee hidden** from the model and both human coders.
- **Two coders, the authors**; agreement is internal consistency, not independent
  validation.
- Per-class F1 and Gwet's AC1 alongside kappa, since one class dominates.

---

## 9. Sunday 13 September — labelling session

- 200 patents, title and abstract only. **Do not look patents up. Do not open
  `results/patent_labels.csv`** — it is public and holds the model's labels.
- The sheet was built before the sampling fix, so its items skew toward 2018–2023 grants.
  That is fine for measuring agreement; it is not used for population rates.
- **Your coding is not blind on the surveillance items** — you have seen the model's
  labels for several. Michael's labels are the reference for those.

---

## 10. Titles

1. **Proximity, Not Transmission: What the Patent Record Can and Cannot Show About NLP and
   Surveillance** — recommended
2. Authentication Is Not Identification: Classifying the Patents That Cite
   Language-Technology Research
3. Earshot: What Are the Patents Citing NLP Research Actually For?

## 11. TL;DR (checked against the 300-character limit)

> Earshot links 127,851 ACL papers to the 9,048 USPTO patents citing them and classifies
> what those patents do. Surveillance is rare (0.46%) and not detectably more common than
> in science-citing patents of the same era; applicant names sway LLM labels.

---

## 12. Draft abstract (checked against the 2,500-character limit)

Only the agreement numbers are pending (Sunday).

> Kalluri et al. (2025) traced computer-vision research into surveillance patents. Whether
> language technology follows the same path is often asserted but rarely measured, and
> patent citations are easy to overread. We ask what the public patent record can reliably
> show. Earshot links 127,851 ACL Anthology papers through OpenAlex to the 9,048 USPTO
> patents that cite them, matching Zhang's (2025) paper count for the core venues (24,829
> vs. 24,821), and classifies what those patents do. 91.6% of these citations appear only
> on a patent's front page. Our rubric separates a system's operator from its subject, and
> authentication from identification: verifying a claimed identity is not surveillance,
> while picking a person out of a population can be. Assignee names are hidden from the
> model and from two human coders (the authors); revealing them changed 32% of the model's
> non-neutral labels, in both directions. Of 69 patents examiners placed in
> surveillance-related technology classes, the rubric codes 2 as surveillance; nearly half
> of the rest are voice assistants. Coders agree with the model at [surveillance F1 = x;
> AC1 = y] on a stratified sample. In a random sample of 2,374 granted citing patents, 0.46%
> (95% CI 0.25–0.80%) are classified as surveillance, no subfield stands out, and the rate
> is not distinguishable from science-citing patents of the same grant era (odds ratio 1.03,
> 95% CI 0.38–2.78). These results do not establish whether NLP flows into surveillance:
> patent abstracts often omit application detail, and citations show proximity, not
> transmission. Earshot shows how dual-use pathways can be studied without mistaking
> technical similarity, applicant identity, or citation for evidence of deployment.

---

## 13. Citations (verified — see refs.bib)

- **Kalluri et al., Nature 2025** — computer vision to surveillance patents. Cite the
  Nature title. Hand-coded 100 papers and 100 patents, then used a keyword list.
- **Zhang, ACL 2025** — linked ACL papers to patents first. Never claim to be first.
- **Alcácer, Gittelman and Sampat, Research Policy 2009** — examiner citations.
- **Marx and Fuegi** — Reliance on Science.
- **Srivastava et al., AI for Peace at ICLR 2026** — in this workshop's own first edition.
- **Garcia and Katirai, FAccT 2026** — the computer-vision version. Noa Garcia chairs this
  workshop.

**Spend so far:** under $1.50 of the $50 budget.
