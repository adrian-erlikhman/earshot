"""Michael's decisive test, step 1 — pull the SBIR/STTR award database.

One CSV, ~290 MB, no key, no registration:
  https://data.www.sbir.gov/awarddatapublic/award_data.csv

Streams to disk with resume, so a dropped connection is not a restart.
"""
from __future__ import annotations
import os, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = RAW / "sbir_award_data.csv"
URL = "https://data.www.sbir.gov/awarddatapublic/award_data.csv"

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    have = OUT.stat().st_size if OUT.exists() else 0
    if have > 200_000_000:
        print(f"[cache] {OUT.name} already {have/1e6:.1f} MB"); return
    headers = {"User-Agent": "ai4peace-research/1.0 (academic; contact via github)"}
    if have:
        headers["Range"] = f"bytes={have}-"
        print(f"[resume] from {have/1e6:.1f} MB")
    req = urllib.request.Request(URL, headers=headers)
    t0 = time.time(); n = have
    with urllib.request.urlopen(req, timeout=300) as r, open(OUT, "ab" if have else "wb") as f:
        total = r.headers.get("Content-Length")
        total = (int(total) + have) if total else None
        print(f"[get ] HTTP {r.status}" + (f", {total/1e6:.1f} MB expected" if total else ""))
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            f.write(chunk); n += len(chunk)
            if n % (25 << 20) < (1 << 20):
                el = time.time() - t0
                print(f"       {n/1e6:>7.1f} MB  ({n/1e6/max(el,1e-9):.1f} MB/s)")
    print(f"[done] {n/1e6:.1f} MB -> {OUT}")

if __name__ == "__main__":
    main()
