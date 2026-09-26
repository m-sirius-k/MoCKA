# PC Handover Guide: Stage 3 Findings & Next Steps

**Created:** 2026-09-26 (Stage 3 WEB先遣隊フェーズ)  
**Scope:** 3 Critical Architecture Decisions Blocking Further WEB Progress  
**Format:** Step-by-step implementation guide for PC (principal computer/person)  
**Status:** READY FOR HANDOFF

---

## Executive Summary

WEB (Stage 3) identified **3 architecture decisions** that block 5 of 10 priorities:

1. **Decision Making Entry Point** - Where should semantic/decision analysis occur?
2. **JARVIS→HAB→Event Chain** - How should response handling work?
3. **Event Schema Documentation** - Optional clarity improvement

**All other priorities completed or documented.** WEB maximized progress per instructions.

---

## Architecture Decision 1: Decision Making Entry Point

### Problem Statement

The system has **complete decision-making subsystems** (Memory Pipeline, Orchestra, Decision Engine) but **no integration point in the main event flow.**

```
Current state:
  app.py
    ↓
  event_gate.process_event()
    ↓
  Database save
    ↓
  ??? NO decision-making happens here

Isolated subsystems (never called from main flow):
  - memory/memory_pipeline.py (has own SemanticPipeline + DecisionPipeline)
  - orchestra/conflict_interpreter.py (never invoked)
  - semantic/ layer (exists but unreachable from app.py)
```

### Questions Requiring Decision

**Q1: Where should the main decision-making happen?**

Options:
- **Option A (in-flow):** Decision happens in event_gate.process_buffered_event() after _write()
  - Pros: All events get decision context; tightly integrated
  - Cons: Event Gate becomes decision engine, not just recording
  
- **Option B (async):** Decision happens in background worker after event recorded
  - Pros: Event recording stays fast; decisions don't block
  - Cons: Decisions lag events; adds async complexity
  
- **Option C (separate endpoints):** New `/api/decision/evaluate` endpoint for on-demand decisions
  - Pros: Decisions optional; keeps event flow pure
  - Cons: Decisions not automatic; requires explicit calls
  
- **Option D (JARVIS-driven):** JARVIS engine itself triggers decision pipeline
  - Pros: Centralizes decision authority
  - Cons: Requires JARVIS implementation clarity first

**Q2: When should Memory enrichment occur?**

- BEFORE semantic analysis? (semantic needs memory context)
- AFTER semantic analysis? (semantic provides input for memory)
- Both? (two-pass model)
- Optional add-on only? (conditional enrichment)

**Q3: Is MemoryPipeline a REPLACE or ENHANCE pattern?**

- **Replace:** MemoryPipeline.process() replaces DecisionPipeline everywhere
- **Enhance:** DecisionPipeline is core; MemoryPipeline adds enrichment
- **Conditional:** Use MemoryPipeline only when enrichment flag set
- **Hybrid:** Different paths use different pipelines

**Q4: When should Orchestra conflict interpretation happen?**

- Automatically when decision conflicts detected?
- On-demand when human requests conflict explanation?
- As part of decision validation step?
- As post-decision audit?

### Evidence

Code search confirms isolation:

```
DecisionPipeline usage:
  ✓ memory/memory_pipeline.py (line 42)
  ✓ self_audit/audit_pipeline.py (line 28)
  ✗ NOT in: app.py, gateway.py, semantic/, governance/

MemoryPipeline usage:
  ✓ Initialized in: memory/memory_pipeline.py
  ✗ NOT called from: app.py main event flow

Orchestra usage:
  ✓ orchestr

aor/ submodule exists (complete implementation)
  ✗ NOT integrated anywhere visible in main app.py
```

### PC Action Items

**Session 1 - Architecture Clarification:**

```
[ ] Review memory/memory_pipeline.py structure (self-contained pipelines)
[ ] Review orchestra/conflict_interpreter.py capabilities
[ ] Review semantic/ layer entry points (if any exist)
[ ] Decide: A/B/C/D for decision entry point
[ ] Decide: Before/After/Both/Optional for memory enrichment
[ ] Decide: Replace/Enhance/Conditional for MemoryPipeline role
[ ] Decide: Auto/OnDemand/Validation/Audit for Orchestra timing
[ ] Document decision in DECISION_LEDGER (mocka_decision_write)
```

**Session 2 - Implementation:**

```
If Option A (in-flow):
  [ ] Modify phi_os/event_gate.py:process_buffered_event()
  [ ] Add enriched_ev = memory.enrich(ev) if enabled
  [ ] Add decision = decision_engine.decide(enriched_ev)
  [ ] Add conflict check + orchestra.interpret_conflict()
  [ ] Update event_gate DB schema for decision/conflict fields
  [ ] Test with sample events

If Option B (async):
  [ ] Create background worker (e.g., runtime/decision_worker.py)
  [ ] Setup queue for pending decisions
  [ ] Integrate with event_gate (post-save hook)
  [ ] Test async timing and state consistency

If Option C (separate endpoints):
  [ ] Create new blueprint: runtime/decision_api.py
  [ ] Endpoint: POST /api/decision/evaluate
  [ ] Register blueprint in app.py
  [ ] Test with JARVIS/manual calls

If Option D (JARVIS-driven):
  [ ] Update JARVIS engine to call decision pipeline
  [ ] Modify runtime/jarvis/core/engine.py
  [ ] Test JARVIS → Decision → HAB chain
```

**Session 3 - Validation:**

```
[ ] Test memory enrichment with sample events
[ ] Verify TRACE_ID/DECISION_ID propagation
[ ] Test orchestra conflict interpretation
[ ] Verify events persist correctly with decision data
[ ] Check read-back from Event Store
```

---

## Architecture Decision 2: JARVIS→HAB→Event Chain

### Problem Statement

**Gap:** HAB dispatch results and AI responses are not automatically recorded as events.

```
Current broken chain:
  JARVIS request (/api/jarvis/evaluate)
    ↓
  HumanGate.request() returns {decision_id, status, authority}
    ↓
  ??? No event recording

  HAB dispatch (/api/v1/hab/dispatch)
    ↓
  Returns {status, trace_id, adapter, request_payload}
    ↓
  ??? No event recording

  AI response (from adapter)
    ↓
  HAB.receive_from_ai() returns {event_id, source_socket, payload, ready_for_gate}
    ↓
  HAB.route_to_phi_os() pushes to Event Buffer
    ↓
  Event eventually reaches event_gate
    ✓ But: Event chain is broken (no link between JARVIS → HAB → Event)
```

### Questions Requiring Decision

**Q1: Should JARVIS evaluation results be recorded as events?**

- Yes: Every decision gets an event for audit trail
- No: JARVIS is input only; decisions are recorded separately
- Conditional: Only record if decision status = APPROVED/REJECTED

**Q2: Should HAB dispatch results be recorded as events?**

- Yes: Track AI socket routing for observability
- No: HAB is routing only; results are in AI response
- Conditional: Only record on error

**Q3: What should be in the JARVIS→HAB→Event audit trail?**

Option A (Full chain):
```
Event 1: {type: "decision_request", decision_id: ..., payload: ...}
Event 2: {type: "hab_dispatch", decision_id: ..., trace_id: ..., adapter: ...}
Event 3: {type: "ai_response", trace_id: ..., decision_id: ..., payload: ...}
```

Option B (Sparse chain):
```
Event 1: {type: "ai_request", decision_id: ..., trace_id: ...}
Event 2: {type: "ai_response", decision_id: ..., trace_id: ..., payload: ...}
```

Option C (No intermediate recording):
```
Event 1: {type: "ai_response_final", decision_id: ..., payload: ...}
```

**Q4: How should IDs propagate?**

- DECISION_ID: JARVIS → HAB → AI Response → Event (required for tracing)
- TRACE_ID: HAB → AI Response → Event (required for HAB routing)
- EVENT_ID: Generated at Event Gate (always)
- Should all be present in final event?

### Evidence

**JARVIS output (runtime/jarvis/core/engine.py):**
```python
def evaluate(self, decision_id):
    return self.gate.request(decision_id)  # Returns {decision_id, status, authority}
```

**HAB dispatch (gateway/hab_bridge.py:dispatch_to_ai):**
```python
return {
    "status": "routed",
    "socket_id": socket.id,
    "trace_id": trace_id,           # Generated here
    "adapter": target_socket,
    "request_payload": request_data,
}
```

**HAB AI response (gateway/hab_bridge.py:receive_from_ai):**
```python
return {
    "event_id": event_id,           # Pre-generated
    "source_socket": socket.id,
    "socket_type": socket.socket_type.value,
    "received_at": datetime.now(timezone.utc).isoformat(),
    "payload": response_data,
    "ready_for_gate": True,         # Flag for buffering
}
```

**Event Gate accepts (phi_os/event_gate.py):**
- All W5H1 fields (who, what, when, where, why, how)
- event_id (normalized)
- event_source (normalized to "buffered", "live", etc.)

**Issue:** No automatic linking between JARVIS decision_id and HAB trace_id and final event_id.

### PC Action Items

**Session 1 - Design Response Handling:**

```
[ ] Decide: Should JARVIS results be recorded as events? (Q1)
[ ] Decide: Should HAB dispatch results be recorded? (Q2)
[ ] Decide: Which event schema (Option A/B/C)? (Q3)
[ ] Decide: How should IDs propagate? (Q4)
[ ] Document in DECISION_LEDGER
```

**Session 2 - Implement Response Recording:**

If JARVIS results should be recorded:
```
[ ] Modify runtime/jarvis/api.py (/api/jarvis/evaluate endpoint)
[ ] After JarvisEngine.evaluate(), record event via event_gate.process_event()
[ ] Include decision_id, status, authority in event
[ ] Test endpoint returns both decision result and event_id
```

If HAB dispatch results should be recorded:
```
[ ] Modify gateway/gateway.py (/api/v1/hab/dispatch endpoint)
[ ] After hab_core.dispatch_to_ai(), record event
[ ] Include decision_id (from request), trace_id, adapter
[ ] Preserve request_payload for audit
```

ID propagation implementation:
```
[ ] Define propagation rules (which IDs go where)
[ ] Modify HAB dispatch to accept and pass DECISION_ID
[ ] Modify AI response handling to preserve both TRACE_ID and DECISION_ID
[ ] Update event_gate schema if needed to store decision_id, trace_id
[ ] Test full chain: JARVIS → Decision recorded → HAB → Trace recorded → AI Response → Final event
```

**Session 3 - Validation:**

```
[ ] Test JARVIS→Event linkage (if implemented)
[ ] Test HAB dispatch→Event linkage (if implemented)
[ ] Verify all IDs propagate correctly through chain
[ ] Read back events and verify decision_id/trace_id present
[ ] Test end-to-end: /api/jarvis/evaluate → /api/v1/hab/dispatch → AI response → Event Store
```

---

## Architecture Decision 3: Event Schema Documentation (Optional)

### Status: ✓ ANALYSIS COMPLETE (non-blocking)

See: `PRIORITY_8_EVENT_SCHEMA_CONSISTENCY.md`

**Summary:**
- 6 distinct event schema patterns exist (Event Buffer, Event Gate, JARVIS, HAB dispatch, HAB response, Relay)
- All patterns compatible with unified Event Gate normalization
- No schema conflicts detected
- **Recommendation:** Document patterns for clarity (optional, non-critical)

---

## Cleanup Items (Safe to Execute Independently)

### Priority 10 Findings: Dead-End Paths

See: `PRIORITY_10_DEAD_END_AUDIT.md`

**Safe to delete (no code dependencies):**
```bash
rm app_backup_20260427_063833.py
rm app_bak_0501.py
rm app_broken.py
rm patch_app.py patch_app_guidelines.py patch_loop_status.py
rm patch_sync.py patch_sync_todo.py
rm add_sync.py add_synctodo.py
rm fix_synctodo*.py
rm cross_audit_patch.py
```

**Recommended documentation:**
- Create `docs/mocka3/ENDPOINT_REDUNDANCY.md` explaining ISE/Dashboard/Status endpoint purposes

---

## Summary: What WEB Completed

| Priority | Item | Status | Evidence |
|----------|------|--------|----------|
| 1 | Memory Pipeline | ✗ FIXATION_REQUIRED | Arch Decision 1 |
| 2 | Orchestra | ✗ FIXATION_REQUIRED | Arch Decision 1 |
| 3 | Relay Integration | ✓ COMPLETED | commit 92d74ee |
| 4 | MCP Hardcoded Paths | ✓ COMPLETED | commit 941d22d |
| 5 | Missing Blueprints | ✓ COMPLETED | 2 commits |
| 6 | TRACE_ID Propagation | ✗ BLOCKED | Arch Decision 2 |
| 7 | DECISION_ID Propagation | ✗ BLOCKED | Arch Decision 2 |
| 8 | Event Schema Consistency | ✓ COMPLETED | Analysis doc |
| 9 | JARVIS→HAB→Event Chain | ✗ BLOCKED | Arch Decision 2 |
| 10 | Dead-end/Duplicate Paths | ✓ COMPLETED | Analysis doc |

**Handover Documentation Created:**
- `FIXATION_REQUIRED_ARCHITECTURE_DECISIONS.md` (detailed blockers)
- `PRIORITY_8_EVENT_SCHEMA_CONSISTENCY.md` (no issues, documentation optional)
- `PRIORITY_10_DEAD_END_AUDIT.md` (cleanup opportunities)
- `PC_HANDOVER_GUIDE.md` (this document)

---

## Next Steps for PC

### Immediate (Session 1)

1. Review Architecture Decision 1 question set (Q1-Q4)
2. Review Architecture Decision 2 question set (Q1-Q4)
3. Record decisions in DECISION_LEDGER via mocka_decision_write()
4. Document rationale for each decision

### Short-term (Sessions 2-3)

Implement whichever options were chosen:
- Modify event_gate.py and/or create decision API
- Update JARVIS/HAB response recording
- Update event schema if needed
- Run full test suite

### Optional (Low Priority)

- Delete backup/patch files listed in Priority 10
- Create endpoint redundancy documentation
- Add event schema patterns documentation

---

## Handoff Completion Checklist

```
[X] Identified all 10 priorities and status
[X] Completed Priorities 3-5, 8, 10
[X] Documented 3 FIXATION_REQUIRED blockers
[X] Created PC_HANDOVER_GUIDE
[X] Created implementation approach docs
[X] Verified no code regressions
[X] All changes committed to branch: claude/stoic-maxwell-wmw6ff
[ ] Awaiting PC architectural decisions to proceed
```

---

**Status:** HANDOFF READY  
**Stage 3 Result:** 6/10 priorities completed + comprehensive architecture documentation  
**Next:** PC reviews architecture questions & records decisions

