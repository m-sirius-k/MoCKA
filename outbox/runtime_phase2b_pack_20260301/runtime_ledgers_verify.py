import csv
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RT = os.path.join(ROOT, "infield", "ai_save", "runtime")
EMIT_LEDGER = os.path.join(RT, "emit_ledger.csv")
ACCEPT_LEDGER = os.path.join(RT, "accept_ledger.csv")

def die(msg: str, code: int = 1) -> int:
    print(msg)
    return code

def read_csv(path: str):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def pick(row: dict, keys: list[str]) -> str:
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return ""

def find_sha_field(row: dict) -> str:
    for _, v in row.items():
        if v is None:
            continue
        s = str(v).strip().lower()
        if len(s) == 64 and all(c in "0123456789abcdef" for c in s):
            return s
    return ""

def find_sig_field(row: dict) -> str:
    for _, v in row.items():
        if v is None:
            continue
        s = str(v).strip()
        if s.lower().endswith(".asc"):
            return s
    return ""

def gpg_verify(sig_path: str, txt_path: str) -> tuple[bool, str]:
    # Do not decode with system locale (cp932). Capture bytes, decode as utf-8 with replacement.
    p = subprocess.run(["gpg", "--verify", sig_path, txt_path], capture_output=True)
    ok = (p.returncode == 0)
    err = (p.stderr or b"").decode("utf-8", errors="replace").strip()
    return ok, err

def main() -> int:
    if not os.path.exists(EMIT_LEDGER):
        return die("HALT: MISSING_EMIT_LEDGER=" + EMIT_LEDGER)
    if not os.path.exists(ACCEPT_LEDGER):
        return die("HALT: MISSING_ACCEPT_LEDGER=" + ACCEPT_LEDGER)

    emits = read_csv(EMIT_LEDGER)
    accepts = read_csv(ACCEPT_LEDGER)

    emit_by_id: dict[str, dict] = {}
    for e in emits:
        eid = pick(e, ["emit_id", "id"])
        if eid != "":
            emit_by_id[eid] = e

    latest_accept_by_emit: dict[str, dict] = {}
    for a in accepts:
        eid = pick(a, ["emit_id", "id"])
        if eid == "":
            continue
        latest_accept_by_emit[eid] = a

    bad = 0
    checked = 0

    for eid, a in latest_accept_by_emit.items():
        e = emit_by_id.get(eid)
        if e is None:
            print("HALT: EMIT_NOT_FOUND emit_id=" + eid)
            bad += 1
            continue

        payload_sha = pick(e, ["payload_sha256", "payload_sha", "sha256"]).lower()

        recv_sha = pick(a, ["recv_payload_sha256", "payload_sha256", "recv_sha256", "payload_sha", "sha256"]).lower()
        if recv_sha == "":
            recv_sha = find_sha_field(a).lower()

        match_flag = pick(a, ["match_flag", "match", "is_match"]).lower()

        sig_name = pick(a, ["accept_sig", "sig", "signature", "sig_file"])
        if sig_name == "":
            sig_name = find_sig_field(a)

        if payload_sha == "" or recv_sha == "":
            print("HALT: HASH_EMPTY emit_id=" + eid)
            bad += 1
            continue

        if payload_sha != recv_sha:
            print("HALT: HASH_MISMATCH emit_id=" + eid + " expected=" + payload_sha + " got=" + recv_sha)
            bad += 1
            continue

        if match_flag not in ["true", "1", "yes"]:
            print("HALT: MATCH_FLAG_FALSE emit_id=" + eid + " match_flag=" + match_flag)
            bad += 1
            continue

        if sig_name == "":
            print("HALT: SIG_NAME_EMPTY emit_id=" + eid)
            bad += 1
            continue

        txt_name = ""
        cand1 = eid + ".accept.migrated.txt"
        cand2 = eid + ".accept.txt"
        if os.path.exists(os.path.join(RT, cand1)):
            txt_name = cand1
        elif os.path.exists(os.path.join(RT, cand2)):
            txt_name = cand2

        if txt_name == "":
            print("HALT: ACCEPT_TXT_MISSING emit_id=" + eid)
            bad += 1
            continue

        txt_path = os.path.join(RT, txt_name)
        sig_path = os.path.join(RT, sig_name)

        if not os.path.exists(sig_path):
            print("HALT: ACCEPT_SIG_MISSING emit_id=" + eid + " sig=" + sig_path)
            bad += 1
            continue

        ok, msg = gpg_verify(sig_path, txt_path)
        if not ok:
            print("HALT: GPG_VERIFY_FAIL emit_id=" + eid)
            print("gpg_stderr: " + msg)
            bad += 1
            continue

        checked += 1

    if bad == 0:
        print("JOINT INTEGRITY OK")
        print("rows_checked=" + str(checked))
        return 0

    print("JOINT INTEGRITY HALT")
    print("bad=" + str(bad))
    print("rows_checked=" + str(checked))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
