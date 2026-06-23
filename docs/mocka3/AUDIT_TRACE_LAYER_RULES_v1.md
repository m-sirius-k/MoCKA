# MoCKA Audit Trace Layer Rules v1

Document ID: AUDIT_TRACE_LAYER_RULES_v1
Version: 1.0.0
Status: Active (operational guardrail, no schema/data change)
Created: 2026-06-23
Decision authority: Human Gate, decision recorded at E20260623_747052560dd91
Supersedes nothing. Depends on:
- [TRACE_ID_SEMANTIC_AUDIT_v1.md](TRACE_ID_SEMANTIC_AUDIT_v1.md)
- [TRACE_ID_CLASSIFICATION_RULES_v1.md](TRACE_ID_CLASSIFICATION_RULES_v1.md)
- [TRACE_ID_OPTION_IMPACT_MATRIX_v1.md](TRACE_ID_OPTION_IMPACT_MATRIX_v1.md)

---

## 0. What this document is

This is a constraint definition (guardrail), not a design document. It exists
to make Human Gate decision E20260623_747052560dd91 (Option 3: Isolate)
enforceable in practice. It introduces no new field, no new table, no new
write path, and changes nothing in `events.db` / `mocka_events.db`.

The decision it enforces, in one line: **`trace_id` is retained, never
deleted, but carries no semantic meaning. It is audit-only.**

## 1. Prohibited uses of `trace_id`

The following are forbidden, effective immediately, for all MoCKA modules
and all AI actors writing to `events`:

| Forbidden use | Reason |
|---|---|
| Using `trace_id` as a grouping/join key to reconstruct "all events of one intention" | Phase 2 established that 0 of 1,308 distinct values satisfy this; treating it as such produces false groupings |
| Writing new code that assigns semantic meaning to a specific `trace_id` value (e.g. `if trace_id == "manual_save..."`) | Would re-introduce the exact ambiguity this decision closed |
| Treating `related_event_id`-matched LINK values (the `EN8N_*` backward-pointer chain) as a general-purpose canonical key outside n8n's own chain-replay logic | LINK was observed, not designed, as a general mechanism (see Classification Rules v1, Section 6, Option 2 rejected) |
| Introducing a `canonical_trace_id` field, or any field serving that role under another name, without a new, separate Human Gate decision | This decision explicitly leaves canonical design as a future, independent item -- it is not authorized by this document |
| Backfilling, normalizing, or "cleaning" existing `trace_id` values in place | Violates Event Foundation v1 Principle P1 (`events.db` is immutable) and P4 (provenance must not be discarded) |

## 2. Permitted uses of `trace_id`

| Permitted use | Scope |
|---|---|
| Reading `trace_id` for audit, debugging, or forensic investigation of a specific incident | Read-only, ad hoc, not relied upon for any automated logic |
| n8n's own internal chain-replay using its `EN8N_*` LINK pointers | Confined to the n8n integration's own code path; must not be exposed as a general API/query pattern for other modules |
| Displaying raw `trace_id` value in audit UIs/dashboards as historical metadata | Display only -- no filtering/grouping logic should depend on its value meaning anything |
| Citing `trace_id` contamination statistics (711 corrupted / 536 link / 405 candidate / 754 single, per Classification Rules v1) in future incident reports or audits | Statistical/historical reference only |

## 3. Relationship to LINK (n8n chain)

LINK is explicitly **not promoted**. It remains what it always was: an
internal implementation detail of the n8n integration's backward-pointer
chain. This document does not change LINK's behavior, does not document it
as a public mechanism, and does not extend it to other modules. Any future
proposal to generalize LINK requires its own Human Gate review -- it is not
pre-approved by this document.

## 4. Relationship to canonical_trace_id (future)

`canonical_trace_id` (or any field serving that role) is explicitly
**undefined and out of scope** of this document. This document does not:
- propose a derivation rule,
- reserve a column name,
- reserve a table,
- or commit to a timeline.

It only confirms that whenever that design work happens, it starts from a
clean slate and does not need to be compatible with, or derived from, any
existing `trace_id` value (since none qualify as intention-spines per
Classification Rules v1 Section 5).

## 5. Zero-DB-change guarantee

This document requires no `ALTER TABLE`, no `UPDATE`, no `INSERT` into
`events` / `mocka_events.db`, and no migration. It is a behavioral rule for
humans and AI actors writing code and events, not a data operation. Existing
`events_v2.db` migration plans (Event Foundation v1, Section 7) are
unaffected -- `trace_id`'s `source_table`/`source_rowid` provenance fields
continue to apply normally; only the *interpretation* of the `trace_id`
value itself is constrained by this document.

## 6. Enforcement

This is a process rule, not a technical lock. There is no code-level
validator preventing violation (consistent with Section 0: no schema change
was authorized). Compliance relies on:
- this document being referenced in code review / Human Gate review when
  new event-writing code touches `trace_id`,
- `mocka_get_guidelines` / future TODO entries surfacing this document when
  relevant,
- incident reporting (per MoCKA's `mocka_get_incidents`) if a violation is
  later discovered.

## 7. Revision

This document can only be superseded by a new, explicit Human Gate decision
that re-opens Phase 3 (Option 1 or Option 2 per
TRACE_ID_OPTION_IMPACT_MATRIX_v1.md), or by a new document defining
`canonical_trace_id` under its own separate Gate review.
