import json
import time
import os
import requests

INPUT_PATH = "input.json"
OUTPUT_PATH = "llm_output.json"

API_KEY = os.getenv("OPENAI_API_KEY")

def ensure_files():
    if not os.path.exists(INPUT_PATH):
        with open(INPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def evaluate_text(text):
    if not API_KEY:
        print("API KEY NOT FOUND")
        return 0

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Evaluate sentiment strictly. Return ONLY one number: -1 (negative), 0 (neutral), or 1 (positive)."},
                    {"role": "user", "content": text}
                ]
            },
            timeout=10
        )

        if res.status_code != 200:
            print("API ERROR:", res.status_code, res.text)
            return 0

        result = res.json()
        content = result["choices"][0]["message"]["content"].strip()

        if content.startswith("-1"):
            return -1
        elif content.startswith("1"):
            return 1
        else:
            return 0

    except Exception as e:
        print("LLM ERROR:", e)
        return 0

def main():
    print("=== LLM EVALUATOR (ENV MODE SAFE) ===")

    while True:
        ensure_files()
        data = load_json(INPUT_PATH)

        if not data:
            time.sleep(5)
            continue

        outputs = []

        for item in data:
            if isinstance(item, dict):
                text = item.get("text", "")
            else:
                text = str(item)

            score = evaluate_text(text)

            outputs.append({
                "text": text,
                "score": score
            })

            print("LLM:", score, text[:60])

        save_json(OUTPUT_PATH, outputs)
        save_json(INPUT_PATH, [])

        time.sleep(5)

if __name__ == "__main__":
    main()
