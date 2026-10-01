# MOCKA BUTTERFLY EFFECT CONTROL IMPLEMENTATION PLAN v1.0 Draft-01

## Document Identity

**Name:**
MOCKA BUTTERFLY EFFECT CONTROL IMPLEMENTATION PLAN v1.0

**Status:**
Draft-01 (Design Phase)

**Effective Date:**
2026-10-01（Design開始日）

**Authority:**
Human Gate Review Panel

**Scope:**
P0 Critical Modules Only
- Module BE-001: Event Read-Back Verification (Risk 002-A)
- Module BE-002: Decision Ledger Infrastructure (Risk 001)

**Principles:**
MoCKA Three Core Elements応用
- Structure: Implementation boundaries と state transitions
- Record: Design decisions in Decision Ledger
- Verification: Design review before implementation

---

## 1. Module BE-001: Event Read-Back Verification

### 1.1 Current State Analysis

**Observed Flow:**
```
mocka_write_event(args)
    ↓
POST GATE_URL/api/gate/event
    ↓
HTTP 201 → {"status":"ok", "event_id":"E20261001_..."}
    ↓
return {"status":"ok", "event_id":...}
    ↓
[CALLER ASSUMES WRITTEN]
```

**State Classification:**
- EXECUTED: POST request sent
- CREATED: HTTP 201 received
- ASSIGNED: event_id returned from response
- ❌ VERIFIED: NOT IMPLEMENTED
- ❌ MONITORED: NOT IMPLEMENTED

**MoCKA Principle Violation:**
```
EXECUTED ≠ VERIFIED

現状: HTTP 201受信 = 永続化確認
  ↓
実態: GATE側の書き込み成功 ≠ DB永続化確認
  ↓
Butterfly Effect Risk: 
  小さな差異（HTTP ACK vs DB確認）
    ↓
  大きな結果差（"成功"が異なる定義）
    ↓
  将来のRuntime判定エラー
```

### 1.2 Required State Transitions

**Target Flow (5-State Model):**
```
[EXECUTED] mocka_write_event() called
    ↓
[CREATED] event_gate.process_event() writes to DB
    ↓
[ASSIGNED] event_id generated and returned from GATE
    ↓
[VERIFIED] Read-back from DB confirms:
           - event_id exists in events table
           - content matches (title, description, etc.)
           - hash/signature verified
           - trace_id/related_event_id populated
    ↓
[MONITORED] Event registered in monitoring system
```

### 1.3 Design: Read-Back Verification Logic

**Requirement:**
After GATE returns HTTP 201, mocka_write_event() must verify persistence before returning success to caller.

**Architecture:**

```python
# mocka_mcp_server.py :: mocka_write_event()

Phase 1: Send
  - Prepare gate_payload
  - POST GATE_URL/api/gate/event
  - ✓ EXECUTED

Phase 2: Create
  - HTTP 201 received
  - Extract event_id
  - ✓ CREATED

Phase 3: Assign
  - event_id returned in response body
  - ✓ ASSIGNED

Phase 4: Verify [NEW]
  - Query: SELECT * FROM events WHERE event_id = ?
  - Confirm: row exists AND content matches
  - Verify: hash/signature present
  - ✓ VERIFIED
  - → If not found: Escalate to RECURRENCE_MONITOR
  - → If mismatch: Log divergence incident

Phase 5: Monitor [PLACEHOLDER for Phase 2]
  - Register in monitoring registry
  - ✓ MONITORED (deferred)
```

**Implementation Targets:**

1. **mocka_mcp_server.py**
   - Location: Lines 666-738 (mocka_write_event function)
   - Change: Add _verify_event_written() call before final return
   - New helper: `_verify_event_written(event_id: str) -> bool`
   - Fallback path: Also verify when using in-process event_gate

2. **phi_os/event_gate.py**
   - Status: Unchanged (already persists correctly)
   - Note: Verification happens in caller, not in gate

3. **New Monitoring Registry** [Phase 2]
   - Location: TBD (phi_os/event_monitor.py or runtime/)
   - Purpose: Track RECURRENCE_MONITOR counters

### 1.4 Verification Helper Function

**Function Signature:**
```python
def _verify_event_written(event_id: str, 
                         expected_content: dict = None,
                         timeout_sec: int = 5) -> dict:
    """
    Verify event persistence after GATE returns success.
    
    Args:
      event_id: Event ID to verify
      expected_content: Fields to verify (title, description, etc.)
      timeout_sec: Wait for DB commit (default 5s)
    
    Returns:
      {
        'verified': bool,
        'state': 'VERIFIED' | 'NOT_FOUND' | 'MISMATCH',
        'details': {...}
      }
    
    States:
      VERIFIED: Event exists, content matches, signature present
      NOT_FOUND: No matching event_id in database
      MISMATCH: event_id exists but content differs
    """
    # 1. Query events table
    # 2. Check: row exists
    # 3. Check: title, description match
    # 4. Check: hash/signature populated
    # 5. Return state
```

### 1.5 Error Handling & Recurrence

**Scenario 1: Event NOT_FOUND (Silent Failure)**
```
POST GATE → HTTP 201 → event_id returned
    ↓
Read-Back → No row found
    ↓
Action:
  1. Record: mocka_write_event → NOT_FOUND incident
  2. Count: Increment recurrence_count[event_id]
  3. Escalate: If count >= 2, trigger alert
  4. Return: {"status":"gate_verification_failed", "event_id":..., "reason":"NOT_FOUND"}
```

**Scenario 2: Content MISMATCH**
```
POST GATE → HTTP 201
    ↓
Read-Back → Row exists but title/description different
    ↓
Action:
  1. Record: Divergence incident
  2. Log: Expected vs Actual
  3. Return: {"status":"gate_verification_failed", "reason":"MISMATCH"}
```

**Scenario 3: Signature Missing**
```
POST GATE → HTTP 201
    ↓
Read-Back → Row exists but trace_id/related_event_id NULL
    ↓
Action:
  1. Record: Signature verification incomplete
  2. Count as UNVERIFIED
  3. Escalate if recurrent
```

### 1.6 Monitoring Integration

**Not Implemented in Phase 1 (deferred to Phase 2):**
- Recurrence counter registry
- Automatic escalation alerts
- Dashboard integration

**Design placeholder:**
```python
# Phase 2 addition
from runtime.event_monitor import register_verification_check
register_verification_check(event_id, status='VERIFIED')
```

### 1.7 Backward Compatibility

**Current Callers:**
- AI via Caliber → mocka_write_event()
- Internal systems → mocka_write_event()
- Human Gate via Workshop → events API

**Impact:**
- Return value changes from `{"status":"ok"}` to `{"status":"ok" | "gate_verification_failed"}`
- Callers must handle new failure state
- Phase 1 scope: Update mocka_write_event() only
- Phase 2 scope: Update all callers to handle verification failures

---

## 2. Module BE-002: Decision Ledger Infrastructure

### 2.1 Current State Analysis

**Observed State:**
```
Decision Schema (referenced in CLAUDE.md)
    ↓
DECISION_LEDGER_SCHEMA_v1.md (design document exists)
    ↓
Storage Path (data/decisions/decision_ledger.jsonl)
    ↓
❌ MISSING: Directory does not exist
❌ MISSING: JSONL file not created
❌ MISSING: Backend implementation
```

**MoCKA Principle Violation:**
```
Record（記録）: NOT SATISFIED

Human Gate判断が記録されない
    ↓
将来のRuntime判定で参照できない
    ↓
同じ判定の重複実行 (Risk 001)
    ↓
Authority boundary消失
```

### 2.2 Required Decision Schema

**From Policy Section 4 (Risk 001):**

```json
{
  "decision_id": "DC_YYYYMMDD_HHMMSS_XXXXX",
  "decision_object": "what is being decided (e.g., 'GL7 abort condition for BA04')",
  "authorization_scope": "who can use this decision (e.g., 'execution_governance.GL7')",
  "runtime_scope": "what components affected (e.g., ['mocka_write_event', 'gate_validator'])",
  "allowed_action": "what is permitted (e.g., 'block mocka_write_event when decision_id missing')",
  "forbidden_action": "what is not permitted (e.g., 'silently proceed without verification')",
  "evidence_requirement": "what proof is needed (e.g., 'event_id present in request')",
  "expiration": "when decision expires (e.g., '2027-10-01' or null for permanent)",
  "rationale": "why this decision (e.g., 'Butterfly Effect Risk 001: Decision tracking')",
  "alternatives": ["rejected_option_1", "rejected_option_2"],
  "human_gate_approval": {
    "approver": "name",
    "timestamp": "2026-10-01T...",
    "session_id": "SESSION_..."
  },
  "related_risk": "Risk 001",
  "related_incident": "IC-BA04-001 (UNKNOWN)",
  "status": "active" | "superseded" | "expired"
}
```

### 2.3 Storage Architecture

**File Structure:**
```
data/
  decisions/
    decision_ledger.jsonl
    decision_ledger.db (optional: indexed query support)
    .gitignore (← ensure not in version control)
```

**Format: JSONL (JSON Lines)**
- One decision per line
- Append-only log (prevents accidental deletion)
- Immutable once written
- Human readable for audits

**Example Entry:**
```
{"decision_id":"DC_20261001_000001","decision_object":"GL7 abort condition BA04_DECISION_ID_MISSING","authorization_scope":"execution_governance.GL7","runtime_scope":["mocka_write_event","gate_validator"],"allowed_action":"block mocka_write_event when decision_id missing","forbidden_action":"silently proceed without verification","evidence_requirement":"event_id present in request","expiration":null,"rationale":"Butterfly Effect Risk 001: Decision tracking","alternatives":[],"human_gate_approval":{"approver":"きむら博士","timestamp":"2026-10-01T09:00:00+00:00","session_id":"SESSION_20261001_090000"},"related_risk":"Risk 001","related_incident":"IC-BA04-001 (UNKNOWN)","status":"active"}
```

### 2.4 Implementation Targets

**1. Create Infrastructure**

**File:** `data/decisions/.gitignore`
```
# Data-only directory
*
!.gitignore
!decision_ledger.jsonl
```

**File:** `data/decisions/decision_ledger.jsonl`
- Created empty (first decisions added via Decision Ledger API)
- Immutable append-only structure

**2. Create Decision Ledger API**

**File:** `mocka_mcp_server.py`
- New tool: `mocka_decision_write()`
  - Accepts: decision_object, authorization_scope, runtime_scope, etc.
  - Generates: decision_id (DC_YYYYMMDD_HHMMSS_XXXXX)
  - Appends: One-line JSON to decision_ledger.jsonl
  - Returns: {"status":"ok", "decision_id":"DC_..."}

- New tool: `mocka_decision_get(decision_id)`
  - Queries: decision_ledger.jsonl by decision_id
  - Returns: Full decision record

- New tool: `mocka_decision_list(filters)`
  - Queries: All decisions matching filters
  - Returns: List of decision records

**3. Create Decision Ledger Reader**

**File:** `phi_os/decision_reader.py` (new)
- Function: `get_decision(decision_id)` → returns record or None
- Function: `list_decisions_by_scope(scope)` → returns active decisions
- Function: `is_decision_active(decision_id)` → bool

**4. Integrate into Execution Pipeline**

**File:** `structural/governance_pipeline.py`
- Import: decision_reader
- In `before_tool()`: Query Decision Ledger for tool scope
- Apply: Authorization_scope constraints from decision

### 2.5 Decision Lifecycle

**States:**
```
active: Currently enforced
superseded: Replaced by newer decision (reference new_decision_id)
expired: Expiration date passed
```

**Transition Rules:**
```
active → superseded [via Human Gate decision]
active → expired [automatic at expiration timestamp]

(No reverse transitions; decisions are immutable)
```

### 2.6 Initialization: IC-BA04-001 as First Decision

**Not in Phase 1 Scope:**
- IC-BA04-001 is UNKNOWN classification (unconfirmed)
- First decision should be PHASE_BEC_001 (see Section 4)

**Phase 2 Scope:**
- Once BA04 is verified, create formal decision
- Link to incident record

---

## 3. Verification Design

### 3.1 Implementation Verification Checklist

**After mocka_write_event() modification:**
```
[ ] Read-back function compiles
[ ] Read-back queries execute (test with mock event_id)
[ ] NOT_FOUND state triggers escalation
[ ] MISMATCH state detected
[ ] Signature check passes for valid events
[ ] Error handling works (DB unavailable, timeout)
[ ] Backward compatibility maintained
```

**After Decision Ledger creation:**
```
[ ] data/decisions/ directory exists
[ ] decision_ledger.jsonl created (empty)
[ ] mocka_decision_write() implemented
[ ] mocka_decision_get() implemented
[ ] mocka_decision_list() implemented
[ ] decision_reader.py functions work
[ ] governance_pipeline integration complete
```

### 3.2 Runtime Verification

**Test Scenarios:**

**Scenario 1: Normal Write Flow**
```
Step 1: mocka_write_event(title="test", description="test desc")
Step 2: Verify read-back returns VERIFIED
Step 3: Check event in events table
Expected: ✓ Event persisted
```

**Scenario 2: GATE Offline Fallback**
```
Step 1: Disable GATE service
Step 2: mocka_write_event() uses in-process fallback
Step 3: Verify read-back confirms persistence
Expected: ✓ In-process path also verified
```

**Scenario 3: Read-Back Failure**
```
Step 1: Write event successfully
Step 2: Simulate DB deletion or corruption
Step 3: Call mocka_write_event() again
Step 4: Verify NOT_FOUND triggers escalation
Expected: ✓ Failure detected and escalated
```

**Scenario 4: Decision Storage**
```
Step 1: mocka_decision_write(decision_object="test")
Step 2: Verify decision_ledger.jsonl contains entry
Step 3: mocka_decision_get() retrieves it
Expected: ✓ Decision persisted and retrievable
```

### 3.3 Acceptance Criteria

**Module BE-001 (Event Read-Back):**
- [ ] mocka_write_event() verifies persistence before success return
- [ ] NOT_FOUND state detected and handled
- [ ] No regression in existing functionality
- [ ] Test scenarios pass

**Module BE-002 (Decision Ledger):**
- [ ] data/decisions/decision_ledger.jsonl created and writable
- [ ] mocka_decision_write() generates unique decision_id
- [ ] mocka_decision_get() retrieves stored decisions
- [ ] decision_reader functions work correctly
- [ ] governance_pipeline can query decisions

---

## 4. Human Gate Authorization Requirement

### 4.1 Decision Record Needed

**Before Implementation Begins:**

```
Decision_ID: DC_20261001_001 (to be generated)

Decision Object:
  "Authorization to implement Butterfly Effect Control modules
   BE-001 (Event Read-Back Verification) and BE-002 (Decision Ledger Infrastructure)"

Authorization Scope:
  "structural/governance_pipeline.py
   mocka_mcp_server.py
   phi_os/event_gate.py
   data/decisions/ (new)
   phi_os/decision_reader.py (new)"

Runtime Scope:
  ["mocka_write_event", "mocka_decision_write", 
   "governance_pipeline.before_tool"]

Allowed Action:
  "Implement read-back verification in mocka_write_event()
   Create Decision Ledger storage in data/decisions/
   Add decision_reader functions for governance access"

Forbidden Action:
  "Modify BA04_DECISION_ID_MISSING logic
   Change Event Store schema beyond read-back fields
   Remove or modify existing governance conditions
   Apply decisions retroactively to past events"

Evidence Requirement:
  "Audit Report (Risk_001_007_Implementation_Audit.md)
   Implementation Plan (this document)
   Test scenarios documented"

Expiration:
  null (permanent, superseded only if requirements change)

Related Risk:
  "Risk 001, Risk 002"

Related Policy:
  "MOCKA_BUTTERFLY_EFFECT_CONTROL_POLICY_v1.0_Draft-01.md
   Section 7: Human Gate Re-Authorization Conditions"
```

### 4.2 Approval Checklist

**Required Before Implementation:**
- [ ] Human Gate Review Panel reviews this plan
- [ ] Decision Record approved and logged
- [ ] Risk understanding confirmed (BUTTERFLY EFFECT implications)
- [ ] Rollback procedure agreed

### 4.3 Constraints from Authorization

**Must Respect:**
- No modifications to BA04 or existing abort conditions
- Event Store schema changes limited to verification fields only
- All decisions immutable once written
- No retroactive application of decisions

---

## 5. Implementation Sequence

### Phase 1 (Current: Design)
1. Design document created (this file)
2. Critical gaps identified (BE-001, BE-002)
3. State machine flows defined
4. Verification checklist prepared

### Phase 2 (Blocked: Awaiting Authorization)
1. Human Gate approval via Decision Record
2. Code implementation
   - Module BE-001: mocka_write_event() modification
   - Module BE-002: Decision Ledger infrastructure
3. Test execution per scenarios
4. Code review & merge

### Phase 3 (Future: Monitoring)
1. Recurrence counter registration
2. Dashboard integration
3. Monitoring alerts
4. Phase 2 Implementation Design for remaining risks

---

## 6. Document Control

**Version:** 1.0 Draft-01  
**Created:** 2026-10-01  
**Status:** Awaiting Human Gate Authorization  
**Next Review:** After DC_20261001_001 approval  

**Change History:**
- v1.0 Draft-01: Initial design covering BE-001 (Event Read-Back), BE-002 (Decision Ledger)

---

## Appendix A: State Machine Diagrams

### Module BE-001: Event Write State Transitions

```
[START]
  ↓
[CONFIGURED] ← gateway_payload prepared
  ↓
[CONNECTED] ← POST GATE_URL
  ↓
[EXECUTED] ← HTTP request sent
  ↓
[CREATED] ← HTTP 201 received, event_id extracted
  ↓
[ASSIGNED] ← event_id returned to caller
  ↓
[NEW] [VERIFIED] ← Read-back confirms:
  |                 - Row exists in events
  |                 - Content matches
  |                 - Signature present
  |
  ↓
[MONITORED] ← Registered in monitoring [Phase 2]
  ↓
[END] return success

[ERROR PATHS]
  NOT_FOUND → Incident(RECURRENCE_MONITOR)
  MISMATCH → Incident(DIVERGENCE)
  TIMEOUT → Incident(GATE_UNAVAILABLE)
```

### Module BE-002: Decision Record Lifecycle

```
[REQUEST]
  ↓
[VALIDATED] ← Schema check
  ↓
[APPROVED] ← Human Gate authorization confirmed
  ↓
[ASSIGNED] ← decision_id generated
  ↓
[WRITTEN] ← Appended to decision_ledger.jsonl
  ↓
[PERSISTED] ← Readable via mocka_decision_get()
  ↓
[ACTIVE] ← Available for governance queries
  ↓
[SUPERSEDED or EXPIRED] ← Status updated
```

---

**EOF**
