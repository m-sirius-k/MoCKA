# Disposition Mapping Design Investigation v1.0

## Overview
Investigation of Disposition State storage as Payload Metadata approach (NOT State Machine expansion).

Date: 2026-08-23  
Status: INVESTIGATION (design-only, no implementation)  
Scope: Semantic metadata storage, state machine boundary enforcement, decision record integration

---

## 1. The Disposition Problem

### 1.1 What is "Disposition"?
**Definition**: The semantic meaning or proposed handling of a decision/contradiction/event after resolution.

**Examples**:
- Decision made: "API deprecation approved"
  - Disposition: "migrate_customers" (what should happen next)

- Contradiction resolved: "Evidence mismatch clarified"
  - Disposition: "investigate_impact" (investigation suggested)

- TIC alert raised: "Performance degradation detected"
  - Disposition: "monitor_closely" (surveillance recommended)

### 1.2 Disposition ≠ State Machine State
**Critical Distinction**:
- **State Machine State** (Phase 2 LOCKED): PENDING | APPROVED | REJECTED | EXPIRED | CANCELED
  - These are system states (formal status)
  - Managed by Human Gate state machine
  - Never to be modified in Phase 3

- **Disposition** (NEW in Phase 3): monitor | investigate | escalate | hold | resolve
  - These are semantic intentions (what to do next)
  - Separate from state machine
  - Stored as metadata in decision/event payload

### 1.3 Why Separate Disposition from State Machine?
**Reason**: Preserve Phase 2 LOCKED guarantee

- Phase 2: State machine confirmed and approved (commit 4512b71c1)
- If we add disposition as a state → we're modifying the state machine
- MoCKA governance principle: Phase 2 decisions are LOCKED

**Solution**: Store disposition as METADATA, not as STATE

```
Human Gate State Machine (LOCKED, Phase 2):
  decision.state = PENDING | APPROVED | REJECTED | EXPIRED | CANCELED
  
Disposition Metadata (NEW, Phase 3):
  decision.payload.disposition = monitor | investigate | escalate | ...
  ↑ This is metadata, NOT state
```

---

## 2. Disposition Semantic Model

### 2.1 Disposition Values (Enumeration)

**Core Disposition Set**:
1. **monitor** — Continue surveillance, no immediate action needed
   - Used when: Decision approved but risk remains
   - Example: "Feature flagged for A/B test, monitor conversion rate"

2. **investigate** — Research required before next action
   - Used when: Incomplete information or contradictions
   - Example: "Contradiction detected, investigate which evidence is correct"

3. **escalate** — Promote to higher authority
   - Used when: Current decision maker lacks authority
   - Example: "Security patch required, escalate to ops team"

4. **hold** — Pause, await external condition
   - Used when: Decision depends on future event
   - Example: "Await Q4 budget approval before implementing"

5. **resolve** — Complete, no further action needed
   - Used when: Decision executed and verified
   - Example: "Bug fixed and verified in production"

6. **defer** — Move to future review cycle
   - Used when: Not blocking, can be revisited later
   - Example: "Performance optimization deferred to Phase 5"

### 2.2 Disposition Lifecycle
```
Decision APPROVED
    ↓
Assign disposition = "monitor" (default)
    ↓
[Monitor evidence accumulates]
    ↓
IF [evidence changes] → disposition = "investigate"
    ↓
[Investigation complete via Orchestration Adapter]
    ↓
Disposition update → "escalate" | "resolve" | "defer"
    ↓
[Human Gate reviews disposition]
    ↓
Final decision on disposition recorded
```

### 2.3 Disposition vs Decision Outcome
**Subtle but Important Difference**:

```
Decision: "Component X deprecation approved"
State: APPROVED (formal, state machine)
Disposition: "escalate" (semantic, metadata)
  ↓
Meaning: The component X deprecation is approved (formal)
         BUT stakeholders need escalation to migrate (semantic guidance)
```

---

## 3. Payload Metadata Storage Design

### 3.1 Storage Location: Decision Ledger
**Where**: `data/decisions/decision_ledger.jsonl`
**What changes**: ADD new field to schema

**BEFORE (current)**:
```json
{
  "decision_id": "DC_20260823_001",
  "title": "...",
  "context": "...",
  "alternatives": [...],
  "decision": "...",
  "rationale": "...",
  "impact": "...",
  "approved_by": "...",
  "approved_at": "...",
  "status": "Active"
}
```

**AFTER (with disposition)**:
```json
{
  "decision_id": "DC_20260823_001",
  "title": "...",
  "context": "...",
  "alternatives": [...],
  "decision": "...",
  "rationale": "...",
  "impact": "...",
  "approved_by": "...",
  "approved_at": "...",
  "status": "Active",
  
  "disposition": {
    "value": "investigate",
    "reason": "Contradiction detected, requires verification",
    "assigned_at_utc": "2026-08-23T12:34:56Z",
    "assigned_by": "human_gate_session_xyz",
    "last_updated_at_utc": "2026-08-23T12:34:56Z",
    "expected_review_by": "2026-08-24T12:34:56Z"
  }
}
```

### 3.2 Metadata Field Definition
**New field**: `decision.disposition` (object, optional)

```json
{
  "disposition": {
    "value": "string, one of: monitor|investigate|escalate|hold|resolve|defer",
    "reason": "string, 50-200 chars, why this disposition?",
    "assigned_at_utc": "RFC3339 timestamp",
    "assigned_by": "string, user/session ID",
    "last_updated_at_utc": "RFC3339 timestamp",
    "expected_review_by": "RFC3339 timestamp or null",
    "related_action_id": "optional reference to TODO/task",
    "notes": "optional, for long-form explanation"
  }
}
```

### 3.3 Immutability Constraints
**Disposition is APPEND-ONLY** (like decision_ledger itself):
- Once recorded, disposition.value is NEVER changed
- Updates create NEW entry with disposition revision history
- History preserved for audit trail

**Design**: If disposition needs to change:
```json
[ENTRY 1]
{
  "decision_id": "DC_20260823_001",
  "disposition": {"value": "investigate", "assigned_at": "..."},
  "version": 1
}

[ENTRY 2]
{
  "decision_id": "DC_20260823_001",
  "disposition": {"value": "resolve", "assigned_at": "...", "supersedes_version": 1},
  "version": 2
}
```

**Query Latest**: version=MAX(version) for each decision_id

### 3.4 Storage NOT in State Machine
**CRITICAL BOUNDARY**:
```
Human Gate State Machine (app.py state={PENDING, APPROVED, REJECTED, ...}):
  ✓ Remains LOCKED
  ✗ Disposition NOT stored here
  
Decision Ledger Payload (data/decisions/decision_ledger.jsonl):
  ✓ Disposition STORED here
  ✓ As metadata, not state
```

---

## 4. Disposition Mapping to Actions

### 4.1 Disposition → Orchestration Trigger
**Orchestration Adapter reads disposition**:

| Disposition | Triggered Action | Agents | Urgency |
|---|---|---|---|
| monitor | observation_continues | TIC Layer 1 | low |
| investigate | auto_orchestration | claude + perplexity | high |
| escalate | escalation_notification | notify_admin | critical |
| hold | wait_for_signal | none | low |
| resolve | satisfaction_confirmation | none | low |
| defer | review_scheduled | none | medium |

**Key**: Disposition suggests action, but does NOT force it
- Human Gate reviews disposition
- Orchestration follows disposition guidance
- Final action is still manual approval

### 4.2 Disposition → Human Gate UI Display
**TODO_207** (TIC Layer 4 Human Gate UI) should display:
- Current decision state (APPROVED/PENDING/etc) ← state machine
- Proposed disposition (investigate/escalate/etc) ← metadata
- Disposition rationale (why this action?)
- Expected next step (by when?)

**UI Mock**:
```
[Decision DC_20260823_001]
Status: ✓ APPROVED (state machine)
Disposition: ⚠ INVESTIGATE (metadata)
  Reason: Contradiction detected between sources
  Expected review by: 2026-08-24 12:34:56Z
  
[Suggested Actions]
- Run automated investigation
- Schedule stakeholder review
- Monitor for conflicts
```

### 4.3 Disposition → Event Store Integration
**Events can have disposition too**:

- Event type: "contradiction_detected"
- Disposition: "investigate" (embedded in event payload)
- Similar to decision, but for events

```json
{
  "event_id": "E20260823_xxxxx",
  "title": "Contradiction Detected",
  "what_type": "contradiction",
  "disposition": {
    "value": "investigate",
    "reason": "Evidence conflict requires resolution"
  }
}
```

---

## 5. Strict Boundary Enforcement

### 5.1 WHAT DOES NOT CHANGE (Phase 2 LOCKED)
**Human Gate State Machine**:
- ✗ NO new states added
- ✗ NO state machine logic modified
- ✗ NO auto-state transitions
- Remains: PENDING | APPROVED | REJECTED | EXPIRED | CANCELED

**Decision Ledger Schema** (existing):
- ✗ NO existing fields modified or removed
- ✓ OK to ADD new optional fields (disposition)
- ✗ NO field semantics changed

**Decision Approval Logic** (existing):
- ✗ NO changes to what makes a decision approved
- ✗ NO changes to Human Gate authority

### 5.2 WHAT CAN CHANGE (New in Phase 3)
**New Payload Field**:
- ✓ ADD optional "disposition" field to decision records
- ✓ New field does NOT affect state machine behavior
- ✓ New field does NOT affect decision approval

**New Metadata Storage**:
- ✓ ADD disposition tracking to decision_ledger.jsonl
- ✓ ADD disposition history (version tracking)
- ✓ READ disposition via new query API

**New UI Display** (TODO_207):
- ✓ Display disposition alongside state
- ✓ Suggest disposition changes (not mandate)
- ✓ Display disposition history

### 5.3 Boundary Validation Checklist
Before implementation, verify:
- [ ] State machine unchanged: `human_gate.py` decision() method identical
- [ ] Decision schema backward compatible: all existing records still valid
- [ ] Disposition is optional: records without disposition field still valid
- [ ] No auto-state-transition: disposition never triggers state change
- [ ] No circular dependency: disposition references do NOT reference back to state

---

## 6. Integration with Phase 3 Components

### 6.1 Orchestration Adapter Integration
**Orchestration Adapter** (Design 1):
- Reads: disposition from related decision
- Example: "disposition=investigate" → triggers investigation
- Writes: orchestration result back to decision.payload

**Flow**:
```
Decision: "API deprecation approved"
  ↓ disposition=investigate
  ↓
Orchestration Adapter detects disposition
  ↓
Auto-trigger: "investigate_migration_impact"
  ↓
Result: "50% customers migrated, 50% at risk"
  ↓
Write back: decision.payload.orchestration_result = "..."
```

### 6.2 COMPARE Adapter Integration
**COMPARE Adapter** (Design 2):
- Detects: contradictions
- Assigns: disposition="investigate"
- Escalates to Human Gate: "Contradiction needs verification"

**Flow**:
```
COMPARE detects contradiction
  ↓
Create decision: "Resolve Evidence Conflict"
  ↓ disposition="investigate"
  ↓
Orchestration Adapter auto-triggers investigation
  ↓
Result feeds back to decision
  ↓
Disposition updated to: "resolve" | "escalate"
```

### 6.3 TIC Layer Integration
**TIC Layer 4** (TODO_207, Human Gate UI):
- Displays: Current disposition for each decision
- Suggests: Update disposition based on new evidence
- Records: Disposition change history

---

## 7. Querying and Retrieving Disposition

### 7.1 New Query APIs (Read-Only)
**Endpoint 1**: `/api/decisions/disposition?id=DC_xxx`
```json
{
  "decision_id": "DC_20260823_001",
  "current_disposition": {
    "value": "investigate",
    "assigned_at": "2026-08-23T12:34:56Z"
  },
  "disposition_history": [
    {"value": "monitor", "assigned_at": "...", "reason": "..."},
    {"value": "investigate", "assigned_at": "...", "reason": "..."}
  ]
}
```

**Endpoint 2**: `/api/decisions/by-disposition?value=investigate`
```json
{
  "disposition": "investigate",
  "matching_decisions": [
    "DC_20260823_001",
    "DC_20260823_002",
    ...
  ]
}
```

**Endpoint 3**: `/api/disposition-queue`
```json
{
  "pending_disposition_actions": [
    {
      "decision_id": "DC_20260823_001",
      "disposition": "investigate",
      "expected_by": "2026-08-24T...",
      "status": "awaiting_orchestration"
    }
  ]
}
```

### 7.2 Disposition Update API (Write)
**Endpoint**: `POST /api/decisions/disposition`
```json
{
  "decision_id": "DC_20260823_001",
  "new_disposition": {
    "value": "resolve",
    "reason": "Investigation complete, no issues found",
    "updated_by": "human_gate_session_xyz"
  }
}
```

**Constraints**:
- Only Human Gate sessions can update
- Creates new version in decision_ledger.jsonl
- Old version preserved (append-only)

---

## 8. Test Strategy (Design-Only)

### 8.1 Schema Validation
- **test_backward_compatibility**: Records without disposition field still parse
- **test_optional_field**: Disposition can be null/absent
- **test_version_tracking**: Disposition versions append correctly

### 8.2 State Machine Isolation
- **test_state_unchanged**: Disposition change does NOT change state
- **test_no_auto_transition**: No state machine field modified
- **test_readonly_state**: State machine operations unaffected

### 8.3 Metadata Integrity
- **test_append_only**: Disposition updates never overwrite
- **test_history_preserved**: All disposition versions retrievable
- **test_no_circular_ref**: Disposition does not reference state

### 8.4 API Integration
- **test_disposition_query**: Can query decisions by disposition
- **test_disposition_update**: Can update disposition safely
- **test_history_retrieval**: Can retrieve disposition history

---

## 9. Outstanding Design Questions

### 9.1 Blocking Questions
1. **Disposition Default**: Should decisions auto-assign a default disposition?
   - Option A: Default = "monitor" for all new approvals
   - Option B: No default, leave null until explicitly assigned
   - Answer needed: Before implementation authorization

2. **Timeline**: When is disposition assigned?
   - Option A: At approval time (same as decision)
   - Option B: At first escalation (lazy)
   - Answer needed: Before implementation

3. **Expiry**: Should "expected_review_by" trigger escalation?
   - Option A: Yes, auto-escalate if review expires
   - Option B: No, just advisory (no auto-action)
   - Answer needed: For safety-critical decisions

### 9.2 Design Questions
1. **Related Action ID**: Should disposition link to TODO/task?
   - Proposal: Optional field for traceability
   - Alternative: Keep separate (no cross-reference)

2. **Disposition Reasoning**: Should rationale field be mandatory?
   - Proposal: Yes, always explain why
   - Alternative: Optional (time-constrained decisions)

---

## 10. Files Affected (Expected, Design-Only)

**New files** (implementation phase):
- interface/disposition_mapper.py (disposition API implementation)
- tests/test_disposition_metadata.py

**Modified files** (implementation phase):
- data/decisions/decision_ledger.jsonl: ADD disposition field (append-only)
- app.py: ADD /api/decisions/disposition endpoints
- governance/human_gate_cli.py: ADD disposition update capability (read-only decision update)

**NOT modified** (boundary enforcement):
- governance/human_gate.py: State machine logic untouched
- schema/decision_schema.py: Existing structure preserved
- Decision approval logic: Unchanged

---

## 11. Conclusion: Design Readiness

**Ready to Proceed to Implementation Preparation:**
- ✓ Disposition semantic model defined
- ✓ Payload metadata structure designed
- ✓ Integration with Orchestration & COMPARE adapters mapped
- ✓ Strict boundary enforcement verified
- ✓ State machine isolation confirmed
- ✓ Query and update APIs specified

**Outstanding Before Implementation Authorization:**
- [ ] Answer blocking design questions (Section 9.1)
- [ ] Confirm disposition defaults
- [ ] Specify expiry/escalation behavior
- [ ] Complete Orchestration Adapter design (cross-reference)
- [ ] Complete COMPARE Adapter design (cross-reference)

---

## Related Documents

- ORCHESTRATION_ADAPTER_DESIGN_INVESTIGATION.md (sibling design)
- COMPARE_ADAPTER_DESIGN_INVESTIGATION.md (sibling design)
- data/decisions/decision_ledger.jsonl (reference)
- docs/governance/DECISION_LEDGER_SCHEMA_v1.md (schema)
- governance/human_gate.py (state machine, to remain LOCKED)
