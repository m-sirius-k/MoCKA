import os
import sys
import sqlite3

DB_PATH_DEFAULT = r"audit\ed25519\audit.db"

def main():
    # Usage:
    #   python tools/unrevoke_key.py <key_id> [db_path]
    if len(sys.argv) < 2:
        print("USAGE: python tools/unrevoke_key.py <key_id> [db_path]", file=sys.stderr)
        return 2

    key_id = sys.argv[1].strip()
    db_path = sys.argv[2] if len(sys.argv) >= 3 else DB_PATH_DEFAULT

    if not os.path.exists(db_path):
        print("DB NOT FOUND:", db_path, file=sys.stderr)
        return 3

    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM key_revocation WHERE key_id=?", (key_id,))
        con.commit()
    finally:
        con.close()

    print("UNREVOKED:", key_id)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())