"""
context_bridge/bridge.py — ContextBridge
Context Runtime v2 (MoCKA/phi_os/context/) との統合。
検索ランキングをContext(現在タスク・インシデント・フェーズ)で補正する。
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

# MoCKA ルートをパスに追加
_MOCKA_ROOT = Path(__file__).parents[4]
if str(_MOCKA_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOCKA_ROOT))


class ContextBridge:
    """
    Context Runtime v2 から Memory/Institution/Working/Execution を取得し、
    SEO Command Index の検索・推薦に注入する。

    Context Runtime が利用不可の場合はフォールバックで空コンテキストを返す。
    """

    def __init__(self) -> None:
        self._runtime = None
        self._available = False
        self._load_runtime()

    def _load_runtime(self) -> None:
        try:
            from phi_os.context import ContextRuntime
            self._runtime = ContextRuntime.boot()
            self._available = True
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def get_memory_runtime(self) -> dict:
        if not self._available or self._runtime is None:
            return self._fallback_context()
        try:
            return self._runtime.memory_runtime()
        except Exception:
            return self._fallback_context()

    def get_current_task(self) -> str:
        if not self._available or self._runtime is None:
            return ""
        try:
            return self._runtime.working.current_task
        except Exception:
            return ""

    def get_open_incidents(self) -> list:
        if not self._available or self._runtime is None:
            return []
        try:
            return self._runtime.institution.open_incidents
        except Exception:
            return []

    def get_phase(self) -> str:
        if not self._available or self._runtime is None:
            return ""
        try:
            return self._runtime.institution.current_phase
        except Exception:
            return ""

    def context_boost(self, command_id: str) -> float:
        """
        現在のContextに基づいてコマンドのスコアブースト値を返す (0.0〜0.3)。
        現在タスクとコマンドカテゴリが一致する場合にブーストする。
        """
        if not self._available:
            return 0.0
        task = self.get_current_task().lower()
        if not task:
            return 0.0
        boosts = {
            "seo":          ["seo", "keyword", "meta", "schema", "ogp"],
            "publish":      ["publish", "deploy", "release"],
            "context":      ["context", "memory", "resume", "snapshot"],
            "governance":   ["governance", "audit", "boundary"],
            "distribution": ["dist", "wordpress", "sftp", "social"],
            "caliber":      ["caliber", "health", "recommend"],
        }
        cat = command_id.split(".")[0] if "." in command_id else ""
        keywords = boosts.get(cat, [])
        if any(kw in task for kw in keywords):
            return 0.2
        return 0.0

    def snapshot(self) -> Optional[str]:
        if not self._available or self._runtime is None:
            return None
        try:
            data = self._runtime.full_context()
            return self._runtime._snapshot.save(data)
        except Exception:
            return None

    def _fallback_context(self) -> dict:
        return {
            "protocol": "Memory Runtime v2 (fallback)",
            "available": False,
            "memory": {"event_count": 0, "related_events": [],
                       "five_w1h": {}, "incident_history": []},
            "architecture": {"allowed_modules": [], "forbidden_modules": []},
            "project": {"project": "PlanningCaliber", "phase": "", "top_todos": []},
            "execution": {"validation_result": "PENDING"},
        }
