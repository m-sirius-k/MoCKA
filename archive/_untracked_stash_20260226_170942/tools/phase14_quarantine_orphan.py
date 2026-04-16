
import os
import json
import sqlite3
import sys
from pathlib import Path

NOTE = "Phase14 quarantine tool (classification + snapshot)"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
OUTDIR = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\quarantine")

VALID_REASON_MINLEN = 8

def utc_now(conn):
    cur = conn.cursor()
    cur.execute("SELECT strftime('%Y-%m-%d %H:%M:%S','now');")
    return cur.fetchone()[0]

def detect_ledger_table(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = [c[1].lower() for c in cur.fetchall()]
        if "event_id" in cols:
            if "prev_event_id" in cols:
                return t, "event_id", "prev_event_id"
            if "prev" in cols:
                return t, "event_id", "prev"
    raise RuntimeError("No ledger-like table found")

def fetch_row_as_dict(conn, table, event_id):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [c[1] for c in cur.fetchall()]
    col_list = ", ".join(cols)
    cur.execute(f"SELECT {col_list} FROM {table} WHERE event_id=? LIMIT 1;", (event_id,))
    row = cur.fetchone()
    if not row:
        return None
    return dict(zip(cols, row))

def ensure_registry(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='branch_registry';")
    if not cur.fetchone():
        raise RuntimeError("branch_registry not found. Run tools/phase14_init_branch_registry.py first.")

def update_classification(conn, orphan_event_id, reason, ts):
    conn.execute(
        """
        UPDATE branch_registry
        SET classification='quarantined',
            note = note || '\nQUARANTINE ' || ? || ' ' || ?
        WHERE orphan_event_id=?
        """,
        (ts, reason, orphan_event_id),
    )
    if conn.total_changes == 0:
        raise RuntimeError("No branch_registry row updated (orphan_event_id not found): " + orphan_event_id)

def main(argv):
    if len(argv) < 3:
        print("Usage: python phase14_quarantine_orphan.py <orphan_event_id> <reason_note>")
        return 1

    orphan_id = argv[1].strip()
    reason = argv[2].strip()

    if len(reason) < VALID_REASON_MINLEN:
        print("ERROR: reason_note too short (min length = %d)" % VALID_REASON_MINLEN)
        return 2

    if not os.path.exists(DB):
        print("ERROR: db not found:", DB)
        return 3

    OUTDIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB)
    try:
        ensure_registry(conn)
        ts = utc_now(conn)
        ledger_table, _, _ = detect_ledger_table(conn)

        row = fetch_row_as_dict(conn, ledger_table, orphan_id)
        if row is None:
            print("ERROR: event not found in ledger table:", ledger_table)
            return 4

        update_classification(conn, orphan_id, reason, ts)
        conn.commit()

        snap = {
            "note": NOTE,
            "utc": ts,
            "db": DB,
            "ledger_table": ledger_table,
            "orphan_event_id": orphan_id,
            "reason": reason,
            "ledger_row": row,
        }

        outpath = OUTDIR / (orphan_id + ".json")
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=True, indent=2)

        print("OK: QUARANTINED:", orphan_id)
        print("UTC:", ts)
        print("SNAPSHOT:", str(outpath))
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
