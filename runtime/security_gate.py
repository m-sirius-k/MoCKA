import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

POLICY_PATH = os.path.join(BASE_DIR, "mocka_governance", "security_policy.json")
LOG_PATH = os.path.join(BASE_DIR, "runtime", "security_log.json")


def load_policy():
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_staged_files():
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    return [f.replace("\\\\", "/") for f in result.stdout.splitlines() if f]


def check_policy(files, policy):
    violations = []

    for f in files:
        for forbidden in policy["forbidden"]:
            if forbidden in f:
                violations.append(f)

    return violations


def write_log(files, violations):
    log = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "checked_files": files,
        "violations": violations,
        "status": "BLOCKED" if violations else "PASS"
    }

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


def run_security_gate():
    policy = load_policy()
    files = get_staged_files()

    if not files:
        print("No staged files")
        return 0

    violations = check_policy(files, policy)
    write_log(files, violations)

    if violations:
        print("SECURITY VIOLATION DETECTED")
        for v in violations:
            print(" -", v)
        return 1

    print("SECURITY CHECK PASSED")
    return 0


if __name__ == "__main__":
    exit(run_security_gate())
