# STEP 17 Phase 2-A: Pre-Decision Evidence Architecture Investigation
**Date:** 2026-09-21  
**Authorization:** HG-D9-5 = B (Sandbox investigation/implementation)  
**Scope:** Design and architecture investigation ONLY - NO CODE CHANGE  
**Objective:** Determine sandbox architecture for Pre-Decision Evidence as canonical institutional record

---

## 1. Execution Timeline: Decision Point and Evidence Availability

### 1.1 Chronological Sequence (VERIFIED)
```
T0: Intent received (intent_id available)
    ↓
T1: Intent → Goal → Plan (plan_id generated)
    ↓
T2: Plan loaded and validated
    - intent_id ✓ AVAILABLE
    - plan_id ✓ AVAILABLE
    - steps[] ✓ AVAILABLE
    - action_ids[] ✓ AVAILABLE
    ↓
T3: GOVERNANCE EVALUATION → Decision formed
    - decision_record_id generated (UUID)
    - governance_decision (PASS/WARNING/FAIL)
    ↓ **← HG-D1 DECISION POINT: Evidence must exist here**
    ↓
T4: HG AUTHORIZATION
    - hg_decision (AUTHORIZED/DENIED/etc.)
    ↓
T5: EXECUTION (per-action loop)
    - execution_id generated
    - action executed
    ↓
T6: Event generation
    - Event created (governance_block OR explicit mocka_write_event)
    - event_id generated
    - request_id stored
    ↓
T7: POST-EXECUTION
    - Result evaluation
    ↓
T8: EVIDENCE GENERATION (COULD HAPPEN)
    - Evidence record created from events.db
    - NOT currently persisted
```

### 1.2 Critical Timing Constraint
- **HG-D1:** Decision at T3 requires Evidence
- **Current:** Evidence can only be generated from events at T8 (AFTER execution at T5)
- **Gap:** T3 → T8 (Evidence needs to exist 5 stages before it can be generated from events)

---

## 2. Plan Metadata Available at Decision Time (T3): VERIFIED

### 2.1 Plan Structure
**Location:** runtime/plan_validator.py (line 17-89)

```python
Plan {
  intent_id: str       # ✓ REQUIRED, available at T1
  plan_id: str         # ✓ REQUIRED, available at T1
  steps: list[str]     # ✓ REQUIRED, available at T2
  action_ids: list[str]  # Format: "{intent_id}:{step_index}", available at T2
  # Additional fields (optional but present in CURRENT plans):
  # - validation_status
  # - created_at
  # - modified_at
}
```

**Status:** ALL plan metadata is AVAILABLE at T2, which is BEFORE T3 Decision point.

### 2.2 Execution Context Tracking (VERIFIED)
**Location:** runtime/execution_context.py (line 15-95)

ExecutionContext carries:
```
intent_id              # ✓ From Plan
plan_id                # ✓ From Plan
action_id              # ✓ Per-step: {intent_id}:{step_index}
decision_record_id     # ✓ Generated at T3 (governance evaluation)
governance_decision    # ✓ Generated at T3
hg_decision            # ✓ Generated at T4
execution_id           # ✓ Generated at T5
```

**Status:** Complete identity chain AVAILABLE at decision time (T3).

---

## 3. Event Database Architecture: VERIFIED

### 3.1 Events Table Schema
**Location:** phi_os/tests/test_integrity.py (EVENTS_SCHEMA)

```sql
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    when_ts TEXT,
    who_actor TEXT,
    what_type TEXT,
    where_component TEXT,
    where_path TEXT,
    why_purpose TEXT,
    how_trigger TEXT,
    channel_type TEXT,
    lifecycle_phase TEXT,
    risk_level TEXT,
    category_ab TEXT,
    target_class TEXT,
    title TEXT,
    short_summary TEXT,
    before_state TEXT,
    after_state TEXT,
    change_type TEXT,
    impact_scope TEXT,
    impact_result TEXT,
    related_event_id TEXT,
    trace_id TEXT,
    free_note TEXT,
    _imported_at TEXT,
    _source TEXT,
    ai_actor TEXT,
    session_id TEXT,
    severity TEXT,
    pattern_score REAL,
    recurrence_flag INTEGER,
    verified_by TEXT
    -- NOTE: request_id field written by event_gate.py (line 75) 
    --       but NOT in test schema; likely in production schema
)
```

### 3.2 Missing Identity Fields (CRITICAL)
- **NOT IN SCHEMA:** plan_id
- **NOT IN SCHEMA:** action_id
- **NOT IN SCHEMA:** decision_record_id
- **NOT IN SCHEMA:** execution_id
- **NOT IN SCHEMA:** intent_id
- **NOT IN SCHEMA:** evidence_id

**Status:** Events cannot reference Plan scope. Therefore, Evidence generated from events cannot be Plan-specific.

### 3.3 Event Generation Triggers (VERIFIED)
**Locations:** 
- mocka_mcp_server.py (governance block at line 283-335)
- phi_os/event_gate.py (process_event entry point at line 116-136)

**Events are created ONLY when:**
1. Governance blocks execution (_record_governance_block)
2. mocka_write_event() is called explicitly
3. **NOT automatically on Plan completion/execution**

**Status:** No automatic event generation from Plan execution.

---

## 4. Evidence Schema and Generation: VERIFIED / PARTIAL

### 4.1 RuntimeEvidenceRecord Schema (VERIFIED)
**Location:** governance/write_path/evidence/schema.py

```python
RuntimeEvidenceRecord {
  record_id: str                  # RER_YYYYMMDD_NNN
  source_event_range: {
    from_event_id: str           # ← Links to events.db
    to_event_id: str             # ← Links to events.db
    event_count: int
  },
  hash: str                       # SHA256(events JSON)
  hash_method_spec: str           # "sha256_json_sorted_v1"
  generated_at: str               # ISO8601 UTC
  generated_by: str               # session_id or AI identifier
  governance_anchor_hash: str?    # Optional
  immutable: bool                 # Always True (append-only)
}
```

### 4.2 Current Evidence Generator (VERIFIED)
**Location:** governance/write_path/runtime/generator.py (line 42-70)

```python
def generate_evidence_record(generated_by: str) -> dict:
    # Reads ALL events from mocka_events.db (readonly)
    rows = _read_events_readonly()
    # Hash entire events dataset
    digest = hashlib.sha256(json.dumps(rows, ...))
    # Create record
    record = {
        "record_id": f"RER_{YYYYMMDD}_{digest[:8]}",
        "source_event_range": {
            "from_event_id": rows[0]["event_id"] if rows else "",
            "to_event_id": rows[-1]["event_id"] if rows else "",
            "event_count": len(rows),
        },
        "hash": digest,
        ...
    }
    # Returns in-memory record (NOT persisted)
    return record
```

**Status:**
- ✓ Generator implemented
- ✓ Signature/integrity checking implemented
- ✗ Persistence NOT implemented
- ✗ Called from: NOWHERE in production code
- ✗ Result stored: NOWHERE (in-memory only)

### 4.3 Evidence Persistence: NOT VERIFIED
**Expected locations:**
- vasai_evidence.db: NOT FOUND in filesystem
- data/evidence/: EXISTS but EMPTY (.gitkeep only)
- governance/write_path/runtime/: Generator exists, persistence path UNDEFINED

**Status:** No canonical Evidence persistence location has been established.

---

## 5. Decision Ledger (Separate Record Type): VERIFIED

### 5.1 Decision Ledger Implementation (VERIFIED)
**Location:** mocka_mcp_server.py (line 76-78, 1107-1168)

```
DECISION_LEDGER_PATH = data/decisions/decision_ledger.jsonl
```

**Decision Ledger contains:**
- decision_id (DC_YYYYMMDD_NNN format)
- title
- context
- alternatives (list of rejected options with reasons)
- decision (selected choice)
- rationale (justification)
- impact (consequences)
- related_events (list of event_ids)
- related_documents
- approved_by (decision authority)
- status (Active / Superseded / Withdrawn)
- supersedes (reference to previous decision)

**Format:** JSONL (append-only, immutable per record)

**Status:**
- ✓ Decision Ledger exists
- ✓ mocka_decision_write() MCP tool available
- ✓ Append-only semantics enforced
- ✓ File exists at data/decisions/decision_ledger.jsonl

### 5.2 Decision ↔ Evidence Relationship
**Current:** Decision Ledger has `related_events` field but NO `related_evidence_records` field

**Status:** Decision can reference Events, but not Evidence records.

---

## 6. Pre-Decision Evidence vs. Post-Execution Evidence: ARCHITECTURAL DISTINCTION

### 6.1 Pre-Decision Evidence (HG-D9-4 = C)
```
Definition: Evidence created BEFORE execution, based on Plan metadata
Inputs:     Plan (intent_id, plan_id, steps, action_ids) + optional context
Timing:     T2-T3 (before Decision formed)
Purpose:    Decision rationale basis (HG-D1 compliance)
Storage:    NEW record type (separate from Post-Execution Evidence)
Record ID:  PER_YYYYMMDD_NNN (Pre-Execution Record)
Scope:      Plan-specific (cannot be all-events snapshot)
Validation: Plan structure, internal consistency
```

### 6.2 Post-Execution Evidence (HG-D9-4 = C)
```
Definition: Evidence created AFTER execution, based on Events
Inputs:     mocka_events.db (snapshot of all recorded events)
Timing:     T8+ (after execution complete)
Purpose:    Execution result verification, assessment, audit trail
Storage:    EXISTING schema (RER_YYYYMMDD_NNN)
Scope:      All events (or filtered event range)
Validation: Event integrity, signature chain, hash verification
```

### 6.3 Key Distinction
**HG-D9-4 Decision:**
> Post-Execution Evidence によって、過去のDecision rationaleを事後的に正当化することはできない。

**Implication:**
- Two DIFFERENT Evidence classes
- Pre-Decision Evidence ≠ Post-Execution Evidence
- Mixing them violates institutional integrity

---

## 7. Identity Binding Architecture: UNRESOLVED

### 7.1 Current Identity Chain
```
intent_id
  ↓ (generated)
plan_id
  ↓ (available at T1-T2)
action_id {intent_id}:{step_index}
  ↓ (available at T2)
decision_record_id
  ↓ (generated at T3)
hg_decision
  ↓ (generated at T4)
execution_id
  ↓ (generated at T5, from execution-runtime-system)
request_id
  ↓ (extracted from JSON-RPC, MCP tool-call level)
event_id
  ↓ (generated at T6 when event created)
?evidence_id
  ↓ (UNDEFINED)
```

### 7.2 Binding Mechanisms: CANDIDATE OPTIONS
**Option A: Table-based binding (NEW)**
```
CREATE TABLE evidence_bindings (
  evidence_id TEXT,
  plan_id TEXT,
  decision_record_id TEXT,
  execution_id TEXT,
  event_id_range_start TEXT,
  event_id_range_end TEXT
)
```
**Cost:** New table, schema extension  
**Benefit:** Explicit, queryable

**Option B: Evidence record extension (MODIFY)**
```
RuntimeEvidenceRecord {
  ...existing...
  plan_id: str?
  decision_record_id: str?
  execution_id: str?
  pre_vs_post: "pre-decision" | "post-execution"
}
```
**Cost:** Schema change to Evidence, breaks existing validators  
**Benefit:** Self-contained

**Option C: Separate manifest file (ADD)**
```
data/evidence/evidence_manifest.jsonl {
  evidence_id: str,
  plan_id: str,
  decision_record_id: str,
  evidence_type: "pre-decision" | "post-execution",
  created_at: str,
  ...
}
```
**Cost:** New file format, append-only semantics needed  
**Benefit:** Non-invasive, backward-compatible

**Status:** NO DECISION MADE. Options A/B/C viable, each with trade-offs.

---

## 8. Migration and Backward Compatibility: EVIDENCE GAPS

### 8.1 Existing Event Records (mocka_events.db)
- **Current:** ~42 events in production DB (from observations)
- **Fields:** 30+ columns as per test schema
- **Missing:** plan_id, action_id, decision_record_id, evidence_id

### 8.2 Backward Compatibility Constraints (HG-D9-5 Condition 4)
> Existing runtime behavior を無断で変更してはならない。

**Implications:**
- ✗ Cannot ALTER TABLE events to add plan_id, action_id
- ✗ Cannot modify existing event records
- ✗ Cannot change event_id generation
- ✓ Can add NEW table for bindings
- ✓ Can add NEW file for manifest
- ✓ Can add NEW Evidence class/table

### 8.3 Forward Compatibility Path
**For New Events (T6+):**
- When mocka_write_event() called, can it reference plan_id/decision_record_id?
- When _record_governance_block() called, can it include plan_id in payload?
- Can event_gate.py be extended to accept and store plan_id (if in payload)?

**Status:** Requires investigation of event_gate.py payload extensibility.

---

## 9. Historical Data and Pre-Decision Evidence Sourcing: UNKNOWN

### 9.1 Question: What should Pre-Decision Evidence contain?
**HG-D1:** "Plan validity + Evidence-based rationale → Decision"

**Interpretation Options:**

**Option I: Plan Structure Only**
```
Pre-Decision Evidence {
  record_id: PER_20260921_xxxx,
  based_on: "Plan metadata",
  plan_id: xyz,
  plan_structure: {
    intent_id: ...,
    steps: [...],
    action_ids: [...]
  },
  structural_validation: {
    consistent: bool,
    gaps: [],
    ambiguities: []
  },
  generated_at: T2-T3,
  generated_by: session_id
}
```
**Viability:** HIGH (all data available at T2-T3)

**Option II: Plan + Historical Patterns**
```
Pre-Decision Evidence {
  record_id: PER_20260921_xxxx,
  based_on: "Plan + execution history",
  plan_id: xyz,
  plan_structure: {...},
  historical_context: {
    prior_similar_plans: N,
    success_rate: X%,
    common_blockers: [...]
  },
  generated_at: T2-T3,
  generated_by: session_id
}
```
**Viability:** MEDIUM (requires historical data query)

**Option III: Plan + Real-Time Governance Signals**
```
Pre-Decision Evidence {
  record_id: PER_20260921_xxxx,
  based_on: "Plan + governance pipeline",
  plan_id: xyz,
  plan_structure: {...},
  governance_check: {
    policy_compliance: bool,
    authority_available: bool,
    risk_assessment: str
  },
  generated_at: T3 (at decision point),
  generated_by: governance_system
}
```
**Viability:** MEDIUM (requires governance system hooks)

### 9.2 Minimum Evidence for HG-D1 Compliance
**Lower bound:** Must demonstrate that Plan itself (structure, validity, metadata) was evaluated BEFORE Decision.

**Sufficient for:** Basic Decision rationalization ("I considered this Plan")

**NOT sufficient for:** Authority justification ("I know this Plan will succeed")

**Status:** MINIMUM = Option I (Plan Structure Only). Options II/III are enhancements.

---

## 10. Persistence Target Analysis: CANDIDATE OPTIONS

### 10.1 Option A: New Database (vasai_evidence.db)
```
CREATE TABLE pre_decision_evidence (
  record_id TEXT PRIMARY KEY,
  plan_id TEXT,
  decision_record_id TEXT,
  evidence_data TEXT,  # JSON
  created_at TEXT,
  generated_by TEXT
)

CREATE TABLE post_execution_evidence (
  record_id TEXT PRIMARY KEY,
  execution_id TEXT,
  event_range_start TEXT,
  event_range_end TEXT,
  hash TEXT,
  created_at TEXT,
  generated_by TEXT
)
```

**Pros:**
- Clean separation of concerns
- Independent from event DB
- Easy to back up / export

**Cons:**
- New DB file to manage
- Transaction coordination needed (Decision Ledger + Evidence DB)
- Naming ambiguity ("vasai" origin unclear)

**Status:** VIABLE

### 10.2 Option B: Extension to mocka_events.db
```
CREATE TABLE evidence_records (
  record_id TEXT PRIMARY KEY,
  evidence_type TEXT,  # "pre-decision" | "post-execution"
  plan_id TEXT,
  decision_record_id TEXT,
  execution_id TEXT,
  evidence_data TEXT,  # JSON
  created_at TEXT,
  generated_by TEXT,
  source_event_range_start TEXT,
  source_event_range_end TEXT
)
```

**Pros:**
- Single DB for related institutional records
- Atomic transactions possible

**Cons:**
- Mixes Evidence with Events (semantic coupling)
- Larger events DB footprint
- Risk of Future schema conflicts

**Status:** VIABLE but less clean

### 10.3 Option C: JSONL Files (Like Decision Ledger)
```
data/evidence/evidence_records.jsonl
{
  "record_id": "PER_20260921_xxxx",
  "evidence_type": "pre-decision",
  "plan_id": "...",
  "decision_record_id": "...",
  "evidence_data": {...},
  "created_at": "...",
  "generated_by": "..."
}
```

**Pros:**
- Same format as Decision Ledger (consistency)
- Append-only semantics easy to enforce
- Natural immutability
- Minimal schema (just fields)

**Cons:**
- Less queryable than DB table
- May need secondary index file
- Larger file per record

**Status:** VIABLE (aligns with existing patterns)

### 10.4 Recommendation for Investigation
**Best fit:** Option C (JSONL, aligned with Decision Ledger)

**Rationale:**
- HG-D9 defines Evidence as "canonical institutional record"
- Decision Ledger already uses JSONL (proven pattern)
- Append-only matches Evidence immutability requirement
- No schema lock-in
- Minimal production risk

---

## 11. Unresolved Human Gate Decisions (For Phase 2-B)

### HG-D9-2 Clarification: Plan ↔ Event Identity Binding
**Q1:** When new Events are created (T6+), should they include plan_id in the payload?

**Options:**
- A: Yes, extend event_gate.py to accept plan_id in payload
- B: No, rely on Decision Ledger `related_events` field for binding
- C: Require separate binding table
- D: Leave undefined for now

**Current:** Undefined. Implementation depends on this.

### HG-D9-3 Clarification: Evidence Persistence Target
**Q2:** Which persistence option for Pre-Decision Evidence?

**Options:**
- A: New DB (vasai_evidence.db)
- B: Extend mocka_events.db
- C: JSONL files (like Decision Ledger)
- D: Other (specify)

**Current:** Investigation favors Option C, but HG decision required.

### HG-D9-4 Clarification: Pre-Decision Evidence Source
**Q3:** What should Pre-Decision Evidence contain?

**Options:**
- A: Plan structure only (Option I from section 9.1)
- B: Plan + historical execution patterns (Option II)
- C: Plan + real-time governance signals (Option III)
- D: Hybrid approach (specify)

**Current:** Investigation favors Option A (minimum), but HG can choose differently.

### HG-D9-5 Clarification: Event Payload Extension Backward Compatibility
**Q4:** Can event_gate.py be extended to accept and store new correlation fields (plan_id, decision_record_id) without modifying existing event records?

**Options:**
- A: Yes, extend event_gate.py payload handling
- B: No, leave event schema as-is
- C: Create separate binding mechanism

**Current:** Undefined. Code changes may require this clarification.

### HG-D9-5 Clarification: Transaction Boundary (Decision ↔ Evidence)
**Q5:** Should Pre-Decision Evidence generation be atomic with Decision Ledger write?

**Options:**
- A: Yes, both written in single transaction
- B: No, Decision recorded first, Evidence separately (asynchronous)
- C: Leave flexible

**Current:** Undefined. Affects architecture robustness.

---

## 12. Transaction Boundaries and Atomicity: UNKNOWN

### 12.1 Decision Formation Sequence
```
T3 Decision Time:
  ├─ governance_evaluate() → decision_record_id
  ├─ _get_hg_decision() → hg_decision
  └─ ??? Write Decision to Decision Ledger?
      └─ ??? Generate Pre-Decision Evidence?
          └─ ??? Store in persistence target?
```

**Current:** No automatic Decision Ledger write. Caller must call mocka_decision_write() separately.

### 12.2 Atomicity Requirement
**If Pre-Decision Evidence is required by HG-D1:**
- Decision must be persisted before execution
- Evidence must exist with Decision
- Both should be atomic (fail-closed if either fails)

**Current:** No atomic write mechanism. Each MCP call is independent.

**Status:** ARCHITECTURAL GAP - requires design decision.

---

## Summary: Pre-Decision Evidence Architecture Requirements

### What IS Verified
1. ✓ Plan metadata available at Decision time (T3)
2. ✓ Complete identity chain defined (intent/plan/action/decision)
3. ✓ Event schema and generation working (but no Plan correlation)
4. ✓ Evidence schema and generator implemented (but not persisted)
5. ✓ Decision Ledger exists and functional
6. ✓ Historical patterns available (in execution-history if queried)
7. ✓ Backward compatibility achievable (no event record modification needed)

### What IS NOT Verified
1. ? Pre-Decision Evidence persistence location (DB/File/Table/Format)
2. ? Plan ↔ Event identity binding mechanism
3. ? Event payload extensibility (can plan_id be added without breaking existing records?)
4. ? Pre-Decision Evidence source specification (Plan-only? + Historical? + Governance?)
5. ? Transaction boundaries (atomic Decision + Evidence writes)
6. ? Whether historical execution data is necessary or optional
7. ? How Pre-Decision Evidence relates to governance validation

### What Requires Human Gate Decision
1. **HG-Q1:** Event payload extension permitted? (plan_id, decision_record_id)
2. **HG-Q2:** Evidence persistence target? (DB / JSONL / Table)
3. **HG-Q3:** Pre-Decision Evidence source? (Plan-only / + History / + Governance)
4. **HG-Q4:** Atomicity requirement? (Decision ↔ Evidence transaction)
5. **HG-Q5:** Identity binding approach? (Separate table / Extended Evidence / Decision Ledger reference)

---

## Conclusion: Phase 2-A Complete

**Readiness for Phase 2-B:** CONDITIONAL

**Proceed to Phase 2-B DESIGN when Human Gate provides answers to:**
- HG-Q1: Event payload extensibility
- HG-Q2: Evidence persistence target
- HG-Q3: Pre-Decision Evidence source
- HG-Q4: Transaction atomicity requirement
- HG-Q5: Identity binding mechanism

**No implementation changes authorized until HG answers provide design constraints.**

**Phase 2-B will produce:** Detailed implementation plan (sandbox) based on HG answers.

---

**Report Author:** KUROKO (Phase 2-A Investigation)  
**Status:** ARCHITECTURE INVESTIGATION COMPLETE  
**Authorization Level:** Sandbox design/investigation only  
**Production Changes:** PROHIBITED until HG-D9 Implementation Decisions made  
**Date:** 2026-09-21
