# -*- coding: utf-8 -*-
"""
gateway/context_projection.py -- Context Projection Layer (Phase-1.6)

ContextRuntime.full_context() の4層構造を、legacy ContextBuilder schema へ
写像する後方互換層。Canonical Source = C:/Users/sirok/MOCKA_OVERVIEW.json
(PHI-OS InstitutionContext が読む正本) を前提とする。

設計方針:
  - 純粋変換層とする。ContextRuntime を import せず、current()/boot() も呼ばない。
    入力dictの取得は呼出側の責務であり、本モジュールはテスト時に実DBも実ファイルも
    必要としない。
  - fail closed。取得できなかった場合に空の値を返さない。
    "存在しない情報"(空リスト等の正常値) と "取得失敗"(例外) を混同しない。
  - 未実装フィールドにplaceholderを置かない。legacy schema の6キーのうち
    現時点で写像可能なのは phase / goal の2つのみであり、残りは
    ProjectionIncompleteError として明示する。

写像状況 (Phase-1.6-Implementation-01 時点):
  phase           <- institution.current_phase          実装済
  goal            <- institution.top_todos[0]           実装済
  last_decision   <- 写像元なし (events.db 再取得が必要)     未実装
  active_todo     <- 写像元なし (MOCKA_TODO.json 再取得が必要) 未実装
  recent_events   <- memory.related_events は構造不一致        未実装
  essence_summary <- 写像元なし (lever_essence.json 再取得が必要) 未実装
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

# legacy ContextBuilder の meta.version。Projection化は消費者から見て
# 透過であるべきなので、legacy の固定値をそのまま維持する。
LEGACY_META_VERSION = "1.1"

# ContextRuntime.full_context() が必ず含む4層。
REQUIRED_INPUT_LAYERS = ("institution", "working", "memory", "execution")

# legacy ContextBuilder が受け付けるmode。未知modeは暗黙フォールバックしない
# (legacy の .get(mode, 5) 相当の挙動は踏襲しない)。
ALLOWED_MODES = ("compact", "standard", "extended")

# 現時点で写像可能なフィールド。
IMPLEMENTED_FIELDS = ("phase", "goal")

# 写像元が存在しないフィールド。placeholderを返さず例外とする。
UNIMPLEMENTED_FIELDS = ("last_decision", "active_todo", "recent_events", "essence_summary")

# InstitutionContext._load_overview() が失敗しても例外を送出せず
# warnings へ追記するのみのため、dataclass既定値 (current_phase="Phase 4" 等) が
# 正常値として素通りする。この文字列を検出して取得失敗と判定する。
_OVERVIEW_FAILURE_MARKER = "MOCKA_OVERVIEW 読み込み失敗"


class ProjectionError(Exception):
    """Projectionが成立しなかったことを示す。空のcontextを返す代わりに送出する。"""


class ProjectionIncompleteError(ProjectionError):
    """写像元が存在しないフィールドを要求されたことを示す(未実装であり、取得失敗ではない)。"""


def _validate_input(context) -> None:
    """入力が ContextRuntime.full_context() 形式であることを検証する。"""
    if not isinstance(context, dict):
        raise ProjectionError(f"context must be a dict, got {type(context).__name__}")

    missing = [k for k in REQUIRED_INPUT_LAYERS if k not in context]
    if missing:
        raise ProjectionError(f"missing required context layers: {','.join(missing)}")

    institution = context["institution"]
    if not isinstance(institution, dict):
        raise ProjectionError(
            f"context['institution'] must be a dict, got {type(institution).__name__}"
        )

    # fail closed: OVERVIEW読み込みに失敗している場合、InstitutionContext は
    # dataclass既定値("Phase 4"等)を保持したままになる。これをphaseとして
    # 返すと、入力が壊れているのに正常な値が返る状態になるため拒否する。
    warnings = institution.get("warnings") or []
    if isinstance(warnings, (list, tuple)):
        for w in warnings:
            if _OVERVIEW_FAILURE_MARKER in str(w):
                raise ProjectionError(
                    f"canonical source unavailable (institution.warnings: {w})"
                )


def _validate_mode(mode: str) -> None:
    if mode not in ALLOWED_MODES:
        raise ProjectionError(
            f"unknown mode: {mode!r} (allowed: {','.join(ALLOWED_MODES)})"
        )


def _project_phase(institution: dict) -> str:
    """phase <- institution.current_phase"""
    value = institution.get("current_phase", "")
    return value if isinstance(value, str) else str(value)


def _project_goal(institution: dict) -> str:
    """
    goal <- institution.top_todos[0]

    legacy ContextBuilder は next_actions.immediate[0] を文字列として取り出す。
    InstitutionContext.top_todos も同じ next_actions.immediate 由来だが、
    リストのまま保持されるため先頭要素を取り出す。
    空リストは未設定を意味する正常値であり、"" を返す(例外にしない)。
    """
    top_todos = institution.get("top_todos") or []
    if not isinstance(top_todos, (list, tuple)) or not top_todos:
        return ""
    head = top_todos[0]
    return head if isinstance(head, str) else str(head)


class ContextProjection:
    """
    ContextRuntime.full_context() -> legacy schema の変換層。

    使い方:
        proj = ContextProjection()
        payload = proj.project(runtime_context, mode="standard")

    ContextRuntime への依存を持たないため、呼出側が full_context() を渡す。
    """

    def project(self, context: dict, mode: str = "standard") -> dict:
        """
        写像可能なフィールドのみを含むpayloadを返す。

        現時点の出力は legacy schema の厳密な部分集合であり、legacy互換ではない。
        未実装フィールド(UNIMPLEMENTED_FIELDS)は placeholder を置かず、
        キー自体を出力しない。legacy互換の完全なpayloadが必要な場合は
        project_legacy() を使うこと(現時点では必ず例外になる)。
        """
        _validate_mode(mode)
        _validate_input(context)

        institution = context["institution"]

        payload = {
            "meta": {
                "version": LEGACY_META_VERSION,
                "mode": mode,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "size_bytes": 0,
            },
            "phase": _project_phase(institution),
            "goal": _project_goal(institution),
        }

        # size_bytes は payload 確定後に自己計測して埋める。
        # 計測対象は size_bytes=0 を含む状態のpayloadであり、更新後は
        # 桁数のぶん(len(str(size))-1 バイト)だけ実バイト長が上回る。
        # legacy ContextBuilder も同じ自己参照を持つ(計測時に size_bytes キー
        # 自体が無いため、legacy のずれ幅はさらに大きい)。
        # legacy互換のためこの意味論をそのまま踏襲する。
        size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        payload["meta"]["size_bytes"] = size
        return payload

    def project_legacy(self, context: dict, mode: str = "standard") -> dict:
        """
        legacy ContextBuilder schema と完全互換のpayloadを返す(未実装)。

        legacy 6キーのうち last_decision / active_todo / recent_events /
        essence_summary は ContextRuntime.full_context() に写像元が存在せず、
        events.db・MOCKA_TODO.json・lever_essence.json への再アクセスを要する。
        空文字列や空リストを返すと "取得失敗" と "存在しない" が区別できなく
        なるため、実装されるまでは常に例外とする。
        """
        _validate_mode(mode)
        _validate_input(context)
        raise ProjectionIncompleteError(
            "legacy projection is not implemented for: "
            + ",".join(UNIMPLEMENTED_FIELDS)
        )
