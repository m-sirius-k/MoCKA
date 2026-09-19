# HG-M3-PHASE1 Authority State Model v1.0

**Design Phase Specification — Authority Model Evolution (AREA A)**

**Classification:** Formal Governance Specification (Design-Only Authorization)  
**Authority:** Human Gate Decision (2026-09-19)  
**Scope:** M3 Phase 1 Design Deliverable #1  
**Status:** DESIGN SPECIFICATION (Implementation authorization deferred to Phase 2)

---

## 1. Purpose

Define the formal state space of authority within MoCKA governance system. Authority State Model specifies:
- What authority states exist (categories, valid combinations)
- How authority state is represented and identified
- What transitions between states are permitted
- What evidence must accompany state transitions
- How authority state persists and is queried

This model establishes the foundation upon which Authority Object Model and Delegation Governance Framework depend.

---

## 2. Normative Requirements

### 2.1 Authority State Definition

Authority is a formal governance status that grants permission to execute a specific Decision or perform a specific Action within MoCKA.

**Requirement #1:** Authority state MUST be explicitly represented as an attribute of a Decision or Action.

**Requirement #2:** Authority state MUST NOT be implicit, assumed, or derived from role/title/history.

**Requirement #3:** Authority state MUST be binary: either authority is explicitly present, or it does not exist (default state = NONE).

**Requirement #4:** Authority state MUST be immutable after Decision Ledger commitment (no retroactive authority assignment or removal).

### 2.2 Authority State Categories

Authority states are categorized by their source:

1. **GRANTED_HUMAN:** Authority explicitly granted by Human Gate (only source for M3 Phase 1)
2. **DELEGATED:** Authority delegated from another authority holder via formal Delegation (see Delegation Governance Framework)
3. **SYSTEM_DEFAULT:** Reserved for future use; NOT ACTIVE in Phase 1
4. **UNDEFINED:** Authority status unknown or not yet queried

All other categorizations are forbidden in Phase 1.

### 2.3 Authority Scope

Authority is always scoped to:
- **Decision Type:** Which Decision types can be authorized (e.g., "Implementation Approval", "Scope Change", "Revocation")
- **Resource Class:** What resources/components the authority covers (e.g., "Sandbox Experimental", "Production Schema", "Governance Runtime")
- **Temporal Scope:** Validity period (e.g., "active from 2026-09-19 to 2026-12-31" or "indefinite")

**Requirement #5:** Authority MUST NOT be granted without explicit Resource Class and Decision Type scoping.

---

## 3. Authority States (State Space Definition)

### 3.1 Formal State Enumeration

```
AUTHORITY_STATE ::=
  | NONE                 # No authority exists (default)
  | GRANTED_HUMAN        # Human Gate explicitly granted this authority
  | DELEGATED_ACTIVE     # Delegated from another authority holder (revocation not yet executed)
  | DELEGATED_REVOKED    # Revoked delegation (authority no longer valid)
  | UNDEFINED            # Authority state not yet determined/queried
```

### 3.2 State Properties

Each authority state carries the following metadata:

```
Authority State Properties:
  - granted_by: WHO granted this authority (Human Gate, or delegating authority ID)
  - granted_at: WHEN authority was granted (ISO 8601 timestamp)
  - decision_type_scoped: Which Decision types this authority applies to
  - resource_class_scoped: Which resource classes this authority applies to
  - valid_until: Expiration date/time (or null for indefinite)
  - decision_ledger_entry_id: Reference to Decision Ledger entry recording this state
  - delegation_source: (if DELEGATED) ID of delegating authority holder
  - revocation_reason: (if DELEGATED_REVOKED) Reason revocation was executed
```

### 3.3 Valid State Combinations

Within a single Decision/Action:
- A Decision MAY have GRANTED_HUMAN authority only (single source)
- A Decision MAY have DELEGATED_ACTIVE authority only (single source)
- A Decision MUST NOT have both GRANTED_HUMAN and DELEGATED_ACTIVE (prohibition on dual sources)
- A Decision with DELEGATED_REVOKED state MUST NOT execute (revocation is terminal)
- A Decision queried as UNDEFINED MUST re-query before execution (UNDEFINED is not executable state)

---

## 4. Allowed Transitions

### 4.1 Valid State Transitions

From **NONE** (no authority):
- Transition to GRANTED_HUMAN: Human Gate explicitly grants authority
- Transition to DELEGATED_ACTIVE: Authority holder delegates this authority via formal Delegation Governance Framework
- Transition to UNDEFINED: Query mechanism cannot locate authority (intermediate state)

From **GRANTED_HUMAN** (authority present):
- Remain in GRANTED_HUMAN: Authority persists indefinitely (unless temporal scope expires)
- Transition to GRANTED_HUMAN with different scope: Human Gate modifies authority scope (requires new Human Gate Decision)
- Transition to NONE: Human Gate revokes authority (see Revocation Rules)

From **DELEGATED_ACTIVE** (delegated authority):
- Remain in DELEGATED_ACTIVE: Delegation persists while valid
- Transition to DELEGATED_REVOKED: Delegating authority holder revokes delegation (see Revocation Rules)

From **DELEGATED_REVOKED** (revocation executed):
- Remain in DELEGATED_REVOKED: Permanent terminal state (no re-delegation of revoked authority)
- NO transitions to any other state permitted

From **UNDEFINED** (state unknown):
- Transition to any valid state: After authority query resolves

---

## 5. Forbidden Transitions

**Prohibition #1:** Transition from any state to UNDEFINED after authority query has been committed to Decision Ledger.

**Prohibition #2:** Transition from DELEGATED_REVOKED to any state other than DELEGATED_REVOKED (revocation is permanent for lifecycle of that delegation).

**Prohibition #3:** Transition from GRANTED_HUMAN to DELEGATED_ACTIVE without explicit new Human Gate decision (authority source cannot change mid-lifecycle).

**Prohibition #4:** Simultaneous holding of GRANTED_HUMAN + DELEGATED_ACTIVE for same Decision (single-source authority only).

**Prohibition #5:** Retroactive authority state change (no backdating authority grants or revocations into Decision Ledger).

**Prohibition #6:** Implicit authority state assignment (all authority state transitions must be explicitly recorded and evidenced).

---

## 6. Delegation Rules (Authority State View)

Delegation creates a new authority state (DELEGATED_ACTIVE) derived from existing GRANTED_HUMAN authority.

**Requirement #6:** Delegation MAY ONLY create DELEGATED_ACTIVE state when source authority is GRANTED_HUMAN.

**Requirement #7:** Delegation from DELEGATED_ACTIVE authority (transitive delegation) is FORBIDDEN in Phase 1.

**Requirement #8:** Each delegation establishes single-level chain: GRANTED_HUMAN → [ONE delegation step] → DELEGATED_ACTIVE.

Authority state does not track the full delegation chain, only immediate source (see Authority Object Model for chain tracking).

---

## 7. Revocation Rules (Authority State View)

Revocation transitions authority from active state (GRANTED_HUMAN or DELEGATED_ACTIVE) to terminal state (NONE or DELEGATED_REVOKED).

**Requirement #9:** GRANTED_HUMAN authority MAY be revoked by Human Gate only.

**Requirement #10:** DELEGATED_ACTIVE authority MAY be revoked by:
- Delegating authority holder (immediate revocation)
- Human Gate (override revocation)

**Requirement #11:** Revocation is IMMEDIATE: authority becomes invalid at revocation timestamp; no grace period.

**Requirement #12:** Revoked authority CANNOT be re-granted without new explicit Human Gate Decision.

**Requirement #13:** Revocation event MUST be recorded in Decision Ledger with reason and timestamp.

---

## 8. Evidence Requirements

Every authority state transition MUST generate evidence for Decision Ledger:

```
Authority_State_Event:
  - event_id: Unique event identifier (E{YYYYMMDD}_{NNN})
  - timestamp: ISO 8601 format
  - authority_id: Identifier of the authority being granted/transitioned
  - from_state: Previous state (or NONE if initial grant)
  - to_state: New state
  - decision_type: Decision type this authority applies to
  - resource_class: Resource class this authority applies to
  - granted_by: WHO executed this state transition (Human Gate, delegating authority ID, system)
  - scope_metadata: Complete scope specification
  - related_decision_id: Decision Ledger ID where this authority is first used
  - revocation_reason: (if revocation) Reason for revocation
```

**Requirement #14:** Authority state transitions MUST be recorded in Decision Ledger BEFORE authority becomes executable.

**Requirement #15:** All authority state queries MUST be logged for audit trail (read-side evidence).

---

## 9. M2 Boundary

### 9.1 M2 Authority State Preservation

All existing M2 Decisions retain their M2 authority state (implicit all-human model). M3 Authority State Model does NOT apply retroactively to M2 Decisions.

**Requirement #16:** M2 Decisions MUST NOT be re-classified into M3 Authority State categories.

**Requirement #17:** M2 authority context (Human Gate approval history) MUST remain immutable and separate from M3 authority state tracking.

**Requirement #18:** M3 queries for authority state of M2 Decisions MUST return "M2_LEGACY" classification, not GRANTED_HUMAN/DELEGATED/NONE.

### 9.2 M2→M3 Transition

First Decision created under M3 authorization becomes first point where M3 Authority State Model applies:
- Requires explicit GRANTED_HUMAN or DELEGATED_ACTIVE state
- Is recorded in Decision Ledger with new authority_state field
- Activates authority scope enforcement from that point forward

---

## 10. UNKNOWN / UNDEFINED Items

The following items are NOT defined in Authority State Model and are deferred to Phase 2 or future decision:

1. **Authority Identity Format:** How authority is formally identified (UUID, semantic name, etc.) — deferred to Phase 2
2. **Authority Lifetime Policy:** Default validity periods, maximum grant durations — deferred to Phase 2
3. **Authority Scope Hierarchies:** Whether resource classes form hierarchy enabling scope inheritance — UNDEFINED
4. **State Query Performance:** Caching, validation latency requirements — deferred to implementation phase
5. **Multi-Authority Composition:** Whether multiple authorities can be composed for single Decision — FORBIDDEN in Phase 1, decision deferred
6. **Temporal Authority:** Whether authority can be scheduled for future activation — UNDEFINED
7. **Authority Audit Retention:** How long authority state history is retained — deferred to governance policy
8. **Authority Delegation Chains:** Analytics on delegation depth/breadth — deferred to Phase 2
9. **Conflict Resolution:** Behavior when multiple conflicting authority states detected — UNDEFINED (should not occur by design)
10. **External Authority Integration:** Whether external systems can grant authority — UNDEFINED (single-source design in Phase 1)

---

## 11. Design-Phase Metadata

**Document:** HG-M3-PHASE1-AUTHORITY-STATE-MODEL-v1.0.md  
**Design Authority:** Human Gate (Dr. Masahito Kimura)  
**Specification Phase:** M3 Phase 1 (Design-Only Authorization)  
**Related Specification:** HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0.md (companion spec)  
**Dependency:** M2 Frozen State (immutable)  
**Next Phase:** Implementation design and runtime binding (Phase 2 authorization)

**Normative References:**
- HG-M3 Phase 1 Scope Lock (DC_20260918_003)
- HG-M3 Phase 3 Conditional Start Activation (DC_20260918_006)
- MoCKA Constitution (governance/CONSTITUTION_v1.0.md)

**Version History:**
- v1.0 (2026-09-19): Initial design specification, Human Gate decisions Q1-Q8 incorporated, ready for review

---

**STATUS: DESIGN SPECIFICATION — Awaiting Human Gate review and approval**

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
