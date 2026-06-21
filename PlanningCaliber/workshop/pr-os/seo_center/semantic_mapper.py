"""
Semantic Mapper — DistributionPolicy(distribution_router_v2) -> platform_targets変換

責務: distribution_router_v2の出力(recommended_channels)を、
SEO-OS publish_queueが受け取れるplatform_targets形式に変換するだけ。
content_id発行・title/body生成等の他責務は持たない。

チャネル名差分対応(Phase1):
  distribution_router_v2側のチャネル名(wordpress/x/newsletter/github_pages/llm_index)と
  publish_queue許可値(wordpress/x/github)の集合不一致は今は無視する(Phase2対応)。
  一致するチャネル(wordpress/x/github_pages->github)のみマッピングし、
  対応外チャネル(newsletter/llm_index)は単純に出力から除外する。
"""
from __future__ import annotations

_CHANNEL_MAP = {
    "wordpress":    "wordpress",
    "x":             "x",
    "github_pages":  "github",
}


def map_to_platform_targets(distribution_policy: dict) -> list[str]:
    """
    distribution_policy.to_dict()の出力からplatform_targetsを生成する。

    Args:
        distribution_policy: DistributionPolicy.to_dict()の戻り値
                              (recommended_channelsキーを使用)

    Returns:
        publish_queueに渡すplatform名のリスト(wordpress/x/github のみ)
    """
    recommended = distribution_policy.get("recommended_channels", [])
    return [_CHANNEL_MAP[ch] for ch in recommended if ch in _CHANNEL_MAP]
