import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "production_observability"))

import pytest

from certification.certificate_generator import generate_certificate
from certification.deployment_certifier import DeploymentCertifier
from contracts.api_contract import APIContract, ContractRegistry
from contracts.schema_validator import (
    SchemaValidationError,
    is_breaking_change,
    validate,
)
from event_stream_collector import EventStreamCollector
from gate.release_gate import ReleaseGate
from scoring.prs_engine import PRSEngine, ReadinessLevel
from sla.sla_definition import SLARecord
from sla.sla_evaluator import SLAEvaluator
from telemetry_registry import EventType, TelemetryEvent


GOOD_SLA = SLARecord(
    service_name="mocka-core",
    availability=99.95,
    latency_ms=120.0,
    error_rate=0.001,
    integrity_score=99.0,
    reproducibility_score=98.0,
)

BAD_SLA = SLARecord(
    service_name="mocka-core",
    availability=80.0,
    latency_ms=1800.0,
    error_rate=0.04,
    integrity_score=60.0,
    reproducibility_score=60.0,
)

GOOD_PRS_METRICS = {
    "test_coverage": 0.98,
    "incident_count": 0,
    "telemetry_completeness": 1.0,
    "rollback_support": True,
    "contract_compliance": 1.0,
}

BAD_PRS_METRICS = {
    "test_coverage": 0.5,
    "incident_count": 4,
    "telemetry_completeness": 0.4,
    "rollback_support": False,
    "contract_compliance": 0.5,
}


# --- SLA tests ---------------------------------------------------------

def test_sla_pass():
    evaluator = SLAEvaluator()
    score = evaluator.evaluate(GOOD_SLA)
    assert score >= 85
    assert evaluator.passes(GOOD_SLA)


def test_sla_fail():
    evaluator = SLAEvaluator()
    score = evaluator.evaluate(BAD_SLA)
    assert score < 85
    assert not evaluator.passes(BAD_SLA)


# --- PRS tests -----------------------------------------------------------

def test_prs_production_eligible():
    engine = PRSEngine()
    score = engine.score(GOOD_PRS_METRICS)
    assert score >= 95
    assert engine.level(score) == ReadinessLevel.PRODUCTION_ELIGIBLE


def test_prs_blocked():
    engine = PRSEngine()
    score = engine.score(BAD_PRS_METRICS)
    assert score < 80
    assert engine.level(score) == ReadinessLevel.BLOCKED


def test_prs_limited_release_band():
    engine = PRSEngine()
    metrics = {
        "test_coverage": 0.85,
        "incident_count": 1,
        "telemetry_completeness": 0.9,
        "rollback_support": True,
        "contract_compliance": 0.9,
    }
    score = engine.score(metrics)
    assert 80 <= score < 95
    assert engine.level(score) == ReadinessLevel.LIMITED_RELEASE


def test_prs_missing_metric_raises():
    engine = PRSEngine()
    with pytest.raises(ValueError):
        engine.score({"test_coverage": 1.0})


# --- Deployment certification tests --------------------------------------

def _populated_collector() -> EventStreamCollector:
    collector = EventStreamCollector()
    for i in range(5):
        collector.emit(TelemetryEvent.create(EventType.REQUEST_START, layer="gateway", request_id=f"r{i}"))
        collector.emit(TelemetryEvent.create(EventType.REQUEST_END, layer="gateway", request_id=f"r{i}"))
    return collector


def test_certification_approved():
    certifier = DeploymentCertifier()
    sla_score = SLAEvaluator().evaluate(GOOD_SLA)
    prs_score = PRSEngine().score(GOOD_PRS_METRICS)

    context = {
        "prs_score": prs_score,
        "sla_pass": True,
        "sla_score": sla_score,
        "incident_count": 0,
        "telemetry_complete": True,
        "rollback_plan_exists": True,
        "model_version_hash": "model-abc123",
        "collector": _populated_collector(),
    }

    cert = certifier.certify(context)
    assert cert.status == "APPROVED"
    assert cert.id
    assert cert.telemetry_hash
    assert cert.model_hash == "model-abc123"


def test_certification_rejected_on_incident():
    certifier = DeploymentCertifier()
    sla_score = SLAEvaluator().evaluate(GOOD_SLA)
    prs_score = PRSEngine().score(GOOD_PRS_METRICS)

    context = {
        "prs_score": prs_score,
        "sla_pass": True,
        "sla_score": sla_score,
        "incident_count": 1,  # blocks certification
        "telemetry_complete": True,
        "rollback_plan_exists": True,
        "model_version_hash": "model-abc123",
        "collector": _populated_collector(),
    }

    cert = certifier.certify(context)
    assert cert.status == "REJECTED"


def test_certification_rejected_on_empty_telemetry():
    certifier = DeploymentCertifier()
    sla_score = SLAEvaluator().evaluate(GOOD_SLA)
    prs_score = PRSEngine().score(GOOD_PRS_METRICS)

    context = {
        "prs_score": prs_score,
        "sla_pass": True,
        "sla_score": sla_score,
        "incident_count": 0,
        "telemetry_complete": True,
        "rollback_plan_exists": True,
        "model_version_hash": "model-abc123",
        "collector": EventStreamCollector(),  # empty -> not replayable
    }

    cert = certifier.certify(context)
    assert cert.status == "REJECTED"


def test_certificate_generation_fields():
    cert = generate_certificate(
        model_hash="hash1", telemetry_hash="hash2", sla_score=96.0, prs_score=97.0, status="APPROVED"
    )
    assert cert.id
    assert cert.model_hash == "hash1"
    assert cert.telemetry_hash == "hash2"
    assert cert.sla_score == 96.0
    assert cert.prs_score == 97.0
    assert cert.status == "APPROVED"
    assert cert.timestamp > 0


# --- Release gate tests ---------------------------------------------------

def test_release_gate_allows_when_all_pass():
    gate = ReleaseGate()
    context = {
        "deployment_certified": True,
        "sla_pass": True,
        "prs": 96.0,
        "contract_valid": True,
        "observability_complete": True,
    }
    assert gate.can_release(context) is True


@pytest.mark.parametrize("field,value", [
    ("deployment_certified", False),
    ("sla_pass", False),
    ("prs", 90.0),
    ("contract_valid", False),
    ("observability_complete", False),
])
def test_release_gate_blocks_on_any_failure(field, value):
    gate = ReleaseGate()
    context = {
        "deployment_certified": True,
        "sla_pass": True,
        "prs": 96.0,
        "contract_valid": True,
        "observability_complete": True,
    }
    context[field] = value
    assert gate.can_release(context) is False


def test_release_gate_missing_key_raises():
    gate = ReleaseGate()
    with pytest.raises(ValueError):
        gate.can_release({"deployment_certified": True})


# --- Contract validation tests --------------------------------------------

CONTRACT_V1 = APIContract(
    name="execute_request",
    version="v1",
    input_schema={"type": "object", "required": ["request_id"], "properties": {"request_id": {"type": "string"}}},
    output_schema={"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}},
)


def test_contract_input_validation_passes():
    validate({"request_id": "abc"}, CONTRACT_V1.input_schema)


def test_contract_input_validation_fails_missing_field():
    with pytest.raises(SchemaValidationError):
        validate({}, CONTRACT_V1.input_schema)


def test_contract_input_validation_fails_wrong_type():
    with pytest.raises(SchemaValidationError):
        validate({"request_id": 123}, CONTRACT_V1.input_schema)


def test_contract_registry_rejects_breaking_redefinition():
    registry = ContractRegistry()
    registry.register(CONTRACT_V1)

    breaking = APIContract(
        name="execute_request",
        version="v1",
        input_schema={"type": "object", "required": ["request_id", "extra"], "properties": {}},
        output_schema=CONTRACT_V1.output_schema,
    )
    with pytest.raises(ValueError):
        registry.register(breaking)


def test_schema_breaking_change_detection():
    old_schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
    new_schema_breaking = {"type": "object", "required": ["a", "b"], "properties": {"a": {"type": "string"}}}
    new_schema_safe = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}, "b": {"type": "string"}}}

    assert is_breaking_change(old_schema, new_schema_breaking) is True
    assert is_breaking_change(old_schema, new_schema_safe) is False
