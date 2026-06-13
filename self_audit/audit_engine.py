"""
MoCKA 3.0 — Self-Audit Layer
audit_engine.py

責務:
  AuditAnalyzerによる評価結果(score/issues/strengths)を受け取り、
  AuditReportを生成する中核エンジン。
  improvement_suggestionsはFeedbackGeneratorに委譲する。

  非実行原則:
    本モジュールはAuditReportを生成するのみであり、対象層への
    変更・実行は行わない。
"""

from audit_analyzer import AuditAnalyzer
from audit_model import AuditReport, Issue
from audit_registry import score_to_severity
from feedback_generator import FeedbackGenerator
from improvement_scorer import ImprovementScorer


class AuditEngine:
    """各層の出力からAuditReportを生成するEngine。"""

    def __init__(self, analyzer: AuditAnalyzer = None, feedback_generator: FeedbackGenerator = None):
        self._analyzer = analyzer or AuditAnalyzer()
        self._feedback_generator = feedback_generator or FeedbackGenerator(ImprovementScorer())
        self._counter = 0

    def audit_decision(self, target_id: str, decision_result, semantic_result=None) -> AuditReport:
        score, issues, strengths = self._analyzer.analyze_decision(decision_result, semantic_result)
        return self._build_report("decision", target_id, score, issues, strengths)

    def audit_memory(self, target_id: str, entries: tuple) -> AuditReport:
        score, issues, strengths = self._analyzer.analyze_memory(entries)
        return self._build_report("memory", target_id, score, issues, strengths)

    def audit_semantic(self, target_id: str, sample_results: tuple) -> AuditReport:
        score, issues, strengths = self._analyzer.analyze_semantic(sample_results)
        return self._build_report("semantic", target_id, score, issues, strengths)

    def audit_governance(self, target_id: str) -> AuditReport:
        score, issues, strengths = self._analyzer.analyze_governance()
        return self._build_report("governance", target_id, score, issues, strengths)

    def _build_report(self, target_type: str, target_id: str, score: float,
                       issues: list, strengths: list) -> AuditReport:
        self._counter += 1
        audit_id = f"AUDIT_{target_type}_{self._counter:04d}"

        severity_level = score_to_severity(score)
        # issue_list内に より重いseverityが存在する場合はそちらを優先する
        for issue in issues:
            issue_severity = issue.get("severity", "info")
            if _severity_rank(issue_severity) > _severity_rank(severity_level):
                severity_level = issue_severity

        suggestions = self._feedback_generator.generate_suggestions(target_type, target_id, tuple(issues))

        issue_objs = tuple(
            Issue(check=i["check"], description=i["description"], severity=i["severity"])
            for i in issues
        )

        return AuditReport(
            audit_id=audit_id,
            target_type=target_type,
            target_id=target_id,
            evaluation_score=score,
            issue_list=issue_objs,
            strength_list=tuple(strengths),
            improvement_suggestions=suggestions,
            severity_level=severity_level,
        )


def _severity_rank(severity: str) -> int:
    from audit_registry import SeverityLevel
    try:
        return SeverityLevel.ORDER.index(severity)
    except ValueError:
        return 0
