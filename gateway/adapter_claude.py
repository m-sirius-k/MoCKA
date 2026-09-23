# -*- coding: utf-8 -*-
# Claude Function Calling インターセプター
# Claude API の tool_use 形式に対応。

import re
import uuid
import time
import hashlib
import hmac
import os
from datetime import datetime, timezone

import requests

# STEP 4: HAB COMMON CORE / AI SOCKET Bridge
try:
    from adapters_claude_socket import ClaudeSocket
    HAB_BRIDGE_AVAILABLE = True
    _claude_socket = ClaudeSocket()
except ImportError:
    HAB_BRIDGE_AVAILABLE = False
    _claude_socket = None

GATEWAY_BASE    = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY   = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
HMAC_SECRET     = os.environ.get("MOCKA_HMAC_SECRET", "").encode()

_AUTH_HEADER_KEY = MOCKA_API_KEY or "unset-local-dev-key"


# ---- Claude Tool スキーマ定義 --------------------------------------------
# Claude API の tools 配列に埋め込む定義

TOOL_DEFINITION = {
    "name": "mocka_record_event",
    "description": (
        "MoCKAシステムにイベントを記録する。"
        "合議回答・設計判断・ファイル変更・外部サービス操作などを記録すること。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "イベントタイトル（50文字以内）",
            },
            "description": {
                "type": "string",
                "description": "詳細説明（5W1H含む）",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "タグリスト（例: [\"Claude\", \"合議\", \"設計\"]）",
            },
        },
        "required": ["title", "description"],
    },
}


# ---- Tool Call実行ハンドラ -------------------------------------------

def handle_tool_call(title: str, description: str, tags: list = None,
                     model: str = "claude-opus-5", runtime: str = "Claude",
                     source: str = "Orchestra") -> dict:
    """
    ClaudeからのtoolUse引数を受け取り、/api/v1/event にPOSTする。
    戻り値は tool_result として返す。
    """
    tags = tags or []
    now  = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex[:16]
    rid   = str(uuid.uuid4())

    payload = {
        "title":       title,
        "description": description,
        "tags":        tags,
        "actor": {
            "vendor":  "Anthropic",
            "model":   model,
            "runtime": runtime,
            "source":  source,
        },
        "request_id": rid,
        "timestamp":  now,
        "nonce":      nonce,
    }

    if HMAC_SECRET:
        payload["hmac_sig"] = _sign(payload)

    try:
        result = {"status": "ok"}

        # STEP 4: Try HAB Bridge via Claude Socket if available
        if HAB_BRIDGE_AVAILABLE and _claude_socket:
            try:
                bridge_result = _claude_socket.submit(model, runtime, title, description, tags)
                if bridge_result.get("status") == "ok":
                    result["hab_request_id"] = bridge_result.get("request_id")
                    result["hab_state"] = bridge_result.get("state")
                    result["hab_decision_id"] = bridge_result.get("decision_id")
            except Exception as hab_err:
                result["hab_error"] = str(hab_err)

        # Original: POST /api/v1/event (kept for compatibility)
        r = requests.post(
            f"{GATEWAY_BASE}/api/v1/event",
            json=payload,
            headers={"X-MoCKA-Key": MOCKA_API_KEY, "Content-Type": "application/json"},
            timeout=5,
        )
        r.raise_for_status()
        result["event_id"] = r.json().get("event_id")
        return result
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _sign(data: dict) -> str:
    keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload = "&".join(f"{k}={data.get(k,'')}" for k in sorted(keys))
    return "sha256:" + hmac.new(HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()


# ---- System Prompt スニペット -------------------------------------------

def call_api(request_text: str, model: str = "claude-opus-5") -> dict:
    """
    Call Claude API directly.
    Outbound: HAB → Socket → Adapter → Claude API.

    Args:
        request_text: Text to send to Claude
        model: Claude model identifier

    Returns:
        {
            "status": "ok" | "error",
            "response": str (if ok),
            "model": str,
            "usage": dict (if ok),
            "error": str (if error),
        }
    """
    try:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "error": "ANTHROPIC_API_KEY not set",
                "model": model,
            }

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": request_text}]
        )

        response_text = response.content[0].text
        return {
            "status": "ok",
            "response": response_text,
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Claude API error: {str(e)}",
            "model": model,
        }


def get_system_prompt_snippet() -> str:
    return (
        "あなたはMoCKAシステムと連携しています。"
        "重要な判断・回答・変更を行った際は必ずmocka_record_event toolを呼び出して記録してください。"
        "記録なき作業はMoCKAとして存在しません。"
    )
