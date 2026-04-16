from __future__ import annotations

# NOTE: Print the exact JSON files used by src.mocka_audit.verify_chain_from_files.
# NOTE: Usage:
# NOTE:   cd C:\Users\sirok\MoCKA
# NOTE:   python -m src.mocka_audit.print_file_chain_inputs

from pathlib import Path

from .verify_chain import BASE_DIR


def main() -> int:
    audit_dir = BASE_DIR / "audit" / "ed25519"
    print("AUDIT_DIR=" + str(audit_dir))

    files = sorted([p for p in audit_dir.glob("*.json") if p.is_file()], key=lambda p: p.name)
    print("FILES=" + str(len(files)))
    for p in files:
        print(str(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())