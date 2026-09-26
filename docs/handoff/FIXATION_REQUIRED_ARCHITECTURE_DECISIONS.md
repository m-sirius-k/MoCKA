# FIXATION_REQUIRED: Architecture Decisions Blocking Further WEB Progress

**Date:** 2026-09-26  
**Session:** Stage 3 - WEB先遣隊フェーズ  
**Status:** WEB work BLOCKED on architecture clarification

---

## Issue 1: Decision Making Entry Point (Blocks Memory & Orchestra)

### Context

**Current State:** 
- Memory Pipeline exists as self-contained system with its own semantic/decision pipeline (memory/memory_pipeline.py)
- Orchestra exists as conflict interpreter (orchestra/conflict_interpreter.py)
- Both are isolated from main event flow (app.py → event_gate → database)

**Finding:**
- DecisionPipeline only used in:
  - memory/memory_pipeline.py (internal to memory)
  - self_audit/audit_pipeline.py (audit only)
- **NOT found in:** app.py, gateway.py, semantic/, governance/
- Main event loop has NO decision making path

**Questions Requiring PC Answer:**

1. **Where is "main decision making" supposed to happen?**
   - In semantic layer (currently isolated)?
   - In governance layer (governance/*.py)?
   - In JARVIS engine (runtime/jarvis/core/engine.py)?
   - In application logic handlers themselves (reflection_engine, etc.)?

2. **When should Memory enrichment occur?**
   - BEFORE semantic analysis? (semantic needs memory context)
   - AFTER semantic analysis? (semantic provides input for memory recording)
   - Both? (two-pass model)
   - As optional add-on only?

3. **Is MemoryPipeline meant to REPLACE or ENHANCE DecisionPipeline?**
   - Replace: Use MemoryPipeline.process() everywhere instead of DecisionPipeline
   - Enhance: DecisionPipeline is core, MemoryPipeline adds enrichment
   - Conditional: Use MemoryPipeline only when enrichment requested
   - Unknown: Needs clarification

4. **When should Orchestra conflict interpretation happen?**
   - Automatically when decision conflicts detected?
   - On-demand when human requests conflict explanation?
   - As part of decision validation?
   - As post-decision audit?

### Evidence

File analysis shows:
```
app.py event flow:
  Event input
    ↓
  [endpoint handler] - NO decision logic found here
    ↓
  event_buffer.push()
    ↓
  event_gate.process_buffered_event()
    ↓
  Database save
    ↓
  relay.ingest() [just added in commit 92d74ee]
    ↓
  ??? No further processing
```

Isolated systems:
- memory/ subsystem: complete but never called
- orchestra/ subsystem: complete but never called
- semantic/ subsystem: complete but only in memory pipeline
- decision/ subsystem: complete but only in memory pipeline

### PC Handoff Actions Needed

```
[ ] Review decision making architecture
    - Where should semantic/decision analysis happen?
    - Should it be per-event or post-event?
    - Is it synchronous or async?
    
[ ] Clarify Memory role
    - Should ALL events go through memory enrichment?
    - Only governance decisions? Only AI operations? All?
    - Is memory optional or mandatory?
    
[ ] Clarify Orchestra role
    - When/where is "conflict detection" implemented?
    - Is Orchestra pre-decision or post-decision?
    
[ ] Decide integration pattern
    - Inject decision making into event_gate flow?
    - Keep isolated and add explicit decision endpoints?
    - Other architecture?
    
[ ] Document "main decision path" in:
    - MOCKA_ARCHITECTURE_CURRENT.md or similar
    - Decision flow diagram
```

### PC Execution Approach

Once architecture decided:

**Option A (if decision should be in event_gate):**
```python
# In phi_os/event_gate.py.process_buffered_event():
# After _write(ev, conn=conn), before return:
enriched_ev = memory.enrich(ev)  # If needed
decision = decision_engine.decide(enriched_ev)
if decision.has_conflict:
    explanation = orchestra.interpret_conflict(decision)
    ev['decision'] = decision.to_dict()
    ev['conflict_interpretation'] = explanation.to_dict()
```

**Option B (if decision should be separate endpoints):**
```python
# Add new endpoints in app.py:
@app.route("/api/decision/evaluate", methods=["POST"])
def evaluate_decision():
    # Accept event or request, invoke semantic/memory/decision
    # Return decision result
```

**Option C (if decision is in semantic/decision layer):**
```python
# Integrate semantic layer call points
# Update event_gate to call decision if provided
# Define async worker for post-event decisions
```

---

## Issue 2: JARVIS → HAB → PHI-OS → Event Store Chain Gaps

### Context

**Current State:**
- JARVIS Engine: Created, has endpoints (commit c2401c4)
- HAB Bridge: Integrated with gateway.py (commit 3d79101)
- Event recording: Works via event_gate
- But: Chain doesn't close

**Finding:**

```
JARVIS (/api/jarvis/evaluate)
  ↓
  → HumanGate.request() [from runtime/jarvis/gate/]
  ↓
  ??? Returns status only, no event generated

HAB (/api/v1/hab/dispatch)
  ↓
  → AISocket routing
  ↓
  ??? No response handling, no event on completion

Expected chain:
  JARVIS request
  → Decision evaluation
  → HAB dispatch to AI
  → AI response
  → Event recording (to Event Store)
  → Event read-back verification
```

**Questions Requiring PC Answer:**

1. **Does JARVIS → HAB need explicit response handling?**
   - Should HAB dispatch results be captured?
   - Should AI responses trigger events?

2. **What should trigger event recording in this chain?**
   - Only final decision?
   - Each step (JARVIS call, HAB dispatch, AI response)?
   - Only on error?

3. **What IDs should propagate through chain?**
   - TRACE_ID (currently in HAB)?
   - DECISION_ID (from JARVIS)?
   - Correlation ID?

### Evidence

Files examined:
- runtime/jarvis/core/engine.py - returns only `{decision_id, status, authority}`
- gateway/hab_bridge.py - returns `{status, trace_id, adapter, request_payload}`
- gateway/gateway.py - HAB dispatch endpoint doesn't record event

### PC Handoff Actions Needed

```
[ ] Define JARVIS→HAB→Event chain
    - What events should be recorded?
    - At what points?
    - With what data?
    
[ ] Implement response handling
    - Capture HAB dispatch results
    - Convert to events
    - Ensure idempotency
    
[ ] Verify ID propagation
    - TRACE_ID through chain
    - DECISION_ID through chain
    - Event correlation
    
[ ] Test read-back
    - All events persist
    - IDs are intact
    - Data is complete
```

---

## Issue 3: Event Schema Consistency

### Context

**Finding:** Multiple event schema patterns in use:
- event_buffer events (with idempotency_key, event_source)
- HAB dispatch result (trace_id, socket_id, adapter)
- JARVIS result (decision_id, status, authority)
- Relay events (state, policy, action)

**Questions:**

1. **Is there a canonical event schema?**
2. **How should different event types coexist?**
3. **What fields are mandatory vs. optional?**

### PC Handoff

```
[ ] Review docs/mocka3/EVENT_SCHEMA_v*.md or create if missing
[ ] Verify all event sources conform to schema
[ ] Update event_gate validation if needed
```

---

## Summary: What WEB Can Continue, What Needs PC

### ✓ WEB Can Continue (no architecture decision needed)

- Priority 6: TRACE_ID propagation (can test with existing HAB/Relay)
- Priority 8: Event schema validation (can analyze without decision changes)
- Priority 10: Dead-end path audit (code inspection only)
- Documentation improvements
- Code cleanup and testing

### ✗ WEB BLOCKED (needs architecture decision)

- Priority 1: Memory Pipeline integration
- Priority 2: Orchestra integration
- Priority 7: DECISION_ID propagation (depends on decision point)
- Priority 9: Completing JARVIS→HAB→Event chain

### ⚠️ CONDITIONAL (depends on architecture answer)

- MCP tool availability (works if imports resolve, may need decision pipeline for some tools)
- Human Gate integration (works as registry, but decision flow unclear)

---

## Recommended PC Action Plan

**Immediate (Session 1):**
1. Review and clarify decision making architecture
2. Define when/where Memory & Orchestra should be invoked
3. Sketch JARVIS→HAB→Event chain with event payloads
4. Document canonical event schema

**Session 2:**
1. Implement decision pipeline integration (if in-flow)
2. Or add decision endpoints (if separate)
3. Update event_gate accordingly
4. Test with actual semantic/memory/orchestra calls

**Session 3:**
1. Implement JARVIS→HAB→Event chain handling
2. Add response capture and event recording
3. Verify ID propagation
4. Test read-back from Event Store

---

## Files Ready for PC Transition

- WEB_STAGE3_IMPLEMENTATION_REPORT.md (progress log)
- STAGE_2_CONNECTION_MATRIX.md (initial audit)
- STAGE_2_COMPREHENSIVE_BROKEN_CONNECTIONS.md (20+ issues found)
- Commits: 92d74ee (Relay), 941d22d (MCP paths), and prior

---

**Next Session:** Awaiting architecture clarification before continuing Priority 1-2, 7, 9

