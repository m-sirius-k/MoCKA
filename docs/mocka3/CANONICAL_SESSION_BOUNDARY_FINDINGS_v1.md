# MoCKA Canonical Session Boundary Findings v1

Document ID: CANONICAL_SESSION_BOUNDARY_FINDINGS_v1
Version: 1.0.0
Status: Draft -- empirical findings only, no boundary rule selected, no schema/data change applied
Created: 2026-06-23
Phase: 4, Route A (session_id basis), Step 1
Decision context: [CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1.md](CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1.md) Candidate 2, selected at E20260623_271756668258f

---

## 1. Question being answered

Route A treats `session_id` as the base cluster for `canonical_trace_id`.
Before accepting "one `session_id` = one canonical unit," it must be checked
whether a `session_id` cluster is internally homogeneous enough to represent
one coherent unit, or whether it actually bundles multiple unrelated runs
under one label.

## 2. Method

Read-only inspection of the largest `session_id` cluster in the dataset,
`SESSION_20260622_072653` (61 events, the largest of 79 distinct sessions
per CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1 Section 1).

## 3. Findings

| Metric | Value |
|---|---|
| Event count | 61 |
| Distinct `who_actor`/actor type in this cluster | 1 (`claude_mcp` only) |
| Time span | 2026-06-21T22:27:00 -- 2026-06-22T02:18:30 (3h 51m) |
| Smallest gap between consecutive events | 5.4 seconds |
| Largest gap between consecutive events | 5,113 seconds (~85 minutes) |
| Gaps exceeding 5 minutes | 9 |

Sample titles observed in this cluster (translated/normalized for this
report): `BEE_DAILY_SCAN`, `HEALTH_FAIL`, `TECH_NO_CHANGE_INFO: Anthropic
API Release Notes`, `TECH_NO_CHANGE_INFO: Claude Code Release Notes`,
`TECH_NO_CHANGE_INFO: Chrome Extensions MV3`, `TECH_NO_CHANGE_INFO: Stripe
Changelog`, `TECH_NO_CHANGE_INFO: MCP Specification`,
`RISK_SCORE_UPDATED: TIC risk score recalculated`.

## 4. Interpretation

This `session_id` cluster is not a single human-driven intention. It is a
**recurring automated monitoring batch** (TIC health checks, BEE daily scan,
tech_watcher polling multiple external sources) spanning nearly 4 hours,
with internal gaps of up to 85 minutes between sub-runs. The events inside
it are homogeneous in actor (`claude_mcp`) but heterogeneous in purpose --
they represent several distinct automated checks, not one decision or one
TODO.

This means: at least for this cluster, `session_id` alone is **coarser than
a canonical intention unit**, and contains internal structure (multiple
sub-runs separated by multi-minute gaps) that a canonical-unit definition
would need to either preserve (sub-segment) or deliberately collapse
(treat the whole daily batch as one canonical unit).

This finding is consistent with the caveat already raised in
CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1 Candidate 2 ("coarser than 'one
intention' by default... requires a sub-segmentation rule"). It is now
backed by a concrete example rather than a general concern.

## 5. Boundary rule candidates (not selected)

| Candidate | Mechanism | Open issue |
|---|---|---|
| Gap-based split | Within one `session_id`, start a new canonical unit whenever the gap to the previous event exceeds a threshold (e.g. 5 or 30 minutes) | Threshold is arbitrary; 9 gaps >5min exist in this single cluster, so the choice of threshold directly determines how many canonical units this one session produces |
| CHANGE_START/CHANGE_DONE title pairing | Use the informal `CHANGE_START:` / `CHANGE_DONE:` title convention (already in active use, e.g. this very session's own events) as explicit boundary markers | This convention is only used for file-change events (per MoCKA's くろこ起動プロトコル); the sampled cluster (automated monitoring) uses neither marker, so this rule would not apply to it at all |
| No split (session = canonical unit) | Treat the entire `session_id` span as one canonical unit regardless of internal gaps or sub-run count | Simplest, but explicitly does not produce intention-level granularity; would only be acceptable if the design goal is relaxed from "one intention" to "one batch/session" |

This document does not select among these. Step 2 (per
CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1 Section 5, Open Question 1 and the
Route A roadmap) requires Human Gate input on which granularity is actually
wanted before a boundary rule can be fixed.

## 6. Non-Goals (explicit)

- No boundary rule is selected.
- No `canonical_trace_id` value is computed or written anywhere.
- No claim is made about whether other (non-largest) `session_id` clusters
  share this same automated-batch composition; only one cluster was sampled.
