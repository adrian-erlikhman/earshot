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
    """95% interval for a rate.

    For binary 0/1 data this returns the exact JEFFREYS interval, not a bootstrap.
    A bootstrap of an all-zero sample collapses to [0, 0], which "excludes" any
    positive base rate and flags a zero-event cell as significant. That produced
    six spurious *** marks in the H1 table on 2026-09-12. Rare events are the whole
    regime here (surveillance ~1%), so exact intervals are required, not optional.
    """
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return float("nan"), float("nan")
    if np.isin(x, (0.0, 1.0)).all():
        from scipy.stats import beta
        k, m = int(x.sum()), len(x)
        lo = 0.0 if k == 0 else float(beta.ppf(0.025, k + 0.5, m - k + 0.5))
        hi = 1.0 if k == m else float(beta.ppf(0.975, k + 0.5, m - k + 0.5))
        return lo, hi
    rng = np.random.default_rng(seed)
    b = x[rng.integers(0, len(x), size=(n, len(x)))].mean(axis=1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


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
        print("  NOTE: classified set is the seed-42 random sample of 2,500 (granted patents only). Rates are sample estimates with exact intervals, not a census.")
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

    # ------------------------------------------------- A2. CONTROL COMPARISON
    print("\n[A2] CONTROL — is the NLP rate different from science-citing patents generally?")
    ctl_path = RESULTS / "control_labels.csv"
    if ctl_path.exists():
        ctl = pd.read_csv(ctl_path).dropna(subset=["label"]).drop_duplicates("patent_id")
        t = (lab["label"] == "surveillance").to_numpy(dtype=float)
        c = (ctl["label"] == "surveillance").to_numpy(dtype=float)
        tlo, thi = boot_ci(t); clo, chi = boot_ci(c)
        print(f"   treatment (cites ACL) {t.sum():>5,.0f}/{len(t):<6,} = {100*t.mean():>5.2f}%  [{100*tlo:.2f}, {100*thi:.2f}]")
        print(f"   control   (no ACL)    {c.sum():>5,.0f}/{len(c):<6,} = {100*c.mean():>5.2f}%  [{100*clo:.2f}, {100*chi:.2f}]")
        # risk ratio with a bootstrap CI
        rng = np.random.default_rng(0)
        rr = []
        for _ in range(10000):
            a1 = t[rng.integers(0, len(t), len(t))].mean()
            a2 = c[rng.integers(0, len(c), len(c))].mean()
            if a2 > 0:
                rr.append(a1 / a2)
        if rr:
            print(f"   risk ratio {np.mean(rr):.2f}x  [{np.percentile(rr,2.5):.2f}, {np.percentile(rr,97.5):.2f}]")
        try:
            from scipy import stats as _st
            tab = [[int(t.sum()), int(len(t)-t.sum())], [int(c.sum()), int(len(c)-c.sum())]]
            _, pv = _st.fisher_exact(tab)
            print(f"   Fisher exact p = {pv:.4g}   {'SIGNIFICANT' if pv<0.05 else 'not significant'}")
        except Exception:
            pass
        print("   NOTE: control is 'the average science-citing USPTO patent', NOT field-matched. CRUDE and era-confounded: report src/compare_arms.py (Mantel-Haenszel) instead.")
    else:
        print("   *** control_labels.csv missing — THE PRE-REGISTERED CONTROL HAS NOT RUN. ***")
        print("   Without it the headline rate is uninterpretable. Do not draft around it.")

    # ---------------------------------------------------------------- B. H1
    print()
    print(f"[B] H1 — surveillance-citation rate BY SUBFIELD (papers <= {a.max_year})")
    print("    Fisher exact per subfield vs rest of corpus; Benjamini-Hochberg q (pre-registered).")
    print("    A lone flag on one event is what chance produces across ten tests.")
    pw = papers[papers["year"] <= a.max_year].copy()
    pw["text"] = pw["title"].fillna("") + " " + pw["abstract"].fillna("")
    surv_pats = set(lab.loc[lab["label"] == "surveillance", "patent_norm"])
    l2 = links[links["patent_norm"].isin(set(lab["patent_norm"]))]
    paper_has_surv = set(l2.loc[l2["patent_norm"].isin(surv_pats), "oaid"])
    pw["surv"] = pw["oaid"].isin(paper_has_surv)

    from scipy.stats import fisher_exact
    rules = load_rules()
    base = pw["surv"].to_numpy(dtype=float)
    blo, bhi = boot_ci(base)
    print(f"   {'BASE (all papers)':<24}{len(pw):>8,}{int(base.sum()):>6,}{100*base.mean():>8.2f}%  [{100*blo:.2f}, {100*bhi:.2f}]")
    rows = []
    for name, rx in rules.items():
        msk = pw["text"].str.contains(rx, na=False)
        inn, outs = pw[msk], pw[~msk]
        if len(inn) < 5:
            rows.append({"subfield": name, "n": int(len(inn)), "rate": None})
            continue
        in_s = int(inn["surv"].sum()); in_n = len(inn) - in_s
        out_s = int(outs["surv"].sum()); out_n = len(outs) - out_s
        _, pval = fisher_exact([[in_s, in_n], [out_s, out_n]])
        lo, hi = boot_ci(inn["surv"].to_numpy(dtype=float))
        rows.append({"subfield": name, "n": int(len(inn)), "n_surv": in_s,
                     "rate": in_s / len(inn), "ci": [lo, hi], "p": float(pval)})

    tested = [r for r in rows if r.get("rate") is not None]
    order = sorted(range(len(tested)), key=lambda i: tested[i]["p"])
    mtot = len(tested)
    prev = 1.0
    for rank in range(mtot - 1, -1, -1):
        i = order[rank]
        qv = min(prev, tested[i]["p"] * mtot / (rank + 1))
        tested[i]["q"] = float(min(qv, 1.0))
        prev = tested[i]["q"]
    for r in tested:
        r["significant"] = bool(r["q"] < 0.05)

    rows.sort(key=lambda r: -(r["rate"] if r.get("rate") is not None else -1))
    print(f"   {'subfield':<24}{'n':>8}{'surv':>6}{'rate':>9}  {'95% CI':<17}{'p':>8}{'q(BH)':>9}")
    for r in rows:
        if r.get("rate") is None:
            print(f"   {r['subfield']:<24}{r['n']:>8,}   (n too small)")
            continue
        flag = "  SIG" if r["significant"] else ""
        print(f"   {r['subfield']:<24}{r['n']:>8,}{r['n_surv']:>6}{100*r['rate']:>8.2f}%  "
              f"[{100*r['ci'][0]:.2f}, {100*r['ci'][1]:.2f}]{r['p']:>9.3f}{r['q']:>9.3f}{flag}")
    nsig = sum(1 for r in tested if r["significant"])
    print(f"   {nsig} of {mtot} subfields significant at BH q < 0.05")

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
