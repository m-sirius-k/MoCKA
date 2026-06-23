# MoCKA trace_id Semantic Audit v1

Document ID: TRACE_ID_SEMANTIC_AUDIT_v1
Version: 1.0.0
Status: Draft (Phase 1 - classification only, no schema change applied)
Created: 2026-06-23
Reference Event: E20260623_84148446346f2

---

## 1. Background

This audit started from a proposal to "redefine the event schema" by introducing
a new `trace_id` field as a cross-event grouping key for intentions (TODO units).

Before implementing anything, the existing structures were checked against this
proposal:

- TODO_322 (PHI-OS Event Gate): single write path, mandatory `actor` field,
  before/after recording. Already complete.
- TODO_301 (Event Taxonomy v1): `what_type` taxonomy
  (LIFECYCLE/OPERATIONAL/DECISION/AUDIT/INCIDENT/SYSTEM). Already complete.
  Introducing a new `event_type` enum (START/DONE/AUDIT/UPDATE) would have
  created a second, conflicting taxonomy.
- TODO_194 / TODO_305 (judgement_reason / Decision Ledger): partial
  trace-reconstruction already exists via `event_id` joins, independent of any
  `trace_id` field.

The critical finding: `events` table in `data/mocka_events.db` already has a
`trace_id` column (see `EVENT_FOUNDATION_v1.md` is silent on it; confirmed via
`PRAGMA table_info(events)`). The proposal to "add trace_id" was therefore
based on a false premise. This document records what the existing column
actually contains.

## 2. Method

Read-only query against `data/mocka_events.db`, table `events`
(12,916 rows total at time of audit).

```sql
SELECT event_id, trace_id, related_event_id FROM events
WHERE trace_id IS NOT NULL AND trace_id != ''
```

No write or migration was performed. This is observation only.

## 3. Headline Numbers

| Metric | Value |
|---|---|
| Total events | 12,916 |
| Events with non-empty `trace_id` | 2,404 (18.6%) |
| Distinct `trace_id` values | 1,308 |
| Distinct values shared by >1 event | 16 |
| Events covered by those 16 shared values | 1,112 |

**Core finding**: of 1,308 distinct `trace_id` values, only 16 are reused
across more than one event, and nearly all of those 16 are noise (see 4.1).
This means `trace_id`, as currently populated, does **not** function as a
cross-event grouping key for intentions. It functions, in practice, as a
free-text annotation field with no enforced semantics.

## 4. Classification (3 categories, non-destructive)

Classification was performed by pattern-matching only; no data was modified.

### 4.1 CORRUPTED (711 records, ~30% of populated rows)

Values that are `"N/A"`, empty after trim, or contain CP932-mojibake markers
(the same class of corruption tracked under TODO_333 / `check_utf8_mandate.py`
Rule 4/5).

Top offenders by repeat count:
- `"N/A"` -- 672 events
- `"no_api|D_i=1|...E=0"` (mojibake) -- 375 events
- Various mojibake Japanese sentences -- 5 events each (at least 6 distinct
  garbled strings found)

These are not meaningful trace data. They are artifacts of upstream encoding
failures or unset defaults.

### 4.2 LINK (536 records)

Values matching a 16-character lowercase hex pattern that also appear as
`related_event_id` on another row. Example chain (descending time order):

```
event EN8N_20260620_063932_PAST  trace_id=db1054e3...  related_event_id=ff898130...
event EN8N_20260620_063925_PAST  trace_id=ff898130...  related_event_id=2ab0e2d6...
event EN8N_20260620_063913_PAST  trace_id=2ab0e2d6...  related_event_id=7dac3409...
```

Here `trace_id` is being used as a **backward link pointer** (this event's
`trace_id` equals the previous event's `related_event_id`), forming a linked
list of single-step transitions. This is a different semantic from "shared key
for all events of one intention" -- it is closer to a hash-chain / blockchain-
style prev-pointer, scoped to the n8n integration (`EN8N_*` event_id prefix).

### 4.3 OTHER / single-use annotation strings (1,157 records)

Free-text strings such as:
- `"manual_save"`
- `"hash=aef7a8c2082eb806|source=chatgpt|msgs=1"`
- `"hash=29fe9858f094ddea|source=chatgpt|mode=full_scroll"`

These look like per-event metadata snapshots (source, hash of payload, msg
count) rather than identifiers meant to be shared across multiple events. Of
this group, essentially none repeat across more than one event -- each is a
one-off annotation, not a grouping key.

## 5. Conclusion

`trace_id` in the current `events` table is a column with three unrelated,
co-mingled semantics, none of which match the "intention-spine" design intent
(a stable key shared by all events belonging to one TODO/intention,
queryable as `WHERE trace_id = X ORDER BY when_ts`):

1. Noise (CORRUPTED) -- should eventually be isolated, not deleted (per
   Event Foundation v1, Principle P3: rejected/invalid records are preserved,
   never discarded).
2. A single-purpose hash-chain pointer used only by the n8n integration
   (LINK) -- a legitimate but narrow mechanism, not a general intention key.
3. Free-text per-event metadata (OTHER) -- useful as metadata, not as a join
   key.

**No existing data currently satisfies the "intention-spine" use case.**
Any future grouping-key design must either:
(a) introduce a new, separate field (e.g. `intent_id`) rather than overloading
`trace_id` further, or
(b) define a strict `canonical_trace_id` derivation rule and backfill it
without overwriting the raw `trace_id` value (preserving Provenance per
Event Foundation v1 Principle P4).

This document makes no recommendation between (a) and (b) and applies no
schema or data change. It exists solely to fix the factual baseline before
any further design decision.

## 6. Non-Goals (explicit)

- This document does NOT modify `events` table data or schema.
- This document does NOT define `event_type` (Taxonomy ownership stays with
  `EVENT_TAXONOMY_v1.md` / TODO_301).
- This document does NOT decide between options (a)/(b) above. That is a
  separate, future decision requiring Human Gate review per MoCKA write
  policy (Phase 18+).
