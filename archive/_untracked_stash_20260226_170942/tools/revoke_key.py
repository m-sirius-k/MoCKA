import os
import sys
import sqlite3
from datetime import datetime, timezone

DB_PATH_DEFAULT = r"audit\ed25519\audit.db"

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    # Usage:
    #   python tools/revoke_key.py <key_id> [reason_code] [revoked_by] [reason_text]
    db_path = DB_PATH_DEFAULT

    if len(sys.argv) < 2:
        print("USAGE: python tools/revoke_key.py <key_id> [reason_code] [revoked_by] [reason_text]", file=sys.stderr)
        return 2

    key_id = sys.argv[1].strip()
    reason_code = sys.argv[2].strip() if len(sys.argv) >= 3 else "compromise"
    revoked_by = sys.argv[3].strip() if len(sys.argv) >= 4 else "operator"
    reason_text = sys.argv[4].strip() if len(sys.argv) >= 5 else "manual revoke test"

    if not os.path.exists(db_path):
        print("DB NOT FOUND:", db_path, file=sys.stderr)
        return 3

    revoked_at = utc_now_iso()

    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO key_revocation(key_id, revoked_at, reason_code, reason_text, revoked_by, audit_event_id)
            VALUES(?,?,?,?,?,NULL)
            ON CONFLICT(key_id) DO UPDATE SET
              revoked_at=excluded.revoked_at,
              reason_code=excluded.reason_code,
              reason_text=excluded.reason_text,
              revoked_by=excluded.revoked_by
            """,
            (key_id, revoked_at, reason_code, reason_text, revoked_by),
        )
        con.commit()
    finally:
        con.close()

    print("REVOKED:", key_id)
    print("revoked_at:", revoked_at)
    print("reason_code:", reason_code)
    print("revoked_by:", revoked_by)
    print("reason_text:", reason_text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())