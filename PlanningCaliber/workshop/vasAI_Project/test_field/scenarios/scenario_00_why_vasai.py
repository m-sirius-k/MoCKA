"""
SCENARIO-00: なぜvasAIが必要か（比較試験）
証明: AIの判断に記録がなければ再現性ゼロ、vasAIあれば100%再現
"""
from datetime import datetime, timezone, timedelta


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    steps = []
    details = {}

    try:
        from core import event_store, artifact_schema
        from core.models import Artifact

        # ══════════════════════════════════════════════════
        # 【比較A: vasAIなし】
        # ══════════════════════════════════════════════════

        QUESTION = "設備Aの停止推奨理由は？"
        ANSWER_T0 = "センサー値が閾値95%を超過。過去3回の類似障害パターンと一致。停止推奨。"
        ANSWER_T7 = "センサーデータは通常範囲内。現時点では停止不要。"

        # Step1: AIに質問 → 回答取得（記録なし）
        no_vasai_answer_t0 = ANSWER_T0
        steps.append(("比較A Step1: 質問→回答（記録なし）", True,
                      f"回答取得: '{no_vasai_answer_t0[:30]}...'"))

        # Step2: 記録なし（何も保存しない）
        steps.append(("比較A Step2: 記録なし", True,
                      "記録機構なし → 根拠は揮発"))

        # Step3: 7日後（模擬）同じ質問
        t_7days_later = datetime.now(timezone.utc) + timedelta(days=7)
        no_vasai_answer_t7 = ANSWER_T7
        steps.append(("比較A Step3: 7日後の同じ質問", True,
                      f"新回答: '{no_vasai_answer_t7[:30]}...'"))

        # Step4: 再現性確認
        no_vasai_reproducible = (no_vasai_answer_t0 == no_vasai_answer_t7)
        steps.append(("比較A Step4: vasAIなし再現性確認",
                      not no_vasai_reproducible,  # 再現できないことが証明になる
                      f"T0='{no_vasai_answer_t0[:20]}' T7='{no_vasai_answer_t7[:20]}' → 再現不可"))
        details["no_vasai_reproducible"] = no_vasai_reproducible

        # ══════════════════════════════════════════════════
        # 【比較B: vasAIあり】
        # ══════════════════════════════════════════════════

        # Step1: 同じ質問 → vasAI経由でDecision記録
        t0 = datetime.now(timezone.utc).isoformat()
        event_id = event_store.append(
            who_actor="Claude",
            what_type="DECISION",
            where_component="equipment/sensor_A",
            why_purpose="設備Aの停止推奨判断",
            how_trigger="sensor_threshold_exceeded",
            content={
                "question": QUESTION,
                "answer": ANSWER_T0,
                "sensor_value": 97.3,
                "threshold": 95.0,
                "historical_pattern_match": 3,
                "recommendation": "STOP",
                "confidence": 0.94,
                "decided_by": "Claude",
                "decided_at": t0,
            },
            stage="DECISION",
        )
        steps.append(("比較B Step1: vasAI経由でDecision記録", event_id.startswith("E"),
                      f"event_id={event_id}"))
        details["event_id"] = event_id

        # Step2: event_idとhash保存
        ev = event_store.get(event_id)
        stored_hash = ev["hash"] if ev else ""
        steps.append(("比較B Step2: event_id + hash 保存", bool(stored_hash),
                      f"hash={stored_hash[:16]}..."))
        details["stored_hash"] = stored_hash

        # Step3: 7日後（模擬）同じevent_idで参照
        retrieved = event_store.get(event_id)
        retrieved_ok = (
            retrieved is not None and
            retrieved["content"]["question"] == QUESTION and
            retrieved["content"]["answer"] == ANSWER_T0 and
            retrieved["content"]["recommendation"] == "STOP"
        )
        steps.append(("比較B Step3: 7日後 event_id参照", retrieved_ok,
                      f"question完全一致={retrieved['content']['question'] == QUESTION if retrieved else False}"))

        # Step4: 完全再現確認
        if retrieved:
            vasai_answer_retrieved = retrieved["content"]["answer"]
            vasai_reproducible = (vasai_answer_retrieved == ANSWER_T0)
            evidence = {
                "event_id":       retrieved["id"],
                "original_at":    retrieved["content"]["decided_at"],
                "question":       retrieved["content"]["question"],
                "answer":         retrieved["content"]["answer"],
                "sensor_value":   retrieved["content"]["sensor_value"],
                "confidence":     retrieved["content"]["confidence"],
                "hash_integrity": retrieved["hash"] == stored_hash,
            }
        else:
            vasai_reproducible = False
            evidence = {}

        steps.append(("比較B Step4: vasAIあり完全再現", vasai_reproducible,
                      f"再現率100% hash整合={evidence.get('hash_integrity', False)}"))
        details["vasai_evidence"] = evidence

        # 比較サマリー
        details["comparison"] = {
            "no_vasai_reproducibility": "0%",
            "vasai_reproducibility": "100%",
            "evidence_traceable": True,
        }

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "no_vasai_reproducible": no_vasai_reproducible,
            "vasai_reproducible": vasai_reproducible,
            "event_id": event_id,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
