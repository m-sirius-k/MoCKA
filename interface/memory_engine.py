import json
import os
import time

LEDGER_PATH = "runtime/external_verification.json"

def save_consensus_result(prompt, decision):
    if not decision: return
    history = []
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except: pass
    
    # グラフ描画に必要なキー "winner_provider" を確実に含める
    entry = {
        "timestamp": time.time(),
        "prompt": prompt,
        "final_output": decision.get("output", ""),
        "winner_provider": decision.get("provider", "unknown"),
        "consensus_stats": decision
    }
    history.append(entry)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(history[-100:], f, ensure_ascii=False, indent=2)

def find_similar(prompt):
    if not os.path.exists(LEDGER_PATH): return None
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
            for entry in reversed(history):
                if entry["prompt"] == prompt: return entry
    except: pass
    return None

# 他の関数はそのまま維持（省略可だが安全のため統合）
def record_taboo(prompt, reason):
    pass
def get_taboos():
    return {}
