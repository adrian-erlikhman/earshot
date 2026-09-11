"""Is the speech arm recoverable? Speaker ID publishes at Interspeech and ICASSP,
not ACL. Both are in OpenAlex, and RoS keys on OpenAlex ids - so we do NOT need
the ACL Anthology for this. Find the source ids and size the opportunity."""
import json, urllib.parse, urllib.request, time

M="babafiraislife@gmail.com"
def oa(path, **p):
    p["mailto"]=M
    u=f"https://api.openalex.org/{path}?"+urllib.parse.urlencode(p)
    r=urllib.request.Request(u,headers={"User-Agent":f"ai4peace (mailto:{M})"})
    for i in range(4):
        try:
            with urllib.request.urlopen(r,timeout=60) as x: return json.load(x)
        except Exception as e:
            if i==3: return {"_e":str(e)}
            time.sleep(3*(i+1))

print("=== candidate speech venues in OpenAlex ===")
for q in ["Interspeech","ICASSP acoustics speech signal processing",
          "IEEE/ACM Transactions on Audio Speech and Language Processing",
          "Odyssey Speaker Language Recognition","Computer Speech and Language",
          "Speech Communication"]:
    d=oa("sources",search=q,per_page=5)
    if "_e" in d: print(f"  {q}: ERR"); continue
    print(f"\n  query: {q}")
    for s in d.get("results",[])[:5]:
        print(f"     {s['id'].rsplit('/',1)[-1]:>12}  works={s.get('works_count',0):>8,}  "
              f"{s.get('display_name','')[:64]}")
