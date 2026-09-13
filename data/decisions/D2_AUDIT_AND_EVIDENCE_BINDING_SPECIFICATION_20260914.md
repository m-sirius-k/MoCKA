# D2: Audit & Evidence Binding Specification
**HG-D2 Track / 2026-09-14**

## Document Control

- **Classification:** GOVERNANCE / HG-D2 DESIGN / AUDIT & EVIDENCE BINDING
- **Authority:** HG-D2-02 (Audit & Evidence Binding Design)
- **Scope:** Formal specification of evidence-consequence-authorization binding and audit trail requirements
- **Implementation Authorization:** NOT_GRANTED
- **Status:** DESIGN SPECIFICATION COMPLETE
- **Dependency:** D1 (Persistence Architecture) - foundation established

---

## PART 1: Foundation from D1 + HG-R10

### Evidence Binding Challenge

**From HG-R10 Binding Model:**
Authorization → Scope → AuthorizedConsequence → Action → ActualConsequence → CO → Evidence → Decision → Closure

**From D1 Domain Status:**
- Domain 4 (Evidence Lineage): NOT_PROVEN - requires D2 to specify
- Domain 3 (Evidence Observations): NOT_VERIFIED - consequence-specific schema missing
- Domain 2 (Consequence Outcomes): EVIDENCE_GAP - no storage specified

**D2 Scope:**
Define how evidence binds consequences to authorizations through the governance chain.

---

## PART 2: Evidence Lineage Model

### Core Binding Definition

```
Authorization Decision
  ↓ grants authority
Scope Specification
  ↓ defines boundary
AuthorizedConsequence Specification
  ↓ expects outcome
Action Execution
  ↓ produces state change
ActualConsequence Observed
  ↓ recorded as event
Evidence Collected
  ↓ documents compliance
Consequential Outcome (CO) Classification
  ↓ COMPLIANT / VIOLATION / UNKNOWN
Governance Decision
  ↓ closure or escalation
Next Authorization
  ↓ (cycle continues)
```

### Lineage Tracking Requirements

**L1: Evidence Unit**
- Evidence ID: {type}_{consequence_id}_{timestamp}_{observer}
- Type: OBSERVATION / VERIFICATION / INFERENCE / GAP_DOCUMENTATION
- Consequence Reference: Links to ActualConsequence that evidence addresses
- Authority Reference: Which authorization is being verified
- Timestamp: When evidence was collected
- Content: What the evidence shows
- Status: VERIFIED / NOT_VERIFIED / PARTIAL / CONFLICTING

**L2: Evidence Chain**
- Chain ID: {authorization_id}_{chain_sequence}
- Start: Authorization decision
- Intermediate: Evidence points (chronologically ordered)
- End: Governance decision or escalation
- Causality: Explicit links between chain elements
- Integrity: Hash chain to detect modification

**L3: Gap Documentation**
- Gap ID: {type}_{consequence_id}_{timestamp}
- Type: EVIDENCE_GAP / VERIFICATION_BLOCKED / CONSEQUENCE_NOT_FOUND
- Expected: What evidence was sought
- Found: What evidence exists
- Status: OPEN / ESCALATED / RESOLVED (if resolved, by what evidence)

---

## PART 3: Consequence-Evidence Binding

### Consequence Types (from Binding Model)

1. **AUTHORIZATION_GRANTED**
   - Evidence: Decision ledger entry + HG signature
   - Binding: Authorization → Decision ledger
   - Verification: Signature valid + timestamp sequence correct

2. **ACCESS_ALLOWED**
   - Evidence: Action execution log + scope verification
   - Binding: Scope → events.db entry
   - Verification: Action within scope + timestamp within validity window

3. **STATE_CHANGED**
   - Evidence: State transition record + causality link
   - Binding: Action → ActualConsequence
   - Verification: State change matches authorized representation

4. **VERIFICATION_COMPLETE**
   - Evidence: Evidence collection summary + verification report
   - Binding: ActualConsequence → CO classification
   - Verification: All evidence reviewed + classification rationale documented

5. **ESCALATION_TRIGGERED**
   - Evidence: Violation detection + gap documentation
   - Binding: Compliance failure → governance decision
   - Verification: Escalation rule satisfied + notification recorded

---

## PART 4: Audit Binding Requirements

### A1: Auditability Requirement

**Specification:** Every authority-granting decision must be traceable from authorization through consequence to evidence.

**Implementation in Persistence:**

Option 1: Event Store + Evidence Ledger
- Events tagged with {authority_id, authorization_id}
- Evidence ledger entries reference events
- Query path: Authorization → Events → Evidence → Verification Report

Option 2: Consequence Ledger + Evidence Ledger
- Consequence entries include {authorization_reference, authority}
- Evidence ledger parallel to consequence ledger
- Query path: Authorization → Consequences → Evidence Chain

Option 3: Relational Schema (BLOCKED)
- Foreign keys: authorizations → consequences → evidence
- Status: CANNOT IMPLEMENT (schema modification NOT_GRANTED)

**Audit Trail Completeness:**
- Every consequence must have at least one evidence record
- Every evidence record must reference its authorization
- Every authorization must link to its consequences
- No orphaned records allowed (fail-closed enforcement)

---

## PART 5: Verification Mechanics

### V1: Lineage Verification

**Procedure:**
1. Start with Authorization decision ID
2. Retrieve all consequences associated with that authorization
3. For each consequence, retrieve all evidence records
4. Verify each evidence record's type and status
5. If any evidence status = NOT_VERIFIED, mark chain as INCOMPLETE
6. If any evidence status = CONFLICTING, mark chain as DISPUTED
7. Chain complete only if all evidence VERIFIED and classification consistent

**Fail-Closed Rule:**
- Unresolved evidence status blocks governance progression
- UNKNOWN evidence must escalate to Human Gate
- NOT_VERIFIED evidence cannot be assumed valid

### V2: Gap Detection

**Procedure:**
1. For each ActualConsequence, verify that expected evidence exists
2. If expected evidence type missing, create gap record
3. If gap record age > threshold, escalate
4. Track all gaps in persistent register

**Gap Classifications:**
- EXPECTED_NOT_FOUND: Evidence type expected but no records exist
- PARTIAL: Some evidence exists but not complete
- CONFLICTING: Evidence contradicts authorization
- UNRESOLVED: Evidence exists but verification inconclusive

---

## PART 6: Authority Boundary in Audit

### Critical Principle: Persistence ≠ Authorization

**What Evidence CANNOT Do:**
- Generate new authorization (evidence is derivative, not generative)
- Modify authorization scope (scope change requires new decision)
- Imply authorization beyond what was explicitly granted (no inference)
- Create binding outside authority's domain

**What Evidence CAN Do:**
- Document that authorization was exercised
- Show consequences that actually resulted
- Reveal compliance or violation of authorization
- Support governance decisions about closure or escalation

---

## PART 7: Evidence Classification Schema

### Status Values (Complete)

- **VERIFIED:** Evidence reviewed by authorized observer, confirmed complete
- **NOT_VERIFIED:** Evidence exists but has not been reviewed
- **PARTIAL:** Evidence incomplete, gap documented
- **CONFLICTING:** Evidence contradicts other evidence or authorization
- **EVIDENCE_GAP:** No evidence exists for expected consequence type
- **UNKNOWN:** Evidence status cannot be determined

### Handling Rules

- VERIFIED: Can support governance decisions
- NOT_VERIFIED: Cannot be used; must escalate
- PARTIAL: Partial progress noted; requires gap closure
- CONFLICTING: Escalate to Human Gate immediately
- EVIDENCE_GAP: Escalate; do not assume absence
- UNKNOWN: Escalate; do not resolve by inference

---

## PART 8: Open Issues (D2-Specific)

### OI-D2-01: Evidence Retention Policy

**Issue:** How long must evidence be retained?
- Related to: D5 (Persistence Verification)
- Impact: Storage requirements for evidence ledger
- Options: Permanent | Fixed period | Authority-dependent
- Status: OPEN - requires Human Gate guidance

### OI-D2-02: Consequence Type Extensibility

**Issue:** Can new consequence types be added after design?
- Related to: Authority boundary - new types = scope expansion?
- Impact: Whether evidence schema is fixed or evolving
- Options: Fixed type list | Extensible with HG approval | Extensible with constraints
- Status: OPEN - requires scope governance policy

### OI-D2-03: Evidence Witness Authority

**Issue:** Who/what can generate evidence records?
- Related to: Authority boundary in audit layer
- Impact: Whether only HG-approved observers can certify evidence
- Options: HG only | Designated observers | AI autonomous recording
- Status: OPEN - requires authority model clarification

---

## PART 9: Consistency Audit

**State Locks Maintained:** All 13 preserved ✓
**Track Separation:** HG-D2 ≠ HG-R08-R15 ✓
**Design Boundary:** Design ≠ Implementation ✓
**Authority Boundary:** Persistence ≠ Authorization ✓

---

## PART 10: Next Phase

**D3 (Failure & Recovery)** will specify what happens when:
- Evidence is lost or corrupted
- Audit trail is broken
- Consequence state is inconsistent

**D4 (Enforcement & Constraint)** will specify:
- How evidence binding is enforced at runtime (NOT implemented)
- How authorization scope is preserved in audit layer

---

**D2 SPECIFICATION COMPLETE — READY FOR HG-D2 REVIEW**

D2 establishes evidence-consequence-authorization binding. Three open issues require Human Gate guidance on evidence retention, consequence types, and witness authority.
