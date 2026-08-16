# D-1 Infrastructure Gaps: Exact Specification for Lifecycle and Approval Records
## Version 0.1 (Investigation - READ-ONLY)

**Date**: 2026-08-16
**Format**: INFRASTRUCTURE REQUIREMENTS SPECIFICATION
**Purpose**: Define exact JSON schema, SQL structure, and initialization procedure needed for D-1 (approval gate) to become operational

---

## CRITICAL STATE: What Currently Exists vs What Is Missing

### Currently Implemented in Code

| Component | Status | Location | Details |
|-----------|--------|----------|---------|
| is_publishable() function | IMPLEMENTED | tools/mocka_restrictions.py L31-69 | Fail-Closed approval logic with 9 FC conditions |
| human_gate.py module | IMPLEMENTED | phi_os/human_gate.py L1-321 | Event-sourced state machine, get_state() function |
| Event sourcing schema | IMPLEMENTED | phi_os/human_gate.py L56-67 | SQLite table definition with event storage |
| Request ID generation | IMPLEMENTED | human_gate.py L70-73 | HG{YYYYMMDD}_{micros}{hex} format |
| State transitions | IMPLEMENTED | human_gate.py L25-40 | PENDING/APPROVED/REJECTED/EXPIRED/CANCELED |

### Currently Missing - Infrastructure Gaps

| Component | Impact | Requirement | Type |
|-----------|--------|-------------|------|
| data/inc_lifecycle/ directory | CRITICAL - FC-1 blocks all | Must be created | Filesystem |
| INC-*.json state files | CRITICAL - FC-1 blocks all | One per incident | File schema |
| human_gate_events table records | CRITICAL - FC-7/FC-8 blocks all | One per approval decision | Database records |
| Existing incident approval records | BLOCKING - INC-001/002 can't publish | At least 1 for INC-001 | Human Gate data |

---

## PART 1: INC_LIFECYCLE State File Schema

### File Naming Convention
```
Location: data/inc_lifecycle/{INC_ID}.json
Example:  data/inc_lifecycle/INC-20260401-001.json
Format:   UTF-8 text, single JSON object
```

### Required Schema (v0.1)

```json
{
  "schema_version": "0.1",
  "incident_id": "INC-20260401-001",
  "state": "PUBLISHED",
  "created_at": "2026-04-01T00:00:00Z",
  "updated_at": "2026-08-16T12:00:00Z",
  "transitions": [
    {
      "from": null,
      "to": "DETECTED",
      "timestamp": "2026-04-01T00:00:00Z",
      "reason": "Manual incident creation"
    },
    {
      "from": "DETECTED",
      "to": "ANALYZED",
      "timestamp": "2026-04-01T06:00:00Z",
      "reason": "Analysis complete"
    },
    {
      "from": "ANALYZED",
      "to": "PUBLISHED",
      "timestamp": "2026-08-16T12:00:00Z",
      "reason": "Approved for publication"
    }
  ]
}
```

### Field Definitions

| Field | Type | Required | Domain | Description |
|-------|------|----------|--------|-------------|
| schema_version | string | YES | {"0.1"} | Version of this schema (FC-4 check) |
| incident_id | string | YES | INC-YYYYMMDD-NNN | Must match filename (FC-6 check) |
| state | string | YES | {DETECTED, ANALYZED, PUBLISHED, CLOSED} | Current lifecycle state (FC-5 check) |
| created_at | string (ISO8601) | YES | Valid timestamp | When INC was first created |
| updated_at | string (ISO8601) | YES | Valid timestamp | When last transitioned |
| transitions | array | NO | Array of transition objects | Audit trail (optional but recommended) |

### Field Rules

1. **schema_version**: MUST be "0.1" for current code
   - Checked by: mocka_restrictions.py L51 `rec.get("schema_version") not in KNOWN_SCHEMA_VERSIONS`
   - Rejection: FC-4 "未知の schema_version"

2. **incident_id**: MUST match filename exactly
   - Checked by: mocka_restrictions.py L55 `rec.get("incident_id") != inc_id`
   - Rejection: FC-6 "incident_id がファイル名と不一致"

3. **state**: MUST be one of {DETECTED, ANALYZED, PUBLISHED, CLOSED}
   - Checked by: mocka_restrictions.py L53 `rec.get("state") not in VALID_STATES`
   - Rejection: FC-5 "state が値域外"
   - IMPORTANT: state value does NOT control publication. Publication is controlled by approval axis (Human Gate).

4. **timestamps**: ISO8601 format, UTC timezone recommended
   - Example: "2026-08-16T12:00:00Z" or "2026-08-16T12:00:00+00:00"
   - No validation in current code; for consistency use UTC

5. **transitions** array: Optional audit trail
   - Not checked by is_publishable() but recommended for traceability
   - Each transition should record from→to states and reason

### Actual Files to Create

For existing incidents that need approval, create these files:

#### For INC-20260401-001 (Manual incident, should be PUBLISHED)
```json
{
  "schema_version": "0.1",
  "incident_id": "INC-20260401-001",
  "state": "PUBLISHED",
  "created_at": "2026-04-01T00:00:00Z",
  "updated_at": "2026-08-16T12:00:00Z",
  "transitions": [
    {"from": null, "to": "DETECTED", "timestamp": "2026-04-01T00:00:00Z", "reason": "Manual creation by Claude Sonnet 4.6"},
    {"from": "DETECTED", "to": "ANALYZED", "timestamp": "2026-04-01T06:00:00Z", "reason": "Analysis completed"},
    {"from": "ANALYZED", "to": "PUBLISHED", "timestamp": "2026-08-16T12:00:00Z", "reason": "Approved via D-1 gate"}
  ]
}
```

#### For INC-20260401-002 (Auto-generated, unapproved, should be ANALYZED)
```json
{
  "schema_version": "0.1",
  "incident_id": "INC-20260401-002",
  "state": "ANALYZED",
  "created_at": "2026-04-01T12:00:00Z",
  "updated_at": "2026-04-01T12:00:00Z",
  "transitions": [
    {"from": null, "to": "DETECTED", "timestamp": "2026-04-01T12:00:00Z", "reason": "Auto-generated by risk_engine"},
    {"from": "DETECTED", "to": "ANALYZED", "timestamp": "2026-04-01T12:00:00Z", "reason": "5W1H analysis appended"}
  ]
}
```

---

## PART 2: Human Gate Event Records Schema

### Overview

Human Gate uses **event sourcing** (not state storage). The human_gate_events SQLite table records a sequence of state transitions (submit → approve/reject → ...). The current state is computed by reading the LATEST event for a given request_id.

### Table Schema

```sql
CREATE TABLE IF NOT EXISTS human_gate_events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT,
    type TEXT,
    action TEXT,
    request_id TEXT,
    payload TEXT,
    previous_state TEXT,
    next_state TEXT
)
```

### Field Definitions (human_gate_events columns)

| Column | Type | Example | Rules |
|--------|------|---------|-------|
| event_id | TEXT (PK) | HG20260816_123456789abc | Generated by _next_event_id(); must be unique |
| timestamp | TEXT (ISO8601) | 2026-08-16T12:00:00+00:00 | Current UTC time when event recorded |
| type | TEXT | HUMAN_GATE_EVENT | Always "HUMAN_GATE_EVENT" for approval records |
| action | TEXT | submit, approve, reject | Must be one of {submit, approve, reject, expire, cancel} |
| request_id | TEXT | INC-LIFECYCLE-INC-20260401-001 | Key for grouping events; format: INC-LIFECYCLE-{INC_ID} |
| payload | TEXT (JSON string) | {"note":"approved by admin"} | JSON serialized payload (can be empty "{}") |
| previous_state | TEXT (nullable) | PENDING | Previous state before this transition; NULL for initial submit |
| next_state | TEXT | APPROVED | Resulting state after this action |

### State Transition Rules

```
PENDING (initial via submit)
  ├→ APPROVED (via approve action)
  ├→ REJECTED (via reject action)
  ├→ EXPIRED (via expire action)
  ├→ CANCELED (via cancel action)
  
APPROVED
  └→ CANCELED (via cancel action only)
  
REJECTED
  └→ CANCELED (via cancel action only)
  
EXPIRED
  └→ CANCELED (via cancel action only)
```

### Request ID Format

```
Format: INC-LIFECYCLE-{INC_ID}
Prefix: INC-LIFECYCLE-
Example: INC-LIFECYCLE-INC-20260401-001
```

This prefix is defined in mocka_restrictions.py L14:
```python
HUMAN_GATE_REQUEST_PREFIX = "INC-LIFECYCLE-"
```

### Records to Create for Existing Incidents

#### Record 1: INC-20260401-001 Approval Chain

```sql
INSERT INTO human_gate_events
(event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
VALUES (
  'HG20260804_000000001aaa',
  '2026-08-04T10:00:00Z',
  'HUMAN_GATE_EVENT',
  'submit',
  'INC-LIFECYCLE-INC-20260401-001',
  '{"incident_id":"INC-20260401-001","reason":"Manual incident approval","submitted_by":"investigation"}',
  NULL,
  'PENDING'
);

INSERT INTO human_gate_events
(event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
VALUES (
  'HG20260816_000000001bbb',
  '2026-08-16T12:00:00Z',
  'HUMAN_GATE_EVENT',
  'approve',
  'INC-LIFECYCLE-INC-20260401-001',
  '{"approved_by":"investigation","reason":"Manual incident with valid content"}',
  'PENDING',
  'APPROVED'
);
```

#### Record 2: INC-20260401-002 Rejection (IMPORTANT: NOT approved, remains in ANALYZED)

```sql
INSERT INTO human_gate_events
(event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
VALUES (
  'HG20260804_000000002aaa',
  '2026-08-04T11:00:00Z',
  'HUMAN_GATE_EVENT',
  'submit',
  'INC-LIFECYCLE-INC-20260401-002',
  '{"incident_id":"INC-20260401-002","reason":"Auto-generated INC requires approval"}',
  NULL,
  'PENDING'
);

INSERT INTO human_gate_events
(event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
VALUES (
  'HG20260816_000000002bbb',
  '2026-08-16T12:00:00Z',
  'HUMAN_GATE_EVENT',
  'reject',
  'INC-LIFECYCLE-INC-20260401-002',
  '{"rejected_by":"investigation","reason":"Auto-generated; requires manual review and confirmation"}',
  'PENDING',
  'REJECTED'
);
```

**OR** (alternative: leave PENDING for delayed approval)

```sql
INSERT INTO human_gate_events
(event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
VALUES (
  'HG20260804_000000002aaa',
  '2026-08-04T11:00:00Z',
  'HUMAN_GATE_EVENT',
  'submit',
  'INC-LIFECYCLE-INC-20260401-002',
  '{"incident_id":"INC-20260401-002","reason":"Auto-generated INC awaiting approval"}',
  NULL,
  'PENDING'
);
-- No approve/reject record; leaves INC-002 in PENDING (not published until approved)
```

---

## PART 3: Execution Sequence for D-1 Infrastructure Setup

### Step 1: Create Directory
```bash
mkdir -p C:\Users\sirok\MoCKA\data\inc_lifecycle
# On Linux systems during investigation:
mkdir -p /home/user/MoCKA/data/inc_lifecycle
```

### Step 2: Create State Files for Existing Incidents

Create `/data/inc_lifecycle/INC-20260401-001.json`:
- Content: PUBLISHED state (defined in Part 1)
- Encoding: UTF-8
- Validation: mocka_check_utf8() after creation

Create `/data/inc_lifecycle/INC-20260401-002.json`:
- Content: ANALYZED state (not PUBLISHED)
- Encoding: UTF-8
- Validation: mocka_check_utf8() after creation

### Step 3: Initialize SQLite Table

Human Gate's `_ensure_table()` function (lines 55-67 of human_gate.py) creates the table automatically on first call:

```python
def _ensure_table(conn) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS human_gate_events (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            action TEXT,
            request_id TEXT,
            payload TEXT,
            previous_state TEXT,
            next_state TEXT
        )
    ''')
```

**Automatic trigger**: First call to any human_gate function (get_state, submit, approve, etc.) will execute CREATE TABLE IF NOT EXISTS.

**Manual verification** (if manual insert needed):
```bash
sqlite3 C:\Users\sirok\MoCKA\data\mocka_events.db
.tables                                  # Verify human_gate_events exists
.schema human_gate_events                # Check structure
```

### Step 4: Insert Approval Records into human_gate_events

Use sqlite3 command-line or Python sqlite3 module:

```python
import sqlite3
from pathlib import Path

db_path = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
conn = sqlite3.connect(db_path)

# INC-001 Approval Chain
conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260804_000000001aaa', '2026-08-04T10:00:00Z', 'HUMAN_GATE_EVENT', 'submit',
     'INC-LIFECYCLE-INC-20260401-001', '{"reason":"Manual incident"}', None, 'PENDING')
)

conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260816_000000001bbb', '2026-08-16T12:00:00Z', 'HUMAN_GATE_EVENT', 'approve',
     'INC-LIFECYCLE-INC-20260401-001', '{"approved_by":"system"}', 'PENDING', 'APPROVED')
)

# INC-002 Submit (leave as PENDING, NOT approved)
conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260804_000000002aaa', '2026-08-04T11:00:00Z', 'HUMAN_GATE_EVENT', 'submit',
     'INC-LIFECYCLE-INC-20260401-002', '{"reason":"Auto-generated"}', None, 'PENDING')
)

conn.commit()
conn.close()
```

---

## PART 4: Failure Mode Analysis

### What Happens When Each Piece Is Missing

#### Scenario A: State Files Missing (FC-1)

**Condition**: `data/inc_lifecycle/` directory exists but `INC-20260401-001.json` does not.

**Code Path**: mocka_restrictions.py L40-41
```python
if not os.path.exists(path):
    return False, "FC-1 state ファイルが存在しない"
```

**Behavior**:
- is_publishable("INC-20260401-001") returns (False, "FC-1...")
- generate_restrictions() line 81 `if not allowed:` → skips this incident
- INC-001 added to withheld list (line 82)
- INC-001 DOES NOT appear in GPT_RESTRICTIONS.md

**Current Status**: This is HAPPENING NOW. INC-001 exists but state file doesn't, so GPT_RESTRICTIONS.md generation would skip it.

#### Scenario B: State File Unreadable (FC-2)

**Condition**: File exists but can't be read (permission issue, binary encoding, etc.)

**Code Path**: mocka_restrictions.py L42-46
```python
try:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
except OSError as e:
    return False, f"FC-2 state ファイルを読めない({e})"
```

**Behavior**: Returns (False, "FC-2..."), incident withheld.

**Prevention**: Use UTF-8 encoding when creating files.

#### Scenario C: State File Invalid JSON (FC-3)

**Condition**: File exists and is readable but contains malformed JSON.

**Code Path**: mocka_restrictions.py L47-50
```python
try:
    rec = json.loads(raw)
except ValueError as e:
    return False, f"FC-3 state ファイルのJSONが不正({e})"
```

**Behavior**: Returns (False, "FC-3..."), incident withheld.

**Prevention**: Validate JSON before writing.

#### Scenario D: Unknown schema_version (FC-4)

**Condition**: schema_version is "1.0" or "0.2" or any value not in KNOWN_SCHEMA_VERSIONS.

**Code Path**: mocka_restrictions.py L51-52
```python
if rec.get("schema_version") not in KNOWN_SCHEMA_VERSIONS:
    return False, f"FC-4 未知の schema_version({rec.get('schema_version')})"
```

**Current KNOWN_SCHEMA_VERSIONS**: {"0.1"} (mocka_restrictions.py L12)

**Behavior**: Returns (False, "FC-4..."), incident withheld.

**Forward Compatibility**: When schema evolves to v0.2, must update KNOWN_SCHEMA_VERSIONS before creating files with v0.2.

#### Scenario E: Invalid state value (FC-5)

**Condition**: state is "INITIATED" or "TODO" or any value not in VALID_STATES.

**Code Path**: mocka_restrictions.py L53-54
```python
if rec.get("state") not in VALID_STATES:
    return False, f"FC-5 state が値域外({rec.get('state')})"
```

**Current VALID_STATES**: {"DETECTED", "ANALYZED", "PUBLISHED", "CLOSED"} (L13)

**Behavior**: Returns (False, "FC-5..."), incident withheld.

**Design Intent**: Even though state doesn't control publication (approval axis does), invalid state signals malformed lifecycle file.

#### Scenario F: incident_id Mismatch (FC-6)

**Condition**: File is `INC-20260401-001.json` but contains `"incident_id": "INC-20260401-999"`.

**Code Path**: mocka_restrictions.py L55-56
```python
if rec.get("incident_id") != inc_id:
    return False, f"FC-6 incident_id がファイル名と不一致({rec.get('incident_id')})"
```

**Behavior**: Returns (False, "FC-6..."), incident withheld.

**Design Intent**: Prevents file swaps and data corruption.

#### Scenario G: No Human Gate Approval Record (FC-7)

**Condition**: No events in human_gate_events for request_id "INC-LIFECYCLE-INC-20260401-001".

**Code Path**: mocka_restrictions.py L61-65
```python
try:
    approval = human_gate_get_state(request_id)
except Exception as e:
    return False, f"FC-9 承認状態の取得に失敗({e})"
if approval is None:
    return False, f"FC-7 承認軸にレコードが存在しない({request_id})"
```

**Behavior**: returns (False, "FC-7..."), incident withheld.

**Current Status**: This is HAPPENING NOW. Neither INC-001 nor INC-002 have approval records, so both would be rejected.

**Fix**: Insert submit + approve records for INC-001; leave INC-002 in PENDING or REJECTED.

#### Scenario H: Approval Not APPROVED (FC-8)

**Condition**: Latest event for request_id has next_state="REJECTED" or "PENDING" or "CANCELED".

**Code Path**: mocka_restrictions.py L66-67
```python
if approval != "APPROVED":
    return False, f"FC-8 承認状態が APPROVED でない({approval})"
```

**Behavior**: Returns (False, "FC-8..."), incident withheld.

**Example**: INC-002 would be rejected here if approval state is REJECTED or PENDING.

#### Scenario I: Human Gate Unavailable (FC-9)

**Condition**: Exception during human_gate_get_state() call (e.g., database corruption, permission denied).

**Code Path**: mocka_restrictions.py L60-63
```python
try:
    approval = human_gate_get_state(request_id)
except Exception as e:
    return False, f"FC-9 承認状態の取得に失敗({e})"
```

**Behavior**: Returns (False, "FC-9..."), incident withheld.

**Redundancy Note**: This is a catch-all for any unexpected error in approval axis lookup.

---

## PART 5: Current State Paradox

### Observation

GPT_RESTRICTIONS.md (generated 2026-07-31 18:07:02) contains INC-001 content, but:
1. INC-001.json state file does not exist
2. INC-LIFECYCLE-INC-20260401-001 approval record does not exist
3. Current is_publishable() would REJECT INC-001 (FC-1 failure)

### Hypothesis: Legacy Generation Path

**Most Likely**: GPT_RESTRICTIONS.md was generated on 2026-07-31 using an earlier version of mocka_restrictions.py that did NOT have is_publishable() checks. The "# RC-B最小実装(DC_20260731_006 / DC_20260731_007)" comment (line 10) suggests the approval gate was recently added.

**Timeline**:
- 2026-07-31 18:07: GPT_RESTRICTIONS.md generated (possibly without approval checks)
- After 2026-07-31: is_publishable() function added (Decision DC_20260731_006/007 approved)
- Current state: Code expects infrastructure that doesn't exist yet

### Implication

**If pipeline runs today with current code**:
```
risk_engine.py → generate new incident (e.g., INC-20260815-xxx)
                ↓
mocka_restrictions.py:
  - Tries to publish INC-20260815-xxx
  - Checks is_publishable()
  - Fails FC-1 (no state file)
  - Withholds from output
  ↓
Result: NEW incidents NOT published; existing INC-001 also withheld
```

**This is correct behavior (Fail-Closed design)**. The infrastructure simply wasn't created yet.

---

## PART 6: Success Criteria for D-1 Operational Readiness

### Minimal Setup (Allows existing INCs to publish)

| Artifact | Type | Status | Required For |
|----------|------|--------|--------------|
| data/inc_lifecycle/ directory | Directory | Must create | All FC-1 checks pass |
| INC-20260401-001.json | File | Must create | INC-001 publication |
| INC-20260401-002.json | File | Must create | INC-002 lifecycle tracking |
| human_gate_events table | DB table | Auto-created via _ensure_table() | FC-7/FC-8 checks |
| HG20260804_000000001aaa event | DB record | Must insert | INC-001 submit |
| HG20260816_000000001bbb event | DB record | Must insert | INC-001 approve |
| HG20260804_000000002aaa event | DB record | Must insert | INC-002 submit |

### Verification Procedure

After setup, run this verification:

```python
# Test 1: State files readable
from pathlib import Path
import json

state_files = [
    r"C:\Users\sirok\MoCKA\data\inc_lifecycle\INC-20260401-001.json",
    r"C:\Users\sirok\MoCKA\data\inc_lifecycle\INC-20260401-002.json",
]

for filepath in state_files:
    p = Path(filepath)
    assert p.exists(), f"Missing: {filepath}"
    content = json.loads(p.read_text(encoding="utf-8"))
    assert content["schema_version"] == "0.1"
    assert content["incident_id"] == p.stem
    print(f"OK: {filepath}")

# Test 2: Human Gate records present
import sqlite3

conn = sqlite3.connect(r"C:\Users\sirok\MoCKA\data\mocka_events.db")
cursor = conn.cursor()

requests = [
    ("INC-LIFECYCLE-INC-20260401-001", "APPROVED"),
    ("INC-LIFECYCLE-INC-20260401-002", "PENDING"),  # or REJECTED
]

for request_id, expected_state in requests:
    cursor.execute(
        "SELECT next_state FROM human_gate_events WHERE request_id = ? ORDER BY timestamp DESC, event_id DESC LIMIT 1",
        (request_id,)
    )
    row = cursor.fetchone()
    assert row is not None, f"No records for {request_id}"
    actual_state = row[0]
    assert actual_state == expected_state, f"{request_id}: expected {expected_state}, got {actual_state}"
    print(f"OK: {request_id} = {actual_state}")

conn.close()

# Test 3: is_publishable() now returns True for INC-001
sys.path.insert(0, r"C:\Users\sirok\MoCKA")
from tools.mocka_restrictions import is_publishable

allowed, reason = is_publishable("INC-20260401-001")
assert allowed, f"INC-001 should be publishable: {reason}"
print("OK: INC-001 is publishable")

allowed, reason = is_publishable("INC-20260401-002")
assert not allowed, f"INC-002 should NOT be publishable yet"
print("OK: INC-002 correctly withheld")
```

### Expected Outcome After Setup

Run mocka_restrictions.py:

```bash
python C:\Users\sirok\MoCKA\tools\mocka_restrictions.py
```

Expected GPT_RESTRICTIONS.md output:

```markdown
# GPT作業禁止事項（自動生成）
生成日時：2026-08-16 XX:XX:XX
ソース：docs/incidents/INC-*.md

---

## 常時禁止（全タスク共通）
...

### INC-20260401-001 より
... (actual "## 再発防止" content from INC-001) ...

[非掲載リスト]
- INC-20260401-002: FC-8 承認状態が APPROVED でない(PENDING)
```

---

## SUMMARY FOR R01 REVIEW

### Gap Confirmation

**Gap 1**: data/inc_lifecycle/ directory does not exist
- **Fix**: mkdir -p

**Gap 2**: INC-*.json state files do not exist for any incident
- **Fix**: Create 2 files with exact schema specified in Part 1
- **Validation**: mocka_check_utf8 after creation

**Gap 3**: human_gate_events table is empty (no approval records)
- **Fix**: Insert 3 records (1 submit + 1 approve for INC-001; 1 submit for INC-002)
- **Table creation**: Automatic via _ensure_table() on first call

### Prerequisite for Case 4 Validation

**Before running Case 4 tests**:
1. Create data/inc_lifecycle/ and JSON state files
2. Populate human_gate_events with approval records
3. Verify is_publishable() returns (True, "APPROVED") for INC-001
4. Verify is_publishable() returns (False, "FC-8...") for INC-002
5. Run mocka_restrictions.py and confirm INC-001 appears in GPT_RESTRICTIONS.md

**Once infrastructure exists**: Case 4 can be validated with test data (Section 4.2 requirements met).

---

