import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECURITY_GATE = os.path.join(BASE_DIR, "runtime", "security_gate.py")


def main():
    result = subprocess.run(
        ["python", SECURITY_GATE],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        print("Commit blocked by Security Gate")
        sys.exit(1)

    print("Commit allowed")
    sys.exit(0)


if __name__ == "__main__":
    main()
