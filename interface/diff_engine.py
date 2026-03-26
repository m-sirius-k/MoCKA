def analyze(results):
    outputs = []
    errors = []

    for r in results:
        if "output" in r:
            outputs.append({
                "provider": r["provider"],
                "text": r["output"]
            })
        else:
            errors.append({
                "provider": r.get("provider"),
                "error": r.get("error")
            })

    summary = {
        "success_count": len(outputs),
        "error_count": len(errors),
        "outputs": outputs,
        "errors": errors
    }

    # 差分（単純比較）
    if len(outputs) >= 2:
        base = outputs[0]["text"]
        diffs = []

        for o in outputs[1:]:
            if o["text"] != base:
                diffs.append({
                    "provider": o["provider"],
                    "different": True
                })
            else:
                diffs.append({
                    "provider": o["provider"],
                    "different": False
                })

        summary["diff"] = diffs

    return summary
