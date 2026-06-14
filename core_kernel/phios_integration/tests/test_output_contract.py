"""
phios_integration.tests.test_output_contract

PHI-OS出力契約(AnalysisResultスキーマ固定・ErrorInfo・出力ラッパー)に関するテスト。
"""

from core_kernel.event_contracts import build_event
from core_kernel.phios_integration import (
    ErrorInfo,
    PrismBridge,
    STATUS_ERROR,
    STATUS_OK,
    build_error_response,
    build_success_response,
    from_bridge_result,
)
from core_kernel.prism.models import PRISM_OUTPUT_SCHEMA_VERSION


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


# ----------------------------------------------------------------------
# Prism出力モデルのバージョン保持確認
# ----------------------------------------------------------------------

def test_prism_models_carry_version_field():
    bridge = PrismBridge()
    bridge.initialize_prism()

    result = bridge.analyze_event(_make_event())["result"]

    assert result.context.version == PRISM_OUTPUT_SCHEMA_VERSION
    assert result.observation.version == PRISM_OUTPUT_SCHEMA_VERSION
    assert result.cognitive_state.version == PRISM_OUTPUT_SCHEMA_VERSION
    for annotation in result.annotations:
        assert annotation.version == PRISM_OUTPUT_SCHEMA_VERSION


def test_prism_models_to_dict_includes_version():
    bridge = PrismBridge()
    bridge.initialize_prism()

    result = bridge.analyze_event(_make_event())["result"]

    assert result.context.to_dict()["version"] == PRISM_OUTPUT_SCHEMA_VERSION
    assert result.observation.to_dict()["version"] == PRISM_OUTPUT_SCHEMA_VERSION
    assert result.cognitive_state.to_dict()["version"] == PRISM_OUTPUT_SCHEMA_VERSION


def test_prism_models_are_frozen_and_dataclass():
    from core_kernel.prism.models import CognitiveState, Context, Observation, SemanticAnnotation

    for cls in (Context, Observation, CognitiveState, SemanticAnnotation):
        assert cls.__dataclass_params__.frozen is True


# ----------------------------------------------------------------------
# ErrorInfo
# ----------------------------------------------------------------------

def test_error_info_to_dict_structure():
    error = ErrorInfo(error_type="validation_error", message="boom", event_id="evt-1")
    data = error.to_dict()

    assert set(data.keys()) == {"error_type", "message", "event_id", "timestamp", "source_module"}
    assert data["error_type"] == "validation_error"
    assert data["message"] == "boom"
    assert data["event_id"] == "evt-1"
    assert data["source_module"] == "phios_integration"
    assert data["timestamp"]


def test_error_info_defaults():
    error = ErrorInfo(error_type="prism_error", message="oops")

    assert error.event_id is None
    assert error.source_module == "phios_integration"
    assert error.timestamp


# ----------------------------------------------------------------------
# 成功/エラーレスポンス形式
# ----------------------------------------------------------------------

def test_build_success_response_with_dict_result():
    response = build_success_response({"a": 1})

    assert response == {"status": STATUS_OK, "result": {"a": 1}}


def test_build_success_response_with_model_result():
    bridge = PrismBridge()
    bridge.initialize_prism()
    analysis = bridge.analyze_event(_make_event())["result"]

    response = build_success_response(analysis.context)

    assert response["status"] == STATUS_OK
    assert response["result"]["context_id"] == analysis.context.context_id
    assert response["result"]["version"] == PRISM_OUTPUT_SCHEMA_VERSION


def test_build_error_response():
    error = ErrorInfo(error_type="validation_error", message="invalid")
    response = build_error_response(error)

    assert response["status"] == STATUS_ERROR
    assert response["error"]["error_type"] == "validation_error"
    assert response["error"]["message"] == "invalid"


# ----------------------------------------------------------------------
# Prism出力ラップ確認 (from_bridge_result)
# ----------------------------------------------------------------------

def test_from_bridge_result_success():
    bridge = PrismBridge()
    bridge.initialize_prism()

    event = _make_event()
    bridge_result = bridge.analyze_event(event)
    wrapped = from_bridge_result(bridge_result, event=event)

    assert wrapped["status"] == STATUS_OK
    assert "result" in wrapped
    assert wrapped["result"]["observation"]["finding"]
    assert wrapped["result"]["context"]["version"] == PRISM_OUTPUT_SCHEMA_VERSION


def test_from_bridge_result_error_includes_event_id():
    bridge = PrismBridge()
    bridge.initialize_prism()

    invalid_event = {"event_type": "change_start", "event_id": "evt-broken"}
    bridge_result = bridge.analyze_event(invalid_event)
    wrapped = from_bridge_result(bridge_result, event=invalid_event)

    assert wrapped["status"] == STATUS_ERROR
    assert wrapped["error"]["error_type"] == "validation_error"
    assert wrapped["error"]["event_id"] == "evt-broken"


def test_from_bridge_result_provider_not_initialized():
    bridge = PrismBridge()

    bridge_result = bridge.analyze_event(_make_event())
    wrapped = from_bridge_result(bridge_result)

    assert wrapped["status"] == STATUS_ERROR
    assert wrapped["error"]["error_type"] == "provider_not_initialized"
    assert wrapped["error"]["event_id"] is None


# ----------------------------------------------------------------------
# null/empty安全性
# ----------------------------------------------------------------------

def test_build_success_response_with_none():
    response = build_success_response(None)
    assert response == {"status": STATUS_OK, "result": None}


def test_build_success_response_with_empty_collections():
    assert build_success_response({}) == {"status": STATUS_OK, "result": {}}
    assert build_success_response([]) == {"status": STATUS_OK, "result": []}
    assert build_success_response(()) == {"status": STATUS_OK, "result": []}


def test_from_bridge_result_empty_events():
    bridge = PrismBridge()
    bridge.initialize_prism()

    bridge_result = bridge.analyze_events([])
    wrapped = from_bridge_result(bridge_result)

    assert wrapped["status"] == STATUS_ERROR
    assert wrapped["error"]["error_type"] == "validation_error"
