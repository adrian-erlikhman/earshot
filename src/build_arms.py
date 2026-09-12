"""Core analysis — patent-proximity by language-technology subfield, ONE corpus.

Yesterday's 13.7% vs 7.2% compared an ACL-Anthology-derived set against an
OpenAlex-derived set. That is apples to oranges: different venue populations,
different eras, different indexing. A reviewer would bin it immediately.

Fix: pull EVERY arm the same way, from OpenAlex, with parallel
title_and_abstract queries, then join all of them to the same Reliance on
Science file. Now the only thing varying between arms is the subfield.

Reports per-subfield patent-proximity rate, stratified by publication era so the
comparison is not driven by age, with bootstrap CIs.

    python -m src.build_arms
"""
from __future__ import annotations
import csv, hashlib, json, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np

csv.field_size_limit(min(sys.maxsize, 2**31-1))
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/"data"/"interim"/"arms_cache"
M = "babafiraislife@gmail.com"
CAP = 12000
RATE = 0.6           # seconds between OpenAlex calls; 429s are what produced fake zeros
FAILURES: list = []          # per query; recorded in output so the cap is never hidden

SUBFIELDS = {
 "speaker_id": ["speaker recognition","speaker verification","speaker identification","voice biometrics"],
 "speech_asr": ["speech recognition","acoustic model speech","speech synthesis","spoken language understanding"],
 "machine_translation": ["machine translation","statistical machine translation","neural machine translation"],
 "information_extraction": ["named entity recognition","relation extraction","information extraction text"],
 "sentiment": ["sentiment analysis","opinion mining","emotion recognition text"],
 "dialogue_qa": ["dialogue system","question answering system","conversational agent"],
 "parsing_syntax": ["syntactic parsing","dependency parsing","part-of-speech tagging"],
 "summarization": ["text summarization","automatic summarization"],
}

class OAError(RuntimeError):
    pass


def oa(**p):
    """Fetch one OpenAlex page. Raises on persistent failure - never returns a
    silent empty result, because an empty arm is indistinguishable from a real
    zero and that is exactly how a rate-limit turns into a fake finding."""
    p["mailto"] = M
    u = "https://api.openalex.org/works?" + urllib.parse.urlencode(p)
    key = CACHE / f"{hashlib.md5(u.encode()).hexdigest()}.json"
    if key.exists():
        try:
            return json.loads(key.read_text(encoding="utf-8"))
        except Exception:
            key.unlink(missing_ok=True)
    r = urllib.request.Request(u, headers={"User-Agent": f"ai4peace (mailto:{M})"})
    last = None
    for i in range(7):
        try:
            with urllib.request.urlopen(r, timeout=120) as x:
                d = json.load(x)
            CACHE.mkdir(parents=True, exist_ok=True)
            key.write_text(json.dumps(d), encoding="utf-8")
            time.sleep(RATE)                      # be a good citizen, always
            return d
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            time.sleep((15 if e.code == 429 else 5) * (i + 1))
        except Exception as e:
            last = f"{type(e).__name__}"
            time.sleep(5 * (i + 1))
    raise OAError(f"giving up after 7 tries ({last}): {u[:110]}")


def pull(queries):
    works, capped, totals, failed = {}, False, {}, []
    for q in queries:
        try:
            d0 = oa(filter=f"title_and_abstract.search:{q}", per_page=1)
            totals[q] = (d0 or {}).get("meta", {}).get("count")
        except OAError as e:
            print(f"    '{q}': COUNT FAILED - {e}")
            failed.append(q); totals[q] = None; continue
        cur, got = "*", 0
        while cur and got < CAP:
            try:
                d = oa(filter=f"title_and_abstract.search:{q}", per_page=200, cursor=cur,
                       select="id,publication_year,type,primary_location")
            except OAError as e:
                print(f"    '{q}': PAGE FAILED at {got:,} - {e}")
                failed.append(q); break
            res = d.get("results", [])
            if not res:
                break
            for w in res:
                oid = (w.get("id") or "").rsplit("/", 1)[-1].lstrip("Ww")
                loc = (w.get("primary_location") or {}).get("source") or {}
                works[oid] = {"year": w.get("publication_year"),
                              "type": loc.get("type"), "venue": loc.get("display_name")}
            got += len(res)
            cur = (d.get("meta") or {}).get("next_cursor")
        if totals.get(q) and got < totals[q]:
            capped = True
        print(f"    '{q}': pulled {got:,} of {totals[q]:,}" if totals.get(q) else f"    '{q}': pulled {got:,} (total unknown)")
    return works, capped, totals, failed


print("[1] pulling arms from OpenAlex")
arms={}; meta={}
for name,qs in SUBFIELDS.items():
    print(f"  {name}:")
    w,capped,tot,failed=pull(qs)
    arms[name]=w; meta[name]={"n_works":len(w),"capped":capped,"query_totals":tot,"failed_queries":failed}
    if failed: FAILURES.extend([(name,q) for q in failed])
    print(f"    -> {len(w):,} distinct works (capped={capped})")

all_ids={}
for name,w in arms.items():
    for oid,info in w.items():
        all_ids.setdefault(oid,{"info":info,"arms":set()})["arms"].add(name)
print(f"\n[2] {len(all_ids):,} distinct works across all arms; joining to RoS")

cited=defaultdict(set)   # oaid -> patents
with open(ROOT/"data"/"raw"/"pcs_oa_uspto.csv",encoding="utf-8",errors="replace",newline="") as f:
    r=csv.reader(f); h=next(r); i={c.strip().lower():k for k,c in enumerate(h)}
    n=0
    for row in r:
        n+=1
        if len(row)<=i["wherefound"]: continue
        oid=row[i["oaid"]].strip()
        if oid in all_ids: cited[oid].add(row[i["patent"]].strip())
        if n%10_000_000==0: print(f"    {n:,} rows, {len(cited):,} cited works so far")

def boot(flags,n=2000,seed=0):
    rng=np.random.default_rng(seed); a=np.asarray(flags,dtype=float)
    if len(a)==0: return (float("nan"),)*2
    s=rng.choice(a,size=(n,len(a)),replace=True).mean(axis=1)
    return float(np.percentile(s,2.5)), float(np.percentile(s,97.5))

ERAS=[(1980,1999),(2000,2009),(2010,2017),(2018,2026)]
print(f"\n{'subfield':<24}{'works':>9}{'cited':>8}{'rate':>8}   {'95% CI':<18}{'patents':>9}")
out={}
for name,w in arms.items():
    flags=[1 if oid in cited else 0 for oid in w]
    pats=set().union(*[cited[o] for o in w if o in cited]) if any(flags) else set()
    lo,hi=boot(flags)
    rate=float(np.mean(flags)) if flags else float("nan")
    print(f"{name:<24}{len(w):>9,}{sum(flags):>8,}{100*rate:>7.1f}%   [{100*lo:>5.1f},{100*hi:>5.1f}]%{len(pats):>9,}")
    era={}
    for lo_,hi_ in ERAS:
        f2=[1 if oid in cited else 0 for oid,inf in w.items()
            if inf["year"] and lo_<=inf["year"]<=hi_]
        era[f"{lo_}-{hi_}"]={"n":len(f2),"rate":(float(np.mean(f2)) if f2 else None)}
    out[name]={"n_works":len(w),"n_cited":int(sum(flags)),"rate":rate,"ci":[lo,hi],
               "n_patents":len(pats),"by_era":era,**meta[name]}

print(f"\n[by era] rate per subfield (n in parens)")
print(f"{'subfield':<24}"+"".join(f"{f'{a}-{b}':>18}" for a,b in ERAS))
for name in arms:
    cells=[]
    for a,b in ERAS:
        e=out[name]["by_era"][f"{a}-{b}"]
        cells.append(f"{(100*e['rate']):>6.1f}% (n={e['n']:,})" if e["rate"] is not None else f"{'--':>18}")
    print(f"{name:<24}"+"".join(f"{c:>18}" for c in cells))

if FAILURES:
    print("\n!! INCOMPLETE - these queries failed, rates above are NOT valid:")
    for a,q in FAILURES: print(f"     {a}: {q}")
    print("   re-run to resume from cache; results/arms.json NOT written")
    sys.exit(1)
(ROOT/"results"/"arms.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print("\n[done] -> results/arms.json")
