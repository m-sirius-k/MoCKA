# D1: Persistence Architecture Specification
**HG-D2 Track / 2026-09-14**

## Document Control

- **Classification:** GOVERNANCE / HG-D2 DESIGN / PERSISTENCE ARCHITECTURE
- **Authority:** HG-D2-01 (Persistence Architecture Design)
- **Scope:** Formal specification of persistence architecture requirements, constraints, and candidate approaches
- **Implementation Authorization:** NOT_GRANTED
- **Status:** DESIGN SPECIFICATION COMPLETE
- **Track Separation:** HG-D2 ≠ HG-R08-R15 / Design ≠ Implementation

---

## PART 1: Foundation Extraction from HG-R08-R15

### Existing Design Inputs

**From HG-R09 (AUTHORIZE PERSISTENCE DESIGN):**
- Persistence Challenge: 5 domains identified (Authorization Decisions, Consequence Outcomes, Evidence Observations, Evidence Lineage, Semantic State Progression)
- 4 Candidate Strategies: Event Store (A), Decision Ledger Extension (B), Relational Schema (C), Hybrid Approach (D)
- Design Scope: Specification only, no implementation
- Authorization Boundary: Design ≠ Implementation ≠ Runtime Binding

**From HG-R10 (AUTHORIZE Binding Model Design):**
- Binding Chain: Authorization → Scope → AuthorizedConsequence → Action → ActualConsequence → CO → Evidence → Decision → Closure
- Domain Status: Authorization DEFINED, Scope PROPOSED, AuthorizedConsequence DEFINED, others PROPOSED/NOT_FOUND
- Governance Principle: Persistence may preserve authority, never manufacture authority

**From HG-R08-R15 Baseline:**
- State Locks: Implementation NOT_GRANTED, M18 HOLD, Semantic Closure NOT_ACHIEVED maintained
- Modifications: Code=0, Schema=0, Database=0, Runtime=0, Production=0
- System Posture: HOLD / FAIL-CLOSED

---

## PART 2: Architecture Requirements

### Non-Functional Requirements

1. **Auditability (A1)**
   - All persistence operations must be traceable to authority
   - Evidence lineage must be preserved
   - Temporal sequence must be verifiable

2. **Integrity (A2)**
   - Append-only semantics for immutable records
   - Causality preservation (events linked to authorizations)
   - State consistency across persistence layers

3. **Fail-Closed (A3)**
   - Unverified consequences must not advance governance state
   - Evidence gaps must block progression
   - UNKNOWN must be preserved, not assumed

4. **Authority Boundary (A4)**
   - Persistence cannot exceed authorization scope
   - Consequence representation must not modify authorization semantics
   - Synchronization ≠ Authorization

5. **Scope Containment (A5)**
   - Persistence operations bounded to HG-D2 scope
   - No production deployment authorization
   - No schema/database modification authorization

6. **Observability (A6)**
   - Persistence operations must be queryable
   - Evidence must be reconstructable
   - Lineage must be traceable

---

## PART 3: Persistence Domains (Refined)

### Domain 1: Authorization Decisions

**Current State:** IMPLEMENTED (decision_ledger.jsonl)
- Storage: existing
- Format: JSONL, append-only
- Schema: Decision ID, title, context, decision, rationale, impact, alternatives
- Scope: HG decisions (HG-L2-01 through HG-R15)
- Retention: Permanent

**Gap Analysis:**
- Status: VERIFIED / COMPLETE
- Evidence: Existing ledger operational
- No additional work required for D1

---

### Domain 2: Consequence Outcomes

**Current State:** NOT_FOUND
- Storage: Required
- Format: TBD (candidates A/B/C/D)
- Schema: consequence_id, type, compliance_status, evidence_chain, temporal_markers
- Scope: ActualConsequence and AuthorizedConsequence instances
- Retention: Design-specified (TBD in D5)

**Gap Analysis:**
- Status: EVIDENCE_GAP
- Issue: No consequence-specific storage yet designed
- Work Required: D2 (Evidence Binding) must specify consequence persistence structure

---

### Domain 3: Evidence Observations

**Current State:** PARTIALLY IMPLEMENTED
- Storage: events.db (SQLite exists)
- Format: Event ID, timestamp, type, payload, classification
- Scope: Execution-time evidence, investigation results
- Retention: Design-specified (TBD in D5)

**Gap Analysis:**
- Status: NOT_VERIFIED
- Evidence: Framework exists, consequence-specific schema missing
- Work Required: D2 (Evidence Binding) must specify evidence-consequence linkage

---

### Domain 4: Evidence Lineage

**Current State:** PROPOSED (not implemented)
- Format: Evidence chain from consequence to decision
- Scope: Chain linkage from action to authorization verification
- Binding: Authorization → Consequence → Evidence → Decision

**Gap Analysis:**
- Status: NOT_PROVEN
- Constraint: Requires Domain 2 and 3 solutions first
- Work Required: D2 must define lineage structure before D4 can specify enforcement

---

### Domain 5: Semantic State Progression

**Current State:** PARTIALLY IMPLEMENTED
- Storage: Canonical state records (CANONICAL_STATE_RECORD_20260913.md exists)
- Format: State transition history, timestamps, authority
- Scope: Semantic Closure readiness, Implementation Authorization status

**Gap Analysis:**
- Status: UNKNOWN (centralized form status unclear)
- Issue: State record exists but persistence through governance cycles not specified
- Work Required: D3 (Failure & Recovery) must specify state preservation on failure

---

## PART 4: Candidate Architecture Strategies

### Strategy A: Event Store (Refined for HG-D2)

**Concept:** Append-only event log as persistence foundation
**Applicability:** Consequence production, evidence lineage, state transitions
**Alignment:** HIGH with binding model (events = consequences)
**Implementation Barrier:** Query complexity, event replay cost
**Authority Boundary:** Explicit (events tagged with grantor authority)

### Strategy B: Consequence Ledger Extension (Refined)

**Concept:** Parallel ledger to decision_ledger.jsonl for consequence outcomes
**Applicability:** Direct consequence representation, structured queries
**Alignment:** HIGH with governance model (ledger paradigm)
**Implementation Barrier:** New infrastructure (consequence ledger storage)
**Authority Boundary:** Explicit (consequences reference authorizations)

### Strategy C: Relational Schema (Refined)

**Concept:** SQL schema with consequences table, evidence table, relationships
**Applicability:** Complex queries, normalized representation
**Alignment:** MEDIUM (requires schema modification authorization)
**Implementation Barrier:** CRITICAL - requires schema modification (currently NOT_GRANTED)
**Authority Boundary:** Foreign keys explicit

### Strategy D: Hybrid Approach (New - HG-D2 Specific)

**Concept:** Event store for causality + ledger for consequence outcomes + relational for queries
**Applicability:** Auditability + query efficiency + authority preservation
**Alignment:** HIGHEST (combines A/B strengths)
**Implementation Barrier:** Synchronization between layers (eventual consistency risk)
**Authority Boundary:** Requires explicit policy on leader/follower

---

## PART 5: Scope Constraints

### What D1 Does NOT Include

- Implementation code selection
- Database schema design
- Table creation specifications
- Runtime binding design (see D4)
- Enforcement mechanism design (see D4)
- Production deployment path (see D3)

### What D1 Establishes

- Architecture options comparison
- Domain identification and status
- Gap analysis for D2-D5 work
- Authority boundary preservation rules
- Auditability requirements
- Fail-closed requirements

---

## PART 6: Consistency Audit

**State Locks Maintained:**
- Implementation Authorization = NOT_GRANTED ✓
- M18 Scope = HOLD ✓
- Semantic Closure = NOT_ACHIEVED ✓
- Code Modification = 0 ✓
- Schema Modification = 0 ✓
- Database Modification = 0 ✓
- Runtime Modification = 0 ✓
- Production Modification = 0 ✓
- System = HOLD / FAIL-CLOSED ✓
- Human Gate Authority = PRESERVED ✓

**Track Separation:**
- HG-R08-R15 (Prior Work) ≠ HG-D2 (Current Work) ✓
- HG-R09 Persistence Design (reference) ≠ D1 Architecture (specification) ✓

**Design Completeness:**
- 5 domains identified and status assessed
- 4 candidate strategies compared
- Authority boundary defined
- Gaps for D2-D5 work specified
- Next step: D2 Evidence Binding

---

## PART 7: Next Phase

**D2 (Audit & Evidence Binding) will specify:**
- Consequence-evidence linking structure
- Audit trail requirements
- Lineage preservation mechanisms
- Evidence verification criteria

**D3 (Failure & Recovery) will specify:**
- State recovery on persistence failure
- Consistency recovery procedures
- Evidence reconstruction paths

**D4 (Enforcement & Constraint) will specify:**
- Runtime persistence binding design (NOT implementation)
- Authorization scope enforcement in persistence layer
- Modification boundary enforcement

**D5 (Persistence Verification) will specify:**
- Verification procedures for persistence integrity
- Audit procedures for evidence lineage
- Recovery validation procedures

---

## DOCUMENT METADATA

- **Classification:** HG-D2 DESIGN / GOVERNANCE
- **Authority:** Formal HG-D2-01
- **Date:** 2026-09-14
- **Status:** DESIGN COMPLETE
- **Next Phase:** D2 - Audit & Evidence Binding Specification
- **Human Gate Decision:** PENDING

---

**D1 SPECIFICATION COMPLETE — READY FOR HG-D2 REVIEW**

D1 establishes architecture foundation. D2-D5 will specify detailed persistence structure, audit binding, failure recovery, enforcement, and verification.
