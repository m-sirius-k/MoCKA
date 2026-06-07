from caliber.performance_ledger import PerformanceLedger
from kernel.logger import info

ledger = PerformanceLedger()

STRATEGIES = ["priority", "balanced",
              "fastest", "highest_success", "lowest_cost"]

def select(candidates: list, strategy: str = "priority") -> object:
    """
    candidates: [worker_instance, ...]
    各戦略でworker_instanceを1件返す。

    strategy:
      priority        → priorityが低いWorkerを優先（デフォルト）
      balanced        → priority + success_rate の複合
      fastest         → avg_duration_ms が短いWorker優先
      highest_success → success_rate が高いWorker優先
      lowest_cost     → priority最低（将来: コスト軸）
    """
    if not candidates:
        return None

    if strategy not in STRATEGIES:
        info(f"[Strategy] 未知の戦略 '{strategy}' → priority使用")
        strategy = "priority"

    info(f"[Strategy] 選択戦略: {strategy}")

    if strategy == "priority":
        return min(candidates, key=lambda w: w.priority)

    if strategy == "fastest":
        return min(candidates, key=lambda w:
                   ledger.get(w.name)["avg_duration_ms"]
                   or 9999)

    if strategy == "highest_success":
        return max(candidates, key=lambda w:
                   ledger.success_rate(w.name))

    if strategy == "balanced":
        # score = priority × 0.4 + (1 - success_rate) × 0.6
        def balanced_score(w):
            sr = ledger.success_rate(w.name)
            return w.priority * 0.4 + (1 - sr) * 0.6 * 10
        return min(candidates, key=balanced_score)

    if strategy == "lowest_cost":
        # Phase5: cost軸は未実装 → priorityにフォールバック
        return min(candidates, key=lambda w: w.priority)

    return candidates[0]
