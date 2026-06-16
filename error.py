# error.py
# MoCKA v1.2.1+ — 制度化例外システム
# 各層の例外は MoCKAError を継承する。層をまたぐ例外伝播を構造化する。

class MoCKAError(Exception):
    """MoCKA 制度OS 基底例外。"""

class BridgeError(MoCKAError):
    """Bridge層での conflict 登録失敗。"""

class PhiClassificationError(MoCKAError):
    """PHI-OS が分類不能な入力を受け取った。"""

class TimelineError(MoCKAError):
    """Timeline への追記失敗（ファイルI/O等）。"""

class AuditError(MoCKAError):
    """Audit層での整合性違反検出。"""

class ConfigError(MoCKAError):
    """設定ファイルの読み込み・検証失敗。"""
