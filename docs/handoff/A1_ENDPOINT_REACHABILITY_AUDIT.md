# A1: Endpoint Reachability Audit

**Date:** 2026-09-26  
**Phase:** Stage 3 Phase 3a (Connectivity)  
**Status:** ANALYSIS COMPLETE - 1 CRITICAL FINDING

---

## Summary

**Total Endpoints Analyzed:** 109 (app.py) + 18 (blueprints) = 127 total  
**Status:** 122 reachable + 5 conditionally hidden = 100% structured, 96% robust

**Critical Finding:** 5 endpoints in try/except block that become unreachable if import fails

---

## Direct @app.route Endpoints (109 total)

### Reachable: 104/109 (95%)

All 104 endpoints have proper function definitions:

```
/ → index
/agent/allocation → agent_allocation_status
/api/action/publish_all → api_action_publish_all
[... 100 more ...]
```

Complete list: See ENDPOINT_LISTING.txt (attached)

### Conditionally Unreachable: 5/109 (5%)

**Issue:** cross_audit endpoints inside try/except import block

**Location:** app.py lines 2692-2734

```python
try:
    from interface.cross_audit import (...)
    print("[app] cross_audit engine loaded")
    
    @app.route("/cross_audit/task", methods=["POST"])
    def cross_audit_task():  ← registered only if import succeeds
    
    @app.route("/cross_audit/submit", methods=["POST"])
    def cross_audit_submit():  ← registered only if import succeeds
    
    @app.route("/cross_audit/check/<task_id>")
    def cross_audit_check(task_id):  ← registered only if import succeeds
    
    @app.route("/cross_audit/report/<task_id>")
    def cross_audit_report(task_id):  ← registered only if import succeeds
    
    @app.route("/cross_audit/list")
    def cross_audit_list():  ← registered only if import succeeds

except Exception as _ce:
    print(f"[app] cross_audit load error: {_ce}")
    # Endpoints silently unregistered if import fails
```

**Affected Endpoints:**
1. `POST /cross_audit/task` → `cross_audit_task()`
2. `POST /cross_audit/submit` → `cross_audit_submit()`
3. `GET /cross_audit/check/<task_id>` → `cross_audit_check(task_id)`
4. `GET /cross_audit/report/<task_id>` → `cross_audit_report(task_id)`
5. `GET /cross_audit/list` → `cross_audit_list()`

**Severity:** MEDIUM - Endpoints fail silently if import fails

**Impact:**
- If `interface/cross_audit.py` doesn't exist or has import errors, endpoints become 404
- No 503 Service Unavailable; no error logged; just silently gone
- Client receives 404 "Not Found" instead of 503 "Service Unavailable"
- Difficult to diagnose without checking app startup logs

**Contrast with ISE Pattern (Better Design):**

```python
try:
    from ise.ai_session_state import AISessionStore
    _ise_session_store = AISessionStore(...)
    _ISE_AVAILABLE = True
except Exception as _e:
    _ISE_AVAILABLE = False
    print(f"[ISE] import failed: {_e}")

@app.route("/api/ise/knock", methods=["POST"])
def ise_knock():
    if not _ISE_AVAILABLE:
        return jsonify({"status": "error", "reason": "ISE not available"}), 503
    # ... logic
```

Result: Endpoints are always registered; they return 503 if unavailable. Better UX.

---

## Blueprint Endpoints (18 total)

### Reachable: 18/18 (100%)

All blueprint endpoints are properly registered and reachable:

| Blueprint | Routes | Status |
|-----------|--------|--------|
| ai_session_bp | 1 | ✓ /session/start |
| handshake_bp | 1 | ✓ /handshake |
| dashboard_bp | 1 | ✓ /dashboard |
| reflection_bp | 2 | ✓ /reflection, /reflection/generate |
| prediction_bp | 1 | ✓ /prediction/risk |
| mentor_bp | 1 | ✓ /mentor |
| commission_bp | 2 | ✓ /commission/list, /commission/<id> |
| context_bp | 1 | ✓ /context/compose |
| gate_bp | 5 | ✓ /api/gate/* (event, batch, extension, audit, health) |
| integrity_bp | 3 | ✓ /api/integrity/* (baseline, diagnose, verify) |
| time_api_bp | 7 | ✓ /time/* (audit, events, query, replay, etc.) |
| human_gate_bp | 5 | ✓ /api/human_gate/* (pending, approve, reject, status, submit) |
| jarvis_bp | 2 | ✓ /evaluate, /health |

**Total:** 32 blueprint routes (not counted in 109 direct routes)

---

## Findings Summary

### All Endpoints Structured

- [x] All 109 direct routes have function definitions
- [x] All 18 blueprint routes are registered
- [x] No undefined endpoints
- [x] No dangling decorators

### Reachability Issues: 1 Identified

**ISSUE #1 (MEDIUM):** cross_audit endpoints in try/except block

**Root Cause:** Entire endpoint registration inside exception handler

**Fix:** Move endpoints outside try/except or add availability flag (like ISE pattern)

**Recommendation:**

Option A (Preferred - Better UX):
```python
try:
    from interface.cross_audit import (...)
    _CROSS_AUDIT_AVAILABLE = True
except Exception as _ce:
    _CROSS_AUDIT_AVAILABLE = False
    print(f"[app] cross_audit load error: {_ce}")

@app.route("/cross_audit/task", methods=["POST"])
def cross_audit_task():
    if not _CROSS_AUDIT_AVAILABLE:
        return jsonify({"status": "error", "reason": "Cross-audit unavailable"}), 503
    return jsonify(create_task(...))
```

Option B (Minimum Fix):
```python
_CROSS_AUDIT_AVAILABLE = False
try:
    from interface.cross_audit import (...)
    _CROSS_AUDIT_AVAILABLE = True
    # Register endpoints here
except Exception as _ce:
    print(f"[app] cross_audit load error: {_ce}")
    # Endpoints NOT registered, but try block reports failure
```

---

## Verification Checklist

- [x] All 109 direct endpoints have function definitions
- [x] All 18 blueprint endpoints are registered
- [x] No 404 shadowing detected
- [x] Exception handler identified for cross_audit
- [x] ISE pattern reviewed (better design reference)
- [ ] cross_audit fix implemented
- [ ] Endpoints tested with import missing scenario

---

## Classification

**WEB Status:** ≈ WEB で継続可能  
**Verification State:** DESIGN + FOUND_ISSUE  
**Next Action:** Fix cross_audit pattern (simple 20-line change)  
**Blocking:** No - issue is graceful degradation, not critical failure

---

## Next: A2 Import Dependency Graph
