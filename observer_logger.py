"""
observer_logger.py
テストパック使用時にMoCKAのledgerへ記録する
使い方: python observer_logger.py <pack_path> <user_id>
"""
import sys
import os
import json
import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(ROOT))
from schema.schema import append_event, verify_ledger

def get_machine_id() -> str:
    """マシンの固有IDを取得（改ざん者の特定に使用）"""
    try:
        if platform.system() == "Windows":
            r = subprocess.run(
                ["wmic", "csproduct", "get", "UUID"],
                capture_output=True, text=True
            )
            uid = r.stdout.strip().split("\n")[-1].strip()
            return hashlib.sha256(uid.encode()).hexdigest()[:16]
    except:
        pass
    return hashlib.sha256(platform.node().encode()).hexdigest()[:16]

def get_pack_hash(pack_path: str) -> str:
    """パックのSHA256を計算"""
    p = Path(pack_path)
    if p.is_file():
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    elif p.is_dir():
        hashes = []
        for f in sorted(p.rglob("*")):
            if f.is_file():
                with open(f, "rb") as fp:
                    hashes.append(hashlib.sha256(fp.read()).hexdigest())
        return hashlib.sha256("".join(hashes).encode()).hexdigest()
    return "unknown"

def log_pack_usage(pack_path: str, user_id: str = "anonymous", action: str = "ACCESS"):
    """テストパック使用をledgerに記録"""

    machine_id = get_machine_id()
    pack_hash = get_pack_hash(pack_path)
    pack_name = Path(pack_path).name

    action_data = {
        "type": "OBSERVER_LOG",
        "pack_name": pack_name,
        "pack_hash": pack_hash[:16],
        "user_id": user_id,
        "machine_id": machine_id,
        "platform": platform.system(),
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # ledgerに記録
    event = append_event("OBSERVER", json.dumps(action_data))

    print(f"OBSERVER LOG RECORDED")
    print(f"  pack   : {pack_name}")
    print(f"  machine: {machine_id}")
    print(f"  hash   : {pack_hash[:16]}...")
    print(f"  event  : {event['event_id']}")

    # 検証
    if verify_ledger():
        print("  ledger : OK")
    else:
        print("  ledger : ERROR")

    return event

if __name__ == "__main__":
    pack_path = sys.argv[1] if len(sys.argv) > 1 else r"F:\MoCKA_Observer_Node"
    user_id = sys.argv[2] if len(sys.argv) > 2 else "anonymous"
    log_pack_usage(pack_path, user_id)
