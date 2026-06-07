import json
from caliber.decision_ledger import DecisionLedger
from caliber.performance_ledger import PerformanceLedger
from caliber.lifecycle_manager import LifecycleManager
from caliber.capability_registry import CapabilityRegistry
from caliber import bootstrap

class ExplainEngine:
    """
    GET /api/caliber/explain/<capability>
    「なぜそのWorkerが選ばれるか」を人間が読める形で返す。
    監査・デバッグ・博士への説明に使用。
    """

    def explain(self, capability: str,
                strategy: str = "priority") -> dict:
        bootstrap.initialize()
        pl  = PerformanceLedger()
        lm  = LifecycleManager()
        dl  = DecisionLedger()

        # 現在の候補Worker
        candidates = []
        for cls in CapabilityRegistry.get(capability):
            w = cls()
            sr    = pl.success_rate(w.name)
            state = lm.get_state(w.name)
            m     = pl.get(w.name)
            candidates.append({
                "name":               w.name,
                "version":            w.version,
                "priority":           w.priority,
                "tags":               w.tags,
                "state":              state,
                "success_rate":       round(sr * 100, 1),
                "avg_duration_ms":    round(
                    m["avg_duration_ms"], 1),
                "consecutive_failures":
                    m["consecutive_failures"],
                "eligible":           state not in
                    ("offline","maintenance") and sr > 0
            })

        # 過去の選択履歴
        history = dl.get_by_capability(capability, 5)
        parsed_history = []
        for h in history:
            try:
                reason = json.loads(
                    h.get("selection_reason","{}"))
            except Exception:
                reason = {}
            parsed_history.append({
                "timestamp":       h["timestamp"],
                "selected_worker": h["selected_worker"],
                "strategy":        h["strategy"],
                "outcome":         h.get("outcome",""),
                "reason":          reason
            })

        # 推薦Worker（現在の戦略で選ばれるWorker）
        eligible = [c for c in candidates
                    if c["eligible"]]
        recommended = None
        if eligible:
            if strategy == "highest_success":
                recommended = max(eligible,
                    key=lambda c: c["success_rate"])
            elif strategy == "fastest":
                recommended = min(eligible,
                    key=lambda c: c["avg_duration_ms"]
                    or 9999)
            else:
                recommended = min(eligible,
                    key=lambda c: c["priority"])

        return {
            "capability":  capability,
            "strategy":    strategy,
            "candidates":  candidates,
            "recommended": recommended,
            "history":     parsed_history,
            "explanation": self._build_text(
                capability, strategy,
                recommended, candidates)
        }

    def _build_text(self, capability, strategy,
                    recommended, candidates) -> str:
        if not recommended:
            return f"⚠️ {capability} を実行できるWorkerがありません"
        lines = [
            f"Capability: {capability}",
            f"Strategy:   {strategy}",
            f"Selected:   {recommended['name']} "
            f"v{recommended['version']}",
            f"",
            f"選択理由:",
            f"  Priority:     {recommended['priority']}",
            f"  State:        {recommended['state']}",
            f"  Success Rate: {recommended['success_rate']}%",
            f"  Avg Duration: "
            f"{recommended['avg_duration_ms']}ms",
            f"",
            f"候補 ({len(candidates)}件):",
        ]
        for c in candidates:
            mark = "→" if c["name"] == \
                          recommended["name"] else " "
            lines.append(
                f"  {mark} {c['name']}: "
                f"priority={c['priority']} "
                f"success={c['success_rate']}% "
                f"state={c['state']}")
        return "\n".join(lines)
