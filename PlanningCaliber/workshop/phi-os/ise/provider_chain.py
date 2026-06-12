# provider_chain.py
from __future__ import annotations
from .schema import ProjectStatus, Warning, TodoItem
from .state_provider import StateProvider


class ProviderChain:
    """
    複数の StateProvider をチェーンで繋ぐ。
    PHI-OS 全体のプラグイン構造の基盤。

    get_project_status: 最初に値を返した Provider を採用
    get_active_warnings: 全 Provider の結果を結合
    get_active_todos: 全 Provider の結果を結合（重複IDは後勝ち）
    get_decision_revision: 最大値を採用
    get_guideline_revision: 最大値を採用

    将来の拡張例:
      ProviderChain([
          DefaultStateProvider(db, todo),
          BEEProvider(bee_path),
          TICProvider(tic_path),
      ])
    """

    def __init__(self, providers: list[StateProvider]):
        if not providers:
            raise ValueError("ProviderChain には最低1つの Provider が必要です")
        self._providers = providers

    def get_project_status(self) -> ProjectStatus:
        for p in self._providers:
            try:
                result = p.get_project_status()
                if result and result.mission != "Unknown":
                    return result
            except Exception:
                continue
        return ProjectStatus(phase=0, mission="unknown", priority=[])

    def get_active_warnings(self) -> list[Warning]:
        seen, result = set(), []
        for p in self._providers:
            try:
                for w in p.get_active_warnings():
                    if w.id not in seen:
                        seen.add(w.id)
                        result.append(w)
            except Exception:
                continue
        return result

    def get_active_todos(self) -> list[TodoItem]:
        seen, result = set(), []
        for p in self._providers:
            try:
                for t in p.get_active_todos():
                    if t.id not in seen:
                        seen.add(t.id)
                        result.append(t)
            except Exception:
                continue
        return result

    def get_decision_revision(self) -> int:
        values = []
        for p in self._providers:
            try:
                values.append(p.get_decision_revision())
            except Exception:
                continue
        return max(values, default=0)

    def get_guideline_revision(self) -> int:
        values = []
        for p in self._providers:
            try:
                values.append(p.get_guideline_revision())
            except Exception:
                continue
        return max(values, default=0)
