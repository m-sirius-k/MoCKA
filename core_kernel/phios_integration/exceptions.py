"""
MoCKA Core Kernel — phios_integration.exceptions
"""


class PhiosIntegrationError(Exception):
    """phios_integrationに関する例外の基底クラス。"""


class ProviderNotInitializedError(PhiosIntegrationError):
    """PrismProviderが初期化されていない状態でanalyzeが呼ばれた場合に発生する。"""


class EventValidationError(PhiosIntegrationError):
    """入力EventがEvent Contractに準拠していない場合に発生する。"""
