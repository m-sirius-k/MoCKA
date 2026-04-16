from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
AUDIT_DIR = BASE_DIR / "audit"

def main():
    print(str(AUDIT_DIR))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
