import hashlib
import subprocess
from typing import List, Tuple

# note: computes summary hash from GIT BLOBS (not working tree)
# usage: python calc_summary_hash_from_git.py <commit>

EXCLUDE_FILES = {
    "governance/anchor_record.json",
    "governance/anchor_bundle.json",
}
EXCLUDE_DIR_PREFIXES = (
    ".git/",
    "__pycache__/",
)

def run_git(args: List[str]) -> bytes:
    p = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", errors="replace"))
    return p.stdout

def list_files(commit: str) -> List[str]:
    out = run_git(["ls-tree", "-r", "--name-only", commit]).decode("utf-8", errors="replace")
    return [line.strip() for line in out.splitlines() if line.strip()]

def should_include(path: str) -> bool:
    if path in EXCLUDE_FILES:
        return False
    if path.endswith(".private.pem"):
        return False
    for pref in EXCLUDE_DIR_PREFIXES:
        if path.startswith(pref):
            return False
    # note: exclude common caches if present in repo history
    if "/__pycache__/" in path:
        return False
    return True

def blob_sha256(commit: str, path: str) -> str:
    data = run_git(["show", f"{commit}:{path}"])
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def main() -> int:
    import sys
    if len(sys.argv) != 2:
        print("usage: python calc_summary_hash_from_git.py <commit>", file=sys.stderr)
        return 2

    commit = sys.argv[1]
    paths = [p for p in list_files(commit) if should_include(p)]
    paths.sort()

    summary = hashlib.sha256()
    for p in paths:
        fh = blob_sha256(commit, p)
        summary.update(p.encode("utf-8"))
        summary.update(b":")
        summary.update(fh.encode("utf-8"))
        summary.update(b"\n")

    print(summary.hexdigest())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
