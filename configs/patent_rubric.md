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
