import random

# 100問をグループ別に定義
groups = {
    "G1_物理証拠": list(range(1, 21)),
    "G2_秘密情報": list(range(21, 41)),
    "G3_多重監査": list(range(41, 61)),
    "G4_PILS純度": list(range(61, 81)),
    "G5_遊動座標": list(range(81, 101))
}

# 各回：各グループから4問ずつ、計20問
# ただし3回で重複しないよう分散

random.seed(20260401)  # 再現性のため固定seed

used = {g: [] for g in groups}
exams = []

for round_num in range(1, 4):
    exam = {}
    for g, questions in groups.items():
        available = [q for q in questions if q not in used[g]]
        selected = random.sample(available, 4)
        used[g].extend(selected)
        exam[g] = sorted(selected)
    exams.append(exam)

# 出力
output = []
output.append("# MoCKA ストレステスト 3回分問題配布表")
output.append("## 分布方針：各グループから4問×5グループ=20問/回 × 3回 = 60問（重複なし）")
output.append("## seed: 20260401（再現可能）")
output.append("")

for i, exam in enumerate(exams, 1):
    output.append(f"---")
    output.append(f"## 第{i}回 試験問題")
    output.append("")
    all_q = []
    for g, qs in exam.items():
        output.append(f"### {g}")
        for q in qs:
            output.append(f"- Q{q}")
        all_q.extend(qs)
    output.append("")
    output.append(f"**出題問題番号（昇順）:** {sorted(all_q)}")
    output.append("")

# 未出題問題
all_used = []
for exam in exams:
    for qs in exam.values():
        all_used.extend(qs)
unused = [q for q in range(1, 101) if q not in all_used]
output.append("---")
output.append(f"## 未出題問題（予備・次回用）: {unused}")

print("\n".join(output))

# ファイル保存
with open(r"C:\Users\sirok\MoCKA\caliber\stress\EXAM_DISTRIBUTION_v2026.04.md", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
print("\n[保存完了] EXAM_DISTRIBUTION_v2026.04.md")
