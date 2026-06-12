import json, os
from datetime import datetime
from caliber import bootstrap
from caliber.capability_registry import CapabilityRegistry
from caliber.performance_ledger import PerformanceLedger
from caliber.lifecycle_manager import LifecycleManager
from caliber.selection_strategy import select
from kernel.logger import info

PIPELINE_DIR = os.path.join(
    os.path.dirname(__file__), "../pipelines")

class SimulationEngine:
    """
    実際には実行せず、Pipeline全体をシミュレーションする。
    新Pipeline・新Workerの導入前検証に使用。
    Worker選択・Policy判定・Rollback判定まで模擬する。
    """

    def simulate(self, pipeline_name: str,
                 job: dict,
                 strategy: str = "priority") -> dict:
        bootstrap.initialize()
        steps    = self._load(pipeline_name)
        pl       = PerformanceLedger()
        lm       = LifecycleManager()
        results  = []
        warnings = []
        can_run  = True

        for i, step in enumerate(steps, 1):
            kind = step.get("type", "capability")

            if kind == "gate":
                results.append({
                    "step":   i,
                    "type":   "gate",
                    "status": "simulated",
                    "note":   "AI Gate: 実行時に品質検査"
                })
                continue

            if kind == "policy":
                results.append({
                    "step":   i,
                    "type":   "policy",
                    "status": "simulated",
                    "note":   f"Policy: {step.get('policy','')} 適用"
                })
                continue

            if kind == "capability":
                cap      = step.get("capability","")
                sel      = step.get("selection", strategy)
                required = step.get("required", True)
                candidates_cls = CapabilityRegistry.get(cap)

                if not candidates_cls:
                    status = "no_worker"
                    note   = f"⚠️ {cap}: Workerなし"
                    chosen = None
                    if required:
                        can_run = False
                        warnings.append(note)
                else:
                    workers = []
                    for cls in candidates_cls:
                        w     = cls()
                        state = lm.get_state(w.name)
                        sr    = pl.success_rate(w.name)
                        if state not in (
                                "offline","maintenance"):
                            workers.append(w)

                    chosen = select(workers, sel) \
                             if workers else None

                    if not chosen:
                        status = "no_eligible"
                        note   = f"⚠️ {cap}: 有効Workerなし"
                        if required:
                            can_run = False
                            warnings.append(note)
                    else:
                        sr = pl.success_rate(chosen.name)
                        status = "ok"
                        note = (
                            f"✅ {cap} → {chosen.name} "
                            f"(strategy={sel}, "
                            f"success={sr*100:.0f}%)")
                        if sr < 0.7:
                            warnings.append(
                                f"⚠️ {chosen.name} "
                                f"成功率{sr*100:.0f}%")

                results.append({
                    "step":     i,
                    "type":     "capability",
                    "capability": cap,
                    "strategy": sel,
                    "worker":   chosen.name
                             if chosen else None,
                    "status":   status,
                    "note":     note
                })

        return {
            "pipeline":  pipeline_name,
            "job_title": job.get("title",""),
            "strategy":  strategy,
            "can_run":   can_run,
            "steps":     results,
            "warnings":  warnings,
            "summary":   (
                f"✅ 実行可能 ({len(steps)}ステップ)"
                if can_run else
                f"❌ 実行不可 — {len(warnings)}件の問題あり")
        }

    def dry_run(self, pipeline_id: str,
                content_sample: str = "") -> dict:
        """
        POST /api/simulate (新形式): {pipeline_id, content_sample}
        Workerを実際には実行せず、どのWorkerが選ばれ
        どのPolicy checkが走るかをドライランする。
        戻り値: {would_run, would_block, estimated_score}
        """
        from gate.ai_gate import AIGate

        result = self.simulate(pipeline_id,
                                {"title": "dry_run",
                                 "content": content_sample,
                                 "type": "blog"},
                                "priority")

        would_run = [
            f"{s['capability']} -> {s['worker']}"
            for s in result["steps"]
            if s.get("type") == "capability" and s.get("status") == "ok"
        ] + [
            f"{s['type']}: {s.get('note', '')}"
            for s in result["steps"]
            if s.get("type") in ("gate", "policy")
        ]

        would_block = list(result["warnings"])

        estimated_score = 0
        if content_sample:
            gate_result = AIGate().check(
                {"content": content_sample, "type": "blog", "id": "dry_run"},
                "blog_policy")
            estimated_score = gate_result["score"]

        return {
            "pipeline_id": pipeline_id,
            "would_run": would_run,
            "would_block": would_block,
            "estimated_score": estimated_score,
        }

    def _load(self, name: str) -> list:
        path = os.path.join(PIPELINE_DIR, f"{name}.json")
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data.get("steps",[]),
                      key=lambda s: s.get("order",0))
