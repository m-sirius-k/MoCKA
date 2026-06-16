# orchestra/conflict_interpreter.py
# Orchestra Layer v1 — Conflict 説明文生成・人間翻訳層
#
# アーキテクチャ上の位置:
#   Bridge → PHI-OS → Orchestra → UI
#
# 責務:
#   ConflictEvent + Decision を受け取り、人間が読める説明文を生成する。
#   文脈補助・翻訳のみ。状態変更禁止。
#
# 禁止:
#   - conflict state の変更
#   - 意味の書き換え・統合
#   - Bridge / PHI-OS へのフィードバック

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Optional

from phi_os.phi_bridge_governance import ConflictEvent, Decision, DecisionKind


# ─────────────────────────────────────────────────────────────
# Interpretation — Orchestra の出力単位
# ─────────────────────────────────────────────────────────────

@dataclass
class Interpretation:
    term: str
    event_id: str
    decision_kind: str
    summary: str          # 1行サマリ
    detail: str           # 詳細説明文（人間向け）
    suggestion: str       # 次のアクション提案（実行権限なし）
    interpreted_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "term":           self.term,
            "event_id":       self.event_id,
            "decision_kind":  self.decision_kind,
            "summary":        self.summary,
            "detail":         self.detail,
            "suggestion":     self.suggestion,
            "interpreted_at": self.interpreted_at,
        }


# ─────────────────────────────────────────────────────────────
# ConflictInterpreter
# ─────────────────────────────────────────────────────────────

class ConflictInterpreter:
    """
    ConflictEvent と Decision を人間可読な Interpretation に変換する。

    このクラスはいかなる状態も保持しない（ステートレス）。
    意味を変更しない。提案するが実行しない。
    """

    def interpret(
        self,
        event: ConflictEvent,
        decision: Decision,
    ) -> Interpretation:
        """
        ConflictEvent + Decision → Interpretation。
        state・意味フィールドには一切書き込まない。
        """
        summary = self._make_summary(event, decision)
        detail  = self._make_detail(event, decision)
        suggestion = self._make_suggestion(decision)

        return Interpretation(
            term=event.term,
            event_id=event.event_id,
            decision_kind=decision.kind.value,
            summary=summary,
            detail=detail,
            suggestion=suggestion,
        )

    def interpret_batch(
        self,
        pairs: list[tuple[ConflictEvent, Decision]],
    ) -> list[Interpretation]:
        return [self.interpret(e, d) for e, d in pairs]

    # ── 内部テンプレート生成 ──────────────────────────────────

    def _make_summary(self, event: ConflictEvent, decision: Decision) -> str:
        kind_label = {
            DecisionKind.OBSERVE: "監視中",
            DecisionKind.TAG:     "保留タグ付き",
            DecisionKind.ROUTE:   "上位ルーティング待ち",
        }.get(decision.kind, "不明")

        return (
            f"「{event.term}」— {kind_label} "
            f"[severity={decision.severity:.2f} / state={event.conflict_state}]"
        )

    def _make_detail(self, event: ConflictEvent, decision: Decision) -> str:
        phi_str = event.phi_os_meaning or "(未定義)"
        per_str = event.personal_meaning or "(未定義)"

        lines = [
            f"用語: {event.term}",
            f"",
            f"PHI-OS の意味:",
            f"  {phi_str}",
            f"",
            f"Personal の意味:",
            f"  {per_str}",
            f"",
            f"衝突状態: {event.conflict_state}",
            f"衝突理由: {event.conflict_reason}",
            f"",
            f"PHI-OS 判断: {decision.kind.value}",
            f"判断メモ: {decision.note}",
            f"",
            f"※ 両意味は保持されています。統合・解決は行われていません。",
        ]
        return "\n".join(lines)

    def _make_suggestion(self, decision: Decision) -> str:
        suggestions = {
            DecisionKind.OBSERVE: (
                "低強度衝突です。現時点では介入不要です。"
                "定期的な状態確認を推奨します。"
            ),
            DecisionKind.TAG: (
                "中強度衝突です。人間による確認を推奨します。"
                "Bridge の conflict_history() で変化経緯を確認できます。"
                "解決する場合は Bridge.unlock() → 手動同期 の順で行ってください。"
            ),
            DecisionKind.ROUTE: (
                "高強度衝突です。上位判断が必要です。"
                "Bridge.lock() で状態を凍結してから意思決定を行ってください。"
                "PHI-OS と Personal の意味は保持されたままです。"
            ),
        }
        return suggestions.get(decision.kind, "判断不能。手動確認を推奨します。")


# ─────────────────────────────────────────────────────────────
# 全パイプライン統合ヘルパー
# ─────────────────────────────────────────────────────────────

def run_full_pipeline(
    records: list,
    governance,
    interpreter: Optional[ConflictInterpreter] = None,
) -> list[dict]:
    """
    BridgeRecord のリストを bridge → PHI-OS → Orchestra に流し、
    結果を辞書リストで返す。状態変更は行わない。

    返り値の各要素:
      {
        "record":         BridgeRecord,
        "event":          ConflictEvent,
        "decision":       Decision,
        "interpretation": Interpretation,
      }
    """
    from phi_os.phi_bridge_governance import event_from_bridge_record

    if interpreter is None:
        interpreter = ConflictInterpreter()

    results = []
    for record in records:
        event = event_from_bridge_record(record)
        decision = governance.process(event)
        interpretation = interpreter.interpret(event, decision)
        results.append({
            "record":         record,
            "event":          event,
            "decision":       decision,
            "interpretation": interpretation,
        })

    return results
