# -*- coding: utf-8 -*-
"""Layer Snapshot Builder (Phase 5 Cross-Layer Consistency Engine)

役割: MoCKA全8層 (Semantic / Decision / Memory / Self-Audit / Feedback /
Learning / Reality / Report) の現在状態を1回の実行で取得し、UnifiedSnapshot
として束ねる。

実装方針:
  - Reality (reality_sync) と Report (report_truth_governance) は Phase 4-2/4-3
    の既存pipelineをそのまま再利用する (判定ロジックの二重実装禁止)。
  - Semantic / Decision / Memory / Self-Audit / Feedback は
    self_audit.audit_pipeline.AuditPipeline().run_full_audit() が単一実行で
    SAMPLE_CASES に対する評価結果を返すため、これを正本データとして使う。
  - Feedback / Learning は feedback.feedback_pipeline.FeedbackPipeline().run()
    および learning_kernel.learning_pipeline.LearningPipeline().run() を実行する。
    LearningPipeline.run() はQueue登録のみでLearning Stateを変更しない
    (learning_pipeline.py のdocstring準拠)。
  - いずれかの層が import/実行に失敗した場合は status="UNAVAILABLE" として
    記録し、推測値で埋めない。
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field

REPO_ROOT = Path("C:/Users/sirok/MoCKA")

for sub in ("", "self_audit", "feedback", "learning_kernel", "memory", "decision", "semantic"):
    p = str(REPO_ROOT / sub) if sub else str(REPO_ROOT)
    if p not in sys.path:
        sys.path.insert(0, p)


@dataclass
class LayerSnapshot:
    layer: str
    status: str               # "OK" / "UNAVAILABLE"
    data: dict = field(default_factory=dict)
    evidence: str = ""


@dataclass
class UnifiedSnapshot:
    layers: dict = field(default_factory=dict)  # layer_name -> LayerSnapshot

    def get(self, layer: str) -> LayerSnapshot:
        return self.layers.get(layer, LayerSnapshot(layer=layer, status="UNAVAILABLE", evidence="NOT_BUILT"))


def _build_self_audit_layers() -> dict:
    """AuditPipeline().run_full_audit() から Semantic/Decision/Memory/Self-Audit
    の4層スナップショットを構築する。"""
    from self_audit.audit_pipeline import AuditPipeline

    result = {}
    try:
        audit_result = AuditPipeline().run_full_audit()

        semantic_report = audit_result["semantic"]
        result["semantic"] = LayerSnapshot(
            layer="semantic",
            status="OK",
            data={
                "target_id": semantic_report.target_id,
                "evaluation_score": semantic_report.evaluation_score,
                "severity_level": semantic_report.severity_level,
                "issue_count": len(semantic_report.issue_list),
            },
            evidence="self_audit.AuditPipeline.run_full_audit()['semantic']",
        )

        decision_reports = audit_result["decision"]
        scores = [r.evaluation_score for r in decision_reports]
        result["decision"] = LayerSnapshot(
            layer="decision",
            status="OK",
            data={
                "target_ids": [r.target_id for r in decision_reports],
                "scores": scores,
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "severity_levels": [r.severity_level for r in decision_reports],
            },
            evidence="self_audit.AuditPipeline.run_full_audit()['decision']",
        )

        memory_report = audit_result["memory"]
        result["memory"] = LayerSnapshot(
            layer="memory",
            status="OK",
            data={
                "target_id": memory_report.target_id,
                "evaluation_score": memory_report.evaluation_score,
                "severity_level": memory_report.severity_level,
                "issue_count": len(memory_report.issue_list),
            },
            evidence="self_audit.AuditPipeline.run_full_audit()['memory']",
        )

        governance_report = audit_result["governance"]
        prioritized_actions = audit_result.get("prioritized_actions", ())
        result["self_audit"] = LayerSnapshot(
            layer="self_audit",
            status="OK",
            data={
                "governance_target_id": governance_report.target_id,
                "governance_score": governance_report.evaluation_score,
                "governance_severity": governance_report.severity_level,
                "prioritized_action_count": len(prioritized_actions),
            },
            evidence="self_audit.AuditPipeline.run_full_audit()['governance'/'prioritized_actions']",
        )

    except Exception as e:
        for layer in ("semantic", "decision", "memory", "self_audit"):
            result[layer] = LayerSnapshot(
                layer=layer, status="UNAVAILABLE",
                evidence=f"AuditPipeline.run_full_audit() failed: {type(e).__name__}: {e}",
            )

    return result


def _build_feedback_layer() -> LayerSnapshot:
    from feedback.feedback_pipeline import FeedbackPipeline

    try:
        batch = FeedbackPipeline().run()
        risk_levels = [p.risk_level for p in batch.proposals]
        return LayerSnapshot(
            layer="feedback",
            status="OK",
            data={
                "governance_status": batch.governance_status,
                "proposal_count": len(batch.proposals),
                "risk_levels": risk_levels,
                "target_layers": [p.target_layer for p in batch.proposals],
            },
            evidence="feedback.FeedbackPipeline().run()",
        )
    except Exception as e:
        return LayerSnapshot(
            layer="feedback", status="UNAVAILABLE",
            evidence=f"FeedbackPipeline().run() failed: {type(e).__name__}: {e}",
        )


def _build_learning_layer() -> LayerSnapshot:
    from learning_kernel.learning_pipeline import LearningPipeline

    try:
        batch, updates = LearningPipeline().run()
        statuses = [u.status for u in updates]
        return LayerSnapshot(
            layer="learning",
            status="OK",
            data={
                "update_count": len(updates),
                "statuses": statuses,
                "governance_status": batch.governance_status,
            },
            evidence="learning_kernel.LearningPipeline().run() [Queue登録のみ、Learning State不変]",
        )
    except Exception as e:
        return LayerSnapshot(
            layer="learning", status="UNAVAILABLE",
            evidence=f"LearningPipeline().run() failed: {type(e).__name__}: {e}",
        )


def _build_reality_layer() -> LayerSnapshot:
    from reality_sync.sync_engine import run as reality_run

    try:
        results = reality_run()
        fixed = [r for r in results if r.actual_status == "FIXED"]
        broken = [r for r in results if r.actual_status == "BROKEN"]
        return LayerSnapshot(
            layer="reality",
            status="OK",
            data={
                "total": len(results),
                "fixed": len(fixed),
                "broken": len(broken),
                "broken_files": [r.file_path for r in broken],
            },
            evidence="reality_sync.sync_engine.run() [Phase 4-2]",
        )
    except Exception as e:
        return LayerSnapshot(
            layer="reality", status="UNAVAILABLE",
            evidence=f"reality_sync.sync_engine.run() failed: {type(e).__name__}: {e}",
        )


def _build_report_layer() -> LayerSnapshot:
    from report_truth_governance.report_pipeline import run as report_run

    try:
        results, statuses, _ = report_run()
        fail_files = [f for f, s in statuses.items() if s == "FAIL"]
        conflict_files = [r.file_path for r in results if r.conflict_flag]
        return LayerSnapshot(
            layer="report",
            status="OK",
            data={
                "total": len(results),
                "governance_fail_count": len(fail_files),
                "conflict_count": len(conflict_files),
                "conflict_files": conflict_files,
            },
            evidence="report_truth_governance.report_pipeline.run() [Phase 4-3]",
        )
    except Exception as e:
        return LayerSnapshot(
            layer="report", status="UNAVAILABLE",
            evidence=f"report_truth_governance.report_pipeline.run() failed: {type(e).__name__}: {e}",
        )


def build() -> UnifiedSnapshot:
    layers = {}
    layers.update(_build_self_audit_layers())
    layers["feedback"] = _build_feedback_layer()
    layers["learning"] = _build_learning_layer()
    layers["reality"] = _build_reality_layer()
    layers["report"] = _build_report_layer()
    return UnifiedSnapshot(layers=layers)


if __name__ == "__main__":
    snap = build()
    for name, ls in snap.layers.items():
        print(f"{name:<12} {ls.status:<12} {ls.data}")
        if ls.status == "UNAVAILABLE":
            print(f"             evidence: {ls.evidence}")
