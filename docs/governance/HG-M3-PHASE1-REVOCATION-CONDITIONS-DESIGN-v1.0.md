# HG-M3-PHASE1 Revocation Conditions Design v1.0

**Design Phase Specification — Authority Model Evolution (AREA A)**

**Classification:** Formal Governance Specification (Design-Only Authorization)  
**Authority:** Human Gate Decision (2026-09-19)  
**Scope:** M3 Phase 1 Design Deliverable #4  
**Status:** DESIGN SPECIFICATION (Implementation authorization deferred to Phase 2)

---

## 1. Purpose

Define the formal conditions, processes, and semantics for revoking authority within MoCKA governance system. Revocation Conditions Design specifies:
- What conditions trigger or permit authority revocation
- Who can initiate revocation
- How revocation is executed and recorded
- What happens to decisions made under revoked authority
- How revocation is irreversible by design

---

## 2. Normative Requirements

### 2.1 Revocation Definition

Revocation is the formal termination of authority, immediately invalidating the Authority Object's ability to authorize further Decisions.

**Requirement #1:** Revocation is IMMEDIATE: authority becomes invalid at revocation timestamp; no grace period or delayed effect.

**Requirement #2:** Revocation is IRREVERSIBLE: a revoked Authority Object cannot be "un-revoked" or restored to active state.

**Requirement #3:** Revocation creates immutable record in Decision Ledger (revocation is an event, not a state change that can be undone).

**Requirement #4:** Revocation applies only prospectively: Decisions authorized before revocation remain valid; revocation does not invalidate past decisions.

---

## 2.2 Revocation Authority

**Requirement #5:** Authority to revoke is hierarchical:
- GRANTED_HUMAN authority: revoked by Human Gate only (no self-revocation)
- DELEGATED authority: revoked by delegating authority holder OR Human Gate

**Requirement #6:** Revocation authority is NOT delegated (authority to revoke is not itself delegable).

---

## 3. Revocation Conditions

### 3.1 Explicit Revocation (Human-Initiated)

Explicit revocation occurs when authority holder or Human Gate issues explicit revocation:

```
Explicit_Revocation_Conditions:
  - Authority holder requests own revocation
  - Human Gate orders revocation
  - Revocation is time-bound (effective at specified timestamp)
  - Reason is provided for audit trail
```

**Condition #1 (Human Request):** Authority holder requests own authority revocation:
- Request includes reason
- Request is recorded in Decision Ledger
- Human Gate approves revocation (default: approval)
- Authority becomes REVOKED at approval timestamp

**Condition #2 (Human Gate Override):** Human Gate unilaterally revokes authority:
- No holder approval required
- Reason provided by Human Gate
- Authority becomes REVOKED immediately at decision timestamp

### 3.2 Implicit Revocation (Time-Based)

Implicit revocation occurs when temporal scope expires:

```
Implicit_Revocation_Conditions:
  - Authority Object valid_until timestamp is reached
  - Current timestamp >= valid_until
  - Authority transitions to EXPIRED state
  - No explicit revocation request needed
```

**Condition #3 (Expiration):** Authority Object temporal scope expires:
- valid_until timestamp is reached
- Authority automatically transitions to EXPIRED state
- Decision Ledger records expiration event
- Expired authority cannot grant new Decisions

**Requirement #7:** Expiration is automatic (system should detect and record), not manual.

### 3.3 Cascade Revocation (Source Authority Revocation)

Cascade revocation occurs when source authority is revoked:

```
Cascade_Revocation_Conditions:
  - GRANTED_HUMAN authority is revoked
  - All DELEGATED authorities with delegation_source = revoked authority must be revoked
  - Cascade occurs atomically (all delegations revoked together)
```

**Condition #4 (Cascade from Source):** When GRANTED_HUMAN authority is revoked:
- All DELEGATED Authority Objects referencing this as delegation_source are identified
- All delegations are marked REVOKED_BY_CASCADE
- Cascade revocation reason = "Source authority revoked: {source_revocation_reason}"
- All cascade events are recorded atomically in Decision Ledger

**Requirement #8:** Cascade revocation MUST be atomic (either all cascade targets are revoked, or none are).

---

## 4. Revocation Process

### 4.1 Revocation Request/Execution

```
Revocation_Process:
  1. Revocation Initiated
  2. Revocation Validation (check conditions, authority, permissions)
  3. Revocation Approved/Authorized
  4. Authority State Transitioned (to REVOKED, EXPIRED, or REVOKED_BY_CASCADE)
  5. Decision Ledger Event Recorded
  6. Notification Sent (to holders, delegatees, audit trail)
```

### 4.2 Revocation Validation

Revocation is validated against:

1. **Authority Check:**
   - Is requester authorized to revoke this authority?
   - For GRANTED_HUMAN: only Human Gate can revoke
   - For DELEGATED: delegating holder or Human Gate can revoke

2. **State Check:**
   - Is authority in ACTIVE, CREATED, or DELEGATED_ACTIVE state?
   - (Already REVOKED or EXPIRED: no re-revocation)

3. **Scope Check:**
   - Does revocation reason provide sufficient audit trail?

### 4.3 Revocation Approval

```
Revocation_Decision:
  case revocation_type of:
    EXPLICIT_HUMAN_REQUEST:     Human Gate approves (explicit decision required)
    EXPLICIT_HUMAN_GATE_ORDER:  No approval needed (Human Gate decision IS authorization)
    IMPLICIT_EXPIRATION:        No approval needed (automatic)
    CASCADE_FROM_SOURCE:        No approval needed (automatic cascade)
```

---

## 5. Revocation Effects

### 5.1 Immediate Effects

When revocation is executed:

```
Revocation_Immediate_Effects:
  1. Authority Object state → REVOKED (or EXPIRED, REVOKED_BY_CASCADE)
  2. authority.is_active → false
  3. authority.can_grant_decision → false
  4. Authority cannot authorize new Decisions (immediate effect)
  5. Decision Ledger records revocation event with timestamp
```

**Requirement #9:** Authority becomes invalid for new Decisions at revocation timestamp (no decisions can be authorized after revocation).

### 5.2 Prospective Effect (Not Retroactive)

Revocation does NOT invalidate past decisions:

```
Revocation_Prospective_Only:
  - Decisions authorized BEFORE revocation timestamp remain valid
  - Decisions authorized AFTER revocation timestamp are rejected
  - Revocation does not "undo" or "invalidate" previous decisions
  - Historical Decision Ledger entries remain unchanged
```

**Requirement #10:** Revocation affects only future decisions, never retroactively.

### 5.3 Evidence Requirements

Revocation generates immutable evidence:

```
Revocation_Evidence:
  event_id:               string   # E{YYYYMMDD}_{NNN}
  timestamp:              timestamp # ISO 8601 (revocation effective time)
  authority_id:           string   # Authority Object being revoked
  revocation_type:        enum     # EXPLICIT_REQUEST | HUMAN_GATE_ORDER | EXPIRATION | CASCADE
  revoked_by:             string   # WHO executed revocation
  revocation_reason:      string   # WHY revocation occurred
  delegation_source:      string   # (if DELEGATED) Source authority ID
  cascade_reason:         string   # (if CASCADE) Reason source was revoked
  
  decision_ledger_entry:  string   # Decision Ledger event ID
```

**Requirement #11:** Revocation evidence MUST be recorded in Decision Ledger BEFORE authority state becomes invalid.

---

## 6. Revocation Irreversibility

### 6.1 No Restoration of Revoked Authority

**Requirement #12:** A revoked Authority Object CANNOT be restored to active state.

**Requirement #13:** If authority needs to be re-granted, a new Authority Object MUST be created (never reuse revoked authority ID).

**Requirement #14:** New Authority Object gets new identity (AUTH-{DATE}-{UUID}); previous revoked authority ID is never re-used.

### 6.2 Revoked Authority Identity Preservation

**Requirement #15:** Revoked Authority Object ID persists permanently in audit trail and Decision Ledger.

**Requirement #16:** Revoked authority cannot be "archived" or removed; immutable records are maintained indefinitely.

---

## 7. Cascade Revocation Semantics

### 7.1 Cascade Mechanism

When GRANTED_HUMAN authority (depth 0) is revoked:

```
Cascade_Revocation_Semantics:
  SOURCE (GRANTED_HUMAN, depth=0):
    state → REVOKED
    
  DELEGATED_CHILD (DELEGATED, depth=1, delegation_source=SOURCE):
    state → REVOKED_BY_CASCADE
    
  NO FURTHER CASCADE (because delegated authority cannot have delegations)
```

### 7.2 Cascade Atomicity

**Requirement #17:** Cascade revocation is atomic:
- Either all delegations are revoked, or the entire cascade fails and none are revoked
- No partial cascade states are permitted

**Requirement #18:** If cascade fails (e.g., database write error), revocation must be rolled back completely (no orphaned revoked delegations).

### 7.3 Cascade Notification

**Requirement #19:** All delegatees affected by cascade revocation must be notified with:
- Which authority was revoked
- That this triggered cascade revocation
- That their delegated authority is now invalid

---

## 8. Revocation and Decision Ledger Integration

### 8.1 Revocation as Ledger Event

Every revocation MUST be recorded as immutable Decision Ledger entry:

```
Decision_Ledger_Revocation_Entry:
  - entry_id: Unique Decision Ledger ID
  - event_type: REVOCATION
  - authority_id: Which Authority Object
  - revocation_timestamp: When revocation took effect
  - revocation_reason: Why
  - revoked_by: Who authorized revocation
  - related_events: IDs of cascade delegations (if applicable)
```

### 8.2 Revocation Query Semantics

Queries for authority state MUST check Decision Ledger:
- If authority_id found with REVOKED event in Ledger: state = REVOKED
- Revocation timestamp determines validity cutoff
- All decisions after revocation timestamp are rejected

---

## 9. M2 Boundary

### 9.1 M2 Authority (No Revocation Model)

M2 Decisions do not use revocation framework. M2 authority is implicit all-human with no formal revocation model.

**Requirement #20:** M2 authority cannot be revoked using M3 revocation conditions.

**Requirement #21:** M2 Decisions remain permanently governed by M2 rules (no retroactive M3 revocation).

### 9.2 M2→M3 Transition

First revocation in M3+ occurs under M3 revocation conditions:
- Revocation request references M3 authority
- Recorded in Decision Ledger with M3 semantics
- Does not affect M2 authority model

---

## 10. Revocation Error Handling

### 10.1 Invalid Revocation Attempts

Revocation attempts that violate conditions are rejected:

```
Invalid_Revocation_Scenarios:
  1. Non-authorized requester tries to revoke GRANTED_HUMAN authority
     → REJECTED (only Human Gate can revoke GRANTED_HUMAN)
  
  2. Delegated authority holder tries to revoke another delegated authority
     → REJECTED (delegated authority cannot revoke)
  
  3. Attempt to revoke already-REVOKED authority
     → REJECTED (authority already revoked)
  
  4. Attempt to revoke with no reason provided
     → REJECTED (reason is mandatory)
```

**Requirement #22:** All invalid revocation attempts MUST be recorded in Decision Ledger with rejection reason.

---

## 11. UNKNOWN / UNDEFINED Items

The following revocation governance aspects are NOT defined in Phase 1 and are deferred:

1. **Revocation Notification Protocol:** How delegatees are notified of revocation (deferred to Phase 2)
2. **Revocation SLA:** Service level agreement for revocation processing time (deferred to Phase 2)
3. **Automatic Revocation Triggers:** Whether certain events (person termination, security incidents) automatically trigger revocation (UNDEFINED; no automatic triggers in Phase 1)
4. **Revocation Appeal Process:** Whether revocation can be appealed or reversed on appeal (UNDEFINED; current design is no appeal)
5. **Revocation Audit Retention:** How long revocation records are retained (deferred to governance policy)
6. **Revocation Analytics:** Reporting on revocation patterns, frequency, reasons (deferred to Phase 2)
7. **Conditional Revocation:** Whether revocation can be conditional (e.g., "revoke if X happens") (UNDEFINED; only explicit revocation in Phase 1)
8. **Revocation Delegation:** Can revocation authority itself be delegated (UNDEFINED; current design: no delegation of revocation authority)
9. **Forced Revocation:** Whether system can force revocation for technical reasons (UNDEFINED)
10. **Revocation Cosmetics:** How revoked authority appears in UI/reports (deferred to implementation)

---

## 12. Design-Phase Metadata

**Document:** HG-M3-PHASE1-REVOCATION-CONDITIONS-DESIGN-v1.0.md  
**Design Authority:** Human Gate (Dr. Masahito Kimura)  
**Specification Phase:** M3 Phase 1 (Design-Only Authorization)  
**Companion Specifications:**
- HG-M3-PHASE1-AUTHORITY-STATE-MODEL-v1.0.md
- HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0.md
- HG-M3-PHASE1-DELEGATION-GOVERNANCE-FRAMEWORK-v1.0.md

**Dependency:** M2 Frozen State (immutable)  
**Next Phase:** Revocation execution engine and audit trail implementation (Phase 2 authorization)

**Normative References:**
- HG-M3 Phase 1 Scope Lock (DC_20260918_003)
- Authority Model specifications (companion docs)
- MoCKA Constitution (governance/CONSTITUTION_v1.0.md)

**Version History:**
- v1.0 (2026-09-19): Initial design specification, immediate revocation enforced, Human Gate decisions incorporated, ready for review

---

**STATUS: DESIGN SPECIFICATION — Awaiting Human Gate review and approval**

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
