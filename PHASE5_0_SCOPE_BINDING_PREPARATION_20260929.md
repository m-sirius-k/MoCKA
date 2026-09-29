# PHASE 5.0 SCOPE BINDING PREPARATION
## Post-HG Decision Phase

**Date:** 2026-09-29  
**HG Decisions:** A-1, B-1, C-1 (All APPROVED)  
**Phase:** SCOPE BINDING REQUIRED (before Implementation)  
**Status:** Preparation / No code changes yet

---

## Overview

HG has approved all 3 connections:
- **A-1:** Implement Orchestra → HAB integration
- **B-1:** Store Orchestra-specific Lineage formally in Event Store
- **C-1:** Implement PHI-OS → Memory auto-sync connection

Before implementation, each decision must be scoped precisely.

---

## DC_20260929_005: Orchestra → HAB Integration

### Current State
```
Authorization
    ↓
Orchestra
    ├─ Existing: Browser/UI pathway (Playwright)
    │   OrchestraSocket → orchestra_one_host.py → Playwright → AI Web UI
    └─ NEW REQUIRED: HAB pathway
        Oracle → HAB → AI
```

### Scope Questions to Resolve
1. **Existing Browser transport handling:**
   - Keep as fallback?
   - Deprecate?
   - Maintain dual pathways?

2. **Provider routing:**
   - Which providers go through HAB?
   - Which remain direct to Browser/UI?

3. **Authorization scope:**
   - Does HAB layer inherit Orchestra authorization?
   - New authorization model needed?

4. **Frozen baseline compatibility:**
   - Current Architecture allows HAB integration?
   - Changes to existing Orchestra contracts needed?

### Scope Binding Tasks
- [ ] Confirm HAB interface contract
- [ ] Define provider routing rules
- [ ] Confirm authorization delegation
- [ ] Check Architecture Frozen Baseline for conflicts

---

## DC_20260929_007: AI → Event Store Lineage

### Current State
```
Generic Event Store pathway exists:
  AI output → event_gate.py → events table (mocka_events.db)
  
But: Orchestra-specific metadata NOT formally captured:
  - provider (gpt / claude / gemini)
  - model (gpt-4 / claude-3-sonnet / etc)
  - runtime (deployed version)
  - source (live / test / cached)
```

### Scope Questions to Resolve
1. **Required evidence fields:**
   - Which of {provider, model, runtime, source, who_actor, request_id} are MANDATORY?
   - Which are OPTIONAL?

2. **Storage location:**
   - events table existing columns sufficient?
   - Need new columns?
   - JSON metadata field?

3. **Validation:**
   - Who validates lineage completeness?
   - What happens if incomplete?

4. **Schema versioning:**
   - Does Event Store schema need versioning?
   - Backward compatibility requirements?

### Scope Binding Tasks
- [ ] Confirm mandatory lineage fields
- [ ] Define Event Store schema changes (if needed)
- [ ] Confirm validation rules
- [ ] Check compatibility with existing events

---

## DC_20260929_009: PHI-OS → Memory Integration

### Current State
```
Separate systems:
  Event Store (mocka_events.db)
    ↓
    ↓ [UNCONNECTED]
    ↓
  Memory Store (memory/data/memory_store.json)

No formal binding:
  event_id (E20260929_...)
  memory_id (M_episodic_000001)
  [NO LINK]
```

### Scope Questions to Resolve
1. **Connection model:**
   - Push (Event Gate triggers MemoryWriter)?
   - Pull (Memory polls Event Store)?
   - Async queue?

2. **ID binding:**
   - Store event_id in memory_id metadata?
   - Create separate junction table?
   - Reverse reference (memory_id in events)?

3. **Event filtering:**
   - All events → Memory?
   - Only certain event types?
   - Governance events only?

4. **Synchronization:**
   - Real-time sync?
   - Batch processing?
   - Retry/compensation logic?

### Scope Binding Tasks
- [ ] Confirm connection model (push/pull/queue)
- [ ] Define event_id ↔ memory_id binding mechanism
- [ ] Confirm event filtering rules
- [ ] Define sync timing and retry policy

---

## Governance

```
STATUS = SCOPE BINDING PHASE

All 3 decisions APPROVED / ready for scoping
No code changes allowed until scope is finalized
No runtime implementation until scope binding complete

Next checkpoint: Scope Binding Completion
Then: Implementation Plan → Implementation → Runtime Evidence
```

---

## Timeline

1. **Current:** Scope Binding Preparation (this document)
2. **Next:** Scope Binding Completion (define answers above)
3. **Then:** Implementation Plan per decision
4. **Then:** Implementation → Runtime Evidence → Readback
5. **Final:** Institutional Memory recording

---

## Restrictions (until Scope Binding Complete)

```
CODE_CHANGE       = NO
COMMIT            = NO
PRODUCTION        = NO
SCOPE_CHANGE      = NO
RUNTIME_TEST      = NO
IMPLEMENTATION    = NO
```

All work is design/documentation only.
