"""Which NLP subfields are most patent-proximate? — computed entirely offline.

Everything here comes from files already on disk: the ACL corpus with OpenAlex
ids, and the patent citation links. No network, so no rate limit can corrupt it.

This is the *within-corpus* comparison. Because every arm is drawn from the same
corpus, indexed the same way, over the same years, the only thing varying between
arms is the subfield — which is what the claim is about. (The earlier
speech-vs-ACL contrast compared two differently-built corpora and is not usable;
see LOG.md.)

Reports, per subfield: n papers, n cited by >=1 patent, rate with bootstrap 95%
CI clustered by paper, distinct citing patents, and the rate by era so age is not
driving the ranking.

    python -m src.subfields_acl
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
RESULTS = ROOT / "results"
ERAS = [(1979, 1999), (2000, 2009), (2010, 2014), (2015, 2019), (2020, 2026)]


def load_rules() -> dict[str, re.Pattern]:
    """Minimal YAML read — the file is a flat map of name -> list of patterns."""
    rules: dict[str, list[str]] = {}
    cur = None
    for raw in (ROOT / "configs" / "subfields.yaml").read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            cur = line[:-1].strip()
            rules[cur] = []
        elif line.strip().startswith("-") and cur:
            pat = line.strip()[1:].strip()
            if pat[:1] in "'\"" and pat[-1:] == pat[:1]:
                pat = pat[1:-1]
            rules[cur].append(pat)
    return {k: re.compile("|".join(f"(?:{p})" for p in v), re.I) for k, v in rules.items() if v}


def boot_ci(flags: np.ndarray, n: int = 10000, seed: int = 0) -> tuple[float, float]:
    if len(flags) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(flags), size=(n, len(flags)))
    means = flags[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main() -> None:
    papers = pd.read_csv(INTERIM / "acl_openalex.csv", low_memory=False)
    papers = papers[papers["openalex_id"].notna()].copy()
    papers["oaid"] = papers["openalex_id"].astype(str).str.lstrip("Ww")
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna(""))
    print(f"[corpus] {len(papers):,} ACL papers with an OpenAlex id")
    print(f"         {papers['abstract'].notna().sum():,} have an abstract "
          f"({100*papers['abstract'].notna().mean():.1f}%) — rules see title only for the rest")

    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    links["oaid"] = links["oaid"].astype(str)
    cited = links.groupby("oaid")["patent"].apply(set).to_dict()
    print(f"[links ] {links['patent'].nunique():,} distinct patents over "
          f"{len(cited):,} cited papers")

    rules = load_rules()
    print(f"[rules ] {len(rules)} subfields from configs/subfields.yaml\n")

    papers["is_cited"] = papers["oaid"].map(lambda o: o in cited)
    overall = papers["is_cited"].mean()
    lo_a, hi_a = boot_ci(papers["is_cited"].to_numpy(dtype=float))
    print(f"[BASE  ] corpus-wide patent-proximity: {100*overall:.2f}% "
          f"[{100*lo_a:.2f}, {100*hi_a:.2f}]  n={len(papers):,}\n")

    rows = []
    for name, rx in rules.items():
        m = papers["text"].str.contains(rx, na=False)
        sub = papers[m]
        if len(sub) == 0:
            rows.append({"subfield": name, "n": 0}); continue
        flags = sub["is_cited"].to_numpy(dtype=float)
        lo, hi = boot_ci(flags)
        pats = set().union(*[cited[o] for o in sub["oaid"] if o in cited]) if flags.any() else set()
        era = {}
        for a, b in ERAS:
            s2 = sub[(sub["year"] >= a) & (sub["year"] <= b)]
            era[f"{a}-{b}"] = {"n": int(len(s2)),
                               "rate": float(s2["is_cited"].mean()) if len(s2) else None}
        rows.append({"subfield": name, "n": int(len(sub)), "n_cited": int(flags.sum()),
                     "rate": float(flags.mean()), "ci_lo": lo, "ci_hi": hi,
                     "n_patents": len(pats), "by_era": era,
                     "excludes_base": bool(lo > overall or hi < overall)})

    rows.sort(key=lambda r: -(r.get("rate") or 0))
    print(f"{'subfield':<24}{'papers':>8}{'cited':>7}{'rate':>8}  {'95% CI':<18}{'patents':>8}  vs base")
    for r in rows:
        if not r.get("n"):
            print(f"{r['subfield']:<24}{0:>8}   (no matches)"); continue
        mark = "***" if r["excludes_base"] else "   "
        print(f"{r['subfield']:<24}{r['n']:>8,}{r['n_cited']:>7,}{100*r['rate']:>7.2f}%  "
              f"[{100*r['ci_lo']:>5.2f},{100*r['ci_hi']:>5.2f}]{r['n_patents']:>8,}  {mark}")
    print("\n  *** = bootstrap CI excludes the corpus-wide rate")

    print(f"\n[by era] patent-proximity rate (n)")
    hdr = "".join(f"{f'{a}-{b}':>17}" for a, b in ERAS)
    print(f"{'subfield':<24}{hdr}")
    for r in rows:
        if not r.get("n"):
            continue
        cells = []
        for a, b in ERAS:
            e = r["by_era"][f"{a}-{b}"]
            cells.append(f"{100*e['rate']:>5.1f}% ({e['n']:,})" if e["rate"] is not None and e["n"] else f"{'--':>17}")
        print(f"{r['subfield']:<24}" + "".join(f"{c:>17}" for c in cells))

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "subfield_rates.json").write_text(
        json.dumps({"corpus_rate": overall, "corpus_ci": [lo_a, hi_a],
                    "n_papers": int(len(papers)), "subfields": rows}, indent=2),
        encoding="utf-8")
    print(f"\n[done] -> results/subfield_rates.json")


if __name__ == "__main__":
    main()
