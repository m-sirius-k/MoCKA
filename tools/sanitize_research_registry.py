import json
from pathlib import Path

p = Path(r"C:\Users\sirok\mocka-ecosystem\MoCKA\tools\research_experiments.json")

j = json.loads(p.read_text(encoding="utf-8-sig"))

exps = j.get("experiments", [])
fixed = []

def blank(x):
    if x is None:
        return True
    if isinstance(x,str) and x.strip()=="":
        return True
    if isinstance(x,dict) and not x:
        return True
    return False

bad = []

for i,e in enumerate(exps):

    if blank(e):
        bad.append((i,e))
        continue

    if isinstance(e,str):
        fixed.append(e.strip())
        continue

    if isinstance(e,dict):

        eid = e.get("id","")
        kind = e.get("kind","")

        if not isinstance(eid,str) or eid.strip()=="":
            bad.append((i,e))
            continue

        if not isinstance(kind,str) or kind.strip()=="":
            e["kind"] = "ps1"

        fixed.append(e)
        continue

    bad.append((i,e))

print("EXPERIMENTS_TOTAL:",len(exps))
print("BAD_ENTRIES:",len(bad))

for b in bad[:20]:
    print("BAD:",b)

j["experiments"] = fixed

p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print("FIXED_COUNT:",len(fixed))
print("REGISTRY_SANITIZED")
