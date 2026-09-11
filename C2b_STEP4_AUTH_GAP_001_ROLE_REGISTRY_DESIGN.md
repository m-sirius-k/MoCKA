# C2-b STEP 4: AUTH_GAP_001 Role Authority Registry Design

**Document Number:** EBGA-C2B-AUD-PH4-001
**Date:** 2026-09-12 09:45 UTC
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Phase:** STEP 4 — Role Authority Registry Design (Pre-Decision)

---

## Executive Summary

**GAP #1 Requirement:** Design a comprehensive role authority registry that defines role identity, capabilities, authority levels, decision rights, execution rights, and escalation procedures for all system roles.

**Current State:** Roles mentioned implicitly in codebase (KUROKO Monitor, GL7 Kernel, Event Validator, Integrity Engine, etc.) but no formal registry exists.

**Design Status:** COMPLETE (3 candidate registries designed; ready for Human Gate decision)

**Design Authority:** Implementation Authorization (pre-decision phase)

**Implementation Authority:** Requires Human Gate Decision on which candidate registry to adopt

---

## Role Authority Design Framework

### 4.1 Role Authority Attributes

Each role requires 8 attributes to fully specify authority:

| Attribute | Definition | Examples |
|---|---|---|
| **D-1: Role Identity** | Unique identifier + canonical name | HUMAN_AUTHORITY, KUROKO_MONITOR |
| **D-2: Description** | Purpose and responsibility summary | "Human decision authority for authorization gates" |
| **D-3: Capabilities** | Specific operations the role can perform | APPROVE_DECISION, WRITE_EVENT, AUDIT_INTEGRITY |
| **D-4: Authority Level** | Rank in decision hierarchy | SUPREME (all decisions), MAJOR (implementation), MINOR (audit only) |
| **D-5: Scope** | Which components/operations this role covers | Authorization decisions, event validation, integrity verification |
| **D-6: Decision Rights** | Who decides on actions this role proposes | HUMAN_AUTHORITY decides on proposals from KUROKO |
| **D-7: Execution Rights** | Who actually executes what the role decides | KUROKO executes design; HUMAN_AUTHORITY executes policy decisions |
| **D-8: Escalation Procedure** | How to handle conflicts, appeals, or deadlocks | Escalation to Human Gate, retry limits, timeout behavior |

---

## Role Analysis from Codebase

### 4.2 Roles Identified

**From phi_os/runtime/authority_manager.py:**
- AuthorityType.GATE (Gate Authority)
- AuthorityType.EVENT (Event Authority)
- AuthorityType.KNOWLEDGE (Knowledge Authority)
- AuthorityType.VERSION (Version Authority)
- AuthorityType.VERIFICATION (Verification Authority)
- AuthorityType.INSTITUTION (Institution Authority)

**From structural/execution_governance.py:**
- GL7 Execution Kernel (gate execution control)
- Repository Grounding Engine (state verification)

**From phi_os/event_gate.py:**
- Event Validator (payload validation)
- Integrity Signer (hash chain creation)
- Gate Policy Enforcer (event source classification)

**From phi_os/human_gate.py:**
- Human Gate Authority (decision approval/rejection)

**From phi_os/integrity.py:**
- Integrity Engine (tamper detection, recovery suggestions)

**Operational Roles (Implied):**
- KUROKO Monitor (audit, monitoring, pre-decision work)
- KUROKO Observer (read-only monitoring)
- Audit Trail Manager (event history maintenance)

**Total Identified:** 7-9 distinct roles

---

## Candidate Registry Designs

### DESIGN CANDIDATE A: Authority-Centric (Maximum Control)

**Philosophy:** Emphasize formal authority types from Constitution; minimize operational roles.

**Registry:**

| Role ID | D-1 Role Identity | D-2 Description | D-3 Capabilities | D-4 Authority Level | D-5 Scope | D-6 Decision Rights | D-7 Execution Rights | D-8 Escalation |
|---|---|---|---|---|---|---|---|---|
| R001 | HUMAN_AUTHORITY | Human decision authority for authorization gates and policy decisions | APPROVE_DECISION, REJECT_DECISION, OVERRIDE_GATE, DELEGATE_AUTHORITY | SUPREME | All authorization decisions, policy changes, escalations | SELF (Human authority is final) | HUMAN_AUTHORITY executes all policy decisions directly | Appeal to Human Authority; no further escalation |
| R002 | GATE_AUTHORITY | System gate enforcement; routes all writes through validation | VALIDATE_PAYLOAD, ENFORCE_GATE_POLICY, CLASSIFY_EVENT_SOURCE, DENY_INVALID | MAJOR | Event validation, gate enforcement, access control | GL7 KERNEL decides abort conditions | GATE_AUTHORITY (phi_os/event_gate.py) executes validation | Reject event; escalate to HUMAN_AUTHORITY if pattern detected |
| R003 | EVENT_AUTHORITY | Event creation and integrity signing | CREATE_EVENT, SIGN_EVENT, COMPUTE_HASH_CHAIN, UPDATE_TRACE_ID | MAJOR | Event persistence, hash chain management | GATE_AUTHORITY approves; EVENT_AUTHORITY implements | EVENT_AUTHORITY (integrity.py) executes signing | Orphan detection triggers audit; escalate to KUROKO |
| R004 | VERIFICATION_AUTHORITY | Tamper detection and integrity audit | VERIFY_CHAIN, DIAGNOSE_ANOMALIES, DETECT_ORPHANS, CHECK_BINDING | MAJOR | Integrity verification, anomaly detection, recovery diagnosis | KUROKO_MONITOR proposes; HUMAN_AUTHORITY approves recovery | VERIFICATION_AUTHORITY (verify_chain()) executes verification | Critical anomalies escalate to HUMAN_AUTHORITY |
| R005 | INSTITUTION_AUTHORITY | Module governance and system structure | DEFINE_MODULE, GATE_MODULE, MANAGE_INSTITUTION, CONTROL_GATES | MAJOR | Institution definitions, module boundaries, gate hierarchy | HUMAN_AUTHORITY approves; INSTITUTION_AUTHORITY implements | INSTITUTION_AUTHORITY manages module structure | Structural conflicts escalate to HUMAN_AUTHORITY |
| R006 | KUROKO_MONITOR | Audit, monitoring, design verification, pre-decision analysis | AUDIT_CODE, AUDIT_DESIGN, COLLECT_EVIDENCE, PROPOSE_DECISIONS, MONITOR_STATUS | MINOR | Pre-decision work, design verification, measurement collection, monitoring | HUMAN_AUTHORITY on all decisions; KUROKO_MONITOR proposes | KUROKO_MONITOR executes audit/design; HUMAN_AUTHORITY decides | HUMAN_AUTHORITY final authority; retry limits on design proposals |
| R007 | AUDIT_TRAIL_MANAGER | Event history maintenance and tracing | MAINTAIN_AUDIT_TRAIL, TRACE_EVENTS, LINK_DECISIONS_TO_EVENTS, VERIFY_LINEAGE | MINOR | Audit trail system, event tracing, decision-event binding | EVENT_AUTHORITY approves write; AUDIT_TRAIL_MANAGER maintains | AUDIT_TRAIL_MANAGER (structural/state_reconstructor.py) maintains trail | Binding gaps escalate to VERIFICATION_AUTHORITY |

**Total Roles:** 7

**Advantages:**
- Clear authority hierarchy
- Maps directly to PHI-OS Constitution
- Minimizes operational overhead

**Disadvantages:**
- May be too abstract; operational details unclear
- Delegation model implicit

**Human Gate Decision Point:**
- D-1 through D-5 confirmed; require decision on:
  - D-6: Is SELF-decision by HUMAN_AUTHORITY sufficient, or needed sub-approval?
  - D-8: Retry limits on KUROKO proposals? (how many design iterations?)

---

### DESIGN CANDIDATE B: Operational-Centric (Maximum Clarity)

**Philosophy:** Emphasize operational roles and responsibilities; explicit decision flows.

**Registry:**

| Role ID | D-1 Role Identity | D-2 Description | D-3 Capabilities | D-4 Authority Level | D-5 Scope | D-6 Decision Rights | D-7 Execution Rights | D-8 Escalation |
|---|---|---|---|---|---|---|---|---|
| R101 | HUMAN_GATE | きむら博士: Final authority on authorization decisions, policy, recovery procedures | APPROVE_DECISION, REJECT_DECISION, OVERRIDE_SYSTEM, DEFINE_POLICY, DECIDE_RECOVERY | SUPREME | All authorization decisions, policy definitions, conflict resolution, recovery approval | SELF (final) | HUMAN_GATE executes all approved decisions | No escalation; HUMAN_GATE is final authority |
| R102 | KUROKO_AUDITOR | Claude/AI: Pre-decision work, design verification, evidence collection, monitoring | AUDIT_DESIGN, COLLECT_EVIDENCE, PROPOSE_CANDIDATES, MONITOR_METRICS, ANALYZE_CODE | MINOR | Design audit, pre-decision analysis, measurement design, monitoring framework | HUMAN_GATE approves proposals | KUROKO_AUDITOR executes audit/design; HUMAN_GATE executes decisions | HUMAN_GATE final; escalate on design gaps |
| R103 | GL7_KERNEL | Execution Governance Layer: Gate enforcement, abort conditions, dry run validation | VALIDATE_DRY_RUN, ENFORCE_ABORT_CONDITIONS, CHECK_GROUNDING, DETECT_SCOPE_VIOLATIONS, PREVENT_MODIFICATIONS | MAJOR | Execution control, modification prevention, scope validation, repository grounding | KUROKO_AUDITOR proposes; GL7_KERNEL enforces | GL7_KERNEL (structural/execution_governance.py) executes validation | Abort conditions trigger escalation; no override except HUMAN_GATE |
| R104 | EVENT_VALIDATOR | Validation gate for event payloads, schema compliance | VALIDATE_PAYLOAD, CHECK_SCHEMA, ENFORCE_RULES, CLASSIFY_SOURCE | MAJOR | Event payload validation, schema enforcement, rule checking | GL7_KERNEL decides gate status; EVENT_VALIDATOR enforces | EVENT_VALIDATOR (phi_os/gate_validator.py) executes validation | Invalid payloads rejected; patterns escalate to KUROKO |
| R105 | INTEGRITY_ENGINE | Event signing, hash chain creation, binding management | SIGN_EVENT, COMPUTE_HASH, CREATE_TRACE_ID, LINK_DECISION_TO_EVENT, MANAGE_BINDINGS | MAJOR | Event integrity, hash chain, decision-event binding, trace creation | EVENT_VALIDATOR approves valid events; INTEGRITY_ENGINE signs | INTEGRITY_ENGINE (phi_os/integrity.py) executes signing | Signing failures create orphans; VERIFICATION detects on next run |
| R106 | VERIFICATION_ENGINE | Integrity verification, tamper detection, orphan detection, recovery diagnosis | VERIFY_CHAIN, DETECT_TAMPERING, DETECT_ORPHANS, DIAGNOSE_ANOMALIES, SUGGEST_RECOVERY | MAJOR | Chain verification, tamper detection, anomaly diagnosis, recovery suggestions | KUROKO_AUDITOR proposes verification; VERIFICATION_ENGINE executes | VERIFICATION_ENGINE (phi_os/integrity.py:verify_chain) executes | Critical anomalies escalate to HUMAN_GATE via KUROKO_AUDITOR |
| R107 | AUDIT_TRAIL_MANAGER | Event history, tracing, lineage verification, binding proof | MAINTAIN_TRAIL, TRACE_DECISIONS, TRACE_EVENTS, VERIFY_LINEAGE, COLLECT_EVIDENCE | MINOR | Audit trail system, event tracing, decision-event lineage, evidence collection | INTEGRITY_ENGINE approves bindings; AUDIT_TRAIL_MANAGER maintains | AUDIT_TRAIL_MANAGER (structural/state_reconstructor.py) maintains trail | Binding gaps escalate to VERIFICATION_ENGINE |
| R108 | MONITORING_FRAMEWORK | Status aggregation, ROUTE metrics, system health | AGGREGATE_STATUS, COLLECT_METRICS, CALCULATE_ROUTE_STATUS, ALERT_ON_THRESHOLD | MINOR | Monitoring system, status metrics, health aggregation, threshold alerts | KUROKO_AUDITOR proposes design; MONITORING_FRAMEWORK executes | MONITORING_FRAMEWORK aggregates metrics; alerts escalate to KUROKO | System health failures escalate to HUMAN_GATE |

**Total Roles:** 8

**Advantages:**
- Clear operational responsibilities
- Explicit decision flows
- Easy to understand who does what

**Disadvantages:**
- More roles = more complexity
- Potential role overlap
- Escalation paths proliferate

**Human Gate Decision Point:**
- D-1 through D-5 confirmed; require decision on:
  - Should KUROKO_AUDITOR authority be limited to audit-only or include design proposals?
  - What is retry limit for rejected proposals? (deadlock prevention)
  - Can MONITORING_FRAMEWORK make autonomous decisions or only alert?

---

### DESIGN CANDIDATE C: Hybrid (Balanced Control & Clarity)

**Philosophy:** Balance authority-centric structure with operational clarity; merge similar roles.

**Registry:**

| Role ID | D-1 Role Identity | D-2 Description | D-3 Capabilities | D-4 Authority Level | D-5 Scope | D-6 Decision Rights | D-7 Execution Rights | D-8 Escalation |
|---|---|---|---|---|---|---|---|---|
| R201 | HUMAN_AUTHORITY | Final decision authority: きむら博士 | APPROVE_DECISION, REJECT_DECISION, OVERRIDE_GATE, DEFINE_POLICY, DECIDE_RECOVERY_PROCEDURES | SUPREME | All authorization decisions, policy, recovery procedures, final escalation | SELF (final authority) | HUMAN_AUTHORITY executes approved decisions | No escalation; HUMAN_AUTHORITY is final |
| R202 | KUROKO_MONITOR | Implementation audit and pre-decision work: Claude/AI | AUDIT_DESIGN, AUDIT_CODE, COLLECT_EVIDENCE, PROPOSE_CANDIDATES, MONITOR_METRICS | MINOR | Pre-decision work, design audit, code review, measurement collection, monitoring | HUMAN_AUTHORITY approves all proposals | KUROKO_MONITOR executes audit/design; HUMAN_AUTHORITY decides | Proposal rejection: max 2 iterations before escalation to HUMAN_AUTHORITY |
| R203 | GATE_SYSTEM | Gate enforcement and payload validation combined | VALIDATE_PAYLOAD, ENFORCE_GATE_POLICY, CHECK_SCHEMA, CLASSIFY_SOURCE, DENY_INVALID | MAJOR | Event validation, gate enforcement, payload rules, source classification, rejection | GL7 Kernel validates; GATE_SYSTEM enforces | GATE_SYSTEM (phi_os/event_gate.py + gate_validator.py) executes validation | Invalid events rejected; patterns escalate to KUROKO_MONITOR |
| R204 | INTEGRITY_SYSTEM | Event signing, binding, hash chain, verification combined | SIGN_EVENT, COMPUTE_HASH, LINK_DECISION_TO_EVENT, VERIFY_CHAIN, DETECT_TAMPERING, DIAGNOSE_ANOMALIES | MAJOR | Event integrity, binding, hash chain, tamper detection, anomaly diagnosis | GATE_SYSTEM approves events; INTEGRITY_SYSTEM signs; INTEGRITY_SYSTEM verifies | INTEGRITY_SYSTEM (phi_os/integrity.py) signs and verifies | Critical anomalies escalate to HUMAN_AUTHORITY via KUROKO_MONITOR |
| R205 | GL7_KERNEL | Execution governance: repository control, modification prevention | VALIDATE_DRY_RUN, ENFORCE_ABORT_CONDITIONS, CHECK_GROUNDING, PREVENT_UNAUTHORIZED_MODS | MAJOR | Execution control, repository grounding, modification prevention, scope validation | KUROKO_MONITOR proposes; GL7_KERNEL enforces | GL7_KERNEL (structural/execution_governance.py) executes validation | Abort conditions escalate to HUMAN_AUTHORITY; no override except by HUMAN_AUTHORITY |
| R206 | AUDIT_SYSTEM | Event tracing, lineage, binding verification, evidence | MAINTAIN_TRAIL, TRACE_EVENTS, VERIFY_LINEAGE, COLLECT_EVIDENCE, LINK_DECISIONS_TO_EVENTS | MINOR | Audit trail, event tracing, decision-event lineage, evidence collection | INTEGRITY_SYSTEM approves bindings; AUDIT_SYSTEM traces | AUDIT_SYSTEM (structural/state_reconstructor.py) maintains trail | Binding gaps escalate to INTEGRITY_SYSTEM |
| R207 | MONITORING_SYSTEM | Status aggregation, ROUTE metrics, alerts | AGGREGATE_STATUS, COLLECT_METRICS, CALCULATE_ROUTE_STATUS, ALERT_ON_THRESHOLD | MINOR | ROUTE status metrics, system health, threshold alerts | KUROKO_MONITOR designs; MONITORING_SYSTEM executes | MONITORING_SYSTEM aggregates; KUROKO_MONITOR analyzes | System health failures alert KUROKO_MONITOR; escalate to HUMAN_AUTHORITY |

**Total Roles:** 7 (merged similar operational roles)

**Advantages:**
- Balances authority and operational clarity
- Fewer roles = less complexity
- Clear decision hierarchy
- Explicit escalation to HUMAN_AUTHORITY

**Disadvantages:**
- Some role consolidation may mask responsibilities
- Still requires detailed D-6/D-7/D-8 specification

**Human Gate Decision Point:**
- D-1 through D-5 confirmed; require decision on:
  - Accept role consolidation (GATE_SYSTEM, INTEGRITY_SYSTEM, AUDIT_SYSTEM)?
  - Accept max 2-iteration retry limit for KUROKO proposals?
  - Accept HUMAN_AUTHORITY as single escalation point?

---

## Decision Requirements for Each Candidate

### Candidate A Decisions Required

**HG-N05-A1: Authority-Centric Model Adoption**
- Question: Accept Authority-type-based role model for formal governance?
- Alternatives: Candidate B (operational-centric) or Candidate C (hybrid)
- Impact: Determines formality level, authority model, delegation patterns
- Timeline: 1 week review

**HG-N05-A2: KUROKO Proposal Retry Limits**
- Question: How many design iteration cycles before KUROKO proposal is rejected?
- Range: 1 (no retry) to 3+ (unlimited)
- Recommendation: 2 iterations (allow refinement, prevent deadlock)
- Impact: Balances design quality vs. decision finality

**HG-N05-A3: HUMAN_AUTHORITY Sub-Approval**
- Question: Does HUMAN_AUTHORITY require sub-approvals for routine decisions?
- Range: No sub-approval to approval from quorum
- Recommendation: No sub-approval (single authority = faster decisions)
- Impact: Decision velocity, approval overhead

---

### Candidate B Decisions Required

**HG-N05-B1: Operational Model Adoption**
- Question: Accept 8-role operational model for clear responsibility assignment?
- Alternatives: Candidate A (authority-centric) or Candidate C (hybrid)
- Impact: Role proliferation, but clear responsibilities
- Timeline: 1 week review

**HG-N05-B2: MONITORING_FRAMEWORK Autonomy**
- Question: Can MONITORING_FRAMEWORK make autonomous decisions (alerts) or only report?
- Range: Fully autonomous to report-only
- Recommendation: Report with auto-escalation on critical threshold (hybrid)
- Impact: System responsiveness, human approval overhead

**HG-N05-B3: Role Overlap Resolution**
- Question: Which role handles decision-event binding conflicts?
- Candidates: EVENT_AUTHORITY, INTEGRITY_ENGINE, AUDIT_TRAIL_MANAGER
- Recommendation: INTEGRITY_ENGINE (responsible for binding creation and verification)
- Impact: Conflict resolution clarity

---

### Candidate C Decisions Required

**HG-N05-C1: Hybrid Model Adoption**
- Question: Accept merged role structure (7 roles vs. 8) for balance?
- Alternatives: Candidate A (7 formal roles) or Candidate B (8 operational roles)
- Impact: Balances formality and clarity
- Timeline: 1 week review

**HG-N05-C2: KUROKO_MONITOR Decision Authority**
- Question: Is audit-only + proposals sufficient, or need limited execution authority?
- Range: Audit-only to audit + implement approved decisions
- Recommendation: Audit + implement (within pre-decision scope only)
- Impact: Work efficiency, authority separation

**HG-N05-C3: Single Escalation Point**
- Question: Accept HUMAN_AUTHORITY as single escalation point for all conflicts?
- Alternatives: Multi-level escalation (GL7 -> KUROKO -> HUMAN_AUTHORITY)
- Recommendation: Direct HUMAN_AUTHORITY (simpler, faster)
- Impact: Decision speed, escalation clarity

---

## Implementation Readiness Assessment

### A. Registry Completeness

**All three candidates define:**
- [x] D-1: Role Identity (unique ID + name)
- [x] D-2: Description (purpose)
- [x] D-3: Capabilities (specific operations)
- [x] D-4: Authority Level (hierarchy rank)
- [x] D-5: Scope (component/operation coverage)
- [x] D-6: Decision Rights (who approves)
- [x] D-7: Execution Rights (who executes)
- [x] D-8: Escalation Procedure (conflict resolution)

**Status:** All 8 attributes defined for all candidates ✓

### B. Mapping to C2-b ROUTEs

**ROUTE 4 Coverage (Role Authority & Escalation):**
- [x] Role definitions specified
- [x] Authority matrix defined
- [x] Escalation procedures documented
- [x] Conflict resolution paths clear
- [x] Decision rights explicit

**Status:** ROUTE 4 requirements met by all candidates ✓

### C. Code Integration Readiness

**For Implementation Phase (After Human Gate Decision):**

**Candidate A:**
- Integrate with phi_os/runtime/authority_manager.py (authority types already defined)
- Map roles to existing AuthorityType enum
- Estimate: 2 hours (minimal code change)

**Candidate B:**
- Create new roles module: phi_os/runtime/role_registry.py
- Implement role lookup, decision rights validation
- Estimate: 2-3 hours (new module)

**Candidate C:**
- Extend authority_manager.py with operational role wrapper layer
- Map operational roles to authority types
- Estimate: 2-3 hours (moderate change)

**Implementation Authority:** Requires explicit Human Gate approval per candidate

---

## STEP 4 Completion Summary

### Pre-Decision Work Completed

- [x] **D-1 (Role Identity):** 7 distinct roles identified and named
- [x] **D-2 (Description):** Purpose and responsibility defined for each
- [x] **D-3 (Capabilities):** Specific operations listed for each role
- [x] **D-4 (Authority Level):** SUPREME/MAJOR/MINOR hierarchy defined
- [x] **D-5 (Scope):** Component/operation coverage specified
- [x] **D-6 (Decision Rights):** Approval structure defined for each candidate
- [x] **D-7 (Execution Rights):** Execution responsibility assigned
- [x] **D-8 (Escalation Procedure):** Conflict resolution paths documented

### Candidates Ready for Human Gate Decision

**Three complete candidates submitted:**
1. **Candidate A:** Authority-Centric (formal, minimal roles)
2. **Candidate B:** Operational-Centric (clear responsibility, 8 roles)
3. **Candidate C:** Hybrid (balanced, 7 roles)

**Each candidate includes:**
- Complete 8-attribute specification table
- Advantages and disadvantages analysis
- Human Gate decision points with recommendations
- Implementation effort estimate
- ROUTE 4 coverage verification

### Authorization Status

**Current Scope:** Implementation Authorization (design only)
- [x] Design analysis: COMPLETE
- [x] Candidate comparison: COMPLETE
- [x] Implementation plan outlined (not implemented)
- [x] No production modifications
- [x] No schema changes

**Next Scope:** Requires Human Gate Decision on preferred candidate

**Decision Timeline:** 1-2 weeks for review and selection

---

## STEP 4 Status

**COMPLETE** ✓

**Role Registry Status:** DESIGN_COMPLETE_AWAITING_DECISION

**Candidates Submitted:** 3 (Candidate A, B, C)

**Decision Required:** HG-N05 (Role Registry Selection)

**Estimated Decision Turnaround:** 1-2 weeks

**Next Step:** STEP 5 — AUTH_GAP_002 Audit Trail Monitoring Design

---

**Event Recording:** Pending mocka_write_event call (CHANGE_DONE)
**Authority:** Implementation Authorization Phase
**Custodian:** KUROKO Monitor (Claude-Haiku-4.5)
**Session:** claude/kuroko-c2b-route-audit-n51wgf

---

## Appendix: Role Consolidation Rationale (Candidate C)

### Why Merge GATE_AUTHORITY + EVENT_AUTHORITY + EVENT_VALIDATOR?

**Separate (Candidate B):**
- GATE_AUTHORITY: Routes writes through validation
- EVENT_VALIDATOR: Validates payloads
- EVENT_AUTHORITY: Creates events after validation

**Merged as GATE_SYSTEM (Candidate C):**
- Single responsibility: Ensure all events are valid before creation
- Reduce role proliferation
- Clearer execution flow: GATE_SYSTEM validates, then signs

**Decision Point for Human Gate:**
- Do you prefer clear role boundaries (Candidate B) or consolidated responsibility (Candidate C)?

### Why Merge INTEGRITY_ENGINE + VERIFICATION_ENGINE?

**Separate (Candidate B):**
- INTEGRITY_ENGINE: Signs events, creates hashes
- VERIFICATION_ENGINE: Verifies chains, detects tampering

**Merged as INTEGRITY_SYSTEM (Candidate C):**
- Single responsibility: Integrity from creation through verification
- Reduces role count
- Clearer: One system manages full integrity lifecycle

**Decision Point for Human Gate:**
- Do you prefer separation of signing/verification (Candidate B) or unified lifecycle (Candidate C)?

### Why Merge AUDIT_TRAIL_MANAGER + AUDIT_TRAIL maintenance?

**Separate (Candidate B):**
- Explicit audit trail role
- Responsibility clearly defined

**Merged as AUDIT_SYSTEM (Candidate C):**
- Consolidates event tracing, lineage, evidence
- Reduces role count
- Unified tracing responsibility

**Decision Point for Human Gate:**
- Do you prefer explicit audit role (Candidate B) or merged audit system (Candidate C)?

