import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 1. データ読み込み
data_path = r'C:\Users\sirok\MoCKA\data\event_z_scores.csv'
df = pd.read_csv(data_path)

# Before / After 分割
before_z = df[df['phase'] == 'before']['Z']
after_z = df[df['phase'] == 'after']['Z']

# 2. 基本統計検定 (Welch's t-test)
t_stat, p_val = stats.ttest_ind(before_z, after_z, equal_var=False)
d = (after_z.mean() - before_z.mean()) / np.sqrt((after_z.std()**2 + before_z.std()**2) / 2)

# 3. 時系列安定性検証 (Afterを前後半に分割)
after_df = df[df['phase'] == 'after'].copy()
mid_point = len(after_df) // 2
after_first = after_df.iloc[:mid_point]['Z']
after_second = after_df.iloc[mid_point:]['Z']

# 4. バランス・ブートストラップ (1000回反復)
n_before = len(before_z)
diff_means = []
for _ in range(1000):
    sample_after = after_z.sample(n_before, replace=True)
    diff_means.append(sample_after.mean() - before_z.mean())

ci_lower, ci_upper = np.percentile(diff_means, [2.5, 97.5])

# --- レポート出力 ---
print("=== MoCKA 制度整合性 検証報告書 ===")
print(f"【基本統計】")
print(f"Before Mean: {before_z.mean():.4f} (n={len(before_z)})")
print(f"After  Mean: {after_z.mean():.4f} (n={len(after_z)})")
print(f"ΔZ (改善幅): {after_z.mean() - before_z.mean():.4f}")
print(f"t-value: {t_stat:.4f}, p-value: {p_val:.4e}")
print(f"Cohen's d (効果量): {d:.4f}")

print(f"\n【時系列安定性 (After分割)】")
print(f"After 前半 Mean: {after_first.mean():.4f}")
print(f"After 後半 Mean: {after_second.mean():.4f}")
print(f"安定性差分: {after_second.mean() - after_first.mean():.4f} (正の値なら習熟/安定を示す)")

print(f"\n【バランス補正 (Bootstrap 1000回)】")
print(f"ΔZ 95%信頼区間: [{ci_lower:.4f} to {ci_upper:.4f}]")
if ci_lower > 0:
    print("判定: 統計的に極めて堅牢な改善を確認（0を跨がない）")

# 5. 可視化 (図表の生成)
plt.figure(figsize=(10, 6))
plt.hist(diff_means, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.axvline(x=0, color='red', linestyle='--', label='No Change Line')
plt.title('Bootstrap Distribution of ΔZ (After_sample - Before_mean)')
plt.xlabel('Mean Difference in Z')
plt.ylabel('Frequency')
plt.legend()
plt.savefig(r'C:\Users\sirok\MoCKA\fig_bootstrap_dz.png')
print(f"\n可視化完了: fig_bootstrap_dz.png を保存しました。")