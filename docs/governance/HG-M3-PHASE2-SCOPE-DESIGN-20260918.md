# HG-M3 Phase 2: Scope Design
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN PREPARATION

---

## Evidence and Decision Binding Scope

Phase 2 implementation will focus on operationalizing Authority Model through 5 key components:

---

## 1. Decision Ledger

### Definition
Immutable, append-only log of all institutional decisions with cryptographic chaining.

### Scope
- **What gets logged:** All decisions affecting system state (adoption/rejection/deferral)
- **Ledger format:** JSON-LD + SHA256 chain
- **Entry fields:** decision_id, timestamp, authority, decision_type, evidence_refs, approval_chain, rationale, hash_chain
- **Storage:** SQLite + distributed backup
- **Retention:** 5-year minimum archive
- **Access:** Read-only audit trail (append-only for new entries)

### Proof Requirements (Phase 2)
- [ ] Ledger schema formally defined and validated
- [ ] Chain integrity verified (all hashes correct)
- [ ] Temporal ordering enforced (no retroactive insertion)
- [ ] Immutability tested (corruption detection)
- [ ] Audit trail completeness verified (no gaps)

### Risk Coverage
- Addresses R1.1 (Evidence Chain Integrity) — design control
- Addresses R1.3 (Revocation Enforcement) — decision preservation
- Addresses R2.3 (Evidence Destruction) — archival retention

---

## 2. Evidence Package

### Definition
Structured container binding evidence, metadata, and proof of origin to decision.

### Scope
- **Package contents:** Evidence payload + metadata wrapper + cryptographic signature
- **Metadata fields:** evidence_id, decision_ref, authority_ref, source, timestamp, content_hash, signature
- **Evidence types:** Test results, compliance records, risk assessments, audit logs, approval forms
- **Serialization:** JSON (human-readable) + binary for encryption
- **Lifecycle:** Created during decision process, sealed upon decision finalization, archived for 5 years

### Proof Requirements (Phase 2)
- [ ] Package schema defined with validation rules
- [ ] Source authentication enforced (signatures verifiable)
- [ ] Content integrity verified (hash collision detection)
- [ ] Timestamp authenticity established (tamper-proof dating)
- [ ] Lifecycle state machine implemented

### Risk Coverage
- Addresses R1.1 (Evidence Chain Integrity) — source authentication
- Addresses R1.2 (Scope Creep) — evidence bounds enforcement
- Addresses R2.3 (Evidence Destruction) — preservation mechanism

---

## 3. Authority Object Reference

### Definition
Runtime representation of authority with identity, scope, temporal bounds, and validation state.

### Scope
- **Authority data model:** id, role, grantor, grantee, scope_domain, valid_from, valid_to, revocation_condition
- **Reference format:** Opaque authority token (HMAC + encoded state)
- **Resolution:** O(1) lookup via token validation
- **State transitions:** ISSUED → ACTIVE → EXPIRED or REVOKED → ARCHIVED
- **Versioning:** Immutable snapshots, no in-place modification

### Proof Requirements (Phase 2)
- [ ] Authority object schema designed
- [ ] Token generation protocol cryptographically sound
- [ ] Token validation algorithm proven collision-free
- [ ] State machine formally verified
- [ ] Expiration enforcement tested under concurrency

### Risk Coverage
- Addresses R1.2 (Delegation Scope Creep) — token-based boundary enforcement
- Addresses R2.1 (Temporal Boundary Violations) — expiration mechanism
- Addresses R2.2 (Human Gate Availability) — proxy authority pre-delegation

---

## 4. Validation Record

### Definition
Formal proof that validation rules were applied and decision passed all checks.

### Scope
- **Rule language:** Declarative DSL (IF conditions THEN constraints)
- **Rule categories:** Authority validation, scope validation, temporal validation, evidence validation, risk threshold
- **Validation flow:** Rule evaluation → constraint check → pass/fail/escalate
- **Logging:** Each validation step recorded with rule_id, input, output, timestamp
- **Escalation:** Violations automatically escalate to Human Gate
- **Audit:** Full validation history preserved per decision

### Proof Requirements (Phase 2)
- [ ] Rule language formally specified
- [ ] Rule engine semantics proven
- [ ] Validation completeness verified (all rules evaluated)
- [ ] Escalation conditions tested
- [ ] False positive rate measured (audit)

### Risk Coverage
- Addresses R1.1 (Scope Creep prevention) — constraint enforcement
- Addresses R1.3 (Revocation enforcement) — validation gate
- Addresses R2.2 (Threshold management) — automated escalation

---

## 5. Audit Memory

### Definition
Queryable history of decision making, authority usage, evidence application, and validation outcomes.

### Scope
- **Query targets:** Decision audit trail, authority usage log, evidence application history, validation record
- **Time range:** 5 years retention
- **Access pattern:** Audit-only (read-only, tamper-apparent)
- **Query interface:** Decision_ID lookup, Authority_ID trace, Evidence trace, Time-range scan
- **Output format:** Decision + Authority + Evidence + Validation_Records triplet
- **Reporting:** Pre-built audit report templates (Authority Lifecycle, Decision Trace, Evidence Chain)

### Proof Requirements (Phase 2)
- [ ] Audit schema designed (queryability, completeness)
- [ ] Query algorithms proven O(n*log n) performance
- [ ] Tampering detection implemented (hash trees)
- [ ] Retention enforcement verified
- [ ] Reporting accuracy tested (sample audits)

### Risk Coverage
- Addresses R1.1 (Evidence integrity) — detection and reporting
- Addresses R1.3 (Revocation enforcement) — decision history trace
- Addresses R2.3 (Evidence destruction prevention) — retention monitoring

---

## Integration Model

```
[Authority Object] ──binds──> [Decision] ──binds──> [Evidence Package]
        ↓                           ↓                      ↓
   [Validation Record]      [Ledger Entry]        [Audit Memory]
        ↓                           ↓                      ↓
    ┌──────────────────────────────────────────────────────┐
    │              AUDIT MEMORY (queryable)                 │
    │  Authority Lifecycle | Decision Trace | Evidence Chain│
    └──────────────────────────────────────────────────────┘
```

---

## Phase 2 Deliverables (Scope)

| Deliverable | Type | Responsibility | Proof Requirement |
|-------------|------|-----------------|-------------------|
| Decision_Ledger_Schema.md | Design | Claude | Schema validation + chain integrity |
| Evidence_Package_Model.md | Design | Claude | Package validation + source auth |
| Authority_Object_Definition.md | Design | Claude | Token generation + validation |
| Validation_Rule_Language.md | Design | Claude | DSL specification + rule engine |
| Audit_Memory_Query_API.md | Design | Claude | Query algorithm + audit reports |
| Phase2_Integration_Tests.py | Implementation | Phase 2 | 42-point compliance test suite |
| Phase2_Performance_Analysis.md | Analysis | Claude | Load testing under concurrency |

---

## Scope Boundaries (NOT Phase 2)

**Out of Scope:**
- Runtime kernel implementation (Phase 3)
- Production deployment (Phase 4)
- Human Gate UI development (separate TODO_207)
- External system integrations (Stripe, Cloudflare, etc.)

---

## Document Status

**Status:** READY FOR HUMAN GATE REVIEW  
**Implementation:** NOT AUTHORIZED (READ ONLY)  
**Next Steps:** Proceed to AUTHORIZATION CONDITION after Human Gate approval
