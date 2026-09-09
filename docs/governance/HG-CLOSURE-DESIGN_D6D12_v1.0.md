# HG Decision Package: Central Runtime Loop Closure Design (D6-D12)

## Executive Summary

This document presents the normative design specification for establishing the **Central Runtime Loop** — the unified execution cycle connecting Commercial MoCKA data flow to Original MoCKA core governance, memory, and context layers.

**Status**: DESIGN REVIEW READY → Design/Planning Phase → Human Gate Submission (next stage)

**Audit Foundation**: Commercial ↔ Original MoCKA Integration Audit (A-D Phases COMPLETE)

**Principal Closure Gap**: E3 (Governance → Memory Binding) identified and design solution specified

---

## D6: Governance → Memory Binding (E3 Closure)

### Problem Statement

**Current State**: `policy.evaluate()` returns `{decision, confidence, reason}` dict, but:
1. Return value DISCARDED at /collect endpoint (app.py:1062)
2. Relay decision NOT PERSISTED to events.db
3. MemoryContext.load() searches "%decision%" in events.db but finds nothing
4. **Result**: Governance decision unreachable to Memory layer

### Design Solution: CanonicalDecisionRecord

**Binding Mechanism**: Governance decision → TypedGovernanceDecisionEvent → events.db → MemoryContext reads

```python
# Type Definition (typing schema)
CanonicalDecisionRecord = {
    "canonical_id": "GD_{timestamp}_{hash}",  # Governance Decision ID
    "source_policy_id": "policy-v1",
    "source_event_id": "E{YYYYMMDD}_{NNN}",  # Idempotency anchor
    "governance_version": "2026-09-09",
    
    # Decision Core (immutable)
    "decision_status": str,  # "defer" | "accept_telemetry" | "reject" | "custom"
    "confidence": float,  # 0.0 to 1.0
    "reasoning": str,     # Free-form rule explanation
    
    # Authorization Separation (CRITICAL)
    "authorization_status": str,  # "PENDING_HUMAN_REVIEW" | "APPROVED" | "REJECTED"
    "authorizing_actor": str,     # "human:{name}" | "AI:{system}" | "SYSTEM"
    "authorization_timestamp": str,  # ISO 8601
    
    # Persistence Semantics
    "persistence_status": str,  # "WRITTEN" | "NOT_WRITTEN" | "WRITE_FAILED"
    "written_to_events_db": bool,
    "event_id_in_db": str | None,
    
    # Fail-Closed State Preservation
    "unknown_preservation": bool,  # Must remain true if ANY upstream state = UNKNOWN
    "not_proven_preservation": bool,  # Must remain true if ANY upstream execution = NOT_PROVEN
}
```

### Idempotency

**Problem**: Same policy evaluation could be called multiple times from same event, creating duplicate records.

**Solution**: Keyed by `source_event_id + governance_version`

```
IF (source_event_id, governance_version) exists in events.db:
  SKIP write (already persisted)
ELSE:
  INSERT CanonicalDecisionRecord
```

### Integration Points

1. **RelayKernel.ingest() → policy.evaluate()**:
   - Capture return value (currently discarded)
   - Wrap in CanonicalDecisionRecord
   - Include source_event_id for idempotency

2. **MCPBridge (currently dead code)**:
   - Uncomment and activate
   - Call: `_write_governance_decision(kernel_result["policy"])`
   - Persist via process_buffered_event()

3. **/collect endpoint (app.py)**:
   - Line 1062: Do NOT discard relay_kernel.ingest() return value
   - Extract policy dict
   - Create CanonicalDecisionRecord
   - Write to events.db via EventBuffer

### Fail-Closed Rules for D6

1. **UNKNOWN Preservation**: If any upstream element (event_gate validation, policy input) = UNKNOWN, decision_record.unknown_preservation = true. DO NOT convert UNKNOWN to default.

2. **NOT_PROVEN Preservation**: If execution path NOT_PROVEN, do NOT assume "normal completion" state. Mark authorization_status = PENDING_HUMAN_REVIEW.

3. **Persistence Failure Blocks Execution**: If write to events.db FAILS, return {status: "governance_bind_failed"} to caller. DO NOT continue with action_router.route().

4. **Missing Authorization Blocks Action**: If authorization_status = PENDING, do NOT route to STORE_EVENT/DROP_EVENT/QUEUE_EVENT. Escalate to Human Gate.

---

## D7: Memory → Context Flow (E4 Continuation)

### Design: MemoryContext Loads Governance Decisions

**Current MemoryContext.load()**:
- Reads events.db for "%decision%" in why_purpose
- Creates DecisionRecord objects
- Stores in architecture_decisions list

**Enhancement**: Explicit typing for Governance Decisions

```python
def _load_governance_decisions(self, limit=10) -> None:
    # Query by typed event structure (not string search)
    rows = conn.execute(
        "SELECT event_id, what_type, governance_decision_json FROM events "
        "WHERE what_type = 'governance_decision_event' "
        "AND event_id NOT IN (already_loaded_set) "
        "ORDER BY rowid DESC LIMIT ?",
        (limit,)
    ).fetchall()
    
    for r in rows:
        decision_record = json.loads(r["governance_decision_json"])
        self.governance_decisions.append({
            "event_id": r["event_id"],
            "decision_status": decision_record["decision_status"],
            "authorization_status": decision_record["authorization_status"],
            "confidence": decision_record["confidence"],
            "reasoning": decision_record["reasoning"],
            "timestamp": r["event_id"][:12],
        })
```

### Integration: Context Assembly

**WorkingContext** (operating context for AI execution):

```python
class WorkingContext:
    def __init__(self, memory: MemoryContext):
        self.memory = memory
        self.five_w1h = memory.five_w1h
        self.recent_decisions = memory.governance_decisions[:5]  # Latest 5
        self.authorized_actions = [
            d for d in self.recent_decisions
            if d["authorization_status"] == "APPROVED"
        ]
        self.pending_reviews = [
            d for d in self.recent_decisions
            if d["authorization_status"] == "PENDING_HUMAN_REVIEW"
        ]
```

### Critical Separation: Memory ≠ Authorization

**MUST ENFORCE**:
- Memory provides CONTEXT (what was decided, why)
- Memory DOES NOT imply AUTHORIZATION (decision is approved)
- Authorization status is EXPLICIT field
- AI execution checks authorization_status BEFORE acting

### Fail-Closed Rules for D7

1. **Missing Governance Decision**: If Memory has no governance_decisions, WorkingContext.authorized_actions = []. Do NOT default to "accept".

2. **UNKNOWN Preservation in Context**: If any governance_decision.unknown_preservation = true, do NOT include in authorized_actions. Mark as pending_clarification.

3. **Memory Load Failure**: If events.db query FAILS, do NOT continue. Set working_context = None, escalate to Human Gate.

---

## D8-D9: Outcome → New Event → Re-entry (E5-E6 Loop)

### Design: Closed-Loop Governance Enforcement

**E5 (Outcome)**: AI executes approved action

**E6 (New Event)**: Action result recorded

**E6a (Re-entry)**: New event re-enters /collect → Relay → Governance cycle

### Implementation: No Governance Bypass

```
Action executed
  ↓
Outcome recorded: {action_id, action_type, result_code, result_data}
  ↓
CREATE new_event = {
    "what_type": "action_outcome_event",
    "why_purpose": f"Outcome of approved action {action_id}",
    "who_actor": "AI:{system}",
    "where_component": "outcome_recorder",
    "raw": outcome
}
  ↓
POST /collect with new_event  ← Re-entry (E6a)
  ↓
/collect → EventBuffer → events.db → Relay.ingest() → policy.evaluate() → new governance decision
  ↓
Cycle repeats (Central Loop continues)
```

### Idempotency: Outcome Recording

**Problem**: Same action outcome could be POSTed multiple times (network retry, UI re-click).

**Solution**: Keyed by `action_id` in decision_record

```
IF action_id already in decision_ledger.decision_outcomes:
  SKIP (already processed)
ELSE:
  RECORD outcome
  GENERATE new governance decision
```

---

## D10: C1-C16 Mandatory Closure Conditions

**Status**: NORMATIVE REQUIREMENTS DEFINED, NOT YET VERIFIED (runtime evidence required)

### C1-C5: Identity & Persistence

- **C1**: CanonicalDecisionRecord has immutable canonical_id (GD_{timestamp}_{hash})
- **C2**: source_event_id + governance_version guarantee idempotency (no duplicate records)
- **C3**: Authorization status SEPARATE from decision status (not conflated)
- **C4**: Written to events.db with what_type='governance_decision_event' (typed, not string search)
- **C5**: MemoryContext reads typed governance_decision_event (not "%decision%" text search)

### C6-C10: Execution & Authorization

- **C6**: Governance decision initiates from policy.evaluate() (not manual writes)
- **C7**: Authorization status explicitly checked BEFORE action routing
- **C8**: Missing authorization → PENDING escalation to Human Gate (not default acceptance)
- **C9**: UNKNOWN preservation enforced at decision creation
- **C10**: NOT_PROVEN preservation enforced at execution boundary

### C11-C16: Loop Closure & Verification

- **C11**: Outcome → New Event → Re-entry cycle executes (E6a confirmed)
- **C12**: New event re-enters /collect endpoint (full cycle restart)
- **C13**: Re-entered event triggers new policy.evaluate() (no bypass)
- **C14**: Fail-Closed blocking rules enforced (persistence failure → escalation)
- **C15**: Human Gate decision recorded in decision_ledger BEFORE action execution
- **C16**: Loop re-entry happens within expected RT window (max 5sec from outcome record)

---

## D11: Seven Fail-Closed Safety Rules

### Rule 1: UNKNOWN → UNKNOWN
If any upstream state = UNKNOWN, decision_record.unknown_preservation = true.
DO NOT convert to default or probabilistic estimate.

### Rule 2: NOT_PROVEN → NOT_PROVEN
If any execution path = NOT_PROVEN, mark authorization_status = PENDING_HUMAN_REVIEW.
DO NOT assume normal completion.

### Rule 3: Persistence Failure → Block
If write to events.db FAILS, return {status: "governance_bind_failed"}.
DO NOT retry silently. Escalate to Human Gate.

### Rule 4: Missing Decision → Block
If policy.evaluate() returns NO decision dict, action_router MUST NOT route.
Set authorization_status = NOT_APPLICABLE. Escalate.

### Rule 5: Missing Context → Block
If MemoryContext.load() FAILS (events.db unavailable), working_context = None.
DO NOT create synthetic context. Escalate to Human Gate.

### Rule 6: Invalid source_id → Block
If source_event_id NOT FOUND in events.db, idempotency check FAILS.
Mark as UNVERIFIED. Escalate to Human Gate.

### Rule 7: Authorization Record ≠ Execution Authorization
Authorization record in decision_ledger MUST be written BEFORE action execution.
Execution begins ONLY after record confirmed in persistent storage.
DO NOT execute pending authorization.

---

## D12: Human Gate Decision Package Structure

### Five Decision Points

**DP-1: Design Adoption**
Question: "ADOPT the Central Runtime Loop Closure Design (D6-D12) as normative architecture for loop establishment?"
Options: ADOPT / ADOPT_WITH_CONDITIONS / HOLD / REJECT

**DP-2: Implementation Planning Authorization**
Question: "AUTHORIZE Implementation Planning Phase to detail C1-C16 verification strategy?"
Depends on: DP-1 = ADOPT or ADOPT_WITH_CONDITIONS
Options: AUTHORIZE / HOLD / REJECT

**DP-3: Implementation Authorization**
Question: "AUTHORIZE code changes to RelayKernel, /collect endpoint, MCPBridge, MemoryContext.load()?"
Depends on: DP-2 = AUTHORIZE
Options: AUTHORIZE / HOLD / REJECT

**DP-4: Runtime Evidence Collection Authorization**
Question: "AUTHORIZE deployment to test environment with instrumentation for C1-C16 verification?"
Depends on: DP-3 = AUTHORIZE
Options: AUTHORIZE / HOLD / REJECT

**DP-5: Loop Closure Verification Judgment**
Question: "VERIFY Central Runtime Loop closure based on collected evidence (C1-C16 runtime confirmation)?"
Depends on: DP-4 = AUTHORIZE + evidence collected
Options: VERIFIED / HOLD / REQUIRE_REDESIGN

### Package Contents

1. **Design Specification** (D6-D12 above)
2. **Audit Evidence** (A-D Phase findings from Commercial ↔ Original Integration Audit)
3. **Closure Conditions** (C1-C16 explicit enumeration)
4. **Fail-Closed Rules** (Rule 1-7, safety enforcement)
5. **Implementation Plan** (TBD post-DP2 approval)
6. **Verification Strategy** (TBD post-DP2 approval)

### Decision Record Format

```json
{
  "decision_id": "DC_CLOSURE_DESIGN_001",
  "decision_package_title": "Central Runtime Loop Closure Design (D6-D12)",
  "submitted_at": "2026-09-09T...",
  "submitted_by": "Claude Haiku 4.5",
  
  "decision_points": [
    {
      "dp_id": "DP-1",
      "question": "ADOPT Central Runtime Loop Closure Design?",
      "decision": "PENDING",
      "authorizing_actor": "きむら博士 (Human Gate)",
      "decision_timestamp": null,
      "reasoning": null,
      "alternatives_considered": [
        "REJECT: Redesign loop architecture (HIGH EFFORT)",
        "HOLD: Collect additional evidence (DELAY)",
        "ADOPT_WITH_CONDITIONS: Specify pre-deployment verifications"
      ]
    }
  ],
  
  "design_narrative": "See D6-D12 specification above",
  "audit_reference": "E20260701_COMMERCIAL_MOCKA_ORIGINAL_MOCKA_INTEGRATION_AUDIT",
  "principal_closure_gap": "E3: Governance → Memory Binding",
  "proposed_solution": "CanonicalDecisionRecord + typed events.db records",
  "fail_closed_enforcement": "7 safety rules + C1-C16 mandatory conditions"
}
```

---

## Design/Planning Phase Completion Checklist

Before submission to Human Gate, Design/Planning must confirm:

- [x] A-D Phase audit complete (Commercial ↔ Original Integration)
- [x] Principal closure gap (E3) identified and design solution specified
- [x] D6-D12 specification documented with NORMATIVE language (not provisional)
- [x] C1-C16 closure conditions enumerated (not verified, but defined)
- [x] D11 fail-closed rules specified (7 safety enforcement mechanisms)
- [x] D12 Human Gate Decision Package structure defined
- [ ] Implementation Plan (TBD post-DP2)
- [ ] Runtime Verification Strategy (TBD post-DP2)
- [ ] Code path review for RelayKernel.ingest() return value capture
- [ ] Events.db schema extension for governance_decision_event type

**Current Status**: Design/Planning COMPLETE. Ready for Human Gate Decision Package submission.

---

## References

- **Audit Foundation**: Commercial MoCKA ↔ Original MoCKA Integration Audit (A-D Phases)
- **Principal Gap**: E3 Closure identified at Governance → Memory binding
- **Loop Definition**: 8-edge Central Runtime Loop (Event→Record→Governance→Memory→Context→AI→Outcome→New Event→Re-entry)
- **Fail-Closed Philosophy**: UNKNOWN and NOT_PROVEN states preserved throughout; persistence failures block execution

---

**Document Version**: v1.0
**Finalized**: 2026-09-09
**Status**: Design/Planning Complete → Human Gate Decision Package Ready
