"""
semantic_scorer.py — backend用ラッパー
seo_center既存ロジックをSemantic Score Vector IFに変換する。
本実装(workshop/pr-os/semantic_scorer.py)が配置されるまでの橋渡し。
"""

import sys
from pathlib import Path

# seo_centerへのパス解決
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from seo_center.seo_center import _calculate_seo_score, _extract_description
    _HAS_SEO_CENTER = True
except ImportError:
    _HAS_SEO_CENTER = False


class SemanticScoreVector:
    def __init__(self, scalar: float):
        # seo_centerのスカラー値を5軸に均等展開（暫定）
        self.s1_semantic_coverage = scalar
        self.s2_structure_completeness = scalar
        self.s3_citation_fitness = scalar
        self.s4_retrieval_fit = scalar
        self.s5_reusability = scalar

    def to_dict(self) -> dict:
        s = self.s1_semantic_coverage
        return {
            "s1_semantic_coverage": round(s, 3),
            "s2_structure_completeness": round(s, 3),
            "s3_citation_fitness": round(s, 3),
            "s4_retrieval_fit": round(s, 3),
            "s5_reusability": round(s, 3),
            "scalar": round(s, 3),
            "_source": "seo_center_stub",  # 本実装に置換されるとここが変わる
        }


def score_content(title: str, body: str, metadata: dict = None) -> SemanticScoreVector:
    if _HAS_SEO_CENTER:
        try:
            description = _extract_description(body, None)
            scalar, _ = _calculate_seo_score(
                title=title,
                description=description,
                tags=[],
                text=body,
                intent="",
            )
            return SemanticScoreVector(scalar)
        except Exception:
            pass
    # フォールバック（seo_centerも失敗した場合）
    import re
    word_count = len(re.findall(r"\S+", body))
    scalar = min(1.0, word_count / 500)
    return SemanticScoreVector(scalar)
