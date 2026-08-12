# TODO_445 Investigation Evidence Package - Final v1.0

**Date:** 2026-08-12  
**Investigation Phase:** COMPLETE  
**Correction Phase:** HOLD (Human Gate pending)  
**Reference:** IC_20260712_001, DC_20260712_003

---

## Summary

TODO_445 investigation of TODO配置ドリフト (configuration placement drift) has been completed. Five (5) distinct root causes have been identified through file-level analysis of MOCKA_TODO_ACTIVE.json, ARCHIVE, and REFERENCE_LOCKED layers.

**Status:** Investigation findings preserved for Human Gate decision on corrective actions.  
**Constraint:** No correction implementation per directive - evidence package only.

---

## Investigation Scope

| Item | Scope |
|------|-------|
| IC Reference | IC_20260712_001(要約層のTODO集計非同期) |
| Files Analyzed | MOCKA_TODO_ACTIVE.json (primary) / ARCHIVE.json / REFERENCE_LOCKED.json |
| Evidence Basis | Direct file-level analysis (not speculation) |
| Time Range | 2026-06-28 to 2026-07-12 |

---

## Finding #1: Canonical Path Specification Error

**Severity:** HIGH  
**Type:** Configuration Management  
**Verified Evidence:** meta.storage.primary mis-points to outdated file

### Observation

```json
{
  "meta": {
    "storage": {
      "primary": "C:/Users/sirok/MOCKA_OVERVIEW.json",
      "backup": "A:/MOCKA_OVERVIEW.json"
    }
  }
}
```

- `primary` field incorrectly specifies path to older duplicate copy (last updated 2026-06-30)
- Actual canonical file location: `C:/Users/sirok/MoCKA/data/MOCKA_TODO_ACTIVE.json`
- Root-directory copy is 6/30 stale and no longer maintained

### Root Cause

Single Root Rule (governance principle) was violated:  
Primary storage path points to deprecated location. This violates the "one source of truth" principle and creates two competing locations with different update timestamps.

### Required Correction

Update `meta.storage.primary` to point to actual canonical location:
```json
"primary": "C:/Users/sirok/MoCKA/data/MOCKA_TODO_ACTIVE.json"
```

**Human Gate Decision Required:** Yes

---

## Finding #2: Missing Flush Mechanism - completed[] to ARCHIVE

**Severity:** HIGH  
**Type:** Data Pipeline  
**Verified Evidence:** No flush implementation in codebase

### Observation

- ARCHIVE.json has NOT been updated since 2026-06-28
- completed[] array exists in ACTIVE layer but contains 55+ items
- No automated or manual flush mechanism exists to move completed items from completed[] into ARCHIVE.json
- Rule in meta says: "完了/廃止TODOはARCHIVE層へ配置する" but implementation is incomplete

### Root Cause

`completed[]` → `ARCHIVE.json` flush mechanism was never implemented in mocka_mcp_server.py or related infrastructure. The conceptual rule exists but the mechanical pathway does not.

### Evidence Trail

- ARCHIVE.json timestamp: 2026-06-28T...
- Last completed[] write: 2026-07-12 (indirect observation via completed array contents)
- Implementation check: grep -n "def.*flush\|ARCHIVE" mocka_mcp_server.py returns no results for automatic flushing

### Required Correction

Implement flush mechanism in mocka_mcp_server.py:
1. Define trigger (periodic, threshold, manual)
2. Implement completed[] → ARCHIVE transfer
3. Verify completed[] count → ARCHIVE count equation (conservation property)

**Human Gate Decision Required:** Yes

---

## Finding #3: mocka_add_todo Incomplete Routing

**Severity:** MEDIUM  
**Type:** Logic Defect  
**Verified Evidence:** 16 completed items remain in todos[] instead of completed[]

### Observation

- 16 TODO items show `status="完了"` but remain in todos[] array
- These items should have been routed to completed[] upon creation or update
- Root cause: mocka_add_todo() does NOT implement the completion routing logic

### Root Cause

When mocka_add_todo() creates or updates TODOs, it does not check if `status="完了"` and route them to completed[]. The old update_todo.py had this logic (lines 74-86), but mocka_add_todo() was never updated to inherit this behavior.

### Evidence Trail

- Diff: Old update_todo.py lines 74-86 (completion routing logic)
- Current: mocka_add_todo() in mocka_mcp_server.py (no equivalent logic found)
- Affected items: todo_ids internal lookup at query time confirms 16 items with status=完了 in todos[] array

### Required Correction

Port completion routing logic from old update_todo.py into mocka_add_todo():
```python
if status == "完了":
    todos.remove(item)
    completed.append(item)
```

**Human Gate Decision Required:** Yes

---

## Finding #4: Non-API Route Entry - TODO_414 Anomaly

**Severity:** HIGH  
**Type:** Governance Violation  
**Verified Evidence:** TODO_414 present in completed[] without API routing

### Observation

- TODO_414 shows status="未着手" but exists in completed[] array
- This violates the invariant: completed[] should contain only items with status="完了"
- No mocka_update_todo() API call for TODO_414 is found in events.db during 2026-07-09 to 2026-07-12 window

### Root Cause

Non-API direct modification of completed[] array. TODO_414 was added by some process outside the MCP API layer, bypassing governance checks.

### Evidence Trail

- completed[] contents (observation)
- events.db mocka_update_todo records (searched for TODO_414 - no hits during suspected window)
- actor field in related events (integrity_warnings list flag shows detection on 2026-07-12)

### Related Issues

- TODO_448: Addresses adding who_actor/session_id logging to detect future non-API writes
- Governance violation fits pattern IC_20260712_002

### Required Correction

1. Immediate: Identify writing process/actor for TODO_414
2. Long-term: Implement per-TODO write-tracking per TODO_448
3. Governance: Clarify whether direct completed[] mutation is ever allowed (assumed: NO)

**Human Gate Decision Required:** Yes

---

## Finding #5: Schema-Rule Contradiction - completed[] location

**Severity:** MEDIUM  
**Type:** Design Inconsistency  
**Verified Evidence:** Rule and implementation do not align

### Observation

- Schema (MOCKA_TODO_ACTIVE.json structure): completed[] is defined as a top-level array within ACTIVE layer
- Rule (meta.rule_廃止_placement): "完了/廃止TODOはARCHIVE層(MOCKA_TODO_ARCHIVE.json)に配置する"
- Actual behavior: completed[] stays in ACTIVE indefinitely (no flush)

### Root Cause

Design mismatch between:
- **Conceptual model** (rule states: ARCHIVE is destination)
- **Physical schema** (structure defines: completed[] lives in ACTIVE)
- **Implementation** (behavior: no flush ever occurs)

### Evidence Trail

- Line 13-14 in MOCKA_TODO_ACTIVE.json meta section: "ACTIVE層のみ。LOCKED/ARCHIVE層は対象外"
- But completed[] is inside ACTIVE according to actual structure
- Rule says items should move to ARCHIVE
- No pathway exists to move them

### Required Correction

Align one of the three (rule / schema / implementation). Options:
- **(A)** Change rule: completed[] stays in ACTIVE, ARCHIVE layer drops
- **(B)** Change schema: remove completed[] from ACTIVE, define in ARCHIVE
- **(C)** Implement: Add completed[] → ARCHIVE flush (Current status: NOT DONE)

**Human Gate Decision Required:** Yes (design decision among A/B/C)

---

## Impact Assessment

| Category | Impact |
|----------|--------|
| Data Integrity | **HIGH** - completed[] content not guaranteed to reflect canonical truth |
| Observability | **HIGH** - metadata points to wrong location, causing confusion in downstream systems |
| Governance | **HIGH** - non-API writes bypass audit trail |
| Consistency | **MEDIUM** - rule/schema/implementation misalignment creates latent drift |

---

## Evidence Preservation

All findings are based on:
1. Direct file observation (hash/timestamp verification possible)
2. Event log trace (mocka_mcp_server.py calls can be cross-referenced)
3. Structural analysis (schema coherence checks)

**Reproducibility:** Findings can be independently verified by:
- File system inspection: C:/Users/sirok/MoCKA/data/MOCKA_TODO_ACTIVE.json
- Event log query: events.db with time-range filter on 2026-07-12 ±2 hours
- Code inspection: mocka_mcp_server.py for flush implementation status

---

## Next Steps (Human Gate Decision Required)

**NOT TO BE IMPLEMENTED IN THIS SESSION**  
**AWAITING Human Gate Approval**

1. **Decide on Finding #5 design option** (A/B/C)
2. **Approve correction scope** (which findings require correction)
3. **Schedule correction implementation** (after Human Gate)
4. **Define rollback strategy** (if correction causes regression)

---

## Classification

- **Investigation Status:** COMPLETE
- **Correction Status:** HOLD (Human Gate pending)
- **Evidence Status:** PRESERVED
- **Risk Level:** MEDIUM (findings do not block current operations, but indicate governance drift)

**Session:** E20260812_597681145589a  
**Preserving Record:** 2026-08-12T20:03:18Z  
**Next Review:** Human Gate decision point
