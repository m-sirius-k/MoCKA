# PHASE 5.0 IMPLEMENTATION AUTHORIZATION

**Date:** 2026-09-29  
**Authority:** Human Gate (HG)  
**Status:** IMPLEMENTATION AUTHORIZED

---

## FIXED CONDITIONS (IMMUTABLE)

```
HG FINAL PLAN APPROVAL = RECORDED
IMPLEMENTATION AUTH     = GRANTED

IP-007 = APPROVED
IP-005 = APPROVED
IP-009 = APPROVED

PRODUCTION              = NOT AUTHORIZED
SCOPE EXPANSION         = NOT AUTHORIZED
NEW AUTHORITY           = NOT AUTHORIZED
```

---

## IMPLEMENTATION SEQUENCE (RECOMMENDED)

### STEP 1: IP-007 (Orchestra-specific Lineage)
**Target:** Store Orchestra AI lineage (vendor/model/runtime/source)

**Scope:**
- Orchestra Session Completion Hook
- Extract lineage metadata
- Call event_gate.process_event() with vendor/model/runtime/source
- Event Store persistence
- Static readback validation

**Critical Check Point:**
- ✓ No new `lineage_recorder.py` creation
- ✓ No schema migration (vendor/model/runtime/source already exist)
- ✓ Reuse existing event_gate interface only

**Readback:** Confirm lineage record in events table with all 4 fields populated

---

### STEP 2: IP-005 (Orchestra → HAB Authorization)
**Target:** Authorization check before Orchestra execution

**Scope:**
- Orchestra request → authorization.py
- Query runtime_scope (HG-approved, immutable)
- Generate APPROVED/REJECTED/DEFERRED decision
- Log to Event Store
- Return decision to Orchestra
- Static readback validation

**Critical Check Point:**
- ✓ `authorization.py` is NOT a new Authority engine
- ✓ Existing HAB authority structure REUSED
- ✓ runtime_scope is SINGLE SOURCE OF TRUTH (not cached, not re-authorized)
- ✓ Fail-closed: any error = REJECTED

**Readback:** Confirm authorization event with approval_status and authority fields

---

### STEP 3: IP-009 (PHI-OS → Memory Auto-Sync)
**Target:** Automatic sync from Event Store to Memory Layer

**Scope:**
- Post-commit hook after event_gate.process_event()
- Check event_id in event_memory_map.jsonl
- If NOT already synced → call memory_writer.write_event()
- Update event_memory_map (append-only)
- Track sync_status: synced/pending/failed
- Retry logic: max 3 attempts
- Static readback validation

**Critical Check Point:**
- ✓ `event_id` idempotency ENFORCED
- ✓ IF event_id already in map → SKIP MemoryWriter (no duplicate)
- ✓ Restart safety: mapping file persists across reboots
- ✓ event_memory_map.jsonl is append-only (no delete)

**Readback:** Confirm 1:1 event_id ↔ memory_id mapping, no duplicates, all synced events in Memory

---

## SCOPE LOCK

**What IS Authorized:**
- Implement exactly per approved plans (IP-007, IP-005, IP-009)
- Minimal code changes per plan
- Reuse existing interfaces
- Add readback validation
- Record runtime evidence

**What is NOT Authorized:**
- Any changes outside 3 approved plans
- Production activation
- Scope expansion
- New Authorization/Policy engine creation
- Bidirectional sync (Event Store ← Memory)
- Volatile-memory based idempotency caching

---

## EXECUTION PROTOCOL

1. **Load Plan:** Read approved PHASE5_0_IMPLEMENTATION_PLAN_XXX.md
2. **Verify Scope:** No changes except what plan specifies
3. **Implement:** Minimal code per plan
4. **Readback:** Verify via static queries/assertions
5. **Record Evidence:** Document runtime behavior
6. **Next Plan:** Do not start until previous plan readback passes

---

## TRANSITION TO IMPLEMENTATION AGENT

**To Implementation Team:**

Execute in this order:
1. IP-007: Lineage → Event Store (FIRST)
2. IP-005: Authorization (PARALLEL or SECOND)
3. IP-009: Memory Sync (THIRD)

**Remember:**
- Approved plans are FIXED
- No scope expansion
- No new engines/authorities
- Idempotency enforced (IP-009)
- Each step requires readback before next

**Status:** Ready to hand off to implementation agent

---

**Approval:** HG AUTHORIZED  
**Scope Binding:** SB-005, SB-007, SB-009  
**Implementation:** BEGIN with IP-007
