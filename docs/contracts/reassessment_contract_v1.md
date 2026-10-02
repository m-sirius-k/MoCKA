# Contract E: Reassessment Contract v1.0

## ID: CONT-REASSESSMENT-v1.0
## Status: ACTIVE
## Date: 2026-10-02
## Author: MoCKA Implementation Session (E20261002_981617553cb52)

---

## 1. Purpose

Reassessment closes the feedback loop by using Experience Memory to inform
new Assessments. Without Reassessment, the system cannot improve its
assessment accuracy over time.

The loop being closed:
  Experience Memory -> Reassessment -> Assessment Context -> Assessment(A)

---

## 2. Scope

This contract governs:
- ReassessmentContext schema (what Reassessment produces for Assessment)
- When Reassessment is triggered
- How Reassessment queries Experience Memory
- How Reassessment results modify Assessment inputs

---

## 3. ReassessmentContext Schema

Required fields:
- reassessment_id: str          (unique, format: REASSESS-{YYYYMMDD}-{hex8})
- action_id: str                (the action being reassessed)
- timestamp: str                (ISO 8601 UTC)
- prior_outcomes: list[str]     (outcomes from similar past experiences)
- failure_patterns: list[str]   (lessons from FAILURE/PARTIAL outcomes)
- success_patterns: list[str]   (lessons from SUCCESS outcomes)
- confidence_adjustment: float  (-0.5 to +0.5, how to adjust base confidence)
- warnings: list[str]           (specific warnings from past failures)
- similar_experience_count: int (how many similar experiences were found)
- has_prior_data: bool          (whether any experience memory was found)

---

## 4. Trigger Conditions

Reassessment MUST be triggered before Assessment when:
1. The action_id has been executed before (prior_outcomes exists)
2. Similar actions have failed in the past (failure_patterns exists)
3. A Human Gate request for this action type was previously rejected

Reassessment MAY be skipped when:
1. No experience memory exists for similar actions (has_prior_data=False)
   - In this case, ReassessmentContext is created with has_prior_data=False
     and confidence_adjustment=0.0
2. The action is a first-time execution with no comparable history

Reassessment MUST NOT be skipped to improve performance or reduce latency.

---

## 5. Experience Memory Query

Reassessment queries experience memory with:
1. memory_type = "experience"
2. content.action_id = target action_id OR similar by scope/axes
3. Returns ScoredMemory list ordered by relevance_score DESC

Similarity is determined by:
- Same action_id: highest relevance
- Same scope (structural/data/etc.): medium relevance
- Same axes values: medium relevance
- Different scope but same axes: low relevance

---

## 6. Confidence Adjustment

The confidence_adjustment field modifies the base Assessment confidence:
- For each FAILURE in prior_outcomes: -0.1 (max -0.4 from failures)
- For each SUCCESS in prior_outcomes: +0.05 (max +0.2 from successes)
- For each DEVIATION_PATTERN: -0.05
- Net adjustment is clamped to [-0.5, +0.5]

The adjusted confidence is: base_confidence + confidence_adjustment
Assessment MUST apply this adjustment to its confidence calculation.

---

## 7. Warning Generation

Warnings are extracted from failure_patterns and deviation_patterns.
Each warning is a string describing a specific condition to watch for.
Warnings are informational; they do not automatically make assessment inadmissible.
However, a warning that matches a current axis value reduces confidence further.

---

## 8. Relationship to Assessment (Contract A)

Reassessment produces a ReassessmentContext.
Assessment MUST accept an optional ReassessmentContext input.
When ReassessmentContext is provided:
1. confidence_adjustment is applied to base confidence
2. warnings are included in axes evaluation
3. failure_patterns are checked against current axes values

When ReassessmentContext.has_prior_data=False:
- Assessment proceeds with base confidence unchanged
- No additional constraints from Reassessment

---

## 9. Fail-Closed

If Reassessment fails to query memory (exception, timeout):
- A minimal ReassessmentContext with has_prior_data=False is returned
- The failure is logged
- Assessment proceeds as if no prior data exists (conservative)
- The failure itself is treated as a WARNING in the assessment
