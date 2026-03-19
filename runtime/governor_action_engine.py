import json
import os
import subprocess

GOVERNOR_FILE = "mocka_civilization_governor.json"


def load_governor():
    if not os.path.exists(GOVERNOR_FILE):
        return None

    with open(GOVERNOR_FILE, "r") as f:
        return json.load(f)


def exploration_mode():
    print("GOVERNOR ACTION : exploration")

    if os.path.exists("repair_strategy_generator.py"):
        subprocess.call(["python", "repair_strategy_generator.py"])


def stable_operation_mode():
    print("GOVERNOR ACTION : stable_operation")

    if os.path.exists("civilization_evolution_loop.py"):
        subprocess.call(["python", "civilization_evolution_loop.py"])


def degrading_mode():
    print("GOVERNOR ACTION : degrading")

    if os.path.exists("deep_diagnostic_engine.py"):
        subprocess.call(["python", "deep_diagnostic_engine.py"])


def run():

    governor = load_governor()

    if not governor:
        print("NO GOVERNOR DATA")
        return

    mode = governor.get("mode")

    if mode == "exploration":
        exploration_mode()

    elif mode == "stable_operation":
        stable_operation_mode()

    elif mode == "degrading":
        degrading_mode()

    else:
        print("UNKNOWN MODE")


if __name__ == "__main__":
    run()
