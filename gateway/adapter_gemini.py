# -*- coding: utf-8 -*-
# Gemini Function Calling インターセプター（Google形式）
# Gemini API の functionDeclarations 形式に対応。

import uuid
import hashlib
import hmac
import os
from datetime import datetime, timezone

import requests

GATEWAY_BASE  = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
HMAC_SECRET   = os.environ.get("MOCKA_HMAC_SECRET", "").encode()


# ---- Gemini functionDeclarations スキーマ ---------------------------------
# Gemini API の tools[].function_declarations[] に埋め込む形式

FUNCTION_DECLARATION = {
    "name": "mocka_record_event",
    "description": (
        "MoCKAシステムにイベントを記録する。"
        "合議回答・設計判断・ファイル変更・外部サービス操作などを記録すること。"
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "title": {
                "type": "STRING",
                "description": "イベントタイトル（50文字以内）",
            },
            "description": {
                "type": "STRING",
                "description": "詳細説明（5W1H含む）",
            },
            "tags": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "タグリスト",
            },
        },
        "required": ["title", "description"],
    },
}

# Gemini API に渡す tools 配列
GEMINI_TOOLS = [{"function_declarations": [FUNCTION_DECLARATION]}]


# ---- Function Call実行ハンドラ -------------------------------------------

def handle_function_call(title: str, description: str, tags: list = None,
                         model: str = "gemini-2.0-flash",
                         runtime: str = "Gemini", source: str = "Orchestra") -> dict:
    """
    GeminiからのfunctionCall引数を受け取り /api/v1/event にPOSTする。
    戻り値はfunctionResponse.responseとして返す。
    """
    tags = tags or []
    now   = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex[:16]
    rid   = str(uuid.uuid4())

    payload = {
        "title":       title,
        "description": description,
        "tags":        tags,
        "actor": {
            "vendor":  "Google",
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
        r = requests.post(
            f"{GATEWAY_BASE}/api/v1/event",
            json=payload,
            headers={"X-MoCKA-Key": MOCKA_API_KEY, "Content-Type": "application/json"},
            timeout=5,
        )
        r.raise_for_status()
        result = {"status": "ok", "event_id": r.json().get("event_id")}
    except Exception as e:
        result = {"status": "error", "detail": str(e)}

    # Gemini functionResponse 形式で返す
    return {
        "functionResponse": {
            "name": "mocka_record_event",
            "response": result,
        }
    }


def _sign(data: dict) -> str:
    keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload = "&".join(f"{k}={data.get(k,'')}" for k in sorted(keys))
    return "sha256:" + hmac.new(HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()
