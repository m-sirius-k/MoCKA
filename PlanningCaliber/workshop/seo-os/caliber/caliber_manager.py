import importlib, os, glob
from caliber.capability_registry import CapabilityRegistry
from caliber.lifecycle_manager import LifecycleManager
from caliber.selection_strategy import select
from caliber.performance_ledger import PerformanceLedger
from caliber.decision_ledger import DecisionLedger
from caliber.decision_policy import DecisionPolicyEngine
from caliber import bootstrap
from kernel.logger import info, warn, error

ledger = PerformanceLedger()

PLUGIN_DIR = os.path.join(os.path.dirname(__file__),
                           "../plugins")

def _load_plugins() -> None:
    """plugins/ 配下の全.pyをimportして自動登録させる"""
    for path in glob.glob(os.path.join(PLUGIN_DIR, "*.py")):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.startswith("_"):
            continue
        module_name = f"plugins.{name}"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            warn(f"[Caliber] plugin読み込み失敗: {name} / {e}")

def request_capability(capability: str,
                       tag: str = "prod",
                       strategy: str = "priority",
                       job_id: str = ""):
    """
    Capabilityを満たす最適Workerを返す。
    選択基準（Phase5）:
      1. Capability一致（バージョン指定可: "publish_blog:v2"）
      2. tag_filter（staging/prod）
      3. health_check（稼働確認）/ 連続失敗チェック
      4. selection strategy（priority / balanced / fastest /
                             highest_success / lowest_cost）
    """
    bootstrap.initialize()

    lm = LifecycleManager()

    # Capability Versioning対応: "publish_blog:v2" → base="publish_blog", version="v2"
    base_cap = capability.split(":")[0]
    version  = capability.split(":")[1] if ":" in capability else None
    raw = CapabilityRegistry.get(capability)
    if not raw and version:
        raw = CapabilityRegistry.get(base_cap)

    if not raw:
        warn(f"[Caliber] {capability} を満たすWorkerなし")
        return None

    candidates = []
    for cls in raw:
        worker = cls()

        # バージョンフィルタ
        if version and hasattr(worker, "version"):
            if not worker.version.startswith(version):
                continue

        if tag not in worker.tags:
            continue

        state = lm.get_state(worker.name)
        if state in ("offline", "maintenance"):
            warn(f"[Caliber] {worker.name} は {state} → スキップ")
            continue

        if ledger.is_degraded(worker.name):
            warn(f"[Caliber] {worker.name} 連続失敗 → スキップ/offline")
            lm.set_state(worker.name, "offline")
            continue

        try:
            healthy = worker.health_check()
        except Exception:
            healthy = False

        if not healthy:
            lm.set_state(worker.name, "offline")
            warn(f"[Caliber] {worker.name} health_check失敗")
            continue

        candidates.append(worker)

    candidates = DecisionPolicyEngine().apply(
        candidates, capability, ledger)

    if not candidates:
        error(f"[Caliber] {capability} / tag={tag} "
              f"で有効なWorkerなし")
        return None

    chosen = select(candidates, strategy)
    lm.set_state(chosen.name, "busy")

    # 選択理由を構造化して記録（Decision Ledger）
    try:
        reason = {
            "strategy":   strategy,
            "tag":        tag,
            "candidates": [
                {
                    "name":         c.name,
                    "priority":     c.priority,
                    "success_rate": round(
                        ledger.success_rate(c.name), 3),
                    "avg_ms":       round(
                        ledger.get(c.name)["avg_duration_ms"], 1),
                    "state":        lm.get_state(c.name)
                }
                for c in candidates
            ],
            "selected_score": {
                "priority":     chosen.priority,
                "success_rate": round(
                    ledger.success_rate(chosen.name), 3),
                "avg_ms":       round(
                    ledger.get(chosen.name)["avg_duration_ms"], 1)
            }
        }
        DecisionLedger().record(
            capability, strategy, chosen,
            candidates, reason, job_id)
    except Exception:
        pass

    info(f"[Caliber] {capability} → {chosen.name} "
         f"(strategy={strategy})")
    return chosen

def release_worker(worker_name: str) -> None:
    LifecycleManager().set_state(worker_name, "ready")
    info(f"[Caliber] {worker_name} → ready")

def list_capabilities() -> dict:
    bootstrap.initialize()
    return CapabilityRegistry.all_capabilities()

def get_worker_stats(conn) -> list:
    rows = conn.execute("""
        SELECT worker,
               COUNT(*) as total,
               SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) as success,
               AVG(duration_ms) as avg_ms
        FROM worker_history
        GROUP BY worker
    """).fetchall()
    return [dict(r) for r in rows]
