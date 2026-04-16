import json
import time
import os

KNOWLEDGE_PATH = "knowledge_log.json"
RANK_PATH = "knowledge_rank.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def compute_score(entry):
    count = entry.get("count", 0)
    total = entry.get("score_total", 0)

    if count == 0:
        return 0

    return total / count

def main():
    print("=== KNOWLEDGE RANKER START ===")

    while True:
        if not os.path.exists(KNOWLEDGE_PATH):
            time.sleep(5)
            continue

        knowledge = load_json(KNOWLEDGE_PATH)

        ranked = []

        for k, v in knowledge.items():
            score = compute_score(v)

            ranked.append({
                "text": k,
                "score": score,
                "count": v.get("count",0)
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        save_json(RANK_PATH, ranked)

        print("RANK UPDATED:", len(ranked))

        time.sleep(5)

if __name__ == "__main__":
    main()
