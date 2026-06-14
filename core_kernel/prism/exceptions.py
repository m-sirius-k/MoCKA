"""
MoCKA Core Kernel — prism.exceptions

Prism内で発生する例外を定義する。
"""


class PrismError(Exception):
    """Prismに関する例外の基底クラス。"""


class InvalidEventError(PrismError):
    """入力EventがEvent Contractに準拠していない場合に発生する。"""


class PipelineError(PrismError):
    """Pipelineの実行中に回復不能な問題が発生した場合に発生する。"""
