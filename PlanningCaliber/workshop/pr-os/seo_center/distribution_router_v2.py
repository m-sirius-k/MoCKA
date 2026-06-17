"""
DISTRIBUTION ROUTER v2 — 6軸確率分布モデル（GPT監査確定版）

設計思想:
  Routerは「ルールベース分類器」ではなく
  「配信の確率分布を決める意思決定関数」かつ「制度ゲート」である。

6軸スコアリング:
  content_type    — コンテンツの意味タイプ
  audience        — ターゲット層
  evidence_density — 証拠密度（Semantic Vector s1/s2 から算出）
  media_form      — メディア形態（テキスト長・構造）
  citation_fitness — LLM引用適性（Semantic Vector s3 から算出）
  temporal_decay  — 鮮度劣化係数（発信後の有効期間）

出力:
  distribution_policy {
    wordpress:    0.0-1.0,   # 永続記録・長文向け
    x:            0.0-1.0,   # 拡散・短文向け
    newsletter:   0.0-1.0,   # 購読者通知向け
    github_pages: 0.0-1.0,   # 技術・構造重視向け
    llm_index:    0.0-1.0,   # LLM引用最適化インデックス向け
  }

各値はチャネルへの配信「強度」（ランキングではなく同時分布）。
1.0 = 最優先配信 / 0.0 = 配信不要
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ── 閾値定数 ─────────────────────────────────────────────────
_THRESHOLD_PUBLISH = 0.35   # この値以上のチャネルに配信推奨
_THRESHOLD_STRONG  = 0.65   # この値以上を「強配信」と分類


@dataclass
class DistributionPolicy:
    """配信チャネルへの強度分布（同時分布・ランキングではない）"""
    wordpress:    float = 0.0
    x:            float = 0.0
    newsletter:   float = 0.0
    github_pages: float = 0.0
    llm_index:    float = 0.0

    # メタデータ
    content_type:     str   = ""
    audience:         str   = ""
    dominant_channel: str   = ""
    axis_scores:      dict  = field(default_factory=dict)
    reasoning:        str   = ""

    def to_dict(self) -> dict:
        channels = {
            "wordpress":    round(self.wordpress,    3),
            "x":            round(self.x,            3),
            "newsletter":   round(self.newsletter,   3),
            "github_pages": round(self.github_pages, 3),
            "llm_index":    round(self.llm_index,    3),
        }
        recommended = [ch for ch, v in channels.items() if v >= _THRESHOLD_PUBLISH]
        return {
            "distribution_policy": channels,
            "recommended_channels": recommended,
            "dominant_channel":   self.dominant_channel,
            "content_type":       self.content_type,
            "audience":           self.audience,
            "axis_scores":        self.axis_scores,
            "reasoning":          self.reasoning,
        }

    def recommended_channels(self) -> list[str]:
        return [ch for ch, v in [
            ("wordpress", self.wordpress),
            ("x", self.x),
            ("newsletter", self.newsletter),
            ("github_pages", self.github_pages),
            ("llm_index", self.llm_index),
        ] if v >= _THRESHOLD_PUBLISH]


# ── コンテンツタイプ検出 ─────────────────────────────────────

_TYPE_SIGNALS: dict[str, dict] = {
    "technical": {
        "tags":  {"tech", "engineering", "code", "architecture", "api", "python",
                  "javascript", "database", "infrastructure", "schema", "開発", "実装"},
        "cats":  {"development", "engineering", "tech", "technical"},
        "title": ("設計", "architecture", "実装", "構造", "design", "code", "api"),
    },
    "research": {
        "tags":  {"research", "study", "analysis", "survey", "data", "paper",
                  "調査", "研究", "分析", "report"},
        "cats":  {"research", "analysis", "report"},
        "title": ("考察", "analysis", "研究", "調査", "survey"),
    },
    "announcement": {
        "tags":  {"release", "update", "launch", "announcement", "リリース", "発表",
                  "news", "changelog"},
        "cats":  {"announcement", "news", "release"},
        "title": ("リリース", "release", "update", "発表", "お知らせ", "launch"),
    },
    "thought": {
        "tags":  {"essay", "thought", "philosophy", "考察", "随筆", "意見", "think",
                  "reflection", "opinion"},
        "cats":  {"essay", "blog", "thought", "philosophy"},
        "title": (),
    },
    "strategic": {
        "tags":  {"strategy", "roadmap", "vision", "planning", "戦略", "計画",
                  "design", "架構"},
        "cats":  {"strategy", "planning", "vision"},
        "title": ("戦略", "ロードマップ", "roadmap", "vision"),
    },
}


def _detect_content_type(title: str, tags: list[str], category: str) -> str:
    tag_set = {t.lower() for t in tags}
    cat_low = (category or "").lower()
    title_l = title.lower()

    scores: dict[str, float] = {}
    for ct, sig in _TYPE_SIGNALS.items():
        s = len(tag_set & sig["tags"])
        s += 2.0 if cat_low in sig["cats"] else 0.0
        s += sum(3.0 for kw in sig["title"] if kw in title_l)
        scores[ct] = s

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


def _detect_audience(content_type: str, tags: list[str], category: str) -> str:
    """ターゲット層を推定"""
    tag_set = {t.lower() for t in tags}
    if content_type == "technical":
        return "engineers"
    if content_type == "research":
        if any(k in tag_set for k in ("paper", "academic", "論文", "学術")):
            return "academics"
        return "analysts"
    if content_type == "strategic":
        return "executives"
    if content_type == "announcement":
        return "general"
    return "general"


# ── 6軸スコアリング ──────────────────────────────────────────

def _axis_content_type(content_type: str) -> float:
    """content_type → 軸スコア（情報密度の高さ）"""
    return {
        "technical":    0.85,
        "research":     0.90,
        "announcement": 0.60,
        "thought":      0.65,
        "strategic":    0.75,
        "unknown":      0.40,
    }.get(content_type, 0.40)


def _axis_audience(audience: str) -> float:
    """ターゲット層 → 軸スコア（専門性の高さ）"""
    return {
        "engineers":  0.80,
        "academics":  0.85,
        "executives": 0.70,
        "analysts":   0.75,
        "general":    0.50,
    }.get(audience, 0.50)


def _axis_evidence_density(semantic_vector: Optional[dict], text: str) -> float:
    """
    証拠密度 — Semantic Vector s1(意味充足率) / s2(構造整合性) から算出。
    vectorなければテキスト構造から推定。
    """
    if semantic_vector:
        return round((semantic_vector.get("s1", 0.5) * 0.6 +
                      semantic_vector.get("s2", 0.5) * 0.4), 3)
    # fallback: 語数・見出し数から推定
    word_count = len(re.findall(r"\S+", text))
    headings   = len(re.findall(r"^#{1,4} .+$", text, re.MULTILINE))
    score = min(1.0, word_count / 400) * 0.6 + min(1.0, headings / 4) * 0.4
    return round(score, 3)


def _axis_media_form(text: str) -> float:
    """メディア形態 — 長文・構造化度を評価"""
    word_count = len(re.findall(r"\S+", text))
    has_code   = bool(re.search(r"```", text))
    headings   = len(re.findall(r"^#{1,4} .+$", text, re.MULTILINE))

    score = 0.0
    if word_count >= 500:
        score += 0.4
    elif word_count >= 200:
        score += 0.25
    elif word_count >= 50:
        score += 0.10

    if headings >= 3:
        score += 0.3
    elif headings >= 1:
        score += 0.15

    if has_code:
        score += 0.2

    if text.startswith("---"):
        score += 0.1

    return round(min(1.0, score), 3)


def _axis_citation_fitness(semantic_vector: Optional[dict], text: str) -> float:
    """
    LLM引用適性 — Semantic Vector s3(Citation Fitness) / s4(Retrieval Fit) から算出。
    """
    if semantic_vector:
        return round((semantic_vector.get("s3", 0.5) * 0.6 +
                      semantic_vector.get("s4", 0.5) * 0.4), 3)
    # fallback: 要約・結論セクション有無
    has_summary = bool(re.search(
        r"^#{1,4} .*(概要|はじめに|intro|abstract|summary)",
        text, re.MULTILINE | re.IGNORECASE
    ))
    has_conclusion = bool(re.search(
        r"^#{1,4} .*(結論|まとめ|conclusion)",
        text, re.MULTILINE | re.IGNORECASE
    ))
    return round(0.3 + (0.35 if has_summary else 0) + (0.35 if has_conclusion else 0), 3)


def _axis_temporal_decay(content_type: str) -> float:
    """
    鮮度劣化係数（1.0 = 時間依存なし・永続価値 / 0.0 = 即時性重要で急速劣化）
    Routerはこの値で「今すぐ配信すべきか」を加味する。
    """
    return {
        "technical":    0.85,   # 技術文書は長期価値あり
        "research":     0.90,   # 研究は最長寿命
        "announcement": 0.30,   # 発表は即時性最優先
        "thought":      0.70,   # エッセイは中程度
        "strategic":    0.80,   # 戦略文書は長期価値あり
        "unknown":      0.50,
    }.get(content_type, 0.50)


# ── チャネル強度計算 ─────────────────────────────────────────

def _compute_channel_weights(axes: dict, content_type: str,
                              audience: str) -> dict[str, float]:
    """
    6軸スコアからチャネル別配信強度（0.0-1.0）を算出する。

    チャネル特性:
      wordpress    — 長文・永続記録・全コンテンツタイプ
      x            — 短文・即時拡散・発表・思考
      newsletter   — 購読者通知・発表・研究
      github_pages — 技術・構造重視・LLM引用基盤
      llm_index    — LLM引用最適化インデックス（全タイプ対象・citation_fitness主導）
    """
    ed  = axes["evidence_density"]
    mf  = axes["media_form"]
    cf  = axes["citation_fitness"]
    td  = axes["temporal_decay"]
    ct  = axes["content_type_score"]
    aud = axes["audience_score"]

    # ── WordPress（長文記録・制度文書） ──────────────────
    wp = (
        mf  * 0.35 +
        ed  * 0.25 +
        ct  * 0.20 +
        td  * 0.20
    )
    # 発表系は短文向けのためWPを下げる
    if content_type == "announcement":
        wp *= 0.6

    # ── X/Twitter（短文拡散・即時性） ────────────────────
    # temporal_decayが低い（=即時性重要）ほど高スコア
    x_score = (
        (1.0 - td)  * 0.45 +
        (1.0 - mf)  * 0.30 +
        ct          * 0.15 +
        aud         * 0.10
    )
    # 研究・技術は長文なのでXには不向き
    if content_type in ("research", "technical"):
        x_score *= 0.5

    # ── Newsletter（購読者通知・要約配信） ───────────────
    nl = (
        ct  * 0.30 +
        (1.0 - td) * 0.35 +
        aud * 0.20 +
        ed  * 0.15
    )
    # 思考・随筆はニュースレターに向く
    if content_type == "thought":
        nl = min(1.0, nl * 1.2)

    # ── GitHub Pages（技術・構造重視） ───────────────────
    gh = (
        ed  * 0.40 +
        mf  * 0.30 +
        cf  * 0.20 +
        td  * 0.10
    )
    # 技術系でなければGHを下げる
    if content_type not in ("technical", "research", "strategic"):
        gh *= 0.4
    # 専門家向けなら上げる
    if audience in ("engineers", "academics"):
        gh = min(1.0, gh * 1.15)

    # ── LLM Index（LLM引用最適化・全タイプ対象） ─────────
    llm = (
        cf  * 0.50 +
        ed  * 0.25 +
        td  * 0.15 +
        aud * 0.10
    )
    # 全コンテンツタイプで一定以上（LLMは常にインデックス対象）
    llm = max(llm, 0.3)

    return {
        "wordpress":    round(min(1.0, max(0.0, wp)),      3),
        "x":            round(min(1.0, max(0.0, x_score)), 3),
        "newsletter":   round(min(1.0, max(0.0, nl)),      3),
        "github_pages": round(min(1.0, max(0.0, gh)),      3),
        "llm_index":    round(min(1.0, max(0.0, llm)),     3),
    }


def _dominant_channel(weights: dict[str, float]) -> str:
    return max(weights, key=weights.get)


def _build_reasoning(content_type: str, audience: str,
                     axes: dict, weights: dict[str, float]) -> str:
    top = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = " > ".join(f"{ch}({v:.2f})" for ch, v in top)
    return (
        f"content_type={content_type} / audience={audience} / "
        f"citation_fitness={axes['citation_fitness']:.2f} / "
        f"temporal_decay={axes['temporal_decay']:.2f} → "
        f"Top3: {top_str}"
    )


# ── メインクラス ─────────────────────────────────────────────

class DistributionRouterV2:
    """
    Distribution Router v2 — 6軸確率分布モデル。

    Usage:
        router = DistributionRouterV2()
        policy = router.route(
            title="...", tags=[...], category="...", text="...",
            semantic_vector={"s1": 0.8, "s2": 0.9, "s3": 0.7, "s4": 0.6, "s5": 0.8}
        )
        print(policy.to_dict())
    """

    def route(self,
              title:           str,
              tags:            list[str],
              category:        str,
              text:            str,
              semantic_vector: Optional[dict] = None) -> DistributionPolicy:
        """
        KS記事メタデータ + Semantic Score Vector から配信方針を決定する。

        Args:
            title:           記事タイトル
            tags:            タグリスト
            category:        カテゴリ
            text:            記事本文（Markdown）
            semantic_vector: gate.py の calculate_semantic_vector() 出力
                             {s1, s2, s3, s4, s5}（省略時は本文から推定）
        """
        # Step 1: コンテンツタイプ・ターゲット層検出
        content_type = _detect_content_type(title, tags, category)
        audience     = _detect_audience(content_type, tags, category)

        # Step 2: 6軸スコア算出
        axes = {
            "content_type_score": _axis_content_type(content_type),
            "audience_score":     _axis_audience(audience),
            "evidence_density":   _axis_evidence_density(semantic_vector, text),
            "media_form":         _axis_media_form(text),
            "citation_fitness":   _axis_citation_fitness(semantic_vector, text),
            "temporal_decay":     _axis_temporal_decay(content_type),
        }

        # Step 3: チャネル強度計算
        weights = _compute_channel_weights(axes, content_type, audience)

        return DistributionPolicy(
            wordpress    = weights["wordpress"],
            x            = weights["x"],
            newsletter   = weights["newsletter"],
            github_pages = weights["github_pages"],
            llm_index    = weights["llm_index"],
            content_type     = content_type,
            audience         = audience,
            dominant_channel = _dominant_channel(weights),
            axis_scores      = {k: round(v, 3) for k, v in axes.items()},
            reasoning        = _build_reasoning(content_type, audience, axes, weights),
        )


if __name__ == "__main__":
    import json

    router = DistributionRouterV2()

    # テスト: 研究論文系（Semantic Vector付き）
    policy = router.route(
        title="MoCKA Silence Prohibition Protocol — 沈黙禁止プロトコルの設計と実装",
        tags=["research", "paper", "mocka", "governance", "ai"],
        category="research",
        text="""# MoCKA Silence Prohibition Protocol

## 概要

MoCKAシステムにおける沈黙禁止プロトコルの設計と実装について述べる。

## 主な貢献

本研究では記録なき作業はMoCKAとして存在しないという原則を制度化する。

## 分析

AIが沈黙する場合の制度的リスクを定量化し、記録強制メカニズムを設計した。

## 結論

沈黙禁止プロトコルはAIガバナンスの基盤として機能する。
""",
        semantic_vector={"s1": 0.85, "s2": 0.92, "s3": 0.78, "s4": 0.71, "s5": 0.88}
    )
    print("=== 研究論文系 ===")
    print(json.dumps(policy.to_dict(), ensure_ascii=False, indent=2))

    print()

    # テスト: 発表系（Semantic Vector なし）
    policy2 = router.route(
        title="MoCKA v4 リリースのお知らせ",
        tags=["release", "mocka", "v4", "announcement"],
        category="announcement",
        text="MoCKA v4 がリリースされました。Semantic Score Vector・Distribution Router v2 を導入。",
    )
    print("=== 発表系 ===")
    print(json.dumps(policy2.to_dict(), ensure_ascii=False, indent=2))
