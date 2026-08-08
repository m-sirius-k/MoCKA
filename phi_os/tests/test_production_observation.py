from phi_os.runtime.production_observation import ProductionObservation


def test_create_incident_is_halted():

    observer = ProductionObservation()

    record = observer.create_incident(
        "EVT_SHA256_REFERENCE"
    )

    assert record.state == "HALTED"
    assert record.evidence_reference == "EVT_SHA256_REFERENCE"
    assert record.incident_id.startswith("INC_")


def test_resume_requires_valid_gate():

    observer = ProductionObservation()

    assert observer.verify_resume_authority(
        {
            "gate_id": "GATE-REL",
            "approved": True
        }
    ) is True


def test_resume_rejects_invalid_gate():

    observer = ProductionObservation()

    assert observer.verify_resume_authority(
        {
            "gate_id": "INVALID",
            "approved": True
        }
    ) is False
