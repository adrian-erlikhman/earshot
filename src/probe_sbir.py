"""Michael's decisive test, step 2 — does the second result exist?

Three questions, in order of how badly a wrong answer would hurt:

  1. Abstract coverage. If DoD systematically withholds abstracts, or coverage
     collapses in some years, the whole lag design is unsound. Reported by year
     and by branch BEFORE any method counting.
  2. Do the agency/award counts match what we think they are?
  3. How often do named AI methods actually appear in defence award abstracts?

On (3) there is a trap in the obvious grep. `bert` is inside Albert, Roberts,
Bertrand, Gilbert; `clip` is inside clipping, clipped, paperclip; `gpt-` is
fine but `yolo` is not a word anyone writes by accident, and `llama` collides
with the animal and with Spanish "llamada". So every term is counted three ways:

  raw        naive substring, i.e. what a careless grep would report
  boundary   regex word boundary
  strict     word boundary AND an AI-context word within the same abstract

The gap between raw and strict is the finding here — it tells us how much of a
naive count is noise. If they are far apart, any headline built on a naive grep
is wrong, and we would rather learn that today than on day 8.

    python -m src.probe_sbir
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "sbir_award_data.csv"
RESULTS = ROOT / "results"

# Terms Michael listed, plus a couple that bound the same question.
TERMS = {
    "llama": r"\bllama[- ]?\d?\b",
    "mistral": r"\bmistral\b",
    "bert": r"\bbert\b",
    "whisper": r"\bwhisper\b",
    "yolo": r"\byolo\s?v?\d?\b",
    "stable diffusion": r"\bstable\s+diffusion\b",
    "clip": r"\bclip\b",
    "segment anything": r"\bsegment\s+anything\b",
    "gpt": r"\bgpt[-‑ ]?\d?\b",
    "transformer": r"\btransformers?\b",
    "diffusion model": r"\bdiffusion\s+model",
    "foundation model": r"\bfoundation\s+model",
    "large language model": r"\blarge\s+language\s+model",
}

AI_CONTEXT = re.compile(
    r"\b(neural|machine learning|deep learning|artificial intelligence|\bAI\b|"
    r"transformer|language model|embedding|fine[- ]?tun|pretrain|pre[- ]?train|"
    r"inference|dataset|training data|computer vision|natural language|LLM)\b",
    re.I,
)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def pick(header: list[str], *cands: str) -> str | None:
    low = {h.lower().strip(): h for h in header}
    for c in cands:
        if c in low:
            return low[c]
    for c in cands:                      # substring fallback
        for k, orig in low.items():
            if c in k:
                return orig
    return None


def main() -> None:
    if not CSV_PATH.exists():
        sys.exit(f"missing {CSV_PATH} — run `python -m src.fetch_sbir` first")

    size = CSV_PATH.stat().st_size
    print(f"[file] {CSV_PATH.name}  {size/1e6:.1f} MB\n")

    f = open(CSV_PATH, encoding="utf-8", errors="replace", newline="")
    rdr = csv.reader(f)
    header = next(rdr)
    print(f"[cols] {len(header)} columns")
    for i, h in enumerate(header):
        print(f"   {i:>2} {h}")

    c_agency = pick(header, "agency")
    c_branch = pick(header, "branch")
    c_year = pick(header, "award year", "award_year", "year")
    c_abs = pick(header, "abstract")
    c_prog = pick(header, "program")
    c_sol = pick(header, "solicitation number", "solicitation_number", "solicitation")
    print(f"\n[map ] agency={c_agency!r} branch={c_branch!r} year={c_year!r} "
          f"abstract={c_abs!r} program={c_prog!r} solicitation={c_sol!r}")
    if not (c_agency and c_abs):
        sys.exit("could not locate agency/abstract columns — inspect the header above")

    idx = {h: i for i, h in enumerate(header)}
    ia, ib = idx[c_agency], (idx[c_branch] if c_branch else None)
    iy = idx[c_year] if c_year else None
    iab = idx[c_abs]
    ip = idx[c_prog] if c_prog else None
    isol = idx[c_sol] if c_sol else None

    compiled = {k: re.compile(v, re.I) for k, v in TERMS.items()}

    n = 0
    agencies = Counter()
    by_year = Counter()
    abs_missing_by_year: dict[str, list[int]] = defaultdict(lambda: [0, 0])   # year -> [missing, total]
    abs_missing_by_branch: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    dod_abs_missing_by_year: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    raw_ct, bnd_ct, strict_ct = Counter(), Counter(), Counter()
    dod_n = dod_with_abs = 0
    sol_present = 0
    examples: dict[str, list[str]] = defaultdict(list)

    DEF = {"DOD", "DOW", "DEPARTMENT OF DEFENSE", "DEPARTMENT OF WAR"}

    for row in rdr:
        if len(row) <= max(ia, iab):
            continue
        n += 1
        agency = norm(row[ia]).upper()
        agencies[agency] += 1
        year = norm(row[iy]) if iy is not None and iy < len(row) else ""
        branch = norm(row[ib]).upper() if ib is not None and ib < len(row) else ""
        abstract = row[iab] if iab < len(row) else ""
        has_abs = len(norm(abstract)) >= 50

        if year:
            by_year[year] += 1
            abs_missing_by_year[year][1] += 1
            if not has_abs:
                abs_missing_by_year[year][0] += 1
        abs_missing_by_branch[branch or "(none)"][1] += 1
        if not has_abs:
            abs_missing_by_branch[branch or "(none)"][0] += 1

        is_def = agency in DEF or "DEFENSE" in agency or agency == "DOW" or "WAR" in agency
        if not is_def:
            continue
        dod_n += 1
        if has_abs:
            dod_with_abs += 1
        if isol is not None and isol < len(row) and norm(row[isol]):
            sol_present += 1
        if year:
            dod_abs_missing_by_year[year][1] += 1
            if not has_abs:
                dod_abs_missing_by_year[year][0] += 1
        if not has_abs:
            continue

        low = abstract.lower()
        ctx = None
        for term, rx in compiled.items():
            if term.split()[0] not in low and term not in low:
                continue
            raw_ct[term] += 1
            if rx.search(abstract):
                bnd_ct[term] += 1
                if ctx is None:
                    ctx = bool(AI_CONTEXT.search(abstract))
                if ctx:
                    strict_ct[term] += 1
                    if len(examples[term]) < 2:
                        m = rx.search(abstract)
                        s = max(0, m.start() - 90)
                        examples[term].append(norm(abstract[s:m.end() + 90]))
        if n % 50000 == 0:
            print(f"       ...{n:,} rows")

    f.close()

    print(f"\n[rows] {n:,} award records")
    print(f"\n[agency] top 15 of {len(agencies)}:")
    for k, v in agencies.most_common(15):
        print(f"   {k[:46]:<46} {v:>7,}")

    civ = sum(v for k, v in agencies.items()
              if any(x in k for x in ("HEALTH", "HHS", "NASA", "AERONAUTICS", "ENERGY", "DOE", "SCIENCE FOUNDATION", "NSF")))
    print(f"\n   defence-coded rows : {dod_n:,}")
    print(f"   HHS/NASA/DOE/NSF   : {civ:,}")

    yrs = sorted(y for y in by_year if y.isdigit())
    if yrs:
        print(f"\n[years] {yrs[0]}–{yrs[-1]}")

    print(f"\n[abstracts] defence awards with a usable abstract: {dod_with_abs:,}/{dod_n:,} "
          f"({100*dod_with_abs/max(dod_n,1):.1f}%)")
    if isol is not None:
        print(f"[solicitation id present on defence awards] {sol_present:,}/{dod_n:,} "
              f"({100*sol_present/max(dod_n,1):.1f}%)  <- needed for the topic-cadence split")

    print("\n[abstract coverage by year — ALL agencies] (missing% ; n)")
    for y in yrs:
        miss, tot = abs_missing_by_year[y]
        flag = "  <-- GAP" if tot > 200 and miss / tot > 0.5 else ""
        print(f"   {y}  {100*miss/max(tot,1):>5.1f}%  n={tot:>6,}{flag}")

    print("\n[abstract coverage by year — DEFENCE only] (missing% ; n)")
    for y in yrs:
        if y not in dod_abs_missing_by_year:
            continue
        miss, tot = dod_abs_missing_by_year[y]
        flag = "  <-- GAP" if tot > 100 and miss / tot > 0.5 else ""
        print(f"   {y}  {100*miss/max(tot,1):>5.1f}%  n={tot:>6,}{flag}")

    print("\n[abstract coverage by branch — worst 12]")
    rows = [(k, m, t) for k, (m, t) in abs_missing_by_branch.items() if t >= 200]
    for k, m, t in sorted(rows, key=lambda r: -r[1] / max(r[2], 1))[:12]:
        print(f"   {k[:40]:<40} {100*m/max(t,1):>5.1f}% missing  n={t:,}")

    print("\n[method mentions in DEFENCE award abstracts]")
    print(f"   {'term':<22}{'raw':>8}{'boundary':>10}{'strict':>9}   raw→strict")
    for term in TERMS:
        r, b, s = raw_ct[term], bnd_ct[term], strict_ct[term]
        drop = f"{100*(1-s/r):.0f}% noise" if r else "-"
        print(f"   {term:<22}{r:>8,}{b:>10,}{s:>9,}   {drop}")

    print("\n[examples of strict matches]")
    for term in ("llama", "bert", "clip", "gpt", "whisper"):
        for ex in examples.get(term, [])[:1]:
            print(f"   {term}: …{ex[:150]}…")

    RESULTS.mkdir(parents=True, exist_ok=True)
    import json
    (RESULTS / "sbir_probe.json").write_text(json.dumps({
        "n_rows": n, "defence_rows": dod_n, "civilian_4agency_rows": civ,
        "defence_with_abstract": dod_with_abs,
        "year_min": yrs[0] if yrs else None, "year_max": yrs[-1] if yrs else None,
        "raw": dict(raw_ct), "boundary": dict(bnd_ct), "strict": dict(strict_ct),
        "abstract_missing_by_year_all": {y: abs_missing_by_year[y] for y in yrs},
        "abstract_missing_by_year_defence": {y: dod_abs_missing_by_year[y] for y in sorted(dod_abs_missing_by_year)},
    }, indent=2), encoding="utf-8")
    print(f"\n[done] -> {RESULTS/'sbir_probe.json'}")


if __name__ == "__main__":
    main()
