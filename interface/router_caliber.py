import json
import subprocess

def get_caliber_status():
    result = subprocess.run(
        ["python", r"C:\Users\sirok\MoCKA\caliber\caliber_engine.py"],
        capture_output=True,
        text=True
    )
    output = result.stdout

    if "CRITICAL" in output:
        return "CRITICAL"
    elif "DANGER" in output:
        return "DANGER"
    elif "WARNING" in output:
        return "WARNING"
    else:
        return "NORMAL"

def route_decision():
    status = get_caliber_status()

    if status == "CRITICAL":
        return "audit_only"
    elif status == "DANGER":
        return "audit_priority"
    elif status == "WARNING":
        return "balanced"
    else:
        return "execution_priority"

def main():
    decision = route_decision()
    print("=== Router Decision ===")
    print("mode:", decision)

if __name__ == "__main__":
    main()
