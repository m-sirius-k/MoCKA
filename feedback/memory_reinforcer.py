"""
MoCKA 3.0 — Feedback Loop
memory_reinforcer.py

責務:
  Memory Layerに対する強化・弱体化提案(成功パターン強化/低価値記憶の
  減衰/再利用頻度の補正)を生成する。

  絶対禁止: Memory自動削除。本モジュールは「減衰提案」のみを生成し、
  実際のMemoryEntryの削除・書き換えは行わない。
"""


class MemoryReinforcer:
    """Memory Layerに対する強化・弱体化提案を生成するReinforcer。"""

    def propose(self, issue) -> dict:
        """issue.checkに応じてMemory Layerへの改善提案を生成する。"""
        if issue.check == "一貫性":
            return self._reinforce_success_patterns(issue)
        if issue.check == "ノイズ率":
            return self._decay_low_value_memories(issue)
        if issue.check == "再利用性":
            return self._adjust_reuse_frequency(issue)

        return {
            "reinforcement_type": "none",
            "description": f"未対応のcheck '{issue.check}' のためMemory Reinforcer提案なし。",
        }

    # ------------------------------------------------------------------
    def _reinforce_success_patterns(self, issue) -> dict:
        """成功パターン(risk_score < 0.4のepisodic記憶)の強化提案。"""
        return {
            "reinforcement_type": "reinforce_success_patterns",
            "module": "memory/memory_writer.py",
            "action": "increase_priority",
            "description": (
                f"{issue.description} を踏まえ、risk_score < 0.4で完了した"
                f"episodic記憶を memory_type=skill として再記録し、"
                f"default_priorityを高める運用を提案する"
                f"(自動削除・自動書き換えは行わない)。"
            ),
        }

    def _decay_low_value_memories(self, issue) -> dict:
        """重複率の高い低価値記憶の減衰提案(削除ではない)。"""
        return {
            "reinforcement_type": "decay_low_value_memories",
            "module": "memory/memory_retriever.py",
            "action": "decrease_relevance_score",
            "description": (
                f"{issue.description} を踏まえ、rationale等が重複する"
                f"低価値記憶について、relevance_score算出時のrecency重みを"
                f"減衰させる(スコアを下げる)ことを提案する。"
                f"エントリ自体の削除は提案しない(Memory自動削除は禁止)。"
            ),
        }

    def _adjust_reuse_frequency(self, issue) -> dict:
        """再利用頻度補正(skill memoryへの変換促進)提案。"""
        return {
            "reinforcement_type": "adjust_reuse_frequency",
            "module": "memory/memory_pipeline.py",
            "action": "promote_to_skill",
            "description": (
                f"{issue.description} を踏まえ、同一intent_keyで"
                f"risk_score < 0.4のDecisionが繰り返し記録された場合に、"
                f"memory_type=skillへの変換を促す運用ルールを"
                f"検討することを提案する。"
            ),
        }
