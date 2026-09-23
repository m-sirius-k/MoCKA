# STEP 16 PHASE 1: EVIDENCE INTEGRATION INVESTIGATION

**Date:** 2026-09-21  
**Purpose:** Confirm Evidence Integration boundary for Real Decision Engine  
**Scope:** Investigation only — no code changes / no schema changes

---

## 1. EVIDENCE STORE ACTUAL PATH

**Location:** `PlanningCaliber/workshop/vasAI_Project/core/evidence_ledger.py`

**Status:** VERIFIED ✓

**Database:**
- Type: SQLite
- Path: `{vasAI_Project}/data/vasai_evidence.db` (configurable via VASAI_EV_DB_PATH env var)
- Current State: Database file NOT FOUND (schema defined but no data)

**Threading:**
- Lock: `_lock = threading.Lock()` (line 14)
- Connection pooling: `_conn_cache` (line 15)
- WAL mode: PRAGMA journal_mode=WAL (line 35)
- Synchronous: NORMAL (line 36)

---

## 2. WRITER (add_evidence)

**Function:** `EvidenceLedger.add_evidence()` (lines 93-128)

**Signature:**
```python
def add_evidence(
    self,
    event_id: str,
    decision_id: str,
    evidence_type: str,
    content: dict,
    source: str,
    confidence: float = 1.0
) -> str:  # Returns evidence_id
```

**Behavior:**
```
1. Validate evidence_type ∈ {FACT, ASSUMPTION, CONSTRAINT, INTENT}
2. Generate evidence_id: EV{YYYYMMDD}_{sequence:06d}
3. Calculate SHA256 hash chain (prev_hash → hash)
4. Transaction: BEGIN → INSERT → COMMIT (or ROLLBACK on error)
5. Return evidence_id
```

**Insert Columns:**
- id (TEXT PRIMARY KEY) - EV20260921_000001
- event_id (TEXT) - event reference
- decision_id (TEXT) - decision reference
- evidence_type (TEXT) - FACT/ASSUMPTION/CONSTRAINT/INTENT
- content (TEXT JSON) - JSON object
- source (TEXT) - origin
- confidence (REAL 0.0-1.0) - normalized
- created_at (TEXT ISO8601)
- hash (TEXT SHA256)
- prev_hash (TEXT SHA256)

**Error Handling:**
- Invalid evidence_type → ValueError raised
- Insert failure → ROLLBACK, exception raised

**Status:** VERIFIED ✓

---

## 3. READER / QUERY INTERFACE

**Methods:**

### A. get_decision_chain(decision_id) → dict

```python
# lines 130-161
def get_decision_chain(self, decision_id: str) -> dict:
    """Decision→Evidence→Approval→Result の全チェーンを返す。"""
    rows = conn.execute(
        "SELECT * FROM evidence WHERE decision_id=? ORDER BY id ASC",
        (decision_id,)
    ).fetchall()
    
    return {
        "decision_id": decision_id,
        "total_evidence": len(evidences),
        "chain": evidences,           # Full list
        "by_type": {...},             # Grouped by type
        "facts": [...],
        "assumptions": [...],
        "constraints": [...],
        "intents": [...]
    }
```

**Returns:** dict with Evidence records organized by type

**Status:** VERIFIED ✓

### B. list_by_event(event_id) → list[dict]

```python
# lines 211-223
def list_by_event(self, event_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM evidence WHERE event_id=? ORDER BY id ASC",
        (event_id,)
    ).fetchall()
    # Returns parsed JSON content
    return result
```

**Returns:** list of Evidence dicts with parsed JSON content

**Status:** VERIFIED ✓

### C. list_by_decision(decision_id) → list[dict]

```python
# lines 225-237
def list_by_decision(self, decision_id: str) -> list[dict]:
    # Same as list_by_event but filters by decision_id
    return result
```

**Returns:** list of Evidence dicts

**Status:** VERIFIED ✓

### D. why_was_this_decided(event_id) → str

```python
# lines 163-185
def why_was_this_decided(self, event_id: str) -> str:
    """自然言語で判断理由を説明する。"""
    # Formats Evidence as human-readable text
    return formatted_explanation
```

**Returns:** Natural-language rationale string

**Note:** Uses evidence content to generate explanation

**Status:** VERIFIED ✓

---

## 4. QUERY INTERFACE SUMMARY

**Query Keys:**
- By decision_id: get_decision_chain() or list_by_decision()
- By event_id: list_by_event() or why_was_this_decided()

**Return Format:**

```python
{
    "id": "EV20260921_000001",
    "event_id": "E20260921_001",
    "decision_id": "DC_20260921_001",
    "evidence_type": "FACT",
    "content": {...},  # JSON dict
    "source": "event_processor",
    "confidence": 0.95,
    "created_at": "2026-09-21T10:30:00Z",
    "hash": "sha256_hex",
    "prev_hash": "sha256_hex_prev"
}
```

**Instantiation:**
```python
ledger = EvidenceLedger()
evidence_list = ledger.list_by_decision("DC_20260921_001")
```

**Status:** VERIFIED ✓

---

## 5. PLAN / EVIDENCE RELATIONSHIP

**Plan Structure (Verified):**

From plan_validator.py:
```python
plan = {
    "intent_id": "intent_001",
    "plan_id": "plan_20260921_001",
    "steps": ["step_0", "step_1", "step_2"],
    "action_ids": [
        "intent_001:0",  # format: intent_id:step_index
        "intent_001:1",
        "intent_001:2"
    ]
}
```

**Evidence Schema Fields:**
- event_id (no direct step_id field)
- decision_id (links to Decision, not Plan)

**Plan → Evidence Mapping:**

| Plan Field | Evidence Field | Relationship | Status |
|-----------|---|---|---|
| plan_id | (NOT PRESENT) | No direct link | **EVIDENCE GAP** |
| intent_id | (NOT PRESENT) | No direct link | **EVIDENCE GAP** |
| steps[i] | event_id? | Unclear | **UNKNOWN** |
| action_ids[i] | (NOT PRESENT) | No direct link | **EVIDENCE GAP** |

**Actual Relationships Found:**

1. **Evidence → Event:** event_id links Evidence to event_store events (external)
2. **Evidence → Decision:** decision_id links Evidence to Decision records
3. **Plan → Event:** No direct mapping in current code
4. **Event → Plan:** Assumed via event_processor, but no schema confirmation

**Critical Finding:**

```
Current EvidenceLedger is designed for Decision→Evidence correlation,
NOT for Plan Step→Evidence correlation.

Evidence.event_id and Evidence.decision_id do NOT directly reference
plan.plan_id or plan.action_ids.

Therefore:
  Plan step i
  → Action ID j
  → Event E
  → Evidence (event_id=E)
  
BUT: No existing schema field to identify WHICH PLAN this evidence supports.
```

**Status:** EVIDENCE GAP ✗

---

## 6. EVIDENCE EVALUATION BOUNDARY

**HG-D1 / HG-D3 / HG-D8 Requirements:**
- Plan + Evidence → Real Decision
- Evidence base is rationale validity critical
- Partial Evidence → RECONSIDER

**Current Evidence Retrieval Capability:**

```python
# Known how to do:
ledger.list_by_decision(decision_id)  # Get evidence FOR a decision

# NOT known how to do:
# Get evidence FOR a plan step
# (need plan_id → event chain → evidence chain mapping)
```

**Evaluation Process (Design Boundary):**

```
T1: Evidence Retrieval
    Input: plan
    Query: evidence_ledger.list_by_decision(??) or list_by_event(??)
    Problem: No existing mapping from plan to evidence
    
    Options:
    A. Assume all evidence for plan_id's decision_id
       (requires decision_id BEFORE decision is made - circular)
    B. Map plan steps → events → evidence
       (requires event_store integration - NOT IN SCOPE)
    C. Assume events pre-exist with plan_id context
       (requires external event ingestion - EXTERNAL DEPENDENCY)
    D. EVIDENCE GAP: Cannot proceed without clarification

T2: Evidence Coverage Classification
    Input: evidence_list (from T1)
    Process:
      - Sort evidence by event_id/plan_step
      - Classify: complete / partial / missing
      - (logic TBD: threshold, confidence weighting)
    Status: ALGORITHM POSSIBLE IF T1 SOLVED

T3: Decision Formation
    Input: evidence_coverage
    Process:
      - complete → PASS
      - partial → RECONSIDER (HG-D8)
      - missing → UNKNOWN (fail-closed)
    Status: ALGORITHM VERIFIED
```

**Status:** BLOCKED BY EVIDENCE GAP ✗

---

## 7. RATIONALE REFERENCE MECHANISM

**HG-D3:** Evidence base is rationale validity critical

**Current Capability:**

EvidenceLedger has `why_was_this_decided(event_id)`:
```python
def why_was_this_decided(self, event_id: str) -> str:
    """自然言語で判断理由を説明する。"""
    # Formats Evidence records into human-readable text
    # Format: [FACT(95%)] description (source)
    return formatted_text
```

**Rationale Generation Path:**

```
Option A: Use evidence content directly
  for each evidence in plan_evidence:
    rationale += evidence["content"]["description"]
  → Requires evidence.content.description field

Option B: Use why_was_this_decided(event_id)
  rationale = ledger.why_was_this_decided(event_id)
  → Generates formatted text from evidence
  → Suitable for human-readable rationale

Option C: Build custom rationale
  rationale = "Steps [supported] supported; steps [missing] lack evidence"
  → Requires evidence classification (T2 boundary)
```

**Implementation Feasibility:**

- Option A (content.description): Possible IF evidence content has description field
- Option B (formatted): Possible, natural-language output
- Option C (summary): Possible, requires evidence classification

**Status:** OPTIONS AVAILABLE BUT EVIDENCE GAP BLOCKS IMPLEMENTATION ✗

---

## 8. FAILURE BEHAVIOR

**Evidence Retrieval Failures:**

| Scenario | Current Code | Real Decision Engine |
|---|---|---|
| Evidence unavailable | list_by_decision() returns [] | decision = UNKNOWN (HG-D3) |
| Query error (DB fail) | Exception raised | decision = UNKNOWN, fail-closed |
| Malformed content JSON | json.loads() raises | Exception in rationale gen |
| Invalid evidence_type | Validation in add_evidence | (input validation, not failure path) |
| Confidence out of range | Clamped to [0.0, 1.0] | (handled) |
| Hash chain broken | verify_chain() detects | Evidence integrity compromised (audit only) |

**Fail-Closed Compliance:**

```python
try:
    evidence_list = ledger.list_by_decision(plan_id)  # OR decision_id?
    if not evidence_list:
        decision = "UNKNOWN"  # No evidence
    else:
        # Evaluate coverage
        decision = evaluate_evidence(evidence_list)
except Exception as e:
    decision = "UNKNOWN"  # Query failed
    rationale = f"Evidence retrieval failed: {e}"
```

**Status:** FAIL-CLOSED APPROACH FEASIBLE ✓

---

## 9. EVIDENCE → DECISION WRITE SEQUENCE

**Critical Question:** When does Evidence link to Decision?

**Evidence Schema Has:**
```
decision_id (TEXT NOT NULL DEFAULT '')
```

**Two Possible Sequences:**

### Sequence A: Evidence Precedes Decision (Evidence Records Future Decision)
```
1. Pre-compute evidence for scenario
   add_evidence(event_id="E1", decision_id="DC_20260921_001", ...)
   (decision_id must exist or be pre-determined)

2. Form decision
   governance_evaluate() → decision_id

3. Link via decision_id

Problem: How does add_evidence know future decision_id?
         Must be pre-assigned or predicted.
```

### Sequence B: Decision Precedes Evidence (Evidence Recorded After Decision)
```
1. Form decision
   governance_evaluate(plan) → decision_id (DC_20260921_001)

2. Retrieve existing evidence by event (HG-D1)
   evidence_list = ledger.list_by_event(plan_event_id)

3. Link existing evidence to decision
   (evidence.decision_id already set OR updated)

4. Build rationale from evidence
   rationale = build_rationale(evidence_list)
```

**Current Implementation (Evidence Ledger) Supports:**
- Both sequences (decision_id is a field, not a process dependency)

**Real Decision Engine Must Use:**
- Sequence B (evidence pre-exists, decision forms from it)

**Status:** SEQUENCE B FEASIBLE ✓ (but requires evidence pre-population)

---

## 10. IMPLEMENTATION BLOCKERS

**Blocker 1: Plan → Event → Evidence Chain (CRITICAL)**

```
Current gap:
  plan.plan_id
  ↓ (unknown mapping)
  event.event_id
  ↓ (known: list_by_event)
  evidence.event_id

Solution required:
  - How does event_id relate to plan_id?
  - Is there an event_store that links them?
  - Is event pre-generated before governance_evaluate?
```

**Status:** BLOCKER ✗

**Blocker 2: Evidence Pre-Population (CRITICAL)**

```
Current state:
  vasai_evidence.db does NOT EXIST
  No evidence data in production

For governance_evaluate(plan) to retrieve evidence:
  Evidence must be populated BEFORE governance_evaluate is called

How does evidence get populated?
  - Event processor?
  - Manual ingestion?
  - Pre-scenario setup?
  - External service?
```

**Status:** BLOCKER ✗

**Blocker 3: Plan Step → Evidence Matching (HIGH)**

```
EvidenceLedger queries by:
  - event_id
  - decision_id
  
But plan has:
  - plan_id
  - action_ids[]
  - steps[]

Missing: how to map steps → events → evidence

Could derive from action_ids:
  action_ids[i] = f"intent_id:step_index"
  → Need event naming convention or lookup table
```

**Status:** BLOCKER ✗

---

## 11. IMPLEMENTATION READINESS

**Can We Implement Plan + Evidence → Decision?**

### YES (If Blockers Resolved):

```python
# Pseudo-code for governance_evaluate with evidence integration

def governance_evaluate(plan, evidence_ledger):
    # Assumption: event_id derivable from plan
    event_id = derive_event_id(plan)  # BLOCKER: how?
    
    # Retrieve evidence
    evidence_list = evidence_ledger.list_by_event(event_id)
    
    if not evidence_list:
        return {"decision": "UNKNOWN", "rationale": "No evidence"}
    
    # Evaluate coverage
    coverage = analyze_coverage(plan, evidence_list)
    
    if coverage["complete"]:
        decision = "PASS"
    elif coverage["partial"]:
        decision = "RECONSIDER"  # HG-D8
    else:
        decision = "UNKNOWN"
    
    rationale = evidence_ledger.why_was_this_decided(event_id)
    
    return {
        "decision": decision,
        "rationale": rationale,
        "evidence_ids": [ev["id"] for ev in evidence_list]
    }
```

### NO (Current State):

- Evidence schema exists
- Query methods exist
- But **no evidence data** and **no plan→event→evidence mapping**

---

## EVIDENCE SUMMARY

| Item | Status | Notes |
|------|--------|-------|
| **Evidence Store Location** | VERIFIED ✓ | PlanningCaliber/vasAI_Project/core/evidence_ledger.py |
| **Database Type** | VERIFIED ✓ | SQLite with WAL mode, connection pooling |
| **Writer (add_evidence)** | VERIFIED ✓ | Supports event_id, decision_id, confidence, content |
| **Reader (list_by_*)** | VERIFIED ✓ | get_decision_chain, list_by_event, list_by_decision |
| **Query Interface** | VERIFIED ✓ | Methods exist, return parsed JSON |
| **Plan → Event → Evidence Chain** | EVIDENCE GAP ✗ | No mapping; plan_id doesn't directly reference events |
| **Evidence Pre-Population** | NOT VERIFIED ✗ | Database empty; no data ingestion path confirmed |
| **Evidence Evaluation Algorithm** | FEASIBLE ✓ | Can classify complete/partial/missing if chain exists |
| **Rationale Generation** | FEASIBLE ✓ | why_was_this_decided() can format explanation |
| **Fail-Closed Behavior** | FEASIBLE ✓ | Can return UNKNOWN on retrieval failure |
| **Confidence Field** | VERIFIED ✓ | Present but no weighting algorithm specified (HG-D8 didn't specify) |

---

## PHASE 1 CONCLUSION

### Implementation Readiness: BLOCKED

**What We CAN Do (Ready):**
1. Instantiate EvidenceLedger
2. Query evidence by event_id or decision_id
3. Parse evidence records
4. Generate natural-language explanations
5. Classify evidence as complete/partial/missing (algorithm only)
6. Fail-closed on retrieval errors

**What We CANNOT Do (Blocked):**
1. ~~Connect plan.plan_id → event.event_id~~ (no mapping)
2. ~~Populate evidence database~~ (no data)
3. ~~Link plan steps to supporting evidence~~ (no naming convention)

### Required for Phase 2 (Real Implementation):

1. **Evidence Pre-Ingestion Path**
   - Where does evidence come from?
   - Who/what populates vasai_evidence.db?
   - Before or after plan generation?

2. **Plan → Event Mapping**
   - How does plan.plan_id relate to event.event_id?
   - Is there an event_store schema?
   - How to derive event_id from plan?

3. **Step → Evidence Matching**
   - How to identify "this evidence supports step_2"?
   - Naming convention?
   - Lookup table?
   - event.step_id field?

4. **Evidence Data Model**
   - Expected format of evidence.content?
   - Should it have "description" field?
   - How to parse natural-language explanation?

### Human Gate Required Before Phase 2:

**HG-D9 (NEW): Evidence Integration Architecture**

Question: How is evidence linked to plan execution?

- A: Pre-computed evidence for each plan (before governance_evaluate)
- B: Evidence generated during event processing (parallel to plan)
- C: Evidence requested on-demand by governance_evaluate
- D: Other

---

## CODE CHANGE AUTHORIZATION

**Current Status:** NO

This Phase 1 confirms that governance_evaluate() cannot be implemented without resolving Evidence pre-population and plan→event mapping.

**Next Step:** Require HG-D9 decision before Phase 2 can proceed.

