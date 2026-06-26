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


# ============================================================
# Phase5-1.5 Schema Integrity Hardening
# events._source列のCHECK制約・Schema Auditが参照する単一の真実。
# SQLite・Python(tag_source)・このリストの3者は常に完全一致させること。
# ============================================================

# Gate確立後（2026-06-16以降）に新規書き込みされ得る値
GATE_SOURCE_VALUES = frozenset(
    {"live", "buffered", "direct_violation"}
    | {f"direct_allowed:{ch}" for ch in ALLOWED_DIRECT_CHANNELS}
)

# Gate確立以前の歴史的バックログ専用ラベル（凍結済み・新規書き込み禁止）。
# data/mocka_events.db移行時(2026-06-16)に実在が確認された値のみを列挙する。
LEGACY_SOURCE_VALUES = frozenset({
    "legacy",
    "csv_legacy",
    "csv_migration",
    "new",
    "gpt_handoff_20260509",
    "caliber_server",
})

# CHECK制約・Schema Auditが許可する_source全許可値
ALLOWED_SOURCE_VALUES = frozenset(GATE_SOURCE_VALUES | LEGACY_SOURCE_VALUES)


def is_allowed_source_value(value: str) -> bool:
    """events._source列の値がGate Policyと一致する許可値かどうかを判定する"""
    return value in ALLOWED_SOURCE_VALUES


# ============================================================
# TODO_347-c: Gate Audit共通ロジック（単一の正規参照元）
# dashboard.py / phi_os/event_gate.py(/api/gate/audit本体) / health_check.py の
# 3箇所で重複実装されていたviolation集計ロジックをここに統一する。
# ============================================================

import re as _re

_ISO8601_RE = _re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def is_iso8601_when_ts(value) -> bool:
    """when_ts値がISO8601として解釈可能かを判定する。
    解釈不能な値（"pipeline"等の文字列リテラル、N/A、16進ハッシュ、
    "YYYYMMDD_N"型の旧式断片等）はFalseを返す。"""
    if not value:
        return False
    return bool(_ISO8601_RE.match(str(value)))


def compute_gate_audit(conn, gate_launch_date: str) -> dict:
    """
    Gate監査の正規集計ロジック（TODO_347-c）。
    判定順序:
      1) _source in LEGACY_SOURCE_VALUES の行は集計対象外（凍結済み歴史的バックログ）
      2) 残りの行のうち is_iso8601_when_ts(when_ts) が False の行は
         timestamp_unparseable_events に加算し、live/buffered/violationの
         いずれにも含めない（文字列比較が信頼できないため、日付窓判定の対象外とする）
      3) 残った行をwhen_ts >= gate_launch_dateで絞り込み、
         real_time(live)/buffered/allowed_direct/violationに分類する
    legacy_events は既存仕様(when_ts < gate_launch_date、_source無関係)を維持する。
    """
    conn.create_function(
        "IS_ISO8601_WHEN_TS", 1, lambda v: 1 if is_iso8601_when_ts(v) else 0
    )
    legacy_ph = ",".join("?" for _ in LEGACY_SOURCE_VALUES)
    legacy_vals = tuple(LEGACY_SOURCE_VALUES)

    def _count(where_sql, params):
        return conn.execute(f"SELECT COUNT(*) FROM events WHERE {where_sql}", params).fetchone()[0]

    total = _count(
        f"_source NOT IN ({legacy_ph}) AND IS_ISO8601_WHEN_TS(when_ts)=1 AND when_ts >= ?",
        (*legacy_vals, gate_launch_date),
    )
    live = _count(
        "_source='live' AND IS_ISO8601_WHEN_TS(when_ts)=1 AND when_ts >= ?",
        (gate_launch_date,),
    )
    buffered = _count(
        "_source='buffered' AND IS_ISO8601_WHEN_TS(when_ts)=1 AND when_ts >= ?",
        (gate_launch_date,),
    )
    allowed_direct = _count(
        "_source LIKE 'direct_allowed:%' AND IS_ISO8601_WHEN_TS(when_ts)=1 AND when_ts >= ?",
        (gate_launch_date,),
    )
    timestamp_unparseable = _count(
        f"_source NOT IN ({legacy_ph}) AND IS_ISO8601_WHEN_TS(when_ts)=0",
        legacy_vals,
    )
    legacy_events = _count("when_ts < ?", (gate_launch_date,))

    gate_routed = live + buffered
    violation = max(total - gate_routed - allowed_direct, 0)
    rate = round(gate_routed / total * 100, 2) if total else 0.0

    return {
        "real_time_events": live,
        "buffered_events": buffered,
        "allowed_direct_events": allowed_direct,
        "legacy_events": legacy_events,
        "violation_events": violation,
        "timestamp_unparseable_events": timestamp_unparseable,
        "gate_passthrough_rate_percent": rate,
    }
