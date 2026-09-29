#!/usr/bin/env python3
import sqlite3

db = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

print("[EVENTS TABLE SCHEMA]", flush=True)
schema_rows = con.execute("PRAGMA table_info(events)").fetchall()
for row in schema_rows[:15]:
    print(f"  {row[1]}: {row[2]} (notnull={row[3]}, pk={row[5]})", flush=True)

print()
print("[FOREIGN KEY CONSTRAINTS]", flush=True)
fk_rows = con.execute("PRAGMA foreign_key_list(events)").fetchall()
if fk_rows:
    for row in fk_rows:
        print(f"  {row[3]} → {row[2]}.{row[4]} (on_delete={row[5]})", flush=True)
else:
    print("  No foreign key constraints", flush=True)

print()
print("[INDEXES]", flush=True)
idx_rows = con.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='events'").fetchall()
for row in idx_rows[:5]:
    print(f"  {row[0]}: {row[1]}", flush=True)

con.close()
