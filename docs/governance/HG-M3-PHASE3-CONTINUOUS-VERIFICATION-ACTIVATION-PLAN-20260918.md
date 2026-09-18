# HG-M3 Phase 3: Continuous Verification Activation Plan
**Date:** 2026-09-18 | **Authority:** Conditional Authorization (Option B) - Q5: OPTION C | **Status:** PREPARATION

---

## PURPOSE

Define continuous monitoring strategy for Phase 3 implementation. Per Human Gate Q5 decision (Option C: Continuous Monitoring), implement 24/7 verification of evidence/authority/runtime/configuration state.

---

## MONITORED STATE DIMENSIONS

### Dimension M1: Evidence State
**What to Monitor:**
- Evidence database integrity (hourly)
- Evidence file availability (hourly)
- SHA256 hash validity (on access)
- Evidence freshness (>1 day old?)
- Data provenance (synthetic vs. production)

**Detection Method:**
- Automated: Evidence validation check
- Trigger: If evidence fails hash check → escalate

**Action If Violated:**
- Log evidence integrity incident
- Halt dependent bindings
- Notify Human Gate
- Trigger rollback assessment

---

### Dimension M2: Authority State
**What to Monitor:**
- Authority registry state (continuous)
- Authority revocation checks (on each binding)
- Temporal snapshots validity (daily)
- Q2 policy compliance (retroactive registration rules)
- Authority freshness (>30 days old?)

**Detection Method:**
- Automated: Authority validation check
- Trigger: If authority invalid → binding fails

**Action If Violated:**
- Mark binding as INVALID
- Log authority state change
- Assess retroactive registration (Q2 policy)
- Notify Human Gate

---

### Dimension M3: Runtime State
**What to Monitor:**
- Sandbox process health (continuous)
- Memory usage (warning >80%, alert >95%)
- Disk usage (sandbox directory only)
- CPU usage (alert if >80% sustained)
- Network connections (should be localhost only)

**Detection Method:**
- Automated: Process monitoring (ps, top, netstat)
- Trigger: Alert thresholds exceeded

**Action If Violated:**
- Log resource alert
- If memory critical: restart process
- If network anomaly: block + investigate
- Notify implementation team

---

### Dimension M4: Configuration State
**What to Monitor:**
- Config file integrity (daily)
- Config values accuracy (sandbox only)
- No production URLs (daily scan)
- No production credentials (continuous scan)
- Policy settings match Q1-Q6 decisions (daily)

**Detection Method:**
- Automated: Config validation check
- Trigger: Config change or policy mismatch

**Action If Violated:**
- Log configuration violation
- Revert to last known good config
- Notify Human Gate
- Assess need for rollback

---

### Dimension M5: Decision Ledger State
**What to Monitor:**
- Ledger integrity (hourly)
- Hash chain validity (hourly)
- No tampering detected (hourly)
- Ledger size growth (daily)
- Retroactive insertion detection (continuous)

**Detection Method:**
- Automated: Ledger hash chain verification
- Trigger: Hash chain broken → tampering detected

**Action If Violated:**
- CRITICAL: Ledger tampering detected
- Halt all bindings
- Preserve ledger for forensics
- Notify Human Gate IMMEDIATELY
- Assess need for full rollback

---

## VERIFICATION SCHEDULE

### Schedule S1: Continuous (Real-Time)
- Evidence hash validation on access
- Authority revocation checks
- Network isolation checks
- Credential leak detection

**Response Time:** < 1 second

---

### Schedule S2: Frequent (Every Hour)
- Evidence database integrity check
- Evidence file availability check
- Decision ledger hash chain validation
- Sandbox process health check

**Response Time:** < 5 minutes alert

---

### Schedule S3: Regular (Daily)
- Evidence freshness check (>1 day old?)
- Authority freshness check (>30 days old?)
- Configuration integrity check
- Q1-Q6 policy compliance check
- Retroactive insertion detection

**Response Time:** < 1 hour alert

---

### Schedule S4: Weekly
- Full state audit (all dimensions)
- Ledger integrity comprehensive check
- Sandbox resource utilization report
- Evidence provenance audit
- Authority registration audit

**Response Time:** Weekly report generation

---

## MONITORING INFRASTRUCTURE

### Infrastructure I1: Continuous Monitoring Agent
**Component:** `monitoring/continuous_verifier.py`

**Functions:**
```python
verify_evidence_state()           # Call hourly
verify_authority_state()          # Call hourly
verify_runtime_state()            # Call continuous
verify_configuration_state()      # Call daily
verify_ledger_integrity()         # Call hourly
```

**Alert Routing:** All alerts → events.db

---

### Infrastructure I2: State Dashboard
**Component:** `monitoring/state_dashboard.py`

**Displays:**
- Evidence state summary (GOOD/WARNING/CRITICAL)
- Authority state summary
- Runtime resource usage
- Configuration status
- Ledger integrity status
- Alert history (last 24 hours)

**Refresh Rate:** Real-time (every 10 seconds)

---

### Infrastructure I3: Alert System
**Component:** `monitoring/alert_manager.py`

**Alert Levels:**
- INFO: Status message (no action needed)
- WARNING: Anomaly detected (investigate)
- CRITICAL: Violation detected (immediate action)

**Alert Routing:**
```
INFO:      → events.db (logged)
WARNING:   → events.db + dashboard (visible)
CRITICAL:  → events.db + dashboard + notification
           → Human Gate alert (email/Slack TBD)
```

---

## ALERT RESPONSE PROCEDURES

### Procedure AR1: Evidence Integrity Alert
**Trigger:** Evidence hash mismatch or unavailable

**Response:**
```
1. Log evidence alert to events.db
2. Mark affected binding as UNKNOWN
3. Attempt to restore from backup
4. If restoration successful: resume binding
5. If restoration failed: escalate to Human Gate
```

---

### Procedure AR2: Authority Revocation Alert
**Trigger:** Authority marked as revoked

**Response:**
```
1. Log authority state change
2. Mark all bindings using that authority as INVALID
3. Assess retroactive registration (Q2 policy)
4. Notify Human Gate
5. Await guidance on next steps
```

---

### Procedure AR3: Configuration Violation Alert
**Trigger:** Production URL or credential detected

**Response:**
```
1. CRITICAL: Immediate shutdown
2. Log violation to events.db
3. Restore clean config from backup
4. Audit code for other violations
5. Escalate to Human Gate
```

---

### Procedure AR4: Ledger Tampering Alert
**Trigger:** Hash chain broken

**Response:**
```
1. CRITICAL: IMMEDIATE HALT
2. Preserve ledger for forensics (read-only)
3. Log tampering incident to events.db
4. Notify Human Gate IMMEDIATELY
5. Await Human Gate decision
6. Do NOT modify or restore ledger without HG approval
```

---

## VERIFICATION AUTOMATION

### Automation A1: Scheduled Verification Jobs
**Using:** Python APScheduler or similar

```python
scheduler.add_job(
    verify_evidence_state,
    'interval',
    hours=1,
    id='evidence_check'
)

scheduler.add_job(
    verify_ledger_integrity,
    'interval',
    minutes=60,
    id='ledger_check'
)

scheduler.add_job(
    verify_configuration_state,
    'interval',
    days=1,
    id='config_check'
)
```

---

### Automation A2: Event-Driven Verification
**Triggers:**
- On evidence access → validate hash
- On authority query → check revocation
- On config file change → validate immediately
- On ledger write → validate hash chain

---

## REPORTING

### Report R1: Hourly Status Report
**Generated:** Every hour

**Contents:**
- Evidence state (OK/ISSUE)
- Authority state (OK/ISSUE)
- Runtime health (OK/ISSUE)
- Configuration status (OK/ISSUE)
- Ledger integrity (OK/ISSUE)
- Alert count (last hour)

**Recipient:** Dashboard + events.db

---

### Report R2: Daily Compliance Report
**Generated:** Daily at end of day

**Contents:**
- All verifications performed (checklist)
- All alerts raised (summary)
- All incidents resolved (summary)
- Policy compliance status (Q1-Q6)
- Recommendations for next day

**Recipient:** Human Gate (if any issues)

---

### Report R3: Weekly Audit Report
**Generated:** Weekly (Friday end-of-day)

**Contents:**
- Full state audit results
- Trend analysis (is system improving/degrading?)
- Incident summary (what went wrong?)
- Evidence completeness assessment
- Authority registration audit
- Preparation for next phase

**Recipient:** Human Gate review

---

## CONTINUOUS VERIFICATION CHECKLIST

- [ ] Monitoring agent implemented (5 verification functions)
- [ ] State dashboard created
- [ ] Alert manager configured
- [ ] Alert routing to events.db
- [ ] Response procedures documented (AR1-4)
- [ ] Scheduled jobs configured (A1)
- [ ] Event-driven verifications active (A2)
- [ ] Reporting templates prepared (R1-3)
- [ ] Q5 policy (Option C: Continuous) enforced
- [ ] 24/7 monitoring capability confirmed

---

**CONTINUOUS VERIFICATION READY FOR ACTIVATION**

