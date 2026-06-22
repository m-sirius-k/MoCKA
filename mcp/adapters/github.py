from .base import BaseAdapter


class GitHubAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "repo": request.get("repository"),
            "action": request.get("action"),
            "ref": request.get("ref")
        }
