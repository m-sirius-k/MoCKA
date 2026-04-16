import argparse
import datetime
import json
import os
import sqlite3
import hashlib
from typing import Any, Dict, Optional


ROOT = r"C:\Users\sirok\MoCKA"
REGISTRY_PATH = os.path.join(ROOT, "audit", "key_registry.json")
INVENTORY_DIR = os.path.join(ROOT, "inventory")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def utc_now_z() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_table(cur, table_name: str):
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL,
      schema_version TEXT NOT NULL,
      event_content TEXT NOT NULL,
      event_id TEXT NOT NULL,
      prev_chain_hash TEXT,
      chain_hash TEXT NOT NULL,
      created_at_utc TEXT NOT NULL
    )
    """)


def get_last_chain_hash(cur, table_name: str) -> str:
    cur.execute(f"SELECT chain_hash FROM {table_name} ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if not row or not row[0]:
        return ""
    return str(row[0])


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _parse_z(ts: Optional[str]) -> Optional[datetime.datetime]:
    if not ts:
        return None
    # supports "...Z" or ISO string
    s = ts.replace("Z", "+00:00")
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None


def derive_rotation_from_registry(reg: dict) -> Dict[str, str]:
    """
    Derive (old_key_id, new_key_id, rotation_chain_hash, activated_at) from key_registry.json.
    Assumes:
      - reg["active_key_id"] exists
      - reg["keys"] contains entries with key_id, status, activated_at, deactivated_at, revocation_reason
      - reg["rotation_chain_hash"] exists (set by key_rotate_ceremony.py)
    """
    new_key_id = reg.get("active_key_id")
    if not new_key_id:
        raise RuntimeError("active_key_id missing in audit/key_registry.json")

    keys = reg.get("keys", [])
    if not isinstance(keys, list):
        raise RuntimeError("keys must be a list in audit/key_registry.json")

    new_entry = None
    for k in keys:
        if k.get("key_id") == new_key_id:
            new_entry = k
            break
    if not new_entry:
        raise RuntimeError(f"active key not found in registry keys: {new_key_id}")

    activated_at = new_entry.get("activated_at") or utc_now_z()

    # old key: latest inactive rotated key by deactivated_at
    old_candidates = []
    for k in keys:
        if k.get("key_id") == new_key_id:
            continue
        if k.get("status") != "inactive":
            continue
        if k.get("revocation_reason") != "rotation":
            continue
        dt = _parse_z(k.get("deactivated_at")) or _parse_z(k.get("activated_at"))
        if dt:
            old_candidates.append((dt, k.get("key_id")))

    if old_candidates:
        old_candidates.sort(key=lambda x: x[0], reverse=True)
        old_key_id = old_candidates[0][1]
    else:
        # Fallback: if no inactive rotation found (first rotation edge-case),
        # treat old as GENESIS
        old_key_id = "GENESIS"

    rotation_chain_hash = reg.get("rotation_chain_hash")
    if not rotation_chain_hash:
        raise RuntimeError("rotation_chain_hash missing in audit/key_registry.json")

    return {
        "old_key_id": str(old_key_id),
        "new_key_id": str(new_key_id),
        "rotation_chain_hash": str(rotation_chain_hash),
        "activated_at": str(activated_at),
    }


def insert_key_rotation_event(
    db_path: str,
    table_name: str,
    schema_version: str,
    old_key_id: str,
    new_key_id: str,
    rotation_chain_hash: str,
    activated_at: str,
):
    payload = {
        "old_key_id": old_key_id,
        "new_key_id": new_key_id,
        "rotation_chain_hash": rotation_chain_hash,
        "activated_at": activated_at,
    }

    event_content_bytes = normalize_json_bytes(payload)
    event_content = event_content_bytes.decode("utf-8")
    event_id = sha256_hex(event_content_bytes)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        ensure_table(cur, table_name)

        prev = get_last_chain_hash(cur, table_name)
        chain_hash = sha256_hex((prev + event_id).encode("utf-8"))

        cur.execute(
            f"""
            INSERT INTO {table_name}
            (event_type, schema_version, event_content, event_id, prev_chain_hash, chain_hash, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "key_rotation",
                schema_version,
                event_content,
                event_id,
                prev if prev != "" else None,
                chain_hash,
                utc_now_z(),
            ),
        )
        conn.commit()

        return {
            "event_type": "key_rotation",
            "schema_version": schema_version,
            "event_id": event_id,
            "prev_chain_hash": prev,
            "chain_hash": chain_hash,
        }
    finally:
        conn.close()


def write_inventory_record(result: dict, details: dict) -> Optional[str]:
    try:
        os.makedirs(INVENTORY_DIR, exist_ok=True)
        ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S.%f+0000")
        path = os.path.join(INVENTORY_DIR, f"phase9_key_rotation_{ts}.json")
        obj = {
            "status": "OK",
            "event_summary": result,
            "event_content_minimal": details,
            "created_at_utc": utc_now_z(),
        }
        with open(path, "wb") as f:
            f.write(json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8"))
        return path
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--table", default="audit_ledger_event")
    ap.add_argument("--schema-version", default="v1")

    # Optional overrides (normally derived from key_registry.json)
    ap.add_argument("--old-key-id")
    ap.add_argument("--new-key-id")
    ap.add_argument("--rotation-chain-hash")
    ap.add_argument("--activated-at")

    args = ap.parse_args()

    reg = load_registry()
    derived = derive_rotation_from_registry(reg)

    old_key_id = args.old_key_id or derived["old_key_id"]
    new_key_id = args.new_key_id or derived["new_key_id"]
    rotation_chain_hash = args.rotation_chain_hash or derived["rotation_chain_hash"]
    activated_at = args.activated_at or derived["activated_at"]

    result = insert_key_rotation_event(
        db_path=args.db,
        table_name=args.table,
        schema_version=args.schema_version,
        old_key_id=old_key_id,
        new_key_id=new_key_id,
        rotation_chain_hash=rotation_chain_hash,
        activated_at=activated_at,
    )

    inv_path = write_inventory_record(result, {
        "old_key_id": old_key_id,
        "new_key_id": new_key_id,
        "rotation_chain_hash": rotation_chain_hash,
        "activated_at": activated_at,
    })
    if inv_path:
        result["inventory_record"] = inv_path

    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()