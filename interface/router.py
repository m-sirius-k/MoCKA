import json
import os
import sys
import csv
import datetime
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EVENTS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "events.csv")
ORCHESTRA_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "mocka_orchestra_v10.py")

def get_next_event_id():
    today = datetime.datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    max_num = 0
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].startswith(prefix):
                    try:
                        num = int(row[0].replace(prefix, ""))
                        max_num = max(max_num, num)
                    except:
                        pass
    return f"{prefix}{str(max_num + 1).zfill(3)}"

def record_to_events_csv(event_id, mode, content, result="", note=""):
    row = {
        "event_id": event_id,
        "when": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "who_actor": "mocka_router",
        "what_type": mode,
        "where_component": "router",
        "where_path": "interface/router.py",
        "why_purpose": content[:100],
        "how_trigger": "cli",
        "channel_type": "internal",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "category_ab": "A",
        "target_class": "outfield",
        "title": f"[{mode}] {content[:50]}",
        "short_summary": result[:200],
        "before_state": "N/A",
        "after_state": f"{mode}_complete",
        "change_type": "generation",
        "impact_scope": "local",
        "impact_result": mode,
        "related_event_id": "N/A",
        "trace_id": "N/A",
        "free_note": note[:200]
    }
    with open(EVENTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writerow(row)
    print(f"[events.csv] 記録完了: {event_id} [{mode}]")

def run_orchestra(prompt, mode):
    result = subprocess.run(
        [sys.executable, ORCHESTRA_SCRIPT, prompt, mode],
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.stdout.strip(), result.stderr.strip()

class MoCKARouter:

    def share(self, content):
        """4AIに送信・返答待たない"""
        print(f"[MoCKARouter] share: {content[:50]}...")
        stdout, stderr = run_orchestra(content, "share")
        print(stdout)
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "share", content, stdout, stderr[:100])
        return {"event_id": event_id, "mode": "share"}

    def save(self, title, content):
        """events.csvに記録のみ"""
        print(f"[MoCKARouter] save: {title}...")
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "save", title, content, "manual_save")
        return {"event_id": event_id, "mode": "save"}

    def collaborate(self, problem):
        """4AI回収→Claude統合分析"""
        print(f"[MoCKARouter] collaborate: {problem[:50]}...")
        stdout, stderr = run_orchestra(problem, "orchestra")
        print(stdout)
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "collaboration", problem, stdout, stderr[:100])
        return {"event_id": event_id, "mode": "orchestra", "final_answer": stdout}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python router.py share      '内容'")
        print("  python router.py save       'タイトル' '内容'")
        print("  python router.py collaborate '問い'")
        sys.exit(1)

    router = MoCKARouter()
    mode = sys.argv[1]

    if mode == "share":
        result = router.share(sys.argv[2])
    elif mode == "save":
        title = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        result = router.save(title, content)
    elif mode == "collaborate":
        result = router.collaborate(sys.argv[2])
    else:
        print(f"不明なモード: {mode}")
        sys.exit(1)

    print(f"\n=== 完了: {result['event_id']} [{result['mode']}] ===")
