# Persistence Design Specification
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / DESIGN / PERSISTENCE ARCHITECTURE
* Authority: HG-R09 (AUTHORIZE PERSISTENCE DESIGN)
* Scope: Design specification only (no implementation)
* Implementation Authorization: NOT_GRANTED (see HG-R14)
* Status: DESIGN SPECIFICATION COMPLETE

---

## PART 1: Authorization Scope (HG-R09)

### Decision Mandate

- **Decision:** HG-R09 = AUTHORIZE PERSISTENCE DESIGN
- **Scope:** Formal design and specification of persistence mechanisms
- **Constraint:** Design specification only; no implementation authorization

### Design Scope (PERMITTED)

```
PERMITTED:
- Candidate comparison framework (A/B/C/D strategies)
- Selection criteria documentation
- Data model proposal
- Evidence lineage model
- Retention requirements specification
- Integrity requirements specification
- Recovery requirements specification
- Auditability requirements specification
- Migration prerequisites documentation
- Implementation preconditions specification

PROHIBITED:
- Database creation
- Schema migration
- Table creation
- Runtime persistence implementation
- Production deployment
- AI method selection (deferred to Human Gate)
```

---

## PART 2: Persistence Challenge Definition

### What Must Be Persisted

1. **Authorization Decisions**
   - Storage: decision_ledger.jsonl (IMPLEMENTED)
   - Format: Decision ID, title, context, decision, rationale, impact, alternatives
   - Scope: All HG decisions (HG-L2-01 through HG-R15)
   - Retention: Permanent (immutable append-only)

2. **Consequence Outcomes**
   - Storage: NOT_FOUND (prerequisite for persistence design)
   - Format: Consequence ID, type, compliance status, evidence chain, temporal markers
   - Scope: All ActualConsequence and AuthorizedConsequence instances
   - Retention: Design-specified (TBD)

3. **Evidence Observations**
   - Storage: events.db (SQLite, framework exists; consequence-specific NOT_FOUND)
   - Format: Event ID, timestamp, type, payload, classification
   - Scope: Execution-time evidence, investigation results, gap documentation
   - Retention: Design-specified (TBD)

4. **Evidence Lineage**
   - Storage: Design-specified in binding model; runtime implementation NOT_FOUND
   - Format: Evidence chain from consequence to decision
   - Scope: Chain linkage from action to authorization verification
   - Retention: Related to consequence retention

5. **Semantic State Progression**
   - Storage: Canonical state records (NOT_FOUND in centralized form)
   - Format: State transition history, timestamps, authority
   - Scope: Semantic Closure readiness, Implementation Authorization status
   - Retention: Governance auditability requirement

---

## PART 3: Candidate Persistence Strategies (A/B/C/D)

### Strategy A: Event Store Architecture

**Concept:**
Append-only immutable event log as system of record. All state changes represented as events. Current state derived from event replay.

**Data Model:**
```
Event Store:
  - event_id (UUID)
  - timestamp (ISO8601)
  - event_type (enum: AUTHORIZATION / CONSEQUENCE / EVIDENCE / STATE_CHANGE)
  - aggregate_id (entity being changed)
  - payload (JSON)
  - metadata (causality, authority, verification status)

Snapshots (optional):
  - snapshot_id
  - aggregate_id
  - event_version
  - state_blob
  - timestamp
```

**Characteristics:**
- Append-only: No updates or deletes
- Complete auditability: Full event history preserved
- Causality tracking: Event dependencies explicit
- State reconstruction: Derived from event replay
- Consequence linkage: Events represent consequence production

**Advantages:**
- Complete evidence trail (immutable)
- Temporal reconstruction possible
- Causality explicit
- Compliance auditing straightforward

**Disadvantages:**
- Query complexity (derived from replay)
- Storage growth (every state change recorded)
- Snapshot management required
- Need for event versioning strategy

**Suitability for Consequence Persistence:**
- HIGH: Consequence production naturally represented as events
- Design alignment: Authorization->Consequence binding maps to event causality
- Evidence lineage: Event metadata captures chain

---

### Strategy B: Decision Ledger Extension

**Concept:**
Extend existing decision_ledger.jsonl model to include consequence outcomes as structured ledger entries. Separate ledger for consequences, parallel to decision ledger.

**Data Model:**
```
Consequence Ledger Entry:
  - consequence_id (structured ID: {auth_id}_{seq}_{timestamp})
  - consequence_type (ActualConsequence | AuthorizedConsequence | CO)
  - authorization_reference (decision ID this consequence relates to)
  - consequence_representation (semantic identity, format, representation semantics)
  - causality_chain (actions that led to this consequence)
  - verification_status (FOUND | VERIFIED | PARTIAL | NOT_FOUND)
  - evidence_lineage (evidence supporting this consequence)
  - temporal_markers (creation_time, verification_time, final_state_time)
  - compliance_status (COMPLIANT | VIOLATION | UNKNOWN)
  - metadata (authority, approval, conditions)
```

**Characteristics:**
- Ledger structure (append-only, but supports structured queries)
- Parallel to decision ledger (natural alignment with governance model)
- Consequence-specific schema (semantics explicit)
- JSONL format (compatible with existing infrastructure)

**Advantages:**
- Natural alignment with existing decision ledger
- Consequence semantics explicit in schema
- Query efficiency (structured ledger vs event replay)
- Familiar format and infrastructure

**Disadvantages:**
- Less granular causality tracking than event store
- Snapshot concept doesn't apply naturally
- Temporal reconstruction limited to ledger entries
- Requires new infrastructure (consequence ledger storage)

**Suitability for Consequence Persistence:**
- HIGH: Direct consequence representation
- Design alignment: Ledger model matches governance decision model
- Query efficiency: Consequence queries straightforward

---

### Strategy C: Relational Schema

**Concept:**
Traditional SQL schema with consequence entity and related tables. Foreign keys and joins represent relationships.

**Data Model:**
```
Consequences Table:
  - consequence_id (PK)
  - consequence_type (FK -> ConsequenceTypes)
  - authorization_id (FK -> Authorizations)
  - actual_representation (JSON column)
  - compliance_status
  - created_at
  - verified_at
  - modified_at

Evidence Table:
  - evidence_id (PK)
  - consequence_id (FK -> Consequences)
  - evidence_type (FK -> EvidenceTypes)
  - evidence_content
  - verification_status
  - recorded_at

ConsequenceEvidence Linking Table:
  - consequence_id (FK)
  - evidence_id (FK)
  - linkage_type
  - confidence_level
```

**Characteristics:**
- Normalized schema (relationships explicit)
- Foreign key constraints (referential integrity)
- ACID properties (SQL guarantees)
- Full-text and complex queries supported

**Advantages:**
- Familiar relational model
- Strong constraints (referential integrity)
- Complex query support
- Transaction support (if needed)

**Disadvantages:**
- Schema evolution challenges (schema changes difficult)
- Less natural for append-only governance model
- Normalization overhead
- Consequence semantics must map to relational structure

**Suitability for Consequence Persistence:**
- MEDIUM: Workable but requires semantic mapping
- Design alignment: Relational model less natural than ledger
- Query efficiency: Good for specific queries, but not optimal for audit trail

---

### Strategy D: Hybrid (Event Store + Ledger)

**Concept:**
Combination of Event Store (detailed causality, immutability) and Decision Ledger (consequence outcomes, governance decisions). Events feed consequence ledger entries.

**Data Model:**
```
Event Store (as Strategy A):
  - Immutable append-only event log
  - All state transitions as events

Consequence Ledger (as Strategy B):
  - Summary ledger entries
  - Derived from event stream
  - Consequence outcomes explicit

Decision Ledger (existing):
  - Governance decisions (HG-*)
  - Already implemented (decision_ledger.jsonl)

Linking:
  - Decision -> Events (caused by) -> Consequences (result in) -> Evidence
```

**Characteristics:**
- Multi-tier: Events (detailed) + Ledger (summary) + Decisions (governance)
- Audit trail complete at event level
- Governance summary at ledger level
- Natural alignment with governance model

**Advantages:**
- Complete evidence trail (event store)
- Efficient governance queries (ledger)
- Familiar decision ledger infrastructure
- Flexibility for future evolution

**Disadvantages:**
- Additional complexity (multi-tier system)
- Synchronization between event store and ledger
- Storage overhead (events + ledger entries)
- Implementation effort significant

**Suitability for Consequence Persistence:**
- HIGH: Combines strengths of A and B
- Design alignment: Three-tier model supports multi-layer governance
- Query efficiency: Both detailed and summary queries supported

---

## PART 4: Comparison Matrix

| Criterion | Strategy A | Strategy B | Strategy C | Strategy D |
|-----------|-----------|-----------|-----------|-----------|
| **Auditability** | Excellent | High | Medium | Excellent |
| **Consequence Semantics** | Implicit (events) | Explicit | Mapped | Explicit |
| **Query Efficiency** | Medium | High | High | High |
| **Governance Alignment** | Medium | High | Low | Excellent |
| **Implementation Complexity** | High | Medium | Low | Very High |
| **Schema Evolution** | Good | Good | Difficult | Good |
| **Storage Efficiency** | Low (events) | Medium | Medium | Low-Medium |
| **Causality Tracking** | Excellent | Medium | Low | Excellent |
| **Temporal Reconstruction** | Excellent | Good | Medium | Excellent |
| **Existing Infrastructure** | events.db framework | decision_ledger.jsonl | schema.py | Both |
| **Evidence Lineage** | Implicit | Explicit | Mapped | Explicit |

---

## PART 5: Design Requirements (Independent of Strategy Selection)

### Persistence Requirements (ALL strategies must satisfy)

1. **Retention Requirements**
   - Consequence outcomes: Permanent retention (immutable, no deletion)
   - Evidence: Minimum retention TBD (recommend aligned with authorization decision retention)
   - Semantic state: Permanent retention (governance auditability)
   - Temporal markers: All timestamps preserved

2. **Integrity Requirements**
   - Append-only (no modification of existing entries)
   - Referential integrity (consequences link to authorizations)
   - Evidence chain integrity (lineage verifiable)
   - No orphaned records (unused consequence IDs, dangling evidence references)

3. **Recovery Requirements**
   - State reconstruction from persistence layer (from any point in time)
   - Evidence chain recovery (full lineage reproducible)
   - Causality recovery (event/decision causality derivable)
   - No single point of failure (backup/replication strategy)

4. **Auditability Requirements**
   - Complete event history accessible
   - Authority tracking (who/what caused each consequence)
   - Timestamp accuracy (temporal ordering preserved)
   - Verification status transparent (FOUND / VERIFIED / NOT_FOUND preserved)

5. **Evidence Lineage Requirements**
   - Authorization -> Consequence link preserved
   - Consequence -> Evidence chain preserved
   - Evidence -> Decision link preserved
   - Temporal causality maintained

6. **Migration Prerequisites**
   - Schema versioning (if changes needed)
   - Data migration path (old format -> new format)
   - Backward compatibility (existing data readable)
   - No data loss during migration

---

## PART 6: Implementation Preconditions

### Before Implementation (HG-R09 Design Scope)

1. **Strategy Selection**
   - Human Gate decision required (not AI selection)
   - Decision record must specify: A / B / C / D / other
   - Rationale for selection documented

2. **Schema Finalization**
   - Consequence data structure finalized
   - Evidence structure finalized
   - Linkage structure finalized
   - Versioning strategy defined

3. **Integration Planning**
   - Connection to existing decision_ledger.jsonl
   - Connection to existing events.db
   - API specification for consequence access
   - Query interface specification

4. **Testing Strategy**
   - Unit tests for persistence layer
   - Integration tests for linkage
   - Evidence lineage verification tests
   - Temporal reconstruction tests

### After Strategy Selection (Implementation Phase, NOT AUTHORIZED by HG-R09)

1. DB creation
2. Schema migration
3. Runtime persistence code
4. Evidence collection integration
5. Consequence production linkage
6. Production deployment

---

## PART 7: Open Questions for Human Gate

### Method Selection (Required Decision)

**Question 1:** Which persistence strategy (A / B / C / D / other) should be adopted?
- A: Event Store Architecture
- B: Decision Ledger Extension
- C: Relational Schema
- D: Hybrid (Event Store + Ledger)

**Question 2:** If Strategy D (Hybrid) selected, what is synchronization strategy between event store and ledger?
- Real-time (events projected to ledger immediately)
- Batch (ledger updated in batches)
- Manual (ledger updated on demand)

**Question 3:** What is minimum evidence retention period?
- Match authorization decision retention (permanent)
- Time-based (e.g., 7 years for compliance)
- Space-based (retention until storage limit)

**Question 4:** Should consequence schema support evolution (versioning)?
- Yes (schema evolution path needed)
- No (consequence structure fixed)

---

## PART 8: Design Specification Complete

### Deliverables Provided

1. Persistence Challenge Definition (4 categories of data to persist)
2. Four Candidate Strategies (A/B/C/D with detailed specifications)
3. Comparison Matrix (10 evaluation criteria)
4. Common Requirements (all strategies must satisfy)
5. Implementation Preconditions (what must happen before implementation)
6. Open Questions for Human Gate (method selection)

### Next Phase

**HG-R09 Scope Complete (Design Specification):**
- Candidate frameworks documented
- Requirements specified
- Comparison provided

**Awaiting:** Human Gate decision on method selection

**After Selection:** Implementation phase (requires separate HG-R14 authorization change for code/schema/database modifications)

---

## FINAL STATUS

**Persistence Design Specification:** COMPLETE

**Authorization Status:** Design specification authorized (HG-R09)
**Implementation Status:** NOT AUTHORIZED (requires HG-R14 change or separate decision)
**Modification Vectors:** Code=0, Schema=0, Database=0, Runtime=0 (all design-only)

**Persistence Strategy Selection:** Awaiting Human Gate decision (HG-designated authority)

---

**Specification Sealed: 2026-09-13**
**Authority: HG-R09 (AUTHORIZE PERSISTENCE DESIGN)**
**Status: DESIGN SPECIFICATION COMPLETE / AWAITING METHOD SELECTION**
