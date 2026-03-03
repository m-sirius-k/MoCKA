import argparse, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = json.load(open(args.input, "r", encoding="utf-8"))

    fail_kinds = sorted(set(src["result"]["fail"]["kinds"]))

    out = {
        "schema_version": "1.3.0",
        "fail_kinds": fail_kinds,
    }

    txt = json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    open(args.output, "w", encoding="utf-8", newline="\n").write(txt)
    print("CALIBER_MIN_WRITTEN", args.output)

if __name__ == "__main__":
    main()

# NOTE:
# - Input must be UTF-8 no-BOM normalized shadow output: outbox/shadow_e2e.utf8.json
# - Determinism proof: same input => identical output bytes => sha256 matches

