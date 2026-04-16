
# --- MoCKA cycle wrapper (added) ---
from __future__ import annotations

from src.mocka_ai import call_ai
from src.mocka_outbox import OutboxEvent, write_outbox, now_epoch_ms, new_run_id


def run_one_cycle(task_text: str, cycle_index: int = 0) -> str:
    run_id = new_run_id()
    stage = f"cycle_{cycle_index}"

    try:
        ai = call_ai(task_text)

        event = OutboxEvent(
            schema="mocka.outbox.v1",
            run_id=run_id,
            ts_ms=now_epoch_ms(),
            stage=stage,
            ok=bool(ai.ok),
            summary=("ai_ok" if ai.ok else "ai_fail"),
            data={
                "task_text": task_text,
                "cycle_index": cycle_index,
                "ai_provider": ai.provider,
                "ai_model": ai.model,
                "ai_text": ai.text,
            },
            error=(None if ai.ok else {"message": ai.error}),
        )

        return write_outbox(event)

    except Exception as e:
        event = OutboxEvent(
            schema="mocka.outbox.v1",
            run_id=run_id,
            ts_ms=now_epoch_ms(),
            stage=stage,
            ok=False,
            summary="exception",
            data={
                "task_text": task_text,
                "cycle_index": cycle_index,
            },
            error={"message": str(e)},
        )
        return write_outbox(event)
