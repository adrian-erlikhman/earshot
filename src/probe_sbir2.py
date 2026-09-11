"""Does the LAG design have data? The modern-method grep came back near-zero, but
that may only mean the corpus predates them. Test older method families that
SHOULD be measurable, in BOTH arms, with adoption curves.

For each method: count of awards mentioning it, per arm, plus the year of the
1st, 5th, 25th and 100th mention. If the k-th mention doesn't exist, the
time-to-k-th-mention estimator Michael proposed has nothing to stand on.
"""
from __future__ import annotations
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path
csv.field_size_limit(min(sys.maxsize, 2**31-1))

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT/"data"/"raw"/"sbir_award_data.csv"

METHODS = {
 "neural network":        r"\bneural\s+net(work)?s?\b",
 "deep learning":         r"\bdeep\s+learning\b",
 "support vector machine":r"\bsupport\s+vector\s+machines?\b|\bSVMs?\b",
 "hidden markov model":   r"\bhidden\s+markov\b|\bHMMs?\b",
 "convolutional nn":      r"\bconvolutional\s+neural\b|\bCNNs?\b",
 "recurrent nn / lstm":   r"\brecurrent\s+neural\b|\bLSTMs?\b|\bRNNs?\b",
 "reinforcement learning":r"\breinforcement\s+learning\b",
 "random forest":         r"\brandom\s+forests?\b",
 "word embedding":        r"\bword\s+embedding|\bword2vec\b|\bGloVe\b",
 "generative adversarial":r"\bgenerative\s+adversarial\b|\bGANs?\b",
 "attention mechanism":   r"\battention\s+mechanism|\bself[- ]attention\b",
 "transformer":           r"\btransformers?\b",
 "bert":                  r"\bBERT\b",
 "gpt":                   r"\bGPT[-\u2011 ]?\d?\b",
 "large language model":  r"\blarge\s+language\s+models?\b|\bLLMs?\b",
 "diffusion model":       r"\bdiffusion\s+models?\b",
 "foundation model":      r"\bfoundation\s+models?\b",
}
# 'transformer' in defence abstracts is often an electrical transformer.
ELEC = re.compile(r"\b(voltage|winding|transformer\s+(core|oil|station)|power\s+transformer|magnetic|kVA|step[- ]down|step[- ]up|rectifi)", re.I)
AI_CTX = re.compile(r"\b(neural|machine learning|deep learning|artificial intelligence|language model|embedding|training data|dataset|inference|computer vision|natural language)\b", re.I)

CIV = ("HEALTH","HHS","NASA","AERONAUTICS","ENERGY","SCIENCE FOUNDATION","NSF")

def main():
    rx = {k: re.compile(v, re.I) for k,v in METHODS.items()}
    hits = defaultdict(lambda: defaultdict(list))   # method -> arm -> [years]
    f = open(CSV_PATH, encoding="utf-8", errors="replace", newline="")
    r = csv.reader(f); h = next(r); i = {c:n for n,c in enumerate(h)}
    ia, iy, iab = i["Agency"], i["Award Year"], i["Abstract"]
    n=0
    for row in r:
        if len(row) <= max(ia,iy,iab): continue
        n+=1
        ag=(row[ia] or "").upper(); ab=row[iab] or ""
        if len(ab)<50: continue
        yr=(row[iy] or "").strip()
        if not yr.isdigit(): continue
        arm = "defence" if ("DEFENSE" in ag or ag in ("DOD","DOW") or "WAR" in ag) else ("civilian" if any(c in ag for c in CIV) else None)
        if arm is None: continue
        for m,cre in rx.items():
            if not cre.search(ab): continue
            if m=="transformer" and ELEC.search(ab) and not AI_CTX.search(ab): continue
            hits[m][arm].append(int(yr))
    f.close()
    print(f"[rows scanned] {n:,}\n")
    print(f"{'method':<24}{'defence n':>10}{'civ n':>8}   {'def 1st/5th/25th/100th':<26}{'civ 1st/5th/25th/100th'}")
    out={}
    for m in METHODS:
        d=sorted(hits[m]["defence"]); c=sorted(hits[m]["civilian"])
        def ks(a):
            g=lambda k: str(a[k-1]) if len(a)>=k else "--"
            return f"{g(1)}/{g(5)}/{g(25)}/{g(100)}"
        print(f"{m:<24}{len(d):>10,}{len(c):>8,}   {ks(d):<26}{ks(c)}")
        out[m]={"defence_n":len(d),"civilian_n":len(c),
                "defence_years":{k:(d[k-1] if len(d)>=k else None) for k in (1,5,25,100)},
                "civilian_years":{k:(c[k-1] if len(c)>=k else None) for k in (1,5,25,100)}}
    (ROOT/"results"/"sbir_lag_probe.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print("\n[done] -> results/sbir_lag_probe.json")

if __name__=="__main__": main()
