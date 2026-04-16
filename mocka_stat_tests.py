import csv
import math
import sys
import os

# ===== 入力ファイル =====
INPUT_FILE = os.path.join("data", "event_z_scores.csv")

# ===== ファイル存在確認 =====
if not os.path.exists(INPUT_FILE):
    print("ERROR: 入力ファイルが存在しない")
    print(f"期待パス: {INPUT_FILE}")
    sys.exit()

# ===== データ読み込み =====
rows = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        try:
            z = float(r["Z"])
            phase = r["phase"].strip().lower()
            rows.append({"Z": z, "phase": phase})
        except:
            continue

# ===== 分割 =====
before = [r["Z"] for r in rows if r["phase"] == "before"]
after  = [r["Z"] for r in rows if r["phase"] == "after"]

print("=== データ確認 ===")
print("total rows:", len(rows))
print("before:", len(before))
print("after :", len(after))

if len(before) < 2 or len(after) < 2:
    print("ERROR: サンプル不足")
    sys.exit()

# ===== 関数 =====
def mean(x):
    return sum(x) / len(x)

def variance(x):
    m = mean(x)
    return sum((i - m) ** 2 for i in x) / (len(x) - 1)

# ===== 統計量 =====
m1 = mean(before)
m2 = mean(after)
v1 = variance(before)
v2 = variance(after)
n1 = len(before)
n2 = len(after)

# ===== Welch t =====
t = (m1 - m2) / math.sqrt(v1/n1 + v2/n2)

# ===== 自由度 =====
df = (v1/n1 + v2/n2)**2 / (((v1/n1)**2/(n1-1)) + ((v2/n2)**2/(n2-1)))

# ===== Cohen's d =====
pooled = math.sqrt(((n1-1)*v1 + (n2-1)*v2) / (n1+n2-2))
d = (m2 - m1) / pooled

# ===== 出力 =====
print("\n=== 統計検定結果 ===")
print(f"Before mean: {m1:.4f}")
print(f"After  mean: {m2:.4f}")
print(f"t-value    : {t:.4f}")
print(f"df         : {df:.2f}")
print(f"Cohen's d  : {d:.4f}")

# ===== 保存 =====
with open("stat_test_results.txt", "w", encoding="utf-8") as f:
    f.write("Statistical Test Results\n")
    f.write(f"Before mean: {m1:.4f}\n")
    f.write(f"After mean: {m2:.4f}\n")
    f.write(f"t-value: {t:.4f}\n")
    f.write(f"df: {df:.2f}\n")
    f.write(f"Cohen's d: {d:.4f}\n")

print("\n完了: stat_test_results.txt 出力")