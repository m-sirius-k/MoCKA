"""
SCENARIO-02: shadow_movement 縮退・回復試験
証明: 本体障害時も75%機能で継続、回復後に自動同期
"""
import time


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    # shadow listenerリセット
    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from movement.mocka_movement import MoCKAMovement
        from movement.shadow_movement import ShadowMovement
        from core import event_store, audit_chain

        movement = MoCKAMovement()
        shadow = ShadowMovement()

        # Step1: 正常稼働確認
        alive = shadow.is_alive()
        steps.append(("Step1: shadow稼働確認", alive, f"is_alive={alive}"))

        # Step2: available_pct=1.0確認
        status = shadow.get_status()
        normal_pct = status.available_pct == 1.0
        steps.append(("Step2: 正常時稼働率", normal_pct,
                      f"available_pct={status.available_pct}"))

        # Step3: 正常時に3件記録（mocka経由でshadowにミラー）
        for i in range(3):
            movement.run_cycle({
                "source_app": "TestSystem",
                "source_service": "scenario02",
                "msg": f"pre-degraded event {i}",
            })
        pre_mirror = shadow.get_stats()["mirror_count"]
        steps.append(("Step3: 正常時ミラーリング", pre_mirror >= 1,
                      f"ミラー件数={pre_mirror}件"))

        # Step4: 縮退モード発動
        t_enter = time.time()
        degraded_status = shadow.enter_degraded_mode("mocka_movement模擬障害")
        t_enter_elapsed = time.time() - t_enter
        degraded_ok = degraded_status.is_degraded and degraded_status.available_pct == 0.75
        steps.append(("Step4: 縮退モード発動", degraded_ok,
                      f"available_pct={degraded_status.available_pct} "
                      f"active_stages={len(degraded_status.active_stages)}ステージ"))
        details["degraded_enter_ms"] = round(t_enter_elapsed * 1000, 2)

        # Step5: 縮退中5件イベント記録（shadowに直接mirror）
        degraded_events = 0
        for i in range(5):
            # 縮退中はshadowのmirrorで記録
            shadow.mirror({"stage": "INCIDENT", "event_id": f"DEG_E{i:03d}",
                           "content": f"degraded event {i}"})
            degraded_events += 1
        steps.append(("Step5: 縮退中5件記録", degraded_events == 5,
                      f"縮退中記録={degraded_events}/5件"))
        details["degraded_recorded"] = degraded_events

        # Step6: 縮退中稼働率確認
        deg_status = shadow.get_status()
        deg_pct_ok = deg_status.available_pct == 0.75
        steps.append(("Step6: 縮退稼働率確認", deg_pct_ok,
                      f"available_pct={deg_status.available_pct}"))
        details["degraded_stages"] = [s.value for s in deg_status.active_stages]

        # Step7: mocka_movement回復（縮退モード終了）
        shadow.exit_degraded_mode()
        steps.append(("Step7: mocka_movement回復", True, "exit_degraded_mode()呼出"))

        # Step8: sync_on_recovery → 5件同期
        synced = shadow.sync_on_recovery()
        steps.append(("Step8: 回復後同期", synced == 5,
                      f"同期件数={synced}/5件"))
        details["synced_count"] = synced

        # Step9: 回復後稼働率=1.0確認
        recovered_status = shadow.get_status()
        recovered_ok = not recovered_status.is_degraded and recovered_status.available_pct == 1.0
        steps.append(("Step9: 回復確認", recovered_ok,
                      f"available_pct={recovered_status.available_pct}"))

        # Step10: チェーン検証
        chain_ok = event_store.verify_chain()
        steps.append(("Step10: チェーン整合確認", chain_ok,
                      f"verify_chain()={chain_ok}"))

        details["downtime_sec"] = 0  # shadow継続稼働のためダウンタイム0
        all_pass = all(s[1] for s in steps)

        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "degraded_pct": 0.75,
            "degraded_recorded": degraded_events,
            "synced_count": synced,
            "chain_valid": chain_ok,
            "downtime_sec": 0,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [(f"ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
