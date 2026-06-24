# MoCKA Global Terminal Map v1.0

**Status: TERMINAL DECLARATION (full-system aggregation of existing,
already-frozen/already-audited material — no new structure, no new
connection, no Phase10-4 specification)**

This document does not design anything. Every node, edge, and
non-connection rule below already exists in a prior document. This map's
only function is to place all of them in one space, simultaneously
visible, as a single terminal state.

## 1. System Layer Model

| Layer | Name | Contents | Nature |
|---|---|---|---|
| 0 | Semantic Generation | O0, O0-&#916;L | active observation, no authority |
| 1 | Semantic Termination | O0-Human Gate | terminal, outputs `closure_tag` |
| 2 | Institutional Adjudication | A6 Human Gate | sole decision authority, 博士 only |
| 3 | External Input | SNAP | external-event-only source |
| 4 | Inactive Domain | A7 | edge-free, inactive |
| 5 | Frozen Civilization | Phase10-3 (v3 + SVG + freeze_log + declaration) | closed canonical reference |
| 6 | Undefined Territory | Phase10-4 | black box, unspecified, no implementation |

Layers are listed in this order because it is the order semantic material
flows and terminates in the defined parts of the system (0 -> 1), runs in
parallel to the separately-governed institutional track (2), sits beside
isolated/external nodes (3, 4), and finally sits beside the two larger
containers that hold everything else in time (5: closed past, 6:
unspecified future). The ordering is descriptive, not a flow path — there
is no edge connecting Layer 1 to Layer 2, or Layer 5 to Layer 6 (see §4).

## 2. Node Definitions (all layers)

- **O0-&#916;L** (Layer 0): detects and classifies semantic difference
  (`structural_difference` / `rule_interpretation_shift` /
  `constraint_drift`); outputs `DIFF_LOG` only; holds no authority.
- **O0-Human Gate** (Layer 1): receives O0-&#916;L output only; outputs
  `closure_tag`; decides nothing; terminal node (nothing reads its
  output as input).
- **A6 Human Gate** (Layer 2): 博士's sole institutional decision point;
  outputs `decision` (APPROVE/HOLD/REJECT/DEFER); Core (evaluation) ->
  Finalization (decision) internal split, unaffected by anything in
  this map.
- **SNAP** (Layer 3): external-system-event input only; cannot read O0,
  cannot bypass A6's existing governance-mediated path.
- **A7** (Layer 4): inactive trigger domain; zero edges in or out, in
  any document to date.
- **Phase10-3** (Layer 5): the closed canonical set declared in
  `phase10_3_final_freeze_declaration_v1.md` — `phase10_3_integrated_mapping_v3.md`
  + `phase10_3_topology_freeze_v1.svg` + `freeze_log.md`. Contains the
  full definitions of Layers 0–4 in compressed/visual form. Frozen;
  reopening requires an explicit future decision, not incremental edit.
- **Phase10-4** (Layer 6): adjudication/Trigger/execution-adjacent
  territory. No internal structure has ever been specified in this
  project. Treated, as always, as an opaque black box. This map does
  not specify it now either.

## 3. Dual Human Gate Separation

O0-Human Gate and A6 Human Gate are not two states of one node. They are
two permanently distinct nodes, restated here in final form:

| | O0-Human Gate | A6 Human Gate |
|---|---|---|
| Layer | 1 (semantic termination) | 2 (institutional adjudication) |
| Function | closure only | decision only |
| Output | `closure_tag` | `decision` |
| Authority | none | 博士 only |
| Relationship to the other | none — no edge, no conversion, no shared state | none — no edge, no conversion, no shared state |

This is restated as "functional asymmetry, not phase symmetry," per
`phase10_3_integrated_mapping_v3.md` §2: one node closes meaning, the
other adjudicates authority, and neither performs any part of the
other's function. No document, including this one, defines a path
between them.

## 4. Non-Connection Matrix

| From \ To | O0-&#916;L | O0-HG | A6-HG | SNAP | A7 | Phase10-3 (frozen) | Phase10-4 |
|---|---|---|---|---|---|---|---|
| O0-&#916;L | — | edge (internal) | forbidden | forbidden | forbidden | n/a (is part of) | forbidden |
| O0-HG | forbidden | — | forbidden | forbidden | forbidden | n/a (is part of) | forbidden |
| A6-HG | forbidden | forbidden | — | indirect, governance-mediated (pre-existing, unchanged) | forbidden | forbidden | unspecified (black box) |
| SNAP | forbidden | forbidden | (see above) | — | forbidden | forbidden | unspecified (black box) |
| A7 | forbidden | forbidden | forbidden | forbidden | — | forbidden | unspecified (black box) |
| Phase10-3 (frozen) | n/a (is part of) | n/a (is part of) | forbidden | forbidden | forbidden | — | non-interfering, opaque citation only (§5) |
| Phase10-4 | forbidden | forbidden | unspecified (black box) | unspecified (black box) | unspecified (black box) | non-interfering, opaque citation only (§5) | — |

"Unspecified (black box)" cells are not asserted as connected or
disconnected at the implementation level — they record that Phase10-4
has never been specified, so no edge can be confirmed *or* denied at
that level of detail. The only thing confirmed is that no document
*defines* such an edge, which is the same epistemic posture held since
`phase10_4_independent_stability_review_v1.md` §2.

## 5. Frozen vs Dynamic vs Undefined Partition

- **Frozen**: Phase10-3 (Layer 5) and everything it contains (Layers 0–4
  as captured in v3/SVG/freeze_log). Per
  `phase10_3_final_freeze_declaration_v1.md`, reopening requires an
  explicit future decision.
- **Dynamic**: nothing, currently. No layer in this map has any active
  runtime behavior — there is no implementation of O0, A6, SNAP, A7, or
  anything else. "Dynamic" is reserved as a category for a future state
  this map does not claim to have reached.
- **Undefined**: Phase10-4 (Layer 6) only. It remains the sole
  unspecified territory in the entire map. This partition is not
  resolved by this document and is not intended to be.

## 6. Global Isolation Proof

Claim: no path exists, anywhere in this map, from the observation/
institutional layers (0–4) or the frozen civilization (5) into an active
execution or trigger state.

1. By the Non-Connection Matrix (§4), O0-&#916;L and O0-Human Gate have
   no edge to A6-HG, SNAP, A7, or Phase10-4.
2. A6-HG's only outbound edge (to SNAP) is indirect, governance-mediated,
   and pre-existing — it does not originate from, or pass through,
   Layers 0–1, and it does not constitute an execution edge (no
   document defines SNAP as executing anything in response; SNAP itself
   is input-only).
3. A7 has zero edges in any direction (§4), so it cannot be reached from,
   or reach, any other layer.
4. Phase10-3, as a frozen set, is declared non-interfering with
   Phase10-4 in both directions (§4, citing
   `phase10_4_independent_stability_review_v1.md` Claims 1–2).
5. Phase10-4 has no specified internal structure (§2, §5) and therefore
   no specified Trigger or execution behavior exists anywhere in MoCKA
   as of this map. A behavior that is not specified cannot be shown to
   be reachable.

Therefore: zero confirmed execution/Trigger reachability from any node
or layer in this map. This conclusion holds at the level of *specified
structure* — it is, as in every prior document, not an empirical
guarantee about a future Phase10-4 implementation, which would require
its own review when proposed (per
`phase10_4_independent_stability_review_v1.md` §6).

## 7. Terminal State Declaration

MoCKA, as of this map, is declared to be:

> A fully separated system of semantic generation (O0), semantic
> termination (O0-Human Gate), institutional adjudication (A6 Human
> Gate), external input (SNAP), an inactive domain (A7), a frozen
> civilization (Phase10-3), and an undefined future (Phase10-4) — with
> no execution path connecting any of them.

This is not a new design. It is the simultaneous visibility of every
prior decision (v1 through `phase10_4_independent_stability_review_v1.md`)
in one terminal artifact. Nothing here changes after this point without
an explicit decision to reopen a specific named layer or document — this
map itself does not self-modify and does not get incrementally edited;
a future change produces a new versioned map, not an edit to v1.

**Resulting state: a structure that does not execute, and is completely
self-describing.**
