"""
vasAI Core Freeze — v1.0.0 凍結マニフェスト生成・検証
「今証明した継続性を、改修後も絶対に失わない」
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent

FREEZE_TARGETS = [
    "core/models.py",
    "core/event_store.py",
    "core/artifact_schema.py",
    "core/audit_chain.py",
    "core/governance.py",
    "movement/mocka_movement.py",
    "movement/shadow_movement.py",
    "movement/stages.py",
    "caliber/base_caliber.py",
    "caliber/example_medical.py",
    "caliber/example_finance.py",
    "test_field/reports/VASAI_OPERATION_REPORT.md",
]

FREEZE_FILE = ROOT / "vasai_core_v1_freeze.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _git_commit() -> str:
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"],
                           capture_output=True, text=True, cwd=str(ROOT))
        return r.stdout.strip()
    except Exception:
        return "unknown"


def create_freeze_manifest() -> dict:
    """全コアファイルのSHA-256を記録したマニフェストを生成。"""
    files = {}
    missing = []
    for rel in FREEZE_TARGETS:
        p = ROOT / rel
        if p.exists():
            files[rel] = {"sha256": _sha256(p), "size_bytes": p.stat().st_size}
        else:
            missing.append(rel)

    if missing:
        print(f"[WARN] Missing files: {missing}")

    manifest = {
        "vasai_version":    "1.0.0",
        "freeze_level":     "L4",
        "proof_event":      "E20260530_014",
        "created_at":       datetime.now(timezone.utc).isoformat(),
        "git_commit":       _git_commit(),
        "total_files":      len(files),
        "missing_files":    missing,
        "files":            files,
        "manifest_hash":    "",  # computed below
    }

    # マニフェスト自体のhash（filesセクションの内容から計算）
    files_str = json.dumps(files, sort_keys=True, ensure_ascii=False)
    manifest["manifest_hash"] = hashlib.sha256(files_str.encode("utf-8")).hexdigest()

    FREEZE_FILE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[OK] Freeze manifest created: {FREEZE_FILE}")
    print(f"     Files: {len(files)}/{len(FREEZE_TARGETS)}")
    print(f"     manifest_hash: {manifest['manifest_hash'][:16]}...")
    return manifest


def verify_against_freeze() -> dict:
    """現在のファイル群を凍結マニフェストと比較。"""
    if not FREEZE_FILE.exists():
        return {"error": "freeze manifest not found", "verified": False}

    manifest = json.loads(FREEZE_FILE.read_text(encoding="utf-8"))
    frozen = manifest["files"]

    unchanged = []
    changed = []
    missing = []

    for rel, info in frozen.items():
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
        else:
            current = _sha256(p)
            if current == info["sha256"]:
                unchanged.append(rel)
            else:
                changed.append({
                    "file": rel,
                    "frozen_hash": info["sha256"][:16],
                    "current_hash": current[:16],
                })

    result = {
        "verified":        len(changed) == 0 and len(missing) == 0,
        "unchanged":       len(unchanged),
        "changed":         changed,
        "missing":         missing,
        "total_frozen":    len(frozen),
        "checked_at":      datetime.now(timezone.utc).isoformat(),
        "frozen_at":       manifest.get("created_at", ""),
        "manifest_hash":   manifest.get("manifest_hash", ""),
    }

    status = "[OK] VERIFIED" if result["verified"] else "[NG] DRIFT DETECTED"
    print(f"\n{status}")
    print(f"  Unchanged : {result['unchanged']}/{result['total_frozen']} files")
    if changed:
        print(f"  Changed   : {len(changed)} files")
        for c in changed:
            print(f"    - {c['file']} ({c['frozen_hash']}... → {c['current_hash']}...)")
    if missing:
        print(f"  Missing   : {missing}")

    return result


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "create"
    if cmd == "create":
        create_freeze_manifest()
    elif cmd == "verify":
        r = verify_against_freeze()
        sys.exit(0 if r["verified"] else 1)
    else:
        print(f"Usage: python core_freeze.py [create|verify]")
        sys.exit(1)
