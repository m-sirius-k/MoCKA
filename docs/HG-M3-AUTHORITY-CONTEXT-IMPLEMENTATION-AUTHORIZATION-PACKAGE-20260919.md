# HG-M3-AUTHORITY-CONTEXT-IMPLEMENTATION-AUTHORIZATION-PACKAGE-20260919

**Date:** 2026-09-19  
**Authority:** Implementation Authorization Package (Decision Gateway)  
**Purpose:** Comprehensive scope, impact, and validation analysis for Authority Context Integration implementation  
**Classification:** Pre-implementation analysis (no code changes, no authorization granted)

---

## 1. CURRENT STATE RECONCILIATION

### Verified Baseline (No Changes)

| Component | Status | Authority | Date | Evidence |
|-----------|--------|-----------|------|----------|
| **Authority Context Design** | COMPLETE | Human Gate Q1-Q5 (2026-09-19) | 2026-09-19 | HG-M3-AUTHORITY-CONTEXT-DESIGN-CLOSURE-HUMAN-GATE-001-20260919.md |
| **Design Decisions Recorded** | Q1-Q5: A+A+A+A+A | Human Gate | 2026-09-19 | Decision Ledger DC_20260919_001-005 (pending verification) |
| **Design Closure Commit** | `4012158` | Git | 2026-09-19 | Branch: claude/phase8-monitoring-verification-25fo8q |
| **Decision Ledger** | GIT-TRACKED | Git | 2026-09-19 | data/decisions/decision_ledger.jsonl (16 records + Q1-Q5 pending) |
| **Canonical Event Schema v1** | CLOSED/VERIFIED | Human Gate | 2026-09-19 | HG-M3-CANONICAL-EVENTS-SCHEMA-V1-CLOSURE-20260919.md |
| **Event Persistence Chain** | VERIFIED (Write→Read→List→Boundary) | Testing | 2026-09-19 | HG-M3-CANONICAL-EVENTS-SCHEMA-V1-STEP2.5-PERSISTENCE-INTEGRITY-VERIFICATION-20260919.md |
| **Phase 8** | HALTED | Human Gate | 2026-09-19 | DC_20260919_009 (Phase 8 Monitoring: HALT) |
| **RTB (Runtime Binding)** | UNKNOWN / EVIDENCE_GAP | Analysis | 2026-09-19 | HG-M3-BLOCKER-CLOSURE-AND-MINIMUM-EVIDENCE-20260919.md |
| **Production Authorization** | NOT_AUTHORIZED | Human Gate | 2026-09-19 | DC_20260919_016 (Formalize Production: NOT_AUTHORIZED) |
| **Authority Model Runtime Change** | NOT_AUTHORIZED | Human Gate | 2026-09-19 | AUTHORITY-CONTEXT-DESIGN-CLOSURE-HG-001 (Design scope only) |
| **Working Tree** | CLEAN | Git | 2026-09-19 | No uncommitted changes |

### Unchanged Elements (Per Directive)

- Authority Model semantic definitions (Identity, Scope, State, Time, Source)
- Decision Ledger existing 16 records (immutable)
- Historical event records (immutable)
- Phase 8 halt status (not restarted)
- Production NOT_AUTHORIZED status (not activated)
- RTB UNKNOWN status (not investigated outside scope)

---

## 2. IMPLEMENTATION SCOPE DECOMPOSITION

### A. Authorization Record Layer

**Purpose:** Explicit artifact linking Decision Ledger decisions to GL7 actions

**Artifact Definition:**
```
Authorization Record (new artifact type)
├─ decision_id (TEXT, NOT NULL, FK → Decision Ledger.decision_id)
├─ decision_date (TEXT ISO 8601, NOT NULL)
├─ authority_identity (TEXT, NOT NULL) — who issued (Human Gate, delegate)
├─ scope (TEXT, NOT NULL) — what actions are permitted
├─ actions (TEXT list, NOT NULL) — specific GL7 tasks authorized
├─ authority_level (TEXT, NOT NULL) — APPROVED | CLOSED | HELD | DENIED
├─ issued_ts (TEXT ISO 8601, NOT NULL) — when authorization created
├─ valid_from (TEXT ISO 8601, optional) — when authorization becomes effective
├─ expires_at (TEXT ISO 8601, optional) — when authorization expires
├─ revoked_at (TEXT ISO 8601, optional) — when authorization was revoked
├─ revocation_reason (TEXT, optional) — why revoked
├─ immutable_flag (BOOLEAN, NOT NULL) — true for audit evidence
├─ evidence_hash (TEXT, optional) — sha256 of record for chain
└─ record_source (TEXT, NOT NULL) — 'decision_ledger' | 'hg_decision' | 'imported'
```

**Storage Options (Design Choice Required):**
- Option 1: New table `authorization_records` in mocka_events.db
- Option 2: Separate file-based ledger (JSONL, similar to decision_ledger.jsonl)
- Option 3: Direct DL.decision_id reference (no separate artifact)

**GL7 Integration Points:**
- GL7 checks Authorization Record before permit/deny decision
- GL7 validates decision_id exists in authorization_records
- GL7 validates expiration (if expires_at, check current_time < expires_at)
- GL7 validates revocation (if revoked_at, check revoked_at IS NULL)
- GL7 logs authorization_record_id in event context

**GL7 Modified Components:**
- `structural/execution_governance.py`: Add `_check_authorization()` function
- `structural/execution_governance.py`: Modify approval logic to reference Authorization Record
- GL7 dry_run output: Include authorization_id and scope

**Estimated Changes:**
- New function: `_check_authorization(task_id, auth_record) → bool`
- GL7 approval method: Add authorization_record lookup (5-10 lines)
- GL7 event emission: Add authorization_id to context (3 lines)

### B. Authority-Event Binding

**Purpose:** Explicit link from Event to authorizing decision

**Event Schema Additions:**
```
Event schema (31 existing columns + 4 new)
├─ authorized_decision_id (TEXT, optional FK → decision_ledger.decision_id)
├─ authorized_by (TEXT, optional) — identity of authorizer
├─ authority_time (TEXT ISO 8601, optional) — when authorization given
└─ authority_level (TEXT, optional) — APPROVED | CLOSED | HELD | DENIED
```

**Binding Semantics:**
- event.authorized_decision_id MUST match a Decision Ledger record OR authorization_record
- If authorized_decision_id is NULL → event has no associated authorization (flag as UNKNOWN_AUTHORITY)
- If authorized_decision_id references missing record → data integrity violation
- authority_time ≠ event creation time (authority_time = when authorized, event when_ts = when executed)

**Event Gate Changes (phi_os/event_gate.py):**
- `_write()` function: Accept authorized_decision_id, authorized_by, authority_time, authority_level in payload
- `_write()` function: Add these 4 columns to INSERT statement (lines 82-88)
- `process_event()`: Pass through authority fields if present (line 133)
- `process_buffered_event()`: Handle authority fields for batch events

**MCP Tool Changes (mocka_mcp_server.py):**
- `mocka_write_event()` endpoint: Accept authorized_decision_id in payload (optional)
- If authorized_decision_id provided: validate it exists before write
- If validation fails: reject write with error (fail-closed)

**Estimated Changes:**
- Event schema: 4 new TEXT columns (schema migration)
- event_gate._write(): 4 additional field assignments (4 lines)
- event_gate.process_event(): Pass-through logic (2 lines)
- MCP tool: Authorization validation (10-15 lines)
- Database migration: ALTER TABLE events ADD 4 columns (SQL schema change)

### C. GL7 ↔ PHI-OS Coordination Protocol

**Purpose:** Explicit authority context handoff between governance and runtime layers

**Current Architecture:**
```
GL7 (Governance)
    ├─ Scope checking (GL1)
    ├─ Policy checking (GL2-GL6)
    ├─ Dry run + approval (GL7)
    └─ If approved: emit event

PHI-OS (Runtime)
    ├─ Event validation (schema, fields)
    ├─ Signature verification
    ├─ Hash chain validation
    └─ Persistence
```

**Problem:** No explicit authority context passed from GL7 → PHI-OS. PHI-OS doesn't know which decision authorized the event.

**Coordination Protocol Design:**

```
GL7 Approval Path:
1. GL7 checks authorization_record (new: _check_authorization)
2. GL7 approves with specific decision_id, decision_date
3. GL7 emits event with:
   - what_type, title, description (existing)
   + authorized_decision_id (new)
   + authorization_level (new)
   + how_trigger = "gl7_approved" (existing but clarified)

PHI-OS Gate Path (event_gate.process_event):
1. Validate schema (existing)
2. Extract authorized_decision_id from payload (new)
3. If authorized_decision_id present:
   a. Lookup Decision Ledger record
   b. Validate record exists (fail-closed if missing)
   c. Check expiration (fail-closed if expired)
   d. Check revocation (fail-closed if revoked)
4. Record decision_id in event.authorized_decision_id (new)
5. Emit signature + hash chain (existing)
6. Persist to events table (existing)

Rejection Behavior:
- GL7 rejects: event not emitted at all (GL7 gate closes)
- PHI-OS validation fails: event rejected (422 error), not persisted
- Both log rejection to integrity ledger (existing)
```

**Implementation Points:**

GL7 Changes (`structural/execution_governance.py`):
- Add `_check_authorization(decision_id)` function
- Modify `ApprovalResult` to include decision_id field
- Emit GL7 event with authorized_decision_id and authority_level
- Estimated: 20-30 lines

PHI-OS Changes (`phi_os/event_gate.py`):
- Add `_validate_authorization(authorized_decision_id)` function
- Modify `process_event()` to call validation
- Pass validation result to `_write()` function
- Update `_write()` to populate 4 new columns
- Estimated: 30-40 lines

Interface Changes:
- GL7 → PHI-OS: Via event payload (authorized_decision_id, authority_level)
- PHI-OS → Integrity Ledger: Log authorization validation attempt + result
- Estimated: 5-10 lines

**Fail-Closed Validation (Critical):**
```python
def _validate_authorization(authorized_decision_id: str) -> dict:
    """
    Fail-closed: If any check fails, reject (return False).
    """
    if not authorized_decision_id:
        return {"valid": False, "reason": "missing_authorization"}
    
    try:
        # Check 1: Record exists
        record = _get_decision_ledger_record(authorized_decision_id)
        if not record:
            return {"valid": False, "reason": "decision_not_found"}
        
        # Check 2: Not expired
        if record.get("expires_at"):
            if datetime.now(tz=UTC) > record["expires_at"]:
                return {"valid": False, "reason": "authorization_expired"}
        
        # Check 3: Not revoked
        if record.get("revoked_at"):
            return {"valid": False, "reason": "authorization_revoked"}
        
        return {"valid": True}
    except Exception as e:
        # Any error → fail-closed (assume invalid)
        return {"valid": False, "reason": f"validation_error: {str(e)}"}
```

### D. Authority Lifetime (Expiration / Revocation)

**Purpose:** Finite-scope authority binding; implement Least Privilege principle

**Schema Changes:**

Authorization Record Layer:
```
expires_at (TEXT ISO 8601, optional)
  ├─ Format: ISO 8601 timestamp (e.g., "2026-12-31T23:59:59Z")
  ├─ Semantics: Authorization valid until this moment
  ├─ If NULL: No expiration (indefinite, if no revoke)
  └─ Example: "2026-10-01T00:00:00Z" → expires Oct 1, 2026

revoked_at (TEXT ISO 8601, optional)
  ├─ Format: ISO 8601 timestamp (when revoked)
  ├─ Semantics: Authorization was revoked at this moment
  ├─ If NULL: Authorization not revoked (assuming not expired)
  └─ Example: "2026-09-20T14:30:00Z" → revoked Sept 20

revocation_reason (TEXT, optional)
  ├─ Why was authorization revoked?
  ├─ Examples: "scope_narrowed", "incident_response", "manual_revocation"
  └─ Used for audit trail
```

Decision Ledger Changes:
- Add optional expires_at field to decision_ledger.jsonl schema (version increment needed)
- Existing 16 records: NO CHANGE (immutable)
- New decisions: May include expires_at

**GL7 Validation Changes (`structural/execution_governance.py`):**
```python
def _check_authority_lifetime(auth_record: dict) -> bool:
    """Check if authorization is still valid (not expired, not revoked)."""
    current_time = datetime.now(timezone.utc)
    
    # Check 1: Not revoked
    if auth_record.get("revoked_at"):
        revoked_time = datetime.fromisoformat(auth_record["revoked_at"])
        if current_time > revoked_time:
            return False  # Authorization is revoked
    
    # Check 2: Not expired
    if auth_record.get("expires_at"):
        expires_time = datetime.fromisoformat(auth_record["expires_at"])
        if current_time > expires_time:
            return False  # Authorization has expired
    
    return True  # Valid
```

**PHI-OS Validation Changes (`phi_os/event_gate.py`):**
- Call `_check_authority_lifetime()` before INSERT
- If expired or revoked: reject event (422 error)
- Log rejection to integrity ledger with reason

**Human Gate Decision Recording:**
- When decision made: Include expires_at (optional) in decision_ledger.jsonl
- Example: `{"decision_id": "DC_20261001_123", "expires_at": "2026-12-31T00:00:00Z", ...}`

**Estimated Changes:**
- GL7: 15-20 lines (validation function)
- PHI-OS: 10-15 lines (call validation)
- Decision Ledger schema: Version bump + optional field

**Revocation Mechanism:**
Not fully defined in this package (design scope). Options:
- Manual Human Gate decision to record revocation_at
- Automatic TTL expiration (if expires_at passed)
- Incident response (automatic revocation on incident)

### E. Authority Metadata / Synchronization

**Purpose:** DL ↔ Event traceability; verification of authority chain

**Event Schema Additions (already in B):**
```
authorized_by (TEXT, optional)
  ├─ Identity of authorizing authority (e.g., "Human Gate", "David Kimura", "claude-haiku-4-5")
  ├─ Links event to authority source
  └─ Enables: "Who approved this?"

authority_time (TEXT ISO 8601, optional)
  ├─ When authorization was issued
  ├─ ≠ event when_ts (authority_time when approved, when_ts when executed)
  └─ Enables: "How long between approval and execution?"

authority_level (TEXT, optional)
  ├─ State of authority: APPROVED | CLOSED | HELD | DENIED | REVOKED
  ├─ Redundant with Decision Ledger but explicit in event
  └─ Enables: "At what level was this authorized?"
```

**DL ↔ Event Synchronization Strategy:**

```
Reconciliation Method:
event.authorized_decision_id ↔ decision_ledger.decision_id

MUST MATCH:
  decision_ledger[id=event.authorized_decision_id].decision_id 
    == event.authorized_decision_id

OPTIONAL FIELDS:
  event.authorized_by       ← should match decision_ledger[id].authority
  event.authority_time      ← should match decision_ledger[id].date (approximately)
  event.authority_level     ← should match decision_ledger[id].decision (APPROVED/CLOSED/etc)

Mismatch Handling:
  if decision_ledger.decision_id != event.authorized_decision_id:
    → Log integrity violation
    → Mark event as UNVERIFIED_AUTHORITY
    → Record in integrity ledger

Orphan Event Handling:
  if event.authorized_decision_id AND no matching DL record:
    → Log data integrity violation
    → Mark event as ORPHAN_AUTHORIZATION
    → Prevent event from being used as authorization evidence
```

**Implementation Points:**

Event Gate (`phi_os/event_gate.py`):
- Accept authorized_by, authority_time, authority_level in payload
- Pass to `_write()` function (5 lines)
- Validate against Decision Ledger if authorized_decision_id present (10 lines)

Verification Function (`phi_os/integrity.py` or new file):
```python
def verify_event_authorization(event_dict: dict, dl_record: dict = None) -> dict:
    """
    Verify that event's authorization metadata matches Decision Ledger record.
    Returns: {"valid": bool, "mismatches": [str], "reasons": [str]}
    """
    if not event_dict.get("authorized_decision_id"):
        return {"valid": True, "reason": "no_authorization_required"}
    
    decision_id = event_dict["authorized_decision_id"]
    if dl_record is None:
        dl_record = _get_decision_ledger_record(decision_id)
    
    if not dl_record:
        return {"valid": False, "reason": "decision_not_found"}
    
    mismatches = []
    
    # Optional field checks (warn if mismatch, don't fail)
    if event_dict.get("authorized_by") != dl_record.get("authority"):
        mismatches.append(f"authorized_by mismatch")
    
    if event_dict.get("authority_level") != dl_record.get("decision"):
        mismatches.append(f"authority_level mismatch")
    
    return {
        "valid": True,
        "mismatches": mismatches,
        "reason": "authorized_decision_id matches" + (f"; {len(mismatches)} metadata mismatches" if mismatches else "")
    }
```

Reconciliation Audit (`phi_os/reconciliation.py` - new file):
```python
def audit_event_authorization_chain(event_id: str) -> dict:
    """
    Full audit: Event → DL Record → GL7 Approval → Authority Source
    """
    event = read_event(event_id)
    if not event.get("authorized_decision_id"):
        return {"status": "unauthorized"}
    
    decision_id = event["authorized_decision_id"]
    dl_record = _get_decision_ledger_record(decision_id)
    
    return {
        "event_id": event_id,
        "decision_id": decision_id,
        "found": dl_record is not None,
        "verified": event["authorized_decision_id"] == dl_record["decision_id"],
        "metadata_mismatches": verify_event_authorization(event, dl_record)["mismatches"]
    }
```

**Estimated Changes:**
- Event gate: 15-20 lines
- Verification function: 30-40 lines
- Reconciliation function: 20-30 lines
- MCP tool: new endpoint `/mcp/verify_event_authorization` (10-15 lines)

---

## 3. EXACT IMPLEMENTATION IMPACT

### Files to Modify

| File | Changes | Lines | Rationale |
|------|---------|-------|-----------|
| `structural/execution_governance.py` | Add authorization checking; emit decision_id in events | 30-40 | GL7 must validate authorization before approval |
| `phi_os/event_gate.py` | Add 4 event columns; add authorization validation | 40-50 | Central event ingestion point; fail-closed validation required |
| `phi_os/integrity.py` (existing) | Add authorization verification functions | 30-40 | Reconciliation verification logic |
| `mocka_mcp_server.py` | Add authorization validation to MCP endpoints | 15-20 | MCP tool must enforce authorization rules |
| `data/decisions/decision_ledger.jsonl` | Schema version bump; optional expires_at field | Minor | Support lifetime management |

### Files to Create

| File | Purpose | Lines | Content |
|------|---------|-------|---------|
| `docs/AUTHORITY-CONTEXT-IMPLEMENTATION-SPEC.md` | Implementation specification | 100+ | Detailed API contracts, error codes, validation rules |
| `phi_os/reconciliation.py` | DL ↔ Event audit functions | 50-100 | Verification and mismatch detection |
| `tests/test_authority_context_integration.py` | Test suite | 200+ | 13+ acceptance criteria tests |
| `governance/authorization_records.py` (optional) | Authorization Record CRUD | 50-100 | If separate artifact chosen over DL reference |

### Interfaces Affected

| Interface | Current | Change | Impact |
|-----------|---------|--------|--------|
| `GL7.approve()` | Returns ApprovalResult(approved, reason) | Add decision_id field | GL7 callers must expect decision_id in result |
| `event_gate.process_event()` | Accepts event payload dict | Add authorized_decision_id, authorized_by, authority_time, authority_level | Callers must provide authority fields (optional but validated if present) |
| `mocka_write_event` MCP tool | Accepts event dict | Add authorization validation | MCP calls fail (422) if authorization missing/invalid |
| `mocka_read_event` MCP tool | Returns event dict | Add 4 new fields in response | Callers must handle new optional fields |
| Integrity Ledger | Records validation attempts | Add authorization validation results | Integrity records include authorization check results |

### Schemas Affected

| Schema | Change | Details |
|--------|--------|---------|
| **mocka_events.db / events table** | ALTER TABLE ADD 4 columns | Add authorized_decision_id, authorized_by, authority_time, authority_level (all optional TEXT) |
| **Authorization Records** (new) | CREATE TABLE OR use DL reference | Either new table in mocka_events.db OR reference decision_ledger.jsonl |
| **decision_ledger.jsonl** | Add optional field | expires_at (ISO 8601), revocation_reason fields |
| **integrity_ledger** (if exists) | Add authorization validation records | Record each authorization check (valid/invalid) |

### Persistence Affected

| Component | Change | Impact |
|-----------|--------|--------|
| **mocka_events.db** | +4 columns, potential new table | Schema migration required (backward compatible if columns optional) |
| **decision_ledger.jsonl** | +optional field | Version bump; existing records unchanged |
| **integrity ledger** | +authorization records | New record type; no schema change if flexible |

### GL7 Affected Components

| Component | Current | Change |
|-----------|---------|--------|
| `_check_authorization()` | N/A (new function) | NEW: Authorization Record lookup + validation |
| `ApprovalResult` | `(approved, reason, dry_run)` | ADD: decision_id field |
| `_emit_gl7_event()` | Emits GL7_EVENT with result/reason | ADD: authorized_decision_id, authority_level to context |
| Dry Run output | Shows file changes, aborts | ADD: Authorization status, scope validation |

### PHI-OS Affected Components

| Component | Current | Change |
|-----------|---------|--------|
| `process_event()` | Validates, signs, persists | ADD: Call `_validate_authorization()` |
| `_write()` | Inserts 18 columns | ADD: Insert 4 authority columns |
| Error responses | 422 for schema errors | ADD: 422 for authorization errors (missing, invalid, expired) |
| Integrity recording | Records validation attempts | ADD: Record authorization validation attempts |

### Tests Affected

| Test | Current Scope | New Scope |
|------|---------------|-----------|
| Write integrity tests | WRITE → READ → LIST → boundary | ADD: Authorization validation tests |
| GL7 approval tests | Test approval/rejection logic | ADD: Authorization Record lookup tests |
| MCP endpoint tests | Test event ingestion | ADD: Authorization validation in MCP tools |
| Persistence tests | Schema + write/read | ADD: DL ↔ Event synchronization tests |

### Documentation Affected

| Doc | Update Required |
|-----|-----------------|
| `docs/AUTHORITY-CONTEXT-INTEGRATION-EVALUATION-20260919.md` | Already exists (design) |
| `docs/AUTHORITY-CONTEXT-DESIGN-CLOSURE-HUMAN-GATE-001-20260919.md` | Already exists (decisions) |
| NEW: Implementation specification | NEW: Detailed API contracts, error codes |
| NEW: Authorization Record schema | NEW: If separate artifact chosen |
| Event schema documentation | UPDATE: Add 4 new fields |
| GL7 governance documentation | UPDATE: Add authorization checking step |

---

## 4. IMPLEMENTATION BOUNDARY

### AUTHORIZED TO IMPLEMENT (Only If Future HG Approves)

```
IF FUTURE HUMAN GATE DECISION APPROVES IMPLEMENTATION:

✓ Authorization Record Layer Design
  - Create artifact (table or file)
  - Define schema (decision_id, scope, expiration, revocation, etc)
  - Implement CRUD operations

✓ Event Schema Modifications
  - ALTER TABLE events ADD 4 columns
  - Backward compatible (all columns optional)
  - Migrate existing data (set new columns to NULL)

✓ GL7 Authorization Checking
  - Add _check_authorization() function
  - Modify approval logic to reference Authorization Record
  - Add decision_id to event context

✓ PHI-OS Authorization Validation
  - Add _validate_authorization() function
  - Implement fail-closed validation (reject if any check fails)
  - Update error responses for authorization failures

✓ GL7 ↔ PHI-OS Coordination Protocol
  - Define explicit authority context handoff
  - Implement authorization_id passing
  - Add coordination logging

✓ Authority Lifetime Mechanisms
  - Add expiration field to Authorization Record
  - Add revocation field to Authorization Record
  - Implement GL7 checks for expiration/revocation

✓ DL ↔ Event Synchronization
  - Implement verification functions
  - Create reconciliation audit
  - Add MCP endpoint for verification

✓ Test Implementation
  - Write unit tests (13+ acceptance criteria)
  - Test fail-closed behavior
  - Test all validation paths

✓ Evidence Collection
  - Log authorization validation attempts
  - Record in integrity ledger
  - Enable audit trail
```

### NOT AUTHORIZED (Remain Prohibited)

```
✗ Production Activation
  - Authorization Context integration is SANDBOX ONLY
  - Production deployment requires separate authorization

✗ Production Authorization
  - Production authorization status remains NOT_AUTHORIZED
  - Separate Human Gate decision required

✗ Production Binding
  - No runtime binding in production
  - Sandbox testing only

✗ Phase 8 Restart
  - Phase 8 remains HALTED
  - Separate authorization required if restart considered

✗ Authority Model Semantic Changes
  - Authority Identity, Scope, State unchanged
  - No modification to foundational concepts

✗ Decision Ledger Historical Modification
  - Existing 16 records immutable
  - Cannot retroactively add/remove/change decisions

✗ Authority Model Runtime Behavior Change
  - Design approved; implementation of behavior separate
  - No runtime behavior changes without explicit authorization

✗ AI-Generated Authorization
  - AI cannot issue, approve, or retroactively authorize decisions
  - AI can only implement human-authorized designs

✗ Automatic Human Gate Approval
  - Human Gate decisions must remain explicit
  - No automatic approval inference
```

---

## 5. ACCEPTANCE CRITERIA

Implementation PASSES only if all 13+ criteria are verified:

| # | Criterion | Test Method | Expected Outcome | Pass/Fail |
|----|-----------|------------|------------------|-----------|
| 1 | **Authorization Record exists and is traceable** | Create auth record, query by decision_id | Record persists, retrievable, contains all fields | ✓ REQUIRED |
| 2 | **Authorization source is identifiable** | Auth record contains authorized_by field | authorized_by correctly identifies Human Gate/delegate | ✓ REQUIRED |
| 3 | **Event ≠ Authorization** | Write event without authorization | Event is written but marked UNKNOWN_AUTHORITY or rejected | ✓ REQUIRED |
| 4 | **Event ↔ Authorization binding is explicit and verifiable** | Write event with authorized_decision_id, verify DL lookup | Event.authorized_decision_id matches DL record; reconciliation passes | ✓ REQUIRED |
| 5 | **GL7 cannot execute without valid authority context** | Try GL7 approval without Authorization Record | GL7 approval fails (returns rejected); no event emitted | ✓ REQUIRED |
| 6 | **PHI-OS does not independently generate authority** | Write event to PHI-OS directly without GL7 auth | Event rejected or marked as UNVERIFIED_AUTHORITY | ✓ REQUIRED |
| 7 | **Expired authority is rejected** | Create auth record with past expires_at, attempt event | Event rejected; error message indicates expiration | ✓ REQUIRED |
| 8 | **Revoked authority is rejected** | Create auth record with revoked_at set, attempt event | Event rejected; error message indicates revocation | ✓ REQUIRED |
| 9 | **Missing authority is rejected** | Write event with invalid authorized_decision_id | Event rejected (422); DL lookup fails | ✓ REQUIRED |
| 10 | **Mismatched DL/Event authority is detected** | Write event with authorized_decision_id that doesn't match DL | Reconciliation audit flags mismatch; logged to integrity ledger | ✓ REQUIRED |
| 11 | **Fail-closed behavior is demonstrated** | Trigger all error paths (missing auth, expired, revoked, invalid) | Every error path results in event rejection or orphan flag; no silent skips | ✓ REQUIRED |
| 12 | **Evidence of verification is recordable** | Enable integrity logging, perform authority validations | Each validation attempt logged (valid/invalid); retrievable from integrity ledger | ✓ REQUIRED |
| 13 | **Production authorization NOT activated** | Inspect Production flag, attempt production event | Production remains NOT_AUTHORIZED; event rejected if production=true | ✓ REQUIRED |

---

## 6. TEST / VALIDATION PLAN

### Pre-Implementation Test Specifications

**Test Suite: Authority Context Integration** (test_authority_context_integration.py)

#### T1: Valid Authority

```
Input: GL7 approval with valid Decision Ledger record
  - decision_id = "DC_20261001_123" (exists in DL)
  - expires_at = "2026-12-31" (future)
  - revoked_at = NULL

Expected: Event persisted with explicit authorization binding
  - event.authorized_decision_id = "DC_20261001_123"
  - event.authorized_by = "Human Gate"
  - event.authority_time = (approval timestamp)
  - event.authority_level = "APPROVED"

Expected Decision: GL7 approves, PHI-OS accepts, event_id returned

Expected Event:
  ```json
  {
    "event_id": "E20261001_...",
    "when_ts": "2026-10-01T10:00:00Z",
    "authorized_decision_id": "DC_20261001_123",
    "authorized_by": "Human Gate",
    "authority_time": "2026-09-30T15:30:00Z",
    "authority_level": "APPROVED",
    "lifecycle_phase": "in_operation"
  }
  ```

Expected Evidence: Event logged to integrity_ledger with "authorization_verified"
```

#### T2: Missing Authority

```
Input: GL7 approval with missing Decision Ledger record
  - decision_id = "DC_INVALID_999" (does not exist)

Expected: Event rejected (fail-closed)

Expected Decision: GL7 permits, but PHI-OS rejects (422 Unauthorized)

Expected Error Response: {"status": "rejected", "error": "decision_not_found", "decision_id": "DC_INVALID_999"}

Expected Evidence: Logged to integrity_ledger as "authorization_lookup_failed"
```

#### T3: Expired Authority

```
Input: GL7 approval with expired Decision Ledger record
  - decision_id = "DC_20260915_111" (exists)
  - expires_at = "2026-09-20" (past date)

Expected: Event rejected (fail-closed)

Expected Decision: GL7 checks expiration, rejects approval

Expected Error: "authorization_expired"

Expected Evidence: Logged as "authorization_expired"
```

#### T4: Revoked Authority

```
Input: GL7 approval with revoked Decision Ledger record
  - decision_id = "DC_20260919_222" (exists)
  - revoked_at = "2026-09-20T12:00:00Z" (in past)

Expected: Event rejected (fail-closed)

Expected Decision: GL7 checks revocation, rejects approval

Expected Error: "authorization_revoked"

Expected Evidence: Logged with revocation_reason
```

#### T5: Mismatched Authorization

```
Input: Event written with authorized_decision_id that mismatches DL record
  - event.authorized_decision_id = "DC_20260919_001"
  - but DL record has different authority_level or expired status

Expected: Reconciliation audit detects mismatch

Expected Decision: Event marked UNVERIFIED_AUTHORITY

Expected Event: Has authorized_decision_id but flags indicate mismatch

Expected Evidence: Logged to integrity_ledger with mismatch details
```

#### T6: Unauthorized Event (No Authorization)

```
Input: Write event without authorized_decision_id
  - payload contains no authorized_decision_id field

Expected: Event written OR rejected (design choice)
  - Option A: Event written with authorized_decision_id = NULL, flagged as UNKNOWN_AUTHORITY
  - Option B: Event rejected (fail-closed interpretation)

Expected Evidence: Logged as "event_without_authorization"
```

#### T7: GL7 Reject (No Emission)

```
Input: GL7 rejects an action (authorization check fails)

Expected: No event emitted to PHI-OS at all

Expected Decision: GL7 approval = False, reason = "authorization_denied"

Expected Event: None (no record created)

Expected Evidence: Logged to GL7_EVENT but not to event table
```

#### T8: Authorization Boundary

```
Input: GL7 approves, but scope doesn't match task

Expected: Scope validation before approval

Expected Decision: GL7 approves only if task within scope

Expected Evidence: Scope validation logged
```

#### T9: Persistence After Validation

```
Input: Valid authority + valid event

Expected: Event persists across connection boundary

Expected Decision: Write → close connection → read returns same event

Expected Event: All 4 authorization fields match

Expected Evidence: Read-back verification passed
```

#### T10: Integrity Ledger Recording

```
Input: 9 test cases (T1-T9)

Expected: Each validation attempt logged to integrity_ledger

Expected Evidence:
  ```json
  {
    "event_id": "E20261001_123",
    "validation_type": "authorization",
    "decision_id": "DC_20261001_001",
    "result": "valid" | "invalid",
    "reason": "authorization_verified" | "authorization_expired" | ...
    "timestamp": "2026-10-01T10:00:00Z"
  }
  ```
```

#### T11: Fail-Closed Verification

```
Input: All error paths (T2, T3, T4, T5, T6, T7)

Expected: Every error path results in event rejection or isolation
  - No silent passes
  - No orphaned events

Expected Evidence: All errors logged with reason codes
```

#### T12: Authority Metadata Sync

```
Input: Event with all 4 authority fields filled

Expected: DL ↔ Event reconciliation passes

Expected Decision: Audit reconciliation shows authorized_by, authority_time, authority_level match DL record

Expected Evidence: Reconciliation audit succeeds
```

#### T13: Production Boundary

```
Input: Attempt to write event with production_flag = true

Expected: Event rejected (Production NOT_AUTHORIZED)

Expected Decision: PHI-OS rejects with "production_not_authorized"

Expected Evidence: Logged as "production_rejection"
```

---

## 7. ROLLBACK / FAILURE CONTAINMENT

### If Implementation Fails

#### Database Schema Rollback

```
Failure: ALTER TABLE events ADD columns fails

Mitigation:
1. Catch exception in migration script
2. Log error with full stack trace
3. Do NOT attempt to continue
4. Restore DB to pre-migration state:
   - DROP newly added columns (if partial)
   - Restore from backup (if available)
   - Or delete mocka_events.db entirely (empty DB, no data loss)

Evidence: Log file records attempted migration + rollback action
```

#### Code Changes Rollback

```
Failure: GL7 or PHI-OS changes introduce bug

Mitigation:
1. git checkout <file> (restore pre-implementation version)
2. Revert any database schema changes (as above)
3. Run tests to verify pre-implementation state restored

Evidence: Git log shows commit revert + reason
```

#### Partial Implementation Detection

```
Failure: Schema partially migrated but code not deployed

Mitigation:
1. Migration script detects schema/code mismatch
2. Fails at startup with clear error
3. Prevents running with mismatched schema/code
4. Rolls back to known-good state

Example Check:
```python
def validate_schema_code_match():
    db_version = get_db_schema_version()
    code_version = EXPECTED_SCHEMA_VERSION
    if db_version != code_version:
        raise RuntimeError(f"Schema/Code mismatch: DB={db_version}, Code={code_version}")
```

Production Impact:
- Fail-closed (refuses to start if mismatch detected)
- Manual intervention required to resolve
```

#### Previous Behavior Preservation

```
Failure: Implementation breaks existing event write/read

Mitigation:
1. All 4 new columns are OPTIONAL (NULL allowed)
2. Existing code that doesn't provide authorization fields still works
3. New fields default to NULL if not provided
4. Backward compatibility maintained

Test: Verify pre-implementation test suite still passes
```

#### Authorization Record Failure (If Separate Table)

```
Failure: Authorization Record table creation fails

Mitigation:
1. If separate table chosen, creation fails at initialization
2. Retry mechanism (up to 3 attempts) before failing
3. If persistent failure, system refuses to start

Recovery:
1. Check DB file integrity
2. Restore from backup
3. Or delete mocka_events.db and reinitialize (data loss only to empty DB)
```

### Sandbox Isolation

```
Authority Context implementation is SANDBOX ONLY.

Isolation Mechanisms:
- No production event writing during implementation
- Authorization Records created in sandbox DB only
- Decision Ledger references tested against sandbox copy
- No Production flag set to true during testing
- All events marked with _source = 'test' or _source = 'sandbox'

Verification:
- Startup check: Inspect _source field of all test events
- Confirmation: All should be 'test' or 'sandbox', not 'production'
- If any production=true event found: Immediate stop + error
```

---

## 8. PHASE 8 RELATIONSHIP

### Critical Separations

```
Authority Context Integration ≠ Phase 8 Monitoring
```

| Aspect | Authority Context | Phase 8 | Relationship |
|--------|-------------------|---------|----------------|
| **Purpose** | Explicit authority binding to events | Monitor Phase 8 effectiveness | Independent |
| **Scope** | Event schema + GL7 + PHI-OS | Monitoring observer + metrics | No overlap |
| **Status** | DESIGN COMPLETE → Awaiting Implementation Auth | HALTED | Both suspended awaiting separate auth |
| **Authorization** | Future HG (this package) | Separate HG (Phase 8 resume conditions) | Independent decisions |
| **Dependencies** | None on Phase 8 | None on Authority Context | No cross-dependencies |
| **Implementation** | Can proceed independently | Cannot proceed (HALTED) | Can be done separately |

### Explicit Non-Implications

**Authority Context Implementation DOES NOT:**
- ✗ Resume Phase 8
- ✗ Activate Production
- ✗ Change Phase 8 authorization status
- ✗ Satisfy Phase 8 resume conditions
- ✗ Enable monitoring deployment
- ✗ Authorize RTB binding
- ✗ Imply Production readiness

**Phase 8 Remains:**
- ✓ HALTED (unchanged)
- ✓ No monitoring deployment authorized
- ✓ No effectiveness verification authorized
- ✓ Authorization baseline CURRENT_UNKNOWN (unchanged)
- ✓ 5 resume conditions still apply (unchanged)

### Independent Evaluations

```
Timeline Scenario A: Authority Context Implementation First
1. HG approves Authority Context Implementation (separate decision)
2. Authority Context is implemented and tested (sandbox only)
3. Production remains NOT_AUTHORIZED
4. Phase 8 remains HALTED
5. Later (if at all): Separate HG decision on Phase 8 resume

Timeline Scenario B: Phase 8 Resume First (Hypothetical)
1. Hypothetical future HG approves Phase 8 resume
2. Phase 8 monitoring initialized
3. Authority Context integration is separate work
4. Later (if at all): Separate HG decision on Authority Context Implementation

Timeline Scenario C: No Authority Context Implementation
1. Phase 8 can still be resumed (separate authorization)
2. Phase 8 monitoring can proceed without Authority Context
3. Authority Context and Phase 8 are orthogonal concerns
```

---

## 9. HUMAN GATE DECISION TICKET

### Package Summary for Human Gate Review

**Package:** HG-M3-AUTHORITY-CONTEXT-IMPLEMENTATION-AUTHORIZATION-PACKAGE-20260919

**Current State:**
- Authority Context Integration Design: COMPLETE (Q1-Q5 decisions recorded)
- Design Closure: APPROVED (2026-09-19)
- Implementation Authorization: NOT YET REQUESTED (this package)

**Scope Overview:**
- 5 design decisions implemented (Auth Record, Auth-Event Binding, GL7↔PHI-OS, Lifetime, Metadata)
- 30-50 lines GL7 changes
- 40-50 lines PHI-OS changes
- 1-2 new files (tests, reconciliation)
- 4 new event schema columns
- Sandbox only (no Production activation)

**Risk Summary:**
- Backward compatible (all new columns optional)
- Fail-closed design (errors reject, don't skip silently)
- Sandbox isolated (no production impact)
- Can be rolled back (schema migration reversible)

---

### Q1 — Implementation Scope Approval

**Question:** Approve the defined implementation scope (5 components, 30-100 lines total)?

```
[ ] A. APPROVE — Scope is clear, achievable, and bounded
      Rationale: _____________________________

[ ] B. HOLD — Scope needs clarification or revision
      Specific concerns: _____________________________

[ ] C. REJECT — Scope is out of bounds or too large
      Reasons: _____________________________
```

**Information for Decision:**
- Scope includes: Auth Record layer, Auth-Event binding, GL7↔PHI-OS protocol, Lifetime mechanisms, DL↔Event sync
- Scope excludes: Production activation, Phase 8 restart, Authority Model changes, Decision Ledger modification
- Estimated effort: 150-250 lines of new/modified code
- Backward compatibility: Yes (new columns optional)
- Breaking changes: None (existing interfaces unchanged)

---

### Q2 — Implementation Environment

**Question:** Should Authority Context Implementation be Sandbox-Only?

```
[ ] A. YES — Sandbox-Only, no Production authorization
      Rationale: _____________________________

[ ] B. HOLD — Environmental constraints need review
      Specify: _____________________________

[ ] C. OTHER — Specify alternative environment
      Details: _____________________________
```

**Information for Decision:**
- Current state: Production remains NOT_AUTHORIZED
- Sandbox isolation: All events marked _source='test' or 'sandbox'
- Testing: Comprehensive test suite in test_authority_context_integration.py
- Future Production transition: Requires separate authorization (not implied by this package)

---

### Q3 — Implementation Changes (File/Schema/Interface)

**Question:** Approve the defined file changes and schema modifications?

```
[ ] A. APPROVE — File list, schema changes, and interface modifications are acceptable
      Rationale: _____________________________

[ ] B. HOLD — Specific changes need review or modification
      Concerns: _____________________________

[ ] C. REJECT — Changes are too invasive or risky
      Reasons: _____________________________
```

**Information for Decision:**

Files to Modify:
- structural/execution_governance.py (GL7, 30-40 lines)
- phi_os/event_gate.py (PHI-OS, 40-50 lines)
- phi_os/integrity.py (verification, 30-40 lines)
- mocka_mcp_server.py (MCP tools, 15-20 lines)

Files to Create:
- docs/AUTHORITY-CONTEXT-IMPLEMENTATION-SPEC.md (100+ lines)
- phi_os/reconciliation.py (50-100 lines)
- tests/test_authority_context_integration.py (200+ lines)

Schema Changes:
- mocka_events.db: ALTER TABLE events ADD 4 TEXT columns (authorized_decision_id, authorized_by, authority_time, authority_level)
- decision_ledger.jsonl: Optional field addition (expires_at, revocation_reason)
- All changes backward compatible (new columns optional)

---

### Q4 — Validation Plan Approval

**Question:** Approve the 13+ acceptance criteria and test plan?

```
[ ] A. APPROVE — Test plan covers all required criteria
      Rationale: _____________________________

[ ] B. HOLD — Test plan needs additional test cases
      Missing scenarios: _____________________________

[ ] C. REJECT — Test plan is insufficient
      Reasons: _____________________________
```

**Information for Decision:**

13 Acceptance Criteria:
1. Authorization Record exists and traceable
2. Authority source identifiable
3. Event ≠ Authorization
4. Event ↔ Authorization binding explicit and verifiable
5. GL7 cannot execute without valid authority
6. PHI-OS doesn't generate authority independently
7. Expired authority rejected
8. Revoked authority rejected
9. Missing authority rejected
10. Mismatched DL/Event authority detected
11. Fail-closed behavior demonstrated
12. Evidence recordable
13. Production boundary maintained

Test Cases: 13+ (T1-T13 + variants)
Evidence: All tests logged to integrity_ledger with reason codes

---

### Q5 — Evidence Collection and Read-Back

**Question:** Approve evidence collection requirements?

```
[ ] A. APPROVE — Evidence requirements are clear and verifiable
      Rationale: _____________________________

[ ] B. HOLD — Evidence requirements need clarification
      Questions: _____________________________

[ ] C. REJECT — Evidence requirements are impossible to meet
      Reasons: _____________________________
```

**Information for Decision:**

Evidence Required:
- Authorization validation attempts logged (valid/invalid) with reason codes
- Each test result recorded to integrity_ledger
- Read-back verification: All events retrieved match written data
- Audit trail: DL ↔ Event reconciliation audit passable
- Fail-closed evidence: Error paths produce rejection records

Example Evidence Entry:
```json
{
  "event_id": "E20261001_123",
  "validation_type": "authorization",
  "decision_id": "DC_20261001_001",
  "result": "valid",
  "reason": "authorization_verified",
  "timestamp": "2026-10-01T10:00:00Z"
}
```

---

### Q6 — Production Boundary (Information Only)

**Statement:** Production remains NOT_AUTHORIZED during Authority Context Implementation.

This is a **confirmation only**, not a choice:
- Production authorization: NOT_AUTHORIZED (per DC_20260919_016)
- Authority Context implementation: SANDBOX ONLY
- No production events with Authority Context binding during development
- Production activation requires separate future authorization

**No action required.** This maintains current policy.

---

### Q7 — Phase 8 Status (Information Only)

**Statement:** Phase 8 remains HALTED; Authority Context Implementation does not imply Phase 8 resume.

This is a **confirmation only**, not a choice:
- Phase 8 status: HALTED (per DC_20260919_009)
- Authority Context and Phase 8: Independent concerns
- Authority Context implementation: Does not resume Phase 8
- Phase 8 resume: Requires separate future authorization (with 5 resume conditions)
- No cross-implications between Authority Context and Phase 8

**No action required.** This maintains current policy.

---

## IMPLEMENTATION PACKAGE SUMMARY

| Section | Status | Summary |
|---------|--------|---------|
| **1. Current State** | VERIFIED | Baseline reconciled; no changes; 8 components confirmed |
| **2. Scope Decomposition** | DEFINED | 5 design components detailed (A-E) with implementation points |
| **3. Implementation Impact** | ANALYZED | 5 files to modify, 4 files to create, 5 interfaces affected, 2 schemas affected |
| **4. Boundaries** | EXPLICIT | AUTHORIZED: 9 implementation areas; NOT AUTHORIZED: 8 prohibited areas |
| **5. Acceptance Criteria** | SPECIFIED | 13+ criteria defined with test methods and expected outcomes |
| **6. Test Plan** | DETAILED | 13+ test cases (T1-T13) with Input→Expected→Evidence mapping |
| **7. Rollback / Containment** | DESIGNED | Failure modes covered; rollback strategies for each; sandbox isolation confirmed |
| **8. Phase 8 Relationship** | CLARIFIED | Independent; non-implications explicit; Timeline scenarios provided |
| **9. Human Gate Ticket** | READY | 7 decision questions (Q1-Q5 substantive, Q6-Q7 confirmation) |

---

## NEXT STEP

**This Implementation Authorization Package is COMPLETE and READY FOR HUMAN GATE REVIEW.**

The package provides Human Gate with:
1. ✓ Comprehensive scope definition (5 components)
2. ✓ Exact implementation impact (files, lines, interfaces, schemas)
3. ✓ Acceptance criteria (13+) and test plan (13+ test cases)
4. ✓ Rollback and failure containment strategies
5. ✓ Clear separation from Phase 8 and Production concerns
6. ✓ 5 substantive decision questions (Q1-Q5)
7. ✓ 2 confirmation statements (Q6-Q7)

**Human Gate is NOT being asked to approve implementation.**  
**Human Gate is being asked to REVIEW and DECIDE whether implementation should be authorized.**

If Human Gate approves Q1-Q5 in future decision:
→ Implementation authorization will be explicitly granted
→ Implementation can proceed (separate execution directive)

If Human Gate holds or rejects any Q1-Q5:
→ Implementation is NOT authorized
→ Package may be revised and resubmitted

---

**IMPLEMENTATION AUTHORIZATION PACKAGE — COMPLETE**

**Date:** 2026-09-19  
**Authority:** Analysis and Design (No Implementation Authorization This Document)  
**Status:** READY FOR HUMAN GATE REVIEW  
**Next:** Await Human Gate Q1-Q7 Decisions

