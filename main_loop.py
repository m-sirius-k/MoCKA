import os
import subprocess
import sys


WRAPPER_ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS_GUARD = os.path.join(WRAPPER_ROOT, "tools", "signature_guard.py")


def _env_flag_true(name: str, default: str = "1") -> bool:
    v = os.environ.get(name, default).strip().lower()
    return v not in ("0", "false", "no", "off")


def _resolve_entry() -> str:
    p = os.environ.get("MOCKA_ENTRY", "").strip()
    if not p:
        return ""
    if not os.path.isabs(p):
        p = os.path.join(WRAPPER_ROOT, p)
    p = os.path.abspath(p)
    return p if os.path.isfile(p) else ""


def _infer_root_from_entry(entry: str) -> str:
    low = entry.lower().replace("/", "\\")
    if "\\infield\\main_loop.py" in low:
        return os.path.abspath(os.path.join(os.path.dirname(entry), ".."))
    if "\\app\\main_loop.py" in low:
        return os.path.abspath(os.path.join(os.path.dirname(entry), ".."))
    return os.path.abspath(os.path.dirname(entry))


def _prepend_pythonpath(env: dict, path: str) -> None:
    cur = env.get("PYTHONPATH", "")
    if cur:
        env["PYTHONPATH"] = path + os.pathsep + cur
    else:
        env["PYTHONPATH"] = path


def main() -> int:
    enforce = _env_flag_true("MOCKA_SIGNATURE_ENFORCE", "1")

    entry = _resolve_entry()
    if not entry:
        print("[main_loop] ERROR: MOCKA_ENTRY is not set or file not found.")
        print(r"[main_loop] Example: $env:MOCKA_ENTRY='C:\Users\sirok\mocka-core-private\infield\main_loop.py'")
        return 2

    run_root = _infer_root_from_entry(entry)

    env = os.environ.copy()
    env["MOCKA_ROOT"] = run_root

    # 重要: mocka-core-private を sys.path に入れて "src.*" import を成立させる
    _prepend_pythonpath(env, run_root)

    cmd = [sys.executable, entry]
    rc = subprocess.call(cmd, cwd=run_root, env=env)

    if rc != 0:
        print(f"[main_loop] entry failed rc={rc} entry={entry}")
        return rc

    if enforce:
        if not os.path.isfile(TOOLS_GUARD):
            print(f"[main_loop] ERROR: signature_guard not found: {TOOLS_GUARD}")
            return 3

        guard_cmd = [sys.executable, TOOLS_GUARD]
        guard_rc = subprocess.call(guard_cmd, cwd=run_root, env=env)
        if guard_rc != 0:
            print(f"[main_loop] signature_guard failed rc={guard_rc}")
            return guard_rc

    print("[main_loop] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())