# Phase C Authorization Boundary Investigation v1.0

**Investigation Focus**: Identify the missing specification for Human Gate Current Authorization in Phase C

**Date**: 2026-09-02

---

## Executive Summary

Phase C implementation (seal_governance_gate.py) currently performs an "Approval Context Consistency Check" - comparing stored historical parameters with current request parameters. This is **NOT** the "Authorization Boundary" that R04-B specifies.

R04-B requires:

```
Execution must verify:
  Human Gate Current Authorization State == APPROVED
    ↓
  Before calling seal script
    ↓
  If not APPROVED → Block execution
```

**Current Implementation Status**: NOT IMPLEMENTED - Authority source and retrieval mechanism not specified.

---

## 1. Human Gate State Machine (Verified Implementation)

### 1.1 Architecture

File: `phi_os/human_gate.py` (fully implemented, production-ready)

State transitions:
```
submit(payload) → PENDING
            ↓ (human approval)
         APPROVED    REJECTED    EXPIRED    CANCELED
```

### 1.2 State Retrieval API

```python
phi_os.human_gate.get_state(request_id: str) -> str | None
```

Returns current state of a request reconstructed from event history.

- Database: `data/mocka_events.db` (SQLite)
- Table: `human_gate_events`
- Immutable: Events are append-only, never modified
- Current State: Derived from latest event per request_id

### 1.3 Validation Pattern

```python
# Check if a request is currently authorized
request_id = "EXEC_20260902T120000_abc123def456"
current_state = phi_os.human_gate.get_state(request_id)

if current_state == "APPROVED":
    # Execute seal
    pass
else:
    # Block execution
    raise AuthorizationDenied(f"Request state: {current_state}")
```

---

## 2. Missing Specification: Request Identification

### 2.1 Problem Statement

SealGovernanceGate needs to know **which Human Gate request_id to check**. Currently unspecified:

| Question | Answer | Status |
|---|---|---|
| Where does request_id originate? | ??? | MISSING |
| Who/what creates the Human Gate request? | ??? | MISSING |
| When is the request submitted to Human Gate? | ??? | MISSING |
| How does SealGovernanceGate.execute() receive the request_id? | ??? | MISSING |
| Is request_id part of the seal action or separate metadata? | ??? | MISSING |

### 2.2 Possible Specification Options

#### Option A: External submission (Pre-approval pattern)

```
Timeline:
  T1: Human Gate request created separately
      execute(seal_message, request_id=REQUEST_1234)
                                ↑
                        passed as parameter

  T2: Human reviews and approves REQUEST_1234 in Human Gate UI

  T3: SealGovernanceGate.execute() is called
      - Checks: get_state(REQUEST_1234) == "APPROVED"
      - If true, proceeds to seal execution
```

**Advantage**: Clear audit trail of "what was approved"  
**Disadvantage**: Requires Human Gate approval BEFORE attempting execution

#### Option B: Internal submission (On-demand pattern)

```
Timeline:
  T1: SealGovernanceGate.execute(seal_message) is called
      - Generates execution_id = "EXEC_20260902_..."
      - Submits to Human Gate: phi_os.human_gate.submit({
          "event_type": "SEAL_EXECUTION",
          "request_id": execution_id,
          "seal_message": seal_message,
          "scope": scope,
          ...
        })
      - Returns "please wait, pending Human Gate review"

  T2: Human reviews seal_message in Human Gate UI
      - Approves/Rejects REQUEST_1234

  T3: Caller polls or is notified
      - Re-calls SealGovernanceGate.execute() with execution_id
      - Checks: get_state(execution_id) == "APPROVED"
      - If true, proceeds to seal execution
```

**Advantage**: Seal request creation tied to execution intent  
**Disadvantage**: Requires polling/notification mechanism; splits execution into approval + execution phases

#### Option C: Embedded authorization metadata (Contract pattern)

```
Timeline:
  T1: Seal action carries authorization metadata:
      execute(
        message=msg,
        authorization={
          "type": "human_gate_preapproval",
          "request_id": "HG_202609_001",
          "expires_at": "2026-09-03T00:00:00Z"
        }
      )

  T2: SealGovernanceGate.execute() validates:
      - Checks expiration
      - Checks: get_state(request_id) == "APPROVED"
      - Verifies authorization matches current action parameters
      - If all pass, proceeds to seal execution
```

**Advantage**: Self-contained request; metadata validates authorization scope  
**Disadvantage**: Authorization coupling to execution parameters; need for expiration/scope validation

---

## 3. Current Implementation Gap Analysis

### 3.1 What Phase C DOES implement

✓ Approval Check (GL7 via ExecutionGovernanceEngine)  
✓ Parameter Consistency Check (scope, expected_max_changes)  
✓ Event Recording (APPROVAL_PASSED/DENIED, AUTHORIZATION_PASSED/DENIED, EXECUTION_COMPLETED/FAILED)  
✓ Separate decision events with linking IDs  

### 3.2 What Phase C DOES NOT implement

✗ Human Gate Current Authorization retrieval  
✗ Request identification mechanism (request_id source)  
✗ Authority source connection: Human Gate → SealGovernanceGate  
✗ Execution consumption of authorization state  

### 3.3 Code Evidence

**File**: `governance/seal_governance_gate.py:87-138`

```python
def _current_authorization_check(self, approval_state: dict, action: dict):
    """
    M3: Current Authorization Re-check at execution time.
    Validates that authorization context hasn't changed since approval.
    """
    # Current implementation:
    # - Compares stored _last_approval_state against current action
    # - Checks: scope matches, max_changes matches
    # - Returns: is_authorized=True/False
    
    # MISSING:
    # - No call to phi_os.human_gate.get_state(request_id)
    # - No external authority consultation
    # - No Human Gate current state validation
    # - Authority is hardcoded: "system:seal_governance_gate" (self-reference)
    #   Should be: "human:gate_approval" (external authority)
```

---

## 4. Authority Boundary Analysis

### 4.1 Current Authority Structure

```
Approval Authority (GL7):
  system:seal_governance_gate
    → ExecutionGovernanceEngine.pre_execution_check()
    → GL7 logic (parameter validation)

Authorization Authority (Phase C):
  system:seal_governance_gate (self-check)
    → _current_authorization_check()
    → Parameter consistency (NOT external authority)

Execution Authority:
  system:seal_governance_gate (self-check)
    → subprocess.run(anchor_update.py)
```

**Problem**: No external Human Gate authority in the chain.

### 4.2 Required Authority Structure (R04-B)

```
Approval Authority (GL7):
  system:seal_governance_gate
    → ExecutionGovernanceEngine.pre_execution_check()
    ✓ As implemented

Authorization Authority (MISSING):
  human:gate_approval
    ← phi_os.human_gate.get_state(request_id)
    ← Should verify: state == "APPROVED"
    ✗ NOT CONNECTED

Execution Authority:
  system:seal_governance_gate
    → subprocess.run(anchor_update.py)
    (may proceed only if both Approval AND Authorization pass)
```

---

## 5. Specification Gap Mapping

| Component | Specification | Status |
|---|---|---|
| Request ID Generation | How is request_id assigned? | MISSING |
| Request ID Lifecycle | When created? When passed to SealGovernanceGate? | MISSING |
| Human Gate Submission | Is request submitted before or during execute()? | MISSING |
| State Check Timing | When does get_state(request_id) get called? | MISSING |
| State Validation | What states block execution? (PENDING→block, REJECTED→block, EXPIRED→block) | MISSING |
| Error Handling | How are authorization denials communicated to caller? | MISSING |
| Audit Trail | What decision_ledger entries should record Human Gate state? | MISSING |
| Expiration | Do Human Gate approvals expire? If so, must SealGovernanceGate check? | MISSING |
| Scope Matching | Must Human Gate authorization scope match seal scope? | MISSING |

---

## 6. Findings and Recommendations

### 6.1 Root Cause

The specification R04-B states:

> "Current Authorization must be validated at execution time from Human Gate"

But does NOT specify:

1. **Request Identification**: How SealGovernanceGate.execute() knows which Human Gate request to check
2. **Submission Timing**: When the Human Gate request is created (before execution or during execute())
3. **Synchronization Model**: Whether execution waits for Human Gate decision or fails immediately if not pre-approved

### 6.2 Implementation Blockers

Cannot implement "Current Authorization retrieval from Human Gate" without clarifying:

- **Option A (pre-approval)**: Design requires Human Gate approval before execute() is called
  - Request ID must be passed as parameter: `execute(message, human_gate_request_id=...)`
  - Implementation: `get_state(human_gate_request_id) == "APPROVED"`

- **Option B (on-demand)**: Design requires async approval after execute() is called
  - Request ID generated internally: `execution_id = f"EXEC_{timestamp}_{uuid}"`
  - Implementation: `submit(request_id)` → return "pending" → `get_state(execution_id) == "APPROVED"` on retry
  - Requires two-phase execution or polling mechanism

- **Option C (embedded)**: Design couples authorization metadata to action parameters
  - Request ID passed with metadata: `execute(message, authorization={request_id:..., expires_at:...})`
  - Implementation: Validation + `get_state(request_id) == "APPROVED"`
  - Requires expiration and scope validation logic

---

## 7. Next Steps (For Human Gate Decision)

This investigation identifies the missing specification. Implementation cannot proceed without clarification:

**Question for Human Gate**: Which of Options A/B/C (or other specification) defines how SealGovernanceGate should retrieve and validate Human Gate's Current Authorization?

Once specified, implementation path is clear:

```python
# Pseudo-code for any option
def _current_authorization_check(self, request_id, action):
    # Step 1: Retrieve current state
    state = phi_os.human_gate.get_state(request_id)
    
    # Step 2: Validate authorization
    if state != "APPROVED":
        return False, f"Human Gate state: {state}", None
    
    # Step 3: (Optional for Option C) Validate scope/expiration
    # ...
    
    # Step 4: Return authorization state from Human Gate
    auth_state = AuthorizationState(
        is_authorized=True,
        authority="human:gate_approval",  # External authority
        scope=current_scope,
        evidence={
            "human_gate_request_id": request_id,
            "human_gate_state": state,
            "checked_at": now,
            "action": action,
        },
        state_at=now,
        provenance="SealGovernanceGate._current_authorization_check()",
    )
    return True, "Human Gate current authorization valid", auth_state
```

---

## References

- Current Implementation: `governance/seal_governance_gate.py`
- Human Gate State Machine: `phi_os/human_gate.py`
- Phase C Completion Report (incorrect assessment): `docs/governance/PHASE_C_COMPLETION_REPORT_v1.0.md`
- Phase C Investigation: `docs/governance/PHASE_C_GOVERNANCE_GATE_INVESTIGATION_v0.1.md`
