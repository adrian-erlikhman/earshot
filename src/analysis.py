"""Stage 7 — the analysis that produces every number in the abstract.

Runs against whatever classification exists; prints coverage first so a partial
run is never mistaken for a complete one.

Produces:
  A. Headline — share of citing patents classified surveillance / military,
     with bootstrap 95% CIs, plus the same restricted to in-text citations.
  B. H1 proper — surveillance-citation rate BY SUBFIELD, the pre-registered
     test. Age-censored (papers <= 2019) as primary.
  C. H2 — time trend in the surveillance share of citing patents.
  D. Convergent validity — LLM label vs examiner-assigned IPC class. This is
     the one check that does not depend on our own rubric.
  E. Assignee concentration.

    python -m src.analysis
    python -m src.analysis --max-year 2019
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
RESULTS = ROOT / "results"

# Examiner-assigned classes that independently indicate the constructs we label.
IPC_SURVEILLANCE = {
    "G10L17": "speaker identification / voice biometrics",
    "G06V40": "biometric pattern recognition (face, iris, gait)",
    "G08B13": "burglar/theft alarm, intrusion detection",
    "G07C9":  "access control / entrance registration",
    "H04N7/18": "CCTV / closed-circuit television",
}


def boot_ci(x: np.ndarray, n: int = 10000, seed: int = 0) -> tuple[float, float]:
    if len(x) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(n, len(x)))].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    labels = pd.read_csv(RESULTS / "patent_labels.csv", low_memory=False)
    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    links["oaid"] = links["oaid"].astype(str)
    papers = pd.read_csv(INTERIM / "acl_openalex.csv", low_memory=False)
    papers = papers[papers["openalex_id"].notna()].copy()
    papers["oaid"] = papers["openalex_id"].astype(str).str.lstrip("Ww")
    return labels, links, papers


def load_rules() -> dict[str, re.Pattern]:
    rules, cur = {}, None
    for raw in (ROOT / "configs" / "subfields.yaml").read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            cur = line[:-1].strip(); rules[cur] = []
        elif line.strip().startswith("-") and cur:
            pat = line.strip()[1:].strip()
            if pat[:1] in "'\"" and pat[-1:] == pat[:1]:
                pat = pat[1:-1]
            rules[cur].append(pat)
    return {k: re.compile("|".join(f"(?:{p})" for p in v), re.I) for k, v in rules.items() if v}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-year", type=int, default=2019)
    a = ap.parse_args()

    labels, links, papers = load()
    labels["patent_norm"] = labels["patent_id"].astype(str).str.upper().str.replace("-", "", regex=False)
    links["patent_norm"] = links["patent"].astype(str).str.upper().str.replace("-", "", regex=False)

    all_pat = links["patent_norm"].nunique()
    lab_pat = labels["patent_norm"].nunique()
    cov = lab_pat / max(all_pat, 1)
    print("=" * 74)
    print(f"COVERAGE  {lab_pat:,} of {all_pat:,} citing patents classified ({100*cov:.1f}%)")
    if cov < 0.95:
        print("  *** PARTIAL. Every rate below is provisional and must not be quoted. ***")
    print("=" * 74)

    lab = labels.dropna(subset=["label"]).drop_duplicates("patent_norm")

    # ---------------------------------------------------------------- A. headline
    print("\n[A] HEADLINE — what are the citing patents for?")
    n = len(lab)
    for k in ("surveillance", "military_defense", "dual_use_ambiguous", "neither"):
        f = (lab["label"] == k).to_numpy(dtype=float)
        lo, hi = boot_ci(f)
        print(f"   {k:<20}{f.sum():>7,.0f}  {100*f.mean():>6.2f}%  [{100*lo:>5.2f}, {100*hi:>5.2f}]")
    surv = (lab["label"].isin(["surveillance", "military_defense"])).to_numpy(dtype=float)
    lo, hi = boot_ci(surv)
    print(f"   {'surveillance+military':<20}{surv.sum():>7,.0f}  {100*surv.mean():>6.2f}%  [{100*lo:>5.2f}, {100*hi:>5.2f}]")

    # in-text only — stronger evidence of use than a front-page disclosure
    intext = set(links.loc[links["wherefound"].isin(["bodyonly", "both"]), "patent_norm"])
    sub = lab[lab["patent_norm"].isin(intext)]
    if len(sub):
        f = (sub["label"] == "surveillance").to_numpy(dtype=float)
        lo, hi = boot_ci(f)
        print(f"\n   ABLATION, in-text citations only (n={len(sub):,}):")
        print(f"   surveillance        {f.sum():>7,.0f}  {100*f.mean():>6.2f}%  [{100*lo:>5.2f}, {100*hi:>5.2f}]")

    # ---------------------------------------------------------------- B. H1
    print(f"\n[B] H1 — surveillance-citation rate BY SUBFIELD (papers <= {a.max_year})")
    pw = papers[papers["year"] <= a.max_year].copy()
    pw["text"] = pw["title"].fillna("") + " " + pw["abstract"].fillna("")
    surv_pats = set(lab.loc[lab["label"] == "surveillance", "patent_norm"])
    l2 = links[links["patent_norm"].isin(set(lab["patent_norm"]))]
    paper_has_surv = set(l2.loc[l2["patent_norm"].isin(surv_pats), "oaid"])

    rules = load_rules()
    base = pw["oaid"].isin(paper_has_surv).to_numpy(dtype=float)
    blo, bhi = boot_ci(base)
    print(f"   {'BASE (all papers)':<24}{len(pw):>8,}{base.sum():>8,.0f}{100*base.mean():>8.2f}%  [{100*blo:.2f}, {100*bhi:.2f}]")
    rows = []
    for name, rx in rules.items():
        m = pw["text"].str.contains(rx, na=False)
        s = pw[m]
        if len(s) < 5:
            rows.append({"subfield": name, "n": int(len(s)), "rate": None}); continue
        f = s["oaid"].isin(paper_has_surv).to_numpy(dtype=float)
        lo, hi = boot_ci(f)
        rows.append({"subfield": name, "n": int(len(s)), "n_surv": int(f.sum()),
                     "rate": float(f.mean()), "ci": [lo, hi],
                     "excludes_base": bool(lo > base.mean() or hi < base.mean())})
    rows.sort(key=lambda r: -(r["rate"] or -1))
    for r in rows:
        if r["rate"] is None:
            print(f"   {r['subfield']:<24}{r['n']:>8,}   (n too small)"); continue
        print(f"   {r['subfield']:<24}{r['n']:>8,}{r['n_surv']:>8,}{100*r['rate']:>8.2f}%  "
              f"[{100*r['ci'][0]:.2f}, {100*r['ci'][1]:.2f}]{'  ***' if r['excludes_base'] else ''}")
    print("   *** = CI excludes the base rate")

    # ---------------------------------------------------------------- C. H2
    print("\n[C] H2 — surveillance share of citing patents over time")
    if "grant_date" in lab:
        yr = pd.to_datetime(lab["grant_date"], errors="coerce", format="mixed").dt.year
        t = pd.DataFrame({"year": yr, "surv": (lab["label"] == "surveillance").astype(int)}).dropna()
        for lo_, hi_ in [(2015, 2017), (2018, 2020), (2021, 2023), (2024, 2026)]:
            s = t[(t["year"] >= lo_) & (t["year"] <= hi_)]
            if len(s):
                b = boot_ci(s["surv"].to_numpy(dtype=float))
                print(f"   {lo_}–{hi_}: {100*s['surv'].mean():>6.2f}%  [{100*b[0]:.2f}, {100*b[1]:.2f}]  n={len(s):,}")

    # ---------------------------------------------------------------- D. IPC
    print("\n[D] CONVERGENT VALIDITY — LLM label vs examiner-assigned IPC class")
    meta_rows = []
    for f in (INTERIM / "patent_meta").glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("ipc"):
            meta_rows.append({"patent_norm": r["patent_id"].upper().replace("-", ""), "ipc": r["ipc"]})
    if meta_rows:
        md = pd.DataFrame(meta_rows).drop_duplicates("patent_norm")
        j = lab.merge(md, on="patent_norm", how="inner")
        print(f"   {len(j):,} patents have both a label and an IPC code")
        pat = "|".join(k.replace("/", r"\/") for k in IPC_SURVEILLANCE)
        j["ipc_surv"] = j["ipc"].str.contains(pat, na=False, regex=True)
        if j["ipc_surv"].any():
            ct = pd.crosstab(j["label"], j["ipc_surv"])
            print(ct.to_string())
            tp = ((j["label"] == "surveillance") & j["ipc_surv"]).sum()
            fp = ((j["label"] == "surveillance") & ~j["ipc_surv"]).sum()
            fn = ((j["label"] != "surveillance") & j["ipc_surv"]).sum()
            prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
            f1 = 2 * prec * rec / max(prec + rec, 1e-9)
            print(f"   vs IPC as reference: precision={prec:.3f} recall={rec:.3f} F1={f1:.3f}")
            print("   (IPC is a weak reference — it marks the technology, not the application —")
            print("    so treat this as convergent validity, not ground truth.)")
        else:
            print("   no surveillance-class IPC codes present in the labelled set yet")
    else:
        print("   no IPC codes captured yet (re-fetch in progress)")

    # ---------------------------------------------------------------- E. assignees
    print("\n[E] WHO OWNS THE SURVEILLANCE-CLASSIFIED PATENTS")
    sv = lab[lab["label"] == "surveillance"]
    if len(sv) and "assignee" in sv:
        for k, v in sv["assignee"].value_counts().head(15).items():
            print(f"   {str(k)[:52]:<52}{v:>5}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "analysis.json").write_text(json.dumps({
        "coverage": cov, "n_labelled": int(lab_pat), "n_patents": int(all_pat),
        "headline": {k: int((lab["label"] == k).sum()) for k in
                     ("surveillance", "military_defense", "dual_use_ambiguous", "neither")},
        "h1_subfields": rows, "max_year": a.max_year,
    }, indent=2), encoding="utf-8")
    print(f"\n[done] -> results/analysis.json")


if __name__ == "__main__":
    main()
