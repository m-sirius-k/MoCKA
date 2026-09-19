# HG-M3-CANONICAL-EVENTS-SCHEMA-V1-PRE-IMPLEMENTATION-SNAPSHOT-20260919

**Date:** 2026-09-19  
**Authority:** Human Gate - Implementation Authorization (Canonical Schema Phase Only)  
**Status:** PRE-IMPLEMENTATION SNAPSHOT (READ-ONLY)  
**Purpose:** Document existing state before Canonical Event Schema v1 implementation

---

## STEP 1: PRE-IMPLEMENTATION SNAPSHOT (Read-Only Verification)

### 1. Related Files List

**Files involved in Event persistence / Write / Read / List / Direct Read:**

| File | Type | Purpose | Impact |
|------|------|---------|--------|
| phi_os/event_gate.py | CORE | Single entry point for events, _write() function, payload validation | HIGH - runtime contract defines INSERT format |
| phi_os/gate_schema.py | VALIDATION | Input payload schema validation | MEDIUM - defines what fields are required |
| phi_os/gate_policy.py | POLICY | Gate policy engine (if exists) | MEDIUM - may define what's allowed to write |
| phi_os/integrity.py | INTEGRITY | sign_event() function for hash chain | MEDIUM - provides trace_id and related_event_id |
| mocka_mcp_server.py | MCP | MCP server with mocka_write_event, mocka_list_events, mocka_read_event | HIGH - implements read/list/direct-read |
| phi_os/tests/test_event_gate.py | TEST | Test schema (31 columns defined in fixture) | MEDIUM - reference for expected schema |
| core_kernel/orchestra/persistence/schema.py | SCHEMA | Orphaned schema definition (5 columns) | LOW - not used in production |
| phi_os/event_replay.py | REPLAY | Event replay functionality (if needed) | LOW - may be affected by schema changes |

**Other files NOT directly modified:**
- All Phase 8 authorization files
- All Decision Ledger files
- All Authority/governance files
- Application code outside Event persistence

---

### 2. SHA / Hash (File Versions at Snapshot Time)

**Current Commit:** `c00af60`
**Branch:** `claude/phase8-monitoring-verification-25fo8q`
**Timestamp:** 2026-09-19

**Key files (by commit):**
- phi_os/event_gate.py: Last changed in commit 430fd7e (2026-08-11)
- mocka_mcp_server.py: Last changed in commit da4d4db (2026-08-11)
- phi_os/tests/test_event_gate.py: Last changed in commit 430fd7e (2026-08-11)

**File Hash (current working tree):**
```
Use: git ls-files -s | grep phi_os/event_gate.py
to get hash at snapshot time
```

---

### 3. Git Status

**Current Status:**
```
On branch claude/phase8-monitoring-verification-25fo8q
Your branch is up to date with 'origin/claude/phase8-monitoring-verification-25fo8q'.
nothing to commit, working tree clean
```

**No uncommitted changes at snapshot time.**

---

### 4. Git Branch

**Current Branch:** `claude/phase8-monitoring-verification-25fo8q`
**Tracking:** `origin/claude/phase8-monitoring-verification-25fo8q`
**Latest Commit:** `c00af60 HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-FINAL-001`

**Other branches:**
- main: `da4d4db GL7-UNENFORCED-CONDITIONS-BUG`

---

### 5. Current Schema Structure

**Actual Database File:**
- Path: `/home/user/MoCKA/mocka_events.db`
- Size: 0 bytes
- Status: EMPTY (never initialized)
- Tables: NONE (no schema created)

**Expected Database Path (per code):**
- event_gate.py line 20: `_REPO_ROOT / 'data' / 'mocka_events.db'`
- mocka_mcp_server.py line 74: `BASE / 'data' / 'mocka_events.db'`
- **LOCATION MISMATCH:** Code expects `data/` subdirectory, but actual file is at root

**Current Tables in mocka_events.db:**
```
NONE - Database completely empty
```

**Tables created elsewhere:**
- mocka_mcp_server.py line 98-104: Creates claude_sessions table in mocka_events.db (for logging)
  ```sql
  CREATE TABLE IF NOT EXISTS claude_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    tool TEXT,
    args TEXT,
    result_summary TEXT
  )
  ```

---

### 6. Event Gate Runtime Contract (Lines 51-95)

**Location:** phi_os/event_gate.py, function _write()

**Runtime INSERT columns (from lines 51-75):**
```python
row = {
    'event_id':        payload.get('event_id', ''),
    'when_ts':         payload.get('when_ts') or payload.get('when', ''),
    'who_actor':       payload.get('who_actor', ''),
    'what_type':       payload.get('what_type', ''),
    'where_component': payload.get('where_component', ''),
    'where_path':      payload.get('where_path', ''),
    'why_purpose':     payload.get('why_purpose', ''),
    'how_trigger':     payload.get('how_trigger', ''),
    'before_state':    payload.get('before_state', ''),
    'after_state':     payload.get('after_state', ''),
    'title':           payload.get('what_title') or payload.get('title', ''),
    'short_summary':   payload.get('description') or payload.get('short_summary', ''),
    'session_id':      payload.get('who_session') or payload.get('session_id', ''),
    '_source':         payload.get('event_source', 'live'),
    'free_note':       (constructed from tags + who_role + event_source + orig_channel),
    'channel_type':    'gate',
    'lifecycle_phase': 'in_operation',
    'risk_level':      'normal',
}
```

**Total columns in INSERT statement (line 86):** 18 columns

**Additional columns updated after INSERT (lines 92-95):**
```python
# UPDATE events SET trace_id = ?, related_event_id = ? WHERE event_id = ?
# trace_id and related_event_id populated via integrity.sign_event()
```

**Total columns involved in write operation:** 20 columns

**Key properties:**
- Empty strings converted to NULL (line 77)
- INSERT OR IGNORE (line 86) — silently ignores duplicate key errors
- Includes integrity chain update (lines 92-95)
- If events table doesn't exist: INSERT silently fails, no error raised

**Failure mode:** If table missing, INSERT OR IGNORE suppresses error and returns success status

---

### 7. MoCKA MCP Server Persistence Path

**Location:** mocka_mcp_server.py lines 70-88

**Database Path Definition:**
```python
BASE = Path(...)  # Root path (Windows: r"C:\Users\sirok\MoCKA", Linux: /home/user/MoCKA)
DB_PATH = BASE / "data" / "mocka_events.db"
```

**Connection Helper (_get_db, lines 94-106):**
- Creates sqlite3 connection to DB_PATH
- Auto-creates claude_sessions table (for session logging)
- Does NOT auto-create events table

**Read Functions:**

1. **_db_read_events(n) — lines 119-141**
   - Queries: `SELECT * FROM events WHERE (data_integrity...) ORDER BY rowid DESC LIMIT n`
   - If table missing: catches exception, returns []
   - Returns all columns from events table as dict list

2. **mocka_list_events — lines 648-651**
   - Calls: `read_events(20)`
   - Returns last 20 events

3. **mocka_read_event — lines 653-657**
   - Calls: `read_events(9999)`
   - In-memory filters: `found = [e for e in read_events(9999) if e.get("event_id") == eid]`
   - Returns single event or {"error": "not found"}

4. **mocka_write_event — lines 666-738**
   - Sends POST to GATE_URL (http://localhost:5000/api/gate/event)
   - Event gate handles persistence
   - Returns response from gate

---

### 8. Database File Status

**Actual File:**
```
Path: /home/user/MoCKA/mocka_events.db
Size: 0 bytes
Ownership: root:root
Permissions: -rw-r--r--
Created: 2026-09-16 22:23 (UTC approx)
Status: EMPTY, never initialized
```

**Database Contents:**
```
SELECT name FROM sqlite_master WHERE type='table';
Result: (empty)
```

**Tables that should exist:**
- events: 31-column table (per Canonical Schema v1)
- claude_sessions: Created by mocka_mcp_server.py on first _get_db() call (NOT yet created)

---

### 9. Existing Tests

**Location:** phi_os/tests/test_event_gate.py

**Test Schema Fixture (lines 25-59):**
```sql
CREATE TABLE events (
  event_id TEXT PRIMARY KEY,
  when_ts TEXT,
  who_actor TEXT,
  what_type TEXT,
  where_component TEXT,
  where_path TEXT,
  why_purpose TEXT,
  how_trigger TEXT,
  channel_type TEXT,
  lifecycle_phase TEXT,
  risk_level TEXT,
  category_ab TEXT,
  target_class TEXT,
  title TEXT,
  short_summary TEXT,
  before_state TEXT,
  after_state TEXT,
  change_type TEXT,
  impact_scope TEXT,
  impact_result TEXT,
  related_event_id TEXT,
  trace_id TEXT,
  free_note TEXT,
  _imported_at TEXT,
  _source TEXT,
  ai_actor TEXT,
  session_id TEXT,
  severity TEXT,
  pattern_score REAL,
  recurrence_flag INTEGER,
  verified_by TEXT
)
```

**Columns in test schema:** 31 total
**Status:** TEST FIXTURE ONLY (monkeypatch, not production)
**Test coverage:** Validates event_gate INSERT/UPDATE logic against fixture schema

---

### 10. Existing Write / Read / List / Direct Read Behavior

**Write Operation (mocka_write_event):**
- Endpoint: /mcp/mocka_write_event (POST)
- Input: Payload dict (what_title, who_actor, description, etc.)
- Process: POST to GATE_URL (http://localhost:5000/api/gate/event)
- Response: {"status": "ok", "event_id": "E20260919_..."} (on success)
- **Current state:** Gate receives event, tries INSERT into mocka_events.db
  - If table missing: INSERT OR IGNORE silently fails
  - Caller receives success response regardless

**Read Operation (mocka_read_event):**
- Endpoint: /mcp/mocka_read_event (POST)
- Input: event_id = "E20260919_..."
- Process: 
  1. Call read_events(9999)
  2. _db_read_events() queries SELECT * FROM events
  3. If table missing: exception caught, returns []
  4. In-memory filter: `found = [e for e in [] if e.get("event_id") == eid]`
  5. Returns: `{"event_id": ...}` if found, else `{"error": "not found"}`
- **Current state:** Always returns "not found" (table missing)

**List Operation (mocka_list_events):**
- Endpoint: /mcp/mocka_list_events (POST)
- Input: count (default 20)
- Process:
  1. Call read_events(20)
  2. _db_read_events() queries SELECT * FROM events
  3. If table missing: exception caught, returns []
  4. Returns last 20 events from list
- **Current state:** Always returns [] (table missing)

**Direct Read Operation (same as Read):**
- Uses read_events() upstream
- Same failure mode

---

## IMPLEMENTATION REQUIREMENTS

### CANONICAL_SCHEMA = APPROVED

Based on Human Gate approval, the following schema must be implemented:

**31 columns, exactly matching:**
- 14 REQUIRED fields (NOT NULL)
- 17 OPTIONAL fields (NULL allowed)
- 3 CONDITIONAL fields (NULL if condition not met)

**No deviations from approved schema design.**

---

### CHANGES REQUIRED

**Location Mismatch (MUST FIX):**
- event_gate.py line 20: Creates DB path as `_REPO_ROOT / 'data' / 'mocka_events.db'`
- mocka_mcp_server.py line 74: Creates DB path as `BASE / 'data' / 'mocka_events.db'`
- Actual file: `/home/user/MoCKA/mocka_events.db` (root, not data/)
- **Resolution:** Must create `data/` subdirectory and migrate DB file, OR update both code paths to match actual location

**Database Initialization:**
- mocka_events.db: 0 bytes, empty
- **Required:** Initialize with Canonical Event Schema v1 (31 columns)
- **Required:** Ensure event_gate INSERT operation succeeds

**Event Gate Integration:**
- event_gate._write() expects events table to exist
- **Currently:** INSERT OR IGNORE silently fails if table missing
- **Required:** Verify events table exists and INSERT succeeds

**MCP Read/Write Verification:**
- mocka_write_event: Must persist events to DB (not just return success)
- mocka_read_event: Must retrieve written events
- mocka_list_events: Must return written events
- **Required:** Write → Read integrity verification

---

## CHANGES NOT REQUIRED

**Following components must NOT be changed:**
- Phase 8 Authorization (CURRENT_UNKNOWN)
- Phase 8 Verification (HALTED)
- RTB binding (UNKNOWN / EVIDENCE_GAP)
- Production Lock (UNKNOWN / EVIDENCE_GAP)
- Authority Model
- Decision Ledger
- Evidence Ledger
- Application code outside Event persistence
- Any other MCP tools

---

## SNAPSHOT SUMMARY

| Item | Status | Impact |
|------|--------|--------|
| **Git State** | CLEAN | No uncommitted changes; ready for implementation |
| **DB File** | EMPTY (0 bytes) | Must initialize with Canonical Schema v1 |
| **DB Location** | MISMATCH | Code expects `data/mocka_events.db`, actual is root `mocka_events.db` |
| **Tables** | NONE | Must create events table with 31 columns |
| **event_gate contract** | VERIFIED | 18 INSERT columns + 2 UPDATE columns; matches v1 (20 total) |
| **Tests** | EXIST | Test schema (31 cols) can validate implementation |
| **Write/Read** | FAILS | Table missing, all read operations return empty |
| **Authorization Scope** | CANONICAL_SCHEMA | Implementation limited to schema + persistence only |

---

**Snapshot Complete: Ready for STEP 2 (implementation scope confirmation)**
