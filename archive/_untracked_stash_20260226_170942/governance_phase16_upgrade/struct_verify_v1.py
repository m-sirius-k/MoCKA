# NOTE: STRUCT verifier v1.3 (Phase16 T10)
# NOTE: governance.db schema confirmed:
# NOTE: governance_ledger_event(event_id, prev_event_id, timestamp_utc, event_type, payload_json, note, chain_hash)
# NOTE: GENESIS is defined as the unique ROOT event:
# NOTE: root = event where prev_event_id is not found in event_id set OR prev_event_id == event_id OR prev_event_id == '0'*64.
# NOTE: branch_registry + event_branch_map are enforced if present.
# NOTE: No unhandled exceptions allowed. Always emit a report.

import os
import sqlite3
import json
from datetime import datetime, timezone

GOV_DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
GOV_TABLE = "governance_ledger_event"

TIP_GOV = r"C:\Users\sirok\MoCKA\governance\last_governance_event_id.txt"
OUT_REPORT = r"C:\Users\sirok\MoCKA\outbox\verify_report_struct_v1.json"

ERR = {
    "GENESIS_DUPLICATE": "ERR-STRUCT-001",
    "TIP_UNREACHABLE": "ERR-STRUCT-002",
    "BRANCH_CLASSIFICATION_INVALID": "ERR-STRUCT-003",
    "QUARANTINE_CONFLICT": "ERR-STRUCT-004",
}

ZERO64 = "0" * 64

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def fail(checks, code, message, details=None):
    checks.append({
        "status": "FAIL",
        "err_code": code,
        "message": message,
        "details": details or {}
    })

def pass_check(checks, invariant_id, message, details=None):
    checks.append({
        "status": "PASS",
        "invariant_id": invariant_id,
        "message": message,
        "details": details or {}
    })

def safe_write_report(checks, overall, fatal_error=None):
    report = {
        "report_version": "v1",
        "utc_now": utc_now(),
        "verifier": {"name": "struct_verify_v1", "version": "v1.3"},
        "inputs": {"governance_db": GOV_DB, "tip_path": TIP_GOV},
        "results": {"overall": overall, "checks": checks},
        "fatal_error": fatal_error or ""
    }
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Wrote report:", OUT_REPORT)
    print("Overall:", overall)

def connect_db(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return sqlite3.connect(path)

def table_exists(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone()[0] == 1

def load_events(conn):
    cur = conn.cursor()
    cur.execute(f"SELECT event_id, prev_event_id, event_type FROM {GOV_TABLE};")
    rows = cur.fetchall()
    by_id = {}
    for event_id, prev_event_id, event_type in rows:
        by_id[event_id] = {"event_id": event_id, "prev_event_id": prev_event_id, "event_type": event_type}
    return by_id

def find_roots(by_id):
    ids = set(by_id.keys())
    roots = []
    for eid, node in by_id.items():
        prev = (node["prev_event_id"] or "").strip()
        if prev == "" or prev == ZERO64 or prev == eid or prev not in ids:
            roots.append(eid)
    return roots

def inv_struct_001_genesis_unique(conn, checks, by_id):
    roots = find_roots(by_id)
    if len(roots) == 1:
        pass_check(checks, "INV-STRUCT-001", "GENESIS(root) unique", {"root_event_id": roots[0]})
        return roots[0]
    fail(checks, ERR["GENESIS_DUPLICATE"], "ROOT(GENESIS) count is not 1", {"root_count": len(roots), "roots": roots[:20]})
    return None

def inv_struct_002_tip_reachable(conn, checks, by_id, root_event_id):
    if not os.path.exists(TIP_GOV):
        fail(checks, ERR["TIP_UNREACHABLE"], "Governance TIP file missing", {"tip_path": TIP_GOV})
        return

    tip_event_id = read_text(TIP_GOV)
    if root_event_id is None:
        fail(checks, ERR["TIP_UNREACHABLE"], "ROOT(GENESIS) not uniquely identifiable; cannot verify reachability")
        return

    if tip_event_id not in by_id:
        fail(checks, ERR["TIP_UNREACHABLE"], "TIP event_id not found in governance ledger", {"tip_event_id": tip_event_id})
        return

    visited = set()
    node_id = tip_event_id
    steps = 0

    while True:
        steps += 1
        if steps > 200000:
            fail(checks, ERR["TIP_UNREACHABLE"], "Traversal exceeded step limit", {"steps": steps})
            return

        if node_id == root_event_id:
            pass_check(checks, "INV-STRUCT-002", "TIP reachable from ROOT(GENESIS)", {"steps": steps, "tip_event_id": tip_event_id})
            return

        if node_id in visited:
            fail(checks, ERR["TIP_UNREACHABLE"], "Cycle detected in prev_event_id traversal", {"steps": steps})
            return
        visited.add(node_id)

        prev_id = (by_id[node_id]["prev_event_id"] or "").strip()
        if prev_id == "" or prev_id == ZERO64:
            fail(checks, ERR["TIP_UNREACHABLE"], "Reached chain start without ROOT(GENESIS)", {"steps": steps})
            return

        if prev_id not in by_id:
            fail(checks, ERR["TIP_UNREACHABLE"], "prev_event_id not found in ledger", {"prev_event_id": prev_id})
            return

        node_id = prev_id

def inv_struct_003_branch_classification_not_null(conn, checks):
    if not table_exists(conn, "branch_registry"):
        fail(checks, ERR["BRANCH_CLASSIFICATION_INVALID"], "branch_registry missing")
        return
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM branch_registry WHERE classification IS NULL;")
    c = cur.fetchone()[0]
    if c == 0:
        pass_check(checks, "INV-STRUCT-003", "branch_registry.classification NOT NULL")
    else:
        fail(checks, ERR["BRANCH_CLASSIFICATION_INVALID"], "NULL classification rows exist", {"count": c})

def inv_struct_004_quarantine_not_tip(conn, checks):
    # Enforce: TIP event's branch classification must not be QUARANTINE
    if not os.path.exists(TIP_GOV):
        fail(checks, ERR["QUARANTINE_CONFLICT"], "Governance TIP file missing", {"tip_path": TIP_GOV})
        return

    if not (table_exists(conn, "branch_registry") and table_exists(conn, "event_branch_map")):
        fail(checks, ERR["QUARANTINE_CONFLICT"], "branch/quarantine tables missing (branch_registry or event_branch_map)")
        return

    tip_event_id = read_text(TIP_GOV)

    cur = conn.cursor()
    cur.execute("SELECT branch_id FROM event_branch_map WHERE event_id=?;", (tip_event_id,))
    row = cur.fetchone()
    if row is None:
        fail(checks, ERR["QUARANTINE_CONFLICT"], "TIP event has no branch mapping", {"tip_event_id": tip_event_id})
        return

    branch_id = row[0]
    cur.execute("SELECT classification FROM branch_registry WHERE branch_id=?;", (branch_id,))
    row2 = cur.fetchone()
    if row2 is None:
        fail(checks, ERR["QUARANTINE_CONFLICT"], "TIP branch_id not found in branch_registry", {"branch_id": branch_id})
        return

    classification = (row2[0] or "").upper()
    if classification == "QUARANTINE":
        fail(checks, ERR["QUARANTINE_CONFLICT"], "TIP points to QUARANTINE branch (forbidden)", {"branch_id": branch_id})
        return

    pass_check(checks, "INV-STRUCT-004", "TIP not selectable from QUARANTINE branch", {"branch_id": branch_id, "classification": classification})

def main():
    checks = []
    conn = None
    try:
        conn = connect_db(GOV_DB)
        by_id = load_events(conn)

        root_event_id = inv_struct_001_genesis_unique(conn, checks, by_id)
        inv_struct_002_tip_reachable(conn, checks, by_id, root_event_id)
        inv_struct_003_branch_classification_not_null(conn, checks)
        inv_struct_004_quarantine_not_tip(conn, checks)

        overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
        safe_write_report(checks, overall)

    except Exception as e:
        fail(checks, ERR["TIP_UNREACHABLE"], "Unhandled exception captured; treated as structural failure", {"error": str(e)})
        safe_write_report(checks, "FAIL", fatal_error=str(e))
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    main()