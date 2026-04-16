import json
import random
import time
import os

INPUT_PATH = "input.json"

def evaluate_text(text):
    # 仮AI評価（ここを将来ChatGPT APIに置換）
    if "good" in text.lower():
        return 1
    if "bad" in text.lower():
        return -1
    return random.choice([1, -1])

def main():
    print("=== AI Evaluator START ===")

    while True:
        if not os.path.exists(INPUT_PATH):
            time.sleep(3)
            continue

        try:
            with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except:
            time.sleep(3)
            continue

        if not data:
            time.sleep(3)
            continue

        new_data = []

        for item in data:
            if isinstance(item, dict):
                text = item.get("text","")
            else:
                text = item

            score = evaluate_text(text)

            new_data.append({
                "text": text,
                "score": score
            })

        with open(INPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)

        print("EVALUATED:", len(new_data))

        time.sleep(3)

if __name__ == "__main__":
    main()
