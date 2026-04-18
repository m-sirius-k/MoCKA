"""
Sanitizer_Gate.py
MoCKA No-Token Architecture - Phase 1
役割: 全入力ファイルのBOM除去・UTF-8強制検証
API通信: 一切なし (0円)
E20260418_007
"""

import os
import sys
from pathlib import Path


BOM = b'\xef\xbb\xbf'  # UTF-8 BOM (EF BB BF)


class SanitizerGate:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.stats = {"processed": 0, "bom_removed": 0, "rejected": 0}

    def _log(self, msg: str):
        if self.verbose:
            print(f"[SANITIZER] {msg}")

    def sanitize_file(self, path: Path) -> bool:
        """
        1ファイルを検問する。
        - BOMをバイナリレベルで除去
        - UTF-8以外は拒絶（Falseを返す）
        - 正常ならTrueを返す
        """
        path = Path(path)
        if not path.exists():
            self._log(f"ERROR: ファイルが存在しない -> {path}")
            return False

        # バイナリで読み込み
        raw = path.read_bytes()

        # BOM検出・除去
        had_bom = raw.startswith(BOM)
        if had_bom:
            raw = raw[3:]  # BOM3バイトを物理削除
            self._log(f"BOM除去: {path.name}")
            self.stats["bom_removed"] += 1

        # UTF-8検証
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as e:
            self._log(f"REJECTED (UTF-8違反): {path.name} -> {e}")
            self.stats["rejected"] += 1
            return False

        # BOMがあった場合のみ書き戻し
        if had_bom:
            path.write_bytes(raw)

        self.stats["processed"] += 1
        return True

    def sanitize_dir(self, dir_path: Path, extensions: list = None) -> dict:
        """
        ディレクトリ内の全ファイルを検問する。
        extensions: 対象拡張子リスト（例: ['.txt', '.md', '.json', '.csv']）
        戻り値: {ok: [Path], rejected: [Path]}
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            self._log(f"ERROR: ディレクトリが存在しない -> {dir_path}")
            return {"ok": [], "rejected": []}

        extensions = extensions or ['.txt', '.md', '.json', '.csv', '.py']
        results = {"ok": [], "rejected": []}

        for f in sorted(dir_path.rglob("*")):
            if f.is_file() and f.suffix in extensions:
                ok = self.sanitize_file(f)
                if ok:
                    results["ok"].append(f)
                else:
                    results["rejected"].append(f)

        self._log(f"完了 — 処理: {self.stats['processed']} / BOM除去: {self.stats['bom_removed']} / 拒絶: {self.stats['rejected']}")
        return results

    def sanitize_bytes(self, raw: bytes) -> tuple:
        """
        バイト列を直接検問する（ファイルなし用途）。
        戻り値: (sanitized_bytes, had_bom: bool, is_valid_utf8: bool)
        """
        had_bom = raw.startswith(BOM)
        if had_bom:
            raw = raw[3:]
        try:
            raw.decode("utf-8")
            return raw, had_bom, True
        except UnicodeDecodeError:
            return raw, had_bom, False


# 単体実行
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python Sanitizer_Gate.py <ファイルまたはディレクトリ>")
        sys.exit(1)

    target = Path(sys.argv[1])
    gate = SanitizerGate(verbose=True)

    if target.is_file():
        ok = gate.sanitize_file(target)
        sys.exit(0 if ok else 1)
    elif target.is_dir():
        results = gate.sanitize_dir(target)
        sys.exit(0 if not results["rejected"] else 1)
    else:
        print(f"ERROR: 対象が見つからない -> {target}")
        sys.exit(1)
