"""Stage 9 — agreement statistics, per rubric AMENDMENTS v1.1 (gate) and v1.2 (redaction).

The v1 rule (omnibus Cohen's κ ≥ 0.6) was withdrawn because κ collapses under
skewed prevalence: two coders each 95% accurate score κ≈0.54 when one class is
95% of items, while raw agreement and Gwet's AC1 sit flat at ~0.93/0.92.

So: **the gate is per-class F1 on `surveillance`, humans as reference.**
κ is still reported, with its caveat, because hiding an unflattering statistic is
worse than explaining one.

Because the gold set is stratified on model label x surveillance-type IPC class, every population rate is
reweighted using data/goldset/strata.json. This script refuses to print an
unweighted population rate.

    python -m src.agreement
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "goldset"
RESULTS = ROOT / "results"
LABELS = ["surveillance", "military_defense", "dual_use_ambiguous", "neither"]
GATE = 0.60


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    po = float(np.mean(a == b))
    pe = sum(np.mean(a == l) * np.mean(b == l) for l in LABELS)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def gwet_ac1(a: np.ndarray, b: np.ndarray) -> float:
    """Prevalence-robust. This is the number to read when one class dominates."""
    po = float(np.mean(a == b))
    q = len(LABELS)
    pi = [(np.mean(a == l) + np.mean(b == l)) / 2 for l in LABELS]
    pe = sum(p * (1 - p) for p in pi) / (q - 1)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def per_class(ref: np.ndarray, hyp: np.ndarray, cls: str) -> dict:
    tp = int(((hyp == cls) & (ref == cls)).sum())
    fp = int(((hyp == cls) & (ref != cls)).sum())
    fn = int(((hyp != cls) & (ref == cls)).sum())
    p = tp / max(tp + fp, 1); r = tp / max(tp + fn, 1)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r,
            "f1": 2 * p * r / max(p + r, 1e-9)}


def boot_f1(ref: np.ndarray, hyp: np.ndarray, cls: str, n: int = 10000, seed: int = 0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        i = rng.integers(0, len(ref), len(ref))
        out.append(per_class(ref[i], hyp[i], cls)["f1"])
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main() -> None:
    need = [GOLD / "goldset_adrian.csv", GOLD / "goldset_michael.csv",
            GOLD / "_model_labels_DO_NOT_OPEN_BEFORE_CODING.csv", GOLD / "strata.json"]
    missing = [p.name for p in need if not p.exists()]
    if missing:
        raise SystemExit(f"missing: {missing}\nRun `python -m src.build_goldset` and complete coding first.")

    A = pd.read_csv(need[0]).dropna(subset=["label"])
    B = pd.read_csv(need[1]).dropna(subset=["label"])
    M = pd.read_csv(need[2])
    strata = json.loads(need[3].read_text(encoding="utf-8"))

    df = (A[["patent_id", "label", "confidence"]].rename(columns={"label": "a", "confidence": "conf_a"})
          .merge(B[["patent_id", "label"]].rename(columns={"label": "b"}), on="patent_id")
          .merge(M.rename(columns={"model_label": "m"})[["patent_id", "m", "stratum"]], on="patent_id"))
    for c in ("a", "b", "m"):
        df[c] = df[c].astype(str).str.strip().str.lower()
    bad = df[~df["a"].isin(LABELS) | ~df["b"].isin(LABELS)]
    if len(bad):
        print(f"[warn] {len(bad)} rows have an unrecognised label; dropping")
        df = df.drop(bad.index)
    print(f"[n] {len(df)} doubly-coded items\n")

    a, b, m = df["a"].to_numpy(), df["b"].to_numpy(), df["m"].to_numpy()

    print("=== HUMAN–HUMAN (internal consistency; both coders are the authors) ===")
    print(f"   raw agreement  {np.mean(a==b):.3f}")
    print(f"   Cohen's kappa  {cohen_kappa(a,b):.3f}   <- prevalence-sensitive, read with AC1")
    print(f"   Gwet's AC1     {gwet_ac1(a,b):.3f}")
    for c in LABELS:
        s = per_class(a, b, c)
        print(f"   {c:<20} P={s['precision']:.3f} R={s['recall']:.3f} F1={s['f1']:.3f}  (tp={s['tp']})")

    print("\n=== HUMAN–MODEL (humans as reference) ===")
    ref = np.where(a == b, a, None)
    mask = np.array([x is not None for x in ref])
    print(f"   consensus subset: {mask.sum()}/{len(df)} items where both coders agree")
    r2, m2 = a[mask], m[mask]
    print(f"   raw agreement  {np.mean(r2==m2):.3f}")
    print(f"   Cohen's kappa  {cohen_kappa(r2,m2):.3f}")
    print(f"   Gwet's AC1     {gwet_ac1(r2,m2):.3f}")
    res = {}
    for c in LABELS:
        s = per_class(r2, m2, c)
        lo, hi = boot_f1(r2, m2, c)
        res[c] = {**s, "f1_ci": [lo, hi]}
        print(f"   {c:<20} P={s['precision']:.3f} R={s['recall']:.3f} F1={s['f1']:.3f} "
              f"[{lo:.3f}, {hi:.3f}]  (tp={s['tp']})")

    f1s = res["surveillance"]["f1"]
    passed = f1s >= GATE
    print("\n" + "=" * 66)
    print(f"GATE (rubric v1.1): surveillance F1 = {f1s:.3f}  vs threshold {GATE}")
    print(f"  -> {'PASS — model labels may carry a headline number' if passed else 'FAIL — report hand-labelled counts ONLY, and say so in the abstract'}")
    print("=" * 66)

    print("\n=== POPULATION-REWEIGHTED RATES (gold set is stratified; raw rates are meaningless) ===")
    w = strata["weights"]; pop_total = sum(strata["population"].values())
    for c in LABELS:
        num = sum(w.get(s, 0) * ((df["stratum"] == s) & (df["a"] == c) & (df["b"] == c)).sum()
                  for s in strata["sample"])
        print(f"   {c:<20} reweighted share of all citing patents: {100*num/max(pop_total,1):.2f}%")
    print("   (human-consensus labels, reweighted by stratum: model label x IPC class)")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "agreement.json").write_text(json.dumps({
        "n": int(len(df)),
        "human_human": {"raw": float(np.mean(a == b)), "kappa": cohen_kappa(a, b), "ac1": gwet_ac1(a, b)},
        "human_model": {"raw": float(np.mean(r2 == m2)), "kappa": cohen_kappa(r2, m2),
                        "ac1": gwet_ac1(r2, m2), "per_class": res},
        "gate": {"metric": "surveillance_f1", "value": f1s, "threshold": GATE, "passed": bool(passed)},
    }, indent=2), encoding="utf-8")
    print("\n[done] -> results/agreement.json")


if __name__ == "__main__":
    main()
