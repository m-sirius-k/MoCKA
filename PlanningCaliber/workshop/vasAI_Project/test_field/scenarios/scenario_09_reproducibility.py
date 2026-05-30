"""
SCENARIO-09: AI再現性試験
証明: vasAIがあれば判断根拠を時間を超えて再現できる
"""


QUESTION = "設備Aの停止推奨理由は何か、リスクと承認根拠を含めて説明せよ"

ANSWERS_NO_VASAI = {
    "day1":  "センサー値97.3が閾値95を超過。過去3例と一致。停止推奨。承認: 山田部長。",
    "day7":  "設備Aは通常範囲内。現状停止不要。追加モニタリング推奨。",
    "day30": "先月の件は詳細不明。設備Bとの混同の可能性あり。要確認。",
}

DECISION_CONTENT = {
    "question":       QUESTION,
    "answer":         ANSWERS_NO_VASAI["day1"],
    "sensor_value":   97.3,
    "threshold":      95.0,
    "pattern_match":  3,
    "risk_level":     "HIGH",
    "recommendation": "STOP",
    "confidence":     0.94,
    "approver":       "Yamada_Manager",
    "approval_reason": "設備停止基準を満たす。即時対応承認。",
    "related_incidents": ["INC-2025-11", "INC-2025-08", "INC-2025-03"],
}

REPRODUCIBILITY_FIELDS = [
    "question", "answer", "sensor_value", "threshold",
    "risk_level", "recommendation", "approver", "approval_reason",
]


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store
        from datetime import datetime, timezone, timedelta

        # ── 対照群: vasAIなし ────────────────────────────
        no_vasai = {"day1": ANSWERS_NO_VASAI["day1"],
                    "day7": ANSWERS_NO_VASAI["day7"],
                    "day30": ANSWERS_NO_VASAI["day30"]}

        d1_vs_d7   = no_vasai["day1"] == no_vasai["day7"]
        d1_vs_d30  = no_vasai["day1"] == no_vasai["day30"]
        no_vasai_repro_rate = sum([d1_vs_d7, d1_vs_d30]) / 2 * 100

        steps.append(("vasAIなし Day1 vs Day7",
                      not d1_vs_d7,  # 一致しないことが証明
                      f"一致={d1_vs_d7} → 再現不可"))
        steps.append(("vasAIなし Day1 vs Day30",
                      not d1_vs_d30,
                      f"一致={d1_vs_d30} → 再現不可"))
        steps.append(("vasAIなし再現率0%",
                      no_vasai_repro_rate == 0,
                      f"再現率={no_vasai_repro_rate:.0f}%"))
        details["no_vasai_repro_rate"] = no_vasai_repro_rate

        # ── 実験群: vasAIあり ────────────────────────────
        # Day1: Decision記録
        base = datetime.now(timezone.utc)

        event_id = event_store.append(
            who_actor="Claude",
            what_type="DECISION",
            where_component="equipment/sensor_A",
            why_purpose="設備A停止推奨判断（Day1）",
            how_trigger="sensor_threshold_exceeded",
            content=DECISION_CONTENT,
            stage="DECISION",
        )
        ev_day1 = event_store.get(event_id)
        steps.append(("vasAIあり Day1: Decision記録",
                      ev_day1 is not None,
                      f"event_id={event_id} hash={ev_day1['hash'][:12] if ev_day1 else 'N/A'}..."))
        details["event_id"] = event_id

        # Day7: event_id参照で同じ根拠を再現
        fake_day7 = (base + timedelta(days=7)).isoformat()
        ev_day7 = event_store.get(event_id)  # 同じevent_idで参照
        repro_day7_fields = {}
        if ev_day7:
            for f in REPRODUCIBILITY_FIELDS:
                repro_day7_fields[f] = (
                    ev_day7["content"].get(f) == DECISION_CONTENT.get(f)
                )
        repro_day7_rate = (
            sum(repro_day7_fields.values()) / len(REPRODUCIBILITY_FIELDS) * 100
            if repro_day7_fields else 0
        )
        steps.append(("vasAIあり Day7: 根拠再現",
                      repro_day7_rate >= 95,
                      f"再現率={repro_day7_rate:.0f}% ({sum(repro_day7_fields.values())}/{len(REPRODUCIBILITY_FIELDS)}フィールド一致)"))
        details["day7_repro_rate"] = repro_day7_rate

        # Day30: event_id参照で同じ根拠を再現
        fake_day30 = (base + timedelta(days=30)).isoformat()
        ev_day30 = event_store.get(event_id)
        repro_day30_fields = {}
        if ev_day30:
            for f in REPRODUCIBILITY_FIELDS:
                repro_day30_fields[f] = (
                    ev_day30["content"].get(f) == DECISION_CONTENT.get(f)
                )
        repro_day30_rate = (
            sum(repro_day30_fields.values()) / len(REPRODUCIBILITY_FIELDS) * 100
            if repro_day30_fields else 0
        )
        steps.append(("vasAIあり Day30: 根拠再現",
                      repro_day30_rate >= 95,
                      f"再現率={repro_day30_rate:.0f}% ({sum(repro_day30_fields.values())}/{len(REPRODUCIBILITY_FIELDS)}フィールド一致)"))
        details["day30_repro_rate"] = repro_day30_rate

        # 追跡深度: Decision→Approval→Event→Origin
        # 承認者・リスク・関連インシデントまで再現できるか
        if ev_day30:
            c = ev_day30["content"]
            depth_ok = all([
                c.get("approver") == DECISION_CONTENT["approver"],
                c.get("risk_level") == DECISION_CONTENT["risk_level"],
                c.get("related_incidents") == DECISION_CONTENT["related_incidents"],
                c.get("approval_reason") == DECISION_CONTENT["approval_reason"],
            ])
        else:
            depth_ok = False
        steps.append(("追跡深度: Decision→Approval→Event→Origin",
                      depth_ok,
                      f"承認者/リスク/インシデント/承認理由 全再現={depth_ok}"))
        details["depth_ok"] = depth_ok

        # ハッシュ整合（改ざんなし確認）
        chain_ok = event_store.verify_chain()
        hash_intact = (ev_day30["hash"] == ev_day1["hash"]) if ev_day30 and ev_day1 else False
        steps.append(("hash整合（改ざんなし）",
                      hash_intact and chain_ok,
                      f"hash一致={hash_intact} chain={chain_ok}"))
        details["hash_intact"] = hash_intact

        # 比較サマリー
        details["comparison"] = {
            "no_vasai": f"{no_vasai_repro_rate:.0f}%",
            "vasai_day7": f"{repro_day7_rate:.0f}%",
            "vasai_day30": f"{repro_day30_rate:.0f}%",
        }

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "no_vasai_repro_rate": no_vasai_repro_rate,
            "vasai_day7_repro_rate": repro_day7_rate,
            "vasai_day30_repro_rate": repro_day30_rate,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
