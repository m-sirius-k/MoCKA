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

Admissibility is a comprehensive contract-based judgment. It is NOT determined
by confidence score alone.

  Evidence + Observation Context + Interpretation Separation
  + Freshness/Validity + Uncertainty + Impact
  + UNKNOWN conditions + contract-specific conditions
      -> admissible (True/False)
      -> confidence = auxiliary value expressing result uncertainty

CRITICAL INVARIANTS:
  UNKNOWN != FALSE
    An axis value of "UNKNOWN" means "could not determine", not "false".
    UNKNOWN does NOT automatically make the assessment inadmissible.
    UNKNOWN reduces confidence and must be reflected in the confidence score.

  UNKNOWN != auto-ALLOW
    UNKNOWN does not grant admissibility. All other admissibility
    conditions must still be satisfied.

  confidence >= threshold alone does NOT make admissible.
    Sufficient confidence is necessary but not sufficient for admissibility.

  confidence < threshold CAN make inadmissible (auxiliary fail-closed gate).
    Low confidence is evidence that admissibility cannot be affirmed.

Assessment is admissible (admissible=True) only when ALL of the following hold:

1. No axis contains a known violation (VIOLATION/FORBIDDEN/BLOCKED)
2. X (Evidence) is present and not absent
   - None or "" (not gathered) -> inadmissible, regardless of confidence
   - "UNKNOWN" (tried but could not determine) -> confidence reduced only
3. T (Freshness) is not expired or invalid
   - "expired", "stale", "invalid" in T -> inadmissible
   - "UNKNOWN" freshness -> confidence reduced only
4. Y (Interpretation) is separated from X (Evidence)
   - Y == X (identical non-UNKNOWN string) -> inadmissible (not separated)
   - "UNKNOWN" interpretation -> confidence reduced only
5. confidence >= CONFIDENCE_THRESHOLD (default: 0.5) — auxiliary gate

Assessment is inadmissible (admissible=False) if any of:
1. Any axis contains a known violation
2. X (Evidence) is None or "" (absent)
3. T (Freshness) contains "expired", "stale", "invalid", "outdated", "revoked"
4. Y (Interpretation) is identical to X (both non-UNKNOWN, not separated)
5. confidence < CONFIDENCE_THRESHOLD after all adjustments

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
