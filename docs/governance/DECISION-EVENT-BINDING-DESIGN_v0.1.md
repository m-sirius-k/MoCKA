# Decision-Event Binding Design Specification v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Design binding relationships between decisions and events; define verification mechanisms
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification defines:
- Decision-Event binding relationship model
- Binding completeness verification mechanism
- Orphaned decision detection and recovery
- Evidence chain linkage design
- Audit trail requirements

**NOT**: Implementation code, runtime modifications, production deployment

---

## Part 1: Binding Relationship Model

### Core Entities and Relationships

```
Decision
  ├─ decision_id: Unique identifier (DC_YYYYMMDD_NNN)
  ├─ timestamp: ISO 8601 UTC (decision creation time)
  ├─ maker: Authority who approved decision
  ├─ title: Decision summary
  ├─ description: Rationale
  ├─ decision: Choice selected from alternatives
  ├─ alternatives: Array of considered options
  └─ evidence_binding: Links to Event(s)

Event
  ├─ event_id: Unique identifier (E_YYYYMMDD_NNN or system-generated)
  ├─ timestamp: ISO 8601 UTC (event record time)
  ├─ title: Event summary
  ├─ tags: Array of classification tags
  │  └─ Contains: "decision_ledger,{decision_id}" for binding tag
  ├─ content: Event details
  ├─ authority: Who recorded event
  └─ binding_status: Links to Decision

Evidence
  ├─ evidence_id: Unique identifier
  ├─ location: Where evidence is stored
  ├─ hash: SHA-256 or equivalent
  ├─ timestamp: When evidence was created
  └─ binding_references: Links to Decision and Event

State Transition
  ├─ decision_id: Which decision triggered change
  ├─ event_id: Which event records the change
  ├─ before_state: Previous state
  ├─ after_state: New state
  ├─ consequence: What changed in system
  └─ timestamp: When transition occurred
```

### Binding Topology

**Binding Chain** (what must exist for complete binding):

```
Decision Created
  │
  ├─ Write to Decision Ledger (JSONL file)
  │  └─ decision_id assigned
  │  └─ timestamp recorded
  │  └─ evidence_binding field initialized
  │
  └─ Companion Event Creation Request
     ├─ POST to GATE with payload containing decision_id
     └─ GATE creates Event with tag "decision_ledger,{decision_id}"
        │
        └─ Event stored in Event Store
           │
           └─ Event carries full context:
              ├─ decision_id reference
              ├─ evidence location reference
              ├─ state consequence details
              └─ authority who approved
```

**Binding State Machine** (COMPLETE / PARTIAL / UNBOUND / UNKNOWN):

```
[START]
  │
  └─→ [UNBOUND]
       │
       ├─ Decision exists: YES
       ├─ Companion event created: NO
       ├─ Status: PARTIAL (decision waiting for event)
       │
       └─→ [COMPLETE]
            │
            ├─ Decision exists: YES
            ├─ Decision ID in Event Store found: YES
            ├─ Event carries full context: YES
            ├─ Status: COMPLETE (binding fully established)
            │
            └─ Audit Result: PASS

[UNBOUND] states:
  - Decision exists alone (no event): PARTIAL
  - Event exists alone (no decision): PARTIAL
  - Neither exists: COMPLETE (transaction rolled back successfully)
  - Both missing but audit finds reference: UNKNOWN

[ORPHANED]:
  - Decision in Ledger, no Event in Store
  - Discovered via audit
  - Requires recovery action (HG decision, auto-create event, quarantine)
```

---

## Part 2: Binding Verification Protocol

### Verification Mechanism Design

**Primary Verification: Cross-Reference Check**

```
Algorithm:
1. LOAD all decision records from Decision Ledger
   Input: decision_ledger.jsonl
   Output: decision_id set = {DC_20260901_001, DC_20260902_001, ...}

2. FOR each decision_id in set:
   a. Search Event Store for event with tag "decision_ledger,{decision_id}"
   b. IF found:
      - Binding Status: COMPLETE
      - Event ID: record event_id
      - Store in binding_audit log
   c. IF NOT found:
      - Binding Status: UNBOUND / ORPHANED
      - Record decision_id, timestamp, missing_event_id
      - Add to orphan_registry

3. OUTPUT binding_audit report:
   - Total decisions: N
   - Complete bindings: N_complete
   - Orphaned decisions: N_orphaned
   - Unresolved: N_unresolved
   - Binding completeness percentage: N_complete / N * 100%
```

**Secondary Verification: Reverse Cross-Reference**

```
Algorithm:
1. LOAD all events from Event Store with tag containing "decision_ledger"
2. FOR each event with decision_ledger tag:
   a. Extract decision_id from tag
   b. Search Decision Ledger for matching decision_id
   c. IF found:
      - Binding Status: COMPLETE (from event side)
   d. IF NOT found:
      - Orphaned Event: event exists but decision missing
      - Record event_id, decision_id reference, missing_decision
      - Add to reverse_orphan_registry

3. OUTPUT reverse_orphan_registry:
   - Events with missing decisions: flags potential data loss
   - May indicate failed rollback or partial deletion
```

**Binding Hash Verification**

```
For each complete binding (Decision + Event both exist):

1. Extract from Decision record:
   - decision_id, timestamp, maker, title, decision, rationale
   - Create decision_binding_hash = SHA-256(decision_id + timestamp + decision + rationale)

2. Extract from Event record:
   - Extract embedded decision context from event content
   - Create event_binding_hash = SHA-256(event_id + decision_id_reference + context)

3. Compare hashes:
   - IF decision_binding_hash == event_binding_hash:
     * Binding Status: VERIFIED (cryptographic proof)
   - IF decision_binding_hash != event_binding_hash:
     * Binding Status: MISMATCH (potential integrity issue)
     * Flag for manual review
     * Add to integrity_violation_registry

4. OUTPUT binding_integrity_report:
   - Total verified bindings: N_verified
   - Hash mismatches: N_mismatch
   - Unverifiable: N_unverifiable (missing hash data)
   - Integrity assurance percentage: N_verified / N_complete * 100%
```

### Verification Frequency

**Automated Verification Schedule**:
- Daily full audit: 02:00 UTC (daily snapshot)
- Hourly spot check: random sample of 100 decisions (early detection)
- Per-operation verification: immediately after mocka_decision_write (inline validation)
- On-demand: triggered by audit request or incident alert

**Verification Triggers**:
- Scheduled (daily, hourly)
- Manual request via audit tool
- Alert threshold exceeded (orphan detection > 5 decisions)
- HG reassessment preparation (comprehensive audit)
- Post-incident (data recovery validation)

---

## Part 3: Orphaned Decision Detection and Recovery

### Orphan Classification

**Type 1: Orphaned Decision** (Decision without Event)
```
Characteristics:
  - Exists in Decision Ledger: YES
  - Corresponding Event in Store: NO
  - decision_id referenced in Event tags: NOT_FOUND
  - Root cause: Event creation failed after decision write
  - Data state: Partial binding created
  - Severity: MEDIUM to HIGH (depends on decision impact)

Detection:
  - Cross-reference audit finds decision_id without event
  - Age of decision: {X days old}
  - Discovery timestamp: {audit_timestamp}

Example:
  Decision Ledger: {"decision_id": "DC_20260901_001", "title": "...", ...}
  Event Store: No event with tag "decision_ledger,DC_20260901_001"
```

**Type 2: Orphaned Event** (Event without Decision)
```
Characteristics:
  - Exists in Event Store: YES
  - Contains tag "decision_ledger,{decision_id}": YES
  - Decision record in Ledger: NO
  - Root cause: Decision rollback or deletion after event creation
  - Data state: Reverse binding broken
  - Severity: LOW to MEDIUM (event exists, can be audit trail)

Detection:
  - Reverse cross-reference finds event without decision
  - Event timestamp: {ts}
  - Discovery timestamp: {audit_timestamp}

Example:
  Event Store: {"event_id": "E_20260901_001", "tags": ["decision_ledger,DC_20260901_001"], ...}
  Decision Ledger: No record with decision_id "DC_20260901_001"
```

**Type 3: Hash Mismatch** (Binding Exists but Integrity Violation)
```
Characteristics:
  - Both Decision and Event exist: YES
  - Cross-reference finds both: YES
  - Hash verification fails: decision_binding_hash != event_binding_hash
  - Root cause: Post-creation modification (should not occur - append-only violation)
  - Data state: Binding exists but compromised
  - Severity: CRITICAL (integrity violation)

Detection:
  - Binding hash verification identifies mismatch
  - Detected decision_id: {DC_...}
  - Detected event_id: {E_...}
  - Discovery timestamp: {audit_timestamp}

Example:
  Decision Ledger: {..., decision: "Choice A", ...}  → hash_A
  Event Store: {..., embedded_decision: "Choice B", ...}  → hash_B
  Result: hash_A != hash_B → INTEGRITY_VIOLATION
```

### Recovery Procedures

**Recovery Option A: Automatic Event Creation** (for Type 1 orphans)

```
Trigger: Orphaned decision detected via audit

Procedure:
1. Retrieve orphaned decision record
   - decision_id: DC_20260901_001
   - decision_timestamp: original timestamp
   - decision_maker: original authority
   - decision content: retrieve from ledger

2. Create compensating event
   - event_type: "binding_recovery"
   - title: "Decision Binding Recovery: {decision_id}"
   - content: "System created compensating event for orphaned decision"
   - tags: ["decision_ledger,DC_20260901_001", "orphan_recovery", "system_initiated"]
   - timestamp: CURRENT (not original decision timestamp)
   - authority: "system_recovery"
   - event_status: "binding_recovered"

3. POST to GATE
   - Endpoint: /api/gate/event
   - Payload: compensating event
   - Timeout: 5s with 3 exponential backoff retries (2s, 4s, 8s)

4. Verification
   - Read back event from Event Store
   - Confirm decision_ledger tag present
   - Update orphan_registry: status = "RECOVERED"
   - Record recovery_timestamp: when binding completed

5. Audit Result
   - Orphan: RESOLVED
   - Binding: NOW COMPLETE
   - Recovery: AUTO_SYSTEM
   - Evidence: Recovery event in Event Store
```

**Recovery Option B: Human Gate Decision** (for Type 1, 2, 3 orphans)

```
Trigger: Decision needs human judgment OR integrity violation detected

Procedure:
1. Escalate to Human Gate
   - Create incident: "Orphaned Decision Requires HG Decision"
   - Include: decision_id, age, discovery_timestamp, orphan_type
   - Attach: Decision Ledger record, Event Store search results, Hash mismatch data (if applicable)

2. Human Gate Options:
   a. Accept decision: "Create compensating event for this decision"
      - Follow Option A (Auto Event Creation) with authority="human_gate_decision"
   b. Reject decision: "This decision is invalid; mark for quarantine/deletion"
      - Follow Option C (Quarantine)
   c. Investigate: "Hold decision pending investigation"
      - Follow Option D (Hold/Investigate)

3. Decision Recording
   - Record HG decision in Decision Ledger
   - Create decision: "HG Decision on Orphaned Decision {DC_20260901_001}"
   - Include: decision (accept/reject/hold), rationale, timestamp, authority
   - Create companion event for this meta-decision

4. Implementation
   - Execute action based on HG decision
   - Update orphan_registry with HG decision
   - Record recovery_timestamp and method
   - Generate recovery report
```

**Recovery Option C: Quarantine** (for Type 1, 2, 3 orphans)

```
Trigger: Decision cannot be auto-recovered; requires investigation hold

Procedure:
1. Mark Decision as Quarantined
   - In Decision Ledger: cannot modify (append-only)
   - In binding_audit: mark status = "QUARANTINED_PENDING_HG"
   - In orphan_registry: status = "QUARANTINED", quarantine_reason = "{reason}"

2. Create Quarantine Record
   - quarantine_id: QU_YYYYMMDD_NNN
   - decision_id: reference to quarantined decision
   - orphan_type: Type 1/2/3
   - discovery_timestamp: when found
   - quarantine_timestamp: when quarantined
   - quarantine_reason: "Hash mismatch" / "Orphaned > 30 days" / "Integrity violation"
   - quarantine_authority: "system_audit" or "human_gate"
   - resolution_status: "PENDING_HG_DECISION"

3. Runtime Behavior
   - Decision cannot be used for enforcement
   - Event search must flag quarantine status
   - Audit reports highlight quarantine
   - Escalation: automatic if quarantine > 14 days unresolved

4. Resolution
   - HG reviews quarantine record
   - Makes decision (accept/reject/hold longer)
   - Implementation updates binding status
   - Record in Decision Ledger: meta-decision on quarantine resolution

5. Post-Resolution
   - If accepted: move from QUARANTINED to COMPLETE/RECOVERED
   - If rejected: move from QUARANTINED to INVALID/REJECTED
   - If hold extended: update quarantine_timestamp, extend deadline
```

**Recovery Option D: Hold / Investigation** (for complex cases)

```
Trigger: Integrity violation needs investigation OR decision impact unclear

Procedure:
1. Create Investigation Record
   - investigation_id: IV_YYYYMMDD_NNN
   - decision_id: which decision to investigate
   - issue_type: "Type 2 Orphan" / "Hash Mismatch" / "Ordering Anomaly"
   - discovery_timestamp: when found
   - investigation_initiated: current timestamp
   - investigator: "system_audit" or "human_gate"

2. Investigation Scope
   - Retrieve full decision record and context
   - Retrieve all related events (both expected and unexpected)
   - Compare timestamps, authorities, content
   - Check for related decisions (dependencies, causality)
   - Examine system logs (if available) for error traces

3. Investigation Output
   - Root cause analysis: why orphan/mismatch occurred
   - Timeline: sequence of events that led to current state
   - Impact assessment: what consequences if binding incomplete
   - Recommendations: auto-recovery / HG decision / deletion

4. Escalation
   - Report findings to Human Gate
   - Provide evidence package
   - Await decision (accept recommendation OR overrule)

5. Post-Investigation
   - Implement HG decision
   - Update orphan/investigation registry
   - Record resolution in Decision Ledger
```

---

## Part 4: Audit Trail and Evidence Binding

### Audit Trail Structure

**Decision Audit Trail**:
```
For each decision record:
  decision_id: DC_20260911_001
  creation_timestamp: 2026-09-11T10:00:00Z
  maker: きむら博士
  decision_approved_timestamp: 2026-09-11T09:55:00Z
  
  audit_trail:
    - Entry 1: "Decision written to ledger" (timestamp, source)
    - Entry 2: "Companion event creation initiated" (timestamp, payload)
    - Entry 3: "Event creation completed" (timestamp, event_id)
    - Entry 4: "Binding verification: COMPLETE" (timestamp, audit_id)
    - Entry N: Any subsequent lookups, modifications to binding status
```

**Event Audit Trail** (for binding-related events):
```
For each event with "decision_ledger" tag:
  event_id: E_20260911_001
  recorded_timestamp: 2026-09-11T10:00:15Z
  authority: "system" or "human_gate"
  
  audit_trail:
    - Entry 1: "Event created in response to mocka_decision_write" (timestamp, decision_id)
    - Entry 2: "Event stored in Event Store" (timestamp, storage_location)
    - Entry 3: "Binding verification: cross-reference found decision" (timestamp, audit_id)
    - Entry 4: "Hash verification passed" (timestamp, hash_values)
    - Entry N: Recovery actions (if any), HG reviews, modifications to binding status
```

**Binding Audit Trail** (binding-specific log):
```
binding_id: BD_20260911_001
decision_id: DC_20260911_001
event_id: E_20260911_001
decision_timestamp: 2026-09-11T10:00:00Z
event_timestamp: 2026-09-11T10:00:15Z

binding_audit_log:
  - 2026-09-11T10:00:15Z: Decision written to ledger (decision_id assigned)
  - 2026-09-11T10:00:16Z: Companion event creation initiated (GATE POST)
  - 2026-09-11T10:00:17Z: Event creation returned 201 (event_id received)
  - 2026-09-11T10:00:18Z: Event stored in Event Store (storage confirmed)
  - 2026-09-11T10:00:19Z: Binding verification run (cross-reference PASS)
  - 2026-09-11T10:00:20Z: Hash verification run (verification PASS)
  - 2026-09-11T10:00:21Z: Binding status finalized (COMPLETE)
  
binding_status: COMPLETE
binding_complete_timestamp: 2026-09-11T10:00:21Z
verified_by: "audit_system_v1"
```

### Evidence Chain Linkage

**Evidence Binding Definition**:
```
Evidence is considered "BOUND" to a Decision if:

1. Chain exists:
   Decision → Event → Evidence
   (decision references event; event references evidence location)

2. Cryptographic proof exists:
   decision_id appears in event tags
   event carries decision context hash
   evidence hash matches expected value

3. Temporal proof exists:
   Decision timestamp < Event timestamp < Evidence timestamp
   (causality chain preserved)

4. Authority proof exists:
   Same authority (or authorized delegator) appears in all three
   OR delegation chain is documented

5. Audit proof exists:
   All three records appear in audit trail
   No gaps in chain
   All operations logged
```

**Evidence Location Encoding**:
```
For each Decision, evidence_binding field contains:

{
  "evidence_references": [
    {
      "evidence_id": "EV_20260911_001",
      "location": "data/decisions/decision_ledger.jsonl#DC_20260911_001",
      "type": "decision_record",
      "hash": "sha256:abc123...",
      "timestamp": "2026-09-11T10:00:00Z"
    },
    {
      "evidence_id": "EV_20260911_002",
      "location": "event_store#tag=decision_ledger,DC_20260911_001",
      "type": "companion_event",
      "hash": "sha256:def456...",
      "timestamp": "2026-09-11T10:00:15Z"
    },
    {
      "evidence_id": "EV_20260911_003",
      "location": "application_log#incident_response_log",
      "type": "system_action",
      "hash": "sha256:ghi789...",
      "timestamp": "2026-09-11T10:05:00Z"
    }
  ]
}
```

---

## Part 5: Summary and Status

**Binding Design Model Selected**: Cross-Reference Verification with Cryptographic Proof

**Key Components**:
- Decision-Event binding topology (chain structure)
- Binding state machine (COMPLETE / PARTIAL / UNBOUND / ORPHANED)
- Cross-reference verification (primary + reverse check)
- Hash-based integrity verification
- Three recovery paths (auto, human gate, quarantine)
- Complete audit trail for all binding operations
- Evidence chain linkage to preserve causality

**Verification Mechanism**:
- Daily full audit (cross-reference + hash verification)
- Hourly spot checks (random sampling)
- Per-operation inline validation (immediately after decision write)
- On-demand manual audit

**Recovery Capability**:
- Type 1 orphans (decision without event): auto-recovery via compensating event
- Type 2 orphans (event without decision): HG review required
- Type 3 violations (hash mismatch): Investigation + HG decision
- All recoveries tracked in binding audit trail

**Not Implemented Yet**: This is design only. Implementation will follow after HG review and approval.

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>
