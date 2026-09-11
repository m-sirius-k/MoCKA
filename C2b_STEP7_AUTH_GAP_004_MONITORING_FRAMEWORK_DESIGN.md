# C2-b STEP 7: AUTH_GAP_004 Monitoring Framework Design

**Document Number:** EBGA-C2B-AUD-PH7-001
**Date:** 2026-09-12 11:45 UTC
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Phase:** STEP 7 — Monitoring Infrastructure (TIC Layers 2-4)

---

## Executive Summary

**GAP #4 Requirement:** Design monitoring framework to collect ROUTE status metrics, aggregate results, and detect authorization boundary violations without creating bypass paths.

**Status:** DESIGN_COMPLETE (3 candidate architectures ready for implementation)

**Implementation Required:** Requires explicit approval; monitoring must preserve authorization semantics

---

## Monitoring Framework Architecture

### 7.1 Three Candidate Approaches

**Candidate A: Centralized Aggregator (Simple)**

```
Events Table
    ↓ (query hourly)
Status Calculator [single process]
    ├─ ROUTE 1 status (sample count, duration, monotonicity)
    ├─ ROUTE 4 status (role definitions, approvals)
    ├─ ROUTE 5 status (enforcement point verification)
    ├─ ROUTE 6-8 status (aggregated)
    ↓
Status Report (JSON)
    ↓ (alert if RED)
KUROKO_MONITOR / HUMAN_AUTHORITY
```

**Pros:** Simple, centralized, easy to audit
**Cons:** Single point of failure, batch processing only

---

**Candidate B: Distributed Monitors (Resilient)**

```
Events Table ← ROUTE 1 Monitor
           ← ROUTE 4 Monitor  
           ← ROUTE 5 Monitor
           ← ROUTE 6-8 Monitor (combined)
    ↓ (each queries independently)
Status Reports (4 channels)
    ↓
Alert Aggregator [consolidates]
    ↓
KUROKO_MONITOR / HUMAN_AUTHORITY
```

**Pros:** Resilient (one failure doesn't stop all), parallel
**Cons:** More complex, potential race conditions

---

**Candidate C: Hybrid (Event-Driven + Periodic)**

```
Events Table
    ├─ Event trigger: on CRITICAL anomaly → immediate alert
    └─ Hourly batch: aggregate status for all ROUTEs
    ↓
Status Report + Alert Stream
    ↓
KUROKO_MONITOR / HUMAN_AUTHORITY
```

**Pros:** Fast response (events) + comprehensive reports (batch)
**Cons:** Dual-path complexity

---

### 7.2 ROUTE Status Metrics

**ROUTE 1 (Clock Synchronization):**
```json
{
  "route": 1,
  "status": "PASS|NOT_PROVEN|FAIL",
  "sample_count": 1000,
  "duration_hours": 24,
  "monotonicity_rate_percent": 100,
  "drift_ms": 50,
  "last_verified": "2026-09-12T12:00:00Z"
}
```

**ROUTE 2-3 (Persistence, Binding):** Already PASS (regression check)

**ROUTE 4 (Role Authority):**
```json
{
  "route": 4,
  "status": "PASS|NOT_READY",
  "role_registry": "implemented|pending",
  "approval_count": 5,
  "rejection_count": 1,
  "escalation_instances": 0
}
```

**ROUTE 5 (Authorization Boundary):**
```json
{
  "route": 5,
  "status": "PASS|NOT_PROVEN",
  "enforcement_points": {
    "EP-1": {"status": "verified", "last_check": "2026-09-12T12:00:00Z"},
    "EP-2": {"status": "verified"},
    "EP-3": {"status": "verified"},
    "EP-4": {"status": "unknown"},
    "EP-5": {"status": "verified"}
  },
  "bypass_attempts": 0
}
```

**ROUTE 6-8 (Audit Trail, Recovery, Monitoring):**
```json
{
  "route": 6,
  "status": "PASS|NOT_PROVEN",
  "trace_verification": "passed",
  "binding_completeness": 99.5
},
{
  "route": 7,
  "status": "NOT_PROVEN",
  "recovery_procedures": "designed_awaiting_approval",
  "test_coverage": 0
},
{
  "route": 8,
  "status": "NOT_PROVEN",
  "monitoring_framework": "designed",
  "alerts_active": 0
}
```

---

### 7.3 Authorization Boundary Verification

**Monitoring Cannot:**
- ❌ Modify events or signatures
- ❌ Override authorization decisions
- ❌ Bypass HUMAN_AUTHORITY approval
- ❌ Create new events (monitoring-only)

**Monitoring Can:**
- ✓ Query events, signatures, decisions
- ✓ Aggregate status
- ✓ Alert on anomalies
- ✓ Suggest actions (not execute)

**Verification:**
- [x] Monitoring queries are read-only
- [x] No write operations in monitoring code
- [x] No decision logic (only reporting)
- [x] All suggestions require approval

**Status:** Authorization boundary MAINTAINED ✓

---

### 7.4 Alert Configuration

| Alert Level | Condition | Action | Recipient |
|---|---|---|---|
| CRITICAL | Tamper detected, recovery failure | Immediate | HUMAN_AUTHORITY + KUROKO |
| HIGH | Decision-event mismatch, orphan found | Hourly aggregate | KUROKO_MONITOR |
| MEDIUM | Audit trail gap, binding incomplete | Daily report | KUROKO_MONITOR |
| LOW | Non-critical anomalies | Weekly report | Archive |

---

## STEP 7 Status

**COMPLETE** ✓

**Framework Status:** DESIGN_COMPLETE_AWAITING_APPROVAL

**Candidates:** 3 (Centralized, Distributed, Hybrid)

**Metrics Defined:** 8 ROUTEs (status + detailed metrics)

**Implementation Effort:** 4-6 hours

**Next Step:** STEP 8 — ROUTE 5 Authorization Boundary Re-Audit

---

**Custodian:** KUROKO Monitor
**Session:** claude/kuroko-c2b-route-audit-n51wgf

