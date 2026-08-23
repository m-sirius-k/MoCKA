# PHASE3_HUMAN_GATE_DECISION_PACKAGE
## Human Gate Authority Review & Decision Preparation

**Date**: 2026-08-23  
**Authority**: Human Gate (きむら博士)  
**Mode**: Investigation Only - Decision Candidates for Review  
**Status**: DECISION PENDING  
**Directive**: KUROKO DIRECTIVE - Human Gate Decision Package Review Phase

---

## Executive Summary

Nine blocking questions have been analyzed and formatted as formal Decision Candidates for Human Gate review. Each candidate presents:
- Alternatives with governance impact assessment
- Recommended decision with rationale
- Authority boundary verification
- Evidence preservation requirements
- Phase 2 LOCKED compatibility confirmation

**Key Principle**: All recommendations preserve Human Gate authority. Final decisions remain with human judgment, not automation.

**Next Actions for Human Gate**:
1. Review each DC_MOCKA_P3_Qx candidate
2. ACCEPT recommended candidate OR MODIFY with alternative OR REJECT
3. Record formal decision in Decision Ledger
4. Authorize implementation phase (or return to investigation)

---

# DECISION CANDIDATE MATRIX

| ID | Question | Recommended Candidate | Authority Impact | Automation Level |
|----|----------|----------------------|------------------|------------------|
| **DC_MOCKA_P3_Q1** | Agent Priority Conflict | A2: Alert Level Priority | Process ordering (not authority) | LOW |
| **DC_MOCKA_P3_Q2** | Result Storage Location | A3: Decision Ledger Integration | Schema decision (optional field) | LOW |
| **DC_MOCKA_P3_Q3** | Conflict Protocol | A2: Payload Update + Contradiction Log | Investigation trigger (not override) | LOW |
| **DC_MOCKA_P3_Q4** | Detection Frequency | B2: Polling 30-60s | Operations choice (not decision) | LOW |
| **DC_MOCKA_P3_Q5** | CRITICAL Threshold | B4: Hybrid Type+Confidence, 95% | Calibration required | MEDIUM |
| **DC_MOCKA_P3_Q6** | Timeout Authority | B2: Auto-Notify Escalation Authority | Notification (not override) | LOW |
| **DC_MOCKA_P3_Q7** | Default Disposition | C1: Auto-Assign "monitor" | Metadata default (not decision) | LOW |
| **DC_MOCKA_P3_Q8** | Assignment Timing | C1: At Approval Time | Timestamp coordination | LOW |
| **DC_MOCKA_P3_Q9** | Expiry Policy | C2: Re-Escalation Notification | Advisory notification (not override) | LOW |

---

# CATEGORY A: ORCHESTRATION GOVERNANCE DECISION CANDIDATES

---

## DC_MOCKA_P3_Q1: Agent Priority Conflict Resolution

**Question**: When COMPARE detects contradiction AND impact_analyzer detects dependency impact simultaneously, how should orchestration prioritize agent allocation?

**Context**: Multiple events may arrive simultaneously requiring orchestration. Processing order affects latency but not authority. Decision determines queue priority algorithm.

**Alternatives**:

**A1: Risk Score Priority**
- Each event has risk_score; highest score processed first
- Pros: Dynamic, reflects actual severity
- Cons: Requires risk_score calibration; may deprioritize frequent contradictions
- Authority Impact: Process ordering only
- Automation: Numerical comparison

**A2: Alert Level Priority** ← RECOMMENDED
- CRITICAL > HIGH > MEDIUM > LOW tier ordering
- Pros: Predictable, rule-based, aligns with COMPARE severity model
- Cons: Requires CRITICAL threshold defined (Q5 prerequisite)
- Authority Impact: Process ordering only (not decision authority)
- Automation: Tier classification (not AI judgment)

**A3: Human Gate Pending Count**
- Prioritize whichever type has fewer pending decisions
- Pros: Balances workload
- Cons: May create bias toward underutilized categories
- Authority Impact: Workload balancing only
- Automation: Decision count comparison

**A4: FIFO Order**
- Process in timestamp arrival order (default)
- Pros: Simple, no bias
- Cons: May delay critical items arriving later
- Authority Impact: None (first-come)
- Automation: Timestamp ordering

**Recommended Candidate**: **A2 - Alert Level Priority**

**Rationale**:
- Predictable and rule-based (system constraint, not AI discretion)
- Aligns with severity classification defined in COMPARE Adapter design
- CRITICAL contradictions receive highest priority (evidence integrity preservation)
- Allows operational tuning based on experience
- Prerequisites: Q5 (CRITICAL threshold) must be decided first

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Process ordering is operational, not authority decision |
| Evidence Preservation | ✓ MAINTAINED | All events queued (none dropped), just reordered |
| UNKNOWN Handling | ✓ VALID | Unclassified events default to MEDIUM tier |
| Phase 2 LOCKED | ✓ COMPATIBLE | No state machine impact, no decision authority change |

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q2: orchestration_results.jsonl Storage Location

**Question**: Where should orchestration results be persisted and how should storage relate to decision records?

**Context**: Orchestration AI analysis produces results that inform Human Gate decisions. Storage location affects query model, audit trail, and decision ledger coupling.

**Alternatives**:

**A1: Dedicated Directory (data/orchestration/)**
- New directory with independent JSONL file
- Pros: Isolated audit trail; independent from decisions
- Cons: Requires separate query endpoint; less tightly coupled
- Authority Impact: Independent evidence stream
- Schema: New orchestration-native schema

**A2: Event Store Integration (data/events/)**
- Extend events.db or event.jsonl with orchestration payloads
- Pros: Single event stream; unified query model
- Cons: Blurs distinction between events and results
- Authority Impact: Embedded in event stream
- Schema: Event payload extension

**A3: Decision Ledger Integration** ← RECOMMENDED
- Optional `orchestration_result` field in decision payload
- Pros: Tight coupling with decision; single source of truth
- Cons: Schema addition (but backward compatible)
- Authority Impact: Linked to decision lifetime
- Schema: decision.payload.orchestration_result (optional)

**A4: Hybrid (A1 + A3)**
- Dual write to both dedicated file and ledger
- Pros: Independent audit trail + tight coupling
- Cons: Dual write complexity, potential sync issues
- Authority Impact: Redundant storage
- Schema: Both A1 and A3 schemas

**Recommended Candidate**: **A3 - Decision Ledger Integration**

**Rationale**:
- Preserves tight semantic coupling: "orchestration informs this decision"
- Single source of truth: decision record includes all related analysis
- Backward compatible: optional field, existing records valid without it
- Query model natural: "get decision with all supporting analysis"
- Unified audit trail: decision_id links orchestration, contradiction, and decision
- Supports rollback: decision version history includes orchestration results

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Orchestration = input to decision, not decision itself |
| Evidence Preservation | ✓ APPEND-ONLY | Decision ledger is append-only; orchestration result immutable once recorded |
| Schema Integrity | ✓ BACKWARD COMPATIBLE | Optional field; existing decisions valid without orchestration_result |
| Phase 2 LOCKED | ✓ COMPATIBLE | No state machine change; decision approval logic unchanged |

**Implementation Prerequisite**:
- decision_ledger.jsonl schema addition: optional `orchestration_result` object field
- No changes to approval mechanism or decision state

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q3: Orchestration Result vs Existing Decision Conflict

**Question**: If orchestration analysis contradicts an already-APPROVED decision, how should conflict be handled?

**Context**: 
```
T1: Human Gate approves "API migration" (state=APPROVED)
T2: Orchestration investigates → Result: "Migration causes 50% service outage"
T3: Original decision vs new evidence conflict

How resolve without overriding authority?
```

**Alternatives**:

**A1: Log as Contradiction** ← PART OF RECOMMENDED
- Record in contradiction_ledger as type=X2 (Evidence-Authority divergence)
- Pros: Evidence preserved; human authority notified
- Cons: Requires contradiction system (depends on Q4-Q6)
- Authority Impact: Evidence escalation (not override)
- Process: New decision required for resolution

**A2: Update Decision Payload** ← PART OF RECOMMENDED
- Add orchestration_result to decision record
- Pros: Evidence enriches decision record
- Cons: Does not change state (APPROVED remains)
- Authority Impact: Information enrichment only
- Process: Human Gate can review and re-decide if needed

**A3: Create Parallel Decision**
- Generate new decision: "Review API migration impact"
- Pros: Clear parallel review trail
- Cons: Multiple decisions clutters ledger
- Authority Impact: Parallel review (original untouched)
- Process: Two independent decisions in timeline

**A4: Auto-Escalation** ← REJECTED
- Automatically escalate to escalation_authority for override
- Pros: Immediate escalation
- Cons: **Violates authority boundary** (auto-override)
- Authority Impact: **COMPROMISED** - implies state change
- Status: **NOT RECOMMENDED** (conflicts with Phase 2 LOCKED)

**Recommended Candidate**: **A1 + A2 Hybrid (Contradiction Logging + Payload Update)**

**Rationale**:
1. Log in contradiction_ledger (type=X2: Evidence-Authority divergence) — preserves evidence integrity
2. Add orchestration_result to decision payload — enriches decision with new analysis
3. Decision state remains APPROVED (authority preserved)
4. Human Gate receives notification: "New evidence for approved decision DC_xxx"
5. Human Gate chooses: accept decision as-is OR trigger formal review
6. If review triggered: create new decision or modify with escalation protocol
7. No automatic state change (authority remains human)

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | State machine unchanged; new evidence informs human review |
| Evidence Chain | ✓ PRESERVED | Contradiction logged + orchestration result recorded (dual trail) |
| No Auto-Override | ✓ GUARANTEED | Decision state remains APPROVED pending human judgment |
| Decision Ledger Integrity | ✓ MAINTAINED | Original decision unchanged; enriched with evidence |
| Phase 2 LOCKED | ✓ COMPATIBLE | State machine: no change (APPROVED → APPROVED or formal review) |

**Implementation Prerequisites**:
- Q4-Q6 decisions required (contradiction detection system)
- Notification system to alert Human Gate on evidence divergence
- Orchestration result storage (Q2 decision: Decision Ledger Integration)

**Workflow**:
```
1. Orchestration completes → result="high risk found"
2. Compare contradiction detection: type=X2, severity=CRITICAL
3. Log: contradiction_ledger + decision.payload.orchestration_result
4. Alert: Human Gate receives "Decision DC_xxx has new evidence"
5. Human Gate reviews evidence
6. Human chooses: (a) Accept original decision, (b) Escalate to review, (c) Override
7. If (b): Create new decision "Review API migration impact" (formal review)
8. Decision state unchanged until formal Human Gate action
```

**Human Gate Decision**: ⏳ PENDING

---

# CATEGORY B: CONTRADICTION GOVERNANCE DECISION CANDIDATES

---

## DC_MOCKA_P3_Q4: Contradiction Detection Frequency

**Question**: How often should COMPARE scan for contradictions: real-time, polling-based, or hybrid?

**Context**: Detection frequency affects latency and resource cost. Slower detection = less CPU, more delay. Faster detection = immediate escalation but higher cost. Does not change Human Gate authority.

**Alternatives**:

**B1: Real-Time (Event-Driven)**
- Detect on each event creation; immediate (<100ms latency)
- Pros: Immediate detection of contradictions
- Cons: HIGH cost (always listening); may create cascades
- Resource Impact: +20-30% baseline CPU
- Authority Impact: None (faster notification, not authority change)
- Automation: Continuous pattern matching

**B2: Polling (30-60s Interval)** ← RECOMMENDED
- Periodic watcher process scans evaluation queue
- Pros: Acceptable latency; low cost; aligns with MoCKA patterns
- Cons: Delayed detection (30-60s); batch processing
- Resource Impact: +5-10% baseline CPU (like essence_auto_updater)
- Authority Impact: None (slower notification, not authority change)
- Automation: Periodic batch detection

**B3: Hybrid**
- Real-time for CRITICAL patterns, polling for others
- Pros: Fast CRITICAL detection + low cost for others
- Cons: Complex logic; dual code paths
- Resource Impact: +10-20% baseline CPU
- Authority Impact: None (mixed notification speed)
- Automation: Pattern-specific routing

**B4: Manual Only**
- Detect only on Human Gate explicit request
- Pros: Minimal cost; human-controlled
- Cons: May miss contradictions between checks
- Resource Impact: +1-2% baseline (no automation)
- Authority Impact: None (human-initiated)
- Automation: None (on-demand)

**Recommended Candidate**: **B2 - Polling (30-60s Intervals)**

**Rationale**:
- Aligns with existing MoCKA architecture pattern (essence_auto_updater uses polling)
- Acceptable latency: 30-60s delay before escalation is operationally reasonable
- Manageable cost: +5-10% overhead vs +20-30% for real-time
- Batch processing enables pattern detection (reduces false positives)
- Allows immediate escalation on CRITICAL contradictions once detected
- Consistent with MoCKA philosophy: "System constraints, not blind trust in AI"

**Configuration**:
- Default interval: 30 seconds
- Tunable: Can adjust to 60s if cost exceeds threshold
- Backoff: Skip scan if no events in previous window

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Frequency is operational monitoring, not authority decision |
| Evidence Preservation | ✓ BATCH CAPTURE | Polling captures persistent contradictions; transient caught in batch |
| Rollback | ✓ POSSIBLE | Can disable watcher if false positive rate exceeds threshold |
| Phase 2 LOCKED | ✓ COMPATIBLE | No decision authority change; only notification latency |

**Monitoring Requirements**:
- Track detection latency (goal: <2 minutes from event to escalation)
- Monitor false positive rate (goal: <5%)
- Alert if batch size exceeds capacity (backpressure handling)

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q5: CRITICAL Severity Threshold

**Question**: What conditions trigger CRITICAL classification (requiring immediate Human Gate escalation)?

**Context**: CRITICAL classification gates escalation. Too strict = miss real issues. Too loose = false positive noise. Not an authority decision (Human Gate decides what to do with CRITICAL), but classification affects escalation volume.

**Alternatives**:

**B1: Type-Based Only**
- CRITICAL if type IN [E1, E3, D1, A1, X1, X2, X3]
- Pros: Predictable; based on known critical patterns
- Cons: May miss confidence-based contradictions
- False Positive Rate: ~3%
- Authority Impact: Type classification (not AI judgment)

**B2: Confidence-Based Only**
- CRITICAL if confidence > threshold (80%/85%/90%)
- Pros: Captures high-confidence contradictions
- Cons: Difficult to tune; many false positives if too low
- False Positive Rate: 10-30% (depends on threshold)
- Authority Impact: Confidence comparison (not AI judgment)

**B3: Evidence-Based**
- CRITICAL if evidence.count > N or evidence.recency < T
- Pros: Fresh evidence prioritized
- Cons: Hard to tune without historical data
- False Positive Rate: 5-15% (tuple-dependent)
- Authority Impact: Evidence freshness criteria

**B4: Hybrid Type + Confidence + Recency** ← RECOMMENDED
- Type-based CORE rules + confidence/recency refinement
- Pros: Known patterns + data-driven adjustments
- Cons: Requires tuning both axes
- False Positive Rate: ~5%
- Authority Impact: Multi-factor classification (not AI judgment)

**Recommended Candidate**: **B4 - Hybrid Type-Based + Confidence Checks**

**Classification Rule**:
```
severity = CRITICAL IF any(
  type IN [E1, E3, D1, A1, X1_clear, X2, X3]           # Type-based (mandatory core patterns)
  OR
  (type == D2 AND evidence.recency < 3600s)            # Evidence-decision mismatch within 1 hour
  OR
  (type == S2 AND confidence >= 95%)                   # TIC assessment conflict with >95% confidence
  OR
  human_gate_override == MANUAL_ESCALATION             # Human override capability
)
```

**Confidence Threshold**: **95%** (not 90%)
- Rationale: Reduces false positives while capturing high-confidence contradictions
- Requires: Calibration with historical case studies (must ground in data)
- Recency: <1 hour (stale evidence less critical)

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Classification is operational (noise tuning), not authority transfer |
| Confidence ≠ Authority | ✓ ENFORCED | High confidence ≠ auto-decision; CRITICAL = escalate for human judgment |
| Evidence Preservation | ✓ COMPLETE | Non-CRITICAL contradictions still logged (just not escalated immediately) |
| Tuning Capability | ✓ ENABLED | Thresholds can be recalibrated based on false positive metrics |
| Phase 2 LOCKED | ✓ COMPATIBLE | Classification affects escalation urgency, not decision authority |

**Calibration Requirement**:
1. Ground 95% confidence threshold in actual contradictions (requires case study data)
2. Monitor false positive rate (target: <5%)
3. Quarterly recalibration based on escalation analytics
4. If false positive rate >10%: escalate to Human Gate for threshold adjustment

**Prerequisites**:
- Q4 decision (detection frequency) must be decided first
- Historical contradiction data for threshold validation

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q6: 24-Hour Timeout Escalation Authority

**Question**: If a CRITICAL contradiction remains unresolved after 24 hours, who has authority to escalate or intervene?

**Context**: 
```
T0: CRITICAL contradiction detected → Human Gate decision created (state=PENDING)
T24: Still PENDING (not resolved by Human Gate yet)

Should system escalate? To whom? With what authority?
```

**Alternatives**:

**B1: Advisory Only**
- Timeout triggers notification + log entry (no action)
- Pros: Transparent (humans notified); no auto-escalation
- Cons: May be missed; no force escalation
- Authority Impact: Advisory notification only
- Automation: Logging and alerting

**B2: Auto-Notify Escalation Authority** ← RECOMMENDED
- Escalation_authority receives notification at 24h mark
- Authority reviews and decides: escalate further or provide guidance
- Pros: Active notification; authority still in control
- Cons: Requires notification system and escalation_authority definition
- Authority Impact: Authority retains full control (can dismiss)
- Automation: Notification delivery

**B3: Re-Escalate to Higher Priority Queue**
- Move to escalation queue or priority bump after 24h
- Pros: Gets higher attention at next scan
- Cons: May create queue congestion; still requires queue system
- Authority Impact: Priority change (not authority change)
- Automation: Queue reordering

**B4: Escalation Authority Override** ← REJECTED
- Escalation_authority can modify decision state automatically
- Pros: Immediate resolution capability
- Cons: **VIOLATES AUTHORITY BOUNDARY** (auto-state-change)
- Authority Impact: **COMPROMISED** - implies state machine change
- Status: **NOT RECOMMENDED** (conflicts with Phase 2 LOCKED)

**Recommended Candidate**: **B2 - Auto-Notify Escalation Authority**

**Rationale**:
- Escalation_authority = human_gate_admin (governance authority)
- Action: Send notification (email/Slack/dashboard) at 24h mark
- Authority reviews and chooses: escalate further, provide guidance, or extend timeline
- Decision state remains PENDING (human retains authority)
- Clear audit trail: notification log + authority response
- Preserves Human Gate override capability

**Implementation**:
1. At decision.created_at + 24h: trigger timeout check
2. If still PENDING: send notification to escalation_authority
3. Notification includes: decision_id, context, timeline, recommendation
4. Escalation_authority can: (a) escalate further, (b) provide guidance, (c) extend timeline, (d) dismiss
5. Decision state unchanged until formal action taken
6. Timeout clock resets if Human Gate provides substantive review

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Notification = signal; escalation_authority decides action |
| No Auto-Override | ✓ GUARANTEED | Decision state remains PENDING (human retains authority) |
| Audit Trail | ✓ CLEAR | Notification log + authority response recorded |
| Phase 2 LOCKED | ✓ COMPATIBLE | State machine unchanged (no auto-state-change) |
| Human Judgment | ✓ MAINTAINED | Authority can override notification or take alternative action |

**Escalation Authority Definition**:
- Proposed: Same as human_gate_admin (MoCKA governance authority)
- Configurable: Via MoCKA configuration or environment variable
- Notification channels: Email, Slack, dashboard alert

**Prerequisites**:
- Notification system must support delivery to escalation_authority
- Escalation_authority identity must be defined (propose: human_gate_admin)

**Human Gate Decision**: ⏳ PENDING

---

# CATEGORY C: DISPOSITION GOVERNANCE DECISION CANDIDATES

---

## DC_MOCKA_P3_Q7: Default Disposition Assignment

**Question**: When a decision is approved, should a default disposition be automatically assigned?

**Context**: Disposition is metadata guidance ("what should happen next"). Default assignment ensures all approvals have explicit semantic intent. Alternative is lazy (null until explicitly assigned).

**Alternatives**:

**C1: Auto-Assign "monitor"** ← RECOMMENDED
- All approvals automatically get disposition="monitor"
- Pros: Safe default (observation without action); complete coverage; enables orchestration
- Cons: All approvals require disposition handling (even if just monitoring)
- Coverage: 100% (no null values)
- Orchestration Trigger: Light (monitoring doesn't trigger investigation)
- Authority Impact: None (metadata assignment, not decision)

**C2: Auto-Assign "investigate"**
- All approvals automatically get disposition="investigate"
- Pros: Ensures all approvals subject to investigation
- Cons: High volume; triggers orchestration for all (CPU intensive)
- Coverage: 100%
- Orchestration Trigger: Heavy (investigation for all approvals)
- Authority Impact: None (metadata, but high orchestration impact)

**C3: No Default (Lazy)**
- disposition=null until explicitly assigned by Human Gate
- Pros: Honest about incomplete analysis; no assumptions
- Cons: Partial coverage; null values complicate queries
- Coverage: Partial (depends on assignment rate)
- Orchestration Trigger: None (until explicit assignment)
- Authority Impact: None (requires explicit action for orchestration)

**C4: Context-Dependent**
- Auto-assign based on decision type (security→"escalate", feature→"monitor", etc.)
- Pros: Tailored defaults; risk-based routing
- Cons: Complex logic; potential for automation bias
- Coverage: 100% (but rule-based)
- Orchestration Trigger: Type-dependent
- Authority Impact: Risk (automation bias in classification)

**Recommended Candidate**: **C1 - Auto-Assign disposition="monitor"**

**Rationale**:
- Safe default: "observe" is least intrusive semantic action
- Complete coverage: no null dispositions cluttering queries and dashboards
- Flexible: Human Gate can update to "investigate", "escalate", "resolve" via UI
- Lightweight: monitoring doesn't trigger resource-intensive orchestration
- Aligned with C8 decision (assignment at approval time)
- Honest baseline: acknowledges approval but requires ongoing attention
- Enables future escalation without rework

**Semantics**:
```
disposition="monitor" means:
- Decision is APPROVED
- No immediate orchestration action required
- Ongoing observation recommended
- Human Gate can update if evidence changes
```

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Authority Boundary | ✓ PRESERVED | Auto-assignment is metadata guidance, not decision |
| UNKNOWN Preservation | ✓ VALID | Can override to explicit value later if needed |
| Metadata ≠ State | ✓ ENFORCED | Disposition is payload metadata, not state machine state |
| Query Completeness | ✓ ENABLED | All records queryable by disposition (no nulls) |
| Human Override | ✓ ENABLED | Human Gate can update disposition anytime via API |

**Implementation**:
1. When decision.state = APPROVED → auto-assign disposition.value = "monitor"
2. Timestamp: same as approval timestamp
3. Reason: "Automatic default for approved decision"
4. Can be updated later via /api/decisions/disposition (Human Gate only)
5. Non-blocking: if assignment fails, decision approval succeeds (logged as incident)

**Prerequisites**:
- decision_ledger.jsonl schema: optional disposition field (from Q2)
- No changes to approval logic

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q8: Disposition Assignment Timing

**Question**: At what point in decision lifecycle is disposition assigned?

**Context**: Assignment timing affects data completeness and orchestration response time. Early = assumes action needed; Late = waits for evidence.

**Alternatives**:

**C1: At Approval Time** ← RECOMMENDED
- Same timestamp as decision approval (concurrent transaction)
- Pros: Complete coverage from T0; enables immediate orchestration
- Cons: Assumes disposition needed immediately
- Timing: decision.approved_at = disposition.assigned_at
- Orchestration: Can start immediately if disposition="investigate"
- Audit Trail: Single timestamp (approval = disposition)

**C2: At Escalation Time**
- When contradiction or evidence triggers escalation
- Pros: Lazy (waits for evidence); data-driven
- Cons: Partial coverage; gap between approval and escalation
- Timing: Two separate timestamps (approval ≠ disposition)
- Orchestration: Delayed until escalation triggered
- Audit Trail: Two timestamps (clear separation)

**C3: At Human Gate Explicit Review**
- Human Gate manually assigns via UI
- Pros: Explicit human intent; clear authority
- Cons: Requires manual action; may be incomplete
- Timing: User-determined (explicitly assigned)
- Orchestration: Only on explicit assignment
- Audit Trail: Explicit human timestamp

**C4: Context-Dependent**
- Auto-assign if risky, else lazy; rules-based routing
- Pros: Tailored timing per decision type
- Cons: Complex logic; potential automation bias
- Timing: Unpredictable (rule-based)
- Orchestration: Depends on rules
- Audit Trail: Implicit timestamps (less transparent)

**Recommended Candidate**: **C1 - At Approval Time**

**Rationale**:
- Aligned with C7 recommendation (auto-assign default="monitor")
- Concurrent assignment (same timestamp as decision)
- Enables immediate orchestration if disposition="investigate"
- Complete coverage: all records have disposition from creation
- Simpler audit trail: one timestamp per record
- Orchestration can respond immediately if needed
- Supports rollback: single concurrent transaction

**Implementation**:
1. Decision approval and disposition assignment in same transaction
2. If assignment fails: decision approval succeeds but logged as incident
3. Retry mechanism: background job retries failed assignments
4. Timestamp: decision.approved_at = disposition.assigned_at
5. Immutable once assigned (can only update via Human Gate, creates new version)

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Data Completeness | ✓ ENABLED | All records have disposition immediately (no gaps) |
| Audit Trail | ✓ UNIFIED | Single timestamp per record (approval = disposition) |
| Orchestration Speed | ✓ OPTIMIZED | Can trigger immediately if needed |
| Human Authority | ✓ PRESERVED | Disposition can be updated anytime by Human Gate |
| Phase 2 LOCKED | ✓ COMPATIBLE | No state machine changes (approval logic unchanged) |

**Prerequisites**:
- C7 decision (default disposition) must be decided first
- Coordination with decision approval process (same transaction)

**Human Gate Decision**: ⏳ PENDING

---

## DC_MOCKA_P3_Q9: Expiry Automation Policy

**Question**: What should happen when a disposition's expected_review_by date expires?

**Context**: Expected_review_by is advisory timeline for disposition review. Expiry may indicate decision needs re-evaluation. Should system escalate? Auto-upgrade disposition? Or just log?

**Alternatives**:

**C1: Advisory Only**
- Log as advisory + make visible in UI (no action)
- Pros: Transparent (visible if checked); no auto-action
- Cons: May be missed; passive only
- Automation: Logging and UI display
- Authority Impact: None (human must act if they notice)

**C2: Re-Escalation Notification** ← RECOMMENDED
- At expiry, notify escalation_authority (like Q6)
- Pros: Active notification; authority in control; clear timeline
- Cons: Requires notification system; may create alert fatigue
- Automation: Notification delivery
- Authority Impact: Authority receives signal (can dismiss)

**C3: Auto-Update Disposition**
- Automatically change disposition to "escalate" at expiry
- Pros: Immediate escalation; forces attention
- Cons: **AUTO-MODIFIES METADATA STATE** (risky)
- Automation: Automatic state upgrade
- Authority Impact: **RISK** - automation decides upgrade (less preferred)

**C4: Create Escalation Decision**
- Auto-generate new decision "Review disposition expiry"
- Pros: Formal escalation; audit trail clear
- Cons: Creates decision proliferation; formal process for timing issue
- Automation: Decision creation
- Authority Impact: Still human review (formal process)

**Recommended Candidate**: **C2 - Re-Escalation Notification**

**Rationale**:
- Expected_review_by is advisory timeline (not hard deadline)
- Expiry triggers notification to escalation_authority (same pattern as Q6)
- Authority reviews: escalate further, extend timeline, or close disposition
- Disposition state unchanged (no auto-modification)
- Preserves decision state and full human authority
- Aligned with Q6 timeout pattern (consistency)
- Notification log provides audit trail

**Implementation**:
1. Daily watcher checks disposition.expected_review_by
2. At expiry: send notification to escalation_authority
3. Notification includes: decision_id, disposition current value, timeline, recommendation
4. Escalation_authority chooses: (a) escalate, (b) extend timeline, (c) close, (d) dismiss
5. Disposition state remains unchanged until formal action
6. Notification log preserved for audit

**Governance Impact**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| No Auto-Modification | ✓ GUARANTEED | Disposition state unchanged (advisory timeline, not deadline) |
| Authority Boundary | ✓ PRESERVED | Escalation_authority decides action (not automation) |
| Audit Trail | ✓ CLEAR | Notification log + authority response recorded |
| Phase 2 LOCKED | ✓ COMPATIBLE | No state machine impact (disposition is metadata) |
| Flexibility | ✓ ENABLED | Authority can extend timeline, escalate, or dismiss as needed |

**Timeline Semantics**:
```
expected_review_by = "Human Gate should review this disposition by this date"
Expiry = "Timeline has passed, needs attention"
Action = "Escalation_authority decides if review/action/extension needed"
```

**Prerequisites**:
- Notification system for escalation_authority alerts
- Escalation_authority identity defined (propose: human_gate_admin)

**Alternative if Notification Insufficient**: 
- C4 (Create Escalation Decision): More formal; guaranteed attention
- Requires: Formal decision process overhead

**Human Gate Decision**: ⏳ PENDING

---

# GOVERNANCE IMPACT ANALYSIS

## Authority Boundary Preservation

All 9 decision candidates preserve Human Gate authority:

| DC | Automation | Authority | Human Override |
|----|-----------|-----------|-----------------|
| Q1 | Process ordering | Tier classification | Always possible via configuration |
| Q2 | Storage location | Schema design | Always possible via Decision Ledger mapping |
| Q3 | Evidence logging | Notification trigger | Always possible via Human Gate review |
| Q4 | Detection frequency | Operations tuning | Always possible via watcher enablement |
| Q5 | Threshold classification | Type+confidence rules | Always tunable via recalibration |
| Q6 | Timeout notification | Escalation authority | Always possible via authority decision |
| Q7 | Default metadata | Value assignment | Always updateable by Human Gate |
| Q8 | Timestamp coordination | Concurrent assignment | Always possible via assignment retry |
| Q9 | Expiry notification | Escalation authority | Always possible via authority decision |

**Conclusion**: ✓ Authority boundary PRESERVED across all categories

---

## Evidence Preservation Chain

All candidates maintain append-only evidence semantics:

| DC | Evidence Type | Storage | Retention | Modification |
|----|--------------|---------|-----------|--------------|
| Q1 | Queue history | Decision Ledger | Permanent | None (version history) |
| Q2 | Orchestration results | Decision payload | Permanent | None (immutable field) |
| Q3 | Contradictions + results | Both ledgers | Permanent | None (append-only) |
| Q4 | Detection events | Event log | Permanent | None (new events only) |
| Q5 | Classification rules | Code + audit log | Permanent | Threshold changes logged |
| Q6 | Timeout notifications | Event log | Permanent | None (new events only) |
| Q7 | Default assignment | Decision payload | Permanent | Only via versioning |
| Q8 | Timestamps | Decision ledger | Permanent | Immutable (created at approval) |
| Q9 | Expiry notifications | Event log | Permanent | None (new events only) |

**Conclusion**: ✓ Evidence preservation MAINTAINED across all categories

---

## UNKNOWN State Handling

Candidates preserve undefined/uncertain states where appropriate:

| DC | Undefined Allowed | Condition | Handling |
|----|------------------|-----------|----------|
| Q1 | Unclassified priority | Unknown event type | Default to MEDIUM tier |
| Q2 | N/A | Results always assigned | Schema enforces assignment |
| Q3 | Unresolved contradictions | No human judgment yet | Remains logged until resolved |
| Q4 | N/A | Frequency is operational | No undefined state |
| Q5 | Low-confidence contradictions | Confidence < threshold | Logged as non-CRITICAL (not escalated) |
| Q6 | Unnotified authority | Notification delivery fails | Retried; logged as incident |
| Q7 | N/A | All approvals get default | No undefined dispositions |
| Q8 | N/A | Concurrent assignment | Immutable once assigned |
| Q9 | N/A | Notification is advisory | Expiry doesn't force action |

**Conclusion**: ✓ UNKNOWN preservation ENABLED where appropriate

---

## Phase 2 LOCKED Compatibility

All candidates are compatible with Phase 2 LOCKED constraints:

| Constraint | Preserved | Verification |
|-----------|-----------|--------------|
| State Machine | ✓ YES | No state added; no auto-transitions |
| Decision Approval Logic | ✓ YES | Approval mechanism unchanged |
| Authority Structure | ✓ YES | Human Gate remains sole decision-maker |
| Event Schema | ✓ YES | Only optional fields added (backward compatible) |
| Historical Records | ✓ YES | All existing data remains valid |

**Conclusion**: ✓ Phase 2 LOCKED CONSTRAINT MAINTAINED across all decisions

---

# HUMAN GATE DECISION SECTION

## D1: Impact Analysis Acceptance

**Question**: Is the comprehensive Phase 3 Impact Analysis acceptable as basis for Implementation Authorization?

**Accepted Alternatives**:
- ✓ **A. ACCEPT** — Impact Analysis is complete, boundaries verified, ready for blocking question resolution
- ✗ **B. REWORK REQUIRED** — If analysis methodology requires revision
- ✗ **C. HOLD** — If additional architecture review needed before proceeding

**Current Status**: ⏳ PENDING HUMAN GATE DECISION

---

## D2: Implementation Authorization

**Question**: Should Phase 3 implementation be authorized to proceed?

**Accepted Alternatives**:
- ✓ **A. AUTHORIZED** — All 9 blocking questions answered; ready to implement
- ✓ **B. PREPARATION ONLY** — Blocking questions answered; design freeze in place; implementation deferred pending further review
- ✗ **C. BLOCKED** — If architectural concerns unresolved

**Current Status**: ⏳ PENDING HUMAN GATE DECISION

**Note**: Blocking questions must be decided before D2 decision can be finalized

---

## D3: Next Phase Direction

**Question**: What is the next actionable phase after blocking questions?

**Accepted Alternatives**:
- ✓ **A. Resolve Blocking Questions** — Answer all 9 questions; record decisions in ledger
- ✓ **B. Begin Implementation** — Only if D2 = AUTHORIZED
- ✗ **C. Return to Architecture Review** — If design requires fundamental revision

**Current Status**: ⏳ PENDING HUMAN GATE DECISION

---

# D1-D3 DECISION PREPARATION

## Blocking Questions Resolution Timeline

### Prerequisites for D1 (Impact Analysis Acceptance)
- ✓ Impact Analysis Report complete
- ✓ Governance boundaries verified
- ✓ Component impact mapped
- ✓ Runtime impact assessed
→ **Ready for D1 decision**

### Prerequisites for D2 (Implementation Authorization)
- ⏳ All 9 blocking questions answered (DC_MOCKA_P3_Q1-Q9)
- ⏳ Decision Ledger formal registration
- ⏳ Governance principal alignment confirmed
→ **Gated on Q1-Q9 resolution**

### Prerequisites for D3 (Next Phase Direction)
- ⏳ D1 decision recorded (Impact Analysis accepted/rejected)
- ⏳ D2 decision recorded (Implementation authorized/preparation/blocked)
- ⏳ Implementation boundary confirmed (if authorized)
→ **Gated on D1 and D2 decisions**

---

## Decision Sequence

**Phase 1: D1 Decision (Now)**
1. Human Gate reviews Impact Analysis Report
2. Human Gate decides: ACCEPT or REWORK or HOLD
3. Record in Decision Ledger

**Phase 2: DC_MOCKA_P3_Q1-Q9 Decisions (After D1 ACCEPT)**
1. Human Gate reviews each decision candidate
2. For each DC: ACCEPT recommendation OR MODIFY OR REJECT
3. Record 9 decisions in Decision Ledger

**Phase 3: D2 Decision (After Q1-Q9 complete)**
1. Human Gate reviews blocking question resolutions
2. Human Gate decides: AUTHORIZED or PREPARATION_ONLY or BLOCKED
3. Record in Decision Ledger

**Phase 4: D3 Decision (After D2 decision)**
1. Human Gate chooses: RESOLVE_QUESTIONS or BEGIN_IMPLEMENTATION or REVIEW_AGAIN
2. Record in Decision Ledger

---

# COMPLETION CRITERIA

- [ ] D1 decision: Impact Analysis accepted by Human Gate
- [ ] DC_MOCKA_P3_Q1-Q9 decisions: All 9 blocking questions decided and recorded
- [ ] D2 decision: Implementation authorization recorded
- [ ] D3 decision: Next phase direction recorded
- [ ] All decisions in Decision Ledger (formal registration)
- [ ] Implementation boundary fixed (or held pending further review)

---

# NEXT ACTIONS

**Awaiting Human Gate Authority**: きむら博士

**Decision Review Checklist**:
1. Review D1 (Impact Analysis Acceptance) — Ready
2. Review DC_MOCKA_P3_Q1-Q9 (9 blocking questions) — Ready
3. Decide each candidate: ACCEPT / MODIFY / REJECT
4. Review D2 (Implementation Authorization) — Gated on Q1-Q9
5. Review D3 (Next Phase) — Gated on D1-D2

**For Each Decision**:
- [ ] Candidate fully understood
- [ ] Governance impact verified
- [ ] Authority boundary preserved
- [ ] Decision made (ACCEPT/MODIFY/REJECT)
- [ ] Recorded in Decision Ledger

---

**Report Status**: READY FOR HUMAN GATE REVIEW  
**Investigation Mode**: Investigation Only (no implementation authorization)  
**Authority**: Human Gate (きむら博士)  
**Date**: 2026-08-23  

**Next Major Gate**: D1-D3 Human Gate Decisions + Decision Ledger Registration
