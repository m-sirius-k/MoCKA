import random
import csv
import sys

# ===== 入力ファイル =====
INPUT_FILE = "event_z_scores.csv"

# ===== データ読み込み =====
rows_out = []

try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["Z"] = float(row["Z"])
                row["phase"] = row["phase"].strip().lower()
                rows_out.append(row)
            except Exception as e:
                continue
except FileNotFoundError:
    print("ERROR: event_z_scores.csv が見つからない")
    sys.exit()

# ===== 基本検証 =====
print("=== データ検証 ===")
print("total rows:", len(rows_out))

if len(rows_out) == 0:
    print("ERROR: データが0件")
    sys.exit()

# ===== Before / After 分割 =====
before = [r["Z"] for r in rows_out if r["phase"] == "before"]
after  = [r["Z"] for r in rows_out if r["phase"] == "after"]

print("before count:", len(before))
print("after count:", len(after))

if len(before) == 0 or len(after) == 0:
    print("ERROR: before/after の分割に失敗")
    print("phase列の値を確認せよ")
    sys.exit()

if len(after) < len(before):
    print("ERROR: after の方が少ないためサンプリング不可")
    sys.exit()

# ===== 平均関数 =====
def mean(x):
    return sum(x) / len(x)

# ===== パラメータ =====
N = 1000

delta_list = []
after_means = []

print("\n=== バランスサンプリング開始 ===")

# ===== サンプリング =====
for i in range(N):
    after_sample = random.sample(after, len(before))
    
    m_before = mean(before)
    m_after  = mean(after_sample)
    
    delta = m_after - m_before
    
    delta_list.append(delta)
    after_means.append(m_after)

# ===== 統計量 =====
delta_mean = mean(delta_list)
delta_sorted = sorted(delta_list)

ci_lower = delta_sorted[int(0.025 * N)]
ci_upper = delta_sorted[int(0.975 * N)]

# ===== 結果出力 =====
print("\n=== バランス比較（分布） ===")
print(f"Before mean: {mean(before):.4f}")
print(f"ΔZ mean: {delta_mean:.4f}")
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

# ===== CSV出力 =====
with open("balanced_sampling_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "delta_z", "after_mean"])
    
    for i in range(N):
        writer.writerow([i, delta_list[i], after_means[i]])

# ===== サマリ出力 =====
with open("balanced_sampling_summary.txt", "w", encoding="utf-8") as f:
    f.write("Balanced Sampling Summary\n")
    f.write(f"Total rows: {len(rows_out)}\n")
    f.write(f"Before count: {len(before)}\n")
    f.write(f"After count: {len(after)}\n")
    f.write(f"Before mean: {mean(before):.4f}\n")
    f.write(f"Delta mean: {delta_mean:.4f}\n")
    f.write(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]\n")

print("\n=== 完了 ===")
print("出力ファイル:")
print("- balanced_sampling_results.csv")
print("- balanced_sampling_summary.txt")