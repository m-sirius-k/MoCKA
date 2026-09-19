# HG-M3-PHASE1 Delegation Governance Framework v1.0

**Design Phase Specification — Authority Model Evolution (AREA A)**

**Classification:** Formal Governance Specification (Design-Only Authorization)  
**Authority:** Human Gate Decision (2026-09-19)  
**Scope:** M3 Phase 1 Design Deliverable #3  
**Status:** DESIGN SPECIFICATION (Implementation authorization deferred to Phase 2)

---

## 1. Purpose

Define the formal process and constraints for delegating authority from one Authority Object to another. Delegation Governance Framework specifies:
- What conditions permit authority delegation
- How delegation decisions are made and authorized
- What lifecycle applies to delegated authority
- How delegation relationships are documented and evidenced
- What prevents invalid delegation chains

---

## 2. Normative Requirements

### 2.1 Delegation Definition

Delegation is the formal transfer of authority from an existing GRANTED_HUMAN Authority Object to a new DELEGATED Authority Object.

**Requirement #1:** Delegation creates a new Authority Object (DELEGATED type) with delegation_depth = 1.

**Requirement #2:** Delegation MUST be explicit: requested by authority holder, evaluated by Human Gate or designated reviewer, recorded in Decision Ledger.

**Requirement #3:** Delegation is NOT automatic: no rule or algorithm automatically creates delegated authorities.

**Requirement #4:** Delegation is NOT reversible: once delegated authority is revoked, it cannot be "un-delegated" back to delegator's direct control.

### 2.2 Single-Level Delegation Only

**Requirement #5:** Transitive delegation is FORBIDDEN. Delegation depth MUST NOT exceed 1.

- GRANTED_HUMAN (depth 0) → delegates → DELEGATED_ACTIVE (depth 1)
- DELEGATED_ACTIVE (depth 1) → cannot delegate further

**Requirement #6:** Authority holder with GRANTED_HUMAN authority MAY delegate if and only if max_delegations >= 1 in their Authority Object.

**Requirement #7:** Authority holder with DELEGATED authority MUST NOT delegate (max_delegations = 0 for all DELEGATED objects).

---

## 3. Delegation Authority and Permission

### 3.1 Who Can Delegate?

**Authority to Delegate:**
- GRANTED_HUMAN Authority Object holders (if max_delegations > 0)
- Human Gate (can initiate delegation on behalf of any holder)
- NO OTHER ENTITIES can initiate delegation

### 3.2 Who Can Accept Delegation?

**Eligible Recipients:**
- Named individual (Human Gate decision must specify recipient)
- Specific Decision Type (recipient can only delegate for that Decision Type)
- Specific Resource Class (recipient can only delegate for that Resource Class)
- NO organizational roles
- NO automatic delegation recipients

### 3.3 Who Approves Delegation?

**Delegation Approval Authority:**
- For delegation initiated by holder: Delegation Governance Committee or Human Gate (Phase 1: deferred to Phase 2 for specific governance body definition)
- For delegation initiated by Human Gate: Human Gate directly

**Requirement #8:** Delegation MUST be approved by authority at same level or higher than delegating authority.

---

## 4. Delegation Process

### 4.1 Delegation Initiation

A Delegation Request is initiated by:

```
Delegation_Request:
  from_authority_id:      string  # Source GRANTED_HUMAN Authority Object
  to_recipient:           string  # Named individual (e.g., "Alice", "Process:Sandbox-Manager")
  decision_type:          string  # Which Decision types may be delegated (must match source scope)
  resource_class:         string  # Which resource classes (must match source scope)
  delegation_reason:      string  # WHY delegation is needed
  requested_at:           timestamp
  requested_by:           string  # WHO initiated this request
  valid_from:             timestamp (default: requested_at)
  valid_until:            timestamp (null = indefinite)
  max_recursive_delegations: integer (must be 0 for Phase 1)
```

### 4.2 Delegation Evaluation

Delegation Request is evaluated against:

1. **Permission Check:**
   - Does source Authority Object have max_delegations > 0?
   - Is delegation_depth of source = 0 (GRANTED_HUMAN only)?
   - Is delegation_depth <= 1 (no transitive chains)?

2. **Scope Check:**
   - Does delegated decision_type match source authority's decision_type scope?
   - Does delegated resource_class match source authority's resource_class scope?

3. **Recipient Check:**
   - Is recipient a named individual or specific process?
   - Is recipient authorized to receive authority for this decision_type and resource_class?

4. **Temporal Check:**
   - Is valid_from <= valid_until?
   - Does temporal scope align with delegator's authority temporal scope?

5. **Chain Check:**
   - Is delegation_depth of resulting DELEGATED object exactly 1?
   - Does request forbid transitive delegation (max_recursive_delegations = 0)?

### 4.3 Delegation Approval

Delegation Request is either:

**APPROVED:** New DELEGATED Authority Object is created with:
- delegation_source = source Authority Object ID
- delegation_depth = 1
- granted_by = delegation approval authority (Human Gate or Governance Committee)
- state = CREATED (or ACTIVE if valid_from <= now)

**REJECTED:** Delegation Request is denied with reason recorded in Decision Ledger:
- No Authority Object created
- Rejection reason documented
- Requestor notified

---

## 5. Delegation Lifecycle

### 5.1 Delegation Lifecycle States

```
Delegation Lifecycle:
  REQUESTED       # Delegation Request created, awaiting approval
  APPROVED        # Delegation approved, DELEGATED Authority Object created
  ACTIVE          # Delegated authority is executable (temporal scope entered)
  REVOKED_BY_DELEGATOR    # Delegating authority revoked the delegation
  REVOKED_BY_GOVERNANCE   # Human Gate or Governance Committee revoked
  EXPIRED         # Temporal scope of delegation expired
```

### 5.2 Valid Lifecycle Transitions

```
REQUESTED → APPROVED → ACTIVE → (REVOKED_BY_DELEGATOR | REVOKED_BY_GOVERNANCE | EXPIRED)
REQUESTED → REJECTED  # (not approved)
```

No other transitions permitted.

---

## 6. Delegation Constraints

### 6.1 Scope Constraints

**Constraint #1:** Delegated authority MUST NOT expand scope beyond source authority.

- If source authority covers {decision_type: "APPROVAL", resource_class: "SANDBOX"}
- Delegated authority MUST be subset: e.g., {decision_type: "APPROVAL", resource_class: "SANDBOX"} (same scope)
- Delegated authority CANNOT be: {decision_type: "APPROVAL", resource_class: "PRODUCTION"} (expanded scope)

**Constraint #2:** Delegated authority MUST match source authority's temporal scope or be more restrictive.

- If source authority valid until 2026-12-31
- Delegated authority MUST expire on or before 2026-12-31
- If source authority is revoked, all delegations from it become revoked

### 6.2 Chain Constraints

**Constraint #3:** Delegation depth MUST be exactly 0 (source) → exactly 1 (delegated). No exceptions.

**Constraint #4:** Delegated authority (depth 1) CANNOT delegate further. max_delegations = 0 for all DELEGATED objects.

**Constraint #5:** No implicit delegation chains are permitted (all delegations must be explicit requests).

### 6.3 Revocation Constraints

**Constraint #6:** When GRANTED_HUMAN authority is revoked, all its delegations MUST be immediately revoked (cascade revocation).

**Constraint #7:** When DELEGATED authority is revoked, no further revocation cascade occurs (no sub-delegations exist).

**Constraint #8:** Revoked delegations are immutable (cannot be "re-delegated" under same Delegation Request).

### 6.4 Quantity Constraints

**Constraint #9:** Single GRANTED_HUMAN Authority Object can support multiple delegations (if max_delegations permits) but each delegation creates exactly one DELEGATED Authority Object (no batch delegation).

**Constraint #10:** Each recipient can receive at most one delegation per {decision_type, resource_class} combination within same temporal window.

---

## 7. Cascade Revocation (Authority Source Revocation)

When a GRANTED_HUMAN Authority Object is revoked:

```
Cascade_Revocation_Process:
  1. Mark GRANTED_HUMAN Authority as REVOKED
  2. Identify all DELEGATED Authority Objects with delegation_source = revoked authority
  3. Mark each DELEGATED Authority as REVOKED_BY_CASCADE
  4. Record revocation events for all cascade targets in Decision Ledger
  5. Notify delegatees of revocation
```

**Requirement #9:** Cascade revocation MUST complete atomically (all delegations revoked together or none).

**Requirement #10:** Cascade revocation reason = "Source authority revoked: {source_revocation_reason}"

---

## 8. Evidence Requirements

Every delegation-related event MUST generate Decision Ledger entry:

```
Delegation_Evidence:
  event_id:               string   # E{YYYYMMDD}_{NNN}
  timestamp:              timestamp # ISO 8601
  event_type:             enum     # DELEGATION_REQUESTED | DELEGATION_APPROVED | DELEGATION_REVOKED | DELEGATION_EXPIRED | DELEGATION_QUERIED
  
  from_authority_id:      string   # Source GRANTED_HUMAN Authority
  to_authority_id:        string   # Resulting DELEGATED Authority (if approved)
  recipient_name:         string   # Named recipient
  
  decision_type:          string   # Delegated decision type
  resource_class:         string   # Delegated resource class
  valid_from:             timestamp
  valid_until:            timestamp
  
  approval_authority:     string   # WHO approved this delegation
  approval_decision_id:   string   # Human Gate Decision ID authorizing delegation
  
  revocation_reason:      string   # (if revoked) Why revocation occurred
  revocation_by:          string   # (if revoked) WHO executed revocation
  revocation_timestamp:   timestamp # (if revoked)
```

**Requirement #11:** Delegation Request MUST be recorded in Decision Ledger before approval is granted.

**Requirement #12:** Delegation approval MUST reference Human Gate Decision authorizing approval.

**Requirement #13:** Delegation revocation MUST record reason and authority responsible.

---

## 9. M2 Boundary

### 9.1 M2 Delegation (None)

M2 Decisions do not use delegation framework. M2 authority model is implicit all-human with no formal delegation.

**Requirement #14:** M2 Authority Objects MUST NOT be created retroactively.

**Requirement #15:** Delegation framework applies only to M3+ Authority Objects.

### 9.2 M2→M3 Transition

First M3 Delegated Authority Object is created under M3 delegation framework:
- Requires Human Gate Decision authorizing delegation
- Recorded in Decision Ledger with delegation evidence
- Establishes delegation precedent for future M3 delegations

---

## 10. UNKNOWN / UNDEFINED Items

The following delegation governance aspects are NOT defined in Phase 1 and are deferred:

1. **Delegation Governance Committee:** Which specific individuals/bodies approve delegations (deferred to Phase 2)
2. **Delegation Request Protocol:** Specific process/interface for submitting delegation requests (deferred to Phase 2)
3. **Delegation Performance Metrics:** SLA for delegation approval time, audit latency (deferred to Phase 2)
4. **Recipient Eligibility Criteria:** How recipients are pre-qualified to receive delegations (UNDEFINED)
5. **Delegation Audit Trail:** How delegation history is queried and reported (deferred to Phase 2)
6. **Delegation Inheritance:** Whether delegated authority carries historical context (UNDEFINED; current design: no inheritance)
7. **Delegation Composition:** Whether multiple delegations can be composed for single Decision (FORBIDDEN in Phase 1)
8. **Automatic Revocation Triggers:** Whether certain events (person termination, scope changes) automatically trigger revocation (UNDEFINED; no automatic triggers in Phase 1)
9. **Delegation Appeal Process:** Whether rejected delegations can be appealed (UNDEFINED)
10. **Delegation Notification Protocol:** How delegatees are notified of delegation events (deferred to implementation)

---

## 11. Design-Phase Metadata

**Document:** HG-M3-PHASE1-DELEGATION-GOVERNANCE-FRAMEWORK-v1.0.md  
**Design Authority:** Human Gate (Dr. Masahito Kimura)  
**Specification Phase:** M3 Phase 1 (Design-Only Authorization)  
**Companion Specifications:**
- HG-M3-PHASE1-AUTHORITY-STATE-MODEL-v1.0.md
- HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0.md
- HG-M3-PHASE1-REVOCATION-CONDITIONS-DESIGN-v1.0.md

**Dependency:** M2 Frozen State (immutable)  
**Next Phase:** Delegation governance committee formation and implementation design (Phase 2 authorization)

**Normative References:**
- HG-M3 Phase 1 Scope Lock (DC_20260918_003)
- Authority Model specifications (companion docs)
- MoCKA Constitution (governance/CONSTITUTION_v1.0.md)

**Version History:**
- v1.0 (2026-09-19): Initial design specification, single-level delegation enforced, Human Gate decisions incorporated, ready for review

---

**STATUS: DESIGN SPECIFICATION — Awaiting Human Gate review and approval**

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
