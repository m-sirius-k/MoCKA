from runtime.dsl_loader import load_dsl, save_dsl
import random

def main():
    dsl = load_dsl()

    if not isinstance(dsl, list):
        dsl = []

    if len(dsl) < 2:
        print("NOT ENOUGH DSL")
        return

    base = random.choice(dsl)

    new = {
        "id": "fusion_boost.py_"+str(random.randint(1000,9999)),
        "action": base.get("action", "EXPLORE")
    }

    dsl.append(new)
    save_dsl(dsl)

    print("fusion_boost.py UPDATED:", new["id"])

if __name__ == "__main__":
    main()
