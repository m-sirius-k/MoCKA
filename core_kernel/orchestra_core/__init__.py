"""
MoCKA Core Kernel — orchestra_core

責務:
  MoCKA全体における意思決定圧縮層(Orchestra)。

  複数の提案ノード(ProposalNode)を評価空間(Decision Field)上で評価し、
  単一の意思決定パケット(DecisionPacket)へ圧縮する。

  Orchestraは「流れを生成する層」ではなく「流れを選別する層」であり、
  PHI-OS/Relay/Memory/PrismBridgeのいずれも直接制御しない。

  本フェーズ(Phase 12)は設計段階であり、execution_statusは常に
  "PROPOSED"で終了する。実行トリガー・状態変更命令・永続書き込み命令・
  外部モジュール制御・自動ワークフロー起動は一切行わない。
"""

from .models import (
    DECISION_FIELD_AXES,
    EXECUTION_STATUS_PROPOSED,
    ORCHESTRA_SCHEMA_VERSION,
    DecisionPacket,
    ProposalNode,
)
from .orchestra import Orchestra

__all__ = [
    "Orchestra",
    "ProposalNode",
    "DecisionPacket",
    "DECISION_FIELD_AXES",
    "EXECUTION_STATUS_PROPOSED",
    "ORCHESTRA_SCHEMA_VERSION",
]
