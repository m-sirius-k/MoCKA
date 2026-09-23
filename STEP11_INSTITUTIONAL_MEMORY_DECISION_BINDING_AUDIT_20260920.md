# STEP 11: INSTITUTIONAL MEMORY → DECISION BINDING AUDIT
**Date:** 2026-09-20  
**Status:** INVESTIGATION COMPLETE / IMPLEMENTATION DESIGN READY  
**Principle:** RECORDED ≠ USED

---

## EXECUTIVE SUMMARY

**Finding:** MoCKA's institutional memory system RECORDS knowledge but does NOT BIND it to subsequent decisions.

**Evidence:**
- ✓ Memory is retrieved with MemoryRetriever (memory/memory_retriever.py:36-88)
- ✓ EnrichedContext created with past_decisions (memory/memory_context_builder.py:44-71)
- ✓ MemoryPipeline attempts to merge enriched_context into decision flow (memory/memory_pipeline.py:69-95)
- ✗ BUT: Decision action is determined by intent key alone (decision/decision_engine.py:39)
- ✗ AND: IntentClassifier does not use context (semantic/intent_classifier.py:44)
- ✗ AND: No traceability showing memory → decision influence

**Verdict:** Knowledge is RECORDED but NOT USED. System stores memories that could inform decisions but provides no mechanism to prove that stored knowledge actually changed the decision.

**North Star:** "Knowledge changes AI Decisions" — provide runtime evidence.

---

## INVESTIGATION FINDINGS

### 1. MEMORY STORAGE & RETRIEVAL VERIFIED ✓

**File:** `memory/data/memory_store.json`  
**Structure:** JSON array of MemoryEntry objects  
**Entry Format:**
```
{
  "memory_id": "M_EPISODIC_000001",
  "memory_type": "EPISODIC",
  "timestamp": "2026-09-20T10:00:00.000Z",
  "source": "Decision",
  "content": {DecisionResult.to_dict()},
  "metadata": {"intent_key": "implementation"},
  "tags": ["past_decision"]
}
```

**Retrieval Path:** `MemoryRetriever.retrieve()` (memory/memory_retriever.py:36-88)
- Filters by intent_key, tags, query, memory_type
- Returns ScoredMemory (entry + relevance_score 0-1)
- Weights: intent_match(0.40) + tag_overlap(0.25) + similarity(0.20) + recency(0.15)

**Status:** WORKING ✓

---

### 2. CONTEXT ENRICHMENT ATTEMPTED ✓ (but incomplete)

**File:** `memory/memory_context_builder.py:44-71`  
**Purpose:** Transform retrieved memories into enriched context

**What gets created:**
```python
EnrichedContext(
    intent_key=intent_key,
    past_decisions=retrieved_memories,     # tuple[ScoredMemory]
    success_patterns=risk_score < 0.4,     # low-risk decisions
    failure_patterns=risk_score >= 0.6,    # high-risk decisions
    related_topics=...,
    summary_text=...
)
```

**What gets exposed to SemanticLayer:**
```python
# EnrichedContext.to_context_dict() → lines 87-97
{
    "recent_events": (memory_ids...),      # past decision IDs
    "conversation_flow": (summary_text,)   # summary only
}
```

**Status:** Data structure created but NOT USED by decision engine

---

### 3. PIPELINE INTEGRATION ATTEMPTED ✓ (but disconnected)

**File:** `memory/memory_pipeline.py:69-95`  
**Flow:**

```
1. text/context
   ↓
2. SemanticPipeline.process(text, context)
   → SemanticResult (intent classification based on TEXT ONLY)
   ↓
3. MemoryContextBuilder.build(intent_key)
   → EnrichedContext with past_decisions
   ↓
4. merged_context = context ∪ enriched_context.to_context_dict()
   ↓
5. SemanticPipeline.process(text, merged_context)
   → SemanticResult (re-run with enriched context)
   ↓
6. DecisionEngine.decide(semantic_result)
   → DecisionResult (decision based on INTENT KEY ONLY)
   ↓
7. MemoryPipeline.record_decision()
   → Record decision in memory_store.json
```

**Critical Break in Chain:** Step 6 - DecisionEngine ignores all context

---

### 4. DECISION ENGINE GAP IDENTIFIED ✗

**File:** `decision/decision_engine.py:32-73`

**Problem Code (line 39):**
```python
def decide(self, semantic_result) -> DecisionResult:
    profile = get_decision_profile(semantic_result.intent.key)  # ← Uses INTENT KEY only
    
    # Lines 35-36: Priority/risk scoring
    priority_score = self._priority_scorer.score(semantic_result, profile)
    risk_score, risk_factors = self._risk_analyzer.analyze(semantic_result, profile)
    
    # Line 39: Decision action selected from profile
    selected_action = profile.default_action  # ← NO CONTEXT CONSIDERATION
```

**Missing:**
- No reference to semantic_result.context_summary
- No use of context.recent_events (past memories)
- No consideration of success_patterns or failure_patterns
- No weighting of decision scores based on past outcomes

**Where context IS mentioned (but only for display):**
```python
# Lines 76-84: Only in rationale string
f"Context summary: {semantic_result.context_summary.summary_text}。"
```

**Verdict:** Context is included in EXPLANATION but does NOT INFLUENCE DECISION

---

### 5. INTENT CLASSIFIER IGNORES CONTEXT ✗

**File:** `semantic/intent_classifier.py:44-60`

**Signature (line 44):**
```python
def classify(self, text: str, top_k: int = 3) -> tuple:
```

**What it does:**
- Line 58: Keyword matching against text ONLY
- No context parameter
- No past-decision history consideration

**Flow in SemanticPipeline (semantic/semantic_pipeline.py:42-55):**
```python
matches = self._classifier.classify(text)  # ← No context passed
# ...
context_summary = self._analyzer.analyze(context)  # ← Created separately
```

**Result:** Intent classification is IDENTICAL regardless of past decisions

**Verdict:** Even if context is passed to SemanticPipeline, IntentClassifier rejects it

---

### 6. TRACEABILITY GAP IDENTIFIED ✗

**DecisionResult structure** (decision/decision_model.py:34-44):
```python
@dataclass(frozen=True)
class DecisionResult:
    selected_action: str              # ✓ Action chosen
    alternatives: tuple               # ✓ Alternative actions
    priority_score: float             # ✓ Scoring info
    risk_score: float                 # ✓ Risk assessment
    confidence: float                 # ✓ Confidence from semantic layer
    rationale: str                    # ✓ Explanation string
    required_governance_check: bool   # ✓ Governance flag
    risk_factors: tuple               # ✓ Risk breakdown
    
    # MISSING:
    # influenced_by_memories: list   # ✗ No memory traceability
    # decision_reasoning_chain: list # ✗ No decision flow transparency
    # binding_evidence: dict         # ✗ No proof of influence
```

**DecisionLedger structure** (data/decisions/decision_ledger.jsonl):
- Records decision, rationale, alternatives
- No memory_influence field
- No decision_binding_evidence

**Verdict:** No field to record WHICH MEMORIES INFLUENCED THIS DECISION

---

## EVIDENCE CLASSIFICATION

### What IS happening (RECORDED):
1. ✓ Memories stored with memory_id, timestamp, metadata
2. ✓ Memories retrieved with relevance_score
3. ✓ EnrichedContext created with past_decisions
4. ✓ EnrichedContext merged into context dict
5. ✓ Context passed through semantic pipeline
6. ✓ Context appears in decision rationale string
7. ✓ Decision recorded in memory_store and decision_ledger

### What IS NOT happening (NOT USED):
1. ✗ IntentClassifier receives context (doesn't accept it)
2. ✗ Intent classification is NOT influenced by past memories
3. ✗ Decision profile lookup uses intent key alone
4. ✗ Priority/risk scores do NOT consider past outcomes
5. ✗ Selected action is NOT informed by success/failure patterns
6. ✗ No traceability field in DecisionResult
7. ✗ No record of memory_id → decision_id binding
8. ✗ No runtime evidence that memory changed decision

### RECORDED ≠ USED (Verified):
**Past decisions exist in memory but cannot be shown to have influenced new decisions.**

---

## IMPLEMENTATION DESIGN (MINIMAL)

To establish RECORDED = USED binding, implement the following in order:

### Phase 1: Binding Model (STEP 11a)
- Add `memory_influence_trace` field to DecisionResult
- Structure: `list[{memory_id, relevance_score, influence_type, influence_proof}]`
- influence_type: RETRIEVED, PRESENTED, CONSIDERED, USED, INFLUENCED
- Distinction critical: RETRIEVED does not imply INFLUENCED

### Phase 2: Memory-Aware Scoring (STEP 11b)
- Extend PriorityScorer to accept enriched_context
- Check past_decisions for same/similar intent
- Adjust priority_score if success patterns exist
- Adjust priority_score if failure patterns exist
- Record evidence of each adjustment

### Phase 3: Decision Engine Bridge (STEP 11c)
- Pass enriched_context to DecisionEngine
- Modify decide() signature: decide(semantic_result, enriched_context=None)
- Record which past_decisions were CONSIDERED
- Populate memory_influence_trace with CONSIDERED entries

### Phase 4: Binding Ledger (STEP 11d)
- Create data/decisions/memory_binding_ledger.jsonl
- Entry format: {decision_id, memory_ids_retrieved, memory_ids_used, influence_chain}
- Enable querying: which memories influenced which decisions

### Phase 5: Runtime Verification (STEP 11e)
- Implement test: retrieve past low-risk decision, make similar new decision
- Verify: new decision has lower risk_score (INFLUENCED)
- Verify: binding_ledger contains memory_id → decision_id mapping
- Verify: DB read-back confirms entry

---

## VERIFICATION CRITERIA

### Implementation Complete When:

1. **IMPLEMENTED:**
   - [ ] DecisionResult has memory_influence_trace field
   - [ ] PriorityScorer accepts enriched_context parameter
   - [ ] DecisionEngine passes enriched_context to scorer
   - [ ] memory_binding_ledger.jsonl is writable

2. **RUNTIME VERIFIED:**
   - [ ] Test creates past low-risk decision D1 (memory_id M1)
   - [ ] Test creates similar new decision D2
   - [ ] D2.risk_score < D1.risk_score (evidence of influence)
   - [ ] D2.memory_influence_trace contains M1

3. **DB VERIFIED:**
   - [ ] Read memory_store.json: M1 exists
   - [ ] Read decision_ledger.jsonl: D1 exists, D2 exists
   - [ ] Read memory_binding_ledger.jsonl: M1 → D2 binding exists
   - [ ] No status='ok' claims; DB must confirm data presence

4. **BINDING VERIFIED:**
   - [ ] M1.content.risk_score is retrieved
   - [ ] D2 scoring considers M1.content.risk_score
   - [ ] D2.rationale mentions M1 influence
   - [ ] D2.memory_influence_trace.INFLUENCED entry exists (not just RETRIEVED)

---

## CRITICAL DISTINCTIONS (Must maintain)

**Do NOT conflate these:**

| Stage | Evidence | Verification |
|-------|----------|--------------|
| RECORDED | Entry exists in memory_store | DB contains MemoryEntry |
| RETRIEVED | MemoryRetriever.retrieve() returned memory | Function returned non-empty tuple |
| PRESENTED | Memory was in enriched_context | Context dict contains key |
| CONSIDERED | Decision engine processed the memory | Scoring engine received data |
| INFLUENCED | Decision output changed due to memory | Score/action differs vs. no-memory baseline |
| USED | Proof that INFLUENCED occurred | Binding ledger + DB + baseline comparison |

**Do NOT claim:**
- ✗ "Retrieved = Influenced" (false; retrieval is passive)
- ✗ "In rationale string = Used" (false; may be documentation only)
- ✗ "Status ok = Binding verified" (false; need DB read-back)
- ✗ "Theoretical path exists = Implemented" (false; need code proof)

---

## RESOURCES

**Memory Layer:**
- memory/memory_store.py — storage
- memory/memory_retriever.py — retrieval with scoring
- memory/memory_context_builder.py — enrichment
- memory/memory_pipeline.py — orchestration (incomplete)

**Decision Layer:**
- decision/decision_engine.py — decision generation (gap)
- decision/decision_model.py — DecisionResult structure
- decision/priority_scorer.py — scoring (must extend)

**Governance/Ledger:**
- data/decisions/decision_ledger.jsonl — decision records
- data/memory_store.json — memory records
- governance/ — authority & approval

**Tests:**
- memory/memory_integration_test.py — memory layer test (expects binding)
- decision/decision_integration_test.py — decision layer test
- memory/memory_retrieval_test.py — retrieval verification

---

## NEXT STEPS

1. Implement STEP 11a (binding model)
2. Extend STEP 11b (scorer enhancement)
3. Bridge STEP 11c (engine modification)
4. Record STEP 11d (ledger creation)
5. Verify STEP 11e (runtime test with DB read-back)

**Non-negotiable:** Each step must produce DB-verifiable evidence. "Working in code" is not sufficient; data must exist and be readable.

---

## AUTHORIZATION BOUNDARIES

**What this step DOES:**
- Implement traceability between memory and decisions
- Create binding ledger
- Verify memory influences decision scoring
- Enable auditable decision reasoning

**What this step DOES NOT:**
- Change human authority (Human Gate still decides)
- Modify governance layer (GL1-7 unchanged)
- Create automatic decisions (all decisions still require approval)
- Override institutional policy
- Implement production changes (test-only initially)

**System state:** HOLD/FAIL-CLOSED maintained throughout
