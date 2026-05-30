"""
vasAI: BaseCALIBER — 企業が継承するインターフェース。
MoCKAを知らなくても、このインターフェースだけ理解すれば良い。
"""
from abc import ABC, abstractmethod
from typing import Optional

from core import artifact_schema, audit_chain, event_store, governance
from core.models import ApprovalRule, Artifact, MovementStage

# グローバルcaliber registry
_registry: dict[str, "BaseCALIBER"] = {}


def register(caliber: "BaseCALIBER") -> None:
    _registry[caliber.get_caliber_id()] = caliber


def get_registry() -> dict[str, "BaseCALIBER"]:
    return dict(_registry)


class BaseCALIBER(ABC):
    """
    企業はこれを継承してカスタムcaliberを作る。
    abstractmethod = 企業が実装する部分（必須）
    具体実装     = 企業が上書きしない部分（共通保証）
    """

    # ── 企業が実装する部分（上書き必須）──────────────────

    @abstractmethod
    def get_caliber_id(self) -> str:
        """例: 'medical_v1' / 'finance_v1'"""

    @abstractmethod
    def classify_event(self, raw_data: dict) -> str:
        """企業固有の分類ロジック → ArtifactType文字列を返す"""

    @abstractmethod
    def get_approval_rules(self) -> list[ApprovalRule]:
        """どのリスクレベルで誰が承認するかを定義"""

    @abstractmethod
    def format_for_intranet(self, artifact: Artifact) -> dict:
        """vasAI → 社内イントラネット向けフォーマット変換"""

    @abstractmethod
    def receive_from_intranet(self, data: dict) -> Artifact:
        """社内イントラネットからの受信 → Artifactに変換"""

    # ── 企業が上書きしない部分（共通保証）────────────────

    def send_to_vasai(self, artifact: Artifact) -> str:
        """
        → vasAI core へ送信（共通実装・上書き禁止）
        1. artifact を vasAI共通スキーマに変換
        2. event_store へ記録
        3. audit_chain に署名
        4. governance を通す
        戻り値: event_id
        """
        if not artifact.hash:
            artifact.hash = artifact_schema.compute_hash(artifact)

        event_id = event_store.append(
            who_actor=artifact.source_app,
            what_type="CALIBER_INBOUND",
            where_component=artifact.source_service,
            why_purpose=f"caliber={self.get_caliber_id()}",
            content=artifact_schema.to_event_content(artifact),
            caliber_id=self.get_caliber_id(),
            stage=MovementStage.OBSERVATION.value,
        )

        audit_chain.sign(event_id, artifact.hash, event_store.get_latest_hash())
        governance.process(event_id, event_store.get(event_id) or {})

        return event_id

    def receive_from_vasai(self, event_id: str) -> dict:
        """← vasAI core から結果受信（共通実装・上書き禁止）"""
        ev = event_store.get(event_id)
        if ev is None:
            raise KeyError(f"Event not found: {event_id}")
        return ev

    def process_intranet_request(self, raw_data: dict) -> dict:
        """
        intranet → vasAI → intranet の完全フロー。
        企業はこれを呼ぶだけで良い。
        """
        artifact_type = self.classify_event(raw_data)
        artifact = self.receive_from_intranet(raw_data)
        # 分類結果をオーバーライド（抽象メソッドの値を使う）
        artifact = artifact.model_copy(update={"artifact_type": artifact_type})
        artifact.hash = artifact_schema.compute_hash(artifact)

        event_id = self.send_to_vasai(artifact)
        result_event = self.receive_from_vasai(event_id)
        return self.format_for_intranet(artifact)
