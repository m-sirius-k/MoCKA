# MoCKA Living Context Snapshot v1

`MOCKA_LIVING_CONTEXT_SNAPSHOT_v1` is a read-only, portable projection of
MoCKA's current recorded state. It is not a canonical source, Decision Ledger,
or Human Gate mechanism. Generating it never writes to TODOs, Ledger, Event
Store, or Human Gate state.

## Run

```powershell
python tools/living_context_snapshot.py snapshot
python tools/living_context_snapshot.py snapshot --format yaml
python tools/living_context_snapshot.py snapshot --output out/snapshot.json
```

## Source mapping

| Snapshot field | Read-only source | Projection rule |
| --- | --- | --- |
| `project.phase`, `current_state`, `unknowns`, `next_boundary` | `data/MOCKA_OVERVIEW.json` | Current phase, current issues, and first immediate next action. |
| `completed`, `active`, `blocked` | `data/MOCKA_TODO.json` | Preserve TODO id/status/title; active is `未着手` or `進行中`, blocked is an explicit status containing `保留`, `ブロック`, `blocked`, or `pending`. |
| `decisions` | `data/mocka_events.db` / `judgement_reason` | Only explicit recorded decisions are returned; events are never reinterpreted as decisions. |
| `human_gate_required` | Active/blocked TODO text | `true` only when an item explicitly includes `Human Gate` or `人間ゲート`; this is an attention flag, not an approval or decision. |
| `source_lineage` | Each listed source | Relative path, SHA-256, modified time, and read-only marker. |
| Context lineage | `data/lever_essence.json`, `gateway/context_builder.py`, `runtime/main/ledger.json` | Recorded in lineage. v1 does not summarize essence or treat the hash-chain ledger as a decision list. |

`data/events.db` is intentionally not used: it is currently empty. The existing
`gateway/context_builder.py` identifies `data/mocka_events.db` as the Event
Store used for current events and decisions.

## Boundaries

- The generator does not write to the Decision Ledger or Event Store.
- It does not approve, reject, route, or create a Human Gate decision.
- Missing/unreadable sources produce empty projections while remaining visible in
  `source_lineage`; they are not silently replaced with inferred data.
