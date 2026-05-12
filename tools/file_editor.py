"""
MoCKA File Editor v1.0
======================
TODO_121: ファイル編集運用制度化 — PowerShell文字列操作禁止・Python統一

【制度的根拠】
- PowerShellのSet-Content/Out-File/-replaceは文字化け・BOM混入の根本原因
- 2026-05-01: app.py修正作業で多発 → Python統一で解消確認済み
- 本ツールはMoCKAの全ファイル編集の唯一の公式経路

【使用法】
  python file_editor.py read <path>
  python file_editor.py write <path> <content_file>
  python file_editor.py replace <path> <old_str> <new_str>
  python file_editor.py replace_file <path> <old_file> <new_file>
  python file_editor.py append <path> <content>
  python file_editor.py backup <path>
  python file_editor.py verify <path>
"""

import sys
import os
import shutil
import hashlib
import datetime
import json

ENCODING = "utf-8"
BACKUP_DIR = "C:/Users/sirok/MoCKA/data/file_edit_backups"


def _timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _log(action, path, result, detail=""):
    log_path = "C:/Users/sirok/MoCKA/data/file_edit_log.jsonl"
    entry = {
        "ts": datetime.datetime.now().isoformat(),
        "action": action,
        "path": path,
        "result": result,
        "detail": detail
    }
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding=ENCODING) as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def backup(path):
    """バックアップ作成"""
    if not os.path.exists(path):
        print(f"[ERROR] ファイルが存在しません: {path}")
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    fname = os.path.basename(path)
    ts = _timestamp()
    bak_path = os.path.join(BACKUP_DIR, f"{fname}.{ts}.bak")
    shutil.copy2(path, bak_path)
    print(f"[BACKUP] {bak_path}")
    _log("backup", path, "ok", bak_path)
    return bak_path


def read(path):
    """ファイル読み込み（BOM自動除去）"""
    if not os.path.exists(path):
        print(f"[ERROR] ファイルが存在しません: {path}")
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    print(content)
    _log("read", path, "ok")
    return content


def write(path, content_file):
    """content_fileの内容をpathに書き込む（UTF-8・BOMなし）"""
    if not os.path.exists(content_file):
        print(f"[ERROR] content_fileが存在しません: {content_file}")
        return False
    with open(content_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
    # BOM除去確認
    if content.startswith("\ufeff"):
        content = content[1:]
        print("[WARN] BOM検出 → 除去済み")
    backup(path) if os.path.exists(path) else None
    with open(path, "w", encoding=ENCODING, newline="\n") as f:
        f.write(content)
    sha = _sha256(path)
    print(f"[WRITE OK] {path} sha256_prefix={sha}")
    _log("write", path, "ok", f"sha256={sha}")
    return True


def replace(path, old_str, new_str):
    """文字列置換（UTF-8保証）"""
    if not os.path.exists(path):
        print(f"[ERROR] ファイルが存在しません: {path}")
        return False
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    if old_str not in content:
        print(f"[ERROR] 対象文字列が見つかりません: {repr(old_str[:50])}")
        return False
    count = content.count(old_str)
    backup(path)
    new_content = content.replace(old_str, new_str)
    with open(path, "w", encoding=ENCODING, newline="\n") as f:
        f.write(new_content)
    print(f"[REPLACE OK] {count}箇所置換 → {path}")
    _log("replace", path, "ok", f"count={count}")
    return True


def replace_file(path, old_file, new_file):
    """ファイルから old/new を読み込んで置換"""
    with open(old_file, "r", encoding="utf-8-sig") as f:
        old_str = f.read()
    with open(new_file, "r", encoding="utf-8-sig") as f:
        new_str = f.read()
    return replace(path, old_str, new_str)


def append(path, content):
    """末尾追記（UTF-8）"""
    backup(path) if os.path.exists(path) else None
    with open(path, "a", encoding=ENCODING, newline="\n") as f:
        f.write(content)
    print(f"[APPEND OK] {path}")
    _log("append", path, "ok")
    return True


def verify(path):
    """UTF-8整合性チェック・BOM検出"""
    if not os.path.exists(path):
        print(f"[ERROR] ファイルが存在しません: {path}")
        return False
    issues = []
    # BOMチェック
    with open(path, "rb") as f:
        raw = f.read(3)
    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append("BOM検出 (UTF-8 with BOM)")
    # UTF-8デコードチェック
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError as e:
        issues.append(f"UTF-8デコードエラー: {e}")
    sha = _sha256(path)
    size = os.path.getsize(path)
    if issues:
        for i in issues:
            print(f"[WARN] {i}")
        print(f"[VERIFY WARN] {path} size={size} sha256={sha}")
        _log("verify", path, "warn", "|".join(issues))
        return False
    else:
        print(f"[VERIFY OK] {path} size={size} sha256={sha} UTF-8クリーン")
        _log("verify", path, "ok", f"sha256={sha}")
        return True


def usage():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "read" and len(sys.argv) == 3:
        read(sys.argv[2])
    elif cmd == "write" and len(sys.argv) == 4:
        write(sys.argv[2], sys.argv[3])
    elif cmd == "replace" and len(sys.argv) == 5:
        replace(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "replace_file" and len(sys.argv) == 5:
        replace_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "append" and len(sys.argv) == 4:
        append(sys.argv[2], sys.argv[3])
    elif cmd == "backup" and len(sys.argv) == 3:
        backup(sys.argv[2])
    elif cmd == "verify" and len(sys.argv) == 3:
        verify(sys.argv[2])
    else:
        usage()
        sys.exit(1)
