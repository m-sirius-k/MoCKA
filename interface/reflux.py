import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
PING_GEN     = Path("C:/Users/sirok/MoCKA/interface/ping_generator.py")

PHILOSOPHY_KEYWORDS = ['失敗は資産', '地道', '文明の基礎', '継承', '復元力', '本質', '哲学', '思想', '再現性', '縛る', '遊動座標', 'A+B/2', '制御可能性', '定量化', '信じない', '記録が', '証明']
INCIDENT_KEYWORDS   = ['インシデント', 'エラー', 'バグ', '捏造', '違反', 'INSTRUCTION_IGNORE', '再発', '誤検知', '不整合', 'INTEGRITY', 'ミス', '断絶', '失敗した', '未実行']
OPERATION_KEYWORDS  = ['router.py', 'commit', '修正', '実装', '手順', 'PowerShell', 'python', 'BAT', 'seal', 'ledger', 'CSV', 'ping_generator', 'essence_classifier']

def classify(text):
    for k in PHILOSOPHY_KEYWORDS:
        if k in text: return 'PHILOSOPHY'
    for k in INCIDENT_KEYWORDS:
        if k in text: return 'INCIDENT'
    for k in OPERATION_KEYWORDS:
        if k in text: return 'OPERATION'
    return 'PHILOSOPHY'

def reflux(text, source="Claude"):
    if len(text.strip()) < 20:
        print("[REFLUX] テキストが短すぎます。スキップ。")
        return None

    d = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    entries = d.get("essence", [])

    existing = [e.get("text","")[:30] for e in entries if isinstance(e, dict)]
    if text[:30] in existing:
        print("[REFLUX] 重複検知。スキップ。")
        return None

    entry = {
        "type": classify(text),
        "text": text[:200],
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    entries.append(entry)
    d["essence"] = entries
    d["filtered_count"] = len(entries)

    ESSENCE_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[REFLUX] 追記完了: type={entry['type']} | {text[:40]}")

    # ping自動更新
    subprocess.run(["python", str(PING_GEN)], capture_output=True)
    print("[REFLUX] ping_latest.json 自動更新完了")

    return entry

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    reflux(text)
