# MoCKA/semantic/query_engine/semantic_projection_layer.py
# Phase9-2 - Semantic Projection Layer v0 (structure + empty methods only)
#
# 契約: docs/contracts/phase9_1_semantic_projection_v1.md
#
# 重要な前提: これは推論器ではない。候補生成アルゴリズム・ランキング
# ロジックはPhase9-3以降に分離する。本ファイルはインターフェースの
# 形のみを固定する(本体はNotImplementedError、候補生成は未実装)。
#
# Phase9-3以降でも恒久的に禁止される事項（監査結果より）:
#   - 自動採択 (return candidates[0])
#   - confidence最大選択 (best = max(candidates))
#   - 候補削除 (if score < threshold: drop())
#   - candidate merge (A + B)
#   - Human Gate代行 (winner = choose(...))
#   - Runtime直接起動 (runtime.execute(...))
# Projectionは候補生成まで。実行権限を持たない。

from semantic.query_engine.projection_result import (
    ProjectionResult,
    DIRECTION_NL_TO_EVENT,
    DIRECTION_EVENT_TO_NL,
)


class SemanticProjectionLayer:
    """自然言語とEventの双方向投影層(構造のみ、候補生成は未実装)。

    PHI-OS Core / Runtime(Phase8) / Human Gate(Phase7-B6/B7)のいずれも
    呼び出し・変更しない。本クラスは候補を生成する権限のみを持ち、
    実行権限は持たない。
    """

    def nl_to_event_candidates(self, text: str) -> ProjectionResult:
        """自然言語 -> Event候補群。候補生成アルゴリズムはPhase9-3以降。"""
        raise NotImplementedError(
            "candidate generation is deferred to Phase9-3 "
            "(see docs/contracts/phase9_1_semantic_projection_v1.md section 6)"
        )

    def event_to_nl_candidates(self, identifier: str) -> ProjectionResult:
        """Event -> 自然言語説明候補群。候補生成アルゴリズムはPhase9-3以降。"""
        raise NotImplementedError(
            "candidate generation is deferred to Phase9-3 "
            "(see docs/contracts/phase9_1_semantic_projection_v1.md section 6)"
        )
