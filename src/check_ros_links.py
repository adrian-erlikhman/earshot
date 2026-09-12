"""Stage 10 — hand-check sample of Reliance on Science paper→patent links.

Two links in our set are a Surface hinge patent and a drug-discovery patent
citing ACL papers. Those are possible but odd. If a meaningful share of the
linkage is spurious, every rate we report moves, because 9,048 is the
denominator for all of them.

Produces a 50-row sheet pairing each cited paper's title with the citing
patent's title, for a plausible / implausible / cannot-tell judgement. Fifty is
enough to distinguish "a few percent" from "a fifth" — the only distinction that
changes what we do.

    python -m src.check_ros_links --n 50
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
RESULTS = ROOT / "results"
GOLD = ROOT / "data" / "goldset"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260913)
    a = ap.parse_args()

    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    links["patent_norm"] = links["patent"].astype(str).str.upper().str.replace("-", "", regex=False)

    meta = []
    for f in (INTERIM / "patent_meta").glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("title"):
            meta.append({"patent_norm": r["patent_id"].upper().replace("-", ""),
                         "patent_title": r.get("title"), "patent_assignee": r.get("assignee")})
    md = pd.DataFrame(meta).drop_duplicates("patent_norm")
    print(f"[meta] {len(md):,} patents with a title available")

    j = links.merge(md, on="patent_norm", how="inner")
    print(f"[join] {len(j):,} links have both sides resolvable")
    if len(j) < a.n:
        print(f"  ! only {len(j)} available; sheet will be short until the fetch finishes")

    s = j.sample(n=min(a.n, len(j)), random_state=a.seed)[
        ["oaid", "title", "patent", "patent_title", "patent_assignee", "confscore", "wherefound"]
    ].rename(columns={"title": "paper_title"})
    s.insert(0, "item", range(1, len(s) + 1))
    s["plausible"] = ""          # yes | no | cannot_tell
    s["note"] = ""

    GOLD.mkdir(parents=True, exist_ok=True)
    out = GOLD / "ros_link_check.csv"
    s.to_csv(out, index=False)
    print(f"[out ] {out}  ({len(s)} links)")
    print("\nJudge: could this patent plausibly have drawn on this paper?")
    print("  yes          — same topic, or the paper is foundational to the patent's field")
    print("  no           — unrelated subject matter, no plausible route")
    print("  cannot_tell  — too generic either side to say")
    print("\nIf 'no' exceeds ~10%, the denominator needs a confscore floor and every")
    print("rate in the paper gets recomputed on the filtered set.")
    if len(s):
        print("\n  preview:")
        for _, r in s.head(5).iterrows():
            print(f"   paper : {str(r['paper_title'])[:66]}")
            print(f"   patent: {str(r['patent_title'])[:66]}  (conf={r['confscore']})")
            print()


if __name__ == "__main__":
    main()
