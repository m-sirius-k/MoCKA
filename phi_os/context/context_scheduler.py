"""
Context Runtime v2 — Snapshot Scheduler
責務: 15分間隔 or イベント100件ごとに ContextRuntime.snapshot() を発火する。
WorkingContext.live_update() と同じ呼び出し元(mocka_write_event)から呼ばれる軽量トリガー。
既存4層ロジック(Gate判定・5チェック)は変更しない。
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

_STATE_PATH = Path(__file__).parents[2] / "data" / "context_snapshots" / "scheduler_state.json"
_INTERVAL_SECONDS = 15 * 60
_EVENT_THRESHOLD = 100


def _load_state() -> dict:
    if _STATE_PATH.exists():
        try:
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_snapshot_at": "", "event_count_since": 0}


def _save_state(state: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def maybe_snapshot() -> bool:
    """
    イベント発生ごとに呼び出す。
    15分経過 or 前回スナップショットから100件のイベントが累積した場合のみ
    ContextRuntime.snapshot() を実行し True を返す。それ以外は状態を更新するだけ。
    """
    state = _load_state()
    state["event_count_since"] = state.get("event_count_since", 0) + 1

    due_by_count = state["event_count_since"] >= _EVENT_THRESHOLD
    due_by_time = True
    last = state.get("last_snapshot_at", "")
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            due_by_time = (datetime.now(timezone.utc) - last_dt).total_seconds() >= _INTERVAL_SECONDS
        except Exception:
            due_by_time = True

    if not (due_by_count or due_by_time):
        _save_state(state)
        return False

    from .context_runtime import ContextRuntime
    rt = ContextRuntime.boot()
    rt.snapshot()

    state["event_count_since"] = 0
    state["last_snapshot_at"] = datetime.now(timezone.utc).isoformat()
    _save_state(state)
    return True
