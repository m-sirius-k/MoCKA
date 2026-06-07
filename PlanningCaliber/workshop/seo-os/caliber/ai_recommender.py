from caliber.performance_ledger import PerformanceLedger
from caliber.lifecycle_manager import LifecycleManager
from kernel.logger import info

ledger = PerformanceLedger()

class AIRecommender:
    """
    蓄積した実績データからWorker推薦・警告を生成。
    Phase5後半: Claudeとの連携で自然言語推薦も可能。
    """

    FAILURE_THRESHOLD    = 3    # 連続失敗警告
    SUCCESS_RATE_WARN    = 0.7  # 成功率70%以下で警告
    SLOW_THRESHOLD_MS    = 5000 # 5秒超で「遅い」警告

    def analyze(self) -> dict:
        metrics = ledger.all_metrics()
        lm      = LifecycleManager()
        states  = {s["name"]: s["state"]
                   for s in lm.all_states()}

        warnings     = []
        suggestions  = []
        auto_actions = []

        for m in metrics:
            name = m["worker_name"]
            sr   = ledger.success_rate(name)
            cf   = m["consecutive_failures"]
            avg  = m["avg_duration_ms"]
            state = states.get(name, "ready")

            # 連続失敗警告
            if cf >= self.FAILURE_THRESHOLD:
                warnings.append({
                    "worker":  name,
                    "level":   "critical",
                    "message": f"連続{cf}回失敗中",
                    "action":  "要確認・offline推奨"
                })
                if state != "offline":
                    auto_actions.append({
                        "type":   "set_offline",
                        "worker": name,
                        "reason": f"連続失敗{cf}回"
                    })

            # 成功率低下警告
            elif sr < self.SUCCESS_RATE_WARN and \
                 (m["success_count"] +
                  m["failure_count"]) > 5:
                warnings.append({
                    "worker":  name,
                    "level":   "warning",
                    "message": f"成功率{sr*100:.0f}%",
                    "action":  "代替Worker検討"
                })

            # 低速Worker警告
            if avg > self.SLOW_THRESHOLD_MS:
                suggestions.append({
                    "worker":  name,
                    "message": f"平均{avg:.0f}ms — "
                               f"'fastest'戦略検討",
                    "suggestion": "selection: fastest"
                })

        return {
            "warnings":     warnings,
            "suggestions":  suggestions,
            "auto_actions": auto_actions,
            "summary": {
                "total_workers":   len(metrics),
                "healthy_workers": sum(
                    1 for m in metrics
                    if ledger.success_rate(
                        m["worker_name"]) >= 0.9),
                "degraded_workers": sum(
                    1 for m in metrics
                    if m["consecutive_failures"] >=
                    self.FAILURE_THRESHOLD)
            }
        }

    def apply_auto_actions(self) -> int:
        """auto_actionsを自動実行。実行件数を返す。"""
        result  = self.analyze()
        lm      = LifecycleManager()
        applied = 0
        for action in result["auto_actions"]:
            if action["type"] == "set_offline":
                lm.set_state(action["worker"], "offline")
                info(f"[AIRecommender] 自動offline: "
                     f"{action['worker']} / "
                     f"{action['reason']}")
                applied += 1
        return applied
