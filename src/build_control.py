"""Stage 11 — the CONTROL ARM. Required by the pre-registered plan.

Without it the headline is uninterpretable. "6% of NLP-citing patents are
surveillance" means nothing until you know what share of science-citing patents
in general are surveillance. Patents in computing cite security-adjacent work
routinely; if the base rate is also 6% we have no finding at all.

Construction: uniform random sample of DISTINCT patents in Reliance on Science
v65 that cite at least one paper but cite **none** of our ACL papers. Same file,
same citation mechanism, same grant-year window (2015-2025), same classifier,
same rubric. The only thing that differs is the field of the cited science.

Sampling is uniform over distinct patents, not over citation rows — row-uniform
sampling would over-represent heavily-citing patents and bias the comparison.

This is "the average science-citing USPTO patent", NOT a field-matched control.
A field-matched arm (non-NLP computer science specifically) needs OpenAlex
subject queries and is listed as a limitation until it exists.

    python -m src.build_control --n 1200
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import pandas as pd

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PCS = ROOT / "data" / "raw" / "pcs_oa_uspto.csv"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=20260912)
    a = ap.parse_args()

    treat = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    treated = set(treat["patent"].astype(str).str.upper().str.replace("-", "", regex=False))
    print(f"[treat] {len(treated):,} patents cite >=1 ACL paper — excluded from the control")

    print("[scan ] collecting distinct patent ids from the full citation file...")
    seen: set[str] = set()
    n = 0
    with open(PCS, encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        i = {c.strip().lower(): k for k, c in enumerate(h)}
        ip = i["patent"]
        for row in r:
            n += 1
            if len(row) <= ip:
                continue
            seen.add(row[ip].strip())
            if n % 10_000_000 == 0:
                print(f"        {n:,} rows, {len(seen):,} distinct patents")
    print(f"[scan ] {n:,} rows -> {len(seen):,} distinct patents total")

    pool = [p for p in seen if p.upper().replace("-", "") not in treated]
    print(f"[pool ] {len(pool):,} patents cite science but no ACL paper")

    rng = random.Random(a.seed)
    pick = sorted(rng.sample(pool, min(a.n, len(pool))))
    print(f"[samp ] {len(pick):,} drawn uniformly over DISTINCT patents (seed {a.seed})")

    out = RESULTS / "control_patents.csv"
    pd.DataFrame({"patent": pick}).to_csv(out, index=False)
    (RESULTS / "control_meta.json").write_text(json.dumps({
        "n_sampled": len(pick), "pool_size": len(pool),
        "distinct_patents_in_file": len(seen), "rows_scanned": n,
        "treated_excluded": len(treated), "seed": a.seed,
        "definition": "uniform over distinct patents citing >=1 paper but no ACL paper",
        "not_a_field_matched_control": True,
    }, indent=2), encoding="utf-8")
    print(f"[out  ] {out}")
    print("\nNext: fetch metadata for these, then classify with the same rubric.")
    print("  python -m src.fetch_patent_meta --source fpo --ids results/control_patents.csv")


if __name__ == "__main__":
    main()
