import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 — Governance Layer 1 (GL1)
grounding_engine.py

責務:
  Task受領後、Repository Policyの次に実行する。
  Repositoryに存在する情報は人間へ質問しない。

  Grounding Priority:
    Working Memory -> Repository Index -> Repository Structure
    -> Event Index -> State Reconstruction -> Git History -> Human
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from repository_policy import get_policy

REPO_ROOT      = Path(r"C:\Users\sirok\MoCKA")
REPO_INDEX     = REPO_ROOT / "structural" / "repository_index.json"
WORKING_MEMORY = REPO_ROOT / "data" / "working_memory.json"


@dataclass
class GroundingResult:
    repository_root: str
    current_branch: str
    git_status: list
    project_structure: list
    repository_index: dict | None
    working_memory: dict | None
    policy: dict = field(default_factory=get_policy)


class RepositoryGroundingEngine:
    """
    Grounding Priority:
    Working Memory -> Repository Index -> Repository Structure
    -> Event Index -> State Reconstruction -> Git History -> Human
    Humanは最後。これはMoCKA制度の基本原則。
    """

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    def get_repository_root(self) -> Path:
        return self.repo_root

    def get_current_branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD")

    def get_working_tree(self) -> list:
        status = self._git("status", "--porcelain")
        return [line for line in status.splitlines() if line]

    def get_project_structure(self) -> list:
        return sorted(p.name for p in self.repo_root.iterdir())

    def get_repository_index(self) -> dict | None:
        if REPO_INDEX.exists():
            with open(REPO_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_working_memory(self) -> dict | None:
        if WORKING_MEMORY.exists():
            with open(WORKING_MEMORY, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_existing_files(self, pattern: str) -> list:
        return [str(p.relative_to(self.repo_root)) for p in self.repo_root.glob(pattern)]

    def ground(self, task: str) -> GroundingResult:
        """
        Task受領後に必ず呼ぶ。
        Repositoryに存在する情報は絶対に人間へ質問しない。
        """
        return GroundingResult(
            repository_root=str(self.get_repository_root()),
            current_branch=self.get_current_branch(),
            git_status=self.get_working_tree(),
            project_structure=self.get_project_structure(),
            repository_index=self.get_repository_index(),
            working_memory=self.get_working_memory(),
        )


def main():
    engine = RepositoryGroundingEngine()
    result = engine.ground("bootstrap")
    print(json.dumps(
        {
            "repository_root": result.repository_root,
            "current_branch": result.current_branch,
            "git_status": result.git_status,
            "project_structure": result.project_structure,
            "policy": result.policy,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
