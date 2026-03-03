import argparse
import hashlib
import json
from datetime import datetime, timezone

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--fail-kinds-json", required=False, default="")
    ap.add_argument("--class", dest="clazz", required=False, default="UNCLASSIFIED")
    ap.add_argument("--repair-id", required=False, default="")
    args = ap.parse_args()

    inp_sha = sha256_file(args.input)
    out_sha = sha256_file(args.output)

    fail_kinds = []
    if args.fail_kinds_json:
        fail_kinds = json.loads(args.fail_kinds_json)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # One-line alert format (stable)
    # TS CLASS INPUT_SHA OUTPUT_SHA FAIL_KINDS REPAIR_ID
    line = f"{ts} {args.clazz} {inp_sha} {out_sha} {','.join(sorted(set(fail_kinds)))} {args.repair_id}".rstrip() + "\n"
    print(line, end="")

if __name__ == "__main__":
    main()
