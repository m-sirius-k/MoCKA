# Deliverable 4: HG Decision Package

Audit ID: MOCKA_INDEPENDENT_GOVERNANCE_AUDIT_20261009_001

Status: PREPARED, NOT DECIDED. This package makes no decision, adopts no contract, grants no authorization, and does not declare Runtime Verification or A1 Closure. Decision authority is named for each item. Items are not to be decided by this audit, by an AI component, or by silence (brief 2.5).

Evidence labels: as in 01 and 02. Lead items from brief section 4 are LOCAL_REPORT_ONLY.

## Priority order and dependencies

The items are not independent. The recommended order is:

1. Event persistence and audit-evidence requirements, and admission and quarantine semantics (these define what "persisted" and "quarantined" mean).
2. Enforcement activation authority and provenance (needs the persistence definitions to know what evidence the activation record must cite).
3. Authorization scope, freshness, identity, and expiry (needs 2).
4. Event Store requirements for recording HG decisions (needs 1 and 3).
5. H8-J1 (CLAIMED versus CONSUME_UNCERTAIN), then H8-J2 (M2 claim step), then H8-J5 (claim entry, owner, expiry, duplicate prevention). These depend on the idempotency and uncertainty rules from 1.
6. J-X4a (day-key source, timezone, overflow) and J-X4b (approved_at authority). Both depend on the timestamp contract, which depends on 1.
7. Evidence required for runtime causal efficacy and A1 Closure. Depends on all of the above.

Why this order: decisions in 5 and 6 can be made wrongly if the persistence definitions in 1 are not fixed first.

---

## Item 1. Enforcement activation authority and provenance requirements

Question: Who may activate enforcement, what record must exist, and how is the effective setting proven?

Options:
- A. Activation only by an HG record with identifier, scope, approved_at, expiry; the gate verifies that record at startup and on each decision. Benefit: direct link from authority to effect. Risk: more startup coupling. Dependency: needs item 4 (store requirements) for the record.
- B. Activation by configuration setting alone, with HG review after the fact. Benefit: simple. Risk: this is the pattern the leads describe (LOCAL_REPORT_ONLY); configured does not equal connected, and enforcement without authority. Not recommended by this audit.
- C. Activation by environment setting plus a verified HG record, with the effective mode recorded in every decision. Benefit: exposes S2. Risk: the setting can still differ between user and machine scopes.

Unresolved assumptions:
- Whether the gate reads the setting from user or machine scope (lead items 1-2; LOCAL_REPORT_ONLY).
- Whether HG-2 records dated 2026-10-04 and 2026-10-05 are the only activation-relevant records (lead items 6-7; LOCAL_REPORT_ONLY).

Benefits and risks summary: option A gives the strongest provenance; option C is acceptable only with A's record requirement.

Required evidence: HG records search across all ledgers; effective setting at each process; provenance of the setting change (who, when, from where); the gate's decision records showing mode.

Decision authority: Human Gate (きむら博士 per MoCKA governance). Not this audit.

## Item 2. Event admission and quarantine semantics

Question: What does the gate return and record for accept, reject, and quarantine? Is "ok" a persistence claim?

Options:
- A. Response states are explicit: REQUEST_ACCEPTED (receipt only), GATE_DECISION_RECORDED, PERSISTED. "ok" is retired as a persistence claim. Benefit: removes S4. Risk: client change needed.
- B. Keep "ok" but require quarantine responses to return a distinct status. Benefit: small change. Risk: ambiguity remains for other paths.
- C. Quarantine writes the payload or its hash plus decision ID before responding; response only after write. Benefit: S5 mitigated. Risk: quarantine write failure blocks the response (must be defined as fail-closed).

Unresolved: whether quarantine rows must hold payload or hash only (retention policy); whether the idempotency record may be written for a quarantine that did not persist (lead item 5, LOCAL_REPORT_ONLY).

Required evidence: the gate's response code paths; the schema of quarantine and idempotency records; the count of gate rows and events rows keyed by request ID (not by time).

Decision authority: HG for the semantics. Implementation authority separate (see item 7).

## Item 3. Event persistence and audit-evidence requirements

Question: What must be recorded, where, and how is it read back?

Options:
- A. Every governed transition writes a record with ID and read-back check before response (see 03, section F). Benefit: complete chain. Risk: write latency and failure coupling.
- B. Write the enforcement record to a separate append-only log, with the event store as a second copy. Benefit: independent of store failures (S3). Risk: two stores can disagree; reconciliation needed.
- C. Anchor hashes of the event history outside the store periodically (RFC 9162 concept, SECONDARY). Benefit: detects rewriting (S15). Risk: anchor location must be outside the same trust domain to be meaningful.

Unresolved: which store is primary; retention period; who may write the anchor.

Required evidence: read-back results by ID; anchor records; the reconciliation output for lead item 4 (LOCAL_REPORT_ONLY).

Decision authority: HG, with the store owner named by HG.

## Item 4. Authorization scope, freshness, identity, and expiry

Question: What fields must an authorization carry, and how are they checked?

Options:
- A. Required fields: authorization ID, HG record reference, actor identity, target, operation, scope, approved_at, expiry, single-use or multi-use flag. Enforcement checks all at the PEP. Benefit: S7 and S8 mitigated. Risk: more fields to maintain.
- B. Fewer fields with scope as free text. Risk: not checkable. Not recommended.

Unresolved: clock source for approved_at and expiry (see item 6); maximum validity period; revocation rule.

Required evidence: sample authorization records checked against the required field list; expiry tests after authorization (controlled testing, rung 4).

Decision authority: HG.

## Item 5. H8-J1: CLAIMED versus CONSUME_UNCERTAIN

Question: Is an item that was claimed but whose consumption result is unknown treated as CLAIMED (still owned) or as CONSUME_UNCERTAIN (requires reconciliation before reuse)?

Options:
- A. Keep CLAIMED until the consumer confirms; expiry returns it to available. Risk: a consumed item may be reused after expiry (duplicate effect). 
- B. Introduce CONSUME_UNCERTAIN as a distinct state that blocks reuse until read-back resolves it. Benefit: no silent reuse (S9, S10). Risk: items stuck if read-back never occurs; needs an owner for resolution.
- C. Treat unknown as consumed. Not recommended: converts uncertainty into a fact.

Unresolved: whether the consumer can always read back its result; what owner resolves CONSUME_UNCERTAIN.

Required evidence: consumer records with item ID and result; read-back method; list of items currently CONSUME_UNCERTAIN (if any; status NOT_VERIFIED).

Decision authority: HG (governance rule); implementation owner separate.

Dependency: item 2 (what "persisted" means) and item 9 below.

## Item 6. H8-J2: whether M2's claim step is accepted or must be redesigned

Question: Is the claim step in M2 acceptable as currently designed, or must it be redesigned?

Note: The design of M2 is not in this audit's evidence set. This item cannot be assessed from external research. It requires the M2 specification and its implementation (LOCAL_REPORT_ONLY until the specification is supplied).

Options:
- A. Accept the claim step as-is. Acceptable only if it has an owner, expiry, and duplicate-prevention rule (item 7).
- B. Accept with conditions: the claim step must write a claim record before the consumer starts, and the consumer must read back the claim record. 
- C. Redesign: separate claim from consume, with CONSUME_UNCERTAIN as a state (item 5).

Required evidence: M2 specification text; claim record schema; a test that double-claim is refused (controlled testing, after authorization).

Decision authority: HG.

## Item 7. H8-J5: claim entry, owner, expiry, and duplicate prevention

Question: What must a claim entry contain, who owns it, when does it expire, and how is a duplicate claim prevented?

Options:
- A. Claim entry with item ID, owner identity, claim time, expiry, and a unique claim ID; duplicate prevention by a uniqueness constraint on item ID for active claims. Benefit: S10 mitigated. Risk: uniqueness constraint must be enforced by the store, not by convention.
- B. Claim without expiry, released by the owner. Risk: a crashed owner holds the item forever. Not recommended.
- C. Claim with expiry and a renewal step. Benefit: handles long actions. Risk: renewal can be used to hold an item indefinitely; renewal must be bounded.

Unresolved: expiry duration; whether renewal is allowed; who may force-release (must not be an AI component by default).

Required evidence: store constraint definition; a duplicate-claim test (controlled testing); expiry behavior test.

Decision authority: HG; the owner identity rule is part of the authority design.

## Item 8. J-X4a: day-key source, timezone, and overflow semantics

Question: How is the day key for a record derived: from which clock, in which timezone, and what happens at a day boundary or overflow?

Options:
- A. Day key from the event's recorded UTC timestamp, converted to a fixed zone (state which). Benefit: deterministic. Risk: a local-zone reader may disagree.
- B. Day key from the server's local clock. Risk: depends on machine configuration (a machine-level value was reported empty in lead item 2; LOCAL_REPORT_ONLY) and daylight changes.
- C. Day key from a monotonic sequence number, with the day derived for display only. Benefit: no clock dependence. Risk: sequence source must be reliable.

Overflow: define behavior when a day holds more records than the key format allows, and when an event timestamp is out of range or mixed format (S14).

Unresolved: timezone of record; whether mixed timestamp formats exist in the store (not established).

Required evidence: sample of timestamp formats in the store; the code that derives the day key; test around midnight UTC and at timezone boundaries.

Decision authority: HG for the rule; store owner for implementation.

## Item 9. J-X4b: approved_at authority and timestamp-setting contract

Question: Who sets approved_at, from which clock, and can a later process overwrite it?

Options:
- A. approved_at is written only by the HG recording step, from the HG clock source, and is immutable after write. Benefit: S8 and S11 mitigated. Risk: HG recording step must be reliable.
- B. approved_at set by the issuance component from its clock. Risk: issuance can backdate approval. Not recommended.
- C. approved_at set by the HG UI from the browser clock. Risk: client clock is untrusted. Not recommended.

Unresolved: the authoritative clock; how an HG record is corrected (supersession, not overwrite).

Required evidence: the HG record write path; the clock source; a test that a second write cannot change approved_at.

Decision authority: HG.

## Item 10. Event Store requirements for recording HG decisions

Question: How must HG decisions be recorded in the event store so that they are verifiable?

Options:
- A. HG decision record written to the Decision Ledger and referenced by an event, with read-back before the decision is considered recorded. Benefit: verifiable. Risk: two records must agree.
- B. HG decision recorded only in the event store. Risk: depends on the store's integrity, which is the thing being audited.
- C. HG decision recorded in a separate append-only ledger with hash anchor (item 3, option C). Benefit: strongest against rewriting. Risk: more infrastructure.

Unresolved: which of the Ledger and the event store is authoritative for HG decisions; whether a missing HG record can be reconstructed from the event store.

Required evidence: Ledger contents for the relevant HG records (lead items 6-7 are LOCAL_REPORT_ONLY); read-back; cross-reference against event store by ID.

Decision authority: HG.

## Item 11. Evidence required for runtime causal efficacy and A1 Closure

Question: What must be shown before MoCKA can declare runtime causal efficacy or A1 closure?

Required (minimum) evidence, all by identifier:
1. Effective policy at execution time, read from the running process.
2. Authorization matches actor, target, operation, scope, and is within expiry.
3. Enforcement decision record cites the authorization reference.
4. Bypass path enumerated and shown absent or blocked by controlled test.
5. Outcome record matched to the action ID.
6. Later configuration change shown not to alter the interpretation of earlier evidence (effective-config hash recorded per decision).
7. Independent review separate from the change author.

Options for closure criteria:
- A. Strict: all seven, each with primary evidence. Benefit: credible. Risk: long timeline.
- B. Staged: closure in parts (for example, activation provenance first, then persistence, then causal efficacy). Benefit: earlier partial closure. Risk: partial closure can be read as full closure; must be labeled.

Unresolved: whether a controlled test in the production environment is permitted and under which authorization (see 05 Stage 7).

Decision authority: HG. A1 closure is HG-owned. This audit does not declare it.

---

## Summary table for HG

| # | Item | Authority | Blocks | Required evidence (summary) |
|---|---|---|---|---|
| 1 | Enforcement activation | HG | 2, 3, 11 | HG record search, effective-setting provenance |
| 2 | Admission and quarantine semantics | HG | 3, 5 | Gate code paths, record schemas, ID-keyed reconciliation |
| 3 | Persistence and audit evidence | HG (store owner named) | 10, 11 | Read-back, anchors, reconciliation |
| 4 | Authorization scope, freshness, identity, expiry | HG | 11 | Record schema check, expiry tests |
| 5 | H8-J1 CLAIMED vs CONSUME_UNCERTAIN | HG | 7 | Consumer records, read-back method |
| 6 | H8-J2 M2 claim step | HG | 7 | M2 specification (not available) |
| 7 | H8-J5 claim entry, owner, expiry | HG | none | Store constraint, duplicate test |
| 8 | J-X4a day key and timezone | HG (rule), store owner | none | Timestamp format sample, boundary tests |
| 9 | J-X4b approved_at authority | HG | 11 | HG write path, clock source |
| 10 | Event Store requirements for HG decisions | HG | 11 | Ledger and store cross-reference |
| 11 | Evidence for causal efficacy and A1 Closure | HG | closure | Seven-point evidence list |

## Items this package cannot assess

- H8-J2 (needs the M2 specification).
- Whether any lead item is true (all LOCAL_REPORT_ONLY).
- Whether any current state is correct. That requires local evidence (see 05).
