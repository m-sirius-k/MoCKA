"""
MoCKA 3.0 — Memory Layer 検索テスト (memory_retriever.py)

確認内容:
  - intentによる検索 (intent_match)
  - tagsによる検索 (tag_overlap)
  - queryによる類似検索 (similarity)
  - timestampによる順序 (recency)
  - relevance_scoreの範囲(0-1)とランキング順序
"""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from memory_model import MemoryEntry  # noqa: E402
from memory_registry import MemoryType, Source  # noqa: E402
from memory_retriever import MemoryRetriever  # noqa: E402
from memory_store import MemoryStore  # noqa: E402


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def _seed_entries(store: MemoryStore):
    """検索テスト用に3件のepisodic memoryを投入する。"""
    samples = [
        {
            "intent_key": "implementation",
            "tags": ("episodic", "history", "decision", "intent:implementation"),
            "rationale": "Decision Engineを実装するためのrationale",
            "risk_score": 0.7,
        },
        {
            "intent_key": "audit",
            "tags": ("episodic", "history", "decision", "intent:audit"),
            "rationale": "Governance Layerの監査に関するrationale",
            "risk_score": 0.3,
        },
        {
            "intent_key": "implementation",
            "tags": ("episodic", "history", "decision", "intent:implementation"),
            "rationale": "Memory Layerを実装するためのrationale",
            "risk_score": 0.65,
        },
    ]

    for sample in samples:
        entry = MemoryEntry(
            memory_id=store.next_memory_id(MemoryType.EPISODIC),
            memory_type=MemoryType.EPISODIC,
            timestamp=store.now_iso(),
            source=Source.DECISION_LAYER,
            content={"rationale": sample["rationale"], "risk_score": sample["risk_score"]},
            metadata={"intent_key": sample["intent_key"]},
            tags=sample["tags"],
        )
        store.append(entry)


def main():
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "memory_store.json"
        store = MemoryStore(store_path)
        _seed_entries(store)

        retriever = MemoryRetriever(store)

        # --- intentによる検索 ---
        by_intent = retriever.retrieve(intent_key="implementation", top_k=10)
        results.append(check(
            "retrieve(intent_key='implementation') returns 2 entries",
            len(by_intent) == 2,
        ))
        results.append(check(
            "retrieve(intent_key=...) entries all match intent_key",
            all(sm.entry.metadata.get("intent_key") == "implementation" for sm in by_intent),
        ))

        # --- tagsによる検索 ---
        by_tag = retriever.retrieve(tags=("intent:audit",), top_k=10)
        results.append(check(
            "retrieve(tags=('intent:audit',)) ranks the audit entry first",
            by_tag[0].entry.metadata.get("intent_key") == "audit",
        ))

        # --- queryによる類似検索 ---
        by_query = retriever.retrieve(query="Memory Layer 実装", top_k=10)
        results.append(check(
            "retrieve(query='Memory Layer 実装') ranks the Memory Layer entry first",
            "Memory Layer" in by_query[0].entry.content["rationale"],
        ))

        # --- timestampによる順序 (検索条件なし -> recencyのみ) ---
        by_recency = retriever.retrieve(top_k=10)
        results.append(check(
            "retrieve() with no filters returns entries newest-first",
            by_recency[0].entry.memory_id == store.all()[-1].memory_id,
        ))

        # --- relevance_scoreの範囲とランキング順序 ---
        all_scores = [sm.relevance_score for sm in by_intent + by_tag + by_query + by_recency]
        results.append(check(
            "All relevance_score values are within [0, 1]",
            all(0.0 <= s <= 1.0 for s in all_scores),
        ))
        results.append(check(
            "retrieve() results are sorted by relevance_score descending",
            all(by_intent[i].relevance_score >= by_intent[i + 1].relevance_score
                for i in range(len(by_intent) - 1)),
        ))

        # --- top_kの制限 ---
        limited = retriever.retrieve(intent_key="implementation", top_k=1)
        results.append(check(
            "retrieve(..., top_k=1) returns exactly 1 entry",
            len(limited) == 1,
        ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
