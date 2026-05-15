import json

def _get_alert_pending():
    """prevention_queue.jsonの未承認件数を返す"""
    try:
        pq = Path(__file__).parent.parent / "data" / "prevention_queue.json"
        if pq.exists():
            items = json.load(open(pq, encoding="utf-8"))
            pending = [i for i in (items if isinstance(items, list) else [])
                       if str(i.get("status","")).lower() in ("pending","未承認","")]
            if pending:
                top = (pending[0].get("summary") or pending[0].get("action")
                       or pending[0].get("description",""))[:60]
                return {"count": len(pending), "top": top}
    except Exception:
        pass
    return None

def _inject_alert_pending_to_ping():
    """ping_latest.jsonにalert_pendingを後付け注入"""
    pending = _get_alert_pending()
    pj = Path(__file__).parent.parent / "data" / "ping_latest.json"
    if not pj.exists():
        return
    try:
        data = json.load(open(pj, encoding="utf-8"))
        data["alert_pending"] = pending
        json.dump(data, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] alert_pending: {e}")

import json, sys
from pathlib import Path
from datetime import datetime
import sqlite3
DB_PATH       = Path("C:/Users/sirok/MoCKA/data/mocka_events.db")
PACKET_PATH   = Path("C:/Users/sirok/MoCKA/data/ping_latest.json")
OVERVIEW_PATH = Path("C:/Users/sirok/MOCKA_OVERVIEW.json")
import urllib.request
NGROK_URL = "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp"

def check_ngrok_status():
    try:
        req = urllib.request.Request("http://localhost:5000/ngrok/status", headers={"User-Agent":"MoCKA-Monitor/2.0"})
        with urllib.request.urlopen(req, timeout=1) as r:
            data = json.loads(r.read().decode())
            return data.get("status") == "online"
    except:
        return False

def _read_essence_from_db():
    """SQLiteのessenceテーブルから3軸を読む"""
    try:
        con = sqlite3.connect(str(DB_PATH))
        rows = con.execute("SELECT axis, content FROM essence").fetchall()
        con.close()
        d = {r[0]: r[1] for r in rows}
        return (
            d.get("INCIDENT",   "") or "none",
            d.get("PHILOSOPHY", "") or "none",
            d.get("OPERATION",  "") or "none",
        )
    except Exception as e:
        print(f"[WARN] DB読み込み失敗: {e}")
        return "none", "none", "none"

def generate_ping():
    new_incident, new_philosophy, new_operation = _read_essence_from_db()

    overview = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
    z_after  = overview.get("fluid_coordinate_theory", {}).get("current_values", {}).get("Z", 0.819)
    ngrok_online = check_ngrok_status()

    essence_updated = True
    if PACKET_PATH.exists():
        prev = json.loads(PACKET_PATH.read_text(encoding="utf-8-sig"))
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
        "current_phase": overview.get("current_phase", "Phase 2進行中"),
        "top_todos": sorted(
            [
                {"id": t.get("id",""), "title": t.get("title",""), "priority": t.get("priority","")}
                for t in json.loads(Path("C:/Users/sirok/MOCKA_TODO.json").read_text(encoding="utf-8-sig")).get("todos",[])
                if t.get("status","") not in ["完了"]
            ],
            key=lambda x: {"最高":0,"高":1,"中":2,"低":3}.get(x["priority"], 9)
        )[:5],
        "generated_at": datetime.now().isoformat()
    }
    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    PACKET_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[PING GENERATED] NGROK_STATUS=" + str(ngrok_online) + " | essence_updated=" + str(essence_updated))
    return packet

if __name__ == "__main__":
    generate_ping()






