def validate_event(event):
    required = ["index","timestamp","event_type","data","prev_hash","hash"]

    for k in required:
        if k not in event:
            raise Exception(f"Missing field: {k}")

    if not isinstance(event["index"], int):
        raise Exception("index must be int")

    if not isinstance(event["timestamp"], str):
        raise Exception("timestamp must be string")

    if not isinstance(event["event_type"], str):
        raise Exception("event_type must be string")

    if not isinstance(event["data"], dict):
        raise Exception("data must be object")

    if not isinstance(event["prev_hash"], str):
        raise Exception("prev_hash must be string")

    if not isinstance(event["hash"], str):
        raise Exception("hash must be string")
