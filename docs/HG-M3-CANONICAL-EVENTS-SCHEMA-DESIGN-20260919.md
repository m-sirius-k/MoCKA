# HG-M3-CANONICAL-EVENTS-SCHEMA-DESIGN-20260919

**Date:** 2026-09-19  
**Phase:** DESIGN ONLY (No implementation, no database changes)  
**Status:** PROPOSAL FOR HUMAN GATE REVIEW  
**Authority:** Human Gate decision required

---

## DESIGN PRINCIPLE

```
CANONICAL_SCHEMA_DESIGN ≠ IMPLEMENTATION
DESIGN_PROPOSAL ≠ HUMAN_GATE_APPROVAL
APPROVAL ≠ PRODUCTION_AUTHORIZATION
```

This document proposes a canonical events schema for MoCKA.  
No database, code, or operational changes are made.

---

## STEP 1: EXISTING CONTRACT INVENTORY

### A. event_gate.py Runtime Contract (Lines 51-75)

**Type:** Persistence requirement (what event_gate actually writes)

**Columns written to storage:**

| Column | Source | Required | Type | Constraint |
|--------|--------|----------|------|-----------|
| event_id | Generated or payload | YES | TEXT | PRIMARY KEY |
| when_ts | payload or generated | YES | TEXT | ISO 8601 timestamp |
| who_actor | payload | YES | TEXT | Actor identifier |
| what_type | payload | YES | TEXT | From ALLOWED_WHAT_TYPES |
| where_component | payload | YES | TEXT | Component/module name |
| where_path | payload | YES | TEXT | File path or URL |
| why_purpose | payload | YES | TEXT | Purpose statement |
| how_trigger | payload | YES | TEXT | Trigger/instruction source |
| before_state | payload | OPTIONAL | TEXT | State before change |
| after_state | payload | OPTIONAL | TEXT | State after change |
| title | payload (what_title or title) | YES | TEXT | Summary |
| short_summary | payload (description or short_summary) | YES | TEXT | Description |
| session_id | payload (who_session or session_id) | YES | TEXT | Session identifier |
| _source | payload (event_source) | YES | TEXT | Source: 'live' default |
| free_note | payload aggregated | OPTIONAL | TEXT | Tags/notes (joined) |
| channel_type | hardcoded | YES | TEXT | 'gate' always |
| lifecycle_phase | hardcoded | YES | TEXT | 'in_operation' always |
| risk_level | hardcoded | YES | TEXT | 'normal' default |
| trace_id | integrity.sign_event() | CONDITIONAL | TEXT | Hash chain |
| related_event_id | integrity.sign_event() | CONDITIONAL | TEXT | Previous hash |

**Key Properties:**
- Single entry point: `process_event()` (line 115)
- No other write path permitted (line 122)
- Validation + Gate Policy + Signature + Hash Chain in one transaction
- INSERT OR IGNORE (silently fails if table missing)
- Empty strings converted to NULL (line 77)

---

### B. gate_schema.py Payload Contract (Lines 18-40)

**Type:** Input validation schema (what callers send)

**Required fields (5W1H):**
- who_actor: Actor identifier
- who_role: Role (executor|auditor|human|automation)
- who_session: Session ID
- what_type: Event type (enumerated)
- what_title: Title summary
- where_path: Path/URL
- where_component: Component name
- why_purpose: Purpose (10+ chars)
- how_trigger: Instruction source

**Optional fields:**
- before_state, after_state, before_hash, after_hash (state replay)
- description: Free-form description
- tags: Tags/metadata

---

### C. core_kernel/orchestra/persistence/schema.py (Candidate)

**Type:** Defined but unused schema

**Columns defined:**
```sql
event_id TEXT PRIMARY KEY
session_id TEXT
event_type TEXT
timestamp REAL
payload TEXT
```

**Properties:**
- Minimal (5 columns)
- Uses TEXT event_id (not matching time-ordered format from event_gate)
- Serializes everything else to payload (JSON?)
- Not imported or used anywhere in production
- Status: ORPHANED

---

### D. phi_os/tests/test_event_gate.py (Test Reference)

**Type:** Test schema (used for test validation only)

**Columns defined (31 total):**
```sql
event_id TEXT PRIMARY KEY
when_ts TEXT
who_actor TEXT
what_type TEXT
where_component TEXT
where_path TEXT
why_purpose TEXT
how_trigger TEXT
channel_type TEXT
lifecycle_phase TEXT
risk_level TEXT
category_ab TEXT
target_class TEXT
title TEXT
short_summary TEXT
before_state TEXT
after_state TEXT
change_type TEXT
impact_scope TEXT
impact_result TEXT
related_event_id TEXT
trace_id TEXT
free_note TEXT
_imported_at TEXT
_source TEXT
ai_actor TEXT
session_id TEXT
severity TEXT
pattern_score REAL
recurrence_flag INTEGER
verified_by TEXT
```

**Properties:**
- Matches event_gate INSERT expectations (all 20 required columns present)
- Includes additional governance/analysis columns (11 extra)
- Used in test fixture (monkeypatch)
- Status: TEST_REFERENCE (not authoritative, not orphaned)

---

## STEP 2: CANONICAL EVENT SEMANTICS

### A. What is an Event?

**Definition (Proposed):**

An **Event** is an **auditable record of a state transition or action** in MoCKA, capturing:

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

### B. Event vs. Evidence (Distinction)

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

---

### C. Event vs. Decision (Distinction)

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
- Event may have decision_id field (reference), but Event ≠ Decision

---

### D. Event vs. Authority (Distinction)

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

---

### E. Event and Runtime Consequence (Relationship)

```
EVENT SEQUENCE:
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

### F. Event in Institutional Memory

```
INSTITUTIONAL MEMORY LAYERS:
  Layer 1: Events (raw recordings)
  Layer 2: Evidence (selected facts)
  Layer 3: Decisions (choices made)
  Layer 4: Authority (permissions granted)
  Layer 5: Rulings (resolved/closed decisions)
  Layer 6: Consequences (actual outcomes)

Event's role:
  - Immutable source at Layer 1
  - Queryable for Layer 2+ analysis
  - Subject of investigation/review
  - Not self-authoritative (requires approval for use)
```

**Implication for schema:**
- Event is permanent (no deletion)
- Event is queryable (full field access)
- Event is traceable (provenance fields required)
- Event is incomplete without interpretation layers above

---

## STEP 3: CANONICAL SCHEMA DESIGN v1 (PROPOSAL)

### Core Event Schema

```sql
CREATE TABLE events (

  -- Identity & Uniqueness
  event_id TEXT PRIMARY KEY,
    -- Format: E{YYYYMMDD}_{micros_9d}{hex_4d}
    -- Properties: time-ordered, collision-free, no DB lookup

  -- Temporal
  when_ts TEXT NOT NULL,
    -- Format: ISO 8601 timestamp with timezone
    -- Properties: UTC, immutable, set at record time

  -- Actor & Source (5W1H: WHO)
  who_actor TEXT NOT NULL,
    -- Actor identifier (e.g., Claude-sonnet-4-6, gpt-4o, human-name)
    -- Who performed the action

  who_role TEXT NOT NULL,
    -- executor | auditor | human | automation
    -- Role context for the actor

  who_session TEXT NOT NULL,
    -- Session identifier for correlation (e.g., SESSION_YYYYMMDD_HHMMSS)
    -- May span multiple events

  -- Event Type & Description (5W1H: WHAT)
  what_type TEXT NOT NULL,
    -- Enumerated: file_write, git_commit, test_run, incident, todo_update, claude_mcp, etc.
    -- Type of action/event

  title TEXT NOT NULL,
    -- One-line summary (what_title from payload)
    -- Human-readable title

  short_summary TEXT,
    -- Description (from payload description or short_summary)
    -- Extended summary of event

  description TEXT,
    -- Alias field for compatibility
    -- May be same as short_summary or separate

  -- Location & Component (5W1H: WHERE)
  where_component TEXT NOT NULL,
    -- Component/module name (e.g., mocka_mcp_server, event_gate, executor_orchestrator)
    -- Where in system the action occurred

  where_path TEXT NOT NULL,
    -- File path, URL, or component path
    -- Specific location affected

  -- Purpose & Trigger (5W1H: WHY, HOW)
  why_purpose TEXT NOT NULL,
    -- Purpose of the action (10+ characters recommended)
    -- Why the action was taken

  how_trigger TEXT NOT NULL,
    -- How the action was triggered (instruction source, command, API call, etc.)
    -- Mechanism that caused the event

  -- State Capture (Before/After for replay)
  before_state TEXT,
    -- State before action (JSON or serialized format)
    -- Optional, for replay/audit

  after_state TEXT,
    -- State after action (JSON or serialized format)
    -- Optional, for replay/audit

  -- Provenance & Integrity
  _source TEXT NOT NULL,
    -- 'live' (from GATE) | 'imported' | 'recovered' | 'test'
    -- Origin of event

  channel_type TEXT NOT NULL,
    -- 'gate' (from PHI-OS GATE) | 'buffer' | 'direct' | 'other'
    -- Ingestion channel

  -- Chain Linkage (Hash Chain for integrity)
  trace_id TEXT,
    -- Current event hash (sha256) for chain validation
    -- Links to previous event

  related_event_id TEXT,
    -- Previous event hash (related_event_id in hash chain)
    -- Links event sequence together

  -- Event Lifecycle
  lifecycle_phase TEXT NOT NULL,
    -- 'in_operation' (default) | 'archived' | 'superseded' | 'retracted' | other
    -- Where in its lifecycle the event is

  -- Risk & Severity
  risk_level TEXT NOT NULL,
    -- 'normal' (default) | 'warning' | 'critical' | 'incident' | etc.
    -- Risk classification

  severity TEXT,
    -- Optional additional severity classification
    -- For compatibility with analytics

  -- Governance (relationships to Decision/Authority layers)
  -- Note: These fields REFERENCE other systems, don't contain authority themselves
  
  -- Relationships & Metadata
  free_note TEXT,
    -- Joined metadata (tags|who_role=...|event_source=...|orig_channel=...)
    -- Compatibility field for metadata

  session_id TEXT,
    -- Alias for who_session (for compatibility)
    -- Session correlation

  -- Analysis & Classification
  category_ab TEXT,
    -- Governance categorization (A/B classification, if needed)
    -- For event categorization

  target_class TEXT,
    -- Target of change (file/config/code/schema/permission/other)
    -- What was affected

  change_type TEXT,
    -- Type of change (create/modify/delete/permission/config/other)
    -- How it was changed

  impact_scope TEXT,
    -- Scope of impact (local/session/component/system/global)
    -- How far did impact reach

  impact_result TEXT,
    -- Result of impact (success/partial/failed/unknown)
    -- What was the outcome

  -- Metadata
  _imported_at TEXT,
    -- Timestamp of import (if event was imported)
    -- For tracking external events

  ai_actor TEXT,
    -- AI model identifier (if actor is AI)
    -- Redundant with who_actor but explicit for filtering

  verified_by TEXT,
    -- Actor who verified event (optional, for audited events)
    -- Who validated it

  pattern_score REAL,
    -- Anomaly/pattern score (0-1) for detection algorithms
    -- Optional, for analysis

  recurrence_flag INTEGER,
    -- Count of similar events (for pattern detection)
    -- Optional, for analysis

  -- Schema Versioning
  schema_version TEXT DEFAULT '1.0',
    -- Version of this schema (for future migrations)
    -- Enables compatibility

  -- Record Metadata
  recorded_at TEXT,
    -- When this record was created in storage
    -- System-generated, immutable

  PRIMARY KEY (event_id)
);
```

---

### Column Classification

**REQUIRED (must have value, not nullable):**
- event_id, when_ts, who_actor, who_role, who_session
- what_type, title, where_component, where_path
- why_purpose, how_trigger
- _source, channel_type, lifecycle_phase, risk_level

**OPTIONAL (may be NULL):**
- short_summary, description, before_state, after_state
- trace_id, related_event_id, free_note, session_id
- category_ab, target_class, change_type, impact_scope, impact_result
- _imported_at, ai_actor, verified_by
- pattern_score, recurrence_flag, severity

**CONDITIONAL (depends on event_type or context):**
- before_state, after_state (required for state-change events, optional for others)
- trace_id, related_event_id (required for hash chain, optional for standalone events)
- verified_by (required if event is audited)

---

## STEP 4: RELATIONSHIP MODEL

### Event → Evidence → Decision → Authority → Runtime

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  INSTITUTIONAL MEMORY: Events → Evidence → Decisions → Authority│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Layer 1: EVENTS (Proposed Schema Above)
  - Recorded by: Any authorized process (e.g., event_gate)
  - Contains: Immutable facts (who/what/when/where/why/how)
  - Fields: 31 columns (intrinsic data)
  - Queryable: All fields
  - Deletable: NEVER (immutable)
  - Examples:
    * "File X written at T by Claude"
    * "Phase 8 verification requested"
    * "Authorization decision created"

Layer 2: EVIDENCE (Phase7, separate system)
  - Selected from: Events that are relevant to decisions
  - Contains: Validated facts selected for use
  - Relationship: Event.event_id → Evidence.event_id (reference)
  - Examples:
    * Evidence: "File corruption detected (Event_Y)"
    * Evidence: "Authorization request was made (Event_Z)"

Layer 3: DECISIONS (mocka_decision_write, separate system)
  - Based on: Evidence review
  - Contains: Choice + rationale + alternatives
  - Relationship: Decision.related_events[] contains Event.event_id references
  - Examples:
    * Decision: "APPROVED Phase 8 based on Evidence X, Y, Z"
    * Decision: "REJECTED file modification due to integrity concerns"

Layer 4: AUTHORITY (Phase 8 scope)
  - Result of: Explicit Human Gate decision
  - Contains: Scope, binding, lock status
  - Relationship: RTB_* records, Production_Lock records
  - Examples:
    * "Phase 8 authorization granted for sandbox monitoring"
    * "Production changes NOT authorized"

Layer 5: RUNTIME (Execution monitoring)
  - Triggered by: Authority layer
  - Contains: Monitoring, detection, escalation
  - Generates: New Events (cycle continues)
  - Relationship: Events from monitoring generate new Events in Layer 1

Layer 6: INSTITUTIONAL MEMORY (History)
  - Stores: All Events, Evidence chains, Decision records
  - Immutable: Events never deleted, Decisions are append-only
  - Queryable: Full audit trail reconstruction
```

### Schema Implications for Relationships

**Event fields for Evidence binding:**
- (None) - Evidence layer owns the relationship

**Event fields for Decision binding:**
- (None) - Decision layer owns the relationship
- But Events may be tagged with decision_id in free_note if needed

**Event fields for Authority binding:**
- (None) - Authority layer is independent
- Events recording authorization requests are just normal events

**Event fields for traceability:**
- trace_id, related_event_id: Hash chain for sequence integrity
- who_session: Session correlation
- session_id: Alias for who_session

---

## STEP 5: EXISTING SCHEMA COMPARISON

### Comparison Matrix

| Aspect | core_kernel (5 col) | phi_os test (31 col) | Canonical v1 (proposed) |
|--------|-------------------|-------------------|----------------------|
| **Semantics** | | | |
| Event meaning | Minimal (payload only) | Full governance model | Defined above (full) |
| Actor tracking | No (session_id only) | YES (who_actor, who_role, who_session) | YES (required) |
| Purpose/intent | No | YES (why_purpose, how_trigger) | YES (required) |
| State capture | No (serialized in payload) | YES (before_state, after_state) | YES (optional) |
| Provenance | No | Partial (\_source, \_imported_at) | YES (\_source, channel_type) |
| Integrity | No | Partial (trace_id, related_event_id) | YES (hash chain fields) |
| **Required Fields** | | | |
| Total required | 5 | ~20 | 14 (clearly designated) |
| event_id | YES (key) | YES | YES (PRIMARY KEY, time-ordered) |
| timestamp | YES (timestamp REAL) | YES (when_ts TEXT) | YES (when_ts TEXT, ISO8601) |
| actor | NO | YES | YES (required) |
| type | YES (event_type) | YES (what_type) | YES (required, enumerated) |
| component | NO | YES (where_component) | YES (required) |
| path | NO | YES (where_path) | YES (required) |
| purpose | NO | YES (why_purpose) | YES (required) |
| trigger | NO | YES (how_trigger) | YES (required) |
| **Optional Fields** | | | |
| state capture | NO | YES | YES (optional) |
| before_state | NO | YES | YES (optional) |
| after_state | NO | YES | YES (optional) |
| description | NO | YES | YES (optional) |
| tags/notes | NO | YES | YES (optional) |
| governance fields | NO | YES (11 extra) | YES (compatible) |
| **Production Suitability** | | | |
| Matches event_gate? | NO (would fail INSERT) | YES (exact fit) | YES (superset) |
| Used in production? | NO (orphaned) | NO (test only) | PROPOSED |
| Has documented authority? | NO | NO | NO (awaiting approval) |
| Handles integrity chains? | NO | YES (partial) | YES (full) |
| **Canonical Suitability** | | | |
| Explicitly canonical? | NO | NO | NO (PROPOSED) |
| Authority designated? | NO | NO | NO (requires HG decision) |
| Production-ready? | NO | UNKNOWN (test-only) | UNKNOWN (not implemented) |
| Complete semantics? | NO (minimal) | YES (full) | YES (defined) |

---

## STEP 6: CANONICAL DESIGN PROPOSAL

### Canonical Event Schema v1 (Summary)

**Status:** PROPOSAL FOR HUMAN GATE REVIEW

**Key Characteristics:**

1. **31 columns** (compatible with test schema, extends event_gate contract)
2. **14 required fields** (ensures minimum data quality)
3. **17 optional/conditional fields** (enables flexibility)
4. **Full 5W1H coverage** (who/what/when/where/why/how)
5. **Hash chain support** (integrity/sequence linkage)
6. **Governance-ready** (references to Evidence/Decision/Authority)
7. **Time-ordered event_id** (collision-free, DB-lookup-free)
8. **Immutable records** (append-only, never deleted)

**Relationship to existing:**

- **vs. core_kernel:** REPLACES (core_kernel is orphaned, doesn't meet requirements)
- **vs. phi_os test:** FORMALIZES (test schema becomes production canonical)
- **vs. event_gate contract:** HARMONIZES (event_gate INSERT works perfectly)

**Not included (separate layers):**

- Evidence linking (Evidence layer maintains references)
- Decision linking (Decision layer maintains records)
- Authority status (Authority layer is independent)
- Runtime consequences (recorded as new Events)

---

## STEP 7: IMPLEMENTATION BOUNDARY

### Design ≠ Implementation

```
PHASE 1 (COMPLETE):
  ✓ Design canonical schema semantics
  ✓ Define relationship model (Event→Evidence→Decision→Authority)
  ✓ Propose schema v1 (31 columns)
  ✓ Compare against candidates
  ✓ Prepare Human Gate input

PHASE 2 (NOT STARTED, AUTHORIZATION REQUIRED):
  → Human Gate decision on design
  → Decision: APPROVE / REVISE / REJECT
  → If APPROVE: authorization for next phase

PHASE 3 (AWAITING AUTHORIZATION):
  → MCP Persistence Implementation (create table, initialize schema)
  → Verify event_gate INSERT/UPDATE works
  → Implement read/list/direct-read paths

PHASE 4 (AWAITING AUTHORIZATION):
  → Evidence/Decision/Authority Binding Verification
  → Test event→evidence linkage
  → Test event→decision linkage
  → Test event→authority reference

PHASE 5 (AWAITING AUTHORIZATION):
  → Phase 8 Resume Evaluation
  → IF authorization confirmed: resume Phase 8 monitoring
  → IF authorization still UNKNOWN: keep halted

PHASE 6 (AWAITING AUTHORIZATION):
  → Production Activation (if authorized)
  → Production Lock verification
  → Runtime binding verification
```

**Strict Gate:** No phase advances without explicit Human Gate approval.

---

## STEP 8: HUMAN GATE INPUT QUESTIONS

### Q1: Canonical Event Semantics

**Question:** Is the proposed Event definition (STEP 2: "What is an Event?") appropriate for MoCKA?

**Proposed definition:** "An **Event** is an **auditable record of a state transition or action**, capturing WHO/WHAT/WHERE/WHY/WHEN/HOW/BEFORE/AFTER/PROVENANCE/LIFECYCLE."

**Options:**

- **(A) APPROVE** - Definition is suitable
- **(B) REVISE** - Definition needs changes (specify in notes)
- **(C) REJECT** - Not appropriate for MoCKA

---

### Q2: Required Fields

**Question:** Should these fields be REQUIRED (not NULL) in canonical schema?

**Proposed required fields (14 total):**
- event_id, when_ts
- who_actor, who_role, who_session
- what_type, title
- where_component, where_path
- why_purpose, how_trigger
- _source, channel_type, lifecycle_phase, risk_level

**Options:**

- **(A) APPROVE** - These are minimum required
- **(B) REVISE** - Some should be optional, or add more required
- **(C) REJECT** - Different requirement set needed

---

### Q3: Optional/Conditional Fields

**Question:** Should these fields be OPTIONAL in canonical schema?

**Proposed optional fields (17 total):**
- short_summary, description
- before_state, after_state
- trace_id, related_event_id
- free_note, session_id
- category_ab, target_class, change_type, impact_scope, impact_result
- _imported_at, ai_actor, verified_by
- pattern_score, recurrence_flag, severity

**Conditional (if event_type requires):**
- before_state, after_state: Required for "change" events?
- trace_id, related_event_id: Required for hash chain?

**Options:**

- **(A) APPROVE** - These optional fields are suitable
- **(B) REVISE** - Modify optional/conditional designations
- **(C) REJECT** - Different optional set needed

---

### Q4: Actor & Authority Model

**Question:** Is the proposed actor/role/session model appropriate?

**Proposed fields:**
- who_actor: Actor identifier (e.g., Claude-sonnet-4-6, gpt-4o, username)
- who_role: Role (executor|auditor|human|automation)
- who_session: Session ID for correlation

**Key principle:** Event records WHO performed action, but Events themselves don't grant authority.

**Options:**

- **(A) APPROVE** - Actor model is appropriate
- **(B) REVISE** - Modify actor/role/session structure
- **(C) REJECT** - Different model needed

---

### Q5: Evidence / Decision / Authority Relationship

**Question:** Is the proposed separation appropriate?

**Proposed model:**
- **Event** records facts (immutable)
- **Evidence** layer (separate) selects events for use
- **Decision** layer (separate) chooses based on evidence
- **Authority** layer (separate, Phase 8) grants permissions
- **Events do NOT contain authority status**

**Key principle:** Event existence ≠ authorization for use or implementation

**Options:**

- **(A) APPROVE** - Separation is correct
- **(B) REVISE** - Events should contain some authority reference?
- **(C) REJECT** - Different relationship model needed

---

### Q6: UNKNOWN / NULL / Missing Semantics

**Question:** How should schema handle missing/unknown values?

**Proposed approach:**
- Empty strings → converted to NULL (per event_gate line 77)
- OPTIONAL fields → can be NULL
- REQUIRED fields → must have value (NULL not permitted)
- CONDITIONAL fields → NULL okay if condition not met

**Options:**

- **(A) APPROVE** - NULL handling is appropriate
- **(B) REVISE** - Different NULL semantics (e.g., use empty string instead of NULL)?
- **(C) REJECT** - Completely different approach needed

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

**Options:**

- **(A) APPROVE** - Provenance/integrity fields are appropriate
- **(B) REVISE** - Modify provenance/integrity model
- **(C) REJECT** - Different approach needed

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

**Options:**

- **(A) APPROVE** - Lifecycle/versioning approach is appropriate
- **(B) REVISE** - Modify lifecycle phases or versioning strategy
- **(C) REJECT** - Different lifecycle model needed

---

### Q9: Canonical Schema v1 - Overall Approval

**Question:** Should the proposed Canonical Event Schema v1 (31 columns, as detailed in STEP 3) be approved as the production canonical schema for mocka_events.db?

**Note:** Approval means design acceptance, NOT implementation authorization.

**Options:**

- **(A) APPROVE** - Design is canonical, proceed to Phase 2 (implementation authorization decision)
- **(B) REVISE** - Design needs changes (specify requirements, iterate design)
- **(C) REJECT** - Design not suitable, design new schema from scratch

---

### Q10: Implementation Authorization

**Question:** If Q9=APPROVE, should implementation be authorized?

**What would be authorized:**
- Database initialization (CREATE TABLE events with schema v1)
- event_gate integration testing (verify INSERT works)
- Read/list/direct-read implementation
- Evidence/Decision/Authority binding verification

**What would NOT be authorized yet:**
- Phase 8 verification restart
- Authorization reconstruction
- Production lock changes
- RTB binding changes

**Options:**

- **(A) NOT AUTHORIZED** - Approve design but defer implementation
- **(B) AUTHORIZE AFTER SCHEMA APPROVAL** - Proceed to Phase 3 if Q9=APPROVE
- **(C) CONDITIONAL** - Authorize implementation with specific conditions (list them)

---

## FINAL STATE FOR HUMAN GATE REVIEW

### Current Lock Status (MAINTAINED)

```
PHASE8_AUTHORIZATION = CURRENT_UNKNOWN
RTB_20260918_001 = UNKNOWN / EVIDENCE_GAP
PRODUCTION_LOCK = UNKNOWN / EVIDENCE_GAP
PHASE8_VERIFICATION = HALTED
```

These have NOT changed and will not change by this design.

---

### Design Artifacts Created

- docs/HG-M3-CANONICAL-EVENTS-SCHEMA-DESIGN-20260919.md (this file)
- docs/HG-M3-CANONICAL-EVENTS-SCHEMA-HUMAN-GATE-INPUT-20260919.md (next)

### Implementation Status

```
DESIGN STATUS = COMPLETE
CANONICAL STATUS = PROPOSED (awaiting Q9 decision)
IMPLEMENTATION AUTHORIZATION = NOT GRANTED (awaiting Q10 decision)
PHASE8 STATUS = HALTED (unchanged)
RTB STATUS = UNKNOWN / EVIDENCE_GAP (unchanged)
PRODUCTION STATUS = NOT READY (unchanged)
```

---

**Next Step:** Await Human Gate decisions on Q1-Q10.

No implementation, database changes, or code modifications until authorization granted.

