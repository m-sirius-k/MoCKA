# O0-Human Gate (Semantic Closure Node) v1.0

**Status: DRAFT (definition only, no implementation, no runtime wiring)**

## 0. Disambiguation (read first)

This document defines **O0-Human Gate**, a node in the **O0 observation layer**.

It is **NOT** the same node as the existing **A6 Human Gate**
(`mocka_human_gate_decision_definition_v1.md`), which is the institutional
final-decision point held exclusively by 博士 (decision values:
APPROVE / HOLD / REJECT / DEFER).

| | A6 Human Gate | O0-Human Gate |
|---|---|---|
| Layer | A6 (institutional / governance) | O0 (observation) |
| Function | Final institutional adjudication | Semantic termination |
| Authority | Held by 博士 only | None — does not decide anything |
| Output | `decision` | `closure_tag` |
| SNAP connection | Indirect, governance-mediated | Forbidden |
| Nature | Sovereignty node | Terminal/analysis node |

The two nodes share a name fragment ("Human Gate") but are structurally and
functionally unrelated. They must never be merged, aliased, or treated as
interchangeable in code, contracts, or future designs. Any future proposal
that uses the bare term "Human Gate" without specifying A6 or O0 must be
clarified before acting on it.

## 1. Definition

O0-Human Gate is the terminal node of the O0 observation boundary's semantic
evaluation path. It receives the output of O0-ΔL (semantic differential
evaluation) and produces a closure label. It does not decide, approve,
reject, or defer anything. It does not generate events. It is the point at
which a detected semantic difference stops being processed further.

Node type: `terminal` / `observer` / `semantic closure node` (these three
labels are equivalent ways of describing the same role — not three separate
states).

## 2. Input/Output Contract

**Input:**
- Source: O0-ΔL only.
- Payload: `DIFF_LOG` entries and `semantic_change_type` classification
  (`structural_difference` / `rule_interpretation_shift` / `constraint_drift`).
- No other node may feed input to O0-Human Gate. In particular, A6, SNAP,
  and A7 cannot be input sources.

**Output:**
- `closure_tag` only.
- A closure_tag is a label asserting "this semantic difference has been
  observed and classified; processing terminates here." It carries no
  permission, no instruction, and no executable payload.
- O0-Human Gate produces **no** `decision` field, ever, under any
  circumstance. If a future revision of this node is proposed to emit a
  `decision` field, that proposal is, by definition, no longer describing
  O0-Human Gate — it is proposing a different node and must be evaluated
  as such (see Section 0).
- Output has no destination node. It terminates (see Section 4).

## 3. Role Separation (evaluation vs execution, reconfirmed)

```
rule: evaluation_result ≠ execution_permission
```

This rule, already established for O0-ΔL, extends unchanged to O0-Human
Gate:

- O0-ΔL evaluates and classifies (detection layer).
- O0-Human Gate terminates and labels (closure layer).
- Neither layer holds, grants, or implies execution permission.
- Execution permission, where it exists at all in MoCKA, lives exclusively
  in the A6 institutional layer (A6 Human Gate Finalization, 博士 only) and
  is entirely outside the scope of this document.

O0-Human Gate is not a lighter-weight or automated substitute for A6 Human
Gate. It does not feed into, prepare for, or pre-approve any A6 decision.
The two are non-interacting by design (Section 4).

## 4. Non-connection Constraints

- O0-Human Gate → SNAP: **FORBIDDEN PATH**.
- O0-Human Gate → A7: **FORBIDDEN PATH**.
- O0-Human Gate → A6: **FORBIDDEN PATH**.
- SNAP, A7, and A6 may not read from, subscribe to, or poll O0-Human Gate's
  output.
- The node is a one-directional terminal: input arrives from O0-ΔL, output
  (`closure_tag`) is recorded (e.g. as part of `semantic_diff_log` /
  `classification_annotation`) and nothing downstream consumes it as a
  trigger, instruction, or evaluation input.
- This non-connection is both logical (no defined interface exists to any
  of SNAP/A7/A6) and physical in intent (no code path may be added later
  that creates one without revisiting this document first).

## 5. Relationship to O0-ΔL

```
O0-ΔL        = diff generation   (detect + classify semantic change)
O0-Human Gate = diff termination (close + label, no further action)
```

No node may be inserted between O0-ΔL and O0-Human Gate. The path is:

```
BASELINE, CURRENT_STATE -> O0-ΔL -> DIFF_LOG/classification -> O0-Human Gate -> closure_tag (end)
```

## 6. System Position Diagram

```
A6   [ static institutional system, FROZEN ]
      Human Gate (A6) -- decision (APPROVE/HOLD/REJECT/DEFER) -- 博士 only
      ^
      | (no connection — see Section 4)
      |
O0   [ observation boundary layer ]
      O0-ΔL  --DIFF_LOG/classification-->  O0-Human Gate --closure_tag--> (terminates)

SNAP [ external event system, non-connected to O0 or O0-Human Gate ]
A7   [ inactive trigger domain ]
```

Resulting three-way separation:

```
O0-ΔL : diff generation
O0-Human Gate : semantic terminus
SNAP : external event input only
```

## 7. Outputs Produced / Not Produced

Produced:
- `closure_tag`
- entries appended to `semantic_diff_log` / `classification_annotation`
  (shared log surface with O0-ΔL, no new storage mechanism introduced)

Not produced:
- `decision`
- `events`
- `triggers`
- any SNAP-consumable payload

## 8. Status

DRAFT. No implementation. No runtime wiring. No connection to A6, SNAP, or
A7. This document defines the node; it does not activate it.
