from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3, uuid, os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/jobs.db")

class BaseWorker(ABC):
    name:         str  = ""
    version:      str  = "1.0.0"
    capabilities: list = []
    priority:     int  = 5        # 低いほど優先
    tags:         list = ["prod"] # staging / prod

    def __init_subclass__(cls, **kwargs):
        """
        サブクラス定義時に自動でCapabilityRegistryに登録。
        plugins/にファイルをimportするだけで完結。
        """
        super().__init_subclass__(**kwargs)
        try:
            from caliber.capability_registry import CapabilityRegistry
            for cap in cls.capabilities:
                CapabilityRegistry.register(cap, cls)
        except ImportError:
            pass

    @abstractmethod
    def execute(self, job: dict) -> dict:
        """
        戻り値:
        {
            "success": bool,
            "result_url": str,
            "artifact_path": str,
            "error": str
        }
        """
        pass

    def health_check(self) -> bool:
        return True

    def rollback(self, job_id: str) -> bool:
        return False

    def _record_history(self, job_id, capability,
                        status, started_at,
                        artifact="", error="", retry=0):
        finished = datetime.now().isoformat()
        duration = int((datetime.fromisoformat(finished) -
                        datetime.fromisoformat(started_at))
                       .total_seconds() * 1000)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO worker_history
            (id,job_id,worker,capability,status,
             started_at,finished_at,duration_ms,
             artifact,error,retry_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (str(uuid.uuid4()), job_id, self.name,
              capability, status, started_at,
              finished, duration, artifact, error, retry))
        conn.commit()
        conn.close()
