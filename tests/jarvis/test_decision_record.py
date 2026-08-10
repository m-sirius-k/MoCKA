from runtime.jarvis.record.schema.decision_record import DecisionRecord


def test_decision_record_schema():
    record = DecisionRecord(
        "DC_TEST_003",
        "APPROVED"
    ).to_dict()

    assert record["decision_id"] == "DC_TEST_003"
    assert record["status"] == "APPROVED"
    assert record["actor"] == "HUMAN_GATE"
    assert "timestamp" in record
