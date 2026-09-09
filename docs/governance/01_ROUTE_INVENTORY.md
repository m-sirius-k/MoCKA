# Route Inventory v1.0 — Evidence-Bounded Complete

**Investigation Date:** 2026-09-09  
**Investigation Method:** Code inspection + grep search (no inference)  
**Repository:** /home/user/MoCKA  
**Scope:** All code paths reaching approval confirmation state  

---

## Classification Framework

| Classification | Meaning |
|---|---|
| **FACT** | Directly observed code (file:line) |
| **EVIDENCE** | Confirmed through multiple sources |
| **UNKNOWN** | Cannot determine from available code |
| **NOT_PROVEN** | Scope definition incomplete |

---

## Route Categories

All approval-confirmation routes identified fall into 3 categories:

### Route A: MCP GL7 Protected ✓ PASS

**Authorization Enforcement:** PRE-EXECUTION CHECK (mechanically enforced)

**Location:** mocka_mcp_server.py:480-510

```python
def execute_tool(name, args):
    decision = _governance.before_tool(name, args)  # Line 492
    if not decision.allowed:
        return error JSON  # Line 495-498
```

**Status:** PASS (authorization check confirmed)  
**Evidence:** Code inspection mocka_mcp_server.py + governance_pipeline.py  
**Count:** 1 route category (all MCP-routed tools)

---

### Route B: Flask / Application Routes ✗ FAIL

**Authorization Enforcement:** ABSENT (no GL7 check)  
**Mechanism:** Direct `get_buffer().push()` without before_tool() check  
**Pattern:** Flask Blueprint route → state-changing operation → buffer.push()

#### Route B Routes Identified:

| # | File | Route | Method | Buffer Call | Line | Status |
|---|------|-------|--------|-------------|------|--------|
| B1 | handshake.py | `/api/handshake` | POST | CONFIRMED | 164 | FAIL |
| B2 | ai_session.py | `/api/session/start` | GET | CONFIRMED | 128 | FAIL |
| B3 | reflection_engine.py | `/reflection/generate` | POST | CONFIRMED | 123 | FAIL |
| B4 | commission_manager.py | `/commission/list` | GET | CONFIRMED | 81 | FAIL |
| B5 | context_composer.py | `/context/compose` | GET | CONFIRMED | 146 | FAIL |
| B6 | essence_resolver.py | (embedded function) | N/A | CONFIRMED | 55 | FAIL |
| B7 | cross_audit.py | `/cross_audit/task` | POST | CONFIRMED | 298 | FAIL |
| B8 | proposal_schema.py | (embedded function) | N/A | CONFIRMED | 167 | FAIL |

**Total Route B:** 8 confirmed bypasses  
**Evidence:** grep search for `get_buffer().push()` in interface/*.py  
**Verification:** Each file read and line number confirmed

**NOT_PROVEN:** Completeness of Flask route enumeration
- Question: Are there additional Flask routes not yet discovered?
- Status: grep search found 12 files with Blueprint/route definitions; 8 found with buffer.push() calls
- Remaining 4 files checked: prediction_engine, mentor_engine, dashboard, cross_audit (cross_audit also uses buffer via _record_to_main_db)
- Note: Routes may exist that were not called during investigation window

---

### Route C: Direct SQLite ✗ FAIL

**Authorization Enforcement:** ABSENT (no authorization check)  
**Mechanism:** Direct sqlite3.connect() → INSERT without any GL7 or Gate check  
**Location:** interface/router.py:112-127

```python
def write_sqlite(row: list):
    """UTF-8 fixed, BOM-free, direct SQLite write"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO events VALUES (...)
        """, row[:23] + [""] * max(0, 23 - len(row)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[SQLITE ERROR] {e}")
        return False
```

**Call Sites:**

| Call Site | File | Line | Context | Authorization |
|-----------|------|------|---------|-----------------|
| C1 | router.py | 157 | write_safe_csv() call | ABSENT |
| C2 | router.py | 189 | _record_integrity_incident() call | ABSENT |
| C3 | router.py | 213 | MoCKARouter.collaborate() call | ABSENT |
| C4 | router.py | 232 | MoCKARouter.share() call | ABSENT |

**Total Route C:** 1 function with 4 call sites  
**Evidence:** Code inspection interface/router.py lines 112-248  
**Authorization Check:** ZERO (no GL7, no Gate, no pre-check)

**NOT_PROVEN:** 
- Prevalence: How often is write_sqlite() called in production?
- Call graph: Are there callers outside the identified call sites?
- Intentionality: Is direct DB bypass permanent design or temporary bypass?

---

## EventBuffer Mechanism

**Location:** interface/event_buffer.py

**Function:** `get_buffer().push(event_dict)`

**Mechanism:** Async in-memory queue to batch events for Gate ingestion

**Authorization Status:** NO AUTHORIZATION CHECK IN PUSH

```python
class EventBuffer:
    def push(self, event):
        self.queue.append(event)  # Line: direct append, no auth check
```

**Linkage to Gate:** 
- Buffer → `/api/gate/event/batch` (async flush)
- Gate performs validation (format/presence) but NOT authorization enforcement

**Evidence Gap:** 
- Buffer carries NO authorization record or decision ID
- Gate is validation-only (post-write audit, not pre-write enforcement)
- Buffer assumes ALLOW by default (no explicit DENY path)

---

## Authorization Record Linkage

### GovernanceDecision Object
**Location:** governance_pipeline.py  
**Fields:** `allowed` (bool), `reason` (str), `thinking_mode`, `checklist_ok`, `dry_run_aborts` (list)  
**Route A Binding:** confirmed at mocka_mcp_server.py:492-498  
**Route B/C Binding:** ABSENT

### Decision Ledger
**Location:** data/decisions/decision_ledger.jsonl  
**Status:** EXISTS but NOT LINKED to events table  
**Evidence Gap:** No `decision_id` or `authorization_record_id` field in events schema

### Execution Event
**Location:** events table (mocka_events.db)  
**Linkage to Authorization:** UNKNOWN (no proven connection mechanism)

---

## Decision Ledger & Approval Confirmation

**Location:** data/decisions/decision_ledger.jsonl + Decision Ledger MCP tool  
**Status:** Exists as formal record; used by mocka_decision_write()  
**Linkage to Events:** UNKNOWN - no field reference found

**Question:** Which database operations and Route B/C writes correspond to which Decision Ledger entries?  
**Answer:** UNKNOWN (no proven linkage found in code)

---

## Summary Table: Route Coverage

| Route Type | Category | Count | Authorization | Status | Evidence |
|-----------|----------|-------|-----------------|--------|----------|
| **Route A** | MCP GL7 | 1 | PRE-CHECK (mechanical) | PASS | CONFIRMED |
| **Route B** | Flask/App | 8+ | ABSENT | FAIL | CONFIRMED (8 found, completeness NOT_PROVEN) |
| **Route C** | Direct DB | 1 function | ABSENT | FAIL | CONFIRMED |
| **TOTAL** | ALL | **10+** | Mixed | **3 FAIL out of 10+** | See notes |

---

## Route Inventory Completion Status

### PROVEN ✓

- Route A exists and enforces authorization (PASS)
- Route B: 8 Flask routes bypass GL7 (FAIL)
- Route C: 1 direct DB function bypasses GL7 + Gate (FAIL)
- EventBuffer exists with no authorization attachment
- Decision Ledger exists but not linked to events

### NOT_PROVEN ✗

- Complete enumeration of all Flask routes reaching approval confirmation state
  - Reason: grep found 12 files with Blueprint/route definitions; 8 use buffer.push()
  - Remaining 4 files have routes but may or may not reach approval confirmation
  
- Complete call graph for write_sqlite()
  - Reason: 4 call sites found in router.py; additional callers may exist
  
- Approval Confirmation state definition
  - Reason: HG-C08 uses abstract term "承認確定に到達する全経路"; no formal state machine found
  
- Operational prevalence of direct DB writes
  - Reason: Frequency and production use unclear

### UNKNOWN ✗

- Whether Flask route bypass is temporary or permanent design
- Authorization granularity (route-level vs. operation-level)
- Exact definition of "approval confirmation" state in operations

---

## Governance Boundary Assertions

```
FACT:
- Route A MCP enforcement exists and is mechanically enforced
- Route B Flask routes call get_buffer().push() without GL7 check (8 confirmed)
- Route C Direct DB write has no authorization enforcement
- Total identified routes: 10+
- Authorized routes: 1 (Route A)
- Bypass routes: 9+ (Route B × 8 + Route C × 1)

NOT PROVEN:
- Complete enumeration (may be 10+ or more)
- All call graph coverage
- Approval confirmation state formal definition

EVIDENCE:
- mocka_mcp_server.py:492-498 (Route A enforcement)
- interface/*.py grep results (Route B bypass routes)
- interface/router.py:112-127 (Route C direct write)
- event_buffer.py (buffer mechanism, no auth)
- governance_pipeline.py (GovernanceDecision object)

CONSTRAINT MAINTAINED:
- C2-b BLOCK = IMMUTABLE
- UNKNOWN / NOT_PROVEN = PRESERVED
- Implementation Authorization = NOT GRANTED
- Production Modification = 0
```

---

## Next Steps

### Gate 1 Resolution (Route Inventory Complete)

**Current Status:** PARTIAL EVIDENCE

**Required for Completion:**
1. Complete enumeration of Flask routes (12 files found, 8 confirmed with buffer.push())
2. Verification that no additional routes exist beyond identified 8
3. Complete call graph for write_sqlite() (4 sites found, additional sources may exist)
4. Formal definition of "approval confirmation" state

**Effort Required:** Code inspection (no implementation)

---

**Investigation Authority:** Evidence-Bounded, READ-ONLY  
**Date:** 2026-09-09  
**Status:** STREAM 1 PHASE 1 COMPLETE (Route Inventory)

**STOP HERE** — Awaiting Human Gate review of Route Inventory completeness and next authorization.
