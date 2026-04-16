import json
import uuid
from datetime import datetime, UTC
import os

INPUT_PATH = "input.json"
CHAT_INPUT_PATH = "chat_input.txt"

def load_chat_input():
    if not os.path.exists(CHAT_INPUT_PATH):
        print("NO CHAT INPUT FILE")
        return None
    with open(CHAT_INPUT_PATH, "r", encoding="utf-8-sig") as f:
        return f.read().strip()

def simple_intent_parser(text):
    intent_type = "analysis"

    if "して" in text or "やれ" in text or "実装" in text:
        intent_type = "command"
    elif "なぜ" in text or "理由" in text:
        intent_type = "analysis"
    elif "間違い" in text or "違う" in text:
        intent_type = "correction"
    elif "教えて" in text:
        intent_type = "request"

    return {
        "intent_id": str(uuid.uuid4()),
        "session_id": "default_session",
        "type": intent_type,
        "goal": text[:100],
        "action": text[:100],
        "context": text,
        "constraints": "",
        "source": "human_chat",
        "timestamp": datetime.now(UTC).isoformat(),
        "confidence": 0.5,
        "priority": 0
    }

def save_input(intent):
    data = {"intent": intent}
    with open(INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("INTENT WRITTEN TO input.json")

def main():
    text = load_chat_input()
    if not text:
        return
    intent = simple_intent_parser(text)
    save_input(intent)

if __name__ == "__main__":
    main()
