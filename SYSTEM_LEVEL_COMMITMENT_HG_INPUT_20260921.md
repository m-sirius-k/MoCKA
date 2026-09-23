# System-level Commitment — Human Gate Input

**Date:** 2026-09-21  
**Mode:** Read-only boundary consolidation  
**Purpose:** Define the unresolved System-level Commitment boundary from existing implementation and recorded investigation evidence.  
**Not included:** Implementation authorization, schema/data change, migration, identifier issuance, architecture selection, or a selected answer to any decision question.

## Evidence basis and reading boundary

This input consolidates observations from:

- `MOCKA_RUNTIME_BINDING_INVESTIGATION_20260921_PHASE6_FINAL.md`
- `MOCKA_EXANTEON_REMAINING_WORK_REPORT.md`
- `PAPER5_CURRENT_IMPLEMENTATION_STATE_REPORT.md`
- `PAPER5_VERIFIED_BOUNDARY_AUDIT.md`
- `P5-PHASE2-FIRST-IMPLEMENTATION-ENVIRONMENT-RECOVERY-20260918.md`
- Current inspected source and persistent-store definitions for the objects listed below.

Status labels mean:

| Label | Meaning in this document |
|---|---|
| VERIFIED | Direct source or persistent-store evidence was inspected. |
| PARTIAL | An adjacent mechanism or one side of a relation was inspected, but the full named relation/semantics was not established. |
| NOT FOUND | The named implementation/binding was not located in the inspected boundary. This is not a claim of non-existence outside that boundary. |
| UNKNOWN | Available evidence does not establish the property. |

## 1. Current verified foundation

### 1.1 Existing persistent governance object boundary map

| Object name | Storage | Identity field | Lifecycle | Authority relation | Evidence relation | Runtime relation |
|---|---|---|---|---|---|---|
| Human Gate event | `data/mocka_events.db`, table `human_gate_events` | `event_id` (`HG...`); grouping/request key `request_id` | Event-sourced transitions: `submit → PENDING`; `approve/reject/expire/cancel` only from enumerated prior states. Current state is reconstructed from the latest event for `request_id`. | The inspected row schema contains action/payload/state fields; no separate authority column was observed. Approval payload is stored as JSON. | A Review Gate helper may place `decision_evidence_ref` in payload for that use case. No general mandatory evidence relation was observed in the table schema. | Human Gate module is stated to be the single state owner; no inspected mandatory binding from its `request_id` to Decision Ledger or execution ID. |
| Decision Ledger record | `data/decisions/decision_ledger.jsonl` | `decision_id` (`DC_YYYYMMDD_NNN`) | Append-only record stream; status vocabulary `Active`, `Superseded`, `Withdrawn`; latest line for an ID is treated as current by the MCP reader. | Schema includes `approved_by` and `approved_at`. | Schema includes optional `related_events` and `related_documents`; current-record inspection found them non-empty in 153 and 256 of 320 records respectively. | Runtime binding investigation finds decision lookup and status validation, but `decision_id` is supplied independently from `req_id`; no inspected mandatory request-to-decision persistence. |
| Authority object | In-memory `AuthorityManager._store`; canonical mappings in code and delegation history in instance memory | `AuthorityType` is the inspected key; no separate persistent authority-record ID was observed | Canonical holder mapping; delegation adds `delegated_to` and `delegation_event_id`; revoke clears those values. | This object is the authority model itself: holder, authority type, Gate mapping, hierarchy, conflict checks, delegation/revocation. | Delegation takes `delegation_event_id`; no mandatory commitment/evidence relation was observed. | `get_for_gate()` resolves authority for a Gate. No inspected runtime lookup from a system-level commitment to an Authority object. |
| Evidence record | Defined by `governance/write_path/evidence/schema.py`; source specifies `RuntimeEvidenceRecord`. Persistent concrete store was not established in inspected source. | `record_id` (`RER_YYYYMMDD_NNN`) | Schema declares `immutable=True` as append-only operational rule; correction is described as a new record. | Source states Runtime Evidence Record is not Authority and is subordinate to Governance Seal. | It is the evidence object: source event range, hash, hash method, generator, timestamp, optional anchor hash. | No inspected runtime requirement resolves an evidence record as a condition for a named commitment. |
| Seal record | `governance/anchor_record.json` is named as the Governance Seal anchor; `seal_auth_record.py` also defines a sandbox-only authorization record path. | Inspected seal-auth schema requires `seal_request_id` and `decision_id`; anchor-record field shape was not re-derived here. | The inspected auth-record source explicitly says it is record-layer/sandbox-only and does not call the actual seal or enforce stopping. | Its documented formation condition is `approved_by=human`; the source prohibits AI/autonomous self-authorization. | Runtime Evidence Record optionally carries `governance_anchor_hash` and is documented as subordinate to the Governance Seal. | Actual seal/auth enforcement connection is described as not connected in the inspected sandbox-only source. |
| Intent record | `runtime/intent_ledger.json` | `intent_id` | Inspected entries are `INTENT_RECEIVED` records with source, timestamp, and goal. No separate lifecycle vocabulary was observed in the inspected JSON records. | No authority field/relation was observed in the inspected intent entries. | No evidence relation was observed in the inspected intent entries. | An untracked `ExecutionContext` data class has optional `intent_id`; its runtime integration/persistence was not established by this inspection. |
| Runtime execution context | `runtime/execution_context.py` defines an in-memory `ExecutionContext`; a persistent execution-context store was not located in this inspection. | Optional `execution_id`; also optional intent/plan/action/decision/HG fields | Context fields include execution status, trace, evidence state, and institutional closure values. No persisted lifecycle was established. | Optional Human Gate fields (`hg_decision`, conditions, reason, timestamp) and governance-decision fields exist in the class. | Optional evidence hash/state/reference fields exist in the class. | `is_valid_for_execution()` checks only `intent_id`, `plan_id`, and `action_id`. Phase 6 independently reports no unique `execution_id` in the inspected MCP execution path; no equivalence or connection between these two paths was established. |
| Event record | `data/mocka_events.db`, table `events` | `event_id` (`E...`) | Event Gate validates, assigns ID/time, writes, signs/hash-chains, and commits. Field `request_id` is mapped from payload. | Event payload maps `who_actor` and `who_role` to event storage fields/notes. | Event Gate updates `trace_id` and `related_event_id` with signature current/previous hashes. | Event Gate is documented as the sole institutional event-save path. Phase 6 classifies persistence/traceability of request-to-event linkage as not verified for the inspected execution return path. |

Source anchors: [Human Gate state model](C:/Users/sirok/MoCKA/phi_os/human_gate.py:5), [Decision Ledger schema](C:/Users/sirok/MoCKA/docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md:23), [AuthorityManager](C:/Users/sirok/MoCKA/phi_os/runtime/authority_manager.py:10), [Evidence schema](C:/Users/sirok/MoCKA/governance/write_path/evidence/schema.py:1), [ExecutionContext](C:/Users/sirok/MoCKA/runtime/execution_context.py:15), and [Event Gate](C:/Users/sirok/MoCKA/phi_os/event_gate.py:34).

### 1.2 Existing cross-layer binding observations

Phase 6 records the following current MCP-path links:

| Path | Status recorded by Phase 6 | Boundary observation |
|---|---|---|
| Request → idempotency | VERIFIED | `req_id` is tracked in `request_executions`. |
| Request → decision | VERIFIED at argument lookup | `decision_id` is read from arguments; Phase 6 states this is independent of `req_id`. |
| Decision → authority | VERIFIED | Decision lookup/status validation is inspected. |
| Authority → execution | VERIFIED | Gate result controls whether execution is allowed. |
| Execution → result | VERIFIED | Tool handlers return result IDs. |
| Request → result | NOT VERIFIED | No defined return-path mapping is recorded. |
| Request → consequence | NOT FOUND | No automatic system-level linking is recorded. |
| Request → execution → result | NOT VERIFIED | Phase 6 records no unique execution ID in the inspected MCP path. |

This evidence establishes an execution-trace boundary. It does not establish that any one of these objects is a System-level Commitment.

## 2. Observed System-level Commitment boundary

### 2.1 Commitment identity analysis — existing objects only

No selection is made in this section.

| Candidate | VERIFIED evidence | NOT VERIFIED evidence | Missing semantic for System-level Commitment |
|---|---|---|---|
| A. Decision Ledger record | Persistent append-only JSONL; `decision_id`; `approved_by`/`approved_at`; status and supersession fields; optional event/document references. | Human Gate `request_id` or `human_gate_request_id` was not observed in current Decision Ledger records; no dedicated `commitment_id`, persisted scope, validity dates, reevaluation date, or mandatory evidence set was observed. | Whether a governed decision record itself has standing beyond its decision/status lifecycle; how authority, scope, evidence, expiry, reevaluation, and runtime consequence jointly determine that standing. |
| B. Human Gate approval event | Persistent event record, `request_id`, event identity, allowed approval/rejection/expiration/cancellation transitions, and current-state reconstruction. | No Decision Ledger `decision_id` column or mandatory link was observed in the Human Gate schema; no distinct commitment identity or general evidence/authority schema relation was observed. | Whether an approval event can establish continuing standing after the event, and how that standing relates to decision, scope, authority change, evidence change, or execution. |
| C. Authority object | Canonical authority type/holder mapping; Gate mapping; delegation with delegation event; revocation; conflict and hierarchy checks. | A persistent authority object ID/store was not observed; no binding to a specific decision/approval/evidence/execution chain was observed. | Whether authority is the subject that owns standing, a condition of standing, or only an evaluator/attribution relation. |
| D. Intent record | Persistent intent entries with `intent_id`, source, time, and goal; optional carrying of `intent_id` in inspected ExecutionContext class. | No authority, approval, decision, evidence, seal, or commitment lifecycle relation was observed in intent ledger entries. | Whether intent can create, identify, or merely precede a governed standing. |
| E. No existing object | The inspected sources contain separate identities for Human Gate, Decision Ledger, evidence, seal, intent, event, request, and some execution-context fields. The prior remaining-work report did not find a dedicated commitment class/field in the searched implementation boundary. | A repository-wide semantic equivalence rule that declares no existing object can represent commitment was not found. | The criteria by which an existing object would be accepted or rejected as a System-level Commitment. |

### 2.2 Commitment relationship matrix

**Legend:** Each cell reports the relation from the named object to the System-level Commitment concept as currently evidenced. It does not assert a design requirement.

| Object | Identity link exists? | Mandatory? | Persistent? | Runtime enforced? | Lifecycle controlled? |
|---|---|---|---|---|---|
| Human Gate | PARTIAL — `request_id`/`HG...` identity exists, but no commitment link | NOT FOUND | VERIFIED — event rows persist | PARTIAL — Human Gate controls its own state; commitment check not observed | VERIFIED — Human Gate event transitions only |
| Decision Ledger | PARTIAL — `decision_id` exists, but no commitment link | NOT FOUND | VERIFIED — append-only JSONL | PARTIAL — decision status is checked in inspected MCP governance path | PARTIAL — decision statuses/supersession exist; commitment lifecycle not observed |
| Authority | PARTIAL — authority type/holder exists, but no commitment link | NOT FOUND | UNKNOWN — inspected manager store is in-memory; separate persistent authority record not established | PARTIAL — Gate authority resolution exists | PARTIAL — delegation/revocation exists; commitment lifecycle not observed |
| Evidence | PARTIAL — `record_id` and source event range exist, but no commitment link | NOT FOUND | PARTIAL — append-only semantics specified; concrete store not established | NOT FOUND | PARTIAL — record correction-as-new-record is specified; commitment lifecycle not observed |
| Seal | PARTIAL — seal request/anchor identifiers exist in inspected sources, but no commitment link | NOT FOUND | PARTIAL — anchor record is named; its full store/lifecycle was not re-verified here | NOT FOUND | PARTIAL — auth-record rules exist in sandbox-only source; actual seal enforcement connection not observed |
| Execution | NOT FOUND — Phase 6 finds no MCP execution ID/binding record | NOT FOUND | NOT FOUND for Phase 6 MCP execution path | PARTIAL — authority result controls tool execution | NOT FOUND — no commitment lifecycle control observed |
| Event | PARTIAL — event `request_id` payload field exists; commitment link not observed | NOT FOUND | VERIFIED — Event Gate persists events | PARTIAL — Event Gate validation/persistence is enforced; commitment check not observed | PARTIAL — event lifecycle phase is stored; commitment lifecycle not observed |
| Intent | PARTIAL — `intent_id` exists; commitment link not observed | NOT FOUND | VERIFIED — inspected intent JSON persists entries | NOT FOUND | NOT FOUND — no intent lifecycle control was observed in the inspected entries |

### 2.3 Approval, decision, and commitment — observed separation

| Concept | Meaning for this Human Gate input | Existing implementation observation | Distinction status |
|---|---|---|---|
| Approval | Human authorization event | Human Gate records `submit`, `approve`, `reject`, `expire`, and `cancel` events keyed by `request_id`, with state reconstructed from events. | VERIFIED as an event/state-machine concept. |
| Decision | Chosen governed action/state | Decision Ledger schema contains `decision_id`, decision text, alternatives, rationale, impact, attribution, timestamp, status, and supersession references. Core runtime receives a DecisionRecord and commits unless its decision is `FAIL`. | VERIFIED as a persistent ledger concept and runtime input concept. |
| Commitment | System-level standing that persists beyond a single decision | No dedicated commitment identity, lifecycle, or runtime verifier was located in the inspected sources and current Decision Ledger records. Existing documents use durable decision/persistent governance reference language, but do not supply the full named commitment semantics. | NOT FOUND as a dedicated implemented concept; whether it is semantically represented by another existing object is unresolved. |

**Observed result:** Current implementation distinguishes Approval and Decision by separate storage, identifiers, and lifecycle/record shapes. The inspected boundary does not establish an implemented third object or an explicit equivalence rule for Commitment.

## 3. Paper 5 boundary

### VERIFIED — Paper 5 currently covers

- M1 evidence-preservation infrastructure: evidence layer, Decision Ledger persistence, and audit infrastructure as recorded in `PAPER5_CURRENT_IMPLEMENTATION_STATE_REPORT.md`.
- M1 Decision Ledger: the Paper 5 audit records append-only Decision Ledger structure and decision/attribution fields as verified core structure, with content-linkage qualifications.
- M2 fail-closed governance-runtime model: runtime executes a DecisionRecord and forwards audit stages; the Paper 5 audit classifies the modeled fail-closed commit logic as verified, while leaving decision-engine evaluation rules unexamined.
- M2 authority attribution in the Decision Ledger: `approved_by` schema presence and sampled records are recorded as verified in the Paper 5 audit.
- M3 Stage 5 isolation properties and sandbox fail-closed behavior in test context only.

### NOT IMPLEMENTED / not established by inspected Paper 5 evidence

- A dedicated System-level Commitment object, identity, or lifecycle.
- UNKNOWN/REM implementation: the Paper 5 audit records specification/memory references but no located implementation.
- Actual Decision Ledger-to-event cross-reference content verification; Paper 5 records schema fields but marks actual linkage as an evidence gap.
- Production M3 binding, full A–J integration, and decision-engine evaluation rules.
- A production runtime condition that resolves and verifies a System-level Commitment before execution.

### DEFERRED / requires future authorization according to the Phase 2 record

- Schema/database modification.
- Route/API modification.
- Runtime binding.
- Production deployment/modification.
- The listed other targets: `Standing_t`, Authority Boundary, Major Change Detection, Audit Trace, Retention Tiers, and Component A–J monitoring.

The Phase 2 record identifies an authorization boundary for `ExecDisposition_t`; it does not establish authorization for System-level Commitment identity or lifecycle semantics.

## 4. Human Gate decision questions

### Q1. Is System-level Commitment a new governed object?

**Current evidence:** Approval events, Decision Ledger records, authority objects, evidence records, seal records, intent records, events, and runtime-context fields are separately observed. No dedicated commitment object/field/class or explicit equivalence rule was located in the inspected boundary.

**Decision boundary:** Determine whether System-level Commitment is a separately governed object or an explicitly defined semantic role of an existing object. No object is selected by this input.

### Q2. Can Decision Ledger represent commitment identity?

**Current evidence:** Decision Ledger has persistent `decision_id`, authority-attribution fields, status/supersession, and optional event/document references. Its current observed records do not contain commitment identity, Human Gate request binding, persisted scope, required evidence, validity dates, or reevaluation fields.

**Decision boundary:** Determine whether `decision_id` may represent commitment identity, and, if so, which semantic/lifecycle information is authoritative outside the currently observed Decision Ledger fields.

### Q3. What is the authoritative identity chain?

**Current evidence:** Existing identities include Human Gate `event_id`/`request_id`, Decision `decision_id`, Event `event_id`, Intent `intent_id`, and request `req_id`. Phase 6 records that an MCP-path unique `execution_id` and a persistent request→execution→result binding are not found. An independent `ExecutionContext` class declares an optional `execution_id`, but its persistence and connection to the Phase 6 MCP path are not established.

**Possible examples only; no chain is selected:**

```
Human Gate ID
→ Decision ID
→ Execution ID
```

or

```
Commitment ID
→ Decision ID
→ Execution ID
```

**Decision boundary:** Identify the authoritative chain, its persistence location, and whether any existing IDs are aliases, inputs, outputs, or mandatory references.

### Q4. Who owns commitment lifecycle?

**Current evidence:** Paper 5 covers identified evidence, decision, authority, and test-only sandbox boundaries; its Phase 2 record defers Standing_t, Authority Boundary, Major Change Detection, runtime binding, and related targets. AuthorityManager owns authority delegation/revocation behavior; Human Gate owns approval-event state; Decision Ledger owns decision record status. No inspected artifact assigns System-level Commitment lifecycle ownership to Paper 5, an Exanteon layer, or Core governance.

**Decision boundary:** Determine lifecycle ownership among:

- Paper 5
- Exanteon layer
- Core governance

No ownership is selected by this input.

### Q5. What runtime condition requires commitment verification?

**Current evidence:** The inspected core runtime receives a decision and performs a commit based on the engine decision; its source states it does not re-evaluate or re-apply rules. GL7/MCP governance validates a supplied Decision Ledger record. Phase 6 records no commitment-oriented runtime verifier and no complete request→execution→result identity binding.

**Decision boundary:** Determine whether any consequential runtime action must verify System-level Commitment standing, and identify the condition/event boundary to which that verification applies. This input does not select a runtime condition or enforcement behavior.

## 5. Unresolved boundary statement for Human Gate

The unresolved boundary is not whether MoCKA has persistent governance records. It has separately evidenced Human Gate event persistence, Decision Ledger persistence, authority primitives, evidence/seal structures, intent records, event records, and partial execution tracing.

The unresolved boundary is whether, and under what authoritative semantics, any existing object represents **System-level Commitment**: a standing that persists beyond a single approval event or decision and can be related to authority, scope, evidence, validity/expiry/reevaluation, change, and runtime execution.

Current evidence does not establish:

- a selected commitment identity;
- a mandatory identity chain across approval, decision, execution, and result;
- a single owner for commitment lifecycle;
- a formal standing/validity predicate;
- a runtime condition that verifies such standing; or
- ownership allocation among Paper 5, Exanteon, and Core governance.

## Read-only verification record

- No code, schema, database, ledger, migration, runtime object, identifier, or commit was created or changed for this input.
- The current branch was inspected only; no checkout or merge occurred.
- The output file is a Human Gate review document, not a governance decision or implementation authorization.

