"""cross_repo/search.py — CrossRepoSearch: Repository横断検索"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOTS = {
    "MoCKA":       Path("C:/Users/sirok/MoCKA"),
    "mini-MoCKA":  Path("C:/Users/sirok/mini-mocka"),
    "vasAI":       Path("C:/Users/sirok/MoCKA/PlanningCaliber/workshop/vasAI_Project"),
    "SEO-OS":      Path("C:/Users/sirok/MoCKA/PlanningCaliber/workshop/seo-os"),
    "PHI-OS":      Path("C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os"),
}


@dataclass
class RepoSearchResult:
    repo: str
    file: str
    line: int
    content: str
    score: float

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "file": self.file,
            "line": self.line,
            "content": self.content.strip(),
            "score": self.score,
        }


class CrossRepoSearch:
    def __init__(self, repos: dict | None = None) -> None:
        self._repos = repos or _REPO_ROOTS

    def available_repos(self) -> list[str]:
        return [name for name, path in self._repos.items() if path.exists()]

    def search(self, query: str, file_pattern: str = "*.py",
               limit_per_repo: int = 5) -> list[RepoSearchResult]:
        results = []
        q_lower = query.lower()
        tokens = q_lower.split()
        for repo_name, root in self._repos.items():
            if not root.exists():
                continue
            for fpath in list(root.rglob(file_pattern))[:200]:
                if any(p in str(fpath) for p in ["__pycache__", ".venv", "archive", ".git"]):
                    continue
                try:
                    lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
                except Exception:
                    continue
                for lineno, line in enumerate(lines, 1):
                    ll = line.lower()
                    matches = sum(1 for t in tokens if t in ll)
                    if matches == 0:
                        continue
                    results.append(RepoSearchResult(
                        repo=repo_name,
                        file=str(fpath.relative_to(root)),
                        line=lineno,
                        content=line[:120],
                        score=matches / len(tokens),
                    ))
        results.sort(key=lambda x: -x.score)
        # リポジトリごとにlimit_per_repoまで
        seen_repos: dict[str, int] = {}
        filtered = []
        for r in results:
            cnt = seen_repos.get(r.repo, 0)
            if cnt < limit_per_repo:
                filtered.append(r)
                seen_repos[r.repo] = cnt + 1
        return filtered

    def search_commands(self, query: str) -> dict[str, list[dict]]:
        """各リポジトリのcommand_index DBを検索する"""
        result: dict[str, list[dict]] = {}
        q = query.lower()
        for repo_name, root in self._repos.items():
            db_path = root / "data" / "command_index.db"
            if not db_path.exists():
                continue
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT id, name, description, category FROM commands "
                    "WHERE name LIKE ? OR description LIKE ? LIMIT 10",
                    (f"%{q}%", f"%{q}%")
                ).fetchall()
                conn.close()
                result[repo_name] = [dict(r) for r in rows]
            except Exception:
                pass
        return result
