"""Policy Engine.

Reference: docs/governance/MODULE_POLICY_ENGINE_v1.md

Third stage of the pipeline. Evaluates each Policy Category (Section 3)
against supplied evidence and produces a tuple of PolicyEvaluation
records (contracts.policy_contract). Pure function.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..contracts.policy_contract import (
    POLICY_CATEGORIES,
    PolicyEvaluation,
    PolicyResult,
)

_VALID_RESULTS = {r.value for r in PolicyResult}


def run_policy(
    module_id: str,
    timestamp: str,
    category_evidence: Mapping[str, Mapping[str, Any]],
) -> tuple[PolicyEvaluation, ...]:
    """Evaluate each Policy Category against ``category_evidence``.

    ``category_evidence`` maps a Policy Category name to a dict with:
      - ``policy_id`` (str)
      - ``criteria`` (str) -- Evaluation Criteria (Section 4)
      - ``result`` (str)   -- one of PolicyResult values; defaults to
        NOT_APPLICABLE if the category is absent from the input.
      - ``evidence`` (dict, optional)
    """

    evaluations: list[PolicyEvaluation] = []
    for category in POLICY_CATEGORIES:
        data = category_evidence.get(category, {})
        result_value = data.get("result", PolicyResult.NOT_APPLICABLE.value)
        if result_value not in _VALID_RESULTS:
            raise ValueError(f"Invalid PolicyResult {result_value!r} for {category!r}")

        evaluations.append(
            PolicyEvaluation(
                policy_id=data.get("policy_id", f"{category.replace(' ', '_').upper()}-{module_id}"),
                category=category,
                target_module=module_id,
                evaluation_criteria=data.get("criteria", f"{category} criteria not provided"),
                result=PolicyResult(result_value),
                evidence=dict(data.get("evidence", {})),
                timestamp=timestamp,
            )
        )

    return tuple(evaluations)
