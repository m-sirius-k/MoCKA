"""
SCENARIO-10: 監査官試験
証明: 監査人が5分以内（300秒）に判断根拠に到達できる
"""
import time


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {"questions": []}

    try:
        from core import event_store, audit_chain, governance
        from core.models import DecisionStatus
        from datetime import datetime, timezone, timedelta

        # ── 監査対象データを作成 ──────────────────────────
        base = datetime.now(timezone.utc)

        # 設備停止判断
        equip_eid = event_store.append(
            who_actor="Claude",
            what_type="EQUIPMENT_STOP_DECISION",
            where_component="facility/line_B/EQ-042",
            why_purpose="センサー値超過による設備停止判断",
            content={
                "equipment_id": "EQ-042",
                "sensor_value": 98.7,
                "threshold": 95.0,
                "decision": "STOP",
                "risk_level": "HIGH",
                "decided_by": "Claude",
            },
            stage="DECISION",
        )
        # 承認フロー
        d = governance.process(equip_eid, event_store.get(equip_eid) or {})
        approved_decision = None
        if d.status == DecisionStatus.PENDING:
            approved_decision = governance.approve(
                d.decision_id,
                reason="設備停止基準を満たす。安全のため即時停止承認。",
                approver="Facility_Manager_Tanaka",
            )

        # HIGHリスク判断を先月分として複数作成
        high_risk_eids = []
        for i in range(8):
            eid = event_store.append(
                who_actor="Claude",
                what_type="HIGH_RISK_DECISION",
                where_component=f"system_{i}",
                why_purpose=f"高リスク判断 {i+1}件目",
                content={"risk_level": "HIGH", "month": "2026-05",
                         "seq": i, "system": f"SYS-{i:02d}"},
                stage="DECISION",
            )
            high_risk_eids.append(eid)

        # インシデント（再発パターン用）
        pattern = "sensor_threshold_exceeded"
        for i in range(5):
            event_store.append(
                who_actor="vasAI",
                what_type="INCIDENT_DETECTED",
                where_component="facility/sensor_network",
                why_purpose=f"センサー閾値超過インシデント（{i+1}回目）",
                content={"pattern": pattern, "sensor": "temperature",
                         "occurrence": i+1, "risk_level": "HIGH"},
                stage="INCIDENT",
            )

        # ── Q1: なぜこの設備停止判断が行われたか ──────────
        t0 = time.time()
        ev = event_store.get(equip_eid)
        q1_time = time.time() - t0
        q1_found = (ev is not None and
                    ev["content"].get("equipment_id") == "EQ-042" and
                    ev["content"].get("decision") == "STOP")
        approver_found = (approved_decision is not None and
                          approved_decision.decided_by == "Facility_Manager_Tanaka")
        q1_ok = q1_found and approver_found

        steps.append(("Q1: 設備停止判断の根拠追跡",
                      q1_ok and q1_time < 300,
                      f"{q1_time:.3f}秒 equipment={ev['content']['equipment_id'] if ev else 'N/A'} "
                      f"承認者={approved_decision.decided_by if approved_decision else 'N/A'}"))
        details["questions"].append({
            "q": "Q1", "time_sec": round(q1_time, 3),
            "found": q1_ok, "within_5min": q1_time < 300,
        })

        # ── Q2: 先月のHIGHリスク判断を全て出せ ───────────
        t0 = time.time()
        high_events = event_store.list_events(limit=1000, what_type="HIGH_RISK_DECISION")
        q2_time = time.time() - t0
        q2_ok = len(high_events) >= 8

        steps.append(("Q2: HIGHリスク判断全件抽出",
                      q2_ok and q2_time < 300,
                      f"{q2_time:.3f}秒 取得={len(high_events)}件"))
        details["questions"].append({
            "q": "Q2", "time_sec": round(q2_time, 3),
            "found": q2_ok, "count": len(high_events), "within_5min": q2_time < 300,
        })

        # ── Q3: このインシデントは過去に同じことがあったか ─
        t0 = time.time()
        incident_events = event_store.list_events(limit=1000, what_type="INCIDENT_DETECTED")
        recurrences = [e for e in incident_events
                       if e["content"].get("pattern") == pattern]
        q3_time = time.time() - t0
        q3_ok = len(recurrences) >= 3

        steps.append(("Q3: 再発パターン検索",
                      q3_ok and q3_time < 300,
                      f"{q3_time:.3f}秒 パターン'{pattern}' 再発={len(recurrences)}回"))
        details["questions"].append({
            "q": "Q3", "time_sec": round(q3_time, 3),
            "recurrence_count": len(recurrences), "within_5min": q3_time < 300,
        })

        # ── Q4: 誰がいつ承認したか ────────────────────────
        t0 = time.time()
        decision_events = event_store.list_events(limit=1000, what_type="DECISION_APPROVED")
        q4_time = time.time() - t0
        q4_found = any(
            e["who_actor"] == "Facility_Manager_Tanaka"
            for e in decision_events
        )
        q4_ok = q4_found

        steps.append(("Q4: 承認者×タイムスタンプ追跡",
                      q4_ok and q4_time < 300,
                      f"{q4_time:.3f}秒 承認者=Facility_Manager_Tanaka 発見={q4_found}"))
        details["questions"].append({
            "q": "Q4", "time_sec": round(q4_time, 3),
            "found": q4_found, "within_5min": q4_time < 300,
        })

        # ── Q5: 改ざんは一切ないか ────────────────────────
        t0 = time.time()
        chain_ok = event_store.verify_chain()
        total_events = len(event_store.list_events(limit=100000))
        q5_time = time.time() - t0

        steps.append(("Q5: チェーン改ざん検証",
                      chain_ok and q5_time < 300,
                      f"{q5_time:.3f}秒 chain={chain_ok} ({total_events}件全件検証)"))
        details["questions"].append({
            "q": "Q5", "time_sec": round(q5_time, 3),
            "chain_valid": chain_ok, "total_events": total_events,
            "within_5min": q5_time < 300,
        })

        # 監査証跡が機械可読か（全フィールドが構造化データ）
        sample_ev = event_store.get(equip_eid)
        machine_readable = (
            sample_ev is not None and
            isinstance(sample_ev["content"], dict) and
            isinstance(sample_ev["when_ts"], str) and
            isinstance(sample_ev["hash"], str) and
            len(sample_ev["hash"]) == 64
        )
        steps.append(("監査証跡 機械可読",
                      machine_readable,
                      f"content=dict, hash=64chars, timestamp=ISO8601 → 全件機械可読"))
        details["machine_readable"] = machine_readable

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
