import json
from pathlib import Path

p = Path(r"C:\Users\sirok\mocka-ecosystem\MoCKA\tools\research_experiments.json")
j = json.loads(p.read_text(encoding="utf-8-sig"))

exps = j.get("experiments", [])
fixed = []
seen = set()

def add_obj(eid, kind="ps1", script=None, expect=None):
    eid = ("" if eid is None else str(eid)).strip()
    if not eid:
        return
    if eid in seen:
        return
    seen.add(eid)

    k = ("" if kind is None else str(kind)).strip() or "ps1"

    if script is None or str(script).strip()=="":
        script = fr"C:\Users\sirok\mocka-ecosystem\MoCKA\experiments\exp_{eid}.ps1"
    s = str(script).strip()

    obj = {"id": eid, "kind": k, "script": s}
    if expect:
        obj["expect_contains"] = list(expect)
    fixed.append(obj)

for e in exps:
    if e is None:
        continue

    # もし過去に文字列配列が混ざっていても救済する
    if isinstance(e, str):
        add_obj(e)
        continue

    if isinstance(e, dict):
        eid = e.get("id", "")
        kind = e.get("kind", "ps1")
        script = e.get("script", None)
        expect = e.get("expect_contains", None)
        add_obj(eid, kind=kind, script=script, expect=expect)
        continue

# 書き戻し（BOM無しUTF-8に統一）
j["experiments"] = fixed
p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("NORMALIZED_OK")
print("EXPERIMENTS_COUNT:", len(fixed))

# その場で空IDが無いことを保証
bad = [i for i,x in enumerate(fixed) if not x.get("id","").strip()]
print("BAD_ID_INDEXES:", bad)
