"""
H2-1 control権限ゲート(封印スタブ) — H2-3(Trust/Enforcement)確定まで無効化する。

絶対制約(博士確定・最終ルール):
  ExecutionContext MUST NOT be imported or referenced inside this module.
このファイル内に"ExecutionContext"という文字列を含むimport文を置いてはならない。
レビュー時はこのファイルのimport文一覧を見るだけで境界遵守を確認できる。

本モジュールはif/else・条件分岐・policy判断・permission evaluationを
一切含めない。control_action()は常に例外を発生させ、
before_control_action()は常にREJECT固定値を返す。
動的な許可判断はH2-3として別途・別セッションで設計する。
"""
from __future__ import annotations

from dataclasses import dataclass

from . import permissions


@dataclass(frozen=True)
class SemanticPacket:
    """意味層からの入力構造(構造のみ)。
    禁止: trust_score, threshold, condition, policy_result 等のフィールド。
    TODO(次フェーズ): payload_refは現状strのみで「参照のみ」を構造的に
    強制できていない。PayloadRef型でのラップを次フェーズで検討。

    [Trust Boundary 制度宣言 — H2-3 Plan A, 2026-06-21確定]
    SemanticPacket は構造のみを保持する。

    評価値・スコア・分類ラベルといった概念は、このデータ構造によって
    表現不能である(these concepts are not representable within this
    data structure)。将来のフィールド追加であっても、この構造的な
    表現不能性は変わらない。"""
    source: str
    timestamp: float
    payload_ref: str


def ingress(packet: SemanticPacket) -> None:
    """意味層からの入力を受け取る差し込み口。
    判断・分岐・評価は一切行わない。既存のH2-1/H2-2スタブと同じ振る舞い:
    常に既存のREJECTスタブへそのまま渡す。

    [Trust Boundary 制度宣言 — H2-3 Plan A, 2026-06-21確定]
    ingress は「行動(action)」ではなく「観測入力の記録点(observation
    record point)」として制度的に位置づけられる。

    これは意味論的不変条件(semantic invariant)である。
    ingress は将来のいかなる拡張においても実行トリガーとして
    解釈されてはならない。"""
    before_control_action()


class ControlDisabledError(Exception):
    """H2-3未確定の間、control_action()は恒久的にこの例外を発生させる。"""
    pass


def before_control_action(actor_id: str = "", **kwargs) -> dict:
    """control行使前の強制インターセプト(7.1c)。H2-3確定まで常にREJECT固定。"""
    return {"result": "REJECT", "reason": "H2_3_PENDING"}


def control_action(*args, **kwargs):
    """control権限の行使スタブ(7.1a)。H2-3確定まで常に例外を発生させる。
    permissions.check_control()によりcontrol権限の所在(HAB専属)を確認できるが、
    本関数自体は行使条件(Trust)を判定しない。"""
    raise ControlDisabledError(
        "CONTROL_DISABLED_H2_3_PENDING: H2-3(Trust/Enforcement)は未確定のため、"
        "control_actionは恒久的に無効化されている。HAB専属(permissions.HAB_ACTOR_ID="
        f"{permissions.HAB_ACTOR_ID!r})であってもH2-3確定前は行使不可。"
    )
