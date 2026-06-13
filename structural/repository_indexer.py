"""
MoCKA 3.0 — Phase 1
repository_indexer.py

責務:
  Repository全体をModule単位で巡回し、
  ファイル・ディレクトリ・更新日時・ハッシュを索引化する。
出力:
  repository_index.json
"""

import os
import json
import hashlib
import datetime
from pathlib import Path

# ============================================================
# 設定: リポジトリルートとModule定義
# ============================================================

REPO_ROOT = Path(r"C:\Users\sirok\MoCKA")

MODULE_MAP = {
    "Orchestra":      ["Orchestra_Project", "PlanningCaliber/workshop/orchestra-product"],
    "Relay":          ["PlanningCaliber/workshop/Relay_Project"],
    "Memory":         ["PlanningCaliber/workshop/memory-product"],
    "PHI-OS":         ["PlanningCaliber/workshop/phl_os"],
    "MoCKA-Core":     ["mocka_caliber_server.py", "anchor_update.py", "health_check.py"],
    "PlanningCaliber":["PlanningCaliber"],
    "Runtime":        ["runtime"],
    "KnowledgeGate":  ["knowledge-gate"],
}

IGNORE_DIRS  = {".git", "node_modules", "__pycache__", ".pytest_cache", "TestProfile",
                "venv", ".venv", "dist", "build", ".DS_Store"}
IGNORE_EXTS  = {".pyc", ".pyo", ".log", ".db-wal", ".db-shm"}
MAX_FILE_MB  = 50  # これ以上は内容ハッシュをスキップ

OUTPUT_PATH  = REPO_ROOT / "structural" / "repository_index.json"

# ============================================================
# ユーティリティ
# ============================================================

def sha256_of_file(path: Path, max_mb: int = MAX_FILE_MB) -> str:
    """ファイルのSHA-256を返す。大きすぎる場合は 'SKIP_LARGE' を返す。"""
    try:
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_mb:
            return "SKIP_LARGE"
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]  # 先頭16桁で十分
    except Exception:
        return "ERROR"


def file_info(path: Path) -> dict:
    """ファイル1件の情報を返す。"""
    try:
        stat = path.stat()
        return {
            "path":     str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "name":     path.name,
            "ext":      path.suffix.lower(),
            "size_kb":  round(stat.st_size / 1024, 2),
            "mtime":    datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "sha256":   sha256_of_file(path),
        }
    except Exception as e:
        return {"path": str(path), "error": str(e)}


def scan_dir(root: Path) -> list[dict]:
    """ディレクトリを再帰走査してファイル情報リストを返す。"""
    results = []
    if not root.exists():
        return results
    for item in root.rglob("*"):
        # 無視ディレクトリ判定
        if any(ig in item.parts for ig in IGNORE_DIRS):
            continue
        if not item.is_file():
            continue
        if item.suffix.lower() in IGNORE_EXTS:
            continue
        results.append(file_info(item))
    return results


# ============================================================
# メイン: Module単位索引生成
# ============================================================

def build_index() -> dict:
    modules = []
    indexed_paths = set()

    for module_name, roots in MODULE_MAP.items():
        files = []
        for rel in roots:
            target = REPO_ROOT / rel
            if target.is_dir():
                for f in scan_dir(target):
                    if f["path"] not in indexed_paths:
                        files.append(f)
                        indexed_paths.add(f["path"])
            elif target.is_file():
                info = file_info(target)
                if info["path"] not in indexed_paths:
                    files.append(info)
                    indexed_paths.add(info["path"])

        modules.append({
            "name":       module_name,
            "roots":      roots,
            "file_count": len(files),
            "files":      files,
        })

    index = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "repo_root":    str(REPO_ROOT),
        "module_count": len(modules),
        "modules":      modules,
    }
    return index


def main():
    print("[repository_indexer] 索引生成開始...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    index = build_index()
    with open(OUTPUT_PATH, "w", encoding="utf-8-sig") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    total = sum(m["file_count"] for m in index["modules"])
    print(f"[repository_indexer] 完了: {total} files / {index['module_count']} modules")
    print(f"[repository_indexer] 出力: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
