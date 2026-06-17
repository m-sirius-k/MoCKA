#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestra Context Bridge (TODO_258)

MoCKAのコンテキスト情報をOrchestra合議プロンプト先頭に自動注入する。
情報格差解消: GPT/Gemini/Perplexity/Copilotが同一のMoCKA文脈を持った状態で回答できる。

動作フロー:
  1. Gateway API (localhost:5010/api/v1/context) からMoCKAコンテキストを取得
  2. コンテキストを構造化テキストに変換
  3. 元のプロンプト先頭に付加して返す

フォールバック:
  Gatewayが起動していない場合は元のプロンプトをそのまま返す（Orchestraをブロックしない）。

使用方法:
  from orchestra_context_bridge import inject_context
  enriched_prompt = inject_context(original_prompt)
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# MoCKA Gateway API設定
GATEWAY_BASE    = os.environ.get("MOCKA_GATEWAY_URL", "http://localhost:5010")
MOCKA_API_KEY   = os.environ.get("MOCKA_API_KEYS", "").split(",")[0].strip()
_CONTEXT_URL    = f"{GATEWAY_BASE}/api/v1/context"
_TIMEOUT_SEC    = 5


def _fetch_mocka_context(mode: str = "compact") -> Optional[dict]:
    """
    Gateway API からMoCKAコンテキストを取得する。
    失敗時は None を返す（呼び出し元がフォールバック処理）。
    """
    if not _REQUESTS_AVAILABLE:
        return None

    headers = {}
    if MOCKA_API_KEY:
        headers["X-MoCKA-Key"] = MOCKA_API_KEY

    try:
        resp = _requests.get(
            _CONTEXT_URL,
            params={"mode": mode},
            headers=headers,
            timeout=_TIMEOUT_SEC,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _build_context_header(ctx: dict) -> str:
    """
    Gateway APIレスポンスをOrchestra向けのコンテキストヘッダーに変換する。
    AIが即座に文脈を把握できる構造化テキストを生成する。
    """
    lines = [
        "## [MoCKA Context] この質問に回答する前に必ず読むこと",
        "",
        f"**現在フェーズ**: {ctx.get('phase', '(不明)')}",
        f"**最優先目標**: {ctx.get('goal', '(不明)')}",
        f"**最終決定**: {ctx.get('last_decision', '(なし)')}",
        "",
    ]

    # アクティブTODO（上位5件）
    active_todo = ctx.get("active_todo", [])
    if active_todo:
        lines.append("**アクティブTODO（上位）**:")
        for t in active_todo[:5]:
            pri = t.get("priority", "")
            tid = t.get("id", "")
            ttl = t.get("title", "")
            lines.append(f"  - [{pri}] {tid}: {ttl}")
        lines.append("")

    # Essence（本質サマリー）
    essence = ctx.get("essence_summary", "")
    if essence:
        lines.append(f"**MoCKA本質**: {essence[:200]}")
        lines.append("")

    # 直近イベント（最新3件）
    recent = ctx.get("recent_events", [])
    if recent:
        lines.append("**直近イベント**:")
        for ev in recent[:3]:
            ev_title = ev.get("title", "")
            ev_when  = ev.get("when", "")[:10]
            lines.append(f"  - ({ev_when}) {ev_title}")
        lines.append("")

    lines += [
        "---",
        "上記はMoCKAシステムの現在状態です。この文脈を踏まえて以下の質問に回答してください。",
        "",
    ]
    return "\n".join(lines)


def inject_context(prompt: str, mode: str = "compact",
                   verbose: bool = True) -> str:
    """
    プロンプト先頭にMoCKAコンテキストを注入して返す。

    Args:
        prompt:  元のOrchestra質問プロンプト
        mode:    "compact" | "standard" | "extended"（Gatewayモード）
        verbose: True のとき注入結果をターミナルに表示

    Returns:
        コンテキスト付きプロンプト（Gateway未起動時は元のプロンプトをそのまま返す）
    """
    ctx = _fetch_mocka_context(mode)

    if ctx is None:
        if verbose:
            print("[Orchestra Bridge] Gateway未接続 — コンテキスト注入をスキップ（フォールバック）")
        return prompt

    header = _build_context_header(ctx)
    enriched = header + prompt

    if verbose:
        phase = ctx.get("phase", "(不明)")[:60]
        print(f"[Orchestra Bridge] MoCKAコンテキスト注入完了: {phase}")

    return enriched


def build_standalone_context(mode: str = "standard") -> str:
    """
    プロンプトなしでコンテキストヘッダーのみを返す（デバッグ・確認用）。
    """
    ctx = _fetch_mocka_context(mode)
    if ctx is None:
        return "[Orchestra Bridge] Gateway未接続"
    return _build_context_header(ctx)


if __name__ == "__main__":
    sample_prompt = "MoCKAのTODO管理で次に優先すべきアクションを提案してください。"

    print("=== inject_context() テスト ===")
    result = inject_context(sample_prompt, mode="compact")
    print(result[:600])
    print(f"\n[合計文字数] {len(result)}")
