"""
MoCKA 3.0 — Governance Layer 2 (GL2)
working_memory.py

責務:
  現在の作業状態を保持する管理層。
  Knowledge Baseでも、Conversation Historyでもない。

  初期化はGL1 (RepositoryGroundingEngine) のGrounding結果を入力とする。
  GL1を迂回してはならない。

更新原則:
  - 毎回答での再構築は禁止
  - Eventによって更新する
  - Repository状態変化によって更新する
  - 明示的な状態遷移によって更新する
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from grounding_engine import RepositoryGroundingEngine

REPO_ROOT      = Path(r"C:\Users\sirok\MoCKA")
MEMORY_PATH    = REPO_ROOT / "data" / "working_memory.json"

WORKING_MEMORY_FIELDS = [
    "current_repository",
    "current_project",
    "current_task",
    "current_target",
    "current_branch",
    "current_phase",
    "current_governance_layer",
    "current_thinking_mode",
    "current_constraints",
    "current_important_rules",
    "current_prohibited_rules",
    "current_encoding",
    "current_event",
    "current_todo",
    "current_goal",
]


class WorkingMemoryEngine:
    """
    load()  : data/working_memory.json から現在の作業状態を読み込む。
              存在しない場合のみ、GL1 Groundingを実行して初期化する。
    update(): Event発生時にのみ呼び出し、指定フィールドを更新する。
    snapshot(): 監査用に現在の状態をそのまま返す。
    """

    def __init__(self, path: Path = MEMORY_PATH):
        self.path = path
        self.engine = RepositoryGroundingEngine()

    def _empty(self) -> dict:
        return {field: None for field in WORKING_MEMORY_FIELDS}

    def _bootstrap(self) -> dict:
        """GL1のGrounding結果からWorking Memoryの初期値を構築する。"""
        result = self.engine.ground("working_memory_init")
        memory = self._empty()
        memory.update({
            "current_repository":       result.repository_root,
            "current_branch":           result.current_branch,
            "current_encoding":         result.policy["encoding"],
            "current_important_rules":  list(result.policy.values()),
            "current_prohibited_rules": [
                "create_new_folder_without_grounding",
                "infer_save_path",
                "infer_branch_name",
                "human_query_before_repository_check",
            ],
            "current_governance_layer": "GL2",
            "_updated_at": datetime.now(timezone.utc).isoformat(),
        })
        return memory

    def load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        memory = self._bootstrap()
        self._save(memory)
        return memory

    def _save(self, memory: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

    def update(self, event: str, changes: dict) -> dict:
        """
        Eventが発生した場合のみ呼ぶ。
        changesに含まれるフィールドのみ更新し、その他は保持する。
        """
        memory = self.load()
        for key, value in changes.items():
            if key not in WORKING_MEMORY_FIELDS:
                raise ValueError(f"unknown working memory field: {key}")
            memory[key] = value
        memory["current_event"] = event
        memory["_updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(memory)
        return memory

    def snapshot(self) -> dict:
        """監査用スナップショット。"""
        return self.load()


def main():
    wm = WorkingMemoryEngine()
    print(json.dumps(wm.snapshot(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
