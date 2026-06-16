"""
DISTRIBUTION ROUTER — 配信先決定レイヤー
コンテンツタイプ・タグ・カテゴリから最適配信先を決定する
"""
from dataclasses import dataclass, field


# コンテンツタイプ定数
class ContentType:
    TECHNICAL    = "technical"
    THOUGHT      = "thought"
    ANNOUNCEMENT = "announcement"
    RESEARCH     = "research"
    STRATEGIC    = "strategic"
    SOCIAL       = "social"
    UNKNOWN      = "unknown"


@dataclass
class RoutingDecision:
    content_type: str
    targets: list[str]
    intent: str
    reasoning: str
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "content_type": self.content_type,
            "targets":      self.targets,
            "intent":       self.intent,
            "reasoning":    self.reasoning,
            "confidence":   self.confidence,
        }


# タグ・カテゴリ → コンテンツタイプ マッピング
_TECHNICAL_SIGNALS = {
    "tags": {"tech", "engineering", "code", "architecture", "api", "python",
             "javascript", "database", "infrastructure", "schema", "開発", "実装"},
    "categories": {"development", "engineering", "tech", "technical"},
}

_THOUGHT_SIGNALS = {
    "tags": {"essay", "thought", "philosophy", "考察", "随筆", "意見", "think",
             "reflection", "opinion"},
    "categories": {"essay", "blog", "thought", "philosophy"},
}

_ANNOUNCEMENT_SIGNALS = {
    "tags": {"release", "update", "launch", "announcement", "リリース", "発表",
             "news", "changelog"},
    "categories": {"announcement", "news", "release"},
}

_RESEARCH_SIGNALS = {
    "tags": {"research", "study", "analysis", "survey", "data", "paper",
             "調査", "研究", "分析", "report"},
    "categories": {"research", "analysis", "report"},
}

_STRATEGIC_SIGNALS = {
    "tags": {"strategy", "roadmap", "vision", "planning", "戦略", "計画",
             "design", "架構"},
    "categories": {"strategy", "planning", "vision"},
}


def _detect_content_type(title: str, tags: list[str], category: str,
                         text: str) -> tuple[str, float]:
    """タグ・カテゴリ・テキストからコンテンツタイプを推定"""
    tag_set  = {t.lower() for t in tags}
    cat_low  = category.lower() if category else ""
    title_low = title.lower()

    def score(signals: dict) -> int:
        s = len(tag_set & signals["tags"])
        s += 2 if cat_low in signals["categories"] else 0
        return s

    scores = {
        ContentType.TECHNICAL:    score(_TECHNICAL_SIGNALS),
        ContentType.THOUGHT:      score(_THOUGHT_SIGNALS),
        ContentType.ANNOUNCEMENT: score(_ANNOUNCEMENT_SIGNALS),
        ContentType.RESEARCH:     score(_RESEARCH_SIGNALS),
        ContentType.STRATEGIC:    score(_STRATEGIC_SIGNALS),
    }

    # テキストヒューリスティック（タイトル含む）
    if any(k in title_low for k in ("リリース", "release", "update", "発表", "お知らせ")):
        scores[ContentType.ANNOUNCEMENT] += 3
    if any(k in title_low for k in ("設計", "architecture", "実装", "構造", "design")):
        scores[ContentType.TECHNICAL] += 2
    if any(k in title_low for k in ("考察", "analysis", "研究", "調査")):
        scores[ContentType.RESEARCH] += 2

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score == 0:
        return ContentType.UNKNOWN, 0.5

    total = sum(scores.values()) or 1
    confidence = min(1.0, best_score / total + 0.3)
    return best_type, round(confidence, 2)


# ルーティングテーブル
_ROUTING_TABLE: dict[str, dict] = {
    ContentType.TECHNICAL: {
        "targets": ["github_pages", "wordpress"],
        "intent":  "Technical",
        "reasoning": "技術コンテンツはGitHub Pages（構造重視）+ WordPress（解説記事）",
    },
    ContentType.THOUGHT: {
        "targets": ["wordpress", "x"],
        "intent":  "Informational",
        "reasoning": "思考・随筆はWordPress（長文）+ X（核心要約スレッド）",
    },
    ContentType.ANNOUNCEMENT: {
        "targets": ["x", "newsletter"],
        "intent":  "Social",
        "reasoning": "発表・リリースはX（拡散）+ Newsletter（購読者通知）",
    },
    ContentType.RESEARCH: {
        "targets": ["github_pages", "wordpress", "newsletter"],
        "intent":  "Informational",
        "reasoning": "研究・分析は全チャネル配信（永続性 + 到達範囲最大化）",
    },
    ContentType.STRATEGIC: {
        "targets": ["wordpress"],
        "intent":  "Strategic",
        "reasoning": "戦略文書はWordPress（制度記録として保存）",
    },
    ContentType.SOCIAL: {
        "targets": ["x", "instagram"],
        "intent":  "Social",
        "reasoning": "ソーシャル向けコンテンツはX + Instagram",
    },
    ContentType.UNKNOWN: {
        "targets": ["wordpress"],
        "intent":  "Informational",
        "reasoning": "タイプ不明のため WordPress をデフォルト配信先とする",
    },
}


class DistributionRouter:
    """コンテンツタイプから配信先を決定するルーター"""

    def route(self, title: str, tags: list[str], category: str,
              text: str, force_type: str = None) -> RoutingDecision:
        """
        配信先を決定して RoutingDecision を返す。

        Args:
            force_type: 強制指定するコンテンツタイプ（省略時は自動検出）
        """
        if force_type:
            content_type = force_type
            confidence   = 1.0
        else:
            content_type, confidence = _detect_content_type(title, tags, category, text)

        rule = _ROUTING_TABLE.get(content_type, _ROUTING_TABLE[ContentType.UNKNOWN])

        return RoutingDecision(
            content_type = content_type,
            targets      = rule["targets"],
            intent       = rule["intent"],
            reasoning    = rule["reasoning"],
            confidence   = confidence,
        )
