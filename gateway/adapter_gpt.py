# -*- coding: utf-8 -*-
# GPT Function Calling インターセプター
# GPTがFunction Callingで呼び出す想定のエンドポイント定義と
# POST /api/v1/event への橋渡しを担う。

import uuid
import time
import hashlib
import hmac
import os
from datetime import datetime, timezone

import requests

GATEWAY_BASE    = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY   = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
HMAC_SECRET     = os.environ.get("MOCKA_HMAC_SECRET", "").encode()


# ---- Function Calling スキーマ定義（GPT向け） ----------------------------
# GPTのsystem promptまたはtools配列に埋め込む定義

FUNCTION_SCHEMA = {
    "name": "mocka_record_event",
    "description": (
        "MoCKAシステムにイベントを記録する。"
        "合議回答・設計判断・ファイル変更・外部サービス操作などを記録すること。"
    ),
    "parameters": {
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
                "description": "タグリスト（例: [\"GPT\", \"合議\", \"設計\"]）",
            },
        },
        "required": ["title", "description"],
    },
}


# ---- Function Call実行ハンドラ -------------------------------------------

def handle_function_call(title: str, description: str, tags: list = None,
                         model: str = "GPT", runtime: str = "ChatGPT",
                         source: str = "Orchestra") -> dict:
    """
    GPTからのFunction Call引数を受け取り、/api/v1/event にPOSTする。
    戻り値はGPTのfunction_call responseとして返す文字列。
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
            "vendor":  "OpenAI",
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
        return {"status": "ok", "event_id": r.json().get("event_id")}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _sign(data: dict) -> str:
    keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload = "&".join(f"{k}={data.get(k,'')}" for k in sorted(keys))
    return "sha256:" + hmac.new(HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()


# ---- GPTへ渡すSystem Promptスニペット -----------------------------------

def get_system_prompt_snippet() -> str:
    return (
        "あなたはMoCKAシステムと連携しています。"
        "重要な判断・回答・変更を行った際は必ずmocka_record_event関数を呼び出して記録してください。"
        "記録なき作業はMoCKAとして存在しません。"
    )
