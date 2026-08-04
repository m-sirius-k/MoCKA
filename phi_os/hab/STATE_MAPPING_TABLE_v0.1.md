# HAB State Mapping Table v0.1

Source:
HG-J04 Observation M-1/M-2/M-3

## HG-1 human_gate_events

PENDING
 -> PENDING_HUMAN_GATE

APPROVED
 -> APPROVED

REJECTED
 -> REJECTED


## HG-2 prevention_queue

NEW
 -> EVALUATING

approved
 -> APPROVED

rejected
 -> REJECTED


## HG-3 git workflow

No canonical mapping.
Requires future observation.


## HG-4 semantic query engine

accept
 -> APPROVED

reject
 -> REJECTED

defer
 -> DEFERRED

split
 -> EVALUATING


## HG-5 continuity layer

WAITING_FOR_HUMAN_GATE
 -> PENDING_HUMAN_GATE


Note:

This document defines mapping only.
No state migration is performed.
