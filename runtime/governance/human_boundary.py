def classify_action(countermeasure_text):
    text = countermeasure_text.lower()

    # --- 危険領域（禁止） ---
    if "削除" in countermeasure_text or "delete" in text:
        return "forbidden"

    if "全書き換え" in countermeasure_text or "rewrite all" in text:
        return "forbidden"

    # --- 要承認領域 ---
    if "コード" in countermeasure_text or "code" in text:
        return "approval"

    if "config" in text or "設定" in countermeasure_text:
        return "approval"

    # --- 自動実行 ---
    return "auto"

def enforce_boundary(countermeasure_text):
    level = classify_action(countermeasure_text)

    if level == "forbidden":
        return {
            "status": "blocked",
            "reason": "forbidden_action"
        }

    if level == "approval":
        return {
            "status": "pending_approval"
        }

    return {
        "status": "allowed"
    }
