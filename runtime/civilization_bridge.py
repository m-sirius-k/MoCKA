"""
civilization_bridge.py
main_loopとcivilization_*エンジン群を接続するブリッジ
"""
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RUNTIME = Path(r"C:\Users\sirok\MoCKA\runtime")

GOAL_PATH     = RUNTIME / "civilization_goal_state.json"
PROGRESS_PATH = RUNTIME / "civilization_progress.json"
PLAN_PATH     = RUNTIME / "plan.json"

# main_loopのアクションをcivilizationのgoalにマッピング
ACTION_TO_GOAL = {
    "ANALYZE":  "increase_knowledge",
    "FIX":      "increase_stability",
    "EXECUTE":  "increase_progress",
    "VERIFY":   "increase_integrity",
    "RESEARCH": "increase_knowledge",
    "SAVE":     "increase_stability",
    "EXPORT":   "increase_progress",
    "UPDATE":   "increase_stability",
    "DELETE":   "increase_stability",
}

def push_to_civilization(action: str):
    """main_loopのアクションをcivilization_goal_stateに反映"""
    goal = ACTION_TO_GOAL.get(action.upper(), "increase_progress")

    if GOAL_PATH.exists():
        state = json.loads(GOAL_PATH.read_text(encoding="utf-8"))
    else:
        state = {"goal": goal, "stability": 0.25, "avg_fitness": 0.125}

    state["goal"] = goal
    state["last_action"] = action
    state["last_updated"] = datetime.now(timezone.utc).isoformat()

    GOAL_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"BRIDGE: {action} → civilization goal: {goal}")

def pull_from_civilization() -> dict:
    """civilization_progressをmain_loopに返す"""
    if not PROGRESS_PATH.exists():
        return {"civilization_progress": 0.0, "stability": 0.0}
    return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))

def run_civilization_step():
    """civilization_loop_engineを1ステップ実行"""
    result = subprocess.run(
        [sys.executable, str(RUNTIME / "civilization_loop_engine.py")],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=str(RUNTIME)
    )
    print(result.stdout[:200] if result.stdout else "NO OUTPUT")
    return result.returncode == 0

if __name__ == "__main__":
    # テスト実行
    push_to_civilization("ANALYZE")
    ok = run_civilization_step()
    progress = pull_from_civilization()
    print(f"CIVILIZATION PROGRESS: {progress}")
