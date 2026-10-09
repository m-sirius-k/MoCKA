# Deliverable 5: Local Audit Execution Blueprint (for KUROKO PC)

Audit ID: MOCKA_INDEPENDENT_GOVERNANCE_AUDIT_20261009_001

This is a plan. It is not an instruction to modify the local environment. Stages 0 to 5 are read-only. Stage 6 and 7 require separate written authorization. Every stage records what was read, when, and its hash.

Rules for all stages:
- Snapshot before reading: copy-on-read or hash, never edit in place.
- Identify records by ID, never by time alone (brief 2.1).
- Each finding is labeled LOCAL_PRIMARY (observed directly) or LOCAL_REPORT (carried over from an earlier report). Do not merge them.
- Do not run the gate, the event writer, the MCP server, or any hook in write mode during Stages 0 to 5.
- Stop and report on any unexpected write, any change to a file during snapshot, or any inconsistency between two stores that cannot be resolved by ID.

## Stage 0. Evidence preservation and baseline

- Prerequisites: none beyond KUROKO PC access. Written start-of-audit authorization from HG (recommended).
- Mode: read-only.
- Actions: hash and copy (to a separate evidence folder) the event store files, the decision ledger, the idempotency store, quarantine store, any events_latest JSON, configuration files, hook scripts, and the audit report. Record file size, mtime, and SHA-256. Record the current UTC time and the machine clock offset.
- Required evidence: the manifest with hashes; the timestamp of the snapshot; the list of files not found (recorded as NOT FOUND, not ABSENT).
- Stop conditions: a file changes during snapshot; a store cannot be opened read-only.
- Exit criteria: manifest complete and self-consistent (re-hash of copies matches).

## Stage 1. Enforcement provenance

- Prerequisites: Stage 0 complete.
- Mode: read-only.
- Actions: record the effective value of the enforcement setting for each scope (process, user, machine) with the source of each value. Identify which process reads the setting, its start time, and its environment. Record any change history available from the OS (registry, system event logs) without modifying them. Search all HG ledgers and decision records for activation-related records (2026-10-04 onward, and earlier).
- Required evidence: scope-by-scope values with source; process start time; list of HG records found, with IDs.
- Stop conditions: a value cannot be read without elevation; a setting appears in a scope that the audit did not expect.
- Exit criteria: for each scope, the value and its source are known or marked UNKNOWN with reason.

## Stage 2. Event and quarantine reconciliation

- Prerequisites: Stages 0 and 1.
- Mode: read-only queries.
- Actions: for the 84 gate rows reported (lead item 4), obtain each row's request ID or event ID. Look up each ID in events, quarantine, idempotency, and any other store. Do not match by time alone. Record for each row: found in events (ID), found in quarantine (ID), found in idempotency (key), or not found in any store. For any row where the gate returned ok, record the exact response. Check whether any quarantine decision since 2026-10-05 23:12 UTC was written with a mode value, and what that value was.
- Required evidence: a per-row table with IDs and the four lookups; response payloads for ok-with-no-event rows; the mode values.
- Distinguish the four cases: stored elsewhere (found by ID in another store), rejected (decision record with reason code), unknown outcome (request record and key with no decision or persistence), and lost (none of the above, with the request evidence still present).
- Stop conditions: a row maps to more than one ID; a store returns different results on two reads within the audit window (possible rewrite, see scenario S15); a lookup requires writing to a store.
- Exit criteria: each row has one of the four labels with its evidence; counts reported; no row labeled "lost" without the request-side evidence.

## Stage 3. Authorization and Ledger reconciliation

- Prerequisites: Stage 2 (so that IDs of decisions are known).
- Mode: read-only.
- Actions: for each gate decision that cites an authorization or mode, find the authorization record and the HG record it refers to. Check approved_at, expiry, scope. Record any decision with no authorization reference, or whose reference does not resolve. Check the Decision Ledger for consistency with the event store on HG records (for example HG-2 records dated 2026-10-04 and 2026-10-05, lead item 6).
- Required evidence: a table of decision ID -> authorization ID -> HG ID -> resolution status.
- Stop conditions: a reference resolves to two different records; the ledger file is modified during the stage.
- Exit criteria: all references resolved or labeled UNRESOLVED with reason; lead items 6-7 checked against the ledger by ID.

## Stage 4. Runtime path and bypass analysis

- Prerequisites: Stage 1 (which process reads which setting).
- Mode: read-only (code and configuration reading; process observation). No test events.
- Actions: enumerate every write path to the event store: the gate, direct writers, fallback branches, hook-based writers, and any non-hook writer. For each, record whether it passes through the gate and what happens if the gate is unavailable. For lead item 8 (hook-signature events last observed 2026-06-19; non-hook writers continued to 2026-10-01): identify the writers and their source identifiers for both periods, and record whether the change in writers is explained by configuration, code, or the hook path being disabled. Do not infer the cause; record the evidence.
- Required evidence: the write-path list with file and line references; the fallback conditions; the writer identifiers with time ranges.
- Stop conditions: a path that writes to the store without a recorded identifier (report immediately); a path that cannot be read.
- Exit criteria: each write path labeled GATED, UNGATED, or UNKNOWN with evidence.

## Stage 5. Specification-to-implementation mapping

- Prerequisites: Stages 1 to 4.
- Mode: read-only.
- Actions: map each governance requirement (03, transition T1 to T8 and persistence states) to the specification text and the implementing code. Record gaps: specified but not implemented, implemented but not specified, specified differently. Include the H8-J1, H8-J2, H8-J5, J-X4a, J-X4b items: their specification text and current status as recorded locally (LOCAL_REPORT, since the local report marks them unresolved or conditional).
- Required evidence: a mapping table with file and section references.
- Stop conditions: the specification is missing for an item that the local report treats as settled.
- Exit criteria: each item has a mapping status; the M2 claim step (H8-J2) specification is present or its absence is recorded.

## Stage 6. Controlled verification (only after separate written authorization)

- Prerequisites: Stages 0 to 5 complete; HG written authorization naming the test scope, the test data, the environment, and the stop conditions; a rollback plan that does not rely on the event store being intact.
- Mode: write-enabled in a test environment only. Production stores must not be written. If the test environment is not separate, this stage does not proceed.
- Actions: run defined tests for: enforcement mode read by the process (test decision with known mode); authorization expiry (expired test authorization refused); scope mismatch refused; quarantine response carries a payload hash and decision ID; read-back after a test write; duplicate claim refused (if H8-J5 is adopted); bypass attempt refused when gate is unavailable (fail-closed, if adopted).
- Required evidence: test inputs, expected outputs, actual outputs, and read-back by ID for each test; the test environment identity; the hash of production stores before and after (must be unchanged).
- Stop conditions: any production store hash changes; any test write appears in production; any test result cannot be read back.
- Exit criteria: each test has a recorded result labeled CONTROLLED_TEST, and the production store hashes are unchanged.

## Stage 7. Causal verification

- Prerequisites: Stage 6 (or equivalent controlled evidence) and Stage 4 (bypass analysis).
- Mode: read-only analysis of records produced by earlier stages.
- Actions: for a chosen set of actions, link: effective policy at the time (from Stage 1 and per-decision effective-config records), authorization (Stage 3), enforcement decision record (Stage 2), outcome record (if any), and the later configuration history. Confirm that the later configuration did not change the interpretation of earlier evidence.
- Required evidence: the linked chain per action, by ID; explicit list of links that are missing.
- Stop conditions: a link cannot be established by ID; a required record is missing (recorded as NOT FOUND; does not establish ABSENT).
- Exit criteria: for each sampled action, the chain is complete or the gap is named. The audit does not declare causal efficacy; the result goes to HG.

## Stage 8. Independent closure review

- Prerequisites: Stages 0 to 7; a reviewer who did not perform Stages 0 to 7 or the change under review.
- Mode: read-only.
- Actions: review all stage outputs against the seven-point list in 04, item 11. Check that each claim cites its evidence label. Check that no LOCAL_REPORT item is presented as LOCAL_PRIMARY. Check that no external research is presented as local evidence.
- Required evidence: the reviewer's checklist with results; HG decision record for closure (not produced by this audit).
- Stop conditions: any claim without evidence; any UNKNOWN presented as FALSE or as approved.
- Exit criteria: review record complete; closure decision is made only by HG.

## Summary of modes

| Stage | Mode | Needs separate authorization |
|---|---|---|
| 0 Preservation | Read-only | Recommended |
| 1 Enforcement provenance | Read-only | No (but HG recommended) |
| 2 Event and quarantine reconciliation | Read-only | No |
| 3 Authorization and Ledger reconciliation | Read-only | No |
| 4 Runtime path and bypass | Read-only | No |
| 5 Spec-to-implementation mapping | Read-only | No |
| 6 Controlled verification | Write (test environment only) | Yes |
| 7 Causal verification | Read-only analysis | No (uses earlier outputs) |
| 8 Independent closure review | Read-only | Closure decision: HG only |
