# HG-M3-CANONICAL-EVENTS-SCHEMA-V1-IMPLEMENTATION-DIFF-20260919

**Date:** 2026-09-19  
**Authority:** Human Gate - Implementation Authorization (Canonical Schema Phase Only)  
**Status:** IMPLEMENTATION DIFF & SCOPE CONFIRMATION (READ-ONLY)  
**Purpose:** Identify exact changes required to implement Canonical Event Schema v1

---

## SUMMARY: CANONICAL SCHEMA v1 IMPLEMENTATION CHANGES

| Component | Status | Change Type | Impact | Authorization |
|-----------|--------|------------|--------|-----------------|
| mocka_events.db | EMPTY → INITIALIZED | Schema Creation | HIGH | REQUIRED |
| events table | MISSING → CREATED | Table Creation | HIGH | REQUIRED |
| event_gate.py | NO CHANGE | Verification | MEDIUM | VERIFICATION ONLY |
| mocka_mcp_server.py | NO CHANGE | Verification | MEDIUM | VERIFICATION ONLY |
| DB path resolution | MISMATCH → RESOLVED | Code/File Alignment | MEDIUM | DEPENDS ON DECISION |
| Write verification | UNKNOWN → VERIFIED | Testing | MEDIUM | REQUIRED |
| Read verification | UNKNOWN → VERIFIED | Testing | MEDIUM | REQUIRED |

---

## CHANGE DETAILS

### CHANGE 1: Database Path Resolution

**Current State:**
- event_gate.py line 20: `DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')`
- mocka_mcp_server.py line 74: `DB_PATH = BASE / 'data' / 'mocka_events.db'`
- Actual file: `/home/user/MoCKA/mocka_events.db` (root, not data/)

**Decision Point:**
```
Option A: CREATE data/ subdirectory and move file
  - Aligns with code expectations
  - Requires: mkdir -p data/ && mv mocka_events.db data/mocka_events.db
  - Impact: No code changes needed

Option B: KEEP file at root, update both code paths
  - Aligns with actual file location
  - Requires: Change line 20 in event_gate.py, line 74 in mocka_mcp_server.py
  - Impact: Code changes in 2 files, but matches current layout

Option C: SYMLINK (not recommended)
  - Fragile, not portable
  - Not recommended for production

RECOMMENDATION: Option A (follow code expectations)
SCOPE: File organization only (no schema/logic change)
AUTHORIZATION: CANONICAL_SCHEMA phase (yes)
```

---

### CHANGE 2: Event Table Creation

**Location:** mocka_events.db

**Current:**
- Table: MISSING
- Columns: NONE
- Rows: N/A

**Required (Canonical Event Schema v1):**
```sql
CREATE TABLE events (
  -- Identity & Uniqueness
  event_id TEXT PRIMARY KEY,
    -- Format: E{YYYYMMDD}_{micros_9d}{hex_4d}
    -- Properties: time-ordered, collision-free, no DB lookup

  -- Temporal
  when_ts TEXT NOT NULL,
    -- Format: ISO 8601 timestamp with timezone
    -- Properties: UTC, immutable, set at record time

  -- Actor & Source (5W1H: WHO)
  who_actor TEXT NOT NULL,
    -- Actor identifier (e.g., Claude-sonnet-4-6, gpt-4o, human-name)
    -- Who performed the action

  who_role TEXT,
    -- executor | auditor | human | automation
    -- Role context for the actor

  who_session TEXT NOT NULL,
    -- Session identifier for correlation (e.g., SESSION_YYYYMMDD_HHMMSS)
    -- May span multiple events

  -- Event Type & Description (5W1H: WHAT)
  what_type TEXT NOT NULL,
    -- Enumerated: file_write, git_commit, test_run, incident, todo_update, claude_mcp, etc.
    -- Type of action/event

  title TEXT NOT NULL,
    -- One-line summary (what_title from payload)
    -- Human-readable title

  short_summary TEXT,
    -- Description (from payload description or short_summary)
    -- Extended summary of event

  description TEXT,
    -- Alias field for compatibility
    -- May be same as short_summary or separate

  -- Location & Component (5W1H: WHERE)
  where_component TEXT NOT NULL,
    -- Component/module name (e.g., mocka_mcp_server, event_gate, executor_orchestrator)
    -- Where in system the action occurred

  where_path TEXT NOT NULL,
    -- File path, URL, or component path
    -- Specific location affected

  -- Purpose & Trigger (5W1H: WHY, HOW)
  why_purpose TEXT NOT NULL,
    -- Purpose of the action (10+ characters recommended)
    -- Why the action was taken

  how_trigger TEXT NOT NULL,
    -- How the action was triggered (instruction source, command, API call, etc.)
    -- Mechanism that caused the event

  -- State Capture (Before/After for replay)
  before_state TEXT,
    -- State before action (JSON or serialized format)
    -- Optional, for replay/audit

  after_state TEXT,
    -- State after action (JSON or serialized format)
    -- Optional, for replay/audit

  -- Provenance & Integrity
  _source TEXT NOT NULL,
    -- 'live' (from GATE) | 'imported' | 'recovered' | 'test'
    -- Origin of event

  channel_type TEXT NOT NULL,
    -- 'gate' (from PHI-OS GATE) | 'buffer' | 'direct' | 'other'
    -- Ingestion channel

  -- Chain Linkage (Hash Chain for integrity)
  trace_id TEXT,
    -- Current event hash (sha256) for chain validation
    -- Links to previous event

  related_event_id TEXT,
    -- Previous event hash (related_event_id in hash chain)
    -- Links event sequence together

  -- Event Lifecycle
  lifecycle_phase TEXT NOT NULL,
    -- 'in_operation' (default) | 'archived' | 'superseded' | 'retracted' | other
    -- Where in its lifecycle the event is

  -- Risk & Severity
  risk_level TEXT NOT NULL,
    -- 'normal' (default) | 'warning' | 'critical' | 'incident' | etc.
    -- Risk classification

  severity TEXT,
    -- Optional additional severity classification
    -- For compatibility with analytics

  -- Relationships & Metadata
  free_note TEXT,
    -- Joined metadata (tags|who_role=...|event_source=...|orig_channel=...)
    -- Compatibility field for metadata

  session_id TEXT,
    -- Alias for who_session (for compatibility)
    -- Session correlation

  -- Analysis & Classification
  category_ab TEXT,
    -- Governance categorization (A/B classification, if needed)
    -- For event categorization

  target_class TEXT,
    -- Target of change (file/config/code/schema/permission/other)
    -- What was affected

  change_type TEXT,
    -- Type of change (create/modify/delete/permission/config/other)
    -- How it was changed

  impact_scope TEXT,
    -- Scope of impact (local/session/component/system/global)
    -- How far did impact reach

  impact_result TEXT,
    -- Result of impact (success/partial/failed/unknown)
    -- What was the outcome

  -- Metadata
  _imported_at TEXT,
    -- Timestamp of import (if event was imported)
    -- For tracking external events

  ai_actor TEXT,
    -- AI model identifier (if actor is AI)
    -- Redundant with who_actor but explicit for filtering

  verified_by TEXT,
    -- Actor who verified event (optional, for audited events)
    -- Who validated it

  pattern_score REAL,
    -- Anomaly/pattern score (0-1) for detection algorithms
    -- Optional, for analysis

  recurrence_flag INTEGER,
    -- Count of similar events (for pattern detection)
    -- Optional, for analysis

  PRIMARY KEY (event_id)
);
```

**Total Columns:** 31
- Required (NOT NULL): 14 fields
- Optional (NULL allowed): 17 fields

**Scope:** Schema creation only (no data migration needed — DB is empty)  
**Authorization:** CANONICAL_SCHEMA phase (yes)  
**Testing:** Verify CREATE TABLE succeeds without errors

---

### CHANGE 3: Event Gate Integration Verification

**File:** phi_os/event_gate.py  
**Status:** NO CODE CHANGES (verification only)

**Verification Required:**
- Line 86: `INSERT INTO events (...) VALUES (...)` must succeed
- Lines 92-95: UPDATE trace_id/related_event_id must succeed
- Test: Write event via gate, verify row appears in events table

**Current Contract Validation:**
- Lines 51-75: Payload → row dict mapping (18 columns)
- Line 77: Empty string → NULL conversion
- Line 86: INSERT OR IGNORE (must NOT ignore — table must exist)
- Lines 92-95: Hash chain update

**No changes required.** Schema v1 is a superset of event_gate's 18 INSERT columns.

---

### CHANGE 4: MCP Server Integration Verification

**File:** mocka_mcp_server.py  
**Status:** NO CODE CHANGES (verification only)

**Verification Required:**

1. **Write Verification (mocka_write_event):**
   - Endpoint: /mcp/mocka_write_event
   - Process: Send event → GATE_URL → event_gate._write() → DB INSERT
   - Verify: Event persists in mocka_events.db (WRITE → READ integrity)

2. **List Verification (mocka_list_events):**
   - Endpoint: /mcp/mocka_list_events
   - Process: _db_read_events() → SELECT * FROM events
   - Verify: Returns list of written events (must not return [])

3. **Direct Read Verification (mocka_read_event):**
   - Endpoint: /mcp/mocka_read_event
   - Process: read_events(9999) → in-memory filter
   - Verify: Returns written event (must not return {"error": "not found"})

**Current Behavior:**
- Lines 119-141 (_db_read_events): Queries events table (currently fails silently)
- Lines 648-651 (mocka_list_events): Returns last 20 events (currently returns [])
- Lines 653-657 (mocka_read_event): Returns single event by ID (currently returns not found)

**Required Test:**
- Write event A
- List events → must contain event A
- Read event A → must return event A's data

**No code changes required for MCP.**

---

### CHANGE 5: Event ID Consistency Verification

**Location:** phi_os/event_gate.py lines 34-43

**Event ID Generation:**
```python
def _next_event_id() -> str:
    d = date.today().strftime('%Y%m%d')
    micros_of_day = time.time_ns() // 1000 % 1_000_000_000
    return f'E{d}_{micros_of_day:09d}{secrets.token_hex(2)}'
```

**Format:** `E{YYYYMMDD}_{micros_9d}{hex_4d}`  
**Example:** `E20260919_827083891ee8c`

**Verification Required:**
- Generate event_id via _next_event_id()
- Write event with event_id to DB
- Read back and verify event_id matches exactly
- Verify no truncation, corruption, or transformation

**No code changes required.**

---

## IMPLEMENTATION CHECKLIST

### Phase: Canonical Event Schema v1 Implementation

**PRE-IMPLEMENTATION:**
- [x] Snapshot created (STEP 1 this file)
- [x] Diff identified (this file, STEP 1)
- [ ] Scope reviewed and approved (STEP 1 CONFIRMATION NEEDED)
- [ ] Rollback strategy documented

**IMPLEMENTATION (STEP 2 - CONDITIONAL):**
- [ ] Database path resolved (Option A or B)
- [ ] Event table created with 31 columns
- [ ] event_gate verified (test INSERT/UPDATE)
- [ ] MCP read/write verified (test write → read)
- [ ] Event ID preservation verified
- [ ] Provenance fields verified

**INTEGRITY VERIFICATION (STEP 4):**
- [ ] Schema contract validation
- [ ] Required fields validation
- [ ] UNKNOWN/NULL preservation
- [ ] Write → Read integrity
- [ ] Write → List consistency
- [ ] Write → Direct Read match
- [ ] Failure/fail-closed behavior

**EVIDENCE & SUBMISSION (STEP 5-6):**
- [ ] Test results documented
- [ ] DB state inspected
- [ ] Implementation diff recorded
- [ ] Human Gate submission prepared

---

## ROLLBACK STRATEGY

**If implementation fails or needs revert:**

1. **For database changes (STEP 2):**
   - Delete mocka_events.db (or data/mocka_events.db)
   - Git checkout any code changes
   - System returns to empty DB state (pre-implementation)

2. **For code changes:**
   - git checkout <file>
   - No other changes should require rollback

3. **For DB path changes:**
   - Move file back to original location
   - Revert code path changes
   - System returns to original state

**No data loss risk:** DB is empty (no production data)

---

## SCOPE CONFIRMATION

### What IS Included (AUTHORIZED):
- Database initialization (mocka_events.db)
- Event table creation (31 columns per Canonical Schema v1)
- Write operation verification (event_gate integration test)
- Read operation verification (MCP read/list/direct-read test)
- Event ID consistency verification
- Provenance field preservation
- DB path resolution (if needed)

### What is NOT Included (NOT AUTHORIZED):
- Phase 8 Authorization changes
- Phase 8 Verification restart
- RTB binding changes
- Production Lock changes
- Production Activation
- Authority Model changes
- Decision Ledger changes
- Evidence Ledger creation
- Application code changes (outside Event persistence)
- Migration of existing data (DB is empty)
- Schema modifications (beyond 31-column canonical design)

---

## DECISION GATE FOR STEP 1→STEP 2 TRANSITION

**Before proceeding to STEP 2 (implementation), confirm:**

1. **Database Path Resolution:**
   - [ ] Option A selected (create data/ subdir): Proceed
   - [ ] Option B selected (update code paths): Proceed
   - [ ] Decision deferred: STOP and await decision

2. **Scope Verification:**
   - [ ] All changes above confirmed as IN-SCOPE: Proceed
   - [ ] Any out-of-scope changes identified: STOP and report
   - [ ] Rollback strategy acceptable: Proceed

3. **Authorization Confirmed:**
   - [ ] Canonical Schema v1 Implementation Authorized
   - [ ] Scope limited to schema + persistence
   - [ ] Phase 8 / RTB / Production locks maintained
   - [ ] All conditions met: Proceed to STEP 2

---

**Status: STEP 1 COMPLETE — AWAITING SCOPE CONFIRMATION BEFORE STEP 2**
