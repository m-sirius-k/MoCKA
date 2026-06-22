from .adapters.github import GitHubAdapter


class MCPRouter:
    def route(self, source: str, request: dict):
        if source == "github":
            return GitHubAdapter().parse(request)

        return request
