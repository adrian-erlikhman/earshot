"""Rebuild paper/BRIEF.pdf from BRIEF.md, then check that what it asserts is true.

Three kinds of check, because a brief is only useful if its numbers survive contact
with the data:
  1. TL;DR length against the 300-character form limit
  2. key numbers actually present in the rendered PDF
  3. two claims the brief makes that are easy to get subtly wrong:
     - which HRL patent is labelled surveillance in the assignee-redacted run
     - the patents-per-arm power figure for 0.69% vs 0.27%

The first run caught the power figure (brief said ~4,200; computed 4,303) and a
false alarm in the TL;DR check, which failed only because markdown blockquote markers
broke the verbatim match. Both fixed.

    python tools/verify_brief.py
"""
import sys
from math import ceil, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pandas as pd  # noqa: E402
import pypdf  # noqa: E402
from md2pdf import convert  # noqa: E402

TLDR = ("We linked 127,851 ACL Anthology papers to the patents citing them, then asked what "
        "those patents are for. The distinction that decides it for speech: verifying a "
        "claimed identity is not the same as picking someone out of a population.")

KEY_STRINGS = ["0.69%", "0 of 10", "25%", "HRL", "Proximity, Not Transmission",
               "4,300", "0.33%", "24,829", "only 2 as surveillance", "17 were"]


def n_per_arm(p1: float, p2: float) -> int:
    za, zb = 1.959964, 0.8416212          # two-sided alpha 0.05, power 0.80
    pbar = (p1 + p2) / 2
    num = (za * sqrt(2 * pbar * (1 - pbar)) + zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return ceil(num / (p1 - p2) ** 2)


def flatten(text: str) -> str:
    """Collapse whitespace and drop markdown blockquote markers before matching."""
    lines = [ln.lstrip()[1:] if ln.lstrip().startswith(">") else ln for ln in text.splitlines()]
    return " ".join(" ".join(lines).split())


def main() -> None:
    md = ROOT / "paper" / "BRIEF.md"
    pdf = ROOT / "paper" / "BRIEF.pdf"

    print(f"[tldr] {len(TLDR)} of 300 characters")
    print(f"[tldr] present in BRIEF.md: {TLDR in flatten(md.read_text(encoding='utf-8'))}")

    convert(md, pdf)
    reader = pypdf.PdfReader(str(pdf))
    text = " ".join("".join(p.extract_text() for p in reader.pages).split())
    print(f"[pdf ] {len(reader.pages)} pages")
    missing = 0
    for k in KEY_STRINGS:
        ok = k in text
        missing += not ok
        print(f"   {k:<30}{'present' if ok else 'MISSING'}")

    print()
    print("[check] HRL patents in the assignee-redacted primary labels:")
    lab = pd.read_csv(ROOT / "results" / "patent_labels.csv")
    hrl = lab[lab["assignee"].astype(str).str.contains("HRL", case=False, na=False)]
    for _, r in hrl.iterrows():
        print(f"   {r['label']:<20} {str(r['title'])[:80]}")
    if hrl.empty:
        print("   none found — the brief's HRL sentence must be removed")

    print()
    p1 = 7 / 1012
    p2 = 1 / 366
    print(f"[check] power, {100*p1:.2f}% vs {100*p2:.2f}%, alpha .05, 80% power: "
          f"{n_per_arm(p1, p2):,} patents per arm (brief says roughly 4,300)")

    print()
    print("ALL KEY STRINGS PRESENT" if missing == 0 else f"{missing} KEY STRING(S) MISSING")


if __name__ == "__main__":
    main()
