"""Decisive: is there a speaker-ID / voice-biometrics patent story AT ALL?

Forget venues. Pull OpenAlex works whose title/abstract match speaker-recognition
terms - wherever published - then join those OpenAlex ids against Reliance on
Science. If this comes back with thousands of patents, the speech arm is real and
lives outside the ACL Anthology. If it comes back thin, the speech framing dies.
"""
from __future__ import annotations
import csv, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
csv.field_size_limit(min(sys.maxsize,2**31-1))

ROOT=Path(__file__).resolve().parents[1]
M="babafiraislife@gmail.com"
QUERIES=["speaker recognition","speaker verification","speaker identification",
         "voice biometrics","speaker diarization","automatic speaker"]

def oa(**p):
    p["mailto"]=M
    u="https://api.openalex.org/works?"+urllib.parse.urlencode(p)
    r=urllib.request.Request(u,headers={"User-Agent":f"ai4peace (mailto:{M})"})
    for i in range(4):
        try:
            with urllib.request.urlopen(r,timeout=90) as x: return json.load(x)
        except Exception:
            if i==3: return None
            time.sleep(4*(i+1))

works={}
for q in QUERIES:
    cur="*"; got=0
    while cur and got<6000:
        d=oa(filter=f"title_and_abstract.search:{q}", per_page=200, cursor=cur,
             select="id,title,publication_year,primary_location")
        if not d: break
        for w in d.get("results",[]):
            oid=(w.get("id") or "").rsplit("/",1)[-1].lstrip("Ww")
            loc=(w.get("primary_location") or {}).get("source") or {}
            works[oid]={"title":w.get("title"),"year":w.get("publication_year"),
                        "venue":loc.get("display_name")}
        got+=len(d.get("results",[]))
        cur=(d.get("meta") or {}).get("next_cursor")
        if not d.get("results"): break
    print(f"  '{q}': {got:,} works (running distinct: {len(works):,})")

print(f"\n[oa] {len(works):,} distinct speaker-ID works")
wanted=set(works)

links=[]
with open(ROOT/"data"/"raw"/"pcs_oa_uspto.csv",encoding="utf-8",errors="replace",newline="") as f:
    r=csv.reader(f); h=next(r); i={c.strip().lower():k for k,c in enumerate(h)}
    n=0
    for row in r:
        n+=1
        if len(row)<=i["wherefound"]: continue
        if row[i["oaid"]].strip() in wanted:
            links.append((row[i["oaid"]].strip(), row[i["patent"]].strip(),
                          row[i["reftype"]].strip(), row[i["wherefound"]].strip()))
        if n%10_000_000==0: print(f"     {n:,} rows, {len(links):,} hits")

pats={l[1] for l in links}; paps={l[0] for l in links}
print(f"\n[RESULT] {len(links):,} links | {len(pats):,} distinct patents | {len(paps):,} distinct papers cited")
print(f"         {100*len(paps)/max(len(works),1):.1f}% of speaker-ID works are cited by >=1 patent")

from collections import Counter
vc=Counter(works[p]["venue"] for p in paps if works.get(p,{}).get("venue"))
print("\n  top venues among cited speaker-ID papers:")
for k,v in vc.most_common(10): print(f"     {str(k)[:60]:<60}{v:>5}")
top=Counter(l[0] for l in links)
print("\n  most-cited speaker-ID papers:")
for oid,c in top.most_common(8):
    w=works.get(oid,{}); print(f"     {c:>4} patents  ({w.get('year')})  {str(w.get('title'))[:66]}")
json.dump({"n_works":len(works),"n_links":len(links),"n_patents":len(pats),"n_papers":len(paps)},
          open(ROOT/"results"/"speaker_id_probe.json","w"),indent=2)
print("\n[done] -> results/speaker_id_probe.json")
