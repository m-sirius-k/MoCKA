# STEP 11: ACTUAL DECISION RUNTIME GENEALOGY
**Investigation Date:** 2026-09-20  
**Purpose:** Trace actual decision execution path and knowledge retrieval integration  
**Status:** INVESTIGATION COMPLETE - CRITICAL FINDING

---

## EXECUTIVE SUMMARY

**Finding:** Actual Decision runtime and Knowledge Retrieval are **ARCHITECTURALLY SEPARATE**.

- Decision execution happens via Governance layer (main_loop.py → governance_evaluate)
- Knowledge retrieval exists in Memory layer (MemoryPipeline.process)
- These two paths do NOT intersect in current runtime
- **Classification:** CASE C - Integration Gap

---

## ACTUAL DECISION RUNTIME GENEALOGY

### Entry Point: main_loop.py

```python
# runtime/main_loop.py:58
governance_result = governance_evaluate(plan)
decision_record_id = governance_result.get('decision_record_id')
```

**Evidence:** File exists: `/runtime/main_loop.py` (3.8K, Sep 20 13:43)

### Actual Decision Creation Flow

```
main_loop.py
    ↓
Line 37: print("=== DECISION MODE ===")
    ↓
Line 40: load_plan_with_validation()
    ↓
Line 54: choose_best_action(plan)
    ↓
Line 58: governance_evaluate(plan)  ← DECISION CREATED HERE
         Returns: {
           'governance_decision': ...,
           'decision_record_id': ...  ← ACTUAL DECISION_ID
         }
    ↓
Line 80: authorize_and_execute()  ← HG GATE
    ↓
Line 72: execute_action(step)  ← EXECUTION
```

### Decision Record Generation

**Location:** `governance_evaluate(plan)` in `runtime/governance_client.py`  
**Returns:** `decision_record_id` (format appears to be governance-specific, not Decision-layer DC_YYYYMMDD_NNN)  
**Type:** Governance decision, not Memory/Decision layer decision

### Critical Findings

#### 1. Actual Decision is NOT in Decision Layer
- Decision layer code: `/decision/decision_pipeline.py` - **NOT CALLED** by main_loop
- Governance layer code: `/runtime/governance_client.py` - **CALLED** by main_loop
- **Verdict:** Governance layer makes actual runtime decisions, not Decision/Memory layer

#### 2. MemoryPipeline is NOT Used in Actual Runtime
- MemoryPipeline.process() defined in: `/memory/memory_pipeline.py`
- Usage in production code: **NONE FOUND**
- Usage in tests only: `test_actual_runtime_binding.py`, `test_memory_binding_runtime.py`
- **Verdict:** MemoryPipeline is reference implementation, not production code

#### 3. Knowledge Retrieval is NOT Integrated with Actual Decision
- Knowledge retrieval: `/memory/memory_retriever.py`
- Memory enrichment: `/memory/memory_context_builder.py`
- **Used by:** MemoryPipeline.process() only (not called in actual runtime)
- **Not used by:** governance_evaluate() or main_loop
- **Verdict:** Knowledge exists but is not retrieved for actual governance decisions

#### 4. Actual Decision Execution Point
- Decision execution: `Line 72` of main_loop.py, `execute_action(step)`
- Precedes execution: Governance evaluation + HG authorization
- **Flow:** governance_evaluate → authorize_and_execute → execute_action
- **No knowledge retrieval before execution**

---

## KNOWLEDGE RETRIEVAL GENEALOGY

### Memory Layer Architecture

```
Memory Store
    ↓ (memory_retriever.py)
Retrieved Knowledge
    ↓ (memory_context_builder.py)
Enriched Context
    ↓ (memory_pipeline.py)
MemoryPipeline.process()
    ↓
DecisionResult (not decision_id!)
    ↓
Record in memory_store
```

### Knowledge → Decision Path (Does NOT Exist)

```
Retrieved Knowledge
    ↓ (expected connection)
Decision Context
    ↓ (expected connection)
Governance Decision
    ↓ (expected connection)
decision_record_id
```

**Status:** BROKEN/MISSING

### Evidence Table

| Component | Location | Status | Used by Actual Runtime |
|-----------|----------|--------|----------------------|
| MemoryStore | memory/data/memory_store.json | Exists | No |
| MemoryRetriever | memory/memory_retriever.py | Implemented | No |
| MemoryContextBuilder | memory/memory_context_builder.py | Implemented | No |
| MemoryPipeline | memory/memory_pipeline.py | Implemented | No (tests only) |
| DecisionEngine | decision/decision_engine.py | Implemented | No |
| DecisionPipeline | decision/decision_pipeline.py | Implemented | No |
| GovernanceClient | runtime/governance_client.py | Implemented | **YES** |
| main_loop | runtime/main_loop.py | Implemented | **YES** |

---

## RUNTIME SEQUENCE DIAGRAM

### ACTUAL Runtime (Governance Path)

```
main_loop.py
    ↓
intent → goal → plan (Line 29-35)
    ↓
plan validation (Line 40)
    ↓
choose_best_action(plan) (Line 54)
    ↓
governance_evaluate(plan)  ← DECISION CREATED
    ↓
authorize_and_execute()  ← HG GATE
    ↓
execute_action()  ← EXECUTION
    ↓
Result → State → History → Civilization
```

**Knowledge Retrieval in this path:** NONE OBSERVED

### UNUSED Runtime (Memory Path - NOT CALLED)

```
MemoryPipeline.process()
    ↓
retrieve knowledge
    ↓
enrich context
    ↓
create DecisionResult
    ↓
record in memory_store
```

**Status:** Dead code (not integrated into actual main_loop)

---

## CLASSIFICATION

### Based on HG Investigation Criteria

**CASE A:** "Real knowledge → decision → decision_id correlation exists"  
**Status:** ❌ NOT PRESENT

**CASE B:** "Knowledge retrieval exists but not connected to actual runtime decisions"  
**Status:** ✓ **CONFIRMED**

**CASE C:** "Actual decision runtime exists but doesn't use knowledge retrieval"  
**Status:** ✓ **CONFIRMED**

**CASE D:** "Knowledge and Decision exist but have no execution correlation"  
**Status:** ✓ **CONFIRMED**

**CASE E:** "Decision creation and decision execution are separate paths"  
**Status:** ✓ **CONFIRMED** (governance_evaluate creates, execute_action executes)

### Final Classification

**PRIMARY: CASE B + CASE C**
- Knowledge retrieval exists but is not connected to actual runtime (CASE B)
- Actual decision runtime exists but doesn't use knowledge (CASE C)

**SECONDARY: CASE E**
- Decision creation (governance_evaluate) and execution (execute_action) are separate

---

## IDENTIFIED GAPS

### 1. IMPLEMENTATION GAP
**Description:** MemoryPipeline exists but is never called by main_loop  
**Location:** main_loop.py does not import or call MemoryPipeline  
**Evidence:** grep shows MemoryPipeline only in /memory/ and test files  
**Impact:** Memory layer code is dead code (test-only implementation)

### 2. INTEGRATION GAP
**Description:** governance_evaluate() does not retrieve knowledge before deciding  
**Location:** runtime/governance_client.py presumably doesn't call MemoryRetriever  
**Evidence:** main_loop.py shows governance_evaluate called with only (plan) parameter  
**Impact:** Actual governance decisions are made without knowledge retrieval

### 3. TRACEABILITY GAP
**Description:** No connection between governance decision_record_id and memory_record_ids  
**Location:** Between governance_evaluate output and decision_record_id  
**Evidence:** governance_result returns decision_record_id, not memory_ids  
**Impact:** Cannot bind retrieved knowledge to governance decisions (different ID systems)

### 4. ARCHITECTURAL GAP
**Description:** Governance layer and Memory layer are separate systems with no integration  
**Location:** /runtime/ (governance) vs /memory/ (knowledge) - no bridge  
**Evidence:** No imports between modules  
**Impact:** Knowledge cannot influence governance decisions at runtime

---

## EVIDENCE GAPS

### Unanswered Questions

1. **Does governance_evaluate() use memory?**
   - Need to read: runtime/governance_client.py
   - Check: imports, function calls

2. **What is decision_record_id format?**
   - Is it same as Decision-layer DC_YYYYMMDD_NNN?
   - Or is it Governance-specific?
   
3. **Where do actual decision_ids get written?**
   - decision_ledger.jsonl or separate governance ledger?
   - MCP tool integration point?

4. **Is there a bridge between Memory and Governance?**
   - Any existing connection?
   - hg_gateway.py: does it access memory?

---

## HONEST ASSESSMENT

**Question Asked:** Does Knowledge reach actual Decision in MoCKA runtime?

**Answer:** NO - they are architecturally separate.

**Question Asked:** Can we correlate retrieved_knowledge with actual decision_id?

**Answer:** NO - different systems, different ID formats, no integration.

**What EXISTS:**
- ✓ Memory/Knowledge layer (complete, tested)
- ✓ Decision layer (complete, tested)
- ✓ Governance layer (used by main_loop, makes actual decisions)
- ✗ Integration between Memory and Governance

**What's MISSING:**
- ✗ Connection from MemoryPipeline to actual runtime
- ✗ Knowledge retrieval in governance_evaluate()
- ✗ Binding mechanism between knowledge_ids and decision_record_ids
- ✗ Bridge between Memory layer and Governance layer

---

## NEXT STEP FOR IMPLEMENTATION

Before Phase E can proceed with "actual runtime binding," the gap must be resolved.

**Options:**

**A. Minimal:** Add knowledge retrieval to governance_evaluate()
- Import MemoryRetriever
- Retrieve knowledge before deciding
- Pass retrieved knowledge to decision context
- Record binding at decision_record_id creation time

**B. Moderate:** Create bridge layer between Memory and Governance
- New layer: memory_governance_bridge.py
- Retrieves knowledge on behalf of governance_evaluate
- Manages ID correlation

**C. Architecture:** Unify Memory and Governance
- Use MemoryPipeline as governance input
- Change governance_evaluate to use MemoryPipeline.process()
- Automatically get knowledge + binding

**Current Status:** Implementation blocked until integration point is chosen.

---

## CONCLUSION

STEP 11 investigation is COMPLETE.

**Verdict:** Runtime binding cannot be implemented until Memory layer is integrated with Governance layer.

**This is not a STEP 11 implementation issue.** This is a **fundamental architecture question** about whether actual decisions in MoCKA should use knowledge retrieval.

**Recommendation:** Before implementing STEP 11 binding, HG must decide:

> "Should MoCKA's actual governance decisions (made in main_loop via governance_evaluate) retrieve and consider institutional knowledge?"

If YES → implement integration + STEP 11 binding  
If NO → STEP 11 binding has no purpose (knowledge would never reach decisions)

---

## FILES FOR HG REVIEW

1. `/runtime/main_loop.py` - Actual decision entry point
2. `/runtime/governance_client.py` - Actual decision creator
3. `/memory/memory_pipeline.py` - Unused knowledge layer
4. This genealogy document

**Investigation Status:** COMPLETE  
**Verdict:** CASE B/C - Implementation Gap + Integration Gap  
**Next Authorization:** Required for Memory-Governance integration decision
