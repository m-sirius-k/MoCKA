SPEC_VERSION = "1.0"
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# note: exclusions (stable fixed-point)
EXCLUDE_FILES = {
    "governance/anchor_record.json",
    "governance/anchor_bundle.json",
}

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    # note: WSL venv created on Windows mount includes Linux-style executables/symlinks
    # Windows Python cannot open some of them (Errno 22). Exclude from summary domain.
    ".wsl_ots_venv",
}

def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()

    # directory-based exclusion
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True

    # file-based exclusion
    if rel in EXCLUDE_FILES:
        return True

    # secret key exclusion
    if rel.endswith(".private.pem"):
        return True

    return False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files():
    files = []
    for root, dirs, filenames in os.walk(ROOT):
        root_path = Path(root)

        # remove excluded dirs in-place (deterministic)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for name in filenames:
            full = root_path / name
            if is_excluded(full):
                continue
            # note: only hash regular files
            if not full.is_file():
                continue
            files.append(full)

    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def main():
    files = collect_files()
    summary_hasher = hashlib.sha256()

    for file_path in files:
        rel = file_path.relative_to(ROOT).as_posix()
        file_hash = sha256_file(file_path)

        summary_hasher.update(rel.encode("utf-8"))
        summary_hasher.update(b":")
        summary_hasher.update(file_hash.encode("utf-8"))
        summary_hasher.update(b"\n")

    print(summary_hasher.hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
