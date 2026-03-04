import json
from pathlib import Path

p = Path(r"C:\Users\sirok\mocka-ecosystem\MoCKA\tools\research_experiments.json")

# BOM対応
j = json.loads(p.read_text(encoding="utf-8-sig"))

exps = j.get("experiments", [])
fixed = []

def is_blank(x):
    return x is None or (isinstance(x, str) and x.strip() == "")

for e in exps:
    if e is None:
        continue

    if isinstance(e, str):
        if e.strip() == "":
            continue
        fixed.append(e.strip())
        continue

    if isinstance(e, dict):
        exp_id = e.get("id", "")
        if is_blank(exp_id):
            continue
        kind = e.get("kind", "")
        if is_blank(kind):
            e["kind"] = "ps1"
        fixed.append(e)
        continue

# string配列なら docs_link_audit を確実に追加
if fixed and isinstance(fixed[0], str):
    if "docs_link_audit" not in fixed:
        fixed.append("docs_link_audit")

j["experiments"] = fixed

# 書き戻しは BOM無しUTF-8 に統一（以後の事故を防ぐ）
p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("FIX_OK")
print("EXPERIMENTS_COUNT:", len(fixed))
