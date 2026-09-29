# IP-005: Execution Path Audit Report
## Date: 2026-09-29
## Status: HG Design Review HOLD

---

## AUDIT FINDINGS

### Critical Discovery: CODE EXISTS ≠ CODE CALLED ≠ CONNECTED

During pre-implementation read-only audit of IP-005 prerequisites, the following three connection paths were traced:

#### A. Human Gate → existing Authorization → runtime_scope

**Expected Flow:**
```
Human Gate
  ↓ (decision result)
existing Authorization (phi_os/context/execution_context.py:ExecutionGate.run())
  ↓ (policy check result)
runtime_scope (check against HG-approved scope)
```

**Actual Trace Result:**
- ExecutionGate class: EXISTS in execution_context.py
- ExecutionGate.run() method: IMPLEMENTED
- Callers of ExecutionGate.run(): NOT FOUND in traced path
- Function phl_build_execution_context() in caliber/chat_pipeline/mocka_caliber_server.py: CALLS execution context functions but does NOT call ExecutionGate.run()
- **Status: NOT CONNECTED**

#### B. Orchestra → HAB :5010

**Expected Flow:**
```
Orchestra (gateway/gateway.py:5010)
  ↓ (execution request)
event_gate.process_event() (phi_os/event_gate.py)
  ↓ (event logged)
HAB decision layer
```

**Actual Trace Result:**
- event_gate.process_event(): EXISTS in phi_os/event_gate.py
- Callers in gateway/: NOT FOUND
- gateway.py imports event_gate: NO
- gateway.py calls process_event(): NO
- **Status: NOT CONNECTED**

#### C. Authorization result → HAB request

**Expected Flow:**
```
Authorization decision (APPROVED/REJECTED/DEFERRED)
  ↓ (propagate)
Human Gate state transition
  ↓ (signal)
HAB request processing
```

**Actual Trace Result:**
- human_gate.py (state machine): EXISTS
- human_gate.get_state(): CALLABLE but not called from traced execution path
- Propagation path from Authorization decision to HAB request: NOT FOUND
- **Status: NOT CONNECTED**

---

## CLASSIFICATION

### Code Existence vs. Execution

| Component | Code | In Path | Called | Status |
|-----------|------|---------|--------|--------|
| ExecutionGate (execution_context.py) | ✓ EXISTS | ✓ FOUND | ✗ NOT CALLED | CONFIGURED |
| event_gate.process_event() | ✓ EXISTS | ✓ FOUND | ✗ NOT CALLED | CONFIGURED |
| human_gate.py (state machine) | ✓ EXISTS | ✓ FOUND | ✗ NOT CALLED | CONFIGURED |
| **A→B→C Connection** | - | - | - | **NOT CONNECTED** |

### Important Distinction

```
NOT FOUND (current traced path)
    ≠
ABSENT (confirmed nonexistent anywhere in codebase)
```

**This audit confirms NOT FOUND only for the specifically traced paths (A, B, C).**
**It does not confirm ABSENT for all possible paths in the repository.**

---

## IMPLICATIONS FOR IP-005

### Original Approval

IP-005 Plan (HG-approved) states:
```
"Establish direct interface between Orchestra execution requests 
and Human Authority Boundary (HAB) decision layer, 
ensuring all Orchestra-initiated execution requires explicit 
HAB authorization before proceeding to AI runtime."

Constraint: Use existing Authorization mechanism (no new scheme)
```

### Current Finding

Three critical connection paths required for "existing Authorization reuse" 
are NOT CONNECTED in the current codebase.

If IP-005 implementation proceeds as planned, it will create:
```
NEW connection paths (A/B/C)
    instead of
EXISTING path reuse
```

This represents a **design change**, not an implementation detail.

---

## RECOMMENDED NEXT STEP FOR HUMAN GATE

This finding requires HG review and decision:

### OPTION 1: Continue IP-005 as Planned
- Keep current plan
- Implement new connection paths (A/B/C)
- Acknowledge scope change from "reuse existing" → "create new"

### OPTION 2: Redefine IP-005 Scope
- Update IP-005 Plan to reflect "new connection path construction"
- Revise scope boundaries
- Obtain re-approval with updated Plan

### OPTION 3: Extended Investigation
- Search for alternative existing call paths (beyond A/B/C)
- Confirm whether ExecutionGate/event_gate are actually unused
- Validate assumption that ABSENT ≠ NOT FOUND in this context

---

## AUDIT CONCLUSION

**Finding Confirmed:**
- Traced execution paths (A, B, C) for "existing Authorization reuse" are NOT CONNECTED
- Code components exist but are not wired into active execution paths
- Current IP-005 Plan assumes connection that does not exist

**Status: IP-005 = HG Design Review HOLD**

No code changes have been made pending HG decision.

---

## GOVERNANCE REFERENCES

- IP-007: CLOSED / STATIC VERIFIED
- IP-005: HOLD / PRE-IMPLEMENTATION AUDIT
- Authority: HG Design Review (decision required)
