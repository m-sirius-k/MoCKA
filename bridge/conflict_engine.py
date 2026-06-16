# bridge/conflict_engine.py
# 用語衝突解消ルールエンジン v1
#
# 責務:
#   PHI-OS meaning と Personal meaning を比較し ConflictResult を返す。
#   「自動修正禁止」「意味改変禁止」「必ず状態を残す」を遵守する。

from __future__ import annotations
import re
from typing import Optional

from bridge.conflict_types import (
    BridgeRecord,
    ConflictJudgment,
    ConflictResult,
    ConflictState,
)


# ─────────────────────────────────────────────────────────────
# 内部ユーティリティ
# ─────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """比較用に正規化（小文字・空白圧縮のみ。意味は変えない）"""
    return re.sub(r"\s+", " ", text.strip().lower())


def _token_overlap_ratio(a: str, b: str) -> float:
    """2文字列のトークン重複率（0.0–1.0）"""
    ta = set(_normalize(a).split())
    tb = set(_normalize(b).split())
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ─────────────────────────────────────────────────────────────
# 判定閾値
# ─────────────────────────────────────────────────────────────

MATCH_THRESHOLD = 0.85   # これ以上 → MATCH
DRIFT_THRESHOLD = 0.30   # これ以上 → SEMANTIC_DRIFT（以下 → FULL_CONFLICT）


# ─────────────────────────────────────────────────────────────
# ConflictEngine
# ─────────────────────────────────────────────────────────────

class ConflictEngine:
    """
    PHI-OS と Personal の意味を比較し、衝突状態を判定する。

    ルール:
      - 上書き禁止: エンジンは判定のみ行い、意味を変更しない
      - 両方保持: CONFLICT でも両系の意味を保存する
      - 解決はBridge経由のみ: エンジンは状態を返すだけ
    """

    # ── 判定 ──────────────────────────────────────────────────

    def detect(
        self,
        term: str,
        phi_os_meaning: Optional[str],
        personal_meaning: Optional[str],
    ) -> ConflictResult:
        """
        conflict_detect(term) の実装。
        片方または両方が None の場合も安全に処理する。
        """
        judgment, state, reason = self._judge(phi_os_meaning, personal_meaning)

        return ConflictResult(
            term=term,
            judgment=judgment,
            state=state,
            phi_os_meaning=phi_os_meaning,
            personal_meaning=personal_meaning,
            reason=reason,
        )

    def _judge(
        self,
        phi_meaning: Optional[str],
        per_meaning: Optional[str],
    ) -> tuple[ConflictJudgment, ConflictState, str]:
        """
        判定ロジック本体。
        Returns: (judgment, state, reason)
        """
        # ── どちらか未定義 ───────────────────────────────────
        if phi_meaning is None and per_meaning is None:
            return (
                ConflictJudgment.MATCH,
                ConflictState.NORMAL,
                "両系とも未定義のため衝突なし",
            )

        if phi_meaning is None:
            return (
                ConflictJudgment.SEMANTIC_DRIFT,
                ConflictState.DRIFT,
                "PHI-OS に意味なし。Personal のみ存在",
            )

        if per_meaning is None:
            return (
                ConflictJudgment.SEMANTIC_DRIFT,
                ConflictState.DRIFT,
                "Personal に意味なし。PHI-OS のみ存在",
            )

        # ── 完全一致 ─────────────────────────────────────────
        if _normalize(phi_meaning) == _normalize(per_meaning):
            return (
                ConflictJudgment.MATCH,
                ConflictState.NORMAL,
                "意味が完全一致",
            )

        # ── トークン重複率で判定 ─────────────────────────────
        ratio = _token_overlap_ratio(phi_meaning, per_meaning)

        if ratio >= MATCH_THRESHOLD:
            return (
                ConflictJudgment.MATCH,
                ConflictState.NORMAL,
                f"意味が高度に一致 (overlap={ratio:.2f})",
            )

        if ratio >= DRIFT_THRESHOLD:
            return (
                ConflictJudgment.SEMANTIC_DRIFT,
                ConflictState.DRIFT,
                f"意味に乖離あり (overlap={ratio:.2f})",
            )

        return (
            ConflictJudgment.FULL_CONFLICT,
            ConflictState.CONFLICT,
            f"意味が根本的に矛盾 (overlap={ratio:.2f})",
        )

    # ── 既存レコードの状態遷移 ────────────────────────────────

    def transition(
        self,
        record: BridgeRecord,
        new_judgment: ConflictJudgment,
    ) -> ConflictState:
        """
        既存 BridgeRecord の state を新たな判定に基づいて遷移させる。

        LOCKED 状態は外部から明示的に解除されるまで変化しない。
        """
        if record.state == ConflictState.LOCKED:
            return ConflictState.LOCKED

        mapping = {
            ConflictJudgment.MATCH:          ConflictState.NORMAL,
            ConflictJudgment.SEMANTIC_DRIFT:  ConflictState.DRIFT,
            ConflictJudgment.FULL_CONFLICT:   ConflictState.CONFLICT,
        }
        return mapping[new_judgment]

    # ── ロック操作 ────────────────────────────────────────────

    def lock(self, record: BridgeRecord) -> BridgeRecord:
        """BridgeRecord を LOCKED 状態にする（コピーを返す）。"""
        return BridgeRecord(
            term=record.term,
            phi_os_meaning=record.phi_os_meaning,
            personal_meaning=record.personal_meaning,
            state=ConflictState.LOCKED,
            last_sync=record.last_sync,
            conflict_reason=record.conflict_reason,
        )

    def unlock(self, record: BridgeRecord) -> BridgeRecord:
        """LOCKED を解除し、再判定して状態を設定する（コピーを返す）。"""
        result = self.detect(
            record.term, record.phi_os_meaning, record.personal_meaning
        )
        return BridgeRecord(
            term=record.term,
            phi_os_meaning=record.phi_os_meaning,
            personal_meaning=record.personal_meaning,
            state=result.state,
            last_sync=record.last_sync,
            conflict_reason=result.reason,
        )
