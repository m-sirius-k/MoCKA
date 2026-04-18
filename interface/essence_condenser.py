"""
essence_condenser.py
MoCKA Knowledge Pipeline v2.0 — 濃縮層
役割: 抽出結果をessenceフィルターに通し、純粋な知識だけを取り出す
      CSV → 抽出 → 【濃縮】 → essence
API通信: なし (0円)
E20260418_018
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
try:
    from language_detector import LanguageDetector
    from incident_learner import IncidentLearner
    _detector = LanguageDetector()
    _learner  = IncidentLearner()
    _has_tools = True
except Exception as e:
    _has_tools = False
    print(f"[CONDENSER] WARNING: {e}")

ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")

# ============================================================
# 除去対象: 定型文・ノイズパターン
# ============================================================
NOISE_PATTERNS = [
    # AIの定型挨拶
    r"^(はい|わかりました|承知しました|了解です|ありがとうございます)[。！\s]",
    r"^(以下に|次に|まず|それでは|では)[、。\s]",
    r"(お役に立てれば|何かあれば|お気軽に)[^\n]*",
    # markdown記号
    r"#{1,6}\s",
    r"\*{1,3}([^*]+)\*{1,3}",
    # URLのみの行
    r"^https?://\S+$",
    # 空白・区切り線
    r"^[-=]{3,}$",
    r"^\s*$",
]

# 最小有効文字数
MIN_LENGTH = 10

# essenceの3軸
AXES = ["INCIDENT", "PHILOSOPHY", "OPERATION"]


class EssenceCondenser:

    def __init__(self, essence_path: Path = None):
        self.essence_path = essence_path or ESSENCE_PATH
        self.existing = self._load_existing()

    def _load_existing(self) -> dict:
        """既存essenceを読み込む"""
        if self.essence_path.exists():
            try:
                return json.loads(self.essence_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _remove_noise(self, text: str) -> str:
        """定型文・ノイズを除去して重要部分だけを取り出す"""
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # ノイズパターン除去
            is_noise = False
            for pattern in NOISE_PATTERNS:
                if re.search(pattern, line):
                    is_noise = True
                    break
            if not is_noise and len(line) >= MIN_LENGTH:
                # markdown記号を除去
                line = re.sub(r'\*{1,3}', '', line)
                line = re.sub(r'#{1,6}\s', '', line)
                line = line.strip()
                if len(line) >= MIN_LENGTH:
                    cleaned.append(line)
        return "\n".join(cleaned)

    def _is_duplicate(self, text: str, axis: str) -> bool:
        """既存essenceと重複するか判定"""
        existing_text = self.existing.get(axis, "")
        if not existing_text:
            return False
        # 先頭50文字で重複判定
        return text[:50] in existing_text

    def _select_best(self, candidates: list, axis: str) -> str:
        """
        複数の候補から最も重要な1件を選ぶ。
        選定基準:
        1. 危険度スコアが高い（INCIDENTは特に）
        2. 5W1H要素を多く含む
        3. 文字数が適切（50〜300文字）
        """
        if not candidates:
            return ""
        if len(candidates) == 1:
            return candidates[0]["text"]

        def score(c):
            t = c["text"]
            s = 0
            # 文字数スコア（50〜300文字が最適）
            if 50 <= len(t) <= 300:
                s += 3
            elif len(t) < 50:
                s += 1
            # 危険度スコア
            s += c.get("danger_score", 0) * 0.1
            # 5W1H要素
            for kw in ["なぜ", "どこ", "いつ", "誰が", "何を", "どうやって",
                       "原因", "対策", "結果", "完了", "修正"]:
                if kw in t:
                    s += 1
            return s

        candidates.sort(key=score, reverse=True)
        return candidates[0]["text"]

    def condense(self, extracted: dict) -> dict:
        """
        抽出結果を濃縮してessenceを更新する。
        extracted: {"INCIDENT": ["text1","text2",...], "PHILOSOPHY": [...], "OPERATION": [...]}
        """
        updated = {}
        timestamp = datetime.now().isoformat()

        for axis in AXES:
            items = extracted.get(axis, [])
            if not items:
                continue

            # Step1: ノイズ除去
            cleaned = []
            for item in items:
                c = self._remove_noise(item)
                if c and len(c) >= MIN_LENGTH:
                    # 危険度スコアを付与
                    danger_score = 0
                    if _has_tools:
                        d = _detector.analyze(c)
                        danger_score = d.get("score", 0)
                        # INCIDENTでCRITICAL/DANGERは即学習
                        if axis == "INCIDENT" and d.get("level") in ("CRITICAL", "DANGER"):
                            _learner.learn(c, incident_id=f"condenser_{timestamp}")
                    cleaned.append({"text": c, "danger_score": danger_score})

            if not cleaned:
                continue

            # Step2: 重複排除
            unique = [c for c in cleaned if not self._is_duplicate(c["text"], axis)]
            if not unique:
                continue

            # Step3: 最重要1件を選択
            best = self._select_best(unique, axis)
            if not best:
                continue

            # Step4: essenceを更新
            self.existing[axis] = best
            self.existing[f"{axis}_updated"] = timestamp
            self.existing[f"{axis}_source_count"] = len(unique)
            updated[axis] = best
            print(f"[CONDENSER] {axis} 更新: {best[:60]}...")

        if updated:
            self.essence_path.parent.mkdir(parents=True, exist_ok=True)
            self.essence_path.write_text(
                json.dumps(self.existing, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"[CONDENSER] lever_essence.json 更新完了 ({len(updated)}軸)")

        return {
            "updated_axes": list(updated.keys()),
            "updated_count": len(updated),
            "timestamp": timestamp
        }

    def condense_from_text(self, text: str, source: str = "manual") -> dict:
        """
        生テキストを直接受け取って濃縮→essence更新する。
        watchdogやraw_processorから呼び出される。
        """
        # ノイズ除去
        cleaned = self._remove_noise(text)
        if not cleaned:
            return {"status": "EMPTY"}

        # 分類
        if _has_tools:
            d = _detector.analyze(cleaned)
            level = d.get("level", "INFO")
            # essence_classifierのclassify関数を使う
            try:
                from essence_classifier import classify
                axis = classify(cleaned)
            except Exception:
                axis = "OPERATION"
        else:
            axis = "OPERATION"

        return self.condense({axis: [cleaned]})


# ============================================================
# 全自動パイプライン統合関数
# ============================================================
def run_pipeline(raw_text: str, source: str = "watchdog") -> dict:
    """
    CSV生テキスト → 抽出 → 濃縮 → essence
    の全工程を1関数で実行する。
    """
    from Sanitizer_Gate import SanitizerGate

    # Step1: BOM除去・サニタイズ
    gate = SanitizerGate(verbose=False)
    raw_bytes, had_bom, is_valid = gate.sanitize_bytes(raw_text.encode("utf-8"))
    if not is_valid:
        return {"status": "SANITIZE_FAILED"}
    clean_text = raw_bytes.decode("utf-8")

    # Step2: 言語危険度判定
    detection = _detector.analyze(clean_text) if _has_tools else {}

    # Step3: 濃縮→essence更新
    condenser = EssenceCondenser()
    result = condenser.condense_from_text(clean_text, source)

    # Step4: インシデントなら学習
    if _has_tools and detection.get("level") in ("DANGER", "CRITICAL"):
        _learner.learn(clean_text)

    return {
        "status": "OK",
        "danger_level": detection.get("level", "INFO"),
        "condense_result": result
    }


# ============================================================
# 単体テスト
# ============================================================
if __name__ == "__main__":
    condenser = EssenceCondenser(essence_path=Path("/tmp/test_condense_essence.json"))

    print("=== essence_condenser.py テスト ===\n")

    # テスト1: ノイズ除去
    noisy = """はい、承知しました。以下に結果をお示しします。

    APIトークン枯渇インシデント。$50消えた。BOM混入が根本原因。
    Sanitizer_Gateで解消済み。再発防止策: バイナリモードでBOM確認必須。

    何かあればお気軽にどうぞ。"""

    print("【ノイズ除去テスト】")
    cleaned = condenser._remove_noise(noisy)
    print(f"  Before: {len(noisy)}文字")
    print(f"  After:  {len(cleaned)}文字")
    print(f"  内容: {cleaned[:80]}")
    print()

    # テスト2: 濃縮
    print("【濃縮テスト】")
    extracted = {
        "INCIDENT": [
            "APIトークン枯渇インシデント。BOM混入が根本原因。Sanitizer_Gateで解消。",
            "はい、承知しました。エラーが発生しました。",
            "batch_ecol2.pyのD_i=4以上の増幅が$50消失の直接原因。No-Token Architectureで解消。"
        ],
        "PHILOSOPHY": [
            "AIを信じるな、システムで縛れ。失敗は資産になる。",
        ],
        "OPERATION": [
            "python watchdog_mocka_v2.py で監視開始。BOMゼロ・API通信ゼロ・D_i=1。"
        ]
    }

    result = condenser.condense(extracted)
    print(f"  更新軸: {result['updated_axes']}")
    print(f"  更新数: {result['updated_count']}")
