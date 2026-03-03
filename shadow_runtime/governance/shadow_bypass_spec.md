# Shadow Bypass Spec v0.1

## Purpose
Shadow is a bypass heart that keeps the business running under attack by switching to a degraded safe path.

## Invariants
- Do not stop the main system unless explicitly commanded.
- Shadow bypass must be able to sustain "75% operation" as defined below.
- All bypass decisions must be observable and reproducible.

## Definition of "75%"
- Scope: core business flows only (define list)
- Default rule: read operations continue; writes are restricted (define allowlist)
- Output: must remain verifiable (deterministic artifacts)

## Switch Conditions
- Condition set A: integrity / determinism failure (sha/signature/CI verifier)
- Condition set B: latency / error threshold (define)
- Manual override always allowed.

## Observation and Recording
- Emit a one-line alert record for each detected change.
- Append a ledger row for each change with input/output hashes and classification.

## Repair Policy
- Auto-repair is allowed only when:
  - playbook is approved (signed/authorized)
  - impact is narrow
  - throttling window allows
- Otherwise, generate a repair proposal only.

## Anti Self-Attack Rules
- Every repair attempt must carry repair_id.
- Suppression window prevents repeated repair on same target.
- Changes tagged with repair_id are not treated as hostile.
