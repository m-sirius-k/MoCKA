# Phase C Current Authorization Evidence v1.0

**Scope**: Identify existing authority source for Current Authorization in Phase C implementation

**Constraint**: R04 Authorization Boundary is finalized. Investigation is evidence-gathering, not design choice.

**Date**: 2026-09-02

---

## R04 Confirmed Boundary (Immutable)

```
Approval (GL7) → Current Authorization Check → Authorization Result → Conditional Execution
```

Current Implementation Separation:
- Approval: `ExecutionGovernanceEngine.pre_execution_check()` ✓
- Current Authorization Check: `_current_authorization_check()` ✓
- Execution: `subprocess.run(anchor_update.py)` ✓

---

## Current Implementation Analysis

### M3: Current Authorization Check (seal_governance_gate.py:87-138)

```python
def _current_authorization_check(self, approval_state: dict, action: dict) 
    -> tuple[bool, str, AuthorizationState | None]:
    """
    Validates that authorization context hasn't changed since approval.
    """
```

**Implementation Actions**:

1. Evidence validation:
   ```python
   if approval_state is None or not approval_state:
       return False, "No prior approval state available..."
   ```
   Evidence source: `approval_state` parameter (dict)

2. Approval state validity:
   ```python
   if not approval_state.get("approved"):
       return False, "Approval state not valid at execution time"
   ```
   Checks: `approval_state.approved == True`

3. Scope validation:
   ```python
   stored_scope = approval_state.get("scope", [])
   current_scope = action.get("scope", [])
   if stored_scope != current_scope:
       return False, f"Scope changed: {stored_scope} → {current_scope}"
   ```
   Compares: Prior scope vs. Current action scope

4. Max changes validation:
   ```python
   stored_max = approval_state.get("expected_max_changes")
   current_max = action.get("expected_max_changes")
   if stored_max != current_max:
       return False, f"Max changes limit changed: {stored_max} → {current_max}"
   ```
   Compares: Prior max_changes vs. Current action max_changes

5. Authority assignment:
   ```python
   authority = "system:seal_governance_gate"
   ```
   **Note**: Hardcoded self-reference

6. Return AuthorizationState:
   ```python
   auth_state = AuthorizationState(
       is_authorized=True,
       authority=authority,
       scope=current_scope,
       evidence={
           "approval_time": approval_state.get("approval_time"),
           "checked_at": now,
           "action": action,
       },
       state_at=now,
       provenance="SealGovernanceGate.current_authorization_check()",
   )
   ```

### M2: Approval State Persistence (seal_governance_gate.py:80-86)

```python
def __init__(self, repo_root: Path, decision_ledger_path: Path):
    self.repo_root = Path(repo_root)
    self.decision_ledger_path = Path(decision_ledger_path)
    self.governance = ExecutionGovernanceEngine(repo_root=self.repo_root)
    self._last_approval_state = None  # <- Instance attribute
```

**Storage**: In-memory instance attribute `_last_approval_state`

**Initialization**: `None` at instance creation

**Mutation Points**:
```python
# Line 190 (execute method)
self._last_approval_state = current_approval_state

# Line 204 (execute method)
self._last_approval_state = current_approval_state
```

### State Initialization (seal_governance_gate.py:176-186)

```python
current_approval_state = {
    "approved": True,
    "approval_time": change_start,  # Execution time
    "scope": action.get("scope"),
    "expected_max_changes": action.get("expected_max_changes"),
}

is_authorized, auth_reason, auth_state = self._current_authorization_check(
    self._last_approval_state or current_approval_state,  # <- Falls back to current
    action
)
```

**Logic**:
1. If `_last_approval_state` exists → use it
2. If `_last_approval_state` is None → use `current_approval_state`

**Result**: First call always passes authorization (no prior state to compare).

---

## Authority Source Tracing

### Question 1: Where does `approval_state` originate?

**Current Implementation**:
- Line 184-186: Constructed in-memory at execution time
- `approved=True` (hardcoded)
- `approval_time=change_start` (current timestamp)
- `scope/expected_max_changes` (from current action)

**Authority Source**: SELF-CONSTRUCTED from current action context

**Status**: ✗ Not retrieved from external authority

### Question 2: What is the relationship between GL7 approval and _last_approval_state?

**GL7 Output** (ExecutionGovernanceEngine.pre_execution_check):
```python
approval.approved: bool
approval.reason: str
approval.dry_run.aborts: list
```

**_last_approval_state Structure**:
```python
{
    "approved": bool,
    "approval_time": str (ISO timestamp),
    "scope": list,
    "expected_max_changes": int
}
```

**Connection**: ✗ MISSING
- GL7 result is checked separately
- _last_approval_state is NOT derived from GL7
- No link between GL7 approval ID and authorization state

### Question 3: Is there a request_id or tracking ID?

**In Current Implementation**: 
- `execution_id` = f"EXEC_{datetime}_{uuid}" (line 143)
- Generated per execute() call
- Used for audit events, not authorization

**Tracking in _last_approval_state**: ✗ NO request_id field

**Authorization State Linking**: 
```python
auth_state = AuthorizationState(
    evidence={
        "approval_time": approval_state.get("approval_time"),
        "checked_at": now,
        "action": action,
    },
    ...
)
```
Evidence contains timestamps and action, but no persistent request_id.

---

## Scope/Max Changes Re-validation Path

### Current Flow (Multiple Calls)

**First Call**:
```
execute(scope=["data"], max_changes=10)
    ↓
_current_authorization_check(approval_state=None, action={scope:["data"], max_changes:10})
    ↓ (Line 185: Falls back to current_approval_state)
current_approval_state = {approved: True, scope: ["data"], max_changes: 10}
    ↓
_last_approval_state = current_approval_state
    ↓
Authorization: PASS
```

**Second Call (Different Scope)**:
```
execute(scope=["structural"], max_changes=10)
    ↓
_current_authorization_check(approval_state={...prior state...}, action={scope:["structural"], max_changes:10})
    ↓
scope check: ["data"] != ["structural"]
    ↓
Authorization: FAIL with "Scope changed"
```

**Validation Mechanism**: ✓ PRESENT (line 108-110)

**Re-validation at Execution Time**: ✓ YES (called before seal execution, line 184-186)

---

## Known vs. Unknown in Current Implementation

### Known (Implemented, Verified)

| Aspect | Status | Evidence |
|---|---|---|
| Separate Approval/Authorization events | ✓ | APPROVAL_PASSED/DENIED, AUTHORIZATION_PASSED/DENIED recorded |
| scope/max_changes re-validation | ✓ | Lines 107-116: Comparison logic |
| Per-execution tracking | ✓ | execution_id per call |
| Scope change detection | ✓ | Test Case 3: "Scope changed" message |
| Max changes change detection | ✓ | Test Case 4: "Max changes limit changed" message |

### Unknown (Not Traced to Authority Source)

| Aspect | Status | Question |
|---|---|---|
| Authority source for "approved" state | UNKNOWN | Where does _last_approval_state.approved=True originate? |
| Request ID persistence | UNKNOWN | Should _last_approval_state have associated request_id field? |
| GL7-to-Authorization linking | UNKNOWN | Should GL7 approval be linked to _last_approval_state? |
| Inter-session persistence | UNKNOWN | Should _last_approval_state survive across sessions/restarts? |
| Current State Retrieval at Execution | UNKNOWN | Should _last_approval_state be re-retrieved from external source before checking? |
| Authorization Expiration | UNKNOWN | Does _last_approval_state expire? If so, how is expiration tracked? |

---

## Critical Finding: Missing Authority Retrieval

### Current Implementation Pattern

```python
# In-memory state, never re-retrieved from external source
self._last_approval_state = None  # Initialized

# In first execute() call:
_current_authorization_check(
    self._last_approval_state or current_approval_state,
    action
)
```

**Behavior**:
- State is constructed in-memory at execution time
- State is stored in instance variable
- State is NOT retrieved from persistent/external source
- State is NOT validated against Human Gate records
- State is NOT connected to request_id tracking

### What "Current Authorization" Currently Means

In R04 boundary terms:

**What IS checked**:
1. Parameter consistency (scope, max_changes)
2. Evidence of prior approval (approval_state exists)
3. Approval flag (approved=True)

**What IS NOT checked**:
1. External Human Gate current state
2. Authorization expiration
3. Request ID tracking
4. Authority source validation
5. Persistent state retrieval

---

## Authority Source Options (Evidence-based)

### Option 1: phi_os.human_gate (Existing Implementation)

**Evidence**:
- File exists: `phi_os/human_gate.py`
- API available: `get_state(request_id: str) -> str | None`
- Storage available: `data/mocka_events.db` (SQLite)
- States available: PENDING, APPROVED, REJECTED, EXPIRED, CANCELED

**Connection Status**: ✗ NOT CONNECTED to SealGovernanceGate

**Required for Integration**:
- UNKNOWN: Should _last_approval_state be retrieved from Human Gate?
- UNKNOWN: What is the request_id for linking?
- UNKNOWN: When should retrieval happen (at each execute() call)?

### Option 2: decision_ledger.jsonl (Existing Storage)

**Evidence**:
- Path: `data/decisions/decision_ledger.jsonl`
- Schema supports: approval events, authorization events
- Current implementation writes to it

**Connection Status**: ✗ NOT USED for reading current authorization

**Required for Integration**:
- UNKNOWN: Should _last_approval_state be read from decision_ledger history?
- UNKNOWN: Should latest AUTHORIZATION_PASSED event serve as current state?
- UNKNOWN: How to query for "current valid authorization"?

### Option 3: GL7 Direct Connection

**Evidence**:
- File: `structural/execution_governance.py`
- Already called: Line 149 in execute()
- Returns: ApprovalResult with scope information

**Connection Status**: ✓ PARTIALLY CONNECTED
- GL7 is called for Approval check
- GL7 approval is NOT used for Current Authorization state

**Required for Integration**:
- UNKNOWN: Should GL7 result be used to populate _last_approval_state?
- UNKNOWN: Should GL7 scope be source of truth for Current Authorization scope?

---

## Execution-Time Re-validation: Current State

### When is _current_authorization_check called?

```python
# seal_governance_gate.py:184-186
is_authorized, auth_reason, auth_state = self._current_authorization_check(
    self._last_approval_state or current_approval_state,
    action
)
```

**Timing**: ✓ YES, happens before seal execution (line 215-218)

### What state is being validated?

**_last_approval_state**:
- Stored in instance variable
- From previous execute() call (or None)
- NOT re-retrieved from any source at this point
- NOT refreshed to check for changes

**Current Action**:
- Passed as parameter to execute()
- Used as comparison baseline

### Re-validation Completeness

| Validation | Done? | Against What? |
|---|---|---|
| Parameter unchanged | ✓ | Stored _last_approval_state |
| Approval flag still True | ✓ | Stored _last_approval_state |
| Evidence exists | ✓ | Stored _last_approval_state |
| External authorization current | ✗ | UNKNOWN - not checked against Human Gate |
| Authorization not expired | ✗ | UNKNOWN - no expiration tracking |
| Request ID valid | ✗ | UNKNOWN - no request_id field |

---

## Summary: Where Authorization Currently Comes From

### Current Authority Source for "approved"

**Source**: Self-constructed from current execution context

```python
current_approval_state = {
    "approved": True,  # <- Hardcoded True
    "approval_time": change_start,  # <- Execution time
    "scope": action.get("scope"),  # <- From parameter
    "expected_max_changes": action.get("expected_max_changes"),  # <- From parameter
}
```

**Authority Chain**: 
```
SealGovernanceGate.execute()
    ↓
    Constructs current_approval_state with approved=True (no question, no check)
    ↓
    Uses this as "current authorization" 
    ↓
    GL7 approval is separate check, not linked
    ↓
    _last_approval_state stores this constructed state
```

### Missing Authoritative Source

The R04 Current Authorization Check requires:

> "Execute must verify Human Gate is currently authorizing this action"

**Current Implementation**: 
- Does NOT contact Human Gate
- Does NOT check human_gate_events table
- Does NOT validate against phi_os.human_gate.get_state()
- Does NOT link to request_id

**What Should Happen** (R04-compliant):
- Retrieve current authorization state from authoritative source (UNKNOWN which)
- Validate scope/max_changes against that source
- Verify authorization is not expired (if applicable)
- Execute only if all checks pass

---

## Investigation Conclusion

**Status**: R04 Authorization Boundary structure is present. Scope/Max Changes re-validation is implemented.

**Gap**: Authority source for Current Authorization state is not traced to external validation system.

**Questions for Clarification**:

1. Should _last_approval_state be populated from phi_os.human_gate?
2. Should request_id be added to track authorization requests?
3. Should execution re-retrieve authorization state from persistent source each time?
4. Should GL7 approval be linked to authorization state tracking?
5. Is current "approved=True" hardcoding intentional, or should it be queried?

**Evidence Status**: DOCUMENTED AS UNKNOWN - Ready for Human Gate specification review.
