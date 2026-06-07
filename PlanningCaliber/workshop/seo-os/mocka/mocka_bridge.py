import sqlite3, os, json
from datetime import datetime
from kernel.logger import info, warn

MOCKA_DB = "C:/Users/sirok/MoCKA/data/mocka_events.db"

class MoCKABridge:
    """
    SEO-OSとMoCKA（PHI-OS/Orchestra）の接続層。
    Decision LedgerをMoCKA events.dbに転送する。
    """

    def push_decision(self, decision: dict) -> bool:
        """Decision LedgerをMoCKA events.dbに記録"""
        try:
            conn = sqlite3.connect(MOCKA_DB)
            eid  = f"ESEOS_DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            conn.execute("""
                INSERT INTO events
                (event_id,who_actor,what_type,
                 where_component,why_purpose,
                 how_trigger,when_ts)
                VALUES (?,?,?,?,?,?,?)
            """, (
                eid,
                "SEO-OS",
                "DECISION",
                "caliber_manager",
                f"{decision['capability']} → "
                f"{decision['selected_worker']} "
                f"/ strategy={decision['strategy']}",
                decision.get("job_id",""),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            info(f"[Bridge] MoCKA転送: {eid}")
            return True
        except Exception as e:
            warn(f"[Bridge] MoCKA転送失敗: {e}")
            return False

    def push_job_completed(self, job: dict) -> bool:
        """Job完了をMoCKA events.dbに記録"""
        try:
            conn = sqlite3.connect(MOCKA_DB)
            eid  = f"ESEOS_JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            conn.execute("""
                INSERT INTO events
                (event_id,who_actor,what_type,
                 where_component,why_purpose,
                 how_trigger,when_ts)
                VALUES (?,?,?,?,?,?,?)
            """, (
                eid,
                "SEO-OS",
                "JOB_COMPLETED",
                "pipeline_engine",
                f"{job['title']} 公開完了 / "
                f"URL={job.get('result_url','')}",
                job["id"],
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            warn(f"[Bridge] Job完了転送失敗: {e}")
            return False
