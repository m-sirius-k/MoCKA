# MoCKA trace_id Classification Rules v1

Document ID: TRACE_ID_CLASSIFICATION_RULES_v1
Version: 1.0.0
Status: Draft (Phase 2 - deterministic rules, no schema/data change applied)
Created: 2026-06-23
Reference Events: E20260623_891376784af46 (Phase 1 audit), E20260623_019546219fb69 (this document)
Precedes: canonical_trace_id generation algorithm (Phase 3, not yet designed)

---

## 1. Purpose

[TRACE_ID_SEMANTIC_AUDIT_v1.md](TRACE_ID_SEMANTIC_AUDIT_v1.md) established that
the existing `trace_id` column mixes three unrelated semantics. This document
turns the manual classification from that audit into a deterministic,
re-runnable function, so that any future `canonical_trace_id` backfill
(Phase 3) has a fixed, auditable input.

This document changes nothing in `events.db`. It only defines and tests a
classification function against the existing data, read-only.

## 2. Inputs

For each row in `events`: `event_id`, `trace_id`, `related_event_id`, `title`.

Precomputed once per full table scan: `related_set` = the set of all non-empty
`related_event_id` values in the table.

## 3. Per-row predicates

### 3.1 `is_corrupted(trace_id) -> bool`

```
mojibake_markers = ['繧','縺','繝','蝗','髱','蜈','邨','迚']  # CP932-as-UTF8 artifacts
                                                              # (TODO_333 class)

is_corrupted(t):
    if t is None: return True
    t = t.strip()
    if t == "" or t == "N/A": return True
    if contains_replacement_char(t):       # U+FFFD literal mojibake
        return True
    if any(marker in t for marker in mojibake_markers):
        return True
    return False
```

Important correction from the Phase 1 manual pass: legitimate non-ASCII
characters such as Greek letters (e.g. `Δ` in `"no_api|D_i=1|ΔE=0"`, a drift
metric snapshot consistent with the project's `ΔZ` notation) must NOT be
flagged as mojibake. Only the specific CP932-corruption character set and the
literal U+FFFD replacement character count as corruption. This was verified
by inspecting raw codepoints (`ord(ch)`) before finalizing the marker list.

### 3.2 `is_link(trace_id, related_set) -> bool`

```
hex16 = regex ^[0-9a-f]{16}$

is_link(t, related_set):
    if not hex16.match(t): return False
    if t not in related_set: return False
    return True
```

A `trace_id` is a LINK pointer if it is a 16-char lowercase hex string that
also appears elsewhere in the table as some other row's `related_event_id`.
Observed exclusively on `EN8N_*`-prefixed event_ids in the current dataset
(n8n integration backward-chain pointers).

## 4. Group-level rule (VALID candidate)

Per-row predicates are not sufficient to detect a grouping key -- grouping is
a property of a `trace_id` *value* across the whole table, not of one row.

```
group rows by trace_id value -> groups[trace_id] = [rows...]

for tid, members in groups:
    if is_corrupted(tid):           classify all members as CORRUPTED
    elif all(is_link(m) for m in members):  classify all members as LINK
    elif len(members) >= 2:         classify all members as VALID_CANDIDATE
    else:                           classify the member as OTHER_SINGLE
```

`VALID_CANDIDATE` is deliberately not named `VALID`. Membership in this
bucket only proves "this string was attached to 2+ events" -- it does not
prove the string represents one coherent intention. Section 5 shows why none
of the current candidates qualify as true intention-spines.

## 5. Result on full dataset (12,916 rows, re-run 2026-06-23)

| Class | Events | Distinct trace_id values |
|---|---|---|
| CORRUPTED | 711 | -- |
| LINK | 536 | -- |
| VALID_CANDIDATE | 405 | 8 |
| OTHER_SINGLE | 754 | 754 |

(Remaining rows have empty/null `trace_id` and are excluded entirely, per
Phase 1: 12,916 - 2,406 classified = 10,510 rows with no `trace_id` at all.)

### 5.1 Inspection of the 8 VALID_CANDIDATE groups

| trace_id value (truncated) | event count |
|---|---|
| `manual_save \| error_rate=0.0 \| router_mode=full_orchestra \| anomaly=NORMAL \| action=NONE` | 15 |
| `no_api\|D_i=1\|ΔE=0` | 375 |
| `save_complete` | 2 |
| `guard=SAFE trace={"version":"v1",...}` (router decision snapshot, variant A) | 2 |
| `guard=SAFE trace={"version":"v1",...}` (variant B) | 5 |
| `guard=SAFE trace={"version":"v2",...}` | 2 |
| `SESSION_20260610_175032` | 2 |
| `SESSION_20260612_091220` | 2 |

Every one of these is a **recurring identical system-state snapshot string**,
logged verbatim each time a particular condition recurred (e.g. drift = 0,
router in a given mode, an identical router decision payload). None of them
represent "all events belonging to one TODO/intention" -- they represent "this
exact status string happened again."

**Conclusion: 0 of 1,308 distinct `trace_id` values in the current dataset
satisfy the original design intent** (a stable key shared by all events of
one intention, queryable end-to-end). The closest analog -- `SESSION_*`
values -- groups by session, not by intention, and only 2 such values exist
with 2 members each.

## 6. Implication for Phase 3 (canonical_trace_id)

Because no existing `trace_id` value already encodes an intention-spine, the
Phase 3 algorithm cannot be a "promote existing good values" function. It has
two honest options, both already named in Phase 1:

(a) Derive `canonical_trace_id` from something else entirely (e.g. TODO_id +
    first-seen timestamp hash, as originally proposed before this audit
    began) and backfill it as a new, additive field -- leaving raw `trace_id`
    untouched (per Event Foundation v1, Principle P4: provenance is never
    discarded).
(b) Treat `SESSION_*`-style and `EN8N_*` LINK-chain values as a narrower,
    already-correct special case, and only synthesize new canonical ids for
    rows that have neither.

This document does not choose between these. That choice, and the exact
derivation rule, is Phase 3 and requires Human Gate review before any write
to `events.db` (per MoCKA write policy, Phase 18+, Core System File Change
Approval).

## 7. Non-Goals (explicit)

- No `events` table data was modified.
- No new column was added.
- No `event_type`/Taxonomy decision was made (out of scope, owned by
  TODO_301 / EVENT_TAXONOMY_v1.md).
- No canonical_trace_id derivation rule was chosen (Phase 3, future).
