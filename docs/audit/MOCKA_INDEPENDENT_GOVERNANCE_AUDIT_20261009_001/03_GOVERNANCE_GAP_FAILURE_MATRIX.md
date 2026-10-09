# Deliverable 3: Governance Gap and Failure-Mode Matrix

Audit ID: MOCKA_INDEPENDENT_GOVERNANCE_AUDIT_20261009_001

Labels: HYPOTHETICAL_SCENARIO unless marked LOCAL_REPORT_ONLY (lead from brief section 4, not verified). Design-level = control exists in design only. Empirical = demonstrated in runtime (none is demonstrated by this audit).

## A. Authorization transitions (brief Workstream B)

Eight stages. For each: inputs and outputs, owner, binding, freshness, provenance, replay risk, timeout behavior, fail-open or fail-closed, independent verification, evidence of success.

| # | Transition | Input -> Output | Authority owner (design) | Scope and target binding | Freshness and expiry | Replay or duplication risk | Failure or timeout disposition (required) | Independent verification | Evidence of successful operation |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Evidence acquisition | source data -> evidence record | Collector component | Source ID, time of capture | Capture time recorded | Duplicate capture | Missing source recorded as MISSING, not as ABSENT | Re-collection by second path | Evidence record with hash and source ID |
| T2 | Assessment | evidence -> assessment (recommendation only) | Assessor (no authority) | Subject ID | Assessment version bound to evidence hash | Re-assessment on stale evidence | Assessment FAILED or UNKNOWN; never default to pass | Assessment reproducible from evidence | Assessment record citing evidence hashes |
| T3 | Decision | assessment -> decision record | Decision function, subject to human-gate rules | Decision scope | Expiry field required | Duplicate decision | Pending if no decision; silence is not decision | Second reviewer or HG | Decision record with identifier |
| T4 | Human authority | HG decision -> HG authority record | Human Gate only | Named scope, operation, target | Explicit expiry | Replay of old HG record | No HG record: no authority (fail-closed) | Signature or tamper-evident anchor; read-back | HG record readable by ID |
| T5 | Authorization issuance | HG record -> authorization token or reference | Issuance component, bound to HG record | Actor, target, operation, scope | approved_at and expiry | Stale or replayed token (scenario 8) | Issuance refused if HG record absent or ambiguous | Issuer cannot grant itself (separate identity) | Token ID equals HG reference |
| T6 | Runtime enforcement | request + token -> allow or refuse, decision record | PEP | Must match token scope | Checked at execution time | Bypass path (scenario 13) | Enforcement unreachable: fail-closed (design requirement, NOT_VERIFIED for MoCKA) | Bypass test; process-level observation | Decision record citing token ID, for each execution |
| T7 | Actual consequence | executed action -> outcome record | Executor and outcome verifier | Same action identifier | Recorded at execution | Duplicate execution (scenario 10) | Outcome UNKNOWN if not observed; never inferred from success response | Independent read-back | Outcome record matched by action ID |
| T8 | Institutional memory | outcome and decisions -> lesson or hypothesis | Memory component has no authority | Provenance links to source records | Retention and supersession rules | Memory as authority (scenario 12) | Lesson remains hypothesis until approved | HG approval for policy change | Lesson record with provenance and approval status |

Transitions that cannot be safely inferred from the adjacent stage:
- T4 to T5: a valid-looking token does not prove an HG decision exists (requires reference check).
- T5 to T6: a token existing does not prove the PEP used it (requires PEP decision record).
- T6 to T7: an allow decision does not prove consequence (requires outcome record).
- T7 to T8: an outcome does not prove the decision was right (brief 2.4: a gap is not automatically a wrong decision).

## B. Persistence states (brief Workstream C)

| State | Meaning | How it can be established from an ordinary API response | Requires independent evidence |
|---|---|---|---|
| REQUEST_ACCEPTED | Server received and validated the request | Yes, from HTTP or API status, but only as receipt | Not sufficient for anything else |
| GATE_DECISION_RECORDED | Admission gate wrote a decision (accept, reject, quarantine) with ID | Only if the response includes the decision ID and it can be looked up | Lookup by ID in the decision store |
| EVENT_PERSISTED | Event row exists in the primary event store | No. A success response does not show a row | Read from the primary store by event ID |
| EVENT_READ_BACK_VERIFIED | A later read returns the same event with the same content hash | No | Independent read, ideally a different process |
| OUTCOME_VERIFIED | The real-world consequence matches the authorized action | No | Observation outside the event system |

Consequence analysis (API success with primary event absent). Legitimate alternate paths include: quarantine table or payload store; idempotency record pointing to a stored result; a deliberate rejection that returns ok with a quarantine status. Data-loss scenarios include: a write that failed after the response was built; a write to a store the reader does not query; or an outdated reader. These are not distinguishable from an API response alone. Lead items 4 and 5 (LOCAL_REPORT_ONLY) describe exactly this ambiguity: 84 gate rows, no events row, time-only match. Per brief 2.1, a missing record does not establish that the event never occurred.

## C. Failure-mode matrix (brief Workstream E)

Each entry: preconditions; failure mechanism; observable symptoms; required evidence; detection method; impact; mitigating control; residual risk; control type (design-level or empirical).

### S1. Unauthorized activation of an enforcement setting
- Preconditions: enforcement setting can be changed without an HG record; setting read by the gate.
- Mechanism: a setting is changed at machine or user level without an authorization reference.
- Symptoms: enforcement behavior appears without a matching HG record. Lead item 1 (user-level value observed), lead item 2 (machine value empty), lead items 6-7 (HG records say not authorized; no later activation found).
- Required evidence: provenance of the setting (who, when, from where); process environment at runtime; HG record search across all ledgers.
- Detection: periodic comparison of effective setting against the HG activation record; setting-change audit.
- Impact: enforcement decisions made under an unauthorized mode.
- Mitigation: the gate refuses to run in enforce mode unless a verified activation record is present; the setting itself is not authority.
- Residual risk: setting changed out-of-band before the check runs.
- Control type: design-level. Status of lead items: LOCAL_REPORT_ONLY.

### S2. Authorized configuration with ineffective runtime enforcement
- Preconditions: a valid authorization exists; the process that handles events does not read the setting (different environment, cached config, or different process).
- Mechanism: configured does not equal connected.
- Symptoms: decision records show a mode that the running process did not apply; or no enforcement log at all.
- Required evidence: effective configuration in the running process; enforcement decision record per event.
- Detection: runtime probe that writes a known test decision and reads back the mode the process reports.
- Impact: policy stated but not applied.
- Mitigation: the enforcement decision record includes the mode actually applied; the mode is in every decision.
- Residual risk: mode reported by the process itself could be wrong.
- Control type: design-level; empirical demonstration NOT performed.

### S3. Correct enforcement with incomplete audit persistence
- Preconditions: gate rejects or quarantines correctly; persistence path for the decision record is separate and can fail.
- Mechanism: enforcement works; the audit write does not.
- Symptoms: blocked actions with no matching decision record; counts disagree between enforcement logs and store.
- Required evidence: enforcement-side log independent of the event store; reconciliation by ID.
- Detection: count and ID reconciliation between independent sources.
- Impact: governance is effective but not reconstructable.
- Mitigation: decision written before the response is returned; a failure to write blocks the response.
- Residual risk: a crash between enforcement and write.
- Control type: design-level.

### S4. API success without a corresponding event record
- Preconditions: response is built before or without a confirmed persistence step; or quarantine path returns ok.
- Mechanism: status ok reports receipt, not persistence.
- Symptoms: lead items 4-5 (LOCAL_REPORT_ONLY): gate rows with no events row; idempotency record written for some quarantine outcomes.
- Required evidence: the gate's response code path; the idempotency record content; the quarantine record content; lookup by request ID.
- Detection: read-back after every write; a monitor that flags response ok with no persisted row.
- Impact: callers believe persistence occurred; audit trail incomplete.
- Mitigation: response carries an explicit state (REQUEST_ACCEPTED, QUARANTINED, PERSISTED) and the client treats only PERSISTED as persistence.
- Residual risk: the state names could be misread.
- Control type: design-level; occurrence LOCAL_REPORT_ONLY.

### S5. Quarantine without sufficient payload traceability
- Preconditions: quarantine stores a decision but not the original payload or its hash.
- Mechanism: the rejected payload cannot be reconstructed.
- Symptoms: quarantine rows with no payload hash; cannot tell which request was quarantined.
- Required evidence: payload hash at quarantine time; request ID; source.
- Detection: schema check requiring payload hash and request ID for quarantine rows.
- Impact: cannot determine whether a quarantined event was legitimate.
- Mitigation: store payload (or its hash plus a retained copy) at quarantine time.
- Residual risk: retention policy removes the payload.
- Control type: design-level.

### S6. Event records without verifiable authorization
- Preconditions: events stored with no authorization reference, or with a reference that is not checked.
- Mechanism: the store accepts events whose authority cannot be traced.
- Symptoms: events with an enforcement mode but no decision ID.
- Required evidence: decision ID on each event; decision record exists and matches.
- Detection: join check from event to decision and from decision to authorization.
- Impact: events look authorized when they were not.
- Mitigation: the event store requires a decision reference for governed event types.
- Residual risk: events from ungoverned types.
- Control type: design-level.

### S7. Valid authorization applied outside its scope
- Preconditions: authorization has scope fields, but the enforcement point does not compare them to the target.
- Mechanism: scope not bound to target and operation.
- Symptoms: an authorized actor performs a different operation or hits a different target.
- Required evidence: scope fields on the authorization; target and operation on the action; comparison result in the decision record.
- Detection: scope check as a test case; audit of mismatched decision records.
- Impact: unauthorized consequence under an authorization that looks valid.
- Mitigation: the enforcement point evaluates scope and records the comparison.
- Residual risk: scope fields too broad.
- Control type: design-level; empirical NOT demonstrated.

### S8. Stale or replayed authorization
- Preconditions: no expiry check, or expiry measured from the wrong clock.
- Mechanism: an old authorization is reused.
- Symptoms: action executed after expiry; same authorization ID appears in multiple decisions beyond intended use.
- Required evidence: approved_at, expiry, and a clock source; the use count.
- Detection: query for uses after expiry; uniqueness check on one-time authorizations.
- Impact: an action is executed under authority that no longer applies.
- Mitigation: expiry enforced at the PEP; one-time use recorded and checked.
- Residual risk: clock skew.
- Control type: design-level.

### S9. Timeout with an unknown write outcome
- Preconditions: client times out after the server may have written.
- Mechanism: the client cannot tell whether the write happened.
- Symptoms: client retries; duplicate or missing event; ambiguous status.
- Required evidence: idempotency key; server-side record keyed by it; the state of the record.
- Detection: reconciliation of client attempts against server records by key.
- Impact: duplicate or missing governance records.
- Mitigation: idempotency keys with a stored result; a claim state (CLAIMED, CONSUMED, CONSUME_UNCERTAIN) that the client cannot silently assume; a rule that UNCERTAIN is resolved by read-back, not by retry alone.
- Residual risk: no result stored if the crash occurs before the record.
- Control type: design-level. Relevant to H8-J1, H8-J2, H8-J5 in 04.

### S10. Duplicate event or repeated execution
- Preconditions: retries without idempotency, or two workers claim the same item.
- Mechanism: duplicate processing.
- Symptoms: two events with the same content and different IDs; the same action executed twice.
- Required evidence: IDs, content hashes, executor identifiers.
- Detection: duplicate detection by content hash and by action ID.
- Impact: repeated consequence.
- Mitigation: single claim owner with expiry; idempotent execution keyed by action ID.
- Residual risk: claim expiry during a long action.
- Control type: design-level.

### S11. Missing, ambiguous, or conflicting HG records
- Preconditions: multiple HG records for one decision; or HG record missing.
- Mechanism: the system picks one, or treats absence as approval.
- Symptoms: conflicting statements about activation (lead items 6-7 are LOCAL_REPORT_ONLY examples of the sort of question this raises).
- Required evidence: all HG records by subject; a rule for conflict resolution.
- Detection: query for multiple open or conflicting records per subject.
- Impact: authority claimed without a valid record.
- Mitigation: conflict makes state UNKNOWN; no default to approval; escalate to HG.
- Residual risk: HG slow to respond.
- Control type: design-level.

### S12. Memory or historical experience treated as authority
- Preconditions: memory retrieval feeds decisions without a provenance or approval check.
- Mechanism: a past lesson is used as a rule.
- Symptoms: a decision cites memory as basis without an approved policy record.
- Required evidence: provenance on each memory item; approval status.
- Detection: decision records that cite memory IDs lacking an approval reference.
- Impact: the system acts on unapproved learning.
- Mitigation: memory items carry status; only approved policy records can be cited as authority.
- Residual risk: uncited influence.
- Control type: design-level.

### S13. A fallback path bypassing the intended gate
- Preconditions: a fallback path exists (for example, a direct write when the gate is unavailable).
- Mechanism: the gate is skipped when it fails.
- Symptoms: events written with no gate decision; fallback counters non-zero.
- Required evidence: list of all write paths to the event store; fallback conditions; logs of fallback use.
- Detection: path enumeration; a fallback counter alert; events without gate decision.
- Impact: ungoverned events.
- Mitigation: fail-closed on gate unavailability for governed types; explicit pending state for unavailable.
- Residual risk: a path not enumerated.
- Control type: NOT_VERIFIED for MoCKA. Design requirement only. Path analysis is in 05 Stage 5.

### S14. Inconsistent timestamps or misleading chronology
- Preconditions: mixed timestamp formats; clock differences; events recorded at different times than they occurred.
- Mechanism: ordering by timestamp produces a wrong story; time-based matching produces false identity.
- Symptoms: matches within a short window that are not the same event; events appearing before their causes.
- Required evidence: event ID and causal link; timestamp source and zone; monotonic sequence where available.
- Detection: timestamp format checks; causal link checks; sequence gaps.
- Impact: false conclusions about who did what and when.
- Mitigation: identity by ID; timestamp in one normalized form with source recorded; no time-only matching for identity.
- Residual risk: sequence source itself unreliable.
- Control type: design-level. Lead item 4 (0.5 second match) is LOCAL_REPORT_ONLY.

### S15. An audit export rewritten by another process during examination
- Preconditions: export file is writable by a process that updates it; no hash or anchor.
- Mechanism: the file changes between reads.
- Symptoms: modification time changes; contents differ between reads; no identified writer.
- Required evidence: hash at each read; writer identification (process, file handle); anchor outside the file.
- Detection: hash and mtime snapshot before and after; file-watch with writer identity.
- Impact: the examined evidence is not the evidence that existed.
- Mitigation: snapshot and hash before examination; examine copies; anchor hashes outside the store (RFC 9162 concept, SECONDARY).
- Residual risk: writer can rewrite the anchor too if in the same trust domain.
- Control type: design-level. Lead item 10 is LOCAL_REPORT_ONLY.

### S16. False closure caused by successful tests that do not establish runtime behavior
- Preconditions: tests run against a library or a mock, not the running process; or tests check that an option exists.
- Mechanism: test passes; runtime behavior not exercised.
- Symptoms: closure claimed; the running environment's behavior differs.
- Required evidence: test that exercises the running process and reads back the consequence.
- Detection: closure review requires runtime read-back; test classification (unit, integration, runtime).
- Impact: an unverified control is recorded as verified.
- Mitigation: closure requires the verification ladder (section D).
- Residual risk: runtime test not performed because it is unsafe.
- Control type: design-level.

## D. Verification ladder (brief Workstream D)

| Rung | Question answered | Evidence type | What it cannot show |
|---|---|---|---|
| 1. Design review | Is the design consistent with the principles? | Documents | That code implements it |
| 2. Implementation review | Does the code do what the design says? | Code at a fixed revision | That the running process uses that code or config |
| 3. Runtime observation | What does the running system do now? | Process state, logs, stored records, read-back | Why it does it |
| 4. Controlled testing | Does the control refuse or allow what it should, under known inputs? | Test with a recorded input and expected output, run after authorization | That untested paths behave the same |
| 5. Causal verification | Did this control cause this outcome? | Decision record, path analysis, bypass test, outcome record matched by ID | Future behavior after a config change |
| 6. Closure approval | Is the claim accepted as closed? | HG decision record, independent review | Anything not in the record |

Limits by method:
- Configuration inspection: shows what is set, not what is in effect.
- Static code review: shows what the code can do, not what it did.
- Runtime telemetry: shows what was emitted, not what was not emitted (absence is not proof).
- Integration testing: shows the tested paths only.
- Adversarial testing: shows the tested attacks only.
- Independent read-back: shows what the store returns now, not what it returned earlier, unless the earlier value is hashed and anchored.

Later configuration change: earlier evidence must be interpreted under the configuration that was effective at its time. This requires recording the effective configuration (or its hash) with each decision.

## E. Dependency relationships between controls

Dependency chain (each arrow means the left control is needed before the right one can be trusted):

1. Decision record with identifiers (per transition) -> everything else. Without IDs, reconciliation is by time and cannot establish identity.
2. Read-back after write -> persistence claims. Without it, REQUEST_ACCEPTED is the only state available.
3. Enforcement decision record citing the authorization reference -> causal efficacy. Without it, authorization and outcome cannot be linked.
4. Fail-closed or explicit-pending for unavailable gate -> no fallback bypass. Without it, S13 remains.
5. Anchor of event history outside the store -> tamper evidence of exports. Without it, S15 can be answered only by trust.
6. Memory with provenance and approval status -> memory cannot become authority (S12). This depends on 1 and on HG records being readable.

So the smallest high-impact set (section F) is not a list of independent controls. It is one chain: identifiers, read-back, enforcement record with authorization reference, and explicit uncertainty disposition.

## F. Smallest high-impact set (Workstream G)

1. Stable identifiers on every governance transition, carried from request to decision to authorization to event to outcome. Enables all reconciliation.
2. Read-back verification before any state is reported as persisted. Converts ok into a checked fact.
3. Enforcement decision record that cites the authorization reference and the effective mode, written before the response is returned. Enables causal attribution.
4. Explicit, non-default disposition for UNKNOWN, PENDING, CONSUME_UNCERTAIN, and gate unavailable, with an owner and expiry. Prevents silent approval or delegation.
5. Event history anchored outside the store, with hash checks on audit exports. Detects rewriting (S15).

Items 1 to 4 are design-level and need empirical demonstration. Item 5 is an add-on that strengthens detection.

## G. Mapping principles to failure modes and evidence

| Principle (brief section 2) | Failure modes that violate it | Evidence required |
|---|---|---|
| Evidence not equal to authority (2.1) | S12, S11 | Approval records for memory and policy |
| Configured not equal to connected (2.3) | S2 | Effective-config readout by process |
| Enforced not equal to verified (2.1) | S16 | Read-back and ladder rung 5 |
| UNKNOWN not equal to FALSE (2.1) | S4, S9, S11 | Explicit UNKNOWN state, not default |
| NOT FOUND not equal to ABSENT (2.1) | S3, S4, S14 | Search across all stores by ID, with search scope recorded |
| HG retains authority (2.2) | S1, S7, S11 | HG record with identifier; issuance check |
| Recorded not equal to used (2.1) | S12 | Use records linking decision to memory item |
| Non-decision is not delegation (2.5) | S9, S11, S13 | Explicit disposition for each uncertain state |
