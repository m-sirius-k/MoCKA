from phi_os.runtime.production_observation import ProductionObservation


class ProductionBridge:

    def __init__(self):
        self.observation = ProductionObservation()

    def halt_production(self, evidence_reference: str):
        return self.observation.create_incident(
            evidence_reference=evidence_reference
        )

    def can_resume(self, decision_record: dict) -> bool:
        return self.observation.verify_resume_authority(
            decision_record
        )
