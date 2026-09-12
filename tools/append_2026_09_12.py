"""Append the 2026-09-12 entries to LOG.md and CLAIMS.md.

Held as Python strings so no shell quoting is involved — a markdown heredoc full of
apostrophes and backticks failed to parse in bash. Idempotent: each block carries a
marker and is skipped if already present.

    python tools/append_2026_09_12.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOG_MARKER = "## 2026-09-12 (Sat) — control experiment, a classifier bias, and the null becomes primary"
CLAIMS_MARKER = "## CURRENT STATUS — 2026-09-12"

LOG_ENTRY = """

## 2026-09-12 (Sat) — control experiment, a classifier bias, and the null becomes primary

### The missing experiment was the control arm
The pre-registered plan made a baseline mandatory ("without this control, any rate
we report is uninterpretable") and it had not been built. `src/build_control.py`
draws patents uniformly over DISTINCT patents (not citation rows) that cite science
but cite no ACL paper: 2,500 from a pool of 2,739,122. RoS v65 holds 2,748,170
distinct patents, so ACL-citing patents are 9,048 / 2,748,170 = **0.33%** of all
science-citing patents. Metadata fetch running in its own cache (`control_meta`).

### Interval bug (fixed)
Bootstrap intervals on zero-event cells collapse to [0, 0], which "excludes" any
positive base rate. That put six spurious `***` marks on the H1 table. `boot_ci` now
returns exact Jeffreys intervals for binary data. Rare events are the whole regime
here, so this was not cosmetic.

### Retraction: the in-text ablation proves nothing
Zero surveillance patents among in-text citations looked like strong support for
"proximity, not transmission". With exact intervals it is 0/89, CI [0, 2.78%] — the
upper bound exceeds the overall rate. At under 1% you expect under one event in 89.
Not reportable as support.

### IPC disagreement mostly validates the rubric
Inspected the 19 patents (first, assignee-shown run) that sit in a surveillance-type
IPC class but were coded `neither`: 17 are consumer assistants that recognise their
own user (Apple voice trigger, user-specific acoustic models, Intel speaker
enrolment, Google and Disney dialogue systems). Operator = subject = beneficiary, so
`neither` is correct under the rubric. An examiner class cannot draw the
authentication/identification line; the rubric can. A class- or keyword-based method
would count these as surveillance. Two cases are genuinely borderline
(speaker-discriminative feature training; an emotion classifier) and match the known
conservative bias.

### A real classifier failure: applicant-name bias
A control patent for a botulism antitoxin was labelled `military_defense` because its
assignee is the Academy of Military Medical Sciences — which the rubric forbids.
The earlier redaction test (0 of 60 flips) was uninformative: those 60 had benign
commercial assignees, so the assignee had nothing to push against. Withdrawn.

`src/redaction_test.py` targets the cases where bias would show: every non-`neither`
label plus every defence/security-sounding assignee, both arms, classified twice at
temperature 0.
- consistency: unredacted re-call reproduced the original label **26/26**
- **4 of 16 non-`neither` labels (25%) flipped** when the assignee was hidden
- 2 of 15 defence-sounding assignees flipped
- 3 of 4 flips were applicant-driven over-labels (botulism antitoxin; Triad
  network-attack simulation; NEC video); 1 (Boeing) was instability on ambiguous text

**Rubric v1.2:** assignee redacted for the model AND both coders. Both arms were
re-classified redacted; that is now the primary specification. Assignee-shown labels
are retained as `*_assignee_shown.csv` for sensitivity.

### Results, assignee-redacted primary (PROVISIONAL: 1,012 treatment, 366 control)
| | value |
|---|---|
| surveillance, ACL-citing | **7 / 1,012 = 0.69%** [0.31, 1.35] |
| military_defense | 0 [0, 0.25] |
| dual_use_ambiguous | 4 = 0.40% [0.13, 0.94] |
| control, science-citing | **1 / 366 = 0.27%** [0.03, 1.27] |
| risk ratio | 1.95x [0.36, 4.34], Fisher p = 0.69 |
| H2, 2018-20 vs 2021-23 | 0.65% vs 0.73%, overlapping |
| IPC convergent validity | F1 0.121; of 26 surveillance-class patents: 2 surveillance, 3 dual-use, 21 neither |
| surveillance owners | Microsoft 2, HRL, Conduent, IBM, ETS, ClearCare |

Redaction lowered treatment surveillance from 10 to 7 and control military from 3 to 1.
The earlier "control has more military than treatment" note was an assignee artifact.

### H1 test corrected to the pre-registered specification
The table used "CI excludes base". The plan specifies per-subfield tests with
Benjamini-Hochberg. Replaced with Fisher exact (subfield vs rest of corpus) + BH:
**0 of 10 subfields significant.** The one flag (authorship, 1 event in 106) has
p = 0.093, q = 0.93. H1 is not supported, and is underpowered to test.

### Power
At 0.69% vs 0.27%, 80% power needs roughly 4,200 patents per arm. We have 1,012
and 366. The comparison is a bound, not a null, and must be written that way.

### Gold set built (due today)
`src/build_goldset.py` rewritten for v1.2. Only 7 model-surveillance items exist, so
the sheet enriches with boundary cases — `neither` patents in a surveillance-type IPC
class, exactly where model and examiner disagree. 200 items: 32 rare/boundary
(7 surveillance, 4 dual-use, 21 boundary) + 168 random `neither`. Per-stratum
inclusion weights in `strata.json`; `agreement.py` now reweights by stratum. With 7
positives the surveillance-F1 gate is indicative, not decisive.

**Blinding.** The per-item answer key is now gitignored and was never committed. But
`results/patent_labels.csv` is public and contains the model's label for every gold
item, so the blind is honor-system. Both coders are authors; this is disclosed.

### Housekeeping
- Stale speech outputs from a run capped at 200 works per query were quarantined as
  `STALE_capped200_*`. OpenAlex `sample` pages only with `page=`, not `cursor=`; 0.7s
  spacing drew 429s, now 1.6s. A watcher relaunches the speech arm when OpenAlex clears.
- A long bash heredoc of markdown failed to parse (quote handling); log and brief
  writes now go through Python or the file-write tool.
- Date correction: the labelling session is **Sunday 13 Sept**, not the 14th.

### Status
The pre-committed framing now leads: surveillance-classified patents are rare among
NLP-citing patents, are not distinguishable from science-citing patents at this
power, and show no subfield concentration — while the method work (authentication vs
identification; class-based overcounting; applicant-name bias) is solid.

**Spend:** under $0.50.
"""

CLAIMS_ENTRY = """

---

## CURRENT STATUS — 2026-09-12 (supersedes conflicting rows above)

Primary specification is **assignee-redacted** (rubric v1.2). All classified rates are
**provisional**: 1,012 treatment and 366 control patents classified.

| # | Claim | Value | Script | Results | Status |
|---|---|---|---|---|---|
| C5 | Surveillance share, ACL-citing patents | **7/1,012 = 0.69%** [0.31, 1.35] | `classify_patents.py --redact-assignee`, `analysis.py` | `patent_labels.csv`, `analysis.json` | 🟡 provisional |
| C5s | Same, assignee shown (sensitivity) | 10/978 = 1.02% [0.53, 1.81] | `classify_patents.py` | `patent_labels_assignee_shown.csv` | sensitivity only |
| C7 | Control: science-citing, no ACL | **1/366 = 0.27%** [0.03, 1.27]; RR 1.95x [0.36, 4.34]; p = 0.69 | `build_control.py`, `analysis.py` | `control_labels.csv` | 🟡 underpowered |
| C16 | ACL-citing share of science-citing patents | 9,048 / 2,748,170 = **0.33%** | `build_control.py` | `control_meta.json` | ✅ |
| C6c | H1: surveillance rate by subfield | **0 of 10** significant, BH q < 0.05; min p = 0.093 (1 event) | `analysis.py` | `analysis.json` | ✅ null, underpowered |
| C8 | H2: time trend | 0.65% -> 0.73%, overlapping CIs | `analysis.py` | `analysis.json` | 🟡 |
| C13 | In-text-citation ablation | 0/89, CI [0, 2.78] | `analysis.py` | `analysis.json` | ⚠️ uninformative, not support |
| C14 | IPC convergent validity | F1 0.121; of 26 surveillance-class patents, 21 coded `neither` | `analysis.py` | `analysis.json` | ✅ class-based methods overcount |
| C15 | Applicant-name bias in LLM labels | **4 of 16** non-`neither` labels (25%) flip under redaction | `redaction_test.py` | `redaction_test.csv` | ✅ |
| C11/C12 | Human agreement | pending coding, Sun 13 Sept | `agreement.py` | `agreement.json` | ⬜ |

**Withdrawn:** positive control 6/7 (circular); redaction test 0/60 (uninformative);
H1 `***` flags (bootstrap artifact); in-text ablation as support; 1.02% as headline
(assignee-biased).
"""

HEADER_EDITS = [
    ("Running total API spend: **$0.00** of $50 budget.",
     "Running total API spend: **under $0.50** of $50 budget (as of 2026-09-12)."),
    ("No LLM calls have been made yet.",
     "LLM classification in use since 2026-09-11; per-run costs are in the dated entries."),
]


def main() -> None:
    log = ROOT / "LOG.md"
    s = log.read_text(encoding="utf-8")
    for old, new in HEADER_EDITS:
        if old in s:
            s = s.replace(old, new)
            print(f"LOG header: replaced {old[:40]!r}")
    if LOG_MARKER in s:
        print("LOG entry already present — skipped")
    else:
        s = s.rstrip("\n") + LOG_ENTRY
        print("LOG entry appended")
    log.write_text(s, encoding="utf-8")

    claims = ROOT / "CLAIMS.md"
    c = claims.read_text(encoding="utf-8")
    if CLAIMS_MARKER in c:
        print("CLAIMS status already present — skipped")
    else:
        claims.write_text(c.rstrip("\n") + CLAIMS_ENTRY, encoding="utf-8")
        print("CLAIMS status appended")


if __name__ == "__main__":
    main()
