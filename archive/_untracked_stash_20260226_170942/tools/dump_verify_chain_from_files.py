from __future__ import annotations

# NOTE: Dump source of verify_chain_from_files from src.mocka_audit.verify_chain
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m tools.dump_verify_chain_from_files

import inspect
import src.mocka_audit.verify_chain as v


def main() -> int:
    print("VERIFY_CHAIN_PY=" + str(inspect.getsourcefile(v)))
    print(inspect.getsource(v.verify_chain_from_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())