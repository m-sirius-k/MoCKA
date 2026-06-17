import subprocess
from pathlib import Path

PROS_DIR = Path(__file__).parent.parent.parent / "workshop" / "pr-os"


def execute_action(action_name: str):
    if action_name == "evaluate":
        return run("python pros.py evaluate", cwd=PROS_DIR)

    if action_name == "submit":
        return run("python pros.py submit", cwd=PROS_DIR)

    if action_name == "publish":
        return run("python pros.py publish", cwd=PROS_DIR)

    if action_name == "sync":
        return {"message": "sync placeholder"}

    return {"error": "unknown action"}


def run(cmd: str, cwd=None):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return {
        "stdout": p.stdout,
        "stderr": p.stderr,
        "code": p.returncode
    }
