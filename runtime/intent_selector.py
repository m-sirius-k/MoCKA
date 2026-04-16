import json

HISTORY_PATH = "runtime/intent_history.json"
OUTPUT_PATH = "runtime/selected_intent.json"

def load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []

def main():
    history = load_history()

    if len(history) == 0:
        print("NO INTENTS")
        return

    # scoreが無い場合も対応
    def get_score(x):
        return x.get("score", 0)

    best = max(history, key=get_score)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(best, f, indent=2)

    print("SELECTED + SAVED:", best)

if __name__ == "__main__":
    main()
