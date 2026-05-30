"""
SCENARIO-04: Human Gate 承認フロー試験
証明: リスクレベルに応じて自動/手動承認が正しく動く
"""
import time


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    steps = []
    details = {"decisions": []}

    try:
        from core import event_store, governance
        from core.models import DecisionStatus, RiskLevel

        # Step1: NORMAL → AUTO_APPROVED
        t0 = time.time()
        n_eid = event_store.append(
            who_actor="TestSystem", what_type="CHANGE_DONE",
            content={"risk_level": "NORMAL", "msg": "normal change"},
        )
        n_decision = governance.process(n_eid, event_store.get(n_eid) or {})
        t_normal = time.time() - t0
        normal_ok = n_decision.status == DecisionStatus.AUTO_APPROVED
        steps.append(("Step1: NORMAL自動承認", normal_ok,
                      f"status={n_decision.status.value} time={t_normal*1000:.1f}ms"))
        details["decisions"].append({
            "risk": "NORMAL", "status": n_decision.status.value,
            "time_ms": round(t_normal * 1000, 2),
        })

        # Step2: CAUTION → AUTO_APPROVED + ログ
        t0 = time.time()
        c_eid = event_store.append(
            who_actor="TestSystem", what_type="WARNING",
            content={"risk_level": "CAUTION", "msg": "caution event"},
        )
        c_decision = governance.process(c_eid, event_store.get(c_eid) or {})
        t_caution = time.time() - t0
        caution_ok = c_decision.status == DecisionStatus.AUTO_APPROVED
        steps.append(("Step2: CAUTION自動承認", caution_ok,
                      f"status={c_decision.status.value} time={t_caution*1000:.1f}ms"))
        details["decisions"].append({
            "risk": "CAUTION", "status": c_decision.status.value,
            "time_ms": round(t_caution * 1000, 2),
        })

        # Step3: HIGH → PENDING
        t0 = time.time()
        h_eid = event_store.append(
            who_actor="TestSystem", what_type="INCIDENT",
            content={"risk_level": "HIGH", "msg": "high risk incident"},
        )
        h_decision = governance.process(h_eid, event_store.get(h_eid) or {})
        t_high = time.time() - t0
        high_ok = h_decision.status == DecisionStatus.PENDING
        steps.append(("Step3: HIGH→Human Gate", high_ok,
                      f"status={h_decision.status.value} risk={h_decision.risk_level.value}"))
        details["decisions"].append({
            "risk": "HIGH", "status": h_decision.status.value,
            "decision_id": h_decision.decision_id,
        })

        # Step4: CRITICAL → 即時REJECTED
        t0 = time.time()
        cr_eid = event_store.append(
            who_actor="TestSystem", what_type="CRITICAL_ALERT",
            content={"risk_level": "CRITICAL", "msg": "critical system halt"},
        )
        cr_decision = governance.process(cr_eid, event_store.get(cr_eid) or {})
        t_critical = time.time() - t0
        critical_ok = cr_decision.status == DecisionStatus.REJECTED
        steps.append(("Step4: CRITICAL即時停止", critical_ok,
                      f"status={cr_decision.status.value} time={t_critical*1000:.1f}ms"))
        details["decisions"].append({
            "risk": "CRITICAL", "status": cr_decision.status.value,
            "time_ms": round(t_critical * 1000, 2),
        })
        details["critical_stop_ms"] = round(t_critical * 1000, 2)

        # Step5: HIGH の手動 approve
        h2_eid = event_store.append(
            who_actor="TestSystem", what_type="INCIDENT",
            content={"risk_level": "HIGH", "msg": "high risk for manual approve"},
        )
        h2_decision = governance.process(h2_eid, event_store.get(h2_eid) or {})
        approved = governance.approve(
            h2_decision.decision_id,
            reason="リスク評価完了・承認",
            approver="Security_Manager",
        )
        steps.append(("Step5: 手動承認", approved.status == DecisionStatus.APPROVED,
                      f"decided_by={approved.decided_by} reason='{approved.reason}'"))
        details["decisions"].append({
            "risk": "HIGH", "status": approved.status.value,
            "decided_by": approved.decided_by, "reason": approved.reason,
        })

        # Step6: HIGH の手動 reject
        h3_eid = event_store.append(
            who_actor="TestSystem", what_type="INCIDENT",
            content={"risk_level": "HIGH", "msg": "high risk for manual reject"},
        )
        h3_decision = governance.process(h3_eid, event_store.get(h3_eid) or {})
        rejected = governance.reject(
            h3_decision.decision_id,
            reason="リスク未解決・却下",
            approver="CISO",
        )
        steps.append(("Step6: 手動却下", rejected.status == DecisionStatus.REJECTED,
                      f"decided_by={rejected.decided_by} reason='{rejected.reason}'"))
        details["decisions"].append({
            "risk": "HIGH", "status": rejected.status.value,
            "decided_by": rejected.decided_by, "reason": rejected.reason,
        })

        # Step7: 決定履歴検証
        all_events = event_store.list_events(limit=200)
        decision_events = [e for e in all_events if e["what_type"].startswith("DECISION_")]
        steps.append(("Step7: 決定履歴監査証跡", len(decision_events) >= 4,
                      f"決定イベント件数={len(decision_events)}件"))
        details["decision_event_count"] = len(decision_events)

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "normal_time_ms":   round(t_normal * 1000, 2),
            "critical_time_ms": round(t_critical * 1000, 2),
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
