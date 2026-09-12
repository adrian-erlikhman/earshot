"""Stage 6 — classify citing patents against the rubric.

The model sees EXACTLY the text in `configs/patent_rubric.md`, plus one patent's
title / abstract / assignee. Nothing else. The human coders see the same, so
human-model agreement is measured on identical inputs — otherwise Cohen's κ is
comparing two different tasks and means nothing.

Every call is cached by md5(model + prompt + params) and every call's cost is
logged, so a re-run is free and the running spend is always known.

    python -m src.classify_patents --limit 50                    # pilot
    python -m src.classify_patents --model qwen/qwen3.7-flash    # pin a model
    python -m src.classify_patents --exclude-gold                # skip gold-set items
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "interim" / "llm_cache"
META = ROOT / "data" / "interim" / "patent_meta"
RESULTS = ROOT / "results"
LABELS = ("surveillance", "military_defense", "dual_use_ambiguous", "neither")

_lock = threading.Lock()
_spend = {"cost": 0.0, "calls": 0, "cached": 0, "errors": 0}


def api_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if line.strip().startswith("OPENROUTER_API_KEY="):
            k = line.split("=", 1)[1].strip()
            return "".join(c for c in k if c.isprintable() and ord(c) < 128)
    sys.exit("OPENROUTER_API_KEY not found in .env")


RUBRIC = (ROOT / "configs" / "patent_rubric.md").read_text(encoding="utf-8")

INSTRUCTION = """You are labelling patents for a study of how language-technology research reaches surveillance and military applications.

Apply the rubric below exactly as written. Code what the patent SAYS IT DOES — not what the assignee is known for, and not what the technology could theoretically enable.

<rubric>
{rubric}
</rubric>

Patent to classify:
  Title:    {title}
  Assignee: {assignee}
  Abstract: {abstract}

Respond with ONLY a JSON object, no prose, no markdown fence:
{{"label": one of {labels}, "confidence": 1|2|3, "rationale": "one sentence quoting the deciding words", "insufficient_info": true|false}}"""


def build_prompt(rec: dict) -> str:
    return INSTRUCTION.format(
        rubric=RUBRIC,
        title=(rec.get("title") or "").strip() or "(none)",
        assignee=(rec.get("assignee") or "").strip() or "(none)",
        abstract=(rec.get("abstract") or "").strip() or "(none)",
        labels=list(LABELS),
    )


def call(prompt: str, model: str, temperature: float, key: str) -> dict | None:
    sig = hashlib.md5(f"{model}|{temperature}|{prompt}".encode()).hexdigest()
    f = CACHE / f"{sig}.json"
    if f.exists():
        with _lock:
            _spend["cached"] += 1
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            f.unlink(missing_ok=True)

    body = {"model": model, "temperature": temperature, "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/adrian-erlikhman/earshot",
                 "X-Title": "Earshot"})
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503):
                time.sleep(5 * (i + 1)); continue
            with _lock:
                _spend["errors"] += 1
            return None
        except Exception:
            time.sleep(4 * (i + 1))
    else:
        with _lock:
            _spend["errors"] += 1
        return None

    txt = (d.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    cost = float((d.get("usage") or {}).get("cost") or 0.0)
    with _lock:
        _spend["cost"] += cost
        _spend["calls"] += 1

    m = re.search(r"\{.*\}", txt, re.S)
    parsed = None
    if m:
        try:
            parsed = json.loads(m.group(0))
        except Exception:
            parsed = None
    out = {"raw": txt, "parsed": parsed, "cost": cost,
           "model_served": d.get("model"), "usage": d.get("usage")}
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out), encoding="utf-8")
    return out


def load_meta(meta_dir: Path | None = None) -> list[dict]:
    recs = []
    for f in sorted((meta_dir or META).glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("_absent") or r.get("_miss"):
            continue
        if not (r.get("title") or r.get("abstract")):
            continue
        recs.append(r)
    return recs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="google/gemini-2.5-flash-lite")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-spend", type=float, default=10.0,
                    help="abort before exceeding this many dollars in one run")
    ap.add_argument("--out", default="patent_labels.csv")
    ap.add_argument("--redact-assignee", action="store_true",
                    help="rubric v1.2 primary specification; true assignee still recorded")
    ap.add_argument("--meta-dir", default=None,
                    help="e.g. control_meta or speech_meta; each arm keeps its own cache")
    a = ap.parse_args()

    key = api_key()
    recs = load_meta(ROOT / "data" / "interim" / a.meta_dir if a.meta_dir else None)
    if a.limit:
        recs = recs[: a.limit]
    print(f"[in   ] {len(recs):,} patents with usable metadata")
    print(f"[model] {a.model}  temp={a.temperature}  budget cap=${a.max_spend:.2f}")
    print(f"[rubric] {len(RUBRIC):,} chars — the coders see this same text\n")

    rows = []
    t0 = time.time()

    def work(rec):
        if _spend["cost"] > a.max_spend:
            return None
        prompt_rec = dict(rec)
        if a.redact_assignee:
            prompt_rec["assignee"] = "(redacted)"   # rubric v1.2: never judge on the applicant
        d = call(build_prompt(prompt_rec), a.model, a.temperature, key)
        if not d:
            return None
        p = d.get("parsed") or {}
        lab = p.get("label")
        return {"patent_id": rec["patent_id"], "title": rec.get("title"),
                "assignee": rec.get("assignee"), "grant_date": rec.get("grant_date"),
                "label": lab if lab in LABELS else None,
                "confidence": p.get("confidence"),
                "rationale": p.get("rationale"),
                "insufficient_info": p.get("insufficient_info"),
                "unparsed": d.get("raw") if lab not in LABELS else None,
                "model": a.model}

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(work, r) for r in recs]
        for n, fu in enumerate(as_completed(futs), 1):
            r = fu.result()
            if r:
                rows.append(r)
            if n % 100 == 0:
                print(f"       {n:,}/{len(recs):,}  ${_spend['cost']:.4f}  "
                      f"calls={_spend['calls']:,} cached={_spend['cached']:,} err={_spend['errors']}")

    df = pd.DataFrame(rows)
    RESULTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS / a.out, index=False)

    print(f"\n[done] {len(df):,} labelled in {time.time()-t0:.0f}s -> results/{a.out}")
    print(f"[COST] ${_spend['cost']:.4f} this run  "
          f"({_spend['calls']:,} calls, {_spend['cached']:,} cache hits, {_spend['errors']} errors)")
    if len(df):
        bad = df["label"].isna().sum()
        if bad:
            print(f"[warn] {bad} responses did not parse into a valid label")
        print("\n[label distribution]")
        for k, v in df["label"].value_counts(dropna=False).items():
            print(f"   {str(k):<22} {v:>6,}  ({100*v/len(df):.1f}%)")
        if "confidence" in df:
            print("\n[confidence]")
            for k, v in df["confidence"].value_counts(dropna=False).sort_index().items():
                print(f"   {k}: {v:,}")
        ii = df["insufficient_info"].fillna(False)
        print(f"\n[insufficient_info] {ii.sum():,} ({100*ii.mean():.1f}%) — "
              f">10% would be a finding about the metadata, not the patents")


if __name__ == "__main__":
    main()
