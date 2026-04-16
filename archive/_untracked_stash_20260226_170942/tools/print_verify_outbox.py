from __future__ import annotations

# NOTE: Print OUTBOX_DIR (or equivalent) from src.mocka_audit.verify_chain.py
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python .\tools\print_verify_outbox.py

import inspect
import re

import src.mocka_audit.verify_chain as v


def main() -> int:
    p = inspect.getsourcefile(v)
    if not p:
        print("ERROR: cannot locate verify_chain module file")
        return 1

    with open(p, "r", encoding="utf-8") as f:
        s = f.read()

    m = re.search(r"OUTBOX_DIR\s*=\s*r?['\"]([^'\"]+)['\"]", s)
    if not m:
        m = re.search(r"OUTBOX\s*=\s*r?['\"]([^'\"]+)['\"]", s)

    print("VERIFY_CHAIN_PY=" + p)
    print("OUTBOX_DIR=" + (m.group(1) if m else "(not found)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())