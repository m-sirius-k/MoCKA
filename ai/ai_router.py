class AIRouter:
    def __init__(self):
        self.registry = {}

    def register(self, name, adapter):
        self.registry[name] = adapter

    def send(self, ai_name, payload):
        if ai_name not in self.registry:
            raise Exception("AI not registered")

        return self.registry[ai_name].execute(payload)
