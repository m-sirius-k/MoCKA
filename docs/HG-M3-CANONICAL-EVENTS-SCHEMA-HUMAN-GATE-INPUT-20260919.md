# HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-INPUT-20260919

**Date:** 2026-09-19  
**Directive:** HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-001  
**Status:** AWAITING HUMAN GATE DECISION  
**Classification:** HUMAN GATE DECISION REQUIRED

---

## STEP 1: DESIGN READ-BACK (Extracted from HG-M3-CANONICAL-EVENTS-SCHEMA-DESIGN-20260919.md)

### 1. Canonical Event Definition (Proposed)

From STEP 2.A of design document:

**An Event is an auditable record of a state transition or action in MoCKA, capturing:**

1. **WHO** did/observed it (actor, role, session)
2. **WHAT** happened (type, title, description)
3. **WHERE** it happened (component, path)
4. **WHY** it happened (purpose, trigger)
5. **WHEN** it happened (timestamp)
6. **HOW** it was triggered (instruction, channel)
7. **BEFORE/AFTER** states (optional replay)
8. **PROVENANCE** (signature, hash chain)
9. **LIFECYCLE** (creation → present state)
10. **RELATIONSHIPS** (related events, evidence, decisions)

**Scope:** An Event is a **record**, not **authority**.

---

### 2. Canonical Schema v1: 31 Column Field Meanings

| Column | Type | Meaning | Source |
|--------|------|---------|--------|
| event_id | TEXT PRIMARY KEY | Time-ordered unique identifier (E{YYYYMMDD}_{micros_9d}{hex_4d}) | Generated |
| when_ts | TEXT NOT NULL | ISO 8601 timestamp with timezone (UTC, immutable) | Payload or generated |
| who_actor | TEXT NOT NULL | Actor identifier (Claude-sonnet-4-6, gpt-4o, human-name) | Payload |
| who_role | TEXT NOT NULL | Role: executor / auditor / human / automation | Payload |
| who_session | TEXT NOT NULL | Session identifier for correlation (SESSION_YYYYMMDD_HHMMSS) | Payload |
| what_type | TEXT NOT NULL | Enumerated event type (file_write, git_commit, test_run, incident, todo_update, claude_mcp, etc.) | Payload |
| title | TEXT NOT NULL | One-line summary / human-readable title (from what_title) | Payload |
| short_summary | TEXT | Extended summary / description of event | Payload |
| description | TEXT | Alias field for compatibility (may equal short_summary or separate) | Payload |
| where_component | TEXT NOT NULL | Component/module name (mocka_mcp_server, event_gate, executor_orchestrator, etc.) | Payload |
| where_path | TEXT NOT NULL | File path, URL, or component path (specific location affected) | Payload |
| why_purpose | TEXT NOT NULL | Purpose of action (10+ characters recommended) | Payload |
| how_trigger | TEXT NOT NULL | How action was triggered (instruction source, command, API call, etc.) | Payload |
| before_state | TEXT | State before change (JSON or serialized format) - optional, for replay/audit | Payload |
| after_state | TEXT | State after change (JSON or serialized format) - optional, for replay/audit | Payload |
| _source | TEXT NOT NULL | Origin: 'live' (from GATE) / 'imported' / 'recovered' / 'test' | Payload (default 'live') |
| channel_type | TEXT NOT NULL | Ingestion channel: 'gate' (PHI-OS GATE) / 'buffer' / 'direct' / 'other' | Hardcoded 'gate' |
| trace_id | TEXT | Current event hash (sha256) from integrity.sign_event() - for chain validation | Integrity |
| related_event_id | TEXT | Previous event hash in chain (related_event_id) - links event sequence | Integrity |
| lifecycle_phase | TEXT NOT NULL | Event lifecycle state: 'in_operation' (default) / 'archived' / 'superseded' / 'retracted' / other | Hardcoded 'in_operation' |
| risk_level | TEXT NOT NULL | Risk classification: 'normal' (default) / 'warning' / 'critical' / 'incident' / etc. | Hardcoded 'normal' |
| severity | TEXT | Optional additional severity classification (for compatibility with analytics) | Optional |
| free_note | TEXT | Joined metadata (tags / who_role=... / event_source=... / orig_channel=...) | Payload |
| session_id | TEXT | Alias for who_session (for compatibility and session correlation) | Payload |
| category_ab | TEXT | Governance categorization (A/B classification, if needed) | Optional |
| target_class | TEXT | Target of change (file / config / code / schema / permission / other) | Optional |
| change_type | TEXT | Type of change (create / modify / delete / permission / config / other) | Optional |
| impact_scope | TEXT | Scope of impact (local / session / component / system / global) | Optional |
| impact_result | TEXT | Result of impact (success / partial / failed / unknown) | Optional |
| _imported_at | TEXT | Timestamp of import (if event was imported from external source) | Optional |
| ai_actor | TEXT | AI model identifier (if actor is AI - redundant with who_actor but explicit for filtering) | Optional |
| verified_by | TEXT | Actor who verified event (optional, for audited events) | Optional |
| pattern_score | REAL | Anomaly/pattern score (0-1) for detection algorithms (optional, for analysis) | Optional |
| recurrence_flag | INTEGER | Count of similar events (for pattern detection - optional, for analysis) | Optional |

Note: Additional fields in proposal (schema_version, recorded_at) are for versioning/metadata.

---

### 3. Column Classification (REQUIRED / OPTIONAL / CONDITIONAL)

**REQUIRED (must have value, not nullable):**
```
event_id, when_ts
who_actor, who_role, who_session
what_type, title
where_component, where_path
why_purpose, how_trigger
_source, channel_type, lifecycle_phase, risk_level
```
Total: 14 required fields

**OPTIONAL (may be NULL):**
```
short_summary, description
before_state, after_state
trace_id, related_event_id
free_note, session_id
category_ab, target_class, change_type, impact_scope, impact_result
_imported_at, ai_actor, verified_by
pattern_score, recurrence_flag, severity
```
Total: 17 optional fields

**CONDITIONAL (depends on event_type or context):**
- before_state, after_state: Required for state-change events, optional for others
- trace_id, related_event_id: Required for hash chain continuation, optional for standalone events
- verified_by: Required if event is audited, optional otherwise

---

### 4. Event ↔ Evidence Relationship

**Event:**
- Auditable record of action/state transition
- Recorded by process/system
- Can be written without authority decision
- Example: "File X was written at time T by actor A"

**Evidence:**
- Fact used in decision-making
- Must be selected/validated for use
- Might require human judgment
- Example: "Evidence that file corruption occurred (from Event Y)"

**Relationship:**
```
Event → (filtered/validated) → Evidence
```

**NOT EQUIVALENT:**
- Not all events are evidence
- Not all evidence comes from events

**Implication for schema:**
- Event has intrinsic fields (who/what/when/how)
- Event may reference evidence but doesn't create it
- Evidence layer is separate (Phase7 Evidence Layer)

---

### 5. Event ↔ Decision Relationship

**Event:**
- Record of what happened
- Factual: "authorization was requested"
- Passive: records action

**Decision:**
- Record of what was chosen
- Judgmental: "authorization APPROVED"
- Active: makes choice

**Relationship:**
```
Event X (authorization requested)
  → triggers review
  → Decision Y (approval / rejection)
  → may generate Event Z (decision recorded)
```

**NOT EQUIVALENT:**
- Events describe states
- Decisions select from alternatives

**Implication for schema:**
- Event stores immutable record
- Decision stores choice + rationale
- Event may have decision_id reference field, but Event ≠ Decision

---

### 6. Event ↔ Authority Relationship

**Event:**
- Record of occurrence
- Generated by any actor/process
- No authority required to create

**Authority:**
- Permission/right to take action
- Assigned by governance process
- Requires explicit decision

**Relationship:**
```
Authority (Phase 8 authorization)
  → permits
  → Event generation (Phase 8 monitoring starts)
  → can reference
  → Phase 8 evidence
```

**NOT EQUIVALENT:**
- Event existence ≠ authority to use it
- Event recording ≠ authorization for implementation

**Implication for schema:**
- Event has no authority_status field (events are recordings, not authority)
- Event may reference authority_id if it's about an authorization process
- Event lifecycle is independent from authorization status

---

### 7. Event ↔ Runtime Relationship

**Runtime Consequence Sequence:**
```
1. Event recorded (what happened)
2. Event used in analysis/detection (Evidence layer)
3. Evidence evaluated (Decision layer)
4. Decision triggers authorization (Authority layer)
5. Authorization triggers runtime (Runtime layer)
6. Runtime generates consequences (new Events)

CYCLE: Event → Evidence → Decision → Authority → Runtime → Event
```

**Implication for schema:**
- Event has timestamp (fixed point in sequence)
- Event has trace_id / related_event_id (sequence linkage)
- Event has lifecycle_phase (where in sequence it is)
- Event records input/output (before_state, after_state)

---

### 8. Event ↔ Actual Consequence Relationship

**From the cycle above:**

Consequences are **recorded as new Events** in Layer 1, which feed back into the institutional memory chain.

Example consequence sequence:
```
Event1: "Authorization request submitted"
  → Evidence: "Authorization request is documented (Event1)"
  → Decision: "APPROVED Phase 8 monitoring"
  → Authority: "Phase 8 monitoring granted for sandbox"
  → Runtime: "Monitoring system started"
  → Consequence Event: "Monitoring system initialization complete" (new Event2)
  → back to Layer 1 Events
```

**Not a separate layer:** Consequences are Events, subject to same schema and immutability rules.

---

### 9. Event ↔ Institutional Memory Relationship

**Institutional Memory Layers:**
```
Layer 1: Events (raw recordings)
  - Immutable source
  - Queryable for Layer 2+ analysis
  - Subject of investigation/review
  - Not self-authoritative (requires approval for use)

Layer 2: Evidence (selected facts)
  - Selected from Events that are relevant to decisions
  - Validated facts selected for use
  - Relationship: Event.event_id → Evidence.event_id

Layer 3: Decisions (choices made)
  - Based on: Evidence review
  - Contains: Choice + rationale + alternatives
  - Relationship: Decision.related_events[] contains Event.event_id references

Layer 4: Authority (permissions granted)
  - Result of: Explicit Human Gate decision
  - Contains: Scope, binding, lock status
  - Relationship: RTB_* records, Production_Lock records

Layer 5: Rulings (resolved/closed decisions)
  - Formal closure of decision processes
  - Recorded in Decision Ledger

Layer 6: Consequences (actual outcomes)
  - Recorded as new Events
  - Feeds back to Layer 1
```

**Event's Role:**
- Permanent (never deleted, only lifecycle_phase changed)
- Queryable (full field access for analysis)
- Traceable (provenance fields required)
- Incomplete without interpretation layers above

---

### 10. Provenance / Integrity / Lifecycle / Versioning

**Provenance:**
- _source field: 'live' (from GATE) / 'imported' / 'recovered' / 'test'
- channel_type field: 'gate' (PHI-OS GATE) / 'buffer' / 'direct' / 'other'
- Purpose: Audit trail (source + channel track origin)

**Integrity:**
- trace_id: Current event hash (sha256) from integrity.sign_event()
- related_event_id: Previous event hash in chain (hash chain)
- Purpose: Hash chain for sequence integrity and verification
- verified_by: Optional field for verified/audited events

**Lifecycle:**
- lifecycle_phase: 'in_operation' (default) / 'archived' / 'superseded' / 'retracted' / other
- Approach: Events never deleted, only lifecycle_phase changed
- Allows: Query all events (including retracted) for audit trail reconstruction

**Versioning:**
- schema_version: Default '1.0' (for future migrations)
- Purpose: Enables forward compatibility
- Migration path: Schema version enables future schema changes without breaking existing queries

---

## STEP 2: HUMAN GATE QUESTION SHEET

**INSTRUCTIONS:**
- Answer each question with ONE selection (APPROVE / REVISE / REJECT, or specific options for Q10)
- Add notes if REVISE selected (specify what needs to change)
- No AI pre-answers or completions
- All 10 questions required for next phase authorization

---

### Q1: Canonical Event Semantics

**Question:** Is the proposed Event definition (above, Section 1) appropriate for MoCKA?

**Proposed definition:** "An auditable record of a state transition or action, capturing WHO/WHAT/WHERE/WHY/WHEN/HOW/BEFORE/AFTER/PROVENANCE/LIFECYCLE."

**Decision:**

- [ ] **(A) APPROVE** - Definition is suitable
- [ ] **(B) REVISE** - Definition needs changes (specify in notes)
- [ ] **(C) REJECT** - Not appropriate for MoCKA

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q2: Required Fields

**Question:** Should these 14 fields be REQUIRED (not NULL) in canonical schema?

**Proposed required fields:**
```
event_id, when_ts
who_actor, who_role, who_session
what_type, title
where_component, where_path
why_purpose, how_trigger
_source, channel_type, lifecycle_phase, risk_level
```

**Decision:**

- [ ] **(A) APPROVE** - These 14 are minimum required
- [ ] **(B) REVISE** - Some should be optional, or add more required
- [ ] **(C) REJECT** - Different requirement set needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q3: Optional / Conditional Fields

**Question:** Should these 17 fields be OPTIONAL in canonical schema?

**Proposed optional fields:**
```
short_summary, description
before_state, after_state
trace_id, related_event_id
free_note, session_id
category_ab, target_class, change_type, impact_scope, impact_result
_imported_at, ai_actor, verified_by
pattern_score, recurrence_flag, severity
```

**Conditional (if event_type requires):**
```
before_state, after_state: Required for state-change events?
trace_id, related_event_id: Required for hash chain?
verified_by: Required if event is audited?
```

**Decision:**

- [ ] **(A) APPROVE** - These optional/conditional fields are suitable
- [ ] **(B) REVISE** - Modify optional/conditional designations
- [ ] **(C) REJECT** - Different optional set needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q4: Actor & Authority Model

**Question:** Is the proposed actor/role/session model appropriate?

**Proposed fields:**
- who_actor: Actor identifier (Claude-sonnet-4-6, gpt-4o, username)
- who_role: Role (executor|auditor|human|automation)
- who_session: Session ID for correlation

**Key principle:** Event records WHO performed action, but Events themselves don't grant authority.

**Decision:**

- [ ] **(A) APPROVE** - Actor model is appropriate
- [ ] **(B) REVISE** - Modify actor/role/session structure
- [ ] **(C) REJECT** - Different model needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q5: Event / Evidence / Decision / Authority Relationship

**Question:** Is the proposed separation appropriate?

**Proposed model:**
- **Event** records facts (immutable)
- **Evidence** layer (separate) selects events for use
- **Decision** layer (separate) chooses based on evidence
- **Authority** layer (separate, Phase 8) grants permissions
- **Events do NOT contain authority status**

**Key principle:** Event existence ≠ authorization for use or implementation

**Decision:**

- [ ] **(A) APPROVE** - Separation is correct
- [ ] **(B) REVISE** - Events should contain some authority reference?
- [ ] **(C) REJECT** - Different relationship model needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q6: UNKNOWN / NULL / Missing Semantics

**Question:** How should schema handle missing/unknown values?

**Proposed approach:**
- Empty strings → converted to NULL (per event_gate)
- OPTIONAL fields → can be NULL
- REQUIRED fields → must have value (NULL not permitted)
- CONDITIONAL fields → NULL okay if condition not met

**Decision:**

- [ ] **(A) APPROVE** - NULL handling is appropriate
- [ ] **(B) REVISE** - Different NULL semantics (e.g., use empty string instead of NULL)?
- [ ] **(C) REJECT** - Completely different approach needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q7: Provenance & Integrity

**Question:** Are the proposed provenance/integrity fields appropriate?

**Proposed fields:**
- _source: 'live' | 'imported' | 'recovered' | 'test'
- channel_type: 'gate' | 'buffer' | 'direct' | 'other'
- trace_id: Current event hash (sha256) from integrity.sign_event()
- related_event_id: Previous event hash (hash chain)
- verified_by: Actor who verified (optional)

**Supports:**
- Audit trail (source + channel)
- Integrity chains (trace_id + related_event_id)
- Verification (verified_by field)

**Decision:**

- [ ] **(A) APPROVE** - Provenance/integrity fields are appropriate
- [ ] **(B) REVISE** - Modify provenance/integrity model
- [ ] **(C) REJECT** - Different approach needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q8: Lifecycle & Versioning

**Question:** Are lifecycle/versioning approaches appropriate?

**Proposed:**
- lifecycle_phase: 'in_operation' | 'archived' | 'superseded' | 'retracted' | other
- schema_version: '1.0' (for future migrations)
- Immutability: Events never deleted, only lifecycle_phase changed

**Implications:**
- Retracted events remain in database (can be queried)
- Schema version enables forward compatibility
- Migration path for future schema changes

**Decision:**

- [ ] **(A) APPROVE** - Lifecycle/versioning approach is appropriate
- [ ] **(B) REVISE** - Modify lifecycle phases or versioning strategy
- [ ] **(C) REJECT** - Different lifecycle model needed

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q9: Canonical Event Schema v1 - Overall Approval

**Question:** Should the proposed Canonical Event Schema v1 (31 columns, as detailed in Section 2 above) be approved as the production canonical schema for mocka_events.db?

**Note:** Approval means design acceptance, NOT implementation authorization. Implementation decision is Q10.

**Current status of proposal:**
- Status: PROPOSED
- Authority: Not yet human-approved
- Implementation: Not authorized

**Decision:**

- [ ] **(A) APPROVE** - Design is suitable, proceed to Q10 (implementation authorization decision)
- [ ] **(B) REVISE** - Design needs changes (specify requirements, iterate design)
- [ ] **(C) REJECT** - Design not suitable, design new schema from scratch

**Notes (if REVISE or REJECT):**
```
[  ]
```

---

### Q10: Implementation Authorization

**Question:** If Q9 APPROVED, should implementation be authorized?

**What implementation would include:**
- Database initialization (CREATE TABLE events with schema v1)
- event_gate integration testing (verify INSERT works)
- Read/list/direct-read implementation
- Evidence/Decision/Authority binding verification

**What would NOT be authorized yet:**
- Phase 8 verification restart
- Authorization reconstruction
- Production lock changes
- RTB binding changes

**Note:** Q10 can only be answered if Q9=APPROVE. If Q9=REVISE or REJECT, skip Q10.

**Decision:**

- [ ] **(A) NOT AUTHORIZED** - Approve design but defer implementation
- [ ] **(B) AUTHORIZE AFTER SCHEMA APPROVAL** - Proceed to Phase 3 if Q9 APPROVED
- [ ] **(C) CONDITIONAL** - Authorize implementation with specific conditions (list them)
- [ ] **(D) N/A** - Q9 not approved, so Q10 decision not applicable

**Conditions (if C selected):**
```
[  ]
```

---

## STEP 3: HUMAN DECISION RULE

AI SHALL NOT:
- Complete/answer Q1-Q10 on behalf of Human Gate
- Pre-select options
- Infer Human Gate intent
- Generate implementation based on design alone

AI SHALL:
- Maintain Q1-Q10 unanswered until Human Gate input received
- Preserve CANONICAL_SCHEMA = PROPOSED status
- Preserve IMPLEMENTATION = NOT_AUTHORIZED status
- Record all Human Gate decisions in Decision Ledger when received

**Enforcement:**
- If Q9 = REVISE or REJECT: Implementation remains NOT_AUTHORIZED
- If Q9 = APPROVE but Q10 = NOT_AUTHORIZED: Implementation remains NOT_AUTHORIZED
- If Q9 = APPROVE and Q10 = AUTHORIZE AFTER SCHEMA APPROVAL: Proceed to Phase 3
- If Q9 = APPROVE and Q10 = CONDITIONAL: Evaluate conditions before Phase 3

---

## STEP 4: CURRENT LOCK STATUS (UNCHANGED)

**Verified re-confirmed from design document:**

```
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN
PHASE8_VERIFICATION = HALTED
RTB_20260918_001 = UNKNOWN / EVIDENCE_GAP
PRODUCTION_LOCK = UNKNOWN / EVIDENCE_GAP
MCP_PERSISTENCE = NOT_READY
DB_INITIALIZATION = NOT_AUTHORIZED
CANONICAL_SCHEMA = PROPOSED (awaiting Q9 decision)
IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED (awaiting Q10 decision)
```

These locks are independent of design document status. No changes have been made to Phase 8, authority, or production state by this design phase.

---

## STEP 5: STOP

**Human Gate Input Ticket Complete**

Awaiting Human Gate decisions on Q1-Q10.

No implementation work will proceed.
No AI judgment will be applied to questions.
All Human Gate answers will be recorded in Decision Ledger upon receipt.

**原則: 止めるのは権限。進めるのは証拠。**  
(Stopping is authority. Evidence is progress.)

**Status:** HALTED - AWAITING HUMAN GATE INPUT
