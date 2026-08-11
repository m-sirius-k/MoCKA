# TODO_452: Event Store Cross-Client Visibility - Evidence Repair Task Definition

**Date**: 2026-08-11
**Phase**: Task Definition Only (Execution BLOCKED - Requires separate Human Gate)
**Related**: TODO_450 Phase A (Observation), TODO_451 (Institutional Decision)
**Status**: NOT STARTED

## Task Scope Definition

This document defines the repair investigation scope based on Phase A observations. Actual repair execution requires separate institutional gate approval (Human Gate Review).

## Investigation Hypothesis Space (Not Causal Determination)

Based on Phase A observation that event E20260712_332720944eac1 was:
- NOT VISIBLE to S02 at 2026-07-12T07:09:55Z
- VISIBLE to R02 at same timestamp (implied by Phase A categorization)
- VISIBLE to Haiku at 2026-08-11T[current]

Repair Task may examine:

### Hypothesis Category A: Query Path Variation
- Did S02 and R02 use different query syntax?
- Did read path implementations diverge?
- Are query parameter normalizations inconsistent?

### Hypothesis Category B: Permission Model
- Did S02 have restricted visibility scope?
- Do actor/session credentials affect event visibility?
- Are permission boundaries documented vs. implemented?

### Hypothesis Category C: Event Store State
- Was event actually stored at query time (2026-07-12T07:09:55Z)?
- Did asynchronous write latency cause transient invisibility?
- Are write-after-read consistency guarantees documented?

### Hypothesis Category D: Session/Actor Metadata
- Can S02 actor identity be determined from historical logs?
- Are session lifecycle boundaries relevant to visibility?
- Do MCP server session tokens affect store access?

### Hypothesis Category E: Time-Dependent Store Semantics
- Did Event Store filtering rules change between 2026-07-12 and 2026-08-11?
- Are TTL/expiration semantics involved?
- Do archive/active layer boundaries affect retrieval?

## Repair Work Items (Definition Only)

**Work Item R-01: Historical Audit of S02 Session**
- Scope: Identify S02 actor identity from available logs
- Method: Search session records, authentication logs, MCP server traces
- Success Criteria: Actor identity determined OR confirmed unrecoverable
- Estimated Effort: 2-4 hours
- Status: DEFINITION ONLY - NOT STARTED

**Work Item R-02: Query Path Reconciliation**
- Scope: Obtain query patterns used by R02 vs S02 during observation window
- Method: Git log (R02 likely Claude-code-related), event traces, MCP logs
- Success Criteria: Query syntax/parameters documented for both actors
- Estimated Effort: 2-4 hours
- Status: DEFINITION ONLY - NOT STARTED

**Work Item R-03: Event Store Write Latency Verification**
- Scope: Verify event write-to-read consistency timeline
- Method: Check event timestamps, creation times, first-read times
- Success Criteria: Latency profile documented, transient visibility ruled in/out
- Estimated Effort: 1-2 hours
- Status: DEFINITION ONLY - NOT STARTED

**Work Item R-04: Permission Model Audit**
- Scope: Check if S02 actor/session has documented visibility restrictions
- Method: Review permission rules, RBAC settings, scope definitions
- Success Criteria: Permission model for S02 documented OR permission checks ruled out
- Estimated Effort: 2-3 hours
- Status: DEFINITION ONLY - NOT STARTED

**Work Item R-05: Store Semantics Documentation**
- Scope: Verify Event Store access guarantees (read-after-write, ordering, filtering)
- Method: Review storage layer design docs, MCP API contracts
- Success Criteria: Documented guarantees vs. observed behavior aligned OR divergence identified
- Estimated Effort: 3-5 hours
- Status: DEFINITION ONLY - NOT STARTED

## Repair Gate Criteria

**Before Repair Execution, the following must be confirmed**:

1. Work Item Scope: Are R-01 through R-05 the complete set, or are additional hypotheses needed?
2. Investigation Authority: Which institutional body (博士, Human Gate, etc.) approves each work item?
3. Evidence Capture: How should findings be recorded (Decision Ledger vs. Event Store vs. Git)?
4. Genesis v1.1: Is current observation sufficient for Genesis formulation, or required for Repair findings?
5. MCP Ledger Sync: Should Repair findings be written to MCP Ledger before Git commit?

## Repair Execution Prohibitions

**The following are EXPLICITLY PROHIBITED during Repair execution phase**:

- Changes to Event Store (read-only access only)
- Changes to MCP Ledger (observation capture only, not modification)
- Retroactive changes to TODO_450 observations
- Creation of new Event records (use existing Event Store only)
- Genesis v1.1 formalization (hold as hypothesis/hypothesis-set only)
- Seal/Tag operations (Durable History via Git commit only)
- Blame assignment or actor accountability determination
- Root cause declaration (findings must remain in "hypothesis" framing)

## Handoff to Phase B (TODO_451 Implementation)

Once Repair Task definition is confirmed (this document), TODO_451 institutional decision becomes executable. TODO_451 will:

1. Approve which Work Items proceed
2. Authorize evidence recording method
3. Define commitment mechanism (MCP → Git path)
4. Establish Repair Branch operation rules

This document is the DEFINITION GATE. Actual execution awaits separate institutional approval.

---

**Phase Sequence**:
- TODO_450: PASS (Observation recorded)
- TODO_451: EXECUTION READY (Repair strategy decision - institutional judgment required)
- TODO_452: DEFINITION ONLY (Repair work items specified, execution requires separate gate)

**Related Records**:
- Decision ID: DC_20260712_011 (Observation approval)
- Event IDs: E20260712_5642006155997, E20260712_4485078319501, E20260712_105311599b4a9, E20260712_332720944eac1
- Integrity Records: Maintained in MCP Ledger (no Git sync in this phase)

---

*Generated by MoCKA execution protocol (TODO_452 Definition Phase)*
*Classification: Task Definition / Architecture Investigation*
*Execution Status: BLOCKED - awaiting separate Human Gate review*
