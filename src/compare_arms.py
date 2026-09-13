"""Treatment vs control, era-matched. The comparison the paper can actually report.

A crude comparison is confounded by grant era. Surveillance-classified patents are
concentrated in recent grants, and patents citing NLP research are recent (58% granted
May 2021 or later), while science-citing patents in general skew old (44% granted
1976-2014, 4% before 1976). A crude ratio therefore mostly measures era composition.

This script reports:
  - per-era surveillance rates for each arm
  - crude rates with exact Jeffreys intervals
  - the control rate reweighted to the treatment arm's era mix
  - a common-window test on granted utility patents from 1976
  - a Mantel-Haenszel pooled odds ratio across eras (0.5 continuity correction)
  - military labels per arm
  - record-type coverage: pre-grant application publications are not retrievable
    from the text source, so the classified sets are granted patents

Treatment is restricted to the seed-42 random sample drawn by fetch_patent_meta.py,
so the rate describes the 9,048 rather than whatever happened to be fetched first.

    python -m src.compare_arms
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, fisher_exact

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
INTERIM = ROOT / "data" / "interim"
ERAS = ["pre-1976", "1976-2014", "2015-May2021", "May2021+", "application", "design/other"]
WINDOW = ["1976-2014", "2015-May2021", "May2021+"]


def norm(pid) -> str:
    return str(pid).strip().upper().replace("-", "")


def era(pid) -> str:
    m = re.match(r"US([A-Z]*)0*(\d+)", norm(pid))
    if not m:
        return "design/other"
    if m.group(1):
        return "design/other"
    digits = m.group(2)
    if len(digits) >= 10:
        return "application"
    n = int(digits)
    if n < 3_930_271:
        return "pre-1976"
    if n < 8_925_000:
        return "1976-2014"
    if n < 11_000_000:
        return "2015-May2021"
    return "May2021+"


def jeffreys(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k + 0.5, n - k + 0.5))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 0.5, n - k + 0.5))
    return lo, hi


def seed42_sample() -> set[str]:
    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    pool = sorted({norm(p) for p in links["patent"].dropna().unique()})
    random.Random(42).shuffle(pool)
    return set(pool[:2500])


def load_arm(path: Path, restrict: set[str] | None) -> pd.DataFrame:
    df = pd.read_csv(path).dropna(subset=["label"]).copy()
    df["key"] = df["patent_id"].map(norm)
    if restrict is not None:
        df = df[df["key"].isin(restrict)]
    df = df.drop_duplicates("key").copy()
    df["era"] = df["key"].map(era)
    df["surv"] = (df["label"] == "surveillance").astype(int)
    df["mil"] = (df["label"] == "military_defense").astype(int)
    return df


def record_types(ids) -> dict:
    out: dict[str, int] = {}
    for i in ids:
        e = era(i)
        kind = "application" if e == "application" else ("design/other" if e == "design/other" else "granted utility")
        out[kind] = out.get(kind, 0) + 1
    return out


def absent_count(meta_dir: str) -> int:
    n = 0
    for f in (INTERIM / meta_dir).glob("*.json"):
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("_absent"):
                n += 1
        except Exception:
            pass
    return n


def main() -> None:
    samp = seed42_sample()
    T = load_arm(RESULTS / "patent_labels.csv", samp)
    C = load_arm(RESULTS / "control_labels.csv", None)
    out: dict = {"n_treatment": int(len(T)), "n_control": int(len(C)), "per_era": {}}

    print(f"treatment (seed-42 random sample, classified): {len(T):,}")
    print(f"control   (uniform over distinct patents, classified): {len(C):,}")

    links = pd.read_csv(RESULTS / "patent_links.csv", low_memory=False)
    ctl_ids = pd.read_csv(RESULTS / "control_patents.csv")["patent"]
    rt_t = record_types({norm(p) for p in links["patent"].dropna().unique()})
    rt_c = record_types(ctl_ids)
    print(f"record types, treatment population: {rt_t}")
    print(f"record types, control sample:       {rt_c}")
    print(f"404 on text source (application publications): treatment {absent_count('patent_meta')}, "
          f"control {absent_count('control_meta')}")
    out["record_types"] = {"treatment_population": rt_t, "control_sample": rt_c}

    print()
    print(f"{'era':<13} | {'TREATMENT surv/n   rate':<26} | {'CONTROL surv/n   rate':<26}")
    for e in ERAS:
        t, c = T[T["era"] == e], C[C["era"] == e]
        row = {}
        cells = []
        for name, d in (("treatment", t), ("control", c)):
            if len(d):
                k, n = int(d["surv"].sum()), len(d)
                row[name] = {"k": k, "n": n, "rate": k / n}
                cells.append(f"{k:>2}/{n:<5} {100 * k / n:5.2f}%")
            else:
                cells.append("-")
        out["per_era"][e] = row
        print(f"{e:<13} | {cells[0]:<26} | {cells[1]:<26}")

    print()
    summary = {}
    for name, d in (("treatment_crude", T), ("control_crude", C),
                    ("treatment_window", T[T["era"].isin(WINDOW)]),
                    ("control_window", C[C["era"].isin(WINDOW)])):
        k, n = int(d["surv"].sum()), len(d)
        lo, hi = jeffreys(k, n)
        summary[name] = {"k": k, "n": n, "rate": k / n, "ci": [lo, hi]}
        print(f"{name:<18} {k:>3}/{n:<5} = {100 * k / n:5.2f}%  [{100 * lo:.2f}, {100 * hi:.2f}]")
    out["summary"] = summary

    w = T["era"].value_counts(normalize=True)
    num = cov = 0.0
    for e, we in w.items():
        c = C[C["era"] == e]
        if len(c):
            num += we * c["surv"].mean()
            cov += we
    reweighted = num / cov if cov else float("nan")
    out["control_reweighted_to_treatment_era_mix"] = {"rate": reweighted, "weight_covered": cov}
    print(f"control reweighted to treatment era mix: {100 * reweighted:.2f}% "
          f"(covers {100 * cov:.0f}% of treatment weight)")

    tw, cw = summary["treatment_window"], summary["control_window"]
    _, p_fisher = fisher_exact([[tw["k"], tw["n"] - tw["k"]], [cw["k"], cw["n"] - cw["k"]]])
    out["fisher_common_window_p"] = float(p_fisher)
    print(f"Fisher exact, granted utility 1976+: p = {p_fisher:.3f}")

    try:
        from statsmodels.stats.contingency_tables import StratifiedTable
        tabs = []
        for e in WINDOW:
            t, c = T[T["era"] == e], C[C["era"] == e]
            if len(t) and len(c):
                tabs.append(np.array([[t["surv"].sum() + 0.5, len(t) - t["surv"].sum() + 0.5],
                                      [c["surv"].sum() + 0.5, len(c) - c["surv"].sum() + 0.5]]))
        st = StratifiedTable(tabs)
        lo, hi = st.oddsratio_pooled_confint()
        p_mh = float(st.test_null_odds().pvalue)
        out["mantel_haenszel"] = {"pooled_or": float(st.oddsratio_pooled), "ci": [float(lo), float(hi)],
                                  "p": p_mh, "strata": WINDOW, "continuity": 0.5}
        print(f"Mantel-Haenszel across eras: pooled OR {st.oddsratio_pooled:.2f} [{lo:.2f}, {hi:.2f}], p = {p_mh:.3f}")
    except Exception as ex:
        print(f"Mantel-Haenszel unavailable: {type(ex).__name__}: {ex}")

    mt, mc = int(T["mil"].sum()), int(C["mil"].sum())
    out["military"] = {"treatment": {"k": mt, "n": int(len(T))}, "control": {"k": mc, "n": int(len(C))}}
    print(f"military_defense: treatment {mt}/{len(T)}, control {mc}/{len(C)}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "compare_arms.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n[done] -> results/compare_arms.json")


if __name__ == "__main__":
    main()
