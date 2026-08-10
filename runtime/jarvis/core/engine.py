from runtime.jarvis.gate.human_gate import HumanGate


class JarvisEngine:
    def __init__(self):
        self.gate = HumanGate()

    def evaluate(self, decision_id):
        return self.gate.request(decision_id)