from __future__ import annotations

# NOTE: Export full source of src\mocka_audit\verify_chain.py to stdout.
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python .\tools\export_verify_chain_full.py > .\tools\verify_chain_full_dump.txt

from pathlib import Path


def main() -> int:
    p = Path(r"C:\Users\sirok\MoCKA\src\mocka_audit\verify_chain.py")
    print(p.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())