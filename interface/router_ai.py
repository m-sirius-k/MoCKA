import subprocess
import os
from datetime import datetime

LOG_PATH = r"C:\Users\sirok\MoCKA\runtime\record\event_log.csv"

def get_mode():
    result = subprocess.run(
        ["python", r"C:\Users\sirok\MoCKA\interface\router_caliber.py"],
        capture_output=True,
        text=True
    )
    output = result.stdout

    if "audit_only" in output:
        return "audit_only"
    elif "audit_priority" in output:
        return "audit_priority"
    elif "balanced" in output:
        return "balanced"
    else:
        return "execution_priority"

def route_ai(task):
    mode = get_mode()

    if mode == "audit_only":
        return "gpt_audit"
    elif mode == "audit_priority":
        if "critical" in task.lower():
            return "gpt_audit"
        return "claude_execute"
    elif mode == "balanced":
        if "analysis" in task.lower():
            return "gpt_audit"
        return "claude_execute"
    else:
        return "claude_execute"

def write_log(task, selected):
    if not os.path.exists(LOG_PATH):
        return

    timestamp = datetime.now().isoformat()
    event = f"{timestamp},router,route,{task}->{selected}\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(event)

def main():
    task = "test analysis task"
    selected = route_ai(task)

    write_log(task, selected)

    print("=== AI Routing + Logged ===")
    print("task:", task)
    print("selected:", selected)

if __name__ == "__main__":
    main()
