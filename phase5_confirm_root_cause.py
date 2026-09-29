import sqlite3, shutil, tempfile, os

DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
EID = "E20260929_54766916458a0"

src = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = src.cursor()

print("=== A: SCHEMA ===")
print(cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()[0])
print("INDEXES:", cur.execute("PRAGMA index_list(events)").fetchall())

print("\n=== EVENT ===")
print(cur.execute("SELECT * FROM events WHERE event_id=?", (EID,)).fetchall())
print("\n=== SIGNATURE ===")
print(cur.execute("SELECT * FROM event_signatures WHERE event_id=?", (EID,)).fetchall())

print("\n=== B: CONSTRAINT CANDIDATES ===")
cols = cur.execute("PRAGMA table_info(events)").fetchall()
for c in cols:
    print(c)

src.close()

print("\n=== C: ISOLATED INSERT TEST ===")
fd, tmp = tempfile.mkstemp(suffix=".db")
os.close(fd)
shutil.copy2(DB, tmp)

con = sqlite3.connect(tmp)
try:
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("BEGIN")
    row = con.execute("SELECT * FROM events WHERE event_id=?", (EID,)).fetchone()
    print("Existing row in isolated DB:", row)
    print("No production write performed.")
    con.rollback()
finally:
    con.close()
    os.remove(tmp)
