"""Record the representative-sample results and the data-description correction.

Appends to LOG.md and CLAIMS.md, and corrects the Reliance on Science note in
paper/refs.bib. Idempotent via markers.

    python tools/append_2026_09_12c.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOG_MARKER = "## 2026-09-12 (Sat, night) — representative samples, era matching, final numbers"
LOG_ENTRY = """

## 2026-09-12 (Sat, night) — representative samples, era matching, final numbers

### Random-order refetch finished
Treatment: the seed-42 sample of 2,500 is fully fetched. 2,374 classified; 125 are
pre-grant application publications and 1 is a fetch failure. Control: 2,241 of 2,500
classified; 257 are application publications. `tools/check_abstract.py` confirms the
classified treatment sample now matches the population: 27.2% granted before mid-2018,
against 26.0% of all 9,048. The primary `results/patent_labels.csv` holds the seed-42
sample only; the full fetch is kept as `patent_labels_all_fetched.csv`.

### Two data facts that were wrong
- **Every 404 is a pre-grant application publication** (treatment 125 of 125, control
  257 of 257). The text source serves granted patents only, so the classified sets are
  granted patents. Application publications are 487 of the 9,048 treatment records (5.4%)
  and 257 of the 2,500 control sample.
- **Reliance on Science v65 is not limited to 2015–2025 grants.** The treatment
  population includes 17% granted 1976–2014, and the control sample includes patents
  granted before 1976. The earlier description, repeated in CLAUDE.md, BRIEF and refs.bib,
  was false and is corrected.

### Grant era confounds the arm comparison
Surveillance-classified patents are recent. NLP-citing patents are recent (58% granted
May 2021 or later) while science-citing patents skew old (44% granted 1976–2014, 4%
before 1976). `src/compare_arms.py` stratifies by era:

| era | NLP-citing | science-citing |
|---|---|---|
| 1976–2014 | 0 / 417 | 2 / 1,110 |
| 2015 – May 2021 | 3 / 634 (0.47%) | 2 / 616 (0.32%) |
| May 2021+ | 8 / 1,322 (0.61%) | 2 / 386 (0.52%) |

- treatment 11 / 2,374 = **0.46%** [0.25, 0.80]; control crude 6 / 2,241 = 0.27%
- control reweighted to the treatment era mix: **0.41%**
- **Mantel–Haenszel pooled OR 1.03 [0.38, 2.78], p = 0.95**; common-window Fisher p = 0.47

The crude gap was grant era. `analysis.py` still prints a crude risk ratio (2.11), now
labelled era-confounded; report `compare_arms.py` instead.

### Other results on the representative sample
- H1: **0 of 10** subfields significant under Fisher exact + Benjamini–Hochberg (min q 0.83).
- H2: 0.00% (2015–17, n=194), 0.83% (2018–20), 0.66% (2021–23), 0.47% (2024–26). No trend.
- In-text ablation: 0 of 292, CI [0, 0.86] — still includes the overall rate; not support.
- Military: 1 of 2,374 treatment vs 6 of 2,241 control; military labels are highly
  assignee-sensitive (below), so treat with care.
- Surveillance owners: Microsoft 2, ETS 2, HRL, Conduent, IBM, PayPal, ClearCare, Discord,
  Zignal Labs. The HRL civil-unrest patent is still labelled surveillance.

### Applicant-name bias runs in both directions
`src/redaction_test.py` on the representative labels, 99 patents targeted:
- redacted re-call reproduces the primary label 99 / 99 (deterministic)
- **10 of 31 non-neutral labels flip (32%)**; 17 of 99 overall; 8 of 71 defence-sounding
- 7 flagged-with-name became neutral when hidden, 6 of them military: defence-sounding
  applicants inflate military labels
- 9 neutral-with-name became flagged when hidden: large consumer-technology and healthcare
  names suppress flags
The earlier "4 of 16 (25%), over-labelling" came from the truncated set and is replaced.

### Examiner classes: reworded, not yet validated
69 patents sit in surveillance-related IPC classes: 2 surveillance, 3 dual-use, 64
neither. Of the 64, 46 carry G10L17 and 29 have voice- or digital-assistant titles —
nearly half, not "most". Examiners assign technology classes and never judged these to be
surveillance; the finding is that using those classes as a surveillance proxy overcounts.
Not human-validated.

### Gold set
Built before the sampling fix, so its 200 items skew toward 2018–2023 grants. The labels
for those items are unchanged (cached, deterministic). It remains valid for measuring
agreement and is not used for population rates.

**Spend:** under $1.50.
"""

CLAIMS_MARKER = "## FINAL STATUS — 2026-09-12 (night): representative samples"
CLAIMS_ENTRY = """

---

## FINAL STATUS — 2026-09-12 (night): representative samples

Supersedes every conflicting row above. Treatment = seed-42 random sample; control =
uniform sample; both assignee-redacted; granted patents only. Checked against the results
files by `tools/verify_brief.py`.

| # | Claim | Value | Script | Results | Status |
|---|---|---|---|---|---|
| C5 | Surveillance share, NLP-citing patents | **11 / 2,374 = 0.46%** [0.25, 0.80] | `compare_arms.py` | `compare_arms.json` | ✅ |
| C7 | Era-matched treatment vs control | **MH OR 1.03 [0.38, 2.78], p = 0.95**; control reweighted 0.41% | `compare_arms.py` | `compare_arms.json` | ✅ bound, not null |
| C7x | Crude control comparison | 0.27%, RR 2.11 | `analysis.py` | `analysis.json` | ❌ era-confounded, never quote |
| C6c | H1 by subfield | 0 of 10, BH q < 0.05 | `analysis.py` | `analysis.json` | ✅ |
| C8 | H2 by grant year | no trend | `analysis.py` | `analysis.json` | ✅ |
| C13 | In-text ablation | 0 / 292 [0, 0.86] | `analysis.py` | `analysis.json` | ⚠️ not support |
| C14 | Examiner classes | 69 patents: 2 surveillance, 3 dual-use, 64 neither | `analysis.py` | `analysis.json` | 🟡 pending human validation |
| C15 | Applicant-name bias | **10 / 31 non-neutral flip (32%)**, both directions | `redaction_test.py` | `redaction_test.csv` | ✅ |
| C16 | ACL-citing share of RoS records | 9,048 / 2,748,170 = 0.33% | `build_control.py` | `control_meta.json` | ✅ |
| C17 | Record types, treatment population | 8,553 granted, 487 application publications, 8 other | `compare_arms.py` | `compare_arms.json` | ✅ |
| C11/C12 | Human agreement | pending coding, Sun 13 Sept | `agreement.py` | `agreement.json` | ⬜ |

**Withdrawn:** 0.69%, 1.02%, 0.81% (truncated samples); control 0.27% with RR 1.95 or 2.11
(crude); 4 of 16 flips (truncated); 21 of 26 examiner-class (truncated); "2015–2025 grants"
(false); positive control 6/7; redaction 0/60; in-text ablation as support.
"""

BIB_OLD = "USPTO-only, grant years 2015--2025,"
BIB_NEW = ("USPTO records spanning patents granted before 1976 through 2025 plus pre-grant "
           "application publications (measured in our samples; an earlier note limiting it to "
           "2015--2025 grants was wrong),")


def append(path: Path, marker: str, entry: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"{path.name}: already present, skipped")
        return
    path.write_text(text.rstrip("\n") + entry, encoding="utf-8")
    print(f"{path.name}: appended")


def main() -> None:
    append(ROOT / "LOG.md", LOG_MARKER, LOG_ENTRY)
    append(ROOT / "CLAIMS.md", CLAIMS_MARKER, CLAIMS_ENTRY)
    bib = ROOT / "paper" / "refs.bib"
    b = bib.read_text(encoding="utf-8")
    if BIB_OLD in b:
        bib.write_text(b.replace(BIB_OLD, BIB_NEW), encoding="utf-8")
        print("refs.bib: Reliance on Science note corrected")
    elif "an earlier note limiting it" in b:
        print("refs.bib: already corrected")
    else:
        print("refs.bib: WARNING - expected text not found; correct the Marx and Fuegi note by hand")


if __name__ == "__main__":
    main()
