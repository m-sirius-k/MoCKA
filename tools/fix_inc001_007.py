"""INC-001〜007 MOCKA_TODO.json 不整合一括修復スクリプト"""
import json
import sys
from pathlib import Path

ROOT_PATH = Path(r"C:\Users\sirok\MOCKA_TODO.json")
REPO_PATH = Path(r"C:\Users\sirok\MoCKA\data\MOCKA_TODO.json")

sys.stdout.reconfigure(encoding="utf-8")

with open(ROOT_PATH, encoding="utf-8") as f:
    data = json.load(f)

todos = data.get("todos", [])
completed = data.get("completed", [])

report = {}

# -------------------------------------------------------
# INC-002: TODO_030 status修正 (completed内)
# -------------------------------------------------------
fixed_002 = 0
for item in completed:
    if item.get("id") == "TODO_030" and item.get("status") != "完了":
        item["status"] = "完了"
        fixed_002 += 1
report["INC-002"] = f"TODO_030 status -> 完了 ({fixed_002}件修正)"

# -------------------------------------------------------
# INC-003: todos内の完了・廃止4件をcompletedへ移動
# -------------------------------------------------------
MOVE_IDS = {"TODO_LB002", "TODO_276", "TODO_279", "TODO_326"}
to_move = [x for x in todos if x.get("id") in MOVE_IDS]
moved_ids = []
for item in to_move:
    if not item.get("completed_at"):
        item["completed_at"] = "2026-06-18T00:00:00"
    completed.append(item)
    moved_ids.append(item["id"])
todos = [x for x in todos if x.get("id") not in MOVE_IDS]
report["INC-003"] = f"todos->completed移動: {moved_ids}"

# -------------------------------------------------------
# INC-004: meta に廃止運用ルールを明記
# -------------------------------------------------------
meta = data.get("meta", {})
meta["rule_廃止_placement"] = "廃止TODOはcompletedに配置する（statusが廃止でもcompletedに入れる。廃止4件: TODO_276/279/326/LB002はINC-003で移動済み）"
report["INC-004"] = "meta.rule_廃止_placement を追記"

# -------------------------------------------------------
# INC-005: completed_at欠落18件の補完
# -------------------------------------------------------
MISSING_IDS = {
    "TODO_092", "TODO_117", "TODO_119", "TODO_120", "TODO_124", "TODO_125",
    "TODO_132", "TODO_133", "TODO_142", "TODO_164", "TODO_167", "TODO_181",
    "TODO_200", "TODO_201", "TODO_202", "TODO_040", "TODO_070", "TODO_072"
}
fixed_005 = []
for item in completed:
    if item.get("id") in MISSING_IDS and not item.get("completed_at"):
        # created_atを近似値として使用、なければ"unknown"
        created = item.get("created_at", "")
        if created and len(created) >= 10:
            approx = created[:10] + "T00:00:00"
        else:
            updated = item.get("updated_at", "")
            if updated and len(updated) >= 10:
                approx = updated[:10] + "T00:00:00"
            else:
                approx = "unknown"
        item["completed_at"] = approx
        fixed_005.append((item["id"], approx))
report["INC-005"] = f"completed_at補完: {len(fixed_005)}件 {fixed_005}"

# -------------------------------------------------------
# INC-006: completed_atが日付のみの場合にT00:00:00を補完
# -------------------------------------------------------
fixed_006 = 0
for item in completed:
    ca = item.get("completed_at")
    if ca and isinstance(ca, str) and len(ca) == 10 and ca != "unknown":
        item["completed_at"] = ca + "T00:00:00"
        fixed_006 += 1
meta["rule_completed_at_format"] = "completed_atは必ずISO 8601フル形式(YYYY-MM-DDTHH:MM:SS)で記録する。日付のみは不可。"
report["INC-006"] = f"completed_atにT00:00:00補完: {fixed_006}件。meta.rule_completed_at_formatを追記"

# -------------------------------------------------------
# INC-007: TODO_TEST_342 削除
# -------------------------------------------------------
before_len = len(completed)
completed = [x for x in completed if x.get("id") != "TODO_TEST_342"]
report["INC-007"] = f"TODO_TEST_342削除: {before_len - len(completed)}件"

# -------------------------------------------------------
# 書き戻し
# -------------------------------------------------------
data["todos"] = todos
data["completed"] = completed
data["meta"] = meta

with open(ROOT_PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("=== INC-002〜007 修復完了 ===")
for k, v in report.items():
    print(f"  {k}: {v}")
print(f"\n最終カウント: todos={len(todos)}, completed={len(completed)}")

# 整合性再検証
bad_todos = [(x["id"], x["status"]) for x in todos if x.get("status") in ("完了", "廃止")]
print(f"todos内完了/廃止残留: {bad_todos} (0件ならOK)")
t030 = [x for x in completed if x.get("id") == "TODO_030"]
print(f"TODO_030 status: {t030[0]['status'] if t030 else 'not found'} (完了ならOK)")
still_missing = [x["id"] for x in completed if not x.get("completed_at")]
print(f"completed_at欠落: {len(still_missing)}件 (0件ならOK)")
test_items = [x["id"] for x in completed if "TEST" in x.get("id", "")]
print(f"TEST残留: {test_items} (空ならOK)")
date_only_remaining = [x["id"] for x in completed if x.get("completed_at") and len(str(x.get("completed_at",""))) == 10]
print(f"日付のみ残留: {len(date_only_remaining)}件 (0件ならOK)")
