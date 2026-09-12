"""Stage 8 — build the hand-labelling sheet (rubric v1.2).

Stratified so the rare classes are actually present. At a ~0.7% surveillance rate
a simple random 200 would hold one or two positives and measure nothing about the
boundary that matters.

Strata (every patent belongs to exactly one):
  model_surveillance   model said surveillance              -> take all
  model_military       model said military_defense          -> take all
  model_dual_use       model said dual_use_ambiguous        -> take all
  neither_surv_ipc     model said neither, but the examiner assigned a
                       surveillance-type IPC class          -> take all (boundary)
  neither_other        everything else                      -> random fill to n

The fourth stratum matters most: it is exactly where model and examiner disagree,
so it is where a human judgement is informative. Inclusion weights (population /
sample, per stratum) go to strata.json so any rate from this sheet is reweighted
to the population; agreement.py refuses to print an unweighted population rate.

Coders see title + abstract only (assignee redacted, rubric v1.2), in independent
random order, with no model label.

    python -m src.build_goldset --n 200
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
META = ROOT / "data" / "interim" / "patent_meta"
GOLD = ROOT / "data" / "goldset"
SURV_IPC = re.compile(r"G10L17|G06V40|G08B13|G07C9|H04N7/18")
TAKE_ALL = ["model_surveillance", "model_military", "model_dual_use", "neither_surv_ipc"]


def load_meta() -> dict:
    out = {}
    for f in META.glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("patent_id") and not r.get("_absent"):
            out[r["patent_id"].upper().replace("-", "")] = r
    return out


def stratum(label: str, ipc: str) -> str:
    if label == "surveillance":
        return "model_surveillance"
    if label == "military_defense":
        return "model_military"
    if label == "dual_use_ambiguous":
        return "model_dual_use"
    if SURV_IPC.search(ipc or ""):
        return "neither_surv_ipc"
    return "neither_other"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260913)
    a = ap.parse_args()

    lab = pd.read_csv(RESULTS / "patent_labels.csv", low_memory=False)
    lab = lab.dropna(subset=["label"]).drop_duplicates("patent_id").copy()
    meta = load_meta()
    lab["key"] = lab["patent_id"].astype(str).str.upper().str.replace("-", "", regex=False)
    lab["ipc"] = lab["key"].map(lambda k: (meta.get(k) or {}).get("ipc") or "")
    lab["abstract"] = lab["key"].map(lambda k: (meta.get(k) or {}).get("abstract"))
    lab["stratum"] = [stratum(l, i) for l, i in zip(lab["label"], lab["ipc"])]

    pop = lab["stratum"].value_counts().to_dict()
    print(f"[pop ] {len(lab):,} labelled patents (assignee-redacted primary labels)")
    for k in TAKE_ALL + ["neither_other"]:
        print(f"       {k:<20} {pop.get(k, 0):>6,}")

    rng = np.random.default_rng(a.seed)
    gold = pd.concat([lab[lab["stratum"] == s] for s in TAKE_ALL])
    room = max(a.n - len(gold), 0)
    rest = lab[lab["stratum"] == "neither_other"]
    if room and len(rest):
        gold = pd.concat([gold, rest.sample(n=min(room, len(rest)),
                                            random_state=int(rng.integers(1e9)))])

    samp = gold["stratum"].value_counts().to_dict()
    weights = {k: pop.get(k, 0) / samp[k] for k in samp}
    rare = sum(samp.get(s, 0) for s in TAKE_ALL)
    print(f"[gold] {len(gold)} items: {rare} from rare/boundary strata, "
          f"{samp.get('neither_other', 0)} random neither")
    ms = samp.get("model_surveillance", 0)
    if ms < 30:
        print(f"  ! only {ms} model-surveillance items exist. The v1.1 surveillance-F1 gate")
        print("    will carry a very wide interval: report it as indicative, not decisive.")

    GOLD.mkdir(parents=True, exist_ok=True)
    (GOLD / "strata.json").write_text(json.dumps({
        "rubric": "v1.2", "seed": a.seed,
        "stratum_variable": "model label x surveillance-type IPC class",
        "population": pop, "sample": samp, "weights": weights,
    }, indent=2), encoding="utf-8")

    cols = ["patent_id", "title", "abstract"]      # assignee redacted, rubric v1.2
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

    gold[["patent_id", "label", "confidence", "stratum"]].rename(
        columns={"label": "model_label", "confidence": "model_confidence"}
    ).to_csv(GOLD / "_model_labels_DO_NOT_OPEN_BEFORE_CODING.csv", index=False)
    print("[out ] model labels + strata held separately")
    print()
    print("Reminder: title and abstract ONLY (assignee redacted, rubric v1.2). Do not look the patent up.")
    print("Rubric: configs/patent_rubric.md including AMENDMENTS v1.1 and v1.2.")


if __name__ == "__main__":
    main()
