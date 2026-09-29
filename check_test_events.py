#!/usr/bin/env python
import sqlite3
import sys
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'mocka_events.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

try:
    # Search for audit events with request_id containing 'test'
    print("=== Searching for test events ===\n")

    query = '''
    SELECT
        event_id,
        what_type,
        request_id,
        when_ts,
        vendor,
        model,
        runtime,
        source
    FROM events
    WHERE request_id LIKE '%test%' OR what_type IN ('audit', 'incident')
    ORDER BY when_ts DESC
    LIMIT 10
    '''

    results = conn.execute(query).fetchall()
    print(f"Found {len(results)} matching events:\n")

    for i, row in enumerate(results, 1):
        print(f"{i}. event_id: {row['event_id']}")
        print(f"   what_type: {row['what_type']}")
        print(f"   request_id: {row['request_id']}")
        print(f"   when_ts: {row['when_ts']}")
        print(f"   vendor: {row['vendor']}")
        print(f"   model: {row['model']}")
        print(f"   runtime: {row['runtime']}")
        print(f"   source: {row['source']}")
        print()

finally:
    conn.close()
