from runtime.jarvis.core.engine import JarvisEngine
from runtime.jarvis.record.ledger import JarvisLedger


def test_jarvis_runtime_smoke():
    engine = JarvisEngine()
    ledger = JarvisLedger()

    result = engine.evaluate("JARVIS-TEST-001")

    record = ledger.append(
        result["decision_id"],
        result["status"]
    )

    assert record["decision_id"] == "JARVIS-TEST-001"
    assert record["status"] == "WAITING"