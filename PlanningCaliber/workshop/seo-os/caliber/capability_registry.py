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
    def register(cls, capability: str, worker_cls) -> None:
        with cls._lock:
            if capability not in cls._registry:
                cls._registry[capability] = []
            names = [w.__name__ for w in cls._registry[capability]]
            if worker_cls.__name__ not in names:
                cls._registry[capability].append(worker_cls)
                info(f"[Registry] 登録: {capability} "
                     f"← {worker_cls.__name__}")

    @classmethod
    def get(cls, capability: str) -> list:
        return cls._registry.get(capability, [])

    @classmethod
    def all_capabilities(cls) -> dict:
        return {cap: [w.__name__ for w in workers]
                for cap, workers in cls._registry.items()}
