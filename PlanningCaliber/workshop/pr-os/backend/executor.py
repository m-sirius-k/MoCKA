"""
executor.py — PR-OS唯一の実行層
実行は必ずホワイトリスト経由。
任意コマンド実行・shell直渡し禁止。
"""

import sys
import os
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from events import write

# ホワイトリスト（これ以外は実行禁止）
ALLOWED_ACTIONS = {"evaluate", "submit", "publish", "sync"}


def run(action: str, payload: dict = None) -> dict:
    """
    アクションを安全に実行する。
    成功・失敗どちらもeventに記録して返す。
    """
    payload = payload or {}

    if action not in ALLOWED_ACTIONS:
        event = write(
            action=action,
            status="failed",
            error=f"Action '{action}' is not in whitelist: {ALLOWED_ACTIONS}",
        )
        return event

    # 実行中イベントを先に記録
    write(action=action, status="running")

    try:
        result = _dispatch(action, payload)
        event = write(action=action, status="success", result=result)
        return event

    except Exception as e:
        event = write(
            action=action,
            status="failed",
            error=str(e),
        )
        return event


def _dispatch(action: str, payload: dict) -> dict:
    """アクション別の実処理。"""

    if action == "evaluate":
        return _evaluate(payload)
    elif action == "submit":
        return _submit(payload)
    elif action == "publish":
        return _publish(payload)
    elif action == "sync":
        return _sync(payload)
    else:
        raise ValueError(f"Unknown action: {action}")


def _evaluate(payload: dict) -> dict:
    """Semantic Score評価。"""
    from semantic_scorer import score_content
    title = payload.get("title", "")
    body = payload.get("body", "")
    if not title or not body:
        raise ValueError("title and body are required")
    sv = score_content(title, body)
    return sv.to_dict()


def _submit(payload: dict) -> dict:
    """KSストアへの投入。"""
    title = payload.get("title", "")
    if not title:
        raise ValueError("title is required")
    import time
    ks_id = f"KS_{int(time.time())}"
    return {"ks_id": ks_id, "title": title, "status": "queued"}


def _publish(payload: dict) -> dict:
    """WordPress等への配信。"""
    ks_id = payload.get("ks_id", "")
    adapter = payload.get("adapter", "wordpress")
    if not ks_id:
        raise ValueError("ks_id is required")
    # TODO: 実際のadapter呼び出しはWordPress認証設定後に実装
    return {"ks_id": ks_id, "adapter": adapter, "status": "queued"}


def _sync(payload: dict) -> dict:
    """MoCKA events.dbとの同期。"""
    return {"status": "sync_completed", "synced": 0}
