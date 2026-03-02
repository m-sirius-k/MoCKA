from pathlib import Path
from key_registry_verify_v4 import verify_registry
from event_signature_verify_v4 import verify_event_signatures

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"

SAMPLE_FILES = [
    "valid_2_of_3.json",
    "insufficient_signature.json",
    "duplicate_signer.json",
    "revoked_key_used.json",
    "canonical_tamper.json",
]

def main():
    print("== REGISTRY VERIFY ==")
    verify_registry()

    print("\n== SAMPLE VERIFY ==")
    for name in SAMPLE_FILES:
        p = SAMPLES / name
        print(f"\n-- {name}")
        try:
            verify_event_signatures(p)
            if name != "valid_2_of_3.json":
                raise Exception("EXPECTED_FAIL_BUT_PASSED")
            print("PASS (expected)")
        except Exception as e:
            if name == "valid_2_of_3.json":
                raise
            print(f"FAIL (expected): {e}")

    print("\nOK: verify_all_v4 complete")

if __name__ == "__main__":
    main()