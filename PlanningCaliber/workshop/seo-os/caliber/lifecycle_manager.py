import sqlite3, os
from datetime import datetime, timedelta
from kernel.logger import info, warn

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")

STATES = ["ready", "busy", "offline", "maintenance"]
BUSY_TIMEOUT_MINUTES = 10

class LifecycleManager:
    """
    Worker状態管理。
    状態遷移:
      ready → busy（実行開始）
      busy  → ready（実行完了）
      busy  → offline（タイムアウト）
      *     → offline（health_check失敗）
      *     → maintenance（手動）
      maintenance → ready（手動復帰）
    """

    def get_state(self, worker_name: str) -> str:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("""
            SELECT state, updated_at FROM worker_registry
            WHERE name=?
        """, (worker_name,)).fetchone()
        conn.close()

        if not row:
            return "ready"

        state, updated_at = row

        if state == "busy" and updated_at:
            try:
                elapsed = (datetime.now() -
                           datetime.fromisoformat(updated_at))
                if elapsed > timedelta(
                        minutes=BUSY_TIMEOUT_MINUTES):
                    warn(f"[Lifecycle] {worker_name} "
                         f"busyタイムアウト → offline")
                    self.set_state(worker_name, "offline")
                    return "offline"
            except Exception:
                pass
        return state

    def set_state(self, worker_name: str,
                  state: str) -> None:
        if state not in STATES:
            warn(f"[Lifecycle] 不正な状態: {state}")
            return
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO worker_registry
                (name, state, updated_at)
            VALUES (?,?,?)
            ON CONFLICT(name) DO UPDATE
            SET state=excluded.state,
                updated_at=excluded.updated_at
        """, (worker_name, state, now))
        conn.commit()
        conn.close()
        info(f"[Lifecycle] {worker_name} → {state}")

    def all_states(self) -> list:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM worker_registry").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def recover(self, worker_name: str) -> None:
        self.set_state(worker_name, "ready")
        info(f"[Lifecycle] {worker_name} 手動復帰 → ready")
