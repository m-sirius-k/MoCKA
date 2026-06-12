# provider_chain.py
from __future__ import annotations
from .schema import ProjectStatus, Warning, TodoItem
from .state_provider import StateProvider


class ProviderChain:
    """
    複数のProviderをチェーンで繋ぎ、
    StateBuilderへの入力を組み立てる。
    各Providerは独立して追加・削除・差し替え可能。
    """
    def __init__(self, providers: list[StateProvider]):
        self._providers = providers

    def get_project_status(self) -> ProjectStatus:
        for p in self._providers:
            result = p.get_project_status()
            if result:
                return result
        return ProjectStatus(phase=0, mission="unknown", priority=[])

    def get_active_warnings(self) -> list[Warning]:
        warnings = []
        for p in self._providers:
            warnings.extend(p.get_active_warnings())
        return warnings

    def get_active_todos(self) -> list[TodoItem]:
        todos = []
        for p in self._providers:
            todos.extend(p.get_active_todos())
        return todos

    def get_decision_revision(self) -> int:
        return max((p.get_decision_revision() for p in self._providers), default=0)

    def get_guideline_revision(self) -> int:
        return max((p.get_guideline_revision() for p in self._providers), default=0)
