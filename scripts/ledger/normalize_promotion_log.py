# ============================================
# MoCKA Promotion Log Normalizer
# promoted_branches.json を統一形式へ変換
# ============================================

import json
import time

FILE = "runtime/promoted_branches.json"

with open(FILE,"r",encoding="utf-8") as f:
    data = json.load(f)

normalized = []

for item in data:

    if isinstance(item,str):

        normalized.append({
            "timestamp":0,
            "branch":item,
            "fitness":0
        })

    else:

        normalized.append(item)

with open(FILE,"w",encoding="utf-8") as f:
    json.dump(normalized,f,indent=2)

print("PROMOTION LOG NORMALIZED")
