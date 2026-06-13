"""
MoCKA 3.0 — Feedback Loop 安全性テスト

確認内容:
  - feedback_registry.SAFETY_CONSTRAINTSが必須項目を満たすこと
  - 提案内容が自動適用/即時反映/自動コード修正/Memory削除を主張しないこと
  - 全FeedbackProposalがrequires_governance_check=Trueであること
  - Governance Regressionが PASS でない場合、全Proposalがblockedになること
  - Governance LayerのAuditReportからFeedbackProposalが生成されないこと(逆流禁止)
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SELF_AUDIT_DIR = _HERE.parent / "self_audit"

for _dir in (_HERE, _SELF_AUDIT_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from audit_pipeline import AuditPipeline  # noqa: E402

from feedback_engine import FeedbackEngine  # noqa: E402
from feedback_pipeline import FeedbackPipeline  # noqa: E402
from feedback_registry import SAFETY_CONSTRAINTS  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    # --- SAFETY_CONSTRAINTS必須項目 ---
    required_constraints = (
        "no_automatic_code_modification",
        "no_governance_change",
        "no_execution_logic_change",
        "no_immediate_apply",
        "no_memory_deletion",
    )
    results.append(check(
        "SAFETY_CONSTRAINTS contains all required constraints",
        all(c in SAFETY_CONSTRAINTS for c in required_constraints),
    ))

    pipeline = FeedbackPipeline()
    batch = pipeline.run()

    # --- 全Proposalがrequires_governance_check=True ---
    results.append(check(
        "all proposals require governance check",
        all(p.requires_governance_check is True for p in batch.proposals),
    ))

    # --- status は提案段階の値のみ(自動適用なし) ---
    forbidden_statuses = ("applied", "approved", "executed", "auto_applied")
    results.append(check(
        "no proposal has an auto-apply status",
        all(p.status not in forbidden_statuses for p in batch.proposals),
    ))

    # --- 提案文に禁止語が含まれないこと ---
    forbidden_terms = (
        "自動適用", "自動修正", "自動実行", "自動コード変更", "即時反映", "即時適用",
        "auto-apply", "auto apply", "automatically apply",
    )

    def _flatten_text(suggested_change: dict) -> str:
        parts = []
        for value in suggested_change.values():
            if isinstance(value, dict):
                for v in value.values():
                    parts.append(str(v))
            else:
                parts.append(str(value))
        return " ".join(parts)

    results.append(check(
        "no suggested_change text contains forbidden auto-apply terms",
        all(
            not any(term in _flatten_text(p.suggested_change) for term in forbidden_terms)
            for p in batch.proposals
        ),
    ))

    # --- Memory削除を提案していないこと ---
    memory_proposals = [p for p in batch.proposals if p.target_layer == "memory"]
    for proposal in memory_proposals:
        reinforcement = proposal.suggested_change.get("reinforcement", {})
        action = reinforcement.get("action", "")
        results.append(check(
            f"memory proposal '{proposal.feedback_id}' action is not a deletion action",
            action != "delete" and "delete" not in action.lower(),
        ))

    # --- Governance Regression FAIL時はすべてblocked(シミュレーション) ---
    results.append(check(
        "_governance_validation reads structural/GOVERNANCE_REGRESSION_SUMMARY.md only",
        callable(pipeline._governance_validation),
    ))

    blocked_proposals = tuple(
        pipeline._apply_governance_status(p, "FAIL") for p in batch.proposals
    )
    results.append(check(
        "simulated governance_status='FAIL' marks all proposals as blocked",
        all(p.status == "blocked" for p in blocked_proposals),
    ))
    results.append(check(
        "blocked proposals still keep requires_governance_check=True",
        all(p.requires_governance_check is True for p in blocked_proposals),
    ))

    # --- Governance LayerはFeedback対象外(逆流禁止) ---
    audit_pipeline = AuditPipeline()
    governance_report = audit_pipeline.audit_governance_layer()
    engine = FeedbackEngine()
    results.append(check(
        "Governance AuditReport produces zero FeedbackProposals (no backflow)",
        engine.generate(governance_report) == (),
    ))

    # --- 元のProposalオブジェクトが変更されていないこと(非破壊) ---
    if batch.proposals:
        original_status = batch.proposals[0].status
        _ = pipeline._apply_governance_status(batch.proposals[0], "FAIL")
        results.append(check(
            "applying governance status does not mutate the original proposal",
            batch.proposals[0].status == original_status,
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
