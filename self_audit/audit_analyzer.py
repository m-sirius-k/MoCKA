"""
MoCKA 3.0 — Self-Audit Layer
audit_analyzer.py

責務:
  Semantic / Decision / Memory / Governance各層の出力を読み取り専用で
  分析し、評価軸ごとのスコア・issue・strengthを算出する。

  非実行原則:
    本モジュールは評価のみを行い、各層のオブジェクト・ファイルを
    一切変更しない。Governance Layerについてはファイル読み取りのみ
    (structural/dogfood_result.json, structural/GL_AUDIT_REPORT.md,
    structural/GOVERNANCE_REGRESSION_SUMMARY.md, mocka_mcp_server.py)。
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_STRUCTURAL_DIR = _ROOT / "structural"

_SEMANTIC_DIR = _ROOT / "semantic"
_DECISION_DIR = _ROOT / "decision"
if str(_SEMANTIC_DIR) not in sys.path:
    sys.path.insert(0, str(_SEMANTIC_DIR))
if str(_DECISION_DIR) not in sys.path:
    sys.path.insert(0, str(_DECISION_DIR))

from decision_registry import get_decision_profile  # noqa: E402


class AuditAnalyzer:
    """各層の評価軸に基づきスコア・issue・strengthを算出するAnalyzer。"""

    # ------------------------------------------------------------------
    # Decision Layer
    # ------------------------------------------------------------------
    def analyze_decision(self, decision_result, semantic_result=None) -> tuple:
        """
        DecisionResultを以下の軸で評価する:
          - priority妥当性
          - risk整合性
          - rationale一貫性

        Returns:
            (score: float, issues: list[dict], strengths: list[str])
        """
        issues = []
        strengths = []
        sub_scores = []

        # --- priority妥当性 ---
        priority_score = decision_result.priority_score
        if 0.0 <= priority_score <= 1.0:
            sub_scores.append(1.0)
            strengths.append("priority_scoreが0-1の範囲内に収まっている")
        else:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "priority妥当性",
                f"priority_score={priority_score} が0-1の範囲外",
                "high",
            ))

        intent_key = None
        if semantic_result is not None:
            intent_key = getattr(semantic_result.intent, "key", None)
        if intent_key:
            profile = get_decision_profile(intent_key)
            if decision_result.selected_action in (profile.default_action,) + profile.alternative_actions:
                sub_scores.append(1.0)
                strengths.append("selected_actionがDecision Registryのaction候補に含まれている")
            else:
                sub_scores.append(0.5)
                issues.append(self._issue(
                    "priority妥当性",
                    f"selected_action='{decision_result.selected_action}' がintent='{intent_key}'の"
                    f"Registry候補に存在しない",
                    "medium",
                ))

        # --- risk整合性 ---
        risk_score = decision_result.risk_score
        if 0.0 <= risk_score <= 1.0:
            sub_scores.append(1.0)
        else:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "risk整合性",
                f"risk_score={risk_score} が0-1の範囲外",
                "high",
            ))

        if risk_score >= 0.6 and not decision_result.risk_factors:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "risk整合性",
                f"risk_score={risk_score}が高いにもかかわらずrisk_factorsが空",
                "medium",
            ))
        else:
            sub_scores.append(1.0)
            if risk_score >= 0.6:
                strengths.append("高risk_scoreに対してrisk_factorsが記録されている")

        if not decision_result.required_governance_check:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "risk整合性",
                "required_governance_check=Falseとなっている"
                "(DecisionLayerは常にGovernance確認を要求すべき)",
                "critical",
            ))
        else:
            sub_scores.append(1.0)
            strengths.append("required_governance_check=Trueが維持されている")

        # --- rationale一貫性 ---
        rationale = decision_result.rationale or ""
        if rationale.strip():
            sub_scores.append(1.0)
        else:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "rationale一貫性",
                "rationaleが空文字列になっている",
                "high",
            ))

        if decision_result.selected_action and decision_result.selected_action in rationale:
            sub_scores.append(1.0)
            strengths.append("rationaleにselected_actionが明記されている")
        else:
            sub_scores.append(0.5)
            issues.append(self._issue(
                "rationale一貫性",
                "rationaleにselected_actionが明記されていない",
                "low",
            ))

        score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        return round(score, 4), issues, strengths

    # ------------------------------------------------------------------
    # Memory Layer
    # ------------------------------------------------------------------
    def analyze_memory(self, entries: tuple) -> tuple:
        """
        MemoryEntryの集合を以下の軸で評価する:
          - 再利用性
          - 一貫性
          - ノイズ率
        """
        issues = []
        strengths = []
        sub_scores = []

        if not entries:
            issues.append(self._issue("一貫性", "Memory Storeにエントリが存在しない", "low"))
            return 0.5, issues, strengths

        # --- 一貫性: 必須フィールドの有無 ---
        consistent = 0
        for entry in entries:
            ok = bool(entry.memory_id) and bool(entry.timestamp) and bool(entry.memory_type)
            if entry.memory_type == "episodic":
                ok = ok and bool((entry.metadata or {}).get("intent_key"))
            if ok:
                consistent += 1
        consistency_ratio = consistent / len(entries)
        sub_scores.append(consistency_ratio)
        if consistency_ratio == 1.0:
            strengths.append("全エントリが必須フィールド(memory_id/timestamp/memory_type)を保持")
        else:
            issues.append(self._issue(
                "一貫性",
                f"必須フィールド欠落エントリが {len(entries) - consistent}/{len(entries)} 件存在",
                "medium",
            ))

        # --- 再利用性: skill memoryの比率 ---
        skill_count = sum(1 for e in entries if e.memory_type == "skill")
        reuse_ratio = skill_count / len(entries)
        sub_scores.append(min(1.0, reuse_ratio * 4))  # skill 25%で満点換算
        if skill_count > 0:
            strengths.append(f"再利用可能なskill memoryが {skill_count} 件蓄積されている")
        else:
            issues.append(self._issue(
                "再利用性",
                "skill memoryが0件であり、再利用可能パターンが蓄積されていない",
                "low",
            ))

        # --- ノイズ率: rationale等の重複率 ---
        texts = []
        for entry in entries:
            content = entry.content or {}
            text = content.get("rationale") or content.get("summary_text") or ""
            if text:
                texts.append(text)

        if texts:
            unique_ratio = len(set(texts)) / len(texts)
            noise_ratio = 1.0 - unique_ratio
            sub_scores.append(unique_ratio)
            if noise_ratio > 0.3:
                issues.append(self._issue(
                    "ノイズ率",
                    f"重複テキストの比率が {noise_ratio:.2f} と高い",
                    "medium",
                ))
            else:
                strengths.append(f"テキストの重複率が低い (noise_ratio={noise_ratio:.2f})")
        else:
            sub_scores.append(1.0)

        score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        return round(score, 4), issues, strengths

    # ------------------------------------------------------------------
    # Semantic Layer
    # ------------------------------------------------------------------
    def analyze_semantic(self, sample_results: tuple) -> tuple:
        """
        sample_results: tuple[(text, expected_intent_key, SemanticResult, context)]

        評価軸:
          - 意図分類精度
          - context補完妥当性
        """
        issues = []
        strengths = []
        sub_scores = []

        if not sample_results:
            issues.append(self._issue("意図分類精度", "評価対象サンプルが0件", "low"))
            return 0.5, issues, strengths

        # --- 意図分類精度 ---
        correct = 0
        for _text, expected_intent, semantic_result, _context in sample_results:
            if expected_intent is None:
                continue
            if semantic_result.intent.key == expected_intent:
                correct += 1

        evaluated = sum(1 for _t, e, _s, _c in sample_results if e is not None)
        if evaluated:
            accuracy = correct / evaluated
            sub_scores.append(accuracy)
            if accuracy >= 0.8:
                strengths.append(f"意図分類精度 {accuracy:.2f} (>= 0.8)")
            else:
                issues.append(self._issue(
                    "意図分類精度",
                    f"意図分類精度 {accuracy:.2f} が0.8未満",
                    "medium",
                ))
        else:
            sub_scores.append(1.0)

        # --- context補完妥当性 ---
        context_checked = 0
        context_ok = 0
        for _text, _expected, semantic_result, context in sample_results:
            if not context:
                continue
            context_checked += 1
            summary = semantic_result.context_summary
            if summary.summary_text.strip():
                context_ok += 1

        if context_checked:
            context_ratio = context_ok / context_checked
            sub_scores.append(context_ratio)
            if context_ratio == 1.0:
                strengths.append("contextが与えられた全サンプルでsummary_textが生成されている")
            else:
                issues.append(self._issue(
                    "context補完妥当性",
                    f"contextが与えられたがsummary_textが空のサンプルが"
                    f" {context_checked - context_ok}/{context_checked} 件存在",
                    "low",
                ))
        else:
            sub_scores.append(1.0)

        score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        return round(score, 4), issues, strengths

    # ------------------------------------------------------------------
    # Governance Layer
    # ------------------------------------------------------------------
    def analyze_governance(self) -> tuple:
        """
        以下のファイルを読み取り専用で分析する:
          - structural/dogfood_result.json   (bypass検出/異常ログ)
          - structural/GOVERNANCE_REGRESSION_SUMMARY.md (Overall PASS)
          - mocka_mcp_server.py (Fail Closed維持)

        評価軸:
          - Fail Closed維持
          - bypass検出
          - 異常ログ
        """
        issues = []
        strengths = []
        sub_scores = []

        # --- Fail Closed維持 ---
        server_path = _ROOT / "mocka_mcp_server.py"
        try:
            server_src = server_path.read_text(encoding="utf-8")
        except OSError:
            server_src = ""

        if "GL_FAIL_CLOSED" in server_src and "READ_ONLY_TOOLS" in server_src:
            sub_scores.append(1.0)
            strengths.append("mocka_mcp_server.pyにGL_FAIL_CLOSED/READ_ONLY_TOOLSの記述を確認")
        else:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "Fail Closed維持",
                "mocka_mcp_server.pyにGL_FAIL_CLOSEDまたはREAD_ONLY_TOOLSの記述が見つからない",
                "critical",
            ))

        # --- bypass検出 / 異常ログ (dogfood_result.json) ---
        dogfood_path = _STRUCTURAL_DIR / "dogfood_result.json"
        try:
            dogfood = json.loads(dogfood_path.read_text(encoding="utf-8"))
            summary = dogfood.get("summary", {})
        except (OSError, json.JSONDecodeError):
            summary = None

        if summary is None:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "bypass検出",
                "structural/dogfood_result.jsonの読み込みに失敗",
                "high",
            ))
        else:
            if summary.get("bypassed", 1) == 0 and summary.get("fatal_errors", 1) == 0:
                sub_scores.append(1.0)
                strengths.append("dogfood_result.json: bypassed=0, fatal_errors=0")
            else:
                sub_scores.append(0.0)
                issues.append(self._issue(
                    "bypass検出",
                    f"bypassed={summary.get('bypassed')}, "
                    f"fatal_errors={summary.get('fatal_errors')}",
                    "critical",
                ))

            if summary.get("write_aborted", 1) == 0 and summary.get("checklist_fail_count", 1) == 0:
                sub_scores.append(1.0)
                strengths.append("dogfood_result.json: write_aborted=0, checklist_fail_count=0")
            else:
                sub_scores.append(0.0)
                issues.append(self._issue(
                    "異常ログ",
                    f"write_aborted={summary.get('write_aborted')}, "
                    f"checklist_fail_count={summary.get('checklist_fail_count')}",
                    "high",
                ))

        # --- Governance Regression Summary (Overall PASS) ---
        regression_path = _STRUCTURAL_DIR / "GOVERNANCE_REGRESSION_SUMMARY.md"
        try:
            regression_text = regression_path.read_text(encoding="utf-8")
        except OSError:
            regression_text = ""

        if "Overall PASS" in regression_text:
            sub_scores.append(1.0)
            strengths.append("GOVERNANCE_REGRESSION_SUMMARY.mdにOverall PASSを確認")
        else:
            sub_scores.append(0.0)
            issues.append(self._issue(
                "異常ログ",
                "GOVERNANCE_REGRESSION_SUMMARY.mdに'Overall PASS'が見つからない",
                "critical",
            ))

        score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
        return round(score, 4), issues, strengths

    # ------------------------------------------------------------------
    @staticmethod
    def _issue(check: str, description: str, severity: str) -> dict:
        return {"check": check, "description": description, "severity": severity}
