# MoCKA canonical_trace_id Design Proposal v1

Document ID: CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1
Version: 1.0.0
Status: Draft -- candidates only, no candidate selected, no schema/data change applied
Created: 2026-06-23
Phase: 4 (Canonical Meaning Layer), opened at E20260623_0077448195363
Constrained by: [AUDIT_TRACE_LAYER_RULES_v1.md](AUDIT_TRACE_LAYER_RULES_v1.md) Section 4
  ("canonical_trace_id ... is explicitly undefined and out of scope" of that
  document; this proposal is the work that document anticipated, not a
  violation of it)

---

## 0. Status

This document selects no option. It exists to give Human Gate concrete
candidates instead of an abstract design space. Selecting a candidate, and
authorizing any write, requires a separate, explicit Gate decision.

## 1. New empirical input: `session_id`

While drafting this proposal, the `events` table was checked for an existing
column that already behaves like a working grouping key, as a sanity check
on what "a key that actually groups events" looks like in this dataset.

```
total events: 12,927
session_id filled: 850 (6.6%)
distinct session_id values: 79
top groups: SESSION_20260622_072653 (61 events), SESSION_20260621_075357
(58), SESSION_20260623_064700 (50), SESSION_20260617_165054 (47),
SESSION_20260622_183747 (38)
```

Unlike `trace_id` (0 of 1,308 values group meaningfully, per Classification
Rules v1), `session_id` genuinely groups multiple events under one value.
Its granularity is **conversation/session**, not **intention/TODO** -- a
session can contain many TODOs, and the design goal (one key per intention)
is finer-grained than this. It is included here as evidence that a working
grouping mechanism is possible in this schema, and as a candidate input for
Option 2 below.

## 2. Connection mode (must be decided regardless of which generation
   principle is chosen)

| Mode | Description | Consequence |
|---|---|---|
| REFERENCE | `canonical_trace_id` points to a row in a separate "intent" table (new table, e.g. `intents`) that holds the canonical record of one TODO/intention | Requires a new table; events become joinable to intents; intent lifecycle (created/closed) can be tracked independently of any single event |
| DERIVED | `canonical_trace_id` is computed deterministically from fields already on the event row (e.g. hash of TODO_id + first-seen date), with no separate table | No new table; cannot represent intent-level metadata (e.g. "this intention is still open") beyond what's inferable from the events that carry the same derived value |

This proposal does not choose between REFERENCE and DERIVED. Each generation
principle below is compatible with either mode.

## 3. Generation principle candidates

### Candidate 1: TODO_id + first-seen timestamp hash

```
canonical_trace_id = sha256(TODO_id + first_seen_event.when_ts)[:16]
```

- Matches the original design intent stated at the start of this session
  (intention-spine keyed by TODO unit).
- Requires a reliable `TODO_id` to be extractable per event. Current schema
  has no dedicated `todo_id` column; TODO references currently appear
  informally in `title`/`tags`/`description` text (e.g. "TODO_322"). A
  reliable extraction rule (regex on `tags`, or a new mandatory field) would
  need to be defined separately.
- Events with no associated TODO (ad hoc fixes, exploratory sessions) would
  have no canonical_trace_id under this rule, unless a fallback principle is
  also defined.

### Candidate 2: session_id-based, narrowed by time-window or what_type

```
canonical_trace_id = session_id + "_" + sequence_number_within_session
  (sequence boundary defined by a gap rule, e.g. >30min between events,
   or a CHANGE_START/CHANGE_DONE pair boundary)
```

- Builds on the one mechanism in this dataset (`session_id`) that is
  empirically proven to group multiple events (Section 1).
- Coarser than "one intention" by default (a session can span multiple
  TODOs); requires a sub-segmentation rule to reach intention-level
  granularity. The CHANGE_START/CHANGE_DONE title convention (used
  informally throughout this very session, e.g. E20260623_84148446346f2 /
  E20260623_891376784af46) is a candidate boundary marker, since it is
  already in active use without being formally specified anywhere.
- Only covers the 6.6% of events that currently have `session_id` set;
  events without `session_id` need a fallback.

### Candidate 3: judgement_reason-table-anchored

```
canonical_trace_id = judgement_reason.event_id  (re-used as the anchor,
  not re-derived)
```

- Leverages the existing `judgement_reason` table (TODO_194), which already
  links a decision back to one `event_id` with `reason`/`tension`/`tags`.
- Only applies to events that went through a recorded judgement -- narrower
  coverage than Candidates 1 or 2, but highest confidence where it does
  apply (it's an existing, audited mechanism, not a new heuristic).

## 4. Non-interference with Audit Trace Layer

All three candidates are additive only:
- None of them write to, read for derivation, or depend on the existing
  `trace_id` column's *value* as meaningful input (consistent with
  AUDIT_TRACE_LAYER_RULES_v1 Section 1 -- `trace_id` itself stays out of any
  new semantic logic).
- The new field, under any candidate, would target `events_v2`
  (per Event Foundation v1 Section 9: new writes go to `events_v2` once
  adopted) or a net-new sidecar table -- never an `UPDATE` to `events`.

## 5. Open questions for whichever candidate Human Gate considers

1. Fallback rule for events that match none of the chosen candidate's
   preconditions (no TODO_id, no session_id, no judgement_reason row).
2. Whether retroactive backfill (applying the rule to all 12,927 historical
   events) is in scope, or only forward-looking (new events only).
3. Whether `canonical_trace_id` needs uniqueness/collision handling beyond
   what a hash naturally provides.
4. Ownership: which module/script is responsible for computing and writing
   `canonical_trace_id` going forward (candidate: PHI-OS Event Gate,
   TODO_322, since it is already the single write path).

## 6. Non-Goals (explicit)

- No candidate is selected here.
- No new table or column is created by this document.
- No retroactive backfill is performed or scheduled.
- This document does not modify AUDIT_TRACE_LAYER_RULES_v1.md or any of its
  constraints on `trace_id`.
