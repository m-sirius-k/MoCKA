# ping_generator.py
# MoCKA-START.bat から呼び出される
# 最新essenceから上位エントリを抽出しDNAパケットを生成する

import json
from pathlib import Path
from datetime import datetime

ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
PACKET_PATH  = Path("C:/Users/sirok/MoCKA/data/storage/infield/PACKET/ping_latest.json")
OVERVIEW_PATH = Path("C:/Users/sirok/MOCKA_OVERVIEW.json")

def generate_ping():
    # 1. essenceロード
    data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    entries = data.get("essence", [])

    # 2. 種別ごとに最新1件ずつ抽出
    incident  = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "INCIDENT"),  None)
    philosophy= next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "PHILOSOPHY"), None)
    operation = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "OPERATION"),  None)

    # 3. Z軸実測値をOVERVIEWから取得
    overview = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
    z_after  = overview.get("fluid_coordinate_theory", {}).get("current_values", {}).get("Z", 0.819)

    # 4. DNAパケット生成
    packet = {
        "H": "MOCKA_DNA_v2",
        "G": 5.0,
        "C": "STRICT",
        "A": f"Z-Axis={z_after} / INCIDENT={incident['text'][:30] if incident else 'none'}",
        "P": "SESSION_START_LOCK",
        "ESSENCE_SUMMARY": {
            "INCIDENT":   incident["text"][:60]   if incident   else "none",
            "PHILOSOPHY": philosophy["text"][:60] if philosophy else "none",
            "OPERATION":  operation["text"][:60]  if operation  else "none",
        },
        "generated_at": datetime.now().isoformat()
    }

    # 5. 保存
    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKET_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[PING GENERATED]")
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return packet

if __name__ == "__main__":
    generate_ping()
