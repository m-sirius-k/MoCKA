import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 現状のBefore(13件)の統計量を抽出
# 平均 0.7477, 標準偏差を実データから計算（仮に0.12とする）
before_mean = 0.7477
before_std = 0.12 

# 1. Beforeを300件に拡張（シミュレーション生成）
np.random.seed(42)
before_sim = np.random.normal(before_mean, before_std, 300)
before_sim = np.clip(before_sim, 0.4, 0.95) # 現実的な範囲にクリップ

# 2. Afterの実データ(489件)を読み込み
df = pd.read_csv(r'C:\Users\sirok\MoCKA\data\event_z_scores.csv')
after_real = df[df['phase'] == 'after']['Z']

# 3. 可視化（密度分布比較）
plt.figure(figsize=(12, 6))
sns.kdeplot(before_sim, fill=True, color="red", label=f"Before (Simulated n=300, Mean={before_mean})", bw_adjust=1)
sns.kdeplot(after_real, fill=True, color="blue", label=f"After (Real n=489, Mean={after_real.mean():.4f})", bw_adjust=1)

plt.axvline(before_mean, color='red', linestyle='--', alpha=0.6)
plt.axvline(after_real.mean(), color='blue', linestyle='--', alpha=0.6)

plt.title("The 'IF' Scenario: Manual Management(300) vs MoCKA Governance(489)")
plt.xlabel("Institutional Integrity Score (Z)")
plt.ylabel("Density")
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.savefig(r'C:\Users\sirok\MoCKA\fig_if_300_comparison.png')
print("シミュレーション完了: fig_if_300_comparison.png を確認してください。")

# 統計的有意差の再計算
from scipy import stats
t_sim, p_sim = stats.ttest_ind(before_sim, after_real, equal_var=False)
print(f"\n--- シミュレーション結果 ---")
print(f"仮にBeforeが300件だった場合のp-value: {p_sim:.2e}")
print(f"この時のt値: {t_sim:.4f}")