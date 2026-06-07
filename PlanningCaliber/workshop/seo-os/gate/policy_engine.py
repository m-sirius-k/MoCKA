import json, os
from kernel.logger import info, warn

POLICY_PATH = os.path.join(
    os.path.dirname(__file__), "../config/policies.json")

class PolicyEngine:
    """
    Policyを満たさないと公開不可。
    approve / reject / human_gate / auto_deploy を返す。
    """

    def load(self) -> dict:
        with open(POLICY_PATH, encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self, job: dict, gate_result: dict) -> dict:
        policies = self.load()
        policy_name = job.get("policy", "") or \
                      self._infer_policy(job.get("type",""))
        policy = policies.get(policy_name, {})

        score = gate_result.get("score", 0)
        passed = gate_result.get("passed", False)
        ai_draft = job.get("ai_draft", 0)

        min_score = policy.get("seo_score_min", 0)
        auto_ok   = policy.get("auto_approve", False)

        if not passed or score < min_score:
            verdict = "reject"
            reason  = f"品質不足: score={score} / 必要={min_score}"
        elif ai_draft and auto_ok:
            verdict = "auto_deploy"
            reason  = "AI生成・Policy合格・自動公開"
        else:
            verdict = "human_gate"
            reason  = "博士承認待ち"

        info(f"[Policy] {job['id']} → {verdict} / {reason}")
        return {
            "verdict":     verdict,
            "reason":      reason,
            "policy_name": policy_name,
            "score":       score
        }

    def _infer_policy(self, job_type: str) -> str:
        return {
            "lp":        "lp_policy",
            "blog":      "blog_policy",
            "bot":       "bot_policy",
            "important": "blog_policy"
        }.get(job_type, "blog_policy")
