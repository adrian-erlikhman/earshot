"""Assignee-reliance test, done properly.

The first redaction test (0 of 60 labels moved) used the pilot sample, whose
assignees were all benign commercial NLP firms. An assignee cannot flip a label
it has no reason to influence, so that test could not detect the failure it was
meant to catch. It then failed in practice: a botulism-antitoxin chemistry patent
was labelled military_defense because its assignee is the Academy of Military
Medical Sciences, which the rubric explicitly forbids.

This version targets the cases where assignee reliance would actually show:
  (a) every patent the model labelled anything other than `neither`, both arms
  (b) every patent whose assignee sounds defence / security / intelligence

Each is classified twice at temperature 0 — assignee shown, assignee redacted —
and flips are counted. The unredacted call reproduces the original prompt byte for
byte, so it is a cache hit and doubles as a consistency check.

    python -m src.redaction_test
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.classify_patents import api_key, build_prompt, call, _spend  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODEL = "google/gemini-2.5-flash-lite"
DEFENSE = re.compile(
    r"military|defen[cs]e|army|navy|air force|national security|lockheed|raytheon|"
    r"northrop|thales|bae systems|general dynamics|leidos|booz allen|palantir|"
    r"hrl laboratories|sandia|los alamos|livermore|triad national|mitre|anduril|"
    r"elbit|rafael|intelligence|homeland|academy of military", re.I)


def meta(d: str) -> dict:
    out = {}
    for f in (ROOT / "data" / "interim" / d).glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("patent_id") and not r.get("_absent"):
            out[r["patent_id"].upper().replace("-", "")] = r
    return out


def main() -> None:
    key = api_key()
    arms = [("treatment", "patent_labels.csv", "patent_meta"),
            ("control", "control_labels.csv", "control_meta")]
    rows = []
    for arm, lab_file, meta_dir in arms:
        lab = pd.read_csv(ROOT / "results" / lab_file).dropna(subset=["label"])
        mm = meta(meta_dir)
        for _, r in lab.iterrows():
            k = str(r["patent_id"]).upper().replace("-", "")
            m = mm.get(k)
            if not m:
                continue
            nonneither = r["label"] != "neither"
            defense = bool(DEFENSE.search(str(m.get("assignee") or "")))
            if nonneither or defense:
                rows.append((arm, r["label"], nonneither, defense, m))

    print(f"[set] {len(rows)} patents: "
          f"{sum(1 for x in rows if x[2])} non-neither, "
          f"{sum(1 for x in rows if x[3])} defence-sounding assignee")

    results = []
    for arm, orig, nonneither, defense, m in rows:
        shown = call(build_prompt(m), MODEL, 0.0, key)
        red = dict(m); red["assignee"] = "(redacted)"
        hidden = call(build_prompt(red), MODEL, 0.0, key)
        ls = ((shown or {}).get("parsed") or {}).get("label")
        lh = ((hidden or {}).get("parsed") or {}).get("label")
        results.append({"arm": arm, "orig": orig, "shown": ls, "hidden": lh,
                        "nonneither": nonneither, "defense": defense,
                        "assignee": m.get("assignee"), "title": m.get("title")})

    df = pd.DataFrame(results)
    df["consistent"] = df["shown"] == df["orig"]
    df["flipped"] = df["shown"] != df["hidden"]
    out = ROOT / "results" / "redaction_test.csv"
    df.to_csv(out, index=False)

    print(f"\n[consistency] unredacted re-call reproduces original label: "
          f"{df['consistent'].sum()}/{len(df)}")
    for name, mask in [("ALL targeted", slice(None)),
                       ("non-neither labels", df["nonneither"]),
                       ("defence-sounding assignee", df["defense"])]:
        s = df[mask]
        if len(s):
            print(f"[flips] {name:<28} {s['flipped'].sum()}/{len(s)} "
                  f"({100*s['flipped'].mean():.0f}%) change when the assignee is hidden")

    fl = df[df["flipped"]]
    print(f"\n[detail] {len(fl)} flipped:")
    for _, r in fl.iterrows():
        print(f"  {r['arm']:<9} {str(r['shown']):<18} -> {str(r['hidden']):<18} "
              f"{str(r['assignee'])[:28]:<28} {str(r['title'])[:40]}")
    print(f"\n[COST] ${_spend['cost']:.4f}   -> {out}")


if __name__ == "__main__":
    main()
