# Phase10-3 Integrated Mapping v2.0

**Status: DRAFT (semantic topology update only — no control structure change,
no implementation, no runtime wiring)**

This document supersedes nothing. It is an additive vocabulary-layer update
to `mocka_phase10_human_gate_insertion_map_v1.md`, reflecting the dual
Human Gate structure (A6 Human Gate + O0-Human Gate) established in
`mocka_human_gate_decision_definition_v1.md` and
`o0_human_gate_semantic_terminal_v1.md`. Phase10-3/10-4 internal FROZEN
adjudication logic remains a black box and is not described, inspected, or
modified here.

## 1. System Overview

MoCKA's structure, as of this mapping, separates into two non-interacting
tracks plus one frozen institutional core:

- **A6 track** (institutional / governance): static, FROZEN, holds the only
  decision authority in the system (博士, via A6 Human Gate).
- **O0 track** (observation): detects and terminates semantic differences;
  holds no authority, makes no decisions, triggers nothing.
- **SNAP / A7** (execution-adjacent): external-event-only input and an
  inactive trigger domain, respectively. Neither is connected to O0 or to
  the O0-Human Gate.

This mapping exists to make the *current vocabulary* explicit and
consistent across documents, not to change what any node does or how it
connects. No edge in this document is new; every edge already existed in
prior documents (`mocka_hab_v1_contract.md`,
`mocka_phase10_human_gate_insertion_map_v1.md`,
`o0_human_gate_semantic_terminal_v1.md`) except where explicitly marked
"FORBIDDEN."

## 2. Node Definitions

### O0
- Type: observation boundary layer.
- Contains: O0-ΔL (semantic diff evaluator), O0-Human Gate (semantic
  closure terminal).
- Authority: none. Produces no decision, no event, no trigger.

### A6
- Type: static institutional system. FROZEN — unchanged by this document.
- Contains: A6 Human Gate (decision gate), and the existing Phase10-3/10-4
  FROZEN adjudication logic (treated here strictly as a black box, per
  `mocka_phase10_blackbox_impact_analysis_v1.md`).
- Authority: sole holder of institutional decision authority (博士 only,
  via A6 Human Gate Finalization).

### SNAP
- Type: external event system.
- Input source: external system events only. Does not read from, poll, or
  subscribe to O0, O0-ΔL, or O0-Human Gate.

### A7
- Type: inactive trigger domain.
- Status: inactive. No wiring in or out is defined by this document.

## 3. Dual Human Gate Structure

MoCKA has two nodes that share the name "Human Gate" and nothing else.
They are not variants of one node, not a Core/Finalization split of one
node, and not interchangeable. They must always be referred to by their
full qualified name (A6 Human Gate / O0-Human Gate), never bare "Human
Gate," in any future document that touches both tracks.

| | A6 Human Gate | O0-Human Gate |
|---|---|---|
| Track | A6 (institutional) | O0 (observation) |
| Role | decision gate | semantic closure terminal |
| Output | `decision` (APPROVE / HOLD / REJECT / DEFER) | `closure_tag` |
| Authority | 博士 only (Finalization) | none |
| Input source | A6 Human Gate Core (evaluation) | O0-ΔL only |
| Connects to SNAP/A7 | indirect, governance-mediated, unchanged by this doc | forbidden |
| Connects to the other Human Gate | no | no |

Integration rule for this mapping: **dual-node structure is explicit and
permanent — the two Human Gates are never merged into one node in any
diagram, contract, or implementation.**

## 4. Non-Connection Constraints

- O0-ΔL → SNAP: forbidden.
- O0-ΔL → A7: forbidden.
- O0-ΔL → A6: forbidden (O0-ΔL feeds O0-Human Gate only).
- O0-Human Gate → SNAP: forbidden.
- O0-Human Gate → A7: forbidden.
- O0-Human Gate → A6: forbidden.
- O0-Human Gate ↔ A6 Human Gate: forbidden in both directions (no shared
  state, no shared output type, no triggering relationship).
- SNAP → O0 (any node): forbidden — SNAP is external-input-only and does
  not read from the observation layer.
- A7 → anything: undefined/inactive. This document does not activate or
  wire A7 in any direction.
- Trigger Wiring (in the sense used across Phase10-Stasis discussions,
  i.e. activation authority / firing conditions) is **not addressed,
  not reopened, and not implied** by any edge in this document.

## 5. Topology Diagram

```
                A6  [ FROZEN institutional core ]
                |
                |   Phase10-3 / Phase10-4 adjudication logic
                |   (black box — not described here)
                |
                +-- A6 Human Gate
                      Core (evaluation) -> Finalization (decision, 博士 only)
                      output: decision (APPROVE/HOLD/REJECT/DEFER)

                ^
                |  (NO CONNECTION — see Section 4)
                v

                O0  [ observation boundary layer ]
                +-- O0-ΔL (semantic diff evaluator)
                |     input:  BASELINE, CURRENT_STATE
                |     output: DIFF_LOG, semantic_change_type
                |
                +-- O0-Human Gate (semantic closure terminal)
                      input:  O0-ΔL output only
                      output: closure_tag
                      (terminates here — no further node)

      SNAP  [ external event system ]         A7  [ inactive trigger domain ]
        - isolated node                          - isolated node
        - input: external system events only     - no defined wiring
        - no read access to O0 or A6              - inactive
```

All four tracks (A6, O0, SNAP, A7) are drawn as parallel, non-intersecting
columns. No line crosses between columns except the explicitly internal
A6 Human Gate Core→Finalization and O0-ΔL→O0-Human Gate edges, both of
which existed before this document.

## 6. Explicit Forbidden Paths List

1. O0-ΔL → SNAP
2. O0-ΔL → A7
3. O0-ΔL → A6
4. O0-Human Gate → SNAP
5. O0-Human Gate → A7
6. O0-Human Gate → A6
7. O0-Human Gate → A6 Human Gate (either direction)
8. SNAP → O0 (any node)
9. SNAP → A6 Human Gate (bypassing existing governance-mediated path)
10. Any node → A7 (A7 remains inactive; no path is defined or implied)

## 7. Success Conditions (self-check)

- [x] Zero new logical connections to the execution track (SNAP/A7).
- [x] No Trigger Wiring reintroduced; none of Sections 1–6 define firing
      conditions, activation authority, or event emission.
- [x] Dual Human Gate structure made explicit (Section 3); the two nodes
      are never merged.
- [x] A6 (including Phase10-3/10-4 adjudication logic) is referenced only
      as a black box and is otherwise unchanged.

## 8. Status

DRAFT. Semantic/topology vocabulary update only. No control-structure
change. No implementation. No runtime wiring.
