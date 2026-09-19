# HG-M3-CANONICAL-EVENTS-SCHEMA-V1-STEP1-CONFIRMATION-20260919

**Date:** 2026-09-19  
**Authority:** Human Gate - Implementation Authorization  
**Status:** STEP 1 COMPLETE — AWAITING SCOPE/PATH CONFIRMATION  
**Purpose:** Confirm implementation scope before proceeding to STEP 2

---

## STEP 1 COMPLETION SUMMARY

**Snapshot Created:** ✓  
**Diff Identified:** ✓  
**Scope Clarified:** ✓  
**Path Decision Required:** ⚠️

Two documents created (both committed to branch):
1. HG-M3-CANONICAL-EVENTS-SCHEMA-V1-PRE-IMPLEMENTATION-SNAPSHOT-20260919.md
2. HG-M3-CANONICAL-EVENTS-SCHEMA-V1-IMPLEMENTATION-DIFF-20260919.md

---

## KEY FINDINGS

### Finding 1: Database Location Mismatch

**Current Code Expectation:**
- event_gate.py line 20: `/data/mocka_events.db`
- mocka_mcp_server.py line 74: `/data/mocka_events.db`

**Actual File Location:**
- `/home/user/MoCKA/mocka_events.db` (root, not data/ subdirectory)

**Impact:** Code will create DB in wrong location unless corrected

**Two Resolution Options:**

| Option | Action | Code Changes | Recommendation |
|--------|--------|--------------|-----------------|
| A | Create data/ subdir, move file | NONE (file organization only) | RECOMMENDED - follows code intent |
| B | Keep file at root, update code paths | event_gate.py line 20, mocka_mcp_server.py line 74 | Alternative - simpler for current structure |

---

### Finding 2: Database Schema Required

**Current:** mocka_events.db is 0 bytes (empty, no tables)

**Required:** Create events table with 31 columns (Canonical Event Schema v1)

**Implementation:** Single CREATE TABLE statement (provided in DIFF document)

**Columns Breakdown:**
- 14 REQUIRED (NOT NULL)
- 17 OPTIONAL (NULL allowed)
- 31 TOTAL

**No code changes to event_gate.py or mocka_mcp_server.py required — schema creation only.**

---

### Finding 3: Implementation Scope Confirmed

**AUTHORIZED for this phase:**
- Database initialization
- Event table creation (31 columns per Canonical Schema v1)
- Write operation integration testing
- Read operation integration testing (list/direct-read)
- Event ID consistency verification
- Provenance field preservation

**NOT AUTHORIZED for this phase:**
- Phase 8 Authorization changes
- Phase 8 Verification restart
- RTB binding
- Production Lock changes
- Authority Model
- Decision Ledger
- Evidence Ledger

**Scope is NARROW and FOCUSED:** Schema + Persistence only

---

### Finding 4: No Destructive Changes Required

**Existing code:** event_gate.py, mocka_mcp_server.py — NO CHANGES (verification only)

**Existing tests:** test_event_gate.py — NO CHANGES (can reuse 31-column fixture)

**Existing functionality:** Application code — NO CHANGES

**Risk level:** LOW (database file is empty, no data loss possible)

**Rollback:** Simple (delete mocka_events.db, git checkout any code changes)

---

## STEP 1→STEP 2 TRANSITION REQUIREMENTS

**Before proceeding to STEP 2 (implementation), Human Gate must confirm:**

### Requirement 1: Database Path Decision

**Question:** How should database location mismatch be resolved?

- [ ] **OPTION A (RECOMMENDED)** — Create `data/` subdirectory and move file
  - mkdir -p data/
  - mv mocka_events.db data/mocka_events.db
  - No code changes needed
  - Aligns with code expectations (event_gate.py, mocka_mcp_server.py)

- [ ] **OPTION B** — Keep file at root, update both code paths
  - Update event_gate.py line 20: `_REPO_ROOT / 'mocka_events.db'` (remove 'data/')
  - Update mocka_mcp_server.py line 74: `BASE / 'mocka_events.db'` (remove 'data/')
  - 2 file changes, but keeps current layout

- [ ] **DEFER** — Do not resolve now (implementation will fail until resolved)

---

### Requirement 2: Scope Verification

**Question:** Are the identified implementation changes within authorized scope?

**Changes identified:**
1. Database path resolution (if needed)
2. Event table creation (31 columns)
3. event_gate integration test (write/update verification)
4. MCP integration test (read/list/direct-read verification)
5. Event ID consistency verification
6. Provenance field verification

**All other components verified as OUT-OF-SCOPE (no changes required)**

**Decision:**

- [ ] **APPROVE** — All identified changes are in-scope and authorized
- [ ] **REVISE** — Some changes are out-of-scope (specify which)
- [ ] **REJECT** — Scope is too broad, reduce authorization

---

### Requirement 3: Authorization to Proceed to STEP 2

**Question:** Should implementation proceed (given path decision + scope confirmation)?

**Prerequisites (must all be true):**
1. Path decision made (Option A or B)
2. Scope verified (in-scope changes identified)
3. Rollback strategy accepted (delete DB, git checkout)
4. Phase 8/RTB/Production locks confirmed as MAINTAINED

**Decision:**

- [ ] **AUTHORIZE STEP 2** — Proceed to implementation
  - Requires: Path decision + Scope approval
  - Effect: Begin database initialization and integration testing

- [ ] **HOLD** — Require additional analysis before proceeding
  - Specify: What additional review needed?

- [ ] **CANCEL** — Do not proceed with implementation
  - Specify: Why cancel?

---

## CURRENT LOCK STATUS (Maintained)

Regardless of STEP 2 authorization, following remain UNCHANGED:

```
CANONICAL_SCHEMA = APPROVED (from Human Gate Q9)
IMPLEMENTATION_AUTHORIZATION = CONDITIONAL (pending STEP 1 confirmation)
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN
PHASE8_VERIFICATION = HALTED
RTB_20260918_001 = UNKNOWN / EVIDENCE_GAP
PRODUCTION_LOCK = UNKNOWN / EVIDENCE_GAP
PRODUCTION = NOT_AUTHORIZED
```

---

## NEXT ACTIONS IF AUTHORIZED

**If all three requirements are confirmed:**

1. Resolve database path (Option A or B)
2. Initialize mocka_events.db with CREATE TABLE (31 columns)
3. Test event_gate write operation (INSERT/UPDATE)
4. Test MCP read/list/direct-read operations
5. Verify Event ID format preservation
6. Document test results as Evidence
7. Submit STEP 5 evidence package to Human Gate

**If any requirement is NOT confirmed:**

- Stop and await clarification
- Do not proceed with implementation

---

## IMPLEMENTATION STATUS AFTER STEP 1

| Phase | Status | Blocked? |
|-------|--------|----------|
| **STEP 1** | ✓ COMPLETE | Awaiting confirmation |
| **STEP 2** | ⏸️ READY | Blocked on Path + Scope decisions |
| **STEP 3** | ⏸️ READY | Blocked on STEP 2 authorization |
| **STEP 4** | ⏸️ READY | Blocked on STEP 3 completion |
| **STEP 5** | ⏸️ READY | Blocked on STEP 4 completion |
| **STEP 6** | ⏸️ READY | Blocked on STEP 5 completion |

---

## PRINCIPLE

**原則: 止めるのは権限。進めるのは証拠。**  
(Stopping is authority. Evidence is progress.)

- STEP 1 provides evidence (snapshot, diff, scope)
- STEP 2 requires authority (Human Gate confirmation)
- No implementation without explicit authorization

---

**AWAITING HUMAN GATE RESPONSES TO:**
1. Database path resolution (Option A / Option B / DEFER)
2. Scope verification (APPROVE / REVISE / REJECT)
3. Authorization to proceed (AUTHORIZE / HOLD / CANCEL)

**Once confirmed, proceed to STEP 2 (implementation)**
