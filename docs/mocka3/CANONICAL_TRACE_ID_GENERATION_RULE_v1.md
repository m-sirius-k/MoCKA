# MoCKA canonical_trace_id Generation Rule v1 (Draft)

Document ID: CANONICAL_TRACE_ID_GENERATION_RULE_v1
Version: 1.0.0
Status: Draft -- no parameter fixed, no algorithm finalized, no schema/data change applied
Created: 2026-06-23
Phase: 4, Step 3
Depends on: Step 2 decision (Hybrid 3-layer model), E20260623_4858243709348

---

## 1. Layer definitions (carried over from Step 2, unchanged)

```
Layer 1 (base)       : session_id as-is, untouched
Layer 2 (provisional) : gap-threshold or event-boundary candidate splits
Layer 3 (semantic)    : re-clustering of Layer 2 candidates into final units
canonical_trace_id    : derived from Layer 3 final cluster
```

## 2. Layer 2: provisional segmentation (parameters open)

```
for each session_id, sort events by when_ts
new_segment_start whenever:
    gap_to_previous > GAP_THRESHOLD_SECONDS   [value not fixed -- candidates: 300, 900, 1800]
    OR an explicit boundary marker is present  [only applies to title-tagged
                                                 CHANGE_START/CHANGE_DONE events,
                                                 confirmed inapplicable to
                                                 automated-batch sessions per
                                                 CANONICAL_SESSION_BOUNDARY_FINDINGS_v1]
```

This produces `provisional_segment_id` per event -- a candidate, not a final
cluster. `GAP_THRESHOLD_SECONDS` is left as an open parameter; no value is
selected by this document.

## 3. Layer 3: semantic reclustering (method open)

Layer 2 segments are inputs to a reclustering step that may merge or split
them based on three stated criteria: operational-purpose consistency,
causal continuity, state-transition consistency. This document does not
define how those criteria are evaluated computationally. Three candidate
methods are listed, none selected:

| Method | Description | Cost / Risk |
|---|---|---|
| Rule-based | Merge adjacent Layer-2 segments if `what_type` (Taxonomy value) matches and `related_event_id` chains connect them | Cheap, deterministic, but limited to mechanical signals already in the schema; may under-merge true intentions that don't share `what_type` |
| LLM-judged | An AI actor reads segment titles/descriptions and judges whether two adjacent segments belong to one operational purpose | Captures intent better, but non-deterministic across runs/models -- conflicts with Event Foundation v1 Principle P5 ("Normalization must be deterministic") unless the judgment itself is recorded and frozen per segment, not re-run |
| Human-reviewed | A human (Human Gate) manually confirms or edits proposed cluster boundaries before they are written | Highest confidence, not scalable to 12,927 historical events without significant manual effort; realistic only for new events going forward, or a small backfill sample |

## 4. canonical_trace_id derivation (draft formula, not fixed)

```
canonical_trace_id = sha256(session_id + ":" + layer3_cluster_index)[:16]
```

Open issues with this draft formula:
- `layer3_cluster_index` presumes Layer 3 clustering already ran and
  produced a stable, reproducible ordering -- not yet guaranteed under the
  LLM-judged method (Section 3) without additional determinism controls.
- Events with no `session_id` (93.4% of the dataset, per
  CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1 Section 1) have no input to this
  formula at all. A fallback rule is still undefined (this gap was already
  flagged as Open Question 1 in that document and remains open here).

## 5. Explicit non-decisions in this draft

- `GAP_THRESHOLD_SECONDS` value: not fixed.
- Layer 3 reclustering method (rule-based / LLM-judged / human-reviewed /
  some combination): not selected.
- Fallback for the ~93% of events without `session_id`: not defined.
- Whether this is applied retroactively to all 12,927 historical events or
  only forward from a cutoff date: not decided.
- Write target (`events_v2` column vs. new sidecar table): not decided.

## 6. Required before any implementation

Per AUDIT_TRACE_LAYER_RULES_v1.md Section 4 and the Phase 3 closure
decision (E20260623_747052560dd91), and consistent with every prior
document in this chain, this draft authorizes nothing. Before any code is
written or any value is computed and stored:
1. `GAP_THRESHOLD_SECONDS` must be fixed by Human Gate.
2. A Layer 3 method must be selected by Human Gate (Section 3).
3. The fallback rule for `session_id`-less events must be defined.
4. The retroactive-vs-forward-only scope must be decided.
5. The write target (additive field on `events_v2`, per Event Foundation v1
   Section 9, vs. a new table) must be decided.

This document closes Step 3 as a draft. Step 4 (per the original Phase 3
roadmap) would be the actual Human Gate sign-off on points 1-5 above,
followed by implementation -- not part of this document.
