# -*- coding: utf-8 -*-
# GPT Function Calling インターセプター
# GPTがFunction Callingで呼び出す想定のエンドポイント定義と
# POST /api/v1/event / GET /api/v1/context への橋渡しを担う。
# Sprint2(Reconnection Sprint, TODO: ChatGPT Read経路復活): ReadContext()追加。
# 対象はadapter_gpt.pyのみ。gateway.py/context_builder.pyは変更しない。

import re
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

# MOCKA_API_KEYS未設定(空集合)の間は、gateway側のVALID_KEYSも空集合となり
# 非空の値であれば何でも通過する(gateway/auth.py:47参照)。
# 本番運用でAPIキーが正式発行された場合は自動的にそちらが使われる。
_AUTH_HEADER_KEY = MOCKA_API_KEY or "unset-local-dev-key"


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


# ---- Function Calling スキーマ定義（GPT向け・読取） ------------------------
# AI_BOOT_HUB.md Boot Procedureに準拠。current_caseは保存せず、
# active_todo(優先度順で先頭)から毎回その場で導出する(起動毎導出、非保存)。

READ_CONTEXT_FUNCTION_SCHEMA = {
    "name": "mocka_read_context",
    "description": (
        "MoCKAの現在状態(現在フェーズ・目的・TODO・Essence・直近イベント・"
        "現在扱う案件)を取得する。ChatGPTセッション開始時、AI_BOOT_HUB.mdの"
        "Boot Procedureに沿って、禁止事項確認の後にまず呼び出すこと。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["compact", "standard", "extended"],
                "description": "compact(~2KB)/standard(~8KB)/extended(~50KB)。省略時はstandard。",
            },
        },
        "required": [],
    },
}


# ---- Function Call実行ハンドラ（読取） -------------------------------------

def handle_read_context(mode: str = "standard") -> dict:
    """
    GETでGATEWAY_BASE/api/v1/contextを呼び出し、OVERVIEW/TODO/Essence/直近イベントを
    まとめて取得する。current_caseはcontext自体には含まれないため、ここで
    active_todoの先頭(優先度順、gateway/context_builder.pyが既に並べ替え済み)から
    その場で導出する(保存はしない)。
    """
    try:
        r = requests.get(
            f"{GATEWAY_BASE}/api/v1/context",
            params={"mode": mode},
            headers={"X-MoCKA-Key": _AUTH_HEADER_KEY},
            timeout=10,
        )
        r.raise_for_status()
        ctx = r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    active_todo   = ctx.get("active_todo", []) or []
    recent_events = ctx.get("recent_events", []) or []
    current_case, current_case_source = _derive_current_case(active_todo, recent_events)

    return {
        "status":              "ok",
        "phase":               ctx.get("phase", ""),
        "goal":                ctx.get("goal", ""),
        "current_case":        current_case,
        "current_case_source": current_case_source,
        "active_todo":         active_todo,
        "essence_summary":     ctx.get("essence_summary", ""),
        "recent_events":       recent_events,
        "last_decision":       ctx.get("last_decision", ""),
        "meta":                ctx.get("meta", {}),
    }


_DECISION_ID_RE = re.compile(r"DC_\d{8}_\d{3}")


def _session_relevant_events(recent_events: list) -> list:
    """直近イベントのうち、この対話のセッションに属するとみなせるものだけに絞り込む。

    (a) 先頭(最新)イベントのsession_idを「現在のセッション」の参照値とみなし、
        同じsession_idを持つイベントに絞り込む(完全一致)。
        注意: gateway/context_builder.py の _load_events() は現状SELECT文で
        session_id列を選択していないため、contextのrecent_eventsにはsession_idが
        含まれない。よってこの分岐は今回は常にデータ無しでスキップされる
        (Gateway側が将来session_idを返すようになれば自動的に有効化される設計として残す)。
    (b) session_idが取得できない場合のフォールバックとして、
        decision_id(DC_YYYYMMDD_NNN)パターンをtitle/short_summaryに含む
        イベントに絞り込む。
    """
    if not recent_events:
        return []

    ref_session = recent_events[0].get("session_id")
    if ref_session:
        return [e for e in recent_events if e.get("session_id") == ref_session]

    return [
        e for e in recent_events
        if _DECISION_ID_RE.search(f"{e.get('title', '')} {e.get('short_summary', '')}")
    ]


def _match_todo_in_events(active_todo: list, events: list):
    haystack = " ".join(
        f"{e.get('title', '')} {e.get('short_summary', '')}" for e in events
    ).lower()
    matched = [t for t in active_todo if t.get("id") and t["id"].lower() in haystack]
    return matched[0] if matched else None


def _format_case(todo: dict) -> str:
    return f"{todo.get('id', '')}: {todo.get('title', '')} (priority={todo.get('priority', '')})"


def _derive_current_case(active_todo: list, recent_events: list):
    """current_caseの導出(3層、優先順位順)。

    層1(session_relevant_events): このセッション/直近の裁定関連イベントに
        言及されているTODOを最優先する。
    層2(recent_activity_match): 層1で一致が無い場合、recent_events全体
        (セッション絞り込み無し)の中で言及されているTODOを使う。
    層3(priority_fallback): 層1・層2いずれも一致が無い場合、従来通り
        優先度先頭を使う。

    戻り値: (current_case: str|None,
             current_case_source: "session_relevant_events"|"recent_activity_match"|"priority_fallback"|None)
    """
    if not active_todo:
        return None, None

    session_events = _session_relevant_events(recent_events)
    top = _match_todo_in_events(active_todo, session_events)
    if top:
        return _format_case(top), "session_relevant_events"

    top = _match_todo_in_events(active_todo, recent_events)
    if top:
        return _format_case(top), "recent_activity_match"

    top = active_todo[0]
    return _format_case(top), "priority_fallback"


# ---- GPTへ渡すSystem Promptスニペット -----------------------------------

def get_system_prompt_snippet() -> str:
    return (
        "あなたはMoCKAシステムと連携しています。"
        "セッション開始時は、まず.claude/CLAUDE.mdおよびdocs/governance/GPT_RESTRICTIONS.mdの"
        "禁止事項を確認したうえで、mocka_read_context関数を呼び出し、"
        "現在フェーズ・目的・TODO・現在扱う案件(current_case)を復元してから作業を開始してください。"
        "重要な判断・回答・変更を行った際は必ずmocka_record_event関数を呼び出して記録してください。"
        "記録なき作業はMoCKAとして存在しません。"
    )
