# STEP 12: REAL DECISION ENGINE MINIMUM CONTRACT
**Date:** 2026-09-20  
**Purpose:** Define minimum contract for Real Decision Engine based on existing MoCKA architecture  
**Status:** SPECIFICATION - No code changes

---

## EXECUTIVE SUMMARY

**Current governance_evaluate():** STUB (always returns PASS + random UUID)

**Required for Real Decision Engine:** Must produce DECISION_LEDGER_SCHEMA_v1 compliant records

**Gap:** governance_evaluate() output format ≠ DECISION_LEDGER requirements

---

## DECISION FIELD CONTRACT

### Existing DECISION_LEDGER_SCHEMA_v1 Requirements

| Field | Type | Required | Source | Current Status |
|-------|------|----------|--------|-----------------|
| **decision_id** | string (DC_YYYYMMDD_NNN) | YES | decision engine | **MISSING** (only UUID exists) |
| **title** | string | YES | decision evaluation | **NOT PROVIDED** |
| **context** | string | YES | plan + environment | **PARTIAL** (plan_id only) |
| **alternatives** | array[{option, rejected_reason}] | YES | evaluation process | **NOT PROVIDED** |
| **decision** | string | YES | decision result | **HARDCODED** ("PASS") |
| **rationale** | string | YES | evaluation rationale | **NOT PROVIDED** |
| **impact** | string | YES | decision consequence | **NOT PROVIDED** |
| **related_events** | array | NO | trace linkage | **NOT PROVIDED** |
| **related_documents** | array | NO | reference | **NOT PROVIDED** |
| **approved_by** | string | YES | authority | **UNKNOWN** ("mock for MVP") |
| **approved_at** | string (ISO8601) | YES | timestamp | **EXISTS** |
| **supersedes** | string | NO | version control | **NOT PROVIDED** |
| **superseded_by** | string | NO | version control | **NOT PROVIDED** |
| **status** | string (Active/Superseded/Withdrawn) | YES | state | **NOT PROVIDED** |

---

## DECISION INPUT CONTRACT

### What Real Decision Engine Must Accept

| Input | Source | Type | Used Before Decision | Required | Current |
|-------|--------|------|--------|-----------|---------|
| **plan_id** | plan.json | string | YES (context) | YES | ✓ Provided |
| **intent_id** | plan.json | string | YES (context) | YES | ✓ Provided |
| **steps** | plan.json | array | MAYBE (evaluation) | ? | ✓ Provided |
| **plan_content** | plan.json | dict | MAYBE | ? | ✓ Provided |
| **knowledge** | memory_store | array | YES (evaluation) | ? | **MISSING** |
| **evidence** | evidence_store | array | YES (rationale) | ? | **MISSING** |
| **context_history** | history | array | MAYBE | ? | **MISSING** |
| **authority_guidance** | HG policy | dict | MAYBE | ? | **MOCKED** |

---

## DECISION EVALUATION RESULT CONTRACT

### What Real Decision Engine Must Produce

```
Input: plan + knowledge + evidence + context
    ↓
Evaluation Process:
    1. Analyze plan feasibility
    2. Consider knowledge/evidence
    3. Evaluate alternatives
    4. Select best option
    5. Generate rationale
    ↓
Output:
    - decision (selected alternative)
    - rationale (why selected)
    - alternatives (evaluated options)
    - impact (consequences)
    - decision_id (DC_YYYYMMDD_NNN format)
    - status (Active)
    ↓
Persist to DECISION_LEDGER_SCHEMA
```

---

## MINIMUM CONTRACT TABLE

### Decision Engine Contract (A-J)

| Aspect | Field | Input | Process | Output | Persisted | Required | Status |
|--------|-------|-------|---------|--------|-----------|----------|--------|
| **A. Identity** | decision_id | - | Generated from timestamp | DC_YYYYMMDD_NNN | YES | YES | **MISSING** |
| **B. Input** | plan + knowledge | plan.json, memory_store | Passed to evaluator | Extracted | N/A | YES | **PARTIAL** |
| **B. Input** | Evidence | evidence_store | Considered in eval | Recorded | N/A | ? | **MISSING** |
| **C. Evaluation** | evaluation_logic | plan+knowledge | Real algorithm | decision | Referenced | YES | **STUB** |
| **C. Result** | decision | evaluation | Real decision | Selected option | YES (ledger) | YES | **HARDCODED** |
| **D. Rationale** | rationale | evaluation process | Analysis of why | Text explanation | YES | YES | **MISSING** |
| **E. Evidence** | related_events | system events | Link to MoCKA events | Event IDs | YES | NO | **MISSING** |
| **F. Knowledge** | knowledge_reference | memory_store | Identify used knowledge | memory_ids | YES | ? | **MISSING** |
| **G. Authority** | approved_by | HG | Determine approver | Person/AI name | YES | YES | **UNKNOWN** |
| **H. Temporal** | approved_at | system clock | Timestamp decision | ISO8601 | YES | YES | ✓ Exists |
| **I. Plan Relation** | context | plan.json | Document background | Text | YES | YES | **PARTIAL** |
| **J. Execution** | impact | decision consequence | Describe effects | Text | YES | YES | **MISSING** |

---

## GAP ANALYSIS: CURRENT vs. REQUIRED

### Current governance_evaluate() Output

```json
{
  "decision_record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",  // Random UUID
  "governance_decision": "PASS",                                   // Hardcoded
  "governance_reason": "Plan {plan_id} passed governance check (stub)",
  "timestamp": "2026-09-20T10:00:00.000Z"
}
```

### Required DECISION_LEDGER_SCHEMA Output

```json
{
  "decision_id": "DC_20260920_001",                       // Format required
  "title": "...",                                         // MISSING
  "context": "Plan {plan_id}: ...",                       // PARTIAL
  "alternatives": [{                                      // MISSING
    "option": "...",
    "rejected_reason": "..."
  }],
  "decision": "...",                                      // Hardcoded PASS
  "rationale": "...",                                     // MISSING
  "impact": "...",                                        // MISSING
  "related_events": ["E20260920_001"],                    // MISSING
  "related_documents": [],                                // MISSING
  "approved_by": "governance_evaluate",                   // UNKNOWN
  "approved_at": "2026-09-20T10:00:00.000Z",            // EXISTS
  "supersedes": null,                                     // MISSING
  "superseded_by": null,                                  // MISSING
  "status": "Active"                                      // MISSING
}
```

**Missing from Current:** 11 of 15 required fields

---

## KNOWLEDGE REQUIREMENT

### Does Decision Engine Need Knowledge?

**Current:** NO - governance_evaluate() doesn't retrieve knowledge

**For Real Decision:** PROBABLY YES

Evidence from architecture:
- MemoryPipeline.process() built and tested (suggests knowledge should be used)
- STEP 11 binding investigation shows knowledge NOT currently retrieved
- DECISION_LEDGER_SCHEMA has no knowledge_reference field (suggests it's optional)

**Classification:** OPTIONAL (not in current schema, but binding requires it)

---

## EVIDENCE REQUIREMENT

### Does Decision Engine Need Evidence?

**Current:** NO - not referenced by governance_evaluate()

**For Rationale:** PROBABLY YES

Evidence from architecture:
- DECISION_LEDGER_SCHEMA requires rationale (field is mandatory)
- Rationale should explain why this decision vs. alternatives
- Evidence would support rationale quality

**Classification:** LIKELY REQUIRED (for rationale field)

---

## AUTHORITY REQUIREMENT

### Does Decision Engine Need Authority Decision?

**Current:** MOCKED - hg_gateway says "mock for MVP"

**For Real System:** YES

Evidence from architecture:
- DECISION_LEDGER_SCHEMA requires approved_by (mandatory)
- DECISION_LEDGER_SCHEMA requires status (mandatory)
- HG is separate gate (authorize_and_execute is separate function)

**Classification:** REQUIRED (mandatory field)

---

## BINDING DEPENDENCY

### What Must be True for STEP 11 Binding to Work?

1. **governance_evaluate() must produce real decisions** (not hardcoded PASS)
2. **Knowledge must be retrieved before decision** (needed for rationale)
3. **Decision must be persisted to decision_ledger** (with decision_id in correct format)
4. **Decision must reference which knowledge was used** (for binding_ledger)
5. **binding_ledger must correlate knowledge_id with decision_id** (traceability)

**Current State:** 0 of 5 are true

**Readiness:** NOT READY

---

## IMPLEMENTATION READINESS

### Can a Real Decision Engine Be Implemented Now?

**Data Model:** YES
- decision_ledger.jsonl exists
- Schema exists (DECISION_LEDGER_SCHEMA_v1)
- Storage is ready

**Input Data:** PARTIAL
- plan.json exists but needs structure verification
- Knowledge/evidence systems exist but not integrated
- Authority (HG) needs real implementation

**Decision Logic:** NOT READY
- Current governance_evaluate() is stub
- Real evaluation algorithm needed
- Alternative generation needed
- Rationale generation needed

**Persistence:** READY
- JSONL append-only ledger ready
- decision_id generation logic ready

**Integration:** PARTIAL
- HG gate exists but is mocked
- Execution path exists
- Memory connection missing

---

## CURRENT STATE

### CURRENT GOVERNANCE:
**STUB / MOCK**

Verdict: governance_evaluate() is placeholder MVP code that:
- Always returns PASS
- Generates random UUID (not DC_ format)
- Does not evaluate anything
- Does not use knowledge/evidence
- Does not produce decision_ledger schema

### MINIMUM DECISION CONTRACT:
```
Input:
  - plan (intent_id, plan_id, steps)
  - knowledge (optional but recommended)
  - evidence (optional but needed for rationale)
  - authority (from HG)

Processing:
  - Evaluate plan against criteria
  - Consider knowledge/evidence
  - Generate alternatives + rationale
  - Select best option

Output (DECISION_LEDGER_SCHEMA compliant):
  - decision_id (DC_YYYYMMDD_NNN)
  - decision (selected option)
  - rationale (evaluation explanation)
  - alternatives (with rejected_reason)
  - impact (consequences)
  - approved_by (authority name)
  - approved_at (timestamp)
  - status (Active)

Persist:
  - Append to decision_ledger.jsonl
  - Create MemoryBindingTrace for knowledge used
  - Append to binding_ledger.jsonl
```

### KNOWLEDGE REQUIREMENT:
**OPTIONAL** (not currently used, not in schema, but needed for binding)

### EVIDENCE REQUIREMENT:
**LIKELY REQUIRED** (needed for rationale field, not currently used)

### BINDING DEPENDENCY:
**Requires:**
1. Real governance_evaluate() implementation
2. Knowledge retrieval integration
3. Decision_id generation in correct format
4. Ledger persistence
5. Binding trace creation

**Current:** 0 of 5 satisfied

### IMPLEMENTATION READINESS:
**NOT READY**

Blockers:
- [ ] Real decision evaluation algorithm
- [ ] Knowledge retrieval in governance path
- [ ] decision_id format generation (DC_YYYYMMDD_NNN)
- [ ] Full schema population (11 missing fields)
- [ ] Alternative generation logic
- [ ] Rationale generation logic
- [ ] Real authority/HG integration
- [ ] Binding trace linkage

---

## CONCLUSION

The Real Decision Engine minimum contract requires replacing the stub governance_evaluate() with:

1. **Real evaluation logic** that produces all 15 DECISION_LEDGER fields
2. **Knowledge retrieval** (optional but needed for binding)
3. **Evidence integration** (needed for rationale)
4. **Authority decision** from HG
5. **Ledger persistence** in correct format
6. **Binding linkage** for STEP 11

Current governance_evaluate() satisfies **0 of 5** requirements.

**Next step:** Implement real governance_evaluate() per this contract before STEP 11 binding can work.
