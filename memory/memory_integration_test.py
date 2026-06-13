"""
MoCKA 3.0 — Memory Layer 統合テスト

確認内容:
  - 保存 -> 検索 -> 再構築 (MemoryPipeline.process -> Storeへ記録 -> 再取得)
  - Decision履歴の記録 (record_decisionでepisodic memoryが残る)
  - Context再現性 (同Intentを再度処理した際、過去Decisionが反映される)
  - 複数Memory統合 (Semantic/Decision/Memoryが連携して動作する)

テストは一時ディレクトリにMemory Storeを作成し、既存の
memory/data/memory_store.json には影響を与えない。
"""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from memory_pipeline import MemoryPipeline  # noqa: E402
from memory_registry import MemoryType  # noqa: E402
from memory_store import MemoryStore  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "memory_store.json"
        store = MemoryStore(store_path)
        pipeline = MemoryPipeline(store)

        # --- 1回目の処理: 実装系の要求 ---
        decision_result_1, enriched_1 = pipeline.process(
            "Decision Engineを実装して新しいモジュールを追加して",
            {"phase": "phase2-3", "active_task": "TODO_implement_memory"},
        )

        results.append(check(
            "1st process returns DecisionResult with selected_action",
            bool(decision_result_1.selected_action),
        ))
        results.append(check(
            "1st process returns EnrichedContext for 'implementation'",
            enriched_1.intent_key == "implementation",
        ))
        results.append(check(
            "1st enriched_context has no past_decisions yet",
            len(enriched_1.past_decisions) == 0,
        ))

        # --- 保存 -> 検索 -> 再構築 ---
        all_entries = store.all()
        results.append(check(
            "Memory Store recorded 1 episodic entry after 1st process",
            len(all_entries) == 1 and all_entries[0].memory_type == MemoryType.EPISODIC,
        ))
        results.append(check(
            "Recorded entry source is 'Decision'",
            all_entries[0].source == "Decision",
        ))
        results.append(check(
            "Recorded entry metadata.intent_key == 'implementation'",
            all_entries[0].metadata.get("intent_key") == "implementation",
        ))

        # 再構築: 別のMemoryStoreインスタンスで同じファイルを読み込めること
        reloaded_store = MemoryStore(store_path)
        reloaded_entries = reloaded_store.all()
        results.append(check(
            "Reloaded MemoryStore reconstructs the same entries",
            len(reloaded_entries) == len(all_entries)
            and reloaded_entries[0].memory_id == all_entries[0].memory_id,
        ))

        # --- 2回目の処理: 同じIntentを再度処理 -> Context再現性 ---
        decision_result_2, enriched_2 = pipeline.process(
            "別のモジュールも実装してください",
            {"phase": "phase2-3", "active_task": "TODO_implement_memory_2"},
        )

        results.append(check(
            "2nd process also classified as 'implementation'",
            enriched_2.intent_key == "implementation",
        ))
        results.append(check(
            "2nd enriched_context includes the 1st decision as past_decisions",
            len(enriched_2.past_decisions) >= 1,
        ))
        results.append(check(
            "2nd enriched_context.summary_text reflects past decision count",
            "過去Decision" in enriched_2.summary_text,
        ))

        # --- 複数Memory統合: Storeには2件のepisodic memoryが存在 ---
        final_entries = store.all()
        results.append(check(
            "Memory Store recorded 2 episodic entries after 2 processes",
            len(final_entries) == 2,
        ))

        # --- 複数Memory統合: 異なるmemory_typeの書き込みも可能 ---
        from memory_writer import MemoryWriter
        from memory_registry import Source

        writer = MemoryWriter(store)
        writer.write_semantic_concept(
            key="action_profile",
            definition={"description": "write_heavy/read_heavy等のDecision分類"},
            tags=("concept", "decision_registry"),
        )
        writer.write_event(
            {"title": "CHANGE_DONE: memory layer test"},
            memory_type=MemoryType.PROCEDURAL,
            source=Source.EXTERNAL,
            tags=("test",),
        )

        mixed_entries = store.all()
        memory_types_present = {e.memory_type for e in mixed_entries}
        results.append(check(
            "Multiple memory types coexist in Memory Store",
            {MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL} <= memory_types_present,
        ))

        # --- to_dict() round-trip ---
        results.append(check(
            "EnrichedContext.to_dict() round-trips",
            isinstance(enriched_2.to_dict(), dict) and "past_decisions" in enriched_2.to_dict(),
        ))
        results.append(check(
            "EnrichedContext.to_context_dict() exposes recent_events",
            "recent_events" in enriched_2.to_context_dict(),
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
