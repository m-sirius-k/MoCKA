import json
from collections import Counter, defaultdict

INPUT_PATH = "runtime/state/contexts.json"
OUTPUT_PATH = "runtime/state/context_stats.json"

def load():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze(data):
    result = {}

    for ctx, actions in data.items():
        counter = Counter(actions)

        total = sum(counter.values())

        stats = []

        for action, count in counter.items():
            stats.append({
                "action": action,
                "count": count,
                "ratio": round(count / total, 3)
            })

        stats = sorted(stats, key=lambda x: x["ratio"], reverse=True)

        result[ctx] = stats

    return result

def save(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load()
    stats = analyze(data)
    save(stats)
    print("CONTEXT ANALYZED")
