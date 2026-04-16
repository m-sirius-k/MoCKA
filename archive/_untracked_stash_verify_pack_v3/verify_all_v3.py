import os
import sys
import subprocess


def run_py(rel_path: str) -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, rel_path)
    if not os.path.isfile(target):
        raise FileNotFoundError(target)

    p = subprocess.run([sys.executable, target], cwd=here)
    if p.returncode != 0:
        raise RuntimeError("verify failed: " + rel_path)


def main() -> int:
    try:
        run_py(os.path.join("verify", "key_generation_verify_v3.py"))
        run_py(os.path.join("verify", "key_anchor_verify_v3.py"))
        run_py(os.path.join("verify", "key_history_verify_v3.py"))
        print("status: OK")
        return 0
    except Exception as e:
        print("status: FAIL")
        print("error: " + str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
