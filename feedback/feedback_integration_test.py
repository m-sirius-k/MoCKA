"""
MoCKA 3.0 — Feedback Loop 統合テスト

確認内容:
  - Feedback Layerが独立モジュールとして動作すること
  - Audit -> Feedback への変換が可能であること
  - Feedback分類(target_layer/feedback_type)が正しく行われること
  - Weight調整提案・Memory強化提案・Decision改善提案が生成されること
  - Governanceチェックを通過すること(requires_governance_check/status)
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SELF_AUDIT_DIR = _HERE.parent / "self_audit"

for _dir in (_HERE, _SELF_AUDIT_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from audit_pipeline import AuditPipeline  # noqa: E402
from audit_registry import TargetType  # noqa: E402

from feedback_engine import FeedbackEngine  # noqa: E402
from feedback_model import FeedbackBatch, FeedbackProposal  # noqa: E402
from feedback_pipeline import FeedbackPipeline  # noqa: E402
from feedback_registry import TargetLayer  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    pipeline = FeedbackPipeline()
    batch = pipeline.run()

    # --- FeedbackBatchの型 ---
    results.append(check(
        "FeedbackPipeline.run() returns a FeedbackBatch",
        isinstance(batch, FeedbackBatch),
    ))
    results.append(check(
        "FeedbackBatch.proposals is a tuple",
        isinstance(batch.proposals, tuple),
    ))
    results.append(check(
        "FeedbackBatch.governance_status is one of PASS/FAIL/UNKNOWN",
        batch.governance_status in ("PASS", "FAIL", "UNKNOWN"),
    ))

    # --- Audit -> Feedback変換 ---
    results.append(check(
        "FeedbackPipeline.run() produces at least 1 proposal",
        len(batch.proposals) > 0,
    ))
    results.append(check(
        "all proposals are FeedbackProposal instances",
        all(isinstance(p, FeedbackProposal) for p in batch.proposals),
    ))

    # --- Feedback分類 ---
    results.append(check(
        "all proposals have target_layer in TargetLayer.ALL",
        all(p.target_layer in TargetLayer.ALL for p in batch.proposals),
    ))

    # --- Decision改善提案 ---
    decision_proposals = [p for p in batch.proposals if p.target_layer == TargetLayer.DECISION]
    results.append(check(
        "at least 1 Decision-layer proposal is generated",
        len(decision_proposals) > 0,
    ))
    results.append(check(
        "Decision proposals contain 'tuning' in suggested_change",
        all("tuning" in p.suggested_change for p in decision_proposals),
    ))

    # --- Weight調整提案 ---
    weight_proposals = [p for p in batch.proposals if "weight_adjustment" in p.suggested_change]
    results.append(check(
        "at least 1 proposal contains a weight_adjustment suggestion",
        len(weight_proposals) > 0,
    ))

    # --- Memory強化提案(存在する場合のみ検証) ---
    memory_proposals = [p for p in batch.proposals if p.target_layer == TargetLayer.MEMORY]
    if memory_proposals:
        results.append(check(
            "Memory proposals contain 'reinforcement' in suggested_change",
            all("reinforcement" in p.suggested_change for p in memory_proposals),
        ))

    # --- Governanceチェック ---
    results.append(check(
        "all proposals have requires_governance_check == True",
        all(p.requires_governance_check is True for p in batch.proposals),
    ))
    results.append(check(
        "all proposals have status in (pending_governance_review, blocked)",
        all(p.status in ("pending_governance_review", "blocked") for p in batch.proposals),
    ))
    if batch.governance_status == "PASS":
        results.append(check(
            "governance_status PASS -> all proposals are pending_governance_review",
            all(p.status == "pending_governance_review" for p in batch.proposals),
        ))

    # --- 値の範囲 ---
    results.append(check(
        "expected_impact/confidence are within [0, 1]",
        all(0.0 <= p.expected_impact <= 1.0 and 0.0 <= p.confidence <= 1.0 for p in batch.proposals),
    ))

    # --- Governance LayerはFeedback対象外(逆流禁止) ---
    audit_pipeline = AuditPipeline()
    governance_report = audit_pipeline.audit_governance_layer()
    engine = FeedbackEngine()
    governance_proposals = engine.generate(governance_report)
    results.append(check(
        f"AuditReport(target_type='{TargetType.GOVERNANCE}') produces no FeedbackProposal",
        governance_proposals == (),
    ))

    # --- to_dict()の動作確認 ---
    batch_dict = batch.to_dict()
    results.append(check(
        "FeedbackBatch.to_dict() contains 'proposals' and 'governance_status'",
        "proposals" in batch_dict and "governance_status" in batch_dict,
    ))
    if batch.proposals:
        proposal_dict = batch.proposals[0].to_dict()
        results.append(check(
            "FeedbackProposal.to_dict() contains required keys",
            all(key in proposal_dict for key in (
                "feedback_id", "source_audit_id", "target_layer", "issue_reference",
                "suggested_change", "expected_impact", "confidence", "risk_level",
                "requires_governance_check", "status",
            )),
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
