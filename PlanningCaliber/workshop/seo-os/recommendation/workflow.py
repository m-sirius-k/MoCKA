"""recommendation/workflow.py — WorkflowRecommendation: 典型ワークフロー推薦"""
from __future__ import annotations
from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry

_WORKFLOWS = {
    "seo_publish": {
        "label": "SEO → Publish",
        "description": "SEO最適化してWordPressへ公開する標準フロー",
        "steps": [
            "seo.analyze", "seo.metadata", "seo.ogp", "seo.schema",
            "publish.job.create", "publish.job.approve", "publish.job.run",
            "dist.wordpress",
        ],
    },
    "seo_social": {
        "label": "SEO → Social",
        "description": "SEO最適化してSNSへ同時配信する",
        "steps": [
            "seo.analyze", "seo.ogp",
            "publish.job.create", "publish.job.approve", "publish.job.run",
            "dist.x", "dist.instagram",
        ],
    },
    "governance_cycle": {
        "label": "Governance Cycle",
        "description": "スナップショット → 監査 → コミット の統治サイクル",
        "steps": [
            "gov.snapshot", "gov.audit", "gov.boundary",
        ],
    },
    "context_resume": {
        "label": "Context Resume",
        "description": "前回状態を復元して作業を再開する",
        "steps": [
            "ctx.memory", "ctx.resume", "ctx.working",
        ],
    },
    "health_check": {
        "label": "Health Check",
        "description": "Caliberワーカー健全性確認フロー",
        "steps": [
            "caliber.health", "caliber.lifecycle", "caliber.recommend",
        ],
    },
}


class WorkflowRecommendation:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)

    def list_workflows(self) -> list[dict]:
        result = []
        for wid, w in _WORKFLOWS.items():
            result.append({
                "id": wid,
                "label": w["label"],
                "description": w["description"],
                "step_count": len(w["steps"]),
                "steps": w["steps"],
            })
        return result

    def get_workflow(self, workflow_id: str) -> dict | None:
        w = _WORKFLOWS.get(workflow_id)
        if not w:
            return None
        steps_meta = []
        for step_id in w["steps"]:
            cmd = self._registry.get(step_id)
            steps_meta.append({
                "id": step_id,
                "name": cmd.name if cmd else step_id,
                "description": cmd.description if cmd else "",
            })
        return {
            "id": workflow_id,
            "label": w["label"],
            "description": w["description"],
            "steps": steps_meta,
        }

    def recommend_for_command(self, command_id: str) -> list[dict]:
        """コマンドが属するワークフローを返す"""
        result = []
        for wid, w in _WORKFLOWS.items():
            if command_id in w["steps"]:
                idx = w["steps"].index(command_id)
                next_step = w["steps"][idx + 1] if idx + 1 < len(w["steps"]) else None
                result.append({
                    "workflow_id": wid,
                    "label": w["label"],
                    "current_step": idx,
                    "next_step": next_step,
                })
        return result
