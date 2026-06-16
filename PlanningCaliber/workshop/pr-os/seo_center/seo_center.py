"""
SEO-CENTER — PR-OS 意味検索最適化レイヤー（中核モジュール）

入力: AI Gate出力（title, summary, confirmed_text, tags, category）
出力: SEOResult（html, json_ld, slug, description, seo_score, intent, targets）
"""
import re
from dataclasses import dataclass, field
from typing import Optional

from .html_generator import HTMLGenerator
from .distribution_router import DistributionRouter


# ── SEO スコアリング定数 ──────────────────────────
_MIN_WORDS_FOR_COVERAGE = 100   # 意味カバレッジ最低語数
_IDEAL_DESCRIPTION_LEN  = (50, 160)  # metaディスクリプション理想文字数


@dataclass
class SEOResult:
    # 入力（参照用）
    title:          str
    confirmed_text: str
    tags:           list[str]
    category:       str

    # SEO生成物
    slug:           str = ""
    description:    str = ""
    html:           str = ""
    json_ld:        dict = field(default_factory=dict)

    # 意味マッピング
    intent:         str = ""
    content_type:   str = ""
    targets:        list[str] = field(default_factory=list)
    routing_reason: str = ""

    # スコアリング
    seo_score:      float = 0.0
    score_breakdown: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "title":          self.title,
            "slug":           self.slug,
            "description":    self.description,
            "intent":         self.intent,
            "content_type":   self.content_type,
            "targets":        self.targets,
            "routing_reason": self.routing_reason,
            "seo_score":      self.seo_score,
            "score_breakdown": self.score_breakdown,
            "json_ld":        self.json_ld,
            # htmlは別途WordPressへ渡すためここでは省略可
        }


# ── ユーティリティ ────────────────────────────────

def _to_slug(title: str) -> str:
    """タイトル → URLスラッグ"""
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] if s else "post"


def _extract_description(text: str, summary: Optional[str], max_len: int = 155) -> str:
    """metaディスクリプション生成（summary優先、なければ本文先頭を抽出）"""
    if summary and len(summary.strip()) >= 20:
        desc = summary.strip()
    else:
        # フロントマター・見出しを除いた最初の段落を使う
        clean = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
        clean = re.sub(r"^#{1,4} .+$", "", clean, flags=re.MULTILINE)
        paras = [p.strip() for p in re.split(r"\n{2,}", clean) if p.strip()]
        desc  = paras[0] if paras else text[:200].strip()

    # Markdownシンタックス除去
    desc = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", desc)
    desc = re.sub(r"`(.+?)`", r"\1", desc)

    if len(desc) > max_len:
        desc = desc[:max_len - 1].rsplit(" ", 1)[0] + "…"

    return desc


def _word_count(text: str) -> int:
    """おおよその語数（日本語1文字=1語としてカウント）"""
    clean = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    clean = re.sub(r"^#{1,4} ", "", clean, flags=re.MULTILINE)
    return len(re.findall(r"\S+", clean))


def _has_section(text: str, keywords: list[str]) -> bool:
    pattern = "|".join(re.escape(k) for k in keywords)
    return bool(re.search(rf"^#{{1,4}} .*({pattern})", text, re.MULTILINE | re.IGNORECASE))


# ── SEO スコアリング ──────────────────────────────

def _calculate_seo_score(title: str, description: str,
                          tags: list[str], text: str,
                          intent: str) -> tuple[float, dict]:
    """
    意味カバレッジベースSEOスコア算出 (0.0〜1.0)

    ─ 評価軸 ─────────────────────────
    title_present    : タイトルが本文中に含まれているか        (0.15)
    description_len  : descriptionが理想範囲内か              (0.15)
    tags_present     : タグが1件以上あるか                    (0.10)
    topic_coverage   : 見出し構造（h2/h3相当）があるか         (0.20)
    content_length   : 十分な語数があるか                     (0.20)
    reading_flow     : intro/conclusion セクションがあるか     (0.20)
    """
    breakdown = {}

    # title_present
    title_in_body = title.split()[:3]
    bp = sum(1 for w in title_in_body if w.lower() in text.lower()) / max(len(title_in_body), 1)
    breakdown["title_present"] = round(bp * 0.15, 3)

    # description_len
    dl = len(description)
    if _IDEAL_DESCRIPTION_LEN[0] <= dl <= _IDEAL_DESCRIPTION_LEN[1]:
        breakdown["description_len"] = 0.15
    elif dl > 0:
        breakdown["description_len"] = 0.08
    else:
        breakdown["description_len"] = 0.0

    # tags_present
    breakdown["tags_present"] = 0.10 if len(tags) >= 1 else 0.0

    # topic_coverage（見出しが2件以上あるか）
    headings = re.findall(r"^#{1,4} .+$", text, re.MULTILINE)
    if len(headings) >= 3:
        breakdown["topic_coverage"] = 0.20
    elif len(headings) >= 1:
        breakdown["topic_coverage"] = 0.10
    else:
        breakdown["topic_coverage"] = 0.0

    # content_length
    wc = _word_count(text)
    if wc >= _MIN_WORDS_FOR_COVERAGE * 3:
        breakdown["content_length"] = 0.20
    elif wc >= _MIN_WORDS_FOR_COVERAGE:
        breakdown["content_length"] = 0.12
    elif wc >= 30:
        breakdown["content_length"] = 0.06
    else:
        breakdown["content_length"] = 0.0

    # reading_flow
    has_intro = _has_section(text, ["概要", "はじめに", "intro", "overview"])
    has_conc  = _has_section(text, ["結論", "まとめ", "conclusion", "おわりに"])
    breakdown["reading_flow"] = 0.20 if (has_intro and has_conc) else (0.10 if (has_intro or has_conc) else 0.0)

    score = round(sum(breakdown.values()), 2)
    return min(1.0, score), breakdown


# ── SEO-CENTER メインクラス ───────────────────────

class SEOCenter:
    """
    意味 → 構造 → 社会配列 変換コア

    Usage:
        center = SEOCenter()
        result = center.process(
            title="...", summary="...", confirmed_text="...",
            tags=[...], category="..."
        )
        # result.html        → WordPress投稿本文
        # result.json_ld     → 構造化データ
        # result.targets     → 配信先リスト
        # result.seo_score   → SEOスコア
    """

    def __init__(self):
        self._html_gen = HTMLGenerator()
        self._router   = DistributionRouter()

    def process(self,
                title:          str,
                confirmed_text: str,
                tags:           list[str] = None,
                category:       str = "",
                summary:        Optional[str] = None,
                force_type:     Optional[str] = None) -> SEOResult:
        """
        AI Gate出力を受け取り、SEO最適化済みSEOResultを返す。

        Args:
            title:          記事タイトル
            confirmed_text: AI Gate確定済み本文（Markdown）
            tags:           タグリスト
            category:       カテゴリ
            summary:        AI Gateが生成した要約（省略可）
            force_type:     コンテンツタイプ強制指定（省略時は自動検出）
        """
        tags = tags or []

        # 1. スラッグ生成
        slug = _to_slug(title)

        # 2. metaディスクリプション生成
        description = _extract_description(confirmed_text, summary)

        # 3. 配信先決定
        routing = self._router.route(
            title=title, tags=tags, category=category,
            text=confirmed_text, force_type=force_type
        )

        # 4. SEOスコアリング（意味カバレッジ評価）
        seo_score, score_breakdown = _calculate_seo_score(
            title=title, description=description,
            tags=tags, text=confirmed_text, intent=routing.intent
        )

        # 5. SEOResult 組み立て（html生成前に渡すため仮オブジェクト）
        result = SEOResult(
            title          = title,
            confirmed_text = confirmed_text,
            tags           = tags,
            category       = category,
            slug           = slug,
            description    = description,
            intent         = routing.intent,
            content_type   = routing.content_type,
            targets        = routing.targets,
            routing_reason = routing.reasoning,
            seo_score      = seo_score,
            score_breakdown = score_breakdown,
        )

        # 6. HTML生成（SEOResult自身を渡す）
        result.html    = self._html_gen.generate(result)
        result.json_ld = self._html_gen.generate_json_ld(result)

        return result

    def process_from_gate(self, gate_result: dict) -> SEOResult:
        """
        AI Gate の process() 戻り値をそのまま受け取るヘルパー。

        gate_result 形式:
            {"ks_id": ..., "status": ..., "score": ...,
             "summary": ..., "confirmed_text": ..., ...}
        KSレコードの title / tags / category は別途渡す必要がある。
        """
        raise NotImplementedError(
            "process_from_gate は pros.py の cmd_seo() 経由で KSレコードと結合して使用してください。"
        )


if __name__ == "__main__":
    import json

    center = SEOCenter()
    result = center.process(
        title="MoCKA PR-OS 設計思想と実装構造",
        confirmed_text="""# MoCKA PR-OS 設計思想と実装構造

## 概要

PR-OSは「意味 → 構造 → 社会配列」変換OSである。
単なる投稿ツールではなく、知識資産を複数の社会層に最適化して配信する制度的システムだ。

## 本質構造

AI Gateが品質を保証し、SEO-CENTERが検索構造に変換し、
Distribution Routerが配信先を決定する。

## 分析

従来の投稿ツールとの最大の差異は「意味の保存」にある。
MoCKA events.dbへのフィードバックにより、配信結果が知識として蓄積される。

## 結論

PR-OSはMoCKAの外部発信制度として機能し、
「記録なき作業はMoCKAとして存在しない」原則を外部配信まで貫徹する。
""",
        tags=["pr-os", "mocka", "architecture", "設計"],
        category="development",
        summary="PR-OSの設計思想と実装構造の概要。意味→構造→社会配列変換OSとしての位置付けを解説する。"
    )

    print(f"Slug:        {result.slug}")
    print(f"Description: {result.description}")
    print(f"ContentType: {result.content_type}")
    print(f"Intent:      {result.intent}")
    print(f"Targets:     {result.targets}")
    print(f"SEO Score:   {result.seo_score}")
    print(f"Breakdown:   {json.dumps(result.score_breakdown, indent=2)}")
    print(f"\n--- JSON-LD ---")
    print(json.dumps(result.json_ld, ensure_ascii=False, indent=2))
    print(f"\n--- HTML (先頭500文字) ---")
    print(result.html[:500])
