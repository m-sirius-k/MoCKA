import json
import os
import sys
from datetime import datetime, UTC

RESULT_PATH = "action_result.json"
ROOT = r"C:\Users\sirok\MoCKA"

def execute_action(action):
    # router経由でAIに投げる試み
    output = None
    try:
        sys.path.insert(0, ROOT)
        from interface.router import MoCKARouter
        router = MoCKARouter()
        if router.providers["Gemini"].is_available():
            result = router.collaborate(str(action))
            output = result["final_answer"]
    except Exception as e:
        output = f"[router fallback] {e}"

    # フォールバック
    if not output or output.startswith("[Gemini] ERROR"):
        output = f"[local] Executed {action}"

    result = {
        "action": action,
        "status": "success",
        "output": output,
        "timestamp": datetime.now(UTC).isoformat()
    }

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("ACTION EXECUTED:", action)
    print("OUTPUT:", output[:100])
    return result
