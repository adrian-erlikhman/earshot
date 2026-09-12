"""Stage 12 — the SPEECH ARM. Third arm of the comparison.

The project's original hypothesis was that speech and speaker-ID research is
closer to surveillance than text NLP. The ACL Anthology cannot test that — it
holds 15 speaker-ID papers in the censored window — because speaker
identification publishes at Interspeech and ICASSP.

Reliance on Science keys on OpenAlex ids and does not care what venue a paper
came from, so we go at the question directly: pull speech / speaker-ID works
from OpenAlex irrespective of venue, join to the same citation file, and
classify the resulting patents with the same rubric.

That gives three arms measured identically:
  speech-citing patents   vs   ACL-citing patents   vs   science-citing patents

Fixes the earlier mistake: uses OpenAlex's `sample` parameter with a fixed seed
rather than truncating a relevance-ordered result set. Truncation enriched for
heavily-cited papers, which is exactly what inflated the withdrawn 13.7% figure.

    python -m src.build_speech_arm --per-query 8000
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "interim" / "speech_cache"
RESULTS = ROOT / "results"
PCS = ROOT / "data" / "raw" / "pcs_oa_uspto.csv"
MAILTO = "babafiraislife@gmail.com"
RATE = 1.6           # 0.7s drew 429s twice on sustained sampled paging

# Narrow, on-purpose: speaker identification proper, plus the speech-processing
# literature it sits in. Kept separate so the two can be reported apart.
QUERIES = {
    "speaker_id": ["speaker recognition", "speaker verification",
                   "speaker identification", "voice biometrics"],
    "speech_general": ["speech recognition", "speech synthesis",
                       "acoustic modeling speech", "spoken language understanding"],
}


class OAError(RuntimeError):
    pass


def oa(**p):
    p["mailto"] = MAILTO
    u = "https://api.openalex.org/works?" + urllib.parse.urlencode(p)
    key = CACHE / f"{hashlib.md5(u.encode()).hexdigest()}.json"
    if key.exists():
        try:
            return json.loads(key.read_text(encoding="utf-8"))
        except Exception:
            key.unlink(missing_ok=True)
    req = urllib.request.Request(u, headers={"User-Agent": f"earshot (mailto:{MAILTO})"})
    last = None
    for i in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as x:
                d = json.load(x)
            CACHE.mkdir(parents=True, exist_ok=True)
            key.write_text(json.dumps(d), encoding="utf-8")
            time.sleep(RATE)
            return d
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            time.sleep((20 if e.code == 429 else 6) * (i + 1))
        except Exception as e:
            last = type(e).__name__
            time.sleep(6 * (i + 1))
    raise OAError(f"{last} on {u[:100]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=20260912)
    a = ap.parse_args()

    works: dict[str, dict] = {}
    totals: dict[str, int] = {}
    failed = []
    for arm, qs in QUERIES.items():
        for q in qs:
            try:
                d0 = oa(filter=f"title_and_abstract.search:{q}", per_page=1)
                totals[q] = d0.get("meta", {}).get("count")
            except OAError as e:
                print(f"  '{q}': COUNT FAILED {e}"); failed.append(q); continue
            # `sample` requires PAGE-based paging; cursor paging silently stops
            # after the first page, which is what capped an earlier run at 200.
            want = min(a.per_query, totals[q] or 0)
            got, page = 0, 1
            while got < want and page <= 50:          # OpenAlex caps page*per_page
                try:
                    d = oa(filter=f"title_and_abstract.search:{q}", sample=want,
                           seed=a.seed, per_page=200, page=page,
                           select="id,title,publication_year,primary_location")
                except OAError as e:
                    print(f"  '{q}': PAGE {page} FAILED {e}"); failed.append(q); break
                res = d.get("results", [])
                if not res:
                    break
                for w in res:
                    oid = (w.get("id") or "").rsplit("/", 1)[-1].lstrip("Ww")
                    loc = (w.get("primary_location") or {}).get("source") or {}
                    works.setdefault(oid, {"arm": arm, "title": w.get("title"),
                                           "year": w.get("publication_year"),
                                           "venue": loc.get("display_name")})
                got += len(res)
                page += 1
            print(f"  {arm:<16} '{q}': {got:,} of {totals[q]:,} (sampled)")

    if failed:
        print(f"\n!! {len(set(failed))} queries failed — rates would be invalid. Re-run to resume from cache.")
        sys.exit(1)

    print(f"\n[oa ] {len(works):,} distinct speech/speaker works")
    wanted = set(works)

    print("[join] scanning the citation file...")
    hits = []
    with open(PCS, encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f); h = next(r)
        i = {c.strip().lower(): k for k, c in enumerate(h)}
        n = 0
        for row in r:
            n += 1
            if len(row) <= i["wherefound"]:
                continue
            oid = row[i["oaid"]].strip()
            if oid in wanted:
                hits.append({"oaid": oid, "patent": row[i["patent"]].strip(),
                             "reftype": row[i["reftype"]].strip(),
                             "confscore": row[i["confscore"]].strip(),
                             "wherefound": row[i["wherefound"]].strip(),
                             "arm": works[oid]["arm"]})
            if n % 10_000_000 == 0:
                print(f"       {n:,} rows, {len(hits):,} hits")

    df = pd.DataFrame(hits)
    RESULTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS / "speech_links.csv", index=False)
    pd.DataFrame([{"oaid": k, **v} for k, v in works.items()]).to_csv(
        RESULTS / "speech_works.csv", index=False)

    print(f"\n[out ] {len(df):,} links | {df['patent'].nunique():,} distinct patents | "
          f"{df['oaid'].nunique():,} distinct papers cited")
    for arm in QUERIES:
        s = df[df["arm"] == arm]
        nw = sum(1 for v in works.values() if v["arm"] == arm)
        print(f"   {arm:<16} {s['patent'].nunique():>7,} patents  "
              f"{s['oaid'].nunique():>6,}/{nw:,} works cited "
              f"({100*s['oaid'].nunique()/max(nw,1):.1f}%)")
    print(f"\n   wherefound: {df['wherefound'].value_counts().to_dict()}")
    pd.DataFrame({"patent": sorted(df["patent"].unique())}).to_csv(
        RESULTS / "speech_patents.csv", index=False)
    print(f"[out ] results/speech_patents.csv — feed to fetch_patent_meta --ids")


if __name__ == "__main__":
    main()
