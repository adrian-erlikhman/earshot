"""Rebuild paper/BRIEF.pdf and check every headline number against the results files.

A brief is only useful if its numbers survive contact with the data, so this checks
the numbers against the files the pipeline wrote, not against what was typed into
the brief:
  1. TL;DR and draft abstract lengths against the form limits
  2. key strings actually present in the rendered PDF
  3. treatment rate and era-matched odds ratio   <- results/compare_arms.json
  4. applicant-name flips                        <- results/redaction_test.csv
  5. examiner-class counts                       <- results/patent_labels.csv + patent_meta
  6. HRL civil-unrest patent still surveillance  <- results/patent_labels.csv

    python tools/verify_brief.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pandas as pd  # noqa: E402
import pypdf  # noqa: E402
from md2pdf import convert  # noqa: E402

TLDR = ("Earshot links 127,851 ACL papers to the 9,048 USPTO patents citing them and classifies "
        "what those patents do. Surveillance is rare (0.46%) and not detectably more common than "
        "in science-citing patents of the same era; applicant names sway LLM labels.")

ABSTRACT = (
    "Kalluri et al. (2025) traced computer-vision research into surveillance patents. Whether "
    "language technology follows the same path is often asserted but rarely measured, and "
    "patent citations are easy to overread. We ask what the public patent record can reliably "
    "show. Earshot links 127,851 ACL Anthology papers through OpenAlex to the 9,048 USPTO "
    "patents that cite them, matching Zhang's (2025) paper count for the core venues (24,829 "
    "vs. 24,821), and classifies what those patents do. 91.6% of these citations appear only "
    "on a patent's front page. Our rubric separates a system's operator from its subject, and "
    "authentication from identification: verifying a claimed identity is not surveillance, "
    "while picking a person out of a population can be. Assignee names are hidden from the "
    "model and from two human coders (the authors); revealing them changed 32% of the model's "
    "non-neutral labels, in both directions. Of 69 patents examiners placed in "
    "surveillance-related technology classes, the rubric codes 2 as surveillance; nearly half "
    "of the rest are voice assistants. Coders agree with the model at [surveillance F1 = x; "
    "AC1 = y] on a stratified sample. In a random sample of 2,374 granted citing patents, 0.46% "
    "(95% CI 0.25–0.80%) are classified as surveillance, no subfield stands out, and the rate "
    "is not distinguishable from science-citing patents of the same grant era (odds ratio 1.03, "
    "95% CI 0.38–2.78). These results do not establish whether NLP flows into surveillance: "
    "patent abstracts often omit application detail, and citations show proximity, not "
    "transmission. Earshot shows how dual-use pathways can be studied without mistaking "
    "technical similarity, applicant identity, or citation for evidence of deployment.")

KEY_STRINGS = ["0.46%", "1.03", "0.38–2.78", "0 of 10", "32%", "64 as neither", "HRL",
               "0.33%", "24,829", "Never quote the crude ratio", "Proximity, Not Transmission"]

SURV_IPC = re.compile(r"G10L17|G06V40|G08B13|G07C9|H04N7/18")

failures = []


def check(name: str, ok: bool, detail: str) -> None:
    print(f"   [{'ok' if ok else 'FAIL'}] {name:<42} {detail}")
    if not ok:
        failures.append(name)


def flatten(text: str) -> str:
    lines = [ln.lstrip()[1:] if ln.lstrip().startswith(">") else ln for ln in text.splitlines()]
    return " ".join(" ".join(lines).split())


def main() -> None:
    md = ROOT / "paper" / "BRIEF.md"
    pdf = ROOT / "paper" / "BRIEF.pdf"
    flat_md = flatten(md.read_text(encoding="utf-8"))

    print("1. lengths")
    check("TL;DR <= 300", len(TLDR) <= 300, f"{len(TLDR)} chars")
    check("TL;DR matches BRIEF.md", TLDR in flat_md, "")
    check("draft abstract <= 2,500", len(ABSTRACT) <= 2500, f"{len(ABSTRACT)} chars")
    check("draft abstract matches BRIEF.md", ABSTRACT in flat_md, "")

    print("2. rendered PDF")
    convert(md, pdf)
    reader = pypdf.PdfReader(str(pdf))
    text = " ".join("".join(p.extract_text() for p in reader.pages).split())
    print(f"   {len(reader.pages)} pages")
    for k in KEY_STRINGS:
        check(f"present: {k}", k in text, "")

    print("3. rates and comparison  <- results/compare_arms.json")
    ca = json.loads((ROOT / "results" / "compare_arms.json").read_text(encoding="utf-8"))
    tc = ca["summary"]["treatment_crude"]
    check("treatment 11 of 2,374", tc["k"] == 11 and tc["n"] == 2374, f"{tc['k']}/{tc['n']}")
    check("treatment CI 0.25–0.80%", round(100 * tc["ci"][0], 2) == 0.25 and round(100 * tc["ci"][1], 2) == 0.80,
          f"[{100*tc['ci'][0]:.2f}, {100*tc['ci'][1]:.2f}]")
    rw = ca["control_reweighted_to_treatment_era_mix"]["rate"]
    check("control reweighted 0.41%", round(100 * rw, 2) == 0.41, f"{100*rw:.2f}%")
    mh = ca["mantel_haenszel"]
    check("MH OR 1.03 [0.38, 2.78]", round(mh["pooled_or"], 2) == 1.03 and round(mh["ci"][0], 2) == 0.38
          and round(mh["ci"][1], 2) == 2.78, f"{mh['pooled_or']:.2f} [{mh['ci'][0]:.2f}, {mh['ci'][1]:.2f}]")

    print("4. applicant-name flips  <- results/redaction_test.csv")
    rt = pd.read_csv(ROOT / "results" / "redaction_test.csv")
    rt["flip"] = rt["shown"] != rt["hidden"]
    nn = rt[rt["nonneither"]]
    check("10 of 31 non-neutral flip (32%)", int(nn["flip"].sum()) == 10 and len(nn) == 31,
          f"{int(nn['flip'].sum())}/{len(nn)}")
    check("deterministic 99 of 99", int((rt["hidden"] == rt["orig"]).sum()) == 99 and len(rt) == 99,
          f"{int((rt['hidden'] == rt['orig']).sum())}/{len(rt)}")

    print("5. examiner classes  <- patent_labels.csv + patent_meta")
    lab = pd.read_csv(ROOT / "results" / "patent_labels.csv")
    meta = {}
    for f in (ROOT / "data" / "interim" / "patent_meta").glob("*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("patent_id") and not r.get("_absent"):
            meta[r["patent_id"].upper().replace("-", "")] = r
    lab["ipc"] = lab["patent_id"].astype(str).str.upper().str.replace("-", "", regex=False) \
        .map(lambda k: (meta.get(k) or {}).get("ipc") or "")
    b = lab[lab["ipc"].str.contains(SURV_IPC, regex=True, na=False)]
    counts = b["label"].value_counts().to_dict()
    check("69 in surveillance-related classes", len(b) == 69, f"{len(b)}")
    check("2 surveillance / 64 neither", counts.get("surveillance") == 2 and counts.get("neither") == 64, str(counts))

    print("6. HRL example  <- patent_labels.csv")
    hrl = lab[lab["title"].astype(str).str.contains("civil unrest", case=False, na=False)]
    check("civil-unrest patent labelled surveillance", len(hrl) == 1 and hrl.iloc[0]["label"] == "surveillance",
          f"{hrl['label'].tolist()}")

    print()
    print("ALL CHECKS PASS" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
