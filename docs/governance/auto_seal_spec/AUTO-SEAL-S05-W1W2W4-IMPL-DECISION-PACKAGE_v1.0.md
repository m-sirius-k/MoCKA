# AUTO-SEAL S0.5 - W-1/W-2/W-4 Implementation Decision Package (APPROVED)

Document: AUTO-SEAL-S05-W1W2W4-IMPL-DECISION-PACKAGE
Version: v1.0
Status: APPROVED WITH BOUNDARY CONDITIONS (Human Gate, kimura, 2026-07-14)
Prepared by: kuroko (Claude-opus-4-8)
Separation: recorded separately from production implementation (D-11 condition)
Proof branch: proof/wxx-validation (uncommitted). Worktree: C:/Users/sirok/mocka_proof_wt (retained per D-10).

Note: this document records the decision package and the Human Gate adjudication only.
No production code, schema, events.db, or decision_ledger.jsonl was changed to produce it.

--------------------------------------------------------------------------------
## 1. Proof Verification Summary

Purpose: confirm implementation feasibility of three residual improvement candidates by
read-only proof, without changing any production asset. Prove: can be built, does not break,
effect is measurable.

Isolation: separate git worktree (proof/wxx-validation, --no-checkout, Windows long-path safe).
Main tree stayed on `main`, no commit/merge. Proof scripts read production assets by absolute
path, read-only; outputs only to proof/out/.

Read-only guarantee: every DB connection opened with `file:...?mode=ro` + `PRAGMA query_only=ON`;
write attempts rejected in all cases (write_rejected = true); jsonl read-only.

Hash verification (production, before vs after full run):
| asset | before | after | result |
| --- | --- | --- | --- |
| data/mocka_events.db | e62a0972..489dd | e62a0972..489dd | identical |
| data/decisions/decision_ledger.jsonl | a0ab38b2..9e458 | a0ab38b2..9e458 | identical |

PASS results:
| proof | result | key evidence |
| --- | --- | --- |
| W-1 provenance convention | PASS | 5-role encode/decode round-trip; 0 key collision; 50-sample reader non-interference |
| W-2 reverse resolver | PASS | reverse map built; superseded = [DC_20260705_008, DC_20260707_002, DC_20260707_007]; DC_20260712_008 self-ref isolated; jsonl sha256 identical |
| W-4 search v2 probe | PASS | scattered-term query v1=0/v2=1 recovered; v1 preserved; traversal bounded 1-hop; db hash identical |

--------------------------------------------------------------------------------
## 2. Implementation Options (as adjudicated)

### W-1 Relay provenance model
Separate 5 roles: operation_actor / relay_operator / origin_author / origin_source / origin_url.
| axis | Option N (free_note convention) | Option S (schema extension) |
| --- | --- | --- |
| integrity impact | none (string composition only) | new columns; existing rows NULL |
| migration load | zero; forward-only from new events | schema + FIELDNAMES + passthrough |
| rollback | revert endpoint logic; no irreversible change | DROP COLUMN constrained |
| proof | PASS | not proof-tested (design only) |

### W-2 Decision Ledger reverse traceability
| axis | Option B (resolver / read layer) | Option A (ledger physical change) |
| --- | --- | --- |
| append-only impact | none; jsonl byte-identical (proven) | appends Superseded rows; Active set changes |
| governance-state change | none (derived at read) | yes: 3 decisions move out of Active |
| rollback | remove logic; zero trace | cancel-rows only; not reversible |
| proof | PASS | requires DC_20260712_008 ruling first |

### W-4 Search inheritance model
| candidate | effect | non-destructiveness |
| --- | --- | --- |
| token search | recovers scattered-term concept queries (proven) | pure function change |
| relationship traversal | 1-hop expansion of event/decision/todo links | read-only, bounded |
| metadata expansion | explicit field/tag filters | read-only convention |
| index layer (FTS5) | speed + ranking | derived table, DROP-able |

--------------------------------------------------------------------------------
## 3. Human Gate Decision (kimura, 2026-07-14) - APPROVED WITH BOUNDARY CONDITIONS

D-1  W-1 method: Option N (free_note convention). Reason: prioritize provenance-semantics
     verification, avoid schema change now. Conditions: keep operation_actor meaning; make
     origin info additionally recordable; no existing-event change; future schema is a separate Decision.
D-2  W-1 apply scope: all of /ask, /success, /ny_extract. Condition: phased; first implementation
     targets new events only.
D-3  W-1 schema change: not permitted now. Reason: non-destructive method proven; revisit after
     operational results.
D-4  W-2 method: Option B (resolver / read layer). Reason: preserves append-only principle.
D-5  W-2 existing 3 superseded decisions status change: NOT performed. Reason: governance-state
     change of existing decisions is a separate Human Gate. Derived display only for now.
D-6  W-2 DC_20260712_008 self-supersession: keep observing. Reason: intent vs typo not determinable
     now. Correction prohibited.
D-7  W-4 candidates and order (proof promotion): 1) token search, 2) relationship traversal,
     3) metadata expansion, 4) index layer (FTS5). Reason: verify effect from minimal change.
D-8  W-4 v1/v2 policy: keep v1 + run v2 in parallel. Condition: make search-result meaning-change
     explicit; v1 replacement prohibited.
D-9  Proof-to-production promotion: APPROVED, scope-limited.
     Approved: read layer, parser, resolver, non-destructive search improvement.
     Not approved: schema change, ledger change, existing-state change.
D-10 Proof worktree: retain, as a reproducible verification environment until production
     application is confirmed.
D-11 Canonical doc record: permitted. Conditions: CHANGE_START/DONE, UTF-8 verification,
     canonical_paths check, recorded separately from production implementation.

--------------------------------------------------------------------------------
## 4. Implementation Boundary (active)

Approved (implementation preparation only):
- W-1 Option N implementation preparation
- W-2 Resolver / read layer implementation preparation
- W-4 token / traversal read layer implementation preparation

Prohibited:
- schema change
- migration
- Decision Ledger physical change
- status change
- existing-event modification

Next phase: move only the Human-Gate-approved scope into the Implementation Phase.

--------------------------------------------------------------------------------
## 5. Traceability
- Investigation records: E20260714_295687584717c (W-1), E20260714_716973138f8f4 (W-2),
  E20260714_9980076371d31 (W-4). Cross-manifest: E20260714_198303840b131.
- TODO: TODO_W1, TODO_W2, TODO_W4 (status improvement candidate, Human Gate reviewed).
- Proof artifacts: proof/w1_provenance_convention.py, proof/w2_reverse_resolver.py,
  proof/w4_search_v2_probe.py, proof/out/*.json (worktree proof/wxx-validation).
- This doc record: CHANGE_START E20260714_0490796397f3d.
