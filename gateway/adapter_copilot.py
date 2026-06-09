# -*- coding: utf-8 -*-
# Copilot / Power Automate 向けアダプター
# OpenAPI定義に基づくレスポンス変換とCopilot Studio Custom Connector用ヘルパー。

import os
import requests
from datetime import datetime, timezone

GATEWAY_BASE  = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()


# ---- Copilot向け GET /api/v1/context ラッパー ----------------------------

def get_context_for_copilot(mode: str = "standard") -> dict:
    """
    Copilot Studio Custom Connector から呼ばれる。
    /api/v1/context を取得してPower Automate向けにフラット化して返す。
    """
    try:
        r = requests.get(
            f"{GATEWAY_BASE}/api/v1/context",
            params={"mode": mode},
            headers={"X-MoCKA-Key": MOCKA_API_KEY},
            timeout=5,
        )
        r.raise_for_status()
        ctx = r.json()

        # Power Automate は深いネストを扱いにくいのでフラット化
        return {
            "phase":         ctx.get("phase", ""),
            "goal":          ctx.get("goal", ""),
            "last_decision": ctx.get("last_decision", ""),
            "mode":          ctx.get("meta", {}).get("mode", mode),
            "generated_at":  ctx.get("meta", {}).get("generated_at", ""),
            "active_todo_count": len(ctx.get("active_todo", [])),
            "top_todo_title":    ctx.get("active_todo", [{}])[0].get("title", "")
                                 if ctx.get("active_todo") else "",
            "top_todo_priority": ctx.get("active_todo", [{}])[0].get("priority", "")
                                 if ctx.get("active_todo") else "",
        }
    except Exception as e:
        return {"error": str(e)}


# ---- Copilot向け POST /api/v1/event ラッパー -----------------------------

def post_event_from_copilot(title: str, description: str,
                             tags: str = "", source: str = "PowerAutomate") -> dict:
    """
    Power Automate HTTP アクションから呼ばれる想定。
    tags は "タグ1,タグ2" 形式の文字列で受け取る。
    """
    payload = {
        "title":       title,
        "description": description,
        "tags":        [t.strip() for t in tags.split(",") if t.strip()],
        "actor": {
            "vendor":  "Microsoft",
            "model":   "Copilot",
            "runtime": "CopilotStudio",
            "source":  source,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nonce":     os.urandom(8).hex(),
        "request_id": __import__("uuid").uuid4().hex,
    }
    try:
        r = requests.post(
            f"{GATEWAY_BASE}/api/v1/event",
            json=payload,
            headers={"X-MoCKA-Key": MOCKA_API_KEY, "Content-Type": "application/json"},
            timeout=5,
        )
        r.raise_for_status()
        return {"status": "ok", "event_id": r.json().get("event_id")}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
