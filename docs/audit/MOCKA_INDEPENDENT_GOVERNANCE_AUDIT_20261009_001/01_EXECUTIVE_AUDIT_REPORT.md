# Deliverable 1: Executive Audit Report

Audit ID: MOCKA_INDEPENDENT_GOVERNANCE_AUDIT_20261009_001
Status: DRAFT for HG review. This report makes no HG decision and grants no authorization. It does not declare Runtime Verification or A1 Closure.

Evidence labels used throughout: PRIMARY_SOURCE_VERIFIED, SECONDARY_SOURCE_CORROBORATED, LOCAL_REPORT_ONLY, ANALYTICAL_INFERENCE, HYPOTHETICAL_SCENARIO, NOT_VERIFIED. Source details are in 02_STANDARDS_RESEARCH_MAPPING.md.

## 1. Bottom line

- External research supports the design vocabulary MoCKA uses. Separating decision from enforcement (PDP/PEP, NIST SP 800-207), tying evidence to provenance (W3C PROV-DM), propagating causal context (W3C Trace Context via OpenTelemetry), and treating append-only logs with verifiable proofs (RFC 9162) are all established concepts. This is ANALYTICAL_INFERENCE on top of SECONDARY_SOURCE_CORROBORATED material.
- External research cannot show that MoCKA's controls work. Standards and architecture describe what a control should do. They do not show that the running EventGate, the configuration, or the Windows environment has the state the design assumes. That needs KUROKO PC primary evidence.
- The local leads (section 4 of the brief) describe a serious possible gap: enforcement configured in a mode that quarantines events, a status: ok response without a corresponding events row, and no located activation authorization. These are LOCAL_REPORT_ONLY. They are the first thing the local audit must test. Nothing in this report confirms them.
- The smallest high-impact step is to make every governance transition emit its own read-back-verifiable record (section 6), so that "accepted", "decided", "persisted", "read back", and "outcome verified" are five separate facts. Most of the failure modes below collapse into one of those five facts being assumed.

## 2. What can be established from external research

| Claim | Basis | Confidence |
|---|---|---|
| NIST AI RMF 1.0 (NIST AI 100-1, 26 January 2023) is voluntary and organized into GOVERN, MAP, MEASURE, MANAGE. | Multiple secondary guides agree; primary PDF fetch blocked | SECONDARY_SOURCE_CORROBORATED |
| NIST SP 800-207 (Zero Trust Architecture) separates a Policy Decision Point (policy engine plus policy administrator) from a Policy Enforcement Point in the traffic path. | Secondary summaries agree; primary blocked | SECONDARY_SOURCE_CORROBORATED |
| RFC 9162 (Certificate Transparency v2.0, Experimental, December 2021) provides append-only logs using Merkle inclusion and consistency proofs, and detects misissuance rather than preventing it. | Search snippet cites rfc-editor and datatracker; primary blocked | SECONDARY_SOURCE_CORROBORATED |
| W3C PROV-DM is a Recommendation dated 30 April 2013 (editors Moreau and Missier) built on entities, activities, and agents. | Search snippet cites W3C URL; primary blocked | SECONDARY_SOURCE_CORROBORATED |
| OpenTelemetry carries parent and trace identity via the W3C traceparent header (trace ID 128 bits, parent ID 64 bits). | Secondary guides; OpenTelemetry page not fetched | SECONDARY_SOURCE_CORROBORATED (field widths also match general W3C layout; verify against primary) |
| OWASP LLM Top 10 2025 lists excessive agency as LLM06. The agentic Top 10 (December 2025) splits that concern across ASI01, ASI02, ASI03, ASI05, ASI10 rather than having one entry. | Secondary sources | SECONDARY_SOURCE_CORROBORATED; a 2026 reordering reported by one source is NOT_VERIFIED |
| ISO/IEC 42001:2023 (published December 2023) is an AI management system standard with Annex SL structure, voluntary certification. | Secondary sources | SECONDARY_SOURCE_CORROBORATED; clause and control counts are NOT_VERIFIED |
| NIST SP 800-92 (2006) is a log management guide. It does not address AI, admission gates, or runtime authorization, and its current revision status is NOT_VERIFIED. | Search snippet | SECONDARY_SOURCE_CORROBORATED |

Points the external sources do not establish:
- That any MoCKA component conforms to, or is certified against, any of these. No standard in this set gives MoCKA formal compliance. Nothing here is a certification claim.
- That an external standard confers internal authorization (brief section 2.1).

## 3. What is technically achievable (design level)

These are achievable with known engineering patterns. Each still needs empirical demonstration in the actual runtime.

1. Separate decision from enforcement. A PDP-style component decides; a PEP-style gate enforces; the enforcement point must refuse actions without a valid decision token. (NIST SP 800-207 concept, SECONDARY.)
2. Make every admission outcome a recorded fact with an explicit state (accepted, rejected, quarantined, persisted, read back). A gate that answers "ok" without a persisted record should be impossible by construction, not by convention. (ANALYTICAL_INFERENCE.)
3. Tamper-evident event history using hash chaining or Merkle commitments, with inclusion and consistency proofs, so that an exported audit can be checked against an earlier anchor. (RFC 9162 concept, SECONDARY; applicability to MoCKA's SQLite/JSON stores is ANALYTICAL_INFERENCE.)
4. Causal linkage by correlation identifiers that cross component boundaries (trace and parent identifiers). (OpenTelemetry concept, SECONDARY.)
5. Provenance graph linking evidence, decision, authorization, action, and outcome as entities, activities, and agents. (PROV-DM concept, SECONDARY.)
6. Idempotency keys so that a retry after a timeout cannot create a second effect, with the key bound to the operation and the result stored. (ANALYTICAL_INFERENCE; no primary standard was verified in this session.)

## 4. What cannot be inferred from standards or architecture alone

- Whether the enforcement setting was in effect in the process that handled a given event. (Brief 2.3.) Requires process-level observation.
- Whether a status: ok response corresponds to a persisted event. Requires read-back on the store, and identity matching by event ID rather than by timestamp.
- Whether the 84 gate rows and the quarantine decisions are the same events. A time match within 0.5 seconds is not identity (brief section 4, item 4).
- Who or what changed data/events_latest.json and when. Requires filesystem audit or OS-level evidence, which this session did not have.
- Whether HG-2 activation was ever authorized in a form the system would accept. Requires the Decision Ledger and HG records, checked against their own integrity evidence.
- Whether the audit expected event is absent, stored elsewhere, rejected, or written with an unknown outcome. Requires the four-way reconciliation in 05 Stage 3.
- Whether the MoCKA observations in section 6 below reflect the local PC. They are MoCKA-side reads, and MoCKA's own overview states that some of its body text has been stale since 2026-06-18.

## 5. Highest-impact failure modes (HYPOTHETICAL unless noted)

Full matrix in 03_GOVERNANCE_GAP_FAILURE_MATRIX.md. Ranked by impact on the governance loop:

1. API success without a corresponding event record (scenario 4). Lead items 3, 4, 5 point here. Its consequence is that REQUEST_ACCEPTED is treated as EVENT_PERSISTED. Status: LOCAL_REPORT_ONLY for the observation; HYPOTHETICAL for the mechanism.
2. Authorized configuration with ineffective runtime enforcement, or enforcement set without a verified activation (scenarios 1, 2). Lead items 1, 2, 6, 7. Status: LOCAL_REPORT_ONLY.
3. Fallback path bypassing the gate (scenario 13). Not observed. Must be ruled in or out by path analysis (05 Stage 5).
4. Timeout with unknown write outcome, leading to duplicate or missing effect (scenarios 9, 10). Relevant to H8-J1, H8-J2, H8-J5. Mechanism is design-level; occurrence NOT_VERIFIED.
5. Misleading chronology (scenario 14). Lead item 8 (hook-signature events stopping 2026-06-19 while other writers continued) is consistent with a source change rather than an outage, but this is not established. Status: LOCAL_REPORT_ONLY.
6. False closure from passing tests (scenario 16). Any closure that rests on tests alone is a risk. Status: design-level.
7. Audit export rewritten during examination (scenario 15). Lead item 10. Status: LOCAL_REPORT_ONLY.

## 6. MoCKA-side observations (read-only, not evidence for the leads)

These were read through MoCKA MCP tools on 2026-10-09. They describe MoCKA's own records. They do not prove what the local PC did.

- MOCKA_OVERVIEW v4.1 states that its body content was last updated 2026-06-18 and that later work is not reflected. This is a direct example of "Recorded does not equal Current" and should be treated as a staleness risk in any review that uses the overview.
- The current_view generated 2026-10-09 reports a latest recent_events timestamp of 2026-10-06 09:28 UTC and a latest recent decision DC_HG_IMPLEMENTATION_AUTHORIZATION_RCL_ORCHESTRA_BRIDGE_20261007 approved 2026-10-07. That decision concerns an RCL-to-Orchestra bridge, not EventGate activation. It is not an activation authorization.
- The essence feed contains an HG-2 related entry (2026-10-04) that asks for an independent governance and architecture research pass before HG-2 activation. This matches the brief's origin but does not itself show an activation decision.
- The essence feed also shows git commit records on a branch named phase5c-runtime-verification, which is not this audit's branch. Not relevant to the audit's scope; noted for chronology.

## 7. Required analytical conclusions (brief section 7)

1. Minimum evidence that a human authorization constrained a runtime action: (a) a signed or otherwise tamper-evident HG decision record with an identifier, the approving authority, scope, target, operation, expiry, and approved_at value; (b) a runtime decision record produced by the enforcement point that cites that authorization identifier; (c) the enforcement point's own record that it refused or permitted the action on that basis; (d) a read-back of the resulting event that carries the same identifiers; and (e) an observed consequence that matches the scope. All five must match on identifiers, not on time. Mechanism: ANALYTICAL_INFERENCE.
2. Distinguishing a missing event from one stored elsewhere, rejected, or with an unknown outcome: stored-elsewhere requires a lookup by event identifier across all stores (including quarantine and idempotency tables). Rejected requires the admission gate's decision record with the same identifier and a reason code. Unknown outcome requires the client's request record and idempotency key with no matching decision or persistence record, plus a time-bounded reconciliation rule. Time-only matching cannot distinguish these.
3. Can a governance system be reliable when enforcement works but audit is incomplete? Only in a narrow sense. Enforcement working means the action was constrained, which is the prevention goal. But the system cannot then prove that it was constrained, cannot reconstruct why, and cannot learn from it. Conditions for a conditional yes: enforcement decisions are recorded by an independent path, the gap is detected and reported as a gap rather than as success, and no closure or memory update uses the incomplete trail as proof. Limitation: this does not satisfy the complete governance loop.
4. Handling uncertainty without silently converting it: every uncertain state needs an explicit, non-default disposition (for example UNKNOWN, PENDING_RECONCILIATION, or ESCALATED_TO_HG), with an owner, a deadline, and a rule that expiry does not produce approval. Silence is not consent (brief 2.5). Mechanism: ANALYTICAL_INFERENCE. The disposition must be tested, not assumed.
5. Smallest high-impact set of controls connecting authorization, execution, consequence, and memory: (a) a per-transition record with stable identifiers linking decision, authorization, enforcement, persistence, and read-back; (b) read-back verification before any state is reported as persisted; (c) an enforcement-point decision record that cannot be produced without a valid authorization reference; (d) an explicit fail-closed or explicit-pending disposition for each uncertain state; and (e) a rule that memory and lessons carry provenance and cannot grant authority. See 03, the dependency section, and 05 Stage 8.
6. Claims established through external research versus those requiring local evidence: section 2 above lists the former. Everything about the local PC, the leads, and the database state requires local evidence.
7. What must be proven before MoCKA can declare Runtime Causal Efficacy or A1 Closure: see section 9.
8. Questions for HG first: see 04, section "Priority order".

## 8. Recommended order of the local audit and validation

1. Evidence preservation and baseline (read-only, snapshot hashes of stores and configs before anything else changes).
2. Enforcement provenance (where the setting came from, which process read it, when).
3. Event and quarantine reconciliation by identifier.
4. Authorization and Ledger reconciliation.
5. Runtime path and bypass analysis.
6. Specification-to-implementation mapping.
7. Controlled verification, only after separate written authorization.
8. Independent closure review.

Details and stop conditions are in 05_LOCAL_AUDIT_BLUEPRINT.md.

## 9. Evidence required before claiming a complete governance loop

A complete loop claim requires all of the following, each with primary evidence:

- Policy active at execution time (process-level or config-at-runtime evidence, not only the file).
- Authorization bound to actor, target, operation, scope, freshness, and expiry, and verifiable from the record.
- The enforcement point mediated the path, with a bypass path shown absent or blocked by test.
- Persistence states individually observed: REQUEST_ACCEPTED, GATE_DECISION_RECORDED, EVENT_PERSISTED, EVENT_READ_BACK_VERIFIED, OUTCOME_VERIFIED.
- Consequence observed and matched to the authorized action by identifier.
- Later configuration changes shown not to alter the interpretation of earlier evidence.
- Memory entries used in decisions carry provenance and an approval record, and are not authority.
- Independent closure review, separate from the author of the change.

None of these is established by this report.

## 10. Next steps

1. HG reviews this package, and decides whether the leads are to be verified (this is a decision for HG, not for this report).
2. KUROKO PC executes 05 Stages 0 to 4 as read-only, after separate authorization to start the audit.
3. Retry primary-source fetches when the egress policy permits, or supply primary PDFs from KUROKO PC. Update 02 with PRIMARY_SOURCE_VERIFIED where confirmed.
4. Integrate the two result sets only by identifier, keeping the web (external) and PC (local) evidence in separate sections.
