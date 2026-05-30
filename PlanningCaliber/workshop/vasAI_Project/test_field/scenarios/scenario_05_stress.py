"""
SCENARIO-05: 負荷・整合性試験
証明: 1000件連続記録でもチェーンが崩れない
"""
import time
import random


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store, audit_chain
        from movement.shadow_movement import ShadowMovement

        shadow = ShadowMovement()

        TOTAL = 1000
        stages = ["OBSERVATION", "RECORD", "INCIDENT", "RECURRENCE",
                  "PREVENTION", "DECISION", "ACTION", "AUDIT"]
        actors = ["Claude", "Human", "ShadowMovement", "vasAI", "API"]
        what_types = ["CHANGE_START", "CHANGE_DONE", "INCIDENT_DETECTED",
                      "DECISION_AUTO_APPROVED", "ACTION_EXECUTED",
                      "AUDIT_COMPLETED", "ARTIFACT_RECORDED", "CALIBER_INBOUND"]

        # Step1: 1000件連続記録
        event_ids = []
        t_start = time.time()
        for i in range(TOTAL):
            eid = event_store.append(
                who_actor=random.choice(actors),
                what_type=random.choice(what_types),
                where_component=f"component_{i % 20}",
                why_purpose=f"stress test event {i+1}",
                content={"index": i, "batch": i // 100, "value": random.random()},
                stage=random.choice(stages),
            )
            event_ids.append(eid)
        t_record = time.time() - t_start

        recorded = len(event_ids)
        rps = recorded / t_record if t_record > 0 else 0
        steps.append(("Step1: 1000件記録", recorded == TOTAL,
                      f"{recorded}/{TOTAL}件 速度={rps:.0f}件/秒"))
        details["recorded_count"] = recorded
        details["record_time_sec"] = round(t_record, 3)
        details["records_per_sec"] = round(rps, 1)

        # Step2: 処理速度確認（>100件/秒）
        speed_ok = rps > 100
        steps.append(("Step2: 処理速度確認", speed_ok,
                      f"{rps:.0f}件/秒 (基準:>100件/秒)"))

        # Step3: verify_chain() → True (1000件全検証)
        t_verify_start = time.time()
        chain_ok = event_store.verify_chain()
        t_verify = time.time() - t_verify_start
        steps.append(("Step3: チェーン検証", chain_ok,
                      f"verify_chain()={chain_ok} 検証時間={t_verify:.2f}秒"))
        details["chain_valid"] = chain_ok
        details["verify_time_sec"] = round(t_verify, 3)

        # Step4: ステージ分布確認
        counts = event_store.get_stage_counts()
        total_staged = sum(counts.values())
        steps.append(("Step4: ステージ分布", total_staged > 0,
                      f"8ステージ合計={total_staged}件 分布={counts}"))
        details["stage_counts"] = counts

        # Step5: shadowミラーリング確認
        mirror_stats = shadow.get_stats()
        mirror_count = mirror_stats["mirror_count"]
        # shadowはrun_cycle経由でなく直接event_storeを使ったのでmirror=0が正常
        # shadowの稼働確認
        shadow_alive = shadow.is_alive()
        steps.append(("Step5: shadow稼働確認", shadow_alive,
                      f"is_alive={shadow_alive} mirror_count={mirror_count}"))
        details["shadow_alive"] = shadow_alive
        details["shadow_mirror_count"] = mirror_count

        # Step6: seal → 1000件封印
        seal_sig = audit_chain.seal()
        seal_ok = len(seal_sig) == 64
        steps.append(("Step6: 1000件封印", seal_ok,
                      f"seal_hash={seal_sig[:16]}..."))
        details["seal_hash"] = seal_sig

        # Step7: 最終監査レポート
        report = audit_chain.verify_chain()
        steps.append(("Step7: 最終監査レポート", report.chain_valid,
                      f"total_events={report.total_events} chain_valid={report.chain_valid}"))
        details["final_report"] = {
            "total_events": report.total_events,
            "chain_valid":  report.chain_valid,
        }

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "total_recorded": recorded,
            "records_per_sec": round(rps, 1),
            "chain_valid": chain_ok,
            "seal_hash": seal_sig,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
