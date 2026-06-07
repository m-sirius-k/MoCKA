import re
from kernel.logger import info, warn

class AIGate:
    """
    品質保証層。
    NGなら差し戻し。人間には届かない。
    """

    def check(self, job: dict, policy_name: str) -> dict:
        content = job.get("content", "")
        job_type = job.get("type", "")
        results = {}

        if job_type in ("lp", "blog"):
            results["html_valid"]   = self._check_html(content)
            results["has_ogp"]      = self._check_ogp(content)
            results["responsive"]   = self._check_viewport(content)
            results["min_length"]   = self._check_length(
                                        content, job_type)

        if job_type == "bot":
            results["char_limit"]   = self._check_char_limit(content)

        passed = all(v for v in results.values())
        score  = int(sum(results.values()) /
                     max(len(results), 1) * 100)

        info(f"[AIGate] {job['id']} score={score} passed={passed}")
        return {
            "passed":  passed,
            "score":   score,
            "details": results
        }

    def _check_html(self, content: str) -> bool:
        return bool(content.strip()) and "<" in content

    def _check_ogp(self, content: str) -> bool:
        return 'og:title' in content or 'og:description' in content

    def _check_viewport(self, content: str) -> bool:
        return 'viewport' in content

    def _check_length(self, content: str, job_type: str) -> bool:
        min_len = {"lp": 500, "blog": 800}.get(job_type, 100)
        return len(content) >= min_len

    def _check_char_limit(self, content: str) -> bool:
        return len(content) <= 140
