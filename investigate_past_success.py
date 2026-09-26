#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 1: Investigate past Claude.ai Web success execution
Extract: timestamp, request_id, session_id, HAB/JARVIS entry, response
"""
import sqlite3
import json

conn = sqlite3.connect('data/mocka_events.db')
cur = conn.cursor()

print("=" * 80)
print("STEP 1: PAST CLAUDE WEB SUCCESS EXECUTION ANALYSIS")
print("=" * 80)

# Find Orchestra events related to Claude.ai
print("\n[1] Orchestra Claude.ai events (9/20-9/23):")
cur.execute('''
    SELECT event_id, title, when_ts, free_note, request_id, session_id
    FROM events
    WHERE title LIKE '%Orchestra%claude%' OR title LIKE '%Orchestra: claude%'
    ORDER BY when_ts DESC
    LIMIT 10
''')

orchestra_events = cur.fetchall()
print(f"Found {len(orchestra_events)} Orchestra Claude events")

if orchestra_events:
    for i, row in enumerate(orchestra_events[:3], 1):
        print(f"\n[Event {i}]")
        print(f"  Event ID: {row[0]}")
        print(f"  Title: {row[1][:60]}")
        print(f"  When: {row[2]}")
        print(f"  Request ID: {row[4]}")
        print(f"  Session ID: {row[5]}")
        print(f"  Note: {row[3]}")

# Find Multi-AI Request events from JARVIS
print("\n" + "=" * 80)
print("[2] HAB/JARVIS Multi-AI Request events:")
cur.execute('''
    SELECT event_id, title, when_ts, free_note, request_id, session_id
    FROM events
    WHERE title LIKE '%Multi-AI Request%JARVIS%'
       OR where_component = 'gateway_multi_dispatcher'
    ORDER BY when_ts DESC
    LIMIT 5
''')

jarvis_events = cur.fetchall()
print(f"Found {len(jarvis_events)} JARVIS Multi-AI Request events")

if jarvis_events:
    for i, row in enumerate(jarvis_events[:3], 1):
        print(f"\n[JARVIS Request {i}]")
        print(f"  Event ID: {row[0]}")
        print(f"  Title: {row[1][:60]}")
        print(f"  When: {row[2]}")
        print(f"  Request ID: {row[4]}")
        print(f"  Session ID: {row[5]}")
        print(f"  Note: {row[3][:100] if row[3] else '(none)'}")

# Try to find related events by timestamp proximity
print("\n" + "=" * 80)
print("[3] Analyzing time correlation (9/20 Orchestra execution):")

# Most recent Orchestra event
cur.execute('''
    SELECT event_id, when_ts, session_id
    FROM events
    WHERE title LIKE '%Orchestra: claude%'
    ORDER BY when_ts DESC
    LIMIT 1
''')

recent_orch = cur.fetchone()
if recent_orch:
    orch_id, orch_time, session_id = recent_orch
    print(f"\nMost recent Orchestra execution:")
    print(f"  Event ID: {orch_id}")
    print(f"  Time: {orch_time}")
    print(f"  Session ID: {session_id}")

    # Find events around this time (within 5 minutes)
    print(f"\nEvents within 5 minutes of this Orchestra execution:")
    cur.execute('''
        SELECT event_id, title, when_ts, where_component, what_type
        FROM events
        WHERE datetime(when_ts) BETWEEN
              datetime(?, '-5 minutes') AND datetime(?, '+5 minutes')
        ORDER BY when_ts
    ''', (orch_time, orch_time))

    related = cur.fetchall()
    for row in related:
        print(f"  {row[0][:20]} | {row[1][:40]} | {row[2]} | {row[3]}")

# Look for actual response content in events
print("\n" + "=" * 80)
print("[4] Looking for response content (Claude.ai responses):")

cur.execute('''
    SELECT event_id, title, before_state, after_state
    FROM events
    WHERE title LIKE '%Orchestra: claude%'
    ORDER BY when_ts DESC
    LIMIT 1
''')

response_row = cur.fetchone()
if response_row:
    print(f"\nOrchestra response event:")
    print(f"  Event ID: {response_row[0]}")
    print(f"  Title: {response_row[1][:70]}")
    print(f"  Before: {response_row[2][:100] if response_row[2] else '(none)'}")
    print(f"  After: {response_row[3][:100] if response_row[3] else '(none)'}")

# Summary: construct minimal reproducible path
print("\n" + "=" * 80)
print("[5] MINIMAL REPRODUCIBLE PATH IDENTIFICATION:")
print("=" * 80)

if orchestra_events:
    latest = orchestra_events[0]
    print(f"\nLatest successful Orchestra Web execution:")
    print(f"  Event ID: {latest[0]}")
    print(f"  Timestamp: {latest[2]}")
    print(f"  Session: {latest[5]}")
    print(f"  Request: {latest[4]}")
    print(f"\nTo reproduce: Use same session_id/request_id to trigger HAB/JARVIS")
    print(f"Entry point: gateway_multi_dispatcher")

conn.close()
