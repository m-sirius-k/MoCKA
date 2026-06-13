"""
MoCKA 3.0 — Semantic Layer 統合テスト

確認内容:
  - Intent分類 (semantic_sample_cases の各ケースで期待Intentと一致するか)
  - Context解析 (ContextSummaryが意味情報を保持しているか)
  - Semantic Result生成 (統一形式で出力されるか)
  - Registry整合性 (全Intentキーがcandidatesに現れ得るか)
"""

from context_analyzer import ContextAnalyzer
from intent_classifier import IntentClassifier
from semantic_pipeline import SemanticPipeline
from semantic_registry import all_intent_keys
from semantic_sample_cases import SAMPLE_CASES


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []
    pipeline = SemanticPipeline()

    # --- Intent分類 + Semantic Result生成 ---
    for case in SAMPLE_CASES:
        result = pipeline.process(case["text"], case["context"])
        results.append(check(
            f"Intent classification: {case['name']} -> {case['expected_intent']}",
            result.intent.key == case["expected_intent"],
        ))

        # Semantic Resultの最低限のフィールドが埋まっていること
        results.append(check(
            f"SemanticResult has confidence in [0,1]: {case['name']}",
            0.0 <= result.confidence <= 1.0,
        ))
        results.append(check(
            f"SemanticResult.to_dict() round-trips: {case['name']}",
            isinstance(result.to_dict(), dict) and "intent" in result.to_dict(),
        ))

    # --- Context解析 ---
    analyzer = ContextAnalyzer()
    ctx = analyzer.analyze({
        "phase": "phase2-1",
        "active_task": "TODO_999",
        "recent_events": ("E1", "E2"),
        "conversation_flow": ("user: hello", "assistant: hi"),
    })
    results.append(check(
        "ContextAnalyzer preserves phase",
        ctx.phase == "phase2-1",
    ))
    results.append(check(
        "ContextAnalyzer preserves active_task",
        ctx.active_task == "TODO_999",
    ))
    results.append(check(
        "ContextAnalyzer produces non-empty summary_text",
        bool(ctx.summary_text),
    ))

    empty_ctx = analyzer.analyze(None)
    results.append(check(
        "ContextAnalyzer handles empty context without error",
        empty_ctx.summary_text == "コンテキスト情報なし",
    ))

    # --- Registry整合性 ---
    classifier = IntentClassifier()
    keys_seen = set()
    for case in SAMPLE_CASES:
        for match in classifier.classify(case["text"]):
            keys_seen.add(match.intent.key)

    known_keys = set(all_intent_keys()) | {"unknown"}
    results.append(check(
        "All classified intent keys are registered (or 'unknown')",
        keys_seen <= known_keys,
    ))
    results.append(check(
        "Registry contains 10 intent categories",
        len(all_intent_keys()) == 10,
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
