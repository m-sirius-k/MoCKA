# HG-M3-CANONICAL-EVENTS-SCHEMA-VERIFICATION-20260919

**Date:** 2026-09-19  
**Directive:** HG-M3-CANONICAL-EVENTS-SCHEMA-VERIFICATION-001  
**Status:** READ-ONLY INVESTIGATION COMPLETE  
**Authority Boundary:** REACHED (Q1-C follow-up)

---

## CANDIDATE SCHEMA INVENTORY

### Candidate 1: core_kernel/orchestra/persistence/schema.py

**File:** `/home/user/MoCKA/core_kernel/orchestra/persistence/schema.py`  
**Lines:** 7-14  
**Classification:** LEGACY_SCHEMA (unused in production)

**Schema Definition:**
```sql
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT,
    event_type TEXT,
    timestamp REAL,
    payload TEXT
);
```

**Properties:**
- Total columns: 5
- Type: Minimal event storage with payload serialization
- Usage: NOT FOUND in any production initialization code
- References: 0 production imports found
- Date: No version marker
- Purpose: Core kernel persistence layer (appears orphaned)
- Creates events table: YES (but not used)

**Status:** LEGACY_SCHEMA (defined but not referenced by runtime)

---

### Candidate 2: phi_os/tests/test_event_gate.py

**File:** `/home/user/MoCKA/phi_os/tests/test_event_gate.py`  
**Lines:** 25-59  
**Classification:** TEST_SCHEMA (canonical reference for testing)

**Schema Definition:**
```sql
CREATE TABLE IF NOT EXISTS events (
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
);
```

**Properties:**
- Total columns: 31
- Type: Full governance schema with operational fields
- Usage: Test fixtures only (monkeypatch.setattr to redirect DB_PATH)
- References: Used in phi_os event_gate tests
- Date: No version marker
- Purpose: Validate event_gate persistence in test environment
- Creates events table: YES (in test setup)
- Runtime applicability: Test environment only

**Status:** TEST_SCHEMA (represents expected schema but test-only)

---

### Candidate 3: scripts/migrate_source_check.py

**File:** `/home/user/MoCKA/scripts/migrate_source_check.py`  
**Lines:** 161  
**Classification:** MIGRATION_SCHEMA (assumes existing table)

**Code:**
```python
conn.execute(f"CREATE TABLE events_new ({cols_sql})")
conn.execute(f"INSERT INTO events_new ({col_list}) SELECT {col_list} FROM events")
conn.execute("DROP TABLE events")
conn.execute("ALTER TABLE events_new RENAME TO events")
```

**Properties:**
- Actual schema: NOT DEFINED IN THIS FILE (dynamically read from existing events table)
- Type: Schema migration script
- Usage: Reads from existing events table, creates new schema
- References: Assumes events table already exists before migration
- Date: No version marker
- Purpose: Migrate schema when events table already exists
- Creates events table: NO (assumes it exists)
- Runtime applicability: Requires pre-existing events table

**Status:** MIGRATION_SCHEMA (not canonical, depends on existing data)

---

### Candidate 4: gateway/gateway.py

**File:** `/home/user/MoCKA/gateway/gateway.py`  
**Lines:** 100-101  
**Classification:** RUNTIME_QUERY_SCHEMA (inferred from actual usage)

**Code:**
```python
cur.execute(
    "SELECT event_id, title, short_summary, when_ts, what_type "
    "FROM events ORDER BY when_ts DESC LIMIT 1"
)
```

**Inferred Required Columns:**
- event_id
- title
- short_summary
- when_ts
- what_type

**Properties:**
- Source: Production code query
- Usage: /api/v1/last_event endpoint
- Assumes table exists: YES
- Creates table: NO
- Columns accessed: 5 (minimum subset)
- Date: No version marker
- Purpose: Last event retrieval for context building

**Status:** RUNTIME_QUERY_SCHEMA (reveals minimum expectations)

---

## STEP 3: TRACE ACTUAL RUNTIME INITIALIZATION

### Search Results: Database Initialization Paths

**Query:** Where is mocka_events.db created/initialized?

**Findings:**

| Component | Initialization | Schema Setup | Status |
|-----------|-----------------|--------------|--------|
| mocka_mcp_server.py | Calls _get_db() | Creates claude_sessions only | NO events table |
| gateway/gateway.py | Creates DB_PATH reference | NO schema setup | NO initialization |
| phi_os/event_gate.py | Calls _get_conn() | NO schema setup | NO initialization |
| core_kernel/orchestra | Defines SCHEMA | NOT imported/used | ORPHANED |
| scripts/migrate_source_check.py | Reads existing table | Assumes table exists | MIGRATION ONLY |

**Conclusion:** No production code actually creates the events table.

### Current mocka_events.db State

```
Path: /home/user/MoCKA/mocka_events.db
Size: 0 bytes
Tables: 0 (zero)
Status: Never initialized
Last modified: Unknown (empty file)
```

**Critical Finding:** The database file exists but has never been initialized with any schema.

---

## STEP 4: TRACE event_gate INSERT CONTRACT

### Source: phi_os/event_gate.py _write() function (lines 51-75)

**INSERT Operation:**
```python
cols = list(row.keys())
placeholders = ','.join('?' * len(cols))
vals = [row[c] for c in cols]
conn.execute(
    f'INSERT OR IGNORE INTO events ({",".join(cols)}) VALUES ({placeholders})',
    vals
)
```

**Payload Mapping to Column Names (lines 51-75):**

| Input Field | DB Column | Data Type | Source |
|-----------|-----------|-----------|--------|
| payload.event_id OR generated | event_id | str | LINE 52 |
| payload.when_ts OR payload.when | when_ts | str | LINE 53 |
| payload.who_actor | who_actor | str | LINE 54 |
| payload.what_type | what_type | str | LINE 55 |
| payload.where_component | where_component | str | LINE 56 |
| payload.where_path | where_path | str | LINE 57 |
| payload.why_purpose | why_purpose | str | LINE 58 |
| payload.how_trigger | how_trigger | str | LINE 59 |
| payload.before_state | before_state | str | LINE 60 |
| payload.after_state | after_state | str | LINE 61 |
| payload.what_title OR payload.title | title | str | LINE 62 |
| payload.description OR payload.short_summary | short_summary | str | LINE 63 |
| payload.who_session OR payload.session_id | session_id | str | LINE 64 |
| payload.event_source (default:'live') | _source | str | LINE 65 |
| (joined from tags/who_role/event_source) | free_note | str | LINES 66-71 |
| 'gate' (hardcoded) | channel_type | str | LINE 72 |
| 'in_operation' (hardcoded) | lifecycle_phase | str | LINE 73 |
| 'normal' (hardcoded) | risk_level | str | LINE 74 |

**Columns Inserted by event_gate:** 18 columns

**Additional Columns (via UPDATE statement, lines 92-95):**

| Update Field | DB Column | Source |
|-----------|-----------|--------|
| sig['current_hash'] | trace_id | Line 93 |
| sig['previous_hash'] | related_event_id | Line 94 |

**Total Columns event_gate Expects:** 20 columns

---

## STEP 5: SCHEMA COMPARISON ANALYSIS

### event_gate INSERT Requirements vs. Candidate Schemas

**Candidate 1: core_kernel/orchestra (5 columns)**

| event_gate Column | core_kernel Present | Match | Conflict |
|-----------|------------|-------|----------|
| event_id | YES | TEXT PRIMARY KEY | NONE |
| when_ts | NO | - | MISSING |
| who_actor | NO | - | MISSING |
| what_type | NO | - | MISSING |
| where_component | NO | - | MISSING |
| where_path | NO | - | MISSING |
| why_purpose | NO | - | MISSING |
| how_trigger | NO | - | MISSING |
| before_state | NO | - | MISSING |
| after_state | NO | - | MISSING |
| title | NO | - | MISSING |
| short_summary | NO | - | MISSING |
| session_id | YES (named differently?) | TEXT | NULLABLE CONFLICT |
| _source | NO | - | MISSING |
| free_note | NO | - | MISSING |
| channel_type | NO | - | MISSING |
| lifecycle_phase | NO | - | MISSING |
| risk_level | NO | - | MISSING |
| trace_id | NO | - | MISSING |
| related_event_id | NO | - | MISSING |

**Status: MISMATCHED (event_gate would fail with "no such column" errors)**

---

**Candidate 2: phi_os/tests (31 columns)**

| event_gate Column | Test Schema Present | Match | Conflict |
|-----------|------------|-------|----------|
| event_id | YES | TEXT PRIMARY KEY | NONE |
| when_ts | YES | TEXT | NONE |
| who_actor | YES | TEXT | NONE |
| what_type | YES | TEXT | NONE |
| where_component | YES | TEXT | NONE |
| where_path | YES | TEXT | NONE |
| why_purpose | YES | TEXT | NONE |
| how_trigger | YES | TEXT | NONE |
| before_state | YES | TEXT | NONE |
| after_state | YES | TEXT | NONE |
| title | YES | TEXT | NONE |
| short_summary | YES | TEXT | NONE |
| session_id | YES | TEXT | NONE |
| _source | YES | TEXT | NONE |
| free_note | YES | TEXT | NONE |
| channel_type | YES | TEXT | NONE |
| lifecycle_phase | YES | TEXT | NONE |
| risk_level | YES | TEXT | NONE |
| trace_id | YES | TEXT | NONE |
| related_event_id | YES | TEXT | NONE |

**Additional columns in test schema (not inserted by event_gate):**
- category_ab TEXT
- target_class TEXT
- change_type TEXT
- impact_scope TEXT
- impact_result TEXT
- _imported_at TEXT
- ai_actor TEXT
- severity TEXT
- pattern_score REAL
- recurrence_flag INTEGER
- verified_by TEXT

**Status: ALIGNED (event_gate expectations are exact subset of test schema)**

---

## STEP 6: CANONICALITY DETERMINATION

### Question: Which schema is canonical?

**Evidence Analysis:**

1. **core_kernel/orchestra schema:**
   - Defined in code: YES
   - Used in runtime initialization: NO
   - Used in production queries: NO
   - Imported anywhere: NO
   - Referenced in comments: NO
   - Classification: ORPHANED (defined but never used)

2. **phi_os/tests schema:**
   - Defined in code: YES (test fixture)
   - Used in event_gate tests: YES
   - Matches event_gate expectations: YES (exact alignment)
   - Expected by event_gate INSERT: YES
   - Used in production: Only in tests
   - Classification: REFERENCE_SCHEMA_FOR_TESTING

3. **No other production schema found:**
   - No SQL schema files in codebase
   - No bootstrap initialization in any production component
   - No schema definition in gateway, phi_os, or mocka_mcp_server startup

### Canonicality Classification

**Result: CANONICAL_NOT_FOUND**

**Reason:**
- No production code currently creates the events table
- No authoritative schema definition is explicitly marked as canonical
- The test schema aligns with event_gate expectations perfectly
- BUT: test schemas are not authoritative for production use
- The core_kernel schema exists but is unused/orphaned

**Implicit Canonical Schema (by necessity):**
If production must work, the implied canonical schema is:
- Based on what event_gate requires (20 columns minimum)
- Extended with test schema fields (31 total columns from test)
- Used in test validation but NOT in production initialization

---

## STEP 7: DETERMINE mocka_events.db INTENDED SCHEMA

### Question: What schema is mocka_events.db intended to use?

**Evidence:**

| Source | Claims | Authority Level |
|--------|--------|-----------------|
| event_gate.py | Expects 20 columns (INSERT contract) | STRONG (code requirement) |
| test_event_gate.py | Uses 31 columns (test fixture) | MODERATE (test reference) |
| gateway.py | Queries 5 columns minimum | STRONG (runtime query) |
| core_kernel/orchestra | Defines 5 columns | WEAK (unused definition) |
| mocka_mcp_server.py | Queries all columns via SELECT * | STRONG (runtime query) |
| Production initialization | NONE FOUND | NONE (missing) |

### Conclusion

**Status: CONFLICTED / UNKNOWN**

**Findings:**

1. **Intended columns (by event_gate):** At least 20 (to avoid INSERT errors)
2. **Test reference columns:** 31 (fully compatible with event_gate)
3. **Actual initialization:** NONE (database is 0 bytes, never created)
4. **Authoritative definition:** NOT FOUND

**Critical Gap:** mocka_events.db has no documented/enforced schema definition in production code.

---

## STEP 8: CONFLICTS AND EVIDENCE GAPS

### Schema Conflicts Identified

**Conflict 1: core_kernel vs. event_gate expectations**
- core_kernel defines 5 columns
- event_gate requires ~20 columns
- Result: event_gate INSERT would fail with "no such column" errors

**Conflict 2: Test schema vs. production initialization**
- Test schema (31 columns) is used in phi_os tests
- No production code uses this schema
- mocka_events.db in production is never initialized

**Conflict 3: Multiple schema definitions exist**
- core_kernel/orchestra (5 columns) - orphaned
- phi_os tests (31 columns) - test reference only
- No unified canonical definition

### Evidence Gaps

| Question | Evidence | Status |
|----------|----------|--------|
| What is THE canonical events schema? | NOT FOUND | EVIDENCE_GAP |
| Who defines the schema? | NO AUTHORITY FOUND | EVIDENCE_GAP |
| When should it be created? | NO INITIALIZATION CODE | EVIDENCE_GAP |
| How is it currently used? | INCONSISTENTLY (tests vs. code) | EVIDENCE_GAP |
| Is initialization documented? | NO DOCUMENTATION FOUND | EVIDENCE_GAP |

---

## STEP 9: IMPACT ASSESSMENT

### Impact on MCP Persistence Infrastructure

**Current State:**
- mocka_events.db: 0 bytes, never initialized
- events table: DOES NOT EXIST
- event_gate INSERT: FAILS SILENTLY (INSERT OR IGNORE)
- mocka_list_events: RETURNS EMPTY (exception caught)
- mocka_read_event: RETURNS "not found" (upstream fails)

**Schema Impact:**
- If core_kernel schema (5 columns) were used: event_gate would fail (missing 15 columns)
- If test schema (31 columns) were used: event_gate would succeed
- If no schema exists: event_gate fails silently (current state)

**Remediation Blocker:** Without canonical schema definition and authorization, database initialization cannot proceed.

---

### Impact on Phase 8

```
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN (unchanged)
PHASE8_VERIFICATION = HALTED (unchanged)
PHASE8_SCOPE = UNKNOWN (unchanged)

MCP Infrastructure Gap:
  Status: CRITICAL (no schema, no initialization)
  Causality: INDEPENDENT of Phase 8
  
Phase 8 cannot resume verification until:
  1. MCP infrastructure resolved (if needed for monitoring)
  2. Phase 8 authorization explicitly confirmed
  3. Production Lock explicitly confirmed
  4. RTB scope explicitly defined
```

---

## FINAL CLASSIFICATIONS

```
CANONICAL_SCHEMA = CANONICAL_NOT_FOUND
  Evidence: No authoritative production schema definition exists
  Orphaned: core_kernel/orchestra schema (unused)
  Reference: test schema aligns with event_gate but test-only
  Authority: NONE ESTABLISHED

EVENT_GATE_SCHEMA_ALIGNMENT = EXTENDED
  event_gate needs: 20 columns (minimum to avoid errors)
  test schema provides: 31 columns (15 extra for governance)
  core_kernel provides: 5 columns (MISMATCHED)

RUNTIME_INITIALIZATION_PATH = NOT_FOUND
  Status: No production code creates events table
  mocka_events.db: 0 bytes, never initialized
  Result: All write/read operations fail silently or with "not found"

MOCKA_EVENTS_DB_INTENDED_SCHEMA = UNKNOWN
  Conflicted: core_kernel (5) vs test (31) vs event_gate needs (20+)
  Authority: No authoritative definition established
  Documentation: MISSING

MCP_REMEDIATION = NOT_PERFORMED
  Per investigation directive: READ-ONLY only
  No database modifications
  No schema creation
  No initialization

PHASE8_AUTHORIZATION = CURRENT_UNKNOWN
  Status: Unchanged by this investigation
  Lock: INDEFINITE

PHASE8_VERIFICATION = HALTED
  Status: Unchanged by this investigation
  Lock: INDEFINITE

AUTHORIZATION_CHANGE = NONE

SCOPE_CHANGE = NONE

RUNTIME_CHANGE = NONE

DATABASE_CHANGE = NONE

NEXT_ACTION = HUMAN_GATE_REVIEW_Q1C
  Question Q1-C: Further investigation required
  Investigation complete: YES
  Recommendation: AUTHORITY_BOUNDARY_REACHED
  
Cannot proceed to database initialization without:
1. Canonical schema authority decision
2. Explicit approval for core_kernel vs test schema
3. Human Gate resolution of conflicting schema definitions
```

---

## GOVERNING PRINCIPLE

```
止めるのは権限。
進めるのは証拠。

Canonical schema was sought, not invented.

Evidence found:
  - Multiple conflicting schema definitions exist
  - No authoritative canonical definition established
  - Production initialization path does not exist
  - Test schema aligns with event_gate but is test-only
  - core_kernel schema is orphaned/unused

Next step requires Human Gate authority to:
  - Designate which schema is canonical
  - Authorize database initialization
  - Establish schema governance
```

---

**Investigation Status:** COMPLETE  
**Authority Boundary:** REACHED (cannot proceed without authorization)  
**Remediation Status:** NOT_PERFORMED (investigation only)

**Q1-C Response:** Further investigation required to resolve:
- Which schema definition is canonical for mocka_events.db?
- Who has authority to designate canonical schema?
- Should database be initialized before Phase 8 verification?
- Should core_kernel (5) or test (31) schema be adopted?

Awaiting Human Gate decision on Q1-C clarification questions.

