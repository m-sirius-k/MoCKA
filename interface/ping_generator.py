import json, sys
from pathlib import Path
from datetime import datetime
ESSENCE_PATH  = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
PACKET_PATH   = Path("C:/Users/sirok/MoCKA/data/ping_latest.json")
OVERVIEW_PATH = Path("C:/Users/sirok/MOCKA_OVERVIEW.json")
import urllib.request
NGROK_URL = "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp"

def check_ngrok_status():
    try:
        req = urllib.request.Request(NGROK_URL, headers={"ngrok-skip-browser-warning":"69420","User-Agent":"MoCKA-Monitor/2.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.getcode() == 200
    except:
        return False

def generate_ping():
    data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))

    # 新形式（トップレベルキー）と旧形式（essenceリスト）の両対応
    if "INCIDENT" in data and "PHILOSOPHY" in data and "OPERATION" in data:
        # 新形式: トップレベルキーを直接参照
        new_incident   = data.get("INCIDENT",   "") or "none"
        new_philosophy = data.get("PHILOSOPHY", "") or "none"
        new_operation  = data.get("OPERATION",  "") or "none"
    else:
        # 旧形式: essenceリストから抽出
        entries = [e for e in data.get("essence", []) if isinstance(e, dict)]
        today   = datetime.now().strftime("%Y-%m-%d")
        def latest(etype):
            hits = [e for e in entries if e.get("type")==etype and e.get("timestamp","").startswith(today) and e.get("timestamp","")[11:16] < "19:00"]
            if not hits:
                hits = [e for e in entries if e.get("type")==etype and e.get("timestamp","").startswith(today)]
            if not hits:
                hits = [e for e in entries if e.get("type")==etype]
            return max(hits, key=lambda e: e.get("timestamp","")) if hits else None
        incident   = latest("INCIDENT")
        philosophy = latest("PHILOSOPHY")
        operation  = latest("OPERATION")
        new_incident   = incident["text"]   if incident   else "none"
        new_philosophy = philosophy["text"] if philosophy else "none"
        new_operation  = operation["text"]  if operation  else "none"

    overview = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
    z_after  = overview.get("fluid_coordinate_theory", {}).get("current_values", {}).get("Z", 0.819)
    ngrok_online = check_ngrok_status()

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
        "P": "SESSION_START_LOCK",
        "A": "Z-Axis=" + str(z_after) + " / INCIDENT=" + new_incident[:30],
        "ESSENCE_SUMMARY": {
            "INCIDENT":   new_incident,
            "PHILOSOPHY": new_philosophy,
            "OPERATION":  new_operation,
        },
        "essence_updated": essence_updated,
        "ngrok_online": ngrok_online,
        "NGROK": ngrok_online,
        "generated_at": datetime.now().isoformat()
    }
    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKET_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[PING GENERATED] NGROK_STATUS=" + str(ngrok_online) + " | essence_updated=" + str(essence_updated))
    return packet

if __name__ == "__main__":
    generate_ping()
