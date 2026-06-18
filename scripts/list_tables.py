import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3
import sys

if len(sys.argv) != 2:
    print("Usage: python list_tables.py <db_path>")
    sys.exit(1)

db_path = sys.argv[1]

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

    print("DB:", db_path)
    rows = cur.fetchall()
    if not rows:
        print("(no tables found)")
    else:
        for row in rows:
            print("-", row[0])

    conn.close()

except Exception as e:
    print("ERROR:", e)