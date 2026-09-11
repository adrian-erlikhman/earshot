"""Stage 4 — join ACL papers to citing patents, and split applicant vs examiner.

This is the number the whole project turns on. Michael's point, which is correct:
an examiner citation means a USPTO employee judged our paper to be relevant prior
art. Only an APPLICANT citation says the firm building the system was reading us.
Alcacer/Gittelman/Sampat show the examiner share is large and is highest in
electronics and computing, which is exactly our neighbourhood.

So we report applicant-only as the headline and carry the examiner number as a
documented contrast, rather than reporting a combined figure that would not
survive a reviewer who knows this literature.

Streams the 1.4 GB citation file; never loads it whole.

    python -m src.join_patents
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
RESULTS = ROOT / "results"
PCS = RAW / "pcs_oa_uspto.csv"


def main() -> None:
    if not PCS.exists():
        sys.exit(f"missing {PCS} — run `python -m src.fetch_ros` first")

    papers = pd.read_csv(INTERIM / "acl_openalex.csv", low_memory=False)
    papers = papers[papers["openalex_id"].notna()].copy()
    # RoS keys on the bare numeric OpenAlex id; ours are 'W2133564696'.
    papers["oaid"] = papers["openalex_id"].astype(str).str.lstrip("Ww")
    oaid_to_rows = defaultdict(list)
    for oaid, acl_id, year, venue in zip(
        papers["oaid"], papers["acl_id"], papers["year"], papers["venue_key"]
    ):
        oaid_to_rows[oaid].append((acl_id, year, venue))
    wanted = set(oaid_to_rows)
    print(f"[paper] {len(papers):,} matched papers -> {len(wanted):,} distinct OpenAlex ids")

    reftypes = Counter()
    wherefound = Counter()
    links: list[dict] = []
    seen_rows = 0

    with open(PCS, encoding="utf-8", errors="replace", newline="") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        print(f"[pcs ] header={header}")
        ix = {h.strip().lower(): i for i, h in enumerate(header)}
        i_ref, i_conf = ix["reftype"], ix["confscore"]
        i_oa, i_pat, i_wf = ix["oaid"], ix["patent"], ix["wherefound"]

        for row in rdr:
            seen_rows += 1
            if seen_rows % 5_000_000 == 0:
                print(f"       {seen_rows:,} citation rows scanned, {len(links):,} hits")
            if len(row) <= i_wf:
                continue
            oa = row[i_oa].strip()
            if oa not in wanted:
                continue
            rt = row[i_ref].strip().lower()
            reftypes[rt] += 1
            wherefound[row[i_wf].strip().lower()] += 1
            links.append(
                {
                    "oaid": oa,
                    "patent": row[i_pat].strip(),
                    "reftype": rt,
                    "confscore": pd.to_numeric(row[i_conf], errors="coerce"),
                    "wherefound": row[i_wf].strip().lower(),
                }
            )

    print(f"\n[scan ] {seen_rows:,} citation rows total")
    df = pd.DataFrame(links)
    if df.empty:
        sys.exit("no matches — check the oaid normalisation")

    # attach paper metadata (a patent may cite several of our papers)
    meta = papers.set_index("oaid")[["acl_id", "year", "venue_key", "title"]]
    df = df.join(meta, on="oaid")

    RESULTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS / "patent_links.csv", index=False)

    n_links = len(df)
    n_patents = df["patent"].nunique()
    n_papers = df["oaid"].nunique()

    print(f"\n[LINKS] {n_links:,} citation links")
    print(f"        {n_patents:,} distinct patents")
    print(f"        {n_papers:,} distinct ACL papers cited by >=1 patent "
          f"({100*n_papers/len(papers):.1f}% of matched corpus)")

    print(f"\n[reftype] (the applicant/examiner split)")
    for k, v in reftypes.most_common():
        print(f"   {k:<12} {v:>9,}  ({100*v/n_links:.1f}% of links)")

    print(f"\n[wherefound]")
    for k, v in wherefound.most_common():
        print(f"   {k:<12} {v:>9,}  ({100*v/n_links:.1f}%)")

    # The headline contrast.
    app = df[df["reftype"].str.startswith("app", na=False)]
    exa = df[~df["reftype"].str.startswith("app", na=False)]
    print(f"\n[HEADLINE] applicant-only: {app['patent'].nunique():,} distinct patents, "
          f"{app['oaid'].nunique():,} distinct papers")
    print(f"           other/examiner : {exa['patent'].nunique():,} distinct patents, "
          f"{exa['oaid'].nunique():,} distinct papers")
    if n_patents:
        print(f"           applicant share of distinct patents: "
              f"{100*app['patent'].nunique()/n_patents:.1f}%")

    print(f"\n[by confscore] (ablation: restrict to >=5)")
    hi = df[df["confscore"] >= 5]
    print(f"   confscore>=5: {hi['patent'].nunique():,} distinct patents "
          f"({100*hi['patent'].nunique()/max(n_patents,1):.1f}%)")
    hi_app = hi[hi["reftype"].str.startswith("app", na=False)]
    print(f"   confscore>=5 AND applicant: {hi_app['patent'].nunique():,} distinct patents")

    print(f"\n[top venues among cited papers]")
    for k, v in df.drop_duplicates("oaid")["venue_key"].value_counts().head(10).items():
        print(f"   {k:<14} {v:,}")

    print(f"\n[cited-paper year distribution]")
    yrs = df.drop_duplicates("oaid")["year"].dropna().astype(int)
    for lo, hi_ in [(1979, 1999), (2000, 2009), (2010, 2014), (2015, 2019), (2020, 2026)]:
        print(f"   {lo}–{hi_}: {((yrs >= lo) & (yrs <= hi_)).sum():,}")

    (RESULTS / "patent_links_summary.json").write_text(json.dumps({
        "n_links": n_links, "n_distinct_patents": n_patents, "n_distinct_papers": n_papers,
        "reftype_counts": dict(reftypes), "wherefound_counts": dict(wherefound),
        "applicant_distinct_patents": int(app["patent"].nunique()),
        "examiner_distinct_patents": int(exa["patent"].nunique()),
        "conf5_distinct_patents": int(hi["patent"].nunique()),
        "conf5_applicant_distinct_patents": int(hi_app["patent"].nunique()),
    }, indent=2), encoding="utf-8")
    print(f"\n[done] -> results/patent_links.csv + patent_links_summary.json")


if __name__ == "__main__":
    main()
