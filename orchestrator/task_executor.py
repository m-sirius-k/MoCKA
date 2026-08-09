import subprocess
import re


def execute_task(task: str, context: dict) -> dict:
    if task == "run_tests":
        result = subprocess.run(
            ["python", "-m", "pytest"],
            capture_output=True,
            text=True,
            timeout=300
        )

        return {
            "task": task,
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:]
        }

    if task == "collect_results":
        source = context.get("test_output", "")

        match = re.search(
            r"(\d+) passed(?:,\s*(\d+) failed)?",
            source
        )

        return {
            "task": task,
            "status": "completed",
            "passed": int(match.group(1)) if match else None,
            "failed": int(match.group(2)) if match and match.group(2) else 0
        }

    return {
        "task": task,
        "status": "pending"
    }
