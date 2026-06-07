import importlib, glob, os
from kernel.logger import info, warn

PLUGIN_DIR   = os.path.join(os.path.dirname(__file__),
                             "../plugins")
WORKER_DIR   = os.path.join(os.path.dirname(__file__),
                             "../workers")
_initialized = False

def initialize() -> None:
    """
    SEO-OS起動時に一度だけ呼ぶ共通初期化。
    標準Worker + plugins/ を全ロードしてRegistryに登録。

    呼び出し元:
      - app.py (起動時)
      - PipelineEngine
      - ExplainEngine
      - SimulationEngine
      - CLI
    すべてここだけを呼べばよい。
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    # 標準Worker
    for name in ["sftp_worker","wordpress_worker"]:
        _import(f"workers.{name}")

    # plugins/ 配下を全ロード
    for path in glob.glob(
            os.path.join(PLUGIN_DIR,"*.py")):
        base = os.path.splitext(
                   os.path.basename(path))[0]
        if not base.startswith("_"):
            _import(f"plugins.{base}")

    info("[Bootstrap] Worker初期化完了")

def _import(module_name: str) -> None:
    try:
        importlib.import_module(module_name)
        info(f"[Bootstrap] ロード: {module_name}")
    except Exception as e:
        warn(f"[Bootstrap] ロード失敗: "
             f"{module_name} / {e}")
