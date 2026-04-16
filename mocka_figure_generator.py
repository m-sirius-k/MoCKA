import csv
import os
import matplotlib.pyplot as plt

INPUT_FILE = os.path.join("data", "event_z_scores.csv")

rows = []
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        try:
            rows.append({
                "Z": float(r["Z"]),
                "phase": r["phase"].strip().lower()
            })
        except:
            continue

before = [r["Z"] for r in rows if r["phase"] == "before"]
after  = [r["Z"] for r in rows if r["phase"] == "after"]

# ===== Figure1: 分布 =====
plt.figure()
plt.hist(before, bins=10, alpha=0.7, label="Before")
plt.hist(after, bins=20, alpha=0.7, label="After")
plt.xlabel("Z")
plt.ylabel("Frequency")
plt.title("Z Distribution Before vs After")
plt.legend()
plt.savefig("fig_z_distribution.png")
plt.close()

# ===== Figure2: 時系列 =====
z_values = [r["Z"] for r in rows]

plt.figure()
plt.plot(z_values)
plt.axvline(x=13, linestyle="--")  # Before=13
plt.xlabel("Event Index")
plt.ylabel("Z")
plt.title("Z Timeline")
plt.savefig("fig_z_timeline.png")
plt.close()

print("完了: Figure生成")
print("fig_z_distribution.png")
print("fig_z_timeline.png")