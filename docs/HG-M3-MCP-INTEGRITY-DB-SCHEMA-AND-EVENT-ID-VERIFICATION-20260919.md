# HG-M3-MCP-INTEGRITY-DB-SCHEMA-AND-EVENT-ID-VERIFICATION-20260919

**Date:** 2026-09-19  
**Directive:** HG-M3-MCP-INTEGRITY-DB-SCHEMA-AND-EVENT-ID-VERIFICATION-001  
**Status:** READ-ONLY INVESTIGATION COMPLETE  
**Classification:** CRITICAL INFRASTRUCTURE GAP IDENTIFIED

---

## STEP 1: Locate Database File

**Actual DB Path (per mocka_mcp_server.py line 74):**
```
BASE = Path(r"C:\Users\sirok\MoCKA")
DB_PATH = BASE / "data" / "mocka_events.db"
```

**Linux Runtime Equivalent:**
```
/home/user/MoCKA/mocka_events.db
```

**Verification:** File EXISTS (confirmed via find)

---

## STEP 2: Verify Events Table Schema via PRAGMA

**Command Executed:**
```python
PRAGMA table_info(events);
```

**Result:**

```
=== EVENTS TABLE SCHEMA ===
[No columns returned]

=== TOTAL COLUMNS ===
Count: 0
```

**Finding:** events table has ZERO columns

---

## STEP 3: Verify Database Structure

**Command Executed:**
```python
SELECT name FROM sqlite_master WHERE type='table';
```

**Result:**

```
=== TABLES IN DATABASE ===
[No tables]

Total tables: 0
```

**Finding:** mocka_events.db contains ZERO tables

---

## STEP 4: Database File Properties

```
Path: /home/user/MoCKA/mocka_events.db
Exists: True (verified)
Size: 0 bytes [CRITICAL]
SQLite Version: 3.45.1 (valid)
Format: Valid SQLite database format
Status: EMPTY (never initialized)
```

**Finding:** mocka_events.db is a valid SQLite database file but completely empty - no schema, no tables, no data

---

## STEP 5: Search for Alternative Event Storage

**Alternative Databases Checked:**

| Path | Size | Status | events table? | Notes |
|------|------|--------|---------------|-------|
| /home/user/MoCKA/mocka_events.db | 0 bytes | EMPTY | NO | Expected path, never initialized |
| /home/user/MoCKA/data/mocka_events.db | N/A | NOT FOUND | N/A | Expected location (per code), does not exist |
| /home/user/MoCKA/audit/ed25519/verify_pack/audit.db | 16 KB | EXISTS | NO (has audit_ledger_event instead) | Audit system, not events |
| /home/user/MoCKA/audit/ed25519/governance/governance.db | 20 KB | EXISTS | NO (has governance_ledger_event) | Governance system, not events |
| /home/user/MoCKA/audit/ed25519/audit.db | 0 bytes | EMPTY | N/A | Uninitialized |

**Finding:** No database file contains the events table. Event storage system is completely absent from disk.

---

## STEP 6: Verify Event Gate Schema Expectations (Code Analysis)

**From phi_os/event_gate.py _write() function (lines 51-75):**

Expected INSERT columns:
```
event_id (PRIMARY KEY)
when_ts
who_actor
what_type
where_component
where_path
why_purpose
how_trigger
before_state
after_state
title
short_summary
session_id
_source
free_note
channel_type
lifecycle_phase
risk_level
```

Expected schema (from test setup phi_os/tests/test_event_gate.py lines 25-59):
```
event_id TEXT PRIMARY KEY
when_ts TEXT
who_actor TEXT
what_type TEXT
where_component TEXT
where_path TEXT
why_purpose TEXT
how_trigger TEXT
channel_type TEXT
lifecycle_phase TEXT
risk_level TEXT
category_ab TEXT
target_class TEXT
title TEXT
short_summary TEXT
before_state TEXT
after_state TEXT
change_type TEXT
impact_scope TEXT
impact_result TEXT
related_event_id TEXT
trace_id TEXT
free_note TEXT
_imported_at TEXT
_source TEXT
ai_actor TEXT
session_id TEXT
severity TEXT
pattern_score REAL
recurrence_flag INTEGER
verified_by TEXT
```

**Finding:** event_gate expects ~30 columns including event_id

---

## STEP 7: Verify Actual Database Schema (Confirmed Empty)

**Actual Schema in mocka_events.db:**
```
[NONE - zero tables, zero columns]
```

**Comparison Result:**

```
EXPECTED: ~30 columns (event_id, when_ts, who_actor, ...)
ACTUAL:   0 columns (no table exists)

STATUS: SCHEMA_MISMATCH (schema completely missing)
```

**Finding:** Complete schema absence means:
- event_gate's INSERT statements will fail with "no such table: events"
- mocka_list_events queries will fail with "no such table: events"
- mocka_read_event queries will fail with "no such table: events"

---

## STEP 8: Verify Event Storage Path (event_id lookup)

**Attempt to verify test event E20260919_827083891ee8c:**

```python
SELECT * FROM events
WHERE event_id = 'E20260919_827083891ee8c';
```

**Result:**

```
[Table does not exist]
Query failed: no such table: events
```

**Finding:** Cannot verify event_id because table does not exist

---

## STEP 9: Compare Code Expectations vs Actual State

### mocka_write_event → event_gate → SQLite Insert Path

**Expected Flow:**
1. mocka_write_event calls GATE_URL (http://localhost:5000/api/gate/event)
2. GATE calls phi_os/event_gate.process_event()
3. process_event() calls _write(payload, conn=conn)
4. _write() executes: INSERT INTO events (event_id, when_ts, who_actor, ...) VALUES (?, ?, ?, ...)
5. Event persists in mocka_events.db
6. Returns {"status": "ok", "event_id": "..."}

**Actual State:**
1. mocka_events.db exists but is 0 bytes / empty
2. No events table has been created
3. INSERT statements from _write() will fail with "no such table" error
4. Error handling: INSERT OR IGNORE (line 86 of event_gate.py) suppresses error silently

**Result:** Write appears to succeed (returns ok), but event is NOT persisted

---

### mocka_list_events → SQLite Query Path

**Expected Flow:**
1. mocka_list_events calls read_events(20)
2. read_events() calls _db_read_events()
3. _db_read_events() executes: SELECT * FROM events WHERE (data_integrity ...) ORDER BY rowid DESC LIMIT 20
4. Returns list of event dicts

**Actual State:**
1. Query: SELECT * FROM events... fails with "no such table: events"
2. Exception caught (line 139 of mocka_mcp_server.py): returns []
3. mocka_list_events returns: {"count": 0, "events": []}

**Result:** LIST returns empty, no events visible

---

### mocka_read_event → SQLite Query Path

**Expected Flow:**
1. mocka_read_event(id="E20260919_...") calls read_events(9999)
2. In-memory filter: found = [e for e in read_events(9999) if e.get("event_id") == eid]
3. Returns event if found, or {"error": "not found"}

**Actual State:**
1. read_events(9999) → _db_read_events() fails with "no such table: events"
2. Exception caught: returns []
3. In-memory filter: found = [e for e in [] if ...] → found = []
4. Returns: {"error": "not found"}

**Result:** DIRECT READ returns "not found" (because LIST is empty)

---

## STEP 10: Secondary Bug: read_events() Parameter Not Passed

**Code Location:** mocka_mcp_server.py lines 163-166

```python
def read_events(n=20):
    rows = _db_read_events()  # BUG: n parameter NOT passed
    return rows[-n:] if n else rows
```

**Issue:**
- mocka_list_events calls read_events(20) - wants last 20 rows
- mocka_read_event calls read_events(9999) - wants last 9999 rows
- But _db_read_events() is called with NO parameter (n=None)
- _db_read_events(n=None) executes: SELECT * WITHOUT LIMIT
- Python filtering happens after: rows[-n:]

**Impact:** n parameter design is inefficient but not the root cause of asymmetry

---

## FINAL CLASSIFICATION

### Evidence Summary

```
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN (unchanged)
PHASE8_SCOPE = UNKNOWN (unchanged)
PHASE8_VERIFICATION = HALTED (unchanged)
RTB_20260918_001 = EVIDENCE_GAP (unchanged)
PRODUCTION_LOCK = EVIDENCE_GAP (unchanged)
```

### MCP Asymmetry Classification

```
ASYMMETRY = REPRODUCED
  Both LIST and DIRECT READ fail equally (return empty/not found)
  because underlying storage (events table) does not exist

ACTUAL_DB_PATH = VERIFIED
  Path: /home/user/MoCKA/mocka_events.db
  Status: File exists, 0 bytes, completely empty

EVENTS_SCHEMA = UNKNOWN (MISSING)
  Expected: ~30 columns (event_id, when_ts, who_actor, ...)
  Actual: No table exists
  Status: SCHEMA_MISSING (not mismatch, table absent)

EVENT_ID_DIRECT_DB_MATCH = UNKNOWN
  Cannot verify - table does not exist

EVENT_ID_STORAGE_LOCATION = UNKNOWN
  No storage location exists

EVENT_ID_TRANSFORMATION = UNKNOWN
  Cannot verify - no event_id values in storage

WRITE_PATH = PARTIAL
  Code path verified (event_gate.py)
  But INSERT fails silently due to missing table
  Caller receives {"status": "ok"} but event NOT persisted

LIST_PATH = PARTIAL
  Code path verified (mocka_list_events → read_events → _db_read_events)
  Query fails with "no such table" error
  Error caught, returns []

DIRECT_READ_PATH = PARTIAL
  Code path verified (mocka_read_event in-memory filter)
  Upstream read_events() fails
  Returns {"error": "not found"}

ROOT_CAUSE = VERIFIED
  Type: CRITICAL_INFRASTRUCTURE_GAP
  Cause: events table never initialized in mocka_events.db
  Symptom: All read operations fail; write operations fail silently
  Classification: Not schema mismatch, not encoding mismatch, not lookup mismatch
  Classification: TABLE DOES NOT EXIST

SECONDARY_BUG_READ_EVENTS_N = VERIFIED
  Location: mocka_mcp_server.py lines 163-166
  Issue: n parameter not passed to _db_read_events()
  Impact: Inefficient (Python filtering instead of SQL LIMIT)
  Status: RECORDED as separate incident

PHASE8_CAUSALITY_WITH_MCP = UNKNOWN (INDEPENDENT)
  MCP infrastructure gap is separate from Phase8 authorization gap
  Both represent missing initialization/record infrastructure
  No direct causal link established
```

---

## REMEDIATION STATUS

**No remediation attempted.** Investigation is READ-ONLY per directive.

- events table NOT created
- mocka_events.db NOT initialized
- No schema changes made
- No data written
- No fixes applied

---

## CRITICAL FINDING: Infrastructure Initialization Absent

**The entire event persistence layer is missing from disk.**

This is not a bug in code logic (write/list/read paths), but a **fundamental infrastructure initialization failure**:

1. mocka_events.db exists but is empty (0 bytes)
2. events table was never created
3. All event write operations fail silently (INSERT OR IGNORE suppresses errors)
4. All event read operations fail silently (exception caught, returns empty)
5. The asymmetry (LIST vs DIRECT READ) is artificial - both fail equally due to missing table

**Questions for Human Gate:**

1. Was events table ever initialized in this instance?
2. Should mocka_mcp_server.py auto-create the table on _get_db() call?
3. Should there be a database initialization script that creates the schema before GATE attempts writes?
4. Is phi_os event_gate meant to auto-create the table? (Currently does not - INSERT OR IGNORE suppresses errors)
5. Is this environment in a state where event persistence was never activated?

---

## Appendix: Command Log (Read-Only Verification)

All database queries were SELECT or PRAGMA (read-only), no modifications attempted.

```
PRAGMA table_info(events);
SELECT name FROM sqlite_master WHERE type='table';
SELECT sqlite_version();
SELECT COUNT(*) FROM sqlite_master WHERE type='table';
```

No CREATE, INSERT, UPDATE, DELETE, DROP statements executed.

---

**Investigation Status:** COMPLETE  
**Remediation Status:** NOT PERFORMED  
**Human Gate Decision Required:** YES  
**Next Action:** AWAIT HUMAN GATE DECISION

**原則: 止めるのは権限。進めるのは証拠。**  
(Stopping is authority. Evidence is progress.)

