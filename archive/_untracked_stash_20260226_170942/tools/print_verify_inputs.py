from __future__ import annotations

# NOTE: Print likely input paths used by src.mocka_audit.verify_chain.py
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m tools.print_verify_inputs

import re
from pathlib import Path


def main() -> int:
    p = Path(r"C:\Users\sirok\MoCKA\src\mocka_audit\verify_chain.py")
    s = p.read_text(encoding="utf-8")

    print("VERIFY_CHAIN_PY=" + str(p))

    # NOTE: Print lines containing these keywords (best-effort).
    keys = [
        "outbox",
        "OUTBOX",
        "last_event",
        "LAST_EVENT",
        "ledger",
        "LEDGER",
        ".json",
        "glob(",
        "Path(",
        "DB_PATH",
    ]

    lines = s.splitlines()
    hit = 0
    for i, line in enumerate(lines, start=1):
        low = line.lower()
        if any(k.lower() in low for k in keys):
            hit += 1
            print(f"L{i}: {line}")

    if hit == 0:
        print("WARN: no keyword hits; file may be very different than expected")
        return 2

    # NOTE: Best-effort: try to find string literals that include 'outbox'
    m = re.findall(r"r?['\"]([^'\"]*outbox[^'\"]*)['\"]", s, flags=re.IGNORECASE)
    if m:
        print("OUTBOX_LITERALS=" + str(m))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())