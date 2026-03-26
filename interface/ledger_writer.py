import json
import time
import os

LEDGER_PATH = "runtime/external_verification.json"

def record(prompt, results, analysis):

    entry = {
        "timestamp": time.time(),
        "prompt": prompt,
        "results": results,
        "analysis": analysis
    }

    # ファイルなければ作成
    if not os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    # 追記
    with open(LEDGER_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
