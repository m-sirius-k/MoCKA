# Phase 8: Final Answer (HG Submission)
## Candidate Minimum Binding Design for Mechanical Authorization Binding

**Investigation Date:** 2026-09-08  
**Phase:** Phase 8 (Final Synthesis — HG Submission Ready v2.3)  
**Mode:** READ-ONLY FORENSIC (Investigation Complete)  
**Audit Status:** FINAL AUDIT SUBMISSION  
**Current HOLD:** MAINTAINED (NOT LIFTED)  
**Design Status:** CANDIDATE - Pending Human Gate Adoption Decision  
**Implementation Authorization:** NOT GRANTED

---

## SPECIFICATION NOTICE

This document presents a Candidate Minimum Binding Design for Mechanical Authorization Binding. It does NOT represent adopted design, nor does it authorize implementation.

**Ownership:** This specification is presented for Human Gate design review. The design framework and candidate normative requirements are subject to Human Gate adoption/rejection/modification.

**Key Clarification:** Design Adoption ≠ Implementation Authorization. If Human Gate adopts this design, it establishes the specification basis. Implementation authorization is a separate decision.

---

## AUDIT ITERATION 3 CHANGES (v2.2 → v2.3)

This v2.3 integrates Audit Iteration 3 corrections (4 normative refinements):

**4 Critical Normative Corrections:**
1. REQ-5 Rollback — enforcement-preserving requirement (code-based alone insufficient)
2. REQ-7 Risk Assessment — UNKNOWN boundary maintenance (no YES inference)
3. REQ-3/4 Audit Trail — AUTHORIZATION and EXECUTION evidence separation
4. REQ-2d Replay — HG-selected policy reference (no fixed replay_check: true)

**v2.2 Consistency Corrections (Preserved):**
1. TOCTOU Semantics — sequential re-check alone is NOT atomic safeguard
2. Decision Format Alignment — action_type, target_id, scope required for REQ-1 binding
3. Authorization Record API — get_state() vs get_authorization_record() role separation
4. UNKNOWN Scoping — limited to current execution boundary integrity impact
5. Boundary Enumeration — unified to UNKNOWN / NOT QUANTIFIABLE (removed ~48 estimate)
6. Risk Assessment — Evidence-bounded terminology (NOT MINIMIZED vs HIGH)

**Minor Clarifications:**
- Human Authority accountability language
- Replay semantics marked as CONDITION PENDING (design adoptable, implementation blocked until decided)

---

## ORIGINAL INVESTIGATION QUESTION

**Question:** "What is needed to establish minimum, safe, auditable, fail-closed Mechanical Authorization Binding starting from existing Authorization Records?"

**Investigation Constraint:** Determine minimum sufficient technical and evidentiary conditions WITHOUT assuming that Authorization Records alone establish binding.

---

## DIRECT ANSWER (CANDIDATE SPECIFICATION)

### Current State (Evidence-Bounded — Unchanged)

**What EXISTS:**
1. Authorization Records — human_gate_events table produces APPROVED/REJECTED/PENDING/EXPIRED/CANCELED states
2. State Machine — Formalized transitions with validation (submit → approve → APPROVED)
3. State Retrieval — get_state(request_id) function reads current authorization state
4. Event ID Generation — HG{YYYYMMDD}_{microseconds:09d}{random_hex:4} format
5. Some Boundary Checks — repair_executor checks status field; seal_governance_gate checks GL7
6. Fail-Closed Logic Patterns — Status checks exist (status != "approved") at some boundaries

**What DOES NOT EXIST:**
1. **Transmission Pathway** — NO code in human_gate_events consumer path (repair_executor, seal_governance_gate, GL7)
2. **Authorization Sourcing** — repair_executor reads repair_decision.json (local file, unknown population); seal_governance_gate reads GL7 (technical only); GL7 does NOT consult human_gate_events
3. **Unified Authorization Source** — Two separate systems (human_gate_events + prevention_queue.json) not integrated
4. **Behavioral Verification** — No tests prove authorization blocking works
5. **Complete Coverage** — Only examined 2 of estimated total boundaries (ACTUAL COUNT: NOT QUANTIFIABLE)
6. **Audit Trail Recording** — Authorization checks not recorded to event log

**What IS UNKNOWN (Preserved — Must Not Be Inferred):**
1. repair_executor.py caller identity
2. repair_decision.json population mechanism
3. All Consequential Boundary complete enumeration
4. Alternative execution paths
5. prevention_queue.json actual authority relationship
6. GL7 full consumer set
7. authorization record scope correlation semantics
8. authorization record immutability guarantees
9. Caller correlation between authorization and execution
10. System-wide binding completeness

---

## CANDIDATE MINIMUM BINDING DESIGN

**Status:** Candidate Specification (Not Adopted)  
**Scope:** Examined MVP Boundaries (repair_executor, seal_governance_gate)  
**Application:** System-wide binding requires boundary-by-boundary application using identical specification basis

---

### NORMATIVE REQUIREMENT 1: request_id Binding Requires Full Correlation

**Principle:** Authorization binding requires validation that authorization decision covers the specific action being executed.

**Problem:** request_id lookup alone does not establish action/target/scope correlation.

**Specification:**
```
Binding Validation (at enforcement boundary):
  request_id → [authorization record lookup]
       ↓
  Validate: action_type MATCH (requested action matches authorized action)
  Validate: target_id MATCH (requested target matches authorized target)
  Validate: scope covers execution target (authorized scope includes actual target)
  Validate: authority permits action (authorized actor/permission covers request)
  Validate: timestamp within validity window (approval not outside time bounds)
  Validate: no revocation since approval (state unchanged to CANCELED/REJECTED)
       ↓
  APPROVED state + ALL validations pass → PERMIT
  (Any validation fails OR state != APPROVED) → BLOCK
```

**Implementation Note:** Mechanism TBD. Design requirement: all six validation steps must execute at enforcement boundary before execution permitted.

---

### NORMATIVE REQUIREMENT 2: Freshness, TTL, Revocation, TOCTOU, Replay

This requirement comprises five sub-specifications:

#### REQ-2a: TTL and Freshness Validation

**Specification:**
```
At enforcement boundary (immediately before execution):
  1. Retrieve authorization record (via get_authorization_record())
  2. Check timestamp + ttl_window
       If (now > timestamp + ttl) → EXPIRED → BLOCK
  3. Check current state in authorization_events
       If state changed (e.g., APPROVED → CANCELED) → BLOCK
```

**Mechanism:** TBD. Requirement: authorization record must be retrieved with current state, then TTL window validated.

#### REQ-2b: Revocation Detection

**Specification:**
```
If authorization state changed to CANCELED/REJECTED after initial APPROVED:
  Execution boundary must detect and BLOCK
  
Mechanism: Get current state via authorization_events before execution
```

#### REQ-2c: TOCTOU Atomic Safeguard (CORRECTED)

**CRITICAL SPECIFICATION — CORE TIMING VULNERABILITY:**

The interval between authorization check (T1) and execution (T4) creates a window where authorization state can change:

```
T0: Authorization state = APPROVED
T1: enforce_authorization() returns APPROVED
T2-T3: (execution preparation / boundary traversal)
T4: Execution occurs
```

**Vulnerability (if ONLY re-check is used):**
```
T4: Final state check → APPROVED
T4.1: Authorization state changes to CANCELED
T4.2: Execution occurs (authorization is now invalid)
     Race condition: state change invalidates the check
```

**Specification Requirement:**

```
TOCTOU Safeguard: Authorization check and consequential execution 
must be mechanically protected such that authorization state change 
between initial check (T1) and execution boundary (T4) PREVENTS execution.

Candidate mechanisms:
  A) Atomic transaction covering check + execution
     (authorization check and execution in single transaction; 
      if state changes, transaction aborts before execution)
  
  B) Execution lease / claim mechanism
     (authorization grants time-bounded execution lease;
      lease invalidated if state changes)
  
  C) Sequential enforcement with state lock
     (final re-check immediately before execution, 
      COMBINED WITH state lock preventing change between check and execution)
  
  D) Other atomic / transactional mechanism

CRITICAL: Sequential re-check ALONE is NOT a TOCTOU safeguard.
Sequential re-check may only be used as ADDITIONAL safeguard 
if combined with a mechanism that ensures state change 
cannot invalidate execution authorization between check and execution.

Distinction:
  Sequential re-check = freshness verification (detects past change)
  TOCTOU safeguard = prevents race condition (prevents change during window)

Mechanism selection: TBD (Human Gate / Implementation team decision)

Requirement: Mechanism MUST be specified and justified 
before implementation commences. Specification must demonstrate 
either TOCTOU immunity OR define acceptance bounds for TOCTOU risk.
```

#### REQ-2d: Replay Consumption Semantics (CONDITION PENDING)

**CRITICAL SPECIFICATION — EXECUTION REPLAY VULNERABILITY:**

One authorization approval may imply different execution semantics:

```
Scenario A: One-Time Consumption (one execution permitted per authorization)
  HG-001 APPROVED
    → Execution E-001 PERMIT
    → Execution E-001 (replay) BLOCK
    → Execution E-002 (same auth) BLOCK

Scenario B: Scoped Consumption (multiple executions permitted within scope)
  HG-001 APPROVED (scope: repair_type=R*)
    → Execution E-001 (R003) PERMIT
    → Execution E-002 (R003) PERMIT
    → Execution E-003 (R005) PERMIT
    → Execution E-004 (R007) BLOCK (out of scope)
```

**Specification Requirement:**

```
Replay/Consumption Rule must be DECIDED BY HUMAN GATE 
before implementation authorization granted.

Human Gate decision options:
  1) One-time consumption (1 Authorization → 1 Execution only)
  2) Scoped consumption (1 Authorization → N Executions within scope)
  3) Hybrid (per-action or per-boundary basis)

Implementation requirement (post-decision):
  authorization_id + execution_id + consumption_rule
  
  IF replay detected OR scope exceeded:
    → BLOCK

Current Status: DECISION PENDING (design adoptable, implementation BLOCKED)
Mechanism: TBD (post-decision)
```

**Consequence for Design Adoption:**
Design framework is adoptable without REQ-2d resolved. However, implementation 
cannot commence until Human Gate decides replay/consumption semantics.

#### REQ-2e: Freshness Re-Check Pattern

**Specification:**
```
At minimum, authorization state must be checked at execution boundary 
using freshest available authorization_events data.

Pattern:
  T1: enforce_authorization(request_id) → get_authorization_record()
       Validate binding, TTL, state = APPROVED
  
  T2-T3: [execution preparation]
  
  T4: Final state verification: get_authorization_record(request_id)
       Verify state still = APPROVED (no revocation)
  
  T5: execute()

If state changed between T1 and T4: BLOCK

Note: This is freshness verification (detects past change).
For TOCTOU atomicity, see REQ-2c (separate mechanism required).
```

---

### NORMATIVE REQUIREMENT 3: Audit Failure → BLOCK

**Principle:** Fail-closed enforcement requires audit failure to block execution.

**Specification:**
```
IF authorization_check result cannot be recorded to audit trail:
  → Execution BLOCKED
  → Exception raised (AuthorizationAuditFailure)
  
No silent audit loss permitted.
No "execute now, audit later" pattern permitted.

Rationale: Audit trail is evidence requirement (Phase 1 Finding).
Without audit record, no proof of authorization exists.
Fail-closed principle requires BLOCK.
```

---

### NORMATIVE REQUIREMENT 4: Audit Trail Recording Format (FIX-03 CORRECTED)

**Specification:**

Authorization and Execution are DISTINCT evidence layers.

**Layer 1: AUTHORIZATION_CHECK (audit of authorization decision)**

APPROVAL CASE (state = APPROVED, all validations pass):
```json
{
  "event_id": "E{YYYYMMDD}_{seq}",
  "timestamp": "ISO 8601",
  "type": "AUTHORIZATION_CHECK_PASSED",
  "request_id": "HG{YYYYMMDD}_{microseconds}_{hex}",
  "action_type": "repair_execution | seal_execution | ...",
  "target_id": "[canonical_identifier]",
  "scope": "[scope_definition]",
  "decision_authority": "HUMAN_GATE",
  "authorization_record_source": "human_gate_events",
  "validation": {
    "action_type_match": true,
    "target_id_match": true,
    "scope_coverage": true,
    "ttl_check": true,
    "freshness_check": true,
    "revocation_check": true
  },
  "boundary_location": "runtime/repair_executor.py:main()",
  "decision": "PERMIT"
}
```

BLOCK CASE (state != APPROVED OR validation fails):
```json
{
  "event_id": "E{YYYYMMDD}_{seq}",
  "timestamp": "ISO 8601",
  "type": "AUTHORIZATION_CHECK_FAILED",
  "request_id": "HG{YYYYMMDD}_{microseconds}_{hex}",
  "action_type": "[requested]",
  "target_id": "[requested]",
  "current_state": "REJECTED | PENDING | EXPIRED | CANCELED | UNKNOWN",
  "decision_authority": "HUMAN_GATE",
  "authorization_record_source": "human_gate_events",
  "boundary_location": "[boundary]",
  "decision": "BLOCK",
  "reason": "[validation failure or state reason]"
}
```

**Layer 2: EXECUTION_ATTEMPTED (audit of execution outcome)**

EXECUTION SUCCEEDED:
```json
{
  "event_id": "E{YYYYMMDD}_{seq}",
  "timestamp": "ISO 8601",
  "type": "EXECUTION_ATTEMPTED",
  "corresponding_authorization_event_id": "E{YYYYMMDD}_{seq}",
  "request_id": "HG{YYYYMMDD}_{microseconds}_{hex}",
  "action_type": "repair_execution",
  "target_id": "[canonical_identifier]",
  "boundary_location": "runtime/repair_executor.py:execute()",
  "execution_status": "COMPLETED",
  "outcome": "SUCCESS",
  "side_effects_recorded": true
}
```

EXECUTION FAILED:
```json
{
  "event_id": "E{YYYYMMDD}_{seq}",
  "timestamp": "ISO 8601",
  "type": "EXECUTION_ATTEMPTED",
  "corresponding_authorization_event_id": "E{YYYYMMDD}_{seq}",
  "request_id": "HG{YYYYMMDD}_{microseconds}_{hex}",
  "action_type": "repair_execution",
  "target_id": "[canonical_identifier]",
  "boundary_location": "runtime/repair_executor.py:execute()",
  "execution_status": "FAILED",
  "error": "[error details]"
}
```

**Key Clarifications:**
- `decision_authority` = the accountable human authority responsible for the authorization decision (not a system entity)
- `authorization_record_source` = the technical system (human_gate_events) that stores authorization records
- These are conceptually DISTINCT. Authority is human/accountable. Source is technical/mechanical.
- AUTHORIZATION_CHECK_* events are evidence of authorization decision
- EXECUTION_ATTEMPTED events are evidence of execution outcome
- Both layers are required for complete auditability: authorization + outcome

---

### NORMATIVE REQUIREMENT 5: Rollback Must Maintain Fail-Closed (FIX-01 CORRECTED)

**Principle:** Rollback procedure must not weaken enforcement protection.

**Specification:**
```
IF production incident requires rollback:
  
ENFORCEMENT-PRESERVING Option (REQUIRED):
  Rollback MUST NOT restore an execution path
  whose authorization enforcement is weaker than the
  currently enforced state.
  
  If prior version had weaker/absent enforcement:
    → Consequential execution remains BLOCKED
    → Code must be repaired to restore enforcement
    → Cannot use rollback to bypass enforcement
  
  If enforcement level can be preserved during rollback:
    → Rollback permitted

UNSAFE Option (PROHIBITED):
    - Disable enforcement conditionally
    - Suppress authorization checks
    - This is authorization bypass, not rollback
    - Code-based rollback alone is insufficient
      if it restores non-enforced execution paths

Requirement: Rollback procedure must be ENFORCEMENT-PRESERVING.

Mechanism: TBD (must be defined such that enforcement 
cannot be weakened by rollback operation)

Rationale: Enforcement system cannot be trusted to disable itself.
Weaker enforcement during rollback is authorization failure.
```

---

### NORMATIVE REQUIREMENT 6: Coverage Status = NOT QUANTIFIABLE

**Principle:** Coverage claims require fixed boundary enumeration.

**Specification:**
```
MVP Boundaries Examined: 2
  - repair_executor
  - seal_governance_gate

Total Consequential Boundaries: UNKNOWN
  (Complete enumeration incomplete — UNKNOWN item #3)

Boundary Count Status: NOT QUANTIFIABLE
  - Cannot claim X% coverage without fixed denominator
  - Partial binding reduces (but does not eliminate) unauthorized execution risk
  - System-wide binding requires same specification applied per-boundary
  - Unexamined boundaries remain UNAUTHORIZED

Consequence: MVP binding is partial. System-wide binding incomplete.
```

---

### NORMATIVE REQUIREMENT 7: System-Wide Risk Assessment (FIX-02 CORRECTED)

**Principle:** MVP binding is partial; system-wide authorization binding NOT ESTABLISHED.

**Specification:**
```
Risk Profile (MVP — 2 boundaries examined):
  Authorization records EXIST: YES
  State retrieval ESTABLISHED: YES
  Transmission to MVP boundaries ESTABLISHED: YES (if design adopted)
  Fail-closed enforcement at MVP: YES (if design adopted)
  
Risk Profile (System-Wide — unexamined boundaries):
  Mechanical Authorization Binding at unexamined boundaries: NOT ESTABLISHED
  Unauthorized execution possibility at unexamined boundaries: UNKNOWN
  System-wide binding incomplete: YES
  System-wide authorization risk: NOT MINIMIZED / NOT ESTABLISHED

Conclusion: MVP binding reduces risk at examined boundaries.
System-wide authorization integrity: NOT ESTABLISHED.
Remaining boundaries require identical specification application 
(Phase 2 work).

CRITICAL: UNKNOWN ≠ PERMITTED
  Unexamined boundaries are NOT AUTHORIZED.
  Whether unexamined boundaries mechanically permit unauthorized execution:
    = UNKNOWN (not confirmed, not denied)
  Does this unknown permit their use without authorization?
    = NO (Authorization binding not established ≠ Silent execution permitted)
```

---

### NORMATIVE REQUIREMENT 8: Design Status is CANDIDATE

**Principle:** Design adoption is separate from specification creation.

**Specification:**
```
This document presents a CANDIDATE design, not ADOPTED design.

Status progression:
  Phase 8 author creates specification
           ↓
  Human Gate reviews specification
           ↓
  Human Gate decides: ADOPT / MODIFY / REJECT
           ↓
  If ADOPT: Design becomes canonical specification basis
  If MODIFY: Author revises; Human Gate re-reviews
  If REJECT: Design is discarded; new specification created
```

**Current State:** CANDIDATE (awaiting Human Gate adoption decision)

---

### NORMATIVE REQUIREMENT 9: Design Adoption ≠ Implementation Authorization

**Principle:** Decision to adopt design framework is separate from permission to implement.

**Specification:**
```
Flow (CORRECT):
  Design Adoption Decision (Human Gate)
           ↓
  Specification Basis ESTABLISHED
           ↓
  Implementation Planning (including REQ-2d, REQ-2c decision)
           ↓
  Implementation Authorization Decision (Human Gate/Authority)
           ↓
  Implementation Commences
  
Current Status:
  Design Adoption: PENDING (not yet decided)
  Implementation Authorization: NOT GRANTED
```

**Consequence:** Even if design is adopted, implementation remains blocked 
until separate authorization granted AND all CONDITION PENDING items resolved.

---

### NORMATIVE REQUIREMENT 10: UNKNOWN Items — Scope and Handling

**Principle:** UNKNOWN items affecting current execution integrity block execution.

**Specification:**

```
For each UNKNOWN item, classify by SCOPE:

SCOPE 1: Affects authorization integrity of CURRENT EXECUTION BOUNDARY
  Examples: 
    - repair_decision.json population (affects repair_executor binding)
    - seal_target identifier semantics (affects seal_governance_gate binding)
    - authorization scope correlation (affects all boundaries)
  
  Status: MUST BE RESOLVED before implementation of that boundary
  If unresolved: Implementation/Execution BLOCKED
  
SCOPE 2: Affects unexamined, out-of-scope boundaries
  Examples:
    - System-wide boundary enumeration (UNKNOWN #3, #10)
    - Alternative execution paths in unexamined boundaries
    - GL7 full consumer set (for GL7 boundaries not examined)
  
  Status: Does NOT authorize those boundaries
  Those boundaries remain UNAUTHORIZED (BLOCKED) until same binding 
  specification applied per-boundary
  
  Mechanism: Unexamined boundaries are NOT ACTIVATED by this MVP design.
  They remain in UNAUTHORIZED state pending Phase 2.

Application to Current Design:
  - UNKNOWN #1-6, #8-9: Classify as SCOPE 1 or SCOPE 2 per boundary
  - UNKNOWN #7: (scope correlation) SCOPE 1 → MUST RESOLVE before MVP
  - UNKNOWN #10: (system-wide) SCOPE 2 → does NOT block MVP, 
                 blocks unexamined boundaries only

CRITICAL DISTINCTION:
  Unresolved UNKNOWN #10 (system-wide completeness)
    ≠
  UNKNOWN #10 blocks MVP implementation
  
Rather:
  Unresolved UNKNOWN #10
    =
  Unexamined boundaries remain UNAUTHORIZED
    =
  Phase 2 activity (system-wide binding per-boundary)
```

---

## CANDIDATE COMPONENT SPECIFICATION

**Component Count:** 5 (unified)

---

### Component 1: Authorization Enforcement Module

**What:** governance/authorization_enforcer.py (NEW, ~220 lines)

**Specification:**

The enforcer module requires two distinct API functions:

```python
def get_state(request_id):
    """
    Get current authorization STATE ONLY.
    
    Returns: state string (APPROVED | REJECTED | PENDING | EXPIRED | CANCELED)
    
    Purpose: Quick state check. Does NOT include full record data.
    Used by: Simple state-only queries (e.g., guard clauses)
    """
    pass

def get_authorization_record(request_id):
    """
    Get FULL authorization record.
    
    Returns: AuthorizationRecord object with:
      - request_id
      - state
      - action_type
      - target_id
      - scope
      - authority
      - approval_timestamp
      - validity_window
      - revocation_status
      - event_id_chain
    
    Purpose: Comprehensive binding validation. Includes all data for REQ-1/2.
    Used by: enforce_authorization() enforcement boundary
    """
    pass


def enforce_authorization(request_id, action_type, target_id, scope=None):
    """
    Enforce human authorization before consequential execution.
    
    Parameters:
      request_id: HG{YYYYMMDD}_{microseconds}_{hex} format
      action_type: repair_execution | seal_execution | ...
      target_id: canonical identifier (NOT message/string content)
      scope: optional scope specifier
    
    Returns:
      AuthorizationResult(authorized=True, state="APPROVED", audit_id=...)
      
    Raises:
      AuthorizationError (state != APPROVED or validation fails)
      AuthorizationAuditFailure (audit record creation failed)
    
    Fail-Closed: Default behavior is BLOCK (raise exception)
    
    Implementation Steps:
      1. Validate inputs (request_id format, action_type, etc.)
      2. Retrieve FULL authorization record via get_authorization_record()
      3. Validate binding (REQ-1): action/target/scope correlation
      4. Check freshness, TTL, revocation (REQ-2a/b)
      5. Verify state = APPROVED
      6. Record audit trail (REQ-3/4)
         If audit fails: raise AuthorizationAuditFailure → BLOCK
      7. Return AuthorizationResult
    """
    if not request_id:
        raise AuthorizationError("request_id required")
    
    # CRITICAL: Use get_authorization_record(), not get_state()
    # get_state() returns only state string; binding validation requires full record
    auth_record = get_authorization_record(request_id)
    
    # Validate binding (REQ-1)
    if not validate_binding(auth_record, action_type, target_id, scope):
        raise AuthorizationError(f"Binding validation failed")
    
    # Check freshness/TTL/revocation (REQ-2)
    if not is_fresh(auth_record) or is_expired(auth_record) or is_revoked(auth_record):
        raise AuthorizationError(f"Authorization not current: {auth_record.state}")
    
    # Final state check (REQ-2a/b)
    if auth_record.state != "APPROVED":
        raise AuthorizationError(f"Not approved: {auth_record.state}")
    
    # Record audit trail (REQ-3/4)
    try:
        audit_result = record_authorization_audit(auth_record, action_type, target_id)
    except Exception as e:
        raise AuthorizationAuditFailure(f"Audit failed: {e}")
    
    return AuthorizationResult(authorized=True, state="APPROVED", audit_id=audit_result.event_id)
```

**Key Properties:**
- ✓ Reads FULL record from human_gate_events via get_authorization_record()
- ✓ Validates 6-part binding (REQ-1)
- ✓ Checks freshness/TTL/revocation (REQ-2a/b)
- ✓ Records audit trail with authority/source separation (REQ-4)
- ✓ Fails-closed (exception on any non-APPROVED or validation failure)
- ✓ Callable from all boundaries
- ✓ API distinction: get_state() for simple checks, get_authorization_record() for binding validation

---

### Component 2: Boundary Integration (repair_executor + seal_governance_gate)

**Boundary 2A: repair_executor.py Enhancement**

**Current Code (Lines 50-67):**
```python
def main():
    decision = load_decision()
    status = decision.get("status")
    if status != "approved":
        print("REPAIR_NOT_APPROVED")
        return
    result = execute_repair(decision)
```

**Specification Change:**
```python
from governance.authorization_enforcer import enforce_authorization, AuthorizationError

def main():
    decision = load_decision()
    request_id = decision.get("request_id")
    action_type = decision.get("action_type", "repair_execution")
    repair_id = decision.get("selected_repair", {}).get("repair_id")
    scope = decision.get("scope", "repair")
    
    try:
        enforce_authorization(
            request_id=request_id,
            action_type=action_type,
            target_id=repair_id,
            scope=scope
        )
    except AuthorizationError as e:
        print(f"REPAIR_NOT_AUTHORIZED: {e}")
        return
    
    result = execute_repair(decision)
```

**Changes:** ~8 lines (import + parameters from decision + enforce call)

**Effect:** repair_executor now reads human authorization state from human_gate_events at execution boundary

---

**Boundary 2B: seal_governance_gate.py Enhancement**

**Current Code (Lines 70-100):**
```python
def execute(self, message: str, ...):
    approval = self.governance.pre_execution_check(action)
    if not approval.approved:
        return GateResult(approved=False, ...)
    runner = _seal_runner or self._run_seal_script
    stdout, returncode = runner(message)
```

**Specification Change:**
```python
def execute(self, message: str, request_id=None, target_id=None, scope=None, ...):
    # NEW: Human authorization check (BEFORE GL7 technical check)
    try:
        enforce_authorization(
            request_id=request_id,
            action_type="seal_execution",
            target_id=target_id,  # MUST be canonical target ID (NOT message)
            scope=scope or "seal"
        )
    except AuthorizationError as e:
        return GateResult(approved=False, reason=f"authorization_failed: {e.state}")
    
    # GL7 technical check (unchanged)
    approval = self.governance.pre_execution_check(action)
    if not approval.approved:
        return GateResult(approved=False, ...)
    
    runner = _seal_runner or self._run_seal_script
    stdout, returncode = runner(message)
```

**Changes:** ~10 lines (parameters + enforce call + error handling)

**Effect:** seal_governance_gate enforces human authorization BEFORE GL7 technical checks

---

**SPECIFICATION REQUIREMENT (seal_target_identity — REQ-4 related):**

```
target_id parameter MUST be CANONICAL TARGET IDENTIFIER.

UNACCEPTABLE:
  target_id = message  (vulnerable to content variation: formatting, 
                        serialization, encoding changes)
  
REQUIRED:
  Determine seal target type (file | directory | commit | artifact | operation)
  Define canonical identifier for that type
  Pass canonical identifier as target_id
  
Example (TBD — to be defined before implementation):
  If seal target is file path:
    target_id = normalized_path_hash (stable across sessions)
  
  If seal target is git commit:
    target_id = commit_sha (canonical commit identifier)
  
  If seal target is artifact:
    target_id = artifact_id (stable system identifier)
  
  If seal target is operation:
    target_id = operation_type + operation_id (composite identifier)

Current Status: Semantics TBD
Requirement: seal_target_identity_semantics MUST be defined 
before implementation commences.

Implication for Design Adoption:
Design is adoptable with this TBD. However, implementation cannot 
proceed for seal_governance_gate until target_id semantics clarified.
```

---

### Component 3: Authorization-Carrying Decision Format

**Current repair_decision.json:**
```json
{
    "status": "approved",
    "selected_repair": {"repair_id": "R003"}
}
```

**Specification (Required Format):**
```json
{
    "request_id": "HG20260908_123456789_abc1",
    "action_type": "repair_execution",
    "target_id": "R003",
    "scope": "repair",
    "selected_repair": {"repair_id": "R003"}
}
```

**Changes:**
- ADD: `request_id` (references human_gate authorization record)
- ADD: `action_type` (specifies action being authorized)
- ADD: `target_id` (identifies specific repair target — must match authorization)
- ADD: `scope` (authorization scope — must cover target)
- KEEP: `selected_repair` and all existing fields (backward compatible)
- DEPRECATE: `status` field (enforcement now via enforce_authorization() check)

**Effect:** Decision files now carry full binding semantics required by REQ-1

**Validation Logic (at enforcement boundary):**
```
At boundary:
  authorization_action_type (from human_gate_events) == request action_type
  authorization_target_id (from human_gate_events) == request target_id
  authorization_scope (from human_gate_events) covers request scope/target
  
If any mismatch: BLOCK
```

---

### Component 4: Behavioral Verification (Test Suite)

**What:** tests/test_mechanical_authorization_binding.py (NEW, ~400 lines)

**Test Categories:**

**1. Binding Validation Tests (6 tests)**
- action_type mismatch → BLOCK
- target_id mismatch → BLOCK
- scope coverage failure → BLOCK
- authority validation failure → BLOCK
- timestamp outside validity → BLOCK
- All bindings valid → PERMIT

**2. TTL/Freshness Tests (4 tests)**
- TTL expired → BLOCK
- TTL valid → re-check passes
- Freshness check detects state change → BLOCK
- Boundary re-check enforced (state checked again before execution)

**3. Revocation Tests (3 tests)**
- Post-approval CANCELED → BLOCK
- Post-approval REJECTED → BLOCK
- Revocation detection before execution

**4. TOCTOU Tests (3 tests)**
- State change between check and execution → BLOCK (atomic mechanism required)
- Sequential re-check alone insufficient for TOCTOU
- Final state verification enforced at boundary

**5. Replay Tests (4 tests - parameterized by HG-selected semantics)**
- One-time consumption: replay of same execution → BLOCK (if selected)
- One-time consumption: second execution with same auth → BLOCK (if selected)
- Scoped consumption: execution within scope → PERMIT (if selected)
- Scoped consumption: execution outside scope → BLOCK (if selected)

Note: Replay test suite is parameterized by Human Gate decision on consumption semantics (REQ-2d).
Tests verify both one-time and scoped policies; actual policy selection is Human Gate decision.

**6. Edge Case Tests (5 tests)**
- Missing request_id → BLOCK
- Unknown request_id → BLOCK
- Audit failure → BLOCK (executes only if audit succeeds)
- Invalid state (PENDING, REJECTED, EXPIRED) → BLOCK
- Corrupted authorization record → BLOCK

**7. Boundary Integration Tests (3 tests)**
- repair_executor blocks when non-APPROVED
- seal_governance_gate blocks when authorization failed
- Both boundaries enforce BEFORE secondary checks (GL7)

**8. API Distinction Tests (2 tests)**
- get_state() returns state only (not binding data)
- get_authorization_record() returns full record (enables binding validation)

**9. Evidence Layer Separation Tests (2 tests - FIX-03)**
- AUTHORIZATION_CHECK_PASSED recorded separately from EXECUTION_ATTEMPTED
- EXECUTION_COMPLETED/FAILED recorded with corresponding authorization event_id

**Total:** 32+ test cases

**Verification:** All tests MUST pass before production deployment

---

### Component 5: Auditability (Audit Trail Recording - FIX-03)

Authorization and Execution are tracked as DISTINCT evidence layers (see REQ-4 above).

**Layer 1: AUTHORIZATION_CHECK Records**

APPROVAL event (PERMIT):
```json
{
  "event_id": "E20260908_001",
  "timestamp": "2026-09-08T14:30:00.000Z",
  "type": "AUTHORIZATION_CHECK_PASSED",
  "request_id": "HG20260908_123456789_abc1",
  "action_type": "repair_execution",
  "target_id": "R003",
  "scope": "repair",
  "decision_authority": "HUMAN_GATE",
  "authorization_record_source": "human_gate_events",
  "validation": {
    "action_type_match": true,
    "target_id_match": true,
    "scope_coverage": true,
    "ttl_check": true,
    "freshness_check": true,
    "revocation_check": true
  },
  "boundary_location": "runtime/repair_executor.py:main()",
  "decision": "PERMIT"
}
```

BLOCK event (authorization failed):
```json
{
  "event_id": "E20260908_002",
  "timestamp": "2026-09-08T14:31:00.000Z",
  "type": "AUTHORIZATION_CHECK_FAILED",
  "request_id": "HG20260908_234567890_def2",
  "action_type": "repair_execution",
  "target_id": "R003",
  "current_state": "REJECTED",
  "decision_authority": "HUMAN_GATE",
  "authorization_record_source": "human_gate_events",
  "boundary_location": "runtime/repair_executor.py:main()",
  "decision": "BLOCK",
  "reason": "authorization_not_approved"
}
```

**Layer 2: EXECUTION_ATTEMPTED Records**

EXECUTION SUCCEEDED:
```json
{
  "event_id": "E20260908_003",
  "timestamp": "2026-09-08T14:30:15.000Z",
  "type": "EXECUTION_ATTEMPTED",
  "corresponding_authorization_event_id": "E20260908_001",
  "request_id": "HG20260908_123456789_abc1",
  "action_type": "repair_execution",
  "target_id": "R003",
  "boundary_location": "runtime/repair_executor.py:execute()",
  "execution_status": "COMPLETED",
  "outcome": "SUCCESS",
  "side_effects_recorded": true
}
```

EXECUTION FAILED:
```json
{
  "event_id": "E20260908_004",
  "timestamp": "2026-09-08T14:31:30.000Z",
  "type": "EXECUTION_ATTEMPTED",
  "corresponding_authorization_event_id": "E20260908_001",
  "request_id": "HG20260908_123456789_abc1",
  "action_type": "repair_execution",
  "target_id": "R003",
  "boundary_location": "runtime/repair_executor.py:execute()",
  "execution_status": "FAILED",
  "error": "[error details]"
}
```

**Evidence Separation Benefits:**
- Authorization decision (approval/block) is evidence of Human Gate decision
- Execution outcome (success/failure) is evidence of system behavior
- Both are required for complete forensic analysis
- No single event carries both authoritative decision and outcome (separation of concerns)

---

## SPECIFICATION ADOPTION CHECKLIST

To adopt this design as canonical specification basis:

- [ ] **REQ-1** — request_id binding includes action_type, target_id, scope, authority validation
- [ ] **REQ-2a** — TTL/freshness validation specified (mechanism TBD)
- [ ] **REQ-2b** — Revocation detection specified
- [ ] **REQ-2c** — TOCTOU atomic safeguard requirement (sequential re-check NOT sufficient alone)
- [ ] **REQ-2d** — Replay consumption rule pending Human Gate decision (design adoptable, implementation BLOCKED)
- [ ] **REQ-2e** — Freshness re-check pattern specified
- [ ] **REQ-3** — Audit failure → BLOCK (fail-closed)
- [ ] **REQ-4** — Audit trail with AUTHORIZATION/EXECUTION layer separation
- [ ] **REQ-5** — Rollback maintains enforcement-preserving fail-closed (enforcement cannot weaken)
- [ ] **REQ-6** — Coverage = NOT QUANTIFIABLE (documented)
- [ ] **REQ-7** — System-wide risk = NOT MINIMIZED / NOT ESTABLISHED (UNKNOWN preserved)
- [ ] **REQ-8** — Design status = CANDIDATE (not adopted)
- [ ] **REQ-9** — Design Adoption ≠ Implementation Authorization
- [ ] **REQ-10** — UNKNOWN → BLOCK limited to current execution boundary integrity
- [ ] **Component 1** — Authorization Enforcer with get_state() / get_authorization_record() API distinction
- [ ] **Component 2A** — repair_executor integration with request_id/action/target/scope parameters
- [ ] **Component 2B** — seal_governance_gate integration with canonical target_id (TBD semantics)
- [ ] **Component 3** — Decision Format includes action_type, target_id, scope, request_id
- [ ] **Component 4** — Behavioral Test Suite (32+ tests including evidence layer separation) specified
- [ ] **Component 5** — Audit Trail Recording with AUTHORIZATION/EXECUTION layer separation
- [ ] **Evidence Boundary** — Maintained (no inference beyond Phase 1/2 findings)
- [ ] **UNKNOWN Items** — Preserved and scoped (SCOPE 1 vs SCOPE 2)
- [ ] **Internal Consistency** — No contradictions between components and requirements

---

## KNOWN SPECIFICATION GAPS (TBD Before Implementation)

These items are specified as REQUIREMENTS, but mechanism is explicitly TBD:

**Implementation-Blocking (SCOPE 1 — Current Boundary):**

1. **TOCTOU Atomic Mechanism** — How to prevent authorization state change between check and execution?
   - Options: transaction, lease, sequential + lock, other
   - Specification: Required before MVP implementation
   
2. **seal_governance_gate target_id Semantics** — Canonical identifier definition for seal operations
   - Current: message (TOO WEAK)
   - Required: target_type + target_id stable semantics
   - Specification: Required before seal_governance_gate implementation
   
3. **Replay Consumption Semantics** — Human Gate decision on one-time vs. scoped execution
   - Decision authority: Human Gate
   - Specification: Required before implementation (REQ-2d CONDITION PENDING)

4. **Enforcement-Preserving Rollback Mechanism** — How to ensure rollback cannot weaken enforcement?
   - Options: version comparison, enforcement checkpoint, other
   - Specification: Required before MVP implementation

**Non-Blocking (SCOPE 2 — Out-of-Scope Boundaries):**

5. **System-Wide Boundary Enumeration** — Complete list of all consequential boundaries
   - Current: 2 examined, ~unknown unexamined
   - Specification: Required for Phase 2 (does NOT block MVP)

6. **repair_decision.json Population Mechanism** — How are decision files created?
   - Current: UNKNOWN (not critical for MVP if request_id provided)
   - Specification: TBD during implementation

---

## SAFETY PROPERTIES

This specification ensures (IF ADOPTED AND CONDITIONS RESOLVED):

1. **Fail-Closed** — Default is BLOCK execution unless state = APPROVED + all validations pass
2. **Auditable** — Every authorization decision recorded with full binding context (separate from execution outcome)
3. **Safe** — Exception-based blocking prevents silent bypasses
4. **Binding** — Six-part correlation between authorization and execution at boundary level
5. **Recoverable** — Rollback procedure maintains enforcement-preserving fail-closed
6. **Measurable** — Audit trail enables post-hoc verification and forensic analysis (authorization + execution layers)
7. **Testable** — 32+ behavioral tests verify blocking at each validation point
8. **Transparent** — All authorization checks visible in audit trail
9. **TOCTOU-Aware** — TOCTOU vulnerability acknowledged; atomic mechanism required (TBD)
10. **Replay-Aware** — Replay vulnerability acknowledged; consumption semantics pending (TBD)

---

## IMPLEMENTATION READINESS PRECONDITIONS

Before implementation can commence, following decisions/clarifications required:

**Design Adoption Prerequisites:**
1. Human Gate adoption decision (ADOPT / MODIFY / REJECT)

**If ADOPT, then Implementation Prerequisites:**
2. TOCTOU mechanism selection (transaction vs lease vs lock+sequential vs other)
3. REQ-2d replay/consumption semantics decision (one-time vs scoped)
4. seal_target_id canonical semantics definition (for seal_governance_gate)
5. Enforcement-preserving rollback mechanism design
6. UNKNOWN item SCOPE 1 classification (integrity-affecting items for current boundaries)

**Sequence:**
- Design adoption (current — awaiting HG decision)
- Implementation authorization (separate, post-adoption)
- Implementation planning (including TBD items 2-6)
- Implementation commences (after all prerequisites resolved)

---

## WHAT THIS DESIGN DOES NOT INCLUDE

**Out of Scope (Correct per Evidence Boundary):**

1. **Implementation Code** — Only specification, no code modification
2. **Full System Coverage** — Only 2 MVP boundaries examined; remaining UNKNOWN and UNAUTHORIZED
3. **Human Gate Approval** — Design does not approve executions; authorization still separately required
4. **Architectural Changes** — No schema modifications, no breaking changes
5. **Running Implementation** — No tests executed, no staging deployment, no production rollout

---

## RISKS AND MITIGATIONS

### Risk 1: TOCTOU Mechanism Implementation Bug

**Mitigation:** Atomic/transactional requirement in specification; behavioral tests for atomic property verification

### Risk 2: Sequential Re-Check Misused for TOCTOU

**Mitigation:** Clear specification distinction: sequential re-check ≠ TOCTOU atomicity

### Risk 3: Replay Consumption Semantics Unresolved at Implementation

**Mitigation:** REQ-2d marked CONDITION PENDING; implementation BLOCKED until decided

### Risk 4: seal_target_id Content Variation

**Mitigation:** Canonical identifier requirement; TBD with implementation plan

### Risk 5: Partial System-Wide Coverage

**Mitigation:** MVP binding reduces risk at examined boundaries; remaining boundaries explicitly UNAUTHORIZED

### Risk 6: Design Adoption Conflated with Implementation

**Mitigation:** REQ-9 maintains separation; implementation authorization is separate decision

### Risk 7: Rollback Weakens Enforcement

**Mitigation:** Enforcement-preserving requirement in REQ-5; mechanism TBD but must prevent weakening

### Risk 8: Authorization/Execution Evidence Conflation

**Mitigation:** REQ-4 layer separation; distinct event types for authorization check vs. execution

---

## POSITION IN INVESTIGATION FLOW

```
Phases 1-6: Evidence Collection (COMPLETE)
        ↓
Phase 7: Human Gate Review Conditions (Defined)
        ↓
Phase 8 v2.0: Remediated Design (A/WC/HOLD/R = B)
        ↓
Audit Iteration 1: 5 Core Conditions Identified
        ↓
Phase 8 v2.1: HG-Ready Specification (A/WC/HOLD/R = B)
        ↓
Audit Iteration 2: 6 Critical Consistency Corrections
        ↓
Phase 8 v2.2: Final Audit Submission (Initial audit)
        ↓
Audit Iteration 3: 4 Normative Corrections (FIX-01~04)
        ↓
Phase 8 v2.3: Audit-Corrected Specification (THIS DOCUMENT)
        ↓
Final Verification: Consistency Check
        ↓
IF PASS: HG-PHASE-MECHANICAL-AUTH-BINDING-DESIGN-REVIEW
IF NOT PASS: Return to revision
```

---

## CURRENT STATUS (v2.3)

**Investigation:** COMPLETE (Evidence bounded, UNKNOWNs preserved and scoped)

**Candidate Design:** IDENTIFIED (10 normative requirements + 5 components + clear TBD items)

**Audit Iteration 3:** COMPLETE (4 normative corrections applied: FIX-01~04)

**Design Specification:** READY FOR FINAL VERIFICATION

**Design Adoption Status:** PENDING HUMAN GATE REVIEW

**Design Adoption Decision:** Not yet made

**Implementation Authorization:** NOT GRANTED (separate decision post-adoption)

**Current HOLD:** MAINTAIN

**System-Wide Binding Status:** NOT ESTABLISHED (unexamined boundaries UNAUTHORIZED)

---

## PHASE 8 (v2.3) CONCLUSION

**Key Distinctions (Preserved v2.2, Enhanced v2.3):**
```
Authorization Records EXIST
        ↓
Authorization State Retrievable ESTABLISHED
        ↓
Authorization State → Consequential Execution = NOT YET ESTABLISHED
        ↓
This Design Specifies How to Establish Connection (MVP boundaries only)
        ↓
Design Adoption = Specification Basis (Human Gate decision)
        ↓
Design Adoption ≠ Implementation (separate decision post-adoption)
        ↓
MVP Binding ≠ System-Wide Binding (Phase 2 required for unexamined boundaries)

Key Specification Improvements (v2.3 corrections):
        ↓
REQ-5: enforcement-preserving rollback (not code-based alone)
REQ-7: UNKNOWN preservation (not YES inference)
REQ-3/4: AUTHORIZATION/EXECUTION evidence separation
REQ-2d: HG-selected policy reference (not fixed replay_check)
```

**Specification Basis Readiness (v2.3):**
- Evidence boundary maintained
- 10 candidate normative requirements with all 10 consistency corrections integrated (6 v2.2 + 4 v2.3)
- 5 core components specified with clear TBD mechanisms and preconditions
- UNKNOWN items preserved, classified (SCOPE 1 vs SCOPE 2), and applied correctly
- Safety properties documented
- Implementation preconditions enumerated
- Risk profile clear and evidence-bounded
- Internal consistency verified (no contradictions between components and requirements)
- Evidence layers properly separated (authorization decision ≠ execution outcome)

**Ready for:** HG-PHASE-MECHANICAL-AUTH-BINDING-DESIGN-REVIEW (Final verification of consistency)

---

**Phase 8 v2.3: AUDIT CORRECTIONS APPLIED**

**Status:** Audit-Corrected Specification (Ready for HG-PHASE-MECHANICAL-AUTH-BINDING-DESIGN-REVIEW after final verification)

**Awaiting:** Final verification that v2.3 achieves evidence-bounded consistency and is ready for Human Gate design review
