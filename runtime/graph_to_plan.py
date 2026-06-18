import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os

GRAPH_PATH = "causal_graph.json"
PLAN_PATH = "plan.json"

def update_plan_from_graph():
    if not os.path.exists(GRAPH_PATH):
        return

    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])

    if not nodes:
        return

    # 最新ノードを戦略に反映
    last = nodes[-1]

    plan = {
        "strategy": f"repeat_{last.get('action')}",
        "based_on": last.get("id")
    }

    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print("PLAN UPDATED")
