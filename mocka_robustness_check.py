import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. データ読み込み
data_path = r'C:\Users\sirok\MoCKA\data\event_z_scores.csv'
df = pd.read_csv(data_path)

after_df = df[df['phase'] == 'after'].copy()
before_z = df[df['phase'] == 'before']['Z']

print("=== MoCKA 追加実証：堅牢性チェック報告書 ===")

# --- 実証①：時系列分割再検証 ---
mid = len(after_df) // 2
after_v1 = after_df.iloc[:mid]['Z']
after_v2 = after_df.iloc[mid:]['Z']

print(f"\n【1. 時系列安定性】")
print(f"After 前半 (n={len(after_v1)}) Mean: {after_v1.mean():.4f}")
print(f"After 後半 (n={len(after_v2)}) Mean: {after_v2.mean():.4f}")
print(f"安定性評価: {'安定' if abs(after_v1.mean()-after_v2.mean()) < 0.01 else '変動あり'}")

# --- 実証②：疑似Before生成（分布比較） ---
# AfterからBeforeと同じ数(13)をサンプリングし、その平均がBefore平均(0.7477)を下回る確率を計算
pseudo_means = [after_df['Z'].sample(len(before_z)).mean() for _ in range(5000)]
prob_lower = np.mean([1 if m <= before_z.mean() else 0 for m in pseudo_means])

print(f"\n【2. 疑似Before分布比較】")
print(f"Afterからn=13をサンプリングした際の平均分布の下限: {min(pseudo_means):.4f}")
print(f"Before平均({before_z.mean():.4f})以下の個体が出現する確率: {prob_lower * 100:.2f}%")
if prob_lower < 0.01:
    print("判定: 現行のBeforeスコアはAfterのランダムな変動では説明不可能なほど低い（＝制度の効果が明確）")

# --- 実証③：低Zイベント（逸脱）抽出 ---
threshold = after_df['Z'].quantile(0.10)
low_z_events = after_df[after_df['Z'] <= threshold]

print(f"\n【3. 低Zイベント分析（ワースト10%）】")
print(f"低Zしきい値: {threshold:.4f}")
print(f"該当件数: {len(low_z_events)} 件")
print("\n--- 低Zイベントの傾向（上位5件の生数値） ---")
print(low_z_events['Z'].head(5).to_string(index=False))

# --- 可視化 ---
plt.figure(figsize=(10, 5))
plt.hist(pseudo_means, bins=50, alpha=0.6, color='green', label='Pseudo-Before Means (from After)')
plt.axvline(before_z.mean(), color='red', linestyle='--', label='Actual Before Mean')
plt.title('Comparison: Actual Before vs Pseudo-Before Distribution')
plt.xlabel('Z Score Mean')
plt.ylabel('Frequency')
plt.legend()
plt.savefig(r'C:\Users\sirok\MoCKA\fig_pseudo_before_comp.png')
print(f"\n可視化完了: fig_pseudo_before_comp.png を保存しました。")