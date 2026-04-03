import json
import os
import sys
import csv
import datetime
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EVENTS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "events.csv")
ORCHESTRA_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "mocka_orchestra_v10.py")

def get_next_event_id():
    today = datetime.datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    max_num = 0
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if row and row[0].startswith(prefix):
                    try:
                        num = int(row[0].replace(prefix, ""))
                        max_num = max(max_num, num)
                    except:
                        pass
    return f"{prefix}{str(max_num + 1).zfill(3)}"

# =====================
# Caliber指標
# =====================
def calc_error_rate():
    """B3: 直近10件のERROR率"""
    if not os.path.exists(EVENTS_CSV):
        return 0.0
    with open(EVENTS_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    recent = rows[-10:] if len(rows) > 10 else rows
    err = sum(1 for r in recent if "ERROR" in str(r))
    return round(err / max(len(recent), 1), 2)

def calc_drift_v3():
    """AEGIS: Drift v3多指標"""
    if not os.path.exists(EVENTS_CSV):
        return 0.0
    with open(EVENTS_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    recent = rows[-20:] if len(rows) > 20 else rows
    error_rate = sum(1 for r in recent if "ERROR" in str(r)) / max(len(recent), 1)
    violation = sum(1 for r in recent if "blocked" in str(r)) / max(len(recent), 1)
    return round(0.45 * error_rate + 0.30 * violation, 2)

def classify_anomaly():
    """AEGIS: 異常タイプ分類"""
    error_rate = calc_error_rate()
    drift = calc_drift_v3()
    if error_rate > 0.5: return "FAST_WRONG"
    if drift > 1.5:      return "SLOW_DRIFT"
    if error_rate > 0.3: return "FORMAT_COLLAPSE"
    if drift > 2.5:      return "DEPENDENCY_BREAK"
    return "NORMAL"

def get_aegis_action(anomaly):
    """AEGIS: 制御アクション"""
    return {
        "FAST_WRONG":       "RETRY_WITH_THINK",
        "SLOW_DRIFT":       "RESET_CONTEXT",
        "FORMAT_COLLAPSE":  "FORCE_FORMAT",
        "DEPENDENCY_BREAK": "FULL_REWRITE",
        "NORMAL":           "NONE"
    }.get(anomaly, "NONE")

def get_router_mode():
    """B4: Drift値に応じたモード決定"""
    error_rate = calc_error_rate()
    drift_score = error_rate * 10
    if drift_score < 1.0: return "full_orchestra"
    if drift_score < 2.0: return "share_only"
    if drift_score < 3.0: return "save_only"
    return "audit_mode"

def record_to_events_csv(event_id, mode, content, result="", note="", response_time=None):
    error_rate = calc_error_rate()
    router_mode = get_router_mode()
    anomaly = classify_anomaly()
    action = get_aegis_action(anomaly)
    caliber_note = f"error_rate={error_rate} | router_mode={router_mode} | anomaly={anomaly} | action={action}"
    if response_time is not None:
        caliber_note += f" | response_time={response_time}s"
    full_note = f"{note} | {caliber_note}" if note else caliber_note

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
        "free_note": full_note[:200]
    }
    with open(EVENTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writerow(row)
    print(f"[events.csv] 記録完了: {event_id} [{mode}] {caliber_note}")
    # 記録後に自動リスク判定
    import subprocess as _sp
    _sp.Popen([sys.executable,
               os.path.join(os.path.dirname(os.path.abspath(__file__)),
               "..", "tools", "mocka_risk_engine.py")],
               stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)

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
        router_mode = get_router_mode()
        print(f"[MoCKARouter] share ({router_mode}): {content[:50]}...")
        if router_mode == "audit_mode":
            print("[AUDIT] Drift CRITICAL: share実行をスキップ")
            event_id = get_next_event_id()
            record_to_events_csv(event_id, "share_blocked", content, "audit_mode_blocked")
            return {"event_id": event_id, "mode": "blocked"}
        start = time.time()
        stdout, stderr = run_orchestra(content, "share")
        response_time = round(time.time() - start, 1)
        print(stdout)
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "share", content, stdout, stderr[:100], response_time)
        return {"event_id": event_id, "mode": "share"}

    def save(self, title, content):
        """events.csvに記録のみ"""
        print(f"[MoCKARouter] save: {title}...")
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "save", title, content, "manual_save")
        return {"event_id": event_id, "mode": "save"}

    def collaborate(self, problem):
        """4AI回収→Claude統合分析"""
        router_mode = get_router_mode()
        print(f"[MoCKARouter] collaborate ({router_mode}): {problem[:50]}...")
        if router_mode == "audit_mode":
            print("[AUDIT] Drift CRITICAL: collaborate実行をスキップ")
            event_id = get_next_event_id()
            record_to_events_csv(event_id, "collaborate_blocked", problem, "audit_mode_blocked")
            return {"event_id": event_id, "mode": "blocked"}
        start = time.time()
        stdout, stderr = run_orchestra(problem, "orchestra")
        response_time = round(time.time() - start, 1)
        print(stdout)
        event_id = get_next_event_id()
        record_to_events_csv(event_id, "collaboration", problem, stdout, stderr[:100], response_time)
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
