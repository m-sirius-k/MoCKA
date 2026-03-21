import uuid
from datetime import datetime

from runtime.record.csv_record_engine import record_event
from runtime.governance.execution_order_engine import execute_order
from runtime.governance.dispatcher import dispatch_event
from runtime.record.recurrence_engine import detect_recurrence
from runtime.record.improvement_loop import improvement_loop
from runtime.governance.meta_audit_engine import meta_audit
from runtime.governance.preventive_rule_engine import check_preventive, apply_preventive_rule


def generate_event():
    # 本番そのままでも発火するようにしている
    return "CSV再生成せず修正のみ実施のケース発生"


def main():
    print("=== MoCKA Layer14 Preventive Civilization ===")

    event_text = generate_event()
    event_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # =====================================================
    # 1. PREVENTIVE（最優先）
    # =====================================================
    preventive = check_preventive(event_text)

    if preventive.get("prevented"):
        result = apply_preventive_rule(preventive)

        record_event(
            "preventive_trigger",
            f"PREVENTED: {result.get('incident_id')}",
            ""
        )

        print("PREVENTED:", result)
        return

    # =====================================================
    # 2. DISPATCH
    # =====================================================
    dispatch = dispatch_event(event_text)
    event_type = dispatch.get("event_type", "chat")

    record_event(event_type, event_text, "")

    # =====================================================
    # 3. DETECTION
    # =====================================================
    detection = detect_recurrence(event_text)

    if detection.get("recurrence_detected"):
        record_event(
            "self_doubt_trigger",
            f"STOP: {detection['matches']}",
            ""
        )

        print("STOP:", detection)

        # =================================================
        # 4. REPAIR
        # =================================================
        repair = improvement_loop(event_text)

        record_event(
            "auto_repair",
            f"EXECUTED: {repair}",
            ""
        )

        print("REPAIR:", repair)

        return

    # =====================================================
    # 5. NORMAL
    # =====================================================
    record_event("system", "continue", "")

    verify = execute_order()
    record_event("verify", str(verify), "")

    audit = meta_audit()
    record_event("audit", str(audit), "")

    print("RESULT:", {
        "event": event_text,
        "dispatch": dispatch,
        "detection": detection,
        "verify": verify,
        "audit": audit
    })


if __name__ == "__main__":
    main()
