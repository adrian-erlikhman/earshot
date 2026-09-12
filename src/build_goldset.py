"""Stage 8 — build Sunday's hand-labelling sheet.

Stratified on the MODEL's label (rubric v1.1, §4) so the positive class is ~100
rather than ~6. A simple random sample of 200 at pilot prevalence would be ~190
`neither` and would measure nothing about the boundary that matters.

Because it is stratified, any rate computed from it must be reweighted to the
population — `src/agreement.py` does that and refuses to print an unweighted rate.

Outputs two CSVs, one per coder, in a DIFFERENT random order each, with no model
label and no rationale. Coders must not see the model's answer or each other's.

    python -m src.build_goldset --n 200
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GOLD = ROOT / "data" / "goldset"
# target counts per model-label stratum
TARGET = {"surveillance": 80, "military_defense": 20, "dual_use_ambiguous": 50, "neither": 50}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260913)
    a = ap.parse_args()

    lab = pd.read_csv(RESULTS / "patent_labels.csv", low_memory=False)
    lab = lab.dropna(subset=["label"]).drop_duplicates("patent_id")
    print(f"[in ] {len(lab):,} classified patents")
    avail = lab["label"].value_counts().to_dict()
    print(f"[avail] {avail}")

    rng = np.random.default_rng(a.seed)
    picks = []
    for strat, want in TARGET.items():
        pool = lab[lab["label"] == strat]
        take = min(want, len(pool))
        if take < want:
            print(f"  ! {strat}: only {len(pool)} available, wanted {want}")
        if take:
            picks.append(pool.sample(n=take, random_state=int(rng.integers(1e9))))
    gold = pd.concat(picks) if picks else pd.DataFrame()

    # top up to n from whatever remains, so the sheet is always full length
    if len(gold) < a.n:
        rest = lab[~lab["patent_id"].isin(gold["patent_id"])]
        if len(rest):
            gold = pd.concat([gold, rest.sample(n=min(a.n - len(gold), len(rest)),
                                                random_state=int(rng.integers(1e9)))])

    strata = gold["label"].value_counts().to_dict()
    print(f"[gold] {len(gold)} items; stratum sizes {strata}")

    GOLD.mkdir(parents=True, exist_ok=True)
    # the weights needed to get back to population rates
    pop = lab["label"].value_counts().to_dict()
    weights = {k: pop.get(k, 0) / max(strata.get(k, 1), 1) for k in strata}
    (GOLD / "strata.json").write_text(json.dumps(
        {"population": pop, "sample": strata, "weights": weights,
         "seed": a.seed, "rubric": "v1.1"}, indent=2), encoding="utf-8")

    cols = ["patent_id", "title", "assignee", "abstract"]
    for c in cols:
        if c not in gold:
            gold[c] = None
    for coder in ("adrian", "michael"):
        sheet = gold[cols].sample(frac=1.0, random_state=int(rng.integers(1e9))).copy()
        sheet.insert(0, "item", range(1, len(sheet) + 1))
        sheet["label"] = ""            # surveillance | military_defense | dual_use_ambiguous | neither
        sheet["confidence"] = ""       # 1 | 2 | 3
        sheet["rationale"] = ""
        sheet["insufficient_info"] = ""
        out = GOLD / f"goldset_{coder}.csv"
        sheet.to_csv(out, index=False)
        print(f"[out ] {out}  ({len(sheet)} items, independent order)")

    # answer key, kept apart so it cannot be opened by accident
    gold[["patent_id", "label", "confidence"]].rename(
        columns={"label": "model_label", "confidence": "model_confidence"}
    ).to_csv(GOLD / "_model_labels_DO_NOT_OPEN_BEFORE_CODING.csv", index=False)
    print(f"[out ] model labels held separately")
    print("\nReminder: title, assignee and abstract only. Do not look the patent up.")
    print("Rubric is configs/patent_rubric.md including AMENDMENT v1.1.")


if __name__ == "__main__":
    main()
