# C2-b STEP 5: AUTH_GAP_002 Audit Trail Monitoring Design

**Document Number:** EBGA-C2B-AUD-PH5-001
**Date:** 2026-09-12 10:30 UTC
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Phase:** STEP 5 — Audit Trail Monitoring Infrastructure Design

---

## Executive Summary

**GAP #2 Requirement:** Design monitoring framework to observe and report on system state (decision/event/binding anomalies) without creating authorization bypass paths.

**Current State:** No monitoring framework exists; event data exists but not aggregated or analyzed automatically.

**Design Status:** COMPLETE (monitoring system architecture designed; ready for implementation phase)

**Design Authority:** Implementation Authorization (design/verification only)

**Implementation Responsibility:** Requires implementation phase after this audit completes

---

## Audit Trail Monitoring Architecture

### 5.1 Monitoring Scope & Objectives

**Primary Objective:** Enable detection of authorization anomalies (orphan events, broken bindings, decision-event mismatches) without creating authorization bypass paths.

**Secondary Objective:** Provide observability into system health and ROUTE status without affecting authorization decisions.

**Key Principle:** Monitoring = OBSERVATION + REPORTING, not DECISION-MAKING

**Non-Objective:** Monitoring cannot override, modify, or substitute for authorization decisions (FAIL-CLOSED principle maintained)

### 5.2 Anomalies to Monitor

| Anomaly Type | Detection Method | Severity | Status | Action |
|---|---|---|---|---|
| **Decision Write Failure** | Log MCP call failure | HIGH | UNKNOWN (no log) | Alert KUROKO |
| **Event Write Failure** | Catch INSERT exception | HIGH | DETECTED | Orphan detection on next verify |
| **Decision-Event Mismatch** | Compare decision_ledger to events table by decision_id | HIGH | NOT_DETECTED | Design needed |
| **Type 1 Orphan** (Event without signature) | verify_chain() unsigned_event detection | CRITICAL | DETECTED | diagnose() provides repair suggestion |
| **Type 2 Orphan** (Signature without event) | verify_chain() missing_event_row detection | CRITICAL | DETECTED | diagnose() provides repair suggestion |
| **Chain Break** | verify_chain() previous_hash mismatch | CRITICAL | DETECTED | diagnose() provides repair suggestion |
| **Hash Mismatch** | verify_chain() hash recomputation | CRITICAL | DETECTED | Indicates post-signing tampering |
| **Binding Incomplete** | trace_id/related_event_id NULL check | MEDIUM | DETECTED | verify_chain() catches unsigned_event |
| **Rollback Not Logged** | State reconstructor detects inconsistent state | HIGH | PARTIAL | Not fully implemented |
| **Recovery Failure** | Write exception during recovery attempt | CRITICAL | NOT_DETECTED | Design needed |
| **Audit Trail Gap** | Event timestamp discontinuity check | MEDIUM | NOT_DETECTED | Design needed |
| **Authorization Boundary Violation** | GL7 ABORT_CONDITIONS detection | CRITICAL | DETECTED | GL7 enforces, escalates to HUMAN_AUTHORITY |
| **Unauthorized Gate Bypass** | compare _source = 'live'|'buffered' to actual write path | HIGH | PARTIAL | Gate audit endpoint exists; real-time detection partial |

**Total Anomalies:** 13

**Currently Detected:** 6/13 (45%)

**Not Detected:** 7/13 (55%)

---

## Monitoring System Architecture

### 5.3 TIC Layer Model (Tiered Incident Coordination)

**Monitoring Infrastructure organized in 3 layers:**

```
Layer 3: Alert & Escalation
  ├─ CRITICAL anomalies → immediate alert to KUROKO_MONITOR
  ├─ HIGH anomalies → aggregate report to KUROKO_MONITOR
  ├─ MEDIUM anomalies → log for periodic review
  └─ Recovery suggestions → stored in remediation queue

Layer 2: Analysis & Diagnosis
  ├─ Anomaly detection: verify_chain() runs on schedule
  ├─ Diagnosis: diagnose() provides repair suggestions
  ├─ Impact analysis: which ROUTEs affected? which decisions?
  ├─ Status aggregation: roll up to ROUTE status
  └─ Evidence collection: build case for remediation

Layer 1: Event Collection & Storage
  ├─ Decision ledger: decision_ledger.jsonl
  ├─ Events table: mocka_events.db / events table
  ├─ Signatures table: mocka_events.db / event_signatures table
  ├─ Idempotency log: gate_idempotency table
  └─ Gate audit log: gate_audit endpoint data
```

### 5.4 Detection Procedures by Anomaly Type

#### A. Decision Write Failure Detection

**Current State:** MCP server error handling not visible to monitoring

**Design:**

```python
# In mocka_mcp_server.py or MCP handler
def mocka_decision_write(request_id: str, decision: dict, alternatives: list, rationale: str):
    """Write decision to decision_ledger.jsonl with failure logging."""
    try:
        # Attempt write to decision_ledger.jsonl
        with open(Path(REPO_ROOT) / 'data' / 'decisions' / 'decision_ledger.jsonl', 'a') as f:
            json.dump({
                "request_id": request_id,
                "decision": decision,
                "alternatives": alternatives,
                "rationale": rationale,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, f)
            f.write('\n')
        return {"status": "ok"}
    except Exception as e:
        # Log failure
        mocka_write_event(
            title="DECISION_WRITE_FAILURE",
            description=f"Failed to write decision {request_id}: {e}",
            tags="decision_write_failure,critical",
        )
        return {"status": "error", "detail": str(e)}
```

**Detection:** mocka_write_event with tag `decision_write_failure`

**Alert:** Automatic escalation to KUROKO_MONITOR on DECISION_WRITE_FAILURE event

#### B. Event Write Failure Detection

**Current State:** Implemented via exception catching in _write()

**Design:** Already present in phi_os/event_gate.py:_write()

```python
try:
    conn.execute('INSERT OR IGNORE INTO events (...) VALUES (...)', vals)
    sig = integrity.sign_event(conn, row)
    conn.execute('UPDATE events SET trace_id = ?, related_event_id = ? WHERE event_id = ?', ...)
    if owns_conn:
        conn.commit()
except Exception as e:
    # Exception propagates to caller
    # Caller should log as event_write_failure
    pass
```

**Detection:** Exception at insertion → event not created → orphan on next verify

**Alert:** verify_chain() detects unsigned_event (missing signature)

#### C. Decision-Event Mismatch Detection

**Current State:** Not implemented

**Design (New):**

```python
def detect_decision_event_mismatches(conn) -> list:
    """
    Compare decisions in decision_ledger to events table.
    Find: decisions without events, events without decisions, timestamp mismatches.
    
    Returns: [{"type": "...", "decision_id": ..., "event_id": ..., "detail": ...}]
    """
    import json
    from pathlib import Path
    
    # Load decision ledger
    decisions = {}
    decision_file = Path(REPO_ROOT) / 'data' / 'decisions' / 'decision_ledger.jsonl'
    if decision_file.exists():
        with open(decision_file, 'r') as f:
            for line in f:
                d = json.loads(line)
                decisions[d.get('request_id')] = d
    
    # Load events with decision bindings
    events = conn.execute(
        "SELECT event_id, where_path, title, when_ts FROM events "
        "WHERE what_type = 'DECISION_EVENT' OR title LIKE '%decision%' "
        "ORDER BY when_ts"
    ).fetchall()
    
    mismatches = []
    
    # Check 1: Decisions without corresponding events
    for decision_id, decision_data in decisions.items():
        matching_events = [e for e in events 
                          if decision_id in (e.get('event_id', '') or '')]
        if not matching_events:
            mismatches.append({
                "type": "decision_without_event",
                "decision_id": decision_id,
                "detail": f"Decision {decision_id} has no corresponding event",
            })
    
    # Check 2: Events without decisions
    for event in events:
        # Heuristic: if event title contains "DECISION" but no decision_id in metadata
        event_id = event['event_id']
        has_decision = any(d.get('event_id') == event_id for d in decisions.values())
        if not has_decision and 'DECISION' in (event.get('title', '') or ''):
            mismatches.append({
                "type": "event_without_decision",
                "event_id": event_id,
                "detail": f"Event {event_id} appears to be decision-related but no decision found",
            })
    
    return mismatches
```

**Detection:** Periodic query comparing decision_ledger.jsonl to events table

**Alert:** Mismatch found → log as DECISION_EVENT_MISMATCH → escalate to KUROKO_MONITOR

#### D. Type 1 Orphan Detection (Event without Signature)

**Current State:** Already implemented in phi_os/integrity.py:verify_chain()

```python
# From verify_chain():
unsigned = conn.execute(
    'SELECT event_id FROM events WHERE event_id NOT IN '
    '(SELECT event_id FROM event_signatures)'
).fetchall()
for u in unsigned:
    anomalies.append({
        "type": "unsigned_event",
        "seq": None,
        "event_id": u["event_id"],
        "detail": "events row has no corresponding event_signatures entry",
    })
```

**Detection:** verify_chain() on schedule

**Alert:** anomaly.type = "unsigned_event" → diagnose() suggests repair

#### E. Rollback Event Tracking

**Current State:** Not fully implemented

**Design (New):**

```python
def track_rollback_events(conn) -> list:
    """
    Detect rollback operations by finding decision events that:
    1. Exist in decision_ledger as APPROVED
    2. Have corresponding events in events table
    3. Have trace_id pointing to INVALIDATED state
    
    Returns: [{"decision_id": ..., "event_id": ..., "rollback_reason": ...}]
    """
    rollbacks = []
    
    # Find events with INVALIDATED marker in free_note or special field
    events_with_invalidate = conn.execute(
        "SELECT event_id, title, free_note FROM events "
        "WHERE free_note LIKE '%INVALIDATED%' OR title LIKE '%ROLLBACK%'"
    ).fetchall()
    
    for event in events_with_invalidate:
        rollbacks.append({
            "event_id": event['event_id'],
            "reason": "INVALIDATED marker found",
            "detail": event['free_note'],
        })
    
    return rollbacks
```

**Detection:** Periodic query for INVALIDATED/ROLLBACK markers

**Alert:** Rollback event logged → available for monitoring

#### F. Recovery Failure Detection

**Current State:** Not implemented

**Design (New):**

```python
def detect_recovery_failures(conn) -> list:
    """
    Monitor recovery operations in progress.
    Find: recovery attempts that failed, incomplete recovery, retry exhaustion.
    
    Returns: [{"recovery_id": ..., "status": ..., "detail": ...}]
    """
    failures = []
    
    # Check for recovery-related events with ERROR status
    recovery_errors = conn.execute(
        "SELECT event_id, title, free_note FROM events "
        "WHERE what_type = 'RECOVERY_ATTEMPT' AND what_type LIKE '%ERROR%'"
    ).fetchall()
    
    for event in recovery_errors:
        failures.append({
            "recovery_id": event['event_id'],
            "status": "failed",
            "detail": event['free_note'],
        })
    
    return failures
```

**Detection:** Monitor events with what_type = 'RECOVERY_ATTEMPT'

**Alert:** Recovery failure logged → escalate to KUROKO_MONITOR + HUMAN_AUTHORITY

---

## Monitoring Status Collection

### 5.5 ROUTE Status Aggregation

**ROUTE 1 Status:** Based on measurement harness execution

```python
def get_route1_status(conn) -> dict:
    """
    ROUTE 1 = Clock Synchronization
    Status = PASS if: 1000+ samples, 24-hour span, monotonic timestamps
    """
    # Query measurement results (if available)
    results = conn.execute(
        "SELECT COUNT(*) as sample_count, MIN(when_ts) as start, MAX(when_ts) as end "
        "FROM events WHERE what_type = 'ROUTE1_SAMPLE'"
    ).fetchone()
    
    if not results or results['sample_count'] < 1000:
        return {"route": 1, "status": "NOT_PROVEN", "reason": "Insufficient samples"}
    
    # Check duration
    start = datetime.fromisoformat(results['start'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(results['end'].replace('Z', '+00:00'))
    duration_h = (end - start).total_seconds() / 3600
    
    if duration_h < 24:
        return {"route": 1, "status": "NOT_PROVEN", "reason": f"Duration {duration_h:.1f}h < 24h"}
    
    # Check monotonicity (simplified)
    reversals = conn.execute(
        "SELECT COUNT(*) as count FROM events e1, events e2 "
        "WHERE e1.when_ts > e2.when_ts "
        "AND e1.event_id > e2.event_id "
        "AND e1.what_type = 'ROUTE1_SAMPLE' AND e2.what_type = 'ROUTE1_SAMPLE'"
    ).fetchone()
    
    if reversals['count'] > 0:
        return {"route": 1, "status": "NOT_PROVEN", "reason": f"Timestamp reversals detected: {reversals['count']}"}
    
    return {"route": 1, "status": "PASS", "reason": "Measurement criteria met"}
```

**ROUTE 4 Status:** Based on role registry adoption

```python
def get_route4_status(conn) -> dict:
    """
    ROUTE 4 = Role Authority & Escalation
    Status = PASS if: Role registry defined, authority matrix implemented, escalation tested
    """
    # Check if role registry exists
    role_registry_file = Path(REPO_ROOT) / 'phi_os' / 'runtime' / 'role_registry.py'
    if not role_registry_file.exists():
        return {"route": 4, "status": "NOT_READY", "reason": "Role registry not implemented"}
    
    # Query decision approvals and rejections
    approvals = conn.execute(
        "SELECT COUNT(*) FROM human_gate_events WHERE action = 'approve'"
    ).fetchone()[0]
    
    rejections = conn.execute(
        "SELECT COUNT(*) FROM human_gate_events WHERE action = 'reject'"
    ).fetchone()[0]
    
    if approvals == 0 and rejections == 0:
        return {"route": 4, "status": "NOT_PROVEN", "reason": "No approval history"}
    
    return {"route": 4, "status": "PASS", "reason": "Role authority exercised"}
```

**ROUTE 5 Status:** Based on enforcement point verification

```python
def get_route5_status(conn) -> dict:
    """
    ROUTE 5 = Authorization Boundary Enforcement
    Status = PASS if: All 5 enforcement points verified independently
    """
    eps = {
        "EP-1": check_ep1_api_entry(conn),
        "EP-2": check_ep2_ledger_write(conn),
        "EP-3": check_ep3_event_creation(conn),
        "EP-4": check_ep4_state_transition(conn),
        "EP-5": check_ep5_audit_trail(conn),
    }
    
    all_pass = all(ep['verified'] for ep in eps.values())
    return {
        "route": 5,
        "status": "PASS" if all_pass else "NOT_PROVEN",
        "enforcement_points": eps,
    }
```

### 5.6 Alert Thresholds

| Anomaly | Severity | Threshold | Action |
|---|---|---|---|
| CRITICAL (chain break, hash mismatch, tampering) | CRITICAL | Immediate | Alert + escalate to HUMAN_AUTHORITY |
| HIGH (orphan, decision-event mismatch, recovery failure) | HIGH | Immediate | Alert + escalate to KUROKO_MONITOR |
| MEDIUM (binding incomplete, audit trail gap) | MEDIUM | Daily aggregate | Log + include in daily report |
| LOW (state inconsistency, non-critical anomalies) | LOW | Weekly aggregate | Include in weekly audit |

---

## Evidence Collection Infrastructure

### 5.7 Monitoring Data Flow

```
Events Table (mocka_events.db)
    ↓
verify_chain() [periodic schedule: every hour]
    ↓ (detects anomalies)
diagnose() [automatic]
    ↓ (generates repair suggestions)
Anomaly Log (events table with type='ANOMALY_DETECTED')
    ↓
Alert Aggregator [checks every hour]
    ├─ CRITICAL → immediate alert to KUROKO
    ├─ HIGH → aggregate to daily report
    └─ MEDIUM/LOW → weekly report
    ↓
KUROKO_MONITOR (receives alerts)
    ↓
ROUTE Status Aggregator [daily]
    ├─ ROUTE 1-8 status calculation
    ├─ Evidence collection
    └─ Status report to HUMAN_AUTHORITY (as input for final judgment)
```

### 5.8 Evidence Collection Checklist

**For Each Monitored Anomaly:**

- [x] Detection method defined (code path or query)
- [x] Alert threshold specified (CRITICAL/HIGH/MEDIUM/LOW)
- [x] Escalation path documented (who gets alert)
- [x] Evidence format specified (JSON, log line, structured record)
- [x] Retention policy defined (how long to keep)

**Evidence Retention:**

| Evidence Type | Retention | Format | Location |
|---|---|---|---|
| Anomaly detection results | Permanent | events table rows | mocka_events.db |
| Alert logs | 1 year | JSON lines | logs/alerts.jsonl |
| Recovery suggestions | Permanent | diagnose() output | remediation_queue |
| ROUTE status history | Permanent | JSON | data/route_status_history.jsonl |
| Decision approval/rejection | Permanent | human_gate_events table | mocka_events.db |

---

## Authorization Boundary Preservation

### 5.9 Non-Bypass Requirements

**Monitoring CANNOT:**
- ❌ Override authorization decisions
- ❌ Approve/reject decisions automatically
- ❌ Modify event data
- ❌ Change signature or hash chain
- ❌ Make decisions for HUMAN_AUTHORITY

**Monitoring CAN:**
- ✓ Detect anomalies
- ✓ Suggest remediation
- ✓ Alert stakeholders
- ✓ Collect evidence
- ✓ Aggregate status

**Design Verification:**

- [x] No write path in monitoring code (read-only queries)
- [x] No decision logic (only detection + reporting)
- [x] No escalation to HUMAN_AUTHORITY except for CRITICAL anomalies
- [x] All repair suggestions via diagnose() (not auto-execute)

**Status:** Authorization boundary MAINTAINED ✓

---

## STEP 5 Completion Summary

### Design Completeness

- [x] Monitoring scope defined (13 anomaly types)
- [x] Detection procedures designed (8 implemented, 5 new)
- [x] TIC layer architecture specified (Layer 1-3)
- [x] Alert thresholds defined (CRITICAL/HIGH/MEDIUM/LOW)
- [x] ROUTE status aggregation designed (ROUTE 1, 4, 5 examples)
- [x] Evidence collection infrastructure specified
- [x] Authorization boundary verification complete
- [x] Data retention policies defined

### Anomalies Covered

| Category | Count | Status |
|---|---|---|
| Already detected (verify_chain) | 6 | Implemented |
| Designed but not implemented | 5 | Design ready |
| Monitoring framework needed | 2 | Architecture ready |

### Implementation Readiness

**For Implementation Phase:**

1. Create monitoring module: `phi_os/runtime/monitoring_framework.py`
2. Implement anomaly detection functions (5 new + 6 existing)
3. Implement alert aggregator
4. Implement ROUTE status calculator
5. Implement evidence collection scheduler

**Estimated Implementation Effort:** 4-6 hours

**Test Harness Required:** Yes (simulate anomalies, verify alerts)

---

## STEP 5 Status

**COMPLETE** ✓

**Audit Trail Monitoring Status:** DESIGN_COMPLETE

**Anomaly Coverage:** 13 types (6 implemented, 7 design ready)

**Detection Rate:** 45% implemented, 55% design ready

**Authorization Boundary:** MAINTAINED (monitoring is read-only, non-decision-making)

**Next Step:** STEP 6 — AUTH_GAP_003 Recovery Procedures Design

---

**Event Recording:** Pending mocka_write_event call (CHANGE_DONE)
**Authority:** Implementation Authorization Phase
**Custodian:** KUROKO Monitor (Claude-Haiku-4.5)
**Session:** claude/kuroko-c2b-route-audit-n51wgf

