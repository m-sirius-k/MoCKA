# -*- coding: utf-8 -*-
# Perplexity Connector (TODO_269)
# Role: PerplexityからMoCKAへのイベント記録アダプター
# PerplexityはWeb検索特化AI。検索結果・調査報告をMoCKAに記録する。

import uuid
import hashlib
import hmac
import os
from datetime import datetime, timezone

import requests

# STEP 5: HAB COMMON CORE / AI SOCKET Bridge
try:
    from adapters_perplexity_socket import PerplexitySocket
    HAB_BRIDGE_AVAILABLE = True
    _perplexity_socket = PerplexitySocket()
except ImportError:
    HAB_BRIDGE_AVAILABLE = False
    _perplexity_socket = None

GATEWAY_BASE  = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
HMAC_SECRET   = os.environ.get("MOCKA_HMAC_SECRET", "").encode()


# ---- Function Callingスキーマ（Perplexity向け） ---------------------------

FUNCTION_SCHEMA = {
    "name": "mocka_record_event",
    "description": (
        "MoCKAシステムにイベントを記録する。"
        "Web調査結果・ソース収集・一次情報レポートなどを記録すること。"
        "evidence フィールドに参照URLまたは情報源を含めること。"
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
                "description": "調査内容の詳細（5W1H + 情報源）",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "タグリスト（例: [\"Perplexity\", \"web_search\", \"調査\"]）",
            },
            "evidence": {
                "type": "string",
                "description": "参照URL・情報源リスト（改行区切り）",
            },
        },
        "required": ["title", "description"],
    },
}


# ---- Function Call 実行ハンドラ -------------------------------------------

def handle_function_call(title: str, description: str, tags: list = None,
                         evidence: str = "",
                         model: str = "sonar-pro",
                         source: str = "Orchestra") -> dict:
    """
    PerplexityからのFunction Call引数を受け取り、/api/v1/event にPOSTする。
    """
    tags = tags or []
    now   = datetime.now(timezone.utc).isoformat()
    nonce = uuid.uuid4().hex[:16]
    rid   = str(uuid.uuid4())

    full_description = description
    if evidence:
        full_description += f"\n\n[Evidence]\n{evidence[:500]}"

    payload = {
        "title":       title,
        "description": full_description,
        "tags":        tags,
        "actor": {
            "vendor":  "Perplexity AI",
            "model":   model,
            "runtime": "Perplexity",
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

        # STEP 5: Try HAB Bridge via Perplexity Socket if available
        if HAB_BRIDGE_AVAILABLE and _perplexity_socket:
            try:
                bridge_result = _perplexity_socket.submit(model, payload['actor']['runtime'], title, description, tags)
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


def call_api(request_text: str, model: str = "sonar-pro") -> dict:
    """
    Call Perplexity API directly.
    Outbound: HAB → Socket → Adapter → Perplexity API.

    Args:
        request_text: Text to send to Perplexity
        model: Perplexity model identifier

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
        import anthropic as pplx
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "error": "PERPLEXITY_API_KEY not set",
                "model": model,
            }

        client = pplx.Anthropic(api_key=api_key, base_url="https://api.perplexity.ai")
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
                "prompt_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Perplexity API error: {str(e)}",
            "model": model,
        }


def _sign(data: dict) -> str:
    keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload = "&".join(f"{k}={data.get(k,'')}" for k in sorted(keys))
    return "sha256:" + hmac.new(HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()


# ---- Perplexityへ渡すSystem Promptスニペット ------------------------------

def get_system_prompt_snippet() -> str:
    return (
        "あなたはMoCKAシステムと連携しています。"
        "Web調査・情報収集・一次ソース確認を行った際は必ずmocka_record_event関数を呼び出して記録してください。"
        "evidenceフィールドに参照URLや情報源を含めることでMoCKA知識の信頼性が高まります。"
        "記録なき調査はMoCKAとして存在しません。"
    )
