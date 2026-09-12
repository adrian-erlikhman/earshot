"""Stage 5 — fetch title / abstract / assignee for every citing patent.

Reliance on Science gives patent IDs only (`us-10494607-b2`). The entire
contribution lives in what those patents are FOR, so we need their text.

Two routes, in order of preference:

  uspto   api.uspto.gov Open Data Portal. Documented, official, needs a free
          key in USPTO_API_KEY. Verified reachable (returns 401 without a key,
          which means the host is live, unlike the retired PatentsView API
          which 301s to a transition-guide page).
  google  patents.google.com/xhr/query — the JSON endpoint their own search
          calls. No key, ~4 KB and ~0.4 s per patent (the HTML page is 1.6 MB).
          Undocumented, so we go slowly and cache aggressively. Fallback only.

Resumable: every response is cached by patent id, so a re-run costs nothing for
what it already has.

    python -m src.fetch_patent_meta --limit 50        # smoke test
    python -m src.fetch_patent_meta                   # all citing patents
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "interim" / "patent_meta"
RESULTS = ROOT / "results"
UA = {"User-Agent": "Mozilla/5.0 (compatible; academic research; contact via github.com/adrian-erlikhman/earshot)"}

_lock = threading.Lock()
_stats = {"cache": 0, "fetched": 0, "miss": 0, "err": 0}


def norm_id(pid: str) -> str:
    """'us-10494607-b2' -> 'US10494607B2'"""
    p = (pid or "").strip().upper().replace("-", "")
    return p


class TransientError(RuntimeError):
    """Request failed. NOT the same as 'this patent has no record' - caching the
    two the same way silently poisons the cache with recoverable failures."""


def gp_fetch(pid: str) -> dict | None:
    q = urllib.parse.quote(f"q={pid}", safe="")
    url = f"https://patents.google.com/xhr/query?url={q}"
    req = urllib.request.Request(url, headers=UA)
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.load(r)
            cl = (d.get("results") or {}).get("cluster") or []
            for c in cl:
                for item in c.get("result", []):
                    pat = item.get("patent") or {}
                    if not pat:
                        continue
                    if norm_id(pat.get("publication_number", "")) != pid:
                        continue          # guard: search can return a neighbour
                    return {
                        "patent_id": pid,
                        "title": pat.get("title"),
                        "abstract": pat.get("snippet"),
                        "assignee": pat.get("assignee"),
                        "inventor": pat.get("inventor"),
                        "grant_date": pat.get("grant_date"),
                        "filing_date": pat.get("filing_date"),
                        "priority_date": pat.get("priority_date"),
                        "source": "google",
                    }
            return None                    # searched fine, no matching patent
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep((20 * (i + 1)) + random.random() * 10)
                continue
            raise TransientError(f"HTTP {e.code}")
        except Exception as e:
            time.sleep(5 * (i + 1))
    raise TransientError("retries exhausted")


def one(pid: str, delay: float) -> dict | None:
    f = CACHE / f"{pid}.json"
    if f.exists():
        with _lock:
            _stats["cache"] += 1
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            f.unlink(missing_ok=True)
    time.sleep(delay + delay * random.random())
    try:
        rec = gp_fetch(pid)
    except TransientError:
        with _lock:
            _stats["err"] += 1
        return None                       # NOT cached - retry on the next run
    with _lock:
        if rec:
            _stats["fetched"] += 1
        else:
            _stats["miss"] += 1
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rec or {"patent_id": pid, "_absent": True}), encoding="utf-8")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sample", type=int, default=None,
                    help="random sample of patents instead of all. Rates estimated "
                         "from a sample with CIs are as valid as a census and cost "
                         "a quarter of the requests.")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=4, help="keep low; undocumented endpoint")
    ap.add_argument("--delay", type=float, default=0.5)
    a = ap.parse_args()

    if os.environ.get("USPTO_API_KEY"):
        print("[note] USPTO_API_KEY is set — the official ODP route is preferred;")
        print("       wire it in before a full run. Using Google for now.")

    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    pids = sorted({norm_id(p) for p in links["patent"].dropna().unique()})
    if a.sample and a.sample < len(pids):
        random.Random(a.seed).shuffle(pids)
        pids = sorted(pids[: a.sample])
        print(f"[samp ] random sample of {len(pids):,} (seed {a.seed})")
    if a.limit:
        pids = pids[: a.limit]
    print(f"[pat ] {len(pids):,} distinct citing patents to resolve")

    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [p for p in pids if not (CACHE / f"{p}.json").exists()]
    print(f"[pat ] {len(pids)-len(todo):,} already cached, {len(todo):,} to fetch")

    recs: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(one, p, a.delay): p for p in pids}
        for n, fu in enumerate(as_completed(futs), 1):
            r = fu.result()
            if r and not r.get("_miss"):
                recs.append(r)
            if n % 250 == 0:
                el = time.time() - t0
                rate = n / max(el, 1e-9)
                print(f"       {n:,}/{len(pids):,}  ok={len(recs):,}  "
                      f"cache={_stats['cache']:,} new={_stats['fetched']:,} miss={_stats['miss']:,}  "
                      f"{rate:.1f}/s  eta={(len(pids)-n)/max(rate,1e-9)/60:.0f}m")

    df = pd.DataFrame(recs)
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "patent_meta.csv"
    df.to_csv(out, index=False)

    print(f"\n[done] {len(df):,}/{len(pids):,} resolved ({100*len(df)/max(len(pids),1):.1f}%) -> {out}")
    print(f"       cache_hits={_stats['cache']:,} fetched={_stats['fetched']:,} "
          f"absent={_stats['miss']:,} transient_errors={_stats['err']:,} (will retry next run)")
    if len(df):
        for col in ("title", "abstract", "assignee"):
            if col in df:
                print(f"       {col:<10} present on {df[col].notna().sum():,} ({100*df[col].notna().mean():.1f}%)")
        print("\n[top assignees]")
        for k, v in df["assignee"].value_counts().head(15).items():
            print(f"   {str(k)[:52]:<52} {v:>5}")


if __name__ == "__main__":
    main()
