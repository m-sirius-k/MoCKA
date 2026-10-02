# Contract A: Assessment Contract v1.0

## ID: CONT-ASSESSMENT-v1.0
## Status: ACTIVE
## Date: 2026-10-02
## Author: MoCKA Implementation Session (E20261002_981617553cb52)

---

## 1. Purpose

Assessment (A) is the formal evaluation of whether an action is admissible
for execution. It is the first condition of the A-U-R theorem:

  Executable(a,t) <=> Assessment_Admissible(a,t) AND Authority_Valid(a,t) AND Runtime_Conformant(a,t)

Assessment does NOT grant permission. It evaluates evidence and returns
a structured record. Authorization (Human Gate) remains the final authority.

---

## 2. Scope

This contract governs:
- AssessmentRecord schema (what fields must be present)
- Assessment admissibility criteria (when is assessment considered admissible)
- Caller obligations (who creates assessments, when, and how)
- Assessment lifecycle (creation, invalidation, use in enforcement)

---

## 3. AssessmentRecord Schema

Required fields:
- assessment_id: str  (unique, format: ASSESS-{YYYYMMDD}-{hex8})
- action_id: str      (the action being assessed)
- timestamp: str      (ISO 8601 UTC)
- axes: dict          (XYZ+T+S+K evidence, see Section 4)
- admissible: bool    (final admissibility judgment)
- reason: str         (human-readable explanation)
- confidence: float   (0.0 to 1.0)
- assessor: str       (who/what performed this assessment)

Optional fields:
- scope: list[str]    (which systems/files are in scope)
- constraints: dict   (assessed constraints)

---

## 4. XYZ+T+S+K Evidence Requirements

Each assessment MUST populate the axes dict with at minimum:
- X (Evidence): factual grounding data used
- Y (Interpretation): how X was interpreted
- Z (Authority): what authority context applies
- T (Time/Freshness): when was the evidence collected, is it stale?
- S (Social Impact): who is affected, what are the side effects?
- K (Institutional Structure): which institutional rules apply?

If an axis cannot be determined, the value MUST be "UNKNOWN" (not None, not omitted).
UNKNOWN on any axis does NOT automatically make assessment inadmissible, but
it reduces confidence and MUST be reflected in the confidence score.

---

## 5. Admissibility Criteria

Assessment is admissible (admissible=True) if and only if:
1. All required axes are populated (UNKNOWN is acceptable for unknown values)
2. No axis indicates a known violation
3. Confidence >= CONFIDENCE_THRESHOLD (default: 0.5)
4. The action_id refers to a known, scoped action

Assessment is inadmissible (admissible=False) if:
1. Any axis contains evidence of a constraint violation
2. Confidence < CONFIDENCE_THRESHOLD
3. Grounding has not been completed (grounding_not_completed abort condition)
4. The action scope would cause deletion_outside_scope

---

## 6. Caller Obligations

Any caller requesting execution MUST:
1. Create an AssessmentRecord BEFORE calling enforcement
2. Pass the assessment_id to the enforcement point
3. NOT cache or reuse assessments across different action executions
4. Record assessment creation as a mocka_write_event

---

## 7. Invalidation

An AssessmentRecord is invalidated when:
- More than 300 seconds have elapsed since timestamp (T axis stale)
- The action scope has changed since assessment was created
- A new GL7 dry run produces different results
- Human Gate rejects the associated request

---

## 8. Relationship to Authorization (U) and Runtime (R)

Assessment (A) is a prerequisite for enforcement but is NOT authorization.
The Human Gate (U) independently verifies authority.
GL7 (R) independently verifies runtime conformance.

The enforcement point checks A AND U AND R simultaneously.
A single assessment does not substitute for U or R.

---

## 9. Fail-Closed Rule

If Assessment cannot be performed (exception, timeout, missing data):
- admissible MUST be False
- reason MUST explain the failure
- The enforcement point MUST deny execution

UNKNOWN != FALSE, but ASSESSMENT_UNAVAILABLE -> DENY (fail-closed).

---

## 10. Non-Delegatable Properties

- assessment_id generation: must be system-generated, not caller-supplied
- timestamp: must be system UTC time, not caller-supplied
- admissible: derived from axes evaluation, not caller-supplied
