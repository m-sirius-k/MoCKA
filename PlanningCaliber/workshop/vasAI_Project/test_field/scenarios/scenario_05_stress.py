"""
SCENARIO-05: 負荷・整合性試験（3段階）
証明: 1K/10K/100K件の連続記録でもチェーンが崩れない
"""
import random
import time


STRESS_LEVELS = [
    ("LEVEL-1",   1_000, "開発規模"),
    ("LEVEL-2",  10_000, "中規模企業"),
    ("LEVEL-3", 100_000, "大規模運用"),
]


def _run_level(count: int, label: str, db_path: str) -> dict:
    """1ストレスレベルを実行して結果を返す。"""
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    # DBキャッシュをこのパスで初期化
    from core import event_store
    event_store.initialize()

    stages = ["OBSERVATION", "RECORD", "INCIDENT", "RECURRENCE",
              "PREVENTION", "DECISION", "ACTION", "AUDIT"]
    actors = ["Claude", "Human", "ShadowMovement", "vasAI", "API"]
    what_types = ["CHANGE_START", "CHANGE_DONE", "INCIDENT_DETECTED",
                  "DECISION_AUTO_APPROVED", "ACTION_EXECUTED",
                  "AUDIT_COMPLETED", "ARTIFACT_RECORDED", "CALIBER_INBOUND"]

    t_start = time.time()
    for i in range(count):
        event_store.append(
            who_actor=actors[i % len(actors)],
            what_type=what_types[i % len(what_types)],
            where_component=f"component_{i % 50}",
            why_purpose=f"stress_{label}_{i}",
            content={"index": i, "batch": i // 1000, "value": i * 0.001},
            stage=stages[i % len(stages)],
        )
    t_record = time.time() - t_start

    rps = count / t_record if t_record > 0 else 0

    t_verify = time.time()
    chain_ok = event_store.verify_chain()
    t_verify_elapsed = time.time() - t_verify

    total_events = len(event_store.list_events(limit=count + 10))

    return {
        "count":           count,
        "label":           label,
        "recorded":        total_events,
        "record_time_sec": round(t_record, 3),
        "records_per_sec": round(rps, 0),
        "chain_valid":     chain_ok,
        "verify_time_sec": round(t_verify_elapsed, 3),
        "success":         total_events >= count and chain_ok and rps > 100,
    }


def run(db_path: str) -> dict:
    import os
    import tempfile

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {"levels": []}
    all_level_pass = True

    for level_id, count, label in STRESS_LEVELS:
        # 各レベル独立したDBを使用
        level_db = tempfile.mktemp(suffix=f"_{level_id}.db")
        os.environ["VASAI_DB_PATH"] = level_db

        # 接続キャッシュをリセット（新DBに切替）
        from core import event_store
        if level_db in event_store._conn_cache:
            event_store._conn_cache.pop(level_db, None)

        result = _run_level(count, label, level_db)
        details["levels"].append({**result, "level_id": level_id})

        ok = result["success"]
        all_level_pass = all_level_pass and ok
        steps.append((
            f"{level_id} {count:,}件 ({label})",
            ok,
            f"{result['records_per_sec']:.0f}件/秒 chain={'VALID' if result['chain_valid'] else 'BROKEN'} "
            f"時間={result['record_time_sec']:.2f}秒",
        ))

        # DB後始末
        try:
            import pathlib
            pathlib.Path(level_db).unlink(missing_ok=True)
        except Exception:
            pass

    return {
        "success": all_level_pass,
        "steps": steps,
        "details": details,
        "levels": details["levels"],
    }
