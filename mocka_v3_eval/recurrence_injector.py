import os, json, sys
from datetime import datetime

INFIELD_DIR = r"C:\Users\sirok\MoCKA\data\storage\infield\PACKET"
LOG_PATH = r"C:\Users\sirok\MoCKA\data\recurrence_injection_log.json"

def inject(packet: dict, source: str = "manual") -> dict:
    os.makedirs(INFIELD_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(INFIELD_DIR, f"injected_{ts}.json")
    packet["_injected_at"] = ts
    packet["_source"] = source
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, ensure_ascii=False, indent=2)
    print(f"[recurrence_injector] 注入完了: {out_path}")
    _append_log(packet, out_path, source)
    return {"status": "ok", "path": out_path}

def _append_log(packet, out_path, source):
    log = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            log = json.load(f)
    log.append({
        "injected_at": packet.get("_injected_at"),
        "source": source,
        "path": out_path,
        "event_id": packet.get("event_id", "unknown")
    })
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def from_share(fpath: str, packet: dict):
    """share_observerからのコールバック用"""
    print(f"[recurrence_injector] share経由受信: {fpath}")
    return inject(packet, source="mocka-share")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            packet = json.load(f)
        inject(packet, source="cli")
    else:
        print("使用法: python recurrence_injector.py <packet.json>")
