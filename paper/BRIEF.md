# EARSHOT — everything needed to write the abstract

- **For:** Adrian Erlikhman — **updated** Saturday 12 September 2026
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

Four numbers maximum. Every number costs a clause of argument.

---

## 2. Where the evidence landed — read this first

The data now points clearly at the framing we committed to before any results
existed. Surveillance-classified patents are **rare** among patents citing NLP
research, are **not distinguishable** from science-citing patents in general at the
sample sizes we have, and show **no concentration in any subfield**. That is not a
failed study. The claim that NLP research feeds surveillance is made constantly, by
critics and defenders alike, on the strength of this kind of evidence — and we can
now say how little the public patent record can actually settle.

The method work is the part that is solid and new, and it is where the abstract
should spend its sentences.

---

## 3. Pipeline numbers — locked

| # | Number | Meaning |
|---|---|---|
| 1 | **127,851** | ACL Anthology papers, 1952–2026 |
| 2 | **69,327** | resolve to OpenAlex |
| 3 | **26,085** | patent-to-paper citation links |
| 4 | **9,048** | distinct USPTO patents citing an ACL paper |
| 5 | **24,829 vs 24,821** | our replication of Zhang vs his own count — eight apart |
| 6 | **0.33%** | ACL-citing patents as a share of all 2,748,170 science-citing patents |
| 7 | **91.6%** | of our links are front-page only (vs 62.3% for patents generally) |

---

## 4. Results — provisional (1,012 treatment, 366 control patents classified)

Assignee-redacted is the primary specification (see section 6).

| Measure | Value |
|---|---|
| Surveillance, ACL-citing patents | **7 of 1,012 = 0.69%** (CI 0.31–1.35%) |
| Military / defence | 0 (CI 0–0.25%) |
| Dual-use / ambiguous | 4 = 0.40% |
| Surveillance, science-citing control | **1 of 366 = 0.27%** (CI 0.03–1.27%) |
| Risk ratio, treatment vs control | 1.95x (CI 0.36–4.34), Fisher p = 0.69 |
| Subfields significant for surveillance | **0 of 10** (Benjamini–Hochberg q < 0.05) |
| Time trend | 0.65% (2018–20) vs 0.73% (2021–23), flat |

**Do not report the treatment-vs-control gap as a finding or as a null.** It is
underpowered: detecting 0.69% vs 0.27% at 80% power needs roughly 4,300 patents per
arm. Report it as a bound.

---

## 5. The three findings you can actually write around

**A. Examiner classes overcount.** Of 26 patents that patent examiners placed in a
surveillance-type classification (speaker identification, biometrics, alarms), our
rubric codes **only 2 as surveillance** — 21 as neither and 3 as dual-use. In a hand
inspection of the 19 such patents from the first classification run, **17 were
consumer voice assistants that recognise their own user** — the phone's owner, not a
watchlist. A method that counts patents by classification code or keyword, as prior
work on computer vision did, would score these as surveillance. This is the concrete
payoff of the authentication-versus-identification distinction.

**B. LLM classifiers read the applicant, not the claim.** When we hid the patent's
assignee, **25% of the model's non-neutral labels changed** (4 of 16). A botulism
antitoxin was called military because its applicant is a military medical academy.
Redacting the assignee fixes this by construction. Anyone using an LLM to classify
patents for this question needs to know it.

**C. The record is thin where it is most cited.** Surveillance-classified patents
are well under 1% of NLP-citing patents, and no subfield stands out. The evidence
the dual-use debate relies on cannot, at present, carry the weight put on it.

One concrete example is worth a clause: **HRL Laboratories' patent for early
detection of civil unrest from social media** remains classified surveillance with
the assignee hidden.

---

## 6. What changed since the last brief — do not reuse old numbers

| Old | Now | Why |
|---|---|---|
| 1.02% surveillance | **0.69%** | applicant-name bias; primary is now assignee-redacted |
| "0 in-text surveillance supports proximity" | **uninformative** | 0 of 89 has an upper bound of 2.78%, above the overall rate |
| authorship flagged significant | **0 of 10 significant** | the flag was a bootstrap artifact; corrected to the pre-registered test |
| redaction test "0 of 60 moved" | **withdrawn** | those patents had benign assignees; the proper test found 25% |
| positive control 6 of 7 | **withdrawn** | its cases came from the rubric the model was given |
| control has more military | **artifact** | 3 military dropped to 1 under redaction |

---

## 7. The two limits — put them early

1. **91.6% of links are front-page citations**, which show prior-art disclosure, not
   use. We measure proximity, not transmission.
2. **Patent abstracts are written to avoid naming an application**, so a low rate
   bounds what the record can show, not what the field does.

---

## 8. What the method paragraph must contain

- **Operator vs subject** — if the person analysed is also the user and beneficiary,
  it is not surveillance.
- **Authentication vs identification** — verifying a claimed identity is not picking
  someone out of a population. Speech patents sit on this line constantly.
- **Assignee redacted** for the model and both human coders.
- **Two coders, the authors**, labelling a stratified sample independently. Disclose
  that they are the authors: agreement is internal consistency, not independent
  validation.
- Report per-class F1 and a prevalence-robust coefficient (Gwet's AC1) alongside
  kappa, since one class dominates.

---

## 9. Sunday 13 September — labelling session

- 200 patents: 32 rare or boundary cases + 168 random `neither`.
- Title and abstract only. **Do not look patents up. Do not open
  `results/patent_labels.csv`** — it holds the model's labels, and it is public, so
  the blind depends on us.
- Only 7 model-surveillance items exist, so the surveillance-F1 check will be
  indicative, not decisive. Say so if it is used.
- Plus Michael's 50-link hand check of the citation data.

---

## 10. Still running or outstanding

- Control metadata fetch (about 430 of 2,500) — rerun the comparison when it lands.
- Speech/speaker-ID arm — waiting on the OpenAlex rate limit.
- Human agreement — Sunday.
- Two citations still to open by hand: Widder et al. and de Rassenfosse et al.

---

## 11. Titles

1. **Proximity, Not Transmission: What the Patent Record Can and Cannot Show About
   NLP's Path Into Surveillance** — recommended now
2. Authentication Is Not Identification: Classifying the Patents That Cite
   Language-Technology Research
3. Earshot: What Are the Patents Citing NLP Research Actually For?

## 12. TL;DR (under 300 characters)

> We linked 127,851 ACL Anthology papers to the patents citing them, then asked what
> those patents are for. The distinction that decides it for speech: verifying a
> claimed identity is not the same as picking someone out of a population.

---

## 13. Citations (verified — see refs.bib)

- **Kalluri et al., Nature 2025** — computer vision to surveillance patents. Cite the
  Nature title, not the arXiv one. Hand-coded 100 papers and 100 patents, then used
  a keyword list.
- **Zhang, ACL 2025** — linked ACL papers to patents first. Never claim to be first;
  we ask what the patents are for.
- **Alcácer, Gittelman and Sampat, Research Policy 2009** — examiner citations.
- **Marx and Fuegi** — Reliance on Science.
- **Srivastava et al., AI for Peace at ICLR 2026** — speech and algorithmic triage;
  in this workshop's own first edition.
- **Garcia and Katirai, FAccT 2026** — the computer-vision version. Noa Garcia chairs
  this workshop.

**Spend so far:** under $0.50 of the $50 budget.
