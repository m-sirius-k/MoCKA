"""
AI Gate — Proofreader
誤字脱字・表記統一・基本校正
"""
import re
from dataclasses import dataclass, field


@dataclass
class ProofreadResult:
    original: str
    corrected: str
    corrections: list = field(default_factory=list)
    correction_count: int = 0


# 表記統一ルール: (検索パターン, 置換後, 説明)
NORMALIZE_RULES = [
    (r"ＭｏＣＫＡ", "MoCKA", "全角→半角"),
    (r"ｗｏｒｄｐｒｅｓｓ", "WordPress", "表記統一"),
    (r"Ｘ\s*[\(（]ツイッター[\)）]", "X (Twitter)", "SNS表記統一"),
    (r"（", "(", "括弧統一"),
    (r"）", ")", "括弧統一"),
    (r"　", " ", "全角スペース→半角"),
    (r"！", "！", "感嘆符統一（日本語文脈保持）"),
    (r"(\d)　(\d)", r"\1 \2", "数字間全角スペース"),
]

# よくある誤字ペア (誤, 正)
TYPO_DICT = {
    "確立する": None,        # 文脈依存のためスキップ
    "既存の機能を活用": None,
}


def normalize_whitespace(text: str) -> tuple[str, int]:
    """改行・スペースの正規化"""
    original = text
    # 連続空行を1行に
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 行末スペース除去
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    count = sum(1 for a, b in zip(original.splitlines(), text.splitlines()) if a != b)
    return text, count


def apply_normalize_rules(text: str) -> tuple[str, list]:
    """表記統一ルールを適用"""
    corrections = []
    for pattern, replacement, desc in NORMALIZE_RULES:
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, replacement, text)
            corrections.append({
                "type": "normalize",
                "description": desc,
                "count": len(matches)
            })
    return text, corrections


def check_structure(text: str) -> list:
    """構造チェック（見出し・段落）"""
    issues = []
    lines = text.splitlines()

    # 見出しが全くない長文チェック
    has_heading = any(line.startswith("#") for line in lines)
    if len(lines) > 30 and not has_heading:
        issues.append({
            "type": "structure",
            "severity": "warning",
            "message": "長文に見出しがありません。構造化を推奨します。"
        })

    # 空のセクション検出
    for i, line in enumerate(lines):
        if line.startswith("#") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if not next_line or next_line.startswith("#"):
                issues.append({
                    "type": "structure",
                    "severity": "info",
                    "message": f"空のセクション検出: 行{i+1} '{line.strip()}'"
                })

    return issues


def proofread(text: str) -> ProofreadResult:
    """
    メイン校正処理。
    Returns ProofreadResult with corrected text and correction log.
    """
    result = ProofreadResult(original=text, corrected=text)

    # Step 1: 空白正規化
    corrected, ws_count = normalize_whitespace(result.corrected)
    if ws_count > 0:
        result.corrections.append({
            "type": "whitespace",
            "description": "空白・改行の正規化",
            "count": ws_count
        })
        result.correction_count += ws_count

    # Step 2: 表記統一
    corrected, norm_corrections = apply_normalize_rules(corrected)
    result.corrections.extend(norm_corrections)
    result.correction_count += sum(c["count"] for c in norm_corrections)

    # Step 3: 構造チェック（修正はしない、ログのみ）
    structure_issues = check_structure(corrected)
    for issue in structure_issues:
        result.corrections.append(issue)

    result.corrected = corrected
    return result


if __name__ == "__main__":
    sample = """# テスト記事

MoCKAは知識を生むOSです。
Ｘ（ツイッター）でも発信しています。


詳細はwordpressを参照。
"""
    res = proofread(sample)
    print("=== 校正結果 ===")
    print(res.corrected)
    print(f"\n修正件数: {res.correction_count}")
    for c in res.corrections:
        print(f"  - {c}")
