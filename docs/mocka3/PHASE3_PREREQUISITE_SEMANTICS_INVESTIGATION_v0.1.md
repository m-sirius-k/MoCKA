# PHASE 3: Prerequisite-Event Semantics Design Investigation

**Status:** Design Investigation Only (No Implementation Authorized)  
**Decision Reference:** DC_20260818_004  
**Event Reference:** E20260818_076648538f3a8  
**Author:** Claude Code (MoCKA Executive)  
**Date:** 2026-08-18

---

## 1. EXECUTIVE SUMMARY

### Phase 2 Closure Evidence

Phase 2 confirmed a **Representation Gap**: MoCKA's Event Store currently lacks the semantic capability to represent prerequisite-event relationships where Event B's validity is mechanically dependent on Event A satisfying prior conditions.

**Confirmed Facts:**
- trace_id, related_event_id = hash-chain integrity + ordering linkage only
- before_state, after_state = event-local state transitions (no cross-event prerequisite validation)
- causal_graph = post-hoc correlational analysis (not prerequisite enforcement)
- No existing primitive enables mechanical prerequisite enforcement

**Not Confirmed (Deferred):**
- What primitive representation is needed
- What validation/enforcement mechanism is required
- Which semantic layer should house this capability
- Authority and governance boundaries

### Human Authority Decision (OPTION B)

**DC_20260818_004:** Prerequisite-event semantics should be addressed as formal MoCKA capability.

**Critical Constraint:** This decision authorizes DESIGN INVESTIGATION ONLY. No implementation, schema change, validator modification, or runtime enforcement is authorized yet.

---

## 2. PHASE 3 SCOPE: DESIGN INVESTIGATION ONLY

### What Phase 3 WILL Do

1. Semantically define "prerequisite" in MoCKA context
2. Identify who has authority to define and judge prerequisites
3. Reconcile state semantics (existence vs. success vs. fulfillment)
4. Investigate multiplicity patterns (single, multiple, AND/OR, chains)
5. Prepare evidence for Design Acceptance Gate

### What Phase 3 WILL NOT Do

❌ Design new fields  
❌ Propose schema changes  
❌ Write implementation code  
❌ Modify validators  
❌ Change runtime enforcement  
❌ Propose data structures  

**This document is design-only. Any concrete field or schema proposal is OUT OF SCOPE.**

---

## 3. SEMANTIC DEFINITION: KEY CONCEPTS

### 3.1 Prerequisite (Semantic Definition)

**Definition (Working):**

A prerequisite is a condition that must be satisfied prior to another event's validity being affirmed.

Characteristics:
- Antecedent: References a prior event (or state)
- Condition: Specifies what "satisfied" means (success, completion, specific state)
- Consequent: Applies to a subsequent event's validation
- Authority: Some entity decides whether prerequisite is met
- Mechanic: MoCKA enforces this relationship at validation time

### 3.2 Event Validity (vs. Existence)

**CRITICAL DISTINCTION** (must be preserved in any design):

| Term | Meaning | MoCKA Current Capability |
|------|---------|-------------------------|
| **Existence** | Event appears in Event Store | Yes - primary model |
| **Success** | Event's action completed successfully | Partial - event.status field |
| **Prerequisite Satisfaction** | Event A met the condition required by Event B | NO - GAP CONFIRMED |
| **UNKNOWN** | Whether prerequisite is satisfied cannot be determined | Must preserve as state, not collapse to failure |

### 3.3 Core Semantic Primitives (To Be Defined)

These terms must be precisely defined in Phase 3 design before any implementation:

- **prerequisite**: A declared condition on prior event state
- **prerequisite_condition**: What "satisfied" means (success, completion, specific result)
- **fulfillment**: The state where a prerequisite condition is met
- **non_fulfillment**: The state where a prerequisite condition is explicitly not met
- **absence**: The prior event does not exist (distinct from non_fulfillment)
- **unknown**: Cannot determine whether prerequisite is fulfilled
- **enforcement**: Mechanism that prevents Event B validation if prerequisite unmet
- **override**: Authority-granted exception to prerequisite enforcement

### 3.4 Semantics That MUST NOT Be Conflated

❌ Event A exists ≠ Event A was successful  
❌ Event A was successful ≠ Event A satisfies prerequisite for Event B  
❌ Event A does not exist ≠ Event A failed  
❌ Cannot determine status ≠ Failed  

Each of these must be representable and distinct.

---

## 4. AUTHORITY BOUNDARY DEFINITION

### 4.1 Key Authority Questions

Before any design can proceed, these questions MUST be answered by Human Authority:

| Question | Current Answer | Authority |
|----------|---------------|---------  |
| **Who defines prerequisites?** | UNKNOWN | ? |
| **Who validates prerequisite fulfillment?** | UNKNOWN | ? |
| **Who can declare a prerequisite satisfied?** | UNKNOWN | ? |
| **Can prerequisites be overridden?** | UNKNOWN | ? |
| **Who can grant an override?** | UNKNOWN | ? |
| **Can prerequisites be retroactively modified?** | UNKNOWN | ? |
| **What happens when prerequisite is violated?** | UNKNOWN | ? |
| **Is prerequisite enforcement optional or mandatory?** | UNKNOWN | ? |

### 4.2 Authority Types (Hypothetical - To Be Confirmed)

Possible authority boundaries:
- **Event Author Authority:** Can define prerequisites for their own events?
- **System Authority:** System-wide prerequisite rules?
- **Role-Based Authority:** Specific roles define prerequisites for certain event types?
- **Declarative Authority:** Prerequisites stated in event definition, enforced by system?
- **Procedural Authority:** Prerequisites checked at validation time by authorized entity?

### 4.3 Separation of Concerns

Must clarify:
- **Definition Authority** (who declares what the prerequisite is)
- **Validation Authority** (who checks if condition is met)
- **Enforcement Authority** (who prevents/allows the event if prerequisite violated)
- **Override Authority** (who can grant exceptions)

These may be held by different entities.

---

## 5. STATE SEMANTICS RECONCILIATION

### 5.1 Event State Axis (Local)

Current MoCKA model:

```
Event {
  id: <event_id>
  status: "pending" | "completed" | "failed" | "unknown"
  before_state: <state_snapshot>
  after_state: <state_snapshot>
}
```

This captures local success/failure of the event itself.

### 5.2 Prerequisite State Axis (Relational)

Proposed additional axis (NOT YET IMPLEMENTED):

```
Prerequisite {
  prerequisite_event_ref: <event_id>
  condition: <definition>
  fulfillment_status: "fulfilled" | "not_fulfilled" | "unknown" | "absent"
}
```

Where:
- `fulfilled`: Condition was verified as satisfied
- `not_fulfilled`: Condition was verified as NOT satisfied
- `unknown`: Cannot determine from available information
- `absent`: Referenced event does not exist

### 5.3 Event Validation Result (Composite)

The final validation state of Event B must be able to express:

```
Event B validation:
  - Local status: (success/failure/unknown of B's own action)
  - Prerequisite A status: (fulfilled/not_fulfilled/unknown/absent)
  - Overall validity: (can proceed or not)
```

These must not be collapsed into a single status field.

### 5.4 Canonical Examples

**Example 1: Event A succeeded, Event B awaits prerequisite**

```
Event A: "Transfer initiated"
  - status: completed
  - result: success

Event B: "Transfer confirmed"
  - depends_on: Event A
  - prerequisite: Event A.status == "completed"
  - prerequisite_fulfillment: "fulfilled" (because A is completed)
  - local_status: ready to proceed
```

**Example 2: Event A absent**

```
Event A: (does not exist)

Event B: "Notification sent"
  - depends_on: Event A (non-existent)
  - prerequisite: Event A.status == "completed"
  - prerequisite_fulfillment: "absent"
  - validation_decision: reject (cannot fulfill prerequisite)
```

**Example 3: Event A succeeded, but prerequisite condition not met**

```
Event A: "Request submitted"
  - status: completed
  - result: success
  - request_type: "TypeX"

Event B: "TypeY processing"
  - depends_on: Event A
  - prerequisite: Event A.request_type == "TypeY"
  - prerequisite_fulfillment: "not_fulfilled" (A is TypeX, not TypeY)
  - validation_decision: reject (prerequisite not met)
```

**Example 4: Cannot determine if prerequisite met**

```
Event A: "Async background job"
  - status: pending (still running)
  - result: unknown

Event B: "Use result of A"
  - depends_on: Event A
  - prerequisite: Event A.status == "completed"
  - prerequisite_fulfillment: "unknown" (A still running)
  - validation_decision: defer or reject? (to be decided)
```

### 5.5 CRITICAL: UNKNOWN as First-Class State

MoCKA must be able to record prerequisites whose fulfillment status is UNKNOWN, and reason about them later as more information arrives.

Collapsing UNKNOWN → FAILED is architecturally incorrect for an audit system.

---

## 6. MULTIPLICITY INVESTIGATION

### 6.1 Question: Does MoCKA Need Multiple Prerequisites per Event?

Current assumption: Events might have zero, one, or multiple prerequisite dependencies.

**To Investigate:**

| Pattern | Example | Required? |
|---------|---------|-----------|
| **Single prerequisite** | B depends on A | Unknown |
| **Multiple prerequisites** | B depends on A AND C | Unknown |
| **AND logic** | All prerequisites must be fulfilled | Unknown |
| **OR logic** | At least one prerequisite must be fulfilled | Unknown |
| **Ordered prerequisites** | A before C before B (sequence) | Unknown |
| **Conditional prerequisites** | "If A succeeded, then C required; if A failed, then D required" | Unknown |
| **Alternative paths** | B can proceed if (A succeeded) OR (B was manually approved) | Unknown |
| **Prerequisite chains** | A -> B -> C (cascading dependencies) | Unknown |
| **Prerequisite expiration** | A must happen within time T of B | Unknown |
| **Mutual prerequisites** | A depends on B, B depends on A (cycle detection) | Unknown |

### 6.2 Design Constraint: Do Not Over-Engineer

Multiplicity complexity should be driven by MoCKA use cases, not by general possibility.

Example wrong approach: Design for all logical combinations, then never use most of them.

Example right approach: Survey existing event patterns, identify which patterns actually occur, design to support those.

---

## 7. REPRESENTATION GAP: CURRENT STATE

### 7.1 What Existing Primitives Cannot Do

1. **trace_id / related_event_id**
   - These track forensic ordering and hash-chain integrity
   - They do NOT encode prerequisite semantics
   - Using them to infer prerequisites would be post-hoc analysis, not mechanically enforced

2. **before_state / after_state**
   - These encode local state transition within an event
   - They do NOT encode cross-event dependency
   - They cannot validate whether prior event satisfies a condition

3. **causal_graph (post-hoc)**
   - Built after-the-fact from event ordering
   - Used for analysis, not for enforcement
   - Different from prerequisite (which is forward-declared requirement)

### 7.2 Why New Semantics Are Required

Prerequisite semantics require:
1. **Declarative statement** of what prior condition is required
2. **Forward-looking** (stated before B is created, not inferred after)
3. **Mechanical validation** (system enforces, doesn't rely on external checking)
4. **Authority binding** (clear who decides if condition met)
5. **State preservation** (can store UNKNOWN, not force resolution)

None of these are currently expressible in MoCKA primitives.

---

## 8. DESIGN ACCEPTANCE GATE CHECKLIST

Before proceeding to implementation design, Human Authority must confirm:

- [ ] Semantic definitions (prerequisite, condition, fulfillment, unknown) approved
- [ ] Authority boundaries (who defines, validates, enforces, overrides) approved
- [ ] State semantics (distinction of existence, success, fulfillment, unknown) approved
- [ ] Multiplicity requirements (which patterns actually needed) approved
- [ ] No existing primitive can be repurposed (or if yes, which ones and how)
- [ ] Risk assessment: impact on existing event models completed
- [ ] Governance model (enforcement, override, audit trail) defined

---

## 9. NEXT STEPS: DESIGN ACCEPTANCE GATE

This document is submitted for **Design Acceptance Gate**.

Human Authority will decide:
1. Are the semantic definitions correct and sufficient?
2. Are the authority boundaries clear and appropriate?
3. Should multiplicity support be included, and which patterns?
4. Should Phase 3 continue to representation/architecture design?

If approved, Phase 3 continues to:
- Representation design (how to express prerequisites)
- Architecture design (where in the system to enforce)
- Governance design (override, audit, versioning)

If NOT approved, findings return to Human Authority for clarification.

**Status:** AWAITING DESIGN ACCEPTANCE GATE

---

## APPENDIX A: TERMINOLOGY SUMMARY (Working Definitions)

These will be formalized during Design Acceptance Gate review.

- **prerequisite**: A declared condition on prior event state required for consequent event validation
- **condition**: The specification of what prerequisite fulfillment means (e.g., "event.status == completed")
- **fulfillment**: The state of prerequisite being satisfied
- **validation**: The act of checking whether a prerequisite is fulfilled
- **enforcement**: The mechanism preventing invalid event acceptance when prerequisite unmet
- **override**: Authority-granted exception to enforcement
- **unknown**: Prerequisite status cannot be determined from available information
- **absence**: The prior event referenced by prerequisite does not exist

---

## APPENDIX B: PHASE 2 EVIDENCE REFERENCE

Related Phase 2 closure events:
- E20260818_0600545581d8f (Phase 2 closure evidence summary)
- Decision Ledger: DC_20260818_004

Related decisions that bound this investigation:
- Prerequisite-event semantics is a formal MoCKA capability need (OPTION B)
- Design investigation phase only (no implementation authority)
- Next gate: Design Acceptance Gate
