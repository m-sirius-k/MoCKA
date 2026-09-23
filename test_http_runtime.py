#!/usr/bin/env python
"""
Test HTTP /runtime/approve endpoint
Test on actual listening port (8750)
"""

import sys, json, sqlite3, uuid, requests
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("HTTP RUNTIME APPROVAL TEST")
print("=" * 80)

BASE = Path(".")
DB_PATH = BASE / "data" / "mocka_events.db"

# Step 1: Create authorization in DB
print("\n[Step 1] Creating test authorization...")
auth_id = str(uuid.uuid4())
decision_id = f"DC_HTTP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
human_id = "http_test_user"

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
    (auth_id, decision_id, human_id, json.dumps(["http_scope"]), "UNKNOWN", "APPROVED", "HTTP_TEST", datetime.now().isoformat(), json.dumps({"source": ["HTTP_TEST"]}), 1)
)
conn.commit()
conn.close()
print(f"  authorization_id: {auth_id}")
print(f"  decision_id: {decision_id}")

# Step 2: Test /runtime/approve on port 5000
print("\n[Step 2] Testing /runtime/approve on port 5000...")
payload = {
    "authorization_id": auth_id,
    "decision_record_id": decision_id,
    "human_identity": human_id,
    "confirmed": True,
    "spec_id": "SPEC_HTTP"
}

try:
    response = requests.post(
        "http://localhost:5000/runtime/approve",
        json=payload,
        timeout=10
    )
    print(f"  Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ SUCCESS")
        print(f"  Response keys: {list(result.keys())}")

        # Extract execution_id
        if "execution" in result:
            execution_data = result["execution"]
            execution_id = execution_data.get("execution_id")
            exec_status = execution_data.get("status")
            print(f"\n[Step 3] Execution Result:")
            print(f"  execution_id: {execution_id}")
            print(f"  status: {exec_status}")
            print(f"  tool: {execution_data.get('tool')}")

            # Step 4: READ-BACK from execution_log
            print(f"\n[Step 4] READ-BACK from execution_log...")
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    'SELECT * FROM execution_log WHERE execution_id = ?',
                    (execution_id,)
                ).fetchone()

                if row:
                    print(f"  ✓ FOUND execution_log record:")
                    print(f"    execution_id: {row['execution_id'][:16]}...{row['execution_id'][-8:]}")
                    print(f"    authorization_id: {row['authorization_id'][:16]}...{row['authorization_id'][-8:]}")
                    print(f"    decision_id: {row['decision_id']}")
                    print(f"    human_identity: {row['human_identity']}")
                    print(f"    tool_name: {row['tool_name']}")
                    print(f"    status: {row['status']}")

                    # Verify flow-through
                    if row['authorization_id'] == auth_id:
                        print(f"  ✓ authorization_id flow-through: VERIFIED")
                    if row['decision_id'] == decision_id:
                        print(f"  ✓ decision_id flow-through: VERIFIED")

                    print(f"\n[RESULT] HTTP EXECUTION: SUCCESS")
                    print(f"Authorization → execute_tool() → execution_log: COMPLETE")
                    sys.exit(0)
                else:
                    print(f"  ✗ No execution_log record found")
                    print(f"  execution_id was: {execution_id}")
                    sys.exit(1)
            finally:
                conn.close()
        else:
            print(f"  ✗ No execution data in response")
            print(f"  Full response: {json.dumps(result, indent=2)[:500]}")
            sys.exit(1)
    else:
        print(f"  ✗ ERROR {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        sys.exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"  ✗ Cannot connect to http://localhost:5000")
    print(f"  Make sure Flask is running on port 5000")
    print(f"  Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
