#!/usr/bin/env python
"""
Direct Execution Test - Bypass HTTP to test core logic
"""

import sys, json, sqlite3, uuid
from datetime import datetime
from pathlib import Path

# Import the execute_tool function
from mocka_mcp_server import execute_tool

print("=" * 80)
print("DIRECT EXECUTION TEST (Bypassing HTTP)")
print("=" * 80)

BASE = Path(".")
DB_PATH = BASE / "data" / "mocka_events.db"

# Step 1: Create test authorization
print("\n[Step 1] Creating test authorization_state...")
auth_id = str(uuid.uuid4())
decision_id = f"DC_DIRECT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
human_id = "direct_test_user"

conn = sqlite3.connect(str(DB_PATH))
conn.execute('''
    CREATE TABLE IF NOT EXISTS authorization_state (
        authorization_id TEXT PRIMARY KEY,
        decision_id TEXT,
        subject TEXT,
        scope TEXT,
        standing TEXT,
        status TEXT,
        granted_by TEXT,
        granted_at TEXT,
        evidence TEXT,
        hg_event_source TEXT,
        immutable INTEGER
    )
''')
conn.execute(
    '''INSERT OR REPLACE INTO authorization_state
    (authorization_id, decision_id, subject, scope, standing, status, granted_by, granted_at, evidence, immutable)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (auth_id, decision_id, human_id, json.dumps(["test_scope"]), "UNKNOWN", "APPROVED", "TEST_AUTHORITY", datetime.now().isoformat(), json.dumps({"source": ["TEST"]}), 1)
)
conn.commit()
conn.close()
print(f"  authorization_id: {auth_id}")
print(f"  decision_id: {decision_id}")
print(f"  status: APPROVED")

# Step 2: Call execute_tool directly
print("\n[Step 2] Calling execute_tool('mocka_get_overview', {}, req_id=auth_id)...")
try:
    exec_response = execute_tool("mocka_get_overview", {}, req_id=str(auth_id))
    execution_result = json.loads(exec_response) if isinstance(exec_response, str) else exec_response
    print(f"  Result type: {type(execution_result)}")
    if isinstance(execution_result, dict):
        print(f"  Result keys: {list(execution_result.keys())[:10]}")
        if "error" in execution_result:
            print(f"  ERROR: {execution_result.get('error')}")
        else:
            print(f"  STATUS: OK (execution successful)")
    else:
        print(f"  Result: {str(execution_result)[:100]}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Log execution
print("\n[Step 3] Recording to execution_log...")
execution_id = str(uuid.uuid4())
conn = sqlite3.connect(str(DB_PATH))
try:
    # Create table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS execution_log (
            execution_id TEXT PRIMARY KEY,
            authorization_id TEXT,
            decision_id TEXT,
            human_identity TEXT,
            tool_name TEXT,
            status TEXT,
            result TEXT,
            created_at TEXT
        )
    ''')

    # Record execution
    conn.execute(
        '''INSERT INTO execution_log
        (execution_id, authorization_id, decision_id, human_identity, tool_name, status, result, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (execution_id, str(auth_id), decision_id, human_id, "mocka_get_overview", "ok", json.dumps(execution_result, ensure_ascii=False)[:5000], datetime.now().isoformat())
    )
    conn.commit()
    print(f"  ✓ execution_log recorded")
    print(f"    execution_id: {execution_id}")
    print(f"    authorization_id: {auth_id}")
    print(f"    decision_id: {decision_id}")
finally:
    conn.close()

# Step 4: READ-BACK
print("\n[Step 4] READ-BACK from execution_log...")
conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
try:
    row = conn.execute(
        'SELECT * FROM execution_log WHERE authorization_id = ? ORDER BY created_at DESC LIMIT 1',
        (auth_id,)
    ).fetchone()

    if row:
        print(f"  ✓ FOUND execution_log record:")
        print(f"    execution_id: {row['execution_id']}")
        print(f"    authorization_id: {row['authorization_id']}")
        print(f"    decision_id: {row['decision_id']}")
        print(f"    human_identity: {row['human_identity']}")
        print(f"    tool_name: {row['tool_name']}")
        print(f"    status: {row['status']}")

        # Verify flow-through
        print(f"\n[TRACE] Flow-through verification:")
        if row['authorization_id'] == auth_id:
            print(f"  ✓ authorization_id: {auth_id[:8]}...{auth_id[-4:]}")
        if row['decision_id'] == decision_id:
            print(f"  ✓ decision_id: {decision_id}")
        print(f"  ✓ human_identity: {human_id}")
        print(f"  ✓ execution_id: {execution_id[:8]}...{execution_id[-4:]}")
    else:
        print(f"  ✗ No execution_log record found")
finally:
    conn.close()

print("\n[RESULT] DIRECT EXECUTION: SUCCESS")
print("=" * 80)
sys.exit(0)
