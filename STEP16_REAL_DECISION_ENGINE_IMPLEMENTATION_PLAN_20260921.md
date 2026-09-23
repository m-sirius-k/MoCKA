# STEP 16: REAL DECISION ENGINE IMPLEMENTATION PLAN

**Date:** 2026-09-21  
**Purpose:** Implementation plan for Real Decision Engine per STEP 15 Contract  
**Scope:** Planning only — no code changes / no schema changes / no runtime activation

---

## 1. SCOPE

**What This Plan Defines:**
- governance_evaluate() replacement strategy
- Evidence integration points
- Decision formation algorithm boundaries
- Decision ID generation strategy
- Runtime Decision persistence
- Authorization/Human Gate integration
- Institutional Record connection (existing MCP endpoint reuse)
- Failure/UNKNOWN handling
- Verification approach
- Implementation order with dependency chain

**What This Plan Does NOT Define:**
- Code implementation (syntax, libraries, etc.)
- Schema migration
- Database structure changes
- STEP 11 Knowledge-Decision Binding (deferred)
- Production deployment strategy
- Performance tuning

---

## 2. CURRENT RUNTIME

**governance_evaluate() Current State:**

```python
# runtime/governance_client.py line 14-41
def evaluate(plan):
    plan_id = plan.get("plan_id", "UNKNOWN")
    intent_id = plan.get("intent_id", "UNKNOWN")
    steps = plan.get("steps", [])
    
    decision_record_id = str(uuid.uuid4())  # STUB: UUID
    decision = "PASS"                         # STUB: hardcoded
    reason = f"Plan {plan_id} passed governance check (stub)"
    
    return {
        "decision_record_id": decision_record_id,
        "governance_decision": decision,
        "governance_reason": reason,
        "timestamp": _now()
    }
```

**Current Limitations:**
- ✗ No evidence input
- ✗ No evidence evaluation
- ✗ No rationale generation
- ✗ No knowledge tracking
- ✗ Always returns PASS
- ✗ Decision ID is UUID (not DC_YYYYMMDD_NNN)
- ✗ No RECONSIDER handling

**Current Callers:**
- main_loop.py line 58: `governance_result = governance_evaluate(plan)`
- Passes result to hg_gateway.authorize_and_execute()
- Expects: decision_record_id, governance_decision, governance_reason, timestamp

---

## 3. TARGET RUNTIME

**Real governance_evaluate() Design:**

```python
def governance_evaluate(
    plan,
    evidence_retriever=None,  # Optional EvidenceLedger interface
    knowledge_retriever=None  # Optional MemoryStore interface (HG-D2)
):
    """
    Real Decision Engine based on STEP 15 Contract.
    
    Input:
      plan: dict with plan_id, intent_id, steps, action_ids
      evidence_retriever: EvidenceLedger interface (REQUIRED for HG-D3)
      knowledge_retriever: MemoryStore interface (OPTIONAL per HG-D2)
    
    Process:
      1. Validate plan
      2. Retrieve evidence (HG-D1)
      3. FOR each step: evaluate supporting evidence
      4. Build rationale from evidence (HG-D3)
      5. Determine decision: PASS / RECONSIDER / UNKNOWN (HG-D8)
      6. IF knowledge_retriever: track conditionally used knowledge (HG-D2)
      7. Generate runtime decision
    
    Output:
      {
        "decision": str (PASS | RECONSIDER | UNKNOWN),
        "rationale": str (evidence-based explanation),
        "evidence_ids": [list of evidence record IDs],
        "knowledge_ids_used": [list if knowledge actually used, else []],
        "timestamp": ISO8601,
        "step_decisions": {step_id: {decision, evidence_ids}} (optional)
      }
    
    Fail-Closed:
      - Evidence unavailable → decision = UNKNOWN
      - Partial evidence → decision = RECONSIDER
      - Decision formation error → decision = UNKNOWN, rationale = error message
    """
    pass
```

**Key Changes:**
- Input: plan + evidence (required) + knowledge (optional)
- Output: Real decision + rationale + evidence refs + conditional knowledge refs
- Behavior: Evidence-based, RECONSIDER for partial, UNKNOWN for gaps
- Caller compatibility: Must not break existing hg_gateway call

---

## 4. IMPLEMENTATION BOUNDARIES

**Timeline (T0-T8):**

```
T0: Plan Reception (existing)
    plan.json loaded in main_loop.py
    ↓
T1: Evidence Retrieval & Evaluation (NEW)
    governance_evaluate() calls evidence_ledger.query()
    Evidence filtering by plan.steps (applies_to/decision_id match)
    Evidence sufficiency check (complete vs. partial)
    ↓
T2: Real Decision Formation (NEW)
    IF complete evidence: decision = PASS
    IF partial evidence: decision = RECONSIDER (HG-D8)
    IF evidence unavailable: decision = UNKNOWN
    ↓
T3: Rationale Generation (NEW)
    Evidence → text explanation mapping
    Supporting/missing classification per step
    ↓
T4: Decision Identity Generation (NEW)
    Generate DC_YYYYMMDD_NNN (not UUID)
    Sequence counter management
    ↓
T5: Runtime Decision Persistence (EXISTING + NEW mapping)
    Runtime Decision object creation
    Mapping to Authorization/Institutional Record (TBD by T6-T8)
    ↓
T6: Authorization / Human Gate (EXISTING)
    hg_gateway.authorize_and_execute()
    RECONSIDER → escalate to Human Reconsideration (NEW routing)
    ↓
T7: Execution (EXISTING)
    action_executor.execute_action() if authorized
    ↓
T8: Institutional Record Persistence (EXISTING)
    mocka_decision_write() MCP endpoint (external caller)
    (NOT automatic from Runtime Decision yet)
```

**Boundary Rationale:**
- T0-T3: New decision logic
- T4: New ID generation
- T5-T8: Minimal change to existing paths
- mocka_decision_write remains external MCP (no auto-generation)

---

## 5. EVIDENCE INTEGRATION

**Evidence Store (Verified):**
- Location: PlanningCaliber/workshop/vasAI_Project/core/evidence_ledger.py
- Type: SQLite (vasai_evidence.db)
- Reader: EvidenceLedger class (inferred .query_evidence() method)

**Evidence Record Schema (Verified):**
```
id:            TEXT (PK, EV20260921_000001 format)
event_id:      TEXT (event reference)
decision_id:   TEXT (decision reference)
evidence_type: TEXT (FACT, ASSUMPTION, CONSTRAINT, INTENT)
content:       TEXT (JSON)
source:        TEXT (origin)
confidence:    REAL (0.0-1.0)
created_at:    TEXT (ISO8601)
hash:          TEXT (SHA256)
prev_hash:     TEXT (chain)
```

**Integration Points:**

```python
# governance_evaluate() implementation boundary

def _get_step_evidence(step_id, plan_id, evidence_ledger):
    """Query evidence for a plan step."""
    # Step-level matching: use event_id or decision_id?
    # Assumption: evidence.event_id or evidence.decision_id links to plan context
    # ACTION: Confirm evidence query method in EvidenceLedger class
    evidence_records = evidence_ledger.query(
        lambda e: (e['event_id'] == step_id or 
                   e['decision_id'] == plan_id)  # TBD: exact match logic
    )
    return evidence_records

def _evaluate_evidence_coverage(plan_steps, evidence_by_step):
    """Classify evidence as complete / partial / missing."""
    complete_steps = []
    partial_steps = []
    missing_steps = []
    
    for step in plan_steps:
        ev = evidence_by_step.get(step.id, [])
        if len(ev) > 0:
            complete_steps.append(step.id)
        else:
            missing_steps.append(step.id)
    
    # HG-D8: partial evidence → RECONSIDER
    is_complete = len(missing_steps) == 0
    is_partial = len(missing_steps) > 0 and len(complete_steps) > 0
    is_missing = len(complete_steps) == 0
    
    return {
        "complete": is_complete,
        "partial": is_partial,
        "missing": is_missing,
        "missing_steps": missing_steps,
        "evidence_coverage": {step: evidence_by_step.get(step, []) 
                              for step in plan_steps}
    }

def _build_rationale(evidence_coverage):
    """Generate evidence-based rationale."""
    if evidence_coverage["complete"]:
        return f"All steps ({len(evidence_coverage)}) have supporting evidence"
    elif evidence_coverage["partial"]:
        return f"Steps {evidence_coverage['complete']} supported; " \
               f"steps {evidence_coverage['missing']} lack evidence"
    else:
        return "No supporting evidence found for any step"
```

**Placeholder Points:**
- How to query evidence by step_id? (needs EvidenceLedger interface confirmation)
- confidence field usage? (evidence weighting not yet decided)
- evidence_type filtering? (FACT vs ASSUMPTION priority?)

---

## 6. DECISION FORMATION

**Algorithm (per HG-D1, D3, D8):**

```python
def governance_evaluate(plan, evidence_retriever=None, knowledge_retriever=None):
    # Precondition: plan validation (existing, keep)
    if not plan or not plan.get("plan_id"):
        return {"decision": "UNKNOWN", 
                "rationale": "Invalid plan", 
                "timestamp": _now()}
    
    # Step 1: Evidence retrieval (NEW)
    if evidence_retriever is None:
        return {"decision": "UNKNOWN",
                "rationale": "Evidence store unavailable",
                "timestamp": _now()}
    
    try:
        evidence_coverage = _evaluate_evidence_coverage(
            plan.get("steps", []),
            _get_step_evidence(plan.get("plan_id"), evidence_retriever)
        )
    except Exception as e:
        return {"decision": "UNKNOWN",
                "rationale": f"Evidence retrieval failed: {e}",
                "timestamp": _now()}
    
    # Step 2: Decision formation (HG-D8 routing)
    if evidence_coverage["complete"]:
        decision = "PASS"
        rationale = _build_rationale(evidence_coverage)
        evidence_ids = [ev["id"] for ev in evidence_coverage["evidence_by_step"].values()]
    elif evidence_coverage["partial"]:
        decision = "RECONSIDER"  # HG-D8: partial → send to Human
        rationale = f"Partial evidence: {evidence_coverage['missing_steps']} lack support"
        evidence_ids = [ev["id"] for ev in evidence_coverage["evidence_by_step"].values()]
    else:  # missing
        decision = "UNKNOWN"
        rationale = "No evidence found for any step"
        evidence_ids = []
    
    # Step 3: Knowledge conditional trace (HG-D2, optional)
    knowledge_ids_used = []
    if knowledge_retriever is not None:
        try:
            # Query knowledge (logic TBD)
            # Only record if actually used (not just retrieved)
            # ACTION: define "actually used" vs. "retrieved"
            knowledge_items = knowledge_retriever.query(lambda k: _is_relevant(k, plan))
            if knowledge_items:
                # Mark as "conditionally used" for STEP 11 binding prep
                knowledge_ids_used = [k["id"] for k in knowledge_items]
        except:
            pass  # Knowledge failure is not decision blocker (HG-D2)
    
    # Step 4: Return runtime decision
    return {
        "decision": decision,
        "rationale": rationale,
        "evidence_ids": evidence_ids,
        "knowledge_ids_used": knowledge_ids_used,
        "timestamp": _now(),
        "step_decisions": evidence_coverage.get("by_step", {})  # For detail
    }
```

**Decision Status Mapping:**

| Evidence State | Decision | HG Basis | Routing |
|---|---|---|---|
| Complete (all steps) | PASS | HG-D1 | Normal execution path |
| Partial (some steps) | RECONSIDER | HG-D8 | → Human Reconsideration → BLOCKED |
| Missing (no steps) | UNKNOWN | Fail-closed | → BLOCKED |
| Retrieval failed | UNKNOWN | Fail-closed | → BLOCKED |

---

## 7. DECISION IDENTITY

**DC_YYYYMMDD_NNN Generation Strategy:**

**Current State:**
- Stub: `decision_record_id = str(uuid.uuid4())`
- Location: governance_client.py line 31

**Target State:**
- Format: DC_20260921_001, DC_20260921_002, etc.
- Generation: per-day sequence counter
- Persistence: decision_ledger.jsonl (already append-only)

**Implementation Plan:**

```python
def _next_decision_id():
    """
    Generate next DC_YYYYMMDD_NNN decision_id.
    
    Design:
      1. Get today's date (YYYYMMDD)
      2. Read decision_ledger.jsonl (or sequence counter store)
      3. Filter records for today: DC_YYYYMMDD_*
      4. Extract max NNN
      5. Return DC_YYYYMMDD_{max+1:03d}
      6. If no records today: DC_YYYYMMDD_001
    
    Concurrency:
      - Append-only ledger provides natural sequencing
      - Need file lock if concurrent governance_evaluate calls
      - ACTION: confirm if concurrent calls possible in main_loop
    
    Location:
      - Candidate 1: governance_client.py (before return)
      - Candidate 2: mocka_mcp_server.py (line 1125, _next_decision_id)
      - ACTION: check if _next_decision_id already exists
    
    Retry:
      - If sequence generation fails, decision formation should fail
      - Does NOT retry with fallback UUID (fail-closed)
    """
    pass
```

**Placeholder Points:**
- Is `_next_decision_id()` already implemented in mocka_mcp_server.py?
- Does governance_client need to call it, or is it called by mocka_decision_write?
- Concurrency: single-threaded main_loop or concurrent governance calls?

---

## 8. RUNTIME DECISION PERSISTENCE

**Runtime Decision Object (Not Institutional Record):**

```python
runtime_decision = {
    "decision": "PASS" | "RECONSIDER" | "UNKNOWN",
    "rationale": str,
    "evidence_ids": [str],  # EV20260921_000001 format
    "knowledge_ids_used": [str],  # MemoryRecord.id if used
    "timestamp": ISO8601,
    "step_decisions": {  # Optional detail
        "step_0": {"decision": "PASS", "evidence_ids": [...]},
        "step_1": {"decision": "UNKNOWN", "evidence_ids": []},
    }
}
```

**Carrier Through T4-T8:**

```python
# main_loop.py line 80-85 (existing)
execution_context = authorize_and_execute(
    plan=plan,
    governance_decision=governance_result,  # ← passes runtime_decision
    governance_record_id=governance_result.get("decision_record_id"),  # ← needs update
    execute_fn=execute_action_with_context
)
```

**Change Required:**
- governance_result now carries more fields (rationale, evidence_ids, knowledge_ids_used)
- hg_gateway needs to extract decision status for RECONSIDER routing
- Institutional Record can defer until T8 (mocka_decision_write)

---

## 9. AUTHORIZATION / HUMAN GATE

**RECONSIDER Routing (HG-D8):**

```python
# hg_gateway.py line 54-60 (existing)
hg_decision_result = _get_hg_decision(execution_context)

# NEW: Check for RECONSIDER
governance_decision = execution_context.governance_decision  # Now: PASS | RECONSIDER | UNKNOWN

if governance_decision == "RECONSIDER":
    # HG-D8: Send to Human Reconsideration
    execution_context.execution_status = "RECONSIDER_ESCALATION"
    execution_context.institutional_closure = "BLOCKED"
    # Route to Human Reconsideration queue (TBD by HG)
    return execution_context  # Block execution
else:
    # Existing HG authorization logic
    # (currently mocked, keep as is)
    hg_decision = _get_hg_decision(execution_context)
    # ... rest of existing logic
```

**Action Items:**
- How to route RECONSIDER to Human? (new MCP tool? existing escalation path?)
- HG decision is currently mocked (keep mock; real HG separate HG decision)
- Authorization is independent of Decision (HG-D4) — maintain

---

## 10. INSTITUTIONAL RECORD MAPPING

**Current State:**
- mocka_decision_write() is external MCP endpoint (line 1107-1168)
- All 15 fields provided as arguments by caller
- NOT automatically called by runtime

**Implementation Strategy (OPTION B: Keep External):**

```python
# T8: After execution completes (or RECONSIDER escalation)
# Somewhere (TBD: which runtime component?):

if execution_context.execution_status != "RECONSIDER_ESCALATION":
    # Call mocka_decision_write via MCP
    # Runtime Decision → Institutional Record mapping
    
    institutional_record_input = {
        # From Runtime Decision
        "decision": runtime_decision["decision"],
        "rationale": runtime_decision["rationale"],
        "related_events": runtime_decision["evidence_ids"],  # evidence IDs → related_events
        
        # From plan
        "title": f"Decision on plan {plan_id}",
        "context": f"Intent: {plan_id}, Steps: {len(plan_steps)}",
        "impact": f"Execution of plan {plan_id}",
        
        # From decision/authorization (NOT auto-generated from Decision)
        "approved_by": hg_decision_result.get("approver"),  # From HG, NOT from Decision
        "alternatives": [{"option": "execute plan", "rejected_reason": "N/A"}],  # Stub
        
        # Auto-generated
        "decision_id": "DC_YYYYMMDD_NNN",  # Generated in T4
        "status": "Active",
        "supersedes": None,
    }
    
    # Call mocka_decision_write (external MCP)
    # mcp_client.mocka_decision_write(**institutional_record_input)
```

**Key Design Points:**
- Runtime Decision and Institutional Record remain separate
- mocka_decision_write retains all caller responsibility (not auto-generated)
- approved_by comes from HG, not Decision (HG-D4 maintained)
- evidence_ids → related_events mapping
- knowledge_ids_used NOT persisted to Institutional Record yet (STEP 11 deferred)

---

## 11. KNOWLEDGE CONDITIONAL TRACE

**Per HG-D2: Knowledge optional, record only if used:**

```python
# In governance_evaluate()

knowledge_ids_used = []
if knowledge_retriever is not None:
    try:
        # Retrieve knowledge relevant to plan
        knowledge_items = knowledge_retriever.query(
            predicate=lambda k: _is_knowledge_relevant(k, plan)
        )
        
        # Mark as "used" only if governance_evaluate actually uses them
        # (not just retrieved)
        # ACTION: define "actually used" — does rationale cite it? does evaluation reference it?
        
        if knowledge_items and _decision_uses_knowledge(runtime_decision, knowledge_items):
            knowledge_ids_used = [k["id"] for k in knowledge_items]
    except:
        pass  # Knowledge unavailable is not decision blocker
```

**Runtime Decision Carries:**
```python
"knowledge_ids_used": knowledge_ids_used  # Empty [] if not used; populated if used
```

**Institutional Record:**
- knowledge_ids_used NOT persisted yet (STEP 11 binding deferred)
- But runtime_decision preserves it for future STEP 11 binding_ledger

**STEP 11 Binding Prep (Not Implemented):**
- runtime_decision.knowledge_ids_used will be used to create binding_ledger records
- binding_ledger links decision_id ↔ knowledge_ids for audit trail

---

## 12. FAILURE HANDLING

**Fail-Closed Per Existing Principles:**

| Failure | Current Behavior | Real Engine Behavior | Rationale |
|---|---|---|---|
| Evidence unavailable | N/A | decision = UNKNOWN | HG-D3 requires evidence; missing → UNKNOWN |
| Evidence query error | N/A | decision = UNKNOWN | Service unavailable → fail-closed |
| Partial evidence | N/A | decision = RECONSIDER | HG-D8 routing |
| Decision formation error | N/A | decision = UNKNOWN | Exception → fail-closed |
| Plan invalid | Plan validation fails | Plan validation fails | Existing, keep |
| Knowledge unavailable | N/A | knowledge_ids_used = [] | HG-D2: optional |
| Knowledge query error | N/A | knowledge_ids_used = [] | Fail-closed, no decision blocker |
| Decision ID generation fails | N/A | Return error, BLOCK | Persistence prerequisite |
| Institutional record write fails | N/A | Log error, continue | Non-blocking (async) |
| Authorization mocked | Existing | Continue (mocked) | Real HG separate decision |
| RECONSIDER escalation fails | N/A | Log error, BLOCK execution | Safety: unknown escalation → block |

---

## 13. VERIFICATION PLAN

**Testing Strategy (No Implementation Yet):**

1. **Complete Evidence Path:**
   - Scenario: Plan with 3 steps, all have supporting evidence
   - Expected: decision = PASS, rationale = "All steps supported"

2. **Partial Evidence Path (HG-D8):**
   - Scenario: Plan with 3 steps, 2 have evidence, 1 missing
   - Expected: decision = RECONSIDER, rationale = "Steps 0,1 supported; step 2 missing"

3. **Missing Evidence Path:**
   - Scenario: Plan with 3 steps, none have evidence
   - Expected: decision = UNKNOWN, rationale = "No supporting evidence"

4. **Evidence-Based Rationale:**
   - Scenario: Plan step with multiple evidence records
   - Expected: rationale incorporates evidence content (not stub "passed governance")

5. **Decision ID Uniqueness:**
   - Scenario: 10 consecutive decision generations
   - Expected: DC_20260921_001, DC_20260921_002, ..., DC_20260921_010

6. **Decision ≠ Authorization:**
   - Scenario: decision = PASS, but HG denies authorization
   - Expected: execution still BLOCKED (HG-D4 maintained)

7. **Knowledge Conditional:**
   - Scenario: Plan with relevant knowledge in MemoryStore
   - Expected: IF governance_evaluate uses it, knowledge_ids_used populated; else empty

8. **Knowledge NOT Used:**
   - Scenario: Plan with irrelevant knowledge
   - Expected: knowledge_ids_used = [] (no false binding trace)

9. **RECONSIDER → Execution BLOCKED:**
   - Scenario: decision = RECONSIDER
   - Expected: execution_context.execution_status = BLOCKED

10. **Fail-Closed on Error:**
    - Scenario: Evidence query throws exception
    - Expected: decision = UNKNOWN (not retry loop)

11. **Institutional Record Mapping:**
    - Scenario: Runtime Decision with evidence_ids
    - Expected: mocka_decision_write receives related_events = evidence_ids

12. **Restart/Retry Behavior:**
    - Scenario: Decision ID counter lost, restart governance_evaluate
    - Expected: Counter recovered from decision_ledger.jsonl, no duplicates

---

## 14. IMPLEMENTATION ORDER

**Dependency Chain:**

```
Phase 1: Evidence Integration (PREREQUISITE)
  1.1. Confirm EvidenceLedger class interface (query method signature)
  1.2. Test evidence_ledger.py accessibility from runtime/
  1.3. Design step-to-evidence matching logic (applies_to / decision_id)

Phase 2: Real Decision Formation (CORE)
  2.1. Implement governance_evaluate() real logic
       (replaces STUB, keeps caller compatibility)
  2.2. Add HG-D1 evidence evaluation
  2.3. Add HG-D3 rationale generation
  2.4. Add HG-D8 RECONSIDER routing

Phase 3: Decision Identity (PREREQUISITE)
  3.1. Check if _next_decision_id() exists in codebase
  3.2. Implement DC_YYYYMMDD_NNN generation
  3.3. Integrate with mocka_decision_write or governance_evaluate

Phase 4: Authorization Integration (EXISTING + CHANGE)
  4.1. Modify hg_gateway to detect RECONSIDER status
  4.2. Implement RECONSIDER → escalation routing (to Human Reconsideration)
  4.3. Keep existing authorization mocking (separate HG decision)

Phase 5: Institutional Record Mapping (MINIMAL)
  5.1. Document mocka_decision_write input requirements
  5.2. Define Runtime Decision → Institutional Record mapping (no code change)
  5.3. Confirm caller responsibility (who calls mocka_decision_write?)

Phase 6: Knowledge Conditional Trace (OPTIONAL, HG-D2)
  6.1. Add knowledge_retriever parameter to governance_evaluate()
  6.2. Implement "actually used" vs. "retrieved" detection
  6.3. Preserve knowledge_ids_used in runtime_decision (for STEP 11 prep)

Phase 7: Verification (TEST DESIGN ONLY)
  7.1. Design test scenarios (no test implementation)
  7.2. Document expected outputs per scenario
  7.3. Identify verification gaps for real HG review

Order Rationale:
- Phase 1: Unblock Phase 2 (Evidence needed for Decision)
- Phase 2: Core algorithm
- Phase 3: Identity generation (needed by Institutional Record)
- Phase 4: Routing (needed for HG-D8)
- Phase 5: Persistence (external, minimal change)
- Phase 6: Optional (HG-D2, non-blocking)
- Phase 7: Verification (design, not execution)
```

---

## 15. AUTHORIZATION BOUNDARIES

**Clear Separation of Decision Authorities:**

| Authority | Scope | Current | This Plan |
|-----------|-------|---------|-----------|
| DESIGN AUTHORIZED | STEP 15 Contract completion | ✓ HG-D1～D8 | ✓ Carry forward |
| IMPLEMENTATION PLAN AUTHORIZED | STEP 16 Plan (this document) | ✓ Planning only | ✓ In progress |
| CODE CHANGE AUTHORIZED | governance_evaluate() replacement | ✗ NOT YET | **Deferred** |
| RUNTIME ACTIVATION AUTHORIZED | main_loop integration | ✗ NOT YET | **Deferred** |
| PRODUCTION AUTHORIZED | Deploy to production | ✗ NOT YET | **NOT REQUESTED** |

**This STEP 16 Authorizes:**
- Design plan for real governance_evaluate()
- Evidence integration strategy
- Decision formation algorithm boundaries
- Failure handling approach
- Implementation order

**This STEP 16 DOES NOT Authorize:**
- Code changes to governance_client.py
- Code changes to hg_gateway.py
- Changes to decision_ledger.jsonl schema
- Changes to mocka_decision_write MCP tool
- Runtime activation of real Decision Engine
- Integration with production systems

**Next Authorization Gates:**
1. Code review of governance_evaluate() implementation (requires separate HG/reviewer decision)
2. Test execution & verification (requires test infrastructure authorization)
3. Runtime activation in main_loop (requires separate HG decision)
4. Production deployment (requires separate production authorization)

---

## 16. REMAINING EVIDENCE GAPS

| Gap | Impact | Resolution |
|-----|--------|-----------|
| **EvidenceLedger Interface** | How to query by step_id? | ACTION: Read EvidenceLedger.query() method signature |
| **confidence Field Usage** | Should evidence confidence affect decision? | NOT DECIDED: HG-D8 deferred weighting to implementation. Use as-is for now. |
| **"Actually Used" Definition** | When is knowledge "used" vs. "retrieved"? | ACTION: Define in Phase 6 (Knowledge trace) |
| **RECONSIDER Escalation Path** | Where does RECONSIDER go? Who processes? | ACTION: Confirm Human Reconsideration infrastructure exists |
| **mocka_decision_write Caller** | Who should call it? Runtime or external? | CURRENT: External (MCP). No change planned. |
| **Institutional Record Auto-Generation** | Should Runtime call mocka_decision_write automatically? | CURRENT: No. Will remain external. Caller responsibility TBD. |
| **DC_YYYYMMDD_NNN Concurrency** | If multiple governance_evaluate calls, sequence safe? | ACTION: Confirm if main_loop is single-threaded or concurrent |
| **Retry Strategy** | If sequence generation fails, what happens? | PLAN: Fail-closed (UNKNOWN decision, block execution) |

---

## IMPLEMENTATION SUMMARY

### Files to Modify (7 potential changes)

| File | Change Type | Scope | Priority |
|------|-------------|-------|----------|
| governance_client.py | Replace STUB | evaluate() function | P0 |
| hg_gateway.py | Add routing | RECONSIDER detection | P1 |
| decision_ledger.jsonl | Add records | (auto via mocka_decision_write) | P2 |
| (TBD) | Add sequence counter | DC_YYYYMMDD_NNN generation | P0 |
| (TBD) | Add escalation | RECONSIDER → Human queue | P1 |
| (TBD) | Document mapping | Runtime → Institutional contract | P2 |
| (TBD) | Verify interface | MemoryStore.query() integration | P2 |

### Key Implementation Points (5 Major Changes)

1. **governance_evaluate() Real Logic**
   - Input: plan + evidence_retriever + knowledge_retriever(opt)
   - Output: decision (PASS/RECONSIDER/UNKNOWN) + rationale + evidence_ids + knowledge_ids_used
   - Effect: Replaces hardcoded PASS; adds HG-D1, D3, D8 support

2. **Evidence Query Integration**
   - Depends: EvidenceLedger interface confirmation
   - Effect: Evidence retrieval in Decision formation

3. **Decision ID Generation (DC_YYYYMMDD_NNN)**
   - Depends: Sequence counter availability
   - Effect: Replaces UUID; enables traceability

4. **RECONSIDER Routing (HG-D8)**
   - Depends: Human Reconsideration infrastructure
   - Effect: Blocks execution; sends to Human for review

5. **Institutional Record Mapping**
   - Effect: Clarifies caller responsibilities; no auto-generation

### Verification Before Production

- Complete evidence → PASS
- Partial evidence → RECONSIDER → BLOCKED
- Evidence-based rationale (not stub)
- Decision ID uniqueness
- Decision ≠ Authorization separation
- Knowledge conditional tracing
- Fail-closed on all errors

