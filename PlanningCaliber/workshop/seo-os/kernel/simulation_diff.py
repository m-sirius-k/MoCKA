import json, os
from kernel.simulation_engine import SimulationEngine
from kernel.logger import info

PIPELINE_DIR = os.path.join(os.path.dirname(__file__),
                             "../pipelines")

class SimulationDiff:
    """
    Pipeline変更前後のSimulation結果を比較する。
    新Pipeline導入・Step変更・Capability変更のレビューに使用。
    """

    def diff(self, pipeline_a: str, pipeline_b: str,
             job: dict = None,
             strategy: str = "priority") -> dict:
        if job is None:
            job = {"title": "simulation_diff",
                   "type": "lp", "content": ""}
        sim = SimulationEngine()
        result_a = sim.simulate(pipeline_a, job, strategy)
        result_b = sim.simulate(pipeline_b, job, strategy)

        added   = self._added(result_a, result_b)
        removed = self._removed(result_a, result_b)
        changed = self._changed(result_a, result_b)

        return {
            "pipeline_a":    pipeline_a,
            "pipeline_b":    pipeline_b,
            "strategy":      strategy,
            "result_a":      result_a,
            "result_b":      result_b,
            "diff": {
                "added":     added,
                "removed":   removed,
                "changed":   changed,
                "unchanged": (len(result_a["steps"]) -
                              len(added) -
                              len(removed) -
                              len(changed)),
                "summary": self._summary(
                    pipeline_a, pipeline_b,
                    added, removed, changed,
                    result_a, result_b)
            },
            "summary": self._summary(
                pipeline_a, pipeline_b,
                added, removed, changed,
                result_a, result_b)
        }

    def _steps_map(self, result: dict) -> dict:
        return {s["step"]: s
                for s in result.get("steps",[])}

    def _added(self, a, b) -> list:
        ma = self._steps_map(a)
        mb = self._steps_map(b)
        return [s for n,s in mb.items() if n not in ma]

    def _removed(self, a, b) -> list:
        ma = self._steps_map(a)
        mb = self._steps_map(b)
        return [s for n,s in ma.items() if n not in mb]

    def _changed(self, a, b) -> list:
        ma = self._steps_map(a)
        mb = self._steps_map(b)
        changed = []
        for n in set(ma) & set(mb):
            sa, sb = ma[n], mb[n]
            if (sa.get("capability") != sb.get("capability") or
                sa.get("worker")     != sb.get("worker") or
                sa.get("status")     != sb.get("status")):
                changed.append({
                    "step":   n,
                    "before": sa,
                    "after":  sb
                })
        return changed

    def _summary(self, a, b, added,
                 removed, changed, ra, rb) -> str:
        lines = [
            f"=== Simulation Diff ===",
            f"Before: {a} "
            f"({'✅' if ra['can_run'] else '❌'})",
            f"After:  {b} "
            f"({'✅' if rb['can_run'] else '❌'})",
            f"",
            f"追加Step:   {len(added)}件",
            f"削除Step:   {len(removed)}件",
            f"変更Step:   {len(changed)}件",
        ]
        for c in changed:
            lines.append(
                f"  Step{c['step']}: "
                f"{c['before'].get('capability','')} → "
                f"{c['after'].get('capability','')}")
        return "\n".join(lines)
