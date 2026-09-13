# Open Issues Register (HG-D2 Track)
**2026-09-14**

## Document Control

- **Classification:** GOVERNANCE / HG-D2 SUPPORTING / OPEN ISSUES
- **Purpose:** Consolidated registry of all open issues from D1-D5 specifications
- **Scope:** Design-level open issues requiring Human Gate guidance
- **Status:** REGISTER COMPLETE

---

## PART 1: Issues from D1 (Persistence Architecture)

### OI-D1 Issues
**Note:** D1 establishes foundation and identifies gaps for D2-D5 work. No design-level open issues in D1 itself; all gaps are addressed through D2-D5 specifications.

---

## PART 2: Issues from D2 (Audit & Evidence Binding)

### OI-D2-01: Evidence Retention Policy

**Issue Number:** OI-D2-01  
**Category:** Operational Policy  
**Question:** How long must evidence be retained?

**Context:**
- Evidence ledger records must be persisted and queryable
- Storage requirements depend on retention period
- Impact on audit trail completeness and system cost

**Options:**
1. **Permanent Retention** — Evidence retained indefinitely
   - Pros: Complete historical audit trail, supports any future investigation
   - Cons: Unbounded storage growth, query performance degradation over time
   
2. **Fixed Period** — Evidence retained for fixed duration (e.g., 7 years, 10 years)
   - Pros: Bounded storage, aligns with common compliance periods
   - Cons: Evidence loss after period, gaps in historical lineage
   
3. **Authority-Dependent** — Retention period varies by authority/consequence type
   - Pros: Tailored retention matching governance requirement
   - Cons: Complex policy, per-type lifecycle management

**Status:** OPEN  
**Resolution Required:** Human Gate guidance  
**Related Document:** D2 Part 8  
**Impact:** Evidence ledger design, archival strategy, query optimization

---

### OI-D2-02: Consequence Type Extensibility

**Issue Number:** OI-D2-02  
**Category:** Schema Design  
**Question:** Can new consequence types be added after design?

**Context:**
- D2 Part 3 defines 5 consequence types: AUTHORIZATION_GRANTED, ACCESS_ALLOWED, STATE_CHANGED, VERIFICATION_COMPLETE, ESCALATION_TRIGGERED
- Question: Is this list exhaustive or extensible?
- Extension has authority implications (new types = scope expansion?)

**Options:**
1. **Fixed Type List** — 5 consequence types are exhaustive, no extension permitted
   - Pros: Scope boundary clearly defined, no scope expansion risk
   - Cons: System inflexible if new authorization types arise
   
2. **Extensible with HG Approval** — New types can be added only with Human Gate formal decision
   - Pros: Bounded flexibility, each extension reviewed by authority
   - Cons: Requires governance overhead per extension
   
3. **Extensible with Constraints** — New types can be added if they fit defined constraint pattern
   - Pros: Flexibility within pre-approved scope, reduces governance overhead
   - Cons: Constraint definition complex, enforcement risk

**Status:** OPEN  
**Resolution Required:** Scope governance policy  
**Related Document:** D2 Part 8  
**Impact:** Evidence schema design, authorization boundary clarity, system evolution capability

---

### OI-D2-03: Evidence Witness Authority

**Issue Number:** OI-D2-03  
**Category:** Authority Boundary  
**Question:** Who/what can generate evidence records?

**Context:**
- Evidence must be collected by authorized observers
- Question: What constitutes "authorized observer"?
- Range from: HG only → Designated observers → AI autonomous recording

**Options:**
1. **HG Only** — Only Human Gate can certify evidence records
   - Pros: Maximum authority control, no autonomous recording
   - Cons: Scalability bottleneck, governance overhead per evidence record
   
2. **Designated Observers** — Pre-approved set of observers (human or AI) can collect evidence
   - Pros: Distributed collection, defined authority set
   - Cons: Observer pre-approval process required, list maintenance
   
3. **AI Autonomous Recording** — AI can record evidence with retrospective verification possible
   - Pros: Scalable, real-time recording capability
   - Cons: Autonomy risk, authority erosion if verification not rigorous

**Status:** OPEN  
**Resolution Required:** Authority model clarification  
**Related Document:** D2 Part 8  
**Impact:** Evidence collection process design, autonomous capability boundaries, governance scope

---

## PART 3: Issues from D3 (Failure & Recovery)

### OI-D3-01: Backup Strategy

**Issue Number:** OI-D3-01  
**Category:** Systems Architecture  
**Question:** How frequently must backups be taken?

**Context:**
- D3 specifies recovery procedures but doesn't define backup frequency
- Recovery Point Objective (RPO) determines acceptable data loss
- Frequency impacts storage, cost, and recovery capability

**Options:**
1. **Continuous Backup** — Real-time or near-real-time backup (replication, streaming)
   - Pros: Minimal RPO (minutes or seconds), most current recovery possible
   - Cons: Highest infrastructure cost, synchronization complexity
   
2. **Periodic Backup** — Regular intervals (hourly, daily, weekly)
   - Pros: Predictable cost, manageable infrastructure
   - Cons: RPO bounded by interval, evidence loss between backups
   
3. **On-Demand Backup** — Backups triggered by events or manual request
   - Pros: Flexible, cost-effective
   - Cons: RPO unpredictable, recovery dependent on manual decision
   
4. **Per-Decision Backup** — Backup taken at each governance decision point
   - Pros: Aligns with authorization lifecycle, decision-specific recovery
   - Cons: Implementation complexity, variable backup frequency

**Status:** OPEN  
**Resolution Required:** Systems architecture guidance  
**Related Document:** D3 Part 8  
**Impact:** Infrastructure design, recovery time objective (RTO), data retention cost

---

### OI-D3-02: Recovery Authority

**Issue Number:** OI-D3-02  
**Category:** Authority Boundary  
**Question:** Who determines if recovered evidence is acceptable?

**Context:**
- D3 Part 2 specifies recovery procedures but leaves authority question open
- Recovery success judgment has governance implications
- Range: Automated verification → HG approval required → Hybrid approach

**Options:**
1. **Automated + Escalate on Failure** — Recovery procedures run automatically, escalate only if verification fails
   - Pros: Efficient, fail-closed escalation
   - Cons: Autonomy risk, authority erosion on routine recovery
   
2. **HG Approves All Recovery** — Every recovery, even if verification passes, requires Human Gate approval
   - Pros: Maximum authority control, governance visibility
   - Cons: Scalability bottleneck, decision overhead per recovery event
   
3. **Hybrid Approach** — Automated for minor/routine recovery, HG approval for major/authority-affecting recovery
   - Pros: Balanced efficiency and control, scaled authority involvement
   - Cons: Categorization of recovery complexity required, hybrid logic

**Status:** OPEN  
**Resolution Required:** Authority boundary decision  
**Related Document:** D3 Part 8  
**Impact:** Recovery workflow design, authority involvement scope, system responsiveness

---

## PART 4: Issues from D4 (Enforcement & Constraint)

### OI-D4-01: Conflict Resolution Policy

**Issue Number:** OI-D4-01  
**Category:** Evidence Adjudication  
**Question:** If two valid evidences conflict, which wins?

**Context:**
- D4 specifies enforcement constraints but doesn't define conflict resolution
- Example: Two verifiable evidence records show contradictory ActualConsequence states
- Resolution policy has governance implications

**Options:**
1. **Last-Write-Wins** — Most recent evidence takes precedence
   - Pros: Deterministic, simple to implement
   - Cons: May not reflect actual truth, earlier evidence preserved
   
2. **First-Write-Wins** — Original evidence takes precedence, conflicts marked DISPUTED
   - Pros: Preserves original record, explicit conflict marking
   - Cons: Later corrections difficult, state divergence risk
   
3. **Escalate to Human Gate** — Conflicts never auto-resolved, always escalated for judgment
   - Pros: Maximum authority control, no automated choice
   - Cons: Governance overhead per conflict, system throughput impact
   
4. **Evidence Quality Priority** — Higher-confidence evidence (VERIFIED > NOT_VERIFIED) wins
   - Pros: Quality-based resolution, aligns with evidence status model
   - Cons: Confidence assessment subjective, complex implementation

**Status:** OPEN  
**Resolution Required:** Governance policy  
**Related Document:** D4 Part 8  
**Impact:** Evidence model completeness, conflict handling mechanism, governance decision frequency

---

### OI-D4-02: Runtime Binding Trigger

**Issue Number:** OI-D4-02  
**Category:** Implementation Sequencing  
**Question:** At what point does runtime binding activate?

**Context:**
- D4 Part 5 defines runtime binding design but doesn't specify activation timing
- Question: When do enforcement constraints become active?
- Options: Immediate (NOT authorized) / On HG approval / Phase-based

**Options:**
1. **Immediate Activation** — Runtime binding activates upon deployment
   - Status: NOT_AUTHORIZED for HG-D2 (state lock preserved)
   - Implication: Would require implementation authorization expansion
   
2. **On HG Approval** — Separate authorization decision required to activate runtime binding
   - Pros: Decoupled implementation from enforcement, explicit authority control
   - Cons: Staged implementation complexity, deployment overhead
   
3. **Phase-Based** — Runtime binding activates at specific phase (e.g., Phase 3 after validation)
   - Pros: Staged risk management, validation gates
   - Cons: Phase definition required, complex sequencing

**Status:** OPEN  
**Resolution Required:** Depends on D5 implementation sequence  
**Related Document:** D4 Part 8  
**Impact:** Deployment strategy, authority expansion scope, implementation phasing

---

### OI-D4-03: Enforcement Audit Detail

**Issue Number:** OI-D4-03  
**Category:** Systems Design  
**Question:** How much detail in enforcement audit trail?

**Context:**
- D4 specifies enforcement audit requirements but granularity undefined
- Audit detail impacts storage, query performance, and governance visibility

**Options:**
1. **Minimal Detail** — Only failed enforcement attempts logged
   - Pros: Minimal storage, high performance
   - Cons: Limited governance visibility, no audit of successful enforcement
   
2. **Standard Detail** — All enforcement operations logged (success and failure)
   - Pros: Complete audit trail, governance visibility
   - Cons: Storage growth, query performance impact
   
3. **Detailed Logging** — All enforcement with context (who, what, when, scope, authorization reference)
   - Pros: Full governance audit trail, root cause analysis enabled
   - Cons: High storage, potential performance degradation, privacy implications

**Status:** OPEN  
**Resolution Required:** Storage and query performance trade-off  
**Related Document:** D4 Part 8  
**Impact:** Audit trail design, systems cost, query optimization strategy

---

## PART 5: Issues from D5 (Persistence Verification)

### OI-D5-01: Verification Frequency

**Issue Number:** OI-D5-01  
**Category:** Operational Policy  
**Question:** How often should verification procedures run?

**Context:**
- D5 Part 3 defines mandatory triggers but not periodic frequency
- Verification cadence impacts system resource consumption and governance assurance

**Options:**
1. **Continuous Verification** — Verification runs on every operation
   - Pros: Real-time integrity assurance, immediate anomaly detection
   - Cons: High CPU/storage overhead, query performance impact
   
2. **Daily Verification** — Scheduled daily verification run
   - Pros: Predictable cadence, manageable overhead, daily assurance
   - Cons: 24-hour anomaly detection lag, evidence degradation possible
   
3. **Weekly Verification** — Scheduled weekly verification run
   - Pros: Low overhead, weekly assurance sufficient for many governance models
   - Cons: Week-long detection lag, evidence loss possible before detection
   
4. **On-Demand Only** — Verification runs only when requested by Human Gate or anomaly detected
   - Pros: Minimal overhead, governance-driven
   - Cons: Assurance depends on HG attentiveness, no routine verification

**Status:** OPEN  
**Resolution Required:** Operational requirements  
**Related Document:** D5 Part 8  
**Impact:** Verification infrastructure cost, governance assurance level, anomaly detection lag

---

### OI-D5-02: Verification Tooling

**Issue Number:** OI-D5-02  
**Category:** Implementation  
**Question:** What tools/code would implement verification?

**Context:**
- D5 specifies verification procedures but implementation mechanisms undefined
- Tooling must support: Consequence record verification, evidence chain verification, audit trail verification, state consistency verification

**Options:**
1. **Custom Implementation** — Build verification tools from scratch
   - Pros: Tailored to HG-D2 specifics, maximum control
   - Cons: Development effort, maintenance burden, testing complexity
   
2. **Leverage Existing Tools** — Adapt existing audit/integrity tools
   - Pros: Reduced development, known reliability
   - Cons: May not fit HG-D2 model perfectly, configuration complexity
   
3. **Hybrid Approach** — Existing base + custom extensions
   - Pros: Balanced effort and customization
   - Cons: Integration complexity, maintenance of two systems

**Status:** OPEN  
**Resolution Required:** Implementation authorization (currently NOT_GRANTED)  
**Related Document:** D5 Part 8  
**Impact:** Verification mechanism design, implementation timeline, tooling dependencies

---

### OI-D5-03: Verification Authority

**Issue Number:** OI-D5-03  
**Category:** Authority Boundary  
**Question:** Who can run verification procedures?

**Context:**
- D5 specifies verification procedures but doesn't define who executes them
- Authority question impacts governance control and system autonomy

**Options:**
1. **HG Only** — Only Human Gate can initiate verification
   - Pros: Maximum authority control, no autonomous verification
   - Cons: Scalability bottleneck, governance overhead
   
2. **Designated Auditors** — Pre-approved auditor set can run verification
   - Pros: Distributed capability, defined authority, audit independence possible
   - Cons: Auditor pre-approval process, roster maintenance
   
3. **AI Autonomous** — AI can run verification procedures automatically and report results
   - Pros: Scalable, real-time verification, no HG overhead per run
   - Cons: Autonomy risk, authority erosion if reporting not rigorous, interpretation questions

**Status:** OPEN  
**Resolution Required:** Authority model clarification  
**Related Document:** D5 Part 8  
**Impact:** Verification governance, autonomous capability boundaries, reporting chain

---

## PART 6: Summary Statistics

### Open Issues by Category

| Category | Count | Documents |
|---|---|---|
| **Operational Policy** | 3 | OI-D2-01, OI-D5-01, (+ OI-D3-01 backup strategy) |
| **Schema Design** | 1 | OI-D2-02 |
| **Authority Boundary** | 3 | OI-D2-03, OI-D3-02, OI-D5-03 |
| **Systems Architecture** | 2 | OI-D3-01, OI-D4-03 |
| **Evidence Adjudication** | 1 | OI-D4-01 |
| **Implementation Sequencing** | 1 | OI-D4-02 |
| **Implementation** | 1 | OI-D5-02 |

**Total Open Issues:** 11  
**All OPEN status (requiring Human Gate guidance)**

### Open Issues by Urgency (Implicit)

**Critical for HG-D2 Decision:**
- OI-D4-02 (Runtime Binding Trigger) — affects authorization boundary
- OI-D3-02 (Recovery Authority) — affects fail-closed enforcement

**Important for Implementation Planning:**
- OI-D5-02 (Verification Tooling) — implementation authorization gates this
- OI-D5-01 (Verification Frequency) — operational design

**Important for Governance Policy:**
- OI-D2-01 (Evidence Retention Policy)
- OI-D4-01 (Conflict Resolution Policy)
- OI-D3-01 (Backup Strategy)

**Important for Authority Model:**
- OI-D2-03 (Evidence Witness Authority)
- OI-D5-03 (Verification Authority)

**Important for Schema Design:**
- OI-D2-02 (Consequence Type Extensibility)

**Deferred for Implementation Phase:**
- OI-D4-03 (Enforcement Audit Detail)

---

## PART 7: Issue Cross-References

### Issues Affecting Multiple Specifications

**Authority Boundary Issues (OI-D2-03, OI-D3-02, OI-D5-03):**
- Theme: Who decides and executes evidence collection, recovery, verification
- Cross-document impact: Evidence Binding → Recovery → Verification chain
- Resolution order: D2 (witness authority) → D3 (recovery authority) → D5 (verification authority)

**Frequency/Timing Issues (OI-D3-01, OI-D5-01, OI-D4-02):**
- Theme: Temporal cadence of operations (backup, verification, binding activation)
- Cross-document impact: Recovery → Verification → Enforcement chain
- Interdependencies: Backup frequency → Recovery RPO → Verification trigger requirements

**Policy Definition Issues (OI-D2-01, OI-D3-01, OI-D4-01, OI-D4-03):**
- Theme: Operational and governance policies undefined at design level
- Cross-document impact: Evidence persistence → Recovery strategy → Enforcement audit → Conflict handling
- Scope: All require Human Gate governance guidance, not architectural change

---

## PART 8: Closure Criteria

### When Can an Open Issue Be Closed?

**Closure Type 1: Direct HG Decision**
- Human Gate issues formal governance decision (e.g., OI-D2-01 retention policy decided as "7-year retention")
- Decision recorded in decision_ledger.jsonl
- Related specification updated if implementation authorization expands

**Closure Type 2: Implementation Realization**
- Issue resolved through implementation (e.g., OI-D5-02 tooling selected, implemented, verified)
- Implementation verified against closure criteria
- Post-implementation audit confirms issue addressed

**Closure Type 3: Supersession**
- Later specification or decision supersedes issue (e.g., OI-D4-02 if D5 implementation sequence clarifies trigger)
- Superseding decision recorded with reference to superseded issue
- Original issue marked SUPERSEDED with pointer to replacement

**No Closure Type: Assumption**
- Issues MUST NOT be closed by assumption or inference
- If evidence insufficient to close, issue remains OPEN
- Fail-closed principle: Open issues escalate, do not resolve by assumption

---

**OPEN ISSUES REGISTER COMPLETE**

11 open issues identified across D1-D5 specifications. All require Human Gate guidance or implementation authorization. No issues closed by design assumption. All issue sources documented for traceability.
