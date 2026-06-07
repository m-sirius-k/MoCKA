import importlib, os, glob
from caliber.capability_registry import CapabilityRegistry
from caliber.lifecycle_manager import LifecycleManager
from kernel.logger import info, warn, error

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
                       tag: str = "prod"):
    """
    Capabilityを満たす最適Workerを返す。
    選択基準（Phase4）:
      1. Capability一致
      2. tag_filter（staging/prod）
      3. health_check（稼働確認）
      4. priority（低いほど優先）
    """
    _load_plugins()

    # workers/ 配下の標準Workerも自動登録対象に含める
    try:
        importlib.import_module("workers.wordpress_worker")
        importlib.import_module("workers.sftp_worker")
    except Exception:
        pass

    lm = LifecycleManager()
    candidates = CapabilityRegistry.get(capability)

    if not candidates:
        warn(f"[Caliber] {capability} を満たすWorkerなし")
        return None

    scored = []
    for cls in candidates:
        worker = cls()

        if tag not in worker.tags:
            continue

        state = lm.get_state(worker.name)
        if state in ("offline", "maintenance"):
            warn(f"[Caliber] {worker.name} は {state} → スキップ")
            continue

        try:
            healthy = worker.health_check()
        except Exception:
            healthy = False

        if not healthy:
            lm.set_state(worker.name, "offline")
            warn(f"[Caliber] {worker.name} health_check失敗")
            continue

        scored.append((worker.priority, worker))

    if not scored:
        error(f"[Caliber] {capability} / tag={tag} "
              f"で有効なWorkerなし")
        return None

    scored.sort(key=lambda x: x[0])
    chosen = scored[0][1]
    lm.set_state(chosen.name, "busy")
    info(f"[Caliber] {capability} → {chosen.name} "
         f"(priority={chosen.priority})")
    return chosen

def release_worker(worker_name: str) -> None:
    LifecycleManager().set_state(worker_name, "ready")
    info(f"[Caliber] {worker_name} → ready")

def list_capabilities() -> dict:
    _load_plugins()
    try:
        importlib.import_module("workers.wordpress_worker")
        importlib.import_module("workers.sftp_worker")
    except Exception:
        pass
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
