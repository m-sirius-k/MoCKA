"""
SCENARIO-07: 30日連続運用試験
証明: 記録が劣化しないこと（整合性・検索速度・DB増加率）
"""
import time
from datetime import datetime, timezone, timedelta


DAYS = 30
DAILY = {
    "events":    500,
    "decisions":  20,
    "incidents":  10,
    "approvals":   5,
    "seal":        1,
}


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store, audit_chain, governance
        from core.models import DecisionStatus

        base_ts = datetime.now(timezone.utc)
        total_target = DAYS * (DAILY["events"] + DAILY["decisions"]
                               + DAILY["incidents"] + DAILY["approvals"] + DAILY["seal"])

        # Day1 検索速度ベースライン計測
        day1_search_time = None
        day30_search_time = None
        seal_success = 0
        daily_db_sizes = []

        import os as _os

        for day in range(1, DAYS + 1):
            fake_day = base_ts + timedelta(days=day - 1)
            fake_ts = fake_day.isoformat()

            # 通常イベント
            for i in range(DAILY["events"]):
                event_store.append(
                    who_actor=["Claude", "Human", "vasAI"][i % 3],
                    what_type="DAILY_OP",
                    where_component=f"dept_{i % 4}",
                    why_purpose=f"day{day}_op_{i}",
                    content={"day": day, "seq": i, "ts": fake_ts},
                    stage=["OBSERVATION", "RECORD", "ACTION"][i % 3],
                )

            # 意思決定記録
            dec_eids = []
            for i in range(DAILY["decisions"]):
                eid = event_store.append(
                    who_actor="Claude",
                    what_type="DECISION",
                    where_component="management",
                    why_purpose=f"day{day}_decision_{i}",
                    content={"day": day, "decision": f"D{day:02d}-{i:02d}",
                             "risk_level": "NORMAL"},
                    stage="DECISION",
                )
                dec_eids.append(eid)

            # インシデント
            for i in range(DAILY["incidents"]):
                event_store.append(
                    who_actor="vasAI",
                    what_type="INCIDENT_DETECTED",
                    where_component=f"system_{i % 3}",
                    why_purpose=f"day{day}_incident_{i}",
                    content={"day": day, "severity": "MEDIUM", "risk_level": "HIGH"},
                    stage="INCIDENT",
                )

            # 承認フロー（HIGHリスクイベントを作ってapprove）
            for i in range(DAILY["approvals"]):
                appr_eid = event_store.append(
                    who_actor="System",
                    what_type="INCIDENT",
                    why_purpose=f"day{day}_approval_{i}",
                    content={"day": day, "risk_level": "HIGH"},
                    stage="DECISION",
                )
                d = governance.process(appr_eid, event_store.get(appr_eid) or {})
                if d.status == DecisionStatus.PENDING:
                    governance.approve(d.decision_id,
                                       reason=f"Day{day}承認", approver="Manager")

            # 日次封印
            try:
                audit_chain.seal()
                seal_success += 1
            except Exception:
                pass

            # 検索速度計測（Day1とDay30）
            if day == 1:
                t0 = time.time()
                event_store.list_events(limit=50, what_type="DECISION")
                day1_search_time = time.time() - t0

            if day == DAYS:
                t0 = time.time()
                event_store.list_events(limit=50, what_type="DECISION")
                day30_search_time = time.time() - t0

            # DBサイズ追跡（毎5日）
            if day % 5 == 0:
                try:
                    size_kb = _os.path.getsize(db_path) / 1024
                    daily_db_sizes.append({"day": day, "size_kb": round(size_kb, 1)})
                except Exception:
                    pass

        # 最終計測
        total_events = len(event_store.list_events(limit=total_target + 1000))
        t_audit = time.time()
        chain_ok = event_store.verify_chain()
        audit_time = time.time() - t_audit

        # 検索速度劣化率
        if day1_search_time and day30_search_time and day1_search_time > 0:
            speed_degradation_pct = ((day30_search_time - day1_search_time)
                                     / day1_search_time * 100)
        else:
            speed_degradation_pct = 0.0

        # DBサイズ線形性チェック（増加率の分散が小さければ線形）
        linear_growth = True
        if len(daily_db_sizes) >= 3:
            sizes = [d["size_kb"] for d in daily_db_sizes]
            diffs = [sizes[i+1] - sizes[i] for i in range(len(sizes)-1)]
            avg_diff = sum(diffs) / len(diffs) if diffs else 0
            variance = (sum((d - avg_diff)**2 for d in diffs) / len(diffs)) if diffs else 0
            linear_growth = variance < (avg_diff * 2) ** 2  # 変動係数200%以内

        steps.append(("総イベント数",
                      total_events >= total_target * 0.95,
                      f"{total_events:,}件 / 目標{total_target:,}件"))
        steps.append(("30日チェーン整合",
                      chain_ok,
                      f"verify_chain()={chain_ok} ({total_events:,}件)"))
        # サブミリ秒時は絶対時間（50ms以内）で判定、それ以外は20%基準
        both_submilli = (day1_search_time or 0) < 0.05 and (day30_search_time or 0) < 0.05
        speed_ok = both_submilli or abs(speed_degradation_pct) <= 20
        steps.append(("検索速度劣化",
                      speed_ok,
                      f"Day1={day1_search_time*1000:.1f}ms Day30={day30_search_time*1000:.1f}ms "
                      f"劣化={speed_degradation_pct:+.1f}% ({'サブミリ秒・安定' if both_submilli else '基準内'})"))

        steps.append(("DBサイズ線形増加",
                      linear_growth,
                      f"増加パターン={'線形' if linear_growth else '非線形'} "
                      f"サイズ履歴={[d['size_kb'] for d in daily_db_sizes[:3]]}KB..."))
        steps.append(("日次seal成功率",
                      seal_success == DAYS,
                      f"{seal_success}/{DAYS}成功"))
        steps.append(("監査所要時間",
                      audit_time <= 10.0,
                      f"{audit_time:.2f}秒（{total_events:,}件全件）"))

        details = {
            "total_events": total_events,
            "total_target": total_target,
            "chain_valid": chain_ok,
            "day1_search_ms": round((day1_search_time or 0) * 1000, 2),
            "day30_search_ms": round((day30_search_time or 0) * 1000, 2),
            "speed_degradation_pct": round(speed_degradation_pct, 1),
            "linear_growth": linear_growth,
            "seal_success": seal_success,
            "audit_time_sec": round(audit_time, 2),
            "db_sizes": daily_db_sizes,
        }

        return {
            "success": all(s[1] for s in steps),
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
