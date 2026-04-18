"""
watchdog_mocka_v2.py
MoCKA No-Token Architecture - Phase 1 (watchdog修正)
役割: ./input/ 監視 -> Sanitizer_Gate -> Essence_Direct_Parser
廃止: batch_ecol2.py への呼び出しを完全切断
API通信: 一切なし (0円)
E20260418_007
"""

import time
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

# 同一ディレクトリからインポート
sys.path.insert(0, str(Path(__file__).parent))
from Sanitizer_Gate import SanitizerGate
from Essence_Direct_Parser import EssenceDirectParser
from language_detector import LanguageDetector
try:
    from essence_condenser import EssenceCondenser
    _has_condenser = True
except Exception:
    _has_condenser = False


# ============================================================
# 設定
# ============================================================
WATCH_DIR     = Path("C:/Users/sirok/MoCKA/input")          # 監視対象
EVENTS_CSV    = Path("C:/Users/sirok/MoCKA/data/events.csv") # ログ（読み取り専用化）
ESSENCE_PATH  = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
PROCESSED_LOG = Path("C:/Users/sirok/MoCKA/data/watchdog_processed.json")
WATCH_EXTS    = {'.txt', '.md'}
POLL_INTERVAL = 10  # 秒


class WatchdogMoCKA:

    def __init__(self):
        self.gate      = SanitizerGate(verbose=True)
        self.parser    = EssenceDirectParser(essence_path=ESSENCE_PATH, verbose=True)
        self.detector  = LanguageDetector()
        self.condenser = EssenceCondenser(essence_path=ESSENCE_PATH) if _has_condenser else None
        self.seen      = self._load_processed()
        self._ensure_dirs()

    def _log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WATCHDOG {ts}] {msg}")

    def _ensure_dirs(self):
        WATCH_DIR.mkdir(parents=True, exist_ok=True)

    def _load_processed(self) -> dict:
        """処理済みファイルのハッシュ辞書を読み込む"""
        if PROCESSED_LOG.exists():
            try:
                return json.loads(PROCESSED_LOG.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_processed(self):
        PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
        PROCESSED_LOG.write_text(
            json.dumps(self.seen, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _file_hash(self, path: Path) -> str:
        """ファイル内容のSHA-256ハッシュ（変更検知用）"""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _append_events_log(self, file_path: Path, result: str, level: str = "INFO", score: float = 0):
        """
        events.csvに処理ログを追記。
        danger_levelとscoreも記録。
        """
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f'{ts},watchdog,{file_path.name},{result},E20260418_007,no_api,danger_level={level},score={score:.1f}\n'
        try:
            with open(EVENTS_CSV, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            self._log(f"WARNING: events.csv書き込み失敗 -> {e}")

    def process_file(self, path: Path):
        """
        1ファイルの処理フロー:
        [Sanitizer_Gate] -> [LanguageDetector] -> [Essence_Direct_Parser] -> [lever_essence.json]
        """
        self._log(f"検知: {path.name}")

        # Phase 1: 検問
        ok = self.gate.sanitize_file(path)
        if not ok:
            self._log(f"BLOCKED: {path.name}")
            self._append_events_log(path, "BLOCKED", "INFO", 0)
            return

        # Phase 2: 言語危険度解析
        detection = self.detector.analyze_file(path)
        level = detection.get("level", "INFO")
        score = detection.get("score", 0)
        matched = detection.get("matched_words", [])

        if matched:
            self._log(f"[{level}] スコア={score} 検知語={matched[:5]}")

        # Phase 3: タグ抽出（::I:: ::P:: ::O::）
        updated = self.parser.process(path)

        # Phase 4: 濃縮 → essence更新（condenser経由）
        if self.condenser:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                self.condenser.condense_from_text(text, source="watchdog")
            except Exception as e:
                self._log(f"CONDENSER ERROR: {e}")

        result = "UPDATED" if updated else "NO_CHANGE"
        self._log(f"{result}: {path.name}")
        self._append_events_log(path, result, level, score)

        # 処理済みとして記録
        self.seen[str(path)] = self._file_hash(path)
        self._save_processed()

    def scan(self):
        """監視ディレクトリをスキャンして新規・変更ファイルを処理する"""
        for f in sorted(WATCH_DIR.rglob("*")):
            if not f.is_file() or f.suffix not in WATCH_EXTS:
                continue
            try:
                current_hash = self._file_hash(f)
                if self.seen.get(str(f)) != current_hash:
                    self.process_file(f)
            except Exception as e:
                self._log(f"ERROR: {f.name} -> {e}")

    def run(self):
        """メインループ"""
        self._log(f"起動 — 監視: {WATCH_DIR} / インターバル: {POLL_INTERVAL}秒")
        self._log("batch_ecol2.py: 切断済み / API通信: ゼロ / D_i = 1")
        while True:
            try:
                self.scan()
            except KeyboardInterrupt:
                self._log("停止。")
                break
            except Exception as e:
                self._log(f"SCAN ERROR: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    WatchdogMoCKA().run()
