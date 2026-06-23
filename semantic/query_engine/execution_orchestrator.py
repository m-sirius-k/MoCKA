# MoCKA/semantic/query_engine/execution_orchestrator.py
# Phase8-3 - Execution Orchestrator v0 (HAB spine, pass-through only)
#
# 契約: docs/contracts/phase8_hab_runtime_integration_v1.md (1.2節)
#
# 重要な定義: Execution Orchestratorは「意味を動かすエンジン」ではなく
# 「意味の流路」である。判断・裁定・解釈・最適化は一切行わない。
# 既存Phase7全クラスのメソッド署名は変更しない。
#
# ルーティング順序（契約1.2節・確定）:
#   1. MeaningCycleExecutor.run_cycle(...)   -> A/B/C/Dの1サイクル
#   2. OrderNormalizer.normalize(...)        -> B-4: 同一identifierのcollision検出
#   3. CollisionGovernor.govern(...)         -> B-5: 分類+エスカレーションのみ
#   4. 裁定(HumanGateEventLog.submit_ruling)は呼ばない。
#      裁定の実行自体は人間が行う(契約1.2節)。Orchestratorは
#      governed collisionsをそのまま下流(Observation Surface/人間)へ
#      渡すだけである。
#
# 絶対禁止（契約2章より、Phase7から継続）:
#   - merge禁止 / collision削除禁止 / 非破壊構造維持 / Human Gate単一裁定点
#   - Orchestrator自身による判断・裁定・最適化・出力の加工

from dataclasses import dataclass, field
from typing import Optional, Sequence

from semantic.query_engine.execution_layer import MeaningCycleExecutor, MeaningCycleResult
from semantic.query_engine.order_normalizer import OrderNormalizer
from semantic.query_engine.collision_governance import CollisionGovernor, GovernedCollisionRecord


@dataclass(frozen=True)
class OrchestrationResult:
    identifier: str
    cycle_result: MeaningCycleResult
    governed_collisions: Sequence[GovernedCollisionRecord] = field(default_factory=tuple)


class ExecutionOrchestrator:
    """既存3クラスを固定順でルーティングするだけの統合層(HABの脊椎)。

    判断・裁定・解釈・最適化は一切行わない。出力は加工せずそのまま
    次レイヤへ渡す(イベントパススルー)。
    """

    def __init__(
        self,
        meaning_executor: MeaningCycleExecutor,
        order_normalizer: OrderNormalizer,
        collision_governor: CollisionGovernor,
    ):
        self._meaning_executor = meaning_executor
        self._order_normalizer = order_normalizer
        self._collision_governor = collision_governor

    def process(
        self,
        identifier: str,
        intent_text_or_key: Optional[str] = None,
        detected_at: Optional[str] = None,
    ) -> OrchestrationResult:
        # Step 1: A/B/C/Dの1サイクルをそのまま通す(加工なし)。
        cycle_result = self._meaning_executor.run_cycle(
            identifier, intent_text_or_key=intent_text_or_key, detected_at=detected_at
        )

        # Step 2: 同一identifierのcollisionをそのまま通す(加工なし)。
        normalized = self._order_normalizer.normalize(identifier)

        # Step 3: 分類+エスカレーションのみ(解消・裁定はしない)。
        governed_collisions = self._collision_governor.govern(normalized["collisions"])

        # Step 4: 裁定は呼ばない。下流(人間/Observation Surface)へそのまま渡す。
        return OrchestrationResult(
            identifier=identifier,
            cycle_result=cycle_result,
            governed_collisions=governed_collisions,
        )
