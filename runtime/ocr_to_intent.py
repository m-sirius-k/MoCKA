import json
import re
import uuid
from datetime import datetime, UTC

INPUT_FILE = "input_raw.txt"
OUTPUT_FILE = "input.json"

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def normalize(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def split_sections(text):
    m = re.split(r"---\s*CURRENT\s*---", text, flags=re.IGNORECASE)
    if len(m) == 2:
        left, current = m
        left = re.sub(r"---\s*CONTEXT\s*---", "", left, flags=re.IGNORECASE)
        return normalize(left), normalize(current)
    return "", normalize(text)

def extract_delta(context, current):
    ctx = set(context.split())
    cur = set(current.split())
    return {"added": list(cur - ctx), "removed": list(ctx - cur)}

# ===== 高精度分類 =====
def detect_goal(context, current, delta):
    cur = current.lower()

    # 最優先：明示的要求
    if re.search(r"(直して|修正|fix|バグ|error|fail|exception)", cur):
        return "error_recovery"

    if re.search(r"(分析|解析|調査|原因|why|なぜ)", cur):
        return "analyze_state"

    if re.search(r"(改善|最適化|高速化|optimize|improve)", cur):
        return "optimize_execution"

    if re.search(r"(作って|実装|build|create|generate)", cur):
        return "build_feature"

    if re.search(r"(次|つぎ|continue|go next)", cur):
        return "continue_process"

    # 差分補助
    if any(k in delta["added"] for k in ["fix", "error", "fail"]):
        return "error_recovery"

    return "context_process"

def calc_confidence(context, current, delta):
    score = 0.6
    if len(current) > 50:
        score += 0.1
    if len(delta["added"]) > 2:
        score += 0.1
    return min(score, 0.9)

def build_intent(context, current, delta):
    return {
        "id": str(uuid.uuid4()),
        "ts": datetime.now(UTC).isoformat(),
        "source": "ocr_dual",
        "context": context,
        "current": current,
        "delta": delta,
        "goal": detect_goal(context, current, delta),
        "confidence": calc_confidence(context, current, delta)
    }

def main():
    raw = load_text(INPUT_FILE)
    ctx, cur = split_sections(raw)
    delta = extract_delta(ctx, cur)
    intent = build_intent(ctx, cur, delta)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(intent, f, indent=2, ensure_ascii=False)

    print("=== OCR DUAL INTENT (PRECISION) ===")
    print(f"GOAL: {intent['goal']}")
    print(f"CONFIDENCE: {intent['confidence']}")
    print(f"DELTA+: {len(delta['added'])} / DELTA-: {len(delta['removed'])}")

if __name__ == "__main__":
    main()
