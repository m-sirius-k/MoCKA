# FILE: C:\Users\sirok\MoCKA\tools\accept_outbox_to_audit_v2.py
# NOTE: Phase13-B accept pipeline (enforced key_policy at entry)
#
# Contract:
# - Reads an outbox json file (mocka.outbox.v1), tolerates UTF-8 BOM (utf-8-sig)
# - Extracts key_id (if present) and enforces key_policy BEFORE writing audit event
# - Writes a payload event into audit ledger via AuditWriter.write_payload()

import json
import os
import sys
from typing import Any, Dict

from src.mocka_audit.audit_writer import AuditWriter
from src.mocka_audit.key_policy import assert_key_active

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def load_outbox(path: str) -> Dict[str, Any]:
    # tolerate UTF-8 BOM
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def extract_key_id(outbox: Dict[str, Any]) -> str:
    data = outbox.get("data") if isinstance(outbox.get("data"), dict) else {}
    return str(data.get("key_id", "")).strip()


def build_accept_payload(outbox: Dict[str, Any], source_path: str) -> Dict[str, Any]:
    return {
        "type": "accept_outbox",
        "source_path": os.path.abspath(source_path),
        "outbox_schema": str(outbox.get("schema", "")),
        "run_id": str(outbox.get("run_id", "")),
        "stage": str(outbox.get("stage", "")),
        "summary": str(outbox.get("summary", "")),
        "ok": bool(outbox.get("ok", False)),
        "error": outbox.get("error"),
        "data": outbox.get("data"),
    }


def main(argv) -> int:
    if len(argv) != 2:
        print("Usage: python -m tools.accept_outbox_to_audit_v2 <outbox_json_path>")
        return 2

    outbox_path = str(argv[1]).strip().strip('"')
    if not outbox_path:
        print("ERROR: empty path")
        return 2
    if not os.path.isfile(outbox_path):
        print(f"ERROR: file not found: {outbox_path}")
        return 2

    outbox = load_outbox(outbox_path)

    # ENTRY ENFORCEMENT (Phase13-B)
    key_id = extract_key_id(outbox)
    if key_id:
        assert_key_active(key_id)

    payload = build_accept_payload(outbox, outbox_path)

    writer = AuditWriter(DB_PATH)
    ev = writer.write_payload(payload, note="accept_outbox_to_audit_v2", commit=True)

    print("ACCEPTED_TO_AUDIT:", ev["event_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))