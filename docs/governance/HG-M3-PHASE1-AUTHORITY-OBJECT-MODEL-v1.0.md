# HG-M3-PHASE1 Authority Object Model v1.0

**Design Phase Specification — Authority Model Evolution (AREA A)**

**Classification:** Formal Governance Specification (Design-Only Authorization)  
**Authority:** Human Gate Decision (2026-09-19)  
**Scope:** M3 Phase 1 Design Deliverable #2  
**Status:** DESIGN SPECIFICATION (Implementation authorization deferred to Phase 2)

---

## 1. Purpose

Define the formal structure and identity of authority objects within MoCKA governance system. Authority Object Model specifies:
- What entities can hold authority (authority objects)
- What properties each authority object must have
- How authority objects are identified and referenced
- What relationships authority objects have to Decisions and delegation chains
- What lifecycle events apply to authority objects

---

## 2. Normative Requirements

### 2.1 Authority Object Definition

An Authority Object is a formal governance entity representing a grant of permission to execute Decisions or Actions within MoCKA.

**Requirement #1:** Each Authority Object MUST have unique identity that persists for lifecycle of that authority.

**Requirement #2:** Authority Objects are NOT roles, personas, or organizational units (M3 Phase 1 uses individual authority grants only).

**Requirement #3:** Authority Objects are NOT transferable between people/systems (if authority holder changes, old Authority Object terminates and new one is created).

**Requirement #4:** Each Authority Object MUST be bound to exactly one Decision Type and exactly one Resource Class (see Authority State Model for scope definition).

**Requirement #5:** Authority Objects are created explicitly via formal grant (Human Gate decision) or formal delegation (Delegation Governance Framework).

---

## 2.2 Authority Object Lifecycle

All Authority Objects follow this lifecycle:

```
CREATED → ACTIVE → [REVOKED | EXPIRED]

- CREATED: Authority Object instantiated but not yet applicable (temporal scope has not begun)
- ACTIVE: Authority Object is executable (current timestamp within temporal scope)
- REVOKED: Authority Object terminated by revocation
- EXPIRED: Authority Object terminated by reaching valid_until timestamp
```

---

## 3. Authority Object Properties (Structure)

### 3.1 Required Properties

Every Authority Object MUST include:

```
Authority_Object:
  id:                     string    # Unique identifier (format: AUTH-{YYYYMMDD}-{UUID})
  label:                  string    # Human-readable name for this authority grant
  
  # Source and Authorization
  granted_by:             string    # WHO granted this authority (Human Gate, or delegating authority ID)
  granted_at:             timestamp # ISO 8601 when this authority was created
  decision_id:            string    # Human Gate Decision ID authorizing this grant (e.g., DC_20260918_003)
  
  # Scope
  decision_type:          string    # Which Decision types this authority enables (e.g., "IMPLEMENTATION_APPROVAL")
  resource_class:         string    # Which resource classes this authority applies to (e.g., "SANDBOX_EXPERIMENTAL")
  
  # Temporal Validity
  valid_from:             timestamp # ISO 8601 when authority becomes effective (default: granted_at)
  valid_until:            timestamp # ISO 8601 when authority expires (null = indefinite)
  
  # Delegation Chain (if delegated)
  delegation_source:      string    # (if delegated) ID of Authority Object this was delegated from
  delegation_depth:       integer   # 0 = GRANTED_HUMAN, 1 = delegated once, >1 FORBIDDEN in Phase 1
  
  # State
  state:                  enum      # Current state: CREATED, ACTIVE, REVOKED, EXPIRED (from Authority State Model)
  
  # Revocation (if applicable)
  revoked_at:             timestamp # (if REVOKED) When revocation was executed
  revoked_by:             string    # (if REVOKED) WHO executed revocation
  revocation_reason:      string    # (if REVOKED) Reason for revocation
  revocation_decision_id: string    # Decision Ledger entry recording revocation
  
  # Constraints
  max_delegations:        integer   # How many delegations this authority can produce (default: 0 in Phase 1)
  
  # Evidence
  ledger_entry_id:        string    # Decision Ledger ID where this authority is recorded
```

### 3.2 Derived Properties (Computed, Not Stored)

```
Authority_Object_Derived:
  is_active:              bool      # (valid_from <= now < valid_until) AND state == ACTIVE
  can_delegate:           bool      # (delegation_depth < 1) AND (max_delegations > 0)
  can_grant_decision:     bool      # is_active AND state != REVOKED
```

---

## 3.3 Forbidden Properties

Authority Objects MUST NOT contain:
- `role` or `persona` (authority is not role-based in Phase 1)
- `auto_apply_to_decisions` (delegation is not automatic)
- `scope_inheritance` (each authority is explicitly scoped; no hierarchy)
- `default_for_type` (no defaults; explicit grant only)
- `renewable` (expired authority cannot be renewed; must create new grant)
- `delegable` flag that contradicts delegation_depth logic (state machine drives delegability)

---

## 4. Authority Objects: Grant Types

### 4.1 GRANTED_HUMAN Authority Objects

Authority Objects created by Human Gate decision (source: Human Gate, never delegated):

```
GRANTED_HUMAN_Authority:
  delegation_depth: 0
  granted_by: "Human Gate" (or specific Human Gate decision ID)
  delegation_source: null
  max_delegations: 0 or 1 (configurable per grant, default 0 = no delegation)
```

**Example:** "Authority to approve sandbox implementation changes, granted by DC_20260918_006"

### 4.2 DELEGATED Authority Objects

Authority Objects created via delegation from GRANTED_HUMAN authority:

```
DELEGATED_Authority:
  delegation_depth: 1 (exactly; no higher depths permitted)
  granted_by: [Source GRANTED_HUMAN Authority ID]
  delegation_source: [Source Authority Object ID]
  max_delegations: 0 (delegated authority cannot be re-delegated in Phase 1)
```

**Constraint:** Transitive delegation (DELEGATED creating another DELEGATED) is FORBIDDEN.

---

## 5. Authority Object Identification

### 5.1 Authority Identity Requirements

**Requirement #6:** Authority Object identifiers MUST be globally unique across all MoCKA instances.

**Requirement #7:** Authority identifiers MUST be persistent (once created, never reused even if revoked).

**Requirement #8:** Authority identifiers MUST NOT encode decision logic or scope (identifier is opaque reference only).

**Requirement #9:** Authority Object identity MUST NOT be human-assigned; MUST be system-generated.

### 5.2 Suggested Identifier Format

```
AUTH-{DATE}-{RANDOM_UUID}

Example: AUTH-20260919-a7f2c81e-4b93-11eb-ae93-0242ac120002

Components:
  AUTH: fixed prefix
  DATE: YYYYMMDD when authority was created
  RANDOM_UUID: 36-character UUID (non-deterministic)
```

(Exact format is implementation detail; design requires only that identifier be unique and persistent)

---

## 6. Authority Object Relationships

### 6.1 Authority → Decision

A Decision MAY reference one Authority Object:

```
Decision:
  authority_id: AUTH-20260919-a7f2c81e-4b93-11eb-ae93-0242ac120002  # Link to Authority Object
  decision_type: IMPLEMENTATION_APPROVAL                             # Must match authority.decision_type
  resource_class: SANDBOX_EXPERIMENTAL                              # Must match authority.resource_class
```

**Requirement #10:** If Decision references an Authority Object, all properties must align (decision_type, resource_class, temporal scope).

### 6.2 Authority → Authority (Delegation Chain)

Delegated Authority Objects reference their source via delegation_source:

```
Source: AUTH-20260919-111111111-4b93-11eb-ae93-0242ac120002 (GRANTED_HUMAN)
  ↓ delegation
Delegated: AUTH-20260920-222222222-4b93-11eb-ae93-0242ac120002 (DELEGATED, delegation_depth=1)
  ↓ transitive delegation FORBIDDEN
(no further delegation permitted)
```

**Requirement #11:** Delegation chain MUST NOT exceed depth 1 in Phase 1.

### 6.3 Authority → Revocation

Revocation creates immutable association:

```
Original: AUTH-20260919-333333333-4b93-11eb-ae93-0242ac120002 (ACTIVE)
  ↓ revocation
Revoked State: Same Authority Object, state changed to REVOKED, revoked_at and revocation_reason recorded
```

---

## 7. Authority Object Constraints

### 7.1 Scope Constraints

**Constraint #1:** Each Authority Object applies to exactly ONE decision_type and ONE resource_class (no wildcard matching in Phase 1).

**Constraint #2:** Authority Object cannot be reused for different decision_type or resource_class (must create new Authority Object).

**Constraint #3:** Scope properties are immutable after creation (cannot modify an Authority Object's decision_type or resource_class).

### 7.2 Temporal Constraints

**Constraint #4:** valid_from MUST be less than or equal to valid_until.

**Constraint #5:** Authority Objects with valid_from in future are CREATED but not ACTIVE (temporal guard).

**Constraint #6:** Authority Objects do NOT automatically transition from EXPIRED to new ACTIVE state (expiration is permanent).

### 7.3 Delegation Constraints

**Constraint #7:** DELEGATED Authority Objects (delegation_depth >= 1) MUST NOT create further delegations.

**Constraint #8:** max_delegations defaults to 0 (no delegation) unless explicitly set to 1 in grant.

**Constraint #9:** If GRANTED_HUMAN Authority Object is revoked, all DELEGATED objects derived from it become invalid (cascade revocation).

### 7.4 Revocation Constraints

**Constraint #10:** Revoked Authority Objects are immutable (cannot be "un-revoked" or re-purposed).

**Constraint #11:** Revocation is recorded with reason and timestamp in Decision Ledger.

**Constraint #12:** Once revoked, Authority Object cannot grant new Decisions.

---

## 8. Authority Object Lifecycle Events

Every significant event in Authority Object lifecycle MUST generate Decision Ledger entry:

```
Authority_Lifecycle_Event:
  - event_id: E{YYYYMMDD}_{NNN}
  - timestamp: ISO 8601
  - authority_id: Which Authority Object
  - event_type: CREATED | DELEGATED | REVOKED | EXPIRED | QUERIED
  - details: Event-specific metadata
  - decision_ledger_id: Entry in Decision Ledger
```

---

## 9. M2 Boundary

### 9.1 M2 Authority Objects

M2 Decisions do not reference Authority Objects (M2 authority model is implicit all-human).

**Requirement #12:** M2 Decisions MUST NOT be retrofitted with Authority Object references.

**Requirement #13:** Authority Objects are purely M3+ construct; M2 Decisions retain legacy authority model.

### 9.2 M2→M3 Transition

First M3 Decision introduces first Authority Object:
- Requires Human Gate Decision authorizing this Authority Object
- Authority Object is recorded in Decision Ledger
- From that point forward, all M3+ Decisions reference authority state

---

## 10. UNKNOWN / UNDEFINED Items

The following Authority Object aspects are NOT defined in Phase 1 and are deferred:

1. **Authority Object Serialization Format:** How Authority Objects are persisted (JSON, SQL, etc.) — deferred to implementation
2. **Authority Lookup Performance:** Query latency requirements, caching strategy — deferred to Phase 2
3. **Authority Object Versioning:** Whether Authority Objects can be versioned (current design: no versioning, only replacement) — UNDEFINED
4. **Scope Semantics:** What exact resource classes exist, their hierarchies — deferred to Phase 2
5. **Decision Type Enumeration:** Complete set of valid decision_type values — deferred to governance policy
6. **Human Gate Representation:** How Human Gate is formally identified in granted_by field — UNDEFINED
7. **Delegation Request Protocol:** How delegation requests are initiated and approved — deferred to Delegation Governance Framework
8. **Authority Composition:** Whether multiple Authority Objects can be combined for single Decision — FORBIDDEN in Phase 1
9. **Authority Transfer:** Can authority be transferred between people without revocation/re-grant — UNDEFINED (no transfer in Phase 1; revoke and re-grant)
10. **Analytics and Reporting:** Authority audit queries, delegation reports — deferred to Phase 2

---

## 11. Design-Phase Metadata

**Document:** HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0.md  
**Design Authority:** Human Gate (Dr. Masahito Kimura)  
**Specification Phase:** M3 Phase 1 (Design-Only Authorization)  
**Companion Specification:** HG-M3-PHASE1-AUTHORITY-STATE-MODEL-v1.0.md  
**Dependency:** M2 Frozen State (immutable)  
**Next Phase:** Implementation design and object lifecycle implementation (Phase 2 authorization)

**Normative References:**
- HG-M3 Phase 1 Scope Lock (DC_20260918_003)
- Authority State Model (companion spec)
- Delegation Governance Framework (companion spec)

**Version History:**
- v1.0 (2026-09-19): Initial design specification, Human Gate decisions incorporated, ready for review

---

**STATUS: DESIGN SPECIFICATION — Awaiting Human Gate review and approval**

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
