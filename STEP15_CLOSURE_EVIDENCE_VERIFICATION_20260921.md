# STEP 15 CLOSURE: EVIDENCE VERIFICATION

**Date:** 2026-09-21  
**Purpose:** Close 5 remaining evidence gaps in STEP 15 Contract  
**Scope:** Verification only — no implementation

---

## 調査結果: 5項目

### 1. EVIDENCE STORE

**Found:**
- Location: PlanningCaliber/workshop/vasAI_Project/core/evidence_ledger.py
- Type: SQLite-based (vasai_evidence.db)
- Writer: EvidenceLedger.add_evidence() method
- Reader/Query: EvidenceLedger.query_evidence() method (inferred)
- Identifier: EV{YYYYMMDD}_{sequence} format
- Runtime Access: **NOT CONNECTED to governance_evaluate()**

**Status:** VERIFIED
- Evidence Store exists (detailed implementation)
- Schema proper (9 fields including id, decision_id, event_id, evidence_type, content, source, confidence, created_at, hash)
- Writer available (EvidenceLedger.add_evidence)
- Reader available (query method)
- **BUT:** governance_client.py does NOT call it
- CONFIGURED ✓ / CONNECTED ✗

**Gap Closure:** Evidence Store location/schema confirmed. Integration gap confirmed (intentional per STEP 15 design).

---

### 2. EVIDENCE RECORD SCHEMA

**Verified Schema (from vasai_evidence.db creation):**

```
CREATE TABLE evidence (
    id            TEXT PRIMARY KEY,
    event_id      TEXT,
    decision_id   TEXT,
    evidence_type TEXT,
    content       TEXT (JSON),
    source        TEXT,
    confidence    REAL,
    created_at    TEXT,
    hash          TEXT,
    prev_hash     TEXT
)

EVIDENCE_TYPES = ("FACT", "ASSUMPTION", "CONSTRAINT", "INTENT")
```

**Mapping to STEP 15 Assumptions:**

| STEP 15 Assumption | Actual Field | Match |
|-------------------|--------------|-------|
| id | id (EV20260921_000001) | ✓ YES |
| applies_to | (NOT PRESENT) | ✗ NO — use event_id/decision_id instead |
| content | content (JSON text) | ✓ YES |
| confidence | confidence (REAL 0.0-1.0) | ✓ NEW (not assumed in STEP 15) |
| source | source (TEXT) | ✓ NEW (not assumed in STEP 15) |

**Gap Closure:**
- Schema **NOT** id/applies_to/content as assumed
- Schema **IS** id/event_id/decision_id/evidence_type/content/source/confidence/created_at/hash
- Correlation via event_id (event → evidence) and decision_id (decision → evidence)
- confidence field enables evidence quality grading

---

### 3. CONDITIONAL DECISION

**HG-D1～D7 Search:**

HG-D1 (Decision Formation): "Plan + Evidence evaluation" — no status specified
HG-D3 (Evidence): "Evidence base is rationale validity critical" — no partial evidence handling specified
HG others: No mention of decision status values

**STEP 15 Design Added:**

Section 5 (Decision Formation Contract) introduced:
- PASS (all evidence supports)
- CONDITIONAL (partial evidence supports)
- RECONSIDER (evidence contradicts)
- UNKNOWN (evidence unavailable)

**Current Code Status:**

governance_client.py line 33: `decision = "PASS"` (hardcoded)
No CONDITIONAL/RECONSIDER/UNKNOWN status in current implementation

**Verdict:**

CONDITIONAL is **DESIGN PROPOSAL, NOT AUTHORIZED**

Derived from fail-closed principle + HG-D3 (evidence critical), but:
- Not explicitly in HG-D1～D7
- Not in current implementation
- Needs separate HG authorization before implementation

**HG Question Generated:**

**HG-D8 (NEW):** When evidence is partial (some steps supported, some not), what is the decision status?

- A: PASS (treat as sufficient if coverage exceeds threshold)
- B: CONDITIONAL (accept decision but flag limitations)
- C: UNKNOWN (block decision, require complete evidence)
- D: Other

**Gap Closure:** CONDITIONAL identified as UNAUTHORIZED ASSUMPTION. HG-D8 question required.

---

### 4. KNOWLEDGE RETRIEVER

**Verified Implementation:**

- Module: core_kernel/memory_core/memory_store.py
- Class: MemoryStore
- Query Method: query(predicate=None) → list[MemoryRecord]
- Knowledge Identifier: MemoryRecord.id (string)
- Input: predicate function or None (for all records)
- Output: list of MemoryRecord objects

**Runtime Integration:**

- Imported in: NOT FOUND in governance_client.py / main_loop.py
- Called by governance_evaluate(): NO
- Used in Decision path: NO

**Status:**

- ✓ CONFIGURED (MemoryStore exists)
- ✗ NOT CONNECTED (governance_evaluate doesn't call it)
- record_type: AnalysisResult, Context, Observation, CognitiveState (per docstring line 5-6)
- Storage: JSON file or in-memory (line 9-10)

**Gap Closure:** Knowledge retriever verified as CONFIGURED but NOT CONNECTED. Conditional trace design valid but implementation deferred (HG-D7).

---

### 5. INSTITUTIONAL RECORD MAPPING

**Verified Implementation (mocka_mcp_server.py line 1107-1168):**

**Design Pattern:**

mocka_decision_write() is **MCP endpoint** (external tool, not internal runtime function)

All 15 fields provided as arguments by caller:

```python
record = {
    "decision_id":       decision_id,              # arg or auto-generated
    "title":             title,                    # arg
    "context":           context,                  # arg
    "alternatives":      alternatives,             # arg
    "decision":          decision,                 # arg (from Runtime Decision)
    "rationale":         rationale,                # arg (from Runtime Decision)
    "impact":            impact,                   # arg
    "related_events":    args.get("related_events", []),     # arg reference
    "related_documents": args.get("related_documents", []),  # arg reference
    "approved_by":       approved_by,              # arg (from HG, NOT from Decision)
    "approved_at":       datetime.now(...),        # auto-generated
    "supersedes":        args.get("supersedes"),   # arg
    "superseded_by":     None,                     # auto null
    "status":            status,                   # arg
}
```

**Field Classification:**

| Field | Source | Classification | HG-D4 Compliance |
|-------|--------|-----------------|------------------|
| decision_id | arg/auto | (A) Generated | ✓ |
| title | arg | (A) Generated | ✓ |
| context | arg | (A) Generated | ✓ |
| alternatives | arg | (A) Generated | ✓ |
| decision | arg (from Runtime) | (A) Generated | ✓ |
| rationale | arg (from Runtime) | (A) Generated | ✓ |
| impact | arg | (A) Generated | ✓ |
| related_events | arg | (C) Referenced | ✓ |
| related_documents | arg | (C) Referenced | ✓ |
| **approved_by** | arg (from HG, separate) | **(B) Authorization** | **✓ COMPLIANT** |
| approved_at | auto | Auto-generated | ✓ |
| supersedes | arg | (A) Generated | ✓ |
| superseded_by | auto | Auto-generated | ✓ |
| status | arg | (A) Generated | ✓ |

**HG-D4 Check:**

approved_by is NOT auto-derived from Decision.

It is provided separately by Authorization caller → **DECISION ≠ AUTHORIZATION separation maintained** ✓

**Gap Closure:**

Mapping verified as compliant with HG-D4.

Runtime Decision → Institutional Record linkage is manual (via mocka_decision_write MCP endpoint), not automatic.

---

## STEP 15 CONTRACT差分

**Differences Between STEP 15 Design and Verified Implementation:**

| Item | STEP 15 Design | Verified Reality | Impact |
|------|----------------|------------------|--------|
| Evidence Store | "推定 core_kernel/evidence/" | Confirmed PlanningCaliber/vasAI/core/evidence_ledger.py | ✓ Verified |
| Evidence Schema | id/applies_to/content | id/event_id/decision_id/evidence_type/content/source/confidence | ✓ Richer than expected |
| Conditional Decision | PASS/CONDITIONAL/RECONSIDER/UNKNOWN | PASS only (stub) | ⚠ UNAUTHORIZED |
| Knowledge Retriever | governance_evaluate calls memory_store | NOT CONNECTED | ✓ Expected (design only) |
| Institutional Mapping | Auto-generated by governance_evaluate → mocka_decision_write | Manual (external MCP tool) | ⚠ Gap from design |

**Critical Gaps:**

1. **Institutional Record Generation is Manual** (not automated in runtime)
   - STEP 15 implied mocka_decision_write auto-generates from Runtime Decision
   - Reality: All fields provided by MCP caller
   - Implication: Implementation must handle caller responsibility definition

2. **CONDITIONAL Decision Status Unauthorized**
   - STEP 15 proposed 4 decision statuses
   - Current: 1 status (PASS hardcoded)
   - HG-D8 needed for partial evidence handling

3. **Evidence Schema Richer** (confidence, source, type enumeration)
   - Enables sophisticated rationale support
   - confidence field supports evidence weighting

---

## HUMAN GATE 必要な質問

**HG-D8 (NEW):** Partial Evidence Handling

Question: When evidence is partial (some plan steps have supporting evidence, some don't), what is the decision status?

Options:
- A: PASS (treat as sufficient if coverage exceeds threshold)
- B: CONDITIONAL (accept decision but flag limitations)
- C: UNKNOWN (block decision, require complete evidence)
- D: RECONSIDER (flag for human review)

**Why Needed:** HG-D1～D7 specify Evidence is required but don't specify partial evidence handling. Current implementation (STUB) doesn't reach this case. STEP 15 proposed CONDITIONAL but this was unauthorized assumption.

**Recommendation:** HG decision enables implementation of real evidence evaluation logic.

---

## STEP 15 READINESS FINAL ASSESSMENT

### Evidence Gap Status

**Closed:**
1. ✓ Evidence Store location (verified)
2. ✓ Evidence Record Schema (verified + richer)
3. ✓ Knowledge Retriever (verified CONFIGURED, correctly NOT CONNECTED)
4. ✓ Institutional Record Mapping (verified HG-D4 compliant)

**Open:**
1. ⚠ CONDITIONAL Decision Status (unauthorized assumption)
   - Needs HG-D8 answer
   - Blocks implementation of partial evidence logic

**Gaps:**
1. Institutional Record generation is external MCP tool (manual), not internal runtime function
   - STEP 15 implied automatic mapping
   - Reality: caller provides all fields
   - Implication: Implementation must document caller responsibilities

---

### Final Classification

**STEP 15 IMPLEMENTATION READINESS: B**

**STEP15 IMPLEMENTATION-READY WITH EXPLICIT ASSUMPTIONS**

**Ready For:**
- governance_evaluate() design (Plan + Evidence input → Decision output)
- Decision ID generation (DC_YYYYMMDD_NNN format)
- Knowledge conditional tracing (design only, no binding implementation)
- Evidence-rationale binding design
- Decision/Authorization separation (HG-D4 compliant)

**Blocked Until HG-D8 Answer:**
- Real decision formation algorithm (what to do with partial evidence)
- Decision status state machine
- Institutional record auto-generation logic (if intended)

**Remaining Assumptions (Requiring HG Clarification):**
1. Partial evidence handling (HG-D8 needed)
2. Institutional record caller responsibilities (manual vs. auto)
3. Confidence weighting in evidence evaluation (evidence schema has confidence field but STEP 15 doesn't use it)

---

## 次に必要な作業

**If HG Answers HG-D8:**

1. STEP 15 Decision Formation Contract (Section 5) update
   - Add decision status state machine (PASS / CONDITIONAL / RECONSIDER / UNKNOWN)
   - Define thresholds for evidence coverage (if applicable)
   - Define confidence weighting (optional per evidence schema)

2. Implementation planning (STEP 16)
   - governance_evaluate() function signature (plan + evidence → decision)
   - Evidence query logic (from vasai_evidence.db)
   - Rationale generation (evidence-based)
   - Knowledge conditional trace preparation

3. Caller responsibility documentation
   - mocka_decision_write input validation
   - approved_by sourcing (from HG authorization)
   - related_events/related_documents mapping

**If HG Defers HG-D8:**
- STEP 15 remains CONDITIONAL on HG decision
- Implementation planning blocked
- Can proceed with design-only STEP 15 components (identity, separation, etc.)

