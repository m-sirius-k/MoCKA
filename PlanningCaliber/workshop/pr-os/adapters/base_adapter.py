"""
PR-OS Output Adapter — 基底クラス
全Adapterはこのクラスを継承して実装する
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class PublishResult:
    success: bool
    adapter_id: str
    ks_id: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    scheduled_at: Optional[str] = None
    error: Optional[str] = None
    published_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class HealthResult:
    adapter_id: str
    adapter_name: str
    status: str          # "ok" | "disabled" | "unreachable" | "error"
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    http_status: Optional[int] = None
    error: Optional[str] = None
    last_post_at: Optional[str] = None
    rate_limit_remaining: Optional[int] = None

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class OutputAdapter(ABC):
    """PR-OS Output Adapter 基底クラス"""

    adapter_id: str = ""
    adapter_name: str = ""

    @abstractmethod
    def convert(self, ks_record: dict, confirmed_text: str) -> dict:
        """原本を媒体別フォーマットに変換"""

    @abstractmethod
    def publish(self, converted: dict) -> PublishResult:
        """変換済みコンテンツを投稿"""

    @abstractmethod
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        """予約投稿登録 (publish_at: ISO 8601)"""

    @abstractmethod
    def health_check(self) -> HealthResult:
        """接続・状態確認"""

    def get_analytics(self) -> dict:
        """投稿後パフォーマンス取得（Phase 3で各自実装）"""
        return {"adapter": self.adapter_id, "analytics": "Phase 3 pending"}

    def _disabled_result(self, ks_id: str = "") -> PublishResult:
        return PublishResult(
            success=False,
            adapter_id=self.adapter_id,
            ks_id=ks_id,
            error=f"{self.adapter_name}: Adapter disabled (set enabled=true in config.json)"
        )

    def _disabled_health(self) -> HealthResult:
        return HealthResult(
            adapter_id=self.adapter_id,
            adapter_name=self.adapter_name,
            status="disabled"
        )
