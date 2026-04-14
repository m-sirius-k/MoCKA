import json
import urllib.request
from pathlib import Path
from datetime import datetime

# パスの定義
ESSENCE_PATH  = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
PACKET_PATH   = Path("C:/Users/sirok/MoCKA/data/ping_latest.json")
OVERVIEW_PATH = Path("C:/Users/sirok/MOCKA_OVERVIEW.json")

# 固定ドメインの監視先
NGROK_URL = "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp"

def check_ngrok_status():
    """ngrokトンネルが生きているか、実際に通信して確認する"""
    try:
        headers = {
            "ngrok-skip-browser-warning": "69420",
            "User-Agent": "MoCKA-Monitor/2.0"
        }
        req = urllib.request.Request(NGROK_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"[MONITOR ERROR] {e}")
        return False

def generate_ping():
    # 各種ファイルの存在確認と読み込み
    if not ESSENCE_PATH.exists():
        print(f"[ERROR] ESSENCE_PATH not found: {ESSENCE_PATH}")
        return None

    data    = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    entries = data.get("essence", [])

    incident   = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "INCIDENT"),   None)
    philosophy = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "PHILOSOPHY"), None)
    operation  = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("type") == "OPERATION"),  None)

    # OVERVIEWの読み込み
    overview = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
    z_after  = overview.get("fluid_coordinate_theory", {}).get("current_values", {}).get("Z", 0.819)

    # ngrokの死活監視を実行
    ngrok_online = check_ngrok_status()

    new_incident   = incident["text"]   if incident   else "none"
    new_philosophy = philosophy["text"] if philosophy else "none"
    new_operation  = operation["text"]  if operation  else "none"

    essence_updated = True
    if PACKET_PATH.exists():
        prev = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        prev_summary = prev.get("ESSENCE_SUMMARY", {})
        if (prev_summary.get("INCIDENT")   == new_incident and
            prev_summary.get("PHILOSOPHY") == new_philosophy and
            prev_summary.get("OPERATION")  == new_operation):
            essence_updated = False

    packet = {
        "H": "MOCKA_DNA_v2",
        "G": 5.0,
        "C": "STRICT",
        "A": f"Z-Axis={z_after} / INCIDENT={new_incident[:40]}",
        "P": "SESSION_START_LOCK",
        "NGROK": ngrok_online,        # GUIの点灯スイッチ（本命）
        "ngrok_online": ngrok_online, # 互換用
        "essence_updated": essence_updated,
        "ESSENCE_SUMMARY": {
            "INCIDENT":   new_incident,
            "PHILOSOPHY": new_philosophy,
            "OPERATION":  new_operation,
        },
        "generated_at": datetime.now().isoformat()
    }

    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PACKET_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(packet, f, ensure_ascii=False, indent=2)

    print(f"[PING GENERATED] NGROK_STATUS={ngrok_online} | essence_updated={essence_updated}")
    return packet

if __name__ == "__main__":
    generate_ping()
