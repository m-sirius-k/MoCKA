#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_policy.py -- PHI-OS Event Gate Policy (Phase5-1 Gate Enforcement)

通常イベントは必ずGateを経由する、という制度を実装するための許可基準。
Gateを通さないDirect Writeは、ここで定義されたチャネル以外は禁止とする。
許可理由が存在しないDirect Writeは「制度違反」として監査対象になる。
"""

POLICY_VERSION = "1.0"

# 許可されたDirect Writeチャネル: {channel: reason}
ALLOWED_DIRECT_CHANNELS = {
    "bootstrap":   "初回起動時、Gateサーバー自体が未起動のため直接書き込みが必要",
    "maintenance": "保守作業による一括修正・補正記録（人間ゲート承認前提）",
    "migration":   "CSV→SQLite等のデータ移行時の一括取り込み（一度限り）",
    "restore":     "バックアップ・障害復旧時のリストア処理",
    "recovery":    "Gate未応答時のfallback書き込み（ネットワーク/プロセス障害からの自己復旧）",
}

# 明示的に禁止するチャネル名（許可リストに追加されることを防ぐガード）
FORBIDDEN_CHANNELS = frozenset({"normal", "default", "unspecified", ""})

AUDIT_FLAG_EXEMPT = "exempt"        # 許可Direct Write — 監査上は違反としない
AUDIT_FLAG_VIOLATION = "violation"  # 許可リスト外のDirect Write — 制度違反


def is_allowed_direct_channel(channel: str) -> bool:
    """channelが許可されたDirect Writeチャネルかどうかを判定する"""
    if not channel or channel in FORBIDDEN_CHANNELS:
        return False
    return channel in ALLOWED_DIRECT_CHANNELS


def classify_direct_write(channel: str) -> str:
    """Direct Writeのaudit_flagを返す（exempt or violation）"""
    return AUDIT_FLAG_EXEMPT if is_allowed_direct_channel(channel) else AUDIT_FLAG_VIOLATION


def direct_write_reason(channel: str) -> str:
    """許可チャネルの理由文字列を返す（未許可の場合は空文字）"""
    return ALLOWED_DIRECT_CHANNELS.get(channel, "")


def tag_source(channel: str) -> str:
    """
    db_helper.write_event()等が_source列に書き込むべき値を返す。
    許可チャネル -> 'direct_allowed:{channel}'
    未許可       -> 'direct_violation'
    """
    if is_allowed_direct_channel(channel):
        return f"direct_allowed:{channel}"
    return "direct_violation"
