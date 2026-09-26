#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('data/mocka_events.db')
cur = conn.cursor()

print("=" * 80)
print("ORCHESTRA EXECUTION HISTORY")
print("=" * 80)

# Orchestra メッセージを確認
cur.execute('''
    SELECT event_id, title, what_type, free_note, when_ts, who_actor
    FROM events
    WHERE title LIKE '%Orchestra%'
    ORDER BY when_ts DESC
    LIMIT 5
''')

for row in cur.fetchall():
    print(f"\nEvent ID: {row[0]}")
    print(f"Title: {row[1]}")
    print(f"Type: {row[2]}")
    print(f"Actor: {row[5]}")
    print(f"When: {row[4]}")
    print(f"Note: {row[3] if row[3] else '(none)'}")

print("\n" + "=" * 80)
print("WEB EXECUTOR RELATED EVENTS")
print("=" * 80)

# Browser / Playwright 関連
cur.execute('''
    SELECT event_id, title, what_type, when_ts
    FROM events
    WHERE what_type LIKE '%browser%' OR what_type LIKE '%web%' OR what_type LIKE '%execute%'
    ORDER BY when_ts DESC
    LIMIT 5
''')

rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"{row[0]} | {row[1][:50]} | {row[2]} | {row[3]}")
else:
    print("(No browser/web executor events found)")

print("\n" + "=" * 80)
print("HAB/JARVIS INTEGRATION EVENTS")
print("=" * 80)

# HAB/JARVIS 関連
cur.execute('''
    SELECT event_id, title, what_type, where_component, when_ts
    FROM events
    WHERE where_component LIKE '%hab%' OR where_component LIKE '%jarvis%'
           OR title LIKE '%hab%' OR title LIKE '%jarvis%'
    ORDER BY when_ts DESC
    LIMIT 5
''')

rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"{row[0]} | {row[1][:40]} | {row[2]} | {row[3]} | {row[4]}")
else:
    print("(No HAB/JARVIS events found)")

conn.close()
