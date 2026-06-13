"""
MoCKA 3.0 — Self-Audit Layer
audit_pipeline.py

責務:
  Semantic / Decision / Memory / Governance各層の出力をAuditEngineに
  渡し、AuditReport群とFeedback(prioritized_actions)を生成する
  単一窓口。

  データフロー:
    Semantic/Decision/Memory/Governance
        -> AuditEngine -> AuditAnalyzer
        -> FeedbackGenerator -> ImprovementScorer
        -> AuditReport

  非実行原則・逆流禁止:
    本Pipelineは各層のPipeline/Storeを読み取り専用で利用し、
    Decision/Governance/Memory/Semanticへの書き込みは一切行わない。
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SEMANTIC_DIR = _ROOT / "semantic"
_DECISION_DIR = _ROOT / "decision"
_MEMORY_DIR = _ROOT / "memory"

for _dir in (_SEMANTIC_DIR, _DECISION_DIR, _MEMORY_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from decision_pipeline import DecisionPipeline  # noqa: E402
from decision_sample_cases import DECISION_SAMPLE_CASES  # noqa: E402
from memory_store import MemoryStore  # noqa: E402
from semantic_pipeline import SemanticPipeline  # noqa: E402
from semantic_sample_cases import SAMPLE_CASES  # noqa: E402

from audit_engine import AuditEngine  # noqa: E402
from audit_model import PrioritizedAction  # noqa: E402
from feedback_generator import FeedbackGenerator  # noqa: E402
from improvement_scorer import ImprovementScorer  # noqa: E402


class AuditPipeline:
    """4層を統合的に評価し、AuditReport群とprioritized_actionsを生成するPipeline。"""

    def __init__(self, engine: AuditEngine = None, memory_store: MemoryStore = None):
        self._engine = engine or AuditEngine()
        self._memory_store = memory_store or MemoryStore()
        self._feedback_generator = FeedbackGenerator(ImprovementScorer())

    # ------------------------------------------------------------------
    def audit_semantic_layer(self, sample_cases: tuple = None) -> "AuditReport":
        """Semantic Layerをsample_casesで評価しAuditReportを返す。"""
        sample_cases = sample_cases if sample_cases is not None else SAMPLE_CASES
        pipeline = SemanticPipeline()

        results = []
        for case in sample_cases:
            semantic_result = pipeline.process(case["text"], case.get("context"))
            results.append((
                case["text"],
                case.get("expected_intent"),
                semantic_result,
                case.get("context"),
            ))

        return self._engine.audit_semantic("semantic_layer", tuple(results))

    # ------------------------------------------------------------------
    def audit_decision_layer(self, sample_cases: tuple = None) -> tuple:
        """Decision Layerをsample_casesで評価し、AuditReportのtupleを返す。"""
        sample_cases = sample_cases if sample_cases is not None else DECISION_SAMPLE_CASES
        semantic_pipeline = SemanticPipeline()
        decision_pipeline = DecisionPipeline()

        reports = []
        for case in sample_cases:
            semantic_result = semantic_pipeline.process(case["text"], case.get("context"))
            decision_result = decision_pipeline.decide_from_semantic(semantic_result)
            target_id = f"decision_layer:{case['name']}"
            reports.append(self._engine.audit_decision(target_id, decision_result, semantic_result))

        return tuple(reports)

    # ------------------------------------------------------------------
    def audit_memory_layer(self) -> "AuditReport":
        """Memory Storeの全エントリを評価しAuditReportを返す。"""
        entries = self._memory_store.all()
        return self._engine.audit_memory("memory_layer", entries)

    # ------------------------------------------------------------------
    def audit_governance_layer(self) -> "AuditReport":
        """Governance Layerの静的状態を評価しAuditReportを返す。"""
        return self._engine.audit_governance("governance_layer")

    # ------------------------------------------------------------------
    def run_full_audit(self) -> dict:
        """
        Semantic/Decision/Memory/Governanceの全層を評価し、
        AuditReport群とprioritized_actionsをまとめて返す。

        Returns:
            {
                "semantic": AuditReport,
                "decision": tuple[AuditReport],
                "memory": AuditReport,
                "governance": AuditReport,
                "prioritized_actions": tuple[PrioritizedAction],
            }
        """
        semantic_report = self.audit_semantic_layer()
        decision_reports = self.audit_decision_layer()
        memory_report = self.audit_memory_layer()
        governance_report = self.audit_governance_layer()

        all_suggestions = list(semantic_report.improvement_suggestions)
        for report in decision_reports:
            all_suggestions.extend(report.improvement_suggestions)
        all_suggestions.extend(memory_report.improvement_suggestions)
        all_suggestions.extend(governance_report.improvement_suggestions)

        prioritized_actions = self._feedback_generator.generate_prioritized_actions(tuple(all_suggestions))

        return {
            "semantic": semantic_report,
            "decision": decision_reports,
            "memory": memory_report,
            "governance": governance_report,
            "prioritized_actions": prioritized_actions,
        }

    @staticmethod
    def to_dict(audit_result: dict) -> dict:
        """run_full_audit()の戻り値をJSON互換のdictに変換する。"""
        return {
            "semantic": audit_result["semantic"].to_dict(),
            "decision": [r.to_dict() for r in audit_result["decision"]],
            "memory": audit_result["memory"].to_dict(),
            "governance": audit_result["governance"].to_dict(),
            "prioritized_actions": [
                a.to_dict() if isinstance(a, PrioritizedAction) else a
                for a in audit_result["prioritized_actions"]
            ],
        }
