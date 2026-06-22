from bootstrap.load_rules import load_moCKA_rules


class RelayBootstrap:
    def __init__(self):
        self.rules = None

    def start(self):
        self.rules = load_moCKA_rules()
        self._validate_rules()

    def _validate_rules(self):
        required = [
            "SINGLE ROOT",
            "NO TEMP STRUCTURES",
            "NO DOUBLE NESTING"
        ]

        for r in required:
            if r not in self.rules:
                raise Exception(f"RULE VIOLATION: {r}")

        print("Relay initialized under MoCKA Global Rules")

    def get_rules(self):
        return self.rules
