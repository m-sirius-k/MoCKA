# RUNTIME PATH CLOSURE MATRIX v1.0
## 15 Consequential Execution Paths — Complete Chain Analysis

**Date**: 2026-09-13  
**Phase**: Audit Phase 2 — Path-Centric Gap Remapping  
**Authorization**: NOT GRANTED (Investigation only)  
**System State**: HOLD / FAIL-CLOSED

---

## MATRIX LEGEND

| Column | Meaning | Values |
|--------|---------|--------|
| **Path** | Consequential execution path ID | E01-E22 |
| **Entry** | Runtime entry point location | File:line or route |
| **Decision** | Where decision/intent is determined | Function/location or "IMPLICIT" |
| **Auth** | Authorization source & binding | File:location or "NOT_FOUND" |
| **Gate** | Enforcement gate location | Function or "NOT_FOUND" |
| **Enforce** | Actual enforcement at runtime | YES/NO/PARTIAL/UNKNOWN |
| **Exec** | Where actual execution occurs | Subprocess/function/API |
| **Evidence** | Audit trail recorded | YES/PARTIAL/NO |
| **Test** | Integration test coverage | YES/PARTIAL/NO/UNKNOWN |
| **Status** | Runtime closure state | See legend below |

### Status Legend
- **✓ CLOSED**: All 8 dimensions verified
- **⚠ PARTIAL**: Some dimensions missing
- **✗ OPEN**: Critical dimensions missing
- **? UNKNOWN**: Insufficient evidence to assess

---

## PROTECTED PATHS (E01-E05) — 5 paths

### E01: action_executor()

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/action_executor.py:13 | execute_action() |
| **Decision** | action_executor.py (implicit in action_type) | Parse action_type parameter |
| **Auth Source** | before_context_update() @ phi_os/context/access_gate.py:32 | AuthorizationResolver imported |
| **Gate Location** | before_context_update() → AuthorizationResolver.resolve() | M18 guard present |
| **Enforcement** | **YES** | Resolver returns ALLOW/BLOCK/UNKNOWN; execution conditional |
| **Exec Location** | subprocess via orchestration or direct action execution | Variable based on action_type |
| **Evidence** | **YES** | action_result.json audit log; CSV write calls |
| **Test Coverage** | **YES** | 61 regression tests PASS (M18 suite) |
| **Status** | **✓ CLOSED** | Runtime enforcement verified, tested, evidenced |

**Chain**: Entry → (M18 guard) → AuthorizationResolver.resolve() → ALLOW/BLOCK → Execution → action_result audit

**Risk**: NONE (protected and tested)

---

### E02: Router.collaborate()

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/router.py:211 | collaborate() method |
| **Decision** | Router object state + method routing | Intent implicit in method |
| **Auth Source** | before_context_update() (M18 guard applied) | M18 added per report |
| **Gate Location** | before_context_update() prior to Popen | M18 guard wraps subprocess call |
| **Enforcement** | **YES** | Resolver blocks unauthorized subprocess |
| **Exec Location** | subprocess.Popen() call | Line 211+ (collaborate subprocess) |
| **Evidence** | **YES** | action_result.json, CSV audit |
| **Test Coverage** | **YES** | Included in 61 regression tests |
| **Status** | **✓ CLOSED** | M18 guard verified; tested |

**Chain**: Router.collaborate() → (M18) → AuthorizationResolver → Subprocess guarded

---

### E03: Router.share()

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/router.py:258 | share() method |
| **Decision** | Router state + method | Intent implicit |
| **Auth Source** | before_context_update() (M18) | M18 guard applied |
| **Gate Location** | before_context_update() | M18 checkpoint |
| **Enforcement** | **YES** | Authorization verification before Popen |
| **Exec Location** | subprocess.Popen() call | Line 258+ |
| **Evidence** | **YES** | Audit logs |
| **Test Coverage** | **YES** | Regression tests PASS |
| **Status** | **✓ CLOSED** | Protected; tested |

---

### E04: action_selector()

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/action_selector.py:73 | main() entry |
| **Decision** | CLI args parse action_type | Explicit argument |
| **Auth Source** | before_context_update() (M18) | M18 guard added |
| **Gate Location** | before_context_update() | M18 checkpoint |
| **Enforcement** | **YES** | State mutation guarded |
| **Exec Location** | state.json mutation + potential subprocess | Line 73+ |
| **Evidence** | **YES** | Audit trail |
| **Test Coverage** | **YES** | M18 tests include |
| **Status** | **✓ CLOSED** | Protected; tested |

---

### E05: access_gate (before_context_update)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | phi_os/context/access_gate.py:32 | Guard layer |
| **Decision** | N/A (guard layer only) | Decision elsewhere |
| **Auth Source** | AuthorizationResolver instance | Created per-execution |
| **Gate Location** | access_gate.py (THIS is the gate) | Line 32+ |
| **Enforcement** | **YES** | ImportError fixed; guard functional |
| **Exec Location** | Not execution location (guard layer) | Wrapper only |
| **Evidence** | **YES** | Calls logged |
| **Test Coverage** | **YES** | M18 tests PASS |
| **Status** | **✓ CLOSED** | Guard operational; part of E01-E04 chain |

---

## UNPROTECTED PATHS (E06-E22) — 10+ paths

### E06-E08: auto_runner.py subprocess.run() calls

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/auto_runner.py:14-16 | Three subprocess.run() calls |
| **Decision** | Implicit in function logic | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization check before call |
| **Gate Location** | **NOT_FOUND** | No M18 guard present |
| **Enforcement** | **NO** | Direct subprocess execution; no guard |
| **Exec Location** | subprocess.run() @ line 14,15,16 | Three separate calls |
| **Evidence** | **NO** | No audit logging for these paths |
| **Test Coverage** | **NO** | Zero integration tests for E06 |
| **Status** | **✗ OPEN** | No authorization, no gate, no test, no evidence |

**Chain**: Entry → subprocess.run() → [NO GUARD] → Execution (uncontrolled)

**Risk**: CRITICAL — Authorization bypass possible; state mutation unaudited

**Closure Blocker**: Add M18 guard before subprocess.run() calls

---

### E09: run_step() in mocka_drift_loop.py

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/analysis/mocka_drift_loop.py:28 | run_step() function |
| **Decision** | Implicit loop iteration | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization check |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Direct execution |
| **Exec Location** | subprocess.run() call | Loop-spawned subprocess |
| **Evidence** | **NO** | No audit trail |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected execution |

**Closure Blocker**: Add M18 guard; create tests

---

### E10-E11: event_watcher.py subprocess calls

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/event_watcher.py:22-23 | Two subprocess calls |
| **Decision** | Event-driven (implicit) | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Unguarded |
| **Exec Location** | subprocess.run() @ line 22,23 | Direct calls |
| **Evidence** | **NO** | No logging |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E12: error_capture_engine()

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/error_capture_engine.py:15 | error_capture_engine() |
| **Decision** | Implicit in error type | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Direct subprocess |
| **Exec Location** | subprocess.run() | Line 15 |
| **Evidence** | **NO** | No audit logging |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E13: run_civilization_step() [CRITICAL]

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | runtime/civilization_bridge.py:58 | Called via app.py threading |
| **Decision** | Implicit in civilization loop | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization chain |
| **Gate Location** | **NOT_FOUND** | No M18 guard |
| **Enforcement** | **NO** | Threading bypasses authorization |
| **Exec Location** | subprocess.run() from app.py daemon thread | Spawned thread execution |
| **Evidence** | **NO** | No audit trail for this path |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | **CRITICAL** — Daemon thread bypass |

**Chain**: app.py threading.Thread() → run_civilization_step() → subprocess.run() [NO GUARD]

**Risk**: CRITICAL — Daemon process circumvents authorization entirely

**Closure Blocker**: Add authorization check at threading spawn point and function entry

---

### E14: run_ping_generator() (essence_auto_updater.py:148)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/essence_auto_updater.py:148 | auto-update function |
| **Decision** | Timer-driven (implicit) | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Subprocess spawned from app.py threads |
| **Exec Location** | subprocess.run() | Spawned from essence update loop |
| **Evidence** | **NO** | No audit logging |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E15: reflux() (reflux.py:50)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/reflux.py:50 | Flask route handler |
| **Decision** | Route implicit | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Direct Flask subprocess execution |
| **Exec Location** | subprocess.run() | Line 50+ |
| **Evidence** | **NO** | No audit trail |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Flask route bypasses governance |

---

### E16: risk_interpreter() (risk_interpreter.py:287)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/risk_interpreter.py:287 | risk_interpreter() function |
| **Decision** | Implicit in analysis type | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Unguarded subprocess |
| **Exec Location** | subprocess.run() | Line 287+ |
| **Evidence** | **NO** | No logging |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E17-E19: router_* variants (caliber, ai, execute)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/router_caliber.py:5, router_ai.py:8, router_execute.py:4,11 | Three router variants |
| **Decision** | Router state implicit | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization binding |
| **Gate Location** | **NOT_FOUND** | No M18 guard |
| **Enforcement** | **NO** | Direct subprocess calls |
| **Exec Location** | subprocess.run() in each | Lines 5, 8, 4/11 |
| **Evidence** | **NO** | No audit trails |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E20: router_playwright() (playwright.py:5)

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/router_playwright.py:5 | Browser automation router |
| **Decision** | Implicit | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Browser automation spawned uncontrolled |
| **Exec Location** | subprocess.run() or playwright execute | Line 5+ |
| **Evidence** | **NO** | No audit logging |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

### E21-E22: language_detector, user_voice_importer

| Dimension | Value | Evidence |
|-----------|-------|----------|
| **Entry** | interface/simulation_layer.py:48, interface/user_voice_importer.py:172 | User input processors |
| **Decision** | Input-driven implicit | No decision gate |
| **Auth Source** | **NOT_FOUND** | No authorization |
| **Gate Location** | **NOT_FOUND** | No guard |
| **Enforcement** | **NO** | Uncontrolled subprocess |
| **Exec Location** | subprocess.run() in each | Lines 48, 172 |
| **Evidence** | **NO** | No audit trails |
| **Test Coverage** | **NO** | Zero tests |
| **Status** | **✗ OPEN** | Unprotected |

---

## SUMMARY TABLE

| Path ID | Entry Point | Decision | Auth | Gate | Enforce | Exec | Evidence | Test | Status | Risk |
|---------|-------------|----------|------|------|---------|------|----------|------|--------|------|
| **E01** | action_executor | action_type | M18 ✓ | ✓ | YES | subprocess | YES | YES | ✓ CLOSED | NONE |
| **E02** | Router.collaborate | method | M18 ✓ | ✓ | YES | Popen | YES | YES | ✓ CLOSED | NONE |
| **E03** | Router.share | method | M18 ✓ | ✓ | YES | Popen | YES | YES | ✓ CLOSED | NONE |
| **E04** | action_selector | CLI args | M18 ✓ | ✓ | YES | state/subproc | YES | YES | ✓ CLOSED | NONE |
| **E05** | access_gate | (guard) | N/A | ✓ (is gate) | YES | (guard) | YES | YES | ✓ CLOSED | NONE |
| **E06-E08** | auto_runner | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | CRIT |
| **E09** | drift_loop | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E10-E11** | event_watcher | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E12** | error_capture | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E13** | civilization_bridge | implicit | ✗ | ✗ | NO | daemon/subproc | NO | NO | ✗ OPEN | **CRIT** |
| **E14** | essence_updater | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E15** | reflux (Flask) | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E16** | risk_interpreter | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E17-E19** | router_* variants | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |
| **E20** | router_playwright | implicit | ✗ | ✗ | NO | playwright | NO | NO | ✗ OPEN | HIGH |
| **E21-E22** | user processors | implicit | ✗ | ✗ | NO | subprocess | NO | NO | ✗ OPEN | HIGH |

---

## CRITICAL FINDINGS

### E01-E05: CLOSED (✓)
- All 8 dimensions verified
- M18 guard present and functional
- Regression tests PASS (61/61)
- Audit trail complete

### E06-E22: OPEN (✗)
- Authorization missing in all 10 paths
- No M18 guard present in any path
- Zero integration tests
- No audit trail
- **Direct authorization bypass possible** (A10 test confirms)

### E13: DAEMON THREAD BYPASS (CRITICAL)
- Authorization bypassed at threading spawn point
- app.py creates threads without authorization context
- Civilization step executes in daemon thread outside request/session context
- Highest risk for unauthorized execution

---

## CLOSURE REQUIREMENTS

### For Each OPEN Path (E06-E22)

To reach ✓ CLOSED status, each path requires:

1. **Add M18 Guard** — before_context_update() wrapper
2. **Add Authorization Test** — Integration test for authorized/denied scenarios
3. **Add Audit Trail** — Record execution in action_result.json or event ledger
4. **Add Decision Point** — Explicit decision (implicit→explicit)
5. **Verify Test PASS** — M18 + authorization tests must pass

### Timeline for E06-E22 Closure
- Implementation: ~40-60 LOC per path (guessing 3-5 LOC/guard + test setup)
- Testing: ~50 integration tests (~1500-2000 LOC)
- Verification: ~1-2 review cycles
- **Total**: 2-3 implementation cycles

---

## NEXT STEPS (FOR HUMAN GATE)

1. **Approve E06-E22 M18 Extension** — Required to close authorization gap
2. **Authorize A10 Fix** — Demonstrate bypass prevention
3. **Mandate E06-E22 Tests** — Require before deployment

---

**END OF RUNTIME PATH CLOSURE MATRIX**

No implementation modifications made. All findings are Investigation-based only.

