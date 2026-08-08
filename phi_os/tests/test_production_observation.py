from phi_os.runtime.production_observation import ProductionObservation


def test_create_incident_is_halted():

    observer = ProductionObservation()

    record = observer.create_incident(
        "EVT_SHA256_REFERENCE"
    )

    assert record.state == "HALTED"
    assert record.evidence_reference == "EVT_SHA256_REFERENCE"
    assert record.incident_id.startswith("INC_")


def test_resume_requires_human_authority():

    observer = ProductionObservation()

    assert observer.verify_resume_authority(
        {
            "authority": "ai",
            "approved": True
        }
    ) is False


def test_resume_requires_approval():

    observer = ProductionObservation()

    assert observer.verify_resume_authority(
        {
            "authority": "human",
            "approved": True
        }
    ) is True
