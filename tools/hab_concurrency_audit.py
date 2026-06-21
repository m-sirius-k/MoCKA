"""
Phase H0: HAB Multi-AI Concurrency Audit
責務: HAB(4層統合ContextRuntime)が複数AI同時接続に耐えるかをスレッド並行
シミュレーションで実証する。next_event_id()には一切触れない(継続遵守)。
既存の単一AI経路(boot/validate/live_update/snapshot)への変更は行わない。
読み取り専用の監査スクリプトであり、本番ファイルへの書き込みは
live_update()/snapshot()自体が行う既存動作のみを使う。
"""
from __future__ import annotations
import json
import shutil
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SNAP_DIR = ROOT / "data" / "context_snapshots"
WORKING_LATEST = SNAP_DIR / "working_context_latest.json"
LOG_PATH = ROOT / "tools" / "hab_concurrency_audit_log.json"

N_THREADS = 10


def _backup_working_latest() -> Path | None:
    if WORKING_LATEST.exists():
        backup = SNAP_DIR / f"working_context_latest.json.bak_audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(WORKING_LATEST, backup)
        return backup
    return None


def test1_boot_concurrency() -> dict:
    from phi_os.context.context_runtime import ContextRuntime

    results: list = []
    errors: list = []
    lock = threading.Lock()

    def call_boot():
        try:
            rt = ContextRuntime.boot()
            with lock:
                results.append(rt)
        except Exception as e:
            with lock:
                errors.append(repr(e))

    threads = [threading.Thread(target=call_boot) for _ in range(N_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    ids = {id(r) for r in results}
    return {
        "test": "1_boot_concurrency",
        "threads": N_THREADS,
        "success_count": len(results),
        "error_count": len(errors),
        "errors": errors,
        "distinct_instances": len(ids),
        "verdict": "OK" if len(errors) == 0 and len(results) == N_THREADS else "NG",
    }


def test2_validate_concurrency() -> dict:
    from phi_os.context.context_runtime import ContextRuntime

    rt = ContextRuntime.boot()
    results: list = []
    errors: list = []
    lock = threading.Lock()

    def call_validate():
        try:
            v = rt.validate()
            with lock:
                results.append(v)
        except Exception as e:
            with lock:
                errors.append(repr(e))

    threads = [threading.Thread(target=call_validate) for _ in range(N_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    verdicts = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in results}
    return {
        "test": "2_validate_concurrency",
        "threads": N_THREADS,
        "success_count": len(results),
        "error_count": len(errors),
        "errors": errors,
        "distinct_results": len(verdicts),
        "verdict": "OK" if len(errors) == 0 and len(results) == N_THREADS else "NG",
    }


def test3_live_update_concurrency() -> dict:
    from phi_os.context.working_context import WorkingContext

    backup = _backup_working_latest()
    errors: list = []
    lock = threading.Lock()

    def call_live_update(task_name: str):
        try:
            WorkingContext.live_update(
                current_task=f"CONCURRENT_TEST_{task_name}",
                current_goal=f"goal_{task_name}",
            )
        except Exception as e:
            with lock:
                errors.append(repr(e))

    threads = [
        threading.Thread(target=call_live_update, args=(f"AI_{i}",))
        for i in range(N_THREADS)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    json_corrupted = False
    final_task = None
    try:
        data = json.loads(WORKING_LATEST.read_text(encoding="utf-8"))
        final_task = data.get("current_task")
    except Exception as e:
        json_corrupted = True
        errors.append(f"JSON_PARSE_FAIL: {e!r}")

    # 元の状態へ復元(テスト汚染を残さない)
    if backup is not None:
        shutil.copy2(backup, WORKING_LATEST)
        backup.unlink()

    return {
        "test": "3_live_update_concurrency",
        "threads": N_THREADS,
        "error_count": len(errors),
        "errors": errors,
        "json_corrupted": json_corrupted,
        "final_current_task": final_task,
        "verdict": "OK" if not json_corrupted and len(errors) == 0 else "NG",
    }


def test4_snapshot_vs_update() -> dict:
    from phi_os.context.context_runtime import ContextRuntime
    from phi_os.context.working_context import WorkingContext

    backup = _backup_working_latest()
    errors: list = []
    lock = threading.Lock()
    snapshot_results: list = []

    def call_snapshot():
        try:
            rt = ContextRuntime.boot()
            data = rt.snapshot()
            with lock:
                snapshot_results.append(data)
        except Exception as e:
            with lock:
                errors.append(f"snapshot: {e!r}")

    def call_update(task_name: str):
        try:
            for i in range(5):
                WorkingContext.live_update(
                    current_task=f"SNAP_RACE_{task_name}_{i}",
                    current_goal=f"goal_{task_name}_{i}",
                )
        except Exception as e:
            with lock:
                errors.append(f"update: {e!r}")

    threads = []
    threads.append(threading.Thread(target=call_snapshot))
    for i in range(N_THREADS):
        threads.append(threading.Thread(target=call_update, args=(f"AI_{i}",)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    working_json_corrupted = False
    try:
        json.loads(WORKING_LATEST.read_text(encoding="utf-8"))
    except Exception as e:
        working_json_corrupted = True
        errors.append(f"JSON_PARSE_FAIL(working): {e!r}")

    snapshot_json_valid = True
    for s in snapshot_results:
        try:
            json.dumps(s, ensure_ascii=False)
        except Exception as e:
            snapshot_json_valid = False
            errors.append(f"JSON_DUMP_FAIL(snapshot): {e!r}")

    if backup is not None:
        shutil.copy2(backup, WORKING_LATEST)
        backup.unlink()

    return {
        "test": "4_snapshot_vs_update",
        "snapshot_calls": len(snapshot_results),
        "error_count": len(errors),
        "errors": errors,
        "working_json_corrupted": working_json_corrupted,
        "snapshot_json_valid": snapshot_json_valid,
        "verdict": "OK" if not working_json_corrupted and snapshot_json_valid and len(errors) == 0 else "NG",
    }


def test5_ownership_check() -> dict:
    import inspect
    from phi_os.context import working_context as wc_module

    live_update_sig = inspect.signature(wc_module.WorkingContext.live_update)
    has_actor_param = any(
        p in live_update_sig.parameters for p in ("actor", "author", "ai_id", "caller_id")
    )

    return {
        "test": "5_ownership_check",
        "live_update_signature": str(live_update_sig),
        "has_explicit_actor_param": has_actor_param,
        "note_current_ai_param": "current_ai" in live_update_sig.parameters,
        "finding": (
            "current_ai は最終更新者の自己申告フィールドであり、書き込み主体を強制識別する"
            "actorパラメータではない。mocka_write_eventのauthorパラメータと同様の仕組みは"
            "WorkingContext.live_update()には伝播していない。"
        ),
        "verdict": "CONFIRMED_GAP" if not has_actor_param else "OK",
    }


def main() -> None:
    print(f"HAB Multi-AI Concurrency Audit - {datetime.now(timezone.utc).isoformat()}")
    print(f"N_THREADS = {N_THREADS}\n")

    results = []
    for fn in (
        test1_boot_concurrency,
        test2_validate_concurrency,
        test3_live_update_concurrency,
        test4_snapshot_vs_update,
        test5_ownership_check,
    ):
        r = fn()
        results.append(r)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print()
        time.sleep(0.2)

    overall_ng = [r for r in results if r.get("verdict") in ("NG",)]
    summary = {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "n_threads": N_THREADS,
        "results": results,
        "ng_count": len(overall_ng),
        "overall_verdict": "PASS" if len(overall_ng) == 0 else "FAIL",
    }

    LOG_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"総合判定: {summary['overall_verdict']} (NG件数: {summary['ng_count']})")
    print(f"ログ保存先: {LOG_PATH}")


if __name__ == "__main__":
    main()
