from phi_os.runtime.production_observation import ProductionObservation


class ProductionBridge:
    """
    Production execution boundary.
    """

    VALID_GATES = {
        "HG-01",
        "HG-02",
        "HG-03",
        "HG-04",
        "HG-05",
    }

    def __init__(self):
        self.observation = ProductionObservation()
        self.production_halted = False

    def halt_production(self, evidence_reference: str = None):
        incident = self.observation.create_incident(
            evidence_reference=evidence_reference
        )

        self.production_halted = True

        return incident

    def can_resume(self, decision_record: dict) -> bool:
        if not isinstance(decision_record, dict):
            return False

        if decision_record.get("approved") is not True:
            return False

        if decision_record.get("gate_id") not in self.VALID_GATES:
            return False

        return True

    def resume(self, decision_record: dict) -> bool:
        if not self.can_resume(decision_record):
            return False

        self.production_halted = False
        return True

    def is_halted(self) -> bool:
        return self.production_halted