# STEP 11: INSTITUTIONAL MEMORY → DECISION BINDING
## Findings Summary & Human Gate Review Package
**Date:** 2026-09-20  
**Status:** INVESTIGATION COMPLETE / AUTHORIZATION REQUIRED FOR IMPLEMENTATION  
**Requesting Authority:** Human Gate Review

---

## INVESTIGATION CONCLUSION

**Research Question:** "Does MoCKA's institutional memory system BIND stored knowledge to subsequent decisions, or merely RECORD them?"

**Answer:** MoCKA RECORDS knowledge but does NOT BIND it.

**Evidence Basis:** Code investigation of 6 critical files:
1. ✓ memory/memory_store.py — memories ARE stored
2. ✓ memory/memory_retriever.py — memories ARE retrievable
3. ✓ memory/memory_context_builder.py — enrichment IS created
4. ✓ memory/memory_pipeline.py — attempted integration (incomplete)
5. ✗ semantic/intent_classifier.py — REJECTS context parameter
6. ✗ decision/decision_engine.py — IGNORES enriched_context

**Key Finding:** Context (including past decisions) is passed through the pipeline but DOES NOT INFLUENCE decision action selection. The decision engine determines selected_action by intent key alone, making past knowledge irrelevant to the outcome.

---

## SYSTEM STATE

### What Happens Today
```
MEMORY RECORD:
  MemoryStore ← past DecisionResult
    ↓
MEMORY RETRIEVAL:
  MemoryRetriever → ScoredMemory(id, relevance_score, entry)
    ↓
CONTEXT ENRICHMENT:
  EnrichedContext(past_decisions, success_patterns, failure_patterns)
    ↓
CONTEXT MERGING:
  MemoryPipeline merges enriched_context into context dict
    ↓
DECISION MAKING (IGNORES CONTEXT):
  DecisionEngine.decide() → selected_action = lookup(intent_key_only)
    ↓
DECISION RECORD:
  Memory ← new DecisionResult
```

**Critical Disconnect:** Context enters the system but does not exit (does not affect decision).

### What's Missing
1. No field in DecisionResult to record which memories influenced the decision
2. No mechanism for PriorityScorer to consider past outcomes
3. No binding ledger linking memory_id → decision_id
4. No runtime verification that knowledge changed the decision

---

## WHAT AUTHORIZATION IS NEEDED

### Phase A: Data Model Extension (Low Risk)
**Change:** Add field to DecisionResult
```python
memory_influence_trace: list = field(default_factory=list)
# [{memory_id, relevance_score, influence_type, proof}]
```
**Risk:** Read-only addition; backward compatible  
**Scope:** decision/decision_model.py only  
**Authority Required:** Structural modification approval

### Phase B: Scorer Enhancement (Medium Risk)
**Change:** Extend PriorityScorer.score() to accept enriched_context
```python
def score(self, semantic_result, profile, enriched_context=None):
    # Consider success_patterns, failure_patterns
    # Adjust scores based on history
```
**Risk:** Changes scoring logic (decision output could change)  
**Scope:** decision/priority_scorer.py + decision_engine.py  
**Authority Required:** Decision logic modification + governance approval

### Phase C: Engine Bridge (Medium Risk)
**Change:** Pass enriched_context to DecisionEngine
```python
def decide(self, semantic_result, enriched_context=None) -> DecisionResult:
    # Populate memory_influence_trace
```
**Risk:** Decision engine now receives additional input  
**Scope:** decision/decision_engine.py + memory/memory_pipeline.py  
**Authority Required:** Component integration approval

### Phase D: Binding Ledger (Low Risk)
**Change:** Create new file data/decisions/memory_binding_ledger.jsonl
```jsonl
{"decision_id": "DC_xxx", "memory_ids_retrieved": [...], "influenced": [...]}
```
**Risk:** New file, no existing code modification  
**Scope:** Ledger creation + read/write functions  
**Authority Required:** Data schema approval

### Phase E: Runtime Verification (Low Risk)
**Change:** Test that demonstrates binding works
```python
# Test: low-risk past decision → similar new decision → lower risk score
# Verify: binding_ledger contains memory_id → decision_id mapping
# Verify: DB read-back confirms binding
```
**Risk:** Test-only, no production changes  
**Scope:** New test file only  
**Authority Required:** Test authorization only

---

## DECISION POINTS FOR HUMAN GATE

### Q1: Scope Authorization
**Question:** Should past decisions influence the risk/priority scores of future decisions?

**Options:**
- A. YES - implement full binding (Phases A-E)
- B. PARTIAL - create binding ledger but don't modify scoring (Phases A, D only)
- C. INVESTIGATION_ONLY - document the gap without implementing (current state)
- D. DEFER - decide after separate policy review

**Current Recommendation:** Options A or B seem aligned with MoCKA philosophy ("Knowledge changes decisions"). Option D recommended to avoid premature implementation before policy is defined.

### Q2: Governance Boundaries
**Question:** Should knowledge binding create new decision authority, or just inform human decisions?

**Answer:** Knowledge binding should NOT create new authority. It should:
- ✓ Make past knowledge visible to decision-makers
- ✓ Allow human to consider historical patterns
- ✗ NOT automatically change human decisions
- ✗ NOT create AI autonomous decision capacity

**Current Status:** Design includes authority preservation (Phase B still requires human oversight).

### Q3: Evidence Requirements
**Question:** What counts as proof that knowledge influenced a decision?

**Options:**
- A. Score changed vs. baseline (with same intent, different enrichment)
- B. Memory field populated + DB verification
- C. Human explicitly states "I considered this memory"
- D. All of the above (most rigorous)

**Current Design:** Supports A + B. Would require separate authorization for C.

### Q4: Failure Modes
**Question:** What happens if binding ledger loses sync with decision_ledger?

**Answer:** Integrity check required. Recommend:
- ✓ Regular audit comparing decision_ledger vs. memory_binding_ledger
- ✓ Alert if memory_id exists but decision_id missing
- ✓ Alert if decision_id exists but no memory_influence_trace

**Current Status:** Would be implemented in Phase E verification.

---

## WHAT'S BEEN COMPLETED THIS SESSION

### Deliverables
1. **STEP11_INSTITUTIONAL_MEMORY_DECISION_BINDING_AUDIT_20260920.md** (12.7 KB, UTF-8 ✓)
   - Complete code investigation
   - Evidence classification (RECORDED vs. USED)
   - 6 critical findings
   - Implementation design (Phases A-E)
   - Verification criteria

2. **Code Review** (6 files examined)
   - memory/memory_store.py — ✓ Working
   - memory/memory_retriever.py — ✓ Working  
   - memory/memory_context_builder.py — ✓ Working
   - memory/memory_pipeline.py — ⚠ Incomplete
   - semantic/intent_classifier.py — ✗ Gap identified
   - decision/decision_engine.py — ✗ Gap identified

### What Was NOT Done (Per GL7 Governance Block)
- ✗ No code modifications (correctly blocked)
- ✗ No system changes (correctly enforced)
- ✗ No production impact (correctly prevented)
- ✗ No automatic decisions created (correctly protected)

**GL7 Block Verdict:** CORRECT AND APPROPRIATE. System properly prevented scope changes without authorization.

---

## RECOMMENDATIONS FOR HUMAN GATE

### Immediate (This Week)
1. **Review** STEP11_INSTITUTIONAL_MEMORY_DECISION_BINDING_AUDIT_20260920.md
2. **Decide** one of four options above (Q1: Scope Authorization)
3. **Record** decision in decision_ledger with rationale

### If Option A Selected (Full Implementation)
1. **Authorize** Phases A-E with explicit scope boundaries
2. **Assign** implementation to next session
3. **Schedule** verification checkpoint after Phase C (engine bridge)

### If Option B Selected (Ledger Only)
1. **Authorize** Phase D only
2. **Defer** Phases A-C to future decision
3. **Continue** design work on scoring policy in parallel

### If Option C or D Selected (Defer/Investigate Only)
1. **Archive** STEP 11 findings as reference
2. **Open** parallel work on "Knowledge-to-Decision Transition Rules" (already flagged in essence as needed)
3. **Resume** STEP 11 implementation after rules are defined

---

## CRITICAL PRINCIPLE (DO NOT LOSE)

> **「止めるのは権限。進めるのは証拠。」**
> (Authority frozen; Evidence moves forward)

This investigation gathered evidence. Authorization to proceed is separate from evidence gathering. The GL7 block is correct — it prevents evidence from crossing into implementation without approval.

---

## TECHNICAL DEBT RECORDED

This investigation revealed that the following are incompletely specified:
1. Scoring algorithm behavior when enriched_context is available
2. Definition of "influence" vs. "consideration"  
3. Ledger schema for memory_binding_ledger.jsonl
4. Verification protocol for binding verification

These become implementation requirements IF authorization is granted.

---

## SIGN-OFF

**Investigation Status:** COMPLETE ✓  
**Evidence Quality:** HIGH (code-verified, 6-file scope, distinctions preserved)  
**Authorization Status:** PENDING  
**System State:** HOLD/FAIL-CLOSED (correctly maintained)

**Ready for:** Human Gate Review and Decision

**Next Gate:** Authorization decision on Phases A-E scope
