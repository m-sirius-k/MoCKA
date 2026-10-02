# Contract B: Action Execution Contract v1.0

## ID: CONT-ACTION-EXECUTION-v1.0
## Status: ACTIVE
## Date: 2026-10-02
## Author: MoCKA Implementation Session (E20261002_981617553cb52)

---

## 1. Purpose

This contract defines the mandatory pipeline that any action execution
MUST pass through. No action may be executed by bypassing this pipeline.

The canonical pipeline is:

  Context(X/Y/Z/T/S/K) -> Assessment(A) -> Authorization(U) ->
  Runtime Conformance(R) -> [A AND U AND R enforcement] -> Execute ->
  Consequence Recording -> Experience Memory

---

## 2. Scope

This contract governs:
- The mandatory execution pipeline steps and their ordering
- What constitutes a valid "execution" for MoCKA purposes
- The role of each pipeline stage
- What records must be created at each stage

---

## 3. Mandatory Pipeline Stages

### Stage 1: Context Grounding
- Grounding engine MUST confirm repository root
- XYZ+T+S+K context MUST be populated from grounding
- If grounding fails: DENY immediately

### Stage 2: Assessment (Contract A)
- AssessmentRecord MUST be created
- All axes MUST be populated (UNKNOWN if not determinable)
- Assessment MUST be admissible before proceeding
- If inadmissible: DENY with assessment_id as evidence

### Stage 3: Authorization (Contract B, this document, Stage 3)
- Human Gate MUST be consulted for APPROVED/REJECTED/PENDING state
- If PENDING: HOLD (do not execute, do not deny immediately)
- If REJECTED or EXPIRED or CANCELED: DENY
- Only APPROVED state allows proceeding to Stage 4

### Stage 4: Runtime Conformance (GL7 dry run)
- GL7 pre_execution_check MUST pass
- No abort conditions may be present
- If abort conditions exist: DENY with abort list

### Stage 5: A AND U AND R Enforcement Point
- All three conditions MUST be True simultaneously
- This is the single, non-byppassable enforcement point
- Enforcement MUST record the check result as an event

### Stage 6: Execute
- Only reachable after Stage 5 passes
- Execution itself is not governed by this contract
- Execution result MUST be captured for Stage 7

### Stage 7: Consequence Recording (Contract C)
- ConsequenceRecord MUST be created after execution
- Success and failure MUST both be recorded
- ConsequenceRecord links to AssessmentRecord

### Stage 8: Experience Memory (Contract D)
- Consequence + Assessment + Context -> ExperienceMemoryEntry
- Entry written to memory store

---

## 4. BA04 Bypass Prevention

This contract defines what constitutes a BA04 bypass:
- Any execution that skips Stage 3 (Authorization) entirely
- Any execution that proceeds when Human Gate returns non-APPROVED
- Any execution where the enforcement point is not evaluated

The enforcement point (Stage 5) is the mechanical implementation of
this contract's BA04 prevention guarantee.

---

## 5. Record Requirements

Each stage that completes MUST produce a traceable record:
- Stage 1: Grounding result (logged by GL7)
- Stage 2: AssessmentRecord (stored in aur/assessment.py)
- Stage 3: Human Gate event (stored in phi_os/human_gate.py SQLite)
- Stage 4: GL7 ApprovalResult (emitted as GL7_EVENT)
- Stage 5: EnforcementRecord (stored by aur/enforcement.py)
- Stage 6: Execution result (caller responsibility)
- Stage 7: ConsequenceRecord (stored by aur/consequence.py)
- Stage 8: ExperienceMemoryEntry (stored in memory store)

---

## 6. Atomicity

Stages 1-5 are a gate (no side effects until Stage 6).
Stages 6-8 are consequence recording (side effects already occurred).
The contract does NOT guarantee atomicity of Stages 6-8 with each other.
If Stage 7 or 8 fails, the execution is still considered to have occurred;
the failure itself MUST be recorded as a consequence.

---

## 7. Fail-Closed

If any stage cannot be determined (exception, timeout, missing data):
- Treat as DENY
- Record the failure reason
- Do NOT proceed to next stage
