from pathlib import Path


def load_moCKA_rules():
    rule_path = Path(__file__).parent.parent / "docs" / "mocka_global_rules.md"

    if not rule_path.exists():
        raise Exception("MoCKA rules not found - SYSTEM HALT")

    with open(rule_path, "r", encoding="utf-8") as f:
        rules = f.read()

    return rules


if __name__ == "__main__":
    rules = load_moCKA_rules()
    print("MoCKA GLOBAL RULES LOADED")
