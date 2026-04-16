import subprocess
import time

PIPELINE = [
    "incident_pipeline.py",
    "incident_trend_detector.py",
    "mocka_guard.py",
    "repair_engine.py",
    "policy_engine.py",
    "repair_executor.py",
    "verify_engine.py",
    "incident_knowledge_base_engine.py",
    "knowledge_learning_engine.py",
    "adaptive_repair_selector.py","shadow_failover_engine.py"
]

SLEEP_SECONDS = 10

def run_step(script):

    try:

        result = subprocess.run(
            ["python", script],
            capture_output=True,
            text=True
        )

        print("STEP:", script)
        print(result.stdout)

    except Exception as e:

        print("STEP_FAILED:", script)
        print(str(e))

def main():

    print("MOCKA_SELF_HEALING_LOOP_START")

    while True:

        for script in PIPELINE:
            run_step(script)

        print("LOOP_COMPLETE")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()

