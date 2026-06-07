"""
AI Gate — Optimizer
構造化・見出し補完・要約自動生成
"""
import re
from dataclasses import dataclass, field


@dataclass
class OptimizeResult:
    original: str
    optimized: str
    summary: str = ""
    added_elements: list = field(default_factory=list)


def extract_summary(text: str, max_chars: int = 120) -> str:
    """
    最初の意味のある段落から要約を抽出。
    見出し・空行を除いた最初のテキストブロック。
    """
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("```"):
            if len(line) > max_chars:
                return line[:max_chars] + "…"
            return line
    return text[:max_chars] + "…" if len(text) > max_chars else text


def add_missing_heading(text: str) -> tuple[str, bool]:
    """
    見出しがない短文にH1を補完。
    最初の行が非見出しで文章が短い場合のみ適用。
    フロントマターがある場合はスキップ。
    """
    lines = text.strip().splitlines()
    if not lines:
        return text, False
    # フロントマターがある場合はスキップ
    if lines[0].startswith("---"):
        return text, False
    if lines[0].startswith("#"):
        return text, False
    # 短いコンテンツ（50行未満）で見出しがない場合のみ
    has_any_heading = any(l.startswith("#") for l in lines)
    if not has_any_heading and len(lines) < 50:
        first_sentence = lines[0][:40].rstrip("。、.，,")
        heading = f"# {first_sentence}\n\n"
        return heading + text, True
    return text, False


def normalize_headings(text: str) -> tuple[str, int]:
    """見出しレベルの正規化（H1が複数あればH2以降に降格）"""
    h1_count = len(re.findall(r"^# ", text, re.MULTILINE))
    if h1_count <= 1:
        return text, 0

    lines = text.splitlines()
    first_h1_seen = False
    result = []
    demoted = 0
    for line in lines:
        if line.startswith("# ") and not first_h1_seen:
            first_h1_seen = True
            result.append(line)
        elif line.startswith("#"):
            # 最初のH1以降のH1をH2に
            if line.startswith("# ") and first_h1_seen:
                result.append("#" + line)
                demoted += 1
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result), demoted


def add_frontmatter(text: str, ks_id: str = "", title: str = "",
                    tags: list = None) -> str:
    """Markdownフロントマターを追加（既存の場合はスキップ）"""
    if text.startswith("---"):
        return text
    tags_str = ", ".join(tags or [])
    fm = f"""---
id: {ks_id}
title: {title}
tags: [{tags_str}]
---

"""
    return fm + text


def optimize(text: str, ks_id: str = "", title: str = "",
             tags: list = None) -> OptimizeResult:
    """
    最適化パイプライン全実行。
    Returns OptimizeResult
    """
    result = OptimizeResult(original=text, optimized=text)

    # Step 1: 要約生成
    result.summary = extract_summary(text)

    # Step 2: 見出し補完
    optimized, added = add_missing_heading(result.optimized)
    if added:
        result.added_elements.append("H1見出し自動補完")
        result.optimized = optimized

    # Step 3: 見出し正規化
    optimized, demoted = normalize_headings(result.optimized)
    if demoted > 0:
        result.added_elements.append(f"重複H1を{demoted}件H2に降格")
        result.optimized = optimized

    # Step 4: フロントマター追加（ks_idがある場合）
    if ks_id:
        result.optimized = add_frontmatter(
            result.optimized, ks_id=ks_id, title=title, tags=tags or []
        )
        result.added_elements.append("フロントマター追加")

    return result


if __name__ == "__main__":
    sample = """MoCKAは知識を生むOSです。

PR-OSと連携して外部配信を担います。

## 機能一覧

- AI Gate
- Knowledge Store
- Command Center
"""
    res = optimize(sample, ks_id="KS_001", title="MoCKA概要", tags=["mocka", "overview"])
    print(res.optimized)
    print(f"\n要約: {res.summary}")
    print(f"追加要素: {res.added_elements}")
