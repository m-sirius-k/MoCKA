# HG-M3 Phase 2: Binding Failure Handling
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN IN PROGRESS

---

## Core Principles

### Principle 1: UNKNOWN ≠ FALSE
- Temporary inability to verify binding does NOT mean binding is invalid
- Must distinguish between "can't determine" (UNKNOWN) and "proven false" (INVALID)
- Example: If Evidence Server is temporarily down → UNKNOWN (retry later), NOT INVALID

### Principle 2: NOT FOUND ≠ ABSENT
- Missing data could mean deletion, corruption, or normal archival
- Must preserve context when data cannot be retrieved
- Example: Old evidence moved to cold storage → NOT FOUND, but still VALID (retrieve from archive)

### Principle 3: Binding Failure → Fail Closed
- If any validation check fails, binding is BLOCKED
- No partial bindings or "mostly valid" state
- Escalate to Human Gate for remediation

### Principle 4: Audit Trail Preservation
- When binding fails, capture:
  - Which check failed and why
  - When failure detected
  - What evidence was missing/corrupted
  - Who attempted the binding
- Enable later investigation and remediation

---

## Failure Pattern 1: Evidence Missing

### Scenario
Evidence Object is referenced in Decision but cannot be found in Evidence Store.

### Root Causes
1. **Accidental Deletion** — Evidence was deleted before 5-year retention period
2. **Archive Failure** — Evidence never made it to cold storage
3. **Storage Corruption** — Evidence corrupted and marked invalid
4. **ID Mismatch** — Decision references wrong evidence_id (typo)
5. **Timing Issue** — Evidence hasn't been ingested yet

### Detection
```
Check 3 fails: evidence_store.lookup(evidence_id) returns None
```

### Handling Protocol

**Step 1: Determine Cause**
```python
def diagnose_missing_evidence(evidence_id: UUID, decision_id: UUID):
    # Check if recently deleted
    deletion_record = archive.find_deletion(evidence_id)
    if deletion_record:
        return "ACCIDENTAL_DELETION", deletion_record
    
    # Check if in cold storage
    cold_storage = archive.search_archive(evidence_id)
    if cold_storage:
        return "IN_COLD_STORAGE", cold_storage
    
    # Check if corrupted
    corruption_record = integrity_log.find_corruption(evidence_id)
    if corruption_record:
        return "STORAGE_CORRUPTION", corruption_record
    
    # Check if typo in ID
    similar_ids = evidence_store.fuzzy_match(evidence_id)
    if similar_ids:
        return "POSSIBLE_ID_TYPO", similar_ids
    
    return "UNKNOWN_REASON", None
```

**Step 2: Action by Cause**

| Cause | Action | Timeline | Result |
|-------|--------|----------|--------|
| ACCIDENTAL_DELETION | Retrieve from backup | Immediate | Retry binding validation |
| IN_COLD_STORAGE | Restore from archive | 24-48 hours | Retry binding validation |
| STORAGE_CORRUPTION | Escalate to Human Gate | Immediate | Manual investigation |
| POSSIBLE_ID_TYPO | Notify decision maker | Immediate | Correct ID and retry |
| UNKNOWN_REASON | Escalate to Human Gate | Immediate | Investigation required |

**Step 3: Fail-Closed Response**
```
Binding State: INVALID
Escalation: YES (to Human Gate)
Escalation Reason: Evidence missing, cannot verify binding
Retry Allowed: YES (after evidence recovered)
Auto-Retry: NO (requires manual intervention)
```

**Step 4: Audit Record**
```json
{
  "failure_type": "EVIDENCE_MISSING",
  "evidence_id": "...",
  "decision_id": "...",
  "detected_at": "2026-09-18T...",
  "root_cause": "ACCIDENTAL_DELETION",
  "escalation_to": "Human Gate",
  "recovery_status": "PENDING",
  "recovery_eta": "2026-09-18T..."
}
```

---

## Failure Pattern 2: Evidence Conflict

### Scenario
Evidence claims contradict each other or conflict with Decision's stated rationale.

### Root Causes
1. **Conflicting Results** — Two tests show opposite outcomes
2. **Retroactive Modification** — Evidence content changed after decision
3. **Integrity Compromise** — Evidence hash no longer matches stored version
4. **Source Dispute** — Multiple signatures claiming different origins
5. **Temporal Inconsistency** — Evidence timestamp conflicts with decision timeline

### Detection
```
Check 4 fails: evidence integrity verification returns False
OR
Check 5 fails: timestamp ordering violated (evidence created after decision)
```

### Handling Protocol

**Step 1: Identify Conflict Type**
```python
def diagnose_evidence_conflict(evidence_set: list[EvidenceObject]):
    for i, ev1 in enumerate(evidence_set):
        for ev2 in evidence_set[i+1:]:
            if contradicts(ev1, ev2):
                return "CONTRADICTORY_RESULTS", (ev1, ev2)
            if ev1.content_hash != compute_hash(ev1.payload):
                return "INTEGRITY_MISMATCH", ev1
            if ev1.timestamp > ev1.decision_reference_timestamp:
                return "RETROACTIVE_MODIFICATION", ev1
            if verify_signature(ev1.payload, ev1.source_signature) is False:
                return "SIGNATURE_INVALID", ev1
    return "NO_CONFLICT", None
```

**Step 2: Action by Conflict Type**

| Conflict Type | Action | Timeline | Result |
|---------------|--------|----------|--------|
| CONTRADICTORY_RESULTS | Require decision maker explanation | 24 hours | Amend decision or escalate |
| INTEGRITY_MISMATCH | Retrieve original from archive | Immediate | Compare versions |
| RETROACTIVE_MODIFICATION | Escalate to Human Gate | Immediate | Investigation required |
| SIGNATURE_INVALID | Verify source identity | Immediate | Re-authenticate or reject |

**Step 3: Fail-Closed Response**
```
Binding State: INVALID
Escalation: YES (always, for conflicts)
Escalation Reason: Evidence integrity or consistency issue
Retry Allowed: YES (after conflict resolved)
Auto-Retry: NO (requires decision maker input)
```

**Step 4: Conflict Resolution Record**
```json
{
  "failure_type": "EVIDENCE_CONFLICT",
  "conflict_type": "INTEGRITY_MISMATCH",
  "evidence_ids": ["...", "..."],
  "decision_id": "...",
  "detected_at": "2026-09-18T...",
  "escalation_to": "Human Gate + Decision Maker",
  "resolution_status": "PENDING",
  "resolution_deadline": "2026-09-19T..."
}
```

---

## Failure Pattern 3: Authority Missing

### Scenario
Authority Reference points to an authority that doesn't exist in Authority Registry.

### Root Causes
1. **Registry Gap** — Authority not registered at decision time
2. **Expired Registry Entry** — Authority was deleted from registry
3. **Authority ID Typo** — Decision references wrong authority_id
4. **Cross-Registry Mismatch** — Decision references authority from different system
5. **Delegation Revoked** — Authority was revoked before decision

### Detection
```
Check 2 fails: authority_registry.lookup(authority_id) returns None
```

### Handling Protocol

**Step 1: Investigate Authority**
```python
def diagnose_missing_authority(authority_id: string, decision_timestamp: ISO8601):
    # Check if ever registered
    historical = authority_registry.history.find(authority_id)
    if historical:
        return "EXPIRED_REGISTRY_ENTRY", historical
    
    # Check if typo
    similar = authority_registry.fuzzy_match(authority_id)
    if similar:
        return "POSSIBLE_TYPO", similar
    
    # Check if revoked
    revocation = authority_registry.find_revocation(authority_id, decision_timestamp)
    if revocation:
        return "REVOKED_BEFORE_DECISION", revocation
    
    return "UNKNOWN_AUTHORITY", None
```

**Step 2: Action by Cause**

| Cause | Action | Result |
|-------|--------|--------|
| EXPIRED_REGISTRY_ENTRY | Restore from historical snapshot | Verify authority was valid at decision time |
| POSSIBLE_TYPO | Notify decision maker | Correct authority_id and retry |
| REVOKED_BEFORE_DECISION | Escalate to Human Gate | Investigate unauthorized decision |
| UNKNOWN_AUTHORITY | Escalate to Human Gate | Binding cannot be verified |

**Step 3: Fail-Closed Response**
```
Binding State: INVALID
Escalation: YES (always)
Escalation Reason: Authority cannot be verified
Retry Allowed: YES (after authority found/corrected)
Auto-Retry: NO (requires manual verification)
```

**Step 4: Authority Verification Record**
```json
{
  "failure_type": "AUTHORITY_MISSING",
  "authority_id": "...",
  "decision_id": "...",
  "decision_timestamp": "2026-09-18T...",
  "detected_at": "2026-09-18T...",
  "escalation_to": "Human Gate",
  "investigation_status": "PENDING"
}
```

---

## Failure Pattern 4: Validation Failure

### Scenario
Validation Record shows validation_result = FAIL, but binding was attempted anyway.

### Root Causes
1. **Rule Violation** — Decision violated one or more validation rules
2. **Risk Threshold Exceeded** — Decision risk > authority's approval threshold
3. **Unevaluated Rules** — One or more validation rules were SKIPPED
4. **Authority Mismatch** — Authority didn't have permission for this decision domain

### Detection
```
Check 6 fails: validation_record.validation_result != PASS
```

### Handling Protocol

**Step 1: Analyze Validation Failure**
```python
def diagnose_validation_failure(validation_record: ValidationRecord):
    # Find which rule(s) failed
    failed_rules = [r for r in validation_record.rule_results if r.result == FAIL]
    
    if not validation_record.authority_valid:
        return "AUTHORITY_INVALID", validation_record
    
    if not validation_record.risk_acceptable:
        return "RISK_EXCEEDED", {
            "risk_score": validation_record.risk_score,
            "threshold": validation_record.risk_threshold,
            "delta": validation_record.risk_score - validation_record.risk_threshold
        }
    
    if failed_rules:
        return "RULE_VIOLATION", failed_rules
    
    unevaluated = [r for r in validation_record.rule_results if r.result == SKIPPED]
    if unevaluated:
        return "UNEVALUATED_RULES", unevaluated
    
    return "UNKNOWN_VALIDATION_FAILURE", None
```

**Step 2: Action by Failure Type**

| Failure Type | Action | Timeline | Result |
|--------------|--------|----------|--------|
| AUTHORITY_INVALID | Investigate authority state | Immediate | Block binding |
| RISK_EXCEEDED | Escalate to Human Gate (override needed) | Immediate | Manual approval required |
| RULE_VIOLATION | Document violation, escalate | 24 hours | Decision amendment or escalation |
| UNEVALUATED_RULES | Re-run validation with all rules | Immediate | Retry validation |

**Step 3: Fail-Closed Response**
```
Binding State: INVALID
Escalation: YES (always)
Escalation Reason: Validation rules failed
Retry Allowed: YES (after failure remedied)
Auto-Retry: NO (requires Human Gate approval for overrides)
```

**Step 4: Validation Failure Record**
```json
{
  "failure_type": "VALIDATION_FAILURE",
  "failure_reason": "RISK_EXCEEDED",
  "risk_score": 0.85,
  "risk_threshold": 0.75,
  "decision_id": "...",
  "authority_id": "...",
  "detected_at": "2026-09-18T...",
  "escalation_to": "Human Gate",
  "override_required": true,
  "override_deadline": "2026-09-19T..."
}
```

---

## Failure Pattern 5: Timestamp Conflict

### Scenario
Evidence timestamp is later than Decision timestamp, or other temporal ordering violated.

### Root Causes
1. **Clock Skew** — System clocks out of sync
2. **Retroactive Evidence** — Evidence created after decision (suspicious)
3. **Data Entry Error** — Wrong timestamp entered manually
4. **Replay Attack** — Old evidence replayed as new

### Detection
```
Check 5 fails: evidence_timestamp > decision_timestamp
```

### Handling Protocol

**Step 1: Classify Timestamp Issue**
```python
def diagnose_timestamp_conflict(evidence_ts, decision_ts, validation_ts):
    delta = abs(decision_ts - evidence_ts).total_seconds()
    
    if delta < 60:
        return "CLOCK_SKEW", delta  # less than 1 minute difference
    
    if evidence_ts > decision_ts:
        return "RETROACTIVE_EVIDENCE", delta  # evidence after decision
    
    if delta > 86400*365:  # 1 year
        return "IMPLAUSIBLE_DELAY", delta  # evidence way too old
    
    if validation_ts < decision_ts:
        return "VALIDATION_BEFORE_DECISION", delta  # validation happened before decision
    
    return "UNKNOWN_TIMESTAMP_ISSUE", delta
```

**Step 2: Action by Issue Type**

| Issue Type | Action | Timeline | Result |
|------------|--------|----------|--------|
| CLOCK_SKEW | Adjust timestamps, verify NTP | Immediate | Retry with corrected times |
| RETROACTIVE_EVIDENCE | Escalate to Human Gate (potential fraud) | Immediate | Investigation required |
| IMPLAUSIBLE_DELAY | Verify archival process (normal) | 24 hours | Accept with documentation |
| VALIDATION_BEFORE_DECISION | Escalate (temporal impossibility) | Immediate | Block binding |

**Step 3: Fail-Closed Response**
```
Binding State: INVALID (initially)
Escalation: YES (for retroactive evidence)
Escalation: NO (for clock skew/implausible delay after documentation)
Retry Allowed: YES (after correction/investigation)
Auto-Retry: YES (clock skew cases after NTP sync)
```

**Step 4: Timestamp Conflict Record**
```json
{
  "failure_type": "TIMESTAMP_CONFLICT",
  "conflict_type": "RETROACTIVE_EVIDENCE",
  "evidence_timestamp": "2026-09-19T12:00:00",
  "decision_timestamp": "2026-09-18T10:00:00",
  "delta_seconds": 86400,
  "detected_at": "2026-09-18T16:00:00",
  "escalation_to": "Human Gate",
  "investigation_status": "PENDING"
}
```

---

## Recovery and Remediation

### Recovery Flowchart

```
Binding Validation Attempted
        │
        ▼
    Check Fails
        │
        ├─→ EVIDENCE_MISSING
        │   ├─→ In Cold Storage? → Restore (24h)
        │   ├─→ Deleted? → Restore from Backup
        │   └─→ Unknown? → Escalate
        │
        ├─→ EVIDENCE_CONFLICT
        │   ├─→ Integrity Mismatch? → Compare versions
        │   ├─→ Signature Invalid? → Re-authenticate
        │   └─→ Contradictory? → Decision maker explanation
        │
        ├─→ AUTHORITY_MISSING
        │   ├─→ Expired? → Restore from history
        │   ├─→ Typo? → Correct ID
        │   └─→ Revoked? → Escalate
        │
        ├─→ VALIDATION_FAILURE
        │   ├─→ Risk Exceeded? → Human Gate override
        │   ├─→ Rule Violation? → Amend decision
        │   └─→ Rule Unevaluated? → Re-run validation
        │
        └─→ TIMESTAMP_CONFLICT
            ├─→ Clock Skew? → Sync NTP, retry
            ├─→ Retroactive? → Escalate (fraud investigation)
            └─→ Implausible? → Accept with documentation
```

### Audit Trail Requirements

For every binding failure:
1. **Record existence** in Audit Memory
2. **Root cause** documented
3. **Escalation status** (to Human Gate or not)
4. **Recovery actions** taken
5. **Resolution timestamp** when resolved

---

## Document Status

**Status:** READY FOR DECISION LEDGER RELATIONSHIP DESIGN  
**Next Step:** HG-M3-PHASE2-DECISION-LEDGER-BINDING-DESIGN-20260918.md
