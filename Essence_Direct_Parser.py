"""
Essence_Direct_Parser.py
MoCKA No-Token Architecture - Phase 2
役割: ::I:: / ::P:: / ::O:: タグを正規表現で物理抽出 -> lever_essence.json更新
API通信: 一切なし (0円)
MoCKA-Language v1.0 準拠
E20260418_007
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

# Sanitizer_Gate をインポート（同一ディレクトリ想定）
sys.path.insert(0, str(Path(__file__).parent))
from Sanitizer_Gate import SanitizerGate


# ============================================================
# MoCKA-Language v1.0 タグ定義
# ::I:: ... ::END::  -> INCIDENT
# ::P:: ... ::END::  -> PHILOSOPHY
# ::O:: ... ::END::  -> OPERATION
# ============================================================
TAG_PATTERNS = {
    "INCIDENT":   re.compile(r'::I::\s*(.*?)\s*::END::', re.DOTALL),
    "PHILOSOPHY": re.compile(r'::P::\s*(.*?)\s*::END::', re.DOTALL),
    "OPERATION":  re.compile(r'::O::\s*(.*?)\s*::END::', re.DOTALL),
}

DEFAULT_ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")


class EssenceDirectParser:

    def __init__(self, essence_path: Path = None, verbose: bool = True):
        self.essence_path = Path(essence_path) if essence_path else DEFAULT_ESSENCE_PATH
        self.verbose = verbose
        self.gate = SanitizerGate(verbose=verbose)

    def _log(self, msg: str):
        if self.verbose:
            print(f"[PARSER] {msg}")

    def extract_from_text(self, text: str) -> dict:
        """
        テキストからMoCKA-Language v1.0タグを抽出する。
        APIは一切使わない。正規表現のみ。
        戻り値: {"INCIDENT": [...], "PHILOSOPHY": [...], "OPERATION": [...]}
        """
        results = {k: [] for k in TAG_PATTERNS}
        for kind, pattern in TAG_PATTERNS.items():
            matches = pattern.findall(text)
            for m in matches:
                cleaned = m.strip()
                if cleaned:
                    results[kind].append(cleaned)
                    self._log(f"抽出 [{kind}]: {cleaned[:60]}...")
        return results

    def extract_from_file(self, file_path: Path) -> dict:
        """
        ファイルからタグを抽出する。
        Sanitizer_Gateを通してBOM除去・UTF-8検証を先に実施。
        """
        file_path = Path(file_path)

        # 検問
        ok = self.gate.sanitize_file(file_path)
        if not ok:
            self._log(f"BLOCKED (検問失敗): {file_path.name}")
            return {k: [] for k in TAG_PATTERNS}

        text = file_path.read_text(encoding="utf-8")
        self._log(f"解析開始: {file_path.name} ({len(text)}文字)")
        return self.extract_from_text(text)

    def extract_from_dir(self, dir_path: Path, extensions: list = None) -> dict:
        """
        ディレクトリ内の全ファイルからタグを抽出して統合する。
        """
        extensions = extensions or ['.txt', '.md']
        merged = {k: [] for k in TAG_PATTERNS}
        dir_path = Path(dir_path)

        for f in sorted(dir_path.rglob("*")):
            if f.is_file() and f.suffix in extensions:
                result = self.extract_from_file(f)
                for kind in TAG_PATTERNS:
                    merged[kind].extend(result[kind])

        return merged

    def update_essence(self, extracted: dict) -> bool:
        """
        抽出結果をlever_essence.jsonに直接書き込む（Append）。
        CSVを介さない。APIを介さない。
        """
        # 既存ファイル読み込み
        if self.essence_path.exists():
            try:
                existing = json.loads(self.essence_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._log("WARNING: essence.jsonが壊れている。新規作成します。")
                existing = {}
        else:
            existing = {}

        updated = False
        timestamp = datetime.now().isoformat()

        for kind in ["INCIDENT", "PHILOSOPHY", "OPERATION"]:
            items = extracted.get(kind, [])
            if not items:
                continue

            # 最新の1件をエッセンスとして上書き（既存の仕様に合わせる）
            # 複数ある場合は結合
            new_text = " / ".join(items)
            if existing.get(kind) != new_text:
                existing[kind] = new_text
                existing[f"{kind}_updated"] = timestamp
                self._log(f"更新 [{kind}]: {new_text[:80]}")
                updated = True

        if updated:
            # 親ディレクトリが存在しない場合は作成
            self.essence_path.parent.mkdir(parents=True, exist_ok=True)
            self.essence_path.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            self._log(f"lever_essence.json 更新完了 -> {self.essence_path}")
        else:
            self._log("変更なし。更新をスキップ。")

        return updated

    def process(self, source) -> bool:
        """
        ファイル・ディレクトリ・テキスト文字列を受け取り、
        抽出 -> lever_essence.json更新を一発で実行する。
        """
        source = Path(source) if not isinstance(source, str) else source

        if isinstance(source, Path) and source.is_dir():
            extracted = self.extract_from_dir(source)
        elif isinstance(source, Path) and source.is_file():
            extracted = self.extract_from_file(source)
        else:
            # 文字列として直接処理
            extracted = self.extract_from_text(str(source))

        total = sum(len(v) for v in extracted.values())
        if total == 0:
            self._log("タグが見つからなかった。::I:: ::P:: ::O:: タグを確認してください。")
            return False

        return self.update_essence(extracted)


# ============================================================
# 使用例（README）
# ============================================================
USAGE = """
MoCKA-Language v1.0 タグ記法:

  ::I::
  APIトークン枯渇インシデント。BOM混入が原因。Sanitizer_Gate導入で解消。
  ::END::

  ::P::
  AIを信じるな、システムで縛れ。外部推論に依存しない構造が10年安定の条件。
  ::END::

  ::O::
  Sanitizer_Gate.py -> Essence_Direct_Parser.py -> lever_essence.json の順で実行。
  ::END::

実行:
  python Essence_Direct_Parser.py <ファイルまたはディレクトリ>

  # テキスト直接入力（パイプ）:
  echo "::I:: 障害発生 ::END::" | python Essence_Direct_Parser.py -
"""


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)

    source = sys.argv[1]

    # essence_path上書き（オプション）
    essence_path = None
    if len(sys.argv) >= 3:
        essence_path = Path(sys.argv[2])

    parser = EssenceDirectParser(essence_path=essence_path, verbose=True)

    if source == "-":
        # 標準入力から読む
        text = sys.stdin.read()
        extracted = parser.extract_from_text(text)
        ok = parser.update_essence(extracted)
    else:
        ok = parser.process(Path(source))

    sys.exit(0 if ok else 1)
