"""Record the grant-date sampling bias found while checking the abstract draft.

Appends to LOG.md, CLAIMS.md and CLAUDE.md. Idempotent via markers.

    python tools/append_2026_09_12b.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOG_MARKER = "## 2026-09-12 (Sat, later) — sampling bias in both classified arms"
LOG_ENTRY = """

## 2026-09-12 (Sat, later) — sampling bias in both classified arms

`tools/check_abstract.py`, run against the draft abstract, found that neither
classified sample was representative.

**Cause.** Patent metadata was fetched in sorted patent-id order, and the runs were
stopped partway. As strings, "US10..." and "US11..." sort before "US9...", so a
partial run silently drops whole grant years.

**Treatment arm.** 0.0% of the 1,012 classified patents have a number below
10,000,000 (granted before about June 2018), against 26.0% of all 9,048 citing
patents. Classified grant years run 2018–2023 only; 2015–2017 and 2024–2025 are
absent. 145 of the 1,012 came from earlier sorted-order fetches rather than the
seed-42 random draw. Within the seed-42 subset alone: 7 of 867 = 0.81%, and that
subset is still date-truncated for the same reason.

**Control arm.** 0.3% of the 366 classified control patents are pre-2018, against
62.5% of the 2,500 sampled. The treatment-versus-control comparison was comparing two
date-truncated slices with different truncation points.

**Consequence.**
- 0.69% is not an estimate for the 9,048. At most it describes patents granted
  mid-2018 to 2023. Withdrawn as a population figure.
- The control comparison (0.27%, risk ratio 1.95, p = 0.69) is withdrawn outright.
- H1 (0 of 10 subfields), the IPC result (2 of 26) and H2 were computed on the same
  truncated labels and must be rerun.
- The redaction result (4 of 16 flips) is a within-patent comparison, so the
  finding holds in kind, though it was drawn from the truncated set.

**Fix.** `fetch_patent_meta.py` now submits patents in random order (seed + 1), so any
partial run is a random subset. The sorted-order control fetch was stopped. Both arms
restarted in random order, one connection at a time: treatment first (the seed-42
sample of 2,500, reusing cache), then control (2,500).

**Also from the abstract review.** "Keyword-like proxies" was never tested; only
examiner IPC classes were. "Systematically overcount" rests on 26 examiner-class
patents whose labels are not yet human-validated. Both need to come out of the draft
or be tested.
"""

CLAIMS_MARKER = "## STATUS UPDATE — 2026-09-12 (later): grant-date sampling bias"
CLAIMS_ENTRY = """

---

## STATUS UPDATE — 2026-09-12 (later): grant-date sampling bias

Both classified arms were fetched in sorted patent-id order and stopped partway, which
truncated them by grant date. See LOG.md. Until random-order fetches finish:

| # | Claim | Status |
|---|---|---|
| C5 | 0.69% surveillance | ❌ **withdrawn as a population estimate** — classified set is grants mid-2018 to 2023 only. Seed-42 subset 7/867 = 0.81%, also truncated |
| C7 | control comparison | ❌ **withdrawn** — classified control is 0.3% pre-2018 vs 62.5% in its sample |
| C6c | H1, 0 of 10 subfields | ⚠️ rerun required on representative labels |
| C8 | H2 trend | ⚠️ rerun required; 2015–2017 absent from current data |
| C14 | IPC, 2 of 26 | ⚠️ rerun required; not human-validated |
| C15 | redaction, 4 of 16 flip | ✅ holds in kind (within-patent comparison) |
"""

CLAUDE_MARKER = "### Sampling gotcha (2026-09-12)"
CLAUDE_ENTRY = """

### Sampling gotcha (2026-09-12)

Never fetch patent metadata in sorted-id order and stop partway. As strings,
"US10..." sorts before "US9...", so a partial run silently drops whole grant years —
this made both classified arms unrepresentative. Fetch order is now randomized.
Before quoting any classified rate, check the grant-year mix of the classified set
against the population with `tools/check_abstract.py`.
"""


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
    append(ROOT / "CLAUDE.md", CLAUDE_MARKER, CLAUDE_ENTRY)


if __name__ == "__main__":
    main()
