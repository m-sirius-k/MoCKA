import sqlite3, os, json
import requests
from datetime import datetime
from kernel.logger import info, warn

MOCKA_DB = "C:/Users/sirok/MoCKA/data/mocka_events.db"
MOCKA_API_BASE = "http://localhost:5000"

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

    def forward_event(self, payload: dict) -> dict:
        """
        POST /api/mocka/event -> MoCKA app.py の /api/phi-os-event に転送する。
        """
        try:
            res = requests.post(
                f"{MOCKA_API_BASE}/api/phi-os-event",
                json=payload, timeout=5)
            info(f"[Bridge] event転送: status={res.status_code}")
            return {
                "ok": res.ok,
                "status_code": res.status_code,
                "response": res.json() if res.ok else res.text,
            }
        except Exception as e:
            warn(f"[Bridge] event転送失敗: {e}")
            return {"ok": False, "error": str(e)}

    def get_context(self, role: str = "ai_claude",
                    mode: str = "full") -> dict:
        """
        GET /api/mocka/context -> MoCKA app.py の
        /api/context/compose から working_context を取得する。
        """
        try:
            res = requests.get(
                f"{MOCKA_API_BASE}/api/context/compose",
                params={"role": role, "mode": mode}, timeout=5)
            if res.ok:
                return res.json()
            return {"ok": False, "status_code": res.status_code, "error": res.text}
        except Exception as e:
            warn(f"[Bridge] context取得失敗: {e}")
            return {"ok": False, "error": str(e)}
