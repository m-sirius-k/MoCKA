import sqlite3, os
from datetime import datetime
from kernel.logger import info, warn

MOCKA_DB = "C:/Users/sirok/MoCKA/data/mocka_events.db"

class PHIOSBridge:
    """
    SEO-OSの意思決定をPHI-OSの監査証跡へ統合する。
    Decision LedgerとPHI-OS判断ログを相互参照可能にする。
    """

    def push_decision_audit(self,
                            decision: dict) -> bool:
        """Decision LedgerをPHI-OS監査証跡に記録"""
        try:
            conn = sqlite3.connect(MOCKA_DB)
            eid  = (f"EPHIOS_DEC_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            detail = (
                f"capability={decision.get('capability','')} "
                f"selected={decision.get('selected_worker','')} "
                f"strategy={decision.get('strategy','')} "
                f"outcome={decision.get('outcome','')}")
            conn.execute("""
                INSERT INTO events
                (event_id,who_actor,what_type,
                 where_component,why_purpose,
                 how_trigger,when_ts)
                VALUES (?,?,?,?,?,?,?)
            """, (eid, "SEO-OS/PHI-OS",
                  "AUDIT_DECISION",
                  "phi_os_bridge",
                  detail,
                  decision.get("job_id",""),
                  datetime.now().isoformat()))
            conn.commit()
            conn.close()
            info(f"[PHIOSBridge] 監査記録: {eid}")
            return True
        except Exception as e:
            warn(f"[PHIOSBridge] 転送失敗: {e}")
            return False

    def push_policy_violation(self,
                              worker_name: str,
                              rule: str,
                              capability: str) -> bool:
        """Decision Policy違反をPHI-OSに通知"""
        try:
            conn = sqlite3.connect(MOCKA_DB)
            eid  = (f"EPHIOS_POL_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            conn.execute("""
                INSERT INTO events
                (event_id,who_actor,what_type,
                 where_component,why_purpose,
                 how_trigger,when_ts)
                VALUES (?,?,?,?,?,?,?)
            """, (eid, "SEO-OS/PHI-OS",
                  "POLICY_VIOLATION",
                  "decision_policy",
                  f"Worker={worker_name} "
                  f"rule={rule} "
                  f"capability={capability}",
                  worker_name,
                  datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            warn(f"[PHIOSBridge] Policy違反通知失敗: {e}")
            return False
