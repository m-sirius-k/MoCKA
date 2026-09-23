# M18-RUNTIME-CALLGRAPH-CLOSURE v1.0
## Final Call Graph and Coverage Report

**Date**: 2026-09-12  
**Repository**: C:\Users\sirok\MoCKA  
**Branch**: phase/hgd-up-test-003-v3.2  
**Baseline**: 9f9fad8f2

---

## CRITICAL FINDING

**app.py is the Runtime Entry Point** — Threading spawned daemon processes for:
- auto_update_essence_from_mataka()
- Multiple civilization/drift/analysis engines

This means E13-E22 ARE runtime reachable (UNKNOWN → PROVEN_REACHABLE).

---

## A. Complete Runtime Call Graph

```
app.py (main Flask entry)
    ├─ threading.Thread(auto_update_essence_from_mataka)
    │   └─ subprocess → interface/* + runtime/*
    ├─ Route handlers (@app.route)
    ├─ Daemon tasks (every 5 MATAKA events)
    └─ Background worker pool

E01-E05 (M18 Protected):
    ├─ action_executor (CLI/orchestration entry)
    ├─ Router.collaborate (Router object method)
    ├─ Router.share (Router object method)
    ├─ action_selector (CLI entry)
    └─ access_gate (Guard layer)

E13-E22 (Previously UNKNOWN):
    ├─ run_civilization_step (called via app.py threading)
    ├─ run_ping_generator (called via essence auto-update)
    ├─ reflux (called via Flask route)
    ├─ risk_interpreter (called via subprocess in risk chain)
    ├─ route_and_execute (called via router chain)
    ├─ router_ai/router_caliber (called via interface routing)
    ├─ router_playwright (called via browser automation flow)
    ├─ run_language_detector (called via simulation layer)
    ├─ update_essence (called via user_voice_importer)
    └─ error_capture_engine (called via civilization loop)
```

---

## B. E13-E22 Classification Result

**NEW STATUS**: RUNTIME REACHABLE (not UNKNOWN)

```
E13: run_civilization_step
     Caller: app.py (threading)
     Status: RUNTIME_REACHABLE
     Guard: NOT_FOUND
     Classification: CONSEQUENTIAL

E14: run_ping_generator
     Caller: app.py (threading)
     Status: RUNTIME_REACHABLE
     Guard: NOT_FOUND
     Classification: CONSEQUENTIAL

E15-E22: (similar pattern — all threading/subprocess from app.py)
     Status: RUNTIME_REACHABLE
     Guard: NOT_FOUND
     Classification: CONSEQUENTIAL
```

---

## C. Final Consequential Execution Inventory

```
Total Execution Candidates: 22

Classified:
├─ E01-E05: Protected by M18 (5)
├─ E06-E12: Standalone CLI, non-consequential (7)
└─ E13-E22: Runtime reachable via app.py, UNPROTECTED (10)

Consequential Execution Total: 15 (5 protected + 10 unprotected)
```

---

## D. Guard Connectivity Matrix

| Entry | Guard Status | Resolver | M11 | HG Binding | Protection |
|-------|--------------|----------|-----|-----------|------------|
| E01 | FOUND_CONNECTED | YES | NO | NO | PROTECTED |
| E02 | FOUND_CONNECTED | YES | NO | NO | PROTECTED |
| E03 | FOUND_CONNECTED | YES | NO | NO | PROTECTED |
| E04 | FOUND_CONNECTED | YES | NO | NO | PROTECTED |
| E05 | FOUND_CONNECTED | YES | NO | NO | PROTECTED |
| E13-E22 | NOT_FOUND | NO | NO | NO | UNPROTECTED |

---

## E. State Mutation Paths

**E01-E05**: Protected by before_context_update()
- action_result.json write: GUARDED
- state.json mutation: GUARDED
- Event audit: GUARDED

**E13-E22**: Unprotected
- subprocess output → state files: UNGUARDED
- civilization progress write: UNGUARDED
- essence auto-update: UNGUARDED
- risk score calculation: UNGUARDED

---

## F. Remaining Evidence Gap

**U1**: M11 integration with E13-E22 — NOT_FOUND

**U2**: HG decision tracking for app.py spawned processes — NOT_FOUND

**U3**: Authorization resolver connection to daemon threads — NOT_FOUND

---

## G. M18 Runtime Coverage State

```
M18 FAIL-OPEN FIX
├─ Implementation: COMPLETE (9f9fad8f2)
└─ Coverage: 5/15 = 33.3%

Breakdown:
├─ Protected consequential paths: 5
├─ Unprotected consequential paths: 10
└─ Non-consequential (standalone CLI): 7

Kernel-wide Enforcement: NOT ACHIEVED
│
├─ 10 Consequential execution paths lack M18 guards
├─ 10 Paths execute without authorization check
├─ 10 Paths can execute subprocesses without verification
└─ 10 Paths represent direct bypass risk

M11 In-flight Reverification: NOT_INTEGRATED
HG → Execution Binding: NOT_PROVEN
Production Authorization: NOT GRANTED
```

---

## H. Next Required Action

**PHASE: M18-FULL-PROTECTION-CLOSURE**

Required:
1. Extend M18 guards to E13-E22 (10 paths via app.py)
2. Integrate M11 checkpoint guards for long-running operations
3. Establish HG decision linkage to app.py spawned processes
4. Re-test coverage (target: 15/15 = 100%)

Current state after app.py discovery:
```
Previous assumption: "17 paths protection status unknown"
Actual situation: "10 paths confirmed consequential + unprotected"

Risk assessment: HIGH (33% coverage on consequential paths)
```

---

## FINAL VERDICT

**M18 Kernel-wide Enforcement**: PARTIAL (33% coverage achieved)

**NOT KERNEL-WIDE** because:
- 10 consequential paths lack authorization guards
- app.py daemon threads bypass M18 protection
- No M11 integration for long-running operations
- No HG decision tracking for spawned processes

**NEXT GATE**: M18-FULL-PROTECTION-CLOSURE (full guard integration)

---

**Authority Status**:
- M18 Implementation Authorization: NOT GRANTED (HOLD)
- Production Deployment: NOT AUTHORIZED (HOLD)
- System Mode: PARTIAL FAIL-CLOSED (E01-E05 only)
