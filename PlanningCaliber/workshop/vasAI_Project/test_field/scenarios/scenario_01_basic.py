"""
SCENARIO-01: 基本記録・監査試験
証明: AIの行動が記録され、改ざん不可で監査できる
"""
import sqlite3
import time
from pathlib import Path


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    steps = []
    details = {}

    try:
        from core import event_store, audit_chain

        # Step1: イベントストア初期化確認
        event_store.initialize()
        steps.append(("Step1: 初期化", True, "event_store initialized"))

        # Step2: 10件のイベントを記録（Claude/Human/ShadowMovement 混在）
        actors = ["Claude", "Human", "ShadowMovement", "Claude", "Human",
                  "Claude", "ShadowMovement", "Human", "Claude", "vasAI"]
        what_types = ["CHANGE_START", "REVIEW", "MIRROR", "CHANGE_DONE",
                      "APPROVAL", "INCIDENT_DETECTED", "SHADOW_VERIFY_OK",
                      "DECISION_APPROVED", "ACTION_EXECUTED", "AUDIT_COMPLETED"]
        event_ids = []
        for i, (actor, what) in enumerate(zip(actors, what_types)):
            eid = event_store.append(
                who_actor=actor,
                what_type=what,
                where_component=f"component_{i}",
                why_purpose=f"scenario01 step {i+1}",
                content={"index": i, "msg": f"test event {i+1}"},
                stage=["OBSERVATION","RECORD","INCIDENT","RECURRENCE",
                       "PREVENTION","DECISION","ACTION","AUDIT","RECORD","AUDIT"][i],
            )
            event_ids.append(eid)
        steps.append(("Step2: 10件記録", len(event_ids) == 10,
                      f"{len(event_ids)}/10件記録成功"))
        details["recorded_ids"] = event_ids

        # Step3: 全件取得して内容確認
        all_events = event_store.list_events(limit=100)
        retrieved = [e for e in all_events if e["id"] in event_ids]
        steps.append(("Step3: 全件取得", len(retrieved) == 10,
                      f"{len(retrieved)}/10件取得確認"))

        # Step4: verify_chain() → True
        chain_ok = event_store.verify_chain()
        steps.append(("Step4: チェーン検証", chain_ok,
                      f"verify_chain() = {chain_ok}"))

        # Step5: 改ざん試行 → verify_chain() → False
        tamper_detected = False
        db_file = Path(db_path)
        if db_file.exists():
            conn = sqlite3.connect(str(db_file))
            try:
                # 最初のイベントのcontentを直接書き換え
                first_id = event_ids[0]
                conn.execute(
                    "UPDATE events SET content = '{\"tampered\": true}' WHERE id = ?",
                    (first_id,)
                )
                conn.commit()
            finally:
                conn.close()
            # 改ざん後の検証
            chain_after_tamper = event_store.verify_chain()
            tamper_detected = not chain_after_tamper  # Falseになれば検知成功

        steps.append(("Step5: 改ざん検知", tamper_detected,
                      f"改ざん後verify_chain() = {not tamper_detected} → 検知{'成功' if tamper_detected else '失敗'}"))

        # 改ざんを元に戻す（DBを再作成 = 新しいテスト用DB）
        # 改ざんしたDBはそのままにして seal だけ新DBで実施
        # Step6: seal()
        try:
            seal_sig = audit_chain.seal()
            steps.append(("Step6: 封印", len(seal_sig) == 64,
                          f"seal hash: {seal_sig[:16]}..."))
            details["seal_hash"] = seal_sig
        except Exception as e:
            steps.append(("Step6: 封印", False, str(e)))
            details["seal_hash"] = ""

        # Step7: ステージカウント確認
        counts = event_store.get_stage_counts()
        steps.append(("Step7: ステージ分布", sum(counts.values()) > 0,
                      f"ステージ分布: {counts}"))
        details["stage_counts"] = counts

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "recorded_count": len(event_ids),
            "chain_valid_normal": chain_ok,
            "tamper_detected": tamper_detected,
            "seal_hash": details.get("seal_hash", ""),
        }

    except Exception as e:
        return {
            "success": False,
            "steps": steps + [(f"ERROR: {e}", False, str(e))],
            "details": details,
            "error": str(e),
        }
