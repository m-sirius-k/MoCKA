# MoCKA/semantic/query_engine/runtime_bridge.py
# Phase8-2 - Runtime Bridge v0 (Boundary Declaration Layer)
#
# 契約: docs/contracts/phase8_2_runtime_bridge_v1.md
#
# 重要な定義: これは「接続装置」ではなく「境界認識レイヤ」である。
# trace_id namespace(Phase7-A4)とcluster_id namespace(Phase7-B3/B4)は
# 別世界として正しく存在している。本ファイルはこの分割状態を固定する
# だけであり、namespace間の変換・統合・正規化・マッピングは一切行わない。
#
# 絶対禁止（契約4章より、恒久的）:
#   - trace_id <-> cluster_id の強制マッピング
#   - 自動補正 / 正規化 / 統一キー生成
#   - namespace間の変換関数の提供

import re
from dataclasses import dataclass
from typing import Optional

NAMESPACE_TRACE_ID = "trace_id"
NAMESPACE_CLUSTER_ID = "cluster_id"
NAMESPACE_EVENT_ID = "event_id"
NAMESPACE_UNKNOWN = "unknown"

DECLARED_NAMESPACES = (NAMESPACE_TRACE_ID, NAMESPACE_CLUSTER_ID, NAMESPACE_EVENT_ID)

_EVENT_ID_PATTERN = re.compile(r"^E\d{8}_\d+$")
_TRACE_ID_PATTERN = re.compile(r"^UV[0-9A-F]+$", re.IGNORECASE)
_CLUSTER_ID_PATTERN = re.compile(r"^[0-9a-f]{16}$")


class NamespaceRegistry:
    """trace_id/cluster_id/event_id namespaceの宣言のみを行う。

    namespace間の対応表・変換関数は提供しない(提供すること自体が
    絶対禁止に該当する)。
    """

    def declared_namespaces(self) -> tuple:
        return DECLARED_NAMESPACES

    def classify(self, identifier: str) -> str:
        """identifierがどのnamespaceに属するかを機械的パターンのみで
        判定する(意味解釈・補正・マッピングは行わない)。
        """
        if _EVENT_ID_PATTERN.match(identifier):
            return NAMESPACE_EVENT_ID
        if _TRACE_ID_PATTERN.match(identifier):
            return NAMESPACE_TRACE_ID
        if _CLUSTER_ID_PATTERN.match(identifier):
            return NAMESPACE_CLUSTER_ID
        return NAMESPACE_UNKNOWN


@dataclass(frozen=True)
class RawEvent:
    payload: dict
    namespace: str
    received_at: Optional[str] = None


class RawEventIngress:
    """外部イベントをrawのまま保持し、namespaceタグのみ付与する受信口。

    ペイロード自体の変更・補完・正規化は行わない。
    """

    def __init__(self, registry: Optional[NamespaceRegistry] = None):
        self._registry = registry or NamespaceRegistry()

    def receive(
        self,
        payload: dict,
        identifier_field: str = "identifier",
        received_at: Optional[str] = None,
    ) -> RawEvent:
        identifier = payload.get(identifier_field, "")
        namespace = self._registry.classify(identifier) if identifier else NAMESPACE_UNKNOWN
        return RawEvent(payload=payload, namespace=namespace, received_at=received_at)
