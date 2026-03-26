import json
import os

LEDGER_PATH = "runtime/external_verification.json"

def load():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def compare(prompt):

    data = load()

    # prompt一致の履歴抽出
    matched = [d for d in data if d["prompt"] == prompt]

    results = []

    for i, entry in enumerate(matched):
        results.append({
            "index": i,
            "analysis": entry["analysis"],
            "outputs": entry["analysis"].get("outputs", [])
        })

    # 差分検出
    diff = []
    if len(results) >= 2:
        base = results[0]["outputs"]

        for r in results[1:]:
            if r["outputs"] != base:
                diff.append({
                    "index": r["index"],
                    "different": True
                })
            else:
                diff.append({
                    "index": r["index"],
                    "different": False
                })

    return {
        "count": len(results),
        "results": results,
        "diff": diff
    }
