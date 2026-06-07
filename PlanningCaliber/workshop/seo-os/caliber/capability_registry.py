import threading
from kernel.logger import info, warn

class CapabilityRegistry:
    """
    Workerクラスを自動登録するシングルトン。
    BaseWorkerのサブクラス定義時に自動で登録される。
    plugins/にファイルを置くだけで完結する設計の核心。
    """
    _registry: dict = {}
    _lock = threading.Lock()

    @classmethod
    def register(cls, capability: str,
                 worker_cls,
                 version: str = None) -> None:
        """
        version指定時は "capability:version" でも登録。
        例: register("publish_blog", WordPressV2Worker, "v2")
        → "publish_blog" と "publish_blog:v2" の両方に登録
        """
        with cls._lock:
            for key in ([capability] +
                        ([f"{capability}:{version}"]
                         if version else [])):
                if key not in cls._registry:
                    cls._registry[key] = []
                names = [w.__name__
                         for w in cls._registry[key]]
                if worker_cls.__name__ not in names:
                    cls._registry[key].append(worker_cls)
                    info(f"[Registry] 登録: {key} "
                         f"← {worker_cls.__name__}")

    @classmethod
    def get(cls, capability: str) -> list:
        return cls._registry.get(capability, [])

    @classmethod
    def all_capabilities(cls) -> dict:
        return {cap: [w.__name__ for w in workers]
                for cap, workers in cls._registry.items()}
