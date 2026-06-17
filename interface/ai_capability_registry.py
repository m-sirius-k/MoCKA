#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Capability Registry (TODO_272 + TODO_276統合)

責務:
  各AIの「能力ドメイン」を管理する制度レジストリ。
  AI名ではなく能力（例: "web_search"）で接続先AIを選択できるようにする。

  既存の capability_registry.py（core_kernel/core_store/）は
  「Pythonモジュール → Capability逆引き」用であり、本ファイルとは独立した別物。

能力ドメイン定義:
  "reasoning"       推論・統合・複雑タスク分解
  "web_search"      Web調査・ソース収集・一次調査
  "multimodal"      画像・音声・マルチモーダル処理
  "code"            コード生成・レビュー・デバッグ
  "report"          レポート作成・比較・情報整理
  "long_context"    長文コンテキスト処理・文書要約
  "governance"      制度設計・ガバナンス・倫理評価

機関連携:
  handshake.py の ROLE_REGISTRY（役職定義）と組み合わせ、
  「どのRoleにどのCapabilityが必要か」の制度的マッピングを提供する。

TODO_273（Connector Router）はこのRegistryを参照して担当AIを決定する。
"""
from __future__ import annotations

from typing import Optional

# ── AI能力ドメイン定義 ──────────────────────────────────────────
# 各AIの固有能力・制約・優先ドメインを制度的に定義する。
# 実際の選定には選好スコア (0.0-1.0) を使い、最高スコアのAIが選ばれる。

AI_CAPABILITY_REGISTRY: dict[str, dict] = {
    "ChatGPT": {
        "vendor": "OpenAI",
        "model_hint": "gpt-4o",
        "adapter_key": "gpt",
        "capabilities": {
            "reasoning":    1.0,
            "web_search":   0.7,
            "multimodal":   0.8,
            "code":         0.9,
            "report":       0.8,
            "long_context": 0.7,
            "governance":   0.9,
        },
        "constraints": {
            "max_context_tokens": 128000,
            "requires_api_key":   True,
            "real_time_web":      True,
        },
        "description": "推論統合・複雑タスク分解・Function Calling対応。MoCKA合議プロトコルの主力AI。",
        "trust_level": "Verified",
    },
    "Perplexity": {
        "vendor": "Perplexity AI",
        "model_hint": "llama-3.1-sonar-large-128k-online",
        "adapter_key": "perplexity",
        "capabilities": {
            "reasoning":    0.7,
            "web_search":   1.0,
            "multimodal":   0.3,
            "code":         0.5,
            "report":       0.7,
            "long_context": 0.6,
            "governance":   0.5,
        },
        "constraints": {
            "max_context_tokens": 127072,
            "requires_api_key":   True,
            "real_time_web":      True,
        },
        "description": "Web調査・ソース収集・一次調査に特化。リアルタイム情報取得最強。",
        "trust_level": "Verified",
    },
    "Gemini": {
        "vendor": "Google",
        "model_hint": "gemini-2.0-flash",
        "adapter_key": "gemini",
        "capabilities": {
            "reasoning":    0.9,
            "web_search":   0.6,
            "multimodal":   1.0,
            "code":         0.8,
            "report":       0.7,
            "long_context": 1.0,
            "governance":   0.7,
        },
        "constraints": {
            "max_context_tokens": 1000000,
            "requires_api_key":   True,
            "real_time_web":      False,
        },
        "description": "マルチモーダル・超長文コンテキスト処理に最強。画像・動画分析対応。",
        "trust_level": "Verified",
    },
    "Copilot": {
        "vendor": "Microsoft",
        "model_hint": "gpt-4o (Copilot)",
        "adapter_key": "copilot",
        "capabilities": {
            "reasoning":    0.8,
            "web_search":   0.5,
            "multimodal":   0.6,
            "code":         1.0,
            "report":       0.6,
            "long_context": 0.6,
            "governance":   0.6,
        },
        "constraints": {
            "max_context_tokens": 128000,
            "requires_api_key":   False,
            "real_time_web":      True,
        },
        "description": "コード生成・レビュー・デバッグに特化。GitHub連携・IDE統合。",
        "trust_level": "Verified",
    },
    "Genspark": {
        "vendor": "Genspark",
        "model_hint": "genspark-default",
        "adapter_key": "genspark",
        "capabilities": {
            "reasoning":    0.6,
            "web_search":   0.8,
            "multimodal":   0.4,
            "code":         0.4,
            "report":       1.0,
            "long_context": 0.5,
            "governance":   0.4,
        },
        "constraints": {
            "max_context_tokens": 64000,
            "requires_api_key":   True,
            "real_time_web":      True,
        },
        "description": "レポート作成・比較・情報整理に特化。構造化出力・スライド生成対応。",
        "trust_level": "Trial",
    },
    "Claude": {
        "vendor": "Anthropic",
        "model_hint": "claude-sonnet-4-6",
        "adapter_key": "claude",
        "capabilities": {
            "reasoning":    0.95,
            "web_search":   0.4,
            "multimodal":   0.7,
            "code":         0.95,
            "report":       0.9,
            "long_context": 0.9,
            "governance":   1.0,
        },
        "constraints": {
            "max_context_tokens": 200000,
            "requires_api_key":   True,
            "real_time_web":      False,
        },
        "description": "制度設計・ガバナンス・コード実装に特化。MoCKA執行官（くろこ）として稼働。",
        "trust_level": "Institution Certified",
    },
}

# ── Role × Capability 制度マッピング ───────────────────────────────────────
# handshake.py の ROLE_REGISTRY と連携。
# 各Roleが「このCapabilityを持つAI」を優先選択する際の制度的根拠。
ROLE_CAPABILITY_MAP: dict[str, list[str]] = {
    "R01": ["reasoning", "code"],                     # General
    "R02": ["reasoning", "governance"],               # Design Reviewer
    "R03": ["governance", "reasoning"],               # Audit Officer
    "R04": ["reasoning", "governance", "long_context"],  # Architecture Advisor
    "R05": ["reasoning", "web_search"],               # Incident Analyst
    "R06": ["reasoning", "long_context", "report"],   # Knowledge Curator
}


# ── Registry API ──────────────────────────────────────────────────────────

class AICapabilityRegistry:
    """
    AI能力ドメインRegistryのメインクラス。
    Connector Router (TODO_273) はこのクラスを通じてAIを選択する。

    Usage:
        registry = AICapabilityRegistry()
        best = registry.best_for("web_search")
        print(best)  # "Perplexity"

        candidates = registry.candidates_for("reasoning", min_score=0.8)
        print(candidates)  # ["ChatGPT", "Claude", "Gemini", ...]
    """

    def __init__(self):
        self._registry = AI_CAPABILITY_REGISTRY

    def best_for(self, capability: str,
                 exclude: Optional[list[str]] = None) -> Optional[str]:
        """
        指定Capabilityで最高スコアのAI名を返す。

        Args:
            capability: 能力ドメイン名 (e.g., "web_search")
            exclude:    除外するAI名リスト
        """
        exclude = set(exclude or [])
        best_ai    = None
        best_score = -1.0
        for ai_name, info in self._registry.items():
            if ai_name in exclude:
                continue
            score = info["capabilities"].get(capability, 0.0)
            if score > best_score:
                best_score = score
                best_ai    = ai_name
        return best_ai

    def candidates_for(self, capability: str,
                       min_score: float = 0.6) -> list[dict]:
        """
        指定Capabilityでmin_score以上のAIをスコア降順で返す。

        Returns:
            [{"ai": "Perplexity", "score": 1.0, "adapter_key": "perplexity"}, ...]
        """
        results = []
        for ai_name, info in self._registry.items():
            score = info["capabilities"].get(capability, 0.0)
            if score >= min_score:
                results.append({
                    "ai":          ai_name,
                    "score":       score,
                    "adapter_key": info["adapter_key"],
                    "trust_level": info["trust_level"],
                    "description": info["description"],
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def best_for_role(self, role_id: str,
                      exclude: Optional[list[str]] = None) -> Optional[str]:
        """
        指定Role（handshake.py ROLE_REGISTRY）に最適なAIを返す。
        ROLE_CAPABILITY_MAPから優先Capabilityを取得し、加重平均で最適AIを選択する。
        """
        priority_caps = ROLE_CAPABILITY_MAP.get(role_id, ["reasoning"])
        exclude = set(exclude or [])

        scores: dict[str, float] = {}
        for ai_name, info in self._registry.items():
            if ai_name in exclude:
                continue
            weighted = sum(
                info["capabilities"].get(cap, 0.0)
                for cap in priority_caps
            ) / len(priority_caps)
            scores[ai_name] = weighted

        return max(scores, key=scores.get) if scores else None

    def get_ai_info(self, ai_name: str) -> Optional[dict]:
        """AI名でRegistryエントリを取得する"""
        return self._registry.get(ai_name)

    def get_by_adapter_key(self, adapter_key: str) -> Optional[str]:
        """adapter_key（gateway.pyのadapters dictキー）からAI名を逆引きする"""
        for ai_name, info in self._registry.items():
            if info["adapter_key"] == adapter_key:
                return ai_name
        return None

    def all_capabilities(self) -> list[str]:
        """登録されている全Capability名を返す"""
        caps = set()
        for info in self._registry.values():
            caps.update(info["capabilities"].keys())
        return sorted(caps)

    def snapshot(self) -> dict:
        """現在のRegistry状態を返す（監査・デバッグ用）"""
        return {
            "ai_count":    len(self._registry),
            "capabilities": self.all_capabilities(),
            "ai_list": [
                {
                    "name":         ai_name,
                    "adapter_key":  info["adapter_key"],
                    "trust_level":  info["trust_level"],
                    "top_capability": max(
                        info["capabilities"], key=info["capabilities"].get
                    ),
                }
                for ai_name, info in self._registry.items()
            ],
        }


# シングルトンインスタンス（Connector Routerから import して使う）
registry = AICapabilityRegistry()


if __name__ == "__main__":
    import json

    reg = AICapabilityRegistry()

    print("=== Snapshot ===")
    print(json.dumps(reg.snapshot(), ensure_ascii=False, indent=2))

    print("\n=== best_for ===")
    for cap in reg.all_capabilities():
        best = reg.best_for(cap)
        print(f"  {cap:<18}: {best}")

    print("\n=== candidates_for('reasoning', min_score=0.8) ===")
    for c in reg.candidates_for("reasoning", min_score=0.8):
        print(f"  {c['ai']:<12} score={c['score']:.2f} adapter={c['adapter_key']}")

    print("\n=== best_for_role ===")
    for role_id in ["R01", "R02", "R03", "R04", "R05", "R06"]:
        best = reg.best_for_role(role_id)
        print(f"  {role_id}: {best}")
