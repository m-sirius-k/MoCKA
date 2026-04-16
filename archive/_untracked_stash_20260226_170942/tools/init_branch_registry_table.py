# C:\Users\sirok\MoCKA\tools\init_branch_registry_table.py

import sqlite3

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"

def main():
    conn = sqlite3.connect(DB)
    try:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS branch_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_utc TEXT NOT NULL,
            tip_event_id TEXT NOT NULL,
            orphan_event_id TEXT,
            orphan_prev_id TEXT,
            classification TEXT NOT NULL
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_branch_registry_tip ON branch_registry(tip_event_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_branch_registry_class ON branch_registry(classification);")
        conn.commit()
        print("OK: branch_registry table ensured in audit.db")
    finally:
        conn.close()

if __name__ == "__main__":
    main()