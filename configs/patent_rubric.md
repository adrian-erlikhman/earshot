# Patent classification rubric — v1

**Written 2026-09-11, before any patent was labelled.** Both human coders and the
model see exactly this text. Changes after labelling begins get a new version
number and a note in `LOG.md`; labels are never silently re-cut.

Kalluri et al. classified surveillance patents with a hand-built keyword list
(their Appendix F.1) — a patent counted if it contained one indicator word like
"face" or "security". That is fast and reproducible but it cannot tell a
call-centre voice-authentication patent from a border-control one. Replacing that
keyword list with a judgement made against written criteria is our methodological
delta, so the criteria have to carry real weight.

---

## What you are judging

One patent, from its **title, abstract, and assignee**. Nothing else.

**Code what the patent says it does.** Not what the company is known for, not what
the technology could theoretically enable, not how you feel about the assignee.
A Palantir patent about database indexing is `neither`. A university patent
about crowd re-identification is `surveillance`.

---

## The four labels

### `surveillance`

A system whose described function includes **identifying, tracking, monitoring,
profiling, or extracting information about people** who are not the system's
operator.

The load-bearing test is **operator vs subject**:

- If the person being analysed is the one using the system *and* the beneficiary
  → not surveillance.
- If a third party analyses people who are not the operator → surveillance.

A second distinction that matters constantly in speech patents:

- **Authentication** — a person *claims* an identity and the system checks it
  (unlocking your own phone, logging into your own bank). The subject initiates,
  knows, and benefits. → usually **not** surveillance.
- **Identification** — the system determines *who someone is* from a population,
  or picks a target out of a group. → **surveillance**.

Counts as surveillance:
- speaker identification against a database of enrolled or unenrolled voices
- re-identifying or linking people across recordings, documents, or accounts
- authorship attribution or deanonymisation of writers
- monitoring communications at scale for content, sentiment, or "threat"
- lawful-intercept, wiretap, or call-monitoring systems
- emotion, deception, or intent inference applied to people being assessed
- border, immigration, asylum, or watchlist screening
- workplace or student monitoring where the monitored party is not the operator

### `military_defense`

Explicitly for armed forces, weapons, or defence operations: targeting, command
and control, battlefield or ISR systems, missile or drone guidance, military
logistics, or a stated military/defence application. A defence-contractor
assignee alone is **not** sufficient — the text must say it.

### `dual_use_ambiguous`

The described function would be `surveillance` or `military_defense` in one
plausible deployment and `neither` in another, and the text does not settle it.

Use this when you genuinely cannot tell. **Do not** use it to avoid a hard call
you can actually make. If the text clearly describes a consumer feature, code
`neither` even though any technology could in principle be repurposed.

Typical cases: generic "person detection" with no stated use; speaker
diarisation with no stated application; a "security" system that could be
physical-access or people-monitoring.

### `neither`

Everything else. Machine translation for documents, summarisation, search
ranking, spell-checking, a voice assistant answering its own user, accessibility
captioning, medical transcription, database internals.

---

## Worked edge cases

These are the disagreements we expect. Decide them the same way.

| Patent describes | Label | Why |
|---|---|---|
| Voice assistant recognises which family member is speaking to personalise results | `neither` | Subjects are the operators and the beneficiaries |
| Call-centre system verifies a caller against their enrolled voiceprint | `neither` | Authentication: subject claims an identity, initiates, benefits |
| Call-centre system flags callers matching a fraud voiceprint database | `surveillance` | Identification against a database the subject did not enrol in |
| Transcribing meetings and attributing each utterance to a named participant | `dual_use_ambiguous` | Consent depends entirely on deployment; text will not say |
| Detecting "aggressive" or "suspicious" speech in public spaces | `surveillance` | Third-party assessment of unaware subjects |
| Machine translation of intercepted communications | `surveillance` | The stated application is interception |
| Machine translation, general purpose | `neither` | Code what is described |
| Authorship attribution to detect plagiarism in student work | `surveillance` | Students are subjects, not operators |
| Author identification for literary or historical scholarship | `neither` | Subjects are historical, no living person assessed |
| Content moderation classifier for a platform | `dual_use_ambiguous` | Platform safety and censorship infrastructure are the same mechanism |
| Keyword spotting to wake a device | `neither` | No person is identified |
| Keyword spotting across a communications stream for terms of interest | `surveillance` | Monitoring at scale |
| Drone navigation using natural-language commands | `military_defense` only if text says military; else `dual_use_ambiguous` | Do not infer from "drone" alone |

---

## Precedence

If more than one label fits, take the **first** that applies:

1. `military_defense`
2. `surveillance`
3. `dual_use_ambiguous`
4. `neither`

---

## What each coder records

- `label` — one of the four
- `confidence` — 1 low / 2 medium / 3 high
- `rationale` — one sentence, quoting the words that decided it
- `insufficient_info` — true if the abstract is too truncated or vague to judge
  at all. Code the label anyway with confidence 1, but flag it; if these exceed
  ~10% of the sample that is a finding about the metadata, not about patents.

---

## Rules for coders

- **Code independently.** Do not discuss items while labelling, do not look at
  the model's label, and do not look at each other's.
- Do not look the patent up. Title, abstract, assignee only — the model gets the
  same, and agreement is meaningless if the inputs differ.
- Uncertain is fine. Confidence 1 is information, and a forced confident guess is
  worse than an honest low-confidence one.
- Expect roughly 15–25 minutes per 50 items. If you are much faster than that you
  are probably pattern-matching on assignee.

## How this gets used

Cohen's κ is computed human–human and human–model on the same 200 items.
**If human–model κ < 0.6 the model's labels do not carry any headline number** —
we report the hand-labelled sample with its own confidence intervals and say so
plainly in the abstract. Human–human κ bounds what is achievable: if the two of
you cannot agree, the construct is underspecified and the rubric is what needs
fixing, not the model.

---

# AMENDMENT v1.1 — 2026-09-11, before any gold-set labelling

The v1 rule ("if human–model κ < 0.6 the model's labels carry no headline
number") is **withdrawn**. It would misfire.

**Why.** Cohen's κ is a chance-corrected statistic and chance agreement is
enormous when one class dominates. Simulated, two coders each 95% accurate,
n=200, four labels:

| P(neither) | E[κ] | P(κ ≥ 0.6) | E[AC1] | raw agreement |
|---|---|---|---|---|
| 25% | 0.90 | 100% | 0.90 | 0.93 |
| 70% | 0.86 | 100% | 0.91 | 0.93 |
| 85% | 0.77 | 99.7% | 0.92 | 0.93 |
| **95%** | **0.54** | **29%** | 0.92 | 0.93 |
| 98% | 0.32 | 1.9% | 0.92 | 0.93 |

Raw agreement and AC1 are flat at 0.93/0.92 throughout. Only κ moves. The pilot
suggests `neither` prevalence near 95%, so the v1 gate had roughly a 1-in-4
chance of passing **even with near-perfect coders**. It would have failed the
paper for the shape of the label distribution, not for disagreement.

**The rule that replaces it, fixed now:**

1. **Primary gate — per-class F1 on the `surveillance` class**, human-anchored,
   with the humans as reference. The model's surveillance rate carries a
   headline number only if **surveillance F1 ≥ 0.60** with its bootstrap CI
   reported. `military_defense` reported the same way but not gated (expected n
   is small).
2. **Always reported, never gated:** the full confusion matrix, raw agreement,
   per-class precision/recall/F1, **Gwet's AC1**, and Cohen's κ. κ stays in the
   paper — with its prevalence caveat stated — because omitting a statistic that
   looks bad would be worse than explaining it.
3. **Human–human agreement** reported on the same basis. If the two coders
   disagree, the construct is underspecified and the rubric is what needs fixing.
4. **The 200 are stratified on the model's label**, not drawn at random, so the
   positive class is ~100 rather than ~6. Rates estimated from the stratified
   sample are **reweighted to the population** before any rate is quoted, and the
   stratification is stated wherever the number appears.
5. Requires the classifier to have run over all citing patents first, since that
   is the sampling frame.
6. **If the gate fails**, only hand-labelled counts are reported, with their own
   CIs, and the abstract says so.

**Coder identity is disclosed.** Both coders are the paper's authors. Human–human
agreement therefore measures whether two people applying our own rubric converge
— internal consistency — and **not** whether the construct is valid to outsiders.
That limitation is stated in the paper; we are not claiming independent validation.

---

# AMENDMENT v1.2 — 2026-09-12, before any gold-set labelling

**The assignee is now REDACTED — for the model and for both human coders.**
Judge from **title and abstract only**. This supersedes "title, abstract, and
assignee" in *What you are judging* above.

**Why.** The rubric already said a defence-contractor assignee alone is not
sufficient and the text must say it. The model did not reliably obey that. A
targeted test re-classified 26 patents twice at temperature 0 — assignee shown,
assignee hidden:

- consistency: the unredacted re-call reproduced the original label 26/26
- **4 of 16 non-`neither` labels (25%) changed when the assignee was hidden**
- 2 of 15 patents with a defence-sounding assignee changed

Three of the four flips were over-labels driven by the applicant's name:
a botulism antitoxin (Academy of Military Medical Sciences) `military` → `neither`;
a network-attack simulation (Triad National Security) `military` → `neither`;
a video system (NEC) `surveillance` → `dual_use_ambiguous`. The fourth (Boeing,
object and activity tracking) moved the other way and reflects instability on
genuinely ambiguous text rather than assignee bias.

An earlier test reported 0 of 60 labels moving under redaction. It was
uninformative: those 60 all had benign commercial assignees, so the assignee had
nothing to push against. It is withdrawn as evidence.

**Rule, fixed now:** primary classification is assignee-redacted for every
labeller. The assignee-shown run is retained and reported as a sensitivity
analysis. The true assignee is still recorded in the data for the assignee
concentration analysis — it is only hidden at the moment of judgement.
