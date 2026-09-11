"""Stage 2 — map ACL Anthology papers to OpenAlex work IDs.

Reliance on Science is keyed on OpenAlex IDs (verified: header is
`reftype,confscore,oaid,patent,wherefound`), so this join is the spine of the
whole downstream analysis.

Two passes:
  1. DOI batch lookup — OpenAlex accepts `filter=doi:a|b|...` up to 50 per call.
     Covers the 54.8% of papers that carry a DOI (essentially everything 2015+).
  2. Title+year fallback for the pre-2015 tail, done by bulk-pulling the ACL
     venue sources and matching locally rather than one query per paper.

Zhang (ACL 2025) reports 21,104/24,821 ≈ 85% matched on ACL/EMNLP/NAACL. That is
our sanity check: land far from it on the same subset and we have a bug.

Resumable: every batch response is cached under data/interim/oa_cache/.

    python -m src.join_openalex --pass doi
    python -m src.join_openalex --pass doi --limit 20     # smoke test: 20 batches
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
CACHE = INTERIM / "oa_cache"
MAILTO = "babafiraislife@gmail.com"          # OpenAlex polite pool
BATCH = 50                                    # OpenAlex max for an OR filter
SELECT = "id,ids,doi,title,publication_year,type,cited_by_count,primary_location"


def _get(url: str, tries: int = 4) -> dict | None:
    key = hashlib.md5(url.encode()).hexdigest()
    cached = CACHE / f"{key}.json"
    if cached.exists():
        try:
            return json.loads(cached.read_text(encoding="utf-8"))
        except Exception:
            cached.unlink(missing_ok=True)

    req = urllib.request.Request(url, headers={"User-Agent": f"ai4peace-research (mailto:{MAILTO})"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            CACHE.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(d), encoding="utf-8")
            return d
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (i + 1))
                continue
            if e.code >= 500:
                time.sleep(3 * (i + 1))
                continue
            print(f"    HTTP {e.code} on batch")
            return None
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def norm_doi(d: str | float | None) -> str | None:
    if not isinstance(d, str) or not d.strip():
        return None
    s = d.strip().lower()
    for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
        if s.startswith(pre):
            s = s[len(pre):]
    return s or None


def doi_pass(limit: int | None = None) -> pd.DataFrame:
    papers = pd.read_csv(INTERIM / "acl_papers.csv", low_memory=False)
    papers["doi_norm"] = papers["doi"].map(norm_doi)
    have = papers.dropna(subset=["doi_norm"]).drop_duplicates("doi_norm")
    dois = have["doi_norm"].tolist()
    batches = [dois[i:i + BATCH] for i in range(0, len(dois), BATCH)]
    if limit:
        batches = batches[:limit]

    print(f"[doi ] {len(dois):,} distinct DOIs -> {len(batches):,} batches of {BATCH}")
    rows: list[dict] = []
    misses = 0

    for n, b in enumerate(batches, 1):
        filt = "doi:" + "|".join(b)
        url = (
            "https://api.openalex.org/works?"
            + urllib.parse.urlencode({"filter": filt, "per-page": BATCH, "select": SELECT, "mailto": MAILTO})
        )
        d = _get(url)
        if d is None:
            misses += len(b)
        else:
            for w in d.get("results", []):
                ids = w.get("ids") or {}
                loc = (w.get("primary_location") or {}).get("source") or {}
                rows.append(
                    {
                        "openalex_id": (w.get("id") or "").rsplit("/", 1)[-1],
                        "mag_id": ids.get("mag"),
                        "doi_norm": norm_doi(w.get("doi")),
                        "oa_title": w.get("title"),
                        "oa_year": w.get("publication_year"),
                        "oa_type": w.get("type"),
                        "cited_by_count": w.get("cited_by_count"),
                        "oa_source": loc.get("display_name"),
                    }
                )
        if n % 50 == 0 or n == len(batches):
            print(f"       {n}/{len(batches)} batches, {len(rows):,} works, {misses} in failed batches")
        time.sleep(0.12)

    oa = pd.DataFrame(rows).drop_duplicates("doi_norm")
    merged = papers.merge(oa, on="doi_norm", how="left")

    INTERIM.mkdir(parents=True, exist_ok=True)
    out = INTERIM / "acl_openalex.csv"
    merged.to_csv(out, index=False)

    matched = merged["openalex_id"].notna()
    with_doi = merged["doi_norm"].notna()
    print(f"\n[done] -> {out}")
    print(f"       papers total          : {len(merged):,}")
    print(f"       papers with a DOI     : {with_doi.sum():,}")
    print(f"       matched to OpenAlex   : {matched.sum():,} "
          f"({100*matched.sum()/max(len(merged),1):.1f}% of all, "
          f"{100*matched[with_doi].mean():.1f}% of DOI-bearing)")

    core = merged[merged["is_core_venue"].fillna(False)]
    if len(core):
        print(f"       core-venue matched    : {core['openalex_id'].notna().sum():,}/{len(core):,} "
              f"({100*core['openalex_id'].notna().mean():.1f}%)  [Zhang 2025 benchmark: ~85%]")
    print("\n       matched by era:")
    for lo, hi in [(1979, 1999), (2000, 2009), (2010, 2014), (2015, 2019), (2020, 2026)]:
        sl = merged[(merged["year"] >= lo) & (merged["year"] <= hi)]
        if len(sl):
            print(f"         {lo}–{hi}: {sl['openalex_id'].notna().sum():>6,}/{len(sl):>6,} "
                  f"({100*sl['openalex_id'].notna().mean():>5.1f}%)")
    return merged


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="which", default="doi", choices=["doi"])
    ap.add_argument("--limit", type=int, default=None, help="cap the number of batches (smoke test)")
    a = ap.parse_args()
    doi_pass(a.limit)
