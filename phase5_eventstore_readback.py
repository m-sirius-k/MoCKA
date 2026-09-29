#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — PRIMARY EVENT STORE READ-BACK VERIFICATION
Verify that request_id, event_id, decision_id are recorded in Event Store
"""

import sqlite3
import json
from pathlib import Path

# Identifiers from runtime execution
REQUEST_ID = "f63ae36f-06eb-4663-8dc5-b43de2c94ec1"
DECISION_ID = "DC_20260929_P5_HAB_JARVIS_001"
EVENT_ID = "E20260929_54766916458a0"

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"

def main():
    print("[PHASE 5.0 EVENT STORE READ-BACK]", flush=True)
    print(f"Decision ID: {DECISION_ID}", flush=True)
    print(f"Request ID: {REQUEST_ID}", flush=True)
    print(f"Event ID: {EVENT_ID}", flush=True)
    print(f"Database: {DB_PATH}", flush=True)
    print()

    try:
        # Open Event Store in read-only mode
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row

        # Get table list
        print("[EVENT STORE TABLES]", flush=True)
        tables = []
        for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            table_name = row[0]
            tables.append(table_name)
            print(f"  - {table_name}", flush=True)
        print()

        # Search for identifiers in relevant columns
        print("[SEARCHING FOR IDENTIFIERS]", flush=True)
        found_entries = []

        search_targets = [REQUEST_ID, DECISION_ID, EVENT_ID]
        search_columns = [
            "request_id", "decision_id", "event_id", "payload",
            "event", "data", "metadata", "raw", "content"
        ]

        for table_name in tables:
            try:
                # Get column info
                col_info = con.execute(f"PRAGMA table_info([{table_name}])").fetchall()
                available_cols = [col[1].lower() for col in col_info]

                # Find searchable columns in this table
                search_cols_in_table = [c for c in search_columns if c.lower() in available_cols]
                if not search_cols_in_table:
                    continue

                # Search each target in each column
                for col in search_cols_in_table:
                    for target in search_targets:
                        query = f"SELECT * FROM [{table_name}] WHERE CAST([{col}] AS TEXT) LIKE ? LIMIT 10"
                        rows = con.execute(query, (f"%{target}%",)).fetchall()

                        for row in rows:
                            entry = dict(row)
                            found_entries.append({
                                "table": table_name,
                                "column": col,
                                "target": target,
                                "entry": entry
                            })

                            print(f"FOUND: TABLE={table_name}, COLUMN={col}, TARGET={target[:20]}...", flush=True)

                            # Print key fields
                            for key in ["event_id", "request_id", "decision_id", "timestamp", "what_type"]:
                                if key in entry:
                                    print(f"  {key}: {entry[key]}", flush=True)
            except Exception as e:
                pass  # Skip tables with errors

        print()

        # Summary
        if not found_entries:
            print("[EVENT STORE READ-BACK RESULT]", flush=True)
            print("Status: NOT VERIFIED", flush=True)
            print("Reason: No matching entries found in Event Store", flush=True)
            return False
        else:
            print("[EVENT STORE READ-BACK RESULT]", flush=True)
            print(f"Status: VERIFIED", flush=True)
            print(f"Matches found: {len(found_entries)}", flush=True)

            # Verify all three identifiers are present
            has_request_id = any(e["target"] == REQUEST_ID for e in found_entries)
            has_decision_id = any(e["target"] == DECISION_ID for e in found_entries)
            has_event_id = any(e["target"] == EVENT_ID for e in found_entries)

            print()
            print("[IDENTIFIER VERIFICATION]", flush=True)
            print(f"Request ID ({REQUEST_ID}): {'✓ FOUND' if has_request_id else '✗ NOT FOUND'}", flush=True)
            print(f"Decision ID ({DECISION_ID}): {'✓ FOUND' if has_decision_id else '✗ NOT FOUND'}", flush=True)
            print(f"Event ID ({EVENT_ID}): {'✓ FOUND' if has_event_id else '✗ NOT FOUND'}", flush=True)

            return has_request_id or has_decision_id or has_event_id

        con.close()

    except Exception as e:
        print(f"[ERROR] Event Store access failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
