# MoCKA trace_id Phase 3 Option Impact Matrix v1

Document ID: TRACE_ID_OPTION_IMPACT_MATRIX_v1
Version: 1.0.0
Status: Draft (decision input artifact only -- no decision made, no schema/data change applied)
Created: 2026-06-23
Precedes: [TRACE_ID_CLASSIFICATION_RULES_v1.md](TRACE_ID_CLASSIFICATION_RULES_v1.md)
Decision authority: Human Gate (pending, see E20260623_165268817f6ec)

---

## 0. Scope note

This document is a state-compression artifact, not a recommendation. It lists
observable facts and direct consequences for each of the three options named
in the Phase 3 freeze decision. It does not rank, score, or recommend any
option. No "best", "optimal", or "recommended" language is used anywhere
below. The decision belongs to Human Gate.

The three options, as named at freeze time:

- Option 1: Redefine -- design and backfill a new `canonical_trace_id` field
  from a fresh derivation rule (e.g. TODO_id + first-seen timestamp).
- Option 2: Reinterpret -- promote the existing `LINK` chain mechanism
  (n8n backward-pointer, 536 events) and/or `SESSION_*` values to serve as
  the de facto canonical grouping, without introducing a new field.
- Option 3: Isolate -- take no canonical action now. Keep `trace_id` exactly
  as-is, formally labeled as a contaminated/legacy layer, for future
  reconsideration.

## 1. Matrix

| Axis | Option 1: Redefine | Option 2: Reinterpret | Option 3: Isolate |
|---|---|---|---|
| New column/field required | Yes -- `canonical_trace_id` added to `events` (additive only, per Event Foundation v1 I1: no UPDATE/DELETE on `events.db` itself; would target `events_v2` or an additive sidecar) | No -- reuses existing `trace_id`/`related_event_id` values as-is | No -- no new field |
| Events.db itself modified | No (write target would be `events_v2.db` or a new table, consistent with Event Foundation v1 immutability) | No | No |
| Coverage of current data | Can be backfilled for all 12,916 events going forward; retroactive backfill for past events requires a derivation rule for each (TODO_id mapping not guaranteed to exist for older events) | Covers only the 536 LINK events (4.1% of total) and 2 SESSION_* groups (4 events); remaining ~12,376 events have no applicable existing mechanism | Covers 0 events with a working mechanism; all 2,404 currently-populated `trace_id` values remain in their present (711 corrupted / 536 link / 405 candidate / 754 single) state |
| Reversibility | High -- new field can be dropped or redefined later without touching raw `trace_id` | Medium -- once consumers (queries, dashboards, audit tools) start treating LINK/SESSION_* as canonical, reversing requires updating those consumers | Highest -- nothing is built, nothing to reverse |
| Dependency on Event Taxonomy (TODO_301) | None directly -- `canonical_trace_id` is a separate axis from `what_type` | None directly | None |
| Dependency on PHI-OS Event Gate (TODO_322) | Any new write path must go through the Gate (single-write-path mandate) | No new writes -- existing LINK values were already written through whatever path created them | No new writes |
| Effect on existing LINK mechanism (n8n) | Untouched -- LINK continues to operate as a chain pointer for n8n, independent of new field | LINK is formally elevated from "incidental chain pointer" to "part of the canonical model" -- changes its documented role | Untouched -- remains an undocumented-as-canonical, informally-observed pattern |
| Effect on CORRUPTED records (711) | Unaffected by the backfill itself; remain visible/queryable as `trace_id` is untouched; could optionally be flagged separately later | Unaffected | Unaffected -- explicitly documented as contaminated, no remediation attempted |
| Work required now | Define derivation rule, write backfill script, define which past events get backfilled (all vs. only post-cutoff), Human Gate review of the rule itself | Define what counts as a "promotable" LINK/SESSION_* group, document the elevation, no backfill script needed | Document the freeze; no implementation |
| Work required later (if option changes) | If Option 1 is later abandoned, the additive field can simply be dropped without affecting `trace_id` | If Option 2 is later expanded to Option 1, existing LINK/SESSION_* groups would need to be re-expressed as `canonical_trace_id` values without breaking whatever consumers were built on the interim model | If later upgraded to Option 1 or 2, work starts from the Phase 1/2 baseline already documented -- no extra unwinding needed since nothing was built |
| Risk of creating a second "canonical" definition | Present if `canonical_trace_id` derivation rule itself ever diverges from any future Taxonomy-side intention model (mitigated by Human Gate review per row 1) | Present by definition -- LINK was observed as an n8n-internal mechanism (Phase 1/2), not designed as a general intention key; declaring it canonical retroactively assigns it a role it wasn't built for | None -- no new canonical claim is made |
| Audit continuity (Event Foundation v1 P1/P4) | Preserved -- raw `trace_id` untouched, new field is additive, provenance intact | Preserved -- no raw values changed | Preserved trivially -- nothing changes |

## 2. Observed facts carried over from Phase 1/2 (for reference, not re-derived here)

- 12,916 total events; 2,404 (18.6%) have non-empty `trace_id`.
- Of 1,308 distinct `trace_id` values, 0 satisfy the original "one intention,
  one trace_id, queryable START-to-DONE" design intent (see
  TRACE_ID_CLASSIFICATION_RULES_v1.md Section 5).
- LINK mechanism (536 events) is currently scoped to `EN8N_*` event_ids only.
- VALID_CANDIDATE groups (405 events, 8 groups) are all recurring identical
  system-snapshot strings, not intention groupings.

## 3. What this document does not do

- It does not state which option is consistent with MoCKA's stated
  principles "better" than another -- that comparison is left to Human Gate.
- It does not propose a specific `canonical_trace_id` derivation formula for
  Option 1.
- It does not propose specific promotion criteria for Option 2.
- It does not set a deadline or trigger condition for revisiting Option 3.
