# HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-FINAL-001

**Date:** 2026-09-19  
**Directive:** HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-FINAL-001  
**Status:** AWAITING HUMAN GATE FINAL DECISION  
**Purpose:** Single unified decision on Canonical Event Schema design and implementation authorization

---

## STEP 1: DESIGN READ-BACK (Extracted without AI interpretation)

### 1. Canonical Event Definition

**CURRENT PROPOSAL:**
```
An Event is an auditable record of a state transition or action in MoCKA, capturing:
  1. WHO did/observed it (actor, role, session)
  2. WHAT happened (type, title, description)
  3. WHERE it happened (component, path)
  4. WHY it happened (purpose, trigger)
  5. WHEN it happened (timestamp)
  6. HOW it was triggered (instruction, channel)
  7. BEFORE/AFTER states (optional replay)
  8. PROVENANCE (signature, hash chain)
  9. LIFECYCLE (creation → present state)
  10. RELATIONSHIPS (related events, evidence, decisions)

Scope: An Event is a RECORD, not AUTHORITY.
```

**UNRESOLVED POINT:**
- Does MoCKA accept this semantic (auditable record) as the canonical meaning of "Event"?
- Should Event include governance/decision fields or remain purely as record?

**IMPLEMENTATION IMPACT:**
- If APPROVED: event_gate INSERT becomes canonical, all event processing must use this definition
- If REVISED: Schema redesign required; event_gate contract may need modification
- If REJECTED: Fundamental schema rewrite necessary

---

### 2. Canonical Schema v1: 31 Columns

**CURRENT PROPOSAL:**

| Category | Fields | Count | Required? |
|----------|--------|-------|-----------|
| Identity | event_id | 1 | YES |
| Temporal | when_ts | 1 | YES |
| Actor (WHO) | who_actor, who_role, who_session | 3 | YES |
| Event Type (WHAT) | what_type, title, short_summary, description | 4 | YES (type, title) |
| Location (WHERE) | where_component, where_path | 2 | YES |
| Purpose/Trigger (WHY/HOW) | why_purpose, how_trigger | 2 | YES |
| State Capture | before_state, after_state | 2 | OPTIONAL |
| Provenance | _source, channel_type | 2 | YES |
| Integrity Chain | trace_id, related_event_id | 2 | CONDITIONAL |
| Lifecycle | lifecycle_phase, risk_level, severity | 3 | YES (phase, level) |
| Metadata | free_note, session_id, category_ab, target_class, change_type, impact_scope, impact_result | 7 | OPTIONAL |
| Audit | _imported_at, ai_actor, verified_by | 3 | OPTIONAL |
| Analysis | pattern_score, recurrence_flag | 2 | OPTIONAL |
| **TOTAL** | | **31** | |

**UNRESOLVED POINT:**
- Which fields are truly required vs. optional for a minimal valid Event?
- Should some analysis fields (pattern_score, recurrence_flag) be in schema or computed separately?
- Are 31 columns the right balance or too many?

**IMPLEMENTATION IMPACT:**
- If APPROVED: CREATE TABLE with all 31 columns as proposed
- If REVISED: Column count/classification changes; may affect event_gate INSERT logic
- If REJECTED: Alternative schema (fewer columns? different fields?)

---

### 3. Required / Optional / Conditional Classification

**CURRENT PROPOSAL:**

**REQUIRED (14 fields - must have value, not nullable):**
```
event_id, when_ts
who_actor, who_role, who_session
what_type, title
where_component, where_path
why_purpose, how_trigger
_source, channel_type, lifecycle_phase, risk_level
```

**OPTIONAL (17 fields - may be NULL):**
```
short_summary, description
before_state, after_state
trace_id, related_event_id
free_note, session_id
category_ab, target_class, change_type, impact_scope, impact_result
_imported_at, ai_actor, verified_by
pattern_score, recurrence_flag, severity
```

**CONDITIONAL (depends on context):**
```
before_state, after_state: Required for state-change events, optional for others
trace_id, related_event_id: Required for hash chain continuation, optional for standalone
verified_by: Required if event is audited, optional otherwise
```

**UNRESOLVED POINT:**
- Are the 14 required fields sufficient as minimum viable Event?
- Should title be required or optional?
- Should state fields be required for any event type?

**IMPLEMENTATION IMPACT:**
- If APPROVED: NOT NULL constraints on 14 fields; NULL allowed on 17
- If REVISED: Changes to NOT NULL constraints; may affect existing event_gate payload validation
- If REJECTED: Different classification scheme needed

---

### 4. Event ↔ Evidence Relationship

**CURRENT PROPOSAL:**
```
EVENT:
  - Auditable record of action/state transition
  - Recorded by process/system
  - Can be written without authority decision
  - Example: "File X was written at time T by actor A"

EVIDENCE:
  - Fact used in decision-making
  - Must be selected/validated for use
  - Might require human judgment
  - Example: "Evidence that file corruption occurred (from Event Y)"

RELATIONSHIP:
  Event → (filtered/validated) → Evidence

NOT EQUIVALENT:
  Not all events are evidence
  Not all evidence comes from events
```

**Implication for schema:**
- Event has intrinsic fields (who/what/when/how)
- Event may reference evidence but doesn't create it
- Evidence layer is separate (Phase7 Evidence Layer)

**UNRESOLVED POINT:**
- Should Event schema include evidence_id field or remain separate?
- Who is responsible for selecting Event → Evidence mapping?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Evidence layer handles linkage; Event schema unchanged
- If REVISED: Event may need evidence_id reference field
- If REJECTED: Different Event-Evidence model required

---

### 5. Event ↔ Decision Relationship

**CURRENT PROPOSAL:**
```
EVENT:
  - Record of what happened
  - Factual: "authorization was requested"
  - Passive: records action

DECISION:
  - Record of what was chosen
  - Judgmental: "authorization APPROVED"
  - Active: makes choice

RELATIONSHIP:
  Event X (authorization requested)
    → triggers review
    → Decision Y (approval / rejection)
    → may generate Event Z (decision recorded)

NOT EQUIVALENT:
  Events describe states
  Decisions select from alternatives
```

**Implication for schema:**
- Event stores immutable record
- Decision stores choice + rationale
- Event may have decision_id reference field, but Event ≠ Decision

**UNRESOLVED POINT:**
- Should Event schema include decision_id field?
- Can one Event trigger multiple Decisions?
- Should Event record Decision reference at all?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Decision layer owns relationship; Event unchanged
- If REVISED: Event needs decision_id field; schema changes
- If REJECTED: Different relationship model needed

---

### 6. Event ↔ Authority Relationship

**CURRENT PROPOSAL:**
```
EVENT:
  - Record of occurrence
  - Generated by any actor/process
  - No authority required to create

AUTHORITY:
  - Permission/right to take action
  - Assigned by governance process
  - Requires explicit decision

RELATIONSHIP:
  Authority (Phase 8 authorization)
    → permits
    → Event generation (Phase 8 monitoring starts)
    → can reference
    → Phase 8 evidence

NOT EQUIVALENT:
  Event existence ≠ authority to use it
  Event recording ≠ authorization for implementation
```

**Implication for schema:**
- Event has no authority_status field (events are recordings, not authority)
- Event may reference authority_id if it's about an authorization process
- Event lifecycle is independent from authorization status

**UNRESOLVED POINT:**
- Should monitoring events (Phase 8) include authority_binding reference?
- Can Events be recorded before authorization is granted?
- Who controls whether Events can be written?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Event schema remains authority-agnostic; no authority fields
- If REVISED: Event needs authority_id or authority_status field
- If REJECTED: Events must reference authority; schema changes needed

---

### 7. Event ↔ Runtime Relationship

**CURRENT PROPOSAL:**
```
CYCLE:
  1. Event recorded (what happened)
  2. Event used in analysis/detection (Evidence layer)
  3. Evidence evaluated (Decision layer)
  4. Decision triggers authorization (Authority layer)
  5. Authorization triggers runtime (Runtime layer)
  6. Runtime generates consequences (new Events)

SEQUENCE: Event → Evidence → Decision → Authority → Runtime → Event
```

**Implication for schema:**
- Event has timestamp (fixed point in sequence)
- Event has trace_id / related_event_id (sequence linkage)
- Event has lifecycle_phase (where in sequence it is)
- Event records input/output (before_state, after_state)

**UNRESOLVED POINT:**
- Is the sequence always linear or can it branch?
- How does hash chain (trace_id/related_event_id) handle parallel events?
- Should lifecycle_phase reflect position in this cycle?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Hash chain fields (trace_id, related_event_id) become operational requirement
- If REVISED: Different sequence model; hash chain redesign
- If REJECTED: No sequence linkage in schema

---

### 8. Event ↔ Actual Consequence Relationship

**CURRENT PROPOSAL:**
```
Consequences are recorded as new Events in Layer 1, which feed back into
the institutional memory chain.

Example consequence sequence:
  Event1: "Authorization request submitted"
    → Evidence: "Request is documented (Event1)"
    → Decision: "APPROVED Phase 8 monitoring"
    → Authority: "Phase 8 monitoring granted"
    → Runtime: "Monitoring system started"
    → Consequence Event: "Monitoring initialization complete" (new Event2)
    → back to Layer 1 Events

Consequences are Events, subject to same schema and immutability rules.
```

**UNRESOLVED POINT:**
- How do we distinguish consequence Events from primary Events?
- Should consequence_parent_id field exist?
- Can consequences trigger consequences (recursive)?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Consequences use same 31-column schema; no special handling
- If REVISED: Add consequence_parent_id or consequence marker
- If REJECTED: Consequences stored separately from Events

---

### 9. Event ↔ Institutional Memory Relationship

**CURRENT PROPOSAL:**
```
INSTITUTIONAL MEMORY LAYERS:
  Layer 1: Events (raw recordings)
    - Immutable source
    - Queryable for Layer 2+ analysis
    - Subject of investigation/review
    - Not self-authoritative (requires approval for use)

  Layer 2: Evidence (selected facts)
    - Selected from Events that are relevant to decisions
    - Validated facts selected for use

  Layer 3: Decisions (choices made)
    - Based on: Evidence review
    - Contains: Choice + rationale + alternatives

  Layer 4: Authority (permissions granted)
    - Result of: Explicit Human Gate decision
    - Contains: Scope, binding, lock status

  Layer 5: Rulings (resolved/closed decisions)
    - Formal closure of decision processes

  Layer 6: Consequences (actual outcomes)
    - Recorded as new Events
    - Feeds back to Layer 1

Event's Role:
  - Permanent (never deleted, only lifecycle_phase changed)
  - Queryable (full field access for analysis)
  - Traceable (provenance fields required)
  - Incomplete without interpretation layers above
```

**UNRESOLVED POINT:**
- Should Events include layer_source field (which layer created this)?
- Can an Event be reclassified between layers?
- Is Layer 1 immutability absolute or can Events be retracted?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Events are Layer 1 only; immutable except lifecycle_phase
- If REVISED: May need layer_source field or reclassification mechanism
- If REJECTED: Different layer model needed

---

### 10. Provenance / Integrity / Lifecycle / Versioning

**CURRENT PROPOSAL:**

**Provenance (source tracking):**
```
_source: 'live' (from GATE) | 'imported' | 'recovered' | 'test'
channel_type: 'gate' (PHI-OS GATE) | 'buffer' | 'direct' | 'other'
Purpose: Audit trail (source + channel track origin)
```

**Integrity (sequence validation):**
```
trace_id: Current event hash (sha256) from integrity.sign_event()
related_event_id: Previous event hash in chain
Purpose: Hash chain for sequence integrity and verification
verified_by: Optional field for verified/audited events
```

**Lifecycle (immutability model):**
```
lifecycle_phase: 'in_operation' (default) | 'archived' | 'superseded' | 'retracted' | other
Approach: Events never deleted, only lifecycle_phase changed
Allows: Query all events (including retracted) for audit trail reconstruction
```

**Versioning (schema evolution):**
```
schema_version: Default '1.0' (for future migrations)
Purpose: Enables forward compatibility
Migration path: Schema version enables future schema changes without breaking queries
```

**UNRESOLVED POINT:**
- Should trace_id always be SHA256 or support other hash algorithms?
- Can retracted events be un-retracted?
- What happens to hash chain if an event is retracted?
- How will schema_version be used for migrations?

**IMPLEMENTATION IMPACT:**
- If APPROVED: Hash chain fields become required for operational events; lifecycle_phase required
- If REVISED: Different hash algorithm? Different retraction model?
- If REJECTED: No hash chain; different provenance/integrity model

---

## STEP 2: HUMAN GATE DECISION QUESTIONS

**INSTRUCTIONS:**
Complete ONCE (all Q1-Q10 or none).  
Each question requires ONE selection.  
Provide notes for REVISE selections.

---

### Q1: Canonical Event Semantics

**Question:** Is the proposed Event definition (Section 1, above) the correct semantic for MoCKA?

Proposed: "Auditable record of state transition/action capturing WHO/WHAT/WHERE/WHY/WHEN/HOW/BEFORE/AFTER/PROVENANCE/LIFECYCLE"

**Decision:**

- [ ] **(A) APPROVE** — This is the correct Event semantic
- [ ] **(B) REVISE** — Semantic needs changes (specify below)
- [ ] **(C) REJECT** — Fundamentally wrong semantic

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q2: Required Fields

**Question:** Are the 14 proposed REQUIRED fields correct?

Proposed: event_id, when_ts, who_actor, who_role, who_session, what_type, title, where_component, where_path, why_purpose, how_trigger, _source, channel_type, lifecycle_phase, risk_level

**Decision:**

- [ ] **(A) APPROVE** — These 14 are the correct minimum
- [ ] **(B) REVISE** — Different fields should be required (specify below)
- [ ] **(C) REJECT** — Completely different requirement set needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q3: Optional / Conditional Fields

**Question:** Are the 17 proposed OPTIONAL fields appropriate?

Proposed optional: short_summary, description, before_state, after_state, trace_id, related_event_id, free_note, session_id, category_ab, target_class, change_type, impact_scope, impact_result, _imported_at, ai_actor, verified_by, pattern_score, recurrence_flag, severity

Proposed conditional: before_state/after_state (required for change events?), trace_id/related_event_id (required for chain?), verified_by (required if audited?)

**Decision:**

- [ ] **(A) APPROVE** — These optional/conditional fields are appropriate
- [ ] **(B) REVISE** — Different optional/conditional designation (specify below)
- [ ] **(C) REJECT** — Different optional field set needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q4: Actor & Authority Model

**Question:** Is the proposed actor/role/session model correct?

Proposed:
- who_actor: Actor identifier (Claude-sonnet-4-6, gpt-4o, username)
- who_role: Role (executor|auditor|human|automation)
- who_session: Session ID for correlation

Key principle: Event records WHO performed action, but Events themselves don't grant authority.

**Decision:**

- [ ] **(A) APPROVE** — Actor model is correct
- [ ] **(B) REVISE** — Modify actor/role/session structure (specify below)
- [ ] **(C) REJECT** — Different actor model needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q5: Event ↔ Evidence / Decision / Authority Relationship

**Question:** Is the proposed separation of Event/Evidence/Decision/Authority correct?

Proposed: Event records facts (immutable) → Evidence layer selects → Decision layer chooses → Authority layer grants → Runtime executes → Consequences as new Events

Key principle: Event existence ≠ authority to use it, Event recording ≠ authorization for implementation

**Decision:**

- [ ] **(A) APPROVE** — Separation is correct
- [ ] **(B) REVISE** — Modify relationships (specify below)
- [ ] **(C) REJECT** — Different relationship model needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q6: UNKNOWN / NULL / Missing Semantics

**Question:** Is the proposed NULL handling appropriate?

Proposed: Empty strings → NULL, OPTIONAL fields → can NULL, REQUIRED → must have value, CONDITIONAL → NULL okay if condition not met

**Decision:**

- [ ] **(A) APPROVE** — NULL handling is appropriate
- [ ] **(B) REVISE** — Different NULL semantics (specify below)
- [ ] **(C) REJECT** — Completely different approach needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q7: Provenance & Integrity

**Question:** Are the proposed provenance/integrity fields appropriate?

Proposed:
- Provenance: _source (live|imported|recovered|test), channel_type (gate|buffer|direct|other)
- Integrity: trace_id (current hash), related_event_id (previous hash), verified_by (optional auditor)

**Decision:**

- [ ] **(A) APPROVE** — Provenance/integrity fields are appropriate
- [ ] **(B) REVISE** — Modify provenance/integrity model (specify below)
- [ ] **(C) REJECT** — Different approach needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q8: Lifecycle & Versioning

**Question:** Is the proposed lifecycle/versioning model appropriate?

Proposed:
- lifecycle_phase: in_operation | archived | superseded | retracted | other
- Events never deleted, only lifecycle_phase changed
- schema_version: '1.0' for future migrations

**Decision:**

- [ ] **(A) APPROVE** — Lifecycle/versioning approach is appropriate
- [ ] **(B) REVISE** — Modify lifecycle phases or versioning (specify below)
- [ ] **(C) REJECT** — Different lifecycle model needed

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q9: Canonical Event Schema v1

**Question:** Should the proposed 31-column Canonical Event Schema v1 (summarized in Section 2, above) be APPROVED as the canonical production schema design?

**CRITICAL:** Approval = design acceptance only. Implementation authorization is Q10.

**Decision:**

- [ ] **(A) APPROVE** — Design is canonical, proceed to Q10 for implementation decision
- [ ] **(B) REVISE** — Design needs changes (specify below and iterate)
- [ ] **(C) REJECT** — Design not suitable, design new schema from scratch

**Notes (if REVISE/REJECT):**
```
[                                                          ]
```

---

### Q10: Implementation Authorization

**Question:** Should implementation of Canonical Event Schema be authorized?

**PREREQUISITE:** Can only be answered if Q9 = APPROVE

**Scope of "implementation":**
- Database initialization (CREATE TABLE events with schema v1)
- event_gate integration testing
- Read/list/direct-read implementation
- Evidence/Decision/Authority binding verification

**Scope of "NOT AUTHORIZED":**
- Phase 8 verification restart
- Authorization reconstruction
- Production lock changes
- RTB binding changes

**Decision:**

- [ ] **(A) NOT AUTHORIZED** — Approve design only, defer implementation
- [ ] **(B) AUTHORIZE AFTER Q9 APPROVAL** — Proceed to Phase 3 implementation if Q9 APPROVED
- [ ] **(C) N/A** — Q9 not approved, so Q10 decision not applicable

---

## STEP 3: DECISION LOGIC (Mechanical application)

```
IF Q1-Q8 contains REVISE or REJECT:
  CANONICAL_SCHEMA = NOT_APPROVED
  IMPLEMENTATION = NOT_AUTHORIZED

IF Q9 = REVISE:
  CANONICAL_SCHEMA = REVISION_REQUIRED
  IMPLEMENTATION = NOT_AUTHORIZED

IF Q9 = REJECT:
  CANONICAL_SCHEMA = REJECTED
  IMPLEMENTATION = NOT_AUTHORIZED

IF Q9 = APPROVE AND Q10 = NOT_AUTHORIZED:
  CANONICAL_SCHEMA = APPROVED
  IMPLEMENTATION = NOT_AUTHORIZED

IF Q9 = APPROVE AND Q10 = AUTHORIZE_AFTER_Q9_APPROVAL:
  CANONICAL_SCHEMA = APPROVED
  IMPLEMENTATION = AUTHORIZED_FOR_PHASE3_ONLY

IF Q10 = N/A (Q9 not approved):
  IMPLEMENTATION = NOT_AUTHORIZED
  (Skip Q10 entirely)
```

**CRITICAL CONSTRAINT:**
Even if Q10 = AUTHORIZE_AFTER_Q9_APPROVAL, the following remain NOT AUTHORIZED:
- Phase 8 Authorization changes
- RTB modification
- Production Lock changes
- Authority Model changes
- Evidence Ledger creation
- Any change outside schema implementation scope

---

## STEP 4: CURRENT LOCK (Maintained until Human Gate answers)

```
CANONICAL_SCHEMA = PROPOSED
IMPLEMENTATION = NOT_AUTHORIZED
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN
PHASE8_VERIFICATION = HALTED
RTB_20260918_001 = UNKNOWN / EVIDENCE_GAP
PRODUCTION_LOCK = UNKNOWN / EVIDENCE_GAP
DB_INITIALIZATION = NOT_AUTHORIZED
MCP_SCHEMA_IMPLEMENTATION = NOT_AUTHORIZED
```

---

## STEP 5: AFTER HUMAN GATE ANSWERS

Upon receipt of Human Gate Q1-Q10 answers:

1. **Record answers** verbatim (no AI interpretation)
2. **Apply decision logic** (STEP 3, mechanical)
3. **Create Decision Record** with answers + AI status updates
4. **Update CANONICAL_SCHEMA status** per decision logic
5. **Update IMPLEMENTATION status** per decision logic
6. **Separate AI interpretation from Human decision**
7. **If schema approved:** Present PHASE 3 scope only (no implementation started)
8. **If implementation authorized:** Present implementation prerequisites only
9. **If not approved:** Stop and await next directive
10. **Do NOT proceed with implementation without explicit authorization**

**Absolute rule:** Human Gate answers are final. No AI completion, inference, or supplementation of answers.

---

## PURPOSE STATEMENT

This decision process is NOT about adopting 31 columns.

**Purpose:** Establish what an Event is in MoCKA:
- What does MoCKA record?
- What structure carries auditable records?
- How do Events relate to Evidence, Decisions, Authority, Runtime?
- What immutability and traceability guarantees must Events have?

Once these questions are answered, implementation becomes possible.

---

**Status: AWAITING HUMAN GATE Q1-Q10 ANSWERS**

**原則: 止めるのは権限。進めるのは証拠。**
(Stopping is authority. Evidence is progress.)

No implementation, no database changes, no Phase 8 reopening.
All pending on Human Gate decision.
