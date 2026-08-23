# COMPARE Adapter Design Investigation v1.0

## Overview
Investigation of Contradiction Severity Classification system with CRITICAL level enforcement and evidence preservation chain.

Date: 2026-08-23  
Status: INVESTIGATION (design-only, no implementation)  
Scope: Contradiction detection, CRITICAL classification, evidence preservation, Human Gate integration

---

## 1. Problem Statement: Why COMPARE Adapter?

### 1.1 The Contradiction Problem
MoCKA generates multiple sources of information:
- **Signal**: External events, observations (TIC input)
- **Evidence**: Documented facts from events, records (event store)
- **Decision**: Human Gate rulings (decision ledger)
- **Authority**: Approved source-of-truth records (anchor_record.json)

**Contradiction Scenario** (Real): Impact Analysis says "A depends on B" but Dependency Map says "A does NOT depend on B" → Which is true?

**Risk**: If contradictions go undetected:
1. Decisions made on false premises
2. Audit trails become unreliable
3. Rollback strategy fails
4. System drifts from real state

### 1.2 Current State: No Systematic Contradiction Detection
**Before COMPARE Adapter**:
- Contradictions discovered: ad-hoc, human review only
- No automated detection mechanism
- No severity classification
- No escalation protocol
- Evidence often lost when contradiction resolved

**After COMPARE Adapter (design)**:
- Automated detection of common contradiction patterns
- Severity classification (CRITICAL → Human Gate escalation)
- Evidence preservation for audit
- Systematic escalation protocol

---

## 2. Contradiction Type Taxonomy

### 2.1 Evidence Layer Contradictions

**Type E1: Evidence → Evidence**
- Source A says: "Event X happened at time T"
- Source B says: "Event X happened at time T+1"
- Classification: CRITICAL (timeline integrity)

**Type E2: Evidence → Multiple Sources**
- Event logs show: "User applied patch P"
- Repository shows: "Patch P was never committed"
- Classification: CRITICAL (state integrity)

**Type E3: Evidence → Evidence Chain**
- Event A requires: Event B to have succeeded
- Event B shows: FAILED
- But Event A still shows: SUCCESS
- Classification: CRITICAL (prerequisite integrity)

### 2.2 Signal Layer Contradictions

**Type S1: TIC Signal → Current State**
- TIC Layer 1 health check: "API responding"
- TIC Layer 3 impact shows: "API marked deprecated"
- Classification: HIGH (stale information)

**Type S2: Multiple TIC Layers**
- Layer 1 (health): "System healthy"
- Layer 3 (impact): "Cascading failures detected"
- Classification: CRITICAL (assessment conflict)

### 2.3 Decision Layer Contradictions

**Type D1: Decision → Decision**
- Decision A: "Feature X approved"
- Decision B: "Feature X rejected"
- Same human gate, different judgment
- Classification: CRITICAL (judgment integrity)

**Type D2: Decision → Evidence**
- Human Gate decision: "Component Y is stable"
- Evidence shows: 47 errors in last 24h
- Classification: HIGH (premise mismatch)

### 2.4 Authority Layer Contradictions

**Type A1: Authority → Authority**
- Anchor record 1: SHA256=XXXX (sealed at 2026-08-20)
- Anchor record 2: SHA256=YYYY (sealed at 2026-08-23)
- Same system, different authoritative values
- Classification: CRITICAL (authority divergence)

### 2.5 Cross-Layer Contradictions (Most Dangerous)

**Type X1: Signal → Decision**
- Signal: "External API deprecated"
- Decision: "Continue using external API"
- Classification: CRITICAL (strategy mismatch)

**Type X2: Evidence → Authority**
- Evidence: Event log shows parameter change
- Authority: Anchor record shows no change
- Classification: CRITICAL (state divergence)

**Type X3: Signal → Authority**
- Signal: "Repository cloned with wrong branch"
- Authority: Seal assumes main branch
- Classification: CRITICAL (bootstrap integrity)

---

## 3. Contradiction Detection Mechanism

### 3.1 Detection Patterns (Rules-Based)

**Pattern E1: Timeline Contradiction**
```
IF:
  event_1.when_ts != event_2.when_ts AND
  event_1.title ≈ event_2.title (fuzzy match >80%)
THEN:
  CREATE contradiction(type=E1, severity=CRITICAL)
  PRESERVE: both event records + comparison
```

**Pattern E3: Prerequisite Violation**
```
IF:
  event.before_state requires related_event.status == "completed" AND
  related_event.status != "completed"
THEN:
  CREATE contradiction(type=E3, severity=CRITICAL)
  PRESERVE: event chain + before_state + related_event record
```

**Pattern D2: Evidence-Decision Mismatch**
```
IF:
  decision.premise contains "Component X is stable" AND
  events.WHERE(component="X" AND error_count > THRESHOLD(10 in 24h)).exists()
THEN:
  CREATE contradiction(type=D2, severity=HIGH)
  PRESERVE: decision record + last 24h events + threshold config
```

**Pattern A1: Authority Divergence**
```
IF:
  anchor_record[i].sha256 != anchor_record[j].sha256 AND
  i != j AND
  sealed_at_utc(i) < sealed_at_utc(j) <  sealed_at_utc(current)
THEN:
  CREATE contradiction(type=A1, severity=CRITICAL)
  PRESERVE: both anchor records + seal timestamps
```

### 3.2 Detection Trigger Points
**When to check for contradictions:**
1. **On Event Creation** (real-time): E1, E3, X1, X2
2. **On Decision Approval** (gating): D2, X3
3. **On Seal/Authority Update** (periodic): A1, E2
4. **On TIC Report** (30-60s intervals): S1, S2
5. **On Evidence Review** (audit phase): All types

### 3.3 Detection Scope Boundaries
**NOT** considered contradictions:
- ✗ Legitimate disagreement (design alternatives under review)
- ✗ Temporal variation (API sometimes slow, sometimes fast)
- ✗ State transitions (moving from state A→B is not contradiction)
- ✗ Incomplete information ("unknown" status is valid)

**ARE** contradictions:
- ✓ Binary incompatibility (both A and NOT A cannot be true)
- ✓ Evidence of modification without audit trail
- ✓ Authority divergence without documented resolution
- ✓ Prerequisite violations in causal chains

---

## 4. Severity Classification Model

### 4.1 Classification Levels
**CRITICAL** (Automatic escalation to Human Gate)
- Threat: Core system integrity or audit trail reliability
- Action: BLOCK until resolved by Human Gate
- Examples: Type E3, D1, A1, X2 contradictions
- Retention: PERMANENT (never auto-resolve)

**HIGH** (Alert + Human Gate review)
- Threat: Decision quality or evidence reliability degraded
- Action: Escalate, but system continues
- Examples: Type D2, S2 contradictions
- Retention: 30 days (auto-resolved if evidence updates)

**MEDIUM** (Logged + TIC monitoring)
- Threat: Drift or warning sign
- Action: Log + monitor for escalation
- Examples: Type S1 contradictions
- Retention: 7 days (auto-resolved if reconciled)

**LOW** (Diagnostic only)
- Threat: Informational
- Action: Append to TIC log (no escalation)
- Examples: Repeated observation of same state
- Retention: 1 day (automatic cleanup)

### 4.2 CRITICAL Classification Rules (Mandatory)
```
severity = CRITICAL IF any(
  type IN [E1, E3, D1, A1, X1_evidence_clear, X2, X3] OR
  (type == D2 AND evidence.recency < 1_hour) OR
  (type == S2 AND confidence > 90%) OR
  human_gate_override == MANUAL_ESCALATION
)
```

### 4.3 Why CRITICAL is Non-Negotiable
**Principle**: "Unknown is not dropped"
- If contradiction exists and severity is UNCERTAIN → classify as CRITICAL
- If contradiction unresolved after 24h → escalate to CRITICAL
- If evidence chain broken → automatically CRITICAL

**Rationale**: Better to over-escalate than to lose audit integrity

---

## 5. Evidence Preservation Chain

### 5.1 What Gets Preserved
**For EACH contradiction:**
1. **Contradiction Record**
   - contradiction_id (auto-generated)
   - type (E1, D2, etc)
   - severity (CRITICAL/HIGH/MEDIUM/LOW)
   - detected_at_utc
   - detected_by (which component)

2. **Evidence Snapshot**
   - source_1: Full record of first evidence
   - source_2: Full record of conflicting evidence
   - context: Surrounding events (±10 events)
   - calculated_field: How conflict was detected

3. **Metadata**
   - detection_method: Pattern rule that fired
   - confidence: Certainty level (0-100%)
   - related_decisions: Any decisions affected
   - resolution_status: (unresolved/escalated/resolved)

### 5.2 Storage Location
**New File**: `data/contradictions/contradiction_ledger.jsonl`
- Append-only (like decision_ledger.jsonl)
- Same integrity properties as event store
- NEVER deleted (archival requirement)
- Indexed by contradiction_id + detected_at_utc

**Schema** (JSONL format):
```json
{
  "contradiction_id": "CONT_20260823_001",
  "type": "E3",
  "severity": "CRITICAL",
  "detected_at_utc": "2026-08-23T12:34:56.789Z",
  "detected_by": "impact_analyzer.py",
  "source_event_1_id": "E20260823_111111",
  "source_event_2_id": "E20260823_222222",
  "evidence_snapshot": {
    "event_1": {...full record...},
    "event_2": {...full record...},
    "surrounding_events": [...]
  },
  "detection_method": "prerequisite_violation_rule_E3",
  "confidence": 98,
  "related_decisions": [],
  "resolution_status": "escalated",
  "escalated_to_human_gate": true,
  "escalation_id": "HG-20260823-001",
  "resolved_at_utc": null,
  "resolution_notes": null
}
```

### 5.3 Preservation Guarantees
- ✓ Once recorded, NEVER modified (append-only)
- ✓ Snapshot is CURRENT state (evidence captured at discovery)
- ✓ References are permanent (contradiction_id never reassigned)
- ✓ Retention: PERMANENT (no expiry)

---

## 6. Human Gate Integration

### 6.1 Escalation Trigger
**When CRITICAL contradiction detected:**
1. Write to contradiction_ledger.jsonl
2. Create Human Gate decision: type="contradiction_review"
3. Decision state: PENDING (awaiting human review)
4. Set timeout: 24 hours (must be resolved by then)

### 6.2 Human Gate Decision Types
**Decision Schema**:
```json
{
  "decision_id": "DC_CONT_20260823_001",
  "type": "contradiction_resolution",
  "context": "CRITICAL contradiction detected: E3 Prerequisite Violation",
  "alternatives": [
    {
      "option": "A: Accept evidence_1 as true, discard evidence_2",
      "rationale": "evidence_1 has better audit trail"
    },
    {
      "option": "B: Accept evidence_2 as true, discard evidence_1",
      "rationale": "evidence_2 is more recent"
    },
    {
      "option": "C: Treat both as valid in different contexts",
      "rationale": "no contradiction, legitimate state difference"
    }
  ],
  "decision": "Option A selected",
  "rationale": "Audit trail integrity requires accepting older source",
  "impact": "Rollback implied if based on evidence_2",
  "approved_by": "human_gate_session_xyz"
}
```

### 6.3 Consequence of Human Gate Decision
**If Option A or B** (one contradicting evidence rejected):
- Record: Which evidence was rejected and why
- Preserve: Rejected evidence (never deleted)
- Action: Update related decisions if based on false evidence

**If Option C** (no contradiction):
- Record: Context that makes both valid
- Mark: Contradiction as "resolved_no_action"
- Preserve: Analysis showing both are compatible

### 6.4 Timeout: 24-Hour Rule
**If no resolution in 24h:**
1. Human Gate escalates to escalation_authority (user config)
2. System enters HOLD state (no auto-actions based on disputed evidence)
3. Record: Timeout event + escalation_authority override
4. Continue: With alternative evidence or suspend feature

---

## 7. Integration Points

### 7.1 TIC Layer Integration
**TIC Layer 1** (health_check.py): Feeds contradictions → detects divergence  
**TIC Layer 3** (impact_analyzer.py): May trigger contradictions if impact analysis conflicts with database  
**TIC Layer 4** (Human Gate UI): Display contradiction status + decision required  

**New feature**: /api/tic/contradictions endpoint (read-only) - shows current CRITICAL contradictions

### 7.2 Orchestration Adapter Integration
**Contradiction Detection** → **Orchestration Trigger**
- When CRITICAL contradiction detected → auto-trigger "investigate_contradiction"
- Agents assigned: Claude (analysis) + Perplexity (evidence checking)
- Result: Orchestration analysis flows back to Human Gate decision

### 7.3 Disposition Mapping Integration
**Contradiction Escalation** → **Disposition Metadata**
- Contradiction marked as: disposition="investigate"
- Decision made → disposition updated: "escalate" | "resolved"
- Metadata stored: In decision_ledger.jsonl (not state machine)

### 7.4 Event Store Integration
**Contradiction Detection watches:**
- events.db (all new events)
- decision_ledger.jsonl (all decisions)
- data/tic/evaluation_queue.jsonl (TIC outputs)
- data/tic/dependency_map.json (reference changes)

**Output**: New entries in contradiction_ledger.jsonl

---

## 8. Test Strategy (Design-Only)

### 8.1 Detection Test Cases
- **test_E1_timeline**: Duplicate events with different timestamps detected
- **test_E3_prerequisite**: Prerequisite violation detected correctly
- **test_D2_evidence_mismatch**: Decision vs evidence conflict detected
- **test_A1_authority**: Authority records divergence detected

### 8.2 Severity Classification
- **test_CRITICAL_rules**: Correct rules trigger CRITICAL classification
- **test_severity_consistency**: Same contradiction always classified same severity
- **test_edge_case**: Unknown confidence → defaults to CRITICAL

### 8.3 Evidence Preservation
- **test_snapshot_integrity**: Full evidence snapshot captured
- **test_append_only**: Contradiction records never modified
- **test_traceability**: Contradiction linked to source evidence

### 8.4 Human Gate Integration
- **test_escalation_trigger**: CRITICAL contradictions escalate
- **test_decision_schema**: Decision format matches requirements
- **test_timeout_escalation**: 24h timeout triggers escalation authority

---

## 9. Outstanding Design Questions

### 9.1 Blocking Questions
1. **Detection Frequency**: How often should COMPARE scan for contradictions?
   - Real-time (expensive, might trigger cascades)
   - vs 30-60 second polling (might miss timing-sensitive contradictions)
   - Answer needed: Before implementation authorization

2. **Confidence Threshold**: What confidence level triggers CRITICAL?
   - Current proposal: >90% confidence OR >95% of evidence agreeing
   - Answer needed: Ground in actual contradiction case studies

3. **Escalation Authority**: Who decides 24h unresolved contradictions?
   - Proposal: Same authority as human_gate_admin
   - Answer needed: Before escalation implementation

### 9.2 Design Questions
1. **Contradiction Merging**: If two contradictions have overlapping evidence, are they separate?
   - Current: Separate records, linked via source evidence
   - Alternative: Merge into single "contradiction cluster"

2. **False Positive Rate**: How to measure if COMPARE creates noise?
   - Proposal: Ratio of escalated contradictions to resolved
   - Target: <5% false positive rate

---

## 10. Files Affected (Expected, Design-Only)

**New files** (implementation phase):
- data/contradictions/contradiction_ledger.jsonl (append-only log)
- interface/compare_adapter.py (detection engine)
- interface/contradiction_detector.py (pattern rules)

**Modified files** (implementation phase):
- app.py: /api/tic/contradictions endpoint (read-only)
- interface/impact_analyzer.py: Trigger contradictions if conflicts detected
- governance/human_gate_cli.py: Accept contradiction_resolution decisions

**NOT modified** (boundary enforcement):
- decision_ledger.jsonl schema (no changes)
- event store schema (no changes)
- Human Gate state machine (no changes)

---

## 11. Conclusion: Design Readiness

**Ready to Proceed to Implementation Preparation:**
- ✓ Contradiction taxonomy defined (5 layers)
- ✓ Detection mechanism designed (pattern-based)
- ✓ Severity classification rules specified
- ✓ Evidence preservation chain designed
- ✓ Human Gate integration specified
- ✓ 24-hour timeout escalation defined

**Outstanding Before Implementation Authorization:**
- [ ] Answer blocking design questions (Section 9.1)
- [ ] Validate confidence thresholds with case studies
- [ ] Confirm escalation authority assignments
- [ ] Complete Orchestration Adapter design (cross-reference)
- [ ] Complete Disposition Mapping design (cross-reference)

---

## Related Documents

- ORCHESTRATION_ADAPTER_DESIGN_INVESTIGATION.md (sibling design)
- DISPOSITION_MAPPING_DESIGN_INVESTIGATION.md (sibling design)
- interface/impact_analyzer.py (TIC Layer 3)
- data/decisions/decision_ledger.jsonl (reference)
- docs/governance/DECISION_LEDGER_SCHEMA_v1.md (schema)
