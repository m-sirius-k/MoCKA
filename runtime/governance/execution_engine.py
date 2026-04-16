from runtime.record.csv_record_engine import record_event

EXECUTION_ORDER = [
    "registry",
    "detection",
    "decision",
    "repair",
    "record",
    "verify",
    "audit"
]

PRIORITY = {
    "incident": 1,
    "instruction": 2,
    "chat": 3,
    "system": 4,
    "audit": 5
}

def sort_by_priority(event_type):
    return PRIORITY.get(event_type, 999)

def execute_pipeline(event_text, event_type,
                     registry_fn,
                     detection_fn,
                     decision_fn,
                     repair_fn,
                     verify_fn,
                     audit_fn):

    context = {
        "event_text": event_text,
        "event_type": event_type
    }

    # --- 優先順位適用 ---
    context["priority"] = sort_by_priority(event_type)

    # --- registry ---
    context["registry"] = registry_fn(event_text)
    record_event("system", f"registry:{context['registry']}")

    # --- detection ---
    context["detection"] = detection_fn(event_text)
    record_event("system", f"detection:{context['detection']}")

    # --- decision ---
    context["decision"] = decision_fn(event_text)
    record_event("system", f"decision:{context['decision']}")

    # --- repair ---
    context["repair"] = repair_fn(event_text)
    record_event("system", f"repair:{context['repair']}")

    # --- verify ---
    context["verify"] = verify_fn()
    record_event("system", f"verify:{context['verify']}")

    # --- audit ---
    context["audit"] = audit_fn()
    record_event("audit", f"audit:{context['audit']}")

    return context
