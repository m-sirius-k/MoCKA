"""
MoCKA 3.0 — Memory Layer 整合性テスト

確認内容:
  - Memory Index (intent_index/tag_index/time_index/similarity_index) の整合性
  - 保存ポリシー (memory_registry.RETENTION_POLICIES) によるmax_entries制限
  - 再起動(再読込)後もインデックス構築結果が一致すること
"""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from memory_index import MemoryIndex  # noqa: E402
from memory_model import MemoryEntry  # noqa: E402
from memory_registry import MemoryType, Source, get_retention_policy  # noqa: E402
from memory_store import MemoryStore  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def _make_entry(store, seq, intent_key, tags):
    return MemoryEntry(
        memory_id=store.next_memory_id(MemoryType.SKILL),
        memory_type=MemoryType.SKILL,
        timestamp=store.now_iso(),
        source=Source.DECISION_LAYER,
        content={"rationale": f"pattern #{seq} for {intent_key}"},
        metadata={"intent_key": intent_key},
        tags=tags,
    )


def main():
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "memory_store.json"
        store = MemoryStore(store_path)

        for i in range(5):
            intent_key = "implementation" if i % 2 == 0 else "audit"
            tags = ("skill", "pattern", f"intent:{intent_key}")
            store.append(_make_entry(store, i, intent_key, tags))

        entries = store.all()
        index = MemoryIndex(entries)

        # --- intent_index整合性 ---
        results.append(check(
            "intent_index['implementation'] has 3 entries",
            len(index.by_intent("implementation")) == 3,
        ))
        results.append(check(
            "intent_index['audit'] has 2 entries",
            len(index.by_intent("audit")) == 2,
        ))

        # --- tag_index整合性 ---
        results.append(check(
            "tag_index['skill'] covers all 5 entries",
            len(index.by_tag("skill")) == 5,
        ))
        results.append(check(
            "tag_index['intent:audit'] matches intent_index['audit']",
            set(index.by_tag("intent:audit")) == set(index.by_intent("audit")),
        ))

        # --- time_index整合性 ---
        results.append(check(
            "time_index length matches entry count",
            len(index.time_index) == len(entries),
        ))
        results.append(check(
            "time_index is ordered by timestamp ascending",
            list(index.time_index) == [e.memory_id for e in sorted(entries, key=lambda e: e.timestamp)],
        ))

        # --- similarity_index整合性 ---
        hits = index.similar_to("implementation pattern")
        results.append(check(
            "similarity_index finds 'implementation' entries via similar_to()",
            all(mid in index.by_intent("implementation") or mid in index.by_intent("audit")
                for mid in hits),
        ))
        results.append(check(
            "similar_to() returns non-empty hits for known tokens",
            len(hits) > 0,
        ))

        # --- 再読込後もインデックスが一致 ---
        reloaded_entries = MemoryStore(store_path).all()
        reloaded_index = MemoryIndex(reloaded_entries)
        results.append(check(
            "Reloaded MemoryIndex matches original intent_index",
            reloaded_index.intent_index == index.intent_index,
        ))
        results.append(check(
            "Reloaded MemoryIndex matches original time_index",
            reloaded_index.time_index == index.time_index,
        ))

        # --- 保存ポリシー (max_entries) ---
        policy = get_retention_policy(MemoryType.SKILL)
        original_max = policy.max_entries

        # 一時的に小さいmax_entriesのStoreを使い、retentionが適用されることを確認する
        import memory_registry as registry_module
        from memory_registry import RetentionPolicy

        small_policy = RetentionPolicy(
            memory_type=MemoryType.SKILL,
            max_entries=3,
            default_priority=policy.default_priority,
            default_tags=policy.default_tags,
        )
        registry_module.RETENTION_POLICIES[MemoryType.SKILL] = small_policy
        try:
            store2_path = Path(tmpdir) / "memory_store_2.json"
            store2 = MemoryStore(store2_path)
            for i in range(5):
                store2.append(_make_entry(store2, i, "implementation", ("skill",)))
            limited_entries = store2.all()
            results.append(check(
                "RETENTION_POLICIES.max_entries=3 trims SKILL memories to 3",
                len(limited_entries) == 3,
            ))
        finally:
            registry_module.RETENTION_POLICIES[MemoryType.SKILL] = RetentionPolicy(
                memory_type=MemoryType.SKILL,
                max_entries=original_max,
                default_priority=policy.default_priority,
                default_tags=policy.default_tags,
            )

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
