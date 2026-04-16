import os
import sys

sys.path.append(os.path.abspath("."))

from runtime.record.csv_record_engine import record_event

def classify_event(text):
    text_lower = text.lower()

    # --- 優先度順に判定 ---
    if "error" in text_lower or "失敗" in text:
        return "incident"

    if "指示" in text or "instruction" in text_lower:
        return "instruction"

    if len(text) > 200:
        return "chat_full"

    if len(text) > 0:
        return "chat_partial"

    return "unknown"

def registry_trigger(event_text):
    event_type = classify_event(event_text)

    # --- 必ずCSVへ記録 ---
    record_event(
        event_type=event_type,
        summary=event_text,
        storage_path=""
    )

    return {
        "classified_type": event_type,
        "text_length": len(event_text)
    }

if __name__ == "__main__":
    print("=== REGISTRY TRIGGER TEST ===")

    test_event = "これは指示です：CSVの保存ルールを確認する"

    result = registry_trigger(test_event)

    print("RESULT:", result)
