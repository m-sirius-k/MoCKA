import subprocess
import time
from incident_engine import record_event

TARGET = ["python","C:\\Users\\sirok\\MoCKA\\civilization_evolution_loop.py"]

def run_once():

    try:

        result = subprocess.run(
            TARGET,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            record_event(
                event_type="incident",
                actor="system",
                title="Python Runtime Error",
                content=result.stderr,
                source="error_capture_engine",
                impact="major",
                focus_point="runtime failure",
                incident_candidate=True
            )

            print("INCIDENT_RECORDED")

        else:

            record_event(
                event_type="system_event",
                actor="system",
                title="Civilization Loop Success",
                content=result.stdout,
                source="error_capture_engine",
                impact="none",
                focus_point="normal operation",
                incident_candidate=False
            )

            print("SUCCESS_RECORDED")

    except Exception as e:

        record_event(
            event_type="incident",
            actor="system",
            title="Execution Failure",
            content=str(e),
            source="error_capture_engine",
            impact="critical",
            focus_point="engine crash",
            incident_candidate=True
        )

        print("ENGINE_CRASH")

def main():

    print("ERROR CAPTURE ENGINE START")

    while True:

        run_once()

        time.sleep(5)

if __name__ == "__main__":

    main()
