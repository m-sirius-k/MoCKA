from runtime.record.improvement_loop import improvement_loop

# 強制的に「再発条件一致」にする
test_event = "CSV再生成せず修正のみ実施"  # ←インシデントのRecurrenceConditionに近づける

result = improvement_loop(test_event)

print(result)
