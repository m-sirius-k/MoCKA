# phi_os/runtime/meaning_registry.py
# Institution Runtime — Meaning辞書
# 参照: PHI_OS_CONSTITUTION_v1.md 原則6 / MEANING_AUTHORITY_v1.md
from datetime import datetime, timezone
from typing import Optional

from .runtime_types import Meaning, MeaningClass
from .runtime_errors import MeaningNotFoundError


class MeaningRegistry:
    """
    Meaningの登録・取得・検証・変更履歴管理。
    Constitution原則6: Meaningが制度上の意味を決定する。
    """

    def __init__(self) -> None:
        self._store: dict[str, Meaning] = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        """Constitution / MEANING_AUTHORITY_v1.md 定義のMeaningを初期登録する"""
        defaults = [
            ("SYSTEM_CORE",  MeaningClass.SYSTEM_CORE,  "制度核システム実装"),
            ("GOVERNANCE",   MeaningClass.GOVERNANCE,   "ガバナンス・制度文書"),
            ("KNOWLEDGE",    MeaningClass.KNOWLEDGE,    "知識資産"),
            ("DESIGN",       MeaningClass.DESIGN,       "設計文書・スキーマ"),
            ("PHASE_RECORD", MeaningClass.PHASE_RECORD, "フェーズ記録"),
            ("REQUIREMENT",  MeaningClass.REQUIREMENT,  "要件定義"),
            ("TOOL",         MeaningClass.TOOL,         "運用ツール"),
            ("INCIDENT",     MeaningClass.INCIDENT,     "インシデント記録"),
            ("UNCLASSIFIED", MeaningClass.UNCLASSIFIED, "未分類（制度登録不可）"),
        ]
        for mid, cls, desc in defaults:
            m = Meaning(
                meaning_id=mid,
                name=mid,
                meaning_class=cls,
                description=desc,
                version="1.0",
                history=[],
            )
            self._store[mid] = m

    # ── 登録 ─────────────────────────────────────────────────────────────────

    def register(self, meaning: Meaning) -> None:
        """Meaningを登録する。既存の場合は変更履歴を残して上書き。"""
        if meaning.meaning_id in self._store:
            prev = self._store[meaning.meaning_id]
            meaning.history = prev.history + [{
                "changed_at": _now(),
                "from_version": prev.version,
                "from_class": prev.meaning_class,
                "reason": "register override",
            }]
        self._store[meaning.meaning_id] = meaning

    # ── 取得 ─────────────────────────────────────────────────────────────────

    def get(self, meaning_id: str) -> Meaning:
        if meaning_id not in self._store:
            raise MeaningNotFoundError(meaning_id)
        return self._store[meaning_id]

    def exists(self, meaning_id: str) -> bool:
        return meaning_id in self._store

    def all_meanings(self) -> list[Meaning]:
        return list(self._store.values())

    # ── 検証 ─────────────────────────────────────────────────────────────────

    def validate(self, meaning_id: str) -> tuple[bool, list[str]]:
        """Meaningが制度登録可能かを検証する。"""
        issues: list[str] = []
        if not self.exists(meaning_id):
            issues.append(f"Meaning '{meaning_id}' 未登録")
            return False, issues
        m = self._store[meaning_id]
        if m.meaning_class == MeaningClass.UNCLASSIFIED:
            issues.append("UNCLASSIFIED MeaningはGate通過不可 (Constitution 原則6)")
        return len(issues) == 0, issues

    # ── 変更履歴 ─────────────────────────────────────────────────────────────

    def change_history(self, meaning_id: str) -> list[dict]:
        return self.get(meaning_id).history

    def update_class(self, meaning_id: str, new_class: MeaningClass, reason: str) -> None:
        """Meaningクラスを変更し履歴に記録する。"""
        m = self.get(meaning_id)
        m.history.append({
            "changed_at": _now(),
            "from_version": m.version,
            "from_class": m.meaning_class,
            "to_class": new_class,
            "reason": reason,
        })
        m.meaning_class = new_class


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
