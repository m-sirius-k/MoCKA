# -*- coding: utf-8 -*-
"""Environment Isolator (Phase 6 Commercial Hardening Layer)

役割:
  - dev / test / prod の3環境を分離する
  - runtime config を一度ロードしたら固定化する (immutable)
  - prod環境ではside-effect (外部I/O・ファイル書き込み・ネットワーク) を
    明示的に許可しない限り遮断する

環境判定は環境変数 MOCKA_ENV (dev/test/prod, default="dev") で行う。
"""

import os
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


@dataclass(frozen=True)
class RuntimeConfig:
    environment: Environment
    allow_side_effects: bool
    allow_network: bool
    allow_file_write: bool
    locked: bool = field(default=True)


_DEFAULTS = {
    Environment.DEV: dict(allow_side_effects=True, allow_network=True, allow_file_write=True),
    Environment.TEST: dict(allow_side_effects=False, allow_network=False, allow_file_write=False),
    Environment.PROD: dict(allow_side_effects=False, allow_network=False, allow_file_write=False),
}

_current_config = None


def detect_environment() -> Environment:
    raw = os.environ.get("MOCKA_ENV", "dev").strip().lower()
    try:
        return Environment(raw)
    except ValueError:
        return Environment.DEV


def load_config(env: Environment = None) -> RuntimeConfig:
    """環境設定を読み込み、一度だけ固定化する。

    2回目以降の呼び出しでは最初にロードされた設定をそのまま返す
    (runtime config固定化)。再ロードが必要な場合は reset() を使う。
    """
    global _current_config
    if _current_config is not None:
        return _current_config

    env = env or detect_environment()
    defaults = _DEFAULTS[env]
    _current_config = RuntimeConfig(
        environment=env,
        allow_side_effects=defaults["allow_side_effects"],
        allow_network=defaults["allow_network"],
        allow_file_write=defaults["allow_file_write"],
        locked=True,
    )
    return _current_config


def reset():
    """テスト専用: 固定化された設定を解除する。本番コードから呼んではならない。"""
    global _current_config
    _current_config = None


def current() -> RuntimeConfig:
    return load_config()


def guard_side_effect(name: str):
    """side-effectを伴う操作の直前に呼ぶ。許可されていない環境では SideEffectBlocked を投げる。"""
    cfg = current()
    if not cfg.allow_side_effects:
        raise SideEffectBlocked(f"{name}: side-effect blocked in environment={cfg.environment.value}")


class SideEffectBlocked(Exception):
    """side-effectが現在の環境で禁止されている場合に投げられる。"""
