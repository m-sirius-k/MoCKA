import sqlite3, os
from datetime import datetime
from kernel.logger import info, warn

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")

class PerformanceLedger:
    """
    Worker実績を記録・参照する台帳。
    Caliber ManagerがPriority以外の軸で選択できる基盤。
    """

    def record_success(self, worker_name: str,
                       duration_ms: int) -> None:
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO worker_metrics
                (worker_name, success_count, failure_count,
                 avg_duration_ms, last_success,
                 consecutive_failures, updated_at)
            VALUES (?,1,0,?,?,0,?)
            ON CONFLICT(worker_name) DO UPDATE SET
                success_count        = success_count + 1,
                avg_duration_ms      = (
                    avg_duration_ms *
                    (success_count + failure_count) + ?
                ) / (success_count + failure_count + 1),
                last_success         = ?,
                consecutive_failures = 0,
                updated_at           = ?
        """, (worker_name, duration_ms, now, now,
              duration_ms, now, now))
        conn.commit()
        conn.close()
        info(f"[Ledger] success: {worker_name} "
             f"({duration_ms}ms)")

    def record_failure(self, worker_name: str) -> None:
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO worker_metrics
                (worker_name, success_count, failure_count,
                 last_failure, consecutive_failures,
                 updated_at)
            VALUES (?,0,1,?,1,?)
            ON CONFLICT(worker_name) DO UPDATE SET
                failure_count        = failure_count + 1,
                last_failure         = ?,
                consecutive_failures = consecutive_failures + 1,
                updated_at           = ?
        """, (worker_name, now, now, now, now))
        conn.commit()
        conn.close()
        warn(f"[Ledger] failure: {worker_name}")

    def get(self, worker_name: str) -> dict:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT * FROM worker_metrics WHERE worker_name=?
        """, (worker_name,)).fetchone()
        conn.close()
        if not row:
            return {
                "worker_name":          worker_name,
                "success_count":        0,
                "failure_count":        0,
                "avg_duration_ms":      0.0,
                "last_success":         None,
                "last_failure":         None,
                "consecutive_failures": 0
            }
        return dict(row)

    def success_rate(self, worker_name: str) -> float:
        m = self.get(worker_name)
        total = m["success_count"] + m["failure_count"]
        if total == 0:
            return 1.0  # 実績なし = 最大信頼
        return m["success_count"] / total

    def all_metrics(self) -> list:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM worker_metrics "
            "ORDER BY worker_name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def is_degraded(self, worker_name: str,
                    threshold: int = 3) -> bool:
        """連続失敗がthreshold以上でTrue"""
        m = self.get(worker_name)
        return m["consecutive_failures"] >= threshold
