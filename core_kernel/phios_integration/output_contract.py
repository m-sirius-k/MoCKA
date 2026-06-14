"""
MoCKA Core Kernel — phios_integration.output_contract

責務:
  PHI-OSがPrismの解析結果を返却する際の出力形式を固定する。

  PHI-OSは必ず以下のいずれかの形式で返却する:

    {"status": "ok", "result": <dict>}
    {"status": "error", "error": <ErrorInfo.to_dict()>}

  例外は投げない。本モジュールはラッピングのみを行い、
  Memory/Relay/Orchestraへの連携は行わない。
"""

from .error_info import ErrorInfo

STATUS_OK = "ok"
STATUS_ERROR = "error"


def build_success_response(result) -> dict:
    """成功時のPHI-OS出力契約に従ったレスポンスを構築する。

    Args:
        result: to_dict()を持つPrism出力モデル(Context/Observation/
                CognitiveState/SemanticAnnotation)、AnalysisResult、
                またはJSON変換可能なdict/None。

    Returns:
        dict: {"status": "ok", "result": <dict>}
    """
    return {"status": STATUS_OK, "result": _to_serializable(result)}


def build_error_response(error_info: ErrorInfo) -> dict:
    """失敗時のPHI-OS出力契約に従ったレスポンスを構築する。

    Args:
        error_info: ErrorInfo

    Returns:
        dict: {"status": "error", "error": <ErrorInfo.to_dict()>}
    """
    return {"status": STATUS_ERROR, "error": error_info.to_dict()}


def from_bridge_result(bridge_result: dict, event: dict = None) -> dict:
    """PrismBridge.analyze_event/analyze_eventsの戻り値を、
    PHI-OS出力契約形式({"status":"ok","result":...} /
    {"status":"error","error":ErrorInfo})へ変換する。

    PrismBridge自体の戻り値形式は変更しない(既存テストへの影響を避ける)。
    本関数はPHI-OS側で出力契約を適用する際の変換層として用いる。

    Args:
        bridge_result: PrismBridge.analyze_event/analyze_eventsの戻り値
        event: 変換対象のEvent(event_idの補完用、省略可)

    Returns:
        dict: PHI-OS出力契約形式のレスポンス
    """
    if bridge_result.get("status") == STATUS_OK:
        return build_success_response(bridge_result.get("result"))

    error_info = ErrorInfo(
        error_type=bridge_result.get("error_type", "unknown_error"),
        message=bridge_result.get("error", ""),
        event_id=(event or {}).get("event_id") if event else None,
    )
    return build_error_response(error_info)


def _to_serializable(value):
    """to_dict()を持つ値を再帰的にJSON変換可能な構造へ変換する。

    null/emptyな入力(None, {}, (), [])はそのまま安全に返す。
    """
    if value is None:
        return None

    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _to_serializable(value.to_dict())

    if hasattr(value, "_asdict"):
        # AnalysisResultなど、to_dict()を持たないdataclassへのフォールバック
        return _to_serializable(dict(value._asdict()))

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _to_serializable(getattr(value, name))
            for name in value.__dataclass_fields__
        }

    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]

    return value
