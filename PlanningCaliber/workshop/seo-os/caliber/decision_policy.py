import sqlite3, uuid, os, json
from datetime import datetime
from kernel.logger import info, warn

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")

RULE_TYPES = [
    "min_success_rate",
    "max_consecutive_failures",
    "exclude_state",
    "require_tag",
]

class DecisionPolicyEngine:
    """
    Worker選択ルール自体をPolicyとして管理する。
    Caliber Managerの選択前にフィルタリングに使用。

    例:
      min_success_rate=0.8  → 成功率80%未満は除外
      max_consecutive_failures=3 → 連続3回失敗は除外
      exclude_state=offline → offline除外（デフォルト動作を明示化）
    """

    def add_policy(self, name: str, rule_type: str,
                   rule_value: str,
                   capability: str = None,
                   note: str = "") -> str:
        if rule_type not in RULE_TYPES:
            raise ValueError(
                f"不正なrule_type: {rule_type}")
        pid = str(uuid.uuid4())
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO decision_policy
            (id,name,capability,rule_type,
             rule_value,enabled,created_at,note)
            VALUES (?,?,?,?,?,1,?,?)
        """, (pid, name, capability, rule_type,
              rule_value, datetime.now().isoformat(),
              note))
        conn.commit()
        conn.close()
        info(f"[DecisionPolicy] 追加: {name} "
             f"/ {rule_type}={rule_value}")
        return pid

    def get_policies(self,
                     capability: str = None) -> list:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        if capability:
            rows = conn.execute("""
                SELECT * FROM decision_policy
                WHERE enabled=1
                AND (capability=? OR capability IS NULL)
            """, (capability,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM decision_policy
                WHERE enabled=1
            """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def apply(self, candidates: list,
              capability: str,
              ledger) -> list:
        """
        Decision Policyを適用してcandidatesをフィルタ。
        ledger: PerformanceLedger インスタンス
        """
        policies = self.get_policies(capability)
        if not policies:
            return candidates

        filtered = []
        for w in candidates:
            ok = True
            for p in policies:
                rt  = p["rule_type"]
                rv  = p["rule_value"]
                m   = ledger.get(w.name)

                if rt == "min_success_rate":
                    sr = ledger.success_rate(w.name)
                    if sr < float(rv):
                        warn(f"[DecisionPolicy] "
                             f"{w.name} 除外: "
                             f"success_rate={sr:.2f}"
                             f"<{rv}")
                        ok = False

                elif rt == "max_consecutive_failures":
                    cf = m["consecutive_failures"]
                    if cf >= int(rv):
                        warn(f"[DecisionPolicy] "
                             f"{w.name} 除外: "
                             f"consecutive_failures="
                             f"{cf}>={rv}")
                        ok = False

                elif rt == "exclude_state":
                    from caliber.lifecycle_manager \
                        import LifecycleManager
                    state = LifecycleManager()\
                                .get_state(w.name)
                    if state == rv:
                        ok = False

                elif rt == "require_tag":
                    if rv not in w.tags:
                        ok = False

                if not ok:
                    break
            if ok:
                filtered.append(w)
        return filtered

    def disable(self, policy_id: str) -> None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE decision_policy
            SET enabled=0 WHERE id=?
        """, (policy_id,))
        conn.commit()
        conn.close()
        info(f"[DecisionPolicy] 無効化: {policy_id}")
