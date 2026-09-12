"""Check Adrian's 13-Sept abstract draft against the form limits and the data.

1. character counts vs the Google Form limits (abstract 2,500, TL;DR 300)
2. is the classified sample behind "0.69%" actually representative of the 9,048?
   Suspicion: metadata was fetched in SORTED patent-id order and stopped partway,
   and as strings "US10..." sorts before "US9...", so the partial set may be
   missing the older (pre-2018) grants entirely.
"""
import random
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

ABSTRACT = """Claims that NLP research feeds surveillance increasingly rely on patent citations, but those citations are easy to overread: most are prior-art disclosures rather than evidence that a research result was actually used. We ask a narrower question: what can the public patent record reliably show about the downstream uses of NLP research? We introduce Earshot, linking 127,851 ACL Anthology papers through OpenAlex to 9,048 distinct USPTO patents and developing a purpose-based framework for classifying what those patents actually do. Our rubric addresses boundary cases that make speech technologies especially misleading by separating the operator from the subject of analysis and, critically, authentication from identification: verifying a claimed identity is not surveillance, whereas selecting someone from a population can be. We further hide assignee names from both the model and human coders to prevent an applicant’s identity from substituting for evidence about the patent’s function. These distinctions materially change the picture. Examiner classifications and keyword-like proxies systematically overcount surveillance, often treating consumer voice authentication as surveillance, while assignee information can independently bias model judgments. In the current assignee-redacted sample, 0.69% of NLP-citing patents are classified as surveillance, and none of ten NLP subfields shows significant concentration. A science-citing control is too small to support a treatment-versus-control conclusion, so we treat that comparison only as a bound. These results do not establish that NLP does or does not flow into surveillance: patent abstracts suppress application detail, and citations establish proximity, not transmission. Instead, Earshot shows how dual-use pathways can be studied without mistaking technical similarity, applicant identity, or citation itself for evidence of deployment."""

TLDR = """Earshot links 127,851 ACL papers to 9,048 citing USPTO patents and classifies what those patents do. Surveillance is rare; examiner classes overcount it, and assignee names bias model labels. Patent citations measure proximity to downstream use, not technology transfer."""

TITLE = "Earshot: Measuring the Downstream Patent Footprint of NLP Research in Surveillance Applications"


def num(pid: str) -> int | None:
    m = re.search(r"(\d{6,})", str(pid))
    return int(m.group(1)) if m else None


def norm(pid: str) -> str:
    return str(pid).strip().upper().replace("-", "")


def main() -> None:
    print("=== 1. LENGTH ===")
    print(f"abstract : {len(ABSTRACT):,} chars (limit 2,500) -> "
          f"{'OVER by ' + str(len(ABSTRACT) - 2500) if len(ABSTRACT) > 2500 else 'fits, ' + str(2500 - len(ABSTRACT)) + ' spare'}")
    print(f"TL;DR    : {len(TLDR):,} chars (limit 300) -> "
          f"{'OVER by ' + str(len(TLDR) - 300) if len(TLDR) > 300 else 'fits, ' + str(300 - len(TLDR)) + ' spare'}")
    print(f"title    : {len(TITLE)} chars")

    print("\n=== 2. IS THE 0.69% SAMPLE REPRESENTATIVE? ===")
    links = pd.read_csv(ROOT / "results" / "patent_links.csv", low_memory=False)
    allp = sorted({norm(p) for p in links["patent"].dropna().unique()})
    lab = pd.read_csv(ROOT / "results" / "patent_labels.csv")
    labp = {norm(p) for p in lab["patent_id"]}

    # rebuild the seed-42 random sample exactly as fetch_patent_meta.py drew it
    shuf = list(allp)
    random.Random(42).shuffle(shuf)
    rand2500 = set(shuf[:2500])
    in_rand = labp & rand2500
    print(f"classified treatment patents        : {len(labp):,} of {len(allp):,}")
    print(f"  of which in the seed-42 random draw : {len(in_rand):,}")
    print(f"  of which NOT from the random draw   : {len(labp - rand2500):,}  (earlier sorted-order fetches)")

    def share_pre2018(ids):
        n = [num(i) for i in ids]
        n = [x for x in n if x]
        return sum(1 for x in n if x < 10_000_000) / max(len(n), 1), len(n)

    s_all, n_all = share_pre2018(allp)
    s_lab, n_lab = share_pre2018(labp)
    print(f"\nshare with patent number < 10,000,000 (granted before ~June 2018):")
    print(f"  all 9,048 citing patents : {100*s_all:5.1f}%  (n={n_all:,})")
    print(f"  classified 1,012         : {100*s_lab:5.1f}%  (n={n_lab:,})")

    yrs = pd.to_datetime(lab["grant_date"], errors="coerce", format="mixed").dt.year
    print("\ngrant years in the classified set:")
    print(yrs.value_counts(dropna=False).sort_index().to_string())

    print("\n=== 3. SAME CHECK, CONTROL ARM ===")
    ctl_all = pd.read_csv(ROOT / "results" / "control_patents.csv")["patent"].map(norm)
    ctl_lab = pd.read_csv(ROOT / "results" / "control_labels.csv")["patent_id"].map(norm)
    c_all, _ = share_pre2018(ctl_all)
    c_lab, _ = share_pre2018(ctl_lab)
    print(f"  all 2,500 sampled control : {100*c_all:5.1f}% pre-2018 numbers")
    print(f"  classified {len(ctl_lab):,}           : {100*c_lab:5.1f}% pre-2018 numbers")

    print("\n=== 4. RATE WITHIN THE CLEAN RANDOM SUBSET ONLY ===")
    lab["key"] = lab["patent_id"].map(norm)
    r = lab[lab["key"].isin(rand2500)]
    k = int((r["label"] == "surveillance").sum())
    print(f"  seed-42 subset: {k} surveillance of {len(r):,} = {100*k/max(len(r),1):.2f}%")


if __name__ == "__main__":
    main()
