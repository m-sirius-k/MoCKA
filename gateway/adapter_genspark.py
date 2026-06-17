# -*- coding: utf-8 -*-
# Genspark Connector (TODO_270)
# Role: GensparkからMoCKAへのイベント記録アダプター
# GensparkはレポートAI。比較・情報整理・スライド生成結果をMoCKAに記録する。
# trust_level: Trial（本番使用前に動作検証が必要）

import uuid
import hashlib
import hmac
import os
from datetime import datetime, timezone

import requests

GATEWAY_BASE  = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
HMAC_SECRET   = os.environ.get("MOCKA_HMAC_SECRET", "").encode()

# Genspark は Trial trust_level — イベント記録時に明示する
TRUST_LEVEL = "Trial"


# ---- Function Callingスキーマ（Genspark向け） -----------------------------

FUNCTION_SCHEMA = {
    "name": "mocka_record_event",
    "description": (
        "MoCKAシステムにイベントを記録する。"
        "レポート作成・比較分析・情報整理の結果をMoCKAに記録すること。"
        "output_format に出力形式（report/comparison/slide等）を指定すること。"
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
                "description": "レポート内容の要約（5W1H含む）",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "タグリスト（例: [\"Genspark\", \"report\", \"比較\"]）",
            },
            "output_format": {
                "type": "string",
                "enum": ["report", "comparison", "slide", "summary", "other"],
                "description": "出力形式",
            },
        },
        "required": ["title", "description"],
    },
}


# ---- Function Call 実行ハンドラ -------------------------------------------

def handle_function_call(title: str, description: str, tags: list = None,
                         output_format: str = "report",
                         model: str = "genspark-default",
                         source: str = "Orchestra") -> dict:
    """
    GensparkからのFunction Call引数を受け取り、/api/v1/event にPOSTする。
    Trialステータスのためタグに trust:Trial を自動付加する。
    """
    tags = list(tags or [])
    if "trust:Trial" not in tags:
        tags.append("trust:Trial")

    now   = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex[:16]
    rid   = str(uuid.uuid4())

    full_description = description
    if output_format and output_format != "report":
        full_description = f"[output_format={output_format}] " + full_description

    payload = {
        "title":       title,
        "description": full_description,
        "tags":        tags,
        "actor": {
            "vendor":      "Genspark",
            "model":       model,
            "runtime":     "Genspark",
            "source":      source,
            "trust_level": TRUST_LEVEL,
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
        return {"status": "ok", "event_id": r.json().get("event_id"), "trust_level": TRUST_LEVEL}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def _sign(data: dict) -> str:
    keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload_str = "&".join(f"{k}={data.get(k,'')}" for k in sorted(keys))
    return "sha256:" + hmac.new(HMAC_SECRET, payload_str.encode(), hashlib.sha256).hexdigest()


# ---- Gensparkへ渡すSystem Promptスニペット ---------------------------------

def get_system_prompt_snippet() -> str:
    return (
        "あなたはMoCKAシステムと連携しています（試験運用中 = trust:Trial）。"
        "レポート・比較・情報整理を完了した際は必ずmocka_record_event関数を呼び出して記録してください。"
        "output_formatフィールドに出力形式を指定してください。"
        "記録なき作業はMoCKAとして存在しません。"
    )
