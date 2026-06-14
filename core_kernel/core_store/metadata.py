"""
MoCKA Core Kernel — core_store.metadata

責務:
  モジュール/サービスに関する共通メタ情報を表すデータ構造を定義する。
  ロジックは持たない(単純なデータ保持のみ)。
"""

import uuid as _uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModuleMetadata:
    """登録対象(モジュール/サービス/イベント種別)の共通メタ情報。

    module_id: 人間可読な名前(レジストリのキーとして使われる, 例: "orchestra")
    module_uuid: 不変の識別子。rename後も追跡できるよう、未指定時は自動発行する。
    version: セマンティックバージョン文字列
    """

    module_id: str
    version: str = "0.0.0"
    capability: tuple = field(default_factory=tuple)
    dependency: tuple = field(default_factory=tuple)
    extra: dict = field(default_factory=dict)
    module_uuid: str = field(default_factory=lambda: str(_uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "module_uuid": self.module_uuid,
            "version": self.version,
            "capability": list(self.capability),
            "dependency": list(self.dependency),
            "extra": dict(self.extra),
        }

    @staticmethod
    def from_dict(data: dict) -> "ModuleMetadata":
        kwargs = dict(
            module_id=data["module_id"],
            version=data.get("version", "0.0.0"),
            capability=tuple(data.get("capability", ())),
            dependency=tuple(data.get("dependency", ())),
            extra=data.get("extra", {}),
        )
        if "module_uuid" in data:
            kwargs["module_uuid"] = data["module_uuid"]
        return ModuleMetadata(**kwargs)
