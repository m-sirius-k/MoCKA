import hashlib
import subprocess

COMMIT = "18058140230fa4f42498e46e283261f7cd6c4de6"

EXCLUDE_PATHS = {
    "governance/anchor_record.json",
}
EXCLUDE_DIRS = {".git", "__pycache__"}
EXCLUDE_SUFFIXES = {".private.pem"}

def git_bytes(args):
    p = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", errors="replace"))
    return p.stdout

def list_paths():
    out = git_bytes(["ls-tree", "-r", "--name-only", COMMIT]).decode("utf-8", errors="replace")
    return [s.strip() for s in out.splitlines() if s.strip()]

def should_include(rel: str) -> bool:
    if rel in EXCLUDE_PATHS:
        return False
    parts = rel.split("/")
    if any(part in EXCLUDE_DIRS for part in parts):
        return False
    name = parts[-1]
    if any(name.endswith(suf) for suf in EXCLUDE_SUFFIXES):
        return False
    return True

def main() -> int:
    h = hashlib.sha256()

    paths = [p for p in list_paths() if should_include(p)]
    paths.sort()

    for rel in paths:
        blob = git_bytes(["show", f"{COMMIT}:{rel}"])
        h.update(rel.encode("utf-8"))
        h.update(b"\n")
        h.update(blob)
        h.update(b"\n")

    print(h.hexdigest())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
