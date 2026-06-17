"""recommendation/engine.py — RecommendationEngine: 統合推薦エンジン"""
from __future__ import annotations
from dataclasses import dataclass

from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry
from command_index.metadata import CommandMetadata
from .dependency import DependencyRecommendation
from .workflow import WorkflowRecommendation


@dataclass
class Recommendation:
    command: CommandMetadata
    reason: str
    score: float
    source: str  # "related" | "next" | "dependency" | "workflow"

    def to_dict(self) -> dict:
        return {
            "command": self.command.to_dict(),
            "reason": self.reason,
            "score": round(self.score, 3),
            "source": self.source,
        }


class RecommendationEngine:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)
        self._deps = DependencyRecommendation(self._db)
        self._workflow = WorkflowRecommendation(self._db)

    def related(self, command_id: str, limit: int = 5) -> list[Recommendation]:
        """同カテゴリの関連コマンドを返す"""
        cmd = self._registry.get(command_id)
        if not cmd:
            return []
        same_cat = self._registry.list_all(category=cmd.category)
        result = []
        for c in same_cat:
            if c.id == command_id:
                continue
            shared_tags = set(c.tags) & set(cmd.tags)
            score = len(shared_tags) / max(len(cmd.tags), 1)
            result.append(Recommendation(
                command=c,
                reason=f"同カテゴリ({cmd.category}) / 共通タグ: {', '.join(list(shared_tags)[:3])}",
                score=score,
                source="related",
            ))
        result.sort(key=lambda x: -x.score)
        return result[:limit]

    def next_recommended(self, command_id: str) -> list[Recommendation]:
        """このコマンドの後に実行すべきコマンドを返す"""
        result = []
        # 依存されているコマンド (このコマンドが前提になっているもの)
        dependents = self._deps.get_dependents(command_id)
        for cmd in dependents:
            result.append(Recommendation(
                command=cmd,
                reason=f"{command_id} の後に実行するコマンド",
                score=0.9,
                source="next",
            ))
        # ワークフロー内の次ステップ
        for wf in self._workflow.recommend_for_command(command_id):
            if wf["next_step"]:
                cmd = self._registry.get(wf["next_step"])
                if cmd:
                    result.append(Recommendation(
                        command=cmd,
                        reason=f"ワークフロー「{wf['label']}」の次ステップ",
                        score=0.85,
                        source="workflow",
                    ))
        return result

    def dependency_recommend(self, command_id: str) -> list[Recommendation]:
        """実行前に必要な依存コマンドを返す"""
        deps = self._deps.get_dependencies(command_id)
        return [
            Recommendation(
                command=dep,
                reason=f"{command_id} の実行前に必要",
                score=1.0,
                source="dependency",
            )
            for dep in deps
        ]

    def full(self, command_id: str, limit: int = 8) -> list[Recommendation]:
        """関連・次・依存を統合した推薦リスト"""
        seen: set[str] = {command_id}
        result = []
        for rec in (
            self.dependency_recommend(command_id)
            + self.next_recommended(command_id)
            + self.related(command_id)
        ):
            if rec.command.id not in seen:
                seen.add(rec.command.id)
                result.append(rec)
        result.sort(key=lambda x: -x.score)
        return result[:limit]
