"""Stage 3 — Reliance on Science patent->paper citations.

v65: USPTO-only, grant years 2015-2025, OpenAlex-keyed.
Header verified by range-request: reftype,confscore,oaid,patent,wherefound

`reftype` is the applicant-vs-examiner flag. Alcacer/Gittelman/Sampat show
examiners add a large share of citations, and an examiner citation only means a
patent office employee judged the paper relevant prior art - it does NOT mean the
assignee was reading us. So the applicant-only count is the real number, and we
find that out now rather than on day 8.
"""
from __future__ import annotations
import time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/"data"/"raw"
OUT = RAW/"pcs_oa_uspto.csv"
URL = "https://zenodo.org/records/21493744/files/pcs_oa_uspto.csv"

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    have = OUT.stat().st_size if OUT.exists() else 0
    if have > 1_400_000_000:
        print(f"[cache] already {have/1e6:.1f} MB"); return
    h = {"User-Agent":"ai4peace-research/1.0 (academic)"}
    if have: h["Range"]=f"bytes={have}-"; print(f"[resume] {have/1e6:.1f} MB")
    req = urllib.request.Request(URL, headers=h)
    t0=time.time(); n=have
    with urllib.request.urlopen(req, timeout=600) as r, open(OUT,"ab" if have else "wb") as f:
        print(f"[get ] HTTP {r.status}")
        while True:
            c=r.read(1<<20)
            if not c: break
            f.write(c); n+=len(c)
            if n % (100<<20) < (1<<20):
                print(f"       {n/1e6:>7.1f} MB ({n/1e6/max(time.time()-t0,1e-9):.1f} MB/s)")
    print(f"[done] {n/1e6:.1f} MB -> {OUT}")

if __name__=="__main__": main()
