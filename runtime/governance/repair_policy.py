def classify_repair(countermeasure_text):
    text = countermeasure_text.lower()

    # --- 修正レベル分類 ---
    if "コード" in countermeasure_text or "code" in text:
        return "level_3"  # 危険（人間承認）

    if "設定" in countermeasure_text or "config" in text:
        return "level_2"  # 中リスク

    return "level_1"  # 安全（ログ・手順）

def repair_policy(countermeasure_text):
    level = classify_repair(countermeasure_text)

    if level == "level_3":
        return {
            "action": "blocked",
            "reason": "requires_human_approval"
        }

    if level == "level_2":
        return {
            "action": "allowed_with_log"
        }

    return {
        "action": "auto_execute"
    }
