# STEP 11B: ACTUAL DECISION INPUT BOUNDARY INVESTIGATION
**Date:** 2026-09-20  
**Purpose:** Trace actual decision inputs and identify binding readiness  
**Status:** INVESTIGATION COMPLETE - CRITICAL IMPLICATIONS FOR STEP 11

---

## EXECUTIVE SUMMARY

**Finding:** The decision system is **STUB/MOCK** for MVP. No actual evaluation happens.

**Decision Input Inventory:**
- Plan structure (intent_id, plan_id, steps) from plan.json
- Governance decision: auto-generated PASS + random UUID
- HG decision: MOCK (not actually decided)

**Knowledge Relation:** NOT CONNECTED (never retrieved)

**Binding Readiness:** NOT READY (nothing real to bind to)

---

## ACTUAL DECISION RUNTIME CALL CHAIN

### Complete Genealogy

```
main_loop.py:22
└─ load_intent() from input.json
   ├─ Line 29: intent = JSON.load("input.json")
   └─ Line 32: append_intent(intent)

main_loop.py:34-35
└─ apply_intent_to_goal()
   └─ update_plan_from_goal()
      └─ plan.json created (structure: intent_id, plan_id, steps)

main_loop.py:40
└─ load_plan_with_validation()
   ├─ Load: plan.json from disk
   ├─ Validate: intent_id + plan_id present (lines 13-14)
   ├─ Status: CURRENT | LEGACY | INVALID
   └─ Return: validated plan dict

main_loop.py:54
└─ choose_best_action(plan)
   └─ Sort steps by evaluation history

main_loop.py:58
└─ governance_evaluate(plan)  ← DECISION POINT
   ├─ Input: plan dict {intent_id, plan_id, steps}
   ├─ Line 27-29: Extract plan_id, intent_id, steps
   ├─ Line 31: decision_record_id = uuid.uuid4()  ← RANDOM UUID
   ├─ Line 33: decision = "PASS"  ← HARDCODED PASS
   ├─ Line 34: reason = f"Plan {plan_id} passed governance check (stub)"
   └─ Return: {decision_record_id, governance_decision, governance_reason, timestamp}

main_loop.py:80-85
└─ authorize_and_execute(plan, governance_decision, governance_record_id, execute_fn)
   ├─ Line 43-49: Create ExecutionContext
   │  ├─ intent_id
   │  ├─ plan_id
   │  ├─ governance_decision (= "PASS")
   │  ├─ governance_reason
   │  └─ decision_record_id (= random UUID)
   ├─ Line 21: "Get HG decision (mock for MVP)"  ← MOCK HG
   ├─ Line 22: "Enforce fail-closed gate"
   └─ Line 23: If permitted: execute_fn()

main_loop.py:72
└─ execute_action(step)
   └─ Actual action execution (not decision)

main_loop.py:95-98
└─ Post-execution: Update state, evaluate, history
```

---

## DECISION INPUT INVENTORY

### What governance_evaluate() Actually Receives

| Input | Source | Type | Value | Used |
|-------|--------|------|-------|------|
| intent_id | plan.json | string | From load_intent() | Extract only |
| plan_id | plan.json | string | From load_plan() | Extract only |
| steps | plan.json | list | Action steps | Extract only (not used) |
| Knowledge | memory_store | (any) | N/A | NOT REFERENCED |
| Evidence | memory_store | (any) | N/A | NOT REFERENCED |
| Context | memory_store | (any) | N/A | NOT REFERENCED |
| Authority | HG | decision | N/A | STUBBED/MOCKED |
| History | evaluation_history | (any) | N/A | NOT REFERENCED |

### What governance_evaluate() Actually Does With It

```python
def evaluate(plan):
    plan_id = plan.get("plan_id", "UNKNOWN")          # Line 27
    intent_id = plan.get("intent_id", "UNKNOWN")      # Line 28
    steps = plan.get("steps", [])                      # Line 29
    
    decision_record_id = str(uuid.uuid4())             # Line 31 - RANDOM
    decision = "PASS"                                  # Line 33 - HARDCODED
    reason = f"Plan {plan_id} passed governance check (stub)"  # Line 34
    
    # Note: steps is read but NEVER USED
    # Note: The evaluation is not real - it's just returning PASS
```

**Verdict:** Inputs are parsed but not evaluated. Decision is hardcoded PASS.

---

## DECISION RECORD ID GENEALOGY

```
governance_evaluate()
    ↓
Line 31: decision_record_id = str(uuid.uuid4())
    ↓
UUID format: "f47ac10b-58cc-4372-a567-0e02b2c3d479" (random)
    ↓
NOT DC_YYYYMMDD_NNN format (Decision layer format)
    ↓
Used only as identifier in ExecutionContext
    ↓
No connection to decision_ledger.jsonl
    ↓
No persistence mechanism (not written to any ledger in this path)
```

**Status:** Decision record ID is generated but not written to decision_ledger. It's only in ExecutionContext.

---

## MEMORY/KNOWLEDGE LAYER SEPARATION POINT

### Where Memory Disconnects from Actual Decision

```
MemoryPipeline.process()
    ├─ retrieve knowledge     ← NOT CALLED
    ├─ enrich context         ← NOT CALLED
    └─ create DecisionResult  ← NOT CALLED

vs.

governance_evaluate(plan)
    ├─ extract plan_id
    ├─ extract intent_id
    ├─ extract steps
    └─ return PASS            ← ACTUAL DECISION MADE
```

**Separation Point:** main_loop.py line 58

- Before: MemoryPipeline.process() exists (not called)
- At: governance_evaluate(plan) called
- After: ExecutionContext created without knowledge reference

**Evidence:** grep shows MemoryPipeline NOT imported into main_loop.py

---

## AUTHORITY TRANSITION

```
Governance Decision
    │
    └─ decision = "PASS" (hardcoded, no evaluation)
       decision_record_id = random UUID
    │
    ↓
HG Authorization
    │
    └─ "Get HG decision (mock for MVP)" (line 21, hg_gateway.py)
       Status: MOCKED, not real authority
    │
    ↓
ExecutionContext
    │
    └─ Contains governance_decision + decision_record_id
    │
    ↓
execute_fn() (actual action execution)
```

**Authority:** Governance and HG both stubbed/mocked for MVP.

---

## EXECUTION TRANSITION

```
authorization
    ↓
execute_fn(execution_context, step, action_id)
    ├─ execution_context.add_trace_event("execute_action_start", ...)
    └─ execute_action(step)
        └─ Actual consequence
            └─ Result returned
    ├─ execution_context.add_trace_event("execute_action_complete", "status=success")
    └─ return result
```

**Decision Identity:** Maintained through ExecutionContext (decision_record_id + governance_decision)

---

## EVIDENCE CLASSIFICATION

### Classification Schema: A/B/C/D/E

For each piece of information:
- **A** = Actual Decision Input (used for deciding)
- **B** = Available but Not Used (exists but not referenced)
- **C** = Recorded After Decision (added later)
- **D** = Not Connected (exists elsewhere)
- **E** = Unknown

### Results

| Information | Classification | Evidence |
|-------------|-----------------|----------|
| Plan structure (intent_id, plan_id, steps) | **A** - Actual Input | governance_client.py:27-29 |
| Knowledge from memory_store | **D** - Not Connected | No import/call in governance_evaluate() |
| Evidence from memory_store | **D** - Not Connected | No import/call in governance_evaluate() |
| Context enrichment | **D** - Not Connected | MemoryContextBuilder not used |
| Historical decisions | **D** - Not Connected | evaluation_history not passed to governance |
| Governance decision | **A** - Actual Input (sort of) | governance_evaluate() returns it |
| Decision evaluation logic | **E** - Unknown/Stub | governance_evaluate() just returns PASS |
| HG authority | **E** - Unknown/Mock | hg_gateway.py:21 says "mock for MVP" |
| Execution trace | **C** - Recorded After | ExecutionContext logs after execution |
| Decision record persistence | **B** - Available but Not Used | Not written to decision_ledger.jsonl in this flow |

---

## FULL RUNTIME SEQUENCE WITH CONNECTIVITY

```
Evidence ←───── NOT CONNECTED ─────→ Decision Input
  │                                    │
  │ (never retrieved)                  │ (only plan.json)
  │                                    ↓
Context ←───── NOT CONNECTED ─────→ governance_evaluate()
  │                                    │
  │ (never provided)                   │ (hardcoded PASS)
  │                                    ↓
Plan ←──────── PARTIAL CONNECTED ──→ Decision
  │ (used)                             │
  │                                    │ (decision_record_id = UUID)
  └──────────────────────────────────→ │
                                       ↓
Authority ←───── MOCKED ─────────→ HG Gate
  │ (stub)                             │
  │                                    │
  └──────────────────────────────────→ │
                                       ↓
Execution ←───── CONNECTED ──────→ ExecutionContext
  │ (full trace)                       │
  │                                    │
  └──────────────────────────────────→ │
                                       ↓
Consequence ←─── CONNECTED ──────→ Result/History
  │ (recorded)                         
  │
  └── Memory (OPTIONAL: write_decision could record it)
```

---

## IMPLEMENTATION IMPLICATIONS

### For STEP 11 Binding

**Current State:**
- ✓ MemoryBindingStore implemented
- ✓ MemoryBindingTrace model exists
- ✓ Can create bindings in theory
- ✗ **NO KNOWLEDGE IS RETRIEVED** for actual decisions
- ✗ **NO DECISIONS ARE REAL** (governance_evaluate is stub)
- ✗ **NO BINDING TARGETS** (nothing to bind to)

**Conclusion:** STEP 11 binding has nothing to bind to. The decision is hardcoded PASS.

### What Would be Needed to Make STEP 11 Work

1. **Replace governance_evaluate() stub with real logic**
   - Actually evaluate plan using real criteria
   - Consider knowledge/evidence/history
   
2. **Connect Memory to governance_evaluate()**
   - Import MemoryRetriever
   - Retrieve knowledge before evaluating
   - Pass retrieved knowledge to evaluation logic

3. **Record binding when decision is made**
   - When governance_evaluate() makes a real decision
   - Record which knowledge was used
   - Create MemoryBindingTrace
   - Append to binding_ledger

4. **Write decision to decision_ledger**
   - Currently decision_record_id is just lost (not persisted)
   - Need to write actual decision to decision_ledger.jsonl

---

## UNRESOLVED QUESTIONS

1. **Is governance_evaluate() meant to be real or stay stub?**
   - Comment says "In production, call actual governance service"
   - But main_loop.py doesn't show any service call

2. **Where does actual governance happen?**
   - Is it in a separate service at localhost:8000 (EXECUTION_RUNTIME_ENDPOINT)?
   - Or is it entirely stubbed for MVP?

3. **Is HG authorization real or mock?**
   - hg_gateway.py says "mock for MVP"
   - But fail_closed_enforcement.py might have real logic

4. **Should decision_record_id be persisted?**
   - Currently it's just a random UUID in ExecutionContext
   - Not written to decision_ledger
   - Is this intentional for MVP?

---

## FINAL DETERMINATION

### CURRENT DECISION INPUT:
```
- intent_id (from input.json)
- plan_id (from plan.json)
- steps (list from plan.json)
- governance_decision: "PASS" (hardcoded)
- governance_reason: "{plan_id} passed governance check (stub)"
- decision_record_id: random UUID
- HG: mocked

KNOWLEDGE USED: NONE
EVIDENCE USED: NONE
CONTEXT USED: NONE
```

### KNOWLEDGE RELATION:
**NOT CONNECTED**

Evidence:
- governance_evaluate() doesn't import MemoryRetriever
- governance_evaluate() doesn't call memory_store.retrieve()
- MemoryPipeline.process() not called in main_loop
- No knowledge reference in decision input

### BINDING READINESS:
**NOT READY**

Reasons:
1. governance_evaluate() is a stub (always returns PASS)
2. No real decision evaluation happens
3. No knowledge is retrieved
4. No binding targets exist
5. decision_record_id is not persisted (not in decision_ledger)

**Verdict:** STEP 11 binding is not implementable until governance_evaluate() is a real system that retrieves and uses knowledge.

---

## SUMMARY TABLE

| Aspect | Status | Evidence |
|--------|--------|----------|
| Decision entry point | STUB/MOCK | governance_evaluate() always returns PASS |
| Decision input source | Plan only | governance_client.py:27-29 |
| Knowledge retrieval | NOT CONNECTED | No call in governance evaluation |
| Authority evaluation | MOCKED | hg_gateway.py:21 |
| Decision persistence | NO LEDGER | UUID not written to decision_ledger.jsonl |
| Binding targets | NONE | No real decisions made |
| STEP 11 readiness | NOT READY | System is stubbed for MVP |

---

## CONCLUSION

STEP 11 binding cannot work because **the decision system itself is not real yet**.

The current architecture:
1. Loads plan from JSON
2. Passes to governance_evaluate() which is a STUB (returns PASS)
3. Passes to HG which is MOCKED
4. Executes action

There is no actual decision-making happening. No knowledge is retrieved. No evaluation occurs.

**For STEP 11 to be meaningful:** governance_evaluate() must become real and must retrieve knowledge.

Until then, binding records would document knowledge that was never actually used.
