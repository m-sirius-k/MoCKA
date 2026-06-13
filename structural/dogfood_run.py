"""
MoCKA 3.0 — GL1-7 Dogfooding Run

きむら博士指示②: 実運用(Dogfooding)
GovernancePipeline.before_tool()を実際のMCP tool呼出パターンに沿って
100回以上実行し、以下を集計する:
  - Tool実行回数
  - バイパス件数(governance未適用で進んだ件数)
  - 重大障害件数(例外発生)
  - Dry Run誤検知率(WRITE_TOOLSでaborted件数 / WRITE_TOOLS呼出件数)

結果はdogfood_result.jsonとしてstructural/に保存する。
"""

import json
import traceback
from collections import Counter

from governance_pipeline import GovernancePipeline, WRITE_TOOLS

# 実際の利用頻度を反映したtool呼出シーケンス
# (読み取り系を多めに、書き込み系を定期的に混在させる)
READ_TOOLS = [
    "mocka_get_overview",
    "mocka_get_todo",
    "mocka_get_essence",
    "mocka_get_guidelines",
    "mocka_get_incidents",
    "mocka_search",
    "mocka_list_events",
    "mocka_read_event",
    "mocka_get_command_center",
]

CALL_SEQUENCE = []
for i in range(11):  # 11 rounds x (9 read + 1 write) = 110 calls
    for t in READ_TOOLS:
        CALL_SEQUENCE.append((t, {"round": i}))
    CALL_SEQUENCE.append(("mocka_write_event", {"round": i, "title": f"dogfood round {i}"}))


def run():
    pipeline = GovernancePipeline()

    total = 0
    bypassed = 0          # before_tool()が呼ばれなかった/例外で素通りした件数
    fatal_errors = 0
    write_calls = 0
    write_aborted = 0
    mode_counter = Counter()
    checklist_fail = 0
    log = []

    for tool_name, args in CALL_SEQUENCE:
        total += 1
        try:
            decision = pipeline.before_tool(tool_name, args)
        except Exception:
            fatal_errors += 1
            bypassed += 1
            log.append({"tool": tool_name, "error": traceback.format_exc().splitlines()[-1]})
            continue

        mode_counter[decision.thinking_mode] += 1
        if not decision.checklist_ok:
            checklist_fail += 1

        if tool_name in WRITE_TOOLS:
            write_calls += 1
            if not decision.allowed:
                write_aborted += 1

        log.append({
            "tool": tool_name,
            "allowed": decision.allowed,
            "mode": decision.thinking_mode,
            "checklist_ok": decision.checklist_ok,
            "aborts": decision.dry_run_aborts,
        })

    dry_run_false_positive_rate = (write_aborted / write_calls) if write_calls else 0.0

    result = {
        "total_calls": total,
        "bypassed": bypassed,
        "fatal_errors": fatal_errors,
        "write_calls": write_calls,
        "write_aborted": write_aborted,
        "dry_run_false_positive_rate": dry_run_false_positive_rate,
        "checklist_fail_count": checklist_fail,
        "thinking_mode_distribution": dict(mode_counter),
    }

    with open("dogfood_result.json", "w", encoding="utf-8") as f:
        json.dump({"summary": result, "log": log}, f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    summary = run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
